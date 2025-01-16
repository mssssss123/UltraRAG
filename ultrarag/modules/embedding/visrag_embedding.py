import json
import torch
import aiohttp
import traceback
from PIL import Image
from pathlib import Path
import torch.nn.functional as F
from typing import List, Callable, Dict, Union, Optional, Any
from transformers import AutoTokenizer, AutoModel
from .base import BaseEmbedding
from loguru import logger
import uuid
import asyncio
from contextlib import asynccontextmanager


class VisNetClient(BaseEmbedding):
    def __init__(self, url_or_path: str, timeout: int = 30) -> None:
        super().__init__()
        self._url = url_or_path
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    @asynccontextmanager
    async def _get_client_session(self):
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            yield session

    async def query_encode(self, query: str) -> List[float]:
        """将文本转换为向量表示。

        Args:
            query (str): 输入的文本字符串
                示例: "今天天气真好"

        Returns:
            Dict: 包含向量的字典
                示例: {"dense_embed": [0.1, 0.2, ..., 0.8]}
        """
        if not isinstance(query, str):
            raise TypeError("Query must be a string")  # 使用更具体的TypeError
            
        try:
            form_data = aiohttp.FormData()
            form_data.add_field('data', json.dumps([query]), content_type='application/json')
            
            async with self._get_client_session() as session:
                async with session.post(self._url, data=form_data) as response:
                    response.raise_for_status()  # 添加这行来处理非200状态码
                    data = await response.json()
                    return data[0]
        except aiohttp.ClientError as e:  # 更具体的异常处理
            logger.error(f"Network error during query encoding: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during query encoding: {str(e)}")
            raise

    async def document_encode(
        self, 
        document: List[str], 
        callback: Optional[Callable[[float, str], None]] = None
    ) -> List[Dict[str, List[float]]]:
        """将图片文件路径列表转换为向量表示。

        Args:
            document (List[str]): 图片文件路径列表
                示例: ["/path/to/image1.jpg", "/path/to/image2.jpg"]
            callback (Optional[Callable]): 回调函数,用于监控处理进度
            
        Returns:
            List[Dict]: 包含向量的字典列表
                示例: [
                    {"dense_embed": [0.1, 0.2, ..., 0.8]},
                    {"dense_embed": [0.2, 0.3, ..., 0.9]} 
                ]
        """
        try:
            # Validate input paths
            for path in document:
                if not Path(path).exists():
                    raise ValueError(f"Image path does not exist: {path}")

            form_data = aiohttp.FormData()
            form_data.add_field('data', json.dumps(document), content_type='application/json')
            
            # Add image files to form data
            for path in document:
                file_id = str(uuid.uuid4())
                # with open(path, "rb") as f:   
                form_data.add_field(
                    file_id,
                    open(path, "rb"),
                    filename=path,
                    content_type='image/jpeg'
                )
            async with self._get_client_session() as session:
                async with session.post(self._url, data=form_data) as response:
                    if response.status == 200:
                        json_data = await response.json()
                        return json_data
                    else:
                        error_text = await response.text()
                        logger.error(f"Request failed with status: {response.status}, content: {error_text}")
                        raise RuntimeError(f"API request failed with status {response.status}")
        except Exception as e:
            logger.error(f"Error during document encoding: {str(e)}")
            raise

    def encode(self, *args, **kwargs):
        raise NotImplementedError("VisRAGNetServer does not support encode method")
    

class VisRAGNetServer(BaseEmbedding):
    def __init__(
        self, 
        url_or_path: str, 
        device: Optional[str] = None,
        batch_size: int = 2
    ) -> None:
        """
        Initialize the VisRAGNetServer.
        
        Args:
            model_path: Path to the model
            device: Device to run the model on ('cuda', 'cpu', etc.)
            batch_size: Default batch size for processing
        """
        super().__init__()
        self._validate_model_path(url_or_path)
        self._batch_size = batch_size
        self._device = self._determine_device(device)
        
        self._tokenizer = AutoTokenizer.from_pretrained(url_or_path, trust_remote_code=True)
        self._model = self._load_model(url_or_path)
        self._model.eval()

    @staticmethod
    def _validate_model_path(model_path: str) -> None:
        if not Path(model_path).exists():
            raise ValueError(f"Model path does not exist: {model_path}")

    def _determine_device(self, device: Optional[str]) -> str:
        if isinstance(device, list): device = device[0]
        
        if device and device.startswith("cuda") and not torch.cuda.is_available():
            logger.warning("CUDA requested but not available. Falling back to CPU.")
            return "cpu"
        if device is None:
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device

    def _load_model(self, model_path: str) -> AutoModel:
        try:
            if self._device.startswith("cuda"):
                return AutoModel.from_pretrained(
                    model_path,
                    trust_remote_code=True,
                    torch_dtype=torch.bfloat16,
                    device_map=self._device
                ).eval()
            return AutoModel.from_pretrained(model_path, trust_remote_code=True)
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise

    @torch.no_grad()
    async def query_encode(
        self, 
        queries: Union[str, List[str]]
    ) -> Union[Dict[str, List[float]], List[Dict[str, List[float]]]]:
        """Convert text to vector representation.

        Args:
            queries (Union[str, List[str]]): Input text string or list of strings
                Example: "The weather is nice today" or ["text1", "text2"]

        Returns:
            Union[Dict[str, List[float]], List[Dict[str, List[float]]]]: Dictionary containing vector representation
                Example for single input: {"dense_embed": [0.1, 0.2, ..., 0.8]}
                Example for list input: [{"dense_embed": [...]}, {"dense_embed": [...]}]
        """
        new_queries = queries
        if isinstance(queries, str):
            new_queries = [queries]

        if any(isinstance(item, Image.Image) for item in queries):
            raise ValueError("VisRAGNetServer does not support image input")
        
        INSTRUCTION = "Represent this query for retrieving relevant documents: "
        new_queries = [INSTRUCTION + query for query in new_queries]
        try:
            outputs = self._model(
                text=new_queries, 
                image=[None], 
                tokenizer=self._tokenizer
            )
            embeddings = self._process_outputs(outputs)
            if isinstance(queries, str):
                return {"dense_embed": embeddings[0]}
            else:
                return [{"dense_embed": item} for item in embeddings]
        except Exception as e:
            logger.error(traceback.format_exc())
            raise

    @staticmethod
    async def _load_images(paths_or_images: List[Any]) -> List[Image.Image]:
        """Asynchronously load images."""
        def load_single_image(path_or_image: Any) -> Image.Image:
            return Image.open(path_or_image) if isinstance(path_or_image, str) else path_or_image

        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(None, load_single_image, path_or_image) 
            for path_or_image in paths_or_images
        ]
        return await asyncio.gather(*tasks)


    @staticmethod
    def _process_outputs(outputs: Any) -> List[List[float]]:
        """Process model outputs to get normalized embeddings."""
        attention_mask = outputs.attention_mask
        hidden = outputs.last_hidden_state
        reps = weighted_mean_pooling(hidden, attention_mask)
        return F.normalize(reps, p=2, dim=1).detach().cpu().numpy().tolist()


    @torch.no_grad()
    async def document_encode(
        self, 
        document: List[Union[str, Image.Image]], 
        batch_size: Optional[int] = 1,
        callback: Optional[Callable[[float, str], None]] = None
    ) -> List[Dict[str, List[float]]]:
        """Convert a list of images or image paths to vector representations.

        Args:
            document (List[Union[str, Image.Image]]): List of image paths or PIL Image objects
                Example: ["/path/to/image1.jpg", <PIL.Image.Image object>]
            batch_size (Optional[int]): Batch size for processing, defaults to None
            callback (Optional[Callable]): Callback function to monitor progress
            
        Returns:
            List[Dict]: List of dictionaries containing vector representations
                Example: [
                    {"dense_embed": [0.1, 0.2, ..., 0.8]},
                    {"dense_embed": [0.2, 0.3, ..., 0.9]}
                ]
        """
        if not document: return []
        
        # Validate input paths
        for item in document:
            if isinstance(item, str) and not Path(item).exists():
                raise ValueError(f"Image path does not exist: {item}")

        batch_size = batch_size or self._batch_size
        try:
            # Load images asynchronously
            images = await self._load_images(document)
            embeddings = []

            for pos in range(0, len(images), batch_size):
                batch_data = images[pos: pos + batch_size]
                outputs = self._model(
                    text=[""] * len(batch_data),
                    image=batch_data,
                    tokenizer=self._tokenizer
                )
                batch_embeddings = self._process_outputs(outputs)
                embeddings.extend(batch_embeddings)

                if callback:
                    callback(pos / len(images), "image embedding")

            return [{"dense_embed": item} for item in embeddings]
        except Exception as e:
            logger.error(f"Error during document encoding: {str(e)}")
            raise


def weighted_mean_pooling(hidden, attention_mask):
    attention_mask_ = attention_mask * attention_mask.cumsum(dim=1)
    s = torch.sum(hidden * attention_mask_.unsqueeze(-1).float(), dim=1)
    d = attention_mask_.sum(dim=1, keepdim=True).float()
    reps = s / d
    return reps
