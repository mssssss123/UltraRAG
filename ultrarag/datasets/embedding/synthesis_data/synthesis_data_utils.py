from tqdm import tqdm
from ultrarag.datasets.others.others import load_file, add_output
from ultrarag.modules.llm import HuggingfaceClient
from ultrarag.datasets.embedding.synthesis_data.prompts import SHOT_EN_PROMPT, SHOT_ZH_PROMPT, FEW_SHOT_NEG_ZH_PROMPT, ZERO_SHOT_NEG_ZH_PROMPT, FEW_SHOT_NEG_EN_PROMPT, ZERO_SHOT_NEG_EN_PROMPT
import os
import numpy as np
from joblib import Parallel, delayed
import json
import asyncio
from ultrarag.modules.llm import OpenaiLLM#, VllmServer

np.random.seed(42)

def praser_doc(input_doc:str, start_prefix:str="Query:"):
    start_index = input_doc.rfind(start_prefix)
    if start_index != -1:
        output = input_doc[start_index+len(start_prefix):]
        return output.strip()
    else:
        return input_doc

async def synthesis_data(generate_model: OpenaiLLM,
                        #  corpus_path:str
                         language:str,
                         input_pair_path:str, output_path:str, 
                         query_num_per_corpus:int, corpus_sample_num:int,
                         negs_start_index:int, negs_end_index:int,
                         shot_num:int, shot_file:str=None, input_prompt_path:str=None,
                         query_path:str=None, corpus_path:str=None
                         ):

    
    # query_num_per_corpus = 1
    # corpus_sample_num = 1
    # negs_start_index = 0
    # negs_end_index = 1
    # shot_num = 1
    has_shot = False
    
    if shot_num > 0 and shot_file is not None:
        has_shot = True
    
    if language == "zh":
        perfix = "查询："
        if has_shot:
            shot_prompt = SHOT_ZH_PROMPT
            input_prompt = FEW_SHOT_NEG_ZH_PROMPT
        else:
            input_prompt = ZERO_SHOT_NEG_ZH_PROMPT
    else:
        perfix = "Query:"
        if has_shot:
            shot_prompt = SHOT_EN_PROMPT
            input_prompt = FEW_SHOT_NEG_EN_PROMPT
        else:
            input_prompt = ZERO_SHOT_NEG_EN_PROMPT
    
    if input_prompt_path is not None:
        with open(input_prompt_path, "r") as f:
            input_prompt = f.read()

    # shot_prompt = SHOT_ZH_PROMPT
    # input_prompt = FEW_SHOT_NEG_ZH_PROMPT
    
    # inputs_path = os.path.join(input_path,"pairs.jsonl")
    # shots_path = os.path.join(input_path,"shots.jsonl")
    # corpus_path = os.path.join(input_path,"corpus.jsonl")
    # # output_query_path = os.path.join(input_path,"synthesis_query.jsonl")
    # output_qrel_path = os.path.join(input_path,"synthesis_qrel.jsonl")
    
    # docs = load_file(corpus_path)
    # docs = [x['contents'] for x in docs]
    # docs_dict = {}
    # for doc in docs:
    #     docs_dict[doc['id']] = doc["contents"]
    

    
    inputs = load_file(input_pair_path)
    
    if corpus_path is not None:
        corpus_reverse_dict = {}
        for _input in inputs:
            corpus_reverse_dict[_input["doc"]] = hash(_input["doc"])
        corpus_list = [{"id":v, "contents":k} for k,v in corpus_reverse_dict.items()]
        add_output(corpus_list, corpus_path, "jsonl")
    
    if has_shot:
        try:
            shots = load_file(shot_file)    
            shots = [x['query'] for x in shots]
        except FileNotFoundError:
            shots = []
    
    # generate_model =  HuggingfaceClient(url=generate_model_url)
    outputs = []

    input_prompts = []
    # pos_ids = []
    poss = []
    np.random.shuffle(inputs)
    inputs = inputs[:corpus_sample_num]
    # for _input in tqdm(inputs):
    def func(_input):
        pos = _input["doc"]
        # pos = docs_dict[_input["doc"]]
        # pos_id = _input["doc"]
        _input["sims"] = np.random.choice(_input["sims"][negs_start_index: negs_end_index], query_num_per_corpus, replace=False)
        for neg in _input["sims"]:
            # neg = docs_dict[neg]
            if has_shot:
                shot_indies = np.random.choice(len(shots),shot_num,replace=False)
                shot = "\n".join([shot_prompt.format(i=i,query=_shot) for i, _shot in enumerate(shot_indies)])
                _input_prompt = input_prompt.format(doc_a=pos,doc_b=neg, shot=shot)
            else:
                _input_prompt = input_prompt.format(doc_a=pos,doc_b=neg)
            
            input_prompts.append(_input_prompt)
            # pos_ids.append(pos_id)
            poss.append(pos)

    Parallel(n_jobs=30,backend="threading")(delayed(func)(_input) for _input in tqdm(inputs))
    
    if query_path is not None and corpus_path is not None:
        with open(output_path, "w") as f:
            f.write(f"query-id\tcorpus-id\tscore\n")
    
        
        
    for i, ctx in tqdm(enumerate(input_prompts), desc=""):
        messages = [dict(role="user", content=ctx)]
        resp = await generate_model.arun(messages=messages, stream=False)#, max_tokens=512)
        try:
            query = praser_doc(resp, start_prefix=perfix)
            # print(resp["data"][0])
            # query_id = hash(query)
            # _query = dict(id=query_id, text=query)
            # add_output([_query], output_query_path, "jsonl")
            
            # _item = dict(query=query_id, pos=[pos_ids[i]], vanilla_output=ctx)
            if query_path is not None:
                query_id = hash(query)
                _item = dict(contents=query, id=hash(query))
                add_output([_item], query_path, "jsonl")
                if corpus_path is not None:
                    with open(output_path, "a") as f:
                        f.write(f"{query_id}\t{corpus_reverse_dict[poss[i]]}\t1\n")                
            if query_path is None or corpus_path is None:
                _item = dict(query=query, pos=[poss[i]], vanilla_output=resp)
                add_output([_item], output_path, "jsonl")
        except:
            # print(json.load(resp))
            pass
    
def synthesis_data_main(parser):
    import argparse
    from ultrarag.modules.llm import OpenaiLLM
    
    parser.add_argument("--api_key", required=True, type=str)
    parser.add_argument("--base_url", required=True, type=str)
    parser.add_argument("--model_name", required=True, type=str)
    

    parser.add_argument("--language", required=True, type=str, help="language")
    parser.add_argument("--input_pair_path", required=True, type=str, help="input pair path")
    parser.add_argument("--output_path", required=True, type=str, help="output path")
    parser.add_argument("--query_num_per_corpus", required=True, type=int, help="query num per corpus")
    parser.add_argument("--corpus_sample_num", default=-1, type=int, help="corpus sample num")
    parser.add_argument("--negs_start_index", default=0, type=int, help="negs start index")
    parser.add_argument("--negs_end_index", default=20, type=int, help="negs end index")
    parser.add_argument("--shot_num", default=0, type=int, help="shot num")
    parser.add_argument("--shot_file", default=None, type=str, help="shot file")
    parser.add_argument("--input_prompt_path", default=None, type=str, help="input prompt path")
    parser.add_argument("--query_path", default=None, type=str, help="save query")
    parser.add_argument("--corpus_path", default=None, type=str, help="save corpus")
    
    args, unknown=parser.parse_known_args()
    llm = OpenaiLLM(base_url=args.base_url, api_key=args.api_key, model=args.model_name)
    # llm = VllmServer(base_url=args.base_url)
    
    asyncio.run(synthesis_data(generate_model=llm,
                               language=args.language,
                               input_pair_path=args.input_pair_path,
                               output_path=args.output_path,
                               query_num_per_corpus=args.query_num_per_corpus,
                               corpus_sample_num=args.corpus_sample_num,
                               negs_start_index=args.negs_start_index,
                               negs_end_index=args.negs_end_index,
                               shot_num=args.shot_num,
                               shot_file=args.shot_file,
                               input_prompt_path=args.input_prompt_path,
                               query_path=args.query_path,
                               corpus_path=args.corpus_path
                               ))