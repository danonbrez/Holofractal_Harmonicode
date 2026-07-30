import {
  $,
  TEXT_MODALITIES,
  state,
  activeFile,
  persist,
  setText,
  log,
  bytesToBase64,
  base64ToBytes,
  mediaTypeFor,
  requestJson,
  ensureProject,
  inferExactExpression,
} from './visual-ide-state.mjs';
import { renderFiles, activateFile, openBottomTab } from './visual-ide-ui.mjs';
import { createStoredZip } from './project-zip.mjs';

const encoder = new TextEncoder();
const MAX_PROJECT_FILES = 64;
const MAX_PROJECT_BYTES = 24 * 1024 * 1024;
const SUPPORTED_TARGETS = [
  'HHS_IR',
  'C_KERNEL_PLAN',
  'C_SOURCE',
  'PYTHON_ADAPTER',
  'JSON_EXECUTION_GRAPH',
  'DOT_GRAPH',
  'BYTECODE_OR_VM_PLAN',
  'RECEIPT_ONLY_PLAN',
];
const DEFAULT_TARGETS = new Set(['HHS_IR', 'C_SOURCE', 'JSON_EXECUTION_GRAPH']);

function safePath(value, fallback = 'untitled') {
  const parts = String(value || fallback)
    .replaceAll('\\', '/')
    .split('/')
    .filter((part) => part && part !== '.');
  if (parts.includes('..')) throw new Error('PROJECT_PATH_TRAVERSAL_REJECTED');
  return parts.join('/') || fallback;
}

function fileBytes(file) {
  return file.bytesB64 ? base64ToBytes(file.bytesB64) : encoder.encode(file.content || '');
}

function sourcePayload(file, projectId) {
  const bytes = fileBytes(file);
  return {
    source_b64: bytesToBase64(bytes),
    source_name: file.name,
    declared_media_type: file.mediaType,
    provenance: `visual-ide://${projectId}/${safePath(file.path)}`,
    authorization_scope: 'HHS_VISUAL_IDE_USER_AUTHORIZED_PROJECT_INGRESS',
  };
}

function targetSelection() {
  return [...document.querySelectorAll('#ide-project-targets input:checked')].map((input) => input.value);
}

function syncActiveEditor() {
  const file = activeFile();
  const editor = $('#ide-source-editor');
  if (file && editor && !file.bytesB64) {
    file.content = editor.value;
    persist();
    renderFiles();
  }
}

function buildStatus(message, stateName = '') {
  setText('#ide-project-build-state', message);
  const node = $('#ide-project-build-state');
  if (node) node.dataset.state = stateName;
}

function setBuildButtons(busy, archiveReady = Boolean(state.projectBuild?.archiveBytes)) {
  const build = $('#ide-build-project');
  const exportButton = $('#ide-export-project');
  if (build) build.disabled = busy;
  if (exportButton) exportButton.disabled = busy || !archiveReady;
}

function updateEntrypoints() {
  const select = $('#ide-project-entrypoint');
  if (!select) return;
  const selected = select.value || state.activePath;
  select.replaceChildren();
  for (const file of state.files) {
    const option = document.createElement('option');
    option.value = file.path;
    option.textContent = file.path;
    option.selected = file.path === selected;
    select.append(option);
  }
}

function addOrReplaceFile(entry) {
  const existing = state.files.findIndex((file) => file.path === entry.path);
  if (existing >= 0) state.files.splice(existing, 1, entry);
  else state.files.push(entry);
}

function createPathFile() {
  const requested = window.prompt('Create project file path', 'src/component.hhs');
  if (!requested) return;
  let path;
  try { path = safePath(requested); }
  catch (error) { log(`File creation rejected: ${error.message}`); return; }
  let mediaType = mediaTypeFor(path);
  if (mediaType === 'BINARY_OBJECT') mediaType = 'TEXT';
  addOrReplaceFile({ path, name: path.split('/').at(-1), mediaType, content: '', dirty: true });
  persist();
  renderFiles();
  updateEntrypoints();
  activateFile(path);
  $('#ide-source-editor')?.focus();
  log(`Created ${path} in the preserved browser working copy.`);
}

const STARTERS = {
  web: [
    ['web/index.html', 'HTML', '<!doctype html>\n<html lang="en">\n<head>\n  <meta charset="utf-8">\n  <meta name="viewport" content="width=device-width,initial-scale=1">\n  <title>HHS Project</title>\n  <link rel="stylesheet" href="./style.css">\n</head>\n<body>\n  <main id="app">HHS project ready.</main>\n  <script src="./app.js"></script>\n</body>\n</html>\n'],
    ['web/app.js', 'SOURCE_CODE', 'document.querySelector("#app").textContent = "HHS application lifecycle online";\n'],
    ['web/style.css', 'SOURCE_CODE', ':root { color-scheme: dark; }\nbody { margin: 0; font-family: system-ui, sans-serif; }\n'],
    ['README.md', 'MARKDOWN', '# HHS Application Project\n\nEdit, compile, validate, and export this project from the visual IDE.\n'],
  ],
  content: [
    ['content/index.md', 'MARKDOWN', '# New Content Project\n\nBegin writing here.\n'],
    ['content/metadata.json', 'JSON', '{\n  "title": "New Content Project",\n  "targets": ["web", "document", "archive"]\n}\n'],
    ['assets/README.md', 'MARKDOWN', '# Assets\n\nImport images, audio, video, PDFs, or other source-preserved media into this folder.\n'],
  ],
  automation: [
    ['src/main.hhs', 'SOURCE_CODE', 'a²=1\nb²=2\nc²=3\nP=72\np=64\nq=81\nΔ=P²-pq\n(P²-pq)-Δ=0\n'],
    ['src/adapter.py', 'SOURCE_CODE', 'def main() -> None:\n    print("HHS automation adapter ready")\n\nif __name__ == "__main__":\n    main()\n'],
    ['project.json', 'JSON', '{\n  "schema": "HHS_MULTIMODAL_PROJECT_V1",\n  "entrypoint": "src/main.hhs"\n}\n'],
  ],
};

function addStarter() {
  const kind = $('#ide-project-starter')?.value || 'web';
  const entries = STARTERS[kind] || STARTERS.web;
  let added = 0;
  for (const [path, mediaType, content] of entries) {
    if (state.files.some((file) => file.path === path)) continue;
    state.files.push({ path, name: path.split('/').at(-1), mediaType, content, dirty: true });
    added += 1;
  }
  persist();
  renderFiles();
  updateEntrypoints();
  if (added) activateFile(entries[0][0]);
  log(`Added ${added} non-destructive ${kind} starter files; existing files were preserved.`);
}

async function importFolder(files) {
  if (!files.length) return;
  for (const browserFile of files) {
    const bytes = new Uint8Array(await browserFile.arrayBuffer());
    const path = safePath(browserFile.webkitRelativePath || browserFile.name);
    const mediaType = mediaTypeFor(browserFile.name, browserFile.type);
    const entry = { path, name: browserFile.name, mediaType, dirty: false };
    if (TEXT_MODALITIES.has(mediaType)) entry.content = new TextDecoder().decode(bytes);
    else entry.bytesB64 = bytesToBase64(bytes);
    addOrReplaceFile(entry);
  }
  state.activePath = safePath(files[0].webkitRelativePath || files[0].name);
  persist();
  renderFiles();
  updateEntrypoints();
  activateFile(state.activePath);
  log(`Imported ${files.length} files with relative folder paths preserved.`);
}

function receiptSummary(result) {
  if (!result) return {};
  if (result.receipts) return result.receipts;
  return {
    receipt_hash72: result.receipt?.receipt_hash72 || result.receipt_hash72 || null,
    projection_hash72: result.projection_hash72 || null,
    operation_hash216: result.ingestion_operation_hash216 || null,
  };
}

async function buildTextFile({ file, bytes, projectId, projectName, targets, steps }) {
  const sourceText = new TextDecoder().decode(bytes);
  const primaryTarget = targets[0];
  const lifecycle = await requestJson('/api/runtime/development/lifecycle', {
    method: 'POST',
    timeoutMs: 180000,
    body: JSON.stringify({
      ...sourcePayload(file, projectId),
      project_id: projectId,
      project_name: projectName,
      expression: inferExactExpression(sourceText),
      interpretation_scope: 'SOURCE_EXACT_NUMERIC_PROBE',
      target: primaryTarget,
      steps,
    }),
  });
  const targetResults = { [primaryTarget]: lifecycle.compilation };
  for (const target of targets.slice(1)) {
    targetResults[target] = await requestJson('/api/runtime/workspace/command', {
      method: 'POST',
      timeoutMs: 120000,
      body: JSON.stringify({
        operation: 'compile.execute',
        payload: {
          project_id: projectId,
          source_object_id: `object:${safePath(file.path)}`,
          source_text: sourceText,
          target,
        },
      }),
    });
  }
  return {
    ok: Boolean(lifecycle.ok && Object.values(targetResults).every((value) => value?.ok !== false)),
    lifecycle,
    targetResults,
    receipts: receiptSummary(lifecycle),
  };
}

async function buildBinaryFile({ file, projectId }) {
  const ingress = await requestJson('/api/runtime/multimodal-ingress/ingest', {
    method: 'POST',
    timeoutMs: 180000,
    body: JSON.stringify(sourcePayload(file, projectId)),
  });
  const sourceHash = ingress.source?.source_hash;
  const snapshot = sourceHash
    ? await requestJson(`/api/runtime/multimodal-ingress/snapshots/${encodeURIComponent(sourceHash)}`, { timeoutMs: 120000 })
    : null;
  return {
    ok: Boolean(ingress?.source && snapshot?.ok),
    ingress,
    snapshot,
    targetResults: {},
    receipts: { ingress: ingress.receipt, snapshot: receiptSummary(snapshot) },
  };
}

function readableBuildSummary(manifest, archiveBytes) {
  const successful = manifest.files.filter((file) => file.ok).length;
  const compiled = manifest.files.reduce((total, file) => total + Object.keys(file.targets || {}).length, 0);
  return [
    'HHS multimodal project archive ready.',
    `Project: ${manifest.project_name}`,
    `Files preserved: ${manifest.file_count}`,
    `Backend-admitted file lifecycles: ${successful}/${manifest.file_count}`,
    `Target artifacts: ${compiled}`,
    `Targets: ${manifest.targets.join(', ')}`,
    `Archive bytes: ${archiveBytes.length}`,
    `Entrypoint: ${manifest.entrypoint}`,
    'The ZIP contains original source files, backend lifecycle evidence, target artifacts, receipts, and the project manifest.',
  ].join('\n');
}

export async function buildProjectArchive() {
  if (state.projectBuildBusy) return state.projectBuild || null;
  syncActiveEditor();
  const files = state.files.map((file) => ({ ...file, path: safePath(file.path) }));
  const targets = targetSelection();
  if (!files.length) throw new Error('PROJECT_HAS_NO_FILES');
  if (!targets.length) throw new Error('PROJECT_HAS_NO_COMPILER_TARGETS');
  if (files.length > MAX_PROJECT_FILES) throw new Error(`PROJECT_FILE_LIMIT_EXCEEDED:${MAX_PROJECT_FILES}`);
  const totalBytes = files.reduce((total, file) => total + fileBytes(file).length, 0);
  if (totalBytes > MAX_PROJECT_BYTES) throw new Error(`PROJECT_BYTE_LIMIT_EXCEEDED:${MAX_PROJECT_BYTES}`);

  state.projectBuildBusy = true;
  setBuildButtons(true, false);
  buildStatus('Binding project authority…', 'running');
  setText('#ide-terminal-state', 'PROJECT BUILD');

  try {
    const projectId = await ensureProject();
    const projectName = ($('#ide-project-name')?.value || 'HHS Multimodal Project').trim();
    const steps = Math.min(32, Math.max(1, Number($('#ide-run-steps')?.value || 8)));
    const entrypoint = $('#ide-project-entrypoint')?.value || files[0].path;
    const archiveEntries = [];
    const fileResults = [];

    for (let index = 0; index < files.length; index += 1) {
      const file = files[index];
      const bytes = fileBytes(file);
      buildStatus(`Processing ${index + 1}/${files.length}: ${file.path}`, 'running');
      archiveEntries.push({ path: `source/${file.path}`, data: bytes });
      let result;
      try {
        result = TEXT_MODALITIES.has(file.mediaType)
          ? await buildTextFile({ file, bytes, projectId, projectName, targets, steps })
          : await buildBinaryFile({ file, projectId });
      } catch (error) {
        result = { ok: false, error: error.message, targetResults: {}, receipts: {} };
        log(`Project file lifecycle failed for ${file.path}: ${error.message}`);
      }

      const evidencePath = `evidence/${file.path}.lifecycle.json`;
      archiveEntries.push({ path: evidencePath, data: JSON.stringify(result, null, 2) });
      for (const [target, targetResult] of Object.entries(result.targetResults || {})) {
        archiveEntries.push({ path: `build/${target}/${file.path}.artifact.json`, data: JSON.stringify(targetResult, null, 2) });
      }
      archiveEntries.push({ path: `receipts/${file.path}.receipts.json`, data: JSON.stringify(result.receipts || {}, null, 2) });
      fileResults.push({
        path: file.path,
        name: file.name,
        media_type: file.mediaType,
        size_bytes: bytes.length,
        ok: Boolean(result.ok),
        source_preserved: true,
        evidence_path: evidencePath,
        targets: Object.fromEntries(Object.keys(result.targetResults || {}).map((target) => [target, `build/${target}/${file.path}.artifact.json`])),
        receipts: result.receipts || {},
        error: result.error || null,
      });
    }

    const manifest = {
      schema: 'HHS_MULTIMODAL_PROJECT_ARCHIVE_MANIFEST_V1',
      project_id: projectId,
      project_name: projectName,
      entrypoint,
      created_at: new Date().toISOString(),
      file_count: files.length,
      total_source_bytes: totalBytes,
      targets,
      files: fileResults,
      original_source_preserved: true,
      relative_folder_paths_preserved: true,
      backend_evidence_unmodified: true,
      frontend_runtime_authority: false,
      frontend_archive_packaging_only: true,
      authority_paths: [
        '/api/runtime/development/lifecycle',
        '/api/runtime/workspace/command',
        '/api/runtime/multimodal-ingress/ingest',
        '/api/runtime/multimodal-ingress/snapshots/{source_hash}',
      ],
    };
    archiveEntries.push({ path: 'project.hhs-manifest.json', data: JSON.stringify(manifest, null, 2) });
    archiveEntries.push({
      path: 'ARCHIVE_README.txt',
      data: 'This archive preserves the project working tree and packages unmodified backend lifecycle, compile, VM81, Hash72, and Hash216 evidence. Frontend ZIP creation is packaging only and does not assert runtime authority.\n',
    });
    const archiveBytes = createStoredZip(archiveEntries);
    const archiveName = `${safePath(projectName.toLowerCase().replace(/[^a-z0-9._-]+/g, '-'), 'hhs-project')}.zip`;
    state.projectBuild = { manifest, archiveBytes, archiveName, archiveEntries: archiveEntries.length };
    setBuildButtons(false, true);
    buildStatus(`READY · ${files.length} files · ${targets.length} targets`, 'complete');
    setText('#ide-egress-state', archiveName);
    setText('#ide-egress-output', readableBuildSummary(manifest, archiveBytes));
    setText('#validation-state', 'PROJECT SOURCES → BACKEND LIFECYCLES → MULTI-TARGET ARTIFACTS → ZIP');
    setText('#ide-terminal-state', fileResults.every((file) => file.ok) ? 'PROJECT BUILD COMPLETE' : 'PROJECT BUILD PARTIAL');
    openBottomTab('egress');
    log('Multifile project lifecycle and ZIP archive completed.', {
      project_id: projectId,
      archive_name: archiveName,
      file_count: files.length,
      targets,
      all_files_ok: fileResults.every((file) => file.ok),
    });
    return state.projectBuild;
  } finally {
    state.projectBuildBusy = false;
    setBuildButtons(false, Boolean(state.projectBuild?.archiveBytes));
  }
}

export async function downloadProjectArchive() {
  const build = state.projectBuild?.archiveBytes ? state.projectBuild : await buildProjectArchive();
  if (!build?.archiveBytes) return;
  const url = URL.createObjectURL(new Blob([build.archiveBytes], { type: 'application/zip' }));
  const link = Object.assign(document.createElement('a'), { href: url, download: build.archiveName });
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  log(`Exported ${build.archiveName} with source, build, evidence, and receipt folders.`);
}

function installTheme() {
  document.documentElement.classList.add('hhs-harmonic-studio-theme');
  if (document.querySelector('link[data-hhs-harmonic-theme]')) return;
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = './src/harmonic-studio-theme.css';
  link.dataset.hhsHarmonicTheme = 'true';
  document.head.append(link);
}

function mountControls() {
  if ($('#ide-project-build')) return;
  const lifecycleWindow = document.querySelector('.lifecycle-control-window');
  if (!lifecycleWindow) return;
  const section = document.createElement('section');
  section.id = 'ide-project-build';
  section.className = 'ide-project-build';
  section.innerHTML = `
    <div class="ide-project-build-heading">
      <div><span>PROJECT LIFECYCLE</span><strong>Multifile build + ZIP export</strong></div>
      <span id="ide-project-build-state" data-state="idle">LOCAL WORKTREE</span>
    </div>
    <div class="ide-project-fields">
      <label>Project name<input id="ide-project-name" value="HHS Multimodal Project" maxlength="120"></label>
      <label>Entrypoint<select id="ide-project-entrypoint"></select></label>
      <label>Starter<select id="ide-project-starter"><option value="web">Web application</option><option value="content">Content package</option><option value="automation">HHS automation</option></select></label>
    </div>
    <div id="ide-project-targets" class="ide-project-targets" aria-label="Compiler targets">
      ${SUPPORTED_TARGETS.map((target) => `<label><input type="checkbox" value="${target}" ${DEFAULT_TARGETS.has(target) ? 'checked' : ''}><span>${target.replaceAll('_', ' ')}</span></label>`).join('')}
    </div>
    <div class="ide-project-actions">
      <button id="ide-create-path" type="button">New path</button>
      <button id="ide-add-starter" type="button">Add starter</button>
      <button id="ide-import-folder" type="button">Import folder</button>
      <input id="ide-folder-input" type="file" multiple hidden webkitdirectory directory>
      <button id="ide-build-project" type="button" class="primary-action">Build project</button>
      <button id="ide-export-project" type="button" disabled>Export ZIP</button>
    </div>`;
  lifecycleWindow.append(section);

  const menu = document.querySelector('.ide-menu-bar');
  const egress = menu?.querySelector('[data-ide-command="egress"]');
  if (menu && egress && !$('#ide-menu-build-project')) {
    const button = document.createElement('button');
    button.type = 'button';
    button.id = 'ide-menu-build-project';
    button.className = 'ide-menu-primary';
    button.textContent = 'Build Project';
    button.onclick = () => void buildProjectArchive().catch((error) => {
      buildStatus(`FAILED · ${error.message}`, 'failed');
      log(`Project build rejected: ${error.message}`);
    });
    menu.insertBefore(button, egress);
  }

  $('#ide-create-path').onclick = createPathFile;
  $('#ide-add-starter').onclick = addStarter;
  $('#ide-import-folder').onclick = () => $('#ide-folder-input').click();
  $('#ide-folder-input').onchange = async (event) => {
    await importFolder([...event.target.files]);
    event.target.value = '';
  };
  $('#ide-build-project').onclick = () => void buildProjectArchive().catch((error) => {
    buildStatus(`FAILED · ${error.message}`, 'failed');
    setText('#ide-terminal-state', 'PROJECT BUILD FAILED');
    log(`Project build rejected: ${error.message}`);
  });
  $('#ide-export-project').onclick = () => void downloadProjectArchive().catch((error) => log(`ZIP export failed: ${error.message}`));
  updateEntrypoints();
}

export function initProjectLifecycle() {
  installTheme();
  mountControls();
  window.HHSProjectLifecycle = Object.freeze({
    build: buildProjectArchive,
    exportZip: downloadProjectArchive,
    supportedTargets: [...SUPPORTED_TARGETS],
  });
}
