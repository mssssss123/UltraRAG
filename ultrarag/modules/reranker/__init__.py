from .base import *
from .bce_reranker import BCERerankClient, BCERerankServer
from .reranker import RerankerClient, RerankerServer

all_reranker = {
    "bce_reranker": BCERerankServer,
    "bge_reranker": RerankerServer,
    "minicpm_reranker": RerankerServer,
}
