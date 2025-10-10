import asyncio
import gc
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
import numpy as np
from PIL import Image
from tqdm import tqdm
import jsonlines

from fastmcp.exceptions import NotFoundError, ToolError, ValidationError
from ultrarag.server import UltraRAG_MCP_Server

app = UltraRAG_MCP_Server("retriever")


class Retriever:
    def __init__(self, mcp_inst: UltraRAG_MCP_Server):
        mcp_inst.tool(
            self.retriever_init,
            output="model_name_or_path,backend_configs,batch_size,corpus_path,index_path,faiss_use_gpu,gpu_ids,is_multimodal,backend->None",
        )
        mcp_inst.tool(
            self.retriever_embed,
            output="embedding_path,overwrite,is_multimodal->None",
        )
        mcp_inst.tool(
            self.retriever_index,
            output="embedding_path,index_path,overwrite,index_chunk_size->None",
        )
        mcp_inst.tool(
            self.retriever_search,
            output="q_ls,top_k,query_instruction->ret_psg",
        )
        mcp_inst.tool(
            self.retriever_search_colbert_maxsim,
            output="q_ls,embedding_path,top_k,query_instruction->ret_psg",
        )
        mcp_inst.tool(
            self.retriever_exa_search,
            output="q_ls,top_k,retrieve_thread_num->ret_psg",
        )
        mcp_inst.tool(
            self.retriever_tavily_search,
            output="q_ls,top_k,retrieve_thread_num->ret_psg",
        )
        mcp_inst.tool(
            self.retriever_zhipuai_search,
            output="q_ls,top_k,retrieve_thread_num->ret_psg",
        )

    def _drop_keys(self, d: Dict[str, Any], banned: List[str]) -> Dict[str, Any]:
        return {k: v for k, v in (d or {}).items() if k not in banned and v is not None}

    def retriever_init(
        self,
        model_name_or_path: str,
        backend_configs: Dict[str, Any],
        batch_size: int,
        corpus_path: str,
        index_path: Optional[str] = None,
        faiss_use_gpu: bool = False,
        gpu_ids: Optional[object] = None,
        is_multimodal: bool = False,
        backend: str = "infinity",
    ):

        try:
            import faiss
        except ImportError:
            err_msg = (
                "faiss is not installed. "
                "Please install it with `pip install faiss-cpu` "
                "or `pip install faiss-gpu-cu12`."
            )
            app.logger.error(err_msg)
            raise ImportError(err_msg)

        self.faiss_use_gpu = faiss_use_gpu
        self.backend = backend.lower()
        self.batch_size = batch_size

        self.backend_configs = backend_configs
        cfg = self.backend_configs.get(self.backend, {})

        gpu_ids = str(gpu_ids)
        os.environ["CUDA_VISIBLE_DEVICES"] = gpu_ids

        self.device_num = len(gpu_ids.split(","))

        if self.backend == "infinity":
            try:
                from infinity_emb import AsyncEngineArray, EngineArgs
            except ImportError:
                err_msg = "infinity_emb is not installed. Please install it with `pip install infinity-emb`."
                app.logger.error(err_msg)
                raise ImportError(err_msg)

            device = str(cfg.get("device", "")).strip().lower()
            if not device:
                warn_msg = f"[infinity] device is not set, default to `cpu`"
                app.logger.warning(warn_msg)
                device = "cpu"

            if device == "cpu":
                info_msg = "[infinity] device=cpu, gpu_ids is ignored"
                app.logger.info(info_msg)
                self.device_num = 1

            app.logger.info(
                f"[infinity] device={device}, gpu_ids={gpu_ids}, device_num={self.device_num}"
            )

            infinity_engine_args = EngineArgs(
                model_name_or_path=model_name_or_path,
                batch_size=self.batch_size,
                **cfg,
            )
            self.model = AsyncEngineArray.from_args([infinity_engine_args])[0]

        elif self.backend == "sentence_transformers":
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError:
                err_msg = (
                    "sentence_transformers is not installed. "
                    "Please install it with `pip install sentence-transformers`."
                )
                app.logger.error(err_msg)
                raise ImportError(err_msg)
            self.st_encode_params = cfg.get("sentence_transformers_encode", {}) or {}
            st_params = self._drop_keys(cfg, banned=["sentence_transformers_encode"])

            device = str(cfg.get("device", "")).strip().lower()
            if not device:
                warn_msg = (
                    f"[sentence_transformers] device is not set, default to `cpu`"
                )
                app.logger.warning(warn_msg)
                device = "cpu"

            if device == "cpu":
                info_msg = "[sentence_transformers] device=cpu, gpu_ids is ignored"
                app.logger.info(info_msg)
                self.device_num = 1

            app.logger.info(
                f"[sentence_transformers] device={device}, gpu_ids={gpu_ids}, device_num={self.device_num}"
            )

            self.model = SentenceTransformer(
                model_name_or_path=model_name_or_path,
                **st_params,
            )

        elif self.backend == "openai":
            from openai import AsyncOpenAI, OpenAIError

            model_name = cfg.get("model_name")
            base_url = cfg.get("base_url")
            api_key = cfg.get("api_key") or os.environ.get("RETRIEVER_API_KEY")

            if not model_name:
                err_msg = "[openai] model_name is required"
                app.logger.error(err_msg)
                raise ValueError(err_msg)
            if not isinstance(base_url, str) or not base_url:
                err_msg = "[openai] base_url must be a non-empty string"
                app.logger.error(err_msg)
                raise ValueError(err_msg)

            try:
                self.model = AsyncOpenAI(base_url=base_url, api_key=api_key)
                self.model_name = model_name
                info_msg = f"[openai] OpenAI client initialized (model='{model_name}', base='{base_url}')"
                app.logger.info(info_msg)
            except OpenAIError as e:
                err_msg = f"[openai] Failed to initialize OpenAI client: {e}"
                app.logger.error(err_msg)
                raise OpenAIError(err_msg)
        else:
            error_msg = (
                f"Unsupported backend: {backend}. "
                "Supported backends: 'infinity', 'sentence_transformers', 'openai'"
            )
            app.logger.error(error_msg)
            raise ValueError(error_msg)

        self.contents = []
        corpus_path_obj = Path(corpus_path)
        corpus_dir = corpus_path_obj.parent
        try:
            with jsonlines.open(corpus_path, mode="r") as r:
                total = sum(1 for _ in r)
        except Exception as e:
            total = None
            warn_msg = (
                f"[corpus] Failed to count records via jsonlines: {e}. "
                "Use indeterminate progress bar."
            )
            app.logger.warning(warn_msg)

        with jsonlines.open(corpus_path, mode="r") as reader:
            pbar = tqdm(total=total, desc="Loading corpus", ncols=100)
            if not is_multimodal:
                for i, item in enumerate(reader):
                    if "contents" not in item:
                        error_msg = (
                            f"Line {i}: missing key 'contents'. full item={item}"
                        )
                        app.logger.error(error_msg)
                        raise ValueError(error_msg)

                    self.contents.append(item["contents"])
                    pbar.update(1)
            else:
                for i, item in enumerate(reader):
                    if "image_path" not in item:
                        error_msg = (
                            f"Line {i}: missing key 'image_path'. full item={item}"
                        )
                        app.logger.error(error_msg)
                        raise ValueError(error_msg)

                    rel = str(item["image_path"])
                    abs_path = str((corpus_dir / rel).resolve())
                    self.contents.append(abs_path)
                    pbar.update(1)

        self.faiss_index = None
        if index_path and os.path.exists(index_path):
            cpu_index = faiss.read_index(index_path)

            if self.faiss_use_gpu:
                co = faiss.GpuMultipleClonerOptions()
                co.shard = True
                co.useFloat16 = True
                try:
                    self.faiss_index = faiss.index_cpu_to_all_gpus(cpu_index, co)
                    info_msg = f"[faiss] Loaded index to GPU(s) with {self.device_num} device(s)."
                    app.logger.info(info_msg)
                except RuntimeError as e:
                    warn_msg = (
                        f"[faiss] GPU index load failed: {e}. Falling back to CPU."
                    )
                    app.logger.warning(warn_msg)
                    self.faiss_use_gpu = False
                    self.faiss_index = cpu_index
            else:
                self.faiss_index = cpu_index
                info_msg = "[faiss] Loaded index on CPU."
                app.logger.info(info_msg)

            info_msg = "[faiss] Index loaded successfully."
            app.logger.info(info_msg)
        else:
            if index_path and not os.path.exists(index_path):
                warn_msg = f"{index_path} does not exist."
                app.logger.warning(warn_msg)
            info_msg = (
                "[faiss] no index_path provided. Retriever initialized without index."
            )
            app.logger.info(info_msg)

    async def retriever_embed(
        self,
        embedding_path: Optional[str] = None,
        overwrite: bool = False,
        is_multimodal: bool = False,
    ):
        embeddings = None

        if embedding_path is not None:
            if not embedding_path.endswith(".npy"):
                err_msg = (
                    f"Embedding save path must end with .npy, "
                    f"now the path is {embedding_path}"
                )
                app.logger.error(err_msg)
                raise ValidationError(err_msg)
            output_dir = os.path.dirname(embedding_path)
        else:
            current_file = os.path.abspath(__file__)
            project_root = os.path.dirname(os.path.dirname(current_file))
            output_dir = os.path.join(project_root, "output", "embedding")
            embedding_path = os.path.join(output_dir, "embedding.npy")

        if not overwrite and os.path.exists(embedding_path):
            app.logger.info("Embedding already exists, skipping")
            return

        os.makedirs(output_dir, exist_ok=True)

        if self.backend == "infinity":
            async with self.model:
                if is_multimodal:
                    data = []
                    for i, p in enumerate(self.contents):
                        try:
                            with Image.open(p) as im:
                                data.append(im.convert("RGB").copy())
                        except Exception as e:
                            err_msg = f"Failed to load image at index {i}: {p} ({e})"
                            app.logger.error(err_msg)
                            raise RuntimeError(err_msg)
                    call = self.model.image_embed
                else:
                    data = self.contents
                    call = self.model.embed

                eff_bs = self.batch_size * self.device_num
                n = len(data)
                pbar = tqdm(total=n, desc="[infinity] Embedding:")
                embeddings = []
                for i in range(0, n, eff_bs):
                    chunk = data[i : i + eff_bs]
                    vecs, _ = (
                        await call(images=chunk)
                        if is_multimodal
                        else await call(sentences=chunk)
                    )
                    embeddings.extend(vecs)
                    pbar.update(len(chunk))
                pbar.close()

        elif self.backend == "sentence_transformers":
            if self.device_num == 1:
                device_param = "cuda:0"
            else:
                device_param = [f"cuda:{i}" for i in range(self.device_num)]
            normalize = bool(self.st_encode_params.get("normalize_embeddings", False))
            csz = int(self.st_encode_params.get("encode_chunk_size", 10000))
            psg_prompt_name = self.st_encode_params.get("psg_prompt_name", None)
            psg_task = self.st_encode_params.get("psg_task", None)

            if is_multimodal:
                data = []
                for p in self.contents:
                    with Image.open(p) as im:
                        data.append(im.convert("RGB").copy())
            else:
                data = self.contents

            if isinstance(device_param, list) and len(device_param) > 1:
                pool = self.model.start_multi_process_pool()
                try:

                    def _encode_all():
                        return self.model.encode(
                            data,
                            pool=pool,
                            batch_size=self.batch_size,
                            chunk_size=csz,
                            show_progress_bar=True,
                            normalize_embeddings=normalize,
                            precision="float32",
                            prompt_name=psg_prompt_name,
                            task=psg_task,
                        )

                    embeddings = await asyncio.to_thread(_encode_all)
                finally:
                    self.model.stop_multi_process_pool(pool)
            else:

                def _encode_single():
                    return self.model.encode(
                        data,
                        device=device_param,
                        batch_size=self.batch_size,
                        show_progress_bar=True,
                        normalize_embeddings=normalize,
                        precision="float32",
                        prompt_name=psg_prompt_name,
                        task=psg_task,
                    )

                embeddings = await asyncio.to_thread(_encode_single)

        elif self.backend == "openai":
            if is_multimodal:
                err_msg = (
                    "openai backend does not support image embeddings in this path."
                )
                app.logger.error(err_msg)
                raise ValueError(err_msg)

            embeddings: list = []
            with tqdm(
                total=len(self.contents),
                desc="[openai] Embedding:",
                unit="item",
            ) as pbar:
                for start in range(0, len(self.contents), self.batch_size):
                    chunk = self.contents[start : start + self.batch_size]
                    resp = await self.model.embeddings.create(
                        model=self.model_name,
                        input=chunk,
                    )
                    embeddings.extend([d.embedding for d in resp.data])
                    pbar.update(len(chunk))
        else:
            err_msg = f"Unsupported backend: {self.backend}"
            app.logger.error(err_msg)
            raise ValueError(err_msg)

        if embeddings is None:
            raise RuntimeError("Embedding generation failed: embeddings is None")
        embeddings = np.array(embeddings, dtype=np.float32)
        np.save(embedding_path, embeddings)

        del embeddings
        gc.collect()
        app.logger.info("embedding success")

    def retriever_index(
        self,
        embedding_path: str,
        index_path: Optional[str] = None,
        overwrite: bool = False,
        index_chunk_size: int = 50000,
    ):
        try:
            import faiss
        except ImportError:
            err_msg = (
                "faiss is not installed. "
                "Please install it with `pip install faiss-cpu` "
                "or `pip install faiss-gpu-cu12`."
            )
            app.logger.error(err_msg)
            raise ImportError(err_msg)

        if not os.path.exists(embedding_path):
            app.logger.error(f"Embedding file not found: {embedding_path}")
            raise NotFoundError(f"Embedding file not found: {embedding_path}")

        if index_path:
            if not index_path.endswith(".index"):
                err_msg = (
                    f"Parameter 'index_path' must end with '.index', got '{index_path}'"
                )
                raise ValidationError(err_msg)
            output_dir = os.path.dirname(index_path)
        else:
            current_file = os.path.abspath(__file__)
            project_root = os.path.dirname(os.path.dirname(current_file))
            output_dir = os.path.join(project_root, "output", "index")
            index_path = os.path.join(output_dir, "index.index")

        if not overwrite and os.path.exists(index_path):
            info_msg = (
                f"Index file already exists: {index_path}. "
                "Set overwrite=True to overwrite."
            )
            app.logger.info(info_msg)
            return

        os.makedirs(output_dir, exist_ok=True)

        embedding = np.load(embedding_path)
        dim = embedding.shape[1]
        vec_ids = np.arange(embedding.shape[0]).astype(np.int64)

        cpu_flat = faiss.IndexFlatIP(dim)
        cpu_index = faiss.IndexIDMap2(cpu_flat)

        total = embedding.shape[0]
        info_msg = f"Start building FAISS index, total vectors: {total}"
        app.logger.info(info_msg)

        with tqdm(
            total=total,
            desc="[faiss] Indexing: ",
            unit="vec",
        ) as pbar:
            for start in range(0, total, index_chunk_size):
                end = min(start + index_chunk_size, total)
                cpu_index.add_with_ids(embedding[start:end], vec_ids[start:end])
                pbar.update(end - start)

        if self.faiss_use_gpu:
            co = faiss.GpuMultipleClonerOptions()
            co.shard = True
            co.useFloat16 = True
            try:
                gpu_index = faiss.index_cpu_to_all_gpus(cpu_index, co)
                index = gpu_index
                info_msg = f"Using GPU for indexing with sharding, device_num: {self.device_num}"
                app.logger.info(info_msg)
            except RuntimeError as e:
                err_msg = f"GPU indexing failed ({e}); fall back to CPU"
                app.logger.warning(err_msg)
                self.faiss_use_gpu = False
                index = cpu_index
        else:
            index = cpu_index

        faiss.write_index(cpu_index, index_path)

        if self.faiss_index is None or overwrite:
            self.faiss_index = index
        info_msg = "[faiss] Indexing success."
        app.logger.info(info_msg)

    async def retriever_search(
        self,
        query_list: List[str],
        top_k: int = 5,
        query_instruction: str = "",
    ) -> Dict[str, List[List[str]]]:

        if isinstance(query_list, str):
            query_list = [query_list]
        queries = [f"{query_instruction}{query}" for query in query_list]

        if self.backend == "infinity":
            async with self.model:
                query_embedding, _ = await self.model.embed(sentences=queries)
        elif self.backend == "sentence_transformers":
            if self.device_num == 1:
                device_param = "cuda:0"
            else:
                device_param = [f"cuda:{i}" for i in range(self.device_num)]
            normalize = bool(self.st_encode_params.get("normalize_embeddings", False))
            q_prompt_name = self.st_encode_params.get("q_prompt_name", "")
            q_task = self.st_encode_params.get("psg_task", None)

            if isinstance(device_param, list) and len(device_param) > 1:
                pool = self.model.start_multi_process_pool()
                try:

                    def _encode_all():
                        return self.model.encode(
                            queries,
                            pool=pool,
                            batch_size=self.batch_size,
                            show_progress_bar=True,
                            normalize_embeddings=normalize,
                            precision="float32",
                            prompt_name=q_prompt_name,
                            task=q_task,
                        )

                    query_embedding = await asyncio.to_thread(_encode_all)
                finally:
                    self.model.stop_multi_process_pool(pool)
            else:

                def _encode_single():
                    return self.model.encode(
                        queries,
                        device=device_param,
                        batch_size=self.batch_size,
                        show_progress_bar=True,
                        normalize_embeddings=normalize,
                        precision="float32",
                        prompt_name=q_prompt_name,
                        task=q_task,
                    )

                query_embedding = await asyncio.to_thread(_encode_single)

        elif self.backend == "openai":
            query_embedding = []
            for i in tqdm(
                range(0, len(queries), self.batch_size),
                desc="[openai] Embedding:",
                unit="batch",
            ):
                chunk = queries[i : i + self.batch_size]
                resp = await self.model.embeddings.create(
                    model=self.model_name, input=chunk
                )
                query_embedding.extend([d.embedding for d in resp.data])

        else:
            error_msg = f"Unsupported backend: {self.backend}"
            app.logger.error(error_msg)
            raise ValueError(error_msg)

        query_embedding = np.array(query_embedding, dtype=np.float32)

        info_msg = f"query embedding shape: {query_embedding.shape}"
        app.logger.info(info_msg)

        _, ids = self.faiss_index.search(query_embedding, top_k)
        rets = []
        for i, _ in enumerate(query_list):
            cur_ret = []
            for _, id in enumerate(ids[i]):
                cur_ret.append(self.contents[id])
            rets.append(cur_ret)
        return {"ret_psg": rets}

    async def retriever_search_colbert_maxsim(
        self,
        query_list: List[str],
        embedding_path: str,
        top_k: int = 5,
        query_instruction: str = "",
    ) -> Dict[str, List[List[str]]]:
        try:
            import torch
        except ImportError:
            err_msg = (
                "torch is not installed. Please install it with `pip install torch`."
            )
            app.logger.error(err_msg)
            raise ImportError(err_msg)

        if self.backend not in ["infinity"]:
            error_msg = (
                "retriever_search_colbert_maxsim only supports 'infinity' backend "
                "with ColBERT/ColPali multi-vector models. "
                "Use retriever_search or other backend-specific retrieval functions instead."
            )
            app.logger.error(error_msg)
            raise ValueError(error_msg)

        if isinstance(query_list, str):
            query_list = [query_list]
        queries = [f"{query_instruction}{query}" for query in query_list]

        async with self.model:
            query_embedding, _ = await self.model.embed(sentences=queries)

        doc_embeddings = np.load(embedding_path)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if (
            isinstance(doc_embeddings, np.ndarray)
            and doc_embeddings.dtype != object
            and doc_embeddings.ndim == 3
        ):
            docs_tensor = torch.from_numpy(
                doc_embeddings.astype("float32", copy=False)
            ).to(device)
        elif isinstance(doc_embeddings, np.ndarray) and doc_embeddings.dtype == object:
            try:
                stacked = np.stack(
                    [np.asarray(x, dtype=np.float32) for x in doc_embeddings.tolist()],
                    axis=0,
                )
                docs_tensor = torch.from_numpy(stacked).to(device)
            except Exception:
                error_msg = (
                    f"Document embeddings in {embedding_path} have inconsistent shapes, "
                    "cannot stack into (N,Kd,D). "
                    f"Check your retriever_embed."
                )
                app.logger.error(error_msg)
                raise ValueError(error_msg)
        else:
            error_msg = (
                f"Unexpected doc_embeddings format: type={type(doc_embeddings)}, "
                f"shape={getattr(doc_embeddings, 'shape', None)}"
            )
            app.logger.error(error_msg)
            raise ValueError(error_msg)

        def _l2norm(t: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
            return t / t.norm(dim=-1, keepdim=True).clamp_min(eps)

        N, _, D_docs = docs_tensor.shape
        docs_tensor = _l2norm(docs_tensor)
        k_pick = min(top_k, N)

        results = []
        for q_np in query_embedding:
            q = torch.as_tensor(
                q_np,
                dtype=torch.float32,
                device=device,
            )
            if q.shape[-1] != D_docs:
                error_msg = (
                    f"Dimension mismatch: query D={q.shape[-1]} vs doc D={D_docs}"
                )
                app.logger.error(error_msg)
                raise ValueError(error_msg)

            q = _l2norm(q)
            sim = torch.einsum("qd,nkd->nqk", q, docs_tensor)
            sim_max = sim.max(dim=2).values
            scores = sim_max.sum(dim=1)

            top_idx = torch.topk(scores, k=k_pick, largest=True).indices.tolist()
            results.append([self.contents[i] for i in top_idx])
        return {"ret_psg": results}

    async def _parallel_search(
        self,
        query_list: List[str],
        retrieve_thread_num: int,
        desc: str,
        worker_factory,
    ) -> Dict[str, List[List[str]]]:
        sem = asyncio.Semaphore(retrieve_thread_num)

        async def _wrap(i: int, q: str):
            async with sem:
                return await worker_factory(i, q)

        tasks = [asyncio.create_task(_wrap(i, q)) for i, q in enumerate(query_list)]
        ret: List[List[str]] = [None] * len(query_list)

        iterator = tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=desc)
        for fut in iterator:
            idx, psg_ls = await fut
            ret[idx] = psg_ls
        return {"ret_psg": ret}

    async def retriever_exa_search(
        self,
        query_list: List[str],
        top_k: Optional[int] | None = 5,
        retrieve_thread_num: Optional[int] | None = 1,
    ) -> Dict[str, List[List[str]]]:

        try:
            from exa_py import AsyncExa
            from exa_py.api import Result
        except ImportError:
            err_msg = (
                "exa_py is not installed. Please install it with `pip install exa_py`."
            )
            app.logger.error(err_msg)
            raise ImportError(err_msg)

        exa_api_key = os.environ.get("EXA_API_KEY", "")
        exa = AsyncExa(api_key=exa_api_key if exa_api_key else "EMPTY")

        async def worker_factory(idx: int, q: str):
            retries, delay = 3, 1.0
            for attempt in range(retries):
                try:
                    resp = await exa.search_and_contents(
                        q, num_results=top_k, text=True
                    )
                    results: List[Result] = getattr(resp, "results", []) or []
                    psg_ls: List[str] = [(r.text or "") for r in results]
                    return idx, psg_ls
                except Exception as e:
                    status = getattr(getattr(e, "response", None), "status_code", None)
                    if status == 401 or "401" in str(e):
                        err_msg = (
                            "Unauthorized (401): Invalid or missing EXA_API_KEY. "
                            "Please set it to use Exa."
                        )
                        app.logger.error(err_msg)
                        raise ToolError(err_msg) from e
                    warn_msg = f"[exa][retry {attempt+1}] failed (idx={idx}): {e}"
                    app.logger.warning(warn_msg)
                    await asyncio.sleep(delay)
            return idx, []

        return await self._parallel_search(
            query_list=query_list,
            retrieve_thread_num=retrieve_thread_num or 1,
            desc="EXA Searching:",
            worker_factory=worker_factory,
        )

    async def retriever_tavily_search(
        self,
        query_list: List[str],
        top_k: Optional[int] | None = 5,
        retrieve_thread_num: Optional[int] | None = 1,
    ) -> Dict[str, List[List[str]]]:

        try:
            from tavily import (
                AsyncTavilyClient,
                BadRequestError,
                UsageLimitExceededError,
                InvalidAPIKeyError,
                MissingAPIKeyError,
            )
        except ImportError:
            err_msg = "tavily is not installed. Please install it with `pip install tavily-python`."
            app.logger.error(err_msg)
            raise ImportError(err_msg)

        tavily_api_key = os.environ.get("TAVILY_API_KEY", "")
        if not tavily_api_key:
            err_msg = (
                "TAVILY_API_KEY environment variable is not set. "
                "Please set it to use Tavily."
            )
            app.logger.error(err_msg)
            raise MissingAPIKeyError(err_msg)
        tavily = AsyncTavilyClient(api_key=tavily_api_key)

        async def worker_factory(idx: int, q: str):
            retries, delay = 3, 1.0
            for attempt in range(retries):
                try:
                    resp = await tavily.search(query=q, max_results=top_k)
                    results: List[Dict[str, Any]] = resp["results"]
                    psg_ls: List[str] = [(r.get("content") or "") for r in results]
                    return idx, psg_ls
                except UsageLimitExceededError as e:
                    err_msg = f"Usage limit exceeded: {e}"
                    app.logger.error(err_msg)
                    raise ToolError(err_msg) from e
                except InvalidAPIKeyError as e:
                    err_msg = f"Invalid API key: {e}"
                    app.logger.error(err_msg)
                    raise ToolError(err_msg) from e
                except (BadRequestError, Exception) as e:
                    warn_msg = f"[tavily][retry {attempt+1}] failed (idx={idx}): {e}"
                    app.logger.warning(warn_msg)
                    await asyncio.sleep(delay)
            return idx, []

        return await self._parallel_search(
            query_list=query_list,
            retrieve_thread_num=retrieve_thread_num or 1,
            desc="Tavily Searching:",
            worker_factory=worker_factory,
        )

    async def retriever_zhipuai_search(
        self,
        query_list: List[str],
        top_k: Optional[int] | None = 5,
        retrieve_thread_num: Optional[int] | None = 1,
    ) -> Dict[str, List[List[str]]]:

        zhipuai_api_key = os.environ.get("ZHIPUAI_API_KEY", "")
        if not zhipuai_api_key:
            err_msg = (
                "ZHIPUAI_API_KEY environment variable is not set. "
                "Please set it to use ZhipuAI."
            )
            app.logger.error(err_msg)
            raise ToolError(err_msg)

        retrieval_url = "https://open.bigmodel.cn/api/paas/v4/web_search"
        headers = {
            "Authorization": f"Bearer {zhipuai_api_key}",
            "Content-Type": "application/json",
        }

        session = aiohttp.ClientSession()

        async def worker_factory(idx: int, q: str):
            retries, delay = 3, 1.0
            for attempt in range(retries):
                try:
                    payload = {
                        "search_query": q,
                        "search_engine": "search_std",  # [search_std, search_pro, search_pro_sogou, search_pro_quark]
                        "search_intent": False,
                        "count": top_k,  # [10,20,30,40,50]
                        "search_recency_filter": "noLimit",  # [oneDay, oneWeek, oneMonth, oneYear, noLimit]
                        "content_size": "medium",  # [medium, high]
                    }
                    async with session.post(
                        retrieval_url, json=payload, headers=headers
                    ) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        results: List[Dict[str, Any]] = data.get("search_result", [])
                        psg_ls: List[str] = [(r.get("content") or "") for r in results]
                        # Respect top_k
                        return idx, (psg_ls[:top_k] if top_k is not None else psg_ls)
                except (aiohttp.ClientError, Exception) as e:
                    warn_msg = f"[zhipuai][retry {attempt+1}] failed (idx={idx}): {e}"
                    app.logger.warning(warn_msg)
                    await asyncio.sleep(delay)
            return idx, []

        try:
            return await self._parallel_search(
                query_list=query_list,
                retrieve_thread_num=retrieve_thread_num or 1,
                desc="ZhipuAI Searching:",
                worker_factory=worker_factory,
            )
        finally:
            await session.close()


if __name__ == "__main__":
    Retriever(app)
    app.run(transport="stdio")
