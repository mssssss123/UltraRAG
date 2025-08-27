#!/bin/bash

CUDA_VISIBLE_DEVICES=0,1 python -m vllm.entrypoints.openai.api_server \
    --served-model-name minicpm4-8b \
    --model OpenBMB/MiniCPM4-8B \
    --trust-remote-code \
    --host 0.0.0.0 \
    --port 8080 \
    --max-model-len 32768 \
    --gpu-memory-utilization 0.9 \
    --tensor-parallel-size 2 \
    --enforce-eager