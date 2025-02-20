import json
import torch
import aiohttp
import warnings
import traceback
from typing import Any, List, Dict
from transformers import AutoTokenizer, AutoModel, AutoConfig
from base import BaseEmbedding
from tqdm import tqdm
from openai import OpenAI, AsyncOpenAI
from loguru import logger
import tiktoken

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

class EmbClient(BaseEmbedding):
    def __init__(self, url_or_path, **kargs) -> None:
        super().__init__()
        self.url = url_or_path


    async def query_encode(self, query: str) -> List[float]:
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json={"text": [query]}, headers=HEADERS, timeout=10) as response:
                if response.status != 200:
                    raise ConnectionError(f"embedding api failed to visit with {response.status}")
                response_data = await response.json()
        if isinstance(response_data, dict):
            vector: list[float] = response_data.get("dense_embed", None)[0]
        else:
            vector = response_data[0]
            
        return {"dense_embed": vector}

    async def document_encode(self, document: List[str]) -> List[List[float]]:
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json={"text": document}, headers=HEADERS, timeout=200) as response:
                if response.status != 200:
                    raise ConnectionError(f"embedding api failed to visit with {response.status}")
                response_data = await response.json()
        if isinstance(response_data, dict):
            vector: list[float] = response_data.get("dense_embed", [])
        else:
            vector = response_data
        return [{"dense_embed": item} for item in vector]


    def encode(self, text: List[str]):
        return super().encode(text)
    

class EmbServer(BaseEmbedding):
    ''' 单节点部署场景，随RAG链路启动调用
        多节点部署场景，API调用此类
    '''
    def __init__(self, url_or_path, device=None, pooling:str="mean", query_instruction:str=None, batch_size = 8192, max_length: int = 512, **kargs) -> None:
        super().__init__(query_instruction)
        self.token = AutoTokenizer.from_pretrained(url_or_path, use_fast=False, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(url_or_path, trust_remote_code=True)
        self.device = self.model.device
        self.pooling = pooling

        # MiniCPM-Embedding-Light need query instruction
        architectures = AutoConfig.from_pretrained(url_or_path, trust_remote_code=True).architectures
        if "MiniCPMModel" in architectures:
            self.pooling = "mean"
            self.query_instruction = "Query: "
            

        if device == None:
            if torch.cuda.is_available():
                self.model = self.model.to('cuda').half()
                self.device = self.model.device
                if torch.cuda.device_count() > 1:
                    self.model = torch.nn.DataParallel(self.model)
            elif torch.backends.mps.is_available():
                self.model = self.model.to('mps').half()
                self.device = self.model.device
        else:
            if device.startswith('cuda') and torch.cuda.is_available():
                self.model = self.model.to(device).half()
                self.device = self.model.device
            elif device.startswith('mps') and torch.backends.mps.is_available():
                self.model = self.model.to(device).half()
                self.device = self.model.device
            elif device.startswith('cpu'):
                warnings.warn(f"device type {device} is not supported, use default cpu")
            else:
                self.device = 'cpu'
        
        self.batch_size: int = batch_size
        self.max_length: int = max_length

    @staticmethod
    def mean_pooling(model_output, attention_mask):
        token_embeddings = model_output
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size())
        sum_embeddings = torch.sum(token_embeddings.float() * input_mask_expanded, 1)
        sum_mask = input_mask_expanded.sum(1)
        return sum_embeddings / sum_mask

    async def query_encode(self, query: str | List[str], **kargs) -> List[float]:
        '''
        Encode a query string or list of query strings into embeddings.

        Args:
            query (str | List[str]): Input query text or list of query texts
            **kargs: Additional keyword arguments

        Returns:
            List[Dict]: List of dictionaries containing embeddings under 'dense_embed' key

        Example:
            >>> model = EmbServer("OpenBMB/MiniCPM-Embedding-Light")
            >>> embeddings = await model.query_encode("What is machine learning?")
            >>> print(embeddings)
            [{'dense_embed': [0.123, 0.456, ...]}]
        '''
        queries = query if isinstance(query, list) else [query]
        if self.query_instruction is not None:
            queries = [f"{self.query_instruction} {query}" for query in queries]
        vector = self.encode(queries)

        resp = [{"dense_embed": vec} for vec in vector]

        if isinstance(query, list):
            return resp
        else:
            return resp[0]

    
    async def document_encode(self, document: List[str], **kargs):
        '''
        Encode a list of document strings into embeddings.

        Args:
            document (List[str]): List of document texts to encode
            **kargs: Additional keyword arguments

        Returns:
            List[Dict]: List of dictionaries containing embeddings under 'dense_embed' key

        Example:
            >>> model = EmbServer("OpenBMB/MiniCPM-Embedding-Light")
            >>> docs = ["Machine learning is a subset of AI.", 
                       "Deep learning uses neural networks."]
            >>> embeddings = await model.document_encode(docs)
            >>> print(embeddings)
            [{'dense_embed': [0.123, 0.456, ...]}, 
             {'dense_embed': [0.789, 0.321, ...]}]
        '''
        if not isinstance(document, list) \
                or any([not isinstance(item, str) for item in document]):
            raise ValueError(f"document_encode input args is not List[str]: {document}")
        vector = self.encode(document)
        return [{"dense_embed": item} for item in vector]


    def encode(self, texts: list[str]) -> list[tuple[list[float] | None, dict[int | str, float] | None]]:
        '''
        Encode a list of texts into embeddings.

        Args:
            texts (list[str]): List of input texts to encode. Each text will be processed in batches
                             if the total length exceeds max_length.

        Returns:
            list[list[float]]: A list of embedding vectors, where each vector is a list of floats.
                              Shape: [batch_size, embedding_dimension]

        Example:
            >>> encoder = EmbServer("OpenBMB/MiniCPM-Embedding-Light")
            >>> texts = ["Hello world", "Machine learning is amazing"]
            >>> embeddings = encoder.encode(texts)
            >>> print(embeddings)
            [[0.123, 0.456, ...], [0.789, 0.012, ...]]
        '''
        vector_buff = []
        # 当batch size 过大的时候分批计算
        for pos in range(0, len(texts), self.batch_size):
            prein = self.token.batch_encode_plus(
                texts[pos: pos + self.batch_size], 
                padding="longest", 
                truncation=True, 
                max_length=self.max_length, 
                return_tensors="pt"
            ).to(self.device)

            with torch.no_grad():
                model_output = self.model(**prein)
                if self.pooling == "cls":
                    model_output = model_output[0][:, 0]
                elif self.pooling == "mean":
                    model_output = self.mean_pooling(model_output[0], prein['attention_mask'])
                vectors = torch.nn.functional.normalize(model_output, 2.0, dim=1)
                vector_buff.append(vectors.to('cpu'))
        vector_buff = torch.vstack(vector_buff)
  
        return vector_buff.tolist()
    
    
    def run_batch(self, texts: List[str]):
        return self.encode(texts)

class OpenAIEmbedding(BaseEmbedding):
    def __init__(self, model_name: str, api_key: str, base_url: str, query_instruction:str=None, batch_size = 1, max_length: int = 512, **kargs) -> None:
        super().__init__(query_instruction)
        self.batch_size: int = batch_size
        self.max_length: int = max_length
        self.max_retries = kargs.pop('max_retries', 3)
        self.kargs = kargs
        self.model_name = model_name
        self._generator = OpenAI(api_key=api_key, base_url=base_url)
        self._generator_async = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.tokenizer = tiktoken.encoding_for_model(model_name)
        logger.info(f"api_key: {api_key}, base_url: {base_url}, kargs: {kargs}")
    
    async def query_encode(self, query: str | List[str], **kargs) -> List[float]:
        '''
        Encode a query string or list of query strings into embeddings.

        Args:
            query (str | List[str]): Input query text or list of query texts
            **kargs: Additional keyword arguments

        Returns:
            List[Dict]: List of dictionaries containing embeddings under 'dense_embed' key

        Example:
            >>> model = EmbServer("OpenBMB/MiniCPM-Embedding-Light")
            >>> embeddings = await model.query_encode("What is machine learning?")
            >>> print(embeddings)
            [{'dense_embed': [0.123, 0.456, ...]}]
        '''
        queries = query if isinstance(query, list) else [query]
        if self.query_instruction is not None:
            queries = [f"{self.query_instruction} {query}" for query in queries]
        vector = await self.encode(queries)

        resp = [{"dense_embed": vec} for vec in vector]

        if isinstance(query, list):
            return resp
        else:
            return resp[0]

    
    async def document_encode(self, document: List[str], **kargs):
        '''
        Encode a list of document strings into embeddings.

        Args:
            document (List[str]): List of document texts to encode
            **kargs: Additional keyword arguments

        Returns:
            List[Dict]: List of dictionaries containing embeddings under 'dense_embed' key

        Example:
            >>> model = EmbServer("OpenBMB/MiniCPM-Embedding-Light")
            >>> docs = ["Machine learning is a subset of AI.", 
                       "Deep learning uses neural networks."]
            >>> embeddings = await model.document_encode(docs)
            >>> print(embeddings)
            [{'dense_embed': [0.123, 0.456, ...]}, 
             {'dense_embed': [0.789, 0.321, ...]}]
        '''
        if not isinstance(document, list) \
                or any([not isinstance(item, str) for item in document]):
            raise ValueError(f"document_encode input args is not List[str]: {document}")
        vector = await self.encode(document)
        return [{"dense_embed": item} for item in vector]


    async def encode(self, texts: list[str]) -> list[tuple[list[float] | None, dict[int | str, float] | None]]:
        '''
        Encode a list of texts into embeddings.

        Args:
            texts (list[str]): List of input texts to encode. Each text will be processed in batches
                             if the total length exceeds max_length.

        Returns:
            list[list[float]]: A list of embedding vectors, where each vector is a list of floats.
                              Shape: [batch_size, embedding_dimension]

        Example:
            >>> encoder = EmbServer("OpenBMB/MiniCPM-Embedding-Light")
            >>> texts = ["Hello world", "Machine learning is amazing"]
            >>> embeddings = encoder.encode(texts)
            >>> print(embeddings)
            [[0.123, 0.456, ...], [0.789, 0.012, ...]]
        '''
        vector_buff = []
        for pos in range(0, len(texts), self.batch_size):
            truncated_texts = [self.tokenizer.decode(self.tokenizer.encode(text)[:self.max_length]) for text in texts[pos: pos + self.batch_size]]
            for _ in range(self.max_retries):
                try:
                    response = await self._generator_async.embeddings.create(
                        model=self.model_name,
                        input=truncated_texts
                    )
                    for item in response.data:
                        vector_buff.append(torch.Tensor(item.embedding))
                    break
                except Exception as e:
                    logger.error(f"Failed to get embeddings: {e}, retrying...")
                    traceback.print_exc()
            
        vector_buff = torch.vstack(vector_buff)
  
        return vector_buff.tolist()
    

    
if __name__ == "__main__":
    import argparse
    from flask import Flask, request

    args = argparse.ArgumentParser()
    args.add_argument("-host", required=False, default="localhost", type=str, help="server url and port")
    args.add_argument("-port", required=False, default=10087, type=int, help="server url and port")
    args.add_argument("-model_path", required=True, type=str, help="server url and port")
    args = args.parse_args()

    embeder = EmbServer(args.model_path)

    app = Flask(__name__)
    @app.route('/embed', methods=['GET', 'POST'])
    def embed():
        data = request.json
        texts = data.get('texts', None)

        # TODO: batch flow implement
        embedding = embeder.encode(texts=texts)
        return json.dumps({"embedding": embedding})

    app.run(host=args.host, port=args.port, debug=True)