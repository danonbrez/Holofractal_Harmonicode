import { $, state, persist, setText, log } from './visual-ide-state.mjs';
import { renderFiles, activateFile, openBottomTab } from './visual-ide-ui.mjs';
import { applicationTemplateList, materializeApplicationTemplate } from './application-templates.mjs';

let selectedTemplate = 'pong';
let previousProject = null;
let priorUndoHandler = null;

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
  window.HHSProjectLifecycle?.refreshEntrypoints?.();
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

export function openApplicationGallery() {
  const gallery = $('#ide-application-gallery');
  if (!gallery) return;
  gallery.hidden = false;
  document.body.classList.add('ide-dialog-open');
  $('#ide-application-name')?.focus();
}

export function createApplicationProject(id = selectedTemplate, requestedName = '') {
  const template = materializeApplicationTemplate(id);
  const name = requestedName.trim() || template.label;
  previousProject = snapshotProject();
  state.files.splice(0, state.files.length, ...template.files);
  state.activePath = template.entrypoint;
  state.projectBuild = null;
  const projectName = $('#ide-project-name');
  if (projectName) projectName.value = name;
  const entrypoint = $('#ide-project-entrypoint');
  if (entrypoint) entrypoint.value = template.entrypoint;
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
  if ($('#ide-application-gallery')) return;
  const gallery = document.createElement('section');
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
      <div class="ide-application-template-grid">
        ${applicationTemplateList().map((template) => `<button type="button" data-application-template="${template.id}" aria-pressed="${template.id === selectedTemplate}"><strong>${template.label}</strong><span>${template.description}</span><small>${template.files.length} editable files</small></button>`).join('')}
      </div>
      <footer><button id="ide-cancel-application-gallery" type="button">Cancel</button><button id="ide-create-application-project" type="button" class="primary-action">Create & Run Project</button></footer>
    </div>`;
  document.body.append(gallery);
  $('#ide-close-application-gallery').onclick = closeGallery;
  $('#ide-cancel-application-gallery').onclick = closeGallery;
  $('#ide-create-application-project').onclick = () => createApplicationProject(selectedTemplate, $('#ide-application-name')?.value || '');
  gallery.addEventListener('click', (event) => { if (event.target === gallery) closeGallery(); });
  gallery.querySelectorAll('[data-application-template]').forEach((button) => {
    button.onclick = () => selectTemplate(button.dataset.applicationTemplate);
  });
  selectTemplate(selectedTemplate);
}

function promotePrimaryWorkflow() {
  const newApp = $('#ide-new-app');
  if (newApp) {
    const replacement = newApp.cloneNode(true);
    newApp.replaceWith(replacement);
    replacement.onclick = openApplicationGallery;
    replacement.querySelector('strong').textContent = 'New Application';
    replacement.querySelector('small').textContent = 'Games, tools, documents, audio, video';
  }
  const status = $('#ide-simple-workflow-state');
  if (status) status.textContent = 'Ready. Create a real application, add your own files, or drop a folder anywhere.';
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
  bindKeyboard();
  window.HHSApplicationStudio = Object.freeze({
    open: openApplicationGallery,
    create: createApplicationProject,
    restorePreviousProject,
    templates: applicationTemplateList().map(({ id, label, description, entrypoint }) => ({ id, label, description, entrypoint })),
    creates_real_runnable_projects: true,
    prior_project_is_recoverable: true,
  });
  log('Application Studio ready with Pong, calculator, puzzle, document, audio, video, web, and automation projects.');
}
