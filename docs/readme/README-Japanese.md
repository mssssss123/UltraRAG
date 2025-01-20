# UltraRAG

<div align="center">
    <img src="../assets/logo.png" alt="UltraRAG Logo" width="450">
</div>
<p align="center">
    【<a href="../README.md">英語</a> | 中国語 | <a href="./README-Japanese.md">日本語</a>】
</p>
<p align="center">
    【📚 <a href="https://modelbest.feishu.cn/docx/UDq0dzzm2omhWMxQ38bciLC7nyc">ドキュメント</a>】
</p>

## 📖 概要

UltraRAGは、典型的な実装と柔軟な編集を目的としたオールインワンのRAGフレームワークです。研究型実験の迅速な実現や、個人でのアジャイルなデプロイ、評価、デモンストレーションをサポートします。現在のRAGフレームワークとは異なり、UltraRAGには以下の利点があります：
  - 即時利用可能なオールインワンRAGフレームワークであり、データ構築、モデルの微調整、評価、体験をすべてカバー
  - 使いやすいWebUIを提供し、コードを書く必要なく、フロントエンド操作のみで多様な要件を満たす
  - 継続的な技術サポートを提供し、UltraRAGの機能を充実させ、研究とプロジェクトの進行を加速

<div align="center">
  <img src='../assets/en/image.png' width=600>
</div>

## ✨️ 主な特徴
- **効果体験**：UltraRAGはモジュール化されたツールを内蔵しており、柔軟にカスタマイズ可能なワークフローを体験できます。また、VisRAG、Adaptive-Note、VanillaRAGなど、さまざまなプリセットワークフローを提供し、異なる使用ニーズに対応します。
- **データ構築**：検索モデルから生成モデルまで、フルプロセスのデータ構築ソリューションを提供し、ナレッジベースからデータを一括インポートおよび生成可能です。
- **適応微調整**：EmbeddingモデルのトレーニングやLLMのDPO/SFT微調整をサポートし、構築したデータを活用してモデルを最適化するための完全なトレーニングスクリプトを提供。
- **効果評価**：検索モデルおよび生成モデルの多次元評価指標をカバーし、全体から各ステップまで、モデルおよび方法の性能を包括的に評価可能。
**以上のすべての機能は、Webフロントエンドで迅速に実現できます。**

<div align="center">
  <img src='../assets/en/image2.png' width=600>
</div>

## 🔧全体アーキテクチャ
UltraRAGのフレームワーク全体は3つの部分に分かれています：フロントエンドページ、バックエンドモジュール、マイクロサービス。
- フロントエンドページはリソース管理と機能ページの2つの部分に分かれています。リソース管理にはモデル管理とナレッジベース管理が含まれます。機能ページにはデータ構築、モデルトレーニング、効果評価、推論体験が含まれます。
- バックエンドモジュールはworkflow、modules、モデル微調整スイートに分かれます：datasets（データ構築）、finetune（モデル微調整）、evaluate（効果評価）。workflowではいくつかの典型的なワークフローを提供しており、それを参考にして独自のワークフローを開発できます。modulesはRAGシナリオでの典型的なモジュールを提供しており、各モジュールはworkflowの開発プロセスで簡単に再利用可能です。モデル微調整スイートは、パイプラインと技術方法の完全なセットを提供しており、各種論文の技術成果をカバーしています。
- マイクロサービスインターフェース：UltraRAGはRAGのオールインワンフレームワークソリューションを提供するため、モデル微調整が含まれるため、マイクロサービスのデプロイ能力が必要です。現在、UltraRAGは主流のRAGリンクでのクラシックモデルをサポートしており、今後さらに機能を充実させ、より多くのモデルに対応する予定です。

<div align="center">
    <img src="../assets/en/image3.png" width="600">
</div>

## ⚡️クイックスタート
UltraRAGは単一マシンで簡単なデモをデプロイできます。Python依存関係をインポートしてローカルで簡単なUI対話サンプルをデプロイできます。以下の方法でUltraRAGフレームワークを利用できます：
1. dockerデプロイ
    
    以下のコマンドを実行し、ブラウザで「http://localhost:8843」を開きます。
    ```bash
    docker-compose up --build -d
    ```
2. condaデプロイ
    ```bash
    # conda環境を作成
    conda create -n UltraRAG python=3.10

    # conda環境をアクティブ化
    conda activate UltraRAG

    # 必要な依存関係をインストール
    pip install -r requirements.txt

    # デモページを実行
    streamlit run UltraRAG/webui/app.py --server.fileWatcherType none
    ```

### モデルダウンロード
以下のコマンドを実行してモデルをダウンロードします。デフォルトでは**resources/models**ディレクトリにダウンロードされ、ダウンロードするモデルのリストは**UltraRAG/resources/models/model_list.txt**に記載されています。
```bash
python UltraRAG/scripts/download_models.py
```

### 必要な環境

**cuda**バージョン: **12.2**以上

**python**バージョン: **3.10**以上

## 💫典型的な実装

### 法律分野データを使用したVanillaRAGモデルの微調整前後の評価

1. **VanillaRAG-original**  
   デフォルトのUltraRAGモデル（BGE-M3 + MiniCPM3-4B）で評価した結果。

2. **VanillaRAG-finetune**  
   MiniCPM-Embedding-LightおよびUltraRAG-DDRを法律分野データで微調整した結果。

以下は、UltraRAGの評価ページから得られた結果です。微調整により、全体のパフォーマンスが**3%**向上しました。知識Q&Aの性能はやや低下しましたが、法条予測と相談のデータセットではそれぞれ**2%以上**の向上が見られました。

---

| **手法**               | **知識Q&A (1-2)** | **法条予測 (3-2)**   | **相談 (3-8)**   | **平均**  |
|------------------------|-------------------|-----------------------|------------------|-----------|
| **Vanilla**            | 68.8             | 44.96                | 23.65           | 45.80     |
| **Renote**             | -                | -                    | -               | -         |
| **Embedding**          | -                | -                    | -               | -         |
| **DDR**                | -                | 53.14                | 23.59           | -         |
| **KBAlign**            | -                | -                    | -               | -         |
| **Finetune**           | 67.8             | 52.80                | 25.85           | 48.82     |

| モデル                                    | GPT-4oによるテストセット200件のMRR@10 | GPT-4oによるテストセット200件のNDCG@10 | GPT-4oによるテストセット200件のRecall@10 |
|------------------------------------------|--------------------------------------|---------------------------------------|-----------------------------------------|
| MiniCPM-Embedding-Light                       | 36.46                                | 40.05                                 | 54.50                                  |
| MiniCPM-Embedding-Light-Finetune(Qwen2.5-14B-instructionによる2800件) | 37.57                                | 42.12                                 | 56.50                                  |

## ‍🤝謝辞
以下の貢献者によるコード提供とテストに感謝します。新しいメンバーの参加を歓迎し、一緒に完全なエコシステムの構築を目指しましょう！

<a href="https://github.com/OpenBMB/UltraRAG/contributors">
  <img src="https://contrib.rocks/image?repo=OpenBMB/UltraRAG" />
</a>

## 🌟トレンド

<a href="https://star-history.com/#OpenBMB/UltraRAG&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=OpenBMB/UltraRAG&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=OpenBMB/UltraRAG&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=OpenBMB/UltraRAG&type=Date" />
 </picture>
</a>

## ⚖️ライセンス

- ソースコードは[Apache-2.0](https://github.com/OpenBMB/MiniCPM/blob/main/LICENSE)ライセンスの下で提供されています。

## 📑引用
このリポジトリが役立つと感じた場合、ぜひスター ⭐ を付け、引用してサポートしてください。

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