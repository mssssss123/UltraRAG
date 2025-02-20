import sys
from pathlib import Path
home_path = Path().resolve()
sys.path.append(home_path.as_posix())
from ultrarag.datasets.others.merge import *

class OthersClass:
    def __init__():
        pass
    
    @staticmethod
    def merge(parser):
        merge_main(parser)
    