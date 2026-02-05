import tiktoken
import openai
import logging
import os
import re
from datetime import datetime
import time
import json
import copy
import asyncio
import pymupdf
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
import yaml
from pathlib import Path
from types import SimpleNamespace as config

CHATGPT_API_KEY = os.getenv("CHATGPT_API_KEY") or os.getenv("OPENAI_API_KEY")
CHATGPT_BASE_URL = os.getenv("CHATGPT_BASE_URL") or os.getenv("OPENAI_BASE_URL")


def _resolve_api_key(api_key=None):
    return api_key or os.getenv("CHATGPT_API_KEY") or os.getenv("OPENAI_API_KEY") or CHATGPT_API_KEY


def _resolve_base_url(base_url=None):
    return base_url or os.getenv("CHATGPT_BASE_URL") or os.getenv("OPENAI_BASE_URL") or CHATGPT_BASE_URL


def _openai_client(api_key=None, base_url=None):
    kwargs = {}
    if api_key:
        kwargs["api_key"] = api_key
    if base_url:
        kwargs["base_url"] = base_url
    return openai.OpenAI(**kwargs)


def _openai_async_client(api_key=None, base_url=None):
    kwargs = {}
    if api_key:
        kwargs["api_key"] = api_key
    if base_url:
        kwargs["base_url"] = base_url
    return openai.AsyncOpenAI(**kwargs)


def count_tokens(text, model=None):
    if not text:
        return 0
    try:
        enc = tiktoken.encoding_for_model(model or "gpt-4o-2024-11-20")
    except Exception:
        enc = tiktoken.get_encoding("gpt2")
    tokens = enc.encode(text)
    return len(tokens)


def load_page_corpus(page_corpus_path: str, model: str | None = None):
    """Load page-level corpus JSONL into a (page_text, token_count) list."""
    page_corpus_path = str(Path(page_corpus_path).expanduser().resolve())
    rows = []
    doc_name = None
    with open(page_corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            if doc_name is None:
                doc_name = data.get("doc_id")
                if not doc_name:
                    src = data.get("source_path")
                    if isinstance(src, str) and src:
                        doc_name = os.path.splitext(os.path.basename(src))[0]

            page_index = data.get("page_index") or data.get("page_number") or data.get("id")
            if page_index is None:
                continue
            text = data.get("text") or data.get("contents") or ""
            token_count = data.get("token_count")
            if token_count is None:
                token_count = count_tokens(text, model=model or "gpt-4o-2024-11-20")
            rows.append((int(page_index), text, int(token_count)))

    rows.sort(key=lambda x: x[0])
    page_list = [(text, token_count) for _, text, token_count in rows]
    return page_list, (doc_name or "document")


def ChatGPT_API_with_finish_reason(model, prompt, api_key=CHATGPT_API_KEY, base_url=None, chat_history=None):
    max_retries = 10
    api_key = _resolve_api_key(api_key)
    base_url = _resolve_base_url(base_url)
    client = _openai_client(api_key=api_key, base_url=base_url)
    for i in range(max_retries):
        try:
            if chat_history:
                messages = chat_history
                messages.append({"role": "user", "content": prompt})
            else:
                messages = [{"role": "user", "content": prompt}]

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )
            if response.choices[0].finish_reason == "length":
                return response.choices[0].message.content, "max_output_reached"
            else:
                return response.choices[0].message.content, "finished"

        except Exception as e:
            print("************* Retrying *************")
            logging.error(f"Error: {e}")
            if i < max_retries - 1:
                time.sleep(1)  # Wait for 1秒 before retrying
            else:
                logging.error("Max retries reached for prompt: " + prompt)
                return "Error"


def ChatGPT_API(model, prompt, api_key=CHATGPT_API_KEY, base_url=None, chat_history=None):
    max_retries = 10
    api_key = _resolve_api_key(api_key)
    base_url = _resolve_base_url(base_url)
    client = _openai_client(api_key=api_key, base_url=base_url)
    for i in range(max_retries):
        try:
            if chat_history:
                messages = chat_history
                messages.append({"role": "user", "content": prompt})
            else:
                messages = [{"role": "user", "content": prompt}]

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )

            return response.choices[0].message.content
        except Exception as e:
            print("************* Retrying *************")
            logging.error(f"Error: {e}")
            if i < max_retries - 1:
                time.sleep(1)  # Wait for 1秒 before retrying
            else:
                logging.error("Max retries reached for prompt: " + prompt)
                return "Error"


async def ChatGPT_API_async(model, prompt, api_key=CHATGPT_API_KEY, base_url=None):
    max_retries = 10
    messages = [{"role": "user", "content": prompt}]
    api_key = _resolve_api_key(api_key)
    base_url = _resolve_base_url(base_url)
    for i in range(max_retries):
        try:
            async with _openai_async_client(api_key=api_key, base_url=base_url) as client:
                response = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0,
                )
                return response.choices[0].message.content
        except Exception as e:
            print("************* Retrying *************")
            logging.error(f"Error: {e}")
            if i < max_retries - 1:
                await asyncio.sleep(1)  # Wait for 1s before retrying
            else:
                logging.error("Max retries reached for prompt: " + prompt)
                return "Error"


def get_json_content(response):
    start_idx = response.find("```json")
    if start_idx != -1:
        start_idx += 7
        response = response[start_idx:]

    end_idx = response.rfind("```")
    if end_idx != -1:
        response = response[:end_idx]

    json_content = response.strip()
    return json_content


def extract_json(content):
    """Extract JSON from LLM output with multiple fallback strategies."""
    if not content:
        return {}
    
    json_content = content.strip()
    
    # Strategy 1: Extract from ```json ... ``` code block
    start_idx = json_content.find("```json")
    if start_idx != -1:
        start_idx += 7
        end_idx = json_content.rfind("```")
        if end_idx > start_idx:
            json_content = json_content[start_idx:end_idx].strip()
    else:
        # Try ``` without json tag
        start_idx = json_content.find("```")
        if start_idx != -1:
            start_idx += 3
            end_idx = json_content.rfind("```")
            if end_idx > start_idx:
                json_content = json_content[start_idx:end_idx].strip()
    
    # Strategy 2: Find JSON object or array boundaries
    def find_json_boundaries(text):
        # Find first { or [
        obj_start = text.find('{')
        arr_start = text.find('[')
        
        if obj_start == -1 and arr_start == -1:
            return None
        
        if obj_start == -1:
            start, open_char, close_char = arr_start, '[', ']'
        elif arr_start == -1:
            start, open_char, close_char = obj_start, '{', '}'
        else:
            if obj_start < arr_start:
                start, open_char, close_char = obj_start, '{', '}'
            else:
                start, open_char, close_char = arr_start, '[', ']'
        
        # Find matching closing bracket
        depth = 0
        in_string = False
        escape = False
        for i, c in enumerate(text[start:], start):
            if escape:
                escape = False
                continue
            if c == '\\':
                escape = True
                continue
            if c == '"' and not escape:
                in_string = not in_string
                continue
            if in_string:
                continue
            if c == open_char:
                depth += 1
            elif c == close_char:
                depth -= 1
                if depth == 0:
                    return text[start:i+1]
        return text[start:]  # Return from start even if unbalanced
    
    def try_parse(text):
        """Try to parse with various cleanups."""
        # Clean up common issues
        text = text.replace("None", "null")
        text = text.replace("True", "true").replace("False", "false")
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try removing trailing commas
        import re
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*\]', ']', text)
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try normalizing whitespace (preserve string contents)
        # This is risky for multi-line strings but may help
        try:
            text = ' '.join(text.split())
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        return None
    
    # Try parsing extracted content first
    result = try_parse(json_content)
    if result is not None:
        return result
    
    # Try finding JSON boundaries in original content
    bounded = find_json_boundaries(content)
    if bounded:
        result = try_parse(bounded)
        if result is not None:
            return result
    
    logging.error("Failed to parse JSON from content (len=%d)", len(content))
    return {}


def write_node_id(data, node_id=0):
    if isinstance(data, dict):
        data["node_id"] = str(node_id).zfill(4)
        node_id += 1
        for key in list(data.keys()):
            if "nodes" in key:
                node_id = write_node_id(data[key], node_id)
    elif isinstance(data, list):
        for index in range(len(data)):
            node_id = write_node_id(data[index], node_id)
    return node_id


def get_nodes(structure):
    if isinstance(structure, dict):
        structure_node = copy.deepcopy(structure)
        structure_node.pop("nodes", None)
        nodes = [structure_node]
        for key in list(structure.keys()):
            if "nodes" in key:
                nodes.extend(get_nodes(structure[key]))
        return nodes
    elif isinstance(structure, list):
        nodes = []
        for item in structure:
            nodes.extend(get_nodes(item))
        return nodes


def structure_to_list(structure):
    if isinstance(structure, dict):
        nodes = []
        nodes.append(structure)
        if "nodes" in structure:
            nodes.extend(structure_to_list(structure["nodes"]))
        return nodes
    elif isinstance(structure, list):
        nodes = []
        for item in structure:
            nodes.extend(structure_to_list(item))
        return nodes


def get_leaf_nodes(structure):
    if isinstance(structure, dict):
        if not structure["nodes"]:
            structure_node = copy.deepcopy(structure)
            structure_node.pop("nodes", None)
            return [structure_node]
        else:
            leaf_nodes = []
            for key in list(structure.keys()):
                if "nodes" in key:
                    leaf_nodes.extend(get_leaf_nodes(structure[key]))
            return leaf_nodes
    elif isinstance(structure, list):
        leaf_nodes = []
        for item in structure:
            leaf_nodes.extend(get_leaf_nodes(item))
        return leaf_nodes


def is_leaf_node(data, node_id):
    # Helper function to find the node by its node_id
    def find_node(data, node_id):
        if isinstance(data, dict):
            if data.get("node_id") == node_id:
                return data
            for key in data.keys():
                if "nodes" in key:
                    result = find_node(data[key], node_id)
                    if result:
                        return result
        elif isinstance(data, list):
            for item in data:
                result = find_node(item, node_id)
                if result:
                    return result
        return None

    # Find the node with the given node_id
    node = find_node(data, node_id)

    # Check if the node is a leaf node
    if node and not node.get("nodes"):
        return True
    return False


def get_last_node(structure):
    return structure[-1]


def _open_pdf_for_utils(pdf_path):
    if isinstance(pdf_path, BytesIO):
        return pymupdf.open(stream=pdf_path, filetype="pdf")
    return pymupdf.open(pdf_path)


def extract_text_from_pdf(pdf_path):
    doc = _open_pdf_for_utils(pdf_path)
    try:
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    finally:
        doc.close()


def get_pdf_title(pdf_path):
    doc = _open_pdf_for_utils(pdf_path)
    try:
        meta = doc.metadata or {}
        title = meta.get("title") or "Untitled"
        return title
    finally:
        doc.close()


def get_text_of_pages(pdf_path, start_page, end_page, tag=True):
    doc = _open_pdf_for_utils(pdf_path)
    try:
        text = ""
        for page_num in range(start_page - 1, end_page):
            page_text = doc[page_num].get_text()
            if tag:
                text += (
                    f"<start_index_{page_num+1}>\n{page_text}\n<end_index_{page_num+1}>\n"
                )
            else:
                text += page_text
        return text
    finally:
        doc.close()


def get_first_start_page_from_text(text):
    start_page = -1
    start_page_match = re.search(r"<start_index_(\d+)>", text)
    if start_page_match:
        start_page = int(start_page_match.group(1))
    return start_page


def get_last_start_page_from_text(text):
    start_page = -1
    # Find all matches of start_index tags
    start_page_matches = re.finditer(r"<start_index_(\d+)>", text)
    # Convert iterator to list and get the last match if any exist
    matches_list = list(start_page_matches)
    if matches_list:
        start_page = int(matches_list[-1].group(1))
    return start_page


def sanitize_filename(filename, replacement="-"):
    # In Linux, only '/' and '\0' (null) are invalid in filenames.
    # Null can't be represented in strings, so we only handle '/'.
    return filename.replace("/", replacement)


def get_pdf_name(pdf_path):
    # Extract PDF name
    if isinstance(pdf_path, str):
        pdf_name = os.path.basename(pdf_path)
    elif isinstance(pdf_path, BytesIO):
        doc = _open_pdf_for_utils(pdf_path)
        meta = doc.metadata or {}
        pdf_name = meta.get("title") or "Untitled"
        doc.close()
        pdf_name = sanitize_filename(pdf_name)
    return pdf_name


class JsonLogger:
    def __init__(self, file_path):
        # Extract PDF name for logger name
        pdf_name = get_pdf_name(file_path)

        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f"{pdf_name}_{current_time}.json"
        os.makedirs("./logs", exist_ok=True)
        # Initialize empty list to store all messages
        self.log_data = []

    def log(self, level, message, **kwargs):
        if isinstance(message, dict):
            self.log_data.append(message)
        else:
            self.log_data.append({"message": message})
        # Add new message to the log data

        # Write entire log data to file
        with open(self._filepath(), "w") as f:
            json.dump(self.log_data, f, indent=2)

    def info(self, message, **kwargs):
        self.log("INFO", message, **kwargs)

    def error(self, message, **kwargs):
        self.log("ERROR", message, **kwargs)

    def debug(self, message, **kwargs):
        self.log("DEBUG", message, **kwargs)

    def exception(self, message, **kwargs):
        kwargs["exception"] = True
        self.log("ERROR", message, **kwargs)

    def _filepath(self):
        return os.path.join("logs", self.filename)


def list_to_tree(data):
    def get_parent_structure(structure):
        """Helper function to get the parent structure code"""
        if not structure:
            return None
        parts = str(structure).split(".")
        return ".".join(parts[:-1]) if len(parts) > 1 else None

    # First pass: Create nodes and track parent-child relationships
    nodes = {}
    root_nodes = []

    for item in data:
        structure = item.get("structure")
        node = {
            "title": item.get("title"),
            "start_index": item.get("start_index"),
            "end_index": item.get("end_index"),
            "nodes": [],
        }

        nodes[structure] = node

        # Find parent
        parent_structure = get_parent_structure(structure)

        if parent_structure:
            # Add as child to parent if parent exists
            if parent_structure in nodes:
                nodes[parent_structure]["nodes"].append(node)
            else:
                root_nodes.append(node)
        else:
            # No parent, this is a root node
            root_nodes.append(node)

    # Helper function to clean empty children arrays
    def clean_node(node):
        if not node["nodes"]:
            del node["nodes"]
        else:
            for child in node["nodes"]:
                clean_node(child)
        return node

    # Clean and return the tree
    return [clean_node(node) for node in root_nodes]


def add_preface_if_needed(data):
    if not isinstance(data, list) or not data:
        return data
    if data[0]["physical_index"] is not None and data[0]["physical_index"] > 1:
        preface_node = {
            "structure": "0",
            "title": "Preface",
            "physical_index": 1,
        }
        data.insert(0, preface_node)
    return data


def get_page_tokens(pdf_path, model="gpt-4o-2024-11-20", pdf_parser="PyMuPDF"):
    enc = tiktoken.encoding_for_model(model)
    if pdf_parser not in ("PyMuPDF", "pymupdf", "PyPDF2"):
        raise ValueError(f"Unsupported PDF parser: {pdf_parser}")

    if isinstance(pdf_path, BytesIO):
        doc = pymupdf.open(stream=pdf_path, filetype="pdf")
    elif isinstance(pdf_path, str) and os.path.isfile(pdf_path) and pdf_path.lower().endswith(".pdf"):
        doc = pymupdf.open(pdf_path)
    else:
        raise ValueError("Unsupported input type for PDF")

    page_list = []
    try:
        for page in doc:
            page_text = page.get_text()
            token_length = len(enc.encode(page_text))
            page_list.append((page_text, token_length))
    finally:
        doc.close()
    return page_list


def get_text_of_pdf_pages(pdf_pages, start_page, end_page):
    text = ""
    for page_num in range(start_page - 1, end_page):
        text += pdf_pages[page_num][0]
    return text


def get_text_of_pdf_pages_with_labels(pdf_pages, start_page, end_page):
    text = ""
    for page_num in range(start_page - 1, end_page):
        text += (
            f"<physical_index_{page_num+1}>\n{pdf_pages[page_num][0]}\n<physical_index_{page_num+1}>\n"
        )
    return text


def get_number_of_pages(pdf_path):
    doc = _open_pdf_for_utils(pdf_path)
    try:
        return int(doc.page_count)
    finally:
        doc.close()


def post_processing(structure, end_physical_index):
    # First convert page_number to start_index in flat list
    for i, item in enumerate(structure):
        item["start_index"] = item.get("physical_index")
        if i < len(structure) - 1:
            if structure[i + 1].get("appear_start") == "yes":
                item["end_index"] = structure[i + 1]["physical_index"] - 1
            else:
                item["end_index"] = structure[i + 1]["physical_index"]
        else:
            item["end_index"] = end_physical_index
    tree = list_to_tree(structure)
    if len(tree) != 0:
        return tree
    else:
        ### remove appear_start
        for node in structure:
            node.pop("appear_start", None)
            node.pop("physical_index", None)
        return structure


def clean_structure_post(data):
    if isinstance(data, dict):
        data.pop("page_number", None)
        data.pop("start_index", None)
        data.pop("end_index", None)
        if "nodes" in data:
            clean_structure_post(data["nodes"])
    elif isinstance(data, list):
        for section in data:
            clean_structure_post(section)
    return data


def remove_fields(data, fields=["text"]):
    if isinstance(data, dict):
        return {k: remove_fields(v, fields) for k, v in data.items() if k not in fields}
    elif isinstance(data, list):
        return [remove_fields(item, fields) for item in data]
    return data


def print_toc(tree, indent=0):
    for node in tree:
        print("  " * indent + node["title"])
        if node.get("nodes"):
            print_toc(node["nodes"], indent + 1)


def print_json(data, max_len=40, indent=2):
    def simplify_data(obj):
        if isinstance(obj, dict):
            return {k: simplify_data(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [simplify_data(item) for item in obj]
        elif isinstance(obj, str) and len(obj) > max_len:
            return obj[:max_len] + "..."
        else:
            return obj

    simplified = simplify_data(data)
    print(json.dumps(simplified, indent=indent, ensure_ascii=False))


def remove_structure_text(data):
    if isinstance(data, dict):
        data.pop("text", None)
        if "nodes" in data:
            remove_structure_text(data["nodes"])
    elif isinstance(data, list):
        for item in data:
            remove_structure_text(item)
    return data


def check_token_limit(structure, limit=110000):
    list = structure_to_list(structure)
    for node in list:
        num_tokens = count_tokens(node["text"], model="gpt-4o")
        if num_tokens > limit:
            print(f"Node ID: {node['node_id']} has {num_tokens} tokens")
            print("Start Index:", node["start_index"])
            print("End Index:", node["end_index"])
            print("Title:", node["title"])
            print("\n")


def convert_physical_index_to_int(data):
    if isinstance(data, list):
        for i in range(len(data)):
            # Check if item is a dictionary and has 'physical_index' key
            if isinstance(data[i], dict) and "physical_index" in data[i]:
                if isinstance(data[i]["physical_index"], str):
                    if data[i]["physical_index"].startswith("<physical_index_"):
                        data[i]["physical_index"] = int(
                            data[i]["physical_index"].split("_")[-1].rstrip(">").strip()
                        )
                    elif data[i]["physical_index"].startswith("physical_index_"):
                        data[i]["physical_index"] = int(
                            data[i]["physical_index"].split("_")[-1].strip()
                        )
    elif isinstance(data, str):
        if data.startswith("<physical_index_"):
            data = int(data.split("_")[-1].rstrip(">").strip())
        elif data.startswith("physical_index_"):
            data = int(data.split("_")[-1].strip())
        # Check data is int
        if isinstance(data, int):
            return data
        else:
            return None
    return data


def convert_page_to_int(data):
    for item in data:
        if "page" in item and isinstance(item["page"], str):
            try:
                item["page"] = int(item["page"])
            except ValueError:
                # Keep original value if conversion fails
                pass
    return data


def add_node_text(node, pdf_pages):
    if isinstance(node, dict):
        start_page = node.get("start_index")
        end_page = node.get("end_index")
        node["text"] = get_text_of_pdf_pages(pdf_pages, start_page, end_page)
        if "nodes" in node:
            add_node_text(node["nodes"], pdf_pages)
    elif isinstance(node, list):
        for index in range(len(node)):
            add_node_text(node[index], pdf_pages)
    return


def add_node_text_with_labels(node, pdf_pages):
    if isinstance(node, dict):
        start_page = node.get("start_index")
        end_page = node.get("end_index")
        node["text"] = get_text_of_pdf_pages_with_labels(
            pdf_pages, start_page, end_page
        )
        if "nodes" in node:
            add_node_text_with_labels(node["nodes"], pdf_pages)
    elif isinstance(node, list):
        for index in range(len(node)):
            add_node_text_with_labels(node[index], pdf_pages)
    return


async def generate_node_summary(node, model=None):
    prompt = f"""You are given a part of a document, your task is to generate a description of the partial document about what are main points covered in the partial document.

Partial Document Text: {node['text']}

Directly return the description, do not include any other text.
"""
    response = await ChatGPT_API_async(model, prompt)
    return response


async def generate_summaries_for_structure(structure, model=None):
    nodes = structure_to_list(structure)
    tasks = [generate_node_summary(node, model=model) for node in nodes]
    summaries = await asyncio.gather(*tasks)

    for node, summary in zip(nodes, summaries):
        node["summary"] = summary
    return structure


def create_clean_structure_for_description(structure):
    """
    Create a clean structure for document description generation,
    excluding unnecessary fields like 'text'.
    """
    if isinstance(structure, dict):
        clean_node = {}
        # Only include essential fields for description
        for key in ["title", "node_id", "summary", "prefix_summary"]:
            if key in structure:
                clean_node[key] = structure[key]

        # Recursively process child nodes
        if "nodes" in structure and structure["nodes"]:
            clean_node["nodes"] = create_clean_structure_for_description(
                structure["nodes"]
            )

        return clean_node
    elif isinstance(structure, list):
        return [create_clean_structure_for_description(item) for item in structure]
    else:
        return structure


def generate_doc_description(structure, model=None):
    prompt = f"""Your are an expert in generating descriptions for a document.
You are given a structure of a document. Your task is to generate a one-sentence description for the document, which makes it easy to distinguish the document from other documents.

Document Structure: {structure}

Directly return the description, do not include any other text.
"""
    response = ChatGPT_API(model, prompt)
    return response


def reorder_dict(data, key_order):
    if not key_order:
        return data
    return {key: data[key] for key in key_order if key in data}


def format_structure(structure, order=None):
    if not order:
        return structure
    if isinstance(structure, dict):
        if "nodes" in structure:
            structure["nodes"] = format_structure(structure["nodes"], order)
        if not structure.get("nodes"):
            structure.pop("nodes", None)
        structure = reorder_dict(structure, order)
    elif isinstance(structure, list):
        structure = [format_structure(item, order) for item in structure]
    return structure


class ConfigLoader:
    def __init__(self, default_path: str = None):
        if default_path is None:
            default_path = Path(__file__).parent / "config.yaml"
        self._default_dict = self._load_yaml(default_path)

    @staticmethod
    def _load_yaml(path):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _validate_keys(self, user_dict):
        unknown_keys = set(user_dict) - set(self._default_dict)
        if unknown_keys:
            raise ValueError(f"Unknown config keys: {unknown_keys}")

    def load(self, user_opt=None) -> config:
        """
        Load the configuration, merging user options with default values.
        """
        if user_opt is None:
            user_dict = {}
        elif isinstance(user_opt, config):
            user_dict = vars(user_opt)
        elif isinstance(user_opt, dict):
            user_dict = user_opt
        else:
            raise TypeError("user_opt must be dict, config(SimpleNamespace) or None")

        self._validate_keys(user_dict)
        merged = {**self._default_dict, **user_dict}
        return config(**merged)
