#!/bin/bash

# Get root directory of the git repository
REPO_ROOT=$(git rev-parse --show-toplevel)

DEFAULT_MODEL_NAME_OR_PATH="/public/kqa/440M_v0"
DEFAULT_OUTPUT_DIR="$REPO_ROOT/workspace/train_session/checkpoints"
DEFAULT_TRAIN_DATA="$REPO_ROOT/workspace/dataset/"
DEFAULT_TRAIN_GROUP_SIZE=1
DEFAULT_LEARNING_RATE=7e-6
DEFAULT_NUM_TRAIN_EPOCHS=2
DEFAULT_PER_DEVICE_TRAIN_BATCH_SIZE=128
DEFAULT_QUERY_MAX_LEN=512
DEFAULT_PASSAGE_MAX_LEN=512
DEFAULT_PAD_TO_MULTIPLE_OF=8
DEFAULT_KNOWLEDGE_DISTILLATION="False"
DEFAULT_SAME_DATASET_WITHIN_BATCH="True"
DEFAULT_SMALL_THRESHOLD=0
DEFAULT_DROP_THRESHOLD=0
DEFAULT_OVERWRITE_OUTPUT_DIR="True"
DEFAULT_FP16="True"
DEFAULT_DATALOADER_DROP_LAST="True"
DEFAULT_WARMUP_RATIO=0.1
DEFAULT_GRADIENT_CHECKPOINTING="True"
DEFAULT_DEEPSPEED="./config/ds_stage0.json"
DEFAULT_LOGGING_STEPS=1
DEFAULT_SAVE_STEPS=1000
DEFAULT_NEGATIVES_CROSS_DEVICE="True"
DEFAULT_TEMPERATURE=0.02
DEFAULT_NORMALIZE_EMBEDDINGS="True"
DEFAULT_KD_LOSS_TYPE="m3_kd_loss"
DEFAULT_UNIFIED_FINETUNING="False"
DEFAULT_USE_SELF_DISTILL="False"
DEFAULT_FIX_ENCODER="False"
DEFAULT_SELF_DISTILL_START_STEP=0
DEFAULT_TRUST_REMOTE_CODE="True"
DEFAULT_SENTENCE_POOLING_METHOD="mean"
DEFAULT_QUERY_INSTRUCTION_FOR_RETRIEVAL=""

# Parameter parsing
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --model_name_or_path) MODEL_NAME_OR_PATH="$2"; shift ;;
        --output_dir) OUTPUT_DIR="$2"; shift ;;
        --train_data) TRAIN_DATA="$2"; shift ;;
        --train_group_size) TRAIN_GROUP_SIZE="$2"; shift ;;
        --learning_rate) LEARNING_RATE="$2"; shift ;;
        --num_train_epochs) NUM_TRAIN_EPOCHS="$2"; shift ;;
        --per_device_train_batch_size) PER_DEVICE_TRAIN_BATCH_SIZE="$2"; shift ;;
        --query_max_len) QUERY_MAX_LEN="$2"; shift ;;
        --passage_max_len) PASSAGE_MAX_LEN="$2"; shift ;;
        --pad_to_multiple_of) PAD_TO_MULTIPLE_OF="$2"; shift ;;
        --knowledge_distillation) KNOWLEDGE_DISTILLATION="$2"; shift ;;
        --same_dataset_within_batch) SAME_DATASET_WITHIN_BATCH="$2"; shift ;;
        --small_threshold) SMALL_THRESHOLD="$2"; shift ;;
        --drop_threshold) DROP_THRESHOLD="$2"; shift ;;
        --overwrite_output_dir) OVERWRITE_OUTPUT_DIR="$2"; shift ;;
        --fp16) FP16="$2"; shift ;;
        --dataloader_drop_last) DATALOADER_DROP_LAST="$2"; shift ;;
        --warmup_ratio) WARMUP_RATIO="$2"; shift ;;
        --gradient_checkpointing) GRADIENT_CHECKPOINTING="$2"; shift ;;
        --deepspeed) DEEPSPEED="$2"; shift ;;
        --logging_steps) LOGGING_STEPS="$2"; shift ;;
        --save_steps) SAVE_STEPS="$2"; shift ;;
        --negatives_cross_device) NEGATIVES_CROSS_DEVICE="$2"; shift ;;
        --temperature) TEMPERATURE="$2"; shift ;;
        --normalize_embeddings) NORMALIZE_EMBEDDINGS="$2"; shift ;;
        --kd_loss_type) KD_LOSS_TYPE="$2"; shift ;;
        --unified_finetuning) UNIFIED_FINETUNING="$2"; shift ;;
        --use_self_distill) USE_SELF_DISTILL="$2"; shift ;;
        --fix_encoder) FIX_ENCODER="$2"; shift ;;
        --self_distill_start_step) SELF_DISTILL_START_STEP="$2"; shift ;;
        --trust_remote_code) TRUST_REMOTE_CODE="$2"; shift ;;
        --sentence_pooling_method) SENTENCE_POOLING_METHOD="$2"; shift ;;
        --query_instruction_for_retrieval) QUERY_INSTRUCTION_FOR_RETRIEVAL="$2"; shift ;;
        *) echo "Unknown parameter passed: $1";
    esac
    shift
done

# Use default values if not provided
MODEL_NAME_OR_PATH=${MODEL_NAME_OR_PATH:-$DEFAULT_MODEL_NAME_OR_PATH}
OUTPUT_DIR=${OUTPUT_DIR:-$DEFAULT_OUTPUT_DIR}
TRAIN_DATA=${TRAIN_DATA:-$DEFAULT_TRAIN_DATA}
TRAIN_GROUP_SIZE=${TRAIN_GROUP_SIZE:-$DEFAULT_TRAIN_GROUP_SIZE}
LEARNING_RATE=${LEARNING_RATE:-$DEFAULT_LEARNING_RATE}
NUM_TRAIN_EPOCHS=${NUM_TRAIN_EPOCHS:-$DEFAULT_NUM_TRAIN_EPOCHS}
PER_DEVICE_TRAIN_BATCH_SIZE=${PER_DEVICE_TRAIN_BATCH_SIZE:-$DEFAULT_PER_DEVICE_TRAIN_BATCH_SIZE}
QUERY_MAX_LEN=${QUERY_MAX_LEN:-$DEFAULT_QUERY_MAX_LEN}
PASSAGE_MAX_LEN=${PASSAGE_MAX_LEN:-$DEFAULT_PASSAGE_MAX_LEN}
PAD_TO_MULTIPLE_OF=${PAD_TO_MULTIPLE_OF:-$DEFAULT_PAD_TO_MULTIPLE_OF}
KNOWLEDGE_DISTILLATION=${KNOWLEDGE_DISTILLATION:-$DEFAULT_KNOWLEDGE_DISTILLATION}
SAME_DATASET_WITHIN_BATCH=${SAME_DATASET_WITHIN_BATCH:-$DEFAULT_SAME_DATASET_WITHIN_BATCH}
SMALL_THRESHOLD=${SMALL_THRESHOLD:-$DEFAULT_SMALL_THRESHOLD}
DROP_THRESHOLD=${DROP_THRESHOLD:-$DEFAULT_DROP_THRESHOLD}
OVERWRITE_OUTPUT_DIR=${OVERWRITE_OUTPUT_DIR:-$DEFAULT_OVERWRITE_OUTPUT_DIR}
FP16=${FP16:-$DEFAULT_FP16}
DATALOADER_DROP_LAST=${DATALOADER_DROP_LAST:-$DEFAULT_DATALOADER_DROP_LAST}
WARMUP_RATIO=${WARMUP_RATIO:-$DEFAULT_WARMUP_RATIO}
GRADIENT_CHECKPOINTING=${GRADIENT_CHECKPOINTING:-$DEFAULT_GRADIENT_CHECKPOINTING}
DEEPSPEED=${DEEPSPEED:-$DEFAULT_DEEPSPEED}
LOGGING_STEPS=${LOGGING_STEPS:-$DEFAULT_LOGGING_STEPS}
SAVE_STEPS=${SAVE_STEPS:-$DEFAULT_SAVE_STEPS}
NEGATIVES_CROSS_DEVICE=${NEGATIVES_CROSS_DEVICE:-$DEFAULT_NEGATIVES_CROSS_DEVICE}
TEMPERATURE=${TEMPERATURE:-$DEFAULT_TEMPERATURE}
NORMALIZE_EMBEDDINGS=${NORMALIZE_EMBEDDINGS:-$DEFAULT_NORMALIZE_EMBEDDINGS}
KD_LOSS_TYPE=${KD_LOSS_TYPE:-$DEFAULT_KD_LOSS_TYPE}
UNIFIED_FINETUNING=${UNIFIED_FINETUNING:-$DEFAULT_UNIFIED_FINETUNING}
USE_SELF_DISTILL=${USE_SELF_DISTILL:-$DEFAULT_USE_SELF_DISTILL}
FIX_ENCODER=${FIX_ENCODER:-$DEFAULT_FIX_ENCODER}
SELF_DISTILL_START_STEP=${SELF_DISTILL_START_STEP:-$DEFAULT_SELF_DISTILL_START_STEP}
TRUST_REMOTE_CODE=${TRUST_REMOTE_CODE:-$DEFAULT_TRUST_REMOTE_CODE}
SENTENCE_POOLING_METHOD=${SENTENCE_POOLING_METHOD:-$DEFAULT_SENTENCE_POOLING_METHOD}
QUERY_INSTRUCTION_FOR_RETRIEVAL=${QUERY_INSTRUCTION_FOR_RETRIEVAL:-$DEFAULT_QUERY_INSTRUCTION_FOR_RETRIEVAL}

# Start torchrun training
torchrun --nproc_per_node 1 \
    -m ultrarag.finetune.bgem3 \
    --model_name_or_path $MODEL_NAME_OR_PATH \
    --output_dir $OUTPUT_DIR \
    --train_data $TRAIN_DATA \
    --train_group_size $TRAIN_GROUP_SIZE \
    --learning_rate $LEARNING_RATE \
    --num_train_epochs $NUM_TRAIN_EPOCHS \
    --per_device_train_batch_size $PER_DEVICE_TRAIN_BATCH_SIZE \
    --query_max_len $QUERY_MAX_LEN \
    --passage_max_len $PASSAGE_MAX_LEN \
    --pad_to_multiple_of $PAD_TO_MULTIPLE_OF \
    --knowledge_distillation $KNOWLEDGE_DISTILLATION \
    --same_dataset_within_batch $SAME_DATASET_WITHIN_BATCH \
    --small_threshold $SMALL_THRESHOLD \
    --drop_threshold $DROP_THRESHOLD \
    --overwrite_output_dir $OVERWRITE_OUTPUT_DIR \
    --fp16 $FP16 \
    --dataloader_drop_last $DATALOADER_DROP_LAST \
    --warmup_ratio $WARMUP_RATIO \
    --gradient_checkpointing $GRADIENT_CHECKPOINTING \
    --deepspeed $DEEPSPEED \
    --logging_steps $LOGGING_STEPS \
    --save_steps $SAVE_STEPS \
    --negatives_cross_device $NEGATIVES_CROSS_DEVICE \
    --temperature $TEMPERATURE \
    --normalize_embeddings $NORMALIZE_EMBEDDINGS \
    --kd_loss_type $KD_LOSS_TYPE \
    --unified_finetuning $UNIFIED_FINETUNING \
    --use_self_distill $USE_SELF_DISTILL \
    --fix_encoder $FIX_ENCODER \
    --self_distill_start_step $SELF_DISTILL_START_STEP \
    --trust_remote_code $TRUST_REMOTE_CODE \
    --sentence_pooling_method $SENTENCE_POOLING_METHOD \
    --query_instruction_for_retrieval  $QUERY_INSTRUCTION_FOR_RETRIEVAL
