import os, json
from pathlib import Path
from typing import Callable, List
from ultrarag.common.utils import GENERATE_PROMPTS
from loguru import logger

class KBAlign:
    def __init__(self, 
        retriever: Callable, 
        generator: Callable, 
        prompt_file: str="", 
        stream=True,
        system_prompt: str=None
    ) -> None:
        ''' args:
                system_prompt: string type and if not none, will add system_prompt at
                the head of answer phase.
        '''
        self._stream = stream
        if not callable(retriever):
            raise ValueError("retriever is not a function")

        if not callable(generator):
            raise ValueError("generator is not a function")

        self.retriever = retriever
        self.generator = generator
        self._system_prompt = system_prompt
        self.prompt = GENERATE_PROMPTS
        
    async def arun(self, query: str, collection, messages, topn: str):
        if query == "": 
            raise ValueError("query is empty")
        logger.info(f"strat find {collection} collection")
        top_docs = await self.retriever(query=query, topn=topn)
        yield dict(state="recall", value=[item.content for item in top_docs])
        content = "\n".join(
                    [f"{k+1}. {item}" for k, item in enumerate(top_docs)]
                )
        history = "\n".join([f"{his['role']}: {his['content']}" for his in messages])
        new_messages = self.prompt.format(query=query, history=history, content=content)
        new_messages = [{"role": "user", "content": new_messages}]
        response = await self.generator(new_messages)
        yield dict(state="first_answer", value=response)
        
        top_docs2 = await self.retriever(query=query+response, topn=topn)
        yield dict(state="query_expansion_recall", value=[item.content for item in top_docs2])
        
        content2 = "\n".join(
                    [f"{k+1}. {item}" for k, item in enumerate(top_docs2)]
                )
        history2 = "\n".join([f"{his['role']}: {his['content']}" for his in messages])
        new_messages2 = self.prompt.format(query=query, history=history2, content=content2)
        new_messages2 = [{"role": "user", "content": new_messages2}]
        final_answer = await self.generator(new_messages2, stream=self._stream)
        
        if self._stream:
            async for item in final_answer:
                yield dict(state="data", value=item)
        else:
            yield dict(state="data", value=final_answer)
            