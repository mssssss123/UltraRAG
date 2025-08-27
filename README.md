<p align="center">
  <picture>
    <img alt="UltraRAG" src="./docs/ultrarag.svg" width=55%>
  </picture>
</p>

<h3 align="center">
Less Code, Lower Barrier, Faster Deployment
</h3>

<p align="center">
| 
<a href="https://openbmb.github.io/UltraRAG"><b>Project Page</b></a> 
| 
<a href="https://ultrarag.openbmb.cn"><b>Documentation</b></a> 
| 
<a href="https://huggingface.co/datasets/UltraRAG/UltraRAG_Benchmark"><b>Datasets</b></a> 
| 
<a href="https://pbem31gvoj.feishu.cn/sheets/TfbisiADfhOpnnt9wBhcE5gsn4o?from=from_copylink&sheet=4d3449"><b>Leaderboard</b></a>
|
<b>English</b>
|
<a href="./docs/README-Chinese.md"><b>简体中文</b></a>
|
</p>

---
## UltraRAG 2.0: Accelerating RAG for Scientific Research

Retrieval-Augmented Generation (RAG) systems are evolving from early-stage simple concatenations of “retrieval + generation” to complex knowledge systems integrating **adaptive knowledge organization**, **multi-turn reasoning**, and **dynamic retrieval** (typical examples include *DeepResearch* and *Search-o1*). However, this increase in complexity imposes high engineering costs on researchers when it comes to **method reproduction** and **rapid iteration of new ideas**.

To address this challenge, [THUNLP](https://nlp.csai.tsinghua.edu.cn/), [NEUIR](https://neuir.github.io), [OpenBMB](https://www.openbmb.cn/home), and [AI9stars](https://github.com/AI9Stars) jointly launched UltraRAG 2.0 (UR-2.0) — the first RAG framework based on the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/overview) architecture design. This design allows researchers to declare complex logic such as sequential, loop, and conditional branching simply by writing YAML files, enabling rapid implementation of multi-stage reasoning systems with minimal code.

Its core ideas are:
- Modular encapsulation: Encapsulate RAG core components as **standardized independent MCP Servers**;
- Flexible invocation and extension: Provide **function-level Tool** interfaces to support flexible function calls and extensions;
- Lightweight workflow orchestration: Use **MCP Client** to build a top-down simplified linkage;

Compared with traditional frameworks, UltraRAG 2.0 significantly lowers the **technical threshold and learning cost** of complex RAG systems, allowing researchers to focus more on **experimental design and algorithm innovation** rather than lengthy engineering implementations.

## 🌟 Key Highlights

- 🚀 **Low-Code Construction of Complex Pipelines**  
  Natively supports **sequential, loop, conditional branching** and other inference control structures. Developers only need to write YAML files to build **iterative RAG workflows** with dozens of lines of code (e.g., *Search-o1*).

- ⚡ **Rapid Reproduction and Functional Extension**  
  Based on the **MCP architecture**, all modules are encapsulated as independent, reusable **Servers**.  
  - Users can customize Servers as needed or directly reuse existing modules;  
  - Each Server’s functions are registered as function-level **Tools**, and new functions can be integrated into the complete workflow by adding a single function;  
  - It also supports calling **external MCP Servers**, easily extending pipeline capabilities and application scenarios.

- 📊 **Unified Evaluation and Comparison**  
  Built-in **standardized evaluation workflows and metric management**, out-of-the-box support for 17 mainstream scientific benchmarks.  
  - Continuously integrate the latest baselines;  
  - Provide leaderboard results;  
  - Facilitate systematic comparison and optimization experiments for researchers.

## The Secret Sauce: MCP Architecture and Native Pipeline Control

In different RAG systems, core capabilities such as retrieval and generation share high functional similarity, but due to diverse implementation strategies by developers, modules often lack unified interfaces, making cross-project reuse difficult. The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/overview) is an open protocol that standardizes the way to provide context for large language models (LLMs) and adopts a **Client–Server** architecture, enabling MCP-compliant Server components to be seamlessly reused across different systems.

Inspired by this, UltraRAG 2.0 is based on the **MCP architecture**, abstracting and encapsulating core functions such as retrieval, generation, and evaluation in RAG systems into independent **MCP Servers**, and invoking them through standardized function-level **Tool interfaces**. This design ensures flexible module function extension and allows new modules to be “hot-plugged” without invasive modifications to global code. In scientific research scenarios, this architecture enables researchers to quickly adapt new models or algorithms with minimal code while maintaining overall system stability and consistency.

<p align="center">
  <picture>
    <img alt="UltraRAG" src="./docs/architecture.png" width=90%>
  </picture>
</p>

Developing complex RAG inference frameworks is significantly challenging. UltraRAG 2.0’s ability to support complex systems under **low-code** conditions lies in its native support for multi-structured **pipeline workflow control**. Whether sequential, loop, or conditional branching, all control logic can be defined and orchestrated at the YAML level, covering various workflow expression forms needed for complex inference tasks. During runtime, inference workflow scheduling is executed by the built-in **Client**, whose logic is fully described by user-written external **Pipeline YAML scripts**, achieving decoupling from the underlying implementation. Developers can call instructions like loop and step as if using programming language keywords, quickly constructing multi-stage inference workflows in a declarative manner.

By deeply integrating the **MCP architecture** with **native workflow control**, UltraRAG 2.0 makes building complex RAG systems as natural and efficient as “orchestrating workflows.” Additionally, the framework includes 17 mainstream benchmark tasks and multiple high-quality baselines, combined with a unified evaluation system and knowledge base support, further enhancing system development efficiency and experiment reproducibility.

## Quick Start

Create a virtual environment using Conda:

```shell
conda create -n ultrarag python=3.11
conda activate ultrarag
```
Clone the project locally or on a server via git:

```shell
git clone https://github.com/OpenBMB/UltraRAG.git
cd UltraRAG
```

We recommend using uv for package management, providing faster and more reliable Python dependency management:

```shell
pip install uv
uv pip install -e .
```

If you prefer pip, you can directly run:

```shell
pip install -e .
```


[Optional] UR-2.0 supports rich Server components; developers can flexibly install dependencies according to actual tasks:

```shell
# If you want to use faiss for vector indexing:
# You need to manually compile and install the CPU or GPU version of FAISS depending on your hardware environment:
# CPU version:
uv pip install faiss-cpu
# GPU version:
uv pip install faiss-gpu-cu12

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


We provide complete tutorial examples from beginner to advanced levels. Welcome to visit the [Tutorial Documentation](https://ultrarag.openbmb.cn
) to quickly get started with UltraRAG 2.0!

## Support

UltraRAG 2.0 is ready to use out-of-the-box, natively supporting the most commonly used **public evaluation datasets**, **large-scale corpus**, and **typical baseline methods** in the current RAG field, facilitating rapid reproduction and extension of experiments for researchers. You can also refer to the [Data Format Specification](https://ultrarag.openbmb.cn/pages/cn/tutorials/part_3/prepare_dataset) to flexibly customize and add any datasets or corpus. The full [datasets](https://huggingface.co/datasets/UltraRAG/UltraRAG_Benchmark) are available for access and download through this link.

### 1. Supported Datasets

| Task Type         | Dataset Name           | Original Data Size                               | Evaluation Sample Size       |
|------------------|----------------------|--------------------------------------------|--------------------|
| QA               | [NQ](https://huggingface.co/datasets/google-research-datasets/nq_open)                   | 3,610                                      | 1,000              |
| QA               | [TriviaQA](https://nlp.cs.washington.edu/triviaqa/)             | 11,313                                     | 1,000              |
| QA               | [PopQA](https://huggingface.co/datasets/akariasai/PopQA)                | 14,267                                     | 1,000              |
| QA               | [AmbigQA](https://huggingface.co/datasets/sewon/ambig_qa)              | 2,002                                      | 1,000              |
| QA               | [MarcoQA](https://huggingface.co/datasets/microsoft/ms_marco/viewer/v2.1/validation)              | 55,636           | 1,000 |
| QA               | [WebQuestions](https://huggingface.co/datasets/stanfordnlp/web_questions)         | 2,032                                      | 1,000              |
| Multi-hop QA     | [HotpotQA](https://huggingface.co/datasets/hotpotqa/hotpot_qa)             | 7,405                                      | 1,000              |
| Multi-hop QA     | [2WikiMultiHopQA](https://www.dropbox.com/scl/fi/heid2pkiswhfaqr5g0piw/data.zip?e=2&file_subpath=%2Fdata&rlkey=ira57daau8lxfj022xvk1irju)      | 12,576                                     | 1,000              |
| Multi-hop QA     | [Musique](https://drive.google.com/file/d/1tGdADlNjWFaHLeZZGShh2IRcpO6Lv24h/view)              | 2,417                                      | 1,000              |
| Multi-hop QA     | [Bamboogle](https://huggingface.co/datasets/chiayewken/bamboogle)            | 125                                        | 125                |
| Multi-hop QA     | [StrategyQA](https://huggingface.co/datasets/tasksource/strategy-qa)          | 2,290                                      | 1,000              |
| Multiple-choice  | [ARC](https://huggingface.co/datasets/allenai/ai2_arc)                  | 3,548    | 1,000              |
| Multiple-choice  | [MMLU](https://huggingface.co/datasets/cais/mmlu)                 | 14,042                     | 1,000              |
| Long-form QA     | [ASQA](https://huggingface.co/datasets/din0s/asqa)                 | 948                                        | 948                |
| Fact-verification| [FEVER](https://fever.ai/dataset/fever.html)                | 13,332    | 1,000              |
| Dialogue         | [WoW](https://huggingface.co/datasets/facebook/kilt_tasks)                  | 3,054                                      | 1,000              |
| Slot-filling     | [T-REx](https://huggingface.co/datasets/facebook/kilt_tasks)                | 5,000                                      | 1,000              |

---

### 2. Supported Corpus

| Corpus Name | Document Count     |
|------------|--------------|
| [wiki-2018](https://huggingface.co/datasets/RUC-NLPIR/FlashRAG_datasets/tree/main/retrieval-corpus)   | 21,015,324   |
| wiki-2024   | Under preparation, coming soon |

---

### 3. Supported Baseline Methods (Continuously Updated)

| Baseline Name | Script     |
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

## Acknowledgments

Thanks to the following contributors for their code submissions and testing. We also welcome new members to join us in collectively building a comprehensive RAG ecosystem!

<a href="https://github.com/OpenBMB/UltraRAG/contributors">
  <img src="https://contrib.rocks/image?repo=OpenBMB/UltraRAG" />
</a>



## Trends

If you find this repository helpful for your research, please consider giving us a ⭐ to show your support.

<a href="https://star-history.com/#OpenBMB/UltraRAG&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=OpenBMB/UltraRAG&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=OpenBMB/UltraRAG&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=OpenBMB/UltraRAG&type=Date" />
 </picture>
</a>

## Contribution Guide

We welcome community contributions!  
- Submit bugs or feature requests via [GitHub Issues](https://github.com/OpenBMB/UltraRAG/issues)  
- Submit code: please discuss in Issues first, then submit via Pull Request  

## Contact Us

- For technical questions and feature requests, please use the [GitHub Issues](https://github.com/OpenBMB/UltraRAG/issues) feature.