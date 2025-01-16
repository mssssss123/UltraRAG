# Description: 启动服务
# 目前的的微服务策略是：每个服务一个进程，每个进程一个端口
# 默认需要两张卡，启动所需的模型包括 Visrag 的两个模型和 vanilla-rag 的三个模型


# 下载模型(需要配置config/models_lists.yaml)
python $(pwd)/scripts/download_model.py 

mkdir -p $(pwd)/logs


export CUDA_VISIBLE_DEVICES=0
nohup python -m ultrarag.server.run_server_hf_llm \
    -host localhost \
    -port 8844 \
    -model_path $(pwd)/resource/models/MiniCPM-V-2_6 \
    -device cuda:0 \
> $(pwd)/logs/hf_llm.log 2>&1 &
HF_PID=$!


export CUDA_VISIBLE_DEVICES=0
# 启动embedding
nohup python -m ultrarag.server.run_embedding \
    -host localhost \
    -port 8845 \
    -model_path $(pwd)/resource/models/bge-large-zh-v1.5 \
    -device cuda:0 \
> $(pwd)/logs/bge-large-zh-v1.5.log 2>&1 &
EMBED_PID=$!


# 启动reranker
export CUDA_VISIBLE_DEVICES=0
nohup python -m ultrarag.server.run_server_reranker \
    -host localhost \
    -port 8846 \
    -model_path $(pwd)/resource/models/bge-reranker-large \
    -model_type bge_reranker \
> $(pwd)/logs/bge-reranker-large.log 2>&1 &
RERNK_PID=$!


export CUDA_VISIBLE_DEVICES=0
# 启动embedding
nohup python -m ultrarag.server.run_embedding \
    -host localhost \
    -port 8848 \
    -model_path $(pwd)/resource/models/VisRAG-Ret \
    -device cuda:0 \
> $(pwd)/logs/VisRAG-Ret.log 2>&1 &
EMBED_PID=$!


export CUDA_VISIBLE_DEVICES=1
nohup vllm serve \
    $(pwd)/resource/models/Qwen2.5-14B-Instruct \
    --host localhost \
    --port 8847 \
    --dtype auto \
    --served-model-name Qwen2.5-14B-Instruct \
    --trust-remote-code \
    --api-key empty \
> $(pwd)/logs/vllm.log 2>&1 &
VLLM_PID=$!


nohup /opt/qdrant > $(pwd)/logs/qdrant.log 2>&1 &

streamlit run ultrarag/webui/webui.py
# # 死循环
# echo "回车终止服务"
# read name
# echo "kill process..."

# kill $EMBED_PID
# kill $RERNK_PID
# kill $VLLM_PID