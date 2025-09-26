const state = {
  selectedPipeline: null,
  steps: [],
  contextStack: [],
  toolCatalog: { order: [], byServer: {} },
  parameterData: null,
  editingPath: null,
  isBuilt: false,
  parametersReady: false,
  mode: "builder",
  logStream: { runId: null, lastId: -1, timer: null, status: "idle" },
};

const LOG_POLL_INTERVAL = 1500;

const els = {
  log: document.getElementById("log"),
  pipelineForm: document.getElementById("pipeline-form"),
  name: document.getElementById("pipeline-name"),
  flowCanvas: document.getElementById("flow-canvas"),
  contextControls: document.getElementById("context-controls"),
  pipelinePreview: document.getElementById("pipeline-preview"),
  stepEditor: document.getElementById("step-editor"),
  stepEditorValue: document.getElementById("step-editor-value"),
  clearSteps: document.getElementById("clear-steps"),
  savePipeline: document.getElementById("save-pipeline"),
  buildPipeline: document.getElementById("build-pipeline"),
  deletePipeline: document.getElementById("delete-pipeline"),
  pipelineDropdownBtn: document.getElementById("pipelineDropdownBtn"),
  pipelineMenu: document.getElementById("pipeline-menu"),
  refreshPipelines: document.getElementById("refresh-pipelines"),
  parameterPanel: document.getElementById("parameter-panel"),
  parameterForm: document.getElementById("parameter-form"),
  parameterSave: document.getElementById("parameter-save"),
  parameterBack: document.getElementById("parameter-back"),
  parameterRun: document.getElementById("parameter-run"),
  nodePickerModal: document.getElementById("nodePickerModal"),
  nodePickerTabs: document.querySelectorAll("[data-node-mode]"),
  nodePickerServer: document.getElementById("node-picker-server"),
  nodePickerTool: document.getElementById("node-picker-tool"),
  nodePickerBranchCases: document.getElementById("node-picker-branch-cases"),
  nodePickerLoopTimes: document.getElementById("node-picker-loop-times"),
  nodePickerCustom: document.getElementById("node-picker-custom"),
  nodePickerPanels: {
    tool: document.getElementById("node-picker-tool-panel"),
    branch: document.getElementById("node-picker-branch-panel"),
    loop: document.getElementById("node-picker-loop-panel"),
    custom: document.getElementById("node-picker-custom-panel"),
  },
  nodePickerError: document.getElementById("node-picker-error"),
  nodePickerConfirm: document.getElementById("node-picker-confirm"),
  shutdownApp: document.getElementById("shutdown-app"),
};

const Modes = {
  BUILDER: "builder",
  PARAMETERS: "parameters",
};

const nodePickerState = {
  mode: "tool",
  server: null,
  tool: null,
  branchCases: "case1, case2",
  loopTimes: 2,
  customValue: "",
};

let nodePickerModalInstance = null;
let pendingInsert = null;
let fallbackModalHandlers = null;

function log(message) {
  const stamp = new Date().toLocaleTimeString();
  els.log.textContent += `[${stamp}] ${message}\n`;
  els.log.scrollTop = els.log.scrollHeight;
}

function resetLogView() {
  if (els.log) {
    els.log.textContent = "";
  }
}

function requestShutdown() {
  if (!window.confirm("确定退出 UltraRAG UI 吗？")) return;
  stopRunLogStream();
  log("正在请求关闭 UltraRAG 服务...");
  fetch("/api/system/shutdown", { method: "POST" })
    .then(async (resp) => {
      let data = {};
      try {
        data = await resp.json();
      } catch (err) {
        // ignore JSON errors
      }
      if (!resp.ok) {
        const msg = (data && data.error) || resp.statusText || "未知错误";
        log(`退出命令发送失败：${msg}`);
        return;
      }
      const mode = (data && data.mode) || "unknown";
      if (mode === "force") {
        log("退出命令已发送（强制模式），服务即将结束。");
      } else if (mode === "graceful") {
        log("退出命令已发送，服务正优雅关闭，请稍候...");
      } else {
        log("退出命令已发送，服务器即将停止。");
      }
    })
    .catch((err) => {
      log(`退出命令发送失败（服务器可能已终止）：${err.message}`);
    });
}

function stopRunLogStream() {
  if (state.logStream.timer) {
    clearTimeout(state.logStream.timer);
  }
  state.logStream.timer = null;
  state.logStream.runId = null;
  state.logStream.lastId = -1;
  state.logStream.status = "idle";
}

async function pollRunLogs() {
  if (!state.logStream.runId) return;
  const params = new URLSearchParams();
  params.set("since", String(state.logStream.lastId));
  params.set("run_id", state.logStream.runId);
  try {
    const data = await fetchJSON(`/api/logs/run?${params.toString()}`);
    if (data.reset) {
      resetLogView();
      state.logStream.lastId = -1;
    }
    const entries = data.entries || [];
    entries.forEach((entry) => {
      state.logStream.lastId = Math.max(state.logStream.lastId, entry.id);
      if (entry.message) {
        log(entry.message);
      }
    });
    const status = data.status || {};
    const stateValue = status.state || "running";
    state.logStream.status = stateValue;
    if (stateValue === "running") {
      state.logStream.timer = window.setTimeout(pollRunLogs, LOG_POLL_INTERVAL);
    } else {
      stopRunLogStream();
    }
  } catch (err) {
    log(`拉取运行日志失败：${err.message}`);
    stopRunLogStream();
  }
}

function startRunLogStream(runId) {
  if (!runId) return;
  stopRunLogStream();
  state.logStream.runId = runId;
  state.logStream.lastId = -1;
  state.logStream.status = "running";
  pollRunLogs();
}

async function fetchJSON(url, options = {}) {
  const resp = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(text || resp.statusText);
  }
  return resp.json();
}

function cloneDeep(value) {
  return value === undefined ? undefined : JSON.parse(JSON.stringify(value));
}

function createLocation(segments = []) {
  return { segments: segments.map((seg) => ({ ...seg })) };
}

function locationsEqual(a, b) {
  return JSON.stringify((a && a.segments) || []) === JSON.stringify((b && b.segments) || []);
}

function getContextKind(location) {
  const segments = (location && location.segments) || [];
  if (!segments.length) return "root";
  const last = segments[segments.length - 1];
  if (last.type === "loop") return "loop";
  if (last.type === "branch") return last.section === "router" ? "branch-router" : "branch-case";
  return "root";
}

function resolveSteps(location) {
  let steps = state.steps;
  const segments = (location && location.segments) || [];
  for (const seg of segments) {
    const entry = steps[seg.index];
    if (!entry) return steps;
    if (seg.type === "loop" && entry.loop) {
      entry.loop.steps = entry.loop.steps || [];
      steps = entry.loop.steps;
    } else if (seg.type === "branch" && entry.branch) {
      entry.branch.router = entry.branch.router || [];
      entry.branch.branches = entry.branch.branches || {};
      if (seg.section === "router") {
        steps = entry.branch.router;
      } else if (seg.section === "branch") {
        entry.branch.branches[seg.branchKey] = entry.branch.branches[seg.branchKey] || [];
        steps = entry.branch.branches[seg.branchKey];
      }
    }
  }
  return steps;
}

function resolveParentSteps(stepPath) {
  return resolveSteps(createLocation(stepPath.parentSegments || []));
}

function createStepPath(parentLocation, index) {
  return {
    parentSegments: (parentLocation.segments || []).map((seg) => ({ ...seg })),
    index,
  };
}

function getStepByPath(stepPath) {
  const steps = resolveParentSteps(stepPath);
  return steps[stepPath.index];
}

function setStepByPath(stepPath, value) {
  const steps = resolveParentSteps(stepPath);
  steps[stepPath.index] = value;
  markPipelineDirty();
}

function removeStepByPath(stepPath) {
  const steps = resolveParentSteps(stepPath);
  steps.splice(stepPath.index, 1);
}

function getEntryForSegments(segments) {
  let steps = state.steps;
  let entry = null;
  for (const seg of segments) {
    entry = steps[seg.index];
    if (!entry) return null;
    if (seg.type === "loop" && entry.loop) {
      steps = entry.loop.steps || [];
    } else if (seg.type === "branch" && entry.branch) {
      if (seg.section === "router") {
        steps = entry.branch.router || [];
      } else if (seg.section === "branch") {
        entry.branch.branches = entry.branch.branches || {};
        steps = entry.branch.branches[seg.branchKey] || [];
      }
    }
  }
  return entry;
}

function ensureContextInitialized() {
  if (!state.contextStack.length) {
    state.contextStack = [createLocation([])];
  }
}

function getActiveLocation() {
  ensureContextInitialized();
  return state.contextStack[state.contextStack.length - 1];
}

function setActiveLocation(location) {
  const segments = (location && location.segments) || [];
  const newStack = [createLocation([])];
  for (let i = 0; i < segments.length; i += 1) {
    newStack.push(createLocation(segments.slice(0, i + 1)));
  }
  state.contextStack = newStack;
  renderContextControls();
  renderSteps();
  updatePipelinePreview();
}

function resetContextStack() {
  state.contextStack = [createLocation([])];
  renderContextControls();
}

function yamlScalar(value) {
  if (value === null || value === undefined) return "null";
  if (typeof value === "boolean") return value ? "true" : "false";
  if (typeof value === "number") return Number.isFinite(value) ? String(value) : "null";
  if (typeof value === "string") {
    if (/^[A-Za-z0-9_.-]+$/.test(value)) return value;
    return JSON.stringify(value);
  }
  return JSON.stringify(value);
}

function yamlStringify(value, indent = 0) {
  const pad = "  ".repeat(indent);
  if (Array.isArray(value)) {
    if (!value.length) return `${pad}[]`;
    return value
      .map((item) => {
        if (item && typeof item === "object") {
          const nested = yamlStringify(item, indent + 1);
          return `${pad}-\n${nested}`;
        }
        return `${pad}- ${yamlScalar(item)}`;
      })
      .join("\n");
  }
  if (value && typeof value === "object") {
    const entries = Object.entries(value);
    if (!entries.length) return `${pad}{}`;
    return entries
      .map(([key, val]) => {
        if (val && typeof val === "object") {
          if (Array.isArray(val) && !val.length) {
            return `${pad}${key}: []`;
          }
          if (!Array.isArray(val) && !Object.keys(val).length) {
            return `${pad}${key}: {}`;
          }
          const nested = yamlStringify(val, indent + 1);
          return `${pad}${key}:\n${nested}`;
        }
        return `${pad}${key}: ${yamlScalar(val)}`;
      })
      .join("\n");
  }
  return `${pad}${yamlScalar(value)}`;
}

function collectServersFromSteps(steps, set = new Set()) {
  for (const step of steps) {
    if (typeof step === "string") {
      const parts = step.split(".");
      if (parts.length > 1) set.add(parts[0]);
    } else if (step && typeof step === "object") {
      if (step.loop && Array.isArray(step.loop.steps)) {
        collectServersFromSteps(step.loop.steps, set);
      } else if (step.branch) {
        collectServersFromSteps(step.branch.router || [], set);
        Object.values(step.branch.branches || {}).forEach((branchSteps) => collectServersFromSteps(branchSteps || [], set));
      }
    }
  }
  return set;
}

function buildServersMapping(steps) {
  const mapping = {};
  collectServersFromSteps(steps, new Set()).forEach((name) => {
    mapping[name] = `servers/${name}`;
  });
  return mapping;
}

function buildPipelinePayloadForPreview() {
  return {
    servers: buildServersMapping(state.steps),
    pipeline: cloneDeep(state.steps),
  };
}

function updatePipelinePreview() {
  if (!els.pipelinePreview) return;
  const payload = buildPipelinePayloadForPreview();
  els.pipelinePreview.textContent = yamlStringify(payload);
}

function setMode(mode) {
  state.mode = mode;
  if (mode === Modes.BUILDER) {
    if (els.pipelineForm) els.pipelineForm.classList.remove("d-none");
    if (els.parameterPanel) els.parameterPanel.classList.add("d-none");
  } else if (mode === Modes.PARAMETERS) {
    if (els.pipelineForm) els.pipelineForm.classList.add("d-none");
    if (els.parameterPanel) els.parameterPanel.classList.remove("d-none");
  }
}

function getNodePickerModal() {
  const modalElement = els.nodePickerModal;
  if (!modalElement) return null;
  if (!nodePickerModalInstance) {
    const hasBootstrap = typeof window !== "undefined" && window.bootstrap && typeof window.bootstrap.Modal === "function";
    if (hasBootstrap) {
      nodePickerModalInstance = new window.bootstrap.Modal(modalElement, { backdrop: "static" });
      modalElement.addEventListener("hidden.bs.modal", () => {
        pendingInsert = null;
        clearNodePickerError();
      });
    } else {
      const body = document.body;
      const beforeOverflow = body.style.overflow;
      const beforePaddingRight = body.style.paddingRight;
      fallbackModalHandlers = {
        show() {
          modalElement.classList.add("show");
          modalElement.style.display = "block";
          modalElement.removeAttribute("aria-hidden");
          body.classList.add("modal-open");
          body.style.overflow = "hidden";
          body.style.paddingRight = "0px";
        },
        hide() {
          modalElement.classList.remove("show");
          modalElement.style.display = "none";
          modalElement.setAttribute("aria-hidden", "true");
          body.classList.remove("modal-open");
          body.style.overflow = beforeOverflow;
          body.style.paddingRight = beforePaddingRight;
          pendingInsert = null;
          clearNodePickerError();
        },
      };
      modalElement.addEventListener("click", (event) => {
        if (event.target === modalElement) {
          fallbackModalHandlers.hide();
        }
      });
      modalElement.querySelectorAll('[data-bs-dismiss="modal"]').forEach((btn) => {
        btn.addEventListener("click", () => fallbackModalHandlers.hide());
      });
      nodePickerModalInstance = fallbackModalHandlers;
    }
  }
  return nodePickerModalInstance;
}

function clearNodePickerError() {
  if (!els.nodePickerError) return;
  els.nodePickerError.textContent = "";
  els.nodePickerError.classList.add("d-none");
}

function showNodePickerError(message) {
  if (!els.nodePickerError) return;
  els.nodePickerError.textContent = message;
  els.nodePickerError.classList.remove("d-none");
}

function populateNodePickerTools() {
  if (!els.nodePickerTool) return;
  const select = els.nodePickerTool;
  select.innerHTML = "";
  const server = nodePickerState.server;
  const tools = (server && state.toolCatalog.byServer[server]) || [];
  if (!tools.length) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = server ? "该服务器暂无工具" : "暂无可用工具";
    select.appendChild(option);
    select.disabled = true;
    nodePickerState.tool = null;
    return;
  }
  select.disabled = false;
  if (!nodePickerState.tool || !tools.some((item) => item.tool === nodePickerState.tool)) {
    nodePickerState.tool = tools[0].tool;
  }
  tools.forEach((tool) => {
    const option = document.createElement("option");
    option.value = tool.tool;
    option.textContent = tool.tool;
    select.appendChild(option);
  });
  select.value = nodePickerState.tool || "";
}

function populateNodePickerServers() {
  if (!els.nodePickerServer) return;
  const select = els.nodePickerServer;
  select.innerHTML = "";
  const servers = state.toolCatalog.order || [];
  if (!servers.length) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "暂无可用服务器";
    select.appendChild(option);
    select.disabled = true;
    nodePickerState.server = null;
    nodePickerState.tool = null;
    populateNodePickerTools();
    return;
  }
  select.disabled = false;
  if (!nodePickerState.server || !servers.includes(nodePickerState.server)) {
    nodePickerState.server = servers[0];
  }
  servers.forEach((server) => {
    const option = document.createElement("option");
    option.value = server;
    option.textContent = server;
    select.appendChild(option);
  });
  select.value = nodePickerState.server;
  populateNodePickerTools();
}

function updateNodePickerInputs() {
  if (els.nodePickerBranchCases) {
    els.nodePickerBranchCases.value = nodePickerState.branchCases || "case1, case2";
  }
  if (els.nodePickerLoopTimes) {
    els.nodePickerLoopTimes.value = nodePickerState.loopTimes || 2;
  }
  if (els.nodePickerCustom) {
    els.nodePickerCustom.value = nodePickerState.customValue || "";
  }
}

function setNodePickerMode(mode) {
  if (!mode) return;
  nodePickerState.mode = mode;
  if (els.nodePickerTabs && els.nodePickerTabs.length) {
    els.nodePickerTabs.forEach((tab) => {
      tab.classList.toggle("active", tab.dataset.nodeMode === mode);
    });
  }
  Object.entries(els.nodePickerPanels).forEach(([key, panel]) => {
    if (!panel) return;
    panel.classList.toggle("d-none", key !== mode);
  });
  clearNodePickerError();
  if (mode === "tool") {
    populateNodePickerServers();
  }
  updateNodePickerInputs();
}

function openNodePicker(location, insertIndex) {
  pendingInsert = { location, index: insertIndex };
  if (!nodePickerState.mode) nodePickerState.mode = "tool";
  if (!state.toolCatalog.order.length && nodePickerState.mode === "tool") {
    nodePickerState.mode = "branch";
  }
  if (!Number.isInteger(nodePickerState.loopTimes) || nodePickerState.loopTimes < 1) {
    nodePickerState.loopTimes = 2;
  }
  populateNodePickerServers();
  updateNodePickerInputs();
  setNodePickerMode(nodePickerState.mode);
  const modal = getNodePickerModal();
  if (modal) {
    modal.show();
  }
}

function handleNodePickerConfirm() {
  if (!pendingInsert) {
    const modal = getNodePickerModal();
    if (modal) modal.hide();
    return;
  }
  clearNodePickerError();
  const { location, index } = pendingInsert;
  let insertedPath = null;
  try {
    switch (nodePickerState.mode) {
      case "tool": {
        const server = nodePickerState.server;
        const tool = nodePickerState.tool;
        if (!server || !tool) {
          showNodePickerError("请选择服务器与工具");
          return;
        }
        const identifier = `${server}.${tool}`;
        insertStepAt(location, index, identifier);
        log(`已添加节点 ${identifier}`);
        break;
      }
      case "loop": {
        const times = Math.max(1, Number(nodePickerState.loopTimes) || 1);
        const loopStep = { loop: { times, steps: [] } };
        insertedPath = insertStepAt(location, index, loopStep);
        enterStructureContext("loop", insertedPath);
        log(`已添加 Loop (times=${times})`);
        break;
      }
      case "branch": {
        const rawCases = (nodePickerState.branchCases || "").split(",").map((c) => c.trim()).filter(Boolean);
        const cases = rawCases.length ? rawCases : ["case1", "case2"];
        const branchStep = { branch: { router: [], branches: {} } };
        cases.forEach((caseKey) => {
          branchStep.branch.branches[caseKey] = [];
        });
        insertedPath = insertStepAt(location, index, branchStep);
        enterStructureContext("branch", insertedPath);
        log(`已添加 Branch (${cases.join(", ")})`);
        break;
      }
      case "custom": {
        const raw = nodePickerState.customValue;
        if (!raw || !raw.trim()) {
          showNodePickerError("请输入自定义节点内容");
          return;
        }
        const parsed = parseStepInput(raw);
        insertStepAt(location, index, parsed);
        log("已添加自定义节点");
        break;
      }
      default:
        showNodePickerError("未知的节点类型");
        return;
    }
    const modal = getNodePickerModal();
    if (modal) modal.hide();
    pendingInsert = null;
  } catch (err) {
    showNodePickerError(err.message || "添加节点失败");
  }
}

function markPipelineDirty() {
  stopRunLogStream();
  state.isBuilt = false;
  state.parametersReady = false;
  if (state.mode !== Modes.BUILDER) {
    setMode(Modes.BUILDER);
  }
  updateActionButtons();
}

function setSteps(steps) {
  state.steps = Array.isArray(steps) ? cloneDeep(steps) : [];
  state.parameterData = null;
  markPipelineDirty();
  resetContextStack();
  renderSteps();
  updatePipelinePreview();
}

function updateActionButtons() {
  if (els.parameterRun) {
    const canRun = !!(state.isBuilt && state.parametersReady && state.selectedPipeline);
    els.parameterRun.disabled = !canRun;
  }
  if (els.parameterSave) {
    const canSave = !!(state.isBuilt && state.selectedPipeline);
    els.parameterSave.disabled = !canSave;
  }
}

function addStepToActive(stepValue) {
  const location = getActiveLocation();
  const stepsArray = resolveSteps(location);
  stepsArray.push(cloneDeep(stepValue));
  markPipelineDirty();
  setActiveLocation(location);
  return createStepPath(location, stepsArray.length - 1);
}

function insertStepAt(location, insertIndex, stepValue) {
  const stepsArray = resolveSteps(location);
  const index = Math.max(0, Math.min(insertIndex, stepsArray.length));
  stepsArray.splice(index, 0, cloneDeep(stepValue));
  markPipelineDirty();
  setActiveLocation(location);
  return createStepPath(location, index);
}

function moveStep(stepPath, targetLocation, insertIndex) {
  const source = resolveParentSteps(stepPath);
  const [item] = source.splice(stepPath.index, 1);
  const target = resolveSteps(targetLocation);
  let idx = insertIndex;
  if (source === target && stepPath.index < insertIndex) {
    idx -= 1;
  }
  target.splice(idx, 0, item);
  markPipelineDirty();
  setActiveLocation(targetLocation);
}

function removeStep(stepPath) {
  removeStepByPath(stepPath);
  markPipelineDirty();
  resetContextStack();
  renderSteps();
  updatePipelinePreview();
  log("已删除节点");
}

function openStepEditor(stepPath) {
  state.editingPath = stepPath;
  const step = getStepByPath(stepPath);
  if (typeof step === "string") {
    els.stepEditorValue.value = step;
  } else {
    els.stepEditorValue.value = JSON.stringify(step, null, 2);
  }
  els.stepEditor.hidden = false;
}

function closeStepEditor() {
  state.editingPath = null;
  els.stepEditor.hidden = true;
  els.stepEditorValue.value = "";
}

function parseStepInput(raw) {
  const trimmed = (raw || "").trim();
  if (!trimmed) throw new Error("节点内容不能为空");
  if ((trimmed.startsWith("{") && trimmed.endsWith("}")) || (trimmed.startsWith("[") && trimmed.endsWith("]"))) {
    return JSON.parse(trimmed);
  }
  return trimmed;
}

function createInsertControl(location, insertIndex, { prominent = false, compact = false } = {}) {
  const holder = document.createElement("div");
  holder.className = "flow-insert-control";
  if (prominent) holder.classList.add("prominent");
  if (compact) holder.classList.add("compact");
  const button = document.createElement("button");
  button.type = "button";
  button.className = "flow-insert-button";
  button.innerHTML = '<span>+</span><span class="d-none d-sm-inline">添加</span>';
  button.addEventListener("click", () => {
    const pendingLocation = createLocation((location.segments || []).map((seg) => ({ ...seg })));
    openNodePicker(pendingLocation, insertIndex);
  });
  holder.appendChild(button);
  return holder;
}

function renderToolNode(identifier, stepPath) {
  const card = document.createElement("div");
  card.className = "flow-node card border-0 tool-node";
  const body = document.createElement("div");
  body.className = "card-body d-flex flex-column gap-2";

  const header = document.createElement("div");
  header.className = "flow-node-header";
  const titleRow = document.createElement("div");
  titleRow.className = "flow-node-title-row";
  const title = document.createElement("h6");
  title.className = "flow-node-title";
  title.textContent = identifier;
  const handle = document.createElement("span");
  handle.className = "step-handle";
  handle.textContent = "☰";
  titleRow.append(title, handle);
  header.appendChild(titleRow);

  const preview = document.createElement("div");
  preview.className = "flow-node-body";
  preview.textContent = identifier;

  const actions = document.createElement("div");
  actions.className = "step-actions";
  const editBtn = document.createElement("button");
  editBtn.type = "button";
  editBtn.className = "btn btn-outline-primary btn-sm";
  editBtn.textContent = "编辑";
  editBtn.addEventListener("click", (event) => {
    event.stopPropagation();
    openStepEditor(stepPath);
  });
  const removeBtn = document.createElement("button");
  removeBtn.type = "button";
  removeBtn.className = "btn btn-outline-danger btn-sm";
  removeBtn.textContent = "删除";
  removeBtn.addEventListener("click", (event) => {
    event.stopPropagation();
    removeStep(stepPath);
  });
  actions.append(editBtn, removeBtn);

  body.append(header, preview, actions);
  card.append(body);
  return card;
}

function renderLoopNode(step, parentLocation, index) {
  const loopLocation = createLocation([...(parentLocation.segments || []), { type: "loop", index }]);
  const container = document.createElement("div");
  container.className = "loop-container card border-0";
  const body = document.createElement("div");
  body.className = "card-body d-flex flex-column gap-3";

  const header = document.createElement("div");
  header.className = "loop-header d-flex justify-content-between align-items-center";
  const title = document.createElement("h6");
  title.className = "mb-0";
  title.textContent = `Loop (times: ${step.loop.times || 1})`;
  const enterBtn = document.createElement("button");
  enterBtn.type = "button";
  enterBtn.className = "btn btn-link btn-sm text-decoration-none";
  enterBtn.textContent = "进入";
  enterBtn.addEventListener("click", () => setActiveLocation(loopLocation));
  header.append(title, enterBtn);

  const innerList = renderStepList(step.loop.steps || [], loopLocation, { placeholderText: "Loop 内暂无节点", compact: true });
  const actions = document.createElement("div");
  actions.className = "step-actions";
  const editBtn = document.createElement("button");
  editBtn.type = "button";
  editBtn.className = "btn btn-outline-primary btn-sm";
  editBtn.textContent = "编辑 Loop";
  editBtn.addEventListener("click", () => openStepEditor(createStepPath(parentLocation, index)));
  const removeBtn = document.createElement("button");
  removeBtn.type = "button";
  removeBtn.className = "btn btn-outline-danger btn-sm";
  removeBtn.textContent = "删除 Loop";
  removeBtn.addEventListener("click", () => removeStep(createStepPath(parentLocation, index)));
  actions.append(editBtn, removeBtn);

  body.append(header, innerList, actions);
  container.append(body);
  if (locationsEqual(loopLocation, getActiveLocation())) {
    container.classList.add("active");
  }
  return container;
}

function renderBranchNode(step, parentLocation, index) {
  step.branch.router = step.branch.router || [];
  step.branch.branches = step.branch.branches || {};
  const branchBase = createLocation([...(parentLocation.segments || []), { type: "branch", index, section: "router" }]);

  const container = document.createElement("div");
  container.className = "branch-container card border-0";
  const body = document.createElement("div");
  body.className = "card-body d-flex flex-column gap-3";

  const header = document.createElement("div");
  header.className = "branch-header d-flex justify-content-between align-items-center";
  const title = document.createElement("h6");
  title.className = "mb-0";
  title.textContent = "Branch";
  const enterBtn = document.createElement("button");
  enterBtn.type = "button";
  enterBtn.className = "btn btn-link btn-sm text-decoration-none";
  enterBtn.textContent = "进入 Router";
  enterBtn.addEventListener("click", () => setActiveLocation(branchBase));
  header.append(title, enterBtn);

  const routerSection = document.createElement("div");
  routerSection.className = "branch-router";
  if (locationsEqual(branchBase, getActiveLocation())) {
    routerSection.classList.add("active");
  }
  routerSection.append(renderStepList(step.branch.router, branchBase, { placeholderText: "Router 区域暂无节点", compact: true }));

  const casesWrap = document.createElement("div");
  casesWrap.className = "branch-cases";
  Object.keys(step.branch.branches).forEach((caseKey) => {
    const caseLocation = createLocation([
      ...(parentLocation.segments || []),
      { type: "branch", index, section: "branch", branchKey: caseKey },
    ]);
    const caseCard = document.createElement("div");
    caseCard.className = "branch-case card border-0";
    if (locationsEqual(caseLocation, getActiveLocation())) {
      caseCard.classList.add("active");
    }
    const caseBody = document.createElement("div");
    caseBody.className = "card-body";
    const caseHeader = document.createElement("div");
    caseHeader.className = "branch-case-header d-flex justify-content-between align-items-center";
    const caseTitle = document.createElement("span");
    caseTitle.textContent = caseKey;
    const selectBtn = document.createElement("button");
    selectBtn.type = "button";
    selectBtn.className = "btn btn-link btn-sm text-decoration-none";
    selectBtn.textContent = "进入";
    selectBtn.addEventListener("click", () => setActiveLocation(caseLocation));
    caseHeader.append(caseTitle, selectBtn);
    caseBody.append(caseHeader, renderStepList(step.branch.branches[caseKey], caseLocation, {
      placeholderText: `分支 ${caseKey} 暂无节点`,
      compact: true,
    }));
    caseCard.append(caseBody);
    casesWrap.append(caseCard);
  });

  const actions = document.createElement("div");
  actions.className = "step-actions";
  const editBtn = document.createElement("button");
  editBtn.type = "button";
  editBtn.className = "btn btn-outline-primary btn-sm";
  editBtn.textContent = "编辑 Branch";
  editBtn.addEventListener("click", () => openStepEditor(createStepPath(parentLocation, index)));
  const addCaseBtn = document.createElement("button");
  addCaseBtn.type = "button";
  addCaseBtn.className = "btn btn-outline-primary btn-sm";
  addCaseBtn.textContent = "新增分支";
  addCaseBtn.addEventListener("click", () => addBranchCase(parentLocation, index));
  const removeBtn = document.createElement("button");
  removeBtn.type = "button";
  removeBtn.className = "btn btn-outline-danger btn-sm";
  removeBtn.textContent = "删除 Branch";
  removeBtn.addEventListener("click", () => removeStep(createStepPath(parentLocation, index)));
  actions.append(editBtn, addCaseBtn, removeBtn);

  body.append(header, routerSection, casesWrap, actions);
  container.append(body);
  return container;
}

function renderGenericNode(step, stepPath) {
  const card = document.createElement("div");
  card.className = "flow-node card border-0 generic-node";
  const body = document.createElement("div");
  body.className = "card-body d-flex flex-column gap-2";

  const header = document.createElement("div");
  header.className = "flow-node-header";
  const title = document.createElement("h6");
  title.className = "flow-node-title";
  title.textContent = "自定义对象";
  header.appendChild(title);

  const preview = document.createElement("div");
  preview.className = "flow-node-body";
  preview.textContent = JSON.stringify(step, null, 2);

  const actions = document.createElement("div");
  actions.className = "step-actions";
  const editBtn = document.createElement("button");
  editBtn.type = "button";
  editBtn.className = "btn btn-outline-primary btn-sm";
  editBtn.textContent = "编辑";
  editBtn.addEventListener("click", () => openStepEditor(stepPath));
  const removeBtn = document.createElement("button");
  removeBtn.type = "button";
  removeBtn.className = "btn btn-outline-danger btn-sm";
  removeBtn.textContent = "删除";
  removeBtn.addEventListener("click", () => removeStep(stepPath));
  actions.append(editBtn, removeBtn);

  body.append(header, preview, actions);
  card.append(body);
  return card;
}

function renderStepNode(step, parentLocation, index) {
  const stepPath = createStepPath(parentLocation, index);
  if (typeof step === "string") return renderToolNode(step, stepPath);
  if (step && typeof step === "object" && step.loop) return renderLoopNode(step, parentLocation, index);
  if (step && typeof step === "object" && step.branch) return renderBranchNode(step, parentLocation, index);
  return renderGenericNode(step, stepPath);
}

function renderStepList(steps, location, options = {}) {
  const wrapper = document.createElement("div");
  wrapper.className = "step-list";
  if (locationsEqual(location, getActiveLocation())) {
    wrapper.classList.add("active-context");
  }
  if (!steps.length) {
    const placeholder = document.createElement("div");
    placeholder.className = "flow-placeholder d-flex flex-column gap-3 align-items-center";
    const message = document.createElement("span");
    message.textContent = options.placeholderText || "点击 + 添加节点";
    message.className = "text-muted";
    placeholder.appendChild(message);
    const control = createInsertControl(location, 0, { prominent: true });
    placeholder.appendChild(control);
    wrapper.appendChild(placeholder);
    return wrapper;
  }
  steps.forEach((step, index) => {
    wrapper.appendChild(createInsertControl(location, index, { compact: options.compact }));
    wrapper.appendChild(renderStepNode(step, location, index));
  });
  wrapper.appendChild(createInsertControl(location, steps.length, { compact: options.compact }));
  return wrapper;
}

function renderSteps() {
  els.flowCanvas.innerHTML = "";
  const rootLocation = createLocation([]);
  els.flowCanvas.appendChild(renderStepList(state.steps, rootLocation, { placeholderText: "点击 + 添加首个节点" }));
}

function ctxLabel(location, idx) {
  if (idx === 0) return "根流程";
  const segments = location.segments || [];
  const last = segments[segments.length - 1];
  if (!last) return "根流程";
  if (last.type === "loop") {
    const entry = getEntryForSegments(segments);
    const times = entry && entry.loop ? entry.loop.times : null;
    return times ? `Loop (times=${times})` : "Loop";
  }
  if (last.type === "branch") {
    if (last.section === "router") return "Branch Router";
    return `Branch ${last.branchKey}`;
  }
  return "节点";
}

function renderContextControls() {
  if (!els.contextControls) return;
  els.contextControls.innerHTML = "";
  ensureContextInitialized();
  const breadcrumb = document.createElement("div");
  breadcrumb.className = "context-breadcrumb d-flex flex-wrap gap-2";

  const rootBtn = document.createElement("button");
  rootBtn.type = "button";
  rootBtn.className = `btn btn-sm ${state.contextStack.length === 1 ? "btn-primary" : "btn-outline-secondary"}`;
  rootBtn.textContent = "根流程";
  rootBtn.addEventListener("click", () => setActiveLocation(createLocation([])));
  breadcrumb.appendChild(rootBtn);

  for (let idx = 1; idx < state.contextStack.length; idx += 1) {
    const location = state.contextStack[idx];
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `btn btn-sm ${idx === state.contextStack.length - 1 ? "btn-primary" : "btn-outline-secondary"}`;
    btn.textContent = ctxLabel(location, idx);
    btn.addEventListener("click", () => setActiveLocation(createLocation(location.segments || [])));
    breadcrumb.appendChild(btn);
  }

  els.contextControls.appendChild(breadcrumb);

  const active = getActiveLocation();
  const kind = getContextKind(active);
  const actionRow = document.createElement("div");
  actionRow.className = "context-actions d-flex flex-wrap gap-2 mt-2";

  if (kind === "loop") {
    const exitLoopBtn = document.createElement("button");
    exitLoopBtn.type = "button";
    exitLoopBtn.className = "btn btn-outline-danger btn-sm";
    exitLoopBtn.textContent = "结束当前 Loop";
    exitLoopBtn.addEventListener("click", endLoopContext);
    actionRow.appendChild(exitLoopBtn);
  } else if (kind === "branch-router" || kind === "branch-case") {
    appendBranchControls(active, actionRow);
  }

  if (actionRow.children.length) {
    els.contextControls.appendChild(actionRow);
  }
}

function endLoopContext() {
  const active = getActiveLocation();
  const segments = (active.segments || []).slice(0, -1);
  setActiveLocation(createLocation(segments));
  log("Loop 模式已结束");
}

function findBranchInfo(location) {
  const segments = location.segments || [];
  for (let i = segments.length - 1; i >= 0; i -= 1) {
    if (segments[i].type === "branch") {
      const parentSegments = segments.slice(0, i);
      const branchSegment = segments[i];
      const parentSteps = resolveSteps(createLocation(parentSegments));
      const branchEntry = parentSteps[branchSegment.index];
      if (!branchEntry || !branchEntry.branch) return null;
      branchEntry.branch.router = branchEntry.branch.router || [];
      branchEntry.branch.branches = branchEntry.branch.branches || {};
      return { parentSegments, branchSegment, branchEntry };
    }
  }
  return null;
}

function appendBranchControls(activeLocation, container) {
  const info = findBranchInfo(activeLocation);
  if (!info) return;
  const { parentSegments, branchSegment, branchEntry } = info;
  const routerBtn = document.createElement("button");
  routerBtn.type = "button";
  routerBtn.className = `btn btn-sm ${branchSegment.section === "router" ? "btn-primary" : "btn-outline-secondary"}`;
  routerBtn.textContent = "Router";
  routerBtn.addEventListener("click", () => switchBranchSection(parentSegments, branchSegment.index, "router"));
  container.append(routerBtn);

  Object.keys(branchEntry.branch.branches).forEach((caseKey) => {
    const caseBtn = document.createElement("button");
    caseBtn.type = "button";
    const active = branchSegment.section === "branch" && branchSegment.branchKey === caseKey;
    caseBtn.className = `btn btn-sm ${active ? "btn-primary" : "btn-outline-secondary"}`;
    caseBtn.textContent = caseKey;
    caseBtn.addEventListener("click", () => switchBranchSection(parentSegments, branchSegment.index, caseKey));
    container.append(caseBtn);
  });

  const newCaseBtn = document.createElement("button");
  newCaseBtn.type = "button";
  newCaseBtn.className = "btn btn-outline-primary btn-sm";
  newCaseBtn.textContent = "新增分支";
  newCaseBtn.addEventListener("click", () => addBranchCase(createLocation(parentSegments), branchSegment.index));
  container.append(newCaseBtn);

  const exitBtn = document.createElement("button");
  exitBtn.type = "button";
  exitBtn.className = "btn btn-outline-danger btn-sm";
  exitBtn.textContent = "结束当前 Branch";
  exitBtn.addEventListener("click", () => {
    setActiveLocation(createLocation(parentSegments));
    log("Branch 模式已结束");
  });
  container.append(exitBtn);
}

function switchBranchSection(parentSegments, branchIndex, target) {
  const branchLocation = createLocation([
    ...parentSegments,
    target === "router"
      ? { type: "branch", index: branchIndex, section: "router" }
      : { type: "branch", index: branchIndex, section: "branch", branchKey: target },
  ]);
  setActiveLocation(branchLocation);
  log(target === "router" ? "已切换至 Branch Router" : `已切换至分支 ${target}`);
}

function addBranchCase(parentLocation, branchIndex) {
  const steps = resolveSteps(parentLocation);
  const entry = steps[branchIndex];
  if (!entry || !entry.branch) return;
  entry.branch.branches = entry.branch.branches || {};
  let counter = Object.keys(entry.branch.branches).length + 1;
  let newKey = `case${counter}`;
  while (entry.branch.branches[newKey]) {
    counter += 1;
    newKey = `case${counter}`;
  }
  entry.branch.branches[newKey] = [];
  markPipelineDirty();
  switchBranchSection(parentLocation.segments || [], branchIndex, newKey);
  log(`已新增分支 ${newKey}`);
}

function enterStructureContext(structureType, stepPath, announce = true) {
  if (!stepPath) return;
  if (structureType === "loop") {
    const segments = [
      ...(stepPath.parentSegments || []),
      { type: "loop", index: stepPath.index },
    ];
    setActiveLocation(createLocation(segments));
    if (announce) log("Loop 模式已开启，后续节点将加入 Loop");
  } else if (structureType === "branch") {
    const segments = [
      ...(stepPath.parentSegments || []),
      { type: "branch", index: stepPath.index, section: "router" },
    ];
    setActiveLocation(createLocation(segments));
    if (announce) log("Branch 模式已开启，当前添加于 Router 区域");
  }
}

function updatePipelineDropdownLabel() {
  if (!els.pipelineDropdownBtn) return;
  els.pipelineDropdownBtn.textContent = state.selectedPipeline ? `Pipeline: ${state.selectedPipeline}` : "选择 Pipeline";
}

function renderPipelineMenu(items) {
  els.pipelineMenu.innerHTML = "";
  if (!items.length) {
    const empty = document.createElement("li");
    empty.innerHTML = '<span class="dropdown-item text-muted">暂无 Pipeline</span>';
    els.pipelineMenu.appendChild(empty);
    return;
  }
  items.forEach((item) => {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "dropdown-item";
    btn.textContent = item.name;
    btn.addEventListener("click", () => loadPipeline(item.name));
    li.appendChild(btn);
    els.pipelineMenu.appendChild(li);
  });
}

async function refreshPipelines() {
  const pipelines = await fetchJSON("/api/pipelines");
  renderPipelineMenu(pipelines);
  if (state.selectedPipeline && !pipelines.some((p) => p.name === state.selectedPipeline)) {
    state.selectedPipeline = null;
  }
  updatePipelineDropdownLabel();
}

async function loadPipeline(name) {
  const cfg = await fetchJSON(`/api/pipelines/${encodeURIComponent(name)}`);
  state.selectedPipeline = name;
  els.name.value = name;
  setSteps(cfg.pipeline || []);
  updatePipelineDropdownLabel();
  log(`已加载 Pipeline ${name}`);
}

function handleSubmit(event) {
  event.preventDefault();
  const name = els.name.value.trim();
  if (!name) {
    log("Pipeline 名称不能为空");
    return;
  }
  if (!state.steps.length) {
    log("请先添加至少一个节点");
    return;
  }
  const payload = {
    name,
    pipeline: cloneDeep(state.steps),
  };
  fetchJSON("/api/pipelines", {
    method: "POST",
    body: JSON.stringify(payload),
  })
    .then((saved) => {
      state.selectedPipeline = saved.name || name;
      updatePipelineDropdownLabel();
      refreshPipelines();
      log(`Pipeline ${state.selectedPipeline} 已保存`);
    })
    .catch((err) => log(err.message));
}

function buildSelectedPipeline() {
  if (!state.selectedPipeline) {
    log("请先保存 Pipeline");
    return;
  }
  fetchJSON(`/api/pipelines/${encodeURIComponent(state.selectedPipeline)}/build`, { method: "POST" })
    .then(() => {
      state.isBuilt = true;
      state.parametersReady = false;
      updateActionButtons();
      log(`Pipeline ${state.selectedPipeline} 构建完成`);
      showParameterPanel(true);
    })
    .catch((err) => log(err.message));
}

function runSelectedPipeline() {
  if (!state.selectedPipeline) {
    log("请先保存 Pipeline");
    return;
  }
  if (!state.parametersReady) {
    log("请先配置并保存参数");
    return;
  }
  stopRunLogStream();
  resetLogView();
  log(`已发送运行请求：${state.selectedPipeline}`);
  fetchJSON(`/api/pipelines/${encodeURIComponent(state.selectedPipeline)}/run`, { method: "POST" })
    .then((resp) => {
      if (resp && resp.run_id) {
        log(`Pipeline ${state.selectedPipeline} 正在运行，run_id=${resp.run_id}`);
        startRunLogStream(resp.run_id);
      } else {
        log("运行接口返回异常：缺少 run_id");
      }
      if (resp && resp.status && resp.status !== "started" && resp.status !== "running") {
        state.logStream.status = resp.status;
      }
    })
    .catch((err) => {
      log(`运行失败：${err.message}`);
      stopRunLogStream();
    });
}

function deleteSelectedPipeline() {
  if (!state.selectedPipeline) {
    log("没有可删除的 Pipeline");
    return;
  }
  if (!confirm(`确定删除 ${state.selectedPipeline}？`)) return;
  fetchJSON(`/api/pipelines/${encodeURIComponent(state.selectedPipeline)}`, { method: "DELETE" })
    .then(() => {
      log(`已删除 Pipeline ${state.selectedPipeline}`);
      state.selectedPipeline = null;
      els.name.value = "";
      setSteps([]);
      updatePipelineDropdownLabel();
      refreshPipelines();
    })
    .catch((err) => log(err.message));
}

function flattenParameters(obj, prefix = "") {
  const entries = [];
  if (!obj || typeof obj !== "object") return entries;
  Object.keys(obj)
    .sort()
    .forEach((key) => {
      const path = prefix ? `${prefix}.${key}` : key;
      const value = obj[key];
      if (value !== null && typeof value === "object" && !Array.isArray(value)) {
        entries.push(...flattenParameters(value, path));
      } else {
        entries.push({ path, value, type: detectParamType(value) });
      }
    });
  return entries;
}

function detectParamType(value) {
  if (value === null) return "null";
  if (Array.isArray(value)) return "array";
  return typeof value;
}

function setNestedValue(obj, path, newValue) {
  const parts = path.split(".");
  let current = obj;
  for (let i = 0; i < parts.length - 1; i += 1) {
    const key = parts[i];
    if (!current[key] || typeof current[key] !== "object") {
      current[key] = {};
    }
    current = current[key];
  }
  current[parts[parts.length - 1]] = newValue;
}

function coerceParameterValue(raw, type, originalValue) {
  const trimmed = raw.trim();
  if (type === "number") {
    const num = Number(trimmed);
    if (!Number.isNaN(num)) return { success: true, value: num };
    return { success: false, value: originalValue };
  }
  if (type === "boolean") {
    if (["true", "false"].includes(trimmed.toLowerCase())) {
      return { success: true, value: trimmed.toLowerCase() === "true" };
    }
    return { success: false, value: originalValue };
  }
  if (type === "null") {
    if (!trimmed || trimmed.toLowerCase() === "null") {
      return { success: true, value: null };
    }
    return { success: false, value: originalValue };
  }
  if (type === "array" || type === "object") {
    try {
      const parsed = JSON.parse(trimmed || "null");
      if (type === "array" && !Array.isArray(parsed)) return { success: false, value: originalValue };
      if (type === "object" && (parsed === null || typeof parsed !== "object" || Array.isArray(parsed))) {
        return { success: false, value: originalValue };
      }
      return { success: true, value: parsed };
    } catch (err) {
      return { success: false, value: originalValue };
    }
  }
  return { success: true, value: trimmed };
}

function renderParameterForm() {
  const container = els.parameterForm;
  container.innerHTML = "";
  if (!state.parameterData || typeof state.parameterData !== "object") {
    container.innerHTML = '<p class="text-muted small">暂无可配置参数，请先执行构建。</p>';
    return;
  }
  const entries = flattenParameters(state.parameterData);
  if (!entries.length) {
    container.innerHTML = '<p class="text-muted small">当前 Pipeline 无可编辑参数。</p>';
    return;
  }
  entries.forEach((entry) => {
    const row = document.createElement("div");
    row.className = "row g-3 align-items-center parameter-row";
    const labelCol = document.createElement("label");
    labelCol.className = "col-sm-5 col-lg-4 col-form-label text-muted";
    labelCol.textContent = entry.path;
    const valueCol = document.createElement("div");
    valueCol.className = "col-sm-7 col-lg-8";
    let control;
    if (entry.type === "array" || entry.type === "object") {
      control = document.createElement("textarea");
      control.rows = 3;
      control.value = JSON.stringify(entry.value, null, 2);
    } else {
      control = document.createElement("input");
      control.type = "text";
      control.value = entry.value === undefined || entry.value === null ? "" : String(entry.value);
    }
    control.className = "form-control";
    control.dataset.path = entry.path;
    control.dataset.type = entry.type;
    control.addEventListener("focus", () => control.classList.remove("is-invalid"));
    control.addEventListener("change", (event) => {
      const { success, value } = coerceParameterValue(event.target.value, entry.type, entry.value);
      if (!success) {
        control.classList.add("is-invalid");
        log(`无法解析 ${entry.path}，已恢复原值`);
        control.value = entry.type === "array" || entry.type === "object"
          ? JSON.stringify(entry.value, null, 2)
          : entry.value === undefined || entry.value === null
            ? ""
            : String(entry.value);
        return;
      }
      control.classList.remove("is-invalid");
      entry.value = value;
      setNestedValue(state.parameterData, entry.path, value);
      state.parametersReady = false;
      updateActionButtons();
    });
    valueCol.appendChild(control);
    row.append(labelCol, valueCol);
    container.appendChild(row);
  });
}

async function showParameterPanel(forceFetch = false) {
  if (!state.selectedPipeline) {
    log("请先保存并选择 Pipeline");
    return;
  }
  if (!state.isBuilt) {
    log("请先构建 Pipeline");
    return;
  }
  if (forceFetch || !state.parameterData) {
    try {
      state.parameterData = cloneDeep(
        await fetchJSON(`/api/pipelines/${encodeURIComponent(state.selectedPipeline)}/parameters`)
      );
      state.parametersReady = false;
    } catch (err) {
      log(`无法载入参数：${err.message}`);
      return;
    }
  }
  renderParameterForm();
  setMode(Modes.PARAMETERS);
  log("已进入参数配置视图");
  updateActionButtons();
}

function saveParameterForm() {
  if (!state.selectedPipeline) {
    log("请先保存 Pipeline");
    return;
  }
  if (!state.parameterData) {
    log("无参数可保存");
    return;
  }
  fetchJSON(`/api/pipelines/${encodeURIComponent(state.selectedPipeline)}/parameters`, {
    method: "PUT",
    body: JSON.stringify(state.parameterData),
  })
    .then(() => {
      log("参数已保存");
      state.parametersReady = true;
      updateActionButtons();
    })
    .catch((err) => log(err.message));
}

function clearSteps() {
  if (!state.steps.length) return;
  if (!confirm("确定清空所有节点？")) return;
  setSteps([]);
  log("已清空 Flow");
}

async function refreshTools() {
  const tools = await fetchJSON("/api/tools");
  const grouped = {};
  tools.forEach((tool) => {
    const server = tool.server || "未命名";
    if (!grouped[server]) grouped[server] = [];
    grouped[server].push(tool);
  });
  Object.values(grouped).forEach((list) => list.sort((a, b) => a.tool.localeCompare(b.tool)));
  state.toolCatalog = {
    order: Object.keys(grouped).sort((a, b) => a.localeCompare(b)),
    byServer: grouped,
  };
  nodePickerState.server = null;
  nodePickerState.tool = null;
  log("Server 工具元数据已加载");
}

function bindEvents() {
  els.pipelineForm.addEventListener("submit", handleSubmit);
  els.clearSteps.addEventListener("click", clearSteps);
  els.buildPipeline.addEventListener("click", buildSelectedPipeline);
  els.deletePipeline.addEventListener("click", deleteSelectedPipeline);
  if (els.shutdownApp) {
    els.shutdownApp.addEventListener("click", requestShutdown);
  }
  if (els.parameterSave) {
    els.parameterSave.addEventListener("click", saveParameterForm);
  }
  if (els.parameterBack) {
    els.parameterBack.addEventListener("click", () => {
      setMode(Modes.BUILDER);
      log("已返回流程画布");
    });
  }
  if (els.parameterRun) {
    els.parameterRun.addEventListener("click", runSelectedPipeline);
  }
  els.refreshPipelines.addEventListener("click", () => refreshPipelines().catch((err) => log(err.message)));
  els.name.addEventListener("input", updatePipelinePreview);
  els.stepEditor.querySelector("#step-editor-save").addEventListener("click", () => {
    if (!state.editingPath) return;
    try {
      const updated = parseStepInput(els.stepEditorValue.value);
      setStepByPath(state.editingPath, updated);
      closeStepEditor();
      renderSteps();
      updatePipelinePreview();
      log("节点已更新");
    } catch (err) {
      log(`更新失败：${err.message}`);
    }
  });
  els.stepEditor.querySelector("#step-editor-cancel").addEventListener("click", closeStepEditor);
  Array.from(els.nodePickerTabs || []).forEach((tab) => {
    tab.addEventListener("click", () => setNodePickerMode(tab.dataset.nodeMode));
  });
  if (els.nodePickerServer) {
    els.nodePickerServer.addEventListener("change", () => {
      nodePickerState.server = els.nodePickerServer.value || null;
      populateNodePickerTools();
    });
  }
  if (els.nodePickerTool) {
    els.nodePickerTool.addEventListener("change", () => {
      nodePickerState.tool = els.nodePickerTool.value || null;
    });
  }
  if (els.nodePickerBranchCases) {
    els.nodePickerBranchCases.addEventListener("input", () => {
      nodePickerState.branchCases = els.nodePickerBranchCases.value;
    });
  }
  if (els.nodePickerLoopTimes) {
    els.nodePickerLoopTimes.addEventListener("input", () => {
      nodePickerState.loopTimes = Math.max(1, Number(els.nodePickerLoopTimes.value || 1));
    });
  }
  if (els.nodePickerCustom) {
    els.nodePickerCustom.addEventListener("input", () => {
      nodePickerState.customValue = els.nodePickerCustom.value;
    });
  }
  if (els.nodePickerConfirm) {
    els.nodePickerConfirm.addEventListener("click", handleNodePickerConfirm);
  }
}

async function bootstrap() {
  setMode(Modes.BUILDER);
  resetContextStack();
  renderSteps();
  updatePipelinePreview();
  bindEvents();
  updateActionButtons();
  try {
    await Promise.all([refreshPipelines(), refreshTools()]);
    log("界面已准备就绪，点击 + 号开始搭建 UltraRAG Flow 吧！");
  } catch (err) {
    log(`初始化失败：${err.message}`);
  }
}

bootstrap();
