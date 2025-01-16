from .bge_embedding import BGEServer
from .bgem3_embedding import BGEM3Server
from .visrag_embedding import VisRAGNetServer

model_mapping = dict(
    BertModel=BGEServer,
    XLMRobertaModel=BGEM3Server,
    MiniCPMModel=BGEM3Server,
    VisRAG_Ret=VisRAGNetServer,
) 