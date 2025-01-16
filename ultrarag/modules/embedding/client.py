import uuid
import json, aiohttp
from pathlib import Path
from loguru import logger
from contextlib import asynccontextmanager
from typing import List, Dict, Callable, Optional, Union

from .base import BaseEmbedding

class EmbeddingClient(BaseEmbedding):
    def __init__(self, url_or_path: str, timeout: int = 30) -> None:
        self._url = url_or_path
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    @asynccontextmanager
    async def _get_client_session(self):
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            yield session


    async def query_encode(self, query: Union[str, List[str]]) -> List[float]:
        """Convert text or image input into vector embeddings.

        Args:
            query (Union[str, List[str]]): Input text string or list of strings/image paths
                Examples:
                - Text input: "How is the weather today" or ["Hello", "How are you"]

        Returns:
            Union[Dict, List[Dict]]: Dictionary or list of dictionaries containing vector embeddings
                Examples:
                - Single input: {"dense_embed": [0.1, 0.2, ..., 0.8]}
                - Multiple inputs: [
                    {"dense_embed": [0.1, 0.2, ..., 0.8]},
                    {"dense_embed": [0.2, 0.3, ..., 0.9]}
                ]
        """
        queries = [query] if isinstance(query, str) else query

        for path in queries:
            if path.lstrip().startswith('file:'):
                raise ValueError("Image path is not supported for query encoding")

        try:
            form_data = aiohttp.FormData()
            form_data.add_field('type', "query", content_type='application/json')
            form_data.add_field('data', json.dumps(queries), content_type='application/json')
            
            async with self._get_client_session() as session:
                async with session.post(self._url, data=form_data) as response:
                    if response.status == 200:
                        data = await response.json()

                        if isinstance(query, str):
                            return data[0]
                        else:
                            return data
                    else:
                        error_text = await response.text()
                        logger.error(f"Request failed with status: {response.status}, content: {error_text}")
                        raise RuntimeError(f"API request failed with status {response.status}")
        except Exception as e:
            logger.error(f"Error during query encoding: {str(e)}")
            raise


    async def document_encode(
        self, 
        document: List[str], 
        callback: Optional[Callable[[float, str], None]] = None
    ) -> List[Dict[str, List[float]]]:
        """Convert a list of text strings or image file paths into vector representations.

        Args:
            document (List[str]): List of text strings or image file paths
                Examples:
                - Text input: ["hello world", "how are you"]
                - Image input: ["file:/path/to/image1.jpg", "file:/path/to/image2.jpg"]
            callback (Optional[Callable]): Callback function to monitor progress
                
        Returns:
            List[Dict]: List of dictionaries containing vector embeddings
                Example: [
                    {"dense_embed": [0.1, 0.2, ..., 0.8]},
                    {"dense_embed": [0.2, 0.3, ..., 0.9]}
                ]
        """

        form_data = aiohttp.FormData()
        form_data.add_field('type', "document", content_type='application/json')
        form_data.add_field('data', json.dumps(document), content_type='application/json')
        
        # Add image files to form data
        for path in document:
            # if not path.lstrip().startswith('file:'):
            #     continue
            if len(path) > 128 or not Path(path).exists():
                continue
            file_id = str(uuid.uuid4())
            
            # new_path = path.lstrip().removeprefix('file:')
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