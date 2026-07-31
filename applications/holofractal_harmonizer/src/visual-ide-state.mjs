export const $ = (selector) => document.querySelector(selector);
export const $$ = (selector) => [...document.querySelectorAll(selector)];
export const TEXT_MODALITIES = new Set(['TEXT', 'MARKDOWN', 'SOURCE_CODE', 'JSON', 'JSONL', 'CSV', 'HTML', 'XML', 'HHS_CONTRACT', 'HHS_RECEIPT', 'HHS_MANIFEST', 'HHS_VECTOR_PACKET']);
const STORAGE_KEY = 'hhs.visualIde.v1';
const STORAGE_PENDING_KEY = `${STORAGE_KEY}.pending`;
const genesis = `a²=1\nb²=2\nc²=3\nP=72\np=64\nq=81\nΔ=P²-pq\n(P²-pq)-Δ=0`;
function storageRead(key) {
  try { return localStorage.getItem(key); }
  catch { return null; }
}
const stored = (() => {
  const candidates = [
    { raw: storageRead(STORAGE_KEY), pending: false },
    { raw: storageRead(STORAGE_PENDING_KEY), pending: true },
  ].filter((candidate) => candidate.raw);
  const parsed = [];
  for (const candidate of candidates) {
    try { parsed.push({ ...JSON.parse(candidate.raw), pending: candidate.pending }); }
    catch { /* malformed recovery candidates do not block the editor */ }
  }
  parsed.sort((left, right) => Number(right.savedAt || 0) - Number(left.savedAt || 0) || Number(right.pending) - Number(left.pending));
  return parsed[0] || null;
})();
export const state = {
  projectId: stored?.projectId || null,
  files: stored?.files?.length ? stored.files : [
    { path: 'src/main.hhs', name: 'main.hhs', mediaType: 'SOURCE_CODE', content: genesis, dirty: true },
    { path: 'project/hhs.lifecycle.json', name: 'hhs.lifecycle.json', mediaType: 'JSON', content: JSON.stringify({ snapshot_bits: 5184, cells: '81×64', hash216: '3×72' }, null, 2), dirty: false },
  ],
  activePath: stored?.activePath || 'src/main.hhs',
  ingress: null,
  snapshot: null,
  compilation: null,
  execution: null,
  lifecycle: null,
  egress: null,
  busy: false,
  scene: { x: 58, z: -24, scale: .78, pointer: null, px: 0, py: 0 },
};
export const activeFile = () => state.files.find((file) => file.path === state.activePath) || state.files[0];
export function persist() {
  const serialized = JSON.stringify({ savedAt: Date.now(), projectId: state.projectId, activePath: state.activePath, files: state.files });
  try {
    // localStorage.setItem replaces one key atomically; keeping a second full copy
    // would require double quota for supported multimodal project payloads.
    localStorage.setItem(STORAGE_KEY, serialized);
    localStorage.removeItem(STORAGE_PENDING_KEY);
    return true;
  } catch (error) {
    window.dispatchEvent(new CustomEvent('hhs:visual-ide:storage-error', {
      detail: { classification: 'HHS_P176_LOCAL_STORAGE_WRITE_FAILED', message: error?.message || String(error) },
    }));
    return false;
  }
}
export function setText(selector, value) {
  const node = $(selector);
  if (node) node.textContent = String(value);
}
export function log(message, data) {
  const output = $('#ide-terminal-output');
  if (!output) return;
  output.textContent += `\n[${new Date().toISOString()}] ${message}${data === undefined ? '' : `\n${JSON.stringify(data, null, 2)}`}`;
  output.scrollTop = output.scrollHeight;
}
export function setStage(name, status) {
  const node = $(`[data-stage="${name}"]`);
  if (!node) return;
  node.classList.remove('running', 'complete', 'failed');
  if (status) node.classList.add(status);
}
export function resetStages() {
  $$('#ide-lifecycle-stages [data-stage]').forEach((node) => node.classList.remove('running', 'complete', 'failed'));
}
export function bytesToBase64(bytes) {
  let result = '';
  for (let offset = 0; offset < bytes.length; offset += 0x8000) {
    result += String.fromCharCode(...bytes.subarray(offset, offset + 0x8000));
  }
  return btoa(result);
}
export function base64ToBytes(encoded = '') {
  return Uint8Array.from(atob(encoded), (character) => character.charCodeAt(0));
}
export function mediaTypeFor(name, browserType = '') {
  const extension = name.split('.').pop()?.toLowerCase() || '';
  if (browserType === 'application/pdf' || extension === 'pdf') return 'PDF';
  if (browserType.startsWith('image/')) return 'IMAGE';
  if (browserType.startsWith('audio/')) return 'AUDIO';
  if (browserType.startsWith('video/')) return 'VIDEO';
  if (extension === 'json') return 'JSON';
  if (extension === 'jsonl') return 'JSONL';
  if (extension === 'csv') return 'CSV';
  if (['md', 'markdown'].includes(extension)) return 'MARKDOWN';
  if (extension === 'html') return 'HTML';
  if (extension === 'xml') return 'XML';
  if (['hhs', 'js', 'mjs', 'ts', 'tsx', 'py', 'c', 'h', 'cpp', 'rs', 'go', 'java', 'css'].includes(extension)) return 'SOURCE_CODE';
  if (browserType.startsWith('text/')) return 'TEXT';
  return 'BINARY_OBJECT';
}
export function inferExactExpression(text = $('#ide-source-editor')?.value || '') {
  const candidates = [];
  for (const rawLine of String(text).split(/\r?\n/)) {
    const line = rawLine.replace(/\/\/.*$/, '').replace(/#.*$/, '').trim();
    if (!line) continue;
    candidates.push(line);
    if (line.includes('=')) candidates.push(line.split('=').at(-1).trim());
  }
  for (const candidate of candidates) {
    const normalized = candidate.replace(/[;,.]+$/, '').trim();
    if (/^[0-9+*/()\s-]+$/.test(normalized) && /\d/.test(normalized)) return normalized;
  }
  const literal = String(text).match(/-?\d+(?:\s*\/\s*\d+)?/);
  return literal ? literal[0] : '0';
}
export function sourceBytes() {
  const file = activeFile();
  return file.bytesB64 ? base64ToBytes(file.bytesB64) : new TextEncoder().encode($('#ide-source-editor').value);
}
export function sourcePayload() {
  const file = activeFile();
  return {
    source_b64: bytesToBase64(sourceBytes()),
    source_name: file.name,
    declared_media_type: file.mediaType,
    provenance: `visual-ide://${state.projectId || 'project:pending'}/${file.path}`,
    authorization_scope: 'HHS_VISUAL_IDE_USER_AUTHORIZED_INGRESS',
  };
}
function responsePreview(raw) {
  return String(raw || '').replace(/\s+/g, ' ').trim().slice(0, 240);
}
function abortMessage(path, signal) {
  const reason = signal?.reason ? String(signal.reason) : 'request aborted';
  return `HHS_P176_REQUEST_ABORTED: ${path} · ${reason}`;
}
export async function requestJson(path, options = {}) {
  const controller = new AbortController();
  const upstream = options.signal || null;
  const timeoutMs = Math.max(1, Number(options.timeoutMs || 120000));
  const retryCount = Math.max(0, Math.min(3, Number(options.retryCount || 0)));
  const method = String(options.method || 'GET').toUpperCase();
  const fetchOptions = { ...options };
  delete fetchOptions.timeoutMs;
  delete fetchOptions.retryCount;
  delete fetchOptions.signal;
  const forwardAbort = () => controller.abort(upstream?.reason || 'HHS_P176_PARENT_JOB_ABORTED');
  if (upstream?.aborted) forwardAbort();
  else upstream?.addEventListener('abort', forwardAbort, { once: true });
  const timer = setTimeout(() => controller.abort('HHS_P176_REQUEST_TIMEOUT'), timeoutMs);
  try {
    let lastError = null;
    for (let attempt = 0; attempt <= retryCount; attempt += 1) {
      if (controller.signal.aborted) throw new DOMException(abortMessage(path, controller.signal), 'AbortError');
      try {
        const response = await fetch(path, {
          ...fetchOptions,
          signal: controller.signal,
          headers: { Accept: 'application/json', ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...(options.headers || {}) },
        });
        const contentType = response.headers.get('content-type') || 'unknown';
        const raw = await response.text();
        let payload;
        try { payload = raw ? JSON.parse(raw) : {}; }
        catch {
          const preview = responsePreview(raw);
          throw new Error(
            `HHS_API_ROUTE_UNREACHABLE: ${path} returned HTTP ${response.status} ${contentType} instead of JSON${preview ? ` · ${preview}` : ''}`,
          );
        }
        if (!response.ok) {
          const message = payload.detail?.detail || payload.detail?.classification || payload.detail || payload.error || `HTTP ${response.status}`;
          const error = new Error(message);
          error.status = response.status;
          throw error;
        }
        return payload;
      } catch (error) {
        lastError = error;
        if (controller.signal.aborted) throw new DOMException(abortMessage(path, controller.signal), 'AbortError');
        const retryable = method === 'GET' && attempt < retryCount && (!error?.status || Number(error.status) >= 500);
        if (!retryable) throw error;
        await new Promise((resolve, reject) => {
          const delay = setTimeout(resolve, 150 * (attempt + 1));
          controller.signal.addEventListener('abort', () => {
            clearTimeout(delay);
            reject(new DOMException(abortMessage(path, controller.signal), 'AbortError'));
          }, { once: true });
        });
      }
    }
    throw lastError || new Error(`HHS_P176_REQUEST_FAILED: ${path}`);
  } finally {
    clearTimeout(timer);
    upstream?.removeEventListener?.('abort', forwardAbort);
  }
}
export async function ensureProject(options = {}) {
  if (state.projectId) return state.projectId;
  const session = await requestJson('/api/runtime/workspace/session', {
    method: 'POST',
    signal: options.signal,
    body: JSON.stringify({ name: 'HHS Visual IDE Project' }),
    timeoutMs: 30000,
  });
  state.projectId = session.project?.project_id || session.project_summaries?.[0]?.project_id || 'project:visual-development';
  setText('#ide-project-label', state.projectId);
  setText('#active-thread', state.projectId);
  persist();
  return state.projectId;
}
