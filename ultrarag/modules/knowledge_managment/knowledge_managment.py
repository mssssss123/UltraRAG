from typing import Any, Dict, List
import torch
import pandas as pd
import os
from ultrarag.common.utils import get_embedding_types
from ultrarag.modules.database import QdrantIndex, BaseNode
from ultrarag.modules.knowledge_managment.doc_index import doc_index, vis_doc_index, doc_to_docx
from ultrarag.modules.embedding import BaseEmbedding
from transformers import AutoConfig
from loguru import logger
from tqdm import tqdm

class QdrantIndexSearchWarper:
    def __init__(self, embedding_model: BaseEmbedding, knowledge_id: str, qdrant_path: str, knowledge_stat_tab_path:str) -> None:
        self.knowledge_id = knowledge_id
        if os.path.exists(knowledge_stat_tab_path):
            self.init_files(knowledge_stat_tab_path)
        self.qdrant_index = QdrantIndex(url = qdrant_path, encoder = embedding_model)
        self.embedding_model = embedding_model

    # todo
    def search_with_data(self, query: str, data: List[str], top_k: int = 5, batch_size: int = 256) -> List[str]:
        """
        Perform search with a given query and data array using GPU.

        Args:
            query (str): The search query.
            data (List[str]): The data array to search against.
            top_k (int): Number of top results to return.
            batch_size (int): Size of batches for embedding computation.

        Returns:
            List[Dict[str, Any]]: Top-k search results.
        """
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        query_embedding = torch.tensor(self.embedding_model.encode([query]), device=device, dtype=torch.float32)

        data_embeddings = []
        for i in range(0, len(data), batch_size):
            batch = [item for item in data[i:i + batch_size]]
            batch_embeddings = self.embedding_model.encode(batch)
            data_embeddings.append(torch.tensor(batch_embeddings, device=device, dtype=torch.float32))
        data_embeddings = torch.cat(data_embeddings, dim=0)

        query_norm = query_embedding.norm(dim=-1, keepdim=True)
        data_norm = data_embeddings.norm(dim=-1, keepdim=True)
        similarities = (data_embeddings @ query_embedding.T) / (data_norm * query_norm)

        top_k_indices = torch.topk(similarities.squeeze(), k=top_k).indices.tolist()
        return [data[i] for i in top_k_indices]

    def init_files(self, knowledge_stat_tab_path): 
        _, ext = os.path.splitext(knowledge_stat_tab_path)
        if ext == '.csv':
            knowledge_stat_tab = pd.read_csv(knowledge_stat_tab_path)
        elif ext == '.json':
            knowledge_stat_tab = pd.read_json(knowledge_stat_tab_path, orient='records', lines=True)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        self.chunk_files = []
        for i,row in enumerate(knowledge_stat_tab['qdrant_path']):
            if knowledge_stat_tab['knowledge_base_id'].values[i] in self.knowledge_id:
                kb_path = row
                kb_base = kb_path.replace("_qdrant", "")
                self.chunk_files.append(os.path.join(kb_base, f"{knowledge_stat_tab['knowledge_base_id'].values[i]}.jsonl"))
        self.org_files = knowledge_stat_tab["file_ids"].values
        
    def search(self, query: str, topn: int=5, method: str="dense", **kargs) -> List[BaseNode]:
        """
        should be called after await, i.e. be called as <search_resaults = await search(...)>
        """
        if 'collection' in kargs:
            del kargs['collection']
        return self.qdrant_index.search(self.knowledge_id, query, topn, method, **kargs)
    
    def search_beta(self, query: str, topn: int=5, method: str="dense", **kargs) -> List[BaseNode]:
        """
        should be called after await, i.e. be called as <search_resaults = await search(...)>
        """
        if 'collection' in kargs:
            del kargs['collection']
        return self.qdrant_index.search_beta(self.knowledge_id, query, topn, method, **kargs)

    def close(self):
        """Release resources."""
        try:
            self.qdrant_index.close()  
        except Exception as e:
            logger.error(e)            
            pass
        
class Knowledge_Managment:
    @classmethod
    async def index(cls, kb_config_id: str, kb_name: str, embedding_model_name: str, 
                    embedding_model_path: str, qdrant_path: str, text_chunks_save_path: str,
                    knowledge_id: str, file_paths: List[str], embedding_model: BaseEmbedding, 
                    chunk_size: int, chunk_overlap: int, other_settings: Dict[str, Any],
                    knowledge_stat_tab: pd.DataFrame) -> pd.DataFrame:
        """
        side-effect: save index-structure on disk
        """
        # 检查并删除 .lock 文件（todo）
        lock_file_path = os.path.join(qdrant_path, '.lock')
        if os.path.exists(lock_file_path):
            logger.info(f"Removing .lock file at: {lock_file_path}")
            os.remove(lock_file_path)
        
        qdrant_index = QdrantIndex(url=qdrant_path, encoder=embedding_model)
        error_files = []
        empty_files = []
        n_file=0
        for i, file_path in enumerate(tqdm(file_paths, desc="Processing files")):
            file_tpye = file_path.split(".")[-1]
            try:
                # Check for empty file
                if os.path.getsize(file_path) == 0:
                    logger.warning(f"Empty file detected: {file_path}")
                    empty_files.append(file_path)
                    continue

                # TODO: install and call unoconv properly
                if file_tpye == "doc":
                    doc_to_docx(doc_file=file_path, docx_file=file_path + "x")
                    file_tpye = "docx"
                    file_path = file_path + "x"

                # 判断用的是哪一个模型 TODO: 微服务支持
                is_using_visrag = False
                if 'http' in embedding_model_path:
                    if "VisRAG_Ret" in get_embedding_types(embedding_model_path.replace("embed", "infos")):
                        is_using_visrag = True
                else:
                    config = AutoConfig.from_pretrained(embedding_model_path, trust_remote_code=True)
                    if "VisRAG_Ret" in config.architectures:
                        is_using_visrag = True

                logger.info(f"is_using_visrag: {is_using_visrag}")

                if is_using_visrag:
                    await vis_doc_index(
                        qdrant_index=qdrant_index,
                        knowledge_id=knowledge_id,
                        file_path=file_path,
                        nth_file=n_file,
                        file_tpye=file_tpye,
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap,
                        text_chunks_save_path=text_chunks_save_path,
                    )
                else:
                    await doc_index(
                        qdrant_index=qdrant_index,
                        knowledge_id=knowledge_id,
                        file_path=file_path,
                        nth_file=n_file,
                        file_tpye=file_tpye,
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap,
                        text_chunks_save_path=text_chunks_save_path,
                        times = i
                    )   
                n_file += 1
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                error_files.append(file_path)
                
        df = pd.DataFrame([{
                            "kb_config_id": kb_config_id,
                            "knowledge_base_id": knowledge_id,
                            "qdrant_path": qdrant_path,
                            "knowledge_base_name": kb_name,
                            "file_ids": file_paths,
                            "embedding_model_name": embedding_model_name,
                            "embedding_model_path": embedding_model_path,
                            "chunk_size": chunk_size,
                            "overlap": chunk_overlap,
                            "others": other_settings,
                        }])
        
        if empty_files:
            logger.warning(f"Empty files detected: {empty_files}")
        if error_files:
            logger.warning(f"Error files detected: {error_files}")
            
        logger.info(f"Updated knowledge_stat_tab:\n{df}")

        return pd.concat([knowledge_stat_tab, df], ignore_index=True)


    @classmethod
    def get_searcher(cls, knowledge_id: List[str], embedding_model: BaseEmbedding, knowledge_stat_tab_path: str) -> QdrantIndexSearchWarper:
        """
        dependence: file@knowledge_stat_tab_path exists
        """
        if not os.path.exists(knowledge_stat_tab_path):
            raise FileNotFoundError(f"File not found: {knowledge_stat_tab_path}")

        _, ext = os.path.splitext(knowledge_stat_tab_path)
        logger.info(f"knowledge_stat_tab_path: {knowledge_stat_tab_path}")
        if ext == '.csv':
            knowledge_stat_tab = pd.read_csv(knowledge_stat_tab_path)
        elif ext == '.json':
            knowledge_stat_tab = pd.read_json(knowledge_stat_tab_path, orient='records', lines=True)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
 
        qdrant_path = knowledge_stat_tab.loc[knowledge_stat_tab["knowledge_base_id"] == knowledge_id[0]]["qdrant_path"].iat[0]
        logger.info(f"qdrant_path: {qdrant_path}")  
        filtered_tab = knowledge_stat_tab.loc[knowledge_stat_tab["knowledge_base_id"].isin(knowledge_id)]
        if filtered_tab.empty:
            raise ValueError(f"No matching knowledge_base_id found for any of the provided IDs: {knowledge_id}")
        qdrant_path = filtered_tab["qdrant_path"].iat[0]
        # 检查并删除 .lock 文件（todo）
        lock_file_path = os.path.join(qdrant_path, '.lock')
        if os.path.exists(lock_file_path):
            logger.info(f"Removing .lock file at: {lock_file_path}")
            os.remove(lock_file_path)
        return QdrantIndexSearchWarper(embedding_model, knowledge_id, qdrant_path, knowledge_stat_tab_path)
