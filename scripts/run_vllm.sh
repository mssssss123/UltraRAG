#!/bin/bash

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --model_path)
            MODEL_PATH="$2"
            shift 2
            ;;
        --gpus)
            GPUS="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

# Set default port
PORT=${PORT:-8000}

# Check for required parameters
if [ -z "$MODEL_PATH" ] || [ -z "$GPUS" ]; then
    echo "使用方法: bash run_vllm.sh --model_path <模型路径> --gpus <GPU列表，如0,1> [--port <端口号>]"
    exit 1
fi

# Get model name (remove path)
MODEL_NAME=$(basename $MODEL_PATH)

# Calculate number of GPUs
NUM_GPUS=$(echo $GPUS | tr ',' '\n' | wc -l)

# Set CUDA visible devices
export CUDA_VISIBLE_DEVICES=$GPUS

# Start vLLM service
nohup python -m vllm.entrypoints.openai.api_server \
    --model $MODEL_PATH \
    --host localhost \
    --port $PORT \
    --api-key "empty" \
    --tensor-parallel-size $NUM_GPUS \
    --gpu-memory-utilization 0.9 \
    --dtype float16 \
    --served-model-name $MODEL_NAME > vllm_${PORT}.log 2>&1 &

echo "vLLM service started:"
echo "- Model path: $MODEL_PATH"
echo "- Model name: $MODEL_NAME"
echo "- Using GPUs: $GPUS" 
echo "- Number of GPUs: $NUM_GPUS"
echo "- Service URL: http://localhost:${PORT}/v1"
echo "- Log file: vllm_${PORT}.log"
echo ""
echo "Use the following configuration to access the API:"
echo "- API Base URL: http://localhost:${PORT}/v1"
echo "- Model Name: $MODEL_NAME"


