import json
import math
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from fastmcp.exceptions import ToolError
from jinja2 import Environment, FileSystemLoader
from ultrarag.server import UltraRAG_MCP_Server

from pageindex_core.utils import (
    add_node_text,
    add_preface_if_needed,
    convert_page_to_int,
    count_tokens,
    convert_physical_index_to_int,
    extract_json,
    load_page_corpus,
    post_processing,
    write_node_id,
)


app = UltraRAG_MCP_Server("pageindex")


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


_PROMPT_ENV = Environment(
    loader=FileSystemLoader(str(_project_root())),
    autoescape=False,
)


def _normalize_template_path(template_path: str) -> str:
    if not template_path:
        raise ToolError("template_path cannot be empty.")
    path = Path(template_path)
    if path.is_absolute():
        try:
            rel = path.resolve().relative_to(_project_root())
        except ValueError as exc:
            raise ToolError("template_path must be under project root.") from exc
        template_key = rel.as_posix()
    else:
        template_key = path.as_posix()
    if ".." in Path(template_key).parts:
        raise ToolError("template_path contains invalid '..' segments.")
    return template_key


def _render_prompt(template_path: str, **kwargs: Any) -> str:
    """Render a Jinja prompt template from a repo-relative path."""
    try:
        template_key = _normalize_template_path(template_path)
        template = _PROMPT_ENV.get_template(template_key)
    except Exception as exc:
        raise ToolError(f"Prompt template not found: {template_path}") from exc
    return template.render(**kwargs)


def _validate_path(user_path: str, must_exist: bool = True) -> Path:
    """Validate and sanitize file path to prevent path traversal attacks."""
    try:
        safe_path = Path(user_path).expanduser().resolve()
        path_str = str(safe_path)
        if ".." in str(Path(user_path)) or path_str.startswith("/etc/") or path_str.startswith("/proc/"):
            raise ValueError(f"Path traversal detected: '{user_path}'")
        if must_exist and not safe_path.exists():
            raise ValueError(f"Path not found: '{user_path}'")
        return safe_path
    except (OSError, ValueError) as exc:
        raise ValueError(str(exc)) from exc


def _resolve_path(path_str: str, must_exist: bool = True) -> Path:
    if not path_str:
        raise ValueError("Path cannot be empty.")
    path = Path(path_str)
    if not path.is_absolute():
        path = _project_root() / path
    return _validate_path(str(path), must_exist=must_exist)


def _resolve_output_path(path_str: str) -> Path:
    if not path_str:
        raise ValueError("Path cannot be empty.")
    path = Path(path_str)
    if not path.is_absolute():
        path = _project_root() / path
    return _validate_path(str(path), must_exist=False)


def _resolve_output_dir(dir_str: str) -> Path:
    base = Path(dir_str) if dir_str else Path("data/pageindex")
    if not base.is_absolute():
        base = _project_root() / base
    return base.resolve()


def _load_tree_json(tree_json_path: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    tree_path = _resolve_path(tree_json_path, must_exist=True)
    with open(tree_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    if isinstance(payload, dict) and "tree" in payload and isinstance(payload["tree"], dict):
        tree = payload["tree"]
    elif isinstance(payload, dict):
        tree = payload
    else:
        raise ToolError("Invalid tree JSON format.")

    structure = tree.get("structure")
    if not isinstance(structure, list):
        raise ToolError("Tree JSON missing 'structure' list.")
    return tree, structure


def _build_outline(
    structure: List[Dict[str, Any]],
    max_depth: int,
    max_nodes: int,
    max_outline_chars: int,
    include_summary: bool,
) -> Tuple[str, Dict[str, Dict[str, Any]]]:
    lines: List[str] = []
    node_map: Dict[str, Dict[str, Any]] = {}
    total_chars = 0
    counter = 0
    truncated = False

    def add_line(line: str) -> bool:
        nonlocal total_chars, truncated
        if max_nodes > 0 and len(lines) >= max_nodes:
            truncated = True
            return False
        if max_outline_chars > 0 and (total_chars + len(line) + 1) > max_outline_chars:
            truncated = True
            return False
        lines.append(line)
        total_chars += len(line) + 1
        return True

    def walk(node: Dict[str, Any], depth: int, path_titles: List[str]) -> None:
        nonlocal counter, truncated
        if truncated:
            return
        if max_depth > 0 and depth > max_depth:
            return

        counter += 1
        node_id = node.get("node_id") or f"node_{counter:04d}"
        title = str(node.get("title") or "").strip()
        summary = node.get("summary") or node.get("prefix_summary") or ""
        text = node.get("text") or ""
        path = path_titles + ([title] if title else [])

        line = f"{'  ' * (depth - 1)}- [{node_id}] {title}".rstrip()
        if include_summary and summary:
            summary = str(summary).strip().replace("\n", " ")
            line = f"{line} | summary: {summary}"

        if add_line(line):
            node_map[node_id] = {
                "node": node,
                "title": title,
                "summary": summary,
                "text": text,
                "depth": depth,
                "path": path,
            }
        else:
            return

        for child in node.get("nodes", []) or []:
            walk(child, depth + 1, path)

    for root in structure:
        walk(root, 1, [])
        if truncated:
            break

    outline = "\n".join(lines)
    return outline, node_map


def _format_passage(node_info: Dict[str, Any], max_passage_chars: int) -> str:
    title = node_info.get("title") or ""
    summary = node_info.get("summary") or ""
    text = node_info.get("text") or ""
    content = text or summary
    content = str(content).strip()
    if max_passage_chars > 0 and len(content) > max_passage_chars:
        content = content[: max_passage_chars].rstrip() + "..."
    if title and content:
        return f"Title: {title}\n{content}"
    if title:
        return f"Title: {title}"
    return content


@app.tool(output="q_ls->orig_q_ls")
def copy_query(q_ls: List[str]) -> Dict[str, List[str]]:
    """Preserve original questions for final answer generation."""
    return {"orig_q_ls": list(q_ls or [])}


def _truncate_text(text: str, max_chars: int) -> str:
    if max_chars > 0 and len(text) > max_chars:
        return text[:max_chars].rstrip() + "..."
    return text


def _strip_code_fences(text: str) -> str:
    if not text:
        return ""
    stripped = str(text).strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```[a-zA-Z0-9_-]*\n?", "", stripped).strip()
        if stripped.endswith("```"):
            stripped = stripped[: -3].strip()
    return stripped


def _tag_page_text(page_text: str, page_num: int) -> str:
    return f"<physical_index_{page_num}>\n{page_text}\n<physical_index_{page_num}>\n\n"


def _page_list_to_group_text(
    page_contents: List[str],
    token_lengths: List[int],
    max_tokens: int = 20000,
    overlap_pages: int = 1,
) -> List[str]:
    num_tokens = sum(token_lengths)
    if num_tokens <= max_tokens:
        return ["".join(page_contents)]

    subsets: List[str] = []
    current_subset: List[str] = []
    current_token_count = 0

    expected_parts_num = math.ceil(num_tokens / max_tokens)
    average_tokens_per_part = math.ceil(((num_tokens / expected_parts_num) + max_tokens) / 2)

    for i, (page_content, page_tokens) in enumerate(zip(page_contents, token_lengths)):
        if current_token_count + page_tokens > average_tokens_per_part and current_subset:
            subsets.append("".join(current_subset))
            overlap_start = max(i - max(overlap_pages, 0), 0)
            current_subset = page_contents[overlap_start:i]
            current_token_count = sum(token_lengths[overlap_start:i])

        current_subset.append(page_content)
        current_token_count += page_tokens

    if current_subset:
        subsets.append("".join(current_subset))
    return subsets


def _group_pages_by_tokens(
    page_list: List[Tuple[str, int]],
    max_tokens: int = 20000,
    overlap_pages: int = 1,
) -> List[str]:
    page_contents: List[str] = []
    token_lengths: List[int] = []
    for idx, (text, token_count) in enumerate(page_list, 1):
        page_contents.append(_tag_page_text(text, idx))
        token_lengths.append(int(token_count) + 8)
    return _page_list_to_group_text(page_contents, token_lengths, max_tokens, overlap_pages)


def _extract_matching_page_pairs(
    toc_page: List[Dict[str, Any]],
    toc_physical_index: List[Dict[str, Any]],
    start_page_index: int,
) -> List[Dict[str, Any]]:
    pairs: List[Dict[str, Any]] = []
    for phy_item in toc_physical_index or []:
        for page_item in toc_page or []:
            if phy_item.get("title") == page_item.get("title"):
                physical_index = phy_item.get("physical_index")
                if physical_index is not None and int(physical_index) >= start_page_index:
                    pairs.append(
                        {
                            "title": phy_item.get("title"),
                            "page": page_item.get("page"),
                            "physical_index": physical_index,
                        }
                    )
    return pairs


def _calculate_page_offset(pairs: List[Dict[str, Any]]) -> Optional[int]:
    differences: List[int] = []
    for pair in pairs or []:
        try:
            physical_index = int(pair["physical_index"])
            page_number = int(pair["page"])
            differences.append(physical_index - page_number)
        except (KeyError, TypeError, ValueError):
            continue

    if not differences:
        return None

    difference_counts: Dict[int, int] = {}
    for diff in differences:
        difference_counts[diff] = difference_counts.get(diff, 0) + 1

    most_common = max(difference_counts.items(), key=lambda x: x[1])[0]
    return int(most_common)


def _apply_page_offset_to_toc(
    toc_with_page_number: List[Dict[str, Any]],
    offset: Optional[int],
) -> List[Dict[str, Any]]:
    if offset is None:
        offset = 0
    for item in toc_with_page_number or []:
        if item.get("page") is not None and isinstance(item["page"], int):
            item["physical_index"] = item["page"] + offset
            item.pop("page", None)
    return toc_with_page_number


def _validate_and_truncate_physical_indices(
    toc_with_page_number: List[Dict[str, Any]],
    page_list_length: int,
    start_index: int = 1,
) -> List[Dict[str, Any]]:
    if not toc_with_page_number:
        return toc_with_page_number

    max_allowed_page = page_list_length + start_index - 1
    for item in toc_with_page_number:
        if item.get("physical_index") is not None:
            original_index = item["physical_index"]
            if original_index > max_allowed_page:
                item["physical_index"] = None
    return toc_with_page_number


@app.tool(
    output="parse_file_path,page_corpus_save_path,tokenizer_model->page_corpus_path"
)
def build_page_corpus(
    parse_file_path: str,
    page_corpus_save_path: str,
    tokenizer_model: str = "gpt-4o-2024-11-20",
) -> Dict[str, str]:
    """Build page-level corpus JSONL from a PDF file.

    The output JSONL is used as the canonical input for PageIndex prompts.
    """
    try:
        pdf_path = _resolve_path(parse_file_path, must_exist=True)
    except ValueError as exc:
        raise ToolError(str(exc)) from exc

    if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
        raise ToolError(f"Only PDF file is supported: {pdf_path}")

    out_path = _resolve_output_path(page_corpus_save_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows: List[Dict[str, Any]] = []

    try:
        import pymupdf
    except ImportError as exc:
        raise ToolError("pymupdf not installed. Please `pip install pymupdf`.") from exc

    doc = None
    try:
        doc = pymupdf.open(str(pdf_path))
        for i, page in enumerate(doc):
            page_text = page.get_text() or ""
            rows.append(
                {
                    "doc_id": pdf_path.stem,
                    "page_index": i + 1,
                    "text": page_text,
                    "token_count": count_tokens(page_text, model=tokenizer_model),
                    "source_path": str(pdf_path),
                }
            )
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass

    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    app.logger.info(
        "Built page corpus: %s (pages=%d, parser=PyMuPDF)",
        out_path,
        len(rows),
    )
    return {"page_corpus_path": str(out_path)}


@app.tool(
    output="page_corpus_path,max_group_tokens,overlap_pages,tokenizer_model->group_texts,group_total,group_idx"
)
def prepare_page_groups(
    page_corpus_path: str,
    max_group_tokens: int = 20000,
    overlap_pages: int = 1,
    tokenizer_model: str = "gpt-4o-2024-11-20",
) -> Dict[str, Any]:
    page_list, _ = load_page_corpus(page_corpus_path, model=tokenizer_model)
    if not page_list:
        raise ToolError("page_corpus is empty.")
    group_texts = _group_pages_by_tokens(
        page_list,
        max_tokens=max_group_tokens,
        overlap_pages=overlap_pages,
    )
    return {"group_texts": group_texts, "group_total": len(group_texts), "group_idx": 0}


@app.tool(output="group_idx,group_total->group_state_ls")
def prepare_group_routing(group_idx: int, group_total: int) -> Dict[str, List[Dict[str, Any]]]:
    """Prepare routing input by wrapping group state into a list."""
    idx = int(group_idx or 0)
    total = int(group_total or 0)
    state = "continue" if total > 0 and idx < (total - 1) else "stop"
    return {"group_state_ls": [{"idx": idx, "total": total, "state": state}]}


@app.tool(output="group_state_ls->group_state_ls")
def route_group_state(group_state_ls: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Route based on group state."""
    result = []
    for item in group_state_ls:
        state = item.get("state", "stop")
        result.append({"data": item, "state": state})
    return {"group_state_ls": result}


@app.tool(output="group_idx->group_idx")
def advance_group_idx(group_idx: int) -> Dict[str, int]:
    return {"group_idx": int(group_idx or 0) + 1}


@app.tool(output="toc_content,toc_detect_page_index_template->prompt_ls")
def prepare_toc_page_index_prompt(
    toc_content: str,
    toc_detect_page_index_template: Union[str, Path],
) -> Dict[str, Any]:
    prompt = _render_prompt(toc_detect_page_index_template, toc_content=toc_content)
    return {"prompt_ls": [prompt]}


@app.tool(output="ans_ls->page_index_given_in_toc")
def parse_toc_page_index(ans_ls: List[str]) -> Dict[str, str]:
    ans = ans_ls[0] if ans_ls else ""
    data = extract_json(ans or "")
    if isinstance(data, dict):
        page_index_given = str(data.get("page_index_given_in_toc") or "no").strip().lower()
    else:
        text = (ans or "").lower()
        page_index_given = "yes" if "yes" in text and "no" not in text else "no"
    if page_index_given not in ("yes", "no"):
        page_index_given = "no"
    return {"page_index_given_in_toc": page_index_given}


@app.tool(output="group_texts,toc_generate_init_template->prompt_ls")
def prepare_toc_generate_init_prompt(
    group_texts: List[str],
    toc_generate_init_template: Union[str, Path],
) -> Dict[str, List[str]]:
    if not group_texts:
        raise ToolError("group_texts is empty.")
    prompt = _render_prompt(toc_generate_init_template, pages_with_tags=group_texts[0])
    return {"prompt_ls": [prompt]}


@app.tool(output="ans_ls->toc_list")
def parse_toc_generate(ans_ls: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    ans = ans_ls[0] if ans_ls else ""
    data = extract_json(ans or "")
    if isinstance(data, list):
        toc_list = data
    elif isinstance(data, dict) and "table_of_contents" in data:
        toc_list = data.get("table_of_contents") or []
    else:
        toc_list = []
    return {"toc_list": toc_list}


@app.tool(
    output="group_texts,group_idx,toc_list,toc_generate_continue_template->prompt_ls"
)
def prepare_toc_generate_continue_prompt(
    group_texts: List[str],
    group_idx: int,
    toc_list: List[Dict[str, Any]],
    toc_generate_continue_template: Union[str, Path],
) -> Dict[str, List[str]]:
    idx = int(group_idx or 0)
    if not group_texts or idx >= len(group_texts):
        raise ToolError("group_idx out of range for group_texts.")
    toc_json = json.dumps(toc_list or [], ensure_ascii=False, indent=2)
    prompt = _render_prompt(
        toc_generate_continue_template,
        pages_with_tags=group_texts[idx],
        toc_json=toc_json,
    )
    return {"prompt_ls": [prompt]}


@app.tool(output="ans_ls->toc_add")
def parse_toc_generate_continue(ans_ls: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    ans = ans_ls[0] if ans_ls else ""
    data = extract_json(ans or "")
    if isinstance(data, list):
        toc_add = data
    else:
        toc_add = []
    return {"toc_add": toc_add}


@app.tool(output="toc_list,toc_add->toc_list")
def merge_toc_lists(
    toc_list: List[Dict[str, Any]],
    toc_add: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    merged = list(toc_list or [])
    merged.extend(toc_add or [])
    return {"toc_list": merged}


@app.tool(output="group_texts,group_idx,toc_list,toc_fill_template->prompt_ls")
def prepare_toc_fill_prompt(
    group_texts: List[str],
    group_idx: int,
    toc_list: List[Dict[str, Any]],
    toc_fill_template: Union[str, Path],
) -> Dict[str, List[str]]:
    idx = int(group_idx or 0)
    if not group_texts or idx >= len(group_texts):
        raise ToolError("group_idx out of range for group_texts.")
    structure_json = json.dumps(toc_list or [], ensure_ascii=False, indent=2)
    prompt = _render_prompt(
        toc_fill_template,
        pages_with_tags=group_texts[idx],
        structure_json=structure_json,
    )
    return {"prompt_ls": [prompt]}


@app.tool(output="ans_ls,toc_list->toc_list")
def parse_toc_fill(
    ans_ls: List[str],
    toc_list: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    ans = ans_ls[0] if ans_ls else ""
    data = extract_json(ans or "")
    if isinstance(data, list):
        new_list = data
    else:
        new_list = list(toc_list or [])
    for item in new_list:
        if isinstance(item, dict):
            item.pop("start", None)
    return {"toc_list": new_list}


@app.tool(
    output="toc_list,toc_with_physical_index,toc_page_list->toc_with_physical_index"
)
def apply_page_offset(
    toc_list: List[Dict[str, Any]],
    toc_with_physical_index: List[Dict[str, Any]],
    toc_page_list: List[int],
) -> Dict[str, List[Dict[str, Any]]]:
    toc_items = [dict(item) for item in (toc_list or [])]
    toc_items = convert_page_to_int(toc_items)
    start_page_index = (toc_page_list[-1] + 1) if toc_page_list else 1

    partial = convert_physical_index_to_int(list(toc_with_physical_index or []))
    pairs = _extract_matching_page_pairs(toc_items, partial, start_page_index)
    offset = _calculate_page_offset(pairs)

    toc_items = _apply_page_offset_to_toc(toc_items, offset)

    # Prefer exact matches from partial mapping when available.
    partial_map = {
        item.get("title"): item.get("physical_index")
        for item in (partial or [])
        if item.get("physical_index") is not None
    }
    for item in toc_items:
        title = item.get("title")
        if title in partial_map:
            item["physical_index"] = partial_map[title]
        item.pop("page", None)

    return {"toc_with_physical_index": toc_items}


@app.tool(output="toc_with_physical_index->toc_with_physical_index")
def normalize_toc_physical_index(
    toc_with_physical_index: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    toc_list = convert_physical_index_to_int(list(toc_with_physical_index or []))
    return {"toc_with_physical_index": toc_list}


@app.tool(output="toc_with_physical_index,page_corpus_path->toc_with_physical_index")
def validate_physical_indices(
    toc_with_physical_index: List[Dict[str, Any]],
    page_corpus_path: str,
) -> Dict[str, List[Dict[str, Any]]]:
    page_list, _ = load_page_corpus(page_corpus_path)
    toc_list = _validate_and_truncate_physical_indices(
        list(toc_with_physical_index or []), len(page_list)
    )
    return {"toc_with_physical_index": toc_list}


@app.tool(output="toc_with_physical_index->toc_with_physical_index")
def apply_preface_if_needed(
    toc_with_physical_index: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    toc_list = add_preface_if_needed(list(toc_with_physical_index or []))
    return {"toc_with_physical_index": toc_list}


@app.tool(
    output="toc_with_physical_index,page_corpus_path,max_page_chars,toc_check_start_template->prompt_ls,start_items"
)
def prepare_title_start_prompts(
    toc_with_physical_index: List[Dict[str, Any]],
    page_corpus_path: str,
    max_page_chars: int = 4000,
    toc_check_start_template: Union[str, Path] = "prompt/pageindex/toc_check_start.jinja",
) -> Dict[str, Any]:
    page_list, _ = load_page_corpus(page_corpus_path)
    prompt_ls: List[str] = []
    start_items: List[Dict[str, Any]] = []
    for list_index, item in enumerate(toc_with_physical_index or []):
        page_num = item.get("physical_index")
        if page_num is None:
            continue
        page_num = int(page_num)
        if page_num <= 0 or page_num > len(page_list):
            continue
        page_text = _truncate_text(page_list[page_num - 1][0], max_page_chars)
        prompt_ls.append(
            _render_prompt(
                toc_check_start_template,
                title=item.get("title", ""),
                page_text=page_text,
            )
        )
        start_items.append({"list_index": list_index})
    return {"prompt_ls": prompt_ls, "start_items": start_items}


@app.tool(output="ans_ls,start_items,toc_with_physical_index->toc_with_physical_index")
def apply_title_start(
    ans_ls: List[str],
    start_items: List[Dict[str, Any]],
    toc_with_physical_index: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    for ans, item in zip(ans_ls or [], start_items or []):
        list_index = item.get("list_index")
        if list_index is None or list_index >= len(toc_with_physical_index):
            continue
        data = extract_json(ans or "")
        if isinstance(data, dict):
            flag = str(data.get("start_begin") or "").strip().lower()
        else:
            flag = ""
        if flag not in ("yes", "no"):
            flag = "no"
        toc_with_physical_index[list_index]["appear_start"] = flag
    return {"toc_with_physical_index": toc_with_physical_index}


@app.tool(output="->current_mode")
def set_mode_with_page_numbers() -> Dict[str, str]:
    """Set current mode to 'with_page_numbers'."""
    return {"current_mode": "with_page_numbers"}


@app.tool(output="->current_mode")
def set_mode_with_toc_no_page() -> Dict[str, str]:
    """Set current mode to 'with_toc_no_page'."""
    return {"current_mode": "with_toc_no_page"}


@app.tool(output="->current_mode")
def set_mode_no_toc() -> Dict[str, str]:
    """Set current mode to 'no_toc'."""
    return {"current_mode": "no_toc"}


@app.tool(output="toc_content,page_index_given_in_toc,toc_page_list->presence_ls")
def prepare_presence_routing(
    toc_content: str,
    page_index_given_in_toc: str,
    toc_page_list: List[int],
) -> Dict[str, List[Dict[str, Any]]]:
    """Prepare routing input by wrapping variables into a list format."""
    has_toc = bool(toc_page_list) and bool(str(toc_content or "").strip())
    flag = str(page_index_given_in_toc or "").strip().lower()
    if has_toc and flag == "yes":
        mode = "with_page_numbers"
    elif has_toc:
        mode = "with_toc_no_page"
    else:
        mode = "no_toc"
    return {
        "presence_ls": [{
            "toc_content": toc_content,
            "page_index_given_in_toc": page_index_given_in_toc,
            "toc_page_list": toc_page_list,
            "mode": mode,
        }]
    }


@app.tool(output="presence_ls->presence_ls")
def route_toc_presence(presence_ls: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Route based on TOC presence mode."""
    result = []
    for item in presence_ls:
        mode = item.get("mode", "no_toc")
        result.append({"data": item, "state": mode})
    return {"presence_ls": result}


@app.tool(output="accuracy,incorrect_items,current_mode,accuracy_threshold->quality_q_ls")
def route_toc_quality(
    accuracy: float,
    incorrect_items: List[Dict[str, Any]],
    current_mode: str,
    accuracy_threshold: float = 0.6,
) -> Dict[str, List[Dict[str, str]]]:
    acc = float(accuracy or 0)
    incorrect_count = len(incorrect_items or [])
    threshold = float(accuracy_threshold or 0.6)

    if acc >= 1.0 or incorrect_count == 0:
        state = "accept"
    elif acc > threshold:
        state = "fix"
    elif current_mode == "with_page_numbers":
        state = "fallback_no_page_numbers"
    elif current_mode == "with_toc_no_page":
        state = "fallback_no_toc"
    else:
        state = "accept"

    return {"quality_q_ls": [{"data": "", "state": state}]}


@app.tool(
    output="page_corpus_path,toc_detect_template,toc_check_page_num,max_page_chars->prompt_ls,toc_candidate_pages"
)
def prepare_toc_detect_prompts(
    page_corpus_path: str,
    toc_detect_template: Union[str, Path],
    toc_check_page_num: int = 20,
    max_page_chars: int = 4000,
) -> Dict[str, Any]:
    """
    Generates a list of LLM prompts to detect a Table of Contents (TOC) in the initial pages of a document.

    This function loads the document corpus, iterates through the first N pages (defined by 
    `toc_check_page_num`), truncates the text to ensure it fits within context limits, and 
    renders a prompt for each page using the provided template.

    Args:
        page_corpus_path (str): The file path to the processed page corpus data.
        toc_detect_template (Union[str, Path]): The prompt template (or path to it) used to ask the LLM 
            to verify if a page contains a TOC.
        toc_check_page_num (int, optional): The maximum number of pages to check from the start 
            of the document. Defaults to 20.
        max_page_chars (int, optional): The maximum number of characters to include from a page 
            to avoid exceeding token limits. Defaults to 4000.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - "prompt_ls": A list of rendered prompt strings ready for LLM inference.
            - "toc_candidate_pages": A list of the corresponding page numbers (1-based index).
    """
    page_list, _ = load_page_corpus(page_corpus_path)
    max_pages = min(len(page_list), max(toc_check_page_num, 0))
    candidate_pages = list(range(1, max_pages + 1))
    prompt_ls: List[str] = []
    for idx in candidate_pages:
        page_text = _truncate_text(page_list[idx - 1][0], max_page_chars)
        prompt_ls.append(
            _render_prompt(toc_detect_template, page_text=page_text)
        )
    return {"prompt_ls": prompt_ls, "toc_candidate_pages": candidate_pages}


@app.tool(output="ans_ls,toc_candidate_pages->toc_page_list")
def parse_toc_detect(
    ans_ls: List[str],
    toc_candidate_pages: List[int],
) -> Dict[str, List[int]]:
    """
    Parses LLM responses to identify which pages contain a Table of Contents (TOC).

    This function iterates through the model's raw string responses (`ans_ls`) corresponding
    to specific page numbers (`toc_candidate_pages`). It employs a two-step verification strategy:
    1. Attempts to extract a structured JSON response (looking for key "toc_detected").
    2. Falls back to a heuristic keyword search ("yes" vs "no") if JSON parsing fails.

    Args:
        ans_ls (List[str]): The list of raw text responses generated by the LLM.
        toc_candidate_pages (List[int]): The list of page numbers corresponding to the
            queries sent to the LLM.

    Returns:
        Dict[str, List[int]]: A dictionary containing:
            - "toc_page_list": A filtered list of page numbers identified as containing a TOC.
    """
    toc_page_list: List[int] = []
    for ans, page_index in zip(ans_ls or [], toc_candidate_pages or []):
        data = extract_json(ans or "")
        if isinstance(data, dict):
            flag = str(data.get("toc_detected", "")).strip().lower()
        else:
            flag = ""
        if not flag:
            text = (ans or "").lower()
            flag = "yes" if "yes" in text and "no" not in text else "no"
        if flag == "yes":
            toc_page_list.append(int(page_index))
    return {"toc_page_list": toc_page_list}


@app.tool(
    output="page_corpus_path,toc_page_list,toc_extract_template,toc_check_page_num,max_toc_chars->prompt_ls,toc_extract_content"
)
def prepare_toc_extract_prompt(
    page_corpus_path: str,
    toc_page_list: List[int],
    toc_extract_template: Union[str, Path],
    toc_check_page_num: int = 20,
    max_toc_chars: int = 12000,
) -> Dict[str, Any]:
    """
    Prepares the final LLM prompt for TOC extraction or generation based on detection results.

    This function employs a hybrid strategy:
    1. If TOC pages were detected (`toc_page_list` is not empty), it concatenates text from 
       those specific pages and instructs the LLM to **extract** the existing TOC.
    2. If no TOC was detected, it concatenates the first N pages (`toc_check_page_num`) 
       and instructs the LLM to **generate** a logical TOC from the content.

    Args:
        page_corpus_path (str): Path to the processed page corpus.
        toc_page_list (List[int]): List of page numbers identified as containing the TOC.
            If empty, the function falls back to generation mode.
        toc_extract_template (Union[str, Path]): The Jinja2 template used to render the prompt.
            Must handle `has_toc` boolean logic.
        toc_check_page_num (int, optional): Number of initial pages to use for TOC generation 
            if no TOC is found. Defaults to 20.
        max_toc_chars (int, optional): Maximum character limit for the context window. 
            Defaults to 12000.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - "prompt_ls": A list containing a single rendered prompt string.
            - "toc_extract_content": The raw content used for extraction/checking.
    """
    page_list, _ = load_page_corpus(page_corpus_path)
    if toc_page_list:
        raw = "".join(page_list[i - 1][0] for i in toc_page_list if 0 < i <= len(page_list))
        raw = _truncate_text(raw, max_toc_chars)
        prompt = _render_prompt(
            toc_extract_template,
            content=raw,
            has_toc=True,
        )
    else:
        max_pages = min(len(page_list), max(toc_check_page_num, 0))
        content = "".join(page_list[i][0] for i in range(max_pages))
        content = _truncate_text(content, max_toc_chars)
        prompt = _render_prompt(
            toc_extract_template,
            content=content,
            has_toc=False,
        )
        raw = content
    return {"prompt_ls": [prompt], "toc_extract_content": raw}


@app.tool(output="ans_ls->toc_content,page_index_given_in_toc")
def parse_toc_extract(ans_ls: List[str]) -> Dict[str, str]:
    """
    Parses the raw LLM response to extract the Table of Contents (TOC) text and metadata.

    This function implements a robust parsing strategy:
    1. It first attempts to parse the response as a structured JSON object.
    2. If JSON parsing fails (e.g., the LLM returns unstructured text), it falls back 
       to treating the entire raw string as the TOC content.
    3. It normalizes the `page_index_given_in_toc` flag to ensure it strictly contains 
       "yes" or "no".

    Args:
        ans_ls (List[str]): A list containing the raw response strings from the LLM. 
            Typically contains a single string element.

    Returns:
        Dict[str, str]: A dictionary containing:
            - "toc_content": The extracted or raw text of the Table of Contents.
            - "page_index_given_in_toc": A normalized flag ("yes" or "no") indicating 
              whether page numbers were detected in the TOC. Defaults to "no" in fallback mode.
    """
    ans = ans_ls[0] if ans_ls else ""
    data = extract_json(ans or "")
    if isinstance(data, dict) and (
        "toc_content" in data or "page_index_given_in_toc" in data
    ):
        toc_content = data.get("toc_content") or ""
        page_index_given = str(data.get("page_index_given_in_toc") or "no").strip().lower()
    else:
        toc_content = ans or ""
        page_index_given = "no"
    if page_index_given not in ("yes", "no"):
        page_index_given = "no"
    return {
        "toc_content": toc_content,
        "page_index_given_in_toc": page_index_given,
    }


@app.tool(
    output="toc_extract_content,toc_content,toc_extract_check_template->prompt_ls"
)
def prepare_toc_extract_check_prompt(
    toc_extract_content: str,
    toc_content: str,
    toc_extract_check_template: Union[str, Path] = "prompt/pageindex/toc_extract_check.jinja",
) -> Dict[str, List[str]]:
    prompt = _render_prompt(
        toc_extract_check_template,
        content=toc_extract_content,
        toc_content=toc_content,
    )
    return {"prompt_ls": [prompt]}


@app.tool(output="ans_ls->ans_ls")
def route_toc_extract_state(ans_ls: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    ans = ans_ls[0] if ans_ls else ""
    data = extract_json(ans or "")
    if isinstance(data, dict):
        completed = str(data.get("completed") or "").strip().lower()
    else:
        completed = ""
    state = "stop" if completed == "yes" else "continue"
    return {"ans_ls": [{"data": a, "state": state} for a in ans_ls]}


@app.tool(output="toc_content,toc_extract_continue_template->prompt_ls")
def prepare_toc_extract_continue_prompt(
    toc_content: str,
    toc_extract_continue_template: Union[str, Path] = "prompt/pageindex/toc_extract_continue.jinja",
) -> Dict[str, List[str]]:
    prompt = _render_prompt(
        toc_extract_continue_template,
        toc_content=toc_content,
    )
    return {"prompt_ls": [prompt]}


@app.tool(output="toc_content,ans_ls->toc_content")
def append_toc_content(
    toc_content: str,
    ans_ls: List[str],
) -> Dict[str, str]:
    extra = _strip_code_fences((ans_ls or [""])[0])
    merged = f"{toc_content}{extra}"
    return {"toc_content": merged}


@app.tool(output="ans_ls->toc_transform_raw")
def parse_toc_transform_raw(ans_ls: List[str]) -> Dict[str, str]:
    ans = ans_ls[0] if ans_ls else ""
    return {"toc_transform_raw": _strip_code_fences(ans)}


@app.tool(
    output="toc_content,toc_transform_raw,toc_transform_check_template->prompt_ls"
)
def prepare_toc_transform_check_prompt(
    toc_content: str,
    toc_transform_raw: str,
    toc_transform_check_template: Union[str, Path] = "prompt/pageindex/toc_transform_check.jinja",
) -> Dict[str, List[str]]:
    prompt = _render_prompt(
        toc_transform_check_template,
        raw_toc=toc_content,
        cleaned_toc=toc_transform_raw,
    )
    return {"prompt_ls": [prompt]}


@app.tool(output="ans_ls->ans_ls")
def route_toc_transform_state(ans_ls: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    ans = ans_ls[0] if ans_ls else ""
    data = extract_json(ans or "")
    if isinstance(data, dict):
        completed = str(data.get("completed") or "").strip().lower()
    else:
        completed = ""
    state = "stop" if completed == "yes" else "continue"
    return {"ans_ls": [{"data": a, "state": state} for a in ans_ls]}


@app.tool(
    output="toc_content,toc_transform_raw,toc_transform_continue_template->prompt_ls"
)
def prepare_toc_transform_continue_prompt(
    toc_content: str,
    toc_transform_raw: str,
    toc_transform_continue_template: Union[str, Path] = "prompt/pageindex/toc_transform_continue.jinja",
) -> Dict[str, List[str]]:
    prompt = _render_prompt(
        toc_transform_continue_template,
        raw_toc=toc_content,
        partial_json=toc_transform_raw,
    )
    return {"prompt_ls": [prompt]}


@app.tool(output="toc_transform_raw,ans_ls->toc_transform_raw")
def append_toc_transform_raw(
    toc_transform_raw: str,
    ans_ls: List[str],
) -> Dict[str, str]:
    extra = _strip_code_fences((ans_ls or [""])[0])
    merged = f"{toc_transform_raw}{extra}"
    return {"toc_transform_raw": merged}


@app.tool(output="toc_transform_raw->toc_list")
def finalize_toc_transform(
    toc_transform_raw: str,
) -> Dict[str, List[Dict[str, Any]]]:
    data = extract_json(toc_transform_raw or "")
    if isinstance(data, dict) and "table_of_contents" in data:
        toc_list = data.get("table_of_contents") or []
    elif isinstance(data, list):
        toc_list = data
    else:
        toc_list = []
    toc_list = convert_page_to_int(toc_list)
    return {"toc_list": toc_list}


@app.tool(output="toc_content,toc_transform_template->prompt_ls")
def prepare_toc_transform_prompt(
    toc_content: str,
    toc_transform_template: Union[str, Path],
) -> Dict[str, List[str]]:
    prompt = _render_prompt(toc_transform_template, toc_content=toc_content)
    return {"prompt_ls": [prompt]}


@app.tool(output="ans_ls->toc_list")
def parse_toc_transform(ans_ls: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    ans = ans_ls[0] if ans_ls else ""
    data = extract_json(ans or "")
    
    toc_list = []
    if isinstance(data, dict) and "table_of_contents" in data:
        toc_list = data.get("table_of_contents") or []
    elif isinstance(data, list):
        toc_list = data
    else:
        # 尝试从原始文本中提取 JSON 数组
        import re
        array_match = re.search(r'\[\s*\{.*\}\s*\]', ans, re.DOTALL)
        if array_match:
            try:
                toc_list = json.loads(array_match.group())
            except json.JSONDecodeError:
                pass
        
        if not toc_list:
            app.logger.warning(
                "Failed to parse TOC transform result (len=%d). Using empty list.",
                len(ans)
            )
    
    toc_list = convert_page_to_int(toc_list)
    return {"toc_list": toc_list}


@app.tool(
    output="toc_list,page_corpus_path,toc_check_page_num,max_map_chars,page_index_given_in_toc,toc_map_template->prompt_ls"
)
def prepare_toc_map_prompt(
    toc_list: List[Dict[str, Any]],
    page_corpus_path: str,
    toc_check_page_num: int = 20,
    max_map_chars: int = 12000,
    page_index_given_in_toc: str = "no",
    toc_map_template: str = "prompt/pageindex/toc_map_physical.jinja",
) -> Dict[str, List[str]]:
    if not toc_list:
        return {"prompt_ls": []}
    page_list, _ = load_page_corpus(page_corpus_path)
    max_pages = min(len(page_list), max(toc_check_page_num, 0))
    tagged = []
    for i in range(max_pages):
        page_text = page_list[i][0]
        tagged.append(f"<physical_index_{i+1}>\n{page_text}\n<physical_index_{i+1}>\n")
    tagged_text = _truncate_text("".join(tagged), max_map_chars)
    prompt = _render_prompt(
        toc_map_template,
        toc_list_json=json.dumps(toc_list, ensure_ascii=False),
        pages_with_tags=tagged_text,
        page_index_given_in_toc=page_index_given_in_toc,
    )
    return {"prompt_ls": [prompt]}


@app.tool(output="ans_ls->toc_with_physical_index")
def parse_toc_map(ans_ls: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    ans = ans_ls[0] if ans_ls else ""
    data = extract_json(ans or "")
    if isinstance(data, list):
        toc_list = data
    else:
        toc_list = []
    toc_list = convert_physical_index_to_int(toc_list)
    return {"toc_with_physical_index": toc_list}


@app.tool(
    output="toc_with_physical_index,page_corpus_path,verify_sample_size,max_page_chars,toc_verify_template->prompt_ls,verify_items"
)
def prepare_verify_title_prompts(
    toc_with_physical_index: List[Dict[str, Any]],
    page_corpus_path: str,
    verify_sample_size: int = 20,
    max_page_chars: int = 4000,
    toc_verify_template: str = "prompt/pageindex/toc_verify_title.jinja",
) -> Dict[str, Any]:
    """Prepare prompts to verify whether section titles appear on assigned pages."""
    page_list, _ = load_page_corpus(page_corpus_path)
    items = [
        (idx, item)
        for idx, item in enumerate(toc_with_physical_index or [])
        if item.get("physical_index") is not None
    ]
    if verify_sample_size is not None and verify_sample_size > 0:
        items = items[: min(len(items), verify_sample_size)]

    prompt_ls: List[str] = []
    verify_items: List[Dict[str, Any]] = []
    for list_index, item in items:
        page_num = int(item["physical_index"])
        if page_num <= 0 or page_num > len(page_list):
            continue
        page_text = _truncate_text(page_list[page_num - 1][0], max_page_chars)
        prompt_ls.append(
            _render_prompt(
                toc_verify_template,
                title=item.get("title", ""),
                page_text=page_text,
            )
        )
        verify_items.append(
            {
                "list_index": list_index,
                "title": item.get("title", ""),
                "physical_index": page_num,
            }
        )
    return {"prompt_ls": prompt_ls, "verify_items": verify_items}


@app.tool(output="ans_ls,verify_items->accuracy,incorrect_items")
def parse_verify_title(
    ans_ls: List[str],
    verify_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Parse verification answers and return incorrect items."""
    correct = 0
    incorrect_items: List[Dict[str, Any]] = []
    for ans, item in zip(ans_ls or [], verify_items or []):
        data = extract_json(ans or "")
        if isinstance(data, dict):
            answer = str(data.get("answer") or data.get("start_begin") or "").strip().lower()
        else:
            answer = ""
        if answer == "yes":
            correct += 1
        else:
            incorrect_items.append(item)

    checked = len(verify_items or [])
    accuracy = (correct / checked) if checked > 0 else 0.0
    return {"accuracy": accuracy, "incorrect_items": incorrect_items}


@app.tool(
    output="incorrect_items,toc_with_physical_index,page_corpus_path,max_fix_pages,toc_fix_template->prompt_ls,fix_items"
)
def prepare_fix_incorrect_prompts(
    incorrect_items: List[Dict[str, Any]],
    toc_with_physical_index: List[Dict[str, Any]],
    page_corpus_path: str,
    max_fix_pages: int = 20,
    toc_fix_template: str = "prompt/pageindex/toc_fix_incorrect.jinja",
) -> Dict[str, Any]:
    """Prepare prompts to fix incorrect physical indices."""
    page_list, _ = load_page_corpus(page_corpus_path)
    prompt_ls: List[str] = []
    fix_items: List[Dict[str, Any]] = []

    for item in incorrect_items or []:
        list_index = item.get("list_index")
        title = item.get("title", "")
        if list_index is None or list_index >= len(toc_with_physical_index):
            continue

        # Find previous and next known indices to narrow the search range
        prev_idx = 1
        for i in range(list_index - 1, -1, -1):
            prev = toc_with_physical_index[i].get("physical_index")
            if prev is not None:
                prev_idx = int(prev)
                break
        next_idx = len(page_list)
        for i in range(list_index + 1, len(toc_with_physical_index)):
            nxt = toc_with_physical_index[i].get("physical_index")
            if nxt is not None:
                next_idx = int(nxt)
                break

        start = max(prev_idx, 1)
        end = min(next_idx, len(page_list))
        if max_fix_pages > 0 and (end - start + 1) > max_fix_pages:
            end = min(start + max_fix_pages - 1, len(page_list))

        tagged = []
        for page_num in range(start, end + 1):
            page_text = page_list[page_num - 1][0]
            tagged.append(
                f"<physical_index_{page_num}>\n{page_text}\n<physical_index_{page_num}>\n"
            )
        tagged_text = _truncate_text("".join(tagged), 12000)

        prompt_ls.append(
            _render_prompt(
                toc_fix_template,
                title=title,
                pages_with_tags=tagged_text,
            )
        )
        fix_items.append(
            {
                "list_index": list_index,
                "title": title,
                "range_start": start,
                "range_end": end,
            }
        )

    return {"prompt_ls": prompt_ls, "fix_items": fix_items}


@app.tool(
    output="toc_with_physical_index,page_corpus_path,max_fix_pages,toc_fix_template->prompt_ls,fix_items"
)
def prepare_fill_missing_prompts(
    toc_with_physical_index: List[Dict[str, Any]],
    page_corpus_path: str,
    max_fix_pages: int = 20,
    toc_fix_template: str = "prompt/pageindex/toc_fix_incorrect.jinja",
) -> Dict[str, Any]:
    """Prepare prompts to fill missing physical indices."""
    page_list, _ = load_page_corpus(page_corpus_path)
    prompt_ls: List[str] = []
    fix_items: List[Dict[str, Any]] = []

    missing_items = [
        {"list_index": idx, "title": item.get("title", "")}
        for idx, item in enumerate(toc_with_physical_index or [])
        if item.get("physical_index") is None
    ]

    for item in missing_items:
        list_index = item.get("list_index")
        title = item.get("title", "")
        if list_index is None or list_index >= len(toc_with_physical_index):
            continue

        # Find previous and next known indices to narrow the search range
        prev_idx = 1
        for i in range(list_index - 1, -1, -1):
            prev = toc_with_physical_index[i].get("physical_index")
            if prev is not None:
                prev_idx = int(prev)
                break
        next_idx = len(page_list)
        for i in range(list_index + 1, len(toc_with_physical_index)):
            nxt = toc_with_physical_index[i].get("physical_index")
            if nxt is not None:
                next_idx = int(nxt)
                break

        start = max(prev_idx, 1)
        end = min(next_idx, len(page_list))
        if max_fix_pages > 0 and (end - start + 1) > max_fix_pages:
            end = min(start + max_fix_pages - 1, len(page_list))

        tagged = []
        for page_num in range(start, end + 1):
            page_text = page_list[page_num - 1][0]
            tagged.append(
                f"<physical_index_{page_num}>\n{page_text}\n<physical_index_{page_num}>\n"
            )
        tagged_text = _truncate_text("".join(tagged), 12000)

        prompt_ls.append(
            _render_prompt(
                toc_fix_template,
                title=title,
                pages_with_tags=tagged_text,
            )
        )
        fix_items.append(
            {
                "list_index": list_index,
                "title": title,
                "range_start": start,
                "range_end": end,
            }
        )

    return {"prompt_ls": prompt_ls, "fix_items": fix_items}


@app.tool(output="ans_ls,fix_items,toc_with_physical_index->toc_with_physical_index")
def parse_fix_incorrect(
    ans_ls: List[str],
    fix_items: List[Dict[str, Any]],
    toc_with_physical_index: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    """Apply corrected physical indices to the toc list."""
    for ans, item in zip(ans_ls or [], fix_items or []):
        data = extract_json(ans or "")
        phys = None
        if isinstance(data, dict):
            phys = data.get("physical_index")
        if isinstance(phys, str) and "physical_index" in phys:
            phys = convert_physical_index_to_int(phys)
        if isinstance(phys, int):
            list_index = item.get("list_index")
            if list_index is not None and 0 <= list_index < len(toc_with_physical_index):
                toc_with_physical_index[list_index]["physical_index"] = phys

    return {"toc_with_physical_index": toc_with_physical_index}


@app.tool(
    output="tree_json_path,page_corpus_path,max_page_num_each_node,max_token_num_each_node,max_chunk_chars,toc_generate_init_template->prompt_ls,split_targets"
)
def prepare_recursive_split_prompts(
    tree_json_path: str,
    page_corpus_path: str,
    max_page_num_each_node: int = 10,
    max_token_num_each_node: int = 20000,
    max_chunk_chars: int = 12000,
    toc_generate_init_template: str = "prompt/pageindex/toc_generate_init.jinja",
) -> Dict[str, Any]:
    """Prepare prompts to split oversized nodes into subtrees."""
    tree, structure = _load_tree_json(tree_json_path)
    page_list, _ = load_page_corpus(page_corpus_path)

    def iter_nodes(nodes):
        """Yield only dict nodes; ignore unexpected types."""
        if isinstance(nodes, dict):
            yield nodes
            for child in nodes.get("nodes", []) or []:
                yield from iter_nodes(child)
            return
        if not isinstance(nodes, list):
            return
        for node in nodes:
            if not isinstance(node, dict):
                continue
            yield node
            for child in node.get("nodes", []) or []:
                yield from iter_nodes(child)

    prompt_ls: List[str] = []
    split_targets: List[Dict[str, Any]] = []
    for node in iter_nodes(structure):
        start = node.get("start_index")
        end = node.get("end_index")
        if not start or not end:
            continue
        if (end - start + 1) <= max_page_num_each_node:
            continue
        token_sum = sum(page_list[i - 1][1] for i in range(start, end + 1) if 0 < i <= len(page_list))
        if token_sum < max_token_num_each_node:
            continue

        tagged = []
        for page_num in range(start, end + 1):
            page_text = page_list[page_num - 1][0]
            tagged.append(
                f"<physical_index_{page_num}>\n{page_text}\n<physical_index_{page_num}>\n"
            )
        tagged_text = _truncate_text("".join(tagged), max_chunk_chars)
        prompt_ls.append(
            _render_prompt(toc_generate_init_template, pages_with_tags=tagged_text)
        )
        split_targets.append(
            {
                "node_id": node.get("node_id"),
                "start_index": start,
                "end_index": end,
            }
        )

    return {"prompt_ls": prompt_ls, "split_targets": split_targets}


@app.tool(output="ans_ls,split_targets,tree_json_path->tree_json_path")
def parse_recursive_split(
    ans_ls: List[str],
    split_targets: List[Dict[str, Any]],
    tree_json_path: str,
    output_path: str = "",
) -> Dict[str, str]:
    """Apply recursive split results to the tree."""
    tree, structure = _load_tree_json(tree_json_path)

    def find_node(nodes: List[Dict[str, Any]], node_id: str):
        for node in nodes:
            if node.get("node_id") == node_id:
                return node
            child = find_node(node.get("nodes", []) or [], node_id)
            if child:
                return child
        return None

    for ans, target in zip(ans_ls or [], split_targets or []):
        node_id = target.get("node_id")
        start = target.get("start_index")
        end = target.get("end_index")
        if not node_id or not start or not end:
            continue
        data = extract_json(ans or "")
        if not isinstance(data, list):
            continue
        data = convert_physical_index_to_int(data)
        data = [item for item in data if item.get("physical_index") is not None]
        if not data:
            continue
        subtree = post_processing(data, end)
        target_node = find_node(structure, node_id)
        if target_node is not None:
            target_node["nodes"] = subtree

    out_path = output_path.strip() or tree_json_path
    out_path = str(_resolve_output_path(out_path))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)
    return {"tree_json_path": out_path}


@app.tool(
    output="tree_json_path,summary_token_threshold,max_summary_chars,node_summary_template->prompt_ls,node_ids"
)
def prepare_node_summary_prompts(
    tree_json_path: str,
    summary_token_threshold: int = 200,
    max_summary_chars: int = 12000,
    node_summary_template: str = "prompt/pageindex/node_summary.jinja",
) -> Dict[str, Any]:
    """Prepare prompts to summarize nodes with long content."""
    _, structure = _load_tree_json(tree_json_path)

    def iter_nodes(nodes):
        """Yield only dict nodes; ignore unexpected types."""
        if isinstance(nodes, dict):
            yield nodes
            for child in nodes.get("nodes", []) or []:
                yield from iter_nodes(child)
            return
        if not isinstance(nodes, list):
            return
        for node in nodes:
            if not isinstance(node, dict):
                continue
            yield node
            for child in node.get("nodes", []) or []:
                yield from iter_nodes(child)

    prompt_ls: List[str] = []
    node_ids: List[str] = []
    for node in iter_nodes(structure):
        node_text = node.get("text") or ""
        if not node_text:
            continue
        if count_tokens(node_text, model="gpt-4o-2024-11-20") < summary_token_threshold:
            continue
        prompt_ls.append(
            _render_prompt(
                node_summary_template,
                node_text=_truncate_text(node_text, max_summary_chars),
            )
        )
        node_ids.append(node.get("node_id"))

    return {"prompt_ls": prompt_ls, "node_ids": node_ids}


@app.tool(output="ans_ls,node_ids,tree_json_path->tree_json_path")
def apply_node_summaries(
    ans_ls: List[str],
    node_ids: List[str],
    tree_json_path: str,
    output_path: str = "",
) -> Dict[str, str]:
    """Apply summaries to the tree nodes and save JSON."""
    tree, structure = _load_tree_json(tree_json_path)

    def find_node(nodes: List[Dict[str, Any]], node_id: str):
        for node in nodes:
            if node.get("node_id") == node_id:
                return node
            child = find_node(node.get("nodes", []) or [], node_id)
            if child:
                return child
        return None

    for summary, node_id in zip(ans_ls or [], node_ids or []):
        if not node_id:
            continue
        node = find_node(structure, node_id)
        if node is not None:
            node["summary"] = str(summary or "").strip()

    out_path = output_path.strip() or tree_json_path
    out_path = str(_resolve_output_path(out_path))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)
    return {"tree_json_path": out_path}


@app.tool(output="tree_json_path,doc_description_template->prompt_ls")
def prepare_doc_description_prompt(
    tree_json_path: str,
    doc_description_template: str = "prompt/pageindex/doc_description.jinja",
) -> Dict[str, List[str]]:
    """Prepare prompt to generate document description from tree."""
    tree, _ = _load_tree_json(tree_json_path)
    structure_json = json.dumps(tree.get("structure", []), ensure_ascii=False)
    prompt = _render_prompt(
        doc_description_template, structure_json=structure_json
    )
    return {"prompt_ls": [prompt]}


@app.tool(output="ans_ls,tree_json_path->tree_json_path")
def apply_doc_description(
    ans_ls: List[str],
    tree_json_path: str,
    output_path: str = "",
) -> Dict[str, str]:
    tree, _ = _load_tree_json(tree_json_path)
    tree["doc_description"] = str((ans_ls or [""])[0]).strip()
    out_path = output_path.strip() or tree_json_path
    out_path = str(_resolve_output_path(out_path))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)
    return {"tree_json_path": out_path}


@app.tool(
    output="page_corpus_path,toc_with_physical_index,index_dir,index_name,if_add_node_id,if_add_node_text->index_path,doc_id"
)
def build_index(
    page_corpus_path: str,
    toc_with_physical_index: List[Dict[str, Any]],
    index_dir: str = "data/pageindex",
    index_name: str = "",
    if_add_node_id: str = "yes",
    if_add_node_text: str = "yes",
) -> Dict[str, str]:
    """Build PageIndex tree from page corpus and mapped TOC."""
    out_dir = _resolve_output_dir(index_dir)
    os.makedirs(out_dir, exist_ok=True)

    page_list, doc_name = load_page_corpus(page_corpus_path)
    if not page_list:
        raise ToolError("page_corpus is empty.")

    # Normalize physical_index to int to avoid mixed-type sorting
    toc_items: List[Dict[str, Any]] = []
    for item in (toc_with_physical_index or []):
        raw_val = item.get("physical_index")
        normalized: Optional[int] = None
        if isinstance(raw_val, str):
            stripped = raw_val.strip()
            if stripped.isdigit():
                normalized = int(stripped)
            else:
                converted = convert_physical_index_to_int(raw_val)
                if isinstance(converted, int):
                    normalized = converted
        elif isinstance(raw_val, (int, float)):
            normalized = int(raw_val)

        if normalized is not None:
            item["physical_index"] = normalized
            toc_items.append(item)

    toc_items.sort(key=lambda x: int(x.get("physical_index", 0) or 0))
    if not toc_items:
        toc_items = [
            {"structure": "1", "title": doc_name or "Document", "physical_index": 1}
        ]
    for idx, item in enumerate(toc_items, 1):
        if not item.get("structure"):
            item["structure"] = str(idx)
        if not item.get("title"):
            item["title"] = f"Section {idx}"

    tree = post_processing(toc_items, len(page_list))
    if if_add_node_id == "yes":
        write_node_id(tree)
    if if_add_node_text == "yes":
        add_node_text(tree, page_list)

    base_name = index_name.strip() or doc_name
    base_name = base_name.replace("/", "-").replace(os.sep, "-")
    doc_id = f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    index_path = out_dir / f"{doc_id}.json"

    payload = {
        "doc_id": doc_id,
        "source_path": page_corpus_path,
        "source_type": "page_corpus",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "tree": {
            "doc_name": doc_name,
            "structure": tree,
        },
    }

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    app.logger.info("PageIndex saved: %s", index_path)
    return {"index_path": str(index_path), "doc_id": doc_id}


@app.tool(
    output="q_ls,tree_json_path,top_k,max_depth,max_nodes,max_outline_chars,include_summary,tree_search_template->prompt_ls"
)
def prepare_tree_search_prompt(
    q_ls: List[str],
    tree_json_path: str,
    top_k: int = 5,
    max_depth: int = 4,
    max_nodes: int = 200,
    max_outline_chars: int = 12000,
    include_summary: bool = True,
    tree_search_template: str = "prompt/pageindex/tree_search_select.jinja",
) -> Dict[str, List[str]]:
    if not q_ls:
        raise ToolError("q_ls cannot be empty.")
    _, structure = _load_tree_json(tree_json_path)
    outline, _ = _build_outline(
        structure=structure,
        max_depth=max_depth,
        max_nodes=max_nodes,
        max_outline_chars=max_outline_chars,
        include_summary=include_summary,
    )
    if not outline.strip():
        raise ToolError("Empty outline generated from tree.")

    prompt_ls = []
    for query in q_ls:
        prompt_ls.append(
            _render_prompt(
                tree_search_template,
                query=query,
                outline=outline,
                top_k=top_k,
            )
        )
    return {"prompt_ls": prompt_ls}


@app.tool(
    output="ans_ls,tree_json_path,top_k,max_depth,max_nodes,max_outline_chars,max_passage_chars,include_summary->ret_psg"
)
def parse_tree_search(
    ans_ls: List[str],
    tree_json_path: str,
    top_k: int = 5,
    max_depth: int = 4,
    max_nodes: int = 200,
    max_outline_chars: int = 12000,
    max_passage_chars: int = 4000,
    include_summary: bool = True,
) -> Dict[str, List[List[str]]]:
    _, structure = _load_tree_json(tree_json_path)
    _, node_map = _build_outline(
        structure=structure,
        max_depth=max_depth,
        max_nodes=max_nodes,
        max_outline_chars=max_outline_chars,
        include_summary=include_summary,
    )

    ret_psg: List[List[str]] = []
    for ans in ans_ls or []:
        data = extract_json(ans or "")
        if isinstance(data, dict):
            node_ids = data.get("node_ids") or data.get("node_list") or data.get("nodes") or []
        else:
            node_ids = []
        if not isinstance(node_ids, list):
            node_ids = []
        node_ids = [str(x).strip() for x in node_ids if x is not None][:top_k]
        passages: List[str] = []
        for node_id in node_ids:
            node_info = node_map.get(node_id)
            if not node_info:
                continue
            passages.append(_format_passage(node_info, max_passage_chars=max_passage_chars))
        ret_psg.append(passages)
    return {"ret_psg": ret_psg}


@app.tool(output="q_ls,ret_psg,search_decision_template->prompt_ls")
def prepare_search_decision_prompt(
    q_ls: List[str],
    ret_psg: List[List[str]],
    search_decision_template: str = "prompt/pageindex/search_decision.jinja",
) -> Dict[str, List[str]]:
    """Prepare prompts to decide whether to continue searching."""
    prompt_ls: List[str] = []
    for q, psg in zip(q_ls or [], ret_psg or []):
        passage_text = "\n".join(psg)
        prompt_ls.append(
            _render_prompt(
                search_decision_template,
                question=q,
                documents=passage_text,
            )
        )
    return {"prompt_ls": prompt_ls}


@app.tool(output="ans_ls->q_ls")
def route_search_state(ans_ls: List[str]) -> Dict[str, List[Dict[str, str]]]:
    """Route to continue/stop based on <search> or <stop> tags."""
    q_out: List[Dict[str, str]] = []
    pattern = re.compile(r"<search>(.*?)</search>", re.DOTALL | re.IGNORECASE)
    for ans in ans_ls or []:
        text = str(ans or "")
        match = pattern.search(text)
        if match:
            query = match.group(1).strip()
            state = "continue"
            q_out.append({"data": query, "state": state})
            continue
        if "<stop>" in text.lower():
            q_out.append({"data": "", "state": "stop"})
        else:
            # Default to stop if no explicit search tag
            q_out.append({"data": "", "state": "stop"})
    return {"q_ls": q_out}


@app.tool(output="q_ls,tree_json_path->ret_psg")
def tree_search(
    q_ls: List[str],
    tree_json_path: str,
) -> Dict[str, List[List[str]]]:
    raise ToolError(
        "Use prepare_tree_search_prompt + generation.generate + parse_tree_search for LLM-based search."
    )


if __name__ == "__main__":
    app.run(transport="stdio")
