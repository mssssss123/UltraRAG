from .bge_embedding import BGEServer
from .minicpm_embedding import MiniCPMEmbServer
from .visrag_embedding import VisRAGNetServer

model_mapping = dict(
    BertModel=BGEServer,
    XLMRobertaModel=MiniCPMEmbServer,
    MiniCPMModel=MiniCPMEmbServer,
    VisRAG_Ret=VisRAGNetServer,
) 