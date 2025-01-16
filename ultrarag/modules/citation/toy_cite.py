from typing import Any, List
import jieba
import asyncio
from .base import BaseCite
from loguru import logger

MARKDOWN_ENDS = \
"""
<style>
#footnotes {
    display: none
}
</style>
"""

class ToyCite(BaseCite):

    async def arun(self, repsponse: Any, reference: List[Any], ths: float=0.7):
        index = [set(jieba.cut(ref.content, cut_all=True)) for ref in reference]
        # logger.info(f"cite info:\n{index}")

        stream_cache = ""
        async for reps in repsponse:
            stream_cache += reps

            if "\n\n" in stream_cache:
                stream_token = set(jieba.cut(stream_cache, cut_all=True))
                repeat_rate = [len(stream_token & token) / len(stream_token) for token in index]
                where_repeat = [pos for pos, val in enumerate(repeat_rate) if val > ths]
                stream_cache = ""
                yield "".join(f"[^{i+1}]" for i in where_repeat)
            yield reps

        if stream_cache:
            stream_token = set(jieba.cut(stream_cache, cut_all=True))
            repeat_rate = [len(stream_token & token) / len(stream_token) for token in index]
            where_repeat = [pos for pos, val in enumerate(repeat_rate) if val > ths]
            stream_cache = ""
            yield "".join(f"[^{i+1}]" for i in where_repeat) + "\n\n"
        
        for idx, ref in enumerate(reference):
            if hasattr(ref, 'url'):
                yield f"[^{idx+1}]:[引用{idx+1}]({ref.url})\n"
            else:
                yield f"[^{idx+1}]:[引用{idx+1}](http://www.baidu.com/)\n"

        yield MARKDOWN_ENDS