# Description: Start microservices
# Current microservice strategy: one process per service, one port per process
# Default requirement: two GPUs to run models including two Visrag models and three vanilla-rag models

# Download models (requires config/models_lists.yaml configuration)
python $(pwd)/scripts/download_model.py 

# Create logs directory if not exists
mkdir -p $(pwd)/logs

# Start HuggingFace LLM service
export CUDA_VISIBLE_DEVICES=0
nohup python -m ultrarag.server.run_server_hf_llm \
    -host localhost \
    -port 8844 \
    -model_path $(pwd)/resource/models/MiniCPM-V-2_6 \
    -device cuda:0 \
> $(pwd)/logs/hf_llm.log 2>&1 &
HF_PID=$!

# Start embedding service
export CUDA_VISIBLE_DEVICES=0
nohup python -m ultrarag.server.run_embedding \
    -host localhost \
    -port 8845 \
    -model_path $(pwd)/resource/models/MiniCPM-Embedding-Light \
    -device cuda:0 \
> $(pwd)/logs/MiniCPM-Embedding-Light.log 2>&1 &
EMBED_PID=$!

# Start reranker service
export CUDA_VISIBLE_DEVICES=0
nohup python -m ultrarag.server.run_server_reranker \
    -host localhost \
    -port 8846 \
    -model_path $(pwd)/resource/models/MiniCPM-Reranker-Light \
    -model_type bge_reranker \
> $(pwd)/logs/MiniCPM-Reranker-Light.log 2>&1 &
RERNK_PID=$!

# Start VisRAG embedding service
export CUDA_VISIBLE_DEVICES=0
nohup python -m ultrarag.server.run_embedding \
    -host localhost \
    -port 8848 \
    -model_path $(pwd)/resource/models/VisRAG-Ret \
    -device cuda:0 \
> $(pwd)/logs/VisRAG-Ret.log 2>&1 &
EMBED_PID=$!

# Start vLLM service for Minicpm model
export CUDA_VISIBLE_DEVICES=1
nohup vllm serve \
    $(pwd)/resource/models/MiniCPM3-4B \
    --host localhost \
    --port 8847 \
    --dtype auto \
    --served-model-name MiniCPM3-4B \
    --trust-remote-code \
    --api-key empty \
> $(pwd)/logs/vllm.log 2>&1 &
VLLM_PID=$!

# Start Qdrant vector database
nohup /opt/qdrant > $(pwd)/logs/qdrant.log 2>&1 &

# Start Streamlit web interface
streamlit run ultrarag/webui/webui.py

# Commented out shutdown logic
# # Infinite loop
# echo "Press Enter to stop services"
# read name
# echo "Killing processes..."
# kill $EMBED_PID
# kill $RERNK_PID
# kill $VLLM_PID