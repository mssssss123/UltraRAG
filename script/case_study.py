# python ./script/case_study.py --data output/memory.json --host 0.0.0.0 --port 8080 --title "Case Study Viewer"


import argparse
import json
import os
from typing import Any, List

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Case Study Viewer Service")


class State:
    data_path: str = ""
    title: str = "Case Study Viewer"
    cases: List[List[dict]] = []


STATE = State()


def load_cases(path: str) -> List[List[dict]]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input file not found: {path}")

    def is_step(d: Any) -> bool:
        return isinstance(d, dict) and ("step" in d) and ("memory" in d)

    def is_case(obj: Any) -> bool:
        return isinstance(obj, list) and all(is_step(x) for x in obj)

    def normalize_case(obj: Any) -> List[dict] | None:
        if is_case(obj):
            return obj
        if isinstance(obj, dict):
            for k in ("steps", "case"):
                if k in obj and is_case(obj[k]):
                    return obj[k]
        return None

    def unwrap_container(obj: Any) -> Any:
        if isinstance(obj, dict):
            for k in (
                "cases",
                "data",
                "items",
                "dataset",
                "results",
                "records",
                "list",
            ):
                if k in obj:
                    return obj[k]
        return obj

    txt = open(path, "r", encoding="utf-8").read().strip()
    try:
        obj = json.loads(txt)
        obj = unwrap_container(obj)

        c = normalize_case(obj)
        if c is not None:
            return [c]

        if isinstance(obj, list):
            out: List[List[dict]] = []
            for elem in obj:
                elem = unwrap_container(elem)
                c = normalize_case(elem)
                if c is None:
                    raise ValueError(
                        "Dataset element is not a valid case; expected a list of {step,memory} or an object with 'steps'."
                    )
                out.append(c)
            if out:
                return out
    except Exception:
        pass

    out: List[List[dict]] = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception as e:
                raise ValueError(f"Line {i} invalid JSON: {e}")
            obj = unwrap_container(obj)
            c = normalize_case(obj)
            if c is None:
                raise ValueError(
                    f"Line {i} is not a valid case (expect steps list or object with 'steps')."
                )
            out.append(c)
    if not out:
        raise ValueError("No valid cases found.")
    return out


def _estimate_case_count_from_steps(steps: List[dict]) -> int:
    max_len = 1
    for st in steps:
        mem = st.get("memory", {}) if isinstance(st, dict) else {}
        if isinstance(mem, dict):
            for v in mem.values():
                if isinstance(v, list):
                    max_len = max(max_len, len(v))
    return max_len


def _slice_case_by_index(steps: List[dict], idx: int) -> List[dict]:
    out_steps: List[dict] = []
    for st in steps:
        step_name = st.get("step")
        mem = st.get("memory", {})
        new_mem = {}
        if isinstance(mem, dict):
            for k, v in mem.items():
                if isinstance(v, list):
                    new_mem[k] = v[idx] if 0 <= idx < len(v) else None
                else:
                    new_mem[k] = v
        out_steps.append({"step": step_name, "memory": new_mem})
    return out_steps


def _expand_cases_if_needed(cases: List[List[dict]]) -> List[List[dict]]:
    expanded: List[List[dict]] = []
    for steps in cases:
        n = _estimate_case_count_from_steps(steps)
        if n <= 1:
            expanded.append(steps)
        else:
            for i in range(n):
                expanded.append(_slice_case_by_index(steps, i))
    return expanded


def escape_html(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


CSS = r"""
:root {
  --bg: #0b1020;
  --card: #131b33;
  --muted: #99a3c7;
  --text: #e8ecff;
  --accent: #7aa2ff;
  --accent-2: #61d5c7;
  --border: #273056;
  --shadow: rgba(0,0,0,0.35);
}
* { box-sizing: border-box; }
html, body {
  margin: 0;
  height: 100%;
  background: linear-gradient(180deg, #0a0f1f, #0e1330);
  color: var(--text);
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji";
}
.container {
  max-width: 1200px;
  margin: 24px auto 80px auto;
  padding: 0 16px;
}
.topbar {
  position: sticky; top: 0; z-index: 20;
  backdrop-filter: blur(8px);
  background: rgba(10,15,31,0.6);
  border-bottom: 1px solid var(--border);
  padding: 10px 16px;
  display: flex; align-items: center; gap: 12px;
}
.title { font-size: 18px; font-weight: 700; letter-spacing: .3px; }
.counter { color: var(--muted); font-size: 14px; margin-left: auto; }
.btn {
  appearance: none; border: 1px solid var(--border);
  background: linear-gradient(180deg, #162145, #121a36);
  color: var(--text); padding: 6px 12px; border-radius: 12px;
  box-shadow: 0 8px 24px var(--shadow); cursor: pointer; font-weight: 600;
  transition: transform .06s ease, border-color .2s ease;
}
.btn:hover { transform: translateY(-1px); border-color: var(--accent); }
.btn:active { transform: translateY(0); }
.grid { display: grid; grid-template-columns: 1fr; gap: 16px; }
.card {
  background: linear-gradient(180deg, #121938, #101630);
  border: 1px solid var(--border);
  border-radius: 16px; padding: 14px 14px;
  box-shadow: 0 12px 40px var(--shadow);
}
.badge {
  display: inline-flex; align-items: center; gap: 6px;
  background: linear-gradient(180deg, #182255, #142047);
  border: 1px solid var(--border);
  color: var(--accent-2);
  padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 700;
  letter-spacing: .3px;
}
.step-head {
  display: flex; align-items: center; justify-content: space-between;
  cursor: pointer; user-select: none;
}
.step-name { font-size: 16px; font-weight: 800; }
.step-meta { color: var(--muted); font-size: 12px; }
.chev { transition: transform .2s ease; opacity: .8; }
.chev.open { transform: rotate(90deg); }
.content { margin-top: 10px; display: none; }
.content.open { display: block; }
pre {
  margin: 0; padding: 12px; border-radius: 12px;
  background: #0c1125; border: 1px solid var(--border);
  overflow: auto; font-size: 13px; line-height: 1.55;
  white-space: pre-wrap; word-wrap: break-word;
}
.row { display: grid; grid-template-columns: 180px 1fr; gap: 10px; align-items: start; }
.key { color: var(--muted); font-weight: 700; padding-top: 6px; }
.copy {
  margin-left: 8px; font-size: 11px; padding: 2px 8px;
  border-radius: 999px; border: 1px solid var(--border);
  background: #0f1630; color: var(--muted); cursor: pointer;
}
.pill {
  display: inline-block; padding: 2px 8px; font-size: 12px; border-radius: 999px;
  background: #0d1532; border: 1px solid var(--border); color: var(--accent);
  margin-left: 8px;
}
.muted { color: var(--muted); }
.small { font-size: 12px; }
.divider { height: 1px; background: var(--border); margin: 10px 0; opacity: .6; }
.footer { color: var(--muted); text-align: center; padding: 24px 8px; }
"""

INDEX_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<style>{css}</style>
</head>
<body>
  <div class="topbar">
    <div class="title">{title}</div>
    <div style="display:flex;gap:8px;margin-left:12px;">
      <button id="prev" class="btn">← 上一条</button>
      <button id="next" class="btn">下一条 →</button>
    </div>
    <div id="counter" class="counter">Case 1 / 1</div>
  </div>

  <div class="container">
    <div id="cases"></div>
  </div>

  <div class="footer small">
    Tips：点击步骤标题可折叠/展开；支持键盘 ← → 切换；URL 支持 #case-<index> 直达；<a href="/api/reload" style="color:#7aa2ff;text-decoration:none;">/api/reload</a> 可热加载最新数据。
  </div>

<script>
const state = { idx: 0, cases: [] };

function $(sel, root=document){ return root.querySelector(sel); }
function $all(sel, root=document){ return Array.from(root.querySelectorAll(sel)); }

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

async function fetchCases() {
  const res = await fetch('/api/cases');
  if (!res.ok) throw new Error('Failed to load cases');
  const data = await res.json();
  state.cases = data.cases || [];
}

function parseHash() {
  if (location.hash.startsWith("#case-")) {
    const n = parseInt(location.hash.replace("#case-", ""), 10);
    if (!Number.isNaN(n)) state.idx = n;
  }
}

function setHash() {
  history.replaceState(null, "", `#case-${state.idx}`);
}

function render() {
  const container = $("#cases");
  let idx = state.idx;
  const casesCount = Array.isArray(state.cases) ? state.cases.length : 0;

  if (casesCount === 0) {
    $("#counter").textContent = `Case 0 / 0`;
    container.innerHTML = '<div class="card"><div class="muted small">没有加载到任何 case（/api/cases 返回为空）。</div></div>';
    $("#prev").disabled = true;
    $("#next").disabled = true;
    return;
  }

  if (idx < 0) idx = 0;
  if (idx > casesCount - 1) idx = casesCount - 1;
  state.idx = idx;

  $("#counter").textContent = `Case ${idx+1} / ${casesCount}`;

  const steps = state.cases[idx] || [];
  const caseBox = document.createElement("div");

  const stepNames = steps.map(s => (s && s.step) ? s.step : "unknown");
  const summaryCard = document.createElement("div");
  summaryCard.className = "card";
  summaryCard.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;">
      <div class="step-name">步骤概览</div>
      <div class="muted small">共 ${steps.length} 步</div>
    </div>
    <div class="divider"></div>
    <div class="muted small">${stepNames.map(n => `<span class="pill">${escapeHtml(n)}</span>`).join(" ") || "—"}</div>
  `;
  caseBox.appendChild(summaryCard);

  steps.forEach((st, i) => {
    const card = document.createElement("div");
    card.className = "card";

    const stepName = String((st && st.step) != null ? st.step : "unknown");
    const memory = (st && st.memory) != null ? st.memory : {};

    const head = document.createElement("div");
    head.className = "step-head";
    head.innerHTML = `
      <div>
        <div class="step-name">${escapeHtml(stepName)}</div>
        <div class="step-meta">Step ${i+1}</div>
      </div>
      <div class="chev ${i < 2 ? "open": ""}">▶</div>
    `;

    const content = document.createElement("div");
    content.className = "content " + (i < 2 ? "open" : "");

    const memoryKeys = Object.keys(memory);
    if (memoryKeys.length === 0) {
      content.innerHTML = `<div class="muted small">No memory</div>`;
    } else {
      const wrap = document.createElement("div");
      wrap.className = "grid";
      memoryKeys.forEach(function(k){
        var val = memory[k];
        var dataKey = k;  // 当前 case 内唯一 key

        const row = document.createElement("div");
        row.className = "row";

        // 左侧 key
        const keyDiv = document.createElement("div");
        keyDiv.className = "key";
        keyDiv.textContent = k;

        // 右侧容器
        const right = document.createElement("div");

        const headBar = document.createElement("div");
        headBar.style = "display:flex;align-items:center;justify-content:space-between;";
        const badge = document.createElement("div");
        badge.className = "badge";
        badge.textContent = "JSON";
        const copyBtn = document.createElement("button");
        copyBtn.className = "copy";
        copyBtn.setAttribute("data-key", dataKey);
        copyBtn.textContent = "复制";
        headBar.appendChild(badge);
        headBar.appendChild(copyBtn);

        // 内容区域：根据类型决定如何渲染，确保字符串按原样显示（含换行），不出现多余反斜杠
        const pre = document.createElement("pre");
        pre.className = "pre-json";
        pre.setAttribute("data-key", dataKey);

        var isStringArray = Array.isArray(val) && val.every(function(x){ return typeof x === "string"; });
        var prettyText;
        if (typeof val === "string") {
          // 字符串：直接原样显示，保留换行
          prettyText = val;
        } else if (isStringArray) {
          // 字符串数组：合并为多行，避免 \" 和 \n 的转义显示
          prettyText = val.join("\n");
        } else {
          // 其他类型：用 JSON 格式化
          try {
            prettyText = JSON.stringify(val, null, 2);
          } catch (e) {
            // 兜底
            prettyText = String(val);
          }
        }
        pre.textContent = prettyText;

        // 拼装
        right.appendChild(headBar);
        right.appendChild(pre);
        row.appendChild(keyDiv);
        row.appendChild(right);

        wrap.appendChild(row);
      });
      content.appendChild(wrap);
    }

    head.addEventListener("click", () => {
      content.classList.toggle("open");
      const chev = head.querySelector(".chev");
      chev.classList.toggle("open");
    });

    card.appendChild(head);
    card.appendChild(content);
    caseBox.appendChild(card);
  });

  container.innerHTML = "";
  container.appendChild(caseBox);

  // 复制
  $all(".copy", caseBox).forEach(btn => {
    btn.addEventListener("click", () => {
      const key = btn.getAttribute("data-key");
      const pre = caseBox.querySelector('.pre-json[data-key="' + CSS.escape(key) + '"]');
      if (!pre) return;
      navigator.clipboard.writeText(pre.textContent || "").then(() => {
        btn.textContent = "已复制";
        setTimeout(() => { btn.textContent = "复制"; }, 1200);
      });
    });
  });

  setHash();
  $("#prev").disabled = (state.idx === 0);
  $("#next").disabled = (state.idx >= casesCount - 1);
}

function goto(delta) {
  const total = Array.isArray(state.cases) ? state.cases.length : 0;
  if (total === 0) return;
  let n = state.idx + delta;
  if (n < 0) n = 0;
  if (n > total - 1) n = total - 1;
  if (n === state.idx) return;
  state.idx = n;
  render();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function main() {
  await fetchCases();
  parseHash();
  if (!Array.isArray(state.cases)) state.cases = [];
  if (state.cases.length === 0) {
    // 空状态
  } else {
    if (state.idx < 0) state.idx = 0;
    if (state.idx > state.cases.length - 1) state.idx = state.cases.length - 1;
    history.replaceState(null, "", `#case-${state.idx}`);
  }
  $("#prev").addEventListener("click", () => goto(-1));
  $("#next").addEventListener("click", () => goto(1));
  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") goto(-1);
    if (e.key === "ArrowRight") goto(1);
  });
  render();
}

window.addEventListener("DOMContentLoaded", main);
window.addEventListener("hashchange", () => { parseHash(); render(); });
</script>
</body>
</html>
""".replace(
    "{css}", CSS
)


@app.get("/", response_class=HTMLResponse)
def index():
    html = INDEX_HTML.replace("{title}", escape_html(STATE.title))
    return HTMLResponse(html)


@app.get("/api/cases")
def api_cases():
    return JSONResponse({"count": len(STATE.cases), "cases": STATE.cases})


@app.get("/api/reload")
def api_reload():
    try:
        STATE.cases = load_cases(STATE.data_path)
        return JSONResponse({"ok": True, "count": len(STATE.cases), "msg": "reloaded"})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.get("/health")
def health():
    return PlainTextResponse("ok")


def parse_args():
    p = argparse.ArgumentParser(
        description="Run a local web service to view case study data."
    )
    p.add_argument(
        "--data",
        "-d",
        required=True,
        help="数据文件路径（.json / .jsonl / 单个 case 的 JSON）",
    )
    p.add_argument("--host", default="127.0.0.1", help="绑定地址，默认 127.0.0.1")
    p.add_argument("--port", type=int, default=8080, help="端口，默认 8080")
    p.add_argument("--title", "-t", default="Case Study Viewer", help="页面标题")
    return p.parse_args()


def main():
    args = parse_args()
    STATE.data_path = args.data
    STATE.title = args.title
    try:
        STATE.cases = _expand_cases_if_needed(load_cases(STATE.data_path))
    except Exception as e:
        raise SystemExit(f"!!! 加载数据失败: {e}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    print(f"[OK] Loaded cases: {len(STATE.cases)} from {STATE.data_path}")
    print(f"[OK] Open: http://{args.host}:{args.port}/")
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
