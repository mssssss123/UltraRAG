import torch
from .base import BaseRerank
from loguru import logger
from typing import List, Tuple, Union
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import json, requests

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

class RerankerModel:
    ''' this class is modified by https://github.com/netease-youdao/BCEmbedding.git
    '''
    def __init__(
            self,
            model_name_or_path: str,
            use_fp16: bool=False,
            device: str=None,
            **kwargs
        ):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, **kwargs)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name_or_path, **kwargs)
        logger.info(f"Loading from `{model_name_or_path}`.")
        
        num_gpus = torch.cuda.device_count()
        if device is None:
            self.device = "cuda" if num_gpus > 0 else "cpu"
        else:
            self.device = 'cuda:{}'.format(int(device)) if device.isdigit() else device
        
        if self.device == "cpu":
            self.num_gpus = 0
        elif self.device.startswith('cuda:') and num_gpus > 0:
            self.num_gpus = 1
        elif self.device == "cuda":
            self.num_gpus = num_gpus
        else:
            raise ValueError("Please input valid device: 'cpu', 'cuda', 'cuda:0', '0' !")

        if use_fp16:
            self.model.half()

        self.model.eval()
        self.model = self.model.to(self.device)

        if self.num_gpus > 1:
            self.model = torch.nn.DataParallel(self.model)
        
        logger.info(f"Execute device: {self.device};\t gpu num: {self.num_gpus};\t use fp16: {use_fp16}")

        # for advanced preproc of tokenization
        self.max_length = kwargs.get('max_length', 512)
        self.overlap_tokens = kwargs.get('overlap_tokens', 80)
    
    def compute_score(
            self, 
            sentence_pairs: Union[List[Tuple[str, str]], Tuple[str, str]], 
            batch_size: int = 256,
            max_length: int = 512,
            enable_tqdm: bool=True,
            **kwargs
        ):
        if self.num_gpus > 1:
            batch_size = batch_size * self.num_gpus
        
        assert isinstance(sentence_pairs, list)
        if isinstance(sentence_pairs[0], str):
            sentence_pairs = [sentence_pairs]
        
        with torch.no_grad():
            scores_collection = []
            for sentence_id in range(0, len(sentence_pairs), batch_size):
                sentence_pairs_batch = sentence_pairs[sentence_id:sentence_id+batch_size]
                inputs = self.tokenizer(
                            sentence_pairs_batch, 
                            padding=True,
                            truncation=True,
                            max_length=max_length,
                            return_tensors="pt"
                        )
                inputs_on_device = {k: v.to(self.device) for k, v in inputs.items()}
                scores = self.model(**inputs_on_device, return_dict=True).logits.view(-1,).float()
                scores = torch.sigmoid(scores)
                scores_collection.extend(scores.cpu().numpy().tolist())
        
        if len(scores_collection) == 1:
            return scores_collection[0]
        return scores_collection


class BCERerankClient(BaseRerank):
    def __init__(self, url: str) -> None:
        super().__init__()
        self.url = url


    def scoring(self, query: str, contents: List[str]) -> List[float]:
        post_parm = {"query": query, "contents": contents}
        response = requests.post(self.url, json.dumps(post_parm), headers=HEADERS)
        return response.json().get("scores", [])


class BCERerankServer(BaseRerank):
    def __init__(self, model_path, device=None, **kargs) -> None:
        super().__init__()

        logger.info(f" reranker device is {device}")
        self.batch_size = kargs.get("batch_size", 256)
        self.max_length = kargs.get("max_length", 512)
        self.rerank_model = RerankerModel(model_name_or_path=model_path, device=device, **kargs)

        
    def scoring(self, query: str, contents: List[str]) -> List[float]:
        qd_pairs = [(query, item) for item in contents]
        scores = self.rerank_model.compute_score(qd_pairs, batch_size=self.batch_size, max_length=self.max_length)
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


if __name__ == "__main__":
    import argparse
    from flask import Flask, request

    args = argparse.ArgumentParser()
    args.add_argument("-host", required=False, default="localhost", type=str, help="server url and port")
    args.add_argument("-port", required=False, default=10086, type=int, help="server url and port")
    args.add_argument("-model_path", required=True, type=str, help="server url and port")
    args = args.parse_args()

    reranker = RerankServer(args.model_path)

    app = Flask(__name__)
    @app.route('/rerank', methods=['GET', 'POST'])
    def rerank():
        data = request.json
        query = data.get('query', None)
        contents = data.get('contents', None)

        scores = reranker.scoring(query=query, contents=contents)
        return json.dumps({"scores": scores})

    app.run(host=args.host, port=args.port, debug=True)