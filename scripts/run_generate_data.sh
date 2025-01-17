python -m ultrarag.datasets.embedding.data_synth \
    -api_key "token-abc123" \
    -base_url "http://localhost:33389/v1" \
    -model "Qwen2.5-7B-Instruct" \
    -embed resource/models/bge-large-zh-v1.5 \
    -corpus resource/research/evorag/temp.jsonl