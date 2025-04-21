from pydantic import BaseModel
from typing import Any, Dict, List, Callable, Union
from abc import ABC, abstractmethod


class BaseNode(BaseModel):
    # idx: int | str
    score: float | None     # query and content similarity score
    content: Any            # the content will be used generate vector
    payload: Dict | None    # schema of the data

    def dump(self) -> Dict:
        return self.model_dump()

    @classmethod
    def load(cls, data: Dict[str, Any]):
        return cls(**data)


class BaseIndex(ABC):
    url: str
    encoder: Any

    @abstractmethod
    async def create(self, collection_name: str, **kargs):
        """
        Create a new collection in the index.
        Args:
            collection_name (str): Name of the collection to create
            **kargs: Additional keyword arguments for collection creation
        Returns:
            None
        """
        raise NotImplementedError("create method not implemented")
    

    @abstractmethod
    async def insert(
        self, collection: str, 
        payloads: List[Dict[str, Any]], 
        func: Callable=lambda x: x,
        callback: Callable=None,   
        **kargs 
    ):
        """
        Insert data into the specified collection in the index.

        Args:
            collection (str): Collection name to insert data into
            payloads (List[Dict[str, Any]]): List of payload dictionaries to insert
            func (Callable, optional): Preprocessing function applied to data before insertion.
            Defaults to identity function (lambda x: x)
            callback (Callable, optional): Progress callback function to monitor insertion.
            Defaults to None
            **kargs: Additional keyword arguments for insertion operation

        Returns:
            None
        """
        raise NotImplementedError("insert method not implemented")

    
    @abstractmethod
    async def search(self, 
        collection: Union[List[str], str], 
        query: str, 
        topn: int=5, 
        **kargs
    ):
        '''
        Asynchronously search through specified collection(s) based on a query.
        Args:
            collection (Union[List[str], str]): Name of collection or list of collection names to search in
            query (str): The search query string
            topn (int, optional): Number of top results to return. Defaults to 5.
            **kargs: Additional keyword arguments for the search
        Returns:
            Abstract method that needs to be implemented by subclasses
        '''
        raise NotImplementedError("search method not implemented")        

    
    @abstractmethod
    async def remove(self, collection):
        '''
        Asynchronously remove a collection from the index.
        Args:
            collection (str): Name of the collection to remove
        Returns:
            None
        '''
        raise NotImplementedError("remove method not implemented")
    

    @abstractmethod
    async def get_collection(self) -> List[str]:
        '''
        Asynchronously retrieve a list of all collections in the index.
        Returns:
            List[str]: List of collection names
        '''
        raise NotImplementedError("get_collection method not implemented")  