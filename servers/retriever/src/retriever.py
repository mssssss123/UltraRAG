import os
from urllib.parse import urlparse, urlunparse
from typing import Any, Dict, List, Optional

import requests
import aiohttp
import asyncio
import jsonlines
import numpy as np
import pandas as pd
from tqdm import tqdm
from flask import Flask, jsonify, request
from PIL import Image

from fastmcp.exceptions import NotFoundError, ToolError, ValidationError
from ultrarag.server import UltraRAG_MCP_Server
from pathlib import Path

app = UltraRAG_MCP_Server("retriever")
retriever_app = Flask(__name__)


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
            self.retriever_deploy_service,
            output="retriever_url->None",
        )
        mcp_inst.tool(
            self.retriever_deploy_search,
            output="retriever_url,q_ls,top_k,query_instruction->ret_psg",
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
    
    def _normalize_gpu_ids(self, gpu_ids) -> None:
        if gpu_ids is None:
            return
        if isinstance(gpu_ids, int):
            val = str(gpu_ids)
        elif isinstance(gpu_ids, (list, tuple)):
            val = ",".join(str(x) for x in gpu_ids if str(x).strip())
        elif isinstance(gpu_ids, str):
            val = ",".join([p.strip() for p in gpu_ids.split(",") if p.strip()])
        else:
            raise TypeError("gpu_ids must be str | int | list | tuple, e.g. '0', 0 or [0,1]")
        os.environ["CUDA_VISIBLE_DEVICES"] = val
        self.gpu_ids = gpu_ids

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
            err_msg = "faiss is not installed. Please install it with `conda install -c pytorch faiss-cpu` or `conda install -c pytorch faiss-gpu`."
            app.logger.error(err_msg)
            raise ImportError(err_msg)

        self.faiss_use_gpu = faiss_use_gpu
        self.backend = backend.lower()
        self.batch_size = int(batch_size)

        self.backend_configs = backend_configs or {}
        cfg = self.backend_configs.get(self.backend, {}) or {}

        if gpu_ids is not None:
            self._normalize_gpu_ids(gpu_ids)
        
        if self.backend == "infinity":
            try:
                from infinity_emb import AsyncEngineArray, EngineArgs
            except ImportError:
                err_msg = "infinity_emb is not installed. Please install it with `pip install infinity-emb`."
                app.logger.error(err_msg)
                raise ImportError(err_msg)
            
            self.model = AsyncEngineArray.from_args(
                [EngineArgs(model_name_or_path=model_name_or_path, batch_size=self.batch_size, **cfg)]
            )[0]
            
        elif self.backend == "sentencetransformers":
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError:
                err_msg = "sentence_transformers is not installed. Please install it with `pip install sentence-transformers torch`."
                app.logger.error(err_msg)
                raise ImportError(err_msg)
            
            self.st_encode_params = cfg.get("sentencetransformers_encode", {}) or {}
            st_params = self._drop_keys(cfg, banned=["sentencetransformers_encode"])
            
            self.model = SentenceTransformer(model_name_or_path=model_name_or_path, **st_params)
        
        elif self.backend == "openai":
            from openai import AsyncOpenAI, OpenAIError

            model_name = cfg.get("openai_model")
            api_base = cfg.get("api_base")
            api_key = cfg.get("api_key") or os.environ.get("RETRIEVER_API_KEY")

            if not model_name:
                raise ValueError("[openai] backend_configs.openai.openai_model is required")
            if not isinstance(api_base, str) or not api_base:
                raise ValueError("[openai] backend_configs.openai.api_base must be a non-empty string")
            if not isinstance(api_key, str) or not api_key:
                raise ValueError("[openai] api_key is required (or via env RETRIEVER_API_KEY)")
            
            try:
                self.model = AsyncOpenAI(base_url=api_base, api_key=api_key)
                self.openai_model = model_name 
                app.logger.info(f"OpenAI client initialized (model='{model_name}', base='{api_base}')")
            except OpenAIError as e:
                app.logger.error(f"Failed to initialize OpenAI client: {e}")
                raise
        else:
            raise ValueError(f"Unsupported backend: {backend}. Supported backends: 'infinity', 'sentencetransformers'")

        self.contents = []
        corpus_path_obj = Path(corpus_path)
        corpus_dir = corpus_path_obj.parent
        with jsonlines.open(corpus_path, mode="r") as reader:
            if not is_multimodal:
                for i, item in enumerate(reader):
                    if "contents" not in item:
                        raise ValueError(
                            f"Line {i}: missing key 'contents'. full item={item}"
                        )
                    self.contents.append(item["contents"])
            else:
                for i, item in enumerate(reader):
                    if "image_path" not in item:
                        raise ValueError(
                            f"Line {i}: missing key 'image_path'. full item={item}"
                        )
                    rel = str(item["image_path"])
                    abs_path = str((corpus_dir / rel).resolve())
                    self.contents.append(abs_path)

        self.faiss_index = None
        if index_path is not None and os.path.exists(index_path):
            cpu_index = faiss.read_index(index_path)

            if self.faiss_use_gpu:
                co = faiss.GpuMultipleClonerOptions()
                co.shard = True
                co.useFloat16 = True
                try:
                    self.faiss_index = faiss.index_cpu_to_all_gpus(cpu_index, co)
                    app.logger.info(f"Loaded index to GPU(s).")
                except RuntimeError as e:
                    app.logger.error(
                        f"GPU index load failed: {e}. Falling back to CPU."
                    )
                    self.faiss_use_gpu = False
                    self.faiss_index = cpu_index
            else:
                self.faiss_index = cpu_index
                app.logger.info("Loaded index on CPU.")

            app.logger.info(f"Retriever index path loaded successfully.")
        else:
            app.logger.info("No index_path provided. Retriever initialized without index.")
  

    async def retriever_embed(
        self,
        embedding_path: Optional[str] = None,
        overwrite: bool = False,
        is_multimodal: bool = False,
    ):
        embeddings = None
        
        if embedding_path is not None:
            if not embedding_path.endswith(".npy"):
                err_msg = f"Embedding save path must end with .npy, now the path is {embedding_path}"
                app.logger.error(err_msg)
                raise ValidationError(err_msg)
            output_dir = os.path.dirname(embedding_path)
        else:
            current_file = os.path.abspath(__file__)
            project_root = os.path.dirname(os.path.dirname(current_file))
            output_dir = os.path.join(project_root, "output", "embedding")
            embedding_path = os.path.join(output_dir, "embedding.npy")

        if not overwrite and os.path.exists(embedding_path):
            app.logger.info("embedding already exists, skipping")
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
                
                bs = max(1, int(getattr(self, "batch_size", 16)))
                n = len(data)
                pbar = tqdm(total=n, desc="Embedding (Infinity)")
                embeddings = []
                for i in range(0, n, bs):
                    chunk = data[i:i+bs]
                    vecs, _usage = await call(images=chunk) if is_multimodal else await call(sentences=chunk)
                    embeddings.extend(vecs)
                    pbar.update(len(chunk))
                pbar.close()
        
        elif self.backend == "sentencetransformers":
            device_param = self._to_st_device_list()  
            bs = int(getattr(self, "batch_size", 16))
            normalize = bool(
                self.st_encode_params.get("normalize_embeddings", False)
            )
            csz = int(self.st_encode_params.get("chunk_size", 10000))
            document_task = self.st_encode_params.get("document_task", None)

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
                            batch_size=bs,
                            chunk_size=csz,
                            show_progress_bar=True,
                            normalize_embeddings=normalize,
                            precision="float32",
                            task=document_task,
                        )
                    embeddings = await asyncio.to_thread(_encode_all)
                finally:
                    self.model.stop_multi_process_pool(pool)
            else:
                def _encode_single():
                    return self.model.encode(
                        data,
                        device=device_param,
                        batch_size=bs,
                        show_progress_bar=True,
                        normalize_embeddings=normalize,
                        precision="float32",
                        task=document_task,
                    )
                embeddings = await asyncio.to_thread(_encode_single)


        elif self.backend == "openai":
            if is_multimodal:
                raise ValueError("openai backend does not support image embeddings in this path.")

            bs = max(1, int(getattr(self, "batch_size", 16)))

            embeddings: list = []
            with tqdm(total=len(self.contents), desc="OpenAI Embedding", unit="item") as pbar:
                for start in range(0, len(self.contents), bs):
                    chunk = self.contents[start:start + bs]
                    resp = await self.model.embeddings.create(
                        model=self.openai_model,
                        input=chunk,
                    )
                    embeddings.extend([d.embedding for d in resp.data])
                    pbar.update(len(chunk))

        else:
            raise ValueError(f"Unsupported backend: {self.backend}")

        if embeddings is None:
            raise RuntimeError("Embedding generation failed: embeddings is None")
        embeddings = np.array(embeddings, dtype=np.float32)
        np.save(embedding_path, embeddings)
        app.logger.info("embedding success")
    
    def _to_st_device_list(self) -> str | list[str]:
        """
        Convert gpu_ids to SentenceTransformers device format:
        - None         -> "cuda" (or "cpu")
        - int / "0"    -> "cuda:0"
        - "0,1" / [0,1]-> ["cuda:0","cuda:1"]
        - If CUDA_VISIBLE_DEVICES="2,3", local process sees GPUs as 0/1
        """

        cd = getattr(self, "gpu_ids", None)
        if cd is None:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"

        if isinstance(cd, int):
            return f"cuda:{cd}"

        if isinstance(cd, str):
            parts = [p.strip() for p in cd.split(",") if p.strip()]
            return f"cuda:{parts[0]}" if len(parts) == 1 else [f"cuda:{i}" for i in range(len(parts))]

        if isinstance(cd, (list, tuple)):
            parts = [str(p).strip() for p in cd if str(p).strip()]
            return f"cuda:{parts[0]}" if len(parts) == 1 else [f"cuda:{i}" for i in range(len(parts))]

        raise TypeError("gpu_ids must be None, int, str, or list[int|str]")
    
    
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
            err_msg = "faiss is not installed. Please install it with `conda install -c pytorch faiss-cpu` or `conda install -c pytorch faiss-gpu`."
            app.logger.error(err_msg)
            raise ImportError(err_msg)

        if not os.path.exists(embedding_path):
            app.logger.error(f"Embedding file not found: {embedding_path}")
            raise NotFoundError(f"Embedding file not found: {embedding_path}")

        if index_path is not None:
            if not index_path.endswith(".index"):
                app.logger.error(
                    f"Parameter index_path must end with .index now is {index_path}"
                )
                ValidationError(
                    f"Parameter index_path must end with .index now is {index_path}"
                )
            output_dir = os.path.dirname(index_path)
        else:
            current_file = os.path.abspath(__file__)
            project_root = os.path.dirname(os.path.dirname(current_file))
            output_dir = os.path.join(project_root, "output", "index")
            index_path = os.path.join(output_dir, "index.index")

        if not overwrite and os.path.exists(index_path):
            app.logger.info("Index already exists, skipping")
            return

        os.makedirs(output_dir, exist_ok=True)

        embedding = np.load(embedding_path)
        dim = embedding.shape[1]
        vec_ids = np.arange(embedding.shape[0]).astype(np.int64)

        # with cpu
        cpu_flat = faiss.IndexFlatIP(dim)
        cpu_index = faiss.IndexIDMap2(cpu_flat)

        # chunk to write
        total = embedding.shape[0]
        app.logger.info(f"Start building FAISS index, total vectors: {total}")
        with tqdm(total=total, desc="Indexing (FAISS)", unit="vec") as pbar:
            for start in range(0, total, index_chunk_size):
                end = min(start + index_chunk_size, total)
                cpu_index.add_with_ids(embedding[start:end], vec_ids[start:end])
                pbar.update(end - start)
        
        # with gpu
        if self.faiss_use_gpu:
            co = faiss.GpuMultipleClonerOptions()
            co.shard = True
            co.useFloat16 = True
            try:
                gpu_index = faiss.index_cpu_to_all_gpus(cpu_index, co)
                index = gpu_index
                app.logger.info("Using GPU for indexing with sharding")
            except RuntimeError as e:
                app.logger.warning(f"GPU indexing failed ({e}); fall back to CPU")
                self.faiss_use_gpu = False
                index = cpu_index
        else:
            index = cpu_index

        # save
        faiss.write_index(cpu_index, index_path)

        if self.faiss_index is None:
            self.faiss_index = index

        app.logger.info("Indexing success")

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
                query_embedding, usage = await self.model.embed(sentences=queries)
        elif self.backend == "sentencetransformers":
            device_param = self._to_st_device_list()  
            bs = int(getattr(self, "batch_size", 16))
            normalize = bool(
                self.st_encode_params.get("normalize_embeddings", False)
            )
            query_task = self.st_encode_params.get("query_task", None)

            if isinstance(device_param, list) and len(device_param) > 1:
                pool = self.model.start_multi_process_pool()
                try:
                    def _encode_all():
                        return self.model.encode(
                            queries,
                            pool=pool,
                            batch_size=bs,
                            show_progress_bar=True,
                            normalize_embeddings=normalize,
                            precision="float32",
                            task=query_task,  
                        )
                    query_embedding = await asyncio.to_thread(_encode_all)
                finally:
                    self.model.stop_multi_process_pool(pool)
            else:
                def _encode_single():
                    return self.model.encode(
                        queries,
                        device=device_param,
                        batch_size=bs,
                        show_progress_bar=True,
                        normalize_embeddings=normalize,
                        precision="float32",
                        task=query_task,
                    )
                query_embedding = await asyncio.to_thread(_encode_single)
       
        elif self.backend == "openai":
            bs = max(1, int(getattr(self, "batch_size", 16)))
            query_embedding = []
            for i in tqdm(range(0, len(queries), bs), desc="Embedding (OpenAI: query)", unit="batch"):
                chunk = queries[i:i + bs]
                resp = await self.model.embeddings.create(model=self.openai_model, input=chunk)
                query_embedding.extend([d.embedding for d in resp.data])

        else:
            raise ValueError(f"Unsupported backend: {self.backend}")
        
        
        query_embedding = np.array(query_embedding, dtype=np.float32)
        app.logger.info("query embedding finish")

        scores, ids = self.faiss_index.search(query_embedding, top_k)
        rets = []
        for i, query in enumerate(query_list):
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
        import torch

        # Ensure that backend is Infinity (i.e., ColBERT/ColPali multi-vector)
        if getattr(self, "backend", None) != "infinity":
            raise ValueError(
                "retriever_search_colbert_maxsim only supports 'infinity' backend "
                "with ColBERT/ColPali multi-vector models. "
                "Use retriever_search or other backend-specific retrieval functions instead."
            )

        if isinstance(query_list, str):
            query_list = [query_list]
        queries = [f"{query_instruction}{query}" for query in query_list]

        # Encode queries -> expected shape (Q, Kq, D)
        async with self.model:
            query_embedding, usage = await self.model.embed(
                sentences=queries
            )  
        
        # Load document embeddings -> expected shape (N, Kd, D)
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
                )  # (N,Kd,D)
                docs_tensor = torch.from_numpy(stacked).to(device)
            except Exception:
                raise ValueError(
                    f"Document embeddings in {embedding_path} have inconsistent shapes, cannot stack into (N,Kd,D). "
                    f"Check your retriever_embed."
                )
        else:
            raise ValueError(
                f"Unexpected doc_embeddings format: type={type(doc_embeddings)}, shape={getattr(doc_embeddings, 'shape', None)}"
            )

        def _l2norm(t: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
            return t / t.norm(dim=-1, keepdim=True).clamp_min(eps)

        N, Kd, D_docs = docs_tensor.shape
        docs_tensor = _l2norm(docs_tensor)  
        k_pick = min(top_k, N)

        results = []
        for q_np in query_embedding:
            q = torch.as_tensor(q_np, dtype=torch.float32, device=device)  # Shape: (Kq, D)
            if q.shape[-1] != D_docs:
                raise ValueError(f"Dimension mismatch: query D={q.shape[-1]} vs doc D={D_docs}")
            q = _l2norm(q)  

            # MaxSim calculation:
            # sim[n, i, j] = dot(q[i], docs_tensor[n, j])
            # Result shape: (N, Kq, Kd)
            sim = torch.einsum("qd,nkd->nqk", q, docs_tensor)
            sim_max = sim.max(dim=2).values # Max over Kd -> shape (N, Kq)
            scores = sim_max.sum(dim=1)     # Sum over Kq -> shape (N,)


            top_idx = torch.topk(scores, k=k_pick, largest=True).indices.tolist()
            results.append([self.contents[i] for i in top_idx])

        return {"ret_psg": results}


    async def retriever_deploy_service(
        self,
        retriever_url: str,
    ):
        if getattr(self, "backend", None) != "infinity":
            raise ValueError("retriever_deploy_service is only supported when backend='infinity'")
        # Ensure URL is valid, adding "http://" prefix if necessary
        retriever_url = retriever_url.strip()
        if not retriever_url.startswith("http://") and not retriever_url.startswith(
            "https://"
        ):
            retriever_url = f"http://{retriever_url}"

        url_obj = urlparse(retriever_url)
        retriever_host = url_obj.hostname
        retriever_port = (
            url_obj.port if url_obj.port else 8080
        )  # Default port if none provided

        @retriever_app.route("/search", methods=["POST"])
        async def deploy_retrieval_model():
            data = request.get_json()
            query_list = data["query_list"]
            top_k = data["top_k"]
            async with self.model:
                query_embedding, _ = await self.model.embed(sentences=query_list)
            query_embedding = np.array(query_embedding, dtype=np.float16)
            _, ids = self.faiss_index.search(query_embedding, top_k)

            rets = []
            for i, _ in enumerate(query_list):
                cur_ret = []
                for _, id in enumerate(ids[i]):
                    cur_ret.append(self.contents[id])
                rets.append(cur_ret)
            return jsonify({"ret_psg": rets})

        retriever_app.run(host=retriever_host, port=retriever_port)
        app.logger.info(f"employ embedding server at {retriever_url}")

    async def retriever_deploy_search(
        self,
        retriever_url: str,
        query_list: List[str],
        top_k: Optional[int] | None = None,
        query_instruction: str = "",
    ):
        # Validate the URL format
        url = retriever_url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"http://{url}"
        url_obj = urlparse(url)
        api_url = urlunparse(url_obj._replace(path="/search"))
        app.logger.info(f"Calling url: {api_url}")

        if isinstance(query_list, str):
            query_list = [query_list]
        query_list = [f"{query_instruction}{query}" for query in query_list]

        payload = {"query_list": query_list}
        if top_k is not None:
            payload["top_k"] = top_k

        async with aiohttp.ClientSession() as session:
            async with session.post(
                api_url,
                json=payload,
            ) as response:
                if response.status == 200:
                    response_data = await response.json()
                    app.logger.debug(
                        f"status_code: {response.status}, response data: {response_data}"
                    )
                    return response_data
                else:
                    err_msg = (
                        f"Failed to call {retriever_url} with code {response.status}"
                    )
                    app.logger.error(err_msg)
                    raise ToolError(err_msg)

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
                        raise ToolError(
                            "Unauthorized (401): Invalid or missing EXA_API_KEY."
                        ) from e
                    app.logger.warning(
                        f"[Retry {attempt+1}] EXA failed (idx={idx}): {e}"
                    )
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
            raise MissingAPIKeyError(
                "TAVILY_API_KEY environment variable is not set. Please set it to use Tavily."
            )
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
                    app.logger.error(f"Usage limit exceeded: {e}")
                    raise ToolError(f"Usage limit exceeded: {e}") from e
                except InvalidAPIKeyError as e:
                    app.logger.error(f"Invalid API key: {e}")
                    raise ToolError(f"Invalid API key: {e}") from e
                except (BadRequestError, Exception) as e:
                    app.logger.warning(
                        f"[Retry {attempt+1}] Tavily failed (idx={idx}): {e}"
                    )
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
            raise ToolError(
                "ZHIPUAI_API_KEY environment variable is not set. Please set it to use ZhipuAI."
            )

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
                    app.logger.warning(
                        f"[Retry {attempt+1}] ZhipuAI failed (idx={idx}): {e}"
                    )
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
