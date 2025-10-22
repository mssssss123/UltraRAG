#!/bin/bash

CUDA_VISIBLE_DEVICES=1 python -m vllm.entrypoints.openai.api_server \
    --served-model-name minicpm-embedding \
    --model openbmb/MiniCPM-Embedding-Light \
    --trust-remote-code \
    --host 127.0.0.1 \
    --port 65502 \
    --task embed \
    --gpu-memory-utilization 0.9