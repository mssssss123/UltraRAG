import json
import argparse
import re
from collections import Counter
import numpy as np
from tqdm import tqdm
from pathlib import Path
import sys
import asyncio
import torch
home_path = Path().resolve()
sys.path.append(home_path.as_posix())
from ultrarag.evaluate.index import BruteIndex
from ultrarag.modules.embedding import EmbServer
from ultrarag.evaluate.utils import load_beir_qrels, save_as_trec

class RetrievalEvaluator(object):
    def __init__(self, model, files_path: dict[str, str],topk:int=10, device='cuda') -> None:
        """
        Args:
            model_path (str): path to the embedding model
            files_path (dict[str, str]): key "queries" for queries file path, key "corpus" for corpus file path, and key "default" for qrels file path.
            device (str, optional): device to use. Defaults to 'cuda'.
        """

        self.files_path = files_path
        self.device = device
        self.model = model
        self.index = BruteIndex(device)
        self.topk = topk
        self.qid_lookup = []
        self.docid_lookup = []

        # Read qrels from file
        self.qrels = load_beir_qrels(files_path['default'])

        # Read queries from file
    
    @staticmethod
    def get_id(data:dict):
        try:
            return str(data["_id"])
        except KeyError:
            return str(data["id"])
    
    @staticmethod
    def get_text(data:dict):
        try:
            return data["text"]
        except KeyError:
            try:
                return data["contents"]
            except KeyError:
                return data["content"]

    async def _embed_corpus(self, batch_size=2048) -> None:
        with open(self.files_path['corpus'], 'r') as f:
            lines = f.readlines()
            for p in tqdm(range(0, len(lines), batch_size)):
                batch = lines[p: p + batch_size]
                texts = [self.get_text(json.loads(line)) for line in batch]
                embeddings = await self.model.document_encode(texts)
                embeddings = torch.Tensor([emb["dense_embed"] for emb in embeddings])
                # print(embeddings.shape)
                self.index.insert(texts, embeddings)
                self.docid_lookup.extend([self.get_id(json.loads(line)) for line in batch])

    async def evaluate(self, topk) -> None:
        """
            Args:
                topk (int): The number of top results to retrieve for each query.

            Returns:
                None

            This method performs the following steps:
            1. Embeds the corpus asynchronously.
            2. Initializes an empty dictionary to store the retrieval results.
            3. Reads the queries from a file and processes each query:
                a. Extracts the query ID and text.
                b. Encodes the query using the model.
                c. Searches the index for the top `topk` results based on the query embedding.
                d. Stores the results in the `self.run` dictionary with query IDs as keys and 
                   document IDs with their corresponding scores as values.
            4. Sorts the retrieval results for each query by score in descending order.
        """
        await asyncio.create_task(self._embed_corpus())
        self.run = {}
        with open(self.files_path['queries'], 'r') as f:
            for line in f:
                data = json.loads(line)
                qid = self.get_id(data)
                query = self.get_text(data)
                embed = await self.model.query_encode(query)
                embed = torch.Tensor(embed["dense_embed"]).unsqueeze(0)
                scores, indices = self.index.search(embed, topn=topk)
                for indices_per_query, scores_per_query in zip(indices, scores):
                    self.run[qid] = {self.docid_lookup[indices_per_query[i]]: scores_per_query[i] for i in range(topk)}
        # Sort the run by score
        for qid in self.run:
            self.run[qid] = {k: v for k, v in sorted(self.run[qid].items(), key=lambda item: item[1], reverse=True)}

    def save_results(self, output_path: str) -> None:
        save_as_trec(self.run, output_path)

    def compute_mrr(self, cutoff=None) -> float:
        """
        Compute MRR@cutoff manually.
        """
        mrr = 0.0
        num_ranked_q = 0
        results = {}
        for qid in self.qrels:
            if qid not in self.run:
                continue
            num_ranked_q += 1
            docid_and_score = [(docid, score) for docid, score in self.run[qid].items()]
            for i, (docid, _) in enumerate(docid_and_score):
                rr = 0.0
                if cutoff is None or i < cutoff:
                    if docid in self.qrels[qid] and self.qrels[qid][docid] > 0:
                        rr = 1.0 / (i + 1)
                        break
            results[qid] = rr
            mrr += rr
        mrr /= num_ranked_q
        return mrr
    
    def compute_ndcg(self, cutoff=None) -> float:
        """
        Compute NDCG@cutoff manually.
        """
        ndcg = 0.0
        num_ranked_q = 0
        for qid in self.qrels:
            if qid not in self.run:
                continue
            num_ranked_q += 1
            ranked_docs = list(self.run[qid].keys())
            relevance_scores = [self.qrels[qid].get(docid, 0) for docid in ranked_docs]
            
            dcg = 0.0
            for i, rel in enumerate(relevance_scores):
                if cutoff is not None and i >= cutoff:
                    break
                dcg += (2**rel - 1) / np.log2(i + 2)  # i + 2 because positions start at 1

            # Compute IDCG
            sorted_rels = sorted(self.qrels[qid].values(), reverse=True)
            if cutoff is not None:
                sorted_rels = sorted_rels[:cutoff]
            idcg = 0.0
            for i, rel in enumerate(sorted_rels):
                idcg += (2**rel - 1) / np.log2(i + 2)
            
            if idcg > 0:
                ndcg += dcg / idcg
            else:
                ndcg += 0.0  # If there are no relevant documents

        if num_ranked_q == 0:
            return 0.0
        ndcg /= num_ranked_q
        return ndcg

    def compute_recall(self, cutoff=None) -> float:
        """
        Compute Recall@k manually.
        """
        recall = 0.0
        num_ranked_q = 0
        for qid in self.qrels:
            if qid not in self.run:
                continue
            num_ranked_q += 1
            ranked_docs = list(self.run[qid].keys())
            relevance_scores = [self.qrels[qid].get(docid, 0) for docid in ranked_docs]
            num_relevant = sum([1 for rel in relevance_scores if rel > 0])
            if num_relevant == 0:
                continue
            if cutoff is not None:
                num_relevant = min(num_relevant, cutoff)
            recall += num_relevant / num_relevant
        recall /= num_ranked_q
        return recall
    
    def get_score(self,metrics=["MRR","NDCG","Recall"],cutoffs=[None],data=None,**kwargs):
        """
        Calculate evaluation metrics for retrieval performance.
        Parameters:
        metrics (list of str): List of metrics to calculate. Supported metrics are "MRR", "NDCG", and "Recall".
        cutoffs (list of int or None): List of cutoff values for the metrics. If None, the metric is calculated for all available data.
        data (optional): Data to be evaluated. Default is None.
        **kwargs: Additional keyword arguments.
        Returns:
        dict: A dictionary with metric names as keys and their corresponding calculated values as values.
        Raises:
        ValueError: If an unsupported metric is provided in the metrics list.
        """
        results = {}
        for metrics in metrics:
            if metrics == "MRR":
                for cutoff in cutoffs:
                    mrr = self.compute_mrr(cutoff)
                    print(f"MRR@{cutoff}: {mrr}")
                    results[f"MRR@{cutoff}"] = mrr
            elif metrics == "NDCG":
                for cutoff in cutoffs:
                    ndcg = self.compute_ndcg(cutoff)
                    print(f"NDCG@{cutoff}: {ndcg}")
                    results[f"NDCG@{cutoff}"] = ndcg
            elif metrics == "Recall":
                for cutoff in cutoffs:
                    recall = self.compute_recall(cutoff)
                    print(f"Recall@{cutoff}: {recall}")
                    results[f"Recall@{cutoff}"] = recall
            else:
                raise ValueError(f"Unsupported metric: {metrics}")
        return results    

    @staticmethod
    def compute_mrr_atom(qrel, ranked_docs, cutoff=None) -> float:
        """
        Compute MRR@cutoff for a single query.
        """
        mrr = 0.0
        for i, docid in enumerate(ranked_docs):
            if cutoff is not None and i >= cutoff:
                break
            if docid in qrel and qrel[docid] > 0:
                mrr = 1.0 / (i + 1)
                break
        return mrr
    
    
    @staticmethod
    def compute_ndcg_atom(qrel, ranked_docs, cutoff=None) -> float:
        """
        Compute NDCG@cutoff for a single query.
        """
        relevance_scores = [qrel.get(docid, 0) for docid in ranked_docs]
        dcg = 0.0
        for i, rel in enumerate(relevance_scores):
            if cutoff is not None and i >= cutoff:
                break
            dcg += (2**rel - 1) / np.log2(i + 2)
            
        # Compute IDCG
        sorted_rels = sorted(qrel.values(), reverse=True)
        if cutoff is not None:
            sorted_rels = sorted_rels[:cutoff]
        idcg = 0.0
        for i, rel in enumerate(sorted_rels):
            idcg += (2**rel - 1) / np.log2(i + 2)
        
        if idcg > 0:
            ndcg = dcg / idcg
        else:
            ndcg = 0.0
        return ndcg

    @staticmethod
    def compute_recall_atom(qrel, ranked_docs, cutoff=None) -> float:
        """
        Compute Recall@k for a single query.
        """
        relevance_scores = [qrel.get(docid, 0) for docid in ranked_docs]
        num_relevant = sum([1 for rel in relevance_scores if rel > 0])
        if num_relevant == 0:
            return 0.0
        if cutoff is not None:
            num_relevant = min(num_relevant, cutoff)
        recall = num_relevant / num_relevant
        return recall

    @staticmethod
    def get_score_atom(qrel, ranked_docs, metric, cutoffs=[None], data=None,**kwargs) -> dict:
        if metric == "MRR":
            for cutoff in cutoffs:
                mrr = RetrievalEvaluator.compute_mrr_atom(qrel, ranked_docs, cutoff)
                return mrr
        elif metric == "NDCG":
            for cutoff in cutoffs:
                ndcg = RetrievalEvaluator.compute_ndcg_atom(qrel, ranked_docs, cutoff)
                return ndcg
        elif metric == "Recall":
            for cutoff in cutoffs:
                recall = RetrievalEvaluator.compute_recall_atom(qrel, ranked_docs, cutoff)
                return recall
        else:
            raise ValueError(f"Unsupported metric: {metric}")
    
    def run_metric_inference(self, metrics=["MRR","NDCG","Recall"],cutoffs=[None]):
        """
        Runs metric inference by evaluating the top-k results and calculating specified metrics.

        Args:
            metrics (list, optional): A list of metric names to calculate. Defaults to ["MRR", "NDCG", "Recall"].
            cutoffs (list, optional): A list of cutoff values for the metrics. Defaults to [None].

        Returns:
            dict: A dictionary containing the calculated scores for the specified metrics.
        """
        asyncio.run(self.evaluate(self.topk))
        self.save_results(self.files_path['output'])
        return self.get_score(metrics,cutoffs)

def main():
    parser = argparse.ArgumentParser(description="Evaluation Script")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the embedding model.")
    parser.add_argument("--pooling", type=str, default="mean", help="Pooling strategy to use.")
    parser.add_argument("--query_instruction", type=str, default=None, help="Instruction to extract query text.")
    parser.add_argument("--queries_path", type=str, required=True, help="Path to the queries file.")
    parser.add_argument("--corpus_path", type=str, required=True, help="Path to the corpus file.")
    parser.add_argument("--qrels_path", type=str, required=True, help="Path to the qrels file.")
    parser.add_argument("--output_path", type=str, required=True, help="Path to save the output results.")
    parser.add_argument("--log_path", type=str, default=None, help="Path to save the log file.")
    parser.add_argument("--topk", type=int, default=10, help="Top k documents to retrieve.")
    parser.add_argument("--cutoffs", type=str, default=None, help="Cutoff for evaluation metrics,split by ,.")
    parser.add_argument("--metrics", type=str, default="MRR,NDCG,Recall", help="Evaluation metrics to use, split by ,.")

    
    args = parser.parse_args()
    args.cutoffs = [int(c) for c in args.cutoffs.split(",")] if args.cutoffs is not None else [args.topk]
    args.metrics = args.metrics.split(",")
    model = EmbServer(args.model_path, pooling=args.pooling, query_instruction=args.query_instruction)
    
    evaluator = RetrievalEvaluator(model, {"queries": args.queries_path, "corpus": args.corpus_path, "default": args.qrels_path, "output": args.output_path}, args.topk)
    metric_result = evaluator.run_metric_inference(args.metrics, args.cutoffs)
    if args.log_path is not None:
        with open(args.log_path, "w") as f:
            f.write(json.dumps(metric_result, indent=4))

if __name__ == "__main__":
    main()