from .base import *
from .bge_embedding import *
from .bgem3_embedding import BGEM3Client, BGEM3Server, BGEM3FlagModel
from .visrag_embedding import VisNetClient, VisRAGNetServer
from .client import EmbeddingClient
from .server import load_model, EmbeddingServer
from .models import model_mapping
all_embedding = dict(
    bgem3=BGEM3Server,
    bge_large=BGEServer,
    visrag=VisRAGNetServer,
)
