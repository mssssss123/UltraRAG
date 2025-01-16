from .base import BaseLLM
from llama_cpp import Llama
from typing import Dict, List


class LlamacppLLMServer(BaseLLM):
    def __init__(self, model_path, max_token=32000, verbose=False, **kargs) -> None:
        super().__init__()
        self.kargs = kargs
        self.model = Llama(model_path=model_path, chat_format="chatml", verbose=verbose, n_ctx=max_token)


    def run(self, messages: List[Dict[str, str]], stream: bool=False, **kargs):
        messages = [messages] if not isinstance(messages, list) else messages
        response = self.model.create_chat_completion_openai_v1(
                messages=messages,
                stream=stream,
                **kargs
        )
        def chat_generator(response):
            for item in response:
                if item.choices[0].delta.content == None: continue
                yield item.choices[0].delta.content
        if stream:
            return chat_generator(response)
        else:
            return response.choices[0].message.content


    async def arun(self, messages: List[Dict[str, str]], stream: bool=False, **kargs):
        messages = [messages] if not isinstance(messages, list) else messages
        response = self.model.create_chat_completion_openai_v1(
                messages=messages,
                stream=stream,
                temperature=0.85,
                **kargs
        )
        async def chat_generator(response):
            for item in response:
                if item.choices[0].delta.content == None: continue
                yield item.choices[0].delta.content
        if stream:
            return chat_generator(response)
        else:
            return response.choices[0].message.content