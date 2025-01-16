from pydantic import BaseModel
from typing import Any, Dict, List
from abc import ABC, abstractmethod

class BaseCite(ABC):
    
    @abstractmethod
    async def arun(self, repsponse: Any, reference: List[str]):
        pass