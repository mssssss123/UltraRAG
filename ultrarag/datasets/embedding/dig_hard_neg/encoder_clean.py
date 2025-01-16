import numpy as np
from tqdm import tqdm
from joblib import Parallel, delayed
import os
from itertools import chain
from ultrarag.datasets.others.merge import load_file, write_output
from ultrarag.modules.embedding import BGEServer
import asyncio

async def encoder_clean(embedding_model:BGEServer,qrel_path:str,
                        output_path:str,search_start_index:int,search_end_index:int,keep_neg_num:int,
                        score_ratio:float, score_margin:float, min_pos_score:float, max_neg_score:float):
    
    # keep_neg_num = 7
    # score_ratio = 0.95
    
    # corpus_path = os.path.join(input_path, 'corpus.jsonl')
    # # query_path = os.path.join(input_path, 'query.jsonl')
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
    
    # doc_ids = list(docs_dict.keys())
    # docs = [docs_dict[doc_id] for doc_id in doc_ids]
    
    queries = [x["query"] for x in dataset]
    for i in range(len(dataset)):
        dataset[i]["neg"] = dataset[i]["neg"][search_start_index:search_end_index]
    # queries = [queries_dict[x["query"]] for x in dataset]
    # pos_ids = [x["pos"] for x in dataset]
    # negs_ids = [x["neg"] for x in dataset]
    # negs_ids = list(chain.from_iterable(negs_ids))
    
    # embedding_model = BGEClient(url_or_path=embedding_model_path)
    
    poss = [x["pos"] for x in dataset]
    negs = [x["neg"] for x in dataset]
    negs = list(chain.from_iterable(negs))
    
    # used_ids = set(negs_ids + list(chain.from_iterable(pos_ids)))
    docs = list(set(negs + list(chain.from_iterable(poss))))
    # docs = [ doc for doc in docs if doc in used_docs]
    doc_index = {x:i for i,x in enumerate(docs)}
    # docs = [ doc for doc in docs if doc["id"] in used_ids]
    # docs_dict = {x["contents"]:x["id"] for x in docs}
    # docs = list(set(list(docs_dict.keys())))
    # doc_ids = [docs_dict[x] for x in docs]
    # id_indices = {x:i for i,x in enumerate(doc_ids)}

    q_embeddings = await embedding_model.document_encode(queries)
    q_embeddings = [emb["dense_embed"] for emb in q_embeddings]
    q_embeddings = np.array(q_embeddings, dtype=np.float32)
    d_embeddings = await embedding_model.document_encode(docs)
    d_embeddings = [emb["dense_embed"] for emb in d_embeddings]
    d_embeddings = np.array(d_embeddings, dtype=np.float32)
    
    
    remove_indies = set()
    def func(i,q_e,ps):    
        for p in ps:
            ns = dataset[i]["neg"]
            n_es = [d_embeddings[doc_index[x]] for x in ns]
            p_e = d_embeddings[doc_index[p]]
            qp_sim = np.dot(q_e, p_e)
            l_nes = len(n_es)
            
            if qp_sim < min_pos_score:
                remove_indies.add(i)
            
            for j in range(l_nes-1,-1,-1):
                n_e = n_es[j]
                qn_sim = np.dot(q_e, n_e)
                
                if qn_sim > qp_sim * score_ratio or qn_sim + score_margin > qp_sim or qn_sim > max_neg_score:
                    n_es.pop(j)
                    dataset[i]["neg"].pop(j)
            l_nes = len(n_es)
            if l_nes == 0:
                continue

        if len(dataset[i]["neg"]) < keep_neg_num:
            remove_indies.add(i)

    Parallel(n_jobs=80,backend="threading")(delayed(func)(i,q_e,ps) for i,(q_e,ps) in tqdm(enumerate(zip(q_embeddings, poss))))
    dataset = [dataset[i] for i in range(len(dataset)) if i not in remove_indies]
    
    
    write_output( dataset,output_path, "jsonl")
    
    
def encoder_clean_main(parser):
    from ultrarag.modules.embedding import BGEServer
    
    parser.add_argument("--embed", required=True, type=str, help="embedding model path")
    parser.add_argument("--pooling", default="mean", type=str, help="pooling method")
    parser.add_argument("--query_instruction", type=str, default=None, help="query instruction")
    # parser.add_argument("--corpus_path", required=True, type=str, help="raw chunk data")
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
    
    encoder = BGEServer(url_or_path=args.embed,pooling=args.pooling, query_instruction=args.query_instruction)
    
    
    asyncio.run(encoder_clean(embedding_model=encoder,
                                # corpus_path=args.corpus_path,
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