from .embedding import EmbServer
from .minicpm_embedding import MiniCPMEmbServer
from .visrag_embedding import VisRAGNetServer

model_mapping = dict(
    BertModel=EmbServer,
    XLMRobertaModel=MiniCPMEmbServer,
    MiniCPMModel=MiniCPMEmbServer,
    VisRAG_Ret=VisRAGNetServer,
) 