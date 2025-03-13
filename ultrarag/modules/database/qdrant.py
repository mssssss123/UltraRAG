import hashlib
from pathlib import Path
from loguru import logger
from typing import List, Callable, Dict, Any, Union
from ultrarag.modules.embedding import BaseEmbedding
from ultrarag.modules.database import BaseIndex, BaseNode

from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams

class QdrantIndex(BaseIndex):
    def __init__(self, url: str, encoder: BaseEmbedding) -> None:
        super().__init__()
        self.encoder = encoder

        # 判断是否为URL
        is_url = url.lstrip().startswith(('http://', 'https://', 'grpc://', ':memory:'))
        if is_url:
            # 如果是URL,使用location参数
            self.client = QdrantClient(location=url)
        elif Path(url).exists():
            # 如果是本地路径,使用path参数
            self.client = QdrantClient(path=url)
        else:
            raise ValueError(f"bad value when create collection! url: {url}")


    async def create(self, collection_name: str, dimension: int=1024, index_type="dense", **kargs):
        if collection_name in self.get_collections():
            return
        if index_type == "dense":
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "dense": VectorParams(size=dimension, distance=Distance.DOT)
                }
            )
        elif index_type == "hybrid":
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "dense": models.VectorParams(size=dimension, distance=Distance.DOT)
                },
                sparse_vectors_config={
                    "sparse": models.SparseVectorParams()
                }
            )
        else:
            raise ValueError(f"bad value when create collection!")
        return collection_name


    async def insert(
            self, 
            collection, 
            payloads: List[Dict[str, Any]], 
            func: Callable=lambda x: x, 
            method="dense", 
            callback: Callable=None
    ) -> None:
        '''
        Insert data into Qdrant vector database.

        Args:
            collection: Collection name
            payloads: List of dictionaries containing data to insert
            func: Function to extract text content from payload
            method: Vector indexing method, either 'dense' or 'hybrid'
            callback: Callback function for insertion progress

        Returns:
            None

        Raises:
            ValueError: When input data format is invalid or embedding fails

        Example:
            >>> payloads = [
            ...     {"text": "This is document 1", "metadata": {"source": "doc1.txt"}},
            ...     {"text": "This is document 2", "metadata": {"source": "doc2.txt"}}
            ... ]
            >>> await qdrant.insert(
            ...     collection="my_collection",
            ...     payloads=payloads,
            ...     method="dense",
            ...     callback=lambda p,m: print(f"Progress: {p*100:.1f}%")
            ... )
            Progress: 50.0%
            Progress: 100.0%
        '''
        if not isinstance(payloads, List):
            raise ValueError("insert data format error")
        content = [func(item) for item in payloads]
        data_embedding = await self.encoder.document_encode(content)

        if len(data_embedding) != len(payloads):
            raise ValueError("insert embedding error")

        points = []
        curr, total = 0, len(payloads)
        for ctx, payload, embed in zip(content, payloads, data_embedding):
            payload = dict(content=payload) if isinstance(payload, str) else payload
            dense_embed = embed.get("dense_embed", None)
            sparse_embed = embed.get("sparse_embed", None)
            if "hybrid" == method:
                points.append(
                    models.PointStruct(
                        id=hashlib.md5(ctx.encode(encoding='utf-8')).hexdigest(), 
                        vector={
                            "dense": dense_embed,
                            "sparse": models.SparseVector(
                                indices=list(sparse_embed.keys()), 
                                values=list(sparse_embed.values())
                            ),
                        }, 
                        payload=payload
                    )
                )
            elif "dense" == method:
                points.append(
                    models.PointStruct(
                        id=hashlib.md5(ctx.encode(encoding='utf-8')).hexdigest(), 
                        vector={
                            "dense": dense_embed
                        }, 
                        payload=payload
                    )
                )
            else:
                raise ValueError("method not implment")
            
            curr += 1
            if callback: callback(curr / total, "insert into qdrant")

        return self.client.upsert(collection_name=collection, wait=True, points=points)


    async def search(self, collection: Union[List[str], str], query: str, topn=5, method="dense", **kargs):
        ''' refer to: https://qdrant.tech/articles/sparse-vectors/
        
        Search for similar documents in Qdrant collections using dense or hybrid retrieval.
        
        Args:
            collection (List[str] or str): Collection name(s) to search in
            query (str): Query text to search for
            topn (int, optional): Number of results to return. Defaults to 5
            method (str, optional): Search method, either "dense" or "hybrid". Defaults to "dense"
            **kargs: Additional keyword arguments
            
        Returns:
            List[BaseNode]: List of search results with content and relevance scores
            
        Example:
            >>> query = "What is machine learning?"
            >>> results = await search("my_collection", query, topn=3)
            >>> print(results[0].content) # Most relevant document
            >>> print(results[0].score)   # Relevance score
        '''
        collection = [collection] if isinstance(collection, str) else collection

        response_result = []

        for coll in collection:
            if not isinstance(coll, str): continue
            if not self.client.collection_exists(coll):
                logger.warning(f"qdrant search collection:<{coll}> is not exist!")
                continue

            query_embedding = await self.encoder.query_encode(query)
            if not isinstance(query_embedding, dict):
                raise ValueError(f"embedding protocol error!")
            
            dense_embed = query_embedding.get("dense_embed", None)
            sparse_embed = query_embedding.get("sparse_embed", None)

            if method == "hybrid":
                search_result = self.client.search_batch(
                    collection_name=coll,
                    requests=[
                        models.SearchRequest(
                            vector=models.NamedVector(
                                name="dense",
                                vector=dense_embed,
                            ),
                            limit=topn,
                            with_payload=True,
                        ),
                        models.SearchRequest(
                            vector=models.NamedSparseVector(
                                name="sparse",
                                vector=models.SparseVector(
                                    indices=sparse_embed.keys(),
                                    values=sparse_embed.values(),
                                ),
                            ),
                            limit=topn,
                            with_payload=True,
                        ),
                    ],
                )
                search_result = search_result[0]
                response_result.extend(
                    [
                        BaseNode(content=item.payload.get('content'), score=item.score, payload=item.payload) 
                        for item in search_result
                    ]
                )
            elif method == "dense":
                search_result = self.client.search_batch(
                    collection_name=coll,
                    requests=[
                        models.SearchRequest(
                            vector=models.NamedVector(
                                name="dense",
                                vector=dense_embed,
                            ),
                            limit=topn,
                            with_payload=True,
                        )
                    ]
                )
                search_result = search_result[0]
                response_result.extend(
                    [
                        BaseNode(content=item.payload.get('content'), score=item.score, payload=item.payload) 
                        for item in search_result
                    ]
                )
        
        return response_result

    def get_collections(self):
        collections = self.client.get_collections().collections
        collections = [item.name for item in collections]
        return collections

    def close(self):
        self.client.close()
        
    async def remove(self, collection):
        self.client.delete_collection(collection_name=collection)
