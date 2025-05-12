import sys
import torch
import torch.multiprocessing as mp
from pathlib import Path
home_path = Path().resolve()
sys.path.append(home_path.as_posix())





if __name__ == "__main__":
    mp.set_start_method('spawn', force=True)