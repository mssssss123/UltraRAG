#!/bin/bash

# GPU settings
gpu_vis="0,1,2,3"
master_port=2223
use_lora=""
task_type="DPO" # The type of task (e.g., DPO/SFT)
model_name_or_path="/Path/to/the/pre-trained/model/or/identifier/from/the/HuggingFace/model/"
train_data_path="/Path/to/the/training/dataset/in/JSON/format"
eval_data_path="/Path/to/the/evaluation/dataset/in/JSON/format"
output_dir="/Directory/to/save/the/model/checkpoints/and/training/outputs/"
logging_dir="/Directory/to/save/the/training/logs/"
deepspeed_config_file="/DeepSpeed/config/path"
config_file="/Path/to/the/YAML/configuration/file" 
log_file="Path/to/the/log/file/for/recording/training/progress"

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --gpu_vis)
            gpu_vis="$2"
            shift; shift ;;
        --master_port)
            master_port="$2"
            shift; shift ;;
        --use_lora)
            use_lora="--use_lora"
            shift ;;
        --task_type)
            task_type="$2"
            shift; shift ;;
        --model_name_or_path)
            model_name_or_path="$2"
            shift; shift ;;
        --train_data_path)
            train_data_path="$2"
            shift; shift ;;
        --eval_data_path)
            eval_data_path="$2"
            shift; shift ;;
        --output_dir)
            output_dir="$2"
            shift; shift ;;
        --logging_dir)
            logging_dir="$2"
            shift; shift ;;
        --deepspeed_config_file)
            deepspeed_config_file="$2"
            shift; shift ;;
        --config_file)
            config_file="$2"
            shift; shift ;;
        --log_file)
            log_file="$2"
            shift; shift ;;
        --pipeline_type)
            pipeline_type="$2"
            shift; shift ;;
        *)
            echo "Unknown argument: $1"
            exit 1 ;;
    esac
done

if [ -z "$output_dir" ]; then
    echo "Error: --output_dir is required"
    exit 1
fi
if [ -z "$logging_dir" ]; then
    echo "Error: --logging_dir is required"
    exit 1
fi

create_dir() {
    local dir_path="$1"
    if [ ! -d "$dir_path" ]; then
        mkdir -p "$dir_path"
        echo "Created directory: $dir_path"
    else
        echo "Directory already exists: $dir_path"
    fi
}

create_dir "$output_dir"
create_dir "$logging_dir"

# Command to run
declare -a CMD=(
    "deepspeed"
    "--include=localhost:$gpu_vis"
    "--master_port=$master_port"
    "ultrarag/finetune/dpo_and_sft/train.py"
    "--model_name_or_path=$model_name_or_path"
    "--task_type=$task_type"
    "--train_data_path=$train_data_path"
    "--eval_data_path=$eval_data_path"
    "--output_dir=$output_dir"
    "--logging_dir=$logging_dir"
    $use_lora
    "--config_file=$config_file"  # Pass the config.yaml file to the Python script
    "--deepspeed=$deepspeed_config_file"  # DeepSpeed config file path
)

# Run the command in the background and redirect output to the log file
nohup "${CMD[@]}" > "$log_file" 2>&1 &

echo "Training started. Check log file: $log_file"
