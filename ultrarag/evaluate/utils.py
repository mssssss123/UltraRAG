import csv
import pathlib
from typing import Dict, Any

def load_beir_qrels(qrels_file):
    qrels = {}
    with open(qrels_file) as f:
        tsvreader = csv.DictReader(f, delimiter="\t")
        for row in tsvreader:
            qid = str(row["query-id"])
            pid = str(row["corpus-id"])
            rel = int(row["score"])
            if qid in qrels:
                qrels[qid][pid] = rel
            else:
                qrels[qid] = {pid: rel}
    return qrels

def save_as_trec(
    rank_result: Dict[str, Dict[str, Dict[str, Any]]], output_path: str, run_id: str = "UltraRAG"
):
    """
    Save the rank result as TREC format:
    <query_id> Q0 <doc_id> <rank> <score> <run_id>
    """
    pathlib.Path("/".join(output_path.split("/")[:-1])).mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for qid in rank_result:
            for i, (doc_id, score) in enumerate(rank_result[qid].items()):
                f.write("{}\tQ0\t{}\t{}\t{}\t{}\n".format(qid, doc_id, i + 1, score, run_id))