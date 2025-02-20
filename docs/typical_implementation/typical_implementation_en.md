## Typical Implementation

### General methods

#### Vanilla RAG

##### Method Overview

UltraRAG has introduced an **intent recognition feature** in this module. For questions that do not require retrieval, a response can be generated directly, thereby improving response efficiency. For questions that require retrieval, the system will perform a single retrieval and re-ranking, then generate an accurate response based on the retrieved content.

##### Diagram:

Recall includes retrieved content. If intent recognition determines that retrieval is not needed, a response is generated directly.

![](../assets/en/implement_1.png)

#### DPO & SFT

##### Training:

###### **Method Overview:**

Direct Preference Optimization (DPO) and Supervised Fine-Tuning (SFT) are two core techniques for enhancing the performance and alignment capabilities of large language models (LLM). Each from the perspective of **preference optimization** and **supervised learning**, these methods provide different solutions for complex tasks and play complementary roles in building high-quality generative models.

The core idea of **DPO** is directly using preference data to optimize the model, making its output more aligned with the actual needs of users. This method structures preference pairs using user feedback and formalizes the generative task as a process of optimizing preference distribution. Unlike reward modeling based on reinforcement learning (e.g., RLHF), DPO directly optimizes the preference function to adjust model behavior, avoiding the complexities of strategy optimization and significantly improving the alignment and user satisfaction of generative results.

**SFT** employs a classical supervised learning paradigm, fine-tuning the model using high-quality input-output pairs (such as task-labeled data) with the aim of accurately learning the mapping relationship of specific tasks to provide strong initial performance. The SFT training process typically relies on large-scale annotated data and improves generation quality by minimizing training error. However, due to its reliance on labeled data, its generalization ability in handling diverse scenarios is relatively limited.

We provide DPO and SFT fine-tuning training schemes based on the trl library. Users can convert their data into the corresponding format and then proceed with the training process as needed.

###### **Parameters:**

| Parameter Name            | Required | Type       | Description                                                    | Example/Default Value                              |
| ------------------------- | -------- | ---------- | -------------------------------------------------------------- | -------------------------------------------------- |
| pipeline_type             | Yes      | str        | Specify method                                                 | DPO (choices: DPO, SFT)                             |
| task_type                 | Yes      | str        | Specify task type                                              | DPO (choices: DPO, SFT)                             |
| use_lora                  | No       | bool(flag) | Specify whether to use lora fine-tuning during training        | -                                                  |
| model_name_or_path        | Yes      | str        | Path to the model for training                                 | your_training_model_path                           |
| train_data_path           | Yes      | str        | Path to the training dataset **(Note: If providing an external dataset, place the data under ~/resource/dataset/train_dataset/ for selection)** | ~/resource/dataset/train_dataset/dpos_train.jsonl  |
| eval_data_path            | Yes      | str        | Path to the validation dataset **(Note: If providing an external validation dataset, place the data under ~/resource/dataset/train_dataset/ for selection)** | ~/resource/dataset/train_dataset/dpos_dev.jsonl    |
| output_dir                | Yes      | str        | Path to save the trained model                                 | ~/output/ddr                                       |
| logging_dir               | Yes      | str        | Path to save training logs                                     | ~/output/logs/ddr                                  |
| deepspeed_config_file     | Yes      | str        | Path to the deepspeed settings file                            | ~/config/ds_config_zero2.json                      |
| config_file               | Yes      | str        | YAML configuration file path                                   | ~/config/pipeline/finetune.yaml                    |
| log_file                  | Yes      | str        | Path to save training logs                                     | ~/output/logs/ddr/finetune_run.log                 |

To simplify user operation experience, only necessary parameters are provided by the system. Some parameters are preset in the **YAML** configuration file. Users can directly use the default values or personalize them according to specific needs. Training parameters are implemented based on the transformers.TrainingArguments class, offering high flexibility and allowing users to customize and extend according to actual requirements to suit various training scenarios.

| Parameter Name            | Required | Type       | Description                                                    | Example/Default Value                              |
| ------------------------- | -------- | ---------- | -------------------------------------------------------------- | -------------------------------------------------- |
| Augment_template          | Yes      | str        | Data augmentation template                                     | Background{}Question:{}Answer:                     |
| QA_template               | Yes      | str        | Question-answering template                                    | Question:{}Answer:                                 |
| passage_separator         | Yes      | str        | Separator between different documents                          |                                                    |
| model_type                | Yes      | str        | Specify the model type                                         | minicpm3 (choices: minicpm3, minicpm2, llama_style)|
| use_template              | Yes      | bool       | Specify whether to use a template in the model input stage     | True                                               |
| max_length                | Yes      | int        | **Only for DPO training**, maximum length of input sequence (including prompt and completion) | 2200                                               |
| max_prompt_length         | Yes      | int        | **Only for DPO training**, maximum length of prompt (should be less than max_length) | 2100                                               |
| max_seq_length            | Yes      | int        | **Only for SFT training**, maximum length of input sequence (including prompt and completion) | 2200                                               |
| max_passage_length        | Yes      | int        | Maximum length of retrieval document (should be less than max_prompt_length or max_seq_length) | 2000                                               |
| top_n                     | Yes      | int        | Number of documents to return during retrieval                  | 5                                                  |
| optim                     | Yes      | str        | Type of optimizer                                               | adamw_torch                                        |
| save_steps                | Yes      | int        | Interval steps for saving the model                             | 100                                                |
| eval_steps                | Yes      | int        | Interval steps for evaluation                                   | 100                                                |
| per_device_train_batch_size| Yes     | int        | Training batch size per device                                  | 1                                                  |
| per_device_eval_batch_size | Yes     | int        | Evaluation batch size per device                                | 2                                                  |
| learning_rate             | Yes      | float      | Learning rate                                                  | 5e-5                                               |
| eval_strategy             | Yes      | str        | Evaluation strategy                                            | steps                                              |
| logging_steps             | Yes      | int        | Interval steps for logging                                      | 10                                                 |
| bf16                      | Yes      | bool       | Whether to enable BF16 (half precision floating point)          | True                                               |
| num_train_epochs          | Yes      | int        | Total number of training epochs                                | 1                                                  |

######  **Diagram:**

![](../assets/en/implement_2.png)

###### **DPO Training Input Data Format: (only listing necessary fields for training data)**

```JSON
{"query": "xxx", "retrieval_result": ["xxx", "xxx", "xxx", "xxx", "xxx"], 
"chosen": {"text": "xxx"}, 
"rejected": {"text": "xxx"}}
```

###### **SFT Training Input Data Format: (only listing necessary fields for training data)**

```JSON
{"messages": [{"role": "system", "content": "You are helpful"}, {"role": "user", "content": "What's the capital of France?"}, {"role": "assistant", "content": "..."}]}
{"messages": [{"role": "system", "content": "You are helpful"}, {"role": "user", "content": "Who wrote 'Romeo and Juliet'?"}, {"role": "assistant", "content": "..."}]}
{"messages": [{"role": "system", "content": "You are helpful"}, {"role": "user", "content": "How far is the Moon from Earth?"}, {"role": "assistant", "content": "..."}]}
```

##### **LoRA Merging:**

If LoRA fine-tuning is used during training, the LoRA fine-tuned parameters need to be merged with the original model parameters after training to generate the complete model weights.


###### **Parameters:**

| Parameter Name      | Required | Type     | Description                        | Example/Default Value       |
| ------------------- | -------- | -------- | ---------------------------------- | --------------------------- |
| model_name_or_path  | Yes      | str      | Path to the trained model          | your_training_model_path    |
| lora_name_or_path   | Yes      | str      | Path to the LoRA fine-tuned parameters to be merged | your_lora_model_path      |
| save_path           | Yes      | str      | Path to save the merged model      | your_save_model_path        |


###### **Diagram:**

![](../assets/en/implement_3.png)

#### Eval

| Parameter Name       | Required | Type     | Description                         | Example/Default Value       |
| -------------------- | -------- | -------- | ----------------------------------- | --------------------------- |
| pipeline_type        | Yes      | str      | Specify the method                  | vanilla                     |
| embedding_model_path | No       | str      | Path to the embedding model         | your_embedding_model_path   |


##### Retrieval Eval

| Parameter Name              | Required | Type       | Description                               | Example/Default Value         |
| --------------------------- | -------- | ---------- | ----------------------------------------- | ----------------------------- |
| selected_retrieval_metrics  | No       | str (list) | List of retrieval metrics to evaluate    | []                            |
| pooling                     | No       | str        | Pooling strategy for text representation | Default: "mean"               |
| query_instruction           | No       | str        | Instructions for extracting query text   | Default: None                 |
| queries_path                | Yes      | str        | Path to the query file                   | Example: "path/to/queries.txt"|
| corpus_path                 | Yes      | str        | Path to the corpus file                  | Example: "path/to/corpus.txt" |
| qrels_path                  | Yes      | str        | Path to the qrels (query-relevance file) | Example: "path/to/qrels.txt"  |
| retrieval_output_path       | Yes      | str        | Path to save the retrieval output        | Example: "path/to/output.txt" |
| log_path                    | No       | str        | Path to save the log file                | Default: None                 |
| topk                        | No       | int        | The number of top-k documents to retrieve| Default: 10                   |
| cutoffs                     | No       | str        | Cutoff values for evaluation metrics     | Default: None                 |

###### Metrics Currently Supported:

MRR、NDCG、Recall

The last line of the output file will contain the average scores for all metrics.

###### Data Format:

Input Data:

Includes three files: `query.jsonl` (query data), `corpus.jsonl` (document data), and `qrels.tsv` (triplet file).

- Query data format (`query.jsonl`) and document data format (`corpus.jsonl`):

```JSON
 {"_id": "aaa", "text": "This is document 1"}
 {"_id": "aaa", "text": "This is query 1"}
```

- Triplet file format (`qrels.tsv`): (Note: tab-separated)

```Plain
query-id    corpus-id    score
aaa         bbb          1
```

Output Data:

`result.trec` (Note: tab-separated)

```Plain
 aaa    Q0    bbb    1    0.1    1

 Meaning of each field:
 <query_id> Q0 <doc_id> <rank> <score> <run_id>
``` 

##### Generated Eval

**The LLM model parameters need to be configured in UltraRAG/config/pipeline/eval/eval.yaml**

| Parameter Name             | Required | Parameter Type   | Description                                                    | Example/Default Value        |
| -------------------------- | -------- | ---------------- | -------------------------------------------------------------- | ---------------------------- |
| selected_generated_metrics | No       | str (list)       | List of generation metrics to evaluate                         | Default: []                  |
| test_dataset               | Yes      | str (list)       | List of dataset files (json or jsonl)                          | dataset1.json dataset2.jsonl |
| output_path                | Yes      | str              | Path to save results                                           | results/output.json          |
| knowledge_id               | No       | str (list)       | List of knowledge bases                                        | collection1 collection2      |
| knowledge_stat_tab_path    | No       | str              | Path to the knowledge management table                         | your_knowledge_stat_tab_path |
| evaluate_only              | No       | bool (flag)      | If set, skip generation and directly evaluate the dataset **(must meet the retrieval or generation evaluation input format)** | False                        |
| metric_api_key             | No       | str              | API key for the model used in metric evaluation                | your_api_key                 |
| metric_base_url            | No       | str              | Base URL for the model used in metric evaluation               | your_base_url                |
| metric_model_name          | No       | str              | Model name for the model used in metric evaluation             | your_model_name              |
| api_key                    | No       | str              | API key for the model being evaluated                          | your_api_key                 |
| base_url                   | No       | str              | Base URL for the model being evaluated                         | your_base_url                |
| model_name                 | No       | str              | Model name for the model being evaluated                       | your_model_name              |
| reranker_model_path        | No       | str              | Path to the reranker model                                     | your_reranker_model_path     |


###### Currently Supported Metrics:

Completeness（RAGEval）、Rouge、EM、Accuracy、F1、BLEU、Meteor、Bert

The last line of the output file will contain the average scores for all metrics respectively.

###### Data Format:

Input Data

Must include query and answer. If a system prompt that is not to be retrieved is needed, pass it in via instruction.

```JSON
{"id": 0, "query": "xxx？", "answer": "xxx", "prediction": "xxxyyy", "instruction":"this is optional key"}
{"id": 0, "query": "aaa？", "answer": "bbb", "prediction": "bbb"}
```

Output Data

```JSON
{"id": 0, "query": "xxx？", "answer": "xxx", "prediction": "xxxyyy", "xxx_score": 20.12, "xxx_score": 20.26}
{"id": 0, "query": "aaa？", "answer": "bbb", "prediction": "bbb", "x_score": 100.00, "xx_score": 100.00}
{"average_scores": {"x": 60.06, "xx": 60.13}
```

### UltraRAG-Series

#### UltraRAG-Adaptive-Note


##### Source, Methods, and Results:

 **Paper URL:** [Retriever-and-Memory: Towards Adaptive Note-Enhanced Retrieval-Augmented Generation](https://arxiv.org/abs/2410.08821)

 **GitHub URL:**[UltraRAG-Adaptive-Note](https://github.com/thunlp/Adaptive-Note)**

![](../assets/en/implement_4.png)

##### Method Overview:


To address the challenges of **lack of information** and **poor interactivity** faced by current Retrieval-Augmented Generation (RAG) systems in complex questioning tasks, we propose a novel end-to-end approach called **UltraRAG-Adaptive-Note**. This method consists of three core modules:

1. **Iterative Information Collector (IIC)**
   
   IIC uses notes as a knowledge carrier to systematically integrate and dynamically update retrieved information. Initially, Large Language Models (LLMs) generate initial notes from retrieved references and store them as optimal memory. During iterations, based on existing optimal memory, IIC predicts new retrieval queries and continuously updates the notes to achieve dynamic knowledge expansion.

2. **Adaptive Memory Reviewer (AMR)**
   
   AMR dynamically evaluates the quality of updated notes and optimal memory content, deciding whether to replace existing notes. Additionally, AMR implements a note-based exploration stop strategy to prevent excessive searches. This strategy ensures timely termination of information collection when information gain becomes insignificant, enhancing system efficiency.

3. **Task-Oriented Generator**

   This module extracts key information from optimal memory to generate high-quality answers and supports various question-answering formats, ensuring answer specificity and accuracy.

   Through the synergistic effect of the above modules, **UltraRAG-Adaptive-Note** achieves efficient solutions to complex problems from a knowledge growth perspective, demonstrating significant performance advantages in **multi-hop Q&A** and **long-text generation** tasks.

#### UltraRAG-KBAlign

##### Source, Methods, and Results:

 **Paper URL:** [KBAlign: Efficient Self Adaptation on Specific Knowledge Bases](https://arxiv.org/abs/2411.14790)

 **GitHub URL:** [KBAlign GitHub](https://github.com/thunlp/KBAlign?tab=readme-ov-file)

![](../assets/en/implement_6.png)

##### Method Overview:

**UltraRAG-KBAlign** aims to enhance large language models' (LLMs) ability to adapt knowledge efficiently when handling tasks involving knowledge bases. Unlike traditional methods that rely on external signals (such as human preference data or annotations from more powerful LLMs), **KBAlign** employs **self-supervised learning** to achieve knowledge adaptation efficiently and cost-effectively. The method mainly includes three key components:

**Self-Annotated Training Data Combining Long and Short Dependencies**

  By combining long and short dependencies, it automatically generates high-quality training data to improve the model's understanding and adaptability to information in knowledge bases.

**Self-Verification and Iterative Training**

  It employs a self-verification mechanism to continuously optimize the model during iterative training, enabling it to gradually improve knowledge alignment in an unsupervised environment.

**Inference Optimization**

  During the inference stage, it optimizes the generation process using aligned knowledge representations to ensure the accuracy and consistency of the answers.

##### Data Construction:

**UltraRAG-KBAlign** uses a **self-annotation method combining long and short dependencies** to construct training data, enhancing the model's ability to adapt knowledge.

- **Short Dependency Annotation** focuses only on the local information of a single **chunk**, ensuring the model's precise understanding of fine-grained knowledge.
- **Long Dependency Annotation** is divided into **homogeneous data** and **heterogeneous data** to build richer Q&A pairs:
  - **Homogeneous data** creates ambiguous questions by integrating multiple related paragraphs to obtain the final answer;
  - **Heterogeneous data** uses methods like clustering to extract more global Q&A pairs from different sections, enhancing the model's cross-sectional inference ability.

###### Parameters:

| Parameter Name          | Required | Parameter Type | Description                                        | Example/Default Value       |
| ----------------------- | -------- | -------------- | -------------------------------------------------- | --------------------------- |
| model_name_or_path      | Yes      | str            | Path to the model to be fine-tuned                 |                             |
| config_path             | Yes      | str            | Path to the YAML configuration file                |                             |
| embedding_model_path    | Yes      | str            | Path to the embedding model                        |                             |
| knowledge_id            | Yes      | str            | ID of the knowledge set in Qdrant                  |                             |
| knowledge_stat_tab_path | Yes      | str            | Path to the knowledge statistics table             |                             |
| clustering              | No       | store_true     | Whether data needs clustering (heterogeneous data) | False                       |
| output_dir              | Yes      | str            | Path to the output directory                       |                             |
| language                | Yes      | str            | Language type (Chinese/English)                    | Chinese or English          |
| functions_to_run        | Yes      | str            | Name of functions to execute (e.g., function_q or function_qr) | function_q function_qr      |
| file_list               | Yes      | list           | List of JSON or JSONL files to be merged           |                             |
| ratios                  | Yes      | list           | Ratio for each file, such as 1:1                   | [1, 1]                      |
| fixed_steps             | No       | int            | Fixed number of merge steps                        | Default is None, a user-provided integer |
| random_merge            | No       | store_true     | Whether to randomly shuffle data before merging    | Default is False            |
| output_file             | Yes      | str            | Path to the merged output file                     |                             |
| output_format           | Yes      | str            | Output format (json or jsonl)                      | json or jsonl               |

##### Training (In Progress):

UltraRAG-KBAlign uses **iterative self-verification** for training, requiring configuration of fixed data volume, iteration counts, and other key parameters. During each training round, the model answers a portion of the data and self-verifies based on the generated answers. Verification results are incorporated into the next round of training data, promoting continuous optimization and gradual improvement in performance and verification ability.

###### Inference Optimization:

During the inference phase, UltraRAG-KBAlign enhances performance through methods such as **Query Expansion** and **Confidence Check**. Training with the KBAlign method enhances the model's mastery of knowledge bases and self-verification capabilities, enabling further optimization in the accuracy of expanded query retrieval and confidence assessment.


#### UltraRAG-DDR

 **Paper URL:** [RAG-DDR: OPTIMIZING RETRIEVAL-AUGMENTED GENERATION USING DIFFERENTIABLE DATA REWARDS](https://arxiv.org/pdf/2410.13509)

 **Project URL:** [RAG-DDR](https://github.com/OpenMatch/RAG-DDR)

![](../assets/en/implement_7.png)

##### **Method Overview**

Existing RAG systems face two major challenges: first, the retrieved documents may contain a large amount of noisy information; second, the retrieved external knowledge may conflict with the inherent knowledge in the model parameters. These issues significantly affect the accuracy and reliability of large language models (LLMs) during the generation process. To enhance the retrieval-augmented capabilities of LLMs, a common approach is to conduct supervised fine-tuning based on knowledge-intensive tasks. However, due to a heavy reliance on labeled data during training, these models often have limited generalization capabilities and struggle to adapt to complex and diverse real-world application scenarios.

To address the above issues, we propose an end-to-end optimization scheme for RAG systems—**UltraRAG-DDR**. This method utilizes **rollout techniques** to systematically evaluate the reward scores of the RAG module, and optimizes the model to better align with data preferences. By targeted data sampling for specific task scenarios, preference data pairs that meet the **Direct Preference Optimization (DPO)** method requirements are generated, and efficient training based on DPO is conducted, significantly enhancing the system's performance in specific tasks.

In **UltraRAG-DDR**, we use preprocessed document information from the knowledge base to construct triplet data containing **Query, Ground-truth, and Keypoints** using a high-performance model, and generate a **Reference** via a retrieval model, thus creating a standardized raw dataset. Additionally, the **DDR data sampling strategy** is employed to enable the model to generate diverse responses for each query in both inherent and external knowledge scenarios by adjusting temperature parameters and using a repetitive sampling mechanism. Supervised labels are utilized to naturally obtain reward scores for each response, with the highest-scoring response selected as a positive example and the lowest as a negative example, thereby constructing high-quality preference training data pairs.

This data construction strategy not only significantly improves the model's adaptability and generation quality across different knowledge scenarios, but also achieves highly integrated one-click data construction functionality. Users simply need to upload documents and select a target model to automatically complete the entire process of generating training data, with support for various training methods like **DPO** and **SFT**. This scheme significantly lowers operational barriers and data construction costs, providing a more efficient and convenient solution for RAG research and practice.


##### **Parameters:**

| Parameter Name           | Required | Type     | Description                                       | Example/Default Value                              |
| ------------------------ | -------- | -------- | ------------------------------------------------- | ------------------------------------------------- |
| pipeline_type            | Yes      | str      | Specify the method                                | ddr                                               |
| Train Model Name or Path | Yes      | str      | Path to the model for training                    | your_training_model_path                          |
| Data Model Name or Path  | Yes      | str      | Path to the model for data construction (stronger performance than training model) | your_data_constructing_model_path                 |
| Embedding Model Path     | Yes      | str      | Path to the embedding model                       | your_embedding_model_path                         |
| Config Path              | Yes      | str      | Path to the yaml configuration file               | ~/config/pipeline/ddr/datasets.yaml               |
| Train Output Path        | Yes      | str      | Output path for the training set                  | ~/resource/dataset/train_dataset/dpos_train.jsonl |
| Dev Output Path          | Yes      | str      | Output path for the validation set                | ~/resource/dataset/train_dataset/dpos_dev.jsonl   |
| current_kb_config_id     | Yes      | str      | Knowledge base configuration ID (automatically inputted after knowledge base configuration) | your_current_kb_config_id                         |
| knowledge_id             | Yes      | str      | Knowledge base ID (automatically inputted after knowledge base configuration) | your_knowledge_id                                 |
| knowledge_stat_tab_path  | Yes      | str      | Path to the knowledge base management table (automatically inputted after knowledge base configuration) | your_knowledge_stat_tab_path                      |

To simplify the user operation experience, we have only listed the necessary parameters. Some optimization parameters have been preset in the YAML configuration file, and users can directly use the default values or adjust them according to special requirements:

| Parameter Name      | Required | Parameter Type | Description                                                   | Example/Default Value                                 |
| ------------------- | -------- | -------------- | ------------------------------------------------------------- | ----------------------------------------------------- |
| VllmServer_params   | Yes      | -              | VLLM service configuration                                    | -                                                     |
| sampling_params     | Yes      | -              | Generation control parameters (to construct data model)       | -                                                     |
| max_data_nums       | Yes      | int            | Maximum number of constructed data                            | 5000                                                  |
| top_k               | Yes      | int            | Number of documents returned during retrieval                 | 5                                                     |
| method              | Yes      | str            | Retrieval method, e.g., "dense" indicates using dense retrieval | dense                                                 |
| Augment_template    | Yes      | str            | Data augmentation template                                    | Background{}Question:{}Answer:                        |
| QA_template         | Yes      | str            | Q&A template                                                  | Question:{}Answer:                                    |
| max_prompt_length   | Yes      | int            | Maximum length of the prompt                                  | 4096                                                  |
| max_passage_length  | Yes      | int            | Maximum length of the retrieved document (should be less than max_prompt_length) | 2000                                                  |
| passage_separator   | Yes      | str            | Separator between different documents                         |                                                       |
| model_type          | Yes      | str            | Specify the type of model                                     | minicpm3 (options: minicpm3, minicpm2, llama_style)  |
| use_template        | Yes      | bool           | Specify whether to use a template during the model input stage| True                                                  |
| batch_size          | Yes      | int            | Batch size during data processing                             | 64                                                    |
| dpo_sampling_params | Yes      | -              | DPO uses generation control parameters (model to be trained)  | -                                                     |
| metric              | Yes      | str            | Sampling evaluation metric                                    | rouge (options: rouge, em, accuracy, f1)              |
| ratio               | Yes      | float          | Division ratio of training and test data, e.g., "0.1" means 10% of the data is used for testing. | 0.1                                                   |


##### **Diagram:**

![](../assets/en/implement_8.png)

##### **Output Data Format**

```JSON
{"file_index": 1, "chunk_index": 1, "chunk": "xxx","query": "xxx", "ground_truth": "xxx", "keypoints": "1. xxx\n2. xxx" , "retrieval_result": ["xxx", "xxx", "xxx", "xxx", "xxx"], "id": 1, "raw_input": "xxx", "augment_input": "xxx",
"context": [
{"text": "xxx", "temperature": 0.5, "type": "raw", "x_score": 0.85}, 
{"text": "xxx", "temperature": 0.5, "type": "aug", "x_score": 0.62}, 
{"text": "xxx", "temperature": 0.6, "type": "raw", "x_score": 0.59}, 
{"text": "xxx", "temperature": 0.6, "type": "aug", "x_score": 0.43, 
{"text": "xxx", "temperature": 0.7, "type": "raw", "x_score": 0.58}, 
{"text": "xxx", "temperature": 0.7, "type": "aug", "x_score": 0.69}, 
{"text": "xxx", "temperature": 0.8, "type": "raw", "x_score": 0.25}, 
{"text": "xxx", "temperature": 0.8, "type": "aug", "x_score": 0.74}, 
{"text": "xxx", "temperature": 0.9, "type": "raw", "x_score": 0.55}, 
{"text": "xxx", "temperature": 0.9, "type": "aug", "x_score": 0.91}
], 
"chosen": {"text": "xxx", "temperature": 0.9, "type": "aug", "x_score": 0.91}, 
"rejected": {"text": "xxx", "temperature": 0.8, "type": "raw", "x_score": 0.25}}
```

#### UltraRAG-Vis

Paper link: [https://arxiv.org/abs/2410.10594](https://arxiv.org/abs/2410.10594)

Model link: [https://huggingface.co/openbmb/VisRAG-Ret](https://huggingface.co/openbmb/VisRAG-Ret)

Repository link: [https://github.com/OpenBMB/VisRAG](https://github.com/OpenBMB/VisRAG)

![](../assets/en/implement_9.png)

#####  Method Overview

**UltraRAG-Vis** is a novel Retrieval-Augmented Generation (RAG) pipeline based on visual language models (VLM). Unlike traditional text parsing methods, UltraRAG-Vis directly embeds documents as images and uses VLM for retrieval and generation. This approach maximizes the retention and utilization of data in the original documents, avoiding potential information loss that may occur during traditional text parsing.

The workflow of **UltraRAG-Vis** is primarily divided into two modules: **Retrieval Module (VisRAG-Ret)** and **Generation Module (VisRAG-Gen)**. Unlike traditional text parsing methods, UltraRAG-Vis directly utilizes image embeddings for information retrieval, avoiding losses that may be introduced in traditional document parsing processes (such as OCR or text extraction).

###### 1. **VisRAG-Ret: Document Retrieval Module**

The core task of the VisRAG-Ret module is to convert the input query and document (image) into embedding vectors. This module uses the MiniCPM-V 2.0 model, integrating SigLIP as a visual encoder and MiniCPM-2B as an LLM Backbone, enabling it to handle both visual and text information simultaneously. When processing queries and documents, VisRAG-Ret first embeds them into a shared vector space and matches the most relevant documents through similarity calculations (e.g., dot product or cosine similarity).

- **Input**: Text query or image document.
- **Processing**: Perform visual encoding and language encoding on the input to generate corresponding embedding vectors.
- **Output**: Embedding vectors for queries and documents, used for subsequent retrieval and generation tasks.

###### 2. **VisRAG-Gen: Generation Module**

The VisRAG-Gen module uses the documents retrieved by the VisRAG-Ret module, in combination with queries, to generate corresponding text content. Unlike traditional RAG methods, VisRAG-Gen directly uses existing visual language models (such as MiniCPM-V 2.0, MiniCPM-V 2.6, and GPT-4o) for generation tasks.

- **Input**: Query and documents obtained from the retrieval module.
- **Processing**: Pass the query and document as inputs to the generation model to generate text via the generation model.
- **Output**: Text generated based on the input query and related documents.

###### 3. **Key Features and Advantages**

- **No Document Parsing Required**: **UltraRAG-Vis** directly accepts documents as image inputs, avoiding information loss during traditional parsing processes.
- **Multimodal Processing**: Handles both visual and linguistic information simultaneously, adapting to various types of documents (such as academic articles, images, or mixed text and image documents).
- **Flexible Generation Capability**: Directly utilizes existing visual language models for generation, providing high flexibility.
- **Enhanced Information Utilization**: Compared with traditional text-parsing RAG, **UltraRAG-Vis** maximizes information utilization by preserving the original visual information of the document.

#### UltraRAG-Embedding**

Model Address: [https://huggingface.co/openbmb/MiniCPM-Embedding-Light](https://huggingface.co/openbmb/MiniCPM-Embedding-Light)  

MiniCPM-Embedding-Light is a bilingual text embedding model for Chinese and English, jointly developed by BAAI (Beijing Academy of Artificial Intelligence), the Natural Language Processing Laboratory of Tsinghua University (THUNLP), and the Information Retrieval Group of Northeastern University (NEUIR). It exhibits excellent performance in Chinese and English retrieval tasks as well as cross-language retrieval between Chinese and English. The model supports long texts (up to 8192 tokens) and provides dense vectors as well as token-level sparse vectors. Additionally, it allows flexible dense vector dimensions (nested representations).  

Structurally, MiniCPM-Embedding-Light adopts bidirectional attention and Weighted Mean Pooling. It employs a multi-stage training approach, leveraging approximately 260 million training samples from open-source, machine-generated, and proprietary datasets. Thanks to a meticulously designed domain-adaptive data synthesis method (integrated into UltraRAG), MiniCPM-Embedding-Light demonstrates exceptional performance in retrieval tasks.

| Model                                                   | C-MTEB/Retrieval(NDCG@10) | BEIR(NDCG@10) |
| ------------------------------------------------------------ | ------------------------- | ------------- |
| bge-large-zh-v1.5                                            | 70.46                     | -             |
| gte-large-zh                                                 | 72.49                     | -             |
| Conan-embedding-v1                                           | 76.67                     |               |
| bge-large-en-v1.5                                            | -                         | 54.29         |
| modernbert-embed-large                                       | -                         | 54.36         |
| snowflake-arctic-embed-l                                     | -                         | 55.98         |
| gte-en-large-v1.5                                            | -                         | 57.91         |
| me5-large                                                    | 63.66                     | 51.43         |
| bge-m3(Dense)                                                | 65.43                     | 48.82         |
| gte-multilingual-base(Dense)                                 | 71.95                     | 51.08         |
| jina-embeddings-v3                                           | 68.60                     | 53.88         |
| gte-Qwen2-1.5B-instruct                                      | 71.86                     | 58.29         |
| MiniCPM-Embedding                                            | 76.76                     | 58.56         |
| MiniCPM-Embedding-Light(Dense)                               | 72.71                     | 55.27         |
| MiniCPM-Embedding-Light(Dense+Sparse)                        | 73.13                     | 56.31         |
| MiniCPM-Embedding-light(Dense+Sparse)+MiniCPM-Reranker-Light | 76.34                     | 61.49         |

| Model                                           | MKQA En-Zh_CN (Recall@20) | NeuCLIR22 (NDCG@10) | NeuCLIR23 (NDCG@10) |
| ----------------------------------------------------- | ------------------------- | ------------------- | ------------------- |
| me5-large                                             | 44.3                      | 9.01                | 25.33               |
| bge-m3(Dense)                                         | 66.4                      | 30.49               | 41.09               |
| gte-multilingual-base(Dense)                          | 68.2                      | 39.46               | 45.86               |
| MiniCPM-Embedding                                     | 72.95                     | 52.65               | 49.95               |
| MiniCPM-Embedding-Light(Dense)                        | 68.29                     | 41.17               | 45.83               |
| MiniCPM-Embedding-Light(Dense)+MiniCPM-Reranker-Light | 71.86                     | 54.32               | 56.50               |


##### Method Overview:

In typical RAG (Retrieval-Augmented Generation) scenarios, the document repository provided by users is often highly specialized in a specific domain. Retrieval models that have not been fine-tuned on the corresponding domain generally perform poorly. However, fine-tuning the retrieval model using domain-specific data can usually significantly improve retrieval results. The challenge lies in the collection of query-doc pairs needed for model fine-tuning. To address this, we automatically generate corresponding queries for the user's provided documents using LLM (Large Language Model), perform negative example mining, and conduct data cleaning for fine-tuning the retrieval model and reranking model, thereby enhancing retrieval performance in the RAG pipeline.

This module consists of four parts: Data Preprocessing, Query Synthesis, Negative Example Mining, and Data Cleaning.

##### Data Preprocessing:

In this module, we process the user documents to extract a certain number of semantically similar documents for each document, which will be used for subsequent data synthesis. The method involves using embeddings to compute the vector representation of the documents and calculating the cosine similarity between each document and other documents in the repository, selecting the top-ranked similar documents based on similarity.

![](../assets/en/implement_10.png)

Document data format `corpus.jsonl`:

```JSON
 {"contents": "This is document 1"}
```

Input Parameters:

| Parameter Name     | Required | Type   | Description                                  | Example/Default Value          |
| ------------------ | -------- | ------ | -------------------------------------------- | ------------------------------ |
| embed              | Yes      | str    | Path to the embedding model used for preprocessing | ~/UltraRAG-Vec                 |
| pooling            | No       | str    | Pooling method for the embedding model      | mean                           |
| corpus_path        | Yes      | str    | Path to user document slices                | ~/dataset/corpus.jsonl         |
| output_path        | Yes      | str    | Output path                                  | ~/dataset/preprocessed.jsonl   |
| search_start_index | No       | int    | Start index of the document extraction range | 1                              |
| search_end_index   | No       | int    | End index of the document extraction range   | 30                             |

Output: Preprocessed data format `synthesis_qd.jsonl`

```JSON
{"doc": "doc", "sims": ["doc", "doc2"]}
```


### Data Synthesis:

In this module, we synthesize corresponding queries for user documents, supporting both Chinese and English. Synthesis can be done using few-shot examples provided by the user, or zero-shot synthesis can be performed directly. We will provide the target document and a randomly selected negatively similar document (obtained in the previous stage) to the generation model. The model will generate a query related to the target document but unrelated to the negative example document.

![](../assets/en/implement_11.png)

Input file format `input.jsonl`:

```JSON
{"doc": "doc", "sims": ["doc", "doc2"]}
```

Example data `shot.jsonl`, output format `output.jsonl`:

```JSON
{"query": "This is query1", "pos": ["This is the correct document1"]}
```

Outputs can also support multiple file formats (aligned with evaluation and BEIR):

Including three files: query data `query.jsonl`, document data `corpus.jsonl`, and triplet file `qrels.tsv`.

Query data format `query.jsonl`, document data format `corpus.jsonl`:

```JSON
 {"_id": "aaa", "text": "This is document1"}
 {"_id": "aaa", "text": "This is query1"}
```

Triplet file format `qrels.tsv` (note the separator is a tab):

```Plain
query-id    corpus-id    score
aaa    bbb    1
```


Input Parameters:

| Parameter Name         | Required | Type   | Description                                                                 | Example/Default Value                                          |
| ---------------------- | -------- | ------ | --------------------------------------------------------------------------- | -------------------------------------------------------------- |
| api_key                | Yes      | str    | API key for model generation similar to OpenAI                              | sk-114514NYNICG                                                |
| base_url               | Yes      | str    | Server URL for model generation similar to OpenAI                           | ~/dataset/corpus.jsonl                                         |
| model_name             | Yes      | str    | Name of the model for generation similar to OpenAI                          | gpt-4o                                                         |
| language               | Yes      | str    | User document language; currently supports Chinese and English ('zh', 'en') | zh                                                             |
| input_pair_path        | Yes      | str    | File address of the pre-processed document                                  | ~/dataset/preprocessed.jsonl                                   |
| output_path            | Yes      | str    | Output file address                                                         | ~/dataset/synthesis_train.jsonl ~/dataset/qrels.tsv (three-file format) |
| query_num_per_corpus   | Yes      | int    | Number of queries to synthesize per document                                | 5                                                              |
| query_path             | No       | str    | Output query file address (if provided, outputs in three-file format)       | ~/dataset/synthesis_query.jsonl                                |
| corpus_path            | No       | str    | Output document file address (if provided, outputs in three-file format)    | ~/dataset/synthesis_corpus.jsonl                               |
| corpus_sample_num      | No       | int    | Number of documents to create queries for                                   | -1 (default is all)                                            |
| neg_start_index        | No       | int    | Start index for extracting negative document examples                        | 1                                                              |
| negs_end_index         | No       | int    | End index for extracting negative document examples                         | 30                                                             |
| shot_num               | No       | int    | Number of shots provided during Few-shot synthesis; set to 0 for Zero-shot | 0 (Zero-shot)                                                  |
| shot_file              | No       | str    | Example file provided by the user                                           | ~/dataset/shot.jsonl                                           |
| input_prompt_path      | No       | str    | Custom data prompt provided by the user                                     | ~/prompt.txt                                                   |

### Negative Example Mining:

For both the embedding model and the reranker model, positive and negative examples need to be provided during training. In the previous step, we synthesized a query from the document, and for this query, the document is considered a positive example. Afterward, we need to mine semantically similar documents as negative examples for the query by examining the similarity between the query and documents in the document library. (Of course, the mined negative examples might also be related to the query, i.e., they might be false negatives; in the next step, we will perform data cleaning to try and filter out these false negatives.)

![](../assets/en/implement_12.png)

Training data format `train.jsonl`

```JSON
{"query": "This is query1", "pos": ["This is the correct document1"]}
```

Document data format `corpus.jsonl`:

```JSON
 {"id": "aaa", "contents": "This is document1"}
```

Input parameters:

| Parameter Name     | Required | Parameter Type | Description                                                   | Example/Default Value   |
| ------------------ | -------- | -------------- | ------------------------------------------------------------- | ----------------------- |
| embed              | Yes      | str            | Path for the embedding model used for data preprocessing      | ~/UltraRAG-Vec          |
| pooling            | No       | str            | Pooling method for the embedding model used for data preprocessing | mean                    |
| query_instruction  | No       | str            | Instruction to be added before the query in the embedding model for data preprocessing | None (no Instruction)   |
| corpus_path        | Yes      | str            | Path to the user document slices                              | ~/dataset/corpus.jsonl  |
| qrel_path          | Yes      | str            | Path to the training data                                     | ~/dataset/train.jsonl   |
| output_path        | Yes      | str            | Output path                                                   | ~/dataset/diged.jsonl   |
| search_start_index | No       | int            | Starting index for document mining range                      | 1                       |
| search_end_index   | No       | int            | Ending index for document mining range                        | 30                      |


### Data Cleaning:

In this stage, we aim to filter out false negative and false positive samples to improve the quality of the training data. Some common methods include filtering false negatives based on the ratio or difference of the similarity scores between the query and positive/negative examples; filtering false positives based on the ranking of positives relative to the query (the method here involves filtering out negatives when a data point contains fewer negatives, which effectively removes samples where positive examples rank lower).

![](../assets/en/implement_13.png)

**Data Format: `train.jsonl`**

```json
{"query": "This is query1", "pos": ["This is the correct document1"]}
```

**Input Parameters:**

| Parameter Name     | Required | Type   | Description                                                   | Example/Default Value              |
| ------------------ | -------- | ------ | ------------------------------------------------------------- | ---------------------------------- |
| embed/reranker     | Yes      | str    | Path to the embedding/reranker model used for data preprocessing | ~/UltraRAG-Vec ~/UltraRAG-Reranker |
| pooling            | No       | str    | Pooling method for the embedding model used in data preprocessing | mean                               |
| query_instruction  | No       | str    | Instruction to be added before the query in the embedding model during data preprocessing | None (do not add Instruction)      |
| qrel_path          | Yes      | str    | Path to the training data                                     | ~/dataset/diged.jsonl              |
| output_path        | Yes      | str    | Output path                                                   | ~/dataset/clean.jsonl              |
| search_start_index | No       | int    | Start index of the document negatives range                   | 1                                  |
| search_end_index   | No       | int    | End index of the document negatives range                     | 30                                 |
| keep_neg_num       | No       | int    | Number of negatives to retain per entry                       | 7                                  |
| score_ratio        | No       | float  | Maximum ratio of negative score to positive score             | 1.0                                |
| score_margin       | No       | float  | Minimum value of positive score minus negative score          | 0.0                                |
| min_pos_score      | No       | float  | Minimum positive score                                        | 0.0                                |
| max_neg_score      | No       | float  | Maximum negative score                                        | 0.0                                |
