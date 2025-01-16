from openai import OpenAI, AsyncOpenAI
from .base import BaseLLM
from typing import Dict, List
import warnings
import traceback
from loguru import logger

class OpenaiLLM(BaseLLM):
    def __init__(self, api_key: str, base_url: str, **kargs) -> None:
        self.max_retries = kargs.pop('max_retries', 3)
        self.kargs = kargs
        self._generator = OpenAI(api_key=api_key, base_url=base_url)
        self._generator_async = AsyncOpenAI(api_key=api_key, base_url=base_url)

        logger.info(f"api_key: {api_key}, base_url: {base_url}, kargs: {kargs}")


    async def arun(self, messages: List[Dict[str, str]], stream: bool=False, **kargs):
        chat_kargs = self.kargs
        chat_kargs.update(kargs)

        if isinstance(messages, dict):
            if 'role' not in messages or 'content' not in messages:
                raise ValueError(f"messages iformat error: {messages}")
            messages = [messages]
        
        if not isinstance(messages, list):
            raise ValueError(f"messages is not list")

        async def chat_generator(messages):
            response = await self._generator_async.chat.completions.create(
                messages=messages,
                **chat_kargs,
                stream=True,
            )
            async for item in response:
                if item.choices[0].delta.content == None: continue
                yield item.choices[0].delta.content


        for retry in range(self.max_retries):
            try:
                if stream:
                    return chat_generator(messages=messages)
                else:
                    response = await self._generator_async.chat.completions.create(
                        messages=messages,
                        **chat_kargs,
                        stream=False,
                    )
                    return response.choices[0].message.content
            except:
                warnings.warn(f"retry {retry}: {traceback.format_exc()}")
        
        raise RuntimeError(f"failed with {self.max_retries} times")
            