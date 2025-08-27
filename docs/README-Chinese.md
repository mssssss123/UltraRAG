<!-- markdownlint-disable MD001 MD041 -->
<p align="center">
  <picture>
    <img alt="UltraRAG" src="../docs/ultrarag.svg" width=55%>
  </picture>
</p>

<h3 align="center">
更少代码，更低门槛，更快实现
</h3>

<p align="center">
| 
<a href="https://openbmb.github.io/UltraRAG"><b>项目主页</b></a> 
| 
<a href="https://ultrarag.openbmb.cn"><b>教程文档</b></a> 
| 
<a href="https://huggingface.co/datasets/UltraRAG/UltraRAG_Benchmark"><b>数据集</b></a> 
| 
<a href="https://pbem31gvoj.feishu.cn/sheets/TfbisiADfhOpnnt9wBhcE5gsn4o?from=from_copylink&sheet=4d3449"><b>评测榜</b></a>
|
<a href="../README.md"><b>英文</b></a>
|
<b>中文</b>
|
</p>

---
## UltraRAG 2.0：面向科研的“RAG实验”加速器 

检索增强生成系统（RAG）正从早期“检索+生成”的简单拼接，走向融合 **自适应知识组织**、**多轮推理**、**动态检索** 的复杂知识系统（典型代表如 *DeepResearch*、*Search-o1*）。但这种复杂度的提升，使科研人员在 **方法复现**、**快速迭代新想法** 时，面临着高昂的工程实现成本。

为了解决这一痛点，清华大学 [THUNLP](https://nlp.csai.tsinghua.edu.cn/) 实验室、东北大学 [NEUIR](https://neuir.github.io) 实验室、[OpenBMB](https://www.openbmb.cn/home) 与 [AI9stars](https://github.com/AI9Stars) 联合推出 UltraRAG 2.0 （UR-2.0）—— 首个基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/overview) 架构设计的 RAG 框架。这一设计让科研人员只需编写 YAML 文件，就可以直接声明串行、循环、条件分支等复杂逻辑，从而以极低的代码量快速实现多阶段推理系统。

其核心思路是：
- 组件化封装：将RAG 的核心组件封装为**标准化的独立 MCP Server**；
- 灵活调用与扩展：提供 **函数级 Tool** 接口，支持功能的灵活调用与扩展；
- 轻量流程编排：借助 **MCP Client**，建立自上而下的简洁化链路搭建；

与传统框架相比，UltraRAG 2.0 显著降低了复杂 RAG 系统的 **技术门槛与学习成本**，让研究者能够将更多精力投入到 **实验设计与算法创新** 上，而不是陷入冗长的工程实现。

## 🌟 核心亮点

- 🚀 **低代码构建复杂 Pipeline**  
  原生支持 **串行、循环、条件分支** 等推理控制结构。开发者只需编写 YAML 文件，即可实现几十行代码构建的 **迭代式 RAG 流程**（如 *Search-o1* 等）。  

- ⚡ **快速复现与功能扩展**  
  基于 **MCP 架构**，所有模块均封装为独立、可复用的 **Server**。  
  - 用户可按需自定义 Server 或直接复用现有模块；  
  - 每个 Server 的功能以函数级 **Tool** 注册，新增功能仅需添加一个函数即可接入完整流程；  
  - 同时支持调用 **外部 MCP Server**，轻松扩展 Pipeline 能力与应用场景。  

- 📊 **统一评测与对比**  
  内置 **标准化评测流程与指标管理**，开箱即用支持 17 个主流科研 Benchmark。  
  - 持续集成最新基线；  
  - 提供 Leaderboard 结果；  
  - 方便科研人员进行系统性对比与优化实验。  

## 秘诀：MCP 架构与原生流程控制

在不同的 RAG 系统中，检索、生成等核心能力在功能上具有高度相似性，但由于开发者实现策略各异，模块之间往往缺乏统一接口，难以跨项目复用。[Model Context Protocol (MCP)](https://modelcontextprotocol.io/overview) 作为一种开放协议，规范了为大型语言模型（LLMs）提供上下文的标准方式，并采用 **Client–Server** 架构，使得遵循该协议开发的 Server 组件可以在不同系统间无缝复用。

受此启发，UltraRAG 2.0 基于 **MCP 架构**，将 RAG 系统中的检索、生成、评测等核心功能抽象并封装为相互独立的 **MCP Server**，并通过标准化的函数级 **Tool 接口**实现调用。这一设计既保证了模块功能扩展的灵活性，又允许新模块以“热插拔”的方式接入，无需对全局代码进行侵入式修改。在科研场景中，这种架构让研究者能够以极低的代码量快速适配新的模型或算法，同时保持整体系统的稳定性与一致性。

<p align="center">
  <picture>
    <img alt="UltraRAG" src="../docs/architecture.png" width=90%>
  </picture>
</p>

复杂 RAG 推理框架的开发具有显著挑战，而 UltraRAG 2.0 之所以能够在**低代码**条件下支持复杂系统的构建，核心在于其底层对多结构 **Pipeline 流程控制**的原生支持。无论是串行、循环还是条件分支，所有控制逻辑均可在 YAML 层完成定义与调度，覆盖复杂推理任务所需的多种流程表达方式。在实际运行中，推理流程的调度由内置 **Client** 执行，其逻辑完全由用户编写的外部 **Pipeline YAML 脚本** 脚本描述，从而实现与底层实现的解耦。开发者可以像使用编程语言关键字一样调用 loop、step 等指令，以声明式方式快速构建多阶段推理流程。

通过将 **MCP 架构** 与 **原生流程控制**深度融合，UltraRAG 2.0 让复杂 RAG 系统的搭建像“编排流程”一样自然高效。此外，框架内置 17 个主流 benchmark 任务与多种高质量 baseline，配合统一的评测体系与知识库支持，进一步提升了系统开发的效率与实验的可复现性。

## 快速开始

使用 Conda 创建虚拟环境：

```shell
conda create -n ultrarag python=3.11
conda activate ultrarag
```
通过 git 克隆项目到本地或服务器：

```shell
git clone https://github.com/OpenBMB/UltraRAG.git
cd UltraRAG
```

我们推荐使用 uv 来进行包管理，提供更快、更可靠的 Python 依赖管理体验：

```shell
pip install uv
uv pip install -e .
```

如果您更习惯 pip，也可以直接运行：

```shell
pip install -e .
```


【可选】UR-2.0支持丰富的Server组件，开发者可根据实际任务灵活安装所需依赖：

```shell
# 如需使用faiss进行向量索引：
# 需要根据自己的硬件环境，手动编译安装 CPU 或 GPU 版本的 FAISS：
# CPU版本：
uv pip install faiss-cpu
# GPU版本：
uv pip install faiss-gpu-cu12

# 如需使用infinity_emb进行语料库编码和索引：
uv pip install -e ."[infinity_emb]"

# 如需使用lancedb向量数据库：
uv pip install -e ."[lancedb]"

# 如需使用vLLM服务部署模型：
uv pip install -e ."[vllm]"

# 如需使用语料库文档解析功能：
uv pip install -e ."[corpus]"

# ====== 安装所有依赖（除faiss） ======
uv pip install -e ."[all]"
```


我们配套提供了从入门到进阶的完整教学示例，欢迎访问[教程文档](https://ultrarag.openbmb.cn
)快速上手 UltraRAG 2.0！

## 支持

UltraRAG 2.0 开箱即用，内置支持当前 RAG 领域最常用的 **公开评测数据集**、**大规模语料库** 以及 **典型基线方法**，方便科研人员快速复现与扩展实验。你也可以参考[数据格式说明](https://ultrarag.openbmb.cn/pages/cn/tutorials/part_3/prepare_dataset)，灵活地自定义并添加任意数据集或语料库。完整的[数据集](https://huggingface.co/datasets/UltraRAG/UltraRAG_Benchmark)可通过该链接访问与下载。

### 1. 支持的数据集

| 任务类型         | 数据集名称           | 原始数据数量                               | 评测采样数量       |
|------------------|----------------------|--------------------------------------------|--------------------|
| QA               | [NQ](https://huggingface.co/datasets/google-research-datasets/nq_open)                   | 3,610                                      | 1,000              |
| QA               | [TriviaQA](https://nlp.cs.washington.edu/triviaqa/)             | 11,313                                     | 1,000              |
| QA               | [PopQA](https://huggingface.co/datasets/akariasai/PopQA)                | 14,267                                     | 1,000              |
| QA               | [AmbigQA](https://huggingface.co/datasets/sewon/ambig_qa)              | 2,002                                      | 1,000              |
| QA               | [MarcoQA](https://huggingface.co/datasets/microsoft/ms_marco/viewer/v2.1/validation)              | 55,636         | 1,000|
| QA               | [WebQuestions](https://huggingface.co/datasets/stanfordnlp/web_questions)         | 2,032                                      | 1,000              |
| Multi-hop QA     | [HotpotQA](https://huggingface.co/datasets/hotpotqa/hotpot_qa)             | 7,405                                      | 1,000              |
| Multi-hop QA     | [2WikiMultiHopQA](https://www.dropbox.com/scl/fi/heid2pkiswhfaqr5g0piw/data.zip?e=2&file_subpath=%2Fdata&rlkey=ira57daau8lxfj022xvk1irju)      | 12,576                                     | 1,000              |
| Multi-hop QA     | [Musique](https://drive.google.com/file/d/1tGdADlNjWFaHLeZZGShh2IRcpO6Lv24h/view)              | 2,417                                      | 1,000              |
| Multi-hop QA     | [Bamboogle](https://huggingface.co/datasets/chiayewken/bamboogle)            | 125                                        | 125                |
| Multi-hop QA     | [StrategyQA](https://huggingface.co/datasets/tasksource/strategy-qa)          | 2,290                                      | 1,000              |
| Multiple-choice  | [ARC](https://huggingface.co/datasets/allenai/ai2_arc)                  | 3,548    | 1,000              |
| Multiple-choice  | [MMLU](https://huggingface.co/datasets/cais/mmlu)                 | 14,042                      | 1,000              |
| Long-form QA     | [ASQA](https://huggingface.co/datasets/din0s/asqa)                 | 948                                        | 948                |
| Fact-verification| [FEVER](https://fever.ai/dataset/fever.html)                | 13,332    | 1,000              |
| Dialogue         | [WoW](https://huggingface.co/datasets/facebook/kilt_tasks)                  | 3,054                                      | 1,000              |
| Slot-filling     | [T-REx](https://huggingface.co/datasets/facebook/kilt_tasks)                | 5,000                                      | 1,000              |

---

### 2. 支持的语料库

| 语料库名称 | 文档数量     |
|------------|--------------|
| [wiki-2018](https://huggingface.co/datasets/RUC-NLPIR/FlashRAG_datasets/tree/main/retrieval-corpus)   | 21,015,324   |
| wiki-2024   | 整理中，即将上线 |

---

### 3. 支持的基线方法（持续更新）

| 基线名称 | 脚本     |
|------------|--------------|
| Vanilla LLM   | examples/vanilla.yaml   |
| Vanilla RAG   | examples/rag.yaml     |
| [IRCoT](https://arxiv.org/abs/2212.10509)   | examples/IRCoT.yaml   |
| [IterRetGen](https://arxiv.org/abs/2305.15294)   | examples/IterRetGen.yaml     |
| [RankCoT](https://arxiv.org/abs/2502.17888)   | examples/RankCoT.yaml   |
| [R1-searcher](https://arxiv.org/abs/2503.05592)   | examples/r1_searcher.yaml     |
| [Search-o1](https://arxiv.org/abs/2501.05366)   | examples/search_o1.yaml   |
| [Search-r1](https://arxiv.org/abs/2503.09516)   | examples/search_r1.yaml     |
| WebNote   | examples/webnote.yaml    |

## 引用

如果您认为本仓库对研究有价值，欢迎给予 ⭐ 支持，并在相关研究中引用本工作。

```bibtex
@article{chen2025ultrarag,
  title={UltraRAG: A Modular and Automated Toolkit for Adaptive Retrieval-Augmented Generation},
  author={Chen, Yuxuan and Guo, Dewen and Mei, Sen and Li, Xinze and Chen, Hao and Li, Yishan and Wang, Yixuan and Tang, Chaoyue and Wang, Ruobing and Wu, Dingjun and others},
  journal={arXiv preprint arXiv:2504.08761},
  year={2025}
}
```

## 贡献指南

我们欢迎社区贡献！  
- 提交 Bug 或功能请求：请使用 [GitHub Issues](https://github.com/OpenBMB/UltraRAG/issues)  
- 提交代码：请先在 Issue 中讨论，再通过 Pull Request 提交  


## 联系我们

- 关于技术问题及功能请求，请使用 [GitHub Issues](https://github.com/OpenBMB/UltraRAG/issues) 功能。