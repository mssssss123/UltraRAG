import json
import yaml
import torch
from tqdm import tqdm
from transformers import AutoTokenizer
from torch.utils.data import Dataset, DataLoader
from vllm import LLM, SamplingParams
import argparse
from pathlib import Path
import sys
home_path = Path().resolve()
sys.path.append(home_path.as_posix())

from ultrarag.modules.llm import VllmServer
from ultrarag.datasets.RankCoT.prompts import PROMPT_DICT

class COTGenerator:
    def __init__(self, input_path, output_path, model_name_or_path, config_path):
        """Initialize DPO data processor.

        This class processes data for Direct Preference Optimization (DPO) by loading configurations,
        setting up tokenizer and LLM service.

        Args:
            input_path (str): Path to the input data directory/file.
            output_path (str): Path where processed data will be saved.
            model_name_or_path (str): Name or path of the pretrained model to use.
            config_path (str): Path to the YAML configuration file.

        Attributes:
            config (dict): Loaded configuration from YAML file.
            tokenizer: Tokenizer initialized from the specified model.
            llm_service: VLLM server instance for language model inference.
            batch_size (int): Batch size for processing, defaults to 4.
            is_llama_style (bool): Flag indicating if using LLaMA-style formatting, defaults to True.
            Augment_template (str): Template for augmented prompts with background information.
            QA_template (str): Template for basic question-answer formatting.
        """
        self.input_path = input_path
        self.output_path = output_path
        self.model_name_or_path = model_name_or_path
        self.config_path = config_path

        self.config = self.load_yaml_config(config_path)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        self.vllm_params = self.config["VllmServer_params"]
        self.llm_service = VllmServer(base_url=self.model_name_or_path, **self.vllm_params)

        self.batch_size = self.config.get('batch_size', 4)

       
    def load_yaml_config(self, config_path):
        """Load YAML configuration file.

        Args:
            config_path (str): Path to the YAML configuration file.

        Returns:
            dict: Loaded configuration as a dictionary.

        Raises:
            yaml.YAMLError: If there is an error parsing the YAML file.
            FileNotFoundError: If the configuration file is not found.
            IOError: If there is an error reading the file.
        """
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    def read_jsonl(self):
        """
        Reads the input JSONL (JSON Lines) file specified by `self.input_path`.

        Each line in the JSONL file is expected to be a valid JSON object. This method reads each line,
        parses it as a JSON object, and appends it to a list. Additionally, it assigns a unique `id`
        to each JSON object based on its line number in the file.

        Returns:
            list: A list of dictionaries, where each dictionary represents a JSON object from the file
                  with an added `id` field indicating its line number.
        """
        data = []
        with open(self.input_path, 'r', encoding='utf-8') as f:
            for idx, line in enumerate(f):
                item = json.loads(line.strip())
                
                data.append(item)
        return data
    def create_dataset(self, input_data):
        """
        Create the dataset using the input data and tokenizer.

        Args:
            input_data (Any): The input data to be used for creating the dataset.

        Returns:
            DPODataset: An instance of the DPODataset class initialized with the input data, tokenizer, and configuration.
        """
        return COTDataset(input_data, self.tokenizer, self.config)
    
    def generate(self, dataloader, sampling_params_dict):
        """
        Run the model and generate results.
        Args:
            dataloader (DataLoader): A DataLoader object that provides batches of data.
            temperature_list (list): A list of temperature values to use for generation.
            sampling_params_dict (dict): A dictionary of sampling parameters.
        Returns:
            dict: A dictionary where keys are item IDs and values are dictionaries containing 
              the item ID and a list of generated contexts with their respective temperatures 
              and types ('raw' or 'aug').
        """
        """Run the model and generate results."""
        output_data = []

        params_dict = {
                "n": sampling_params_dict.get('n', 5),
                "best_of": sampling_params_dict.get('best_of', 5),
                "presence_penalty": sampling_params_dict.get('presence_penalty', 1.0),
                "frequency_penalty": sampling_params_dict.get('frequency_penalty', 0.0),
                "temperature": sampling_params_dict.get('temperature', 1.0),
                "top_p": sampling_params_dict.get('top_p', 0.8),
                "top_k": sampling_params_dict.get('top_k', -1),
                "stop": sampling_params_dict.get('stop', None),
                "stop_token_ids": sampling_params_dict.get('stop_token_ids', None),
                "ignore_eos": sampling_params_dict.get('ignore_eos', False),
                "max_tokens": sampling_params_dict.get('max_tokens', 100),
                "logprobs": sampling_params_dict.get('logprobs', None),
                "prompt_logprobs": sampling_params_dict.get('prompt_logprobs', None),
                "skip_special_tokens": sampling_params_dict.get('skip_special_tokens', True),
        }

        sampling_params = SamplingParams(**params_dict)

        for batch in tqdm(dataloader):
            input_prompt = batch['input_prompt']
            outputs = self.llm_service._generator.generate(input_prompt, sampling_params)
            cleaned_outputs = [output.outputs[0].text for output in outputs]
            maxindex = len(batch['id'])
            for index in range(maxindex):
                id=batch['id'][index]
                datatype = batch['data_type'][index]
                query = batch['query'][index]
                passage = batch['passage'][index]
                ground_truth = batch['ground_truth'][index]
                model_output = cleaned_outputs[index] 
                output_item = {
                    "id":id,
                    "data_type":datatype,
                    "query": query,
                    "model_output": model_output,
                    "passage": passage,
                    "ground_truth":ground_truth
                    }
                output_data.append(output_item)
      

        return output_data


    def save_results(self, saved_data):
        """
        Save the updated results to the output file.

        Args:
            updated_data (list): A list of dictionaries or objects to be saved to the output file.

        The method writes each item in the updated_data list to the output file in JSON format, 
        ensuring that non-ASCII characters are preserved.
        """
        with open(self.output_path, 'w', encoding='utf-8') as f:
            for item in saved_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')


    def run(self):
        """
        Run the data generation process.

        This method orchestrates the entire data generation workflow, which includes:
        1. Reading input data from a JSONL file.
        2. Creating a dataset from the input data.
        3. Initializing a DataLoader with the created dataset.
        4. Setting up sampling parameters for the DPO (Data Processing Operation).
        5. Generating data using the DataLoader and sampling parameters.
        6. Updating the input data with the generated results.
        7. Saving the updated data to the specified output path.

        The method also prints a completion message indicating where the results have been saved.

        Returns:
            None
        """
        """Run the data generation process."""

       
        input_data = self.read_jsonl()
        dataset = self.create_dataset(input_data)
        dataloader = DataLoader(dataset=dataset, batch_size=self.batch_size, collate_fn=dataset.collator)
    

        sampling_params_dict = self.config.get('cot_sampling_params', {})
     

        all_save_list = self.generate(dataloader, sampling_params_dict)
 
        self.save_results(all_save_list)
        print(f"COT data completed, results have been saved in real-time to {self.output_path}")


class COTDataset(Dataset):
    def __init__(self, data_list, tokenizer, args):
        """
        Initializes the DPO_data class with the given parameters.

        Args:
            data_list (list): A list of data items.
            tokenizer (object): The tokenizer to be used for processing the data.
            args (dict): A dictionary of additional arguments.

        Attributes:
            data_list (list): Stores the provided data list.
            tokenizer (object): Stores the provided tokenizer.
            args (dict): Stores the provided arguments.
            top_k (int): The number of top items to consider, default is 5.
            sep_token (str): The token used to separate passages, default is "\n".
            max_passage_length (int): The maximum length of a passage, default is 2000.
            model_type (str): The type of model to use, default is "minicpm3".
            use_template (bool): Whether to use a template, default is True.
        """
        self.data_list = data_list
        self.tokenizer = tokenizer
        self.args = args

    def __len__(self):
        return len(self.data_list)

    def __getitem__(self, index):
        item = self.data_list[index]

    
        datatype=item['data_type']
        query = item['question']
        passage = item['passage']['segment']
        ground_truth = item['answer']

        if datatype in ['math_qa', 'commonsense_qa', 'aqua_rat', 'ecqa']:
            template = PROMPT_DICT['Mutichoice_querypassage_to_CoT']
        if datatype in ['gsm8k', 'strategyqa', 'web_questions', 'wiki_qa', 'yahoo_answers_qa', 'marcoqa']:
            template = PROMPT_DICT['QA_querypassage_to_CoT']
        template = template.format(passage=passage, question=query)

        messages = [
            {"role": "user", "content": template},
        ]
        input_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        item['input_prompt'] = input_prompt
        item['ground_truth'] = ground_truth
      

        return item
    
    def collator(self, batch):     
        id = [f['id'] for f in batch]
        datatype = [f['data_type'] for f in batch]
        query = [f['question'] for f in batch]
        passage = [f['passage'] for f in batch]
        ground_truth = [f['ground_truth'] for f in batch]
        input_prompt = [f['input_prompt'] for f in batch]
        
        return{ 
            'id':id,
            'data_type':datatype,
            'query':query,
            'passage':passage,
            'ground_truth':ground_truth,
            'input_prompt': input_prompt,
        }


def main():
    parser = argparse.ArgumentParser(description="Generate DPO data candidates")
    parser.add_argument('--input_path', type=str, default='/data/groups/QY_LLM_Other/meisen/dataset/rankcot/retriever_train_4000_noread_psg_modify10passage.jsonl', help="Path to save the retrieval results (JSONL format).")
    parser.add_argument('--output_path', type=str, default='/data/groups/QY_LLM_Other/meisen/dataset/rankcot/result_data/querypassage_to_CoT.jsonl', help="Path to save the generate results (JSONL format).")
    parser.add_argument('--model_name_or_path', type=str, default='/data/groups/QY_LLM_Other/meisen/pretrained_model/llama3/Meta-Llama-3-8B-Instruct', help="Path to the model to be trained.")
    parser.add_argument('--config_path', type=str, default='/home/meis23/project/ultrarag-dev/UltraRAG/config/pipeline/rankcot/datasets.yaml', help="Path to the YAML configuration file.")
    args = parser.parse_args()

    generator = COTGenerator(args.input_path, args.output_path, args.model_name_or_path, args.config_path)
    generator.run()
 

  

if __name__ == '__main__':
    main()