import argparse
import sys
from pathlib import Path
import json
from tqdm import tqdm
home_path = Path().resolve()
sys.path.append(home_path.as_posix())
import os
from loguru import logger
import asyncio
import yaml
import traceback
from ultrarag.evaluate.evaluator.generated_evaluator import GeneratedEvaluator
from ultrarag.evaluate.evaluator.retrieval_evaluator import RetrievalEvaluator
from ultrarag.modules.llm import OpenaiLLM, VllmServer
from ultrarag.modules.knowledge_managment import Knowledge_Managment
from ultrarag.modules.embedding import EmbServer, load_model
from ultrarag.modules.reranker import RerankerClient, RerankerServer

parser = argparse.ArgumentParser(description="Pipeline for processing datasets")

parser.add_argument('--pipeline_type', type=str, required=True, help="Type of pipeline: 'vanilla' or 'renote'")
parser.add_argument('--test_dataset', type=str, nargs='+', required=False, help="List of dataset files (json or jsonl)")
parser.add_argument('--selected_generated_metrics', default=[], type=str, nargs='+', help="List of generated metrics to evaluate")
parser.add_argument('--output_path', type=str, required=True, help="Path to save the results")
parser.add_argument('--knowledge_id', type=str, nargs='+', help="List of collections")

parser.add_argument('--evaluate_only', action='store_true', help="If set, skip generation and directly evaluate datasets")
parser.add_argument("--metric_api_key", type=str)
parser.add_argument("--metric_base_url", type=str)
parser.add_argument("--metric_model_name", type=str)
parser.add_argument("--metric_model_name_or_path", type=str)
parser.add_argument("--model_name_or_path", type=str)
parser.add_argument("--api_key", type=str)
parser.add_argument("--base_url", type=str)
parser.add_argument("--model_name", type=str)
parser.add_argument("--embedding_model_path", type=str)
parser.add_argument("--knowledge_stat_tab_path", type=str)
parser.add_argument("--reranker_model_path", type=str)
parser.add_argument("--config_path", type=str, 
                    default=(home_path / "config/pipeline/eval/eval.yaml").as_posix(), help="Path to the YAML configuration file.")

parser.add_argument("--pooling", type=str, default="mean", help="Pooling strategy to use.")
parser.add_argument("--query_instruction", type=str, default=None, help="Instruction to extract query text.")
parser.add_argument("--queries_path", type=str, help="Path to the queries file.")
parser.add_argument("--corpus_path", type=str, help="Path to the corpus file.")
parser.add_argument("--qrels_path", type=str, help="Path to the qrels file.")
parser.add_argument("--retrieval_output_path", type=str, help="Path to save the retrieval output results.")
parser.add_argument("--log_path", type=str, default=None, help="Path to save the log file.")
parser.add_argument("--topk", type=int, default=10, help="Top k documents to retrieve.")
parser.add_argument("--cutoffs", type=str, default=None, help="Cutoff for evaluation metrics,split by ,.")
parser.add_argument('--selected_retrieval_metrics', default=[], type=str, nargs='+', help="List of retrieval metrics to evaluate")

parser.add_argument("--embedding_gpu", type=str, default="cuda:0")
parser.add_argument("--reranker_gpu", type=str, default="cuda:0")


args, unknown = parser.parse_known_args()
args.cutoffs = [int(c) for c in args.cutoffs.split(",")] if args.cutoffs is not None else [args.topk]

def load_config(config_path):
    """Load prompts and sampling parameters from a YAML configuration file."""
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

if args.config_path:
    config= load_config(args.config_path)
    vllm_params = config.get("VllmServer_params",{})
    metric_vllm_params = config.get("metric_VllmServer_params",{})
    
def ensure_output_path(file_path):
    dir_name=os.path.dirname(file_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    counter = 1
    new_file_path = file_path
    while os.path.exists(new_file_path):
        base_name, ext = os.path.splitext(file_path)
        new_file_path = f"{base_name}_({counter}){ext}"
        counter += 1
    return new_file_path

def load_rerank_model(url, device='cuda'):
    if Path(url).exists():
        return RerankerServer(model_path=url, device=device)
    else:
        return RerankerClient(url=url)
    
    
def load_dataset(file_path):
    """Load dataset from json or jsonl file."""
    dataset = []
    with open(file_path, 'r', encoding='utf-8') as f:
        if file_path.endswith('.jsonl'):
            dataset = [json.loads(line) for line in f]
        elif file_path.endswith('.json'):
            dataset = json.load(f)
        else:
            raise ValueError("Unsupported file format: {}".format(file_path))
    return dataset

# Process each dataset
async def process_datasets(metric_llm, flow, collections, datasets, evaluate_only, generated_metrics):
    """
    Process and evaluate a list of datasets.

    Args:
        metric_llm (object): The language model used for evaluation metrics.
        flow (object): The flow object used to generate predictions.
        collections (list): A list of collections to be used in the flow query.
        datasets (list): A list of dataset file paths to be processed.
        evaluate_only (bool): If True, only evaluate the datasets without generating predictions.
        generated_metrics (list): A list of metrics to be generated during evaluation.

    Returns:
        None

    This function processes each dataset file in the provided list of datasets. For each dataset, it loads the data,
    generates predictions using the provided flow object (if evaluate_only is False), and evaluates the dataset using
    the provided metric language model. The results are then saved to the specified output path.
    """
    for dataset_file in tqdm(datasets, desc="Processing datasets"):
        print(f"Processing dataset: {dataset_file}")
        dataset = load_dataset(dataset_file)

        if not evaluate_only:
            for item in tqdm(dataset, desc=f"Processing items in {dataset_file}"):
                try:
                    query = item.get('query')
                    answer = item.get('answer')
                    system_prompt = item.get('instruction')
                    predictions = await flow.aquery(query=query, messages=[], collection = collections, system_prompt=system_prompt)
                    buff = ""
                    async for chunk in predictions:
                        if isinstance(chunk, dict):
                            if chunk['state'] == "data": 
                                buff += chunk['value']
                        else:
                            buff += chunk
                    prediction = buff

                    item['prediction'] = prediction
                except Exception as e:
                    logger.error(traceback.format_exc())
                    pass
        try:
            dataset = evaluate_metrics(metric_llm, dataset, generated_metrics)
        except Exception as e:
            logger.error(e)
        output_file_path = ensure_output_path(os.path.join(args.output_path, os.path.basename(dataset_file)))
        with open(output_file_path, 'w', encoding='utf-8') as f:
            if dataset_file.endswith('.jsonl'):
                for item in dataset:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
            else:
                json.dump(dataset, f, ensure_ascii=False, indent=2)


def evaluate_metrics(llm, dataset, generated_metrics):
    """
    Evaluate metrics for a given dataset using a language model.
    Args:
        llm: The language model to be used for evaluation.
        dataset (list): A list of dictionaries, where each dictionary contains 'answer' and 'prediction' keys.
        generated_metrics (list): A list of metric names to be evaluated.
    Returns:
        list: The updated dataset with individual metric scores and average scores appended.
    Raises:
        Exception: Logs any exceptions that occur during metric evaluation.
    """
    scores_summary = {}
    for item in tqdm(dataset, desc="Evaluating metrics"):
        # todo
        for metric_name in generated_metrics:
            try:
                if metric_name == "completeness":
                    score = generated_evaluator.get_score(metric_name, item["answer"], item["prediction"], item, llm=llm)
                else:
                    score = generated_evaluator.get_score(metric_name, item["answer"], item["prediction"], item)
                item[f"{metric_name}_score"] = score
                scores_summary.setdefault(metric_name, []).append(score)
            except Exception as e:
                logger.error(metric_name,e)
                pass

    average_scores = {}
    for metric_name, scores in scores_summary.items():
        average_score = sum(scores) / len(scores) if scores else 0
        average_scores[metric_name] = average_score
        
    print(f"Average scores:{average_scores}")
    dataset.append({"average_scores": average_scores})
    return dataset


if __name__ == "__main__":
    generated_evaluator=GeneratedEvaluator()
    # retrieval_evaluator=RetrievalEvaluator()
    llm = None
    flow = None
    if not args.evaluate_only:
        if args.model_name_or_path:
            llm = VllmServer(base_url=args.model_name_or_path, **vllm_params)
        else:
            llm = OpenaiLLM(api_key=args.api_key, base_url=args.base_url, model=args.model_name, **vllm_params["sampling_params"])
        if args.metric_model_name_or_path:
            metric_llm = VllmServer(base_url=args.metric_model_name_or_path, **metric_vllm_params)
        elif args.metric_api_key and args.metric_base_url and args.metric_model_name:
            metric_llm = OpenaiLLM(api_key=args.metric_api_key, base_url=args.metric_base_url, model=args.metric_model_name)
        else:
            metric_llm = None
            
        if args.pooling and args.query_instruction:
            encoder = EmbServer(args.embedding_model_path, pooling=args.pooling, query_instruction=args.query_instruction)
        else:
            encoder = load_model(args.embedding_model_path, device=args.embedding_gpu)   
        
        searcher = Knowledge_Managment.get_searcher(embedding_model=encoder,knowledge_id=args.knowledge_id, knowledge_stat_tab_path = args.knowledge_stat_tab_path)
        reranker = load_rerank_model(args.reranker_model_path,device=args.reranker_gpu)
        if args.pipeline_type == "vanilla":
            from ultrarag.workflow.ultraragflow.simple_flow import NaiveFlow
            flow = NaiveFlow.from_modules(llm=llm,index=searcher,reranker=reranker)
        elif args.pipeline_type == "renote":
            from ultrarag.workflow.ultraragflow.renote_flow import RenoteFlow
            flow = RenoteFlow.from_modules(llm=llm,database=searcher)
        elif args.pipeline_type == "kbalign":
            from ultrarag.workflow.ultraragflow.kbalign_flow import KBAlignFlow
            flow = KBAlignFlow.from_modules(llm=llm,database=searcher)

    try:
        if args.selected_retrieval_metrics:
            evaluator = RetrievalEvaluator(encoder, {"queries": args.queries_path, "corpus": args.corpus_path, "default": args.qrels_path, "output": args.retrieval_output_path}, args.topk)
            metric_result = evaluator.run_metric_inference(args.selected_retrieval_metrics, args.cutoffs)
            if args.log_path is not None:
                with open(args.log_path, "w") as f:
                    f.write(json.dumps(metric_result, indent=4))
            print(f"Retrieval eval completed. Results saved to {args.retrieval_output_path}")
    except Exception as e:
        logger.error(e)
        
    try:
        if args.selected_generated_metrics:
            asyncio.run(process_datasets(llm, flow, args.knowledge_id, args.test_dataset, args.evaluate_only, args.selected_generated_metrics))
            print(f"Processing completed. Results saved to {args.output_path}")
    except Exception as e:
        logger.error(e)
        