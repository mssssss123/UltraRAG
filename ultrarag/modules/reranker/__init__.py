from .base import *
from .bce_reranker import BCERerankClient, BCERerankServer
from .bge_reranker import BGERerankClient, BGERerankServer

all_reranker = {
    "bce_reranker": BCERerankServer,
    "bge_reranker": BGERerankServer
}
