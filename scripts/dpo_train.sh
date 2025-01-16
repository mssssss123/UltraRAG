gpu_vis=0,1,2,3
MASTER_PORT=2223
deepspeed  --include localhost:$gpu_vis --master_port $MASTER_PORT /home/chenhao23/UltraRAG/scripts/6_dpo_train.py \
    --model_name_or_path /home/chenhao23/RAG/models/MiniCPM-4B/minicpm_release \
    --train_data_path /home/chenhao23/UltraRAG/data/DPO_data/train.jsonl \
    --eval_data_path /home/chenhao23/UltraRAG/data/DPO_data/dev.jsonl \
    --max_length 2200 \
    --max_prompt_length 2100 \
    --output_dir /home/chenhao23/UltraRAG/checkpoint/1210cpm3/train \
    --save_steps 100 \
    --eval_steps 100 \
    --per_device_train_batch_size 1 \
    --per_device_eval_batch_size 2 \
    --learning_rate 5e-5 \
    --evaluation_strategy steps \
    --logging_strategy steps \
    --logging_steps 10 \
    --logging_dir /home/chenhao23/UltraRAG/checkpoint/1210cpm3/log \
    --bf16 True \
    --use_lora True \
    --num_train_epochs 1 \
    --llama_style False \
    --cpm3 True \
    --deepspeed /home/chenhao23/RAG_Minicpm_2B/MiniCPM/finetune/configs/ds_config_zero2.json > /home/chenhao23/UltraRAG/checkpoint/1210cpm3/run.log 2>&1 &

