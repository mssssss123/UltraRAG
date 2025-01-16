import subprocess
import json
import re
import fitz
import jsonlines
from PIL import Image
from pathlib import Path
from ultrarag.common.utils import get_image_md5
# TODO
use_stanza = False
if use_stanza:
    import stanza

from llama_index.core import SimpleDirectoryReader

from ultrarag.modules.database import QdrantIndex
from loguru import logger


FILE_TPYE_FOR_SimpleDirectoryReader = ["txt", "pdf", "docx", "pptx", "ppt", "md"]


class LocalSentenceSplitter:
    def __init__(self, chunk_size, chunk_overlap) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        if use_stanza:
            self.nlp = stanza.Pipeline(lang='zh', processors='tokenize')

    def _zng(self, paragraph):
        if use_stanza:
            return [s.text for s in self.nlp(paragraph).sentences]
        else:
            return [sent for sent in re.split(u'(！|？|。|\\n)', paragraph, flags=re.U)]

    def split_text(self, segment):
        chunks, chunk_now, size_now = [], [], 0
        no_left = False
        for s in self._zng(segment):
            no_left = False
            chunk_now.append(s)
            size_now += len(s)
            if size_now > self.chunk_size:
                chunk = "".join(chunk_now)
                chunk_now, size_now = self._get_overlap(chunk_now)
                chunks.append(chunk)
                no_left = True

        if no_left == False:
            chunks.append("".join(chunk_now))
        return chunks

    def _get_overlap(self, chunk):
        rchunk = chunk[:]
        rchunk.reverse()
        size_now, overlap = 0, []
        for s in rchunk[:-1]:
            overlap.append(s)
            size_now += len(s)
            if size_now > self.chunk_overlap:
                break
        overlap.reverse()
        return overlap, size_now


def doc_to_docx(doc_file, docx_file):
    subprocess.run(['unoconv', '-f', 'docx', '-o', docx_file, doc_file], 
                   env={'PYTHONPATH': "/usr/bin/python"})


def file2text(file_tpye, file_path, text_splitter):
    if file_tpye in FILE_TPYE_FOR_SimpleDirectoryReader:
        reader = SimpleDirectoryReader(input_files=[file_path])
        text_chunks = text_splitter.split_text("\n".join([d.text for d in reader.load_data()]))
    else:
        print(f"file_tpye not supported: [{file_tpye}]")
    return text_chunks


def file2data(session_id, file_tpye, file_path, nth_file, text_splitter):
    text_chunks = file2text(file_tpye, file_path, text_splitter)
    knowledge_id = [f"{session_id}_{nth_file}" for _ in range(len(text_chunks))]
    knowledge_name = knowledge_id[:]
    file_id = [nth_file for _ in range(len(text_chunks))]
    segment_id = [i for i in range(len(text_chunks))]
    full_title = [f"" for _ in range(len(text_chunks))]
    content = text_chunks[:]
    span, start_index, end_index = get_spans(text_chunks)
    return ([
        {
            "knowledge_id": knowledge_id[i],
            "knowledge_name": knowledge_name[i],
            "file_id": file_id[i],
            "segment_id": segment_id[i],
            "full_title": full_title[i],
            "content": content[i],
            "span": span[i],
            "start_index": start_index[i],
            "end_index": end_index[i],
        } for i in range(len(text_chunks))
    ],
    text_chunks)


def get_spans(text_chunks):
    span, start_index, end_index = [], [-len(text_chunks[0])], []
    for c in text_chunks:
        span.append(len(c))
        start_index.append(start_index[-1] + len(c))
        end_index.append(start_index[-1] + len(c))
    return span, start_index[1:], end_index


async def doc_index(
        qdrant_index: QdrantIndex,
        knowledge_id,
        file_path,
        nth_file,
        file_tpye,
        chunk_size,
        chunk_overlap,
        text_chunks_save_path,
        times,
        ):
    # NOTE: if the file name end with jsonl, the file will be considered as chunked file, without extra chunking 
    if file_path.rstrip().endswith('.jsonl'):
        with jsonlines.open(file_path, "r") as fr:
            chunked_context = list(fr)
        # NOTE: here performs merge file title and content
        contents = [ctx['index'] + ': ' + ctx['content'] for ctx in chunked_context]

        # save chunks
        with jsonlines.open(text_chunks_save_path, "w") as fw:
            fw.write(contents)

        if knowledge_id not in qdrant_index.get_collections():
            await qdrant_index.create(collection_name=knowledge_id, index_type=method)
        
        await qdrant_index.insert(
            knowledge_id, 
            chunked_context, 
            func=lambda x: x['index'] + ": " + x["content"], 
            method=method
        )
        return 
    
    text_splitter=LocalSentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap)
    payloads, text_chunks = file2data(knowledge_id, file_tpye, file_path, nth_file, text_splitter)

    if times == 0:
        with open(text_chunks_save_path, "w", encoding="utf8") as fout:
            fout.write(json.dumps(text_chunks, ensure_ascii=False) + "\n")
    else:
        with open(text_chunks_save_path, "a", encoding="utf8") as fout:
            fout.write(json.dumps(text_chunks, ensure_ascii=False) + "\n")
    # todo 有的模型没有sparse
    method = "dense"
    if nth_file == 0:
        await qdrant_index.create(collection_name=knowledge_id, index_type=method)
    await qdrant_index.insert(knowledge_id, payloads, func=lambda x: x["content"], method=method)


async def vis_doc_index(
        qdrant_index: QdrantIndex,
        knowledge_id,
        file_path,
        nth_file,
        file_tpye,
        chunk_size,
        chunk_overlap,
        text_chunks_save_path,
        ):
    docs = fitz.open(file_path)
    collection = Path(file_path).stem
    images_path_list = []

    Path(text_chunks_save_path).mkdir(parents=True, exist_ok=True)
    
    # save page images
    for idx, page in enumerate(docs):
        pix = page.get_pixmap(dpi=200)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        cache_image_path = Path(text_chunks_save_path) / f"{collection}-{get_image_md5(image.tobytes())}.png"
        image.save(cache_image_path.as_posix())
        images_path_list.append(cache_image_path.as_posix())

    if nth_file == 0:
        await qdrant_index.create(collection_name=knowledge_id, dimension=2304)
    # insert the data into the database
    await qdrant_index.insert(knowledge_id, [dict(content=url) for url in images_path_list], func=lambda x: x['content'])
