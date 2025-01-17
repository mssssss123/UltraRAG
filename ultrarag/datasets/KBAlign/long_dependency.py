import json
import pickle
import re
from pathlib import Path
import sys
import os
from tqdm import tqdm
import argparse
import yaml
import asyncio
from ultrarag.modules.llm import VllmServer
from ultrarag.modules.embedding.bge_embedding import BGEServer
from ultrarag.modules.knowledge_managment.knowledge_managment import Knowledge_Managment
from ultrarag.datasets.KBAlign.prompts import long_dependency_prompt
from ultrarag.datasets.KBAlign.utils import get_nested_arrays, read_and_concatenate_jsonl
from sklearn.cluster import MiniBatchKMeans
from sentence_transformers import SentenceTransformer
import random
from typing import Optional


class LongDependecy:
    def __init__(self, output_dir, language, model_name_or_path, config_path, embedding_model_path, knowledge_id, knowledge_stat_tab_path,clustering):
        self.config = self.load_config(config_path)
        self.vllm_params = self.config["VllmServer_params"]
        self.top_k = self.config.get('top_k', 8)
        self.method = self.config.get('method', "dense")
        self.is_example = self.config.get('is_example', False)
        self.knowledge_id = knowledge_id
        self.llm_service = VllmServer(base_url=model_name_or_path, **self.vllm_params)
        self.clustering = clustering
        
        self.language = language
        self.output_dir1 = os.path.join(output_dir, "kbalign_long_final_data")
        output_filename1 = (f"kbalign_long_final_data.json")
        output_file1 = os.path.join(self.output_dir1, output_filename1)
        self.output_path = output_file1
        os.makedirs(self.output_dir1, exist_ok=True)  

        encoder = BGEServer(url_or_path=embedding_model_path,device="cuda:5")
        self.searcher = Knowledge_Managment.get_searcher(
            knowledge_id = [knowledge_id],
            embedding_model = encoder,
            knowledge_stat_tab_path = knowledge_stat_tab_path
        )
    
    def main(self):
        final_result = []
        is_example = "is_example" if self.is_example else "not_example"
        prompt_gen_q = long_dependency_prompt[self.language][is_example]["prompt_gen_q"]
        prompt_gen_a = long_dependency_prompt[self.language][is_example]["prompt_gen_a"]
        prompt_refine = long_dependency_prompt[self.language][is_example]["prompt_refine"] 
        chunk_fils =self.searcher.chunk_files
        if self.clustering:
            kb_data = self.cluster_data(read_and_concatenate_jsonl(chunk_fils))
        else:
            kb_data = get_nested_arrays(chunk_fils)
            
        for i, data in enumerate(tqdm(kb_data, desc="Processing data")):
            # todo
            questions, answers = [], []
            for d in data:
                # if self.is_example:
                #     example, example_index = rc.get_top_k(query=[d], documents=ex_questions,documents_path=args.documents_path, top_k=1)
                #     e_q = example[0]
                #     e_a = ex_data[example_index[0]]["answer"]
                #     prompt=prompt_gen_q.format(document=d, e_q=e_q, e_a=e_a)
                # else:
                prompt = prompt_gen_q.format(document=d)
                prompt_messages = [dict(role="user", content=prompt)]
                qs = self.llm_service.run(messages=prompt_messages, stream=False)
                qs = qs.split("\n")
                filtered_qs = [re.sub(r'^(\d+\.?)?\s*(question|问题)?:?\s*', "", q).strip() for q in qs if '?' in q or '？' in q]
                questions.extend(filtered_qs)
                
            for q in questions:
                # if self.is_example:
                #     e_q=example[0]
                #     e_a=ex_data[example_index[0]]["answer"]
                a = ""
                d_arr = self.searcher.search_with_data(query=q, data=data, top_k=10 if len(data) > 9 else 3, batch_size=512)
                for doc in d_arr:
                    # if args.is_example:
                        # prompt=prompt_gen_a.format(document=doc, e_q=e_q, e_a=e_a, q=q)
                    # else:
                    prompt = prompt_gen_a.format(document=doc, q=q)
                    prompt_messages = [dict(role="user", content=prompt)]
                    a = self.llm_service.run(messages=prompt_messages, stream=False)
                    if "none" not in a.lower():
                        a += f"\n{a}"
                prompt = prompt_refine.format(q=q, a=a)
                prompt_messages = [dict(role="user", content=prompt)]
                refined_answer = self.llm_service.run(messages=prompt_messages, stream=False)
                answers.append(refined_answer)

            try:
                with open(self.output_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                existing_data = []

            for idx, (q, a) in enumerate(zip(questions, answers)):
                include_references = random.choice([True, False])
                if include_references:
                    most_similar_docs = asyncio.run(self.searcher.search(query=q, topn=self.top_k, method=self.method))
                    format_references = "\n".join(
                        [f"{i+1}. {item}" for i, item in enumerate(most_similar_docs)]
                    )
                    if self.language == "English":
                        user_message = {
                            "role": "user",
                            "content": (
                                "User: You are an expert who has read a lot of knowledge base. "
                                "Please answer the question according to the content of the KB. "
                                "You can refer to some segments from the KB to help you answer the question. "
                                f"References:\n{format_references}\n"
                                f"Now the question is: {q}\nPlease answer this question."
                            )
                        }
                    else:
                        user_message = {
                            "role": "user",
                            "content": (
                                "User: 你是一个法律知识专家，"
                                "请你根据知识库直接回答问题"
                                "你可以参考一些知识库的片段帮助你回答问题。 "
                                f"参考资料:\n{format_references}\n"
                                f"现在的问题是: {q}\n请你回答这个问题。"
                            )
                        }
                else:
                    if self.language == "English":
                        user_message = {
                            "role": "user",
                            "content": (
                                "User: You are an expert who has read a lot of knowledge base. "
                                "Please answer the question according to the content of the KB. "
                                f"Now the question is: {q}\nPlease answer this question."
                            )
                        }
                    else:
                        user_message = {
                            "role": "user",
                            "content": (
                                "User: 你是一个法律知识专家，"
                                "请你根据知识库直接回答问题"
                                f"现在的问题是: {q}\n请你回答这个问题。"
                            )
                        }
                assistant_message = {
                    "role": "assistant",
                    "content": a
                }
                dialog_entry = {
                    "messages": [user_message, assistant_message],
                    "golden_reference": None
                }
                final_result.append(dialog_entry)
                existing_data.append(dialog_entry)

            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=4, ensure_ascii=False)

    def cluster_data(self, sentences_data):
        model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        embeddings = model.encode(sentences_data)
        n_clusters = len(sentences_data) // 10
        kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=42, batch_size=100)
        kmeans.fit(embeddings)
        clusters = [[] for _ in range(n_clusters)]
        for idx, label in enumerate(kmeans.labels_):
            if len(clusters[label]) < 10:
                clusters[label].append(sentences_data[idx])
        return [''.join(cluster) for cluster in clusters]
    
    def load_config(self, config_path):
        """Load prompts and sampling parameters from a YAML configuration file."""
        with open(config_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)




