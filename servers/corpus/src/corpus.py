import json
import os
from pathlib import Path
from typing import Dict, Optional, Union, Any
from tqdm import tqdm
import ast


from ultrarag.server import UltraRAG_MCP_Server

app = UltraRAG_MCP_Server("corpus")


def _load_jsonl(file_path):
    documents = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            documents.append(json.loads(line))
    return documents

def _save_jsonl(documents, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        for doc in documents:
            f.write(json.dumps(doc) + "\n")


@app.tool(output="file_path->raw_data")
def parse_documents(
    file_path: Union[str, Path]
) -> Dict[str, str]:

    try:
        from llama_index.core import SimpleDirectoryReader
    except ImportError:
        raise ImportError(
            "Missing optional dependency 'llama-index-readers-file'. "
            "Please install it with: pip install llama-index-readers-file"
        )

    file_path = Path(file_path) if not isinstance(file_path, Path) else file_path
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = file_path.suffix.lower()
    if ext in [".pdf", ".docx", ".txt", ".md"]:
        reader = SimpleDirectoryReader(input_files=[file_path])
        documents = reader.load_data()
        raw_data = "\n".join([d.text for d in documents])
    else:
        raise ValueError(
            f"Unsupported file format: {file_path.suffix}. "
            "Currently supported: .docx, .txt, .pdf, .md. "
            "Please convert your file to a supported format."
        )

    return {"raw_data": raw_data}

@app.tool(output="pdf_file_path,mineru_dir,mineru_extra_params->None")
async def mineru_parse(
    pdf_file_path: str,
    mineru_dir: str,
    mineru_extra_params: Optional[Dict[str, Any]] = None,                    
):
    import asyncio
    import shutil

    if shutil.which("mineru") is None:
        raise ToolError("`mineru` executable not found. Please install it or add it to PATH.")

    if not pdf_file_path:
        raise ToolError("`pdf_file_path` cannot be empty.")

    pdf_path = os.path.abspath(pdf_file_path)
    if not os.path.exists(pdf_path):
        raise ToolError(f"PDF file does not exist: {pdf_path}")
    if not pdf_path.lower().endswith(".pdf"):
        raise ToolError(f"Only .pdf files are supported: {pdf_path}")

    output_path = os.path.abspath(mineru_dir)
    os.makedirs(output_path, exist_ok=True)

    cmd = ["mineru", "-p", pdf_path, "-o", mineru_dir]

    if mineru_extra_params:
        if not isinstance(mineru_extra_params, dict):
            raise ToolError("`mineru_extra_params` must be a dict, e.g. {'source': 'modelscope'}.")

        for k in sorted(mineru_extra_params.keys()):
            v = mineru_extra_params[k]
            cmd.append(f"--{k}")
            if v is not None and v != "":
                cmd.append(str(v))  


    try:
        app.logger.info("Starting mineru command: %s", " ".join(cmd))
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        assert proc.stdout is not None
        async for line in proc.stdout:
            app.logger.info(line.decode("utf-8", errors="replace").rstrip())

        returncode = await proc.wait()
        if returncode != 0:
            raise ToolError(f"mineru exited with non-zero code: {returncode}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Unexpected error while running mineru: {e}")




@app.tool(
    output="raw_chunk_path,chunk_backend_configs,chunk_backend,chunk_path,use_title->None"
)
async def chunk_documents(
    raw_chunk_path: str,
    chunk_backend_configs: Dict[str, Any],
    chunk_backend: str = "token",
    chunk_path: Optional[str] = None,
    use_title: bool = True,
) -> None:

    try:
        import chonkie
    except ImportError:
        raise ImportError("Please install 'chonkie' via pip to use chunk_documents.")

    if chunk_path is None:
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(current_file))
        output_dir = os.path.join(project_root, "output", "corpus")
        chunk_path = os.path.join(output_dir, "chunks.jsonl")
    else:
        chunk_path = str(chunk_path)
        output_dir = os.path.dirname(chunk_path)
    os.makedirs(output_dir, exist_ok=True)

    documents = _load_jsonl(raw_chunk_path)

    cfg = (chunk_backend_configs.get(chunk_backend) or {}).copy()
    if chunk_backend == "token":
        from chonkie import TokenChunker
        import tiktoken
        
        tokenizer_name = cfg.get("tokenizer_or_token_counter")
        if tokenizer_name not in ['word','character']:
            tokenizer = tiktoken.get_encoding(tokenizer_name)
        else:
            tokenizer = tokenizer_name  
        chunk_size = cfg.get("chunk_size")
        chunk_overlap = cfg.get("chunk_overlap")
        
        chunker = TokenChunker(
            tokenizer=tokenizer, 
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    elif chunk_backend == "sentence":
        from chonkie import SentenceChunker
        import tiktoken
        
        tokenizer_name = cfg.get("tokenizer_or_token_counter")
        if tokenizer_name not in ['word','character']:
            tokenizer = tiktoken.get_encoding(tokenizer_name)
        else:
            tokenizer = tokenizer_name  
        chunk_size = cfg.get("chunk_size")
        chunk_overlap = cfg.get("chunk_overlap")
        min_sentences_per_chunk = cfg.get("min_sentences_per_chunk")
        delim = cfg.get("delim")
        delim = ast.literal_eval(delim)
        chunker = SentenceChunker(
            tokenizer_or_token_counter=tokenizer, 
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,               
            min_sentences_per_chunk=min_sentences_per_chunk,
            delim=delim 
        )
    elif chunk_backend == "recursive":
        from chonkie import RecursiveChunker, RecursiveRules
        import tiktoken
        
        tokenizer_name = cfg.get("tokenizer_or_token_counter")
        if tokenizer_name not in ['word','character']:
            tokenizer = tiktoken.get_encoding(tokenizer_name)
        else:
            tokenizer = tokenizer_name  
        chunk_size = cfg.get("chunk_size")
        min_characters_per_chunk = cfg.get("min_characters_per_chunk")
        chunker = RecursiveChunker(
            tokenizer_or_token_counter=tokenizer,
            chunk_size=chunk_size,
            rules=RecursiveRules(),
            min_characters_per_chunk=min_characters_per_chunk,
        )
    else:
        raise ValueError(
            f"Invalid chunking method: {chunk_backend}. Supported: token, sentence, recursive."
        )

    chunked_documents = []
    current_chunk_id = 0
    for doc in tqdm(documents, desc=f"Chunking ({chunk_backend})", unit="doc"):
        doc_id = doc.get("id") or ""  
        title = (doc.get("title") or "").strip()  
        text = (doc.get("contents") or "").strip()

        if not text:
            app.logger.info(f"[WARN] doc_id={doc_id} has no contents, skipped.")
            continue
        try:
            chunks = chunker.chunk(text)
        except Exception as e:
            raise RuntimeError(f"fail chunked(doc_id={doc_id}): {e}")

        for chunk in chunks:
            if use_title:
                contents = title + "\n" + chunk.text
            else:
                contents = chunk.text
            meta_chunk = {
                "id": current_chunk_id,
                "doc_id": doc_id,
                "title": title,
                "contents": contents.strip(),
            }
            chunked_documents.append(meta_chunk)
            current_chunk_id += 1



    _save_jsonl(chunked_documents, chunk_path)




if __name__ == "__main__":
    app.run(transport="stdio")
