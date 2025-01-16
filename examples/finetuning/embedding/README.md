### 模型finetune说明

#### 背景介绍

该目录下的所有文件用于微调embedding模型，受限于训练卡，当前仅支持bert模型微调。我们期望的是，用户上传切分好的文档之后，给定大模型，我们可以合成query，构造负例，从而得到训练数据来优化模型，并可以通过评测集得到模型优化效果。

#### 部署要求

linux环境

显存不低于40GB

#### 数据格式

训练数据格式(train.jsonl)

```
{"query": "这是query1"， “pos": ["这是正例1"]， “neg": ["这是负例1"， “这是负例2"]}
{"query": "这是query2"， “pos": ["这是正例2"]， “neg": ["这是负例1"， “这是负例2"]}
```

测试数据格式(query.jsonl, corpus.jsonl, qrels.tsv)

query.jsonl:
- {"_id": "这是query1的id"， "text": "这是query1"}
- {"_id": "这是query2的id"， "text": "这是query2"}

corpus.jsonl:
- {"_id": "这是文档1的id"， "text": "这是文档1"}
- {"_id": "这是文档2的id"， "text": "这是文档2"}

qrels.tsv:
- query-id, corpus-id, score
- 这是query1的id, 这是文档1的id, 1  

#### 使用流程

当前整个文件为初版工程，还在整理之中，src中有一些脚本，分别实现了query生成、负例构建、模型微调、效果分析的整个流程。

1. 合成query的问题-文档对。

   ```
   python data_synth.py -prompt ../resource/prompt.txt -src_path ../workspace/content.jsonl -dst_path ../workspace/query-content.jsonl
   ```
2. 构造负例

   ```
   python negs_build.py -m ../resource/stella_large_zh -q ../workspace/query-content.jsonl -c ../workspace/content.jsonl -s ../workspace/train.jsonl
   ```
3. 微调模型

   deepspeed --num_gpus 1 finetune.py  -src_file ../workspace/train.jsonl -dst_path ../workspace/finetune-model
4. 测试效果

   ```
   python recall_test.py -m ../workspace/finetune-model -q ../workspace/test.jsonl -c ../workspace/corpus.jsonl -t 5 -s ../workspace/
   ```

#### 备注说明

- 微调模型的效果和生成数据质量有关系，如果文档质量不高，可能微调效果会变差
- 评测集最好自己构建，使用合成数据作为测试集测试效果一般会变好，但不意味着客观效果就会变好

#### TODO

* [ ] 优化整体流程，包括筛选数据
* [ ] 评估脚本支持编辑距离，bleu等方法判断召回是否正确，增加其他召回的评估指标，例如MRR等
* [ ] 微调流程可视化
