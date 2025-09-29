import asyncio
import logging
import os
from typing import Any, Dict, List, Union, Optional

from openai import AsyncOpenAI, AuthenticationError
from openai._utils._logs import httpx_logger
from tqdm import tqdm
import base64
import mimetypes

from fastmcp.exceptions import ToolError
from ultrarag.server import UltraRAG_MCP_Server

app = UltraRAG_MCP_Server("generation")
httpx_logger.setLevel(logging.WARNING)


class Generation:
    def __init__(self, mcp_inst: UltraRAG_MCP_Server):
        mcp_inst.tool(
            self.generation_init,
            output="backend_configs,sampling_params,backend->None",
        )
        mcp_inst.tool(
            self.generate,
            output="prompt_ls,system_prompt->ans_ls",
        )
        mcp_inst.tool(
            self.multimodal_generate,
            output="multimodal_path,prompt_ls,system_prompt->ans_ls",
        )
        mcp_inst.tool(
            self.vllm_shutdown,
            output="->None",
        )

    def _drop_keys(self, d: Dict[str, Any], banned: List[str]) -> Dict[str, Any]:
        return {k: v for k, v in (d or {}).items() if k not in banned and v is not None}

    def _extract_text_prompts(
        self, prompt_ls: List[Union[str, Dict[str, Any]]]
    ) -> List[str]:
        prompts = []
        for m in prompt_ls:
            if hasattr(m, "content") and hasattr(m.content, "text"):
                prompts.append(m.content.text)
            elif isinstance(m, dict):
                if (
                    "content" in m
                    and isinstance(m["content"], dict)
                    and "text" in m["content"]
                ):
                    prompts.append(m["content"]["text"])
                elif "content" in m and isinstance(m["content"], str):
                    prompts.append(m["content"])
                elif "text" in m:
                    prompts.append(m["text"])
                else:
                    raise ValueError(f"Unsupported dict prompt format: {m}")
            elif isinstance(m, str):
                prompts.append(m)
            else:
                raise ValueError(f"Unsupported message format: {m}")
        return prompts

    def _to_data_url(self, path_or_url: str) -> str:
        s = str(path_or_url).strip()

        if s.startswith(("http://", "https://", "data:image/")):
            return s

        if not os.path.isfile(s):
            raise FileNotFoundError(f"image not found: {s}")
        mime, _ = mimetypes.guess_type(s)
        mime = mime or "image/jpeg"
        with open(s, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime};base64,{b64}"

    def generation_init(
        self,
        backend_configs: Dict[str, Any],
        sampling_params: Dict[str, Any],
        backend: str = "vllm",
    ) -> None:

        self.backend = backend.lower()
        self.backend_configs = backend_configs or {}
        cfg: Dict[str, Any] = (self.backend_configs.get(self.backend) or {}).copy()

        if self.backend == "vllm":
            try:
                from vllm import LLM, SamplingParams
            except ImportError:
                err_msg = (
                    "vllm is not installed. Please install it with `pip install vllm`."
                )
                app.logger.error(err_msg)
                raise ImportError(err_msg)

            gpu_ids = str(cfg.get("gpu_ids"))

            os.environ["CUDA_VISIBLE_DEVICES"] = gpu_ids
            os.environ.setdefault("VLLM_WORKER_MULTIPROC_METHOD", "spawn")

            model_name_or_path = cfg.get("model_name_or_path")

            vllm_pass_cfg = self._drop_keys(
                cfg,
                banned=["gpu_ids", "model_name_or_path"],
            )
            vllm_sampling_params = self._drop_keys(
                sampling_params,
                banned=["chat_template_kwargs"],
            )
            vllm_pass_cfg["tensor_parallel_size"] = len(gpu_ids.split(","))
            self.chat_template_kwargs = sampling_params.get("chat_template_kwargs", {})

            self.model = LLM(model=model_name_or_path, **vllm_pass_cfg)
            self.sampling_params = SamplingParams(**vllm_sampling_params)

        elif self.backend == "openai":
            self.model_name = cfg.get("model_name")
            if not self.model_name:
                error_msg = "model_name is required for openai backend"
                app.logger.error(error_msg)
                raise ValueError(error_msg)

            base_url = cfg.get("base_url")
            if not base_url:
                base_url = "https://api.openai.com/v1"
                warn_msg = f"base_url is not set, default to {base_url}"
                app.logger.warning(warn_msg)

            api_key = cfg.get("api_key") or os.environ.get("LLM_API_KEY")
            if not api_key:
                api_key = "None"
                warn_msg = "api_key is not set, default to None"
                app.logger.warning(warn_msg)

            self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)

            self.chat_template_kwargs = sampling_params.get("chat_template_kwargs", {})
            openai_sampling_params = self._drop_keys(
                sampling_params, banned=["chat_template_kwargs"]
            )
            extra_body = {}
            if "top_k" in openai_sampling_params:
                extra_body["top_k"] = openai_sampling_params["top_k"]
            if self.chat_template_kwargs:
                extra_body["chat_template_kwargs"] = self.chat_template_kwargs
            if extra_body:
                openai_sampling_params["extra_body"] = extra_body
            self.sampling_params = openai_sampling_params

            self._max_concurrency = int(cfg.get("concurrency", 1))
            self._retries = int(cfg.get("retries", 3))
            self._base_delay = float(cfg.get("base_delay", 1.0))

        elif self.backend == "hf":
            try:
                from transformers import AutoTokenizer, AutoModelForCausalLM
            except ImportError:
                err_msg = "transformers is not installed. Please install it with `pip install transformers`."
                app.logger.error(err_msg)
                raise ImportError(err_msg)

            gpu_ids = str(cfg.get("gpu_ids"))
            os.environ["CUDA_VISIBLE_DEVICES"] = gpu_ids

            model_name_or_path = cfg.get("model_name_or_path")
            hf_pass_cfg = self._drop_keys(
                cfg,
                banned=["gpu_ids", "model_name_or_path", "batch_size"],
            )
            hf_sampling_params = self._drop_keys(
                sampling_params, banned=["chat_template_kwargs"]
            )
            self.chat_template_kwargs = sampling_params.get("chat_template_kwargs", {})
            self.sampling_params = hf_sampling_params
            self.batch_size = int(cfg.get("batch_size", 1))

            self.model = AutoModelForCausalLM.from_pretrained(
                model_name_or_path,
                device_map="auto",
                **hf_pass_cfg,
            )
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name_or_path,
                padding_side="left",
            )
            added_tokens = 0
            if self.tokenizer.pad_token is None:
                if self.tokenizer.eos_token is not None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                else:
                    added_tokens = self.tokenizer.add_special_tokens(
                        {"pad_token": "[PAD]"}
                    )

            if added_tokens > 0 and hasattr(self.model, "resize_token_embeddings"):
                self.model.resize_token_embeddings(len(self.tokenizer))
        else:
            err_msg = f"Unsupported backend: {self.backend}"
            app.logger.error(err_msg)
            raise ValueError(err_msg)

    async def _generate(
        self,
        msg_ls: List[List[Dict[str, str]]],
    ) -> List[str]:

        if self.backend == "vllm":
            outputs = self.model.chat(
                msg_ls,
                self.sampling_params,
                chat_template_kwargs=self.chat_template_kwargs,
            )
            ret = [o.outputs[0].text for o in outputs]

        elif self.backend == "openai":
            sem = asyncio.Semaphore(self._max_concurrency)

            async def call_with_retry(
                idx,
                msg,
                client,
                model_name,
                sampling_params,
                retries: int,
                base_delay: float,
            ):

                import random
                from openai import RateLimitError, APIStatusError

                delay = base_delay
                for attempt in range(retries):
                    try:
                        async with sem:
                            resp = await client.chat.completions.create(
                                model=model_name,
                                messages=msg,
                                **sampling_params,
                            )
                        return idx, (resp.choices[0].message.content or "")
                    except AuthenticationError as e:
                        raise ToolError(
                            f"Unauthorized (401): Access denied at {getattr(client, 'base_url', 'unknown')}."
                            " Invalid or missing LLM_API_KEY."
                        ) from e
                    except RateLimitError as e:
                        app.logger.warning(
                            f"[429] Rate limited (idx={idx}, attempt={attempt+1}): {e}"
                        )
                    except APIStatusError as e:
                        if 500 <= e.status_code < 600:
                            app.logger.warning(
                                f"[{e.status_code}] Server error (idx={idx}, attempt={attempt+1}): {e}"
                            )
                        else:
                            raise
                    except Exception as e:
                        app.logger.warning(
                            f"[Retry {attempt+1}] Failed (idx={idx}): {e}"
                        )

                    await asyncio.sleep(delay + random.random() * 0.25)
                    delay *= 2

                return idx, "[ERROR]"

            tasks = [
                asyncio.create_task(
                    call_with_retry(
                        i,
                        m,
                        self.client,
                        self.model_name,
                        self.sampling_params,
                        retries=getattr(self, "_retries", 3),
                        base_delay=getattr(self, "_base_delay", 1.0),
                    )
                )
                for i, m in enumerate(msg_ls)
            ]
            ret = [None] * len(msg_ls)

            for coro in tqdm(
                asyncio.as_completed(tasks), total=len(tasks), desc="Generating: "
            ):
                idx, ans = await coro
                ret[idx] = ans

        elif self.backend == "hf":
            prompt_txt_ls: List[str] = []
            for msg in msg_ls:
                prompt_txt = self.tokenizer.apply_chat_template(
                    msg,
                    tokenize=False,
                    add_generation_prompt=True,
                    **self.chat_template_kwargs,
                )
                prompt_txt_ls.append(prompt_txt)

            device = self.model.device
            bs = self.batch_size

            ret: List[str] = []
            for i in tqdm(range(0, len(prompt_txt_ls), bs), desc="HF Generating"):
                batch_prompts = prompt_txt_ls[i : i + bs]
                enc = self.tokenizer(
                    batch_prompts,
                    return_tensors="pt",
                    padding=True,
                ).to(device)

                generated = self.model.generate(
                    **enc,
                    use_cache=False,
                    **self.sampling_params,
                )

                input_lens = enc["attention_mask"].sum(dim=1).tolist()
                for row_idx, in_len in enumerate(input_lens):
                    out_ids = generated[row_idx, int(in_len) :].tolist()
                    text = self.tokenizer.decode(out_ids, skip_special_tokens=True)
                    ret.append(text)

        else:
            raise ValueError(f"Unsupported backend: {self.backend}")

        return ret

    async def generate(
        self,
        prompt_ls: List[Union[str, Dict[str, Any]]],
        system_prompt: str = "",
    ) -> Dict[str, List[str]]:
        prompts = self._extract_text_prompts(prompt_ls)
        msg_ls: List[List[Dict[str, str]]] = []
        for p in prompts:
            msgs = []
            if system_prompt:
                msgs.append({"role": "system", "content": system_prompt})
            msgs.append({"role": "user", "content": p})
            msg_ls.append(msgs)
        ret = await self._generate(msg_ls)
        return {"ans_ls": ret}

    async def multimodal_generate(
        self,
        multimodal_path: List[List[str]],
        prompt_ls: List[Union[str, Dict[str, Any]]],
        system_prompt: str = "",
    ) -> Dict[str, List[str]]:

        prompts = self._extract_text_prompts(prompt_ls)

        msg_ls: List[List[Dict[str, str]]] = []
        for i, p in enumerate(prompts):
            msgs = []
            if system_prompt:
                msgs.append({"role": "system", "content": system_prompt})

            content = []
            curr_path = multimodal_path[i]
            for mp in curr_path:
                try:
                    content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": self._to_data_url(mp)},
                        }
                    )
                except Exception as e:
                    app.logger.warning(f"[Image skip] idx={i}, path={mp}, err={e}")
                print(f"multimodal_path item: {mp}")
            content.append({"type": "text", "text": p})

            msgs.append({"role": "user", "content": content})
            msg_ls.append(msgs)

        ret = await self._generate(msg_ls)
        return {"ans_ls": ret}

    def vllm_shutdown(self) -> None:

        try:
            if getattr(self, "backend", None) != "vllm":
                app.logger.info("[vllm_shutdown] backend is not 'vllm'; skip.")
                return

            if getattr(self, "model", None) is None:
                app.logger.info("[vllm_shutdown] model is None; nothing to do.")
                return

            fn = getattr(self.model, "shutdown", None)
            if callable(fn):
                app.logger.info("[vllm_shutdown] calling self.model.shutdown()")
                fn()
            else:
                for path in ("llm_engine", "engine"):
                    eng = getattr(self.model, path, None)
                    if eng:
                        for attr in ("shutdown", "close", "terminate"):
                            f = getattr(eng, attr, None)
                            if callable(f):
                                app.logger.info(
                                    f"[vllm_shutdown] calling self.model.{path}.{attr}()"
                                )
                                f()
                                break

            self.model = None
            import gc, torch

            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()

            app.logger.info("[vllm_shutdown] complete")

        except Exception as e:
            app.logger.warning(f"[vllm_shutdown] cleanup warning: {e}")


if __name__ == "__main__":
    Generation(app)
    app.run(transport="stdio")
