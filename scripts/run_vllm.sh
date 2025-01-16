#!/bin/bash

# 解析命令行参数
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

# 设置默认端口
PORT=${PORT:-8000}

# 检查必需参数
if [ -z "$MODEL_PATH" ] || [ -z "$GPUS" ]; then
    echo "使用方法: bash run_vllm.sh --model_path <模型路径> --gpus <GPU列表，如0,1> [--port <端口号>]"
    exit 1
fi

# 获取模型名称（去除路径）
MODEL_NAME=$(basename $MODEL_PATH)

# 计算GPU数量
NUM_GPUS=$(echo $GPUS | tr ',' '\n' | wc -l)

# 设置CUDA可见设备
export CUDA_VISIBLE_DEVICES=$GPUS

# 启动vLLM服务
nohup python -m vllm.entrypoints.openai.api_server \
    --model $MODEL_PATH \
    --host localhost \
    --port $PORT \
    --api-key "empty" \
    --tensor-parallel-size $NUM_GPUS \
    --gpu-memory-utilization 0.9 \
    --dtype float16 \
    --served-model-name $MODEL_NAME > vllm_${PORT}.log 2>&1 &

echo "vLLM服务已启动:"
echo "- 模型路径: $MODEL_PATH"
echo "- 模型名称: $MODEL_NAME" 
echo "- 使用GPU: $GPUS"
echo "- GPU数量: $NUM_GPUS"
echo "- 服务地址: http://localhost:${PORT}/v1"
echo "- 日志文件: vllm_${PORT}.log"
echo ""
echo "使用以下配置访问API:"
echo "- API Base URL: http://localhost:${PORT}/v1"
echo "- Model Name: $MODEL_NAME"


