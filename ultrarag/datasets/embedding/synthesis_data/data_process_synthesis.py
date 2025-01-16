import numpy as np
from tqdm import tqdm
import faiss
import os
import asyncio
from ultrarag.datasets.others.others import load_file, write_output
from ultrarag.modules.embedding import BGEServer


np.random.seed(42)

async def data_preprocess_synthesis(embedding_model:BGEServer,
                                    corpus_path:str,
                                    output_path:str,
                                    search_start_index:int,
                                    search_end_index:int):    
    
    # corpus_path = os.path.join(input_path, 'corpus.jsonl')
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
    
    # embedding_model = BGEClient(url_or_path=embedding_model_path)
    # print(docs)
    d_embeddings = await embedding_model.document_encode(docs)
    d_embeddings = [emb["dense_embed"] for emb in d_embeddings]
    d_embeddings = np.array(d_embeddings, dtype=np.float32)

    dim = d_embeddings.shape[1]
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
    similarity_d_index = []
    for i in tqdm(range(0, len(d_embeddings), batch_size)):
        batch_embeddings = d_embeddings[i:i+batch_size]
        _,_similarity_d_index = index.search(batch_embeddings, search_end_index)
        similarity_d_index = similarity_d_index + _similarity_d_index.tolist()
        
    sims = [([docs[similarity_d_index[i][j]]for j in range(search_start_index,search_end_index)]) for i in range(len(docs))]

    # serialize
    docs_dict = {}
    for i in range(len(docs)):
        docs_dict[docs[i]] = hash(docs[i])
    
    res = []
    for doc, sim_pairs in zip(docs, sims):
        # sim_pairs = [docs_dict[x] for x in sim_pairs]
        # res.append({"doc": docs_dict[doc], "sims": sim_pairs})
        res.append({"doc": doc, "sims": sim_pairs})
    
    # output_path = os.path.join(input_path, "pairs.jsonl")
    write_output(res, output_path, "jsonl")
    
    hashed_docs = [{"id": doc, "contents": _id} for _id, doc in docs_dict.items()]
    write_output(hashed_docs, corpus_path, "jsonl")

def data_preprocess_synthesis_main(parser):
    from ultrarag.modules.embedding import BGEServer
    
    parser.add_argument("--embed", required=True, type=str, help="embedding model path")
    parser.add_argument("--pooling", default="mean", type=str, help="pooling method")
    parser.add_argument("--corpus_path", required=True, type=str, help="raw chunk data")
    parser.add_argument("--output_path", required=True, type=str, help="output path")
    parser.add_argument("--search_start_index", type=int, default=1)
    parser.add_argument("--search_end_index", type=int, default=30)
    
    args, unknown=parser.parse_known_args()
    encoder = BGEServer(url_or_path=args.embed,pooling=args.pooling)
    
    asyncio.run(data_preprocess_synthesis(embedding_model=encoder,
                                            corpus_path=args.corpus_path,
                                            output_path=args.output_path,
                                            search_start_index=args.search_start_index,
                                            search_end_index=args.search_end_index))