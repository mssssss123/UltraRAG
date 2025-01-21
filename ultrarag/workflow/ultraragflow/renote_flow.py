import sys
from loguru import logger
from typing import Dict, List, Generator
from pathlib import Path
home_path = Path().resolve()
sys.path.append(home_path.as_posix())

from ultrarag.modules.llm import BaseLLM, OpenaiLLM
from ultrarag.modules.router import BaseRouter
from ultrarag.modules.embedding import BGEClient
from ultrarag.modules.database import BaseIndex, QdrantIndex
from ultrarag.modules.renote import ReNote
from ultrarag.common.utils import load_prompt, chunk_by_sentence, GENERATE_PROMPTS


class RenoteFlow:
    def __init__(self, api_key, base_url, llm_model, embed_model, database_url=":memory:", **args) -> None:
        """
        Initialize RenoteFlow with necessary components.
        
        Args:
            api_key: API key for LLM service
            base_url: Base URL for LLM service
            llm_model: Name of the LLM model
            embed_model: Path or URL to the embedding model
            database_url: URL for vector database, defaults to in-memory
        """
        self._synthesizer = OpenaiLLM(api_key=api_key, base_url=base_url, model=llm_model)
        self._router = BaseRouter(llm_call_back=self._synthesizer.arun, 
                                intent_list=[{"intent": "retriever", "description": "检索知识库"}])
        self._index = QdrantIndex(database_url, encoder=BGEClient(url_or_path=embed_model))
        
        self._renote = ReNote(
            retriever=self._index.search, 
            generator=self._synthesizer.arun
        )
        self.prompt = GENERATE_PROMPTS
    

    @classmethod
    def from_modules(cls, llm: BaseLLM, database: BaseIndex, **args):
        """
        Create an instance of RenoteFlow using provided LLM and database.
        
        Args:
            llm (BaseLLM): Language model instance
            database (BaseIndex): Database instance
        """
        inst = RenoteFlow(api_key="", base_url="", llm_model="", embed_model="")
        inst._synthesizer = llm
        inst._router = BaseRouter(llm_call_back=llm.arun, intent_list=[{"intent": "retriever", "description": "检索知识库"}])
        inst._index = database

        inst._renote = ReNote(
            retriever=inst._index.search, 
            generator=inst._synthesizer.arun
        )
        inst.prompt = GENERATE_PROMPTS
        return inst
    

    async def ingest(self, file_path: str, collection_name: str):
        """
        Ingest documents into the vector database.
        
        Args:
            file_path: Path to the document file
            collection_name: Name of the collection to store documents
        """
        if not file_path:
            logger.warning(f"no found file_path when ingest")
            return
        
        if not collection_name:
            logger.warning(f"no found collection_name when ingest")
            return

        documents = open(file_path, "r", encoding="utf8").read()
        chunks = chunk_by_sentence(documents)

        await self._index.create(collection_name)
        await self._index.insert(collection_name, chunks)
        logger.info(f'finish ingest file {file_path} into {collection_name} with {len(chunks)} chunks')


    async def aquery(self, query: str, messages: List[Dict[str, str]], collection, system_prompt=""):
        """
        Process queries and generate responses based on intent classification.
        
        Args:
            query: User's input query
            messages: Chat history in message format
            collection: Collection name for knowledge retrieval
            system_prompt: Optional system prompt for response generation
            
        Returns:
            Generator or None: Response stream if query is valid
        """
        if not query: return None

        route = await self._router.arun(query, messages)

        if not route.get("intent", None): return None
        
        if route.get("intent") == 'retriever':
            self._renote._system_prompt = system_prompt
            return self._renote.arun(query=query, collection=collection)
    
        if route.get('intent') == 'chat':
            new_messages = messages + [{"role": "user", "content": query}]
            return await self._synthesizer.arun(messages=new_messages, stream=True)