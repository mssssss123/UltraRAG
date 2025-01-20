from tqdm import tqdm
import os
from ultrarag.datasets.others.merge import load_file, write_output
from ultrarag.modules.reranker import BGERerankServer
import asyncio
async def reranker_clean(reranker_model : BGERerankServer,
                            qrel_path:str, 
                            output_path:str,
                            search_start_index:int,
                            search_end_index:int,
                            keep_neg_num:int,
                            score_ratio:float,
                            score_margin:float,
                            min_pos_score:float,
                            max_neg_score:float):
    """
    Asynchronously cleans a dataset by reranking positive and negative samples using a reranker model.
    Parameters:
        reranker_model (BGERerankServer): The reranker model used for scoring.
        qrel_path (str): Path to the input dataset file in JSONL format.
        output_path (str): Path to the output cleaned dataset file in JSONL format.
        search_start_index (int): The starting index for the search.
        search_end_index (int): The ending index for the search.
        keep_neg_num (int): The number of negative samples to keep.
        score_ratio (float): The ratio of the minimum positive score to filter negative samples.
        score_margin (float): The margin to add to the minimum positive score to filter negative samples.
        min_pos_score (float): The minimum score for positive samples.
        max_neg_score (float): The maximum score for negative samples.
    Returns:
        None
    The function processes the dataset by:
    1. Loading the dataset from the specified qrel_path.
    2. Scoring the positive and negative samples using the reranker model.
    3. Removing samples that do not meet the specified score criteria.
    4. Writing the cleaned dataset to the specified output_path.
    """
    # keep_neg_num = 7
    
    # corpus_path = os.path.join(input_path, 'corpus.jsonl')
    # query_path = os.path.join(input_path, 'query.jsonl')
    # qrel_path = os.path.join(input_path, "diged.jsonl")
    # output_path = os.path.join(input_path, "clean_diged.jsonl")

    # docs = load_file(corpus_path)
    # docs = [x['contents'] for x in docs]
    # docs_dict = {}
    # for doc in docs:
    #     docs_dict[doc['id']] = doc["contents"]
        
    # queries = load_file(query_path)
    # queries_dict = {}
    # for query in queries:
    #     queries_dict[query['id']] = query["query"]
    
    dataset = load_file(qrel_path)
    

    # reranker_model = BGERerankClient(url=reranker_model_url)    
    remove_indies = set()
    for i,item in tqdm(enumerate(dataset),total=len(dataset)):
        pos_scores = await reranker_model.scoring(item["query"], item["pos"])
        _min_pos_score = min(pos_scores)
        if _min_pos_score < min_pos_score:
            remove_indies.add(i)
        neg_scores = await reranker_model.scoring(item["query"], item["neg"])
        l_nes = len(item["neg"])
        for j in range(l_nes-1, -1, -1):
            if neg_scores[j] > _min_pos_score * score_ratio or neg_scores[j] + score_margin  > _min_pos_score or neg_scores[j] > max_neg_score:
                dataset[i]["neg"].pop(j)
                neg_scores.pop(j)
        if len(dataset[i]["neg"]) < keep_neg_num:
            remove_indies.add(i)    
    
    dataset = [dataset[i] for i in range(len(dataset)) if i not in remove_indies]
    
    write_output( dataset,output_path,"jsonl")
    
    
def reranker_clean_main(parser):
    import argparse
    from ultrarag.modules.reranker import BGERerankServer
    
    parser.add_argument("--reranker", required=True, type=str, help="reranker model path")
    # args.add_argument("--corpus_path", required=True, type=str, help="raw chunk data")
    parser.add_argument("--qrel_path", required=True, type=str, help="raw chunk data")
    parser.add_argument("--output_path", required=True, type=str, help="output path")
    parser.add_argument("--search_start_index", type=int, default=1)
    parser.add_argument("--search_end_index", type=int, default=30)
    parser.add_argument("--keep_neg_num", type=int, default=7)
    parser.add_argument("--score_ratio", type=float, default=1.0)
    parser.add_argument("--score_margin", type=float, default=0.0)
    parser.add_argument("--min_pos_score", type=float, default=0.0)
    parser.add_argument("--max_neg_score", type=float, default=1.0)
    

    
    args, unknown=parser.parse_known_args()
    
    reranker = BGERerankServer(model_path=args.reranker)
    
    asyncio.run(reranker_clean(reranker_model=reranker,
                                qrel_path=args.qrel_path,
                                output_path=args.output_path,
                                search_start_index=args.search_start_index,
                                search_end_index=args.search_end_index,
                                keep_neg_num=args.keep_neg_num,
                                score_ratio=args.score_ratio,
                                score_margin=args.score_margin,
                                min_pos_score=args.min_pos_score,
                                max_neg_score=args.max_neg_score
                                ))