import traceback
from typing import List
from loguru import logger
from ultrarag.common.utils import timer_record
from ultrarag.modules.embedding import BaseEmbedding
from ultrarag.modules.database import BaseSchema, BaseIndex, BaseNode

from typing import Any, Dict, List, Tuple
from pymilvus import AnnSearchRequest, RRFRanker, Collection
from pymilvus import MilvusClient, DataType, Function, FunctionType
MAX_RETRY_COUNT = 3

class MilvusBM25Index(BaseIndex):
    def __init__(self, url: str, encoder: BaseEmbedding, **kargs) -> None:
        self.client = MilvusClient(uri=url)
        self.encoder = encoder


    def create(self, collection: str, schema: BaseSchema, **kargs):
        schema = self.client.create_schema()
        schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True, auto_id=True)
        schema.add_field(field_name="content", datatype=DataType.VARCHAR, max_length=1000, enable_analyzer=True)
        schema.add_field(field_name="sparse", datatype=DataType.SPARSE_FLOAT_VECTOR)

        bm25_function = Function(
            name="text_bm25_emb", # Function name
            input_field_names=["content"], # Name of the VARCHAR field containing raw text data
            output_field_names=["sparse"], # Name of the SPARSE_FLOAT_VECTOR field reserved to store generated embeddings
            function_type=FunctionType.BM25,
        )

        schema.add_function(bm25_function)

        index_params = self.client.prepare_index_params()

        index_params.add_index(
            field_name="sparse",
            index_type="AUTOINDEX", 
            metric_type="BM25"
        )

        self.client.create_collection(
            collection_name=collection, 
            schema=schema, 
            index_params=index_params
        )
        

    def insert(self, collection: str, data: List[str]):
        data = [dict(content=d) for d in data]
        self.client.insert(collection, data)


    async def search(self, collection: str, query: str, topn: int, **kargs):
        resp = self.client.search(
            collection_name=collection, 
            data=[query],
            anns_field='sparse',
            limit=topn,
            output_fields=['content'],
            search_params={'params': {'drop_ratio_search': 0.2}}
        )
        return resp
    

    async def remove(self, collection):
        pass