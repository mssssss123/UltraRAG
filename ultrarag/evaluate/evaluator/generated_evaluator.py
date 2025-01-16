import json
import argparse
import re
from collections import Counter
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
import torch
import string
from rouge import Rouge
from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.meteor_score import meteor_score
from nltk.tokenize import word_tokenize
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from functools import lru_cache
from loguru import logger

@lru_cache(None)
def get_text2vec():
    from text2vec import SentenceModel
    return SentenceModel("shibing624/text2vec-base-multilingual")


class GeneratedEvaluator:
    # todo
    relation_prompt_template = """请根据模型生成内容Generate Text，请判断该生成与Ground Truth Keypoint是否具备相关性：\n
    Ground Truth Keypoint: {keypoint}\n
    Generate Text: {generate_text}\n
    请判断它们是否相关，如果相关，请回复“<EVAL>relavant</EVAL>”，如果不相关，请回复“<EVAL>irrelavant</EVAL>。”"""

    def __init__(self, input_path=None, output_path=None, metric='completeness', completeness_model=None):
        """
        初始化方法，传入输入文件路径、输出文件路径和评估指标（metric）。
        metric: 可选值 'completeness', 'rouge', 'em', 'accuracy', 'f1'，默认为 'completeness'。
        completeness_model: 用于completeness计算的模型路径
        """
        try:
            self.input_path = input_path
            self.output_path = output_path
            self.metric = metric  
            self.rouge = Rouge()
            self.completeness_model = completeness_model
            self.tokenizer = AutoTokenizer.from_pretrained(completeness_model)

            self.sampling_params = SamplingParams(
                temperature=0.8,
                max_tokens=500,
                frequency_penalty=1.2
            )

            self.llm = LLM(
                model=completeness_model,
                tokenizer_mode="auto",
                dtype=torch.bfloat16,
                gpu_memory_utilization=0.9,
                enforce_eager=True,
                tensor_parallel_size=4
            )
        except:
            self.llm = None
            pass
        
    def get_score(self, metric_name, ground_truth, prediction, data, **kwargs):
        """
        根据指定的评估指标计算分数。

        :param metric_name: 评估指标的名称 ('completeness', 'rouge', 'em', 'accuracy', 'f1')
        :param ground_truth: 正确答案 (string)
        :param prediction: 生成内容 (string)
        :param kwargs: 额外参数，用于特定评估指标
        :return: 计算的分数
        """
        if metric_name == 'completeness':
            if not self.llm:
                self.llm = kwargs.get("llm")
            keypoints_string = data.get("keypoints", "")
            keypoints = self.extract_keypoints(keypoints_string)
            return self._calculate_completeness(keypoints, prediction)*100
        elif metric_name == 'rouge':
            return self._rougel_score(prediction, ground_truth)*100
        elif metric_name == 'em':
            return self._calculate_em(prediction, ground_truth)*100
        elif metric_name == 'accuracy':
            return self._calculate_accuracy(prediction, ground_truth)*100
        elif metric_name == 'f1':
            return self._calculate_f1(prediction, ground_truth)*100
        elif metric_name == 'bleu':
            return sentence_bleu([gt.split() for gt in [ground_truth]], prediction.split(), weights=[0.25,0.25,0.25,0.25])*100
        elif metric_name == 'meteor':
            return meteor_score([word_tokenize(ground_truth)], word_tokenize(prediction))*100
        elif metric_name == 'bert':
            return self._bert_score(prediction, [ground_truth]) * 100
        elif metric_name == 'jec':
            return self._jec_score(prediction, ground_truth) * 100
        else:
            raise ValueError(f"Unsupported metric: {metric_name}")

    def _jec_score(self, prediction, ground_truth):
        # Extract capital letters from both strings
        answer_letter = re.search(r'[A-Z]', ground_truth)
        prediction_letter = re.search(r'[A-Z]', prediction)
        
        if answer_letter and prediction_letter and answer_letter.group() == prediction_letter.group():
            return 1.00
        else:
            return 0.00

    def _bert_score(self, continuation: str, references):
        model = get_text2vec()
        sentences = [continuation] + references
        embeddings = model.encode(sentences)
        continuation_embedding = embeddings[0].reshape(1, -1)
        reference_embeddings = np.array(embeddings[1:])
        similarities = cosine_similarity(continuation_embedding, reference_embeddings)
        max_similarity = np.max(similarities)
        return max_similarity

    def extract_keypoints(self, keypoints_string):
        """提取每个关键点并返回列表"""
        keypoint_pattern = r"\d+\.\s*([^\n]+)"
        keypoints = re.findall(keypoint_pattern, keypoints_string)
        return keypoints

    def extract_eval_content(self, model_output):
        """从模型返回的结果中提取<EVAL></EVAL>之间的内容"""
        eval_pattern = r"<EVAL>(.*?)</EVAL>"
        match = re.search(eval_pattern, model_output)
        return match.group(1) if match else None

    def normalize_answer(self, s):
        """转换为小写，去除标点符号、冠词和多余的空格"""
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
        try:
            max_length = 512
            prediction = prediction[:max_length] if len(prediction) > max_length else prediction
            ground_truth = ground_truth[:max_length] if len(ground_truth) > max_length else ground_truth
            scores = self.rouge.get_scores(' '.join(list(prediction)), ' '.join(list(ground_truth)), avg=True)
        except ValueError:
            return 0.0
        return scores["rouge-l"]["f"]

    def _calculate_em(self, prediction, ground_truth):
        """计算Exact Match（EM）"""
        if self.normalize_answer(prediction) == self.normalize_answer(ground_truth):
            return 1.0
        else:
            return 0.0

    def _calculate_accuracy(self, prediction, ground_truth):
        """计算准确率"""
        if ground_truth in prediction or ground_truth.lower() in prediction or ground_truth.capitalize() in prediction:
            return 1.0
        else:
            return 0.0

    def _calculate_f1(self, prediction, ground_truth):
        """计算F1分数"""
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

    def _calculate_completeness(self, keypoints, generate_text):
        """计算completeness"""
        correct_count = 0
        total_keypoints = len(keypoints)

        for keypoint in keypoints:
            relation_prompt = self.relation_prompt_template.format(keypoint=keypoint, generate_text=generate_text)
            relation_prompt = [{"role": "user", "content": relation_prompt}]
            relation_prompt = self.tokenizer.apply_chat_template(relation_prompt, add_generation_prompt=True, tokenize=False)

            try:
                relation_result = self.llm.arun(messages=relation_prompt, stream=True)
                # .generate(relation_prompt, self.sampling_params)
                # relation_result = relation_output[0].outputs[0].text.strip()

                eval_content = self.extract_eval_content(relation_result)

                if eval_content == "relavant":
                    correct_count += 1

            except Exception as e:
                print(f"Error processing keypoint '{keypoint}': {e}")
                continue

        return (correct_count / total_keypoints) * 100 if total_keypoints > 0 else 0

    def run_metric_inference(self):
        """根据选择的metric执行不同的评估"""
        total_score = 0
        total_count = 0

        with open(self.output_path, "w", encoding="utf-8") as outfile:
            with open(self.input_path, "r", encoding="utf-8") as infile:
                for line_num, line in enumerate(infile, start=1):
                    data = json.loads(line)

                    prediction = data.get("generate_text", "").strip()
                    ground_truth = data.get("ground_truth", "").strip()
                    keypoints_string = data.get("keypoints", "")

                    if not prediction or not ground_truth:
                        continue

                    if self.metric == 'completeness': 
                        keypoints = self.extract_keypoints(keypoints_string)
                        score = self._calculate_completeness(keypoints, prediction)

                    elif self.metric == 'rouge':
                        score = self._rougel_score(prediction, ground_truth)
                    elif self.metric == 'em':
                        score = self._calculate_em(prediction, ground_truth)
                    elif self.metric == 'accuracy':
                        score = self._calculate_accuracy(prediction, ground_truth)
                    elif self.metric == 'f1':
                        score = self._calculate_f1(prediction, ground_truth)
                    else:
                        raise ValueError(f"Unsupported metric: {self.metric}")

                    total_score += score
                    total_count += 1

                    result = {
                        "doc_id": data.get("doc_id", ""),
                        "file_id": data.get("file_id", ""),
                        "prediction": prediction,
                        "ground_truth": ground_truth,
                        "score": score
                    }

                    outfile.write(json.dumps(result, ensure_ascii=False) + "\n")

                    print(f"Processed {line_num} line, {self.metric} score: {score}")

            average_score = total_score / total_count if total_count > 0 else 0

            summary = {
                "average_score": average_score,
                "total_score": total_score,
                "total_count": total_count
            }

            outfile.write("\n" + json.dumps(summary, ensure_ascii=False) + "\n")
            print(f"Processing completed, average {self.metric} score: {average_score}")
            print(f"The result has been saved to {self.output_path}")


def main():
    parser = argparse.ArgumentParser(description="Evaluation Script")
    parser.add_argument("--input_path", type=str, required=True, help="Path to the file that needs to be evaluated.")
    parser.add_argument("--output_path", type=str, required=True, help="Path to save the Output evaluation results.")
    parser.add_argument("--completeness_model", type=str, required=True, help="Path to the model used for completeness evaluation.")
    parser.add_argument("--metric", type=str, choices=["completeness", "rouge", "em", "accuracy", "f1"], default="completeness", help="Evaluation metric to use.")

    args = parser.parse_args()

    evaluator = GeneratedEvaluator(
        input_path=args.input_path,
        output_path=args.output_path,
        metric=args.metric,
        completeness_model=args.completeness_model
    )

    evaluator.run_metric_inference()


if __name__ == "__main__":
    main()
