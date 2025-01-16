import warnings
from loguru import logger
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

class BaseRerank(ABC):    
    async def rerank(self, query: str, nodes: List[Any], func):
        if not isinstance(query, str):
            raise ValueError(f"query in rerank not a str: \n{query}")
        
        if not isinstance(nodes, list):
            raise ValueError(f"nodes in rerank is not in list! \n{nodes}")
        
        if query == "":
            warnings.warn("rerank input query is empty")
        
        if any([item == "" for item in nodes]):
            warnings.warn("rerank input document exist empty str")

        if not nodes:
            warnings.warn("rerank input document is empty list")
            return [], []

        documnets = [func(item) for item in nodes]
        
        if not all([isinstance(item, str) for item in documnets]):
            raise ValueError(f"nodes in rerank not are all str! \n{documnets}")

        scores = await self.scoring(query, documnets)
        
        if len(scores) != len(nodes):
            raise ValueError("scores length is not same with nodes")
        
        logger.debug(f"reranker score before sorting: {scores}")
        scores_sorted, nodes_sorted = [], []
        try:
            for score, node in sorted(zip(scores, nodes), key=lambda x: x[0], reverse=True):
                scores_sorted.append(score)
                nodes_sorted.append(node)
        except:
            logger.error(f"reranker score is {len(scores)} {len(nodes)}")

        return scores_sorted, nodes_sorted


    @abstractmethod
    async def scoring(self, query: str, documnets: List[str]) -> List[float]:
        raise NotImplementedError("scoring function has not implemented!")

    
    def run_server(self, url):
        raise NotImplementedError("run_server Not implement!")

