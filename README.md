<div align="center">
    <img src="docs/assets/logo.png" alt="UltraRAG Logo" width="450">
</div>
<p align="center">
    【English | <a href="docs/readme/README-Chinese.md">Chinese</a>】
</p>

## 📖 Overview

The **UltraRAG framework** was jointly proposed by the THUNLP group from Tsinghua University, the NEUIR group from Northeastern University, and Modelbest.Inc . It is based on agile deployment and modular construction, introducing an automated "data construction-model fine-tuning-inference evaluation" knowledge adaptation technology system. This provides a one-stop, researcher and developer-friendly RAG system solution. UltraRAG significantly simplifies the entire process from data construction to model fine-tuning in domain adaptation for RAG systems, assisting researchers and developers in efficiently tackling complex tasks.

<div align="center">
  <img src='docs/assets/en/feature.jpg' width=600>
</div>

- **No-Code Programming WebUI Support:** Users with no programming experience can easily operate the full link setup and optimization process, including the **multimodal RAG solution VisRAG**;
- **One-Click Solution for Synthesis and Fine-Tuning:** Centered around proprietary methods such as **KBAlign, RAG-DDR**, the system allows for one-click systematic data construction + retrieval, and supports performance optimization with diverse model fine-tuning strategies;
- **Multidimensional, Multi-Stage Robust Evaluation:** Using the proprietary **RAGEval** method at its core, it incorporates multi-stage assessment methods focused on effective/key information, significantly enhancing the robustness of "model evaluation";
- **Research-Friendly Exploration Work Integration:** It includes **THUNLP-RAG group's proprietary methods** and other cutting-edge RAG methods, supporting continuous module-level exploration and development.

**All of the above features can be quickly implemented directly through the web frontend.**

<div align="center">
  <img src='docs/assets/en/image2.png' width=600>
</div>

## ⚡️ Quick Start

### Environmental Dependencies

**CUDA** version should be **12.2** or above.

**Python** version should be **3.10** or above.

### Quick Deployment

You can deploy UltraRAG and run the front-end page using the following methods:

1. **Deploy via Docker**

Run the following command, then visit "[http://localhost:8843](http://localhost:8843/)" in your browser.

```Bash
docker-compose up --build -d
```

2. **Deploy via Conda**

Run the following commands, then visit "[http://localhost:8843](http://localhost:8843/)" in your browser.

```Bash
# Create a conda environment
conda create -n ultrarag python=3.10

# Activate the conda environment
conda activate ultrarag

# Install relevant dependencies
pip install -r requirements.txt

# Run the following script to download models, by default they will be downloaded to the resources/models directory
# The list of downloaded models is in resources/models/model_list.txt
python scripts/download_models.py

# Run the demo page
streamlit run ultrarag/webui/webui.py --server.fileWatcherType none
```

### Easy to Get Started

https://github.com/user-attachments/assets/b07d20d9-4121-404a-9cba-e89590bd4f4e

The above video provides a simple demonstration of the getting started experience. To facilitate your use of UltraRAG, we offer a detailed guide to help you get started with UltraRAG, complete the experience, and optimize the model [User Guide](../user_guide/user_guide_en.md).

If you are interested in the technical solutions involved, you can gain a more comprehensive understanding through the [UltraRAG Series](../typical_implementation/typical_implementation_en.md).

## 🔧 Overall Architecture

The architecture of UltraRAG is composed of three parts: **Frontend**, **Service**, and **Backend**. The specifics are as follows:

* **Backend**
  * **Modules (Module Layer):** Defines the key components in the RAG system, such as the knowledge base, retrieval model, and generation model, supporting users to customize flexibly based on standard classes.
  * **Workflow (Process Layer):** Standardizes the composition patterns of the RAG system, provides a standardized basic RAG implementation, and integrates team-developed typical methods like Adaptive-Note and VisRAG. It supports users in building and adjusting flexibly and will continue to be supplemented and optimized.
  * **Function (Function Layer):** Responsible for key operations in the optimization process of the RAG system, including data synthesis, system evaluation, and model fine-tuning, contributing to the comprehensive improvement of system performance.
* **Service:** Apart from supporting instance-based RAG system construction, UltraRAG also provides a microservice deployment mode to optimize user experience during application, supporting flexible deployment of key services like Embedding Model, LLM, and vector databases.
* **Frontend:** The frontend is divided into Resource Management and Function Pages. Resource Management includes **Model Management** and **Knowledge Base Management**, while the Function Pages cover **Data Construction, Model Training, Effect Evaluation**, and **Inference Experience**, providing users with convenient interactive support.

<div align="center">
    <img src='docs/assets/en/image3.png' width=600>
</div>

## 💫 Performance Evaluation

To verify the application effectiveness of UltraRAG in vertical domains, we took the legal field as an example, collected various professional books, and built a knowledge base containing **880,000 slices**. We then performed a systematic evaluation on UltraRAG based on a relatively comprehensive evaluation dataset. The following are our evaluation results. For more detailed evaluation content, please refer to the relevant document. [Evaluation Report](../evaluation_report/evaluation_report_en.md).

| **End-to-End Performance** | **Statute Prediction (3-2) ROUGE-L** |
| -------------------------------- | ------------------------------------------ |
| **VanillaRAG**             | 40.75                                      |
| **UltraRAG-DDR**           | 53.14                                      |
| **UltraRAG-KBAlign**       | 48.72                                      |

| **End-to-End Performance** | **Consultation (3-8) ROUGE-L** |
| -------------------------------- | ------------------------------------ |
| **VanillaRAG**             | 23.65                                |
| **UltraRAG-Adaptive-Note** | 24.62                                |
| **VanillaRAG-finetune**    | 25.85                                |

## ‍🤝 Acknowledgments

Thanks to the following contributors for code submissions and testing. New members are welcome to join us in striving to build a complete ecosystem!

<a href="https://github.com/OpenBMB/UltraRAG/contributors">
  <img src="https://contrib.rocks/image?repo=OpenBMB/UltraRAG" />
</a>

## 🌟 Trends

<a href="https://star-history.com/#OpenBMB/UltraRAG&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=OpenBMB/UltraRAG&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=OpenBMB/UltraRAG&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=OpenBMB/UltraRAG&type=Date" />
 </picture>
</a>

## ⚖️ License

- The source code is licensed under the [Apache-2.0](https://github.com/OpenBMB/MiniCPM/blob/main/LICENSE) license.

## 📑 Citation

If you find this repository useful, please consider giving it a star ⭐ and citing it to show your support.

```bib
@article{li2024rag,
  title={RAG-DDR: Optimizing Retrieval-Augmented Generation Using Differentiable Data Rewards},
  author={Li, Xinze and Mei, Sen and Liu, Zhenghao and Yan, Yukun and Wang, Shuo and Yu, Shi and Zeng, Zheni and Chen, Hao and Yu, Ge and Liu, Zhiyuan and others},
  journal={arXiv preprint arXiv:2410.13509},
  year={2024}
}

@article{yu2024visrag,
  title={Visrag: Vision-based retrieval-augmented generation on multi-modality documents},
  author={Yu, Shi and Tang, Chaoyue and Xu, Bokai and Cui, Junbo and Ran, Junhao and Yan, Yukun and Liu, Zhenghao and Wang, Shuo and Han, Xu and Liu, Zhiyuan and others},
  journal={arXiv preprint arXiv:2410.10594},
  year={2024}
}

@article{wang2024retriever,
  title={Retriever-and-Memory: Towards Adaptive Note-Enhanced Retrieval-Augmented Generation},
  author={Wang, Ruobing and Zha, Daren and Yu, Shi and Zhao, Qingfei and Chen, Yuxuan and Wang, Yixuan and Wang, Shuo and Yan, Yukun and Liu, Zhenghao and Han, Xu and others},
  journal={arXiv preprint arXiv:2410.08821},
  year={2024}
}

@article{zeng2024kbalign,
  title={KBAlign: KBAlign: Efficient Self Adaptation on Specific Knowledge Bases},
  author={Zeng, Zheni and Chen, Yuxuan and Yu, Shi and Yan, Yukun and Liu, Zhenghao and Wang, Shuo and Han, Xu and Liu, Zhiyuan and Sun, Maosong},
  journal={arXiv preprint arXiv:2411.14790},
  year={2024}
}

@article{zhu2024rageval,
  title={Rageval: Scenario specific rag evaluation dataset generation framework},
  author={Zhu, Kunlun and Luo, Yifan and Xu, Dingling and Wang, Ruobing and Yu, Shi and Wang, Shuo and Yan, Yukun and Liu, Zhenghao and Han, Xu and Liu, Zhiyuan and others},
  journal={arXiv preprint arXiv:2408.01262},
  year={2024}
}
```
