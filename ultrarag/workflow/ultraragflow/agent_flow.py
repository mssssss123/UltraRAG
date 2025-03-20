import os
import json
from loguru import logger
from openai import OpenAI
from typing import List, Dict
from transformers import ReactCodeAgent, tool, Tool

class LLM:
    def __init__(self, api_key: str, model: str, base_url: str, summarize_past: bool = True):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url= base_url)
        self.summarize_past = summarize_past


    def __call__(self, 
        messages: List[Dict[str, str]], 
        stop_sequences: list[str] = '<end_action>') -> str:
        # logger.info(json.dumps(messages, ensure_ascii=False))
        if self.summarize_past and len(messages) > 4:
            past_observations = [m['content'] for m in messages[:-1]
                                 if ((m['role'] == 'tool-response') and not ("-> Error" in m['content']))]
            # remove print outputs string to save some tokens
            past_observations = "\n".join(past_observations).replace('Print outputs:\n', '')
            formatted_messages = [messages[0],
                                  messages[1],
                                  messages[-2],
                                  {"role": "user",
                                   "content": f"Output of the previous steps:\n {past_observations} \n\n"
                                              + messages[-1]['content']}]
        else:
            formatted_messages = messages.copy()
            for m in formatted_messages:
                if m['role'] == 'tool-response':
                    m['role'] = 'user'

        result = self.client.chat.completions.create(
            model=self.model, 
            messages=formatted_messages,
            stop=stop_sequences
        )
        return result.choices[0].message.content




# chater = LLM(api_key=os.getenv("GLM_KEY"), model="glm-4-0520", base_url=os.getenv("BASE_URL"))
# react_agent = ReactCodeAgent(system_prompt=SYSTEM_PROMPT, llm_engine=chater, tools=[search_agent_tool()])

# input_text = input("请输入你的问题：")
# while input_text != "exit":
#     answer = react_agent.run(input_text)
#     print(answer)
#     input_text = input("请输入你的问题：")


import sys, json
import asyncio, time
from loguru import logger
from typing import List, Dict
from ultrarag.modules.llm import BaseLLM, OpenaiLLM
from ultrarag.modules.router import BaseRouter
from ultrarag.modules.embedding import EmbClient
from ultrarag.modules.database import BaseIndex, QdrantIndex
from ultrarag.modules.reranker import BaseRerank, RerankerClient
from ultrarag.modules.knowledge_managment.knowledge_managment import QdrantIndexSearchWarper
from ultrarag.common import AGENT_SYSTEM_PROMPT

from pathlib import Path
home_path = Path().resolve()
sys.path.append(home_path.as_posix())


class AgentRAGFlow:
    def __init__(self, 
                api_key, 
                base_url, 
                llm_model, 
                embedding_url, 
                database_url=":memory:", 
                system_prompt: str = None, 
                **args
        ) -> None:
        """
        Initialize the NaiveFlow with required components.
        
        Args:
            api_key (str): API key for LLM service
            base_url (str): Base URL for LLM service
            llm_model (str): Name of the LLM model to use
            embedding_url (str): URL for embedding service
            database_url (str): URL for vector database, defaults to in-memory
        """
        self.prompt = system_prompt or AGENT_SYSTEM_PROMPT
        chater = LLM(api_key=api_key, model=llm_model, base_url=base_url)
        self._index = QdrantIndex(database_url, encoder=EmbClient(url_or_path=embedding_url))
        self._synthesizer = ReactCodeAgent(system_prompt=self.prompt, llm_engine=chater, tools=[self.search_agent_tool()])
    

    @classmethod
    def from_modules(cls, llm: BaseLLM, index: QdrantIndexSearchWarper, collection, system_prompt: str = None, **args):
        """
        Alternative constructor that creates NaiveFlow from pre-configured modules.
        
        Args:
            llm (BaseLLM): Language model instance
            index (QdrantIndexSearchWarper): Vector database instance
        
        Returns:
            NaiveFlow: Configured instance
        """
        inst = AgentRAGFlow(api_key="", base_url="", llm_model="", embedding_url="")
        inst._index = index
        inst.prompt = system_prompt or AGENT_SYSTEM_PROMPT
        chater = LLM(api_key=llm.api_key, model=llm.model, base_url=llm.base_url)
        inst._synthesizer = ReactCodeAgent(system_prompt=inst.prompt, llm_engine=chater, tools=[inst.search_agent_tool()])
        inst.collection = collection
        return inst


    async def aquery(self, query: str, system_prompt=""):
        """
        Main query method that routes requests to appropriate handlers.
        
        Args:
            query (str): User query
            messages (List[Dict]): Conversation history
            collection (List[str]): Knowledge base collections to search
            system_prompt (str): Optional system prompt
            
        Returns:
            AsyncGenerator: Yields response chunks with state information
        """
        logger.info(f"query: {query}")

        async def response():
            resp = self._synthesizer.run(task=query, stream=True)
            for item in resp:
                # logger.warning(f"item: {json.dumps(item, ensure_ascii=False)}")
                if isinstance(item, dict):continue
                yield dict(state='data', value=str(item))
        
        return response()

    
    def search_agent_tool(self) -> Tool:
        @tool
        def search_agent(query: str) -> str:
            """Use this tool to retrieve information relevant to the given query from Wikipedia. 
            Always print and inspect the output of this tool, do not parse its output using regex.
            If you already used this tool, and you didn't get the information you needed, 
            try calling it again with a more specific query.
            Args:
                query: The query to search for answer.
            Returns:
                str: The information retrieved.
            """
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._index.search(collection=self.collection, query=query))
            response = "\n\n ".join([item.content for item in response])
            return response

        return search_agent
