'''
the simple tools is used to generate query for embedding model training
'''
import random
import json
from tqdm import tqdm
from typing import Any, Dict, List
from ultrarag.modules.llm import BaseLLM
from ultrarag.modules.database import BaseIndex
from .prompts import QUERY_GENERATE_PROMPT
import asyncio
import uuid
import argparse

class DataSyntheiser:
    def __init__(self, llm: BaseLLM = None, index: BaseIndex = None):
        self._llm = llm
        self._index = index

    async def arun(self, corpus: List[str], ratio: float):
        ''' corpus: 用户语料，用于合成数据
            ratio:  用于分割训练集和测试集的比率，默认0.1, 代表合成数据的10%被用做测试数据
        '''
        dataset = []
        for ctx in tqdm(corpus, desc=""):
            prompt = random.choice(list(QUERY_GENERATE_PROMPT.values()))
            messages = [dict(role="user", content=prompt.format(content=ctx))]
            resp = await self._llm.arun(messages=messages, stream=False)
            try:
                jsonline = json.loads(resp)
                for item in jsonline:
                    dataset.append(dict(query=item["query"], content=ctx))
            except:
                pass
        
        # 从数据中抽取出测试集
        random.shuffle(dataset)
        cut_line = int(len(dataset) * ratio)
        testset, trainset = dataset[:cut_line], dataset[cut_line:]

        collection = str(uuid.uuid1())
        await self._index.create(collection_name=collection)
        await self._index.insert(collection, corpus)

        trainset_with_negs = []
        for item in trainset:
            query, pos = item["query"], item["content"]
            recalls = await self._index.search(collection, query=query, topn=50)
            recalls = [item.content for item in recalls[-5:]]
            trainset_with_negs.append(dict(query=query, pos=[pos], neg=[recalls]))
        await self._index.remove(collection)
            
        return testset, trainset_with_negs

    def update(self, llm: BaseLLM, index: BaseIndex):
        self._llm = llm
        self._index = index
        
    def main(self, parser):
        import jsonlines
        args = argparse.ArgumentParser()
        args.add_argument("--api_key", required=True, type=str)
        args.add_argument("--base_url", required=True, type=str)
        args.add_argument("--model_name", required=True, type=str)
        args.add_argument("--embed", required=True, type=str, help="embedding model path")
        args.add_argument("--corpus_path", required=True, type=str, help="raw chunk data")
        args.add_argument("--output_dir", required=True, type=str, help="output dir")
        args.add_argument("--ratio", required=True, type=float, help="dataset ratio")
        args, unknown=parser.parse_known_args()
        if not self._llm or not self._index:
            from ultrarag.modules.llm import OpenaiLLM
            from ultrarag.modules.embedding import BGEServer
            from ultrarag.modules.database import QdrantIndex
            encoder = BGEServer(url_or_path=args.embed)
            index = QdrantIndex(url=":memory:", encoder=encoder)
            llm = OpenaiLLM(api_key=args.api_key, base_url=args.base_url, model=args.model_name)
            self.update(llm=llm, index=index)
        corpus = list(jsonlines.open(args.corpus_path, "r"))
        corpus = [item["content"] for item in corpus]
        testset, trainset = asyncio.run(self.arun(corpus=corpus, ratio=args.ratio))

        with jsonlines.open(f"{args.output_dir}/testset.jsonl", "w") as fw:
            fw.write_all(testset)
            
        with jsonlines.open(f"{args.output_dir}/trainset.jsonl", "w") as fw:
            fw.write_all(trainset)
            
            
if __name__ == "__main__":
    import argparse
    import jsonlines
    from ultrarag.modules.llm import OpenaiLLM
    from ultrarag.modules.embedding import BGEServer
    from ultrarag.modules.database import QdrantIndex

    args = argparse.ArgumentParser()
    args.add_argument("-api_key", required=True, type=str)
    args.add_argument("-base_url", required=True, type=str)
    args.add_argument("-model", required=True, type=str)
    args.add_argument("-embed", required=True, type=str, help="embedding model path")

    args.add_argument("-corpus", required=True, type=str, help="raw chunk data")
    args = args.parse_args()
    encoder = BGEServer(url_or_path=args.embed)
    index = QdrantIndex(url=":memory:", encoder=encoder)
    llm = OpenaiLLM(api_key=args.api_key, base_url=args.base_url, model=args.model)
    synther = DataSyntheiser(llm=llm, index=index)

    corpus = list(jsonlines.open(args.corpus, "r"))
    corpus = [item["content"] for item in corpus]
    testset, trainset = asyncio.run(synther.arun(corpus=corpus))

    with jsonlines.open("testset.jsonl", "w") as fw:
        fw.write_all(testset)
        
    with jsonlines.open("trainset.jsonl", "w") as fw:
        fw.write_all(trainset)