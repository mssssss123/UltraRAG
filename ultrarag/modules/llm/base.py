from typing import Dict, List, Union, Generator, AsyncGenerator

class BaseLLM:
    def run(self, messages: List[Dict[str, str]], stream: bool, **kargs) \
        -> Union[Generator, str]:
        ''' 大模型生成的请求过程处理
        '''
        raise NotImplementedError("base llm not implement chat function")


    async def arun(self, messages: List[Dict[str, str]], stream: bool=False, **kargs) \
        -> Union[AsyncGenerator, str]:
        ''' 调用大模型获得结果
            输入参数:
                messages: 标准输入格式为：[{'role': 'user', 'content': 'hello'}]
                stream: 是否为流式输出，默认为否
                kargs: 其他参数，用于透传
            输出格式：
                当"strem=True"时, AsyncGenerator
                当"strem=False"时, str
            举例说明：
            >>> model = BaseLLM()
            >>> await model.arun(messages=[dict(role="user", content="hello")])
            hello, I am LLM
        '''
        raise NotImplementedError("base llm not implement achat function")