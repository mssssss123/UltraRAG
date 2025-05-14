import argparse
from rouge import Rouge
import json
import string
import re
import yaml
from collections import Counter
import random
from tqdm import tqdm
random.seed(1)

class DPOGenerator:
    def __init__(self, input_path, train_output_path, dev_output_path, config_path):
        """
        Initializes the DPO_score class with the given input and output paths and configuration file.
        Args:
            input_path (str): Path to the input data.
            train_output_path (str): Path to the training output data.
            dev_output_path (str): Path to the development output data.
            config_path (str): Path to the configuration file.
        Attributes:
            input_path (str): Path to the input data.
            train_output_path (str): Path to the training output data.
            dev_output_path (str): Path to the development output data.
            metric (str): Evaluation metric to be used, default is 'rouge'.
            ratio (float): Ratio value from the configuration, default is 0.1.
            rouge (Rouge): Instance of the Rouge class for evaluation.
        """
        self.input_path = input_path
        self.train_output_path = train_output_path
        self.dev_output_path = dev_output_path

        with open(config_path, 'r', encoding='utf-8') as config_file:
            config = yaml.safe_load(config_file)
        
        self.ratio = config.get('ratio', 0.1)
        self.rouge = Rouge()


    def _rougel_score(self, prediction, ground_truth):
        """Calculate Rouge score."""
        try:
            scores = self.rouge.get_scores(prediction, ground_truth, avg=True)
        except ValueError:  # "Hypothesis is empty."
            return 0.0
        return scores["rouge-l"]["f"]

    
    def _custom_json_decoder(self, obj):
        if 'id' in obj:
            obj['id'] = str(obj['id'])
        return obj
    
    def gen_initial_dpo_data(self):
        results = []
        with open(self.input_path, 'r', encoding='utf-8') as infile:
            question_data = {}
            for line in infile:
                data = json.loads(line, object_hook=self._custom_json_decoder)
                question_id = data['id']  

                if question_id not in question_data:
                    question_data[question_id] = {
                        'query': data['query'],
                        'passages': [],  
                        'model_answers': [],
                        'ground_truth': data['ground_truth'],
                        'data_type': data['data_type'],
                        'COTs': []
                    }
                
                question_data[question_id]['passages'].append(data['passage'])  
                question_data[question_id]['model_answers'].append(data['model_answer'])
                question_data[question_id]['COTs'].append(data['COT'])
        
          
            for question_id, data in question_data.items():
                query = data['query']
                passages = data['passages']  
                model_answers = data['model_answers']
                ground_truth = data['ground_truth']
                datatype = data['data_type']
                COTs = data['COTs']

            

                correct_answers = []
                incorrect_answers = []

                if datatype in ['math_qa', 'commonsense_qa','aqua_rat']:
                    for model_answer, cot in zip(model_answers, COTs):
                        model_answer_len = len(model_answer)
                        minindex = min(model_answer_len, 15)
                        choice_answer = model_answer[:minindex]
                    
                        if ground_truth.lower() in choice_answer.lower():
                            correct_answers.append((model_answer, cot))
                        else:
                            incorrect_answers.append((model_answer, cot))

                    chosen_answer = random.choice(correct_answers) if correct_answers else (None, None)
                    rejected_answer = random.choice(incorrect_answers) if incorrect_answers else (None, None)
                
                elif datatype in ['ecqa', 'gsm8k','strategyqa', 'web_questions']:
                    for model_answer, cot in zip(model_answers, COTs):
                        if  ground_truth.lower() in model_answer.lower():
                            correct_answers.append((model_answer, cot))
                        else:
                            incorrect_answers.append((model_answer, cot))

                    chosen_answer = random.choice(correct_answers) if correct_answers else (None, None)
                    rejected_answer = random.choice(incorrect_answers) if incorrect_answers else (None, None)

                elif datatype in ['wiki_qa','yahoo_answers_qa','marcoqa']:
                    scored_answers = []
                    for model_answer, cot in zip(model_answers, COTs):
                        score = self._rougel_score(model_answer, ground_truth)
                        scored_answers.append((model_answer, cot, score))

                    scored_answers.sort(key=lambda x: x[2]) 
                    chosen_answer = scored_answers[-1] if scored_answers else (None, None, None)
                    rejected_answer = scored_answers[0] if scored_answers else (None, None, None)

            
                result_entry = {
                    'id': question_id,
                    'query': query,
                    'model_answer': {
                        'chosen': chosen_answer[0],  
                        'rejected': rejected_answer[0]  
                    },
                    'COT': {
                        'chosen': chosen_answer[1],  
                        'rejected': rejected_answer[1]  
                    },
                    'passages': passages,  
                    'ground_truth':ground_truth,
                    'data_type': datatype
                }

                results.append(result_entry)
       
        return results


    def filter_dpo_data(self, intital_dpo_data):
        filtered_data = []
        for data in intital_dpo_data:
            model_answer = data.get('model_answer', {})
            cot = data.get('COT', {})

        
            model_chosen = model_answer.get('chosen')
            model_rejected = model_answer.get('rejected')
            cot_chosen = cot.get('chosen')
            cot_rejected = cot.get('rejected')

            if not model_chosen or not model_rejected or not cot_chosen or not cot_rejected:
                continue

            filtered_data.append(data)
    
        return filtered_data
    
    def _split_data(self, data):
        """Splits data into training and testing sets based on the ratio."""
        random.shuffle(data)
        split_index = int(len(data) * (1 - self.ratio))
        return data[:split_index], data[split_index:]
    
    def save_results(self, output_path, saved_data):
        """
        Save the updated results to the output file.

        Args:
            updated_data (list): A list of dictionaries or objects to be saved to the output file.

        The method writes each item in the updated_data list to the output file in JSON format, 
        ensuring that non-ASCII characters are preserved.
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in saved_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')

    def save_best_worst_data(self):
        """
        Select the best and worst data based on a scoring metric and save the results.

        This method reads input data from a JSONL file, splits it into training and testing datasets,
        scores each context item against the ground truth, and identifies the best and worst items
        based on the specified metric. The results are then saved to the specified output paths.

        The method performs the following steps:
        1. Reads input data from a JSONL file.
        2. Splits the data into training and testing datasets.
        3. For each item in the training and testing datasets:
           a. Scores each context item against the ground truth.
           b. Identifies the context item with the highest score (chosen).
           c. Identifies the context item with the lowest score (rejected).
           d. Adds the chosen and rejected items to the original item.
        4. Writes the modified training data to the training output path.
        5. Writes the modified testing data to the testing output path.

        The results are saved in real-time to the specified output paths.

        Raises:
            FileNotFoundError: If the input file does not exist.
            IOError: If there is an error reading from or writing to the files.
        """
        
        intital_dpo_data = self.gen_initial_dpo_data()

        filter_dpo_data = self.filter_dpo_data(intital_dpo_data)

        train_data, dev_data = self._split_data(filter_dpo_data)

        self.save_results(self.train_output_path, train_data)

        self.save_results(self.dev_output_path, dev_data)


       
        print(f"DPO score completed, results have been saved in real-time to {self.train_output_path} and {self.dev_output_path}")

    def read_jsonl(self, file_path):
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line.strip()))
        return data

    def find_max_element_by_key(self, data_list, key):
        return max(data_list, key=lambda x: x[key])

    def find_min_element_by_key(self, data_list, key):
        return min(data_list, key=lambda x: x[key])



def main():
    parser = argparse.ArgumentParser(description="Calculate DPO score")
    parser.add_argument("--input_path", type=str, default='/data/groups/QY_LLM_Other/meisen/dataset/rankcot/result_data/queryCoT_to_answer.jsonl', help="Path to the input dpo data JSONL file.")
    parser.add_argument("--train_output_path", type=str, default='/data/groups/QY_LLM_Other/meisen/dataset/rankcot/result_data/train.jsonl', help="Path to save the train data JSONL file.")
    parser.add_argument("--dev_output_path", type=str, default='/data/groups/QY_LLM_Other/meisen/dataset/rankcot/result_data/dev.jsonl', help="Path to save the dev data JSONL file.")
    parser.add_argument('--config_path', type=str, default='/home/meis23/project/ultrarag-dev/UltraRAG/config/pipeline/rankcot/datasets.yaml', help="Path to the YAML configuration file.")
    args = parser.parse_args()

    scorer = DPOGenerator(args.input_path, args.train_output_path, args.dev_output_path, args.config_path)
    scorer.save_best_worst_data()

if __name__ == "__main__":
    main()
