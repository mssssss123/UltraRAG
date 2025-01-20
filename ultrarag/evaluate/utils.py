import csv
import pathlib
from typing import Dict, Any

def load_beir_qrels(qrels_file):
    """
    Load BEIR qrels from a TSV file.

    Args:
        qrels_file (str): Path to the qrels file.

    Returns:
        dict: A dictionary where keys are query IDs (str) and values are dictionaries.
              The inner dictionaries have corpus IDs (str) as keys and relevance scores (int) as values.
    """
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
    Save the ranking results in TREC format.

    Args:
        rank_result (Dict[str, Dict[str, Dict[str, Any]]]): A dictionary containing the ranking results.
            The structure of the dictionary is:
            {
                query_id: {
                    doc_id: score,
                    ...
                },
                ...
            }
        output_path (str): The file path where the TREC formatted results will be saved.
        run_id (str, optional): The identifier for the run. Defaults to "UltraRAG".

    The TREC format is:
    <query_id> Q0 <doc_id> <rank> <score> <run_id>
    """
    pathlib.Path("/".join(output_path.split("/")[:-1])).mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for qid in rank_result:
            for i, (doc_id, score) in enumerate(rank_result[qid].items()):
                f.write("{}\tQ0\t{}\t{}\t{}\t{}\n".format(qid, doc_id, i + 1, score, run_id))