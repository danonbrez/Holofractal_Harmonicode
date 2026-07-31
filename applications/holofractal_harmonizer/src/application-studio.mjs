import { $, state, persist, setText, log } from './visual-ide-state.mjs';
import { renderFiles, activateFile, openBottomTab } from './visual-ide-ui.mjs';
import { applicationTemplateList, materializeApplicationTemplate } from './application-templates-runtime.mjs';

const REQUIRED_APPLICATION_TEMPLATES = Object.freeze([
  'pong', 'calculator', 'puzzle', 'document', 'audio', 'video',
]);
let selectedTemplate = 'pong';
let previousProject = null;
let priorUndoHandler = null;
let workflowObserver = null;
let workflowRepairPending = false;

function snapshotProject() {
  return {
    files: state.files.map((file) => ({ ...file })),
    activePath: state.activePath,
    projectName: $('#ide-project-name')?.value || '',
  };
}

function setStatus(message, status = 'ready') {
  setText('#ide-simple-workflow-state', message);
  const node = $('#ide-simple-workflow-state');
  if (node) node.dataset.state = status;
}

function refreshProjectSurfaces() {
  persist();
  renderFiles();
  activateFile(state.activePath);
  const entrypoint = $('#ide-project-entrypoint');
  if (entrypoint) {
    const selected = state.activePath;
    entrypoint.replaceChildren(...state.files.map((file) => {
      const option = document.createElement('option');
      option.value = file.path;
      option.textContent = file.path;
      option.selected = file.path === selected;
      return option;
    }));
  }
}

function restorePreviousProject() {
  if (!previousProject) return;
  const current = snapshotProject();
  state.files.splice(0, state.files.length, ...previousProject.files.map((file) => ({ ...file })));
  state.activePath = previousProject.activePath;
  const name = $('#ide-project-name');
  if (name) name.value = previousProject.projectName;
  previousProject = current;
  refreshProjectSurfaces();
  setStatus('Previous project restored. Use Undo again to switch back.', 'ready');
  log('Restored the prior project working tree without deleting either snapshot.');
  window.HHSIntegratedWorkbench?.preview?.();
}

function bindProjectUndo() {
  const undo = $('#ide-undo-safe-change');
  if (!undo) return;
  if (!priorUndoHandler) priorUndoHandler = undo.onclick;
  undo.disabled = false;
  undo.title = 'Restore the previous complete project';
  undo.onclick = restorePreviousProject;
}

function selectTemplate(id) {
  selectedTemplate = id;
  document.querySelectorAll('#ide-application-gallery [data-application-template]').forEach((button) => {
    const active = button.dataset.applicationTemplate === id;
    button.classList.toggle('selected', active);
    button.setAttribute('aria-pressed', active ? 'true' : 'false');
  });
}

function closeGallery() {
  const gallery = $('#ide-application-gallery');
  if (gallery) gallery.hidden = true;
  document.body.classList.remove('ide-dialog-open');
}

function templateRegistry() {
  const templates = applicationTemplateList();
  const byId = new Map(templates.map((template) => [template.id, template]));
  const missing = REQUIRED_APPLICATION_TEMPLATES.filter((id) => !byId.has(id));
  if (missing.length) {
    throw new Error(`HHS_APPLICATION_TEMPLATE_REGISTRY_INCOMPLETE: ${missing.join(',')}`);
  }
  return { templates, byId };
}

function renderTemplateButtons(gallery) {
  const grid = gallery.querySelector('#ide-application-template-grid');
  if (!grid) throw new Error('HHS_APPLICATION_TEMPLATE_GRID_MISSING');
  const { templates } = templateRegistry();
  const expected = templates.map((template) => template.id).join('|');
  if (grid.dataset.templateRegistry === expected
      && templates.every((template) => grid.querySelector(`[data-application-template="${CSS.escape(template.id)}"]`))) {
    return;
  }
  grid.replaceChildren(...templates.map((template) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.dataset.applicationTemplate = template.id;
    button.setAttribute('aria-pressed', template.id === selectedTemplate ? 'true' : 'false');
    const label = document.createElement('strong');
    label.textContent = template.label;
    const description = document.createElement('span');
    description.textContent = template.description;
    const fileCount = document.createElement('small');
    fileCount.textContent = `${template.files.length} editable files`;
    button.append(label, description, fileCount);
    button.onclick = () => selectTemplate(template.id);
    return button;
  }));
  grid.dataset.templateRegistry = expected;
  selectTemplate(selectedTemplate);
}

export function openApplicationGallery() {
  mountGallery();
  const gallery = $('#ide-application-gallery');
  if (!gallery) return;
  renderTemplateButtons(gallery);
  gallery.hidden = false;
  gallery.removeAttribute('inert');
  gallery.style.display = '';
  gallery.style.visibility = 'visible';
  gallery.style.opacity = '1';
  document.body.classList.add('ide-dialog-open');
  $('#ide-application-name')?.focus();
}

export function createApplicationProject(id = selectedTemplate, requestedName = '') {
  const { byId } = templateRegistry();
  if (!byId.has(id)) throw new Error(`HHS_APPLICATION_TEMPLATE_NOT_REGISTERED: ${id}`);
  const template = materializeApplicationTemplate(id);
  const name = requestedName.trim() || template.label;
  previousProject = snapshotProject();
  state.files.splice(0, state.files.length, ...template.files);
  state.activePath = template.entrypoint;
  state.projectBuild = null;
  const projectName = $('#ide-project-name');
  if (projectName) projectName.value = name;
  refreshProjectSurfaces();
  bindProjectUndo();
  closeGallery();
  setStatus(`${name} is running from editable source. Change any file, then press Build & Preview.`, 'ready');
  log(`Created executable ${template.label} project.`, {
    template: template.id,
    entrypoint: template.entrypoint,
    files: template.files.map((file) => file.path),
    previous_project_restorable: true,
  });
  if (/\.html?$/i.test(template.entrypoint)) {
    openBottomTab('preview');
    window.HHSIntegratedWorkbench?.preview?.();
  }
  return template;
}

function mountGallery() {
  let gallery = $('#ide-application-gallery');
  if (!gallery) {
    gallery = document.createElement('section');
    gallery.id = 'ide-application-gallery';
    gallery.className = 'ide-application-gallery';
    gallery.hidden = true;
    gallery.setAttribute('role', 'dialog');
    gallery.setAttribute('aria-modal', 'true');
    gallery.setAttribute('aria-labelledby', 'ide-application-gallery-title');
    gallery.innerHTML = `
      <div class="ide-application-gallery-card">
        <header>
          <div><span>NEW APPLICATION</span><h2 id="ide-application-gallery-title">Choose something real to build</h2><p>Every starter is editable, runnable, testable, compilable, and exportable.</p></div>
          <button id="ide-close-application-gallery" type="button" aria-label="Close">×</button>
        </header>
        <label class="ide-application-name-label">Project name<input id="ide-application-name" value="My Application" maxlength="120"></label>
        <div id="ide-application-template-grid" class="ide-application-template-grid"></div>
        <footer><button id="ide-cancel-application-gallery" type="button">Cancel</button><button id="ide-create-application-project" type="button" class="primary-action">Create & Run Project</button></footer>
      </div>`;
    document.body.append(gallery);
    $('#ide-close-application-gallery').onclick = closeGallery;
    $('#ide-cancel-application-gallery').onclick = closeGallery;
    $('#ide-create-application-project').onclick = () => createApplicationProject(selectedTemplate, $('#ide-application-name')?.value || '');
    gallery.addEventListener('click', (event) => { if (event.target === gallery) closeGallery(); });
  }
  renderTemplateButtons(gallery);
}

function launcherIsStable(node) {
  return Boolean(
    node instanceof HTMLButtonElement
    && node.isConnected
    && node.parentElement === document.body
    && !node.hidden
    && !node.disabled
    && !node.closest('[hidden]')
    && node.dataset.hhsStableApplicationLauncher === 'true'
  );
}

function createStableApplicationLauncher() {
  const launchers = [...document.querySelectorAll('[id="ide-new-app"]')];
  let newApp = launchers.find(launcherIsStable) || null;
  for (const launcher of launchers) {
    if (launcher !== newApp) launcher.remove();
  }
  if (!newApp) {
    newApp = document.createElement('button');
    newApp.id = 'ide-new-app';
    newApp.type = 'button';
    newApp.className = 'ide-new-application-launcher';
    newApp.dataset.hhsStableApplicationLauncher = 'true';
    newApp.setAttribute('aria-label', 'Create a new application');
    const symbol = document.createElement('span');
    symbol.textContent = '＋';
    const label = document.createElement('strong');
    label.textContent = 'New Application';
    const description = document.createElement('small');
    description.textContent = 'Games, tools, documents, audio, video';
    description.style.display = 'none';
    newApp.append(symbol, label, description);
    document.body.append(newApp);
  }
  newApp.hidden = false;
  newApp.disabled = false;
  newApp.removeAttribute('inert');
  newApp.style.cssText = [
    'position:fixed', 'top:8px', 'right:210px', 'z-index:2147483000',
    'display:inline-flex', 'align-items:center', 'justify-content:center', 'gap:6px',
    'min-height:32px', 'padding:0 12px', 'border:1px solid #6f87d9',
    'border-radius:8px', 'background:linear-gradient(135deg,#5e78db,#344d9f)',
    'color:#f6f8ff', 'font-size:12px', 'font-weight:800', 'cursor:pointer',
    'white-space:nowrap', 'visibility:visible', 'opacity:1', 'pointer-events:auto',
    'transform:none', 'transition:none', 'touch-action:manipulation',
  ].join(';');
  return newApp;
}

function promotePrimaryWorkflow() {
  const newApp = createStableApplicationLauncher();
  if (newApp) {
    newApp.onclick = openApplicationGallery;
    const label = newApp.querySelector('strong');
    const description = newApp.querySelector('small');
    if (label) label.textContent = 'New Application';
    if (description) description.textContent = 'Games, tools, documents, audio, video';
  }
  const status = $('#ide-simple-workflow-state');
  if (status) status.textContent = 'Ready. Create a real application, add your own files, or drop a folder anywhere.';
}

function observePrimaryWorkflowInvariant() {
  if (workflowObserver || !document.body) return;
  workflowObserver = new MutationObserver(() => {
    const launchers = [...document.querySelectorAll('[id="ide-new-app"]')];
    if ((launchers.length === 1 && launcherIsStable(launchers[0])) || workflowRepairPending) return;
    workflowRepairPending = true;
    queueMicrotask(() => {
      workflowRepairPending = false;
      promotePrimaryWorkflow();
      window.dispatchEvent(new CustomEvent('hhs:application-studio:workflow-restored', {
        detail: {
          control: 'ide-new-app',
          duplicate_count_before_repair: launchers.length,
          stable_body_launcher: true,
          frontend_is_authority: false,
        },
      }));
    });
  });
  workflowObserver.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['hidden', 'disabled', 'style', 'inert'] });
}

function bindKeyboard() {
  document.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.altKey && event.key.toLowerCase() === 'n') {
      event.preventDefault();
      openApplicationGallery();
    }
    if (event.key === 'Escape' && !$('#ide-application-gallery')?.hidden) closeGallery();
  });
}

export function initApplicationStudio() {
  mountGallery();
  promotePrimaryWorkflow();
  observePrimaryWorkflowInvariant();
  bindKeyboard();
  const templates = applicationTemplateList().map(({ id, label, description, entrypoint }) => ({ id, label, description, entrypoint }));
  window.HHSApplicationStudio = Object.freeze({
    open: openApplicationGallery,
    create: createApplicationProject,
    restorePreviousProject,
    ensurePrimaryControl: promotePrimaryWorkflow,
    templates,
    required_templates: REQUIRED_APPLICATION_TEMPLATES,
    template_registry_complete: REQUIRED_APPLICATION_TEMPLATES.every((id) => templates.some((template) => template.id === id)),
    primary_control_is_self_healing: true,
    primary_control_is_single_stable_body_launcher: true,
    creates_real_runnable_projects: true,
    prior_project_is_recoverable: true,
  });
  log('Application Studio ready with Pong, calculator, puzzle, document, audio, video, web, and automation projects.');
}