from modelscope.hub.snapshot_download import snapshot_download
from pathlib import Path
import yaml
import argparse
import os
from loguru import logger

# Get root path and create model directory
root_path = Path(__file__).resolve().parent.parent
model_path = root_path / "resource/models"
model_path.mkdir(parents=True, exist_ok=True)

# Set up argument parser for config file
parser = argparse.ArgumentParser()
parser.add_argument(
    "--config", 
    type=str, 
    default=(root_path / "config/models_download_list.yaml").as_posix(),
    help="Path to the model download configuration file"
)
args = parser.parse_args()

# Load model configuration from yaml file
with open(args.config, "r", encoding="utf-8") as f:
    models_lists = yaml.load(f, Loader=yaml.FullLoader)

# Download each model specified in the configuration
for model_name, model_info in models_lists.items():
    model_id = model_info["model_id"]
    model_type = model_info["model_type"]
    curr_model_path = model_path / model_name
    
    # Skip if model is already downloaded
    if curr_model_path.is_dir() and len(os.listdir(curr_model_path)) > 0:
        logger.info(f'Directory {curr_model_path} is not empty, skipping download.')
        continue
        
    # Download model from modelscope hub
    logger.info(f"Downloading model {model_name} from {model_id} to {curr_model_path}")
    snapshot_download(model_id, local_dir=curr_model_path.as_posix())

