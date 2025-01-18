# UltraRAG

<div align="center">
    <img src="docs/assets/logo.png" alt="UltraRAG Logo" width="450">
</div>
<p align="center">
    【English | <a href="docs/readme/README-Chinese.md">Chinese</a> | <a href="docs/readme/README-Chinese.md">Japanese</a>】
</p>
<p align="center">
    【📚 <a href="https://modelbest.feishu.cn/docx/UDq0dzzm2omhWMxQ38bciLC7nyc">Document</a>】
</p>

## 📖 Overview

UltraRAG is a one-stop RAG framework designed for typical implementations and flexible editing. It supports rapid research-oriented experiments, agile deployment, evaluation, and demonstration for individuals. Unlike existing RAG frameworks, UltraRAG offers the following advantages:
  - A plug-and-play, one-stop RAG framework that covers data construction, model fine-tuning, evaluation, and demonstration.
  - Provides a user-friendly WebUI that allows you to meet various needs without writing any code.
  - Continuously improving technical support to enrich and enhance UltraRAG's functionality, accelerating your research and project progress.

<div align="center">
  <img src='docs/assets/en/image.png' width=600>
</div>

## ✨️ Key Features
- **Performance Experience**: UltraRAG includes modular tools for flexible customization and personalized workflows. It also offers several preset workflows, such as VisRAG, Adaptive-Note, and VanillaRAG, to meet different usage requirements.
- **Data Construction**: From retrieval models to generation models, UltraRAG offers end-to-end data construction solutions. It allows one-click data import and generation from knowledge bases.
- **Fine-tuning Adaptation**: Supports training of embedding models and DPO/SFT fine-tuning of LLMs, with complete training scripts provided to facilitate model optimization using constructed data.
- **Performance Evaluation**: Covers multidimensional evaluation metrics for retrieval and generation models, enabling comprehensive performance assessment from individual components to the overall system.
**All these features can be accessed directly through the web frontend.**

<div align="center">
  <img src='docs/assets/en/image2.png' width=600>
</div>

## 🔧 Architecture
UltraRAG's framework is divided into three main parts: frontend interface, backend modules, and microservices.
- The frontend interface consists of resource management and functional pages. Resource management includes model and knowledge base management. Functional pages cover data construction, model training, performance evaluation, and inference experience.
- Backend modules are categorized into workflow, modules, and model fine-tuning suites: datasets (data construction), finetune (model fine-tuning), and evaluate (performance evaluation). The workflow module implements several typical workflows, which you can use as examples to develop your own workflows. The modules provide typical components for RAG scenarios, which can be easily reused in workflow development. The model fine-tuning suite offers a complete pipeline and technical methods, incorporating results from various papers, and is continuously updated.
- Microservice Interfaces: As a one-stop framework for RAG, UltraRAG involves microservice deployment capabilities for model fine-tuning. It currently supports mainstream RAG pipeline models and will continue to expand compatibility with more models.

<div align="center">
  <img src='docs/assets/en/image3.png' width=600>
</div>

## ⚡️ Quick Start
UltraRAG supports simple demo deployment on a single machine. You can deploy a basic UI dialogue demo locally by installing Python dependencies. Here are several ways to use the UltraRAG framework:
1. Docker Deployment

    Run the following commands, then access "http://localhost:8843" in your browser:
    ```bash
    docker-compose up --build -d
    ```
2. Conda Deployment
    ```bash
    # Create a conda environment
    conda create -n UltraRAG python=3.10

    # Activate the conda environment
    conda activate UltraRAG

    # Install dependencies
    pip install -r requirements.txt

    # Run the demo page
    streamlit run UltraRAG/webui/app.py --server.fileWatcherType none
    ```

### Model Download
Run the following command to download models. By default, models will be downloaded to the **resources/models** directory. The list of downloadable models is in **UltraRAG/resources/models/model_list.txt**.
```bash
python UltraRAG/scripts/download_models.py
```

### Environment Requirements

**CUDA** version: **12.2** or higher

**Python** version: **3.10** or higher

## 💫Typical implementation

### Evaluation of VanillaRAG Model Before and After Fine-tuning with Legal Domain Data

1. **VanillaRAG-original**  
   Results evaluated using the default UltraRAG model (BGE-M3 + MiniCPM3-4B).

2. **VanillaRAG-finetune**  
   Results after fine-tuning UltraRAG-Embedding and UltraRAG-DDR with legal domain data.

The following results are obtained from the UltraRAG evaluation page for these two workflows. Fine-tuning led to an overall improvement of **3%**, with a slight decrease in knowledge Q&A performance but over **2% improvements** in the legal provision prediction and consultation datasets.

---

| **Method**            | **Knowledge Q&A (1-2)** | **Provision Prediction (3-2)** | **Consultation (3-8)** | **Average** |
|------------------------|-------------------------|---------------------------------|-------------------------|-------------|
| **Vanilla**            | 68.8                   | 44.96                          | 23.65                  | 45.80       |
| **Renote**             | -                      | -                              | -                      | -           |
| **Embedding**          | -                      | -                              | -                      | -           |
| **DDR**                | -                      | 53.14                          | 23.59                  | -           |
| **KBAlign**            | -                      | -                              | -                      | -           |
| **Finetune**           | 67.8                   | 52.80                          | 25.85                  | 48.82       |

| Model                                    | MRR@10 for 200 Test Samples by GPT-4o | NDCG@10 for 200 Test Samples by GPT-4o | Recall@10 for 200 Test Samples by GPT-4o |
|------------------------------------------|---------------------------------------|----------------------------------------|------------------------------------------|
| UltraRAG-Embedding                       | 36.46                                 | 40.05                                  | 54.50                                    |
| UltraRAG-Embedding-Finetune(Qwen2.5-14B-instruction, 2800 samples) | 37.57                                 | 42.12                                  | 56.50                                    |

## ‍🤝Acknowledgments
We sincerely thank the following contributors for their code contributions and testing. New members are welcome to join us in building a complete ecosystem!

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
If you find this repository useful, please consider giving it a star ⭐ and citing it in your work.

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
```