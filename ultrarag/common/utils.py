import os
import json
import time
import asyncio
import hashlib
from typing import List
from loguru import logger
from functools import wraps
import requests

def get_embedding_types(url):
    response = requests.get(url)
    logger.info(f"url: {url}, response: {response.text}")
    return json.loads(response.text)

GENERATE_PROMPTS = """您是优秀的聊天助手，根据下面文档的内容回答问题，必要时请考虑之前的对话的历史记录。

问题：{query}

之前的对话的历史记录：
-------------------------------------
{history}

相关的检索信息：
-------------------------------------
{content}

请你根据以上信息回答问题：{query}，并进行简单的回复，下面请开始输出：

"""

def load_prompt(prompt: str):
    if not os.path.isfile(prompt):
        logger.info(f"ultrarag use outdoor prompt: {prompt}")
        return prompt
    
    with open(prompt, "r", encoding="utf8") as fr:
        logger.info(f"ultrarag load prompt from {prompt}")
        return "".join(fr.readlines())


def timer_record(func):
    ''' the wappar is used to record time spend '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        src_time = time.perf_counter()
        result = func(*args, **kwargs)  # 执行被装饰的函数
        dst_time = time.perf_counter()
        logger.info(f"TimeCounter of {func.__name__}: {(dst_time - src_time)*1000.0} ms")
        return result
    return wrapper


def always_get_an_event_loop() -> asyncio.AbstractEventLoop:
    try:
        # If there is already an event loop, use it.
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # If in a sub-thread, create a new event loop.
        logger.info("Creating a new event loop in a sub-thread.")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop



def chunk_by_sentence(document: str, chunk_size: int=512, pattern="([.。？！])"):
    import re
    slices = re.split(pattern, document)
    buff, new_slieces = "", []
    for item in slices:
        if item and item not in pattern:
            new_slieces.append(buff)
            buff = item
        else:
            buff += item
    if buff: new_slieces.append(buff)
    curr, responses = "", []

    for item in new_slieces:
        curr += item
        if len(curr) > chunk_size:
            responses.append(curr)
            curr = ""
    
    if curr:
        responses.append(curr)
    return responses
        

TEMPLATE = \
'''
<details>

<summary>{title}</summary>

```json
   {context}
```

</details>
'''

def get_debug_fold(title: str, context: any):
    """Convert any data type to HTML-formatted collapsible table for display
    
    Args:
        title (str): Title of the collapsible table
        context (any): Data to display, can be dictionary, list or other serializable data
        
    Returns:
        str: HTML-formatted collapsible table containing title and data
    """
    if isinstance(context, dict) or isinstance(context, list):
        context = json.dumps(context, ensure_ascii=False, indent=4)
        
    debug_fold_style = TEMPLATE.format(title=title, context=context)
    return debug_fold_style


def get_image_md5(img_byte_array):
    md5_hash = hashlib.md5(img_byte_array).hexdigest()
    return md5_hash

FLOD_IMAGE_STYLE = '''
<details>

<summary>{title}</summary>

<style>
.modal-image {{
    cursor: pointer;
    transition: transform 0.3s ease;
}}
.modal-image:hover {{
    transform: scale(1.05);
}}
.modal {{
    display: none;
    position: fixed;
    z-index: 1000;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.9);
}}
.modal-content {{
    margin: auto;
    display: block;
    max-width: 90%;
    max-height: 90%;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}}
</style>

<div align="center">
<table style="border-spacing: 10px; border-collapse: separate;">
  <tr>
    {img_url}
  </tr>
  <tr style="text-align: center;">
    {img_name}
  </tr>
</table>
</div>

<div id="imageModal" class="modal" onclick="this.style.display='none'">
  <img class="modal-content" id="modalImage">
</div>

<script>
function showModal(imgSrc) {{
    var modal = document.getElementById('imageModal');
    var modalImg = document.getElementById('modalImage');
    modal.style.display = "block";
    modalImg.src = imgSrc;
}}
</script>

</details>
'''

def get_image_fold(title: str, context: List[str]):
    """Generate an HTML-formatted collapsible table to display images
    
    Args:
        title (str): Title of the collapsible table
        context (List[str]): List of image file paths to display
        
    Returns:
        str: HTML-formatted collapsible table containing the images with uniform styling
    """
    logger.debug(f"context: {context}")
    # 统一图片宽度和样式
    img_url = [f'<td style="padding: 5px;"><img src={url} width="300px" style="max-width: 100%;"></td>' for url in context]
    img_url = "\n\t".join(img_url)
    
    # 文字居中显示
    img_name = [f'<td style="text-align: center;">{name.split("/")[-1]}</td>' for name in context]
    img_name = "\n\t".join(img_name)
    
    return FLOD_IMAGE_STYLE.format(title=title, img_url=img_url, img_name=img_name)