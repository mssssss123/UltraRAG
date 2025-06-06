import sys, json
import asyncio, time
from loguru import logger
from typing import List, Dict
from ultrarag.modules.llm import BaseLLM, OpenaiLLM
from ultrarag.modules.router import BaseRouter
from ultrarag.modules.embedding import EmbClient
from ultrarag.modules.database import BaseIndex, QdrantIndex
from ultrarag.modules.reranker import BaseRerank, RerankerClient
from ultrarag.modules.knowledge_managment.knowledge_managment import QdrantIndexSearchWarper
from ultrarag.modules.rankcot import RANKCOT_PROMPTS
from ultrarag.common.utils import format_view, GENERATE_PROMPTS

from pathlib import Path
home_path = Path().resolve()
sys.path.append(home_path.as_posix())

class RankCoTFlow:
    def __init__(self, api_key, base_url, llm_model, embedding_url, reranker_url, database_url=":memory:", **args) -> None:
        """
        Initialize the RankCoTFlow with required components.
        
        Args:
            api_key (str): API key for LLM service
            base_url (str): Base URL for LLM service
            llm_model (str): Name of the LLM model to use
            embedding_url (str): URL for embedding service
            reranker_url (str): URL for reranker service 
            database_url (str): URL for vector database, defaults to in-memory
        """
        self._synthesizer = OpenaiLLM(api_key=api_key, base_url=base_url, model=llm_model)
        self._router = BaseRouter(llm_call_back=self._synthesizer.arun, intent_list=[{"intent": "retriever", "description": "检索知识库"}])
        self._index = QdrantIndex(database_url, encoder=EmbClient(url_or_path=embedding_url))
        self._rerank = RerankerClient(url=reranker_url)

        self.prompt = GENERATE_PROMPTS

    @classmethod
    def from_modules(cls, llm: BaseLLM, index: QdrantIndexSearchWarper, **args):
        """
        Alternative constructor that creates RankCoTFlow from pre-configured modules.
        
        Args:
            llm (BaseLLM): Language model instance
            index (QdrantIndexSearchWarper): Vector database instance
        
        Returns:
            NaiveFlow: Configured instance
        """
        inst = RankCoTFlow(api_key="", base_url="", llm_model="", embedding_url="", reranker_url="")
        inst._synthesizer = llm
        inst._router = BaseRouter(llm_call_back=llm.arun, intent_list=[{"intent": "retriever", "description": "检索知识库"}])
        inst._index = index
        inst.prompt = GENERATE_PROMPTS
    
        return inst


    async def aquery(self, query: str, messages: List[Dict[str, str]], collection: List[str], system_prompt=""):
        """
        Main query method that routes requests to appropriate handlers.
        
        Args:
            query (str): User query
            messages (List[Dict]): Conversation history
            collection (List[str]): Knowledge base collections to search
            system_prompt (str): Optional system prompt
            
        Returns:
            AsyncGenerator: Yields response chunks with state information
        """
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
        """
        Implements RAG workflow: retrieval -> reranking -> generation.
        
        Args:
            query (str): User query
            collection (List[str]): Knowledge base collections to search
            messages (List[Dict]): Conversation history
            system_prompt (str): Optional system prompt
            
        Yields:
            Dict: Contains state ('recall' or 'data') and response values
        """
        logger.info(f"strat find {collection} collection")
        recalls = await self._index.search(query=query, topn=25)
        scores, reranks = await self._rerank.rerank(query=query, nodes=recalls, func=lambda x: x.content)
        reranks = reranks[:5]

        yield dict(state="recall", value=[item.content for item in reranks])
        content = "\n".join([item.content for item in reranks])
        history = "\n".join([f"{his['role']}: {his['content']}" for his in messages])

        cot_prompt = RANKCOT_PROMPTS["cot"].format(history=history, content=content, query=query)
        cot_messages = [{"role": "user", "content": cot_prompt}]
        cot_response = await self._synthesizer.arun(messages=cot_messages, stream=False)
        yield dict(state="cot", value=cot_response)

        answer_prompt = RANKCOT_PROMPTS["answer"].format(query=query, cot_response=cot_response)
        answer_messages = [{"role": "user", "content": answer_prompt}]
        final_response = await self._synthesizer.arun(messages=answer_messages, stream=True)

        if isinstance(final_response,str):
            yield dict(state='data',value=final_response)
        else:
            async for item in format_view(final_response):
                yield dict(state='data', value=item)