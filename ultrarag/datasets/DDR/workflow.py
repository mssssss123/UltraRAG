import argparse
import sys
import tempfile
import os
import torch
import torch.multiprocessing as mp
from pathlib import Path
home_path = Path().resolve()
sys.path.append(home_path.as_posix())
from ultrarag.datasets.DDR.Generate_dataset import DataGenerator
from ultrarag.datasets.DDR.DPO_data import DPOGenerator
from ultrarag.datasets.DDR.DPO_score import DPOScorer

class GenerationFlow:
    def __init__(self, parser):
        parser.add_argument("--data_model_name_or_path", type=str, required=True, help="Path to the model used for data construction.")
        parser.add_argument("--train_model_name_or_path", type=str, required=True, help="Path to the model to be trained.")
        parser.add_argument("--config_path", type=str, required=True, help="Path to the YAML configuration file.")
        parser.add_argument("--embedding_model_path", type=str, required=True, help="Path to the embedding model.")
        parser.add_argument("--knowledge_id", type=str, required=True, help="Knowledge collection ID in Qdrant.")
        parser.add_argument("--knowledge_stat_tab_path", type=str, required=True, help="Path to the knowledge statistics table.")
        parser.add_argument("--train_output_path", type=str, required=True, help="Path to save the train data JSONL file.")
        parser.add_argument("--dev_output_path", type=str, required=True, help="Path to save the dev data JSONL file.")
        args, unknown=parser.parse_known_args()
        self.args = args

        self.fixed_dir = "./resource/dataset/train_dataset/fixed_temp_dir"
        os.makedirs(self.fixed_dir, exist_ok=True)

    def run_DataGenerator(self, step1_output):
        data_generator = DataGenerator(
            self.args.data_model_name_or_path, 
            self.args.config_path, 
            self.args.embedding_model_path, 
            self.args.knowledge_id, 
            self.args.knowledge_stat_tab_path
        )
        data_generator.process_data_async(step1_output)

    def run_DPOGenerator(self, step1_output, step2_output):
        generator = DPOGenerator(step1_output, step2_output, self.args.train_model_name_or_path, self.args.config_path)
        generator.run()

    def run_DPOScorer(self, step2_output):
        scorer = DPOScorer(step2_output, self.args.train_output_path, self.args.dev_output_path, config_path=self.args.config_path)
        scorer.save_best_worst_data()

    def execute(self):
        step1_output = os.path.join(self.fixed_dir, "step1_output.json")
        step2_output = os.path.join(self.fixed_dir, "step2_output.json")

        processes = [
            mp.Process(target=self.run_DataGenerator, args=(step1_output,)),
            mp.Process(target=self.run_DPOGenerator, args=(step1_output, step2_output)),
            mp.Process(target=self.run_DPOScorer, args=(step2_output,)),
        ]

        for process in processes:
            process.start()
            process.join()

if __name__ == "__main__":
    mp.set_start_method('spawn', force=True)

    parser = argparse.ArgumentParser(description="Datasets Workflow Pipeline")
    pipeline = GenerationFlow(parser)
    pipeline.execute()
