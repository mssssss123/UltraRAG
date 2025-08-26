import json
import os
from pathlib import Path
from typing import Dict, Optional, Union

from ultrarag.server import UltraRAG_MCP_Server

app = UltraRAG_MCP_Server("corpus")


@app.tool(output="file_path->raw_data")
def parse_documents(file_path: Union[str, Path]) -> Dict[str, str]:

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


@app.tool(
    output="chunk_strategy,chunk_size,raw_data,output_path,tokenizer_name_or_path->status"
)
async def chunk_documents(
    chunk_strategy: str,
    chunk_size: int,
    raw_data: str,
    output_path: Optional[str] = None,
    tokenizer_name_or_path: Optional[str] = None,
) -> Dict[str, str]:

    try:
        import chonkie
    except ImportError:
        raise ImportError("Please install 'chonkie' via pip to use chunk_documents.")

    if output_path is None:
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(current_file))
        output_dir = os.path.join(project_root, "output", "corpus")
        output_path = os.path.join(output_dir, "chunks.jsonl")
    else:
        output_path = str(output_path)
        output_dir = os.path.dirname(output_path)

    os.makedirs(output_dir, exist_ok=True)

    if chunk_strategy == "token":
        chunker = chonkie.TokenChunker(
            tokenizer=tokenizer_name_or_path, chunk_size=chunk_size
        )
    elif chunk_strategy == "word":
        chunker = chonkie.TokenChunker(tokenizer="word", chunk_size=chunk_size)
    elif chunk_strategy == "sentence":
        chunker = chonkie.SentenceChunker(
            tokenizer_or_token_counter=tokenizer_name_or_path, chunk_size=chunk_size
        )
    elif chunk_strategy == "recursive":
        chunker = chonkie.RecursiveChunker(
            tokenizer_or_token_counter=tokenizer_name_or_path,
            chunk_size=chunk_size,
            min_characters_per_chunk=1,
        )
    else:
        raise ValueError(
            f"Invalid chunking method: {chunk_strategy}. Supported: token, word, sentence, recursive"
        )

    chunks = chunker(raw_data)

    chunked_documents = [
        {"id": i, "contents": chunk.text} for i, chunk in enumerate(chunks)
    ]

    with open(output_path, "w", encoding="utf-8") as f:
        for doc in chunked_documents:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    return {"status": "save chunks successful"}


if __name__ == "__main__":
    app.run(transport="stdio")
