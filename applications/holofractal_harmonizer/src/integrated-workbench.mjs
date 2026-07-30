import {
  $, state, activeFile, persist, setText, log, base64ToBytes, requestJson,
} from './visual-ide-state.mjs';
import { renderFiles, openBottomTab } from './visual-ide-ui.mjs';

const encoder = new TextEncoder();
let previewUrl = null;
let previewDocument = '';
const repositoryState = {
  status: null,
  passes: [],
  commits: [],
  commitPage: 1,
  commitsHaveMore: false,
  mode: 'passes',
  loading: false,
};

function syncActiveEditor() {
  const file = activeFile();
  const editor = $('#ide-source-editor');
  if (file && editor && !file.bytesB64) {
    file.content = editor.value;
    persist();
    renderFiles();
  }
}

function normalizePath(path) {
  const output = [];
  for (const part of String(path || '').replaceAll('\\', '/').split('/')) {
    if (!part || part === '.') continue;
    if (part === '..') output.pop();
    else output.push(part);
  }
  return output.join('/');
}

function resolvePath(basePath, reference) {
  if (/^(?:[a-z]+:|\/\/|#|data:|blob:)/i.test(reference)) return null;
  const base = normalizePath(basePath).split('/');
  base.pop();
  return normalizePath([...base, reference].join('/'));
}

function findFile(path) {
  const normalized = normalizePath(path);
  return state.files.find((file) => normalizePath(file.path) === normalized) || null;
}

function fileText(file) {
  if (!file) return '';
  if (!file.bytesB64) return file.content || '';
  try { return new TextDecoder().decode(base64ToBytes(file.bytesB64)); }
  catch { return ''; }
}

function fileBytes(file) {
  return file?.bytesB64 ? base64ToBytes(file.bytesB64) : encoder.encode(file?.content || '');
}

function browserMime(file) {
  const extension = String(file?.name || '').split('.').pop()?.toLowerCase();
  const byExtension = {
    png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', gif: 'image/gif', webp: 'image/webp', svg: 'image/svg+xml',
    mp3: 'audio/mpeg', wav: 'audio/wav', ogg: 'audio/ogg', flac: 'audio/flac',
    mp4: 'video/mp4', webm: 'video/webm', mov: 'video/quicktime',
    pdf: 'application/pdf', html: 'text/html', css: 'text/css', js: 'text/javascript', mjs: 'text/javascript',
    json: 'application/json', md: 'text/markdown', txt: 'text/plain',
  };
  return byExtension[extension] || ({ IMAGE: 'image/*', AUDIO: 'audio/*', VIDEO: 'video/*', PDF: 'application/pdf' }[file?.mediaType]) || 'application/octet-stream';
}

function entrypointOptions() {
  const select = $('#ide-preview-entrypoint');
  if (!select) return;
  const previous = select.value;
  const candidates = state.files.filter((file) => /\.html?$/i.test(file.path));
  select.replaceChildren();
  for (const file of candidates) {
    const option = document.createElement('option');
    option.value = file.path;
    option.textContent = file.path;
    select.append(option);
  }
  if (candidates.length) select.value = candidates.some((file) => file.path === previous) ? previous : candidates[0].path;
  select.disabled = !candidates.length;
}

function inlineProjectReferences(htmlFile) {
  let html = fileText(htmlFile);
  html = html.replace(/<link\b([^>]*?)href=["']([^"']+)["']([^>]*)>/gi, (match, before, reference, after) => {
    const resolved = resolvePath(htmlFile.path, reference);
    const file = resolved ? findFile(resolved) : null;
    if (!file || !/\.css$/i.test(file.path)) return match;
    return `<style data-hhs-inline-source="${resolved.replaceAll('"', '&quot;')}">${fileText(file).replace(/<\/style/gi, '<\\/style')}</style>`;
  });
  html = html.replace(/<script\b([^>]*?)src=["']([^"']+)["']([^>]*)><\/script>/gi, (match, before, reference, after) => {
    const resolved = resolvePath(htmlFile.path, reference);
    const file = resolved ? findFile(resolved) : null;
    if (!file || !/\.(?:m?js)$/i.test(file.path)) return match;
    const moduleType = /type\s*=\s*["']module["']/i.test(`${before} ${after}`) ? ' type="module"' : '';
    return `<script${moduleType} data-hhs-inline-source="${resolved.replaceAll('"', '&quot;')}">${fileText(file).replace(/<\/script/gi, '<\\/script')}</script>`;
  });
  const bridge = `<script>
(() => {
  const send = (kind, values) => parent.postMessage({ source: 'hhs-application-preview', kind, values: values.map((value) => {
    try { return typeof value === 'string' ? value : JSON.stringify(value); } catch { return String(value); }
  }) }, '*');
  for (const kind of ['log', 'info', 'warn', 'error']) {
    const original = console[kind].bind(console);
    console[kind] = (...values) => { original(...values); send(kind, values); };
  }
  addEventListener('error', (event) => send('error', [event.message + ' @ ' + event.filename + ':' + event.lineno]));
  addEventListener('unhandledrejection', (event) => send('error', ['Unhandled rejection', event.reason]));
  send('ready', ['Application preview initialized']);
})();
<\/script>`;
  return html.includes('</body>') ? html.replace(/<\/body>/i, `${bridge}</body>`) : `${html}${bridge}`;
}

function revokePreviewUrl() {
  if (previewUrl) URL.revokeObjectURL(previewUrl);
  previewUrl = null;
}

function previewLog(message, kind = 'info') {
  const output = $('#ide-preview-console');
  if (!output) return;
  output.textContent += `\n[${kind.toUpperCase()}] ${message}`;
  output.scrollTop = output.scrollHeight;
}

export function refreshApplicationPreview() {
  syncActiveEditor();
  entrypointOptions();
  revokePreviewUrl();
  const host = $('#ide-preview-host');
  if (!host) return;
  host.replaceChildren();
  const selectedEntry = $('#ide-preview-entrypoint')?.value;
  const htmlFile = selectedEntry ? findFile(selectedEntry) : null;
  const file = activeFile();

  if (htmlFile) {
    previewDocument = inlineProjectReferences(htmlFile);
    const frame = document.createElement('iframe');
    frame.id = 'ide-application-frame';
    frame.title = `Application preview: ${htmlFile.path}`;
    frame.sandbox = 'allow-scripts allow-forms allow-modals allow-downloads';
    frame.referrerPolicy = 'no-referrer';
    frame.srcdoc = previewDocument;
    host.append(frame);
    setText('#ide-preview-state', `RUNNING · ${htmlFile.path}`);
    previewLog(`Rendered ${htmlFile.path} with project-local CSS and JavaScript in a sandbox.`, 'ready');
    return;
  }

  if (!file) return;
  const mime = browserMime(file);
  previewUrl = URL.createObjectURL(new Blob([fileBytes(file)], { type: mime }));
  let element;
  if (mime.startsWith('image/')) {
    element = document.createElement('img');
    element.alt = file.name;
    element.src = previewUrl;
  } else if (mime.startsWith('audio/')) {
    element = document.createElement('audio');
    element.controls = true;
    element.src = previewUrl;
  } else if (mime.startsWith('video/')) {
    element = document.createElement('video');
    element.controls = true;
    element.src = previewUrl;
  } else if (mime === 'application/pdf') {
    element = document.createElement('iframe');
    element.title = file.name;
    element.src = previewUrl;
  } else {
    element = document.createElement('pre');
    element.textContent = fileText(file) || `[Binary source preserved: ${file.path} · ${fileBytes(file).length} bytes]`;
  }
  element.className = 'ide-modality-preview';
  host.append(element);
  setText('#ide-preview-state', `PREVIEW · ${file.path}`);
}

function openPreviewWindow() {
  if (!previewDocument) refreshApplicationPreview();
  if (!previewDocument) return;
  const url = URL.createObjectURL(new Blob([previewDocument], { type: 'text/html' }));
  window.open(url, '_blank', 'noopener,noreferrer');
  setTimeout(() => URL.revokeObjectURL(url), 60_000);
}

function addBottomTab(name, label) {
  const tabs = document.querySelector('.ide-bottom-tabs');
  const terminalState = $('#ide-terminal-state');
  if (!tabs || tabs.querySelector(`[data-bottom-tab="${name}"]`)) return;
  const button = document.createElement('button');
  button.type = 'button';
  button.dataset.bottomTab = name;
  button.textContent = label;
  button.onclick = () => openBottomTab(name);
  tabs.insertBefore(button, terminalState);
}

function mountPreviewPanel() {
  const bottom = document.querySelector('.ide-bottom-pane');
  if (!bottom || $('#ide-preview-panel')) return;
  addBottomTab('preview', 'Application Preview');
  const panel = document.createElement('div');
  panel.id = 'ide-preview-panel';
  panel.className = 'ide-bottom-panel ide-preview-panel';
  panel.dataset.bottomPanel = 'preview';
  panel.innerHTML = `
    <div class="ide-preview-toolbar">
      <label>Web entrypoint<select id="ide-preview-entrypoint"></select></label>
      <button id="ide-refresh-preview" type="button" class="primary-action">Run Preview</button>
      <button id="ide-open-preview" type="button">Open Window</button>
      <span id="ide-preview-state">READY</span>
    </div>
    <div class="ide-preview-grid">
      <div id="ide-preview-host" class="ide-preview-host" aria-live="polite"></div>
      <pre id="ide-preview-console" class="ide-preview-console">Application preview console.</pre>
    </div>`;
  bottom.append(panel);
  $('#ide-refresh-preview').onclick = refreshApplicationPreview;
  $('#ide-open-preview').onclick = openPreviewWindow;
  $('#ide-preview-entrypoint').onchange = refreshApplicationPreview;
  entrypointOptions();
}

function mountRepositoryExplorer() {
  const registry = $('#registry-nav');
  const runtimeSection = registry?.querySelector('.ide-registry-explorer');
  if (!registry || $('#ide-repository-explorer')) return;
  const section = document.createElement('section');
  section.id = 'ide-repository-explorer';
  section.className = 'ide-repository-explorer';
  section.innerHTML = `
    <div class="explorer-section-title"><span>PASS CONSTRAINTS + HISTORY</span><span id="ide-repository-count">LOADING</span></div>
    <div class="ide-repository-shortcuts">
      <button id="ide-open-passes" type="button"><strong>Pass catalog</strong><small>Contracts · constraints · evidence</small></button>
      <button id="ide-open-commits" type="button"><strong>Commit lineage</strong><small>Legacy history · authoritative main</small></button>
    </div>`;
  registry.insertBefore(section, runtimeSection || null);
  $('#ide-open-passes').onclick = () => openRepositoryPanel('passes');
  $('#ide-open-commits').onclick = () => openRepositoryPanel('commits');
}

function mountRepositoryPanel() {
  const bottom = document.querySelector('.ide-bottom-pane');
  if (!bottom || $('#ide-repository-panel')) return;
  addBottomTab('repository', 'Repository Lineage');
  const panel = document.createElement('div');
  panel.id = 'ide-repository-panel';
  panel.className = 'ide-bottom-panel ide-repository-panel';
  panel.dataset.bottomPanel = 'repository';
  panel.innerHTML = `
    <div class="ide-repository-toolbar">
      <button id="ide-repository-passes" type="button" class="active">Pass constraints</button>
      <button id="ide-repository-commits" type="button">Commit history</button>
      <input id="ide-repository-search" type="search" placeholder="Search passes, constraints, paths, status…">
      <button id="ide-repository-refresh" type="button">Refresh</button>
      <span id="ide-repository-state">LOADING</span>
    </div>
    <div class="ide-repository-layout">
      <div id="ide-repository-list" class="ide-repository-list"></div>
      <article id="ide-repository-detail" class="ide-repository-detail"><h3>Repository lineage</h3><p>Select a pass contract or commit. The editor remains the primary product surface.</p></article>
    </div>
    <div class="ide-repository-footer"><button id="ide-load-more-commits" type="button" hidden>Load older commits</button></div>`;
  bottom.append(panel);
  $('#ide-repository-passes').onclick = () => setRepositoryMode('passes');
  $('#ide-repository-commits').onclick = () => setRepositoryMode('commits');
  $('#ide-repository-search').oninput = renderRepositoryList;
  $('#ide-repository-refresh').onclick = () => void loadRepositoryData(true);
  $('#ide-load-more-commits').onclick = () => void loadMoreCommits();
}

function setRepositoryMode(mode) {
  repositoryState.mode = mode;
  $('#ide-repository-passes')?.classList.toggle('active', mode === 'passes');
  $('#ide-repository-commits')?.classList.toggle('active', mode === 'commits');
  $('#ide-load-more-commits').hidden = mode !== 'commits' || !repositoryState.commitsHaveMore;
  renderRepositoryList();
}

function passSearchText(item) {
  return JSON.stringify(item).toLowerCase();
}

function commitSearchText(item) {
  return `${item.sha} ${item.message} ${item.author} ${item.authored_at}`.toLowerCase();
}

function renderRepositoryList() {
  const host = $('#ide-repository-list');
  if (!host) return;
  host.replaceChildren();
  const needle = ($('#ide-repository-search')?.value || '').trim().toLowerCase();
  const values = repositoryState.mode === 'passes'
    ? repositoryState.passes.filter((item) => !needle || passSearchText(item).includes(needle))
    : repositoryState.commits.filter((item) => !needle || commitSearchText(item).includes(needle));
  for (const item of values) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'ide-repository-item';
    if (repositoryState.mode === 'passes') {
      const heading = document.createElement('strong');
      heading.textContent = `PASS ${String(item.pass_number).padStart(3, '0')} · ${item.title}`;
      const meta = document.createElement('small');
      meta.textContent = `${item.file_count} files · ${item.kinds.join(' / ')} · ${item.constraint_count_sampled} sampled constraints`;
      button.append(heading, meta);
      button.onclick = () => void showPassDetail(item);
    } else {
      const heading = document.createElement('strong');
      heading.textContent = `${item.short_sha} · ${item.message}`;
      const meta = document.createElement('small');
      meta.textContent = `${item.authored_at || 'unknown time'} · ${item.author || 'unknown author'} · ${item.parents?.length || 0} parent(s)`;
      button.append(heading, meta);
      button.onclick = () => showCommitDetail(item);
    }
    host.append(button);
  }
  if (!values.length) {
    const empty = document.createElement('p');
    empty.className = 'ide-repository-empty';
    empty.textContent = repositoryState.loading ? 'Loading repository lineage…' : 'No matching repository history.';
    host.append(empty);
  }
}

async function showPassDetail(item) {
  const detail = $('#ide-repository-detail');
  if (!detail) return;
  detail.replaceChildren();
  const heading = document.createElement('h3');
  heading.textContent = `Pass ${item.pass_number}: ${item.title}`;
  const summary = document.createElement('p');
  summary.textContent = `${item.file_count} repository files carry this pass identity. Types: ${item.kinds.join(', ')}. Status terms: ${item.status_terms.join(', ') || 'not explicitly classified'}.`;
  const fileList = document.createElement('div');
  fileList.className = 'ide-pass-file-list';
  for (const file of item.files) {
    const link = document.createElement('a');
    link.href = file.github_url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = `${file.kind} · ${file.path}`;
    fileList.append(link);
  }
  const constraints = document.createElement('ul');
  for (const excerpt of item.files.flatMap((file) => file.constraint_excerpts || []).slice(0, 20)) {
    const row = document.createElement('li');
    row.textContent = excerpt;
    constraints.append(row);
  }
  const source = document.createElement('pre');
  source.textContent = 'Loading primary contract source…';
  detail.append(heading, summary, fileList, constraints, source);
  try {
    const payload = await requestJson(`/api/runtime/repository/file?path=${encodeURIComponent(item.primary_path)}`, { timeoutMs: 60_000 });
    source.textContent = payload.content || 'No text returned.';
  } catch (error) {
    source.textContent = `Contract source unavailable: ${error.message}`;
  }
}

function showCommitDetail(item) {
  const detail = $('#ide-repository-detail');
  if (!detail) return;
  detail.replaceChildren();
  const heading = document.createElement('h3');
  heading.textContent = item.message;
  const metadata = document.createElement('dl');
  for (const [name, value] of Object.entries({ SHA: item.sha, Parents: (item.parents || []).join(', ') || 'genesis', Author: item.author, Time: item.authored_at })) {
    const term = document.createElement('dt'); term.textContent = name;
    const description = document.createElement('dd'); description.textContent = value || 'unknown';
    metadata.append(term, description);
  }
  const link = document.createElement('a');
  link.href = item.url;
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  link.textContent = 'Open commit on GitHub';
  detail.append(heading, metadata, link);
}

async function loadMoreCommits() {
  if (!repositoryState.commitsHaveMore || repositoryState.loading) return;
  repositoryState.loading = true;
  setText('#ide-repository-state', 'LOADING OLDER COMMITS');
  try {
    const nextPage = repositoryState.commitPage + 1;
    const payload = await requestJson(`/api/runtime/repository/commits?page=${nextPage}&limit=100`, { timeoutMs: 60_000 });
    repositoryState.commitPage = nextPage;
    repositoryState.commits.push(...(payload.commits || []));
    repositoryState.commitsHaveMore = Boolean(payload.has_more);
    renderRepositoryList();
  } finally {
    repositoryState.loading = false;
    setText('#ide-repository-state', `${repositoryState.commits.length} COMMITS LOADED`);
    $('#ide-load-more-commits').hidden = !repositoryState.commitsHaveMore;
  }
}

async function loadRepositoryData(force = false) {
  if (repositoryState.loading || (!force && repositoryState.status)) return;
  repositoryState.loading = true;
  renderRepositoryList();
  setText('#ide-repository-state', 'INDEXING REPOSITORY');
  try {
    const [status, passes, commits] = await Promise.all([
      requestJson('/api/runtime/repository/status', { timeoutMs: 60_000 }),
      requestJson('/api/runtime/repository/passes', { timeoutMs: 120_000 }),
      requestJson('/api/runtime/repository/commits?page=1&limit=100', { timeoutMs: 60_000 }),
    ]);
    repositoryState.status = status;
    repositoryState.passes = passes.passes || [];
    repositoryState.commits = commits.commits || [];
    repositoryState.commitPage = 1;
    repositoryState.commitsHaveMore = Boolean(commits.has_more);
    setText('#ide-repository-count', `${status.pass_count} PASSES`);
    setText('#ide-repository-state', `${status.pass_count} PASSES · ${repositoryState.commits.length} COMMITS`);
    renderRepositoryList();
  } catch (error) {
    setText('#ide-repository-state', 'HISTORY DEGRADED');
    log(`Repository lineage unavailable: ${error.message}`);
  } finally {
    repositoryState.loading = false;
  }
}

function openRepositoryPanel(mode) {
  setRepositoryMode(mode);
  openBottomTab('repository');
  void loadRepositoryData();
}

function mountMenuActions() {
  const menu = document.querySelector('.ide-menu-bar');
  const api = $('#open-api');
  if (!menu || !api) return;
  if (!$('#ide-menu-preview')) {
    const preview = document.createElement('button');
    preview.id = 'ide-menu-preview';
    preview.type = 'button';
    preview.textContent = 'Preview App';
    preview.onclick = () => { openBottomTab('preview'); refreshApplicationPreview(); };
    menu.insertBefore(preview, api);
  }
  if (!$('#ide-menu-history')) {
    const history = document.createElement('button');
    history.id = 'ide-menu-history';
    history.type = 'button';
    history.textContent = 'Pass History';
    history.onclick = () => openRepositoryPanel('passes');
    menu.insertBefore(history, api);
  }
}

function onPreviewMessage(event) {
  if (event.data?.source !== 'hhs-application-preview') return;
  previewLog((event.data.values || []).join(' '), event.data.kind || 'log');
}

export function initIntegratedWorkbench() {
  mountPreviewPanel();
  mountRepositoryExplorer();
  mountRepositoryPanel();
  mountMenuActions();
  addEventListener('message', onPreviewMessage);
  window.HHSIntegratedWorkbench = Object.freeze({
    preview: refreshApplicationPreview,
    openHistory: openRepositoryPanel,
    loadRepositoryData,
  });
  void loadRepositoryData();
}
