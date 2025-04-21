import json
from elasticsearch import Elasticsearch, helpers
from typing import Any, Dict, List, Callable, Union, Optional

from .base import BaseIndex


class ESIndex(BaseIndex):
    def __init__(self, url: str):
        self._index = Elasticsearch(hosts=url, timeout=500)

    
    async def create(self, collection_name: str, **kargs):
        '''
        Create a new collection in the index.
        Args:
            collection_name (str): Name of the collection to create
            **kargs: Additional keyword arguments for collection creation
        Returns:
            None
        '''
        index_settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "content_analyzer": {  # 自定义分析器用于 content 字段
                            "type": "standard",  # 或者根据您的需求选择其他分析器
                            "tokenizer": "standard",
                            "filter": ["lowercase"]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "content": {
                        "type": "text",
                        "analyzer": "content_analyzer"  # 使用自定义分析器进行分词和检索
                    }
                },
                "dynamic_templates": [
                    {
                        "strings_as_keywords": {
                            "match_mapping_type": "string",
                            "mapping": {
                                "type": "keyword",
                                "index": False  # 默认情况下，所有字符串字段都不创建索引
                            }
                        }
                    }
                ]
            }
        }

        if not self._index.indices.exists(index=collection_name):
            response = self._index.indices.create(
                index=collection_name,
                body=index_settings,
                ignore=400
            )

            if response['acknowledged'] is False:
                raise ValueError(f"Failed to create collection {collection_name}: {response}")

        return True
    

    async def insert(
        self, collection: str, 
        payloads: List[Dict[str, Any]], 
        func: Callable=lambda x: x,
        callback: Callable = None,   
        **kargs 
    ):
        '''
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
        '''
        if not self._index.indices.exists(index=collection):
            raise ValueError(f"Collection {collection} does not exist.")
        
        batch_size = kargs.get("batch_size", 256)

        for idx in range(0, len(payloads), batch_size):
            batch_chunk = payloads[idx:idx + batch_size]
            batch_chunk = [dict(_index=collection, _source=item) for item in func(batch_chunk)]

            success, failed = helpers.bulk(self._index, batch_chunk, stats_only=True)
            if callback:
                callback()


    async def search(self,
        collection: Union[List[str], str], 
        query: str, 
        topn: int=5, 
        **kargs
    ):
        '''
        Search for documents in the specified collection.
        Args:
            collection (Union[List[str], str]): Collection name(s) to search in
            query (str): Search query string
            topn (int, optional): Number of top results to return. Defaults to 5.
            **kargs: Additional keyword arguments for search operation
        Returns:
            List[Dict]: List of search results
        '''
        if isinstance(collection, list):
            collection = ",".join(collection)
        
        response = self._index.search(
            index=collection,
            body={
                "query": {
                    "match": {
                        "content": query
                    }
                },
                "size": topn
            }
        )
        
        return response['hits']['hits']
    

    async def remove(self, collection: str):
        '''
        Remove a collection from the index.
        Args:
            collection (str): Name of the collection to remove
        Returns:
            None
        '''
        if self._index.indices.exists(index=collection):
            self._index.indices.delete(index=collection)


    async def get_collection(self):
        '''
        Get a list of all collections in the index.
        Returns:
            List[str]: List of collection names
        '''
        collections = self._index.indices.get_alias("*").keys()
        return list(collections)