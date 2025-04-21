from typing import Any, Dict, List
from abc import ABC, abstractmethod


class BaseEmbedding(ABC):
    def __init__(self, query_instruction: str="", document_instruction: str=""):
        '''
        Args:
            query_instruction (str): Instruction for query encoding. 
                                It will be used to prefix the query for encoding
            document_instruction (str): Instruction for document encoding. 
                                It will be used to prefix the document for encoding
        '''

        self.query_instruction = query_instruction
        self.document_instruction = document_instruction

    @abstractmethod
    async def query_encode(self, query: str) -> List[float]:
        pass
    
    @abstractmethod
    async def document_encode(self, document: List[str]) -> List[List[float]]:
        pass
    
    def q_prefix(self, query: List[str]):
        '''
        prefix the query with the query instruction
        '''
        return [self.query_instruction + q if isinstance(q, str) else q for q in query]
    
    
    def d_prefix(self, document: List[str]):
        '''
        prefix the document with the document instruction
        '''
        return [self.document_instruction + d if isinstance(d, str) else d for d in document]        