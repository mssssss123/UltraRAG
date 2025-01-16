import os
import torch
from transformers import (
    AutoTokenizer,
)
from openai import OpenAI
from pathlib import Path
import sys
top_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(top_dir))
import json
import argparse
chat_parser = argparse.ArgumentParser("")
client = OpenAI()
from vllm import LLM,SamplingParams

def asking_api(
    content, cont_dics=None, temperature=0.1, top_p=0.9, model="gpt-4-1106-preview"
):
    if cont_dics is not None:
        messages = cont_dics
    else:
        messages = [{"role": "system", "content": content}]
    response = client.chat.completions.create(model=model,
    messages=messages,
    max_tokens=4096,
    stop=None,
    temperature=temperature,
    top_p=top_p)
    response_content = response.choices[0].message.content
    return response_content.strip()        
        
class ChatClass:
    def __init__(self, model_path="", tokenizer_path="", model_type="llama", system_prompt="Please response directly, without any unnecessary supplements", base_url="", api_key=""):
        self.llm = None
        self.model_type = model_type
        self.system_prompt = system_prompt
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, cache_dir=tokenizer_path)
        self.update_model(model_path, tokenizer_path)

    def update_model(self, model_path, tokenizer_path):
        """Update the model and tokenizer paths and reload the LLM instance."""
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        try:
            self.llm = LLM(self.model_path, gpu_memory_utilization=0.80, trust_remote_code=True,max_model_len=4096)
        except:
            self.llm = LLM(self.model_path, gpu_memory_utilization=0.50, trust_remote_code=True,max_model_len=4096)
            
    def vllm_model_chat(self, prompts, temperature=0.8, top_p=0.95, max_tokens=3000, use_beam_search=False, times=1):
        sampling_params = SamplingParams(temperature=temperature, top_p=top_p, max_tokens=max_tokens, use_beam_search=use_beam_search,skip_special_tokens=True)
        results = [self.generate_text(prompts, sampling_params) for _ in range(times)]
        return list(map(list, zip(*results)))

    def generate_text(self, prompts, sampling_params):
        """Generate text for each prompt using the configured LLM."""
        try:
            if isinstance(prompts, str):
                prompts = [prompts]
            prompt_chunks = [prompts[i:i+500] for i in range(0, len(prompts), 500)]
            outputs = []
            for chunk in prompt_chunks:
                if self.is_llama:
                    messages =  [[{"role": "system", "content":f"{self.system_prompt}"},{"role": "user", "content": c}] for c in chunk]
                    chunk = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                else:
                    prompt_template = "<用户>{}<AI>"
                    chunk =  [prompt_template.format(c.strip()) for c in chunk]
                chunk_output = self.llm.generate(chunk, sampling_params)
                outputs.extend([output.outputs[0].text.strip() for output in chunk_output])
            return outputs
        except Exception as e:
            print(f"Error during text generation: {str(e)}")
            return []