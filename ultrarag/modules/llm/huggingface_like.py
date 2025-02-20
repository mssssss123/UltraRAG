'''
This file implements inference deployment for Huggingface models, 
compatible with regular LLMs and CPM-V series models

HuggingfaceClient: Used to establish connection with microservices 
in microservice mode

HuggingfaceServer: Used for deploying microservices or in 
standalone mode
'''
import torch
import json
import aiohttp
from PIL import Image
from pathlib import Path
from typing import List, Dict
from transformers import AutoModel, AutoTokenizer
from .base import BaseLLM
from typing import List, Dict
from loguru import logger


class HuggingfaceClient(BaseLLM):
    def __init__(self, url_or_path: str) -> None:
        super().__init__()
        self._url = url_or_path

    
    async def arun(self, messages: List[Dict[str, str]], stream: bool, **kargs):
        """Connect to microservice, send requests and get responses.

        Args:
            messages (List[Dict[str, str]]): List of input messages
                Example: [
                    {"role": "user", "content": ["hello", "/path/to/image.jpg"]},
                    {"role": "assistant", "content": ["This is a landscape photo"]}
                ]
            stream (bool): Whether to use streaming output
                Example: True

        Returns:
            If stream=False, returns complete response:
                Example: {"data": "This is a beautiful landscape photo"}
            If stream=True, returns generator with incremental responses:
                Example: yield {"data": "This is"}
                         yield {"data": "a beautiful"}
                         yield {"data": "landscape photo"}
        """
        async def func(form_data):
            async with aiohttp.ClientSession() as session:
                async with session.post(self._url, data=form_data) as response:
                    if response.status == 200:
                        async for chunk in response.content.iter_any():
                            data = chunk.decode("utf8").strip("data:\n")
                            try:
                                yield eval(data)
                            except:
                                print(data)
                    else:
                        raise ConnectionError(f"请求失败，状态码：{response.status}，错误信息：{await response.text()}")
            
    
        form_data = aiohttp.FormData()
        json_data = dict(messages=messages, stream=stream)
        form_data.add_field('data', json.dumps(json_data), content_type='application/json')
        
        # 找到message中的图片，然后加载图片
        file_path = [cnt for msg in messages for cnt in msg['content']]
        # 过滤出字符串类型且长度小于1024的路径进行检查
        file_path = [path for path in file_path if isinstance(path, str) and len(path) < 1024]
        file_path = [path for path in file_path if Path(path).exists()]
        for path in file_path:
            form_data.add_field("images", open(path, "rb"), filename=path, content_type='image/jpeg')
        

        if not stream:
            async with aiohttp.ClientSession() as session:
                async with session.post(self._url, data=form_data) as response:
                    if response.status == 200:
                        resp = await response.json()
                        return resp
                    else:
                        raise ConnectionError(f"请求失败，状态码：{response.status}，错误信息：{await response.text()}")
        else:
            return func(form_data)


class HuggingFaceServer(BaseLLM):
    def __init__(self, model_path, device=None) -> None:
        self._model = AutoModel.from_pretrained(model_path, trust_remote_code=True)
        self._tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        if device:
            self._model.to(device)
        elif torch.cuda.is_available():
            self._model.cuda()
        

    async def arun(self, messages: List[Dict[str, str]], stream: bool, **kargs):
        """Run the model with messages and return the response.

        Args:
            messages (List[Dict[str, str]]): List of input messages
                Example: [
                    {"role": "user", "content": ["hello", "/path/to/image.jpg"]},
                    {"role": "assistant", "content": ["This is a landscape photo"]}
                ]
            stream (bool): Whether to use streaming output
                Example: True

        Returns:
            If stream=False, returns complete response:
                Example: {"data": "This is a beautiful landscape photo"}
            If stream=True, returns generator with incremental responses:
                Example: yield {"data": "This is"}
                         yield {"data": "a beautiful"}
                         yield {"data": "landscape photo"}
        """
        new_messages = []
        for msg in messages:
            role, content = msg["role"], msg['content']
            if isinstance(content, list):
                content = [Image.open(item) if len(item) < 256 and Path(item).exists() else item for item in content]
            new_messages.append(dict(role=role, content=content))

        if not stream:
            answer = self._model.chat(
                image=None,
                msgs=new_messages,
                tokenizer=self._tokenizer,
                stream=stream,
                sampling=True,
            )
            return {"data": answer}
        else:
            return self._stream_response(new_messages)


    def _stream_response(self, messages):
        answer = self._model.chat(
            image=None,
            msgs=messages,
            tokenizer=self._tokenizer,
            stream=True,
            sampling=True,
        )
        
        for item in answer:
            if not item: continue
            yield dict(data=item)


    def run(self, messages: List[Dict[str, str]], stream: bool, **kargs):
        """Run the model with a list of messages and return the response.

        Args:
            messages (List[Dict[str, str]]): List of input messages
                Each message contains role and content fields:
                - role: Message role, can be "user" or "assistant"
                - content: Message content, can be a list of text or image paths
                Example: [
                    {"role": "user", "content": ["hello", "/path/to/image.jpg"]},
                    {"role": "assistant", "content": ["This is a landscape photo"]}
                ]
            stream (bool): Whether to use streaming output
                True: Returns a generator that yields responses incrementally
                False: Returns complete response at once
                
        Returns:
            When stream=False:
                Returns complete response dict: {"data": "complete response text"}
            When stream=True:
                Returns generator yielding responses: {"data": "partial response text"}
        """
        def _chat(self, messages, stream=False):
            return self._model.chat(
                image=None,
                msgs=messages,
                tokenizer=self._tokenizer,
                stream=stream,
                sampling=True,
            )
        
        def stream_response():
            answer = _chat(self, messages, stream)
            for item in answer:
                if not item: continue
                data = dict(data=item)
                yield f"data:{data}\n\n"
                print(item, end="", flush=True)
        if stream:
            return stream_response()
        else:
            answer = _chat(self, messages)
            print(answer)
            return {"data": answer}