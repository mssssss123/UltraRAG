import sys
from pathlib import Path
home_path = Path().resolve()
sys.path.append(home_path.as_posix())
import os
from ultrarag.datasets.KBAlign.short_dependency import ShortDependecy
from ultrarag.datasets.KBAlign.long_dependency import LongDependecy
from ultrarag.datasets.others.merge import load_files, split_data, merge_data, write_output

class KBAlignClass:
    def __init__(self, parser):
        self.parser = parser
        parser.add_argument("--model_name_or_path", type=str, required=True, help="Path to the external model.")
        parser.add_argument("--config_path", type=str, required=True, help="Path to the YAML configuration file.")
        parser.add_argument("--embedding_model_path", type=str, required=True, help="Path to the embedding model.")
        parser.add_argument("--knowledge_id", type=str, required=True, help="Knowledge collection ID in Qdrant.")
        parser.add_argument("--knowledge_stat_tab_path", type=str, required=True, help="Path to the knowledge statistics table.")
        parser.add_argument("--clustering", action='store_true', help="Heterogeneous data requires clustering.")
        
        parser.add_argument("--output_dir", type=str, required=True, help="Path to save the output dir.")
        parser.add_argument("--language", type=str, required=True, help="Chinese/English")
        parser.add_argument("--functions_to_run", default=[], type=str, nargs='+', required=True, help="function_q/function_qr")
        
        parser.add_argument("--file_list", nargs='+', required=True, help="List of JSON or JSONL files to merge.")
        parser.add_argument("--ratios", nargs='+', type=int, required=True, help="Proportions for each file in format 1:1.")
        parser.add_argument("--fixed_steps", type=int, default=None, help="Number of fixed steps for merging.")
        parser.add_argument("--random_merge", action='store_true', help="Whether to shuffle data before merging.")
        parser.add_argument("--output_file", required=True, help="Output file for merged data.")
        parser.add_argument("--output_format", required=True, choices=['json', 'jsonl'], help="Output format: 'json' or 'jsonl'.")
        args, unknown=parser.parse_known_args()
        self.args = args
    
    def short_dependency(self):
        short_dependecy = ShortDependecy(self.args.output_dir,self.args.language,self.args.model_name_or_path,self.args.config_path,self.args.functions_to_run,self.args.embedding_model_path,self.args.knowledge_id,self.args.knowledge_stat_tab_path)
        short_dependecy.gen_data()
        short_dependecy.merge_data()
    
    def long_dependency(self):
        long_dependecy = LongDependecy(self.args.output_dir, self.args.language, self.args.model_name_or_path, self.args.config_path, self.args.embedding_model_path, self.args.knowledge_id, self.args.knowledge_stat_tab_path,self.args.clustering)
        long_dependecy.main()
    
    def main(self):
        # self.short_dependency()
        self.long_dependency()
        
        output_dir1 = os.path.join(self.args.output_dir, "kbalign_short_final_data")
        output_filename1 = (f"kbalign_short_final_data.json")
        output_file1 = os.path.join(output_dir1, output_filename1)
        output_dir2 = os.path.join(self.args.output_dir, "kbalign_long_final_data")
        output_filename2 = (f"kbalign_long_final_data.jsonl")
        output_file2 = os.path.join(output_dir2, output_filename2)
        
        all_data = load_files([output_file1,output_file2])
        counts = split_data(all_data, self.args.ratios)
        merged_data = merge_data(all_data, counts, fixed_steps=self.args.fixed_steps, random_merge=self.args.random_merge)
        write_output(merged_data, self.args.output_file, self.args.output_format)
        