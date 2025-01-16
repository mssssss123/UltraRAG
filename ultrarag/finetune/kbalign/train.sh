#!/bin/bash
cd "$(dirname "$0")"


create_dir() {
    local dir_path="$1"
    if [ ! -d "$dir_path" ]; then
        mkdir -p "$dir_path"
        echo "Created directory: $dir_path"
    else
        echo "Directory already exists: $dir_path"
    fi
}

# todo
gpu_vis="0,1,2,3"
master_port=2223
use_lora="--use_lora"
task_type="SFT"
model_name_or_path="/Path/to/the/pre-trained/model/or/identifier/from/the/HuggingFace/model/"
deepspeed_config_file="/DeepSpeed/config/path"
config_file="/Path/to/the/YAML/configuration/file" 
logging_dir="/Directory/to/save/the/training/logs/"
language="English"
embedding_model_path="/Path/to/the/embedding/model/"
knowledge_id="/Knowledge/collection/ID/in/Qdrant"
knowledge_stat_tab_path="/Path/to/the/knowledge/statistics/table"


# todo: you can give iter_num, train_step_num and split_num directly or give total_train_step, KB_size and to calculate others.
total_train_step=20000 # annotation_data/(batch_size*gradient_accumulation_steps*cuda_num)
pair_w_tokens=15
KB_size=640000
iter_num=3

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
        --deepspeed_config_file)
            deepspeed_config_file="$2"
            shift; shift ;;
        --config_file)
            config_file="$2"
            shift; shift ;;
        --logging_dir)
            logging_dir="$2"
            shift; shift ;;
        --language)
            language="$2"
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
        --total_train_step)
            total_train_step="$2"
            shift; shift ;;
        --pair_w_tokens)
            pair_w_tokens="$2"
            shift; shift ;;
        --KB_size)
            KB_size="$2"
            shift; shift ;;
        --iter_num)
            iter_num="$2"
            shift; shift ;;
        *)
            echo "Unknown argument: $1"
            exit 1 ;;
    esac
done


# # 8=batch_size*gradient_accumulation_steps
train_step_num=$(echo "scale=0; $KB_size/8 * $pair_w_tokens / $iter_num" | bc)
split_num=$((total_train_step / train_step_num))

input_path=/YOUR_DATASET_PATH.jsonl

bm_data_format_dir=$(dirname ${input_path})
filename=$(basename ${input_path} .jsonl)
bm_data_format_dir=${bm_data_format_dir}/kbalign/${filename}



# 分割数据集
cd verify
OPTS=""
OPTS+=" --in_path ${input_path}" # todo
OPTS+=" --output_dir ${bm_data_format_dir}/${split_num}_${train_step_num}"
OPTS+=" --num $split_num"
CMD="python split_verify.py  ${OPTS}"

echo "split dataset..."

# 分割的数量循环
for ((step_num=1; step_num<=$iter_num; step_num+=1)); do
    export CUDA_VISIBLE_DEVICES=$total_CUDA
    cd ../../dpo_and_sft
    # 第一轮用原始的训练
    last_num=$((step_num - 1))
    next_num=$((step_num + 1))
    output_dir=${model_save_path}/$train_step_num/iter$step_num
    lora_name_or_path=${model_save_path}/$train_step_num/lora_iter$step_num
    now_logging_dir=$logging_dir/$train_step_num/iter$step_num
    now_log_file=$logging_dir/$train_step_num/iter$step_num/log.log
    create_dir "$output_dir"
    create_dir "$lora_name_or_path"
    create_dir "$logging_dir"
    if [ "$step_num" -eq 1 ]; then
        train_data_path="${bm_data_format_dir}/${split_num}_${train_step_num}/part$step_num"
        model_path=$model_name_or_path
    else
        model_path=${model_save_path}/$train_step_num/iter$last_num
        train_data_path="${bm_data_format_dir}/${split_num}_${train_step_num}/part${step_num}_verify"
    fi
    # Command to run
    declare -a CMD=(
        "deepspeed"
        "--include=localhost:$gpu_vis"
        "--master_port=$master_port"
        "train.py"
        "--model_name_or_path=$model_path"
        "--task_type=$task_type"
        "--train_data_path=$train_data_path"
        "--output_dir=$lora_name_or_path"
        "--logging_dir=$logging_dir"
        $use_lora
        "--config_file=$config_file"  # Pass the config.yaml file to the Python script
        "--deepspeed=$deepspeed_config_file"  # DeepSpeed config file path
    )

    # Run the command in the background and redirect output to the log file
    nohup "${CMD[@]}" > "$log_file" 2>&1 &
    wait

    echo "Training started. Check log file: $log_file"

    save_path
    OPTS=""
    OPTS+=" --model_name_or_path $model_name_or_path"
    OPTS+=" --lora_name_or_path $lora_name_or_path"
    OPTS+=" --save_path $output_dir"
    CMD="python3 ./Merge_model.py ${OPTS}"
    echo "-------final CMD is------"
    echo "${CMD}"
    echo "-------final CMD end------"
    nohup python3 ./Merge_model.py ${OPTS} &

    # verify
    if [ "$step_num" -eq $iter_num ]; then
        echo "next"
    else
        cd ../verify
        OPTS=""
        OPTS+=" --embedding_model_path $embedding_model_path"
        OPTS+=" --knowledge_id $knowledge_id"
        OPTS+=" --knowledge_stat_tab_path $knowledge_stat_tab_path"
        OPTS+=" --in_path ${bm_data_format_dir}/${split_num}_${train_step_num}/part${next_num}.jsonl"
        OPTS+=" --out_path ${bm_data_format_dir}/${split_num}_${train_step_num}/part${next_num}_verify.jsonl"
        OPTS+=" --model_path ${output_dir}"
        OPTS+=" --language ${language}"
        CMD="python3 ./gen_iterate_verify.py ${OPTS}"
        echo "-------final CMD is------"
        echo "${CMD}"
        echo "-------final CMD end------"
        nohup python3 ./gen_iterate_verify.py ${OPTS} &
    fi
    wait
    # rm -r "${model_save_path}/$train_step_num/iter$step_num/mc/v1_$train_step_num"
done




