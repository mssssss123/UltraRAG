import sys
from loguru import logger
from typing import Dict, List, Generator
from pathlib import Path
home_path = Path().resolve()
sys.path.append(home_path.as_posix())

from ultrarag.modules.llm import BaseLLM, OpenaiLLM
# from ultrarag.modules.weather import Weather
from ultrarag.modules.router import BaseRouter
from ultrarag.modules.embedding import BGEClient
from ultrarag.modules.database import BaseIndex, QdrantIndex
from ultrarag.modules.kbalign import KBAlign
from ultrarag.common.utils import GENERATE_PROMPTS


class KBAlignFlow:
    def __init__(self, api_key, base_url, llm_model, embed_model, database_url=":memory:", **args) -> None:
        # self._weather = Weather()
        self._synthesizer = OpenaiLLM(api_key=api_key, base_url=base_url, model=llm_model)
        self._router = BaseRouter(llm_call_back=self._synthesizer.arun, intent_list=[{"intent": "retriever", "description": "检索知识库"}])
        self._index = QdrantIndex(database_url, encoder=BGEClient(url_or_path=embed_model))
        
        self._kbalign = KBAlign(
            retriever=self._index.search, 
            generator=self._synthesizer.arun,
        )
        self.prompt = GENERATE_PROMPTS
    

    @classmethod
    def from_modules(cls, llm: BaseLLM, database: BaseIndex, **args):
        inst = KBAlignFlow(api_key="", base_url="", llm_model="", embed_model="")
        # inst._weather = Weather()
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
        if not query: return None

        route = await self._router.arun(query, messages)

        if not route.get("intent", None): return None
        # if route.get("intent") == 'weather':
        #     city = route.get("args", '北京')
        #     weather_info = await self._weather.arun(city)
        #     content = self.prompt.format(query=query, history="", content=weather_info)
        #     message = {"role": "user", "content": content}
        #     return await self._synthesizer.arun(messages=message, stream=True) 
        
        if route.get("intent") == 'retriever':
            self._kbalign._system_prompt = system_prompt
            return self._kbalign.arun(query=query, collection=collection,messages=messages,topn=8)
    
        if route.get('intent') == 'chat':
            new_messages = messages + [{"role": "user", "content": query}]
            return await self._synthesizer.arun(messages=new_messages, stream=True)
        