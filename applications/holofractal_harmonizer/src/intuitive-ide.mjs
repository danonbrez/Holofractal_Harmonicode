import {
  $, TEXT_MODALITIES, state, persist, mediaTypeFor, bytesToBase64, log, setText,
} from './visual-ide-state.mjs';
import { renderFiles, activateFile, openBottomTab } from './visual-ide-ui.mjs';

const undoStack = [];
const MAX_UNDO = 20;
let selectedTemplate = 'web';
let dragDepth = 0;

function cloneFiles(files) {
  return files.map((file) => ({ ...file }));
}

function checkpoint(label) {
  undoStack.push({ label, files: cloneFiles(state.files), activePath: state.activePath });
  if (undoStack.length > MAX_UNDO) undoStack.shift();
  updateUndoState();
}

function updateUndoState() {
  const button = $('#ide-undo-safe-change');
  if (!button) return;
  button.disabled = !undoStack.length;
  button.title = undoStack.length ? `Undo ${undoStack.at(-1).label}` : 'Nothing to undo';
}

function undoSafeChange() {
  const prior = undoStack.pop();
  if (!prior) return;
  state.files.splice(0, state.files.length, ...cloneFiles(prior.files));
  state.activePath = prior.activePath;
  persist();
  renderFiles();
  activateFile(state.activePath);
  window.HHSIntegratedWorkbench?.preview?.();
  setWorkflowStatus(`Undid ${prior.label}.`, 'ready');
  log(`Reversible project change restored: ${prior.label}.`);
  updateUndoState();
}

function normalizePath(value) {
  const parts = [];
  for (const raw of String(value || '').replaceAll('\\', '/').split('/')) {
    const part = raw.trim();
    if (!part || part === '.') continue;
    if (part === '..') throw new Error('PROJECT_PATH_TRAVERSAL_REJECTED');
    parts.push(part.replace(/[\u0000-\u001f]/g, ''));
  }
  return parts.join('/');
}

function splitExtension(path) {
  const slash = path.lastIndexOf('/');
  const directory = slash >= 0 ? path.slice(0, slash + 1) : '';
  const filename = slash >= 0 ? path.slice(slash + 1) : path;
  const dot = filename.lastIndexOf('.');
  if (dot <= 0) return { directory, stem: filename, extension: '' };
  return { directory, stem: filename.slice(0, dot), extension: filename.slice(dot) };
}

function collisionSafePath(requested) {
  const normalized = normalizePath(requested) || 'untitled';
  if (!state.files.some((file) => file.path === normalized)) return normalized;
  const { directory, stem, extension } = splitExtension(normalized);
  let index = 2;
  let candidate = `${directory}${stem}-${index}${extension}`;
  while (state.files.some((file) => file.path === candidate)) {
    index += 1;
    candidate = `${directory}${stem}-${index}${extension}`;
  }
  return candidate;
}

function setWorkflowStatus(message, status = 'working') {
  setText('#ide-simple-workflow-state', message);
  const node = $('#ide-simple-workflow-state');
  if (node) node.dataset.state = status;
}

async function safeImportFiles(browserFiles, { preserveFolders = false, runPreview = true } = {}) {
  const files = [...browserFiles];
  if (!files.length) return [];
  checkpoint(`import of ${files.length} file${files.length === 1 ? '' : 's'}`);
  setWorkflowStatus(`Adding ${files.length} file${files.length === 1 ? '' : 's'}…`);
  const added = [];
  for (const browserFile of files) {
    const relative = preserveFolders && browserFile.webkitRelativePath
      ? browserFile.webkitRelativePath
      : `assets/${browserFile.name}`;
    const path = collisionSafePath(relative);
    const bytes = new Uint8Array(await browserFile.arrayBuffer());
    const mediaType = mediaTypeFor(browserFile.name, browserFile.type);
    const entry = {
      path,
      name: path.split('/').at(-1),
      mediaType,
      dirty: false,
      importedName: browserFile.name,
    };
    if (TEXT_MODALITIES.has(mediaType)) entry.content = new TextDecoder().decode(bytes);
    else entry.bytesB64 = bytesToBase64(bytes);
    state.files.push(entry);
    added.push(entry);
  }
  state.activePath = added[0].path;
  persist();
  renderFiles();
  activateFile(state.activePath);
  setWorkflowStatus(`${added.length} file${added.length === 1 ? '' : 's'} added safely.`, 'ready');
  log(`Added ${added.length} project files without replacing existing paths.`, {
    paths: added.map((file) => file.path),
  });
  if (runPreview) window.HHSIntegratedWorkbench?.preview?.();
  return added;
}

function safeCreatePath() {
  const requested = window.prompt('New file name or path', 'src/new-file.js');
  if (!requested) return;
  let path;
  try { path = collisionSafePath(requested); }
  catch (error) { setWorkflowStatus(error.message, 'failed'); return; }
  checkpoint(`creation of ${path}`);
  let mediaType = mediaTypeFor(path);
  if (mediaType === 'BINARY_OBJECT') mediaType = 'TEXT';
  state.files.push({ path, name: path.split('/').at(-1), mediaType, content: '', dirty: true });
  state.activePath = path;
  persist();
  renderFiles();
  activateFile(path);
  $('#ide-source-editor')?.focus();
  setWorkflowStatus(`Created ${path}.`, 'ready');
}

function openNewProjectDialog() {
  const dialog = $('#ide-new-project-dialog');
  if (!dialog) return;
  dialog.hidden = false;
  document.body.classList.add('ide-dialog-open');
  $('#ide-new-project-name')?.focus();
}

function closeNewProjectDialog() {
  const dialog = $('#ide-new-project-dialog');
  if (dialog) dialog.hidden = true;
  document.body.classList.remove('ide-dialog-open');
}

function selectTemplate(kind) {
  selectedTemplate = kind;
  document.querySelectorAll('[data-project-template]').forEach((button) => {
    button.classList.toggle('selected', button.dataset.projectTemplate === kind);
    button.setAttribute('aria-pressed', button.dataset.projectTemplate === kind ? 'true' : 'false');
  });
}

function createSelectedProject() {
  const name = ($('#ide-new-project-name')?.value || 'My HHS Project').trim();
  checkpoint(`creation of ${name}`);
  const projectName = $('#ide-project-name');
  const starter = $('#ide-project-starter');
  if (projectName) projectName.value = name;
  if (starter) starter.value = selectedTemplate;
  $('#ide-add-starter')?.click();
  closeNewProjectDialog();
  setWorkflowStatus(`${name} is ready. Edit a file or press Build & Preview.`, 'ready');
  if (selectedTemplate === 'web') {
    openBottomTab('preview');
    window.HHSIntegratedWorkbench?.preview?.();
  }
}

async function buildAndPreview() {
  setWorkflowStatus('Building every project file…');
  try {
    await window.HHSProjectLifecycle?.build?.();
    openBottomTab('preview');
    window.HHSIntegratedWorkbench?.preview?.();
    setWorkflowStatus('Build complete. Application preview is running.', 'ready');
  } catch (error) {
    setWorkflowStatus(`Build needs attention: ${error.message}`, 'failed');
    log(`Build & Preview failed: ${error.message}`);
  }
}

async function testProject() {
  setWorkflowStatus('Testing the active application path…');
  try {
    await window.HHSVisualIDE?.lifecycle?.();
    openBottomTab('terminal');
    setWorkflowStatus('Test lifecycle completed. Results are in Output.', 'ready');
  } catch (error) {
    setWorkflowStatus(`Test needs attention: ${error.message}`, 'failed');
  }
}

async function exportProject() {
  setWorkflowStatus('Preparing a portable ZIP…');
  try {
    await window.HHSProjectLifecycle?.exportZip?.();
    setWorkflowStatus('ZIP exported with source, builds, evidence, and receipts.', 'ready');
  } catch (error) {
    setWorkflowStatus(`Export needs attention: ${error.message}`, 'failed');
  }
}

function mountSimpleWorkflowBar() {
  const view = $('#ide-view');
  const tabs = view?.querySelector('.ide-tab-strip');
  if (!view || !tabs || $('#ide-simple-workflow')) return;
  const bar = document.createElement('section');
  bar.id = 'ide-simple-workflow';
  bar.className = 'ide-simple-workflow';
  bar.setAttribute('aria-label', 'Simple application development workflow');
  bar.innerHTML = `
    <div class="ide-simple-primary-actions">
      <button id="ide-new-app" type="button"><span>＋</span><strong>New App</strong><small>Choose a ready project</small></button>
      <button id="ide-add-files-simple" type="button"><span>⇧</span><strong>Add Files</strong><small>Text, code, media, PDF</small></button>
      <button id="ide-add-folder-simple" type="button"><span>▣</span><strong>Add Folder</strong><small>Keep its structure</small></button>
      <button id="ide-build-preview-simple" type="button" class="primary-action"><span>▶</span><strong>Build & Preview</strong><small>Compile and run the app</small></button>
      <button id="ide-test-simple" type="button"><span>✓</span><strong>Test</strong><small>Run the active lifecycle</small></button>
      <button id="ide-export-simple" type="button"><span>↓</span><strong>Export</strong><small>Download project ZIP</small></button>
    </div>
    <div class="ide-simple-status-row">
      <span id="ide-simple-workflow-state" data-state="ready">Ready. Start with New App or drop files anywhere in the workspace.</span>
      <button id="ide-undo-safe-change" type="button" disabled>Undo</button>
      <button id="ide-open-assistant-simple" type="button">Ask Assistant</button>
      <details><summary>Advanced HHS controls</summary><p>The exact ingress, Hash216, VM81, compiler, replay, and receipt controls remain available in the Lifecycle and Output panes.</p></details>
    </div>`;
  view.insertBefore(bar, tabs);
  $('#ide-new-app').onclick = openNewProjectDialog;
  $('#ide-add-files-simple').onclick = () => $('#ide-file-input')?.click();
  $('#ide-add-folder-simple').onclick = () => $('#ide-folder-input')?.click();
  $('#ide-build-preview-simple').onclick = () => void buildAndPreview();
  $('#ide-test-simple').onclick = () => void testProject();
  $('#ide-export-simple').onclick = () => void exportProject();
  $('#ide-undo-safe-change').onclick = undoSafeChange;
  $('#ide-open-assistant-simple').onclick = () => window.HHSIntegratedAssistant?.open?.();
}

function mountNewProjectDialog() {
  if ($('#ide-new-project-dialog')) return;
  const dialog = document.createElement('section');
  dialog.id = 'ide-new-project-dialog';
  dialog.className = 'ide-new-project-dialog';
  dialog.hidden = true;
  dialog.setAttribute('role', 'dialog');
  dialog.setAttribute('aria-modal', 'true');
  dialog.setAttribute('aria-labelledby', 'ide-new-project-title');
  dialog.innerHTML = `
    <div class="ide-dialog-card">
      <header><div><span>NEW PROJECT</span><h2 id="ide-new-project-title">What are you building?</h2></div><button id="ide-close-project-dialog" type="button" aria-label="Close">×</button></header>
      <label class="ide-project-name-label">Project name<input id="ide-new-project-name" value="My HHS Project" maxlength="120"></label>
      <div class="ide-template-grid">
        <button type="button" data-project-template="web" class="selected" aria-pressed="true"><strong>Web Application</strong><span>HTML, CSS, JavaScript, live preview</span></button>
        <button type="button" data-project-template="content" aria-pressed="false"><strong>Content Project</strong><span>Markdown, metadata, images, audio and video</span></button>
        <button type="button" data-project-template="automation" aria-pressed="false"><strong>HHS Automation</strong><span>HARMONICODE source with a Python adapter</span></button>
      </div>
      <footer><button id="ide-cancel-project" type="button">Cancel</button><button id="ide-create-project" type="button" class="primary-action">Create Project</button></footer>
    </div>`;
  document.body.append(dialog);
  $('#ide-close-project-dialog').onclick = closeNewProjectDialog;
  $('#ide-cancel-project').onclick = closeNewProjectDialog;
  $('#ide-create-project').onclick = createSelectedProject;
  dialog.addEventListener('click', (event) => { if (event.target === dialog) closeNewProjectDialog(); });
  document.querySelectorAll('[data-project-template]').forEach((button) => {
    button.onclick = () => selectTemplate(button.dataset.projectTemplate);
  });
}

function mountDropSafety() {
  const view = $('#ide-view');
  if (!view || $('#ide-global-drop-overlay')) return;
  const overlay = document.createElement('div');
  overlay.id = 'ide-global-drop-overlay';
  overlay.className = 'ide-global-drop-overlay';
  overlay.innerHTML = '<strong>Drop files to add them safely</strong><span>Existing project files will never be replaced.</span>';
  view.append(overlay);

  const containsFiles = (event) => [...(event.dataTransfer?.types || [])].includes('Files');
  view.addEventListener('dragenter', (event) => {
    if (!containsFiles(event)) return;
    event.preventDefault();
    dragDepth += 1;
    view.classList.add('ide-global-drag-active');
  });
  view.addEventListener('dragover', (event) => { if (containsFiles(event)) event.preventDefault(); });
  view.addEventListener('dragleave', (event) => {
    if (!containsFiles(event)) return;
    dragDepth = Math.max(0, dragDepth - 1);
    if (!dragDepth) view.classList.remove('ide-global-drag-active');
  });
  view.addEventListener('drop', (event) => {
    if (!event.dataTransfer?.files?.length) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    dragDepth = 0;
    view.classList.remove('ide-global-drag-active');
    void safeImportFiles(event.dataTransfer.files);
  }, true);
}

function interceptNativeInputs() {
  const fileInput = $('#ide-file-input');
  const folderInput = $('#ide-folder-input');
  fileInput?.addEventListener('change', (event) => {
    if (!event.target.files?.length) return;
    event.stopImmediatePropagation();
    void safeImportFiles(event.target.files).finally(() => { event.target.value = ''; });
  }, true);
  folderInput?.addEventListener('change', (event) => {
    if (!event.target.files?.length) return;
    event.stopImmediatePropagation();
    void safeImportFiles(event.target.files, { preserveFolders: true }).finally(() => { event.target.value = ''; });
  }, true);
  const createPath = $('#ide-create-path');
  if (createPath) createPath.onclick = safeCreatePath;
}

function disableAccidentalInternalDragging() {
  const tree = $('#ide-file-tree');
  if (!tree) return;
  const apply = () => tree.querySelectorAll('.ide-file-item').forEach((item) => {
    item.draggable = false;
    item.setAttribute('aria-description', 'Click to open. Files are moved only through explicit commands.');
  });
  apply();
  new MutationObserver(apply).observe(tree, { childList: true, subtree: true });
}

function bindShortcuts() {
  document.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'z' && !event.shiftKey) {
      const target = event.target;
      if (target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement) return;
      event.preventDefault();
      undoSafeChange();
    }
    if (event.key === 'Escape' && !$('#ide-new-project-dialog')?.hidden) closeNewProjectDialog();
  });
}

export function initIntuitiveIDE() {
  mountSimpleWorkflowBar();
  mountNewProjectDialog();
  mountDropSafety();
  interceptNativeInputs();
  disableAccidentalInternalDragging();
  bindShortcuts();
  updateUndoState();
  window.HHSIntuitiveIDE = Object.freeze({
    newProject: openNewProjectDialog,
    importFiles: safeImportFiles,
    buildAndPreview,
    test: testProject,
    exportZip: exportProject,
    undo: undoSafeChange,
    collisionSafePath,
    existing_files_are_never_silently_replaced: true,
    system_knowledge_required: false,
  });
  log('Intuitive IDE workflow ready: New App → Add Files → Build & Preview → Test → Export.');
}
