import sys, json
import asyncio, time
from loguru import logger
from typing import List, Dict
from ultrarag.modules.llm import BaseLLM, OpenaiLLM
from ultrarag.modules.router import BaseRouter
from ultrarag.modules.embedding import BGEClient
from ultrarag.modules.database import BaseIndex, QdrantIndex
from ultrarag.modules.reranker import BaseRerank, BGERerankClient
from ultrarag.modules.knowledge_managment.knowledge_managment import QdrantIndexSearchWarper
from ultrarag.common.utils import load_prompt, GENERATE_PROMPTS

from pathlib import Path
home_path = Path().resolve()
sys.path.append(home_path.as_posix())

class NativeFlow:
    def __init__(self, api_key, base_url, llm_model, embedding_url, reranker_url, database_url=":memory:", **args) -> None:
        self._synthesizer = OpenaiLLM(api_key=api_key, base_url=base_url, model=llm_model)
        self._router = BaseRouter(llm_call_back=self._synthesizer.arun, intent_list=[{"intent": "retriever", "description": "检索知识库"}])
        self._index = QdrantIndex(database_url, encoder=BGEClient(url_or_path=embedding_url))
        self._rerank = BGERerankClient(url=reranker_url)

        self.prompt = GENERATE_PROMPTS


    @classmethod
    def from_modules(cls, llm: BaseLLM, index: QdrantIndexSearchWarper, reranker: BaseRerank, **args):
        inst = NativeFlow(api_key="", base_url="", llm_model="", embedding_url="", reranker_url="")
        inst._synthesizer = llm
        inst._router = BaseRouter(llm_call_back=llm.arun, intent_list=[{"intent": "retriever", "description": "检索知识库"}])
        inst._index = index
        inst._rerank = reranker
        inst.prompt = GENERATE_PROMPTS
    
        return inst


    async def aquery(self, query: str, messages: List[Dict[str, str]], collection: List[str],system_prompt=""):
        logger.info(f"query: {query}")

        route = await self._router.arun(query=query, history_dialogue=messages)

        if not route.get("intent", None):
            raise ValueError("route output error")
        
        elif route.get("intent") == 'retriever':
            return self.naive_rag(query, collection, messages, system_prompt)
    
        elif route.get('intent') == 'chat':
            new_messages = messages + [{"role": "user", "content": query}]
            return await self._synthesizer.arun(messages=new_messages, stream=True)


    async def naive_rag(self, query, collection, messages, system_prompt=""):
        logger.info(f"strat find {collection} collection")
        recalls = await self._index.search(query=query, topn=25)
        scores, reranks = await self._rerank.rerank(query=query, nodes=recalls, func=lambda x: x.content)
        reranks = reranks[:5]

        yield dict(state="recall", value=[item.content for item in reranks])
        content = "\n".join([item.content for item in reranks])
        history = "\n".join([f"{his['role']}: {his['content']}" for his in messages])
        prompt = self.prompt.format(query=query, history=history, content=content)
        new_messages = []
        if system_prompt:
            new_messages = [{"role": "system", "content": system_prompt}]
        new_messages += [{"role": "user", "content": prompt}]
        response = await self._synthesizer.arun(messages=new_messages, stream=True)
        if isinstance(response,str):
            yield dict(state='data',value=response)
        else:
            async for item in response:
                yield dict(state='data',value=item)