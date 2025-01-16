import sys
from pathlib import Path
home_path = Path().resolve()
sys.path.append(home_path.as_posix())
from ultrarag.datasets.embedding.dig_hard_neg.dig_hard_neg_utils import dig_hard_main
from ultrarag.datasets.embedding.dig_hard_neg.encoder_clean import encoder_clean_main
from ultrarag.datasets.embedding.dig_hard_neg.reranker_clean import reranker_clean_main


class DigHardNegClass:
    def __init__():
        pass
    def dig_hard_neg(parser):
        dig_hard_main(parser)
        
class CleanDataClass:
    def __init__():
        pass
    def encoder_clean(parser):
        encoder_clean_main(parser)      
        
class RerankerCleanDataClass:
    def __init__():
        pass
    def reranker_clean(parser):
        reranker_clean_main(parser)