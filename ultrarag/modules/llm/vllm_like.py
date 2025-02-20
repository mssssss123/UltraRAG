from .base import BaseLLM
from typing import Any, Dict, List, Generator

import torch
import logging
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
logging.basicConfig(handlers=[logging.NullHandler()])

dtype_maping = dict(
    bfloat16=torch.bfloat16,
    float32=torch.float32,
    float16=torch.float16
)

class VllmServer(BaseLLM):
    def __init__(self, base_url: str, **kargs) -> None:
        tokenizer_mode = kargs.get("tokenizer_mode", "auto")
        dtype = kargs.get("dtype", "bfloat16")
        dtype = dtype_maping[dtype]
        gpu_memory_utilization = kargs.get("gpu_memory_utilization", 0.9)
        enforce_eager = kargs.get("enforce_eager", False)
        tensor_parallel_size = kargs.get("tensor_parallel_size", 1)
        self.sampling_params = kargs.get("sampling_params", None)

        self._generator = LLM(
            model=base_url,
            tokenizer_mode=tokenizer_mode,
            trust_remote_code=True,
            dtype=dtype,
            gpu_memory_utilization=gpu_memory_utilization,
            enforce_eager=enforce_eager,
            tensor_parallel_size=tensor_parallel_size
        )

        self._tokenizer = AutoTokenizer.from_pretrained(base_url, trust_remote_code=True)


    def run(self, messages, stream, **kargs):
        ''' TODO: 支持流式输出
        '''
        if kargs:
            sampling_params_dict = kargs
        elif self.sampling_params:
            sampling_params_dict = self.sampling_params
        else:
            sampling_params_dict = kargs
        
        
        params_dict = {
            "n": sampling_params_dict.get('n', 5),
            "best_of": sampling_params_dict.get('best_of', 5),
            "presence_penalty": sampling_params_dict.get('presence_penalty', 1.0),
            "frequency_penalty": sampling_params_dict.get('frequency_penalty', 0.0),
            "temperature": sampling_params_dict.get('temperature', 0.8),
            "top_p": sampling_params_dict.get('top_p', 0.8),
            "top_k": sampling_params_dict.get('top_k', -1),
            "stop": sampling_params_dict.get('stop', None),
            "stop_token_ids": sampling_params_dict.get('stop_token_ids', None),
            "ignore_eos": sampling_params_dict.get('ignore_eos', False),
            "max_tokens": sampling_params_dict.get('max_tokens', 1024),
            "logprobs": sampling_params_dict.get('logprobs', None),
            "prompt_logprobs": sampling_params_dict.get('prompt_logprobs', None),
            "skip_special_tokens": sampling_params_dict.get('skip_special_tokens', True),
        }

        sampling_params = SamplingParams(**params_dict)
                
        question_prompt = self._tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=False)
        print(question_prompt)
        resp = self._generator.generate(question_prompt, sampling_params=sampling_params)
        return resp[0].outputs[0].text
    

    async def arun(self, messages, stream: bool=False, **kargs):
        ''' TODO: 支持流式输出
        '''
        if kargs:
            sampling_params_dict = kargs
        elif self.sampling_params:
            sampling_params_dict = self.sampling_params
        else:
            sampling_params_dict = kargs
        
        params_dict = {
            "n": sampling_params_dict.get('n', 5),
            "best_of": sampling_params_dict.get('best_of', 5),
            "presence_penalty": sampling_params_dict.get('presence_penalty', 1.0),
            "frequency_penalty": sampling_params_dict.get('frequency_penalty', 0.0),
            "temperature": sampling_params_dict.get('temperature', 0.8),
            "top_p": sampling_params_dict.get('top_p', 0.8),
            "top_k": sampling_params_dict.get('top_k', -1),
            "stop": sampling_params_dict.get('stop', None),
            "stop_token_ids": sampling_params_dict.get('stop_token_ids', None),
            "ignore_eos": sampling_params_dict.get('ignore_eos', False),
            "max_tokens": sampling_params_dict.get('max_tokens', 1024),
            "logprobs": sampling_params_dict.get('logprobs', None),
            "prompt_logprobs": sampling_params_dict.get('prompt_logprobs', None),
            "skip_special_tokens": sampling_params_dict.get('skip_special_tokens', True),
        }

        sampling_params = SamplingParams(**params_dict)
                
        question_prompt = self._tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=False)
        print(question_prompt)
        resp = self._generator.generate(question_prompt, sampling_params=sampling_params)
        return resp[0].outputs[0].text
    
    
if __name__ == "__main__":
    import asyncio
    import argparse
    args = argparse.ArgumentParser()
    args.add_argument("-model", required=True, type=str, help="model path")
    args = args.parse_args()

    model = VllmServer(base_url=args.model)
    messages = [dict(role="user", content="你好")]
    resp = asyncio.run(model.arun(messages=messages))
    print(resp)