import json
import os
from pathlib import Path
from typing import Dict, Optional, Union, Any, List, Iterable
from tqdm import tqdm
import ast
from fastmcp.exceptions import NotFoundError, ToolError, ValidationError
import asyncio
import shutil
from PIL import Image

from ultrarag.server import UltraRAG_MCP_Server

app = UltraRAG_MCP_Server("corpus")


def _save_jsonl(rows: Iterable[Dict[str, Any]], file_path: str) -> None:
    out_dir = os.path.dirname(os.path.abspath(file_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(file_path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def _load_jsonl(file_path: str) -> List[Dict[str, Any]]:
    docs = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            docs.append(json.loads(line))
    return docs


@app.tool(
    output="parse_file_path,text_corpus_save_path->None"
)
async def build_text_corpus(
    parse_file_path: str,          
    text_corpus_save_path: str,     
) -> None:
    TEXT_EXTS  = {".txt", ".md"}
    PMLIKE_EXT = {".pdf", ".xps", ".oxps", ".epub", ".mobi", ".fb2"}

    in_path = os.path.abspath(parse_file_path)
    if not os.path.exists(in_path):
        raise ToolError(f"Input path not found: {in_path}")

    rows: List[Dict[str, Any]] = []

    def process_one_file(fp: str) -> None:
        ext = os.path.splitext(fp)[1].lower()
        stem = os.path.splitext(os.path.basename(fp))[0]  

        if ext in TEXT_EXTS:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    text = f.read()
            except UnicodeDecodeError:
                with open(fp, "r", encoding="latin-1", errors="ignore") as f:
                    text = f.read()
            text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
            rows.append({"id": stem, "title": stem, "contents": text})

        elif ext in PMLIKE_EXT:
            try:
                import pymupdf
            except ImportError:
                raise ToolError("pymupdf not installed. Please `pip install pymupdf`.")

            try:
                doc = pymupdf.open(fp)
            except Exception as e:
                app.logger.warning(f"Skip (open failed): {fp} | reason: {e}")
                return

            if getattr(doc, "is_encrypted", False):
                try:
                    doc.authenticate("")
                except Exception:
                    app.logger.warning(f"Skip (encrypted): {fp}")
                    return

            texts = []
            for pg in doc:
                try:
                    t = pg.get_text("text")
                except Exception:
                    t = ""
                texts.append(t.replace("\r\n", "\n").replace("\r", "\n").strip())
            merged = "\n\n".join(texts).strip()
            rows.append({"id": stem, "title": stem, "contents": merged})

        else:
            app.logger.warning(f"Unsupported file type, skip: {fp}")
            return

    if os.path.isfile(in_path):
        process_one_file(in_path)
    else:
        for dp, _, fns in os.walk(in_path):
            for fn in fns:
                process_one_file(os.path.join(dp, fn))

    out_path = os.path.abspath(text_corpus_save_path)
    _save_jsonl(rows, out_path)

    app.logger.info(
        f"Built text corpus: {out_path} "
        f"(rows={len(rows)}, from={'dir' if os.path.isdir(in_path) else 'file'}: {in_path})"
    )

@app.tool(output="parse_file_path,image_corpus_save_path->None")
async def build_image_corpus(
    parse_file_path: str,
    image_corpus_save_path: str,
) -> None:
    try:
        import pymupdf
    except ImportError:
        raise ToolError("Please install required packages: pip install pymupdf pillow")

    in_path = os.path.abspath(parse_file_path)
    if not os.path.exists(in_path):
        raise ToolError(f"Input path not found: {in_path}")

    corpus_jsonl = os.path.abspath(image_corpus_save_path)
    out_root = os.path.dirname(corpus_jsonl) or os.getcwd()
    base_img_dir = os.path.join(out_root, "image")  
    os.makedirs(base_img_dir, exist_ok=True)

    pdf_list: List[str] = []
    if os.path.isfile(in_path):
        if not in_path.lower().endswith(".pdf"):
            raise ToolError(f"Only PDF is supported here. Got: {os.path.splitext(in_path)[1]}")
        pdf_list = [in_path]
    else:
        for dp, _, fns in os.walk(in_path):
            for fn in fns:
                if fn.lower().endswith(".pdf"):
                    pdf_list.append(os.path.join(dp, fn))
        pdf_list.sort()

    if not pdf_list:
        raise ToolError(f"No PDF files found under: {in_path}")

    valid_rows: List[Dict[str, Any]] = []
    gid = 0  

    for pdf_path in pdf_list:
        stem = os.path.splitext(os.path.basename(pdf_path))[0]           
        out_img_dir = os.path.join(base_img_dir, stem)                
        os.makedirs(out_img_dir, exist_ok=True)

        try:
            doc = pymupdf.open(pdf_path)
        except Exception as e:
            app.logger.warning(f"Skip PDF (open failed): {pdf_path} | reason: {e}")
            continue

        if getattr(doc, "is_encrypted", False):
            try:
                doc.authenticate("")  
            except Exception:
                app.logger.warning(f"Skip PDF (encrypted): {pdf_path}")
                continue

        zoom = 144 / 72.0
        mat = pymupdf.Matrix(zoom, zoom)

        for i, page in enumerate(doc):
            try:
                pix = page.get_pixmap(matrix=mat, alpha=False, colorspace=pymupdf.csRGB)
            except Exception as e:
                app.logger.warning(f"Skip page {i} in {pdf_path}: render error: {e}")
                continue

            filename = f"page_{i}.jpg"
            save_path = os.path.join(out_img_dir, filename)             
            rel_path = f"image/{stem}/{filename}"                        

            try:
                pix.save(save_path, jpg_quality=90)  
            except Exception as e:
                app.logger.warning(f"Skip page {i} in {pdf_path}: save error: {e}")
                continue
            finally:
                pix = None

            try:
                with Image.open(save_path) as im:
                    im.verify()
            except Exception as e:
                app.logger.warning(f"Skip page {i} in {pdf_path}: invalid image after save: {e}")
                try:
                    os.remove(save_path)
                except OSError:
                    pass
                continue

            valid_rows.append({
                "id": gid,
                "image_id": f"{stem}/{filename}",  
                "image_path": rel_path,           
            })
            gid += 1

    _save_jsonl(valid_rows, corpus_jsonl)
    app.logger.info(
        f"Built image corpus: {corpus_jsonl} (valid images={len(valid_rows)}), "
        f"images root: {base_img_dir}, pdf_count={len(pdf_list)}"
    )

@app.tool(output="parse_file_path,mineru_dir,mineru_extra_params->None")
async def mineru_parse(
    parse_file_path: str,
    mineru_dir: str,
    mineru_extra_params: Optional[Dict[str, Any]] = None,
) -> None:

    if shutil.which("mineru") is None:
        raise ToolError("`mineru` executable not found. Please install it or add it to PATH.")

    if not parse_file_path:
        raise ToolError("`parse_file_path` cannot be empty.")

    in_path = os.path.abspath(parse_file_path)
    if not os.path.exists(in_path):
        raise ToolError(f"Input path not found: {in_path}")

    if os.path.isfile(in_path) and not in_path.lower().endswith(".pdf"):
        raise ToolError(f"Only .pdf files or directories are supported: {in_path}")

    out_root = os.path.abspath(mineru_dir)
    os.makedirs(out_root, exist_ok=True)

    extra_args: List[str] = []
    if mineru_extra_params:
        if not isinstance(mineru_extra_params, dict):
            raise ToolError("`mineru_extra_params` must be a dict, e.g. {'source': 'modelscope'}.")
        for k in sorted(mineru_extra_params.keys()):
            v = mineru_extra_params[k]
            extra_args.append(f"--{k}")
            if v is not None and v != "":
                extra_args.append(str(v))

    cmd = ["mineru", "-p", in_path, "-o", out_root] + extra_args
    app.logger.info("Starting mineru command: %s", " ".join(cmd))

    try:
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

    app.logger.info(f"mineru finished processing {in_path} into {out_root}")

def _list_images(images_dir: str) -> List[str]:
    if not os.path.isdir(images_dir):
        return []
    exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
    rels = []
    for dp, _, fns in os.walk(images_dir):
        for fn in fns:
            if os.path.splitext(fn)[1].lower() in exts:
                rel = os.path.relpath(os.path.join(dp, fn), start=images_dir)
                rels.append(rel.replace("\\", "/"))
    rels.sort()
    return rels


@app.tool(
    output="mineru_dir,parse_file_path,text_corpus_save_path,image_corpus_save_path->None"
)
async def build_mineru_corpus(
    mineru_dir: str,             
    parse_file_path: str,              
    text_corpus_save_path: str, 
    image_corpus_save_path: str,
) -> None:
    import os, shutil
    from typing import List, Dict, Any, Set
    from fastmcp.exceptions import ToolError
    from PIL import Image

    root = os.path.abspath(mineru_dir)
    if not os.path.isdir(root):
        raise ToolError(f"MinerU root not found: {root}")
    if not parse_file_path:
        raise ToolError("`parse_file_path` cannot be empty.")
    in_path = os.path.abspath(parse_file_path)
    if not os.path.exists(in_path):
        raise ToolError(f"Input path not found: {in_path}")

    stems: List[str] = []
    if os.path.isfile(in_path):
        if not in_path.lower().endswith(".pdf"):
            raise ToolError(f"Only .pdf supported for file input: {in_path}")
        stems = [os.path.splitext(os.path.basename(in_path))[0]]
    else:
        seen: Set[str] = set()
        for dp, _, fns in os.walk(in_path):
            for fn in fns:
                if fn.lower().endswith(".pdf"):
                    stem = os.path.splitext(fn)[0]
                    if stem not in seen:
                        stems.append(stem)
                        seen.add(stem)
        stems.sort()
        if not stems:
            raise ToolError(f"No PDF files found under: {in_path}")

    text_rows: List[Dict[str, Any]] = []
    image_rows: List[Dict[str, Any]] = []
    image_out = os.path.abspath(image_corpus_save_path)
    out_root_dir = os.path.dirname(image_out)
    base_out_img_dir = os.path.join(out_root_dir, "images")
    os.makedirs(base_out_img_dir, exist_ok=True)

    for stem in stems:
        auto_dir = os.path.join(root, stem, "auto")
        if not os.path.isdir(auto_dir):
            app.logger.warning(f"Auto dir not found for '{stem}': {auto_dir} (skip)")
            continue

        md_path = os.path.join(auto_dir, f"{stem}.md")
        if not os.path.isfile(md_path):
            app.logger.warning(f"Markdown not found for '{stem}': {md_path} (skip text)")
        else:
            with open(md_path, "r", encoding="utf-8") as f:
                md_text = f.read().strip()
            text_rows.append({
                "id": stem,
                "title": stem,
                "contents": md_text
            })

        images_dir = os.path.join(auto_dir, "images")
        if not os.path.isdir(images_dir):
            app.logger.info(f"No images dir for '{stem}': {images_dir} (skip images)")
            continue

        rel_list = _list_images(images_dir)  
        for idx, rel in enumerate(rel_list):
            src = os.path.join(images_dir, rel)
            dst = os.path.join(base_out_img_dir, stem, rel)  
            os.makedirs(os.path.dirname(dst), exist_ok=True)

            try:
                with Image.open(src) as im:
                    im.convert("RGB").copy()  
            except Exception as e:
                app.logger.warning(f"Skip invalid image for '{stem}': {src}, reason: {e}")
                continue

            shutil.copy2(src, dst)
            image_rows.append({
                "id": len(image_rows),  
                "image_id": f"{stem}/{os.path.basename(rel)}",  
                "image_path": f"images/{stem}/{rel}",          
            })

    text_out = os.path.abspath(text_corpus_save_path)
    _save_jsonl(text_rows, text_out)
    _save_jsonl(image_rows, image_out)

    app.logger.info(
        "Built MinerU corpus from %s | docs=%d | text_rows=%d | image_rows=%d\n"
        "Text corpus -> %s\nImage corpus -> %s (images root: %s)",
        in_path, len(stems), len(text_rows), len(image_rows),
        text_out, image_out, base_out_img_dir
    )


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
