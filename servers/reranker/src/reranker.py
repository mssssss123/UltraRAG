import asyncio
import os
from urllib.parse import urlparse, urlunparse
from typing import Any, Dict, List, Optional

import aiohttp
from flask import Flask, jsonify, request
from infinity_emb import AsyncEngineArray, EngineArgs
from infinity_emb.log_handler import LOG_LEVELS, logger

from fastmcp.exceptions import ToolError
from ultrarag.server import UltraRAG_MCP_Server

retriever_app = Flask(__name__)
app = UltraRAG_MCP_Server("reranker")


class Reranker:
    def __init__(self, mcp_inst: UltraRAG_MCP_Server):
        mcp_inst.tool(
            self.reranker_init,
            output="reranker_path,infinity_kwargs,cuda_devices->None",
        )
        mcp_inst.tool(
            self.reranker_rerank,
            output="q_ls,ret_psg,top_k,query_instruction->rerank_psg",
        )
        mcp_inst.tool(
            self.rerank_deploy_service,
            output="rerank_url->None",
        )
        mcp_inst.tool(
            self.rerank_deploy_search,
            output="rerank_url,q_ls,ret_psg,top_k,query_instruction->rerank_psg",
        )

    async def reranker_init(
        self,
        reranker_path: str,
        infinity_kwargs: Optional[Dict[str, Any]] = None,
        cuda_devices: Optional[str] = None,
    ):
        app.logger.setLevel(LOG_LEVELS["warning"])

        if infinity_kwargs is None:
            infinity_kwargs = {}
        if cuda_devices is not None:
            assert isinstance(cuda_devices, str), "cuda_devices should be a string"
            os.environ["CUDA_VISIBLE_DEVICES"] = cuda_devices
        try:
            self.model = AsyncEngineArray.from_args(
                [EngineArgs(model_name_or_path=reranker_path, **infinity_kwargs)]
            )[0]
        except Exception as e:
            app.logger.error(f"Reranker initialization failed: {str(e)}")
            raise RuntimeError(f"Reranker initialization failed: {str(e)}")
        app.logger.info(f"Reranker initialized")

    async def reranker_rerank(
        self,
        query_list: List[str],
        passages_list: List[List[str]],
        top_k: int = 5,
        query_instruction: str = "",
    ) -> Dict[str, List[Any]]:

        assert (
            hasattr(self, "model") and self.model is not None
        ), "reranker model is not initialized"
        formatted_queries = [f"{query_instruction}{q}" for q in query_list]

        assert len(formatted_queries) == len(
            passages_list
        ), "queries and passages must have same length"

        async def rerank_single(query: str, docs: List[str]) -> List[str]:
            ranking, _ = await self.model.rerank(query=query, docs=docs, top_n=top_k)
            return [d.document for d in ranking]

        async with self.model:
            reranked_results = await asyncio.gather(
                *[
                    rerank_single(query, docs)
                    for query, docs in zip(formatted_queries, passages_list)
                ]
            )

        return {"rerank_psg": reranked_results}

    async def rerank_deploy_service(
        self,
        rerank_url: str,
    ):

        @retriever_app.route("/rerank", methods=["POST"])
        async def deploy_rerank_model():
            data = request.get_json()
            query_list = data["query_list"]
            passages_list = data["passages_list"]
            top_k = data["top_k"]

            async def rerank_single(query: str, docs: List[str]) -> List[str]:
                ranking, _ = await self.model.rerank(
                    query=query, docs=docs, top_n=top_k
                )
                return [d.document for d in ranking]

            async with self.model:
                reranked_results = await asyncio.gather(
                    *[
                        rerank_single(query, docs)
                        for query, docs in zip(query_list, passages_list)
                    ]
                )
            return jsonify({"rerank_psg": reranked_results})

        rerank_url = rerank_url.split(":")
        retriever_port = rerank_url[-1] if len(rerank_url) > 1 else 8080
        retriever_app.run(host=rerank_url[0], port=retriever_port)

        app.logger.info(f"employ embedding server at {rerank_url}")

    async def rerank_deploy_search(
        self,
        rerank_url: str,
        query_list: List[str],
        passages_list: List[List[str]],
        top_k: Optional[int] | None = None,
        query_instruction: str = "",
    ) -> Dict[str, List[Any]]:
        # Validate the URL format
        url = rerank_url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"http://{url}"
        url_obj = urlparse(url)
        api_url = urlunparse(url_obj._replace(path="/search"))
        app.logger.info(f"Calling url:{rerank_url}")

        if isinstance(query_list, str):
            query_list = [query_list]
        query_list = [f"{query_instruction}{query}" for query in query_list]

        payload = {
            "query_list": query_list,
            "passages_list": passages_list,
            "top_k": top_k,
        }

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
                    err_msg = f"Failed to call {rerank_url} with code {response.status}"
                    app.logger.error(err_msg)
                    raise ToolError(err_msg)


provider = Reranker(app)

if __name__ == "__main__":
    app.run(transport="stdio")
