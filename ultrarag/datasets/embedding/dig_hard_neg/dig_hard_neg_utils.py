import numpy as np
from tqdm import tqdm
import faiss
import os
from ultrarag.datasets.others.merge import load_file, write_output
from ultrarag.modules.embedding import EmbServer
import asyncio

async def dig_hard(embedding_model:EmbServer,corpus_path:str,qrel_path:str,
                   output_path:str,search_start_index:int,search_end_index:int):
    """
    Asynchronously performs hard negative mining for a given set of queries and documents using an embedding model.
    Args:
        embedding_model (EmbServer): The embedding model used to encode documents and queries.
        corpus_path (str): Path to the corpus file containing documents.
        qrel_path (str): Path to the qrel file containing query relevance information.
        output_path (str): Path to the output file where the results will be saved.
        search_start_index (int): The starting index for the range of hard negatives to consider.
        search_end_index (int): The ending index for the range of hard negatives to consider.
    Returns:
        None: The function writes the output to the specified output_path.
    """
    # search_start_index = 1
    # search_end_index = 30
    
    # corpus_path = os.path.join(input_path, 'corpus.jsonl')
    # query_path = os.path.join(input_path, 'query.jsonl')
    # qrel_path = os.path.join(input_path, 'train.jsonl')
    # output_qrel_path = os.path.join(input_path, "diged.jsonl")

    docs = load_file(corpus_path)
    try:
        docs = [x['contents'] for x in docs]
    except:
        new_docs = []
        for doc in docs:
            output_data = {}
            output_data["contents"] = doc
            new_docs.append(output_data)
        docs = new_docs
    
    # docs_dict = {}
    # for doc in docs:
    #     docs_dict[doc['id']] = doc["contents"]
        
    # queries = load_file(query_path)
    # queries_dict = {}
    # for query in queries:
        # queries_dict[query['id']] = query["query"]
    
    dataset = load_file(qrel_path)
    
    # doc_ids = list(docs_dict.keys())
    # docs = [docs_dict[doc_id] for doc_id in doc_ids]
    
    # queries = [queries_dict[x["query"]] for x in dataset]
    queries = [x["query"] for x in dataset]
    # TODO: Add instruction
    
    # embedding_model = EmbClient(url_or_path=embedding_model_path)

    q_embeddings = await embedding_model.document_encode(queries)
    q_embeddings = [emb["dense_embed"] for emb in q_embeddings]
    q_embeddings = np.array(q_embeddings, dtype=np.float32)
    d_embeddings = await embedding_model.document_encode(docs)
    d_embeddings = [emb["dense_embed"] for emb in d_embeddings]
    d_embeddings = np.array(d_embeddings, dtype=np.float32)
    
    dim = q_embeddings.shape[1]
    measure = faiss.METRIC_INNER_PRODUCT
    param =  "Flat"
    index = faiss.index_factory(dim, param, measure)
    # co = faiss.GpuMultipleClonerOptions()
    # co.shard = True
    # co.useFloat16 = True
    # index = faiss.index_cpu_to_all_gpus(index, co=co)
    index.add(d_embeddings)
    
    index.nprobe = 10
    batch_size = 4096
    similarity_q_index = []
    for i in tqdm(range(0, len(q_embeddings), batch_size)):
        batch_embeddings = q_embeddings[i:i+batch_size]
        _,_similarity_q_index = index.search(batch_embeddings, search_end_index)
        similarity_q_index = similarity_q_index + _similarity_q_index.tolist()
        
    # negs = [([doc_ids[similarity_q_index[i][j]] for j in range(search_start_index, search_end_index)]) for i in range(len(dataset))]
    negs = [([docs[similarity_q_index[i][j]] for j in range(search_start_index, search_end_index)]) for i in range(len(dataset))]
    
    for data,neg in tqdm(zip(dataset,negs), total=len(dataset)):
        data["neg"] = neg
    
    write_output(dataset,output_path,"jsonl")
    
    
def dig_hard_main(parser):
    import argparse
    from ultrarag.modules.embedding import EmbServer
    parser.add_argument("--embed", required=True, type=str, help="embedding model path")
    parser.add_argument("--pooling", default="mean", type=str, help="pooling method")
    parser.add_argument("--query_instruction", type=str, default=None, help="query instruction")
    parser.add_argument("--corpus_path", required=True, type=str, help="raw chunk data")
    parser.add_argument("--qrel_path", required=True, type=str, help="raw chunk data")
    parser.add_argument("--output_path", required=True, type=str, help="output path")
    parser.add_argument("--search_start_index", type=int, default=1)
    parser.add_argument("--search_end_index", type=int, default=30)
    # parser.add_argument("--input_path", type=str, default=".")
    # args.add_argument("--embedding_model_path", type=str, default="http://localhost:12306/embed")
    args, unknown=parser.parse_known_args()

    
    encoder = EmbServer(url_or_path=args.embed,pooling=args.pooling,query_instruction=args.query_instruction)
    
    asyncio.run(dig_hard(embedding_model=encoder, 
                         corpus_path=args.corpus_path,
                            qrel_path=args.qrel_path,
                            output_path=args.output_path,
                            search_start_index=args.search_start_index,
                            search_end_index=args.search_end_index
                            ))