"""Helper utilities for the UltraRAG UI backend."""
from __future__ import annotations

import asyncio
from asyncio import run_coroutine_threadsafe
import importlib.util
import ast
import logging
import sys
import io
import threading
import time
import uuid
from collections import deque
from contextlib import redirect_stdout, redirect_stderr
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from types import ModuleType

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

build_pipeline = None
run_pipeline = None
_CLIENT_IMPORT_ERROR: Optional[str] = None

LOGGER = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
SERVERS_DIR = PROJECT_ROOT / "servers"
PIPELINES_DIR = PROJECT_ROOT / "examples"
LEGACY_PIPELINES_DIR = BASE_DIR / "pipelines"
if LEGACY_PIPELINES_DIR.exists():
    LEGACY_PIPELINES_DIR.mkdir(parents=True, exist_ok=True)

STUBBED_MODULES: set[str] = set()


class RunLogStream:
    def __init__(self, max_entries: int = 2000) -> None:
        self._lock = threading.Lock()
        self._entries: deque[Dict[str, Any]] = deque(maxlen=max_entries)
        self._counter: int = 0
        self._run_id: Optional[str] = None
        self._status: Dict[str, Any] = {
            "state": "idle",
            "result": None,
            "error": None,
            "pipeline": None,
        }
        self._pipeline_name: Optional[str] = None

    def is_running(self) -> bool:
        with self._lock:
            return self._status.get("state") == "running"

    def start(self, pipeline_name: str) -> str:
        with self._lock:
            self._entries.clear()
            self._counter = 0
            self._run_id = f"{int(time.time() * 1000)}-{uuid.uuid4().hex[:6]}"
            self._status = {
                "state": "running",
                "result": None,
                "error": None,
                "pipeline": pipeline_name,
            }
            self._pipeline_name = pipeline_name
            self._append_unlocked(f"开始运行 {pipeline_name}", level="info", system=True)
            return self._run_id

    def _append_unlocked(self, message: str, *, level: str = "info", system: bool = False) -> Dict[str, Any]:
        entry = {
            "id": self._counter,
            "message": message,
            "timestamp": time.time(),
            "run_id": self._run_id,
            "level": level,
            "system": system,
        }
        self._entries.append(entry)
        self._counter += 1
        return entry

    def append(self, message: str, *, level: str = "info", system: bool = False, run_id: Optional[str] = None) -> None:
        if message is None:
            return
        text = str(message)
        if not text:
            return
        text = text.replace("\r\n", "\n")
        with self._lock:
            if self._run_id is None:
                return
            if run_id and run_id != self._run_id:
                return
            parts = text.split("\n")
            for idx, part in enumerate(parts):
                if part == "" and idx == len(parts) - 1:
                    continue
                self._append_unlocked(part, level=level, system=system)

    def finish(self, run_id: str, state: str, *, result: Optional[str] = None, error: Optional[str] = None) -> None:
        with self._lock:
            if self._run_id != run_id:
                return
            self._status = {
                "state": state,
                "result": result,
                "error": error,
                "pipeline": self._pipeline_name,
            }

    def snapshot(self, since: int = -1, run_id: Optional[str] = None) -> Dict[str, Any]:
        with self._lock:
            current_run_id = self._run_id
            reset = bool(run_id and current_run_id and run_id != current_run_id)
            start_from = -1 if reset else since
            entries = [dict(entry) for entry in self._entries if entry["id"] > start_from]
            status = dict(self._status)
        return {
            "entries": entries,
            "run_id": current_run_id,
            "reset": reset,
            "status": status,
        }


class _RunLogWriter(io.TextIOBase):
    def __init__(self, stream: RunLogStream, run_id: str) -> None:
        self._stream = stream
        self._run_id = run_id
        self._buffer: str = ""

    @property
    def encoding(self) -> str:
        return "utf-8"

    def write(self, data: str) -> int:  # type: ignore[override]
        if not data:
            return 0
        text = str(data).replace("\r\n", "\n")
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            if line:
                self._stream.append(line, run_id=self._run_id)
        return len(data)

    def flush(self) -> None:  # type: ignore[override]
        if self._buffer:
            self._stream.append(self._buffer, run_id=self._run_id)
            self._buffer = ""


RUN_LOG_STREAM = RunLogStream()
RUN_EXECUTOR = ThreadPoolExecutor(max_workers=1)


def _summarize_result(result: Any) -> Optional[str]:
    if result is None:
        return None
    if isinstance(result, (str, int, float, bool)):
        return str(result)
    try:
        rendered = yaml.safe_dump(result, sort_keys=False, allow_unicode=True).strip()
        return rendered or None
    except Exception:  # pragma: no cover - fallback repr
        return repr(result)


def _execute_run_task(name: str, run_id: str) -> None:
    root_logger = logging.getLogger()
    writer = _RunLogWriter(RUN_LOG_STREAM, run_id)
    handler = logging.StreamHandler(writer)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(handler)
    try:
        config_file = _find_pipeline_file(name)
        if config_file is None:
            RUN_LOG_STREAM.append(f"未找到 Pipeline {name}", level="error", system=True, run_id=run_id)
            RUN_LOG_STREAM.finish(run_id, "failed", error="pipeline-not-found")
            return
        RUN_LOG_STREAM.append(f"使用配置文件: {config_file}", system=True, run_id=run_id)
        try:
            _, run_func = _ensure_client_funcs()
        except Exception as exc:  # pragma: no cover - dependency issues
            writer.flush()
            RUN_LOG_STREAM.append(f"无法加载运行环境: {exc}", level="error", system=True, run_id=run_id)
            RUN_LOG_STREAM.finish(run_id, "failed", error=str(exc))
            return
        try:
            with redirect_stdout(writer), redirect_stderr(writer):
                result = _run_async(run_func(str(config_file)))
        except Exception as exc:
            writer.flush()
            RUN_LOG_STREAM.append(f"运行过程中出现异常: {exc}", level="error", system=True, run_id=run_id)
            RUN_LOG_STREAM.finish(run_id, "failed", error=str(exc))
            return
        writer.flush()
        summary = _summarize_result(result)
        if summary:
            RUN_LOG_STREAM.append(f"运行结果: {summary}", system=True, run_id=run_id)
        RUN_LOG_STREAM.append("Pipeline 运行完成", system=True, run_id=run_id)
        RUN_LOG_STREAM.finish(run_id, "succeeded", result=summary)
    finally:
        root_logger.removeHandler(handler)

def _missing_dependency(module_name: str):
    def _stub(*_args, **_kwargs):
        raise ImportError(
            f"Optional dependency '{module_name}' is required by this server."
        )

    return _stub


AsyncEngineArrayStub = type(
    "AsyncEngineArrayStub",
    (),
    {
        "from_args": classmethod(
            lambda cls, *a, **kw: (_missing_dependency("infinity_emb"))(*a, **kw)
        )
    },
)

EngineArgsStub = type(
    "EngineArgsStub",
    (),
    {
        "__init__": lambda self, *_a, **_kw: None,
    },
)


class LoggerStub:
    def setLevel(self, *_args, **_kwargs):
        return None


LOGGER_STUB_INSTANCE = LoggerStub()

OPTIONAL_MODULE_ATTRS: Dict[str, Dict[str, Any]] = {
    "jsonlines": {"open": _missing_dependency("jsonlines")},
    "infinity_emb": {
        "AsyncEngineArray": AsyncEngineArrayStub,
        "EngineArgs": EngineArgsStub,
    },
    "infinity_emb.log_handler": {
        "LOG_LEVELS": {"warning": "warning"},
        "logger": LOGGER_STUB_INSTANCE,
    },
    "exa_py": {"Client": lambda *a, **kw: (_missing_dependency("exa_py"))(*a, **kw)},
    "tavily": {},
    "tavily.tavily": {},
    "tavily.client": {"TavilyClient": lambda *a, **kw: (_missing_dependency("tavily"))(*a, **kw)},
}


def _ensure_stub_module(fullname: str):
    if fullname in sys.modules:
        return sys.modules[fullname]
    parts = fullname.split(".")
    current = []
    for part in parts:
        current.append(part)
        name = ".".join(current)
        if name not in sys.modules:
            module = ModuleType(name)
            module.__dict__.setdefault("__path__", [])
            sys.modules[name] = module
            if len(current) > 1:
                parent_name = ".".join(current[:-1])
                setattr(sys.modules[parent_name], current[-1], module)
    module = sys.modules[fullname]
    for attr, value in OPTIONAL_MODULE_ATTRS.get(fullname, {}).items():
        setattr(module, attr, value)
    return module


def _flatten_param_keys(data: Any, prefix: str = "") -> set[str]:
    keys: set[str] = set()
    if isinstance(data, dict):
        for key, value in data.items():
            path = f"{prefix}.{key}" if prefix else key
            keys.add(path)
            keys |= _flatten_param_keys(value, path)
    return keys


def _generate_server_stub(server_dir: Path, module_path: Path, parameter_path: Path) -> Dict[str, Any]:
    try:
        source = module_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise PipelineManagerError(f"Server module not found: {module_path}")

    tree = ast.parse(source, filename=str(module_path))
    functions: Dict[str, List[str]] = {}

    class FuncVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef):
            args = [arg.arg for arg in node.args.args if arg.arg != "self"]
            functions[node.name] = args

    FuncVisitor().visit(tree)

    param_keys: set[str] = set()
    if parameter_path.exists():
        try:
            param_data = yaml.safe_load(parameter_path.read_text(encoding="utf-8")) or {}
            param_keys = {k.split(".")[0] for k in _flatten_param_keys(param_data)}
        except yaml.YAMLError:
            param_keys = set()

    tools: Dict[str, Dict[str, Any]] = {}
    prompts: Dict[str, Dict[str, Any]] = {}

    class CallVisitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr in {"tool", "prompt"}:
                tool_name = None
                if node.args:
                    first = node.args[0]
                    if isinstance(first, ast.Attribute):
                        tool_name = first.attr
                    elif isinstance(first, ast.Name):
                        tool_name = first.id
                if not tool_name:
                    return
                output_spec = None
                for kw in node.keywords:
                    if kw.arg == "output" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                        output_spec = kw.value.value
                        break

                args = functions.get(tool_name, [])
                input_mapping: Dict[str, Any] = {}
                for arg in args:
                    if arg in param_keys:
                        input_mapping[arg] = f"${arg}"
                    else:
                        input_mapping[arg] = arg

                outputs: List[str] = []
                if output_spec:
                    out_part = output_spec.split("->", 1)[-1]
                    outputs = [item.strip() for item in out_part.split(",") if item.strip() and item.strip().lower() != "none"]

                target = prompts if node.func.attr == "prompt" else tools
                entry: Dict[str, Any] = {"input": input_mapping}
                if outputs:
                    entry["output"] = outputs
                target[tool_name] = entry

    CallVisitor().visit(tree)

    if not tools and not prompts:
        raise PipelineManagerError(f"Unable to infer tools for server {server_dir.name}")

    return {
        "path": str(module_path),
        "parameter": str(parameter_path),
        "tools": tools,
        "prompts": prompts,
    }


class PipelineManagerError(RuntimeError):
    """Raised when UI pipeline management actions fail."""


def _ensure_client_funcs():
    global build_pipeline, run_pipeline, _CLIENT_IMPORT_ERROR
    if build_pipeline and run_pipeline:
        return build_pipeline, run_pipeline
    try:
        from ultrarag.client import build as _build, run as _run
    except ModuleNotFoundError as exc:
        missing = exc.name or "fastmcp"
        if missing == "dotenv":
            dotenv_stub = ModuleType("dotenv")
            dotenv_stub.load_dotenv = lambda *args, **kwargs: None
            sys.modules["dotenv"] = dotenv_stub
            from ultrarag.client import build as _build, run as _run
        else:
            _CLIENT_IMPORT_ERROR = missing
            raise PipelineManagerError(
                f"UltraRAG client 依赖缺失：{missing}。请安装项目依赖后再使用构建/运行功能。"
            ) from exc
    build_pipeline = _build
    run_pipeline = _run
    return build_pipeline, run_pipeline


@dataclass
class ServerTool:
    server: str
    tool: str
    kind: str  # "tool" or "prompt"
    input_spec: Dict[str, str]
    output_spec: List[str]

    @property
    def identifier(self) -> str:
        return f"{self.server}.{self.tool}"


@dataclass
class PipelineDefinition:
    name: str
    description: Optional[str]
    steps: List[Any]

    def _collect_servers(self, steps: List[Any]) -> set[str]:
        servers: set[str] = set()
        for step in steps:
            if isinstance(step, str):
                if "." in step:
                    servers.add(step.split(".")[0])
            elif isinstance(step, dict):
                for key, value in step.items():
                    if isinstance(key, str) and "." in key:
                        servers.add(key.split(".")[0])
                    if isinstance(value, dict):
                        if "steps" in value and isinstance(value["steps"], list):
                            servers |= self._collect_servers(value["steps"])
                        if "branches" in value and isinstance(value["branches"], dict):
                            for branch_steps in value["branches"].values():
                                if isinstance(branch_steps, list):
                                    servers |= self._collect_servers(branch_steps)
                        if "router" in value and isinstance(value["router"], list):
                            servers |= self._collect_servers(value["router"])
        return servers

    def to_yaml_payload(self) -> Dict[str, Any]:
        server_names = sorted(self._collect_servers(self.steps))
        servers = {name: f"servers/{name}" for name in server_names}
        return {
            "name": self.name,
            "description": self.description or "",
            "servers": servers,
            "pipeline": self.steps,
        }


def _load_module_from_path(server_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(f"ultrarag_ui_{server_name}", file_path)
    if spec is None or spec.loader is None:
        raise PipelineManagerError(f"Cannot load server module for {server_name}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
    except ModuleNotFoundError as exc:
        missing = exc.name or ""
        if not missing or missing in STUBBED_MODULES:
            raise PipelineManagerError(
                f"Failed to import server {server_name}: missing dependency '{missing}'"
            ) from exc
        STUBBED_MODULES.add(missing)
        _ensure_stub_module(missing)
        return _load_module_from_path(server_name, file_path)
    except Exception as exc:  # pragma: no cover - bubble up
        raise PipelineManagerError(f"Failed to import server {server_name}: {exc}") from exc
    return module


def _ensure_server_yaml(server_dir: Path) -> Dict[str, Any]:
    server_name = server_dir.name
    parameter_path = server_dir / "parameter.yaml"
    module_path = server_dir / "src" / f"{server_name}.py"
    server_yaml_path = server_dir / "server.yaml"

    def load_yaml(path: Path) -> Optional[Dict[str, Any]]:
        if not path.exists():
            return None
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            return data if isinstance(data, dict) else None
        except yaml.YAMLError:
            LOGGER.warning("Failed to parse %s", path)
            return None

    cached_cfg = load_yaml(server_yaml_path)

    if not module_path.exists():
        if cached_cfg is not None:
            LOGGER.warning(
                "Server %s missing source module, using cached server.yaml", server_name
            )
            return cached_cfg
        raise PipelineManagerError(f"Server module not found: {module_path}")

    needs_rebuild = not server_yaml_path.exists()
    if not needs_rebuild and parameter_path.exists():
        needs_rebuild = server_yaml_path.stat().st_mtime < parameter_path.stat().st_mtime

    if needs_rebuild:
        try:
            module = _load_module_from_path(server_name, module_path)
            app = getattr(module, "app", None)
            if app is None:
                raise PipelineManagerError(
                    f"Server {server_name} missing 'app' instance"
                )
            LOGGER.info("Building server.yaml for %s", server_name)
            app.build(str(parameter_path))
        except PipelineManagerError as exc:
            if cached_cfg is not None:
                LOGGER.warning(
                    "Falling back to cached server.yaml for %s due to error: %s",
                    server_name,
                    exc,
                )
                return cached_cfg
            raise
        except Exception as exc:
            LOGGER.warning(
                "Unable to build server %s (%s), attempting stub", server_name, exc
            )
            try:
                return _generate_server_stub(server_dir, module_path, parameter_path)
            except Exception as stub_exc:
                if cached_cfg is not None:
                    LOGGER.warning(
                        "Using cached server.yaml for %s despite build errors", server_name
                    )
                    return cached_cfg
                raise PipelineManagerError(
                    f"Unable to build server {server_name}: {exc}"
                ) from stub_exc

    final_cfg = load_yaml(server_yaml_path)
    if final_cfg and (final_cfg.get("tools") or final_cfg.get("prompts")):
        return final_cfg

    LOGGER.warning(
        "Server %s metadata incomplete; generating stub from source", server_name
    )
    return _generate_server_stub(server_dir, module_path, parameter_path)


def list_servers() -> Dict[str, Dict[str, Any]]:
    servers: Dict[str, Dict[str, Any]] = {}
    for server_dir in sorted(SERVERS_DIR.iterdir()):
        if not server_dir.is_dir():
            continue
        try:
            cfg = _ensure_server_yaml(server_dir)
            if not isinstance(cfg, dict):
                LOGGER.warning("Server %s returned no configuration", server_dir.name)
                continue
            servers[server_dir.name] = cfg
        except PipelineManagerError as exc:
            LOGGER.warning("Skipping server %s: %s", server_dir.name, exc)
    return servers


def list_server_tools() -> List[ServerTool]:
    tools: List[ServerTool] = []
    servers = list_servers()
    for server, cfg in servers.items():
        if not isinstance(cfg, dict):
            LOGGER.warning("Skipping server %s due to invalid config type: %s", server, type(cfg).__name__)
            continue
        for tool_name, meta in (cfg.get("tools") or {}).items():
            tools.append(
                ServerTool(
                    server=server,
                    tool=tool_name,
                    kind="tool",
                    input_spec=meta.get("input", {}) or {},
                    output_spec=meta.get("output", []) or [],
                )
            )
        for prompt_name, meta in (cfg.get("prompts") or {}).items():
            tools.append(
                ServerTool(
                    server=server,
                    tool=prompt_name,
                    kind="prompt",
                    input_spec=meta.get("input", {}) or {},
                    output_spec=meta.get("output", []) or [],
                )
            )
    return tools


def pipeline_path(name: str) -> Path:
    safe_name = name.replace("..", "_")
    return PIPELINES_DIR / f"{safe_name}.yaml"


def _find_pipeline_file(name: str) -> Path | None:
    primary = pipeline_path(name)
    if primary.exists():
        return primary
    legacy = LEGACY_PIPELINES_DIR / f"{name}.yaml"
    if legacy.exists():
        return legacy
    return None


def load_pipeline(name: str) -> Dict[str, Any]:
    path = _find_pipeline_file(name)
    if path is None:
        raise PipelineManagerError(f"Pipeline {name} not found")
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _iter_pipeline_files() -> List[Path]:
    files = list(PIPELINES_DIR.glob("*.yaml"))
    if LEGACY_PIPELINES_DIR.exists():
        files.extend(f for f in LEGACY_PIPELINES_DIR.glob("*.yaml") if f.stem not in {p.stem for p in files})
    return sorted(files)


def list_pipelines() -> List[Dict[str, Any]]:
    pipelines: List[Dict[str, Any]] = []
    for yaml_file in _iter_pipeline_files():
        with yaml_file.open("r", encoding="utf-8") as handle:
            cfg = yaml.safe_load(handle) or {}
        pipelines.append({"name": yaml_file.stem, "config": cfg})
    return pipelines


def save_pipeline(payload: Dict[str, Any]) -> Dict[str, Any]:
    name = payload.get("name")
    steps = payload.get("pipeline") or []
    description = payload.get("description")
    if not name or not isinstance(name, str):
        raise PipelineManagerError("Pipeline name is required")
    if not isinstance(steps, list) or not steps:
        raise PipelineManagerError("Pipeline must contain at least one step")

    definition = PipelineDefinition(name=name, description=description, steps=steps)
    yaml_payload = definition.to_yaml_payload()
    path = pipeline_path(name)
    print(f"save in: {path}")
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(yaml_payload, handle, sort_keys=False, allow_unicode=True)
    return yaml_payload


def delete_pipeline(name: str) -> None:
    path = _find_pipeline_file(name)
    if path and path.exists():
        path.unlink()


def _run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        return run_coroutine_threadsafe(coro, loop).result()
    return asyncio.run(coro)


def build(name: str) -> Dict[str, Any]:
    config_file = _find_pipeline_file(name)
    if config_file is None:
        raise PipelineManagerError(f"Pipeline {name} not found")
    LOGGER.info("Building pipeline %s", name)
    build_func, _ = _ensure_client_funcs()
    _run_async(build_func(str(config_file)))
    return {"status": "ok"}


def run(name: str, *, wait: bool = False) -> Dict[str, Any]:
    if not wait and RUN_LOG_STREAM.is_running():
        raise PipelineManagerError("已有 Pipeline 正在运行，请稍候再试")
    LOGGER.info("Running pipeline %s", name)
    run_id = RUN_LOG_STREAM.start(name)
    if wait:
        _execute_run_task(name, run_id)
        snapshot = RUN_LOG_STREAM.snapshot()
        status = snapshot.get("status", {})
        return {
            "status": status.get("state", "unknown"),
            "run_id": run_id,
            "result": status.get("result"),
            "error": status.get("error"),
        }
    RUN_EXECUTOR.submit(_execute_run_task, name, run_id)
    return {"status": "started", "run_id": run_id}


def _parameter_candidates(config_file: Path) -> List[Path]:
    base_name = config_file.stem
    primary = config_file.parent / "parameter" / f"{base_name}_parameter.yaml"
    examples_param = PIPELINES_DIR / "parameter" / f"{base_name}_parameter.yaml"
    candidates: List[Path] = [primary]
    if examples_param != primary:
        candidates.append(examples_param)
    # ensure uniqueness while preserving order
    unique: List[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        if candidate not in seen:
            unique.append(candidate)
            seen.add(candidate)
    return unique


def _resolve_parameter_path(name: str, *, for_write: bool = False) -> Path:
    config_file = _find_pipeline_file(name)
    if config_file is None:
        raise PipelineManagerError(f"Pipeline {name} not found")
    candidates = _parameter_candidates(config_file)
    if not for_write:
        for candidate in candidates:
            if candidate.exists():
                return candidate
    # fall back to the first candidate that has an existing directory or can be created
    for candidate in candidates:
        if candidate.parent.exists() or for_write:
            return candidate
    return candidates[0]


def parameter_file(name: str) -> Path:
    return _resolve_parameter_path(name, for_write=False)


def load_parameters(name: str) -> Dict[str, Any]:
    param_path = parameter_file(name)
    if not param_path.exists():
        raise PipelineManagerError("Parameters not available; build the pipeline first")
    LOGGER.info("Loading parameters for %s from %s", name, param_path)
    with param_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def save_parameters(name: str, params: Dict[str, Any]) -> None:
    param_path = _resolve_parameter_path(name, for_write=True)
    param_path.parent.mkdir(parents=True, exist_ok=True)
    LOGGER.info("Saving parameters for %s to %s", name, param_path)
    with param_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(params, handle, sort_keys=False, allow_unicode=True)


def fetch_run_logs(since: int = -1, run_id: Optional[str] = None) -> Dict[str, Any]:
    return RUN_LOG_STREAM.snapshot(since=since, run_id=run_id)
