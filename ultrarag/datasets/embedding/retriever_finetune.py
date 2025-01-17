import argparse
import sys
from pathlib import Path
home_path = Path().resolve()
sys.path.append(home_path.as_posix())

class RetrieverFinetune:
    def __init__(self):
        pass
    def main(self,parser):
        parser.add_argument('--pipeline_step', type=str)
        args, unknown=parser.parse_known_args()
        if args.pipeline_step == "data_preprocessing_synthesis":
            from ultrarag.datasets.embedding.synthesis_data.synthesis_data import DataPreprocessingSynthesisClass
            DataPreprocessingSynthesisClass.data_preprocess_synthesis(parser)

        if args.pipeline_step == "data_synthesis":
            from ultrarag.datasets.embedding.synthesis_data.synthesis_data import SynthesisDataClass
            SynthesisDataClass.synthesis_data(parser)

        if args.pipeline_step == "dig_hard_neg":
            from ultrarag.datasets.embedding.dig_hard_neg.dig_hard_neg import DigHardNegClass
            DigHardNegClass.dig_hard_neg(parser)

        if args.pipeline_step == "clean_data":
            from ultrarag.datasets.embedding.dig_hard_neg.dig_hard_neg import CleanDataClass
            CleanDataClass.encoder_clean(parser)

        if args.pipeline_step == "reranker_clean_data":
            from ultrarag.datasets.embedding.dig_hard_neg.dig_hard_neg import RerankerCleanDataClass
            RerankerCleanDataClass.reranker_clean(parser)