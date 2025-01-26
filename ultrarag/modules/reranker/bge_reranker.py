from .base import BaseRerank
from loguru import logger
from typing import Tuple, Union, List
import json, aiohttp
import traceback
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification, is_torch_npu_available

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

class FlagReranker:
    def __init__(
            self,
            model_name_or_path: str = None,
            use_fp16: bool = False,
            cache_dir: str = None,
            device: Union[str, int] = None
    ) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, cache_dir=cache_dir, trust_remote_code=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name_or_path, cache_dir=cache_dir, trust_remote_code=True)

        if device and isinstance(device, str):
            self.device = torch.device(device)
            if device == 'cpu':
                use_fp16 = False
        else:
            if torch.cuda.is_available():
                if device is not None:
                    self.device = torch.device(f"cuda:{device}")
                else:
                    self.device = torch.device("cuda")
            elif torch.backends.mps.is_available():
                self.device = torch.device("mps")
            elif is_torch_npu_available():
                self.device = torch.device("npu")
            else:
                self.device = torch.device("cpu")
                use_fp16 = False
        if use_fp16:
            self.model.half()

        self.model = self.model.to(self.device)

        self.model.eval()

        if device is None:
            self.num_gpus = torch.cuda.device_count()
            if self.num_gpus > 1:
                print(f"----------using {self.num_gpus}*GPUs----------")
                self.model = torch.nn.DataParallel(self.model)
        else:
            self.num_gpus = 1

    @torch.no_grad()
    def compute_score(self, sentence_pairs: Union[List[Tuple[str, str]], Tuple[str, str]], batch_size: int = 256,
                      max_length: int = 512, normalize: bool = False) -> List[float]:
        if self.num_gpus > 0:
            batch_size = batch_size * self.num_gpus

        assert isinstance(sentence_pairs, list)
        if isinstance(sentence_pairs[0], str):
            sentence_pairs = [sentence_pairs]

        all_scores = []
        for start_index in range(0, len(sentence_pairs), batch_size):
            sentences_batch = sentence_pairs[start_index:start_index + batch_size]
            inputs = self.tokenizer(
                sentences_batch,
                padding=True,
                truncation=True,
                return_tensors='pt',
                max_length=max_length,
            ).to(self.device)

            scores = self.model(**inputs, return_dict=True).logits.view(-1, ).float()
            all_scores.extend(scores.cpu().numpy().tolist())

        if normalize:
            all_scores = [sigmoid(score) for score in all_scores]

        if len(all_scores) == 1:
            return all_scores[0]
        return all_scores



class BGERerankClient(BaseRerank):
    def __init__(self, url: str) -> None:
        super().__init__()
        self.url = url
        logger.info(f"{self.__class__.__name__} use url in {url}")


    async def scoring(self, query: str, contents: List[str]) -> List[float]:
        HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, json={"query": query, "texts": contents}, headers=HEADERS, timeout=20) as response:
                    if response.status != 200:
                        raise ValueError(f"response.status is {response.status}")
                    r = await response.text()
                    scores: list[float] = json.loads(r)
                    if not isinstance(scores, list):
                        logger.error(f"scores result is not list: {scores}")
                    if len(scores) != len(contents):
                        logger.error(f"scores lens is not equal contents: {scores} and {contents}")
        except Exception as e:
            logger.error(f'reranker raise {traceback.format_exc()}')
            return [1.0] * len(contents)
        return scores
    


class BGERerankServer(BaseRerank):
    def __init__(self,
            model_path: str,
            padding='longest',
            max_length=512,
            batch_size=256,
            **build_kwargs,
    ) -> None:
        self.rerank_model = FlagReranker(
            model_name_or_path=model_path,
            **build_kwargs,
        )
        self.padding = padding
        self.max_length = max_length
        self.batch_size = batch_size


    async def scoring(self, query: str, contents: List[str]) -> List[float]:
        ''' 计算query和doc的打分结果
        '''
        qd_pairs = [(query, item) for item in contents]
        scores = self.rerank_model.compute_score(
            qd_pairs, 
            batch_size=self.batch_size, 
            max_length=self.max_length
        )
        scores = [scores] if isinstance(scores, float) else scores
        return scores
    

    def run_batch(self, texts: list[tuple[str, str]]) -> list[float]:
        ''' 计算两个文本的相似性得分
        '''
        scores = self.rerank_model.compute_score(
            texts,
            batch_size=self.batch_size,
            max_length=self.max_length,
        )
        scores = [scores] if isinstance(scores, float) else scores
        return scores
    
