<div align="center">
    <img src="docs/assets/logo.png" alt="UltraRAG Logo" width="450">
</div>

## 什么是 UltraRAG

UltraRAG 是一个针对miniCPM 系列模型开发的的RAG 框架，用于快速部署、评估和演示RAG 效果。UltraRAG 使用模块化的框架结构，既可以在端侧部署，也可以通过微服务的方式进行分布式部署。

**主要特点：**

- 自动化构造训练数据：UltraRAG 将自动从用户输入的文档中构造出训练数据
- 自动微调训练模型：UltraRAG提供一键式的embedding / 生成模型的训练，帮助用户快速训练出符合需求的模型
- 基于RAGeval的效果评测：UltraRAG集成了模块化的评测算法，能够评估模型以及端到端的链路效果
- 简单的 webui：UltraRAG 提供一个简单的 webui，用于演示生成的 rag
- 支持UltraRAG-Adaptive-Note模块

## 快速开始

### 安装使用

UltraRAG支持在单机部署简单的演示demo，你可以通过导入python依赖的方式在本地部署简单的UI对话示例。你可以通过以下三种方式使用 UltraRAG 框架：

#### 1. docker部署

运行以下命令，然后在浏览器访问“http://localhost:8843",

```
docker-compose up --build -d
```

#### 2. conda部署

```
# 创建conda环境
conda create -n ultrarag python=3.10

# 激活conda环境
conda activate ultrarag

# 安装相关依赖
pip install -r requirements.txt

# 运行微服务
bash ./scripts/run_server.sh

# 运行demo页面
streamlit run ultrarag/webui/webui.py --server.fileWatcherType none
```

#### 3. setup.py安装

cd UltraRAG，然后运行以下命令

```
# 安装UltraRAG
pip install -e .

# 运行demo页面
streamlit run ultrarag/webui/webui.py --server.fileWatcherType none
```

### 模型下载

运行以下脚本，下载模型，默认下载到/resources/models目录下，下载的模型列表在config/models_download_list.yaml中

```
python ./scripts/download_models.py
```

## 贡献者名单

<a href="https://github.com/gdw439/UltraRAG/contributors">
  <img src="https://contrib.rocks/image?repo=gdw439/UltraRAG" />
</a>


## Star History

<a href="https://star-history.com/#gdw439/UltraRAG&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=gdw439/UltraRAG&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=gdw439/UltraRAG&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=gdw439/UltraRAG&type=Date" />
 </picture>
</a>
