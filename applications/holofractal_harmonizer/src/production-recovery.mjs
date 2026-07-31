import {
  $, state, activeFile, persist, setText, log, bytesToBase64, base64ToBytes,
  inferExactExpression,
} from './visual-ide-state.mjs';
import { renderFiles, openBottomTab } from './visual-ide-ui.mjs';
import { createStoredZip } from './project-zip.mjs';
import { compileStandaloneApplication, buildDeployableApplicationZip } from './deployable-app-compiler.mjs';

const JOB_STORAGE_KEY = 'hhs.pass176.lifecycleJob.v1';
const WORKSPACE_STORAGE_KEY = 'hhs.pass176.workspace.v1';
const PER_JOB_TIMEOUT_MS = 10_000;
const PREVIEW_READY_TIMEOUT_MS = 5_000;
const encoder = new TextEncoder();

let activeJob = null;
let lastRetry = null;
let previewSequence = 0;
let previewPending = new Map();
const detachedAdvanced = [];

function uuid() {
  return globalThis.crypto?.randomUUID?.() || `job-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function now() { return new Date().toISOString(); }

function syncActiveEditor() {
  const file = activeFile();
  const editor = $('#ide-source-editor');
  if (file && editor && !file.bytesB64) {
    file.content = editor.value;
    persist();
    renderFiles();
  }
}

function fileBytes(file) {
  return file.bytesB64 ? base64ToBytes(file.bytesB64) : encoder.encode(file.content || '');
}

function safeSlug(value, fallback = 'hhs-project') {
  return String(value || fallback).toLowerCase().replace(/[^a-z0-9._-]+/g, '-').replace(/^-+|-+$/g, '') || fallback;
}

function projectName() {
  return ($('#ide-project-name')?.value || 'HHS Multimodal Project').trim();
}

function persistJob(job) {
  try { localStorage.setItem(JOB_STORAGE_KEY, JSON.stringify(job)); } catch { /* bounded persistence is best effort */ }
}

function updateJobControls() {
  const running = activeJob?.state === 'running';
  for (const selector of ['#hhs-app-test', '#ide-test-simple', '#ide-run-lifecycle', '#hhs-app-preview', '#ide-build-preview-simple', '#ide-build-project', '#ide-menu-build-project']) {
    const node = $(selector);
    if (node) node.disabled = running;
  }
  const cancel = $('#hhs-app-cancel');
  if (cancel) cancel.disabled = !running;
  const retry = $('#hhs-app-retry');
  if (retry) retry.disabled = running || !lastRetry;
  for (const selector of ['#hhs-app-export', '#ide-export-simple', '#ide-export-project']) {
    const node = $(selector);
    if (node) node.disabled = false;
  }
}

function presentJob(job) {
  const stage = job.current_file ? ` · ${job.current_file}` : '';
  const detail = job.failure_reason ? ` · ${job.failure_reason}` : '';
  const label = `${job.state.toUpperCase()} · ${job.kind}${stage}${detail}`;
  setText('#hhs-app-job-state', label);
  setText('#ide-project-build-state', label);
  setText('#ide-simple-workflow-state', label);
  const status = $('#hhs-app-job-state');
  if (status) status.dataset.state = job.state;
  updateJobControls();
}

function startJob(kind, currentFile = null) {
  if (activeJob?.state === 'running') throw new Error('ANOTHER_LIFECYCLE_JOB_IS_RUNNING');
  const controller = new AbortController();
  const job = {
    schema: 'HHS_PASS_176_FINITE_LIFECYCLE_JOB_V1',
    job_id: uuid(),
    kind,
    state: 'running',
    created_at: now(),
    started_epoch_ms: Date.now(),
    updated_at: now(),
    current_file: currentFile,
    last_successful_checkpoint: 'JOB_ADMITTED',
    timeout_ms: PER_JOB_TIMEOUT_MS,
    correlation_id: uuid(),
    failure_reason: null,
    frontend_runtime_authority: false,
  };
  activeJob = { ...job, controller };
  persistJob(job);
  presentJob(job);
  return activeJob;
}

function finishJob(stateName, patch = {}) {
  if (!activeJob) return null;
  const job = {
    ...activeJob,
    ...patch,
    controller: undefined,
    state: stateName,
    updated_at: now(),
    completed_at: now(),
  };
  activeJob = job;
  persistJob(job);
  presentJob(job);
  return job;
}

function errorClassification(error) {
  if (error?.name === 'AbortError') return activeJob?.cancel_requested ? 'CANCELLED_BY_USER' : 'TIMEOUT';
  return String(error?.message || error || 'UNKNOWN_FAILURE');
}

async function requestBoundedJson(path, options, job) {
  const elapsed = Math.max(0, Date.now() - Number(job.started_epoch_ms || Date.now()));
  const remaining = Math.max(1, PER_JOB_TIMEOUT_MS - elapsed);
  const timeout = setTimeout(() => job.controller.abort('HHS_PASS_176_JOB_TIMEOUT'), remaining);
  try {
    const response = await fetch(path, {
      ...options,
      signal: job.controller.signal,
      headers: {
        Accept: 'application/json',
        ...(options?.body ? { 'Content-Type': 'application/json' } : {}),
        ...(options?.headers || {}),
        'X-HHS-Job-ID': job.job_id,
        'X-HHS-Correlation-ID': job.correlation_id,
      },
    });
    const raw = await response.text();
    let payload;
    try { payload = raw ? JSON.parse(raw) : {}; }
    catch { throw new Error(`NON_JSON_RESPONSE_HTTP_${response.status}`); }
    if (!response.ok) throw new Error(payload.detail?.detail || payload.detail?.classification || payload.detail || payload.error || `HTTP_${response.status}`);
    return payload;
  } finally {
    clearTimeout(timeout);
  }
}

async function ensureProjectBounded(job) {
  if (state.projectId) return state.projectId;
  const session = await requestBoundedJson('/api/runtime/workspace/session', {
    method: 'POST',
    body: JSON.stringify({ name: projectName() }),
  }, job);
  state.projectId = session.project?.project_id || session.project_summaries?.[0]?.project_id || 'project:visual-development';
  setText('#ide-project-label', projectName());
  setText('#active-thread', projectName());
  persist();
  return state.projectId;
}

function sourcePayload(file, projectId) {
  return {
    source_b64: bytesToBase64(fileBytes(file)),
    source_name: file.name,
    declared_media_type: file.mediaType,
    provenance: `visual-ide://${projectId}/${file.path}`,
    authorization_scope: 'HHS_VISUAL_IDE_USER_AUTHORIZED_PROJECT_TEST',
  };
}

export async function runBoundedProjectTest() {
  syncActiveEditor();
  const selectedPath = $('#ide-preview-entrypoint')?.value;
  const file = state.files.find((candidate) => candidate.path === selectedPath) || activeFile();
  if (!file) throw new Error('NO_ACTIVE_PROJECT_FILE');
  const job = startJob('TEST_ACTIVE_APPLICATION_PATH', file.path);
  lastRetry = runBoundedProjectTest;
  setText('#ide-terminal-state', 'TEST RUNNING');
  try {
    const projectId = await ensureProjectBounded(job);
    job.last_successful_checkpoint = 'PROJECT_AUTHORITY_BOUND';
    persistJob({ ...job, controller: undefined });
    const sourceText = file.bytesB64 ? '' : file.content || '';
    const result = await requestBoundedJson('/api/runtime/development/lifecycle', {
      method: 'POST',
      body: JSON.stringify({
        ...sourcePayload(file, projectId),
        project_id: projectId,
        project_name: projectName(),
        expression: inferExactExpression(sourceText),
        interpretation_scope: 'SOURCE_EXACT_NUMERIC_PROBE',
        target: 'HHS_IR',
        steps: Math.min(32, Math.max(1, Number($('#ide-run-steps')?.value || 8))),
      }),
    }, job);
    state.lifecycle = result;
    state.ingress = result?.ingress || state.ingress;
    state.snapshot = result?.vm_snapshot || state.snapshot;
    state.egress = result?.egress || state.egress;
    const succeeded = result?.ok !== false;
    finishJob(succeeded ? 'succeeded' : 'failed', {
      last_successful_checkpoint: succeeded ? 'RECEIPT_BOUND_LIFECYCLE_COMPLETE' : 'BACKEND_PARTIAL_RESULT_RECEIVED',
      failure_reason: succeeded ? null : (result?.status || 'BACKEND_LIFECYCLE_PARTIAL'),
      result_summary: {
        status: result?.status,
        lifecycle_receipt_hash72: result?.receipts?.lifecycle_receipt_hash72 || null,
        lifecycle_hash216: result?.receipts?.lifecycle_hash216 || null,
      },
    });
    setText('#ide-terminal-state', succeeded ? 'TEST COMPLETE' : 'TEST FAILED');
    setText('#ide-receipt-output', JSON.stringify(result?.receipts || result, null, 2));
    openBottomTab('terminal');
    log(succeeded ? 'Bounded governed lifecycle completed.' : 'Governed lifecycle returned a partial result.', result);
    return result;
  } catch (error) {
    const classification = errorClassification(error);
    const cancelled = classification === 'CANCELLED_BY_USER';
    finishJob(cancelled ? 'cancelled' : (classification === 'TIMEOUT' ? 'timed_out' : 'failed'), {
      failure_reason: classification,
      last_successful_checkpoint: activeJob?.last_successful_checkpoint || 'JOB_ADMITTED',
    });
    setText('#ide-terminal-state', cancelled ? 'TEST CANCELLED' : 'TEST FAILED');
    log(`Bounded test ${cancelled ? 'cancelled' : 'failed'}: ${classification}. Retry is available; editing and source export remain enabled.`);
    throw error;
  }
}

export function cancelActiveJob() {
  if (!activeJob || activeJob.state !== 'running') return false;
  activeJob.cancel_requested = true;
  activeJob.controller.abort('HHS_PASS_176_USER_CANCEL');
  return true;
}

export async function retryLastJob() {
  if (!lastRetry || activeJob?.state === 'running') return null;
  return lastRetry();
}

function sourceArchiveBuild() {
  syncActiveEditor();
  const entries = state.files.map((file) => ({ path: `source/${file.path}`, data: fileBytes(file) }));
  const manifest = {
    schema: 'HHS_PASS_176_SOURCE_PROJECT_ARCHIVE_V1',
    project_name: projectName(),
    exported_at: now(),
    file_count: state.files.length,
    files: state.files.map((file) => ({ path: file.path, media_type: file.mediaType, size_bytes: fileBytes(file).length })),
    original_source_preserved: true,
    compilation_required: false,
    backend_runtime_authority_claimed: false,
    pass_constraints_preserved: true,
  };
  entries.push({ path: 'project.hhs-source-manifest.json', data: JSON.stringify(manifest, null, 2) });
  entries.push({ path: 'README.txt', data: 'Source export is intentionally independent of compiler and runtime lifecycle success. No backend authority is fabricated by this archive.\n' });
  return {
    archiveBytes: createStoredZip(entries),
    archiveName: `${safeSlug(projectName())}-source.zip`,
    manifest,
  };
}

function downloadBytes(bytes, name, type) {
  const url = URL.createObjectURL(new Blob([bytes], { type }));
  const link = Object.assign(document.createElement('a'), { href: url, download: name });
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function downloadSourceProject() {
  const build = sourceArchiveBuild();
  downloadBytes(build.archiveBytes, build.archiveName, 'application/zip');
  log(`Exported source project independently of lifecycle state: ${build.archiveName}.`, build.manifest);
  return build;
}

export function downloadRunnableApplication() {
  syncActiveEditor();
  const build = buildDeployableApplicationZip();
  downloadBytes(build.archiveBytes, build.archiveName, 'application/zip');
  log(`Exported runnable browser application: ${build.archiveName}.`, build.manifest);
  return build;
}

function previewBridge(previewId) {
  return `<script>
(() => {
  const PREVIEW_ID = ${JSON.stringify(previewId)};
  const serialize = (value) => {
    try { return typeof value === 'string' ? value : JSON.stringify(value); }
    catch { return String(value); }
  };
  const send = (kind, payload = {}) => parent.postMessage({ source: 'hhs-preview-bridge-v1', previewId: PREVIEW_ID, kind, ...payload }, '*');
  for (const kind of ['log', 'info', 'warn', 'error']) {
    const original = console[kind].bind(console);
    console[kind] = (...values) => { original(...values); send('console', { level: kind, values: values.map(serialize) }); };
  }
  addEventListener('error', (event) => send('runtime-error', { message: event.message, filename: event.filename, line: event.lineno, column: event.colno }));
  addEventListener('unhandledrejection', (event) => send('runtime-error', { message: 'Unhandled rejection: ' + serialize(event.reason) }));
  addEventListener('message', (event) => {
    const request = event.data;
    if (!request || request.source !== 'hhs-preview-parent-v1' || request.previewId !== PREVIEW_ID) return;
    let result = null;
    let error = null;
    try {
      const node = request.selector ? document.querySelector(request.selector) : null;
      if (request.command === 'query') result = node ? { found: true, text: node.textContent, value: node.value, ariaLabel: node.getAttribute('aria-label') } : { found: false };
      else if (request.command === 'click') { if (!node) throw new Error('PREVIEW_SELECTOR_NOT_FOUND'); node.click(); result = { clicked: true }; }
      else if (request.command === 'type') { if (!node) throw new Error('PREVIEW_SELECTOR_NOT_FOUND'); node.focus(); node.value = request.value ?? ''; node.dispatchEvent(new Event('input', { bubbles: true })); node.dispatchEvent(new Event('change', { bubbles: true })); result = { typed: true, value: node.value }; }
      else if (request.command === 'key') { if (!node) throw new Error('PREVIEW_SELECTOR_NOT_FOUND'); node.dispatchEvent(new KeyboardEvent('keydown', { key: request.key, bubbles: true })); node.dispatchEvent(new KeyboardEvent('keyup', { key: request.key, bubbles: true })); result = { key: request.key }; }
      else if (request.command === 'snapshot') result = { title: document.title, activeElement: document.activeElement?.outerHTML?.slice(0, 500) || null, bodyText: document.body?.innerText?.slice(0, 10000) || '' };
      else if (request.command === 'accessibility') result = [...document.querySelectorAll('button,input,select,textarea,a,[role],[aria-label]')].slice(0, 500).map((element) => ({ tag: element.tagName.toLowerCase(), role: element.getAttribute('role'), ariaLabel: element.getAttribute('aria-label'), text: element.textContent?.trim().slice(0, 160) || '', disabled: Boolean(element.disabled), tabIndex: element.tabIndex }));
      else throw new Error('PREVIEW_COMMAND_REJECTED');
    } catch (caught) { error = String(caught?.message || caught); }
    send('test-result', { requestId: request.requestId, result, error });
  });
  const ready = () => requestAnimationFrame(() => send('ready', { title: document.title, href: location.href }));
  if (document.readyState === 'loading') addEventListener('DOMContentLoaded', ready, { once: true }); else ready();
})();
<\/script>`;
}

function appendBridge(html, previewId) {
  const bridge = previewBridge(previewId);
  if (/<head[^>]*>/i.test(html)) return html.replace(/<head([^>]*)>/i, `<head$1>${bridge}`);
  return `${bridge}${html}`;
}

function previewConsole(message, kind = 'info') {
  const output = $('#ide-preview-console');
  if (!output) return;
  output.textContent += `\n[${kind.toUpperCase()}] ${message}`;
  output.scrollTop = output.scrollHeight;
}

export function renderStablePreview() {
  syncActiveEditor();
  const host = $('#ide-preview-host');
  if (!host) throw new Error('PREVIEW_HOST_UNAVAILABLE');
  const previewId = `preview-${++previewSequence}-${Date.now()}`;
  const compiled = appendBridge(compileStandaloneApplication(), previewId);
  host.replaceChildren();
  const frame = document.createElement('iframe');
  frame.id = 'ide-application-frame';
  frame.title = `Application preview: ${projectName()}`;
  frame.dataset.previewId = previewId;
  frame.sandbox = 'allow-scripts allow-forms allow-modals allow-downloads';
  frame.referrerPolicy = 'no-referrer';
  frame.srcdoc = compiled;
  host.append(frame);
  setText('#ide-preview-state', 'LOADING');
  openBottomTab('preview');
  const timeout = setTimeout(() => {
    if (frame.dataset.ready === 'true') return;
    setText('#ide-preview-state', 'ERROR · PREVIEW_READY_TIMEOUT');
    previewConsole('Preview did not reach ready within 5 seconds. Reload Preview is available.', 'error');
  }, PREVIEW_READY_TIMEOUT_MS);
  frame.addEventListener('load', () => previewConsole('Sandbox document loaded; waiting for explicit preview-ready bridge.', 'info'), { once: true });
  frame.dataset.readyTimer = String(timeout);
  return frame;
}

function previewCommand(command, selector = null, value = null, key = null) {
  const frame = $('#ide-application-frame');
  if (!frame?.contentWindow || !frame.dataset.previewId) return Promise.reject(new Error('PREVIEW_NOT_READY'));
  const requestId = uuid();
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      previewPending.delete(requestId);
      reject(new Error('PREVIEW_TEST_BRIDGE_TIMEOUT'));
    }, 2_000);
    previewPending.set(requestId, { resolve, reject, timer });
    frame.contentWindow.postMessage({
      source: 'hhs-preview-parent-v1',
      previewId: frame.dataset.previewId,
      requestId,
      command,
      selector,
      value,
      key,
    }, '*');
  });
}

function onPreviewMessage(event) {
  const message = event.data;
  if (!message || message.source !== 'hhs-preview-bridge-v1') return;
  const frame = $('#ide-application-frame');
  if (!frame || frame.dataset.previewId !== message.previewId || event.source !== frame.contentWindow) return;
  if (message.kind === 'ready') {
    frame.dataset.ready = 'true';
    clearTimeout(Number(frame.dataset.readyTimer || 0));
    setText('#ide-preview-state', `READY · ${message.title || projectName()}`);
    previewConsole('Preview ready. Keyboard and automated test bridge are active.', 'ready');
  } else if (message.kind === 'runtime-error') {
    setText('#ide-preview-state', `RUNTIME ERROR · ${message.message}`);
    previewConsole(message.message, 'error');
  } else if (message.kind === 'console') {
    previewConsole((message.values || []).join(' '), message.level || 'info');
  } else if (message.kind === 'test-result') {
    const pending = previewPending.get(message.requestId);
    if (!pending) return;
    clearTimeout(pending.timer);
    previewPending.delete(message.requestId);
    if (message.error) pending.reject(new Error(message.error)); else pending.resolve(message.result);
  }
}

export function buildAndPreview() {
  const job = startJob('BUILD_AND_PREVIEW', $('#ide-preview-entrypoint')?.value || null);
  lastRetry = buildAndPreview;
  try {
    const frame = renderStablePreview();
    finishJob('succeeded', {
      last_successful_checkpoint: 'RUNNABLE_PREVIEW_DOCUMENT_CREATED',
      preview_id: frame.dataset.previewId,
    });
    setText('#ide-terminal-state', 'PREVIEW READY');
    return frame;
  } catch (error) {
    finishJob('failed', { failure_reason: errorClassification(error) });
    setText('#ide-terminal-state', 'BUILD FAILED');
    throw error;
  }
}

function exportDialog() {
  let dialog = $('#hhs-export-dialog');
  if (dialog) return dialog;
  dialog = document.createElement('section');
  dialog.id = 'hhs-export-dialog';
  dialog.className = 'hhs-export-dialog';
  dialog.hidden = true;
  dialog.setAttribute('role', 'dialog');
  dialog.setAttribute('aria-modal', 'true');
  dialog.setAttribute('aria-labelledby', 'hhs-export-title');
  dialog.innerHTML = `
    <div class="hhs-export-card">
      <header><div><span>EXPORT</span><h2 id="hhs-export-title">Choose the artifact</h2></div><button id="hhs-export-close" type="button" aria-label="Close export dialog">×</button></header>
      <button id="hhs-export-source" type="button"><strong>Source project ZIP</strong><small>Always available; does not require compilation</small></button>
      <button id="hhs-export-runnable" type="button"><strong>Runnable web app ZIP</strong><small>Inlines project-local HTML, CSS, JavaScript and media</small></button>
      <button id="hhs-export-evidence" type="button"><strong>Receipts / evidence bundle</strong><small>Available after a governed lifecycle returns evidence</small></button>
    </div>`;
  document.body.append(dialog);
  const close = () => { dialog.hidden = true; };
  $('#hhs-export-close').onclick = close;
  $('#hhs-export-source').onclick = () => { downloadSourceProject(); close(); };
  $('#hhs-export-runnable').onclick = () => { try { downloadRunnableApplication(); close(); } catch (error) { log(`Runnable export failed: ${error.message}`); } };
  $('#hhs-export-evidence').onclick = () => {
    if (!state.egress && !state.lifecycle) { log('No governed lifecycle evidence is available yet. Source export remains available.'); return; }
    window.HHSVisualIDE?.egress?.();
    close();
  };
  dialog.addEventListener('click', (event) => { if (event.target === dialog) close(); });
  return dialog;
}

export function openExportDialog() {
  exportDialog().hidden = false;
  $('#hhs-export-source')?.focus();
}

function markGeneratedStarterClean(originalCreate) {
  return function createAndCheckpoint(...args) {
    const priorPaths = new Set(state.files.map((file) => file.path));
    const result = originalCreate?.apply(this, args);
    for (const file of state.files) {
      if (!priorPaths.has(file.path)) file.dirty = false;
    }
    persist();
    renderFiles();
    const name = projectName();
    setText('#ide-project-label', name);
    setText('#active-thread', name);
    log(`Created from ${name} starter checkpoint; generated files are clean.`);
    return result;
  };
}

function detachAdvancedSurfaces() {
  if (detachedAdvanced.length) return;
  const selectors = [
    '#ide-repository-explorer', '.ide-registry-explorer', '.lifecycle-control-window',
    '#ide-pass175-processor', '#ide-pass175-terminal', '.ide-object-space-window',
  ];
  for (const selector of selectors) {
    for (const node of document.querySelectorAll(selector)) {
      if (node.closest('#hhs-app-command-bar')) continue;
      const marker = document.createComment(`hhs-pass176:${selector}`);
      node.parentNode?.insertBefore(marker, node);
      detachedAdvanced.push({ node, marker });
      node.remove();
    }
  }
}

function restoreAdvancedSurfaces() {
  while (detachedAdvanced.length) {
    const { node, marker } = detachedAdvanced.shift();
    marker.parentNode?.insertBefore(node, marker);
    marker.remove();
  }
}

function setWorkspace(mode) {
  const resolved = mode === 'advanced' ? 'advanced' : 'application';
  document.body.dataset.hhsWorkspace = resolved;
  localStorage.setItem(WORKSPACE_STORAGE_KEY, resolved);
  $('#hhs-workspace-application')?.classList.toggle('active', resolved === 'application');
  $('#hhs-workspace-advanced')?.classList.toggle('active', resolved === 'advanced');
  if (resolved === 'application') detachAdvancedSurfaces(); else restoreAdvancedSurfaces();
  setText('#hhs-workspace-state', resolved === 'application' ? 'APPLICATION IDE' : 'ADVANCED RUNTIME');
}

function installStyles() {
  if ($('#hhs-pass176-production-recovery-style')) return;
  const style = document.createElement('style');
  style.id = 'hhs-pass176-production-recovery-style';
  style.textContent = `
    .hhs-app-command-bar{display:grid;grid-template-columns:auto 1fr auto;gap:12px;align-items:center;padding:10px 14px;border-bottom:1px solid var(--line,#26324a);background:rgba(9,14,25,.96);position:sticky;top:0;z-index:80}
    .hhs-workspace-switch,.hhs-app-actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.hhs-app-command-bar button{min-height:36px}.hhs-app-command-bar button.active,.hhs-app-command-bar .primary-action{font-weight:700}
    #hhs-app-job-state[data-state="failed"],#hhs-app-job-state[data-state="timed_out"]{color:#ff9d9d}#hhs-app-job-state[data-state="succeeded"]{color:#9effbd}
    .hhs-export-dialog{position:fixed;inset:0;z-index:1000;background:rgba(0,0,0,.72);display:grid;place-items:center;padding:16px}.hhs-export-dialog[hidden]{display:none}.hhs-export-card{width:min(560px,100%);display:grid;gap:10px;background:#101827;border:1px solid #33415f;border-radius:14px;padding:18px}.hhs-export-card header{display:flex;justify-content:space-between;align-items:start}.hhs-export-card button:not(#hhs-export-close){text-align:left;padding:14px}.hhs-export-card small{display:block;opacity:.75;margin-top:4px}
    body[data-hhs-workspace="application"] #registry-nav .ide-repository-shortcuts,body[data-hhs-workspace="application"] .ide-menu-bar [data-ide-command="ingress"],body[data-hhs-workspace="application"] .ide-menu-bar [data-ide-command="interpret"],body[data-hhs-workspace="application"] .ide-menu-bar [data-ide-command="compile"],body[data-hhs-workspace="application"] .ide-menu-bar [data-ide-command="run"],body[data-hhs-workspace="application"] .ide-menu-bar [data-ide-command="lifecycle"],body[data-hhs-workspace="application"] .ide-menu-bar [data-ide-command="egress"]{display:none!important}
    @media(max-width:700px){.hhs-app-command-bar{grid-template-columns:1fr;position:relative}.hhs-workspace-switch,.hhs-app-actions{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))}.hhs-app-actions .primary-action{grid-column:1/-1}.hhs-app-status{display:flex;justify-content:space-between;gap:8px;overflow:auto}.ide-mobile-dock{display:flex!important}.ide-preview-grid{grid-template-columns:1fr!important}}
  `;
  document.head.append(style);
}

function mountCommandBar() {
  if ($('#hhs-app-command-bar')) return;
  const view = $('#ide-view');
  const anchor = view?.querySelector('.ide-tab-strip') || view?.firstChild;
  if (!view) return;
  const bar = document.createElement('section');
  bar.id = 'hhs-app-command-bar';
  bar.className = 'hhs-app-command-bar';
  bar.setAttribute('aria-label', 'Canonical application IDE commands');
  bar.innerHTML = `
    <div class="hhs-workspace-switch"><button id="hhs-workspace-application" type="button">Application</button><button id="hhs-workspace-advanced" type="button">Advanced Runtime</button></div>
    <div class="hhs-app-actions"><button id="hhs-app-save" type="button">Save</button><button id="hhs-app-preview" type="button" class="primary-action">Build & Preview</button><button id="hhs-app-test" type="button">Test</button><button id="hhs-app-export" type="button">Export</button><button id="hhs-app-cancel" type="button" disabled>Cancel</button><button id="hhs-app-retry" type="button" disabled>Retry</button></div>
    <div class="hhs-app-status"><span id="hhs-workspace-state">APPLICATION IDE</span><span id="hhs-app-job-state" data-state="idle">READY</span></div>`;
  view.insertBefore(bar, anchor || null);
  $('#hhs-workspace-application').onclick = () => setWorkspace('application');
  $('#hhs-workspace-advanced').onclick = () => setWorkspace('advanced');
  $('#hhs-app-save').onclick = () => $('#ide-save')?.click();
  $('#hhs-app-preview').onclick = () => { try { buildAndPreview(); } catch (error) { log(`Build & Preview failed: ${error.message}`); } };
  $('#hhs-app-test').onclick = () => void runBoundedProjectTest().catch(() => {});
  $('#hhs-app-export').onclick = openExportDialog;
  $('#hhs-app-cancel').onclick = cancelActiveJob;
  $('#hhs-app-retry').onclick = () => void retryLastJob().catch(() => {});
}

function patchExistingCommands() {
  const bind = (selector, handler) => { const node = $(selector); if (node) node.onclick = handler; };
  bind('#ide-build-preview-simple', () => { try { buildAndPreview(); } catch (error) { log(`Build & Preview failed: ${error.message}`); } });
  bind('#ide-test-simple', () => void runBoundedProjectTest().catch(() => {}));
  bind('#ide-export-simple', openExportDialog);
  bind('#ide-run-lifecycle', () => void runBoundedProjectTest().catch(() => {}));
  bind('#ide-build-project', () => { try { buildAndPreview(); } catch (error) { log(`Build failed: ${error.message}`); } });
  bind('#ide-export-project', openExportDialog);
  bind('#ide-menu-build-project', () => { try { buildAndPreview(); } catch (error) { log(`Build failed: ${error.message}`); } });
  bind('#ide-refresh-preview', () => { try { renderStablePreview(); } catch (error) { setText('#ide-preview-state', `ERROR · ${error.message}`); } });
  const exportButton = $('#ide-export-project');
  if (exportButton) exportButton.disabled = false;
  state.projectBuildBusy = false;

  const create = $('#ide-create-project');
  if (create?.onclick && !create.dataset.pass176Patched) {
    create.onclick = markGeneratedStarterClean(create.onclick);
    create.dataset.pass176Patched = 'true';
  }
}

function recoverPriorJob() {
  try {
    const prior = JSON.parse(localStorage.getItem(JOB_STORAGE_KEY) || 'null');
    if (!prior) return;
    if (prior.state === 'running') {
      prior.state = 'failed';
      prior.failure_reason = 'RECOVERED_AFTER_RELOAD';
      prior.updated_at = now();
      prior.completed_at = now();
      persistJob(prior);
    }
    activeJob = prior;
    presentJob(prior);
  } catch { /* ignore malformed local recovery record */ }
}

export function initProductionRecovery() {
  installStyles();
  mountCommandBar();
  exportDialog();
  addEventListener('message', onPreviewMessage);
  patchExistingCommands();
  recoverPriorJob();
  setWorkspace(localStorage.getItem(WORKSPACE_STORAGE_KEY) || 'application');
  const observer = new MutationObserver(() => patchExistingCommands());
  observer.observe(document.body, { childList: true, subtree: true });
  window.HHSPass176Recovery = Object.freeze({
    buildAndPreview,
    test: runBoundedProjectTest,
    cancel: cancelActiveJob,
    retry: retryLastJob,
    exportSource: downloadSourceProject,
    exportRunnable: downloadRunnableApplication,
    preview: renderStablePreview,
    previewTest: Object.freeze({
      query: (selector) => previewCommand('query', selector),
      click: (selector) => previewCommand('click', selector),
      type: (selector, value) => previewCommand('type', selector, value),
      key: (selector, key) => previewCommand('key', selector, null, key),
      snapshot: () => previewCommand('snapshot'),
      accessibility: () => previewCommand('accessibility'),
    }),
    setWorkspace,
    timeout_ms: PER_JOB_TIMEOUT_MS,
    preview_ready_timeout_ms: PREVIEW_READY_TIMEOUT_MS,
    frontend_runtime_authority: false,
  });
  log('Pass 176 production recovery active: bounded lifecycle jobs, source-independent export, stable preview bridge, and application-first workspace.');
}
