from modelscope.hub.snapshot_download import snapshot_download
from pathlib import Path

import yaml
import argparse
import os
from loguru import logger
root_path = Path(__file__).resolve().parent.parent
model_path = Path(__file__).resolve().parent.parent / "resource/models"
model_path.mkdir(parents=True, exist_ok=True)


parser = argparse.ArgumentParser()
parser.add_argument("--config", type=str, default=(root_path / "config/models_download_list.yaml").as_posix())
args = parser.parse_args()


with open(args.config, "r", encoding="utf-8") as f:
    models_lists = yaml.load(f, Loader=yaml.FullLoader)

for model_name, model_info in models_lists.items():
    model_id = model_info["model_id"]
    model_type = model_info["model_type"]
    curr_model_path = model_path / model_name
    if curr_model_path.is_dir() and len(os.listdir(curr_model_path)) > 0:
        logger.info(f'Directory {curr_model_path} is not empty, skipping download.')
        continue
    logger.info(f"Downloading model {model_name} from {model_id} to {curr_model_path}")
    snapshot_download(model_id, local_dir=curr_model_path.as_posix())

