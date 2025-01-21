

# WebUI介绍与使用说明

WebUI 采用  **两段式布局** ，页面上方为  **全局设置（Global Settings）** ，下方为  **各阶段流程配置** 。全局设置包括 **模型管理** 和 **知识管理** 两个分页，而流程配置涵盖 **数据构造、训练、评测** 及 **推理** 等环节。

在使用 WebUI 时，通常需按照以下步骤操作：

1. 在 **模型管理** 页面选择并加载相应模型；
2. 切换至 **知识管理** 页面，上传文档并完成知识库构建；
3. 进入 **Chat/Inference** 页面，选择合适的工作流进行对话。

下面将分别介绍 WebUI 各个环节的具体使用方法。

![](https://modelbest.feishu.cn/space/api/box/stream/download/asynccode/?code=NzNlOWM2MzBkYjNkNzdmNGY3NDQ0NWZjNzdlZjIxYzFfNkZjd2JSdnQwRmhzcllFaHFXeE92TVhpMVpORm9PYmhfVG9rZW46T1A5MmJDbDdFb0R4UjB4ZFVGNGNtYXV0bkpmXzE3Mzc0NDUwNzg6MTczNzQ0ODY3OF9WNA)

## 模型管理

模型管理涵盖 **LLM、Embedding** 和 **Reranker** 三类模型，当前支持 **本地加载** 与 **API 加载** 两种方式。未来将进一步扩展支持更多模型，并提供  **一键启动微服务** ，以优化模型管理流程。

用户可从  **ModelScope** 、**Hugging Face** 等模型仓库下载所需模型，灵活部署并满足不同应用场景的需求。

## 推理支持模型

| 模型类型  | 本地模型               | 微服务                              |
| --------- | ---------------------- | ----------------------------------- |
| LLM       | VLLM 支持的模型        | MiniCPM-V、以及其他 VLLM 支持的模型 |
| embedding | bge、minicpm-embedding | bge、minicpm-embedding              |
| reranker  | bge-large-reranker     |                                     |

## 知识库管理

知识库管理由 **文件管理** 和 **知识库管理** 两部分组成，目前支持的文件类型包括 **PDF** 和  **TXT** 。使用流程如下：

1. **上传文件** ：用户需先上传文件，并加载相应的 Embedding 模型；
2. **文件选择** ：选择所需文件后，配置知识库的基础参数；
3. **知识库构建** ：完成参数配置后，即可构建知识库。其中，**模型名称** 是判断知识库是否可混用的唯一标识，需由用户自定义。

注意：文件管理与知识库管理均由各自的 **CSV 表格** 进行维护，记录相关的基础信息。

构建完成的知识库将包含以下三个部分，供下游算法使用：

* **Index** （用于检索 top_k 结果）；
* **Org_Files** （原始文件）；
* **Chunk_Files** （切片后的文件）。

##### 图示：

![](https://modelbest.feishu.cn/space/api/box/stream/download/asynccode/?code=NTI4MmYxMmIzZmYwNWE1ODBmZTVhMDE4Mzk0NTdiZmJfWDA0WUVTYllrR0Zjc09nQlQ3UDV3dFpxVWo0R3RuQ25fVG9rZW46VXI4WmJVcGRob1BiWHB4cERjamM4eHJsbnFnXzE3Mzc0NDUwNzg6MTczNzQ0ODY3OF9WNA)

## 数据构造

在 **数据构造** 页面，我们提供了各类算法的数据构造方法，目前主要支持 **训练、评测** 等下游任务，未来将进一步扩展功能，如支持知识库数据的自动构建。

##### 图示：

![](https://modelbest.feishu.cn/space/api/box/stream/download/asynccode/?code=OGZjYjdlYTAwN2VjNGQ1OGI3OWI4NWY1MzVmZGNlODdfMnhFUmNMS3FIUHZxdUlVZ2dRR3JNT1phUnVPOW1GdGZfVG9rZW46Q0l2NWJHd3IzbzZkdEF4NHZUamN5dnllbjhjXzE3Mzc0NDUwNzg6MTczNzQ0ODY3OF9WNA)

## 训练

训练页面主要支持 **LLM** 和 **Embedding** 模型的训练，界面仅开放部分核心参数配置。LLM 训练采用 **LoRA** 方法为主，用户可通过配置 **YAML** 文件灵活传入具体参数。

**主要功能包括：**

* **数据集预览** （resource/dataset/train_dataset）；
* **SFT/DPO 训练** ，满足多种微调需求；
* **Embedding 模型训练** ，实现高效向量表示；
* **其他训练算法支持** （如 UltraRAG-KBAlign）；
* **LoRA 参数合并** ，提升模型训练的灵活性。

##### 图示：

![](https://modelbest.feishu.cn/space/api/box/stream/download/asynccode/?code=NTlkMDMzN2ZmN2JhNzYwNjcyN2Q3MTdkYWFhNmFmZWRfVU4yOXJpZlhCeWkwRWNHZWlad0JKM0NOVHhWcDJKY0hfVG9rZW46TDNQcmJhRjcxb1AwMTN4NE1meGNQVjF1bjBmXzE3Mzc0NDUwNzg6MTczNzQ0ODY3OF9WNA)

## 评测

评测页面支持对处理后的多个数据集进行一键评测，涵盖 **检索** 和 **生成** 两大模块。此外，用户还可对已生成的结果文件直接计算各项指标分数，前提是文件格式符合规范。

**主要功能包括：**

* **数据集预览** （resource/dataset/test_dataset），便于检查数据完整性；
* **检索指标评测** ，衡量模型的检索精度与召回性能；
* **生成指标评测** ，评估生成文本的质量和一致性；
* **检索+推理+评测** ，支持基于 **API** 和 **vLLM** 的一体化流程；
* **直接评测** ，适用于已生成且符合规范的结果文件，快速获取评测结果。

##### 图示：

![](https://modelbest.feishu.cn/space/api/box/stream/download/asynccode/?code=YzFhMTgzZGE1NDk4NTljYWY5YjEwMmVkOThlNTM2MmNfYjJYTHZZNm42N3BlWVRZUjlXbFgwWWM3VkZUMkJaMjRfVG9rZW46Ujc0RmJTaDlBb052ZjZ4OW56RWNWMnEwbmJmXzE3Mzc0NDUwNzg6MTczNzQ0ODY3OF9WNA)

## 聊天/推理

聊天页面支持多种工作流，包括  **Vanilla RAG** 、 **UltraRAG-VisRAG** 、**UltraRAG-KBAlign** 和  **UltraRAG-Adaptive-Note** ，未来将持续扩展更多工作流，进一步提升系统的灵活性与适用性。使用聊天功能前，用户需先完成以下步骤：

1. 选择合适的模型并构建知识库；
2. 在完成上述环节后，选择对应的工作流和知识库，即可启动对话流程。

##### 基本使用 **基本使用.mov**

**使用 WebUI 与 VanillaRAG 进行对话，需按以下步骤操作：**

1. **模型配置：** 在 **模型配置栏** ，选择默认的模型路径，依次加载 **大模型、Embedding 模型** 和  **Rerank 模型** 。
2. **知识配置**
   1. 在 **知识配置栏** ，上传文件（以 PDF 为例）；
   2. 选择已上传的文件，并使用默认参数构建知识库。
3. **对话体验：** 在 **体验栏** ，选择  **Chat/Inference** ，勾选知识库和工作流，即可在对话窗口中开始交互。

如需详细操作说明，请参考演示视频。

##### VisRAG **visrag.mov**

**使用 WebUI 与 VisRAG 进行对话，需按以下步骤操作：**

1. **加载 LLM 模型：** 在 **模型配置栏** ，输入 **MiniCPM-V** 模型路径，选择  **显卡** ，然后点击 **加载** ，完成 LLM 的加载。
2. **加载 Embedding 模型：** 在 **模型配置栏** ，输入 **VisRAG-Ret** 模型路径，选择  **显卡** ，然后点击 **加载** ，完成 Embedding 模型的加载。
3. **知识库构建**
4. 在 **知识配置栏** ，上传文件（以 PDF 为例），或勾选已上传文件；
5. 选择已上传的文件，并使用默认参数构建知识库。
6. **对话体验：** 在 **体验栏** ，选择  **Chat/Inference** ，勾选知识库和工作流，即可在窗口中进行对话。

如需详细操作说明，请参考演示视频。

##### VisRAG/Adaptive-Note评测**评测.mov**

参考演示视频，评测操作需按照以下步骤进行：

1. **选择工作流：** 选中需要测试的工作流。
2. **选择知识库：** 选择测试所需的知识库。
3. **配置评测参数：** 勾选评测集和评测指标；指定结果的输出路径。
4. **运行命令：** 点击  **预览命令** ，获取对应的运行命令；点击  **执行命令** ，在前端执行评测，并在下方窗口实时预览执行结果。

**建议：** 由于评测时间较长，前端关闭可能导致命令执行中断，推荐将获取的命令复制后在服务器本地运行，以确保评测过程的稳定性和完整性。

![](https://modelbest.feishu.cn/space/api/box/stream/download/asynccode/?code=NjBmNzNhOTA4MWIyZDE5ZGQyOWVhYTdjYTk5NzUwZjFfRDlQMWJsUkJhSkhMSGFldVg5b3FDbjhrZm9INWNaTTNfVG9rZW46UDlqR2JOQ0ljb0NpZ3V4b3FrN2NsaURMbkdSXzE3Mzc0NDUwNzg6MTczNzQ0ODY3OF9WNA)
