import { $, setText, log } from './visual-ide-state.mjs';

const LIVENESS_PATHS = ['/health', '/api/health', '/healthz'];
const PRODUCT_HEALTH_PATH = '/api/product/health';
const REQUEST_TIMEOUT_MS = 4_000;
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

let current = Object.freeze({ checked: false, reachable: false, runtimeReady: false, assistantReady: false, mode: 'checking', detail: 'Checking runtime backend…' });
let pollTimer = null;
let checking = false;
let consoleObserver = null;
let mutationObserver = null;
let suppressConsoleObserver = false;

function withTimeout(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort('HHS_BACKEND_HEALTH_TIMEOUT'), REQUEST_TIMEOUT_MS);
  return fetch(path, { cache: 'no-store', credentials: 'same-origin', ...options, signal: controller.signal, headers: { Accept: 'application/json', ...(options.headers || {}) } })
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

async function probeBackend() {
  const liveness = await firstReachable(LIVENESS_PATHS);
  let product = null;
  try { product = await withTimeout(PRODUCT_HEALTH_PATH); } catch { product = null; }
  const live = liveness.payload || {};
  const productPayload = product?.payload || {};
  const runtimeReady = capability(productPayload, ['runtime.ok', 'runtime_authority.ok'], capability(live, ['runtime_ready', 'authority_ready', 'runtime_authority.ok', 'ok'], false));
  const assistantReady = capability(productPayload, ['assistant.online', 'assistant.ok'], capability(live, ['assistant_ready'], false));
  let detail = 'Runtime backend reachable.';
  if (!runtimeReady && !assistantReady) detail = 'Runtime service is reachable, but execution authority and the assistant are unavailable.';
  else if (!runtimeReady) detail = 'Runtime service is reachable, but VM81 lifecycle authority is not ready.';
  else if (!assistantReady) detail = 'VM81 runtime authority is online; the assistant provider is unavailable.';
  return Object.freeze({ checked: true, reachable: true, runtimeReady, assistantReady, mode: runtimeReady && assistantReady ? 'online' : 'degraded', detail, checkedAt: new Date().toISOString(), livenessPath: liveness.path, liveness: live, product: productPayload });
}

function mountBanner() {
  if ($('#hhs-backend-health-banner')) return;
  const banner = document.createElement('section');
  banner.id = 'hhs-backend-health-banner';
  banner.className = 'hhs-backend-health-banner';
  banner.setAttribute('role', 'status');
  banner.setAttribute('aria-live', 'polite');
  banner.innerHTML = `<div><strong id="hhs-backend-health-title">Checking runtime backend…</strong><span id="hhs-backend-health-message">Editing, preview, and export remain available during this check.</span></div><div class="hhs-backend-health-actions"><button id="hhs-backend-health-retry" type="button">Retry backend</button><details><summary>Details</summary><pre id="hhs-backend-health-detail">No health result yet.</pre></details></div>`;
  document.body.prepend(banner);
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
      node.title = reason;
      node.setAttribute('aria-description', reason);
    } else if (node.dataset.hhsBackendDisabled === 'true') {
      node.disabled = false;
      delete node.dataset.hhsBackendDisabled;
      if (/backend|runtime authority|assistant provider/i.test(node.title || '')) node.removeAttribute('title');
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
  prompt.setAttribute('aria-describedby', 'hhs-backend-health-message');
  prompt.setAttribute('autocomplete', 'off');
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
  ['#pass175-terminal-window .pass175-terminal-output', '#pass175-processor-window .pass175-result'].forEach((selector) => { const node = $(selector); if (node) { node.textContent = message; node.classList.add('error'); } });
}

function updateAssistantSurface() {
  repairAssistantInput();
  if (current.assistantReady) return;
  setText('#provider-status', current.reachable ? 'ASSISTANT DEGRADED' : 'ASSISTANT API OFFLINE');
  setText('#backend-id', current.reachable ? 'provider unavailable' : 'backend unreachable');
  const provider = $('#provider-status');
  if (provider) provider.className = 'status degraded';
}

function applyHealthState() {
  mountBanner();
  const banner = $('#hhs-backend-health-banner');
  if (!banner) return;
  banner.dataset.mode = current.mode;
  banner.hidden = current.mode === 'online';
  let title = 'Runtime backend online';
  let message = 'VM81 lifecycle authority and assistant provider are available.';
  if (current.mode === 'offline') { title = 'Runtime backend unreachable'; message = 'Editing, preview, and source/runnable ZIP export remain available. Lifecycle, receipts, VM81, Pass 175, and assistant actions are disabled.'; }
  else if (current.mode === 'degraded') { title = 'Runtime backend degraded'; message = `${current.detail} Editing, preview, and export remain available.`; }
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

function scheduleNext() {
  clearTimeout(pollTimer);
  pollTimer = setTimeout(() => void checkBackend(false), current.mode === 'online' ? ONLINE_POLL_MS : DEGRADED_POLL_MS);
}

export async function checkBackend(userInitiated = false) {
  if (checking) return current;
  checking = true;
  if (userInitiated) showBackendMessage('Checking runtime backend…', 'Testing liveness, VM81 authority, and assistant provider status.');
  try { current = await probeBackend(); }
  catch (error) { current = Object.freeze({ checked: true, reachable: false, runtimeReady: false, assistantReady: false, mode: 'offline', detail: String(error?.message || error || 'BACKEND_UNREACHABLE'), checkedAt: new Date().toISOString() }); }
  finally { checking = false; applyHealthState(); scheduleNext(); }
  log(`Deployment backend health: ${current.mode}.`, { reachable: current.reachable, runtime_ready: current.runtimeReady, assistant_ready: current.assistantReady, detail: current.detail });
  return current;
}

export function initDeploymentHealth() {
  installStyles();
  mountBanner();
  repairAssistantInput();
  dedupePreviewConsole();
  if (!mutationObserver) {
    mutationObserver = new MutationObserver(() => { applyHealthState(); repairAssistantInput(); dedupePreviewConsole(); });
    mutationObserver.observe(document.body, { childList: true, subtree: true });
  }
  document.addEventListener('visibilitychange', () => { if (!document.hidden) void checkBackend(false); });
  window.HHSDeploymentHealth = Object.freeze({ check: checkBackend, get state() { return current; }, frontend_runtime_authority: false, editing_preview_export_remain_available_offline: true });
  void checkBackend(false);
}
