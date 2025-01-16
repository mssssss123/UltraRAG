import sys
from pathlib import Path
home_path = Path().resolve()
sys.path.append(home_path.as_posix())
from ultrarag.datasets.embedding.synthesis_data.data_process_synthesis import data_preprocess_synthesis_main
from ultrarag.datasets.embedding.synthesis_data.synthesis_data_utils import synthesis_data_main


class DataPreprocessingSynthesisClass:
    def __init__():
        pass
    
    def data_preprocess_synthesis(parser):
        data_preprocess_synthesis_main(parser)

class SynthesisDataClass:
    def __init__():
        pass
    
    def synthesis_data(parser):
        synthesis_data_main(parser)