LANGUAGES = ['en', 'zh']
MODEL_TYPES = ['API', 'Custom']
EMBEDDING_MODEL_TYPES = ['Custom','API']
RERANKER_MODEL_TYPES = ['Custom']
# MODEL_TYPES = ['openbmb/MiniCPM-2B-sft-bf16', 'openbmb/MiniCPM-2B-dpo-bf16', 'API', 'Custom']
# EMBEDDING_MODEL_TYPES = ['OpenBMB/MiniCPM-Embedding-Light', 'OpenBMB/MiniCPM-Embedding-Light', 'Custom']
# RERANKER_MODEL_TYPES = ['OpenBMB/MiniCPM-Reranker-Light','OpenBMB/MiniCPM-Reranker', 'Custom']
ADVANCE_TABS=["Knowledge Base Manage"]
TABS = [
    {"name": "Data Construction", "module": "pages.data_construction.main", "file_path":"ultrarag/datasets/data_construction.py"},
    {"name": "Train", "module": "pages.train.main", "file_path":"ultrarag/finetune/train.py"},
    {"name": "Evaluation", "module": "pages.eval.main", "file_path":"ultrarag/evaluate/eval.py"},
    {"name": "Chat/Inference", "module": "pages.chat.main", "file_path":"ultrarag/chat/chat.py"},
]

DATA_PIPELINE = [    
    {"name": "Merge", "module": "pages.data_construction.pipeline.merge", "pipeline": "merge"},
    {"name": "UltraRAG-Embedding", "module": "pages.data_construction.pipeline.embedding", "pipeline": "embedding_training_data"},
    {"name": "UltraRAG-DDR", "module": "pages.data_construction.pipeline.ddr", "pipeline": "ddr"},
    {"name": "UltraRAG-KBAlign", "module": "pages.data_construction.pipeline.kbalign", "pipeline": "kbalign"},
]

TRAIN_PIPELINE = [    
    {"name": "Embedding", "module": "pages.train.pipeline.bgem3", "pipeline": "bgem3"},
    {"name": "DPO", "module": "pages.train.pipeline.dpo", "pipeline": "dpo"},
    {"name": "SFT", "module": "pages.train.pipeline.sft", "pipeline": "sft"},
    # {"name": "KBAlign", "module": "pages.train.pipeline.kbalign", "pipeline": "kbalign"},
]

EMBEDDING_STEPS = [
    {"name": "Data Preprocessing Synthesis", "module": "pages.data_construction.pipeline.embedding_step.data_preprocessing_synthesis", "pipeline": "data_preprocessing_synthesis"},
    {"name": "Data Synthesis", "module": "pages.data_construction.pipeline.embedding_step.data_synthesis", "pipeline": "data_synthesis"},
    {"name": "Dig Hard Neg", "module": "pages.data_construction.pipeline.embedding_step.dig_hard_neg", "pipeline": "dig_hard_neg"},
    {"name": "Clean Data", "module": "pages.data_construction.pipeline.embedding_step.clean_data", "pipeline": "clean_data"},
    {"name": "Reranker Clean Data", "module": "pages.data_construction.pipeline.embedding_step.reranker_clean_data", "pipeline": "reranker_clean_data"},
]

EVAL_PIPELINE = [    
    {"name": "Vanilla RAG", "module": "pages.eval.pipeline.vanilla", "pipeline": "vanilla"},
    {"name": "KBAlign", "module": "pages.eval.pipeline.kbalign", "pipeline": "kbalign"},
    {"name": "UltraRAG-Adaptive-Note", "module": "pages.eval.pipeline.renote", "pipeline": "renote"},
]

CHAT_PIPELINE = [    
    {"name": "Vanilla RAG", "module": "pages.chat.pipeline.vanilla", "pipeline": "vanilla"},
    {"name": "KBAlign", "module": "pages.chat.pipeline.kbalign", "pipeline": "kbalign"},
    {"name": "UltraRAG-Adaptive-Note", "module": "pages.chat.pipeline.renote", "pipeline": "renote"},
    {"name": "VisRAG", "module": "pages.chat.pipeline.visrag", "pipeline": "visrag"},
    {"name": "AgentRAG", "module": "pages.chat.pipeline.agentrag", "pipeline": "agentrag"},
]
RETRIEVAL_METRICS = ["MRR","NDCG","Recall"]
GENERATED_METRICS = ["completeness","rouge","em","accuracy","f1","bleu","meteor","bert","jec"]