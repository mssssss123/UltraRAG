# 将R1融入多轮RAG --- UltraRAG+R1本地化部署教程

最近，深度求索开源的DeepSeek R1 系列的模型火遍全球，但是因为“服务器繁忙”问题劝退不少人。这里我将使用 UltraARG 框架为例，给大家介绍下 DeepSeek R1的本地部署流程，并带着搭建熟悉了解下UltrRAG 细节和功能。在成功跑通 VanillaRAG 后，我还简单尝试了DeepSeek R1加持下的 Adaptive-Note，在法律场景下简单提问了几个问题，效果居然出乎意料的好，不吹不黑，截图为证。

![](../assets/zh/vrag.png)

![](../assets/zh/adaptive-note.png)

以截图为例，我在 UltraRAG 上对 [VanillaRAG]() 和 [Adaptive-Note]()分别提问“我喝多后撞了人可能会承担什么罪责？”，VanillaRAG 简单直接，分别列出了罪名和建议，看起来似乎可以，但是确不够细致；再来看下Adaptive-Note，不光是总结了可能的几点罪名，并且分析了酒精含量和事后的处理态度对量刑和赔偿的影响，引经据典，有理有据。整体上来看，似乎是Adaptive-Note更好一些。

> VanillaRAG：是最基础的 RAG（Retrieval-Augmented Generation，检索增强生成）架构，通常指的是 **未经优化或改进的标准 RAG 方法** 。它的基本流程如下： **查询构造（** **Query**** Formation）、检索（Retrieval）、生成（Generation）**
>
> Adaptive-Note:  一种用于复杂问答任务的  **自适应笔记增强 RAG 方法** ，采用 **检索-记忆（Retriever-and-Memory）** 机制， iteratively 收集和优化知识结构。它通过 **自适应记忆复审** 和 **任务导向生成** 提高知识交互质量，并采用 **基于笔记的探索终止策略** 确保信息充分获取，最终提升答案质量。论文:https://arxiv.org/abs/2410.08821.

看到这里，我想大家已经开始想要体验下这个 UltraRAG 了，接下来我们详细介绍下 UltraRAG 的部署流程。

## 硬件环境准备

DeepSeek R1 的模型有多个蒸馏版本，分别是 7B、14B、70B 以及满血的 671B 版本。权衡下条件和效果，我们选择 14B 版本的模型进行部署，而以下是运行 UltraRAG 的基本硬件要求：

| **参数** | **值**                    |
| -------------- | ------------------------------- |
| 显卡           | A100-80GB(或者其他 80GB 的显卡) |
| cuda           | ≥ 12.4                         |
| 系统           | ubuntu 22.04 (非必需)           |
| 磁盘空间       | ≥ 50GB                         |

这里需要注意nvidia 的显卡驱动要和 cuda 版本兼容，否则vllm 运行模型有可能出现报错的情况。如果你的显卡出现不兼容的情况，请可以尝试下重装驱动和 cuda，这里推荐一个简单好用的安装方法，可以有效避免 cuda 和驱动的不兼容问题，你只需要登录[nvidia 官方网站](https://developer.nvidia.com/cuda-toolkit-archive)，然后选择适合的版本 cuda-toolkit 版本安装即可，注意选择适合你的安装参数（推荐使用 runfile 方式安装，因为它真的简单好用）：

![](../assets/zh/nvidia.png)

## UltraRAG配置

好了，现在你已经拥有了一个稳定的运行环境，现在可以配置 UltraRAG 了。你需要从仓库中下载并放到合适的位置，[https://github.com/OpenBMB/UltraRAG](https://github.com/OpenBMB/UltraRAG) （记得点个 star～），接下来我们来配置 UltraRAG 所需要的 python 库依赖。

现在我们有两种办法运行 UltraRAG，一种是通过 docker 运行，这种方式是最简单的，前提是你的机器上已经安装配置好了nvidia-docker，并拥有它的运行的权限（一般情况下需要 root 权限）。这种情况下，你只需要执行这行代码就行了：

```Bash
docker-compose up --build -d
```

但是呢，如果你的机器上没有nvidia-docker，也不要紧，我们也可以配置 conda 环境来运行。

首先你要确保本地机器安装了 conda，如果没有的话也不要紧，可以在这个[网址](https://docs.anaconda.com/miniconda/install/)中找到安装的方法，使用普通账户直接安装就完了，几行代码很好执行～

![](../assets/zh/conda.png)

接着，就是在 conda 环境上安装 UltraRAG 的依赖，下面的代码依次执行就好了～

```Bash
创建conda环境
conda create -n ultrarag python=3.10
#激活conda环境
conda activate ultrarag
安装相关依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

以上步骤操作完之后，环境依赖就准备好了，但是我们还没完成呢，因为接下来是下载模型。

关于模型下载，这里我们需要下载以下3 个模型，分别执行以下命令即可，

| **模型**               | **功能** | **下载命令**                                                                                                             |
| ---------------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| DeepSeek-R1-Distill-Qwen-14B | LLM            | modelscope download --model deepseek-ai/DeepSeek-R1-Distill-Qwen-14B --local_dir ./resource/model/DeepSeek-R1-Distill-Qwen-14B |
| MiniCPM-Embedding-Light      | embedding      | modelscope download --model OpenBMB/MiniCPM-Embedding-Light --local_dir ./resource/model/MiniCPM-Embedding-Light               |
| MiniCPM-Reranker-Light       | reranker       | modelscope download --model OpenBMB/MiniCPM-Reranker-Light --local_dir ./resource/model/MiniCPM-Reranker-Light                 |

 模型下载完成之后，我们来运行 llm 的服务，具体地，执行这个命令即可～

```Bash
vllm serve DeepSeek-R1-Distill-Qwen-14B --gpu-memory-utilization 0.8 --dtype auto --api-key token-abc123
```

这里简单说明下参数的含义：

* --gpu-memory-utilization 0.8：表示 GPU 的占用率，显存 80G 的话，0.8 意味着最大占用 64GB 的显存
* --dtype auto：表示vllm 自动选择模型参数类型
* --api-key token-abc123：自定义模型 API 的密钥为token-abc123

vllm 服务部署完成后将会启动 OpenAI-Compatibly 的服务，默认参数为：

| base_url | http://localhost:8000/v1     |
| -------- | ---------------------------- |
| model    | DeepSeek-R1-Distill-Qwen-14B |
| api-key  | token-abc123                 |

为了常驻后台，你也可以使用以下命令运行：

```Bash
nohup  vllm serve DeepSeek-R1-Distill-Qwen-14B --gpu-memory-utilization 0.8 --dtype auto --api-key token-abc123 &
```

好了，现在环境搭好了，模型也下载好了，我们现在来运行UltraRAG：

```Bash
streamlit run ultrarag/webui/webui.py --server.fileWatcherType none
```

一切顺利的话，我们会看到以下结果，这意味着WebUI 已经跑起来了，我们把 URL复制到浏览器，应该就能访问页面了，这里它提供了3 个 URL，你可以使用任何一个来访问：

![](https://mmbiz.qpic.cn/mmbiz_jpg/y4aUF5lic8SRNHOxlxO5UkiaCuSoDzLmRicLMicleIGibqicJkibkk6fDFyNHuO87ibnIkHmNWqJu3nlNwb6mNLia9ibb2jQ/640?wx_fmt=jpeg&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1)

## 和 DeepSeek R1 对话
这里附上超详细视频教程，可以对照细节一步步上手：


[![链接详情中的视频](https://i1.hdslb.com/bfs/archive/78dcd00013b817c45cad33e114d1ac3508c2bd8f.jpg@672w_378h_1c.webp)](https://www.bilibili.com/video/BV1vRAbezEcu/?share_source=copy_web)