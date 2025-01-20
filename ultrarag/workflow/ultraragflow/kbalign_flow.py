import sys
from loguru import logger
from typing import Dict, List, Generator
from pathlib import Path
home_path = Path().resolve()
sys.path.append(home_path.as_posix())

from ultrarag.modules.llm import BaseLLM, OpenaiLLM
from ultrarag.modules.router import BaseRouter
from ultrarag.modules.embedding import EmbClient
from ultrarag.modules.database import BaseIndex, QdrantIndex
from ultrarag.modules.kbalign import KBAlign
from ultrarag.common.utils import GENERATE_PROMPTS


class KBAlignFlow:
    def __init__(self, api_key, base_url, llm_model, embed_model, database_url=":memory:", **args) -> None:
        """
        Initialize KBAlignFlow with necessary components.
        
        Args:
            api_key (str): API key for OpenAI
            base_url (str): Base URL for API endpoint
            llm_model (str): Name of the LLM model to use
            embed_model (str): Path or URL to embedding model
            database_url (str): URL for database connection
            **args: Additional arguments
        """
        # self._weather = Weather()
        self._synthesizer = OpenaiLLM(api_key=api_key, base_url=base_url, model=llm_model)
        self._router = BaseRouter(llm_call_back=self._synthesizer.arun, intent_list=[{"intent": "retriever", "description": "检索知识库"}])
        self._index = QdrantIndex(database_url, encoder=EmbClient(url_or_path=embed_model))
        
        self._kbalign = KBAlign(
            retriever=self._index.search, 
            generator=self._synthesizer.arun,
        )
        self.prompt = GENERATE_PROMPTS
    

    @classmethod
    def from_modules(cls, llm: BaseLLM, database: BaseIndex, **args):
        """
        Create an instance of KBAlignFlow using provided LLM and database.
        
        Args:
            llm (BaseLLM): Language model instance
            database (BaseIndex): Database instance
            **args: Additional arguments
        """
        inst = KBAlignFlow(api_key="", base_url="", llm_model="", embed_model="")
        inst._synthesizer = llm
        inst._router = BaseRouter(llm_call_back=llm.arun, intent_list=[{"intent": "retriever", "description": "检索知识库"}])
        inst._index = database

        inst._kbalign = KBAlign(
            retriever=inst._index.search, 
            generator=inst._synthesizer.arun
        )
        inst.prompt = GENERATE_PROMPTS
        return inst

    async def aquery(self, query: str, messages: List[Dict[str, str]], collection, system_prompt=""):
        """
        Asynchronously process a query through the workflow.

        Args:
            query (str): User input query
            messages (List[Dict[str, str]]): Chat history
            collection: Target collection for retrieval
            system_prompt (str): System prompt to guide response generation

        Returns:
            Generator or None: Response stream or None if query is empty or routing fails
        """
        if not query: return None

        route = await self._router.arun(query, messages)

        if not route.get("intent", None): return None
 
        if route.get("intent") == 'retriever':
            self._kbalign._system_prompt = system_prompt
            return self._kbalign.arun(query=query, collection=collection,messages=messages,topn=8)
    
        if route.get('intent') == 'chat':
            new_messages = messages + [{"role": "user", "content": query}]
            return await self._synthesizer.arun(messages=new_messages, stream=True)
        