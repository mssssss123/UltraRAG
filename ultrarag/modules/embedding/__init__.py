from .base import *
from .bge_embedding import *
from .minicpm_embedding import MiniCPMEmbClient, MiniCPMEmbServer, BGEM3FlagModel
from .visrag_embedding import VisNetClient, VisRAGNetServer
from .client import EmbeddingClient
from .server import load_model, EmbeddingServer
from .models import model_mapping
all_embedding = dict(
    bgem3=MiniCPMEmbServer,
    bge_large=BGEServer,
    visrag=VisRAGNetServer,
)
