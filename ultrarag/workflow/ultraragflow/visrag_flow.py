import fitz
import inspect
import warnings
from loguru import logger
from PIL import Image
from pathlib import Path
from typing import Callable
from ultrarag.common.utils import get_image_md5
from ultrarag.modules.database import BaseIndex, QdrantIndex
from ultrarag.modules.llm import BaseLLM, HuggingFaceServer
from ultrarag.modules.embedding import BaseEmbedding, VisRAGNetServer

class VisRagFLow:
    def __init__(self, embed_model: str, llm_model: str, database_url: str):
        """
        Initialize VisRagFlow with required components.
        
        Args:
            embed_model (str): Name or path of the embedding model
            llm_model (str): Name or path of the language model
            database_url (str): URL for vector database connection
        """
        pass
        # if embed_model and llm_model:
        #     self._embed_model = VisRAGNetServer(embed_model,)
        #     self._database = QdrantIndex(database_url, encoder=self._embed_model)
        #     self._llm = HuggingFaceServer(llm_model, device="cuda:1")
        # else:
        #     warnings.warn("some init args is empty")


    @classmethod
    def from_modules(cls, llm_model: BaseLLM, database: BaseIndex):
        """
        Alternative constructor that creates VisRagFlow from pre-configured modules.
        Useful for sharing common modules across multiple flows.
        
        Args:
            llm_model (BaseLLM): Language model instance
            database (BaseIndex): Vector database instance
            
        Returns:
            VisRagFlow: Configured instance
        """
        instance = cls(None, None, None)
        instance._database = database
        instance._llm = llm_model

        return instance


    async def insert(self, pdf_path: str, collection: str, collection_path: str, call_func: Callable=None):
        """
        Process PDF document and insert extracted images into the database.
        
        Args:
            pdf_path (str): Path to the PDF file
            collection (str): Name of the vector database collection
            collection_path (str): Path to store extracted images
            call_func (Callable, optional): Callback function for progress updates [0.0, 1.0]
            
        Returns:
            Response from database insertion
        """
        await self._database.create(collection, 2304)
        docs = fitz.open(pdf_path)
        images_path_list = []

        # save page images
        for idx, page in enumerate(docs):
            pix = page.get_pixmap(dpi=200)
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            cache_image_path = Path(collection_path) / f"{collection}-{get_image_md5(image.tobytes())}.png"
            image.save(cache_image_path.as_posix())
            images_path_list.append(cache_image_path.as_posix())
            if call_func: call_func(idx / len(docs), "convert to image")

        # insert the data into the database
        resp = await self._database.insert(collection, data=images_path_list, callback=call_func)
        return resp
    

    async def aquery(self, query: str, collection: str, messages: list):
        """
        Process multimodal query through RAG pipeline.
        
        Args:
            query (str): User query
            collection (str): Name of the collection to search
            messages (list): Conversation history
            
        Yields:
            dict: Contains state ('recall' or 'answer') and response values
        """
        recalls = await self._database.search(query=query, topn=1)
        messages = [{"role": "user", "content": [query, *[item.content for item in recalls]]}]
        yield dict(state="recall", value=[item.content for item in recalls])
        resp = await self._llm.arun(messages=messages, stream=True)
        
        if inspect.isgenerator(resp):
            for item in resp:
                item = item['data']
                yield dict(state="answer", value=item)
        if inspect.isasyncgen(resp):
            async for item in resp:
                item = item['data']
                yield dict(state="answer", value=item)
