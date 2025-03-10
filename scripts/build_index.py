import sys
from loguru import logger
import asyncio
import argparse
import jsonlines
import pandas as pd
sys.path.append(".")
sys.path.append("..")
from pathlib import Path
from ultrarag.modules.embedding import load_model
from ultrarag.modules.database import QdrantIndex

def main():
    args = argparse.ArgumentParser()
    args.add_argument('--file', type=str, required=True, help='a jsonl file , each line with ‘content‘ fleid')
    args.add_argument('--index', type=str, default='./resource/kb_manager/', help='vector database save path')
    args.add_argument('--model', type=str, required=True, help='the embedding model path')
    
    args = args.parse_args()
    qdrant_path = Path(args.index) / 'kb_qdrant'
    qdrant_path.mkdir(exist_ok=True)
    qdrant_path = qdrant_path.as_posix()
    
    encoder = load_model(args.model, device='cuda:0')
    qdrant_index = QdrantIndex(qdrant_path, encoder=encoder)

    with jsonlines.open(args.file, 'r') as fr:
        chunked_context = list(fr)

    collection_name = Path(args.file).stem
    asyncio.run(qdrant_index.create(collection_name=collection_name))
    asyncio.run(qdrant_index.insert(collection_name, chunked_context, func=lambda x: x["content"]))

    config_list = Path(args.index) / 'manage_table/knowledge_base_manager.csv'
    config_list.parent.mkdir(exist_ok=True)
    config_list = config_list.as_posix()
    
    logger.info(f"config_list: {config_list}")
    if Path(config_list).exists():
        df = pd.read_csv(config_list)
    else:
        df = pd.DataFrame()

    new_line = dict(
        kb_config_id="123456",
        knowledge_base_id='31234',
        qdrant_path=qdrant_path,
        knowledge_base_name=Path(args.file).stem,
        file_ids=args.file,	
        embedding_model_name=Path(args.model).stem,
        embedding_model_path=args.model,
        chunk_size = 256,
        overlap= 10,
        others={}
    )
    df = pd.concat([df, pd.DataFrame([new_line])])
    df.to_csv(config_list, index=False)


if __name__ == "__main__":
    main()