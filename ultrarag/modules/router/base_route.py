import re, json
import traceback
from loguru import logger
from typing import Callable, List, Dict


class BaseRouter:
    prompt: str = ''' \
你是一个聪明的、思辨能力强的文字处理专家，现在给你以下几个工具选项，请你根据用户的对话历史，以及最后输入的问题，
请根据每一项的description，判断应当输出哪一个intent，你只需要输出 intent，不需要解释
{intent_list}

用户的对话历史：
{history_dialogue}

用户最后输出的问题：{query}
现在仅需要给出输出，请勿解释：
输出:
'''

    def __init__(self, llm_call_back: Callable, intent_list: Dict[str, str]) -> None:
        '''
        llm_call_back: llm call back function
        intent_list: format like:
        {
            "intent": "weather",
            "description": "查询天气",
        }
        '''
        if not callable(llm_call_back):
            raise ValueError(f'{llm_call_back} is not callable')
        
        self.llm_call_back = llm_call_back
        self.intent_list = intent_list
        if not intent_list:
            raise ValueError(f'intent_list is empty')
        self.intent_list_map = {item['intent']: item for item in intent_list}

    async def arun(self, query: str, history_dialogue: List[str]) -> dict:
        ''' query: e.g. "how are you?"
            history_dialogue: dialogue sort by time
        '''

        if len(self.intent_list) == 1:
            return self.intent_list[0]
        
        dialogue = [f"{item['role']}: {item['content']}" for item in history_dialogue]
        dialogue = "\n".join(dialogue)
        request_data = self.prompt.format(query=query, history_dialogue=dialogue, intent_list=self.intent_list)

        messages = [{'role': 'user', 'content': request_data}]
        response = await self.llm_call_back(messages, stream=False)
        logger.info(f"Router repsonse with {response}")
        
        try:
            return self.intent_list_map[response]
        except Exception as e:
            logger.warning(f"router output {response} error by {traceback.format_exc()}")
            return self.intent_list[0]
    