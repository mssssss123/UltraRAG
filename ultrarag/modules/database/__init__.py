import warnings
import importlib.util
from ultrarag.modules.database.base import *

try: 
    from ultrarag.modules.database.milvus import MilvusIndex
except:
    warnings.warn("failed to load MilvusIndex beacause not available qdrant_client, ignored it if you do not need it")

try: 
    from ultrarag.modules.database.qdrant import QdrantIndex
except:
    warnings.warn("failed to load QdrantIndex beacause not available qdrant_client, ignored it if you do not need it")


if importlib.util.find_spec("elasticsearch"):
    from ultrarag.modules.database.elasticsearch import ESIndex