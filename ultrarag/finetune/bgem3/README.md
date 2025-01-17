# 微调

UltraRAG提供模型微调，用于微调embedding模型，提升垂直领域的文档召回效果。

#### 微调说明

在CLI环境下，可以使用以下命令微调模型，其中每次微调需要修改的参数如下所示：

| 参数                          | 说明                                     |
| ----------------------------- | ---------------------------------------- |
| --nproc_per_node              | 每个服务器节点的显卡数目                 |
| --model_name_or_path          | 指定微调前模型版本的路径                 |
| --train_data                  | 训练数据路径                             |
| --output_dir                  | 微调之后模型的输出路径                   |
| --per_device_train_batch_size | 调节batch_size, 对于小显存的显卡适度调低 |

```bash
torchrun --nproc_per_node 4 \
    -m ultrarag.finetune.bgem3 \
    --model_name_or_path resource/dataset/soda_bgem3/finetune-model/model_1128/ \
    --cache_dir ./cache/model \
    --train_data  resource/dataset/soda_bgem3/workspace/train_history_2/train_v3_incr.jsonl \
    --cache_path ./cache/data \
    --train_group_size 1 \
    --query_max_len 512 \
    --passage_max_len 512 \
    --pad_to_multiple_of 8 \
    --knowledge_distillation False \
    --same_dataset_within_batch True \
    --small_threshold 0 \
    --drop_threshold 0 \
    --output_dir resource/dataset/soda_bgem3/finetune-model/model_1206-incr/ \
    --overwrite_output_dir \
    --learning_rate 1e-5 \
    --fp16 \
    --num_train_epochs 2 \
    --per_device_train_batch_size 32 \
    --dataloader_drop_last True \
    --warmup_ratio 0.1 \
    --gradient_checkpointing \
    --deepspeed ../ds_stage0.json \
    --logging_steps 1 \
    --save_steps 1000 \
    --negatives_cross_device \
    --temperature 0.02 \
    --sentence_pooling_method cls \
    --normalize_embeddings True \
    --kd_loss_type m3_kd_loss \
    --unified_finetuning True \
    --use_self_distill False \
    --fix_encoder False \
    --self_distill_start_step 0

```

#### 支持的模型

- bgem3
- minicpm-embedding

#### 数据格式


#### 引用说明

为了减少外部依赖，我们没有直接使用FlagEmbedding的python包，此处的部分代码来源于[FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding.git)，后续我们将逐渐替换为自己的代码。
