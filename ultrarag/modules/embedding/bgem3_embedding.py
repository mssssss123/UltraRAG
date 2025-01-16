import json, aiohttp
from typing import Union, List, Dict
from .base import BaseEmbedding

import os, sys
import torch
from torch import nn, Tensor
import torch.distributed as dist
import numpy as np
from collections import defaultdict
from transformers import AutoModel, AutoTokenizer, is_torch_npu_available, AutoConfig
from loguru import logger
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

class BGEM3Client(BaseEmbedding):
    def __init__(self, url_or_path, **kargs) -> None:
        super().__init__()
        self.url = url_or_path

    async def query_encode(self, query: str) -> List[float]:
        '''
            input args:
                embedding_url: str, e.g: "http://127.0.0.1:10992/embed"
                segments: str, e.g "北京天气怎么样"
            output args:
                response: dict, e.g {"dense_embed": [0.1, 0.5, ... , 0.8], "sparse_embed": {1: 0.5, 2: 0.62}}
        '''
        if not isinstance(query, str):
            logger.error(f"input text {query} is not str")
            raise ValueError("bge embedding input error")
        
        post_parm = dict(
            model = 'default',
            text = query,
            return_dense = True,
            return_sparse = True,
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=post_parm, headers=HEADERS, timeout=10) as response:
                if response.status != 200:
                    raise ConnectionError(f"embedding api failed to visit\n {response.content}")
                r = await response.text()
                result = json.loads(r)[0]

        result['sparse_embed'] = {int(k): float(v) for k, v in result['sparse_embed'].items()}
        return result


    async def document_encode(self, document: List[str]):
        if isinstance(document, str):
            document = [document]
        
        post_parm = dict(
            model = 'default',
            text = document,
            return_dense = True,
            return_sparse = True,
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=post_parm, headers=HEADERS, timeout=10) as response:
                if response.status != 200:
                    raise ConnectionError(f"embedding api failed to visit\n {response.content}")
                r = await response.text()
                result = json.loads(r)

        response = dict(
            sparse_embed=[
                {int(k): float(v) for k, v in item['sparse_embed'].items()}
                for item in result
            ],
            dense_embed=[
                item['dense_embed'] for item in result
            ]
        )
        return result


    def encode(self, text: List[str]):
        return super().encode(text)



class BGEM3ForInference(nn.Module):
    def __init__(self,
                 model_name: str = None,
                 normlized: bool = True,
                 sentence_pooling_method: str = 'cls',
                 negatives_cross_device: bool = False,
                 temperature: float = 1.0,
                 enable_sub_batch: bool = True,
                 unified_finetuning: bool = True,
                 use_self_distill: bool = False,
                 colbert_dim: int = -1,
                 self_distill_start_step: int = -1,
                 ):
        super().__init__()
        self.load_model(model_name, colbert_dim=colbert_dim)
        self.vocab_size = self.model.config.vocab_size
        self.cross_entropy = nn.CrossEntropyLoss(reduction='mean')

        self.unified_finetuning = unified_finetuning
        if not self.unified_finetuning:
            self.colbert_linear = None
            self.sparse_linear = None

        self.normlized = normlized
        self.sentence_pooling_method = sentence_pooling_method
        self.enable_sub_batch = enable_sub_batch
        self.temperature = temperature
        self.use_self_distill = use_self_distill
        self.self_distill_start_step = self_distill_start_step

        self.step = 0
        if not normlized:
            self.temperature = 1.0
            logger.info("reset temperature = 1.0 due to using inner product to compute similarity")

        self.negatives_cross_device = negatives_cross_device
        if self.negatives_cross_device:
            if not dist.is_initialized():
                raise ValueError('Distributed training has not been initialized for representation all gather.')

            self.process_rank = dist.get_rank()
            self.world_size = dist.get_world_size()


    def load_model(self, model_name, colbert_dim: int = -1):
        if not os.path.exists(model_name):
            raise ValueError(f"model file not exist in {model_name}")

        self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

        self.colbert_linear = torch.nn.Linear(in_features=self.model.config.hidden_size,
                                              out_features=self.model.config.hidden_size if colbert_dim == -1 else colbert_dim)
        self.sparse_linear = torch.nn.Linear(in_features=self.model.config.hidden_size, out_features=1)

        if os.path.exists(os.path.join(model_name, 'colbert_linear.pt')) and os.path.exists(
                os.path.join(model_name, 'sparse_linear.pt')):
            logger.info('loading existing colbert_linear and sparse_linear---------')
            self.load_pooler(model_dir=model_name)
        else:
            logger.info(
                'The parameters of colbert_linear and sparse linear is new initialize. Make sure the model is loaded for training, not inferencing')


    def load_pooler(self, model_dir):
        colbert_state_dict = torch.load(os.path.join(model_dir, 'colbert_linear.pt'), map_location='cpu', weights_only=True)
        sparse_state_dict = torch.load(os.path.join(model_dir, 'sparse_linear.pt'), map_location='cpu', weights_only=True)
        self.colbert_linear.load_state_dict(colbert_state_dict)
        self.sparse_linear.load_state_dict(sparse_state_dict)

    def dense_embedding(self, hidden_state, mask):
        if self.sentence_pooling_method == 'cls':
            return hidden_state[:, 0]
        elif self.sentence_pooling_method == 'mean':
            s = torch.sum(hidden_state * mask.unsqueeze(-1).float(), dim=1)
            d = mask.sum(axis=1, keepdim=True).float()
            return (s / d).half()

    def sparse_embedding(self, hidden_state, input_ids, return_embedding: bool = True):
        max_hidden_norm = torch.max(torch.norm(hidden_state,dim=-1),dim = -1).values.half()
        self.sparse_linear = self.sparse_linear.float()
        token_weights = torch.relu(self.sparse_linear(hidden_state)/max_hidden_norm.unsqueeze(-1).unsqueeze(-1))
        if not return_embedding: return token_weights

        sparse_embedding = torch.zeros(input_ids.size(0), input_ids.size(1), self.vocab_size,
                                       dtype=token_weights.dtype,
                                       device=token_weights.device)
        sparse_embedding = torch.scatter(sparse_embedding, dim=-1, index=input_ids.unsqueeze(-1), src=token_weights)

        unused_tokens = [self.tokenizer.cls_token_id, self.tokenizer.eos_token_id, self.tokenizer.pad_token_id,
                         self.tokenizer.unk_token_id]
        unused_tokens = [0,1,2,73440]
        sparse_embedding = torch.max(sparse_embedding, dim=1).values
        sparse_embedding[:, unused_tokens] *= 0.
        return sparse_embedding

    def colbert_embedding(self, last_hidden_state, mask):
        colbert_vecs = self.colbert_linear(last_hidden_state[:, 1:])
        colbert_vecs = colbert_vecs * mask[:, 1:][:, :, None].float()
        return colbert_vecs

    def forward(self,
                text_input: Dict[str, Tensor] = None,
                return_dense: bool = True,
                return_sparse: bool = False,
                return_colbert: bool = False,
                return_sparse_embedding: bool = False):
        assert return_dense or return_sparse or return_colbert, 'Must choose one or more from `return_colbert`, `return_sparse`, `return_dense` to set `True`!'

        last_hidden_state = self.model(**text_input, return_dict=True).last_hidden_state

        output = {}
        if return_dense:
            dense_vecs = self.dense_embedding(last_hidden_state, text_input['attention_mask'])
            output['dense_vecs'] = dense_vecs
        if return_sparse:
            sparse_vecs = self.sparse_embedding(last_hidden_state, text_input['input_ids'],
                                                return_embedding=return_sparse_embedding)
            output['sparse_vecs'] = sparse_vecs
        if return_colbert:
            colbert_vecs = self.colbert_embedding(last_hidden_state, text_input['attention_mask'])
            output['colbert_vecs'] = colbert_vecs

        if self.normlized:
            if 'dense_vecs' in output:
                output['dense_vecs'] = torch.nn.functional.normalize(output['dense_vecs'], dim=-1)
            if 'colbert_vecs' in output:
                output['colbert_vecs'] = torch.nn.functional.normalize(output['colbert_vecs'], dim=-1)

        return output
    

class BGEM3FlagModel:
    def __init__(
            self,
            model_name_or_path: str = None,
            pooling_method: str = 'cls',
            normalize_embeddings: bool = True,
            use_fp16: bool = True,
            device: str = None
    ) -> None:
        architectures = AutoConfig.from_pretrained(model_name_or_path, trust_remote_code=True).architectures
        if "MiniCPMModel" in architectures:
            pooling_method = "mean"

        self.model = BGEM3ForInference(
            model_name=model_name_or_path,
            normlized=normalize_embeddings,
            sentence_pooling_method=pooling_method,
        )

        self.tokenizer = self.model.tokenizer
        if device:
            self.device = torch.device(device)
        else:
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
            elif torch.backends.mps.is_available():
                self.device = torch.device("mps")
            elif is_torch_npu_available():
                self.device = torch.device("npu")
            else:
                self.device = torch.device("cpu")
                use_fp16 = False
        if use_fp16: self.model.half()
        self.model = self.model.to(self.device)

        if device is None:
            self.num_gpus = torch.cuda.device_count()
            if self.num_gpus > 1:
                print(f"----------using {self.num_gpus}*GPUs----------")
                self.model.model = torch.nn.DataParallel(self.model.model)
        else:
            self.num_gpus = 1

        self.model.eval()

    @torch.no_grad()
    def encode(self,
               sentences: Union[List[str], str],
               batch_size: int = 12,
               max_length: int = 8192,
               return_dense: bool = True,
               return_sparse: bool = False,
               return_colbert_vecs: bool = False) -> Dict:

        if self.num_gpus > 1:
            batch_size *= self.num_gpus
        self.model.eval()

        input_was_string = False
        if isinstance(sentences, str):
            sentences = [sentences]
            input_was_string = True

        def _process_token_weights(token_weights: np.ndarray, input_ids: list):
            # conver to dict
            result = defaultdict(int)
            unused_tokens = set([self.tokenizer.cls_token_id, self.tokenizer.eos_token_id, self.tokenizer.pad_token_id,
                                 self.tokenizer.unk_token_id])
            # token_weights = np.ceil(token_weights * 100)
            for w, idx in zip(token_weights, input_ids):
                if idx not in unused_tokens and w > 0:
                    idx = str(idx)
                    # w = int(w)
                    if w > result[idx]:
                        result[idx] = w
            return result

        def _process_colbert_vecs(colbert_vecs: np.ndarray, attention_mask: list):
            # delte the vectors of padding tokens
            tokens_num = np.sum(attention_mask)
            return colbert_vecs[:tokens_num - 1]  # we don't use the embedding of cls, so select tokens_num-1


        all_dense_embeddings, all_lexical_weights, all_colbert_vec = [], [], []
        for start_index in range(0, len(sentences), batch_size):
            sentences_batch = sentences[start_index:start_index + batch_size]
            batch_data = self.tokenizer(
                sentences_batch,
                padding=True,
                truncation=True,
                return_tensors='pt',
                max_length=max_length,
            ).to(self.device)
            output = self.model(batch_data,
                                return_dense=return_dense,
                                return_sparse=return_sparse,
                                return_colbert=return_colbert_vecs)
            if return_dense:
                all_dense_embeddings.append(output['dense_vecs'].cpu().numpy())

            if return_sparse:
                token_weights = output['sparse_vecs'].squeeze(-1)
                all_lexical_weights.extend(list(map(_process_token_weights, token_weights.cpu().numpy(),
                                                    batch_data['input_ids'].cpu().numpy().tolist())))

            if return_colbert_vecs:
                all_colbert_vec.extend(list(map(_process_colbert_vecs, output['colbert_vecs'].cpu().numpy(),
                                                batch_data['attention_mask'].cpu().numpy())))

        if return_dense:
            all_dense_embeddings = np.concatenate(all_dense_embeddings, axis=0)

        if return_dense:
            if input_was_string:
                all_dense_embeddings = all_dense_embeddings[0]
        else:
            all_dense_embeddings = None

        if return_sparse:
            if input_was_string:
                all_lexical_weights = all_lexical_weights[0]
        else:
            all_lexical_weights = None

        if return_colbert_vecs:
            if input_was_string:
                all_colbert_vec = all_colbert_vec[0]
        else:
            all_colbert_vec = None

        return {"dense_vecs": all_dense_embeddings, "lexical_weights": all_lexical_weights,
                "colbert_vecs": all_colbert_vec}


class BGEM3Server(BaseEmbedding):
    def __init__(self, url_or_path, batch_size=256, max_length=8192, query_instruction:str=None, **kargs) -> None:
        super().__init__(query_instruction)
        self.model= BGEM3FlagModel(model_name_or_path=url_or_path, **kargs)
        self.max_length = max_length
        self.batch_size = batch_size
        # UltraRAG-Embedding need query instruction
        architectures = AutoConfig.from_pretrained(url_or_path, trust_remote_code=True).architectures
        if "MiniCPMModel" in architectures:
            self.query_instruction = "Query: "

    def configs(self):
        dimension = 1024
        index_type = 'hybrid'
        return dimension, index_type

    async def query_encode(self, query: str | List[str]) -> List[float]:
        """Encode a query string or list of query strings into embeddings.

        Args:
            query (str | List[str]): Input query text or list of query texts

        Returns:
            Union[Dict, List[Dict]]: Dictionary or list of dictionaries containing:
                - dense_embed: Dense embedding vector
                - sparse_embed: Sparse embedding dictionary mapping token ids to weights

        Example:
            >>> server = BGEM3Server("BAAI/bge-m3")
            >>> # Single query
            >>> result = await server.query_encode("What is machine learning?")
            >>> print(result)
            {
                'dense_embed': [0.123, 0.456, ...],
                'sparse_embed': {1: 0.8, 5: 0.3, ...}
            }
            
            >>> # Multiple queries
            >>> results = await server.query_encode(["What is ML?", "How does AI work?"])
            >>> print(results)
            [
                {
                    'dense_embed': [0.123, 0.456, ...],
                    'sparse_embed': {1: 0.8, 5: 0.3, ...}
                },
                {
                    'dense_embed': [0.789, 0.321, ...], 
                    'sparse_embed': {2: 0.6, 7: 0.4, ...}
                }
            ]
        """
        queries = [query] if isinstance(query, str) else query
        if self.query_instruction is not None:
            queries = [f"{self.query_instruction} {query}" for query in queries]
        result = self.encode(queries)

        if isinstance(query, str):
            return result[0]
        else:
            return result


    async def document_encode(self, document: List[str]):
        """Encode a list of document strings into embeddings.

        Args:
            document (List[str]): List of document texts to encode

        Returns:
            List[Dict]: List of dictionaries containing:
                - dense_embed: Dense embedding vector
                - sparse_embed: Sparse embedding dictionary mapping token ids to weights

        Example:
            >>> server = BGEM3Server("BAAI/bge-m3")
            >>> docs = ["Machine learning is a subset of AI.", 
                       "Deep learning uses neural networks."]
            >>> results = await server.document_encode(docs)
            >>> print(results)
            [
                {
                    'dense_embed': [0.123, 0.456, ...],
                    'sparse_embed': {1: 0.8, 5: 0.3, ...}
                },
                {
                    'dense_embed': [0.789, 0.321, ...],
                    'sparse_embed': {2: 0.6, 7: 0.4, ...}
                }
            ]
        """
        return self.encode(document)


    def encode(self, texts: List[str]):
        """Encode a list of texts into dense and sparse embeddings.

        Args:
            texts (List[str]): List of input texts to encode. Each text will be processed in batches
                             if the total length exceeds max_length.

        Returns:
            List[Dict]: List of dictionaries containing:
                - dense_embed: Dense embedding vector 
                - sparse_embed: Sparse embedding dictionary mapping token ids to weights

        Example:
            >>> encoder = BGEM3Server("BAAI/bge-m3")
            >>> texts = ["Hello world", "Machine learning is amazing"]
            >>> results = encoder.encode(texts)
            >>> print(results)
            [
                {
                    'dense_embed': [0.123, 0.456, ...],
                    'sparse_embed': {1: 0.8, 5: 0.3, ...}
                },
                {
                    'dense_embed': [0.789, 0.321, ...],
                    'sparse_embed': {2: 0.6, 7: 0.4, ...}
                }
            ]
        """
        result_dict = self.model.encode(
            texts,
            batch_size=self.batch_size,
            max_length=self.max_length,
            return_dense=True,
            return_sparse=True,
        )
        denses = result_dict['dense_vecs'].tolist()
        sparses = [{int(k): float(v) for k, v in i.items()} for i in result_dict['lexical_weights']]
        assert len(denses) == len(texts)
        assert len(sparses) == len(texts)

        response = [{"dense_embed": val1, "sparse_embed": val2} for val1, val2 in zip(denses, sparses)]
        return response
    

    def run_batch(self, texts: List[str]):
        return self.encode(texts)