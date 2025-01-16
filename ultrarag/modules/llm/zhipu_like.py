import traceback
from loguru import logger
from .base import BaseLLM
from zhipuai import ZhipuAI
from typing import Dict, List, Generator
from zhipuai.core._errors import APIRequestFailedError

class ZhipuLLM(ZhipuAI, BaseLLM):
    def __init__(self, api_key: str, base_url: str, **kargs) -> None:
        ZhipuAI.__init__(self, api_key=api_key, base_url=base_url)
        self.max_retries = kargs.get("max_retries", 3)


    async def arun(self, messages: List[Dict[str, str]], stream: bool, **kargs) -> Generator | str:
        return self.run(messages=messages, stream=stream, **kargs)
   
    
    def run(self, messages: List[Dict[str, str]], stream: bool, **kargs) -> Generator | str:
        def stream_output(response):
            for chunk in response:
                status = chunk.choices[0].finish_reason
                content = chunk.choices[0].delta.content

                if "sensitive" == status:
                    raise RuntimeError("sensitive")
                yield content

        if stream:
            response = self.chat.completions.create(messages=messages, stream=stream, **kargs)
            return stream_output(response)
        else:
            for retry in range(self.max_retries):
                try:
                    response = self.chat.completions.create(messages=messages, stream=stream, **kargs)
                    return response.choices[0].message.content
                except APIRequestFailedError as err:
                    if '"code":"1301"' in str(err):
                        raise RuntimeError("sensitive")
                    else:
                        logger.info(f"retry {retry+1} time failed")
            raise RuntimeError(f"retry {self.max_retries} failed when request zhipu api because: \n \
                    {traceback.format_exc()}")


    