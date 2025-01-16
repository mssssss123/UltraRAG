import argparse
from rouge import Rouge
import json
import string
import re
import yaml
from collections import Counter
import random

class DPOScorer:
    def __init__(self, input_path, train_output_path, dev_output_path, config_path):
        self.input_path = input_path
        self.train_output_path = train_output_path
        self.dev_output_path = dev_output_path

        with open(config_path, 'r', encoding='utf-8') as config_file:
            config = yaml.safe_load(config_file)
        
        self.metric = config.get('metric', 'rouge')
        self.ratio = config.get('ratio', 0.1)
        self.rouge = Rouge()

    def normalize_answer(self, s):
        """Lower text and remove punctuation, articles and extra whitespace."""
        def remove_articles(text):
            return re.sub(r"\b(a|an|the)\b", " ", text)

        def white_space_fix(text):
            return " ".join(text.split())

        def remove_punc(text):
            exclude = set(string.punctuation)
            return "".join(ch for ch in text if ch not in exclude)

        def lower(text):
            return text.lower()

        return white_space_fix(remove_articles(remove_punc(lower(s))))

    def _rougel_score(self, prediction, ground_truth):
        """Calculate Rouge score."""
        try:
            max_length = 512
            prediction = prediction[:max_length] if len(prediction) > max_length else prediction
            ground_truth = ground_truth[:max_length] if len(ground_truth) > max_length else ground_truth
            scores = self.rouge.get_scores(' '.join(list(prediction)), ' '.join(list(ground_truth)), avg=True)
        except ValueError:
            return 0.0
        return scores["rouge-l"]["f"]

    def _calculate_em(self, prediction, ground_truth):
        """Calculate Exact Match (EM)."""
        if self.normalize_answer(prediction) == self.normalize_answer(ground_truth):
            return 1.0
        else:
            return 0.0

    def _calculate_accuracy(self, prediction, ground_truth):
        """Calculate Accuracy."""
        if ground_truth in prediction or ground_truth.lower() in prediction or ground_truth.capitalize() in prediction:
            return 1.0
        else:
            return 0.0

    def _calculate_f1(self, prediction, ground_truth):
        """Calculate F1 score."""
        prediction_tokens = self.normalize_answer(prediction).split()
        ground_truth_tokens = self.normalize_answer(ground_truth).split()
        common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
        num_same = sum(common.values())
        if num_same == 0:
            return 0
        precision = 1.0 * num_same / len(prediction_tokens)
        recall = 1.0 * num_same / len(ground_truth_tokens)
        f1 = (2 * precision * recall) / (precision + recall)
        return f1

    def _score(self, prediction, ground_truth):
        if self.metric == 'rouge':
            return self._rougel_score(prediction, ground_truth)
        elif self.metric == 'em':
            return self._calculate_em(prediction, ground_truth)
        elif self.metric == 'accuracy':
            return self._calculate_accuracy(prediction, ground_truth)
        elif self.metric == 'f1':
            return self._calculate_f1(prediction, ground_truth)
        else:
            raise ValueError(f"Unsupported metric: {self.metric}")

    def _split_data(self, data):
        """Splits data into training and testing sets based on the ratio."""
        random.shuffle(data)
        split_index = int(len(data) * (1 - self.ratio))
        return data[:split_index], data[split_index:]

    def save_best_worst_data(self):
        """Select the best and worst data."""
        input_data = self.read_jsonl(self.input_path)

        train_data, test_data = self._split_data(input_data)

        with open(self.train_output_path, 'w', encoding='utf-8') as train_file:
            for item in train_data:
                ground_truth = item['ground_truth']
                context = item['context']

                for sub_item in context:
                    score = self._score(sub_item['text'], ground_truth)
                    sub_item[self.metric + '_score'] = score

                max_score_element = self.find_max_element_by_key(context, f'{self.metric}_score')
                min_score_element = self.find_min_element_by_key(context, f'{self.metric}_score')

                item['chosen'] = max_score_element
                item['rejected'] = min_score_element

                train_file.write(json.dumps(item, ensure_ascii=False) + '\n')

        with open(self.dev_output_path, 'w', encoding='utf-8') as test_file:
            for item in test_data:
                ground_truth = item['ground_truth']
                context = item['context']

                for sub_item in context:
                    score = self._score(sub_item['text'], ground_truth)
                    sub_item[self.metric + '_score'] = score

                max_score_element = self.find_max_element_by_key(context, f'{self.metric}_score')
                min_score_element = self.find_min_element_by_key(context, f'{self.metric}_score')

                item['chosen'] = max_score_element
                item['rejected'] = min_score_element

                test_file.write(json.dumps(item, ensure_ascii=False) + '\n')
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
    parser.add_argument("--input_path", type=str, required=True, help="Path to the input dpo data JSONL file.")
    parser.add_argument("--train_output_path", type=str, required=True, help="Path to save the train data JSONL file.")
    parser.add_argument("--dev_output_path", type=str, required=True, help="Path to save the dev data JSONL file.")
    parser.add_argument("--config_path", type=str, required=True, help="Path to the YAML configuration file.")

    args = parser.parse_args()

    scorer = DPOScorer(args.input_path, args.train_output_path, args.dev_output_path, args.config_path)
    scorer.save_best_worst_data()

if __name__ == "__main__":
    main()
