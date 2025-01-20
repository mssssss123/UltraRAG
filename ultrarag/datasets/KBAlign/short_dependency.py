import json
import os
import re
from tqdm import tqdm
import argparse
import glob
import random
import streamlit as st
from ultrarag.datasets.KBAlign.filter_words import filter_words, filter_words2
import yaml
import asyncio
from ultrarag.modules.llm import VllmServer
from ultrarag.modules.embedding.bge_embedding import BGEServer
from ultrarag.modules.knowledge_managment.knowledge_managment import Knowledge_Managment
from ultrarag.datasets.KBAlign.prompts import short_dependency_prompt, merge_data_prompt
from ultrarag.datasets.KBAlign.utils import count_words, read_and_concatenate_jsonl, iter_jsonl, dump_jsonl



class ShortDependecy:
    def __init__(self, output_dir, language, model_name_or_path, config_path, 
                
                 functions_to_run, embedding_model_path, knowledge_id, knowledge_stat_tab_path):
        """
        Initializes the class with the given parameters.
        Args:
            output_dir (str): The directory where output files will be saved.
            language (str): The language to be used.
            model_name_or_path (str): The base URL or path for the VllmServer model.
            config_path (str): The path to the configuration file.
            functions_to_run (list): A list of functions to run.
            embedding_model_path (str): The path to the embedding model.
            knowledge_id (str): The ID of the knowledge base.
            knowledge_stat_tab_path (str): The path to the knowledge statistics table.
        Attributes:
            config (dict): The configuration loaded from the config file.
            vllm_params (dict): Parameters for the VllmServer.
            top_k (int): The top K results to consider, default is 5.
            method (str): The method to use, default is "dense".
            knowledge_id (str): The ID of the knowledge base.
            llm_service (VllmServer): The VllmServer instance.
            language (str): The language to be used.
            output_dir1 (str): The directory for the generated data output.
            output_dir2 (str): The directory for the final data output.
            gen_data_output_file (str): The file path for the generated data output.
            merge_output_file (str): The file path for the final data output.
            functions_to_run (list): A list of functions to run.
            searcher (object): The searcher instance for knowledge management.
        """
        
        self.config = self.load_config(config_path)
        self.vllm_params = self.config["VllmServer_params"]
        self.top_k = self.config.get('top_k', 5)
        self.method = self.config.get('method', "dense")
        self.knowledge_id = knowledge_id
        self.llm_service = VllmServer(base_url=model_name_or_path, **self.vllm_params)
        
        self.language = language
        self.output_dir1 = os.path.join(output_dir, "kbalign_short_gen_data")
        self.output_dir2 = os.path.join(output_dir, "kbalign_short_final_data")
        output_filename1 = (f"kbalign_short_gen_data.jsonl")
        output_filename2 = (f"kbalign_short_final_data.jsonl")
        output_file1 = os.path.join(self.output_dir1, output_filename1)
        output_file2 = os.path.join(self.output_dir2, output_filename2)
        self.gen_data_output_file = output_file1
        self.merge_output_file = output_file2
        self.functions_to_run = functions_to_run
        os.makedirs(self.output_dir1, exist_ok=True)  
        os.makedirs(self.output_dir2, exist_ok=True)  
        encoder = BGEServer(url_or_path=embedding_model_path)
        self.searcher = Knowledge_Managment.get_searcher(
            knowledge_id = [knowledge_id],
            embedding_model = encoder,
            knowledge_stat_tab_path = knowledge_stat_tab_path
        )

    def load_config(self, config_path):
        """Load prompts and sampling parameters from a YAML configuration file."""
        with open(config_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    def get_qa(self, content):
        """
        Extracts question-answer pairs from the provided content using a language model service.

        Args:
            content (str): The input content from which to generate question-answer pairs.

        Returns:
            tuple: A tuple containing two lists:
                - questions (list of str): The list of extracted questions.
                - answers (list of str): The list of corresponding answers.

        Raises:
            Any exceptions raised by the language model service or during processing.

        Notes:
            - The function uses a predefined prompt template based on the language to generate question-answer pairs.
            - It filters out invalid question-answer pairs based on word count, presence of certain characters, and specific keywords.
            - The function supports both English and Chinese languages.
        """
        questions = []
        answers = []
        prompt = short_dependency_prompt[self.language]["q_a_pair"].format(content=content)
        prompt_messages = [dict(role="user", content=prompt)]
        q_a = self.llm_service.run(messages=prompt_messages, stream=False)
        q_a = [q_a]
        q_as = []
        q_as = q_as+q_a[0].split("\n")
        generated_qa=[]
        temp_dict={"question":"","answer":""}
        c=1
        for i,qa in enumerate(q_as):
            if not qa:
                continue
            if c==1:
                temp_dict["question"]=qa
                c=2
            elif c==2:
                temp_dict["answer"]=qa
                generated_qa.append(temp_dict)
                temp_dict={"question":"","answer":""}
                c=1
        for i,qa in enumerate(generated_qa):
            q_count=count_words(qa["question"])
            a_count=count_words(qa["answer"])
            if q_count<4 or q_count>25 or a_count>70 or a_count=="" or ("?" not in qa["question"] and "？" not in qa["question"]) or any(neg in qa["answer"].lower() for neg in filter_words2) or any(w in qa["question"].lower() for w in filter_words2) or ("?" in qa["answer"] or "？" in qa["answer"]):
                continue
            if self.language=="English":
                question = re.sub(r'^(\d+\.?)?\s*(question)?:?\s*', "", qa["question"], flags=re.IGNORECASE).strip()
                answer = re.sub(r'^(\d+\.?)?\s*(answer)?:?\s*', "", qa["answer"], flags=re.IGNORECASE).strip()
            elif self.language=="Chinese":
                question = re.sub(r'问题\s*\d*[：:]*\s*', "", qa["question"], flags=re.IGNORECASE).strip()
                answer = re.sub(r'答案\s*\d*[：:]*\s*', "", qa["answer"], flags=re.IGNORECASE).strip()
            questions.append(question)
            answers.append(answer)
        return questions, answers

    def get_valid_qa(self, content, max_retries=3):
        retry_count = 0
        while retry_count < max_retries:
            questions, answers = self.get_qa(content)
            if questions and answers:
                return questions, answers
            retry_count += 1
        return [], []

    def write_to_file(self, data):
        progress_file = f"{self.output_dir1}/{os.path.splitext(os.path.basename(self.gen_data_output_file))[0]}_progress.txt"
        if os.path.exists(progress_file):
            with open(progress_file, "r") as pf:
                start_id = int(pf.read().strip()) + 1
        else:
            start_id = 0
        for i, item in enumerate(
            tqdm(data[start_id:], initial=start_id, total=len(data))
        ):
            # if i % 4000 != 0:
            #     continue
            # todo
            try:
                item = item.strip()
                line_data = {"id": i, "content": item}
                (line_data["questions"], line_data["answers"]) = self.get_valid_qa(item)
                line = json.dumps(line_data, ensure_ascii=False)
                with open(self.gen_data_output_file, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
                start_id += 1
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(e)
        if os.path.exists(progress_file):
            os.remove(progress_file)

    def gen_data(self):
        chunk_files_path = self.searcher.chunk_files
        segments = read_and_concatenate_jsonl(chunk_files_path=chunk_files_path)
        self.write_to_file(segments)
    

    def get_messages_list(self, user_contents, assistant_contents, example_idx, output_path,reference=None):
        """
        Generates a list of message dictionaries from user and assistant contents and saves them to a JSONL file.

        Args:
            user_contents (list): A list of strings containing the user's messages.
            assistant_contents (list): A list of strings containing the assistant's messages.
            example_idx (int): An index or identifier for the example.
            output_path (str): The file path where the JSONL file will be saved.
            reference (optional): Additional reference information to be included in the JSONL file.

        Returns:
            None
        """
        messages_list = []
        for i in range(len(user_contents)):
            messages = [
                {"role": "user", "content": user_contents[i]},
                {"role": "assistant", "content": assistant_contents[i]},
            ]
            messages_list.append({"messages": messages})
        dump_jsonl(messages_list, example_idx, output_path,reference)


    def process_files(self, input_paths, output_path, function_list):
        """
        Processes a list of input files by applying a list of functions to each line of the files and writes the processed data back to the files.

        Args:
            input_paths (list of str): List of paths to the input files to be processed.
            output_path (str): Path to the output directory where processed files will be saved.
            function_list (list of callable): List of functions to be applied to each line of the input files. Each function should accept three arguments: the data line, the output path, and the input path.

        Returns:
            None
        """
        for input_path in input_paths:
            in_file=list(iter_jsonl(input_path))
            for line_idx, data in enumerate(tqdm(in_file, desc=f"Processing {input_path}")):
                for func in function_list:
                    func(data, output_path, input_path)
            with open(input_path, "w", encoding="utf8") as file:
                for item in in_file:
                    file.write(json.dumps(item) + '\n')

    def check_and_update_references(self, data, key, qid, content):
        """
        Check and update references in the provided data dictionary.

        This method ensures that the specified key in the data dictionary is associated with a list of the same length as the 'questions' list.
        If the key does not exist or is not a list of the correct length, it initializes it with empty strings.
        Then, it updates the list at the specified key with the provided content at the given question ID (qid).

        Args:
            data (dict): The data dictionary containing the references and questions.
            key (str): The key in the data dictionary to check and update.
            qid (int): The question ID indicating the position in the list to update.
            content (str): The content to insert at the specified position.

        Returns:
            dict: The updated data dictionary.

        Raises:
            IndexError: If the provided qid is out of range.
        """
        if key not in data or not isinstance(data[f'{key}'], list) or len(data[f'{key}']) != len(data.get('questions')):
            data[f'{key}'] = ['' for _ in data.get('questions')]
        if 0 <= qid < len(data[f'{key}']):
            data[f'{key}'][qid] = content
        else:
            raise IndexError("Provided qid is out of range.")
        return data

    # q->a
    def function_q(self, data, output_path, input_path):
        """
        Processes a dataset of questions and answers, formats them into user and assistant content, 
        and generates a list of messages.

        Args:
            data (dict): A dictionary containing the dataset with keys "questions", "answers", "id", 
                         and optionally "content".
            output_path (str): The path where the output will be saved.
            input_path (str): The path where the input data is located.

        Returns:
            None
        """
        user_contents = []
        assistant_contents = []
        for i in range(0, len(data["questions"])):
            if data["questions"][i] and data["answers"][i]:
                prompt0 = merge_data_prompt[self.language]["prompt0"]
                prompt2 = merge_data_prompt[self.language]["prompt2"]
                prompt3 = merge_data_prompt[self.language]["prompt3"]
                user_content = "User: "+prompt0+f'{prompt2}'+f'{data["questions"][i]}'+f'{prompt3}\nAssistant: '
                user_contents.append(user_content)
                assistant_contents.append(data["answers"][i])
        self.get_messages_list(user_contents, assistant_contents, data["id"], output_path,data.get("content"))

    # q+r->a
    def function_qr(self, data, output_path, input_path):
        """
        Processes a dataset of questions and answers, retrieves top documents for each question,
        formats the data into user and assistant content, and saves the results to the specified output path.
        Args:
            data (dict): A dictionary containing "questions" and "answers" lists.
            output_path (str): The path where the output will be saved.
            input_path (str): The path where the input data is located.
        Returns:
            None
        """
        user_contents = []
        assistant_contents = []
        for i in range(0, len(data["questions"])):
            if data["questions"][i] and data["answers"][i]:
                query=data["questions"][i]
                top_docs = asyncio.run(self.searcher.search(query=query, topn=self.top_k, method=self.method))
                format_references = "\n".join(
                    [f"{k+1}. {item}" for k, item in enumerate(top_docs)]
                )
                prompt0 = merge_data_prompt[self.language]["prompt0"]
                prompt1 = merge_data_prompt[self.language]["prompt1"]
                prompt2 = merge_data_prompt[self.language]["prompt2"]
                prompt3 = merge_data_prompt[self.language]["prompt3"]    
                user_content = "User: "+prompt0+prompt1+format_references+f'\n{prompt2}'+f'{data["questions"][i]}'+f'\n{prompt3} \nAssistant: '
                user_contents.append(user_content)
                assistant_content = f'{data["answers"][i]}'
                assistant_contents.append(assistant_content)
                data=self.check_and_update_references(data=data,key="references",qid=i,content=format_references)
                
        self.get_messages_list(user_contents, assistant_contents, data["id"], output_path)
        
    def merge_data(self):
        input_paths = glob.glob(os.path.join(self.output_dir1, "*"))
        fuc_list = []
        available_functions = {
            "function_q": self.function_q,
            "function_qr": self.function_qr,
        }

        for func_name in self.functions_to_run:
            if func_name in available_functions:
                fuc_list.append(available_functions[func_name])
        self.process_files(input_paths, self.merge_output_file, fuc_list)
        self.transfer_json()

    def transfer_json(self):
        data_messages = list(iter_jsonl(self.merge_output_file))
        for item in data_messages:
            if 'golden_reference' in item:
                item['data']['golden_reference'] = item['golden_reference']
        data_messages = [item['data'] for item in data_messages]
        
        out_file = os.path.splitext(self.merge_output_file)[0] + ".json"
        with open(out_file, 'w') as file:
            json.dump(data_messages, file, ensure_ascii=False, indent=4)
            

