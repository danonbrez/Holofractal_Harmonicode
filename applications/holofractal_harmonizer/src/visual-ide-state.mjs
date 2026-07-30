export const $ = (selector) => document.querySelector(selector);
export const $$ = (selector) => [...document.querySelectorAll(selector)];
export const TEXT_MODALITIES = new Set(['TEXT', 'MARKDOWN', 'SOURCE_CODE', 'JSON', 'JSONL', 'CSV', 'HTML', 'XML', 'HHS_CONTRACT', 'HHS_RECEIPT', 'HHS_MANIFEST', 'HHS_VECTOR_PACKET']);
const STORAGE_KEY = 'hhs.visualIde.v1';
const genesis = `a²=1\nb²=2\nc²=3\nP=72\np=64\nq=81\nΔ=P²-pq\n(P²-pq)-Δ=0`;
const stored = (() => {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null'); }
  catch { return null; }
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
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ projectId: state.projectId, activePath: state.activePath, files: state.files }));
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
export async function requestJson(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), options.timeoutMs || 120000);
  try {
    const response = await fetch(path, {
      ...options,
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
      throw new Error(payload.detail?.detail || payload.detail?.classification || payload.detail || payload.error || `HTTP ${response.status}`);
    }
    return payload;
  } finally { clearTimeout(timer); }
}
export async function ensureProject() {
  if (state.projectId) return state.projectId;
  const session = await requestJson('/api/runtime/workspace/session', {
    method: 'POST',
    body: JSON.stringify({ name: 'HHS Visual IDE Project' }),
    timeoutMs: 30000,
  });
  state.projectId = session.project?.project_id || session.project_summaries?.[0]?.project_id || 'project:visual-development';
  setText('#ide-project-label', state.projectId);
  setText('#active-thread', state.projectId);
  persist();
  return state.projectId;
}