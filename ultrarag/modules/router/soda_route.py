import json
from loguru import logger
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Protocol

@dataclass
class SodaRouterOutput:
    intent_type: str
    collection_name: str
    rag_enable: bool = False


class LLMCallable(Protocol):
    def __call__(self, model: str, messages: Dict[str, str], stream: bool, **kargs) -> str:
        ''' 大模型回调函数需要满足的格式
        '''
        ...


class SodaRouter:
    def __init__(self, chat_callback: LLMCallable, prompt_file: str, intent_config: str, **kargs) -> None:
        self.chat_callback = chat_callback
        self._model_name = kargs.get('model', "")
        
        if not Path(prompt_file).is_file():
            raise ValueError(f"param prompt_file is not an exist path: {prompt_file}")
        
        if not Path(intent_config).is_file():
            raise ValueError(f"param intent_config is not an exist path: {prompt_file}")
        
        with open(prompt_file, "r", encoding="utf8") as fr:
            self.prompt = "".join(fr.readlines())

        with open(intent_config, "r", encoding="utf8") as fr:
            self.intent_dict = json.load(fr)

        task_list_str = ""
        for key, val in self.intent_dict.items():
            task_list_str += f"任务 {val['option']}：{val['description']}\n---\n"
        
        self.label_map = {
            val["option"]: SodaRouterOutput(intent_type=key, rag_enable=val["rag_enable"], collection_name=val["collection_name"])
            for key, val in self.intent_dict.items()
        }

        self.route_prompt = self.prompt.replace("{task_list_str}", task_list_str)

        logger.info(f"{self.__class__.__name__} use prompt in {prompt_file}")
        logger.info(f"{self.__class__.__name__} use intent_config in {intent_config}")


    def run(self, query: str, is_course_select=False) -> str:
        if is_course_select:
            # TODO: 改成可配置的
            return self.label_map['c']

        request_data = self.route_prompt.replace("{query_str}", query)

        intent_label = self.chat_callback(
            messages=[{"role": "user", "content": request_data}],
            model=self._model_name,
            max_tokens=5,
            stream=False,
        )
        
        intent_label = intent_label if intent_label in self.label_map else 'z' # TODO: 改进下这个'z'
        logger.info(f"SodaRouter repsonse with {intent_label}, and intent is {self.label_map[intent_label]}")
        
        return self.label_map[intent_label]
