
# UltraRAG 2.0入门教程：从零跑通RAG

## 什么是RAG？

> 想象你在参加一次开卷考试。你本人就是大语言模型，具备理解题目和写答案的能力。  
> 但你不可能记住所有知识点。这时，允许你带一本教材或参考书进考场——这就是检索。  
> 当你翻书找到相关内容，再结合自己的理解去写答案，这样答案既准确又有根据。  
> 这就是 RAG —— 检索增强生成。

RAG（Retrieval-Augmented Generation，检索增强生成）是一种让大语言模型（LLM）在“生成”之前，先去“检索”相关文档或知识库，再结合这些信息生成回答的技术。

### 流程

**检索阶段**：根据用户问题，从文档库中找到最相关的内容（比如知识库、网页等）；  
<p align="left">
  <img src="../image/00/retrieve_stage.png" alt="检索阶段" width="300"/>
</p>

**生成阶段**：把检索到的内容作为上下文，输入给 LLM，让它基于这些信息生成回答  
<p align="left">
  <img src="../image/00/gen_stage.png" alt="生成阶段" width="300"/>
</p>

### 作用

- 提升准确度、降低“幻觉”
- 无需重训模型，也能保持时效性和专业性
- 增强可信度
  

## 关于UltraRAG 2.0
UltraRAG 2.0 是由清华大学 THUNLP 实验室、东北大学 NEUIR 实验室、OpenBMB 和 AI9stars 联合推出的开源 RAG 框架。它最大的特色，是首个基于 Model Context Protocol，也就是 MCP 架构设计的 RAG 系统。
借助 MCP 的模块化设计，研究者只需要编写一份 YAML 文件，就能直接描述检索和生成的完整流程。无论是简单的串行推理，还是更复杂的循环、条件分支逻辑，都可以轻松实现。
<p align="left">
  <img src="../image/00/architecture.png" alt="架构" />
</p>
这种方式大幅降低了工程实现的复杂度。科研人员无需再为繁琐的控制逻辑耗费时间，可以将更多精力投入到实验设计和算法创新中。用一句话总结就是：**少写代码，多写想法**。


## 安装

1. 克隆仓库

```bash
git clone https://github.com/OpenBMB/UltraRAG.git
cd UltraRAG
```

2. 创建并激活虚拟环境

```bash
conda create -n ultrarag python=3.11
conda activate ultrarag

pip install uv
uv pip install -e .

# If you want to use faiss for vector indexing:
# You need to manually compile and install the CPU or GPU version of FAISS depending on your hardware environment:
# CPU version:
uv pip install faiss-cpu
# GPU version (example: CUDA 12.x)
uv pip install faiss-gpu-cu12
# For other CUDA versions, install the corresponding package (e.g., faiss-gpu-cu11 for CUDA 11.x).

# If you want to use infinity_emb for corpus encoding and indexing:
uv pip install -e ."[infinity_emb]"

# If you want to use lancedb vector database:
uv pip install -e ."[lancedb]"

# If you want to deploy models with vLLM service:
uv pip install -e ."[vllm]"

# If you want to use corpus document parsing functionality:
uv pip install -e ."[corpus]"

# ====== Install all dependencies (except faiss) ======
uv pip install -e ."[all]"
```

3. 验证安装

```bash
# 输出：Hello, UltraRAG 2.0!
ultrarag run examples/sayhello.yaml
```

## 语料库编码与索引

在使用 RAG 之前，需要先将原始文档转化为 向量表示，并建立 检索索引。这样，当用户提问时，系统才能在大规模语料库中快速找到最相关的内容。
- **编码（Embedding）**：把自然语言文本转化为向量，让计算机可以用数学方式比较语义相似度。
- **索引（Indexing）**：把这些向量组织起来，比如用 FAISS，这样检索时才能在几百万条文档中瞬间找到最相关的若干条。

<p align="left">
  <img src="../image/00/emb_index.png" alt="编码与索引" />
</p>

### 示例语料（Wiki 文本）

```json
{
    "id": "2066692", 
    "contents": "Truman Sports Complex The Harry S. Truman Sports Complex is a sports and entertainment facility located in Kansas City, Missouri. It is home to two major sports venues: Arrowhead Stadium—home of the National Football League's Kansas City Chiefs, and Kauffman Stadium—home of Major League Baseball's Kansas City Royals. The complex also hosts various other events during the year."
}
```
这是一条典型的 Wiki 语料，其中 id 是文档的唯一标识符，contents 是实际的文本内容。后续我们会对 contents 做向量化并建立索引。

### 编写编码、索引Pipeline

```yaml
# MCP Server
servers:
  retriever: servers/retriever

# MCP Client Pipeline
pipeline:
- retriever.retriever_init
- retriever.retriever_embed
- retriever.retriever_index
```
这里定义了一个最小的三步流程：初始化 → 编码 → 建索引。

### 编译Pipeline文件

```bash
ultrarag build examples/embedding_and_index.yaml
```

### 修改参数文件

```yaml
# examples/parameter/embedding_and_index_parameter.yaml
retriever:
  corpus_path: data/corpus_example.jsonl
  cuda_devices: 0,1
  embedding_path: embedding/embedding.npy
  faiss_use_gpu: true
  index_chunk_size: 50000
  index_path: index/index.index
  infinity_kwargs:
    batch_size: 16
    bettertransformer: false
    device: cuda
    pooling_method: cls
  overwrite: false
  retriever_path: your_path
```

### 运行Pipeline文件

```bash
ultrarag run examples/embedding_and_index.yaml
```
运行成功后，就会得到对应的语料向量和索引文件，后续 RAG Pipeline 就可以直接使用它们来完成检索。

## 搭建RAG Pipeline

当语料库的索引准备完成后，下一步就是将 检索器 和 大语言模型（LLM） 组合起来，搭建一个完整的 RAG Pipeline。这样，问题可以经过检索找到相关文档，再交由模型生成最终回答。

### 检索流程

<p align="left">
  <img src="../image/00/retrieve.png" alt="检索" />
</p>

### 生成流程

<p align="left">
  <img src="../image/00/gen_stage.png" alt="检索" />
</p>

### 数据格式（以 NQ 数据集为例）

```json
{
    "id": 0, 
    "question": "when was the last time anyone was on the moon", 
    "golden_answers": ["14 December 1972 UTC", "December 1972"], 
    "meta_data": {}
}
```
每条样本包含问题、标准答案（golden_answers）和附加信息（meta_data），后续会作为输入与评测基准。

### 编写RAG Pipeline

```yaml
# Vanilla RAG demo

# MCP Server
servers:
  benchmark: servers/benchmark
  retriever: servers/retriever
  prompt: servers/prompt
  generation: servers/generation
  evaluation: servers/evaluation
  custom: servers/custom

# MCP Client Pipeline
pipeline:
- benchmark.get_data
- retriever.retriever_init
- retriever.retriever_search
- generation.initialize_local_vllm
- prompt.qa_rag_boxed
- generation.generate
- custom.output_extract_from_boxed
- evaluation.evaluate
```

整个流程依次完成：
1. 读取数据 → 2. 初始化检索器并搜索 → 3. 启动 LLM 服务 →
2. 拼接 Prompt → 5. 生成回答 → 6. 提取结果 → 7. 评测性能。

### 编译 Pipeline 文件

```bash
ultrarag build examples/vanilla_rag.yaml
```

### 修改参数文件（指定数据集、模型与检索配置）

```yaml
# examples/parameter/vanilla_rag_parameter.yaml
benchmark:
  benchmark:
    key_map:
      gt_ls: golden_answers
      q_ls: question
    limit: -1
    name: nq
    path: data/sample_nq_10.jsonl
    seed: 42
    shuffle: false
custom: {}
evaluation:
  metrics:
  - acc
  - f1
  - em
  - coverem
  - stringem
  - rouge-1
  - rouge-2
  - rouge-l
  save_path: output/evaluate_results.json
generation:
  api_key: ''
  base_url: http://localhost:8000/v1
  gpu_ids: 2,3
  model_name: Qwen3-8B
  model_path: your_path
  port: 8081
  sampling_params:
    extra_body:
      chat_template_kwargs:
        enable_thinking: false
      include_stop_str_in_output: true
      top_k: 20
    max_tokens: 2048
    temperature: 0.7
    top_p: 0.8
prompt:
  template: prompt/qa_rag_boxed.jinja
retriever:
  corpus_path: data/corpus_example.jsonl
  cuda_devices: '0'
  faiss_use_gpu: true
  index_path: index/index.index
  infinity_kwargs:
    batch_size: 1024
    bettertransformer: false
    device: cuda
    pooling_method: auto
  query_instruction: 'Query: '
  retriever_path: your_path
  top_k: 5
  use_openai: false
```

### 运行Pipeline文件

```bash
ultrarag run examples/vanilla_rag.yaml
```

### 查看生成结果

使用可视化脚本快速浏览模型输出

```python
python ./script/case_study.py \
  --data output/memory_nq_vanilla_rag_20250830_161907.json \
  --host 0.0.0.0 \
  --port 8017 \
  --title "Case Study Viewer"
```
