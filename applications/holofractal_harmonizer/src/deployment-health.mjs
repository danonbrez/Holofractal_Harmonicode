import { $, setText, log } from './visual-ide-state.mjs';

const LIVENESS_PATHS = ['/api/health'];
const RUNTIME_AUTHORITY_PATH = '/api/runtime/authority/status';
const ASSISTANT_STATUS_PATH = '/api/assistant/status';
const REQUEST_TIMEOUT_MS = 30_000;
const ASSISTANT_TIMEOUT_MS = 5_000;
const ONLINE_POLL_MS = 30_000;
const DEGRADED_POLL_MS = 12_000;

const RUNTIME_SELECTORS = [
  '#hhs-app-test', '#ide-test-simple', '#ide-run-lifecycle', '#ide-ingest',
  '#ide-interpret', '#ide-compile', '#ide-run', '#ide-replay',
  '[data-ide-command="ingress"]', '[data-ide-command="interpret"]',
  '[data-ide-command="compile"]', '[data-ide-command="run"]',
  '[data-ide-command="lifecycle"]', '[data-stage]',
  '#pass175-processor-window button', '#pass175-terminal-window button',
];
const ASSISTANT_SELECTORS = ['#send-prompt', '#new-thread'];

let current = Object.freeze({ checked: false, reachable: false, runtimeReady: false, assistantReady: false, assistantProbePending: false, mode: 'checking', detail: 'Checking runtime backend…' });
let pollTimer = null;
let checking = false;
let assistantChecking = false;
let consoleObserver = null;
let mutationObserver = null;
let suppressConsoleObserver = false;
let healthReconcileTimer = null;
let healthReconcileRunning = false;

function withTimeout(path, options = {}) {
  const { timeoutMs = REQUEST_TIMEOUT_MS, ...fetchOptions } = options;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort('HHS_BACKEND_HEALTH_TIMEOUT'), timeoutMs);
  return fetch(path, { cache: 'no-store', credentials: 'same-origin', ...fetchOptions, signal: controller.signal, headers: { Accept: 'application/json', ...(fetchOptions.headers || {}) } })
    .then(async (response) => {
      const raw = await response.text();
      let payload = {};
      try { payload = raw ? JSON.parse(raw) : {}; }
      catch { payload = { status: `NON_JSON_HTTP_${response.status}`, raw_preview: raw.slice(0, 240) }; }
      return { path, response, payload };
    }).finally(() => clearTimeout(timeout));
}

async function firstReachable(paths) {
  let lastError = null;
  for (const path of paths) {
    try {
      const result = await withTimeout(path);
      if (result.response.status < 500 || result.payload?.service_available) return result;
      lastError = new Error(`HTTP_${result.response.status}`);
    } catch (error) { lastError = error; }
  }
  throw lastError || new Error('BACKEND_UNREACHABLE');
}

function capability(payload, keys, fallback = false) {
  for (const key of keys) {
    const value = key.split('.').reduce((node, part) => node?.[part], payload);
    if (typeof value === 'boolean') return value;
  }
  return fallback;
}

function detailFor({ runtimeReady, assistantReady, assistantProbePending = false } = {}) {
  if (!runtimeReady) return 'Runtime service is reachable, but VM81 lifecycle authority is not ready.';
  if (assistantProbePending) return 'VM81 runtime authority is online; assistant provider status is checking independently.';
  if (!assistantReady) return 'VM81 runtime authority is online; the assistant provider is unavailable.';
  return 'Runtime backend and assistant provider are reachable.';
}

async function probeBackend() {
  const liveness = await firstReachable(LIVENESS_PATHS);
  let runtimeResult;
  try { runtimeResult = { status: 'fulfilled', value: await withTimeout(RUNTIME_AUTHORITY_PATH) }; }
  catch (reason) { runtimeResult = { status: 'rejected', reason }; }
  const live = liveness.payload || {};
  const runtimePayload = runtimeResult.status === 'fulfilled' ? runtimeResult.value.payload || {} : {};
  const runtimeReady = capability(
    runtimePayload,
    ['ok', 'authority_ready', 'runtime_authority.ok'],
    false,
  );
  return Object.freeze({
    checked: true,
    reachable: true,
    runtimeReady,
    assistantReady: current.assistantReady,
    assistantProbePending: true,
    mode: runtimeReady && current.assistantReady ? 'online' : 'degraded',
    detail: detailFor({ runtimeReady, assistantReady: current.assistantReady, assistantProbePending: true }),
    checkedAt: new Date().toISOString(),
    livenessPath: liveness.path,
    liveness: live,
    runtime: runtimePayload,
    assistant: current.assistant || {},
    runtimeAuthorityError: runtimeResult.status === 'rejected' ? String(runtimeResult.reason?.message || runtimeResult.reason || 'RUNTIME_AUTHORITY_UNAVAILABLE') : null,
    boundedStatusRoutes: Object.freeze([RUNTIME_AUTHORITY_PATH, ASSISTANT_STATUS_PATH]),
    assistantProbeBlocksRuntimeControls: false,
  });
}

async function refreshAssistantStatus() {
  if (assistantChecking) return current;
  assistantChecking = true;
  let assistantPayload = {};
  let assistantReady = false;
  let assistantError = null;
  try {
    const result = await withTimeout(ASSISTANT_STATUS_PATH, { timeoutMs: ASSISTANT_TIMEOUT_MS });
    assistantPayload = result.payload || {};
    assistantReady = capability(assistantPayload, ['online', 'ok'], false);
  } catch (error) {
    assistantError = String(error?.message || error || 'ASSISTANT_STATUS_UNAVAILABLE');
  } finally {
    assistantChecking = false;
  }
  current = Object.freeze({
    ...current,
    assistantReady,
    assistantProbePending: false,
    assistant: assistantPayload,
    assistantError,
    mode: current.reachable && current.runtimeReady && assistantReady ? 'online' : current.reachable ? 'degraded' : 'offline',
    detail: current.reachable
      ? detailFor({ runtimeReady: current.runtimeReady, assistantReady, assistantProbePending: false })
      : current.detail,
    assistantCheckedAt: new Date().toISOString(),
  });
  reconcileHealthSurfaces();
  return current;
}

function mountBanner() {
  if ($('#hhs-backend-health-banner')) return;
  const banner = document.createElement('section');
  banner.id = 'hhs-backend-health-banner';
  banner.className = 'hhs-backend-health-banner';
  banner.setAttribute('role', 'status');
  banner.setAttribute('aria-live', 'polite');
  banner.innerHTML = `<div><strong id="hhs-backend-health-title">Checking runtime backend…</strong><span id="hhs-backend-health-message">Editing, preview, and export remain available during this check.</span></div><div class="hhs-backend-health-actions"><button id="hhs-backend-health-retry" type="button">Retry backend</button><details><summary>Details</summary><pre id="hhs-backend-health-detail">No health result yet.</pre></details></div>`;
  const anchor = document.querySelector('.ide-control-pane, .ide-system-bar, #ide-layout');
  (anchor?.parentElement || document.body).insertBefore(banner, anchor || null);
  $('#hhs-backend-health-retry').onclick = () => void checkBackend(true);
}

function installStyles() {
  if ($('#hhs-backend-health-style')) return;
  const style = document.createElement('style');
  style.id = 'hhs-backend-health-style';
  style.textContent = `.hhs-backend-health-banner{position:sticky;top:0;z-index:160;display:grid;grid-template-columns:1fr auto;gap:12px;align-items:center;padding:10px 14px;border-bottom:1px solid #7d5f27;background:#2a2112;color:#fff3cf;box-shadow:0 4px 18px #0008}.hhs-backend-health-banner[data-mode="online"]{display:none}.hhs-backend-health-banner[data-mode="offline"]{background:#3a1717;border-color:#a85050}.hhs-backend-health-banner[data-mode="degraded"]{background:#302511;border-color:#9a742e}.hhs-backend-health-banner strong,.hhs-backend-health-banner span{display:block}.hhs-backend-health-banner span{margin-top:2px;font-size:.82rem;opacity:.9}.hhs-backend-health-actions{display:flex;align-items:center;gap:8px}.hhs-backend-health-actions details{position:relative}.hhs-backend-health-actions pre{position:absolute;right:0;top:100%;width:min(620px,90vw);max-height:45vh;overflow:auto;z-index:5;background:#080b12;color:#e8edf7;border:1px solid #55627a;padding:10px;white-space:pre-wrap}[data-hhs-backend-disabled="true"]{cursor:not-allowed!important;opacity:.48!important}@media(max-width:700px){.hhs-backend-health-banner{grid-template-columns:1fr}.hhs-backend-health-actions{justify-content:space-between}}`;
  document.head.append(style);
}

function setDisabled(selector, disabled, reason) {
  document.querySelectorAll(selector).forEach((node) => {
    if (!(node instanceof HTMLButtonElement || node instanceof HTMLInputElement || node instanceof HTMLSelectElement)) return;
    if (disabled) {
      if (!node.disabled) { node.disabled = true; node.dataset.hhsBackendDisabled = 'true'; }
      if (node.title !== reason) node.title = reason;
      if (node.getAttribute('aria-description') !== reason) node.setAttribute('aria-description', reason);
    } else if (node.dataset.hhsBackendDisabled === 'true') {
      node.disabled = false;
      delete node.dataset.hhsBackendDisabled;
      if (/backend|runtime authority|assistant provider/i.test(node.title || '')) node.removeAttribute('title');
      node.removeAttribute('aria-description');
    }
  });
}

function showBackendMessage(title, message) {
  mountBanner();
  setText('#hhs-backend-health-title', title);
  setText('#hhs-backend-health-message', message);
  const banner = $('#hhs-backend-health-banner');
  if (banner) { banner.hidden = false; banner.scrollIntoView({ block: 'nearest' }); }
}

function repairAssistantInput() {
  const prompt = $('#prompt-input');
  if (!prompt) return;
  prompt.disabled = false;
  prompt.readOnly = false;
  prompt.tabIndex = 0;
  prompt.style.pointerEvents = 'auto';
  if (prompt.getAttribute('aria-describedby') !== 'hhs-backend-health-message') prompt.setAttribute('aria-describedby', 'hhs-backend-health-message');
  if (prompt.getAttribute('autocomplete') !== 'off') prompt.setAttribute('autocomplete', 'off');
  const form = $('#prompt-form');
  if (form && !form.dataset.hhsBackendGuarded) {
    form.addEventListener('submit', (event) => {
      if (current.assistantReady) return;
      event.preventDefault();
      event.stopImmediatePropagation();
      showBackendMessage('Assistant unavailable', 'The assistant provider is offline. Your draft remains in the input; retry the backend without losing it.');
    }, true);
    form.dataset.hhsBackendGuarded = 'true';
  }
}

function updateRuntimePanels() {
  if (current.runtimeReady) return;
  const message = current.reachable ? 'Backend reachable, but VM81/Pass 175 authority is not ready. Retry after the health state changes.' : 'Backend unreachable. No firmware, VM81, Hash216, or receipt state was changed.';
  ['#pass175-terminal-window .pass175-terminal-state', '#pass175-processor-window .pass175-state'].forEach((selector) => setText(selector, current.reachable ? 'AUTHORITY DEGRADED' : 'BACKEND OFFLINE'));
  ['#pass175-terminal-window .pass175-terminal-output', '#pass175-processor-window .pass175-result'].forEach((selector) => {
    const node = $(selector);
    if (!node) return;
    setText(selector, message);
    node.classList.add('error');
  });
}

function updateAssistantSurface() {
  repairAssistantInput();
  const provider = $('#provider-status');
  if (current.assistantReady) {
    const assistant = current.assistant || {};
    setText('#provider-status', 'ASSISTANT ONLINE');
    setText(
      '#backend-id',
      assistant.effective_mode || assistant.selected_provider_id || assistant.provider_id || 'HHS provider',
    );
    if (provider && provider.className !== 'status online') provider.className = 'status online';
    return;
  }
  setText('#provider-status', current.reachable ? 'ASSISTANT DEGRADED' : 'ASSISTANT API OFFLINE');
  setText('#backend-id', current.reachable ? 'provider unavailable' : 'backend unreachable');
  if (provider && provider.className !== 'status degraded') provider.className = 'status degraded';
}

function applyHealthState() {
  mountBanner();
  const banner = $('#hhs-backend-health-banner');
  if (!banner) return;
  if (banner.dataset.mode !== current.mode) banner.dataset.mode = current.mode;
  const hidden = current.mode === 'online';
  if (banner.hidden !== hidden) banner.hidden = hidden;
  let title = 'Runtime backend online';
  let message = 'VM81 lifecycle authority and assistant provider are available.';
  if (current.mode === 'offline') { title = 'Runtime backend unreachable'; message = 'Editing, preview, and source/runnable ZIP export remain available. Lifecycle, receipts, VM81, Pass 175, and assistant actions are disabled.'; }
  else if (current.mode === 'degraded') { title = current.runtimeReady ? 'Runtime online · assistant degraded' : 'Runtime backend degraded'; message = `${current.detail} Editing, preview, and export remain available.`; }
  setText('#hhs-backend-health-title', title);
  setText('#hhs-backend-health-message', message);
  setText('#hhs-backend-health-detail', JSON.stringify(current, null, 2));
  const runtimeReason = current.reachable ? 'Runtime authority is not ready. Retry the backend health check.' : 'Runtime backend is unreachable. Editing, preview, and export remain available.';
  const assistantReason = current.reachable ? 'Assistant provider is unavailable. Retry the backend health check.' : 'Assistant backend is unreachable. Your prompt can still be drafted.';
  RUNTIME_SELECTORS.forEach((selector) => setDisabled(selector, !current.runtimeReady, runtimeReason));
  ASSISTANT_SELECTORS.forEach((selector) => setDisabled(selector, !current.assistantReady, assistantReason));
  repairAssistantInput();
  updateRuntimePanels();
  updateAssistantSurface();
  if (!current.runtimeReady) setText('#validation-state', current.reachable ? 'Preview ready locally · Verifiable runtime receipt unavailable because authority is degraded.' : 'Preview ready locally · Verifiable runtime receipt unavailable because the backend is offline.');
  document.dispatchEvent(new CustomEvent('hhs:backend-health', { detail: current }));
}

function dedupePreviewConsole() {
  const output = $('#ide-preview-console');
  if (!output || output.dataset.hhsDedupeBound) return;
  const normalize = () => {
    if (suppressConsoleObserver) return;
    const lines = output.textContent.split('\n');
    const seenReady = new Set();
    const compact = [];
    for (const line of lines) {
      const normalized = line.trim();
      const readyClass = /Rendered .*sandbox|Application preview initialized|Preview ready/i.test(normalized);
      if (readyClass && seenReady.has(normalized)) continue;
      if (readyClass) seenReady.add(normalized);
      if (compact.length && compact.at(-1) === line && normalized) continue;
      compact.push(line);
    }
    const next = compact.join('\n');
    if (next !== output.textContent) { suppressConsoleObserver = true; output.textContent = next; suppressConsoleObserver = false; }
  };
  consoleObserver = new MutationObserver(normalize);
  consoleObserver.observe(output, { childList: true, characterData: true, subtree: true });
  output.dataset.hhsDedupeBound = 'true';
  normalize();
}

function reconcileHealthSurfaces() {
  if (healthReconcileRunning) return;
  healthReconcileRunning = true;
  try {
    applyHealthState();
    repairAssistantInput();
    dedupePreviewConsole();
  } finally {
    healthReconcileRunning = false;
  }
}

function scheduleHealthReconciliation() {
  if (healthReconcileTimer !== null) return;
  healthReconcileTimer = window.setTimeout(() => {
    healthReconcileTimer = null;
    reconcileHealthSurfaces();
  }, 0);
}

function scheduleNext() {
  clearTimeout(pollTimer);
  pollTimer = setTimeout(() => void checkBackend(false), current.runtimeReady ? ONLINE_POLL_MS : DEGRADED_POLL_MS);
}

export async function checkBackend(userInitiated = false) {
  if (checking) return current;
  checking = true;
  if (userInitiated) showBackendMessage('Checking runtime backend…', 'Testing process liveness and VM81 authority. Assistant status is checked independently.');
  try {
    current = await probeBackend();
    reconcileHealthSurfaces();
    void refreshAssistantStatus();
  } catch (error) {
    current = Object.freeze({ checked: true, reachable: false, runtimeReady: false, assistantReady: current.assistantReady, assistantProbePending: false, mode: 'offline', detail: String(error?.message || error || 'BACKEND_UNREACHABLE'), checkedAt: new Date().toISOString() });
    reconcileHealthSurfaces();
  } finally {
    checking = false;
    scheduleNext();
  }
  log(`Deployment backend health: ${current.mode}.`, { reachable: current.reachable, runtime_ready: current.runtimeReady, assistant_ready: current.assistantReady, assistant_probe_blocks_runtime: false, detail: current.detail });
  return current;
}

export function initDeploymentHealth() {
  installStyles();
  mountBanner();
  repairAssistantInput();
  dedupePreviewConsole();
  if (!mutationObserver) {
    mutationObserver = new MutationObserver(scheduleHealthReconciliation);
    mutationObserver.observe(document.body, { childList: true, subtree: true });
  }
  document.addEventListener('visibilitychange', () => { if (!document.hidden) void checkBackend(false); });
  window.HHSDeploymentHealth = Object.freeze({
    check: checkBackend,
    get state() { return current; },
    frontend_runtime_authority: false,
    editing_preview_export_remain_available_offline: true,
    reconciliation_task_bounded: true,
    heavyweight_product_health_probe_duplicated: false,
    startup_liveness_paths: Object.freeze([...LIVENESS_PATHS]),
    startup_health_timeout_ms: REQUEST_TIMEOUT_MS,
    assistant_health_timeout_ms: ASSISTANT_TIMEOUT_MS,
    assistant_probe_blocks_runtime_controls: false,
    runtime_authority_independent_of_assistant: true,
    healthz_startup_probe_disabled: true,
  });
  void checkBackend(false);
}