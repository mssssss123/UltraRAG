#!/bin/bash

gpu_vis="0,1,2,3"
data_model_name_or_path="/Path/to/the/model/used/for/data/construction/"
train_model_name_or_path="/Path/to/the/model/to/be/trained/"
config_path="/Path/to/the/YAML/configuration/file"
train_output_path="/Path/to/save/the/train/data/JSONL/file"
dev_output_path="/Path/to/save/the/dev/data/JSONL/file"
embedding_model_path="/Path/to/the/embedding/model/"
knowledge_id="/Knowledge/collection/ID/in/Qdrant"
knowledge_stat_tab_path="/Path/to/the/knowledge/statistics/table"

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --gpu_vis)
            gpu_vis="$2"
            shift; shift ;;
        --data_model_name_or_path)
            data_model_name_or_path="$2"
            shift; shift ;;
        --train_model_name_or_path)
            train_model_name_or_path="$2"
            shift; shift ;;
        --config_path)
            config_path="$2"
            shift; shift ;;
        --train_output_path)
            train_output_path="$2"
            shift; shift ;;
        --dev_output_path)
            dev_output_path="$2"
            shift; shift ;;
        --embedding_model_path)
            embedding_model_path="$2"
            shift; shift ;;
        --knowledge_id)
            knowledge_id="$2"
            shift; shift ;;
        --knowledge_stat_tab_path)
            knowledge_stat_tab_path="$2"
            shift; shift ;;
        --pipeline_type)
            pipeline_type="$2"
            shift; shift ;;
        --current_kb_config_id)
            current_kb_config_id="$2"
            shift; shift ;;
        *)
            echo "Unknown argument: $1"
            exit 1 ;;
    esac
done

export CUDA_VISIBLE_DEVICES=$gpu_vis
nohup python ultrarag/datasets/DDR/workflow.py  \
    --data_model_name_or_path "$data_model_name_or_path"  \
    --train_model_name_or_path "$train_model_name_or_path"  \
    --config_path "$config_path"  \
    --embedding_model_path "$embedding_model_path" \
    --knowledge_id "$knowledge_id" \
    --knowledge_stat_tab_path "$knowledge_stat_tab_path"  \
    --train_output_path "$train_output_path"  \
    --dev_output_path "$dev_output_path" > data.out  2>&1 &