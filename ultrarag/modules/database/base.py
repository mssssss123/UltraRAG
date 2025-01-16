from pydantic import BaseModel
from typing import Any, Dict, List
from abc import ABC, abstractmethod

class BaseSchema(BaseModel):
    idx: int
    content: str

    def dump(self) -> Dict:
        return self.model_dump()

    @classmethod
    def load(cls, data: Dict[str, Any]):
        return cls(**data)

class BaseNode(BaseModel):
    # idx: int | str
    score: float | None
    content: Any
    # payload: Dict

    def dump(self) -> Dict:
        return self.model_dump()

    @classmethod
    def load(cls, data: Dict[str, Any]):
        return cls(**data)



class BaseIndex(ABC):
    url: str
    encoder: Any

    @abstractmethod
    def create(self, collection_name: str, schema: BaseSchema, **kargs):
        pass
    

    @abstractmethod
    def insert(self, collection: str, data: List[BaseSchema]):
        pass

    
    @abstractmethod
    async def search(self, collection: str, query: str, **kargs):
        pass

    
    @abstractmethod
    async def remove(self, collection):
        pass