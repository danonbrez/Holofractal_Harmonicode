import { WORKFLOW_TEMPLATES, templateById, validateWorkflowTemplates } from './workflow-templates.mjs';

const STORAGE_KEY = 'hhs.visualIde.workflowTemplate.v1';
const ADVANCED_KEY = 'hhs.visualIde.advancedOpen.v1';

const ready = async () => {
  if (document.readyState === 'loading') {
    await new Promise((resolve) => document.addEventListener('DOMContentLoaded', resolve, { once: true }));
  }
  for (let attempt = 0; attempt < 100; attempt += 1) {
    if (document.querySelector('#assistant-view') && document.querySelector('#prompt-input')) return;
    await new Promise((resolve) => setTimeout(resolve, 20));
  }
  throw new Error('HHS visual assistant DOM did not become ready');
};

const el = (tag, options = {}) => {
  const node = document.createElement(tag);
  if (options.className) node.className = options.className;
  if (options.text !== undefined) node.textContent = options.text;
  if (options.html !== undefined) node.innerHTML = options.html;
  if (options.attrs) for (const [name, value] of Object.entries(options.attrs)) node.setAttribute(name, String(value));
  return node;
};

const state = {
  template: templateById(localStorage.getItem(STORAGE_KEY)),
  stage: 0,
};

function setAdvanced(open) {
  document.body.classList.toggle('advanced-open', open);
  localStorage.setItem(ADVANCED_KEY, open ? '1' : '0');
  const toggle = document.querySelector('#workflow-advanced-toggle');
  if (toggle) toggle.setAttribute('aria-pressed', String(open));
  const inspector = document.querySelector('#inspector');
  if (inspector && matchMedia('(max-width:980px)').matches) inspector.classList.toggle('open', open);
}

function stageStatus(index) {
  if (index < state.stage) return 'COMPLETE';
  if (index === state.stage) return 'ACTIVE';
  return 'QUEUED';
}

function renderStages(container) {
  container.replaceChildren(...state.template.stages.map((label, index) => {
    const item = el('div', { className: `workflow-stage ${index < state.stage ? 'complete' : ''} ${index === state.stage ? 'active' : ''}` });
    item.append(el('span', { text: stageStatus(index) }), el('strong', { text: label }));
    return item;
  }));
}

function applyTemplate(template, { focusPrompt = false } = {}) {
  state.template = template;
  state.stage = 0;
  localStorage.setItem(STORAGE_KEY, template.template_id);
  document.querySelectorAll('.workflow-template-button').forEach((button) => {
    button.classList.toggle('active', button.dataset.templateId === template.template_id);
    button.setAttribute('aria-pressed', String(button.dataset.templateId === template.template_id));
  });
  const title = document.querySelector('#workflow-launcher-title');
  const description = document.querySelector('#workflow-launcher-description');
  const start = document.querySelector('#workflow-start');
  if (title) title.textContent = template.outcome;
  if (description) description.textContent = template.description;
  if (start) start.textContent = `Start ${template.label}`;
  const strip = document.querySelector('#workflow-stage-strip');
  if (strip) renderStages(strip);
  const prompt = document.querySelector('#prompt-input');
  if (prompt) prompt.value = template.prompt;
  const quickPrompts = document.querySelector('.quick-prompts');
  if (quickPrompts) {
    quickPrompts.replaceChildren(...[
      `Plan ${template.label}`,
      `Inspect ${template.default_panels[1]}`,
      'Review authority',
    ].map((label, index) => {
      const button = el('button', { text: label, attrs: { type: 'button' } });
      button.addEventListener('click', () => {
        if (!prompt) return;
        prompt.value = index === 0 ? template.prompt : `${label} for the active ${template.label} workflow and identify the next admitted action.`;
        prompt.focus();
      });
      return button;
    }));
  }
  if (focusPrompt && prompt) {
    prompt.focus();
    prompt.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'center' });
  }
}

function startWorkflow() {
  state.stage = 1;
  const strip = document.querySelector('#workflow-stage-strip');
  if (strip) renderStages(strip);
  applyTemplate(state.template, { focusPrompt: true });
  state.stage = 1;
  if (strip) renderStages(strip);
  const validation = document.querySelector('#validation-state');
  if (validation) validation.textContent = `${state.template.category} · PLAN READY`;
}

function buildLauncher() {
  const launcher = el('section', { className: 'workflow-launcher', attrs: { id: 'workflow-launcher', 'aria-label': 'Workflow templates' } });
  const header = el('div', { className: 'workflow-launcher-header' });
  const copy = el('div');
  copy.append(
    el('span', { className: 'eyebrow', text: 'WORKFLOW-FIRST GLOBAL DEFAULT' }),
    el('h2', { attrs: { id: 'workflow-launcher-title' } }),
    el('p', { attrs: { id: 'workflow-launcher-description' } }),
  );
  const actions = el('div', { className: 'workflow-launcher-actions' });
  const start = el('button', { className: 'primary-action', attrs: { id: 'workflow-start', type: 'button' } });
  start.addEventListener('click', startWorkflow);
  const advanced = el('button', { className: 'workflow-advanced-toggle', text: 'Advanced Object Controls', attrs: { id: 'workflow-advanced-toggle', type: 'button', 'aria-pressed': 'false' } });
  advanced.addEventListener('click', () => setAdvanced(!document.body.classList.contains('advanced-open')));
  actions.append(advanced, start);
  header.append(copy, actions);

  const templates = el('div', { className: 'workflow-template-strip' });
  for (const template of WORKFLOW_TEMPLATES) {
    const button = el('button', {
      className: 'workflow-template-button',
      attrs: { type: 'button', 'data-template-id': template.template_id, 'aria-pressed': 'false' },
    });
    const title = el('span', { className: 'workflow-template-title' });
    title.append(el('span', { className: 'workflow-template-glyph', text: template.glyph }), el('span', { text: template.label }));
    button.append(title, el('small', { text: template.outcome }));
    button.addEventListener('click', () => applyTemplate(template));
    templates.append(button);
  }
  const stages = el('div', { className: 'workflow-stage-strip', attrs: { id: 'workflow-stage-strip', 'aria-label': 'Workflow stages' } });
  launcher.append(header, templates, stages);
  return launcher;
}

function buildCommandPalette() {
  const overlay = el('div', { className: 'workflow-command-palette', attrs: { id: 'workflow-command-palette', hidden: '', role: 'dialog', 'aria-modal': 'true', 'aria-label': 'Workflow command palette' } });
  const card = el('div', { className: 'workflow-command-card' });
  const input = el('input', { attrs: { id: 'workflow-command-input', type: 'search', placeholder: 'Search workflows and registered objects…', autocomplete: 'off' } });
  const results = el('div', { className: 'workflow-command-results', attrs: { id: 'workflow-command-results' } });
  card.append(input, results);
  overlay.append(card);
  document.body.append(overlay);

  const render = (query = '') => {
    const normalized = query.trim().toLowerCase();
    const templates = WORKFLOW_TEMPLATES.filter((template) => !normalized || JSON.stringify(template).toLowerCase().includes(normalized));
    const objects = window.HHSHarmonizer?.registry?.search?.(query)?.slice?.(0, 8) ?? [];
    results.replaceChildren(
      ...templates.map((template) => {
        const button = el('button', { className: 'workflow-command-result', attrs: { type: 'button' } });
        const copy = el('span');
        copy.append(el('strong', { text: template.label }), el('small', { text: template.outcome }));
        button.append(el('span', { className: 'workflow-template-glyph', text: template.glyph }), copy, el('small', { text: 'WORKFLOW' }));
        button.addEventListener('click', () => { applyTemplate(template, { focusPrompt: true }); close(); });
        return button;
      }),
      ...objects.map((object) => {
        const button = el('button', { className: 'workflow-command-result', attrs: { type: 'button' } });
        const copy = el('span');
        copy.append(el('strong', { text: object.display_name }), el('small', { text: object.object_id }));
        button.append(el('span', { className: 'workflow-template-glyph', text: object.object_type.slice(0, 2) }), copy, el('small', { text: object.object_type }));
        button.addEventListener('click', () => { document.querySelector(`[data-object-id="${CSS.escape(object.object_id)}"]`)?.click(); close(); });
        return button;
      }),
    );
  };
  const open = () => { overlay.hidden = false; render(''); requestAnimationFrame(() => input.focus()); };
  const close = () => { overlay.hidden = true; };
  input.addEventListener('input', () => render(input.value));
  input.addEventListener('keydown', (event) => { if (event.key === 'Escape') close(); });
  overlay.addEventListener('click', (event) => { if (event.target === overlay) close(); });
  document.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); overlay.hidden ? open() : close(); }
    if (event.key === 'Escape' && !overlay.hidden) close();
  });
  document.querySelector('#object-search')?.addEventListener('focus', open);
  return { open, close, render };
}

function buildMobileTabs() {
  const tabs = el('nav', { className: 'workflow-mobile-tabs', attrs: { 'aria-label': 'Mobile workspace modes' } });
  const definitions = [
    ['Assistant', () => document.querySelector('#assistant-home')?.click()],
    ['Workflows', () => document.querySelector('#workflow-launcher')?.scrollIntoView({ block: 'start' })],
    ['Objects', () => document.querySelector('#nav-toggle')?.click()],
    ['Evidence', () => { setAdvanced(true); document.querySelector('#inspect-toggle')?.click(); }],
  ];
  for (const [label, handler] of definitions) {
    const button = el('button', { text: label, attrs: { type: 'button' } });
    button.addEventListener('click', handler);
    tabs.append(button);
  }
  document.body.append(tabs);
}

function observeAssistantCompletion() {
  const conversation = document.querySelector('#conversation');
  if (!conversation) return;
  const observer = new MutationObserver(() => {
    const assistantMessages = conversation.querySelectorAll('.assistant-message');
    if (assistantMessages.length > 1 && state.stage > 0) {
      state.stage = 5;
      const strip = document.querySelector('#workflow-stage-strip');
      if (strip) renderStages(strip);
      const validation = document.querySelector('#validation-state');
      if (validation) validation.textContent = `${state.template.category} · ASSISTANT TURN ADMITTED`;
    }
  });
  observer.observe(conversation, { childList: true, subtree: true });
}

await ready();
const validation = validateWorkflowTemplates();
if (!validation.ok) throw new Error(`Workflow templates failed validation: ${validation.failures.join(', ')}`);
document.body.classList.add('workflow-default');
document.querySelector('#harmonizer')?.setAttribute('data-ux-default', 'WORKFLOW_FIRST_PROGRESSIVE_DISCLOSURE');
const assistantView = document.querySelector('#assistant-view');
const statusGrid = document.querySelector('.assistant-status-grid');
if (assistantView && statusGrid) assistantView.insertBefore(buildLauncher(), statusGrid);
const systemState = document.querySelector('.system-state');
if (systemState && !document.querySelector('#workflow-advanced-toggle-top')) {
  const topToggle = el('button', { className: 'workflow-advanced-toggle', text: 'Evidence', attrs: { id: 'workflow-advanced-toggle-top', type: 'button', 'aria-label': 'Toggle advanced evidence inspector' } });
  topToggle.addEventListener('click', () => setAdvanced(!document.body.classList.contains('advanced-open')));
  systemState.append(topToggle);
}
const objectSearch = document.querySelector('#object-search');
if (objectSearch) objectSearch.placeholder = 'Search workflows, objects, services, commands…';
buildCommandPalette();
buildMobileTabs();
observeAssistantCompletion();
applyTemplate(state.template);
setAdvanced(localStorage.getItem(ADVANCED_KEY) === '1');
window.HHSWorkflowTemplates = WORKFLOW_TEMPLATES;
window.HHSWorkflowUX = Object.freeze({ validation, applyTemplate, startWorkflow, setAdvanced });
