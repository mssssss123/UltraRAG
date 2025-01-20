import csv
import json
import torch
import yaml
import asyncio
import argparse
import os
import random
import sys
from pathlib import Path
home_path = Path().resolve()
sys.path.append(home_path.as_posix())
from ultrarag.modules.llm import VllmServer
from UltraRAG.ultrarag.modules.embedding.embedding import EmbServer
from ultrarag.modules.knowledge_managment.knowledge_managment import Knowledge_Managment
from prompts import question_prompt, answer_prompt, keypoint_prompt

class DataGenerator:
    def __init__(self, model_name_or_path, config_path, embedding_model_path, knowledge_id, knowledge_stat_tab_path):
        """
        Initializes the dataset generator with the given parameters.

        Args:
            model_name_or_path (str): The path or name of the model to be used.
            config_path (str): The path to the configuration file.
            embedding_model_path (str): The path to the embedding model.
            knowledge_id (str): The identifier for the knowledge base.
            knowledge_stat_tab_path (str): The path to the knowledge statistics table.

        Attributes:
            config (dict): The loaded configuration parameters.
            sampling_params (dict): Parameters for sampling.
            vllm_params (dict): Parameters for the VllmServer.
            top_k (int): The top K value for retrieval, default is 5.
            method (str): The method for retrieval, default is "dense".
            knowledge_id (str): The identifier for the knowledge base.
            llm_service (VllmServer): The language model server instance.
            max_data_nums (int): The maximum number of data points, default is 5000.
            record_count (int): The current count of records processed.
            searcher (object): The searcher instance for knowledge management.
        """
        self.config = self.load_config(config_path)
        self.sampling_params = self.config["sampling_params"]
        self.vllm_params = self.config["VllmServer_params"]
        self.top_k = self.config.get('top_k', 5)
        self.method = self.config.get('method', "dense")
        self.knowledge_id = knowledge_id
        self.llm_service = VllmServer(base_url=model_name_or_path, **self.vllm_params)
        self.max_data_nums = self.config.get('max_data_nums', 5000)
        self.record_count = 0

        encoder = EmbServer(url_or_path=embedding_model_path)
        self.searcher = Knowledge_Managment.get_searcher(
            knowledge_id = [knowledge_id],
            embedding_model = encoder,
            knowledge_stat_tab_path = knowledge_stat_tab_path
        )

    def load_config(self, config_path):
        """
        Load prompts and sampling parameters from a YAML configuration file.

        Args:
            config_path (str): The path to the YAML configuration file.

        Returns:
            dict: A dictionary containing the configuration parameters.
        """
        with open(config_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    def generate_query(self, document):
        """
        Generate a query from the given document using a predefined prompt.

        Args:
            document (str): The document from which to generate the query.

        Returns:
            str: The generated query based on the document.
        """
        question = question_prompt.format(document=document)
        question_messages = [dict(role="user", content=question)]
        return self.llm_service.run(messages=question_messages, stream=False, **self.sampling_params)

    def generate_answer(self, document, question):
        """
        Generate the answer from the given document and question.

        Args:
            document (str): The document from which the answer is to be generated.
            question (str): The question for which the answer is to be generated.

        Returns:
            str: The generated answer.
        """
        answer = answer_prompt.format(document=document, question=question)
        answer_messages = [dict(role="user", content=answer)]
        return self.llm_service.run(messages=answer_messages, stream=False, **self.sampling_params)

    def generate_keypoints(self, question, answer):
        """
        Generate keypoints based on the provided question and answer.

        Args:
            question (str): The question to generate keypoints for.
            answer (str): The answer to generate keypoints for.

        Returns:
            dict: The generated keypoints as a dictionary.
        """
        keypoint = keypoint_prompt.format(question=question, answer=answer)
        keypoint_messages = [dict(role="user", content=keypoint)]
        return self.llm_service.run(messages=keypoint_messages, stream=False, **self.sampling_params)
    
    def generate_reference(self, question):
        """
        Generate reference based on the given question.

        Args:
            question (str): The question for which to generate references.

        Returns:
            list: A list of document contents retrieved based on the question.
        """
        top_docs = asyncio.run(self.searcher.search(query=question, topn=self.top_k, method=self.method))
        retrieval_result = [doc.content for doc in top_docs if hasattr(doc, "content")]
        return retrieval_result
    
    def process_chunk(self, chunk, line_idx, chunk_idx, outfile):
        """
        Processes a chunk of data, generates a query, answer, keypoints, and retrieval results, 
        and writes the results to an output file.
        Args:
            chunk (str): The chunk of data to be processed.
            line_idx (int): The index of the line in the input file.
            chunk_idx (int): The index of the chunk within the line.
            outfile (file object): The file object to write the results to.
        Returns:
            str: Returns "STOP" if the maximum number of records has been reached.
        """
        if self.record_count >= self.max_data_nums:
            return "STOP"
        
        question = self.generate_query(chunk)
        if not question:
            return

        answer = self.generate_answer(chunk, question)
        if not answer:
            return

        keypoint = self.generate_keypoints(question, answer)
        if not keypoint:
            return
        
        retrieval_result = self.generate_reference(question)
        if not retrieval_result:
            return

        result = {
            "file_index": line_idx,
            "chunk_index": chunk_idx,
            "chunk": chunk,
            "query": question,
            "ground_truth": answer,
            "keypoints": keypoint,
            "retrieval_result": retrieval_result,
        }

        outfile.write(json.dumps(result, ensure_ascii=False) + "\n")
        outfile.flush()

        self.record_count += 1
        if self.record_count >= self.max_data_nums:
            return "STOP"
            
    def process_data_async(self, output_path):
        """
        Process data from the CSV file asynchronously and generate the result.

        Args:
            output_path (str): The path where the processed data will be saved.

        Returns:
            None

        This method performs the following steps:
        1. Loads data from the input CSV file and records line and chunk indices.
        2. Shuffles the loaded data.
        3. Processes the shuffled data and writes the results to the output file.

        During processing, it prints the progress every 100 chunks and stops if the limit of 
        `self.max_data_nums` records is reached. Any JSON decoding errors encountered during 
        loading are printed with the line number.
        """
        input_path = next((f for f in self.searcher.chunk_files if self.knowledge_id in f), None)
        all_data = []

        # Step 1: Load data and record line and chunk indices
        with open(input_path, "r", encoding="utf-8") as infile:
            for line_idx, line in enumerate(infile):
                try:
                    data_array = json.loads(line.strip())
                    for chunk_idx, chunk in enumerate(data_array):
                        all_data.append((line_idx, chunk_idx, chunk))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON on line {line_idx + 1}: {e}")
                    continue

        # Step 2: Shuffle the data
        random.shuffle(all_data)

        # Step 3: Process shuffled data
        with open(output_path, "w", encoding="utf-8") as outfile:
            for idx, (line_idx, chunk_idx, chunk) in enumerate(all_data):
                result = self.process_chunk(chunk, line_idx, chunk_idx, outfile)
                if result == "STOP":
                    print(f"Reached the limit of {self.max_data_nums} records. Stopping.")
                    return
                if idx % 100 == 0: 
                    print(f"Processed {idx + 1} chunks out of {len(all_data)}")

        print(f"Generation completed, results have been saved in real-time to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate dataset")
    parser.add_argument("--output_path", type=str, required=True, help="Path to save the generated results (JSONL format).")
    parser.add_argument("--model_name_or_path", type=str, required=True, help="Path to the external model.")
    parser.add_argument("--config_path", type=str, required=True, help="Path to the YAML configuration file.")
    parser.add_argument("--embedding_model_path", type=str, required=True, help="Path to the embedding model.")
    parser.add_argument("--knowledge_id", type=str, required=True, help="Knowledge collection ID in Qdrant.")
    parser.add_argument("--knowledge_stat_tab_path", type=str, required=True, help="Path to knowledge statistics table.")

    args = parser.parse_args()

    data_generator = DataGenerator(args.model_name_or_path, args.config_path, args.embedding_model_path, args.knowledge_id, args.knowledge_stat_tab_path)
    data_generator.process_data_async(args.output_path)

if __name__ == '__main__':
    main()