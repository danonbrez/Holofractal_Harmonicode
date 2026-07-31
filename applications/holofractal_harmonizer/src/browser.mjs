import {
  HarmonizerRuntime,
  OBJECT_TYPES,
  selectPerformanceProfile,
} from './core.mjs';

const runtime = new HarmonizerRuntime();
const $ = (selector) => document.querySelector(selector);
const ASSISTANT_THREAD_KEY = 'hhs:assistant:active-thread';
const assistantState = {
  threadId: null,
  sending: false,
  status: null,
};

const objects = [
  {
    object_id: 'hhs:application:harmonizer',
    object_type: 'APPLICATION',
    canonical_name: 'HOLOFRACTAL_HARMONIZER',
    display_name: 'Holofractal Harmonizer',
    description: 'Unified metadata-rich control environment for registered HHS services and multimodal objects.',
    modality_classes: ['TEXT', 'IMAGE', 'AUDIO', 'VIDEO', '3D', 'CODE', 'RECEIPT'],
    lifecycle_state: 'ACTIVE',
    authority_state: 'VALIDATED_PROJECTION',
    validation_state: 'VERIFIED',
    capabilities: ['OBJECT_REGISTRY', 'NESTED_PANELS', 'API_CONTROLLER', 'SPATIAL_PROJECTION'],
    actions: [{ action_id: 'open', label: 'Open Workspace' }],
  },
  {
    object_id: 'hhs:agent:visual-development-assistant',
    object_type: 'AGENT',
    canonical_name: 'HHS_VISUAL_DEVELOPMENT_ASSISTANT',
    display_name: 'HHS Development Assistant',
    description: 'Repository-native LiteRT-LM natural-language thread bound to governed HHS API tools.',
    modality_classes: ['TEXT', 'CODE', 'RECEIPT'],
    lifecycle_state: 'ACTIVE',
    authority_state: 'ADVISORY',
    validation_state: 'PROVIDER_PENDING',
    capabilities: ['NATURAL_LANGUAGE', 'HHS_API_TOOLS', 'THREAD_MEMORY'],
    actions: [{ action_id: 'message', label: 'Send Message' }],
    dependencies: ['hhs:model:litert-lm:gemma4', 'hhs:api:assistant'],
  },
  {
    object_id: 'hhs:model:litert-lm:gemma4',
    object_type: 'MODEL',
    canonical_name: 'HHS_LITERT_LM_GEMMA4',
    display_name: 'LiteRT-LM Gemma 4',
    description: 'Local repository-native language model provider used through the HHS assistant service.',
    modality_classes: ['TEXT', 'CODE'],
    lifecycle_state: 'READY',
    authority_state: 'ADVISORY',
    validation_state: 'RUNTIME_HEALTH_REQUIRED',
    capabilities: ['CHAT_COMPLETION', 'TOOL_CALLS', 'BOUNDED_REASONING'],
    actions: [{ action_id: 'health', label: 'Check Provider Health' }],
  },
  {
    object_id: 'hhs:runtime:vm81',
    object_type: 'RUNTIME',
    canonical_name: 'HHS_VM81_RUNTIME',
    display_name: 'VM81 Runtime',
    description: 'Validated projection of the canonical backend execution authority for admitted state transitions.',
    modality_classes: ['RUNTIME_STATE', 'RECEIPT'],
    lifecycle_state: 'READY',
    authority_state: 'VALIDATED_PROJECTION',
    validation_state: 'VERIFIED',
    capabilities: ['EXECUTE', 'REPLAY', 'RECEIPT_COMMIT'],
    actions: [{ action_id: 'status', label: 'Runtime Status' }],
  },
  {
    object_id: 'hhs:service:hash72',
    object_type: 'SERVICE',
    canonical_name: 'HHS_HASH72_RECEIPT_SERVICE',
    display_name: 'Hash72 Receipt Service',
    description: 'Validated projection of the append-only receipt identity and verification surface.',
    modality_classes: ['RECEIPT', 'LEDGER'],
    lifecycle_state: 'READY',
    authority_state: 'VALIDATED_PROJECTION',
    validation_state: 'VERIFIED',
    capabilities: ['RECEIPT_READ', 'RECEIPT_VERIFY'],
    actions: [{ action_id: 'tip', label: 'Read Tip' }],
  },
  {
    object_id: 'hhs:api:assistant',
    object_type: 'API',
    canonical_name: 'HHS_ASSISTANT_API',
    display_name: 'Assistant API',
    description: 'Governed conversation, health, tools, thread, and WebSocket routes.',
    modality_classes: ['JSON', 'TEXT', 'WEBSOCKET'],
    lifecycle_state: 'READY',
    authority_state: 'VALIDATED_PROJECTION',
    validation_state: 'VERIFIED',
    capabilities: ['THREAD_CREATE', 'MESSAGE_SEND', 'TOOLS_READ'],
    actions: [{ action_id: 'status', method: 'GET', endpoint: '/api/assistant/status' }],
  },
  {
    object_id: 'hhs:api:object-search',
    object_type: 'API',
    canonical_name: 'HHS_OBJECT_SEARCH_API',
    display_name: 'Registered Object Search',
    description: 'Read-only search across registered object metadata.',
    modality_classes: ['JSON'],
    lifecycle_state: 'ACTIVE',
    authority_state: 'VALIDATED_PROJECTION',
    validation_state: 'VERIFIED',
    capabilities: ['OBJECT_SEARCH'],
    actions: [{ action_id: 'search', method: 'POST', endpoint: '/api/objects/search' }],
  },
];

async function initializeBrowserRegistry() {
  for (const object of objects) {
    await runtime.registry.register(object, 'system:pass161-browser');
  }
  await runtime.registry.relate('hhs:application:harmonizer', 'hhs:agent:visual-development-assistant', 'HOSTS', 'system:pass161-browser');
  await runtime.registry.relate('hhs:application:harmonizer', 'hhs:runtime:vm81', 'PROJECTS', 'system:pass161-browser');
  await runtime.registry.relate('hhs:application:harmonizer', 'hhs:service:hash72', 'PROJECTS', 'system:pass161-browser');
  await runtime.registry.relate('hhs:agent:visual-development-assistant', 'hhs:model:litert-lm:gemma4', 'USES_PROVIDER', 'system:pass161-browser');
  await runtime.registry.relate('hhs:agent:visual-development-assistant', 'hhs:api:assistant', 'USES_API', 'system:pass161-browser');

  runtime.authority.grant('human:owner', [
    'registry.read',
    'api.invoke',
    'application.launch',
    'analysis.exact',
  ]);

  runtime.apis.register(
    'hhs:api:object-search',
    {
      endpoint: '/registry/search',
      operation: 'OBJECT_SEARCH',
      authority_requirements: ['api.invoke'],
    },
    async ({ query = '' } = {}) => {
      const matches = runtime.registry.search(query);
      return {
        schema: 'HHS_REGISTERED_OBJECT_SEARCH_RESPONSE_V1',
        count: matches.length,
        objects: matches,
        mutation_authority: false,
        authoritative_completion_evidence: true,
      };
    },
  );

  await runtime.faces.register({
    face_id: 'p161:face:browser-default',
    object_type_binding: '*',
    projection_class: 'CARD',
    field_layout: [],
    responsive_rules: { mobile: 'STACK', desktop: 'PANEL' },
    accessibility_profile: { keyboard: true, screen_reader: true },
  });

}

function objectGlyph(object) {
  const glyphs = {
    APPLICATION: 'APP', AGENT: 'AI', MODEL: 'LM', RUNTIME: '81', SERVICE: 'SVC', API: 'API',
    DATA: 'DAT', PIPELINE: 'PIP', VISUALIZER: 'VIS', DOCUMENT: 'DOC', RECEIPT: '72',
  };
  return glyphs[object.object_type] || object.object_type.slice(0, 3);
}

function receiptTipFor(object) {
  return object.receipt_tip
    || object.receipts?.at(-1)
    || runtime.ledger.tip
    || '0'.repeat(64);
}

function renderObjects(list = runtime.registry.list()) {
  const tree = $('#registry-tree');
  tree.replaceChildren();
  const groups = new Map();
  for (const object of list) {
    const group = groups.get(object.object_type) || [];
    group.push(object);
    groups.set(object.object_type, group);
  }
  for (const type of OBJECT_TYPES) {
    const group = groups.get(type);
    if (!group?.length) continue;
    const section = document.createElement('section');
    section.className = 'registry-group';
    section.innerHTML = `<div class="registry-group-title"><span>${type}</span><span>${group.length}</span></div>`;
    for (const object of group) {
      const button = document.createElement('button');
      button.className = 'registry-object';
      button.dataset.objectId = object.object_id;
      button.innerHTML = `<span class="object-glyph">${objectGlyph(object)}</span><span><strong>${object.display_name}</strong><small>${object.lifecycle_state} · ${object.authority_state}</small></span>`;
      button.addEventListener('click', () => selectObject(object.object_id));
      section.append(button);
    }
    tree.append(section);
  }
  $('#object-count').textContent = `${list.length} objects`;

  const grid = $('#object-grid');
  grid.replaceChildren();
  for (const object of list) {
    const card = document.createElement('button');
    card.className = 'object-card';
    card.dataset.objectId = object.object_id;
    card.innerHTML = `<span class="object-glyph large">${objectGlyph(object)}</span><span class="object-type">${object.object_type}</span><strong>${object.display_name}</strong><small>${object.description}</small><span class="state-line">${object.lifecycle_state} · ${object.validation_state}</span>`;
    card.addEventListener('click', () => selectObject(object.object_id));
    grid.append(card);
  }
}

function renderInspector(result) {
  const object = result.object;
  const receiptTip = receiptTipFor(object);
  const content = $('#inspector-content');
  content.innerHTML = `
    <section class="object-identity">
      <span class="object-glyph large">${objectGlyph(object)}</span>
      <div><span class="object-type">${object.object_type}</span><h2>${object.display_name}</h2><code>${object.object_id}</code></div>
    </section>
    <p>${object.description}</p>
    <dl class="metadata-grid">
      <div><dt>Lifecycle</dt><dd>${object.lifecycle_state}</dd></div>
      <div><dt>Authority</dt><dd>${object.authority_state}</dd></div>
      <div><dt>Validation</dt><dd>${object.validation_state}</dd></div>
      <div><dt>Receipt tip</dt><dd>${receiptTip.slice(0, 16)}</dd></div>
    </dl>
    <details open><summary>Capabilities</summary><div class="chip-list">${object.capabilities.map((item) => `<span>${item}</span>`).join('')}</div></details>
    <details><summary>Actions</summary><pre>${JSON.stringify(object.actions, null, 2)}</pre></details>
    <details><summary>Dependencies</summary><pre>${JSON.stringify(object.dependencies, null, 2)}</pre></details>
    <details><summary>Canonical metadata</summary><pre>${JSON.stringify(object.metadata, null, 2)}</pre></details>
  `;
  $('#lineage').textContent = result.lineage.map((item) => item.display_name).join('  ›  ');
  $('#selected-object').textContent = `${object.object_type} · ${object.object_id}`;
  $('#receipt-tip').textContent = receiptTip.slice(0, 16);
  document.querySelectorAll('[data-object-id]').forEach((element) => {
    element.classList.toggle('selected', element.dataset.objectId === object.object_id);
  });
}

async function selectObject(objectId) {
  runtime.panels.reset();
  await runtime.panels.open(objectId, { allow_repeat: true, stateful: false });
  const result = {
    object: runtime.registry.lookup(objectId),
    lineage: runtime.panels.path().map((entry) => runtime.registry.lookup(entry.object_id)),
  };
  renderInspector(result);
  $('#inspector').classList.add('open');
  return result;
}

function showView(name) {
  $('#assistant-view').hidden = name !== 'assistant';
  $('#workspace-view').hidden = name !== 'workspace';
  $('#spatial-view').hidden = name !== 'spatial';
  $('#api-view').hidden = name !== 'api';
  $('#assistant-home').classList.toggle('active', name === 'assistant');
  $('#object-workspace').classList.toggle('active', name === 'workspace');
  $('#registry-nav').classList.remove('open');
}

function appendMessage(role, content, metadata = {}) {
  const article = document.createElement('article');
  article.className = `message ${role}-message`;
  article.innerHTML = `<div class="message-role">${role === 'assistant' ? 'HHS ASSISTANT' : 'YOU'}</div><div class="message-content"></div>`;
  article.querySelector('.message-content').textContent = content;
  if (Object.keys(metadata).length) {
    const meta = document.createElement('small');
    meta.className = 'message-metadata';
    meta.textContent = Object.entries(metadata).map(([key, value]) => `${key}: ${value}`).join(' · ');
    article.append(meta);
  }
  $('#conversation').append(article);
  article.scrollIntoView({ block: 'end', behavior: 'smooth' });
  return article;
}

async function requestJson(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
  });
  const payload = await response.json().catch(() => ({ error: `Non-JSON response from ${path}` }));
  if (!response.ok) {
    const detail = payload.detail?.reason || payload.detail || payload.error || `HTTP ${response.status}`;
    const error = new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
    error.status = response.status;
    error.payload = payload;
    throw error;
  }
  return payload;
}

function setProviderStatus(ok, label) {
  const status = $('#provider-status');
  status.textContent = label;
  status.className = `status ${ok ? 'verified' : 'degraded'}`;
}

function updateThreadIdentity(thread) {
  assistantState.threadId = thread.thread_id;
  localStorage.setItem(ASSISTANT_THREAD_KEY, thread.thread_id);
  $('#active-thread').textContent = thread.thread_id.slice(0, 16);
  $('#thread-label').textContent = thread.title || 'HHS Assistant';
  $('#message-count').textContent = `${thread.message_count ?? thread.messages?.length ?? 0} messages`;
}

function renderThread(thread) {
  $('#conversation').replaceChildren();
  const messages = thread.messages || [];
  if (!messages.length) {
    appendMessage('assistant', 'The repository-native LiteRT-LM assistant is ready. Ask about the runtime, registered services, HARMONICODE, conformance, receipts, or the active project.');
    return;
  }
  for (const message of messages) {
    appendMessage(message.role, message.content, {
      hash72: message.message_root_hash72?.slice(0, 16),
    });
  }
}

async function createThread() {
  const payload = await requestJson('/api/assistant/threads', {
    method: 'POST',
    body: JSON.stringify({
      project_id: 'project:visual-development',
      title: 'HHS Visual Development Thread',
      metadata: { surface: 'pass161_harmonizer', provider: 'litert-lm' },
    }),
  });
  updateThreadIdentity(payload.thread);
  renderThread(payload.thread);
  return payload.thread;
}

async function restoreOrCreateThread() {
  const stored = localStorage.getItem(ASSISTANT_THREAD_KEY);
  if (stored) {
    try {
      const payload = await requestJson(`/api/assistant/threads/${encodeURIComponent(stored)}`);
      updateThreadIdentity(payload.thread);
      renderThread(payload.thread);
      return payload.thread;
    } catch (error) {
      if (error.status !== 404) throw error;
      localStorage.removeItem(ASSISTANT_THREAD_KEY);
    }
  }
  return createThread();
}

async function refreshAssistantStatus() {
  try {
    const [status, health, tools] = await Promise.all([
      requestJson('/api/assistant/status'),
      requestJson('/api/assistant/health'),
      requestJson('/api/assistant/tools'),
    ]);
    assistantState.status = health;
    $('#model-id').textContent = health.selected_provider_id
      || status.model_id
      || status.request_model_id
      || 'hhs-native-language-v1';
    $('#backend-id').textContent = `${health.effective_mode || status.execution_backend || 'local'} · ${health.selected_provider_id || status.provider_id || 'HHS provider'}`;
    const toolList = tools.tools || tools.registry || tools.capabilities || [];
    const count = tools.count ?? (Array.isArray(toolList) ? toolList.length : Object.keys(toolList || {}).length);
    $('#tool-count').textContent = String(count);
    setProviderStatus(Boolean(health.online && health.ok), health.online ? 'LITERT-LM ONLINE' : 'ASSISTANT DEGRADED');
  } catch (error) {
    setProviderStatus(false, 'ASSISTANT API OFFLINE');
    $('#backend-id').textContent = 'backend unavailable';
    appendMessage('assistant', `Assistant status could not be loaded: ${error.message}`);
  }
}

async function sendAssistantMessage(content) {
  if (assistantState.sending || !content.trim()) return;
  if (!assistantState.threadId) await createThread();
  assistantState.sending = true;
  $('#conversation').setAttribute('aria-busy', 'true');
  $('#send-prompt').disabled = true;
  appendMessage('user', content.trim());
  const pending = appendMessage('assistant', 'Processing through LiteRT-LM and the governed HHS API tool loop…');

  try {
    const result = await requestJson(`/api/assistant/threads/${encodeURIComponent(assistantState.threadId)}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content: content.trim() }),
    });
    pending.remove();
    const assistantMessage = result.assistant_message;
    if (assistantMessage?.content) {
      appendMessage('assistant', assistantMessage.content, {
        status: result.status,
        tools: result.hhs_api_tool_call_count ?? 0,
        hash72: assistantMessage.message_root_hash72?.slice(0, 16),
      });
    } else {
      appendMessage('assistant', result.error || result.status || 'LiteRT-LM returned no assistant message.', {
        admitted: result.ok,
      });
    }
    const receipt = result.provider_invocation_receipt?.provider_invocation_receipt_hash72
      || result.provider_result_ingress?.provider_result_ingress_root_hash72
      || result.turn_root_hash72;
    if (receipt) $('#receipt-tip').textContent = receipt.slice(0, 16);
    if (result.thread) updateThreadIdentity(result.thread);
  } catch (error) {
    pending.remove();
    appendMessage('assistant', `The assistant request failed without runtime mutation: ${error.message}`);
    setProviderStatus(false, 'ASSISTANT DEGRADED');
  } finally {
    assistantState.sending = false;
    $('#conversation').setAttribute('aria-busy', 'false');
    $('#send-prompt').disabled = false;
    $('#prompt-input').focus();
  }
}

$('#object-search').addEventListener('input', (event) => renderObjects(runtime.registry.search(event.target.value)));
$('#nav-toggle').addEventListener('click', () => $('#registry-nav').classList.toggle('open'));
$('#inspect-toggle').addEventListener('click', () => $('#inspector').classList.toggle('open'));
$('#inspector-back').addEventListener('click', () => {
  runtime.panels.back();
  const lineage = runtime.panels.path();
  const previous = lineage.at(-1);
  if (previous) selectObject(previous.object_id);
});
$('#profile-select').addEventListener('change', (event) => {
  const profile = selectPerformanceProfile(event.target.value);
  $('#harmonizer').dataset.profile = profile.profile;
  $('#latency-state').textContent = `${profile.profile} · ${profile.animation_rate}HZ`;
});
$('#assistant-home').addEventListener('click', () => showView('assistant'));
$('#object-workspace').addEventListener('click', () => showView('workspace'));
$('#return-assistant').addEventListener('click', () => showView('assistant'));
$('#open-3d').addEventListener('click', () => showView('spatial'));
$('#open-api').addEventListener('click', () => showView('api'));
document.querySelectorAll('[data-close-view]').forEach((button) => {
  button.addEventListener('click', () => showView('assistant'));
});
document.querySelectorAll('.spatial-node').forEach((node) => {
  node.addEventListener('click', () => selectObject(node.dataset.objectId));
});

$('#api-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const query = new FormData(event.currentTarget).get('query');
  try {
    $('#api-output').textContent = JSON.stringify(
      await runtime.apis.invoke('hhs:api:object-search', 'human:owner', { query }),
      null,
      2,
    );
  } catch (error) {
    $('#api-output').textContent = JSON.stringify({
      schema: 'HHS_REGISTERED_OBJECT_SEARCH_CLIENT_ERROR_V1',
      ok: false,
      error: error.message,
      mutation_authority: false,
    }, null, 2);
  }
});

$('#prompt-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const input = $('#prompt-input');
  const content = input.value;
  input.value = '';
  await sendAssistantMessage(content);
});

$('#prompt-input').addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    $('#prompt-form').requestSubmit();
  }
});

document.querySelectorAll('[data-prompt]').forEach((button) => {
  button.addEventListener('click', () => {
    $('#prompt-input').value = button.dataset.prompt;
    $('#prompt-input').focus();
  });
});

$('#new-thread').addEventListener('click', async () => {
  localStorage.removeItem(ASSISTANT_THREAD_KEY);
  await createThread();
  $('#prompt-input').focus();
});

async function finishBrowserBootstrap() {
  await initializeBrowserRegistry();
  renderObjects();
  showView('assistant');

  // The terminal-verified object environment is available before optional
  // provider health and conversation restoration finish. It is a projection;
  // canonical execution remains in the backend runtime.
  window.HHSHarmonizer = runtime;
  window.HHSAssistant = Object.freeze({
    get threadId() { return assistantState.threadId; },
    get status() { return assistantState.status; },
    refreshStatus: refreshAssistantStatus,
    newThread: createThread,
    send: sendAssistantMessage,
  });

  try {
    await selectObject('hhs:agent:visual-development-assistant');
  } catch (error) {
    runtime.diagnostics.emit({
      diagnostic_id: 'diag:initial-inspector-selection',
      class: 'APPLICATION',
      severity: 'WARNING',
      object_id: 'hhs:agent:visual-development-assistant',
      message: error.message,
      projection_state: 'VALIDATED_PROJECTION',
    });
  }

  void Promise.allSettled([refreshAssistantStatus(), restoreOrCreateThread()]);
  return runtime;
}

const browserReadyPromise = finishBrowserBootstrap();
window.HHSBrowserReady = browserReadyPromise;
void browserReadyPromise.catch((error) => {
  console.error('HHS Pass 161 browser bootstrap failed', error);
  window.dispatchEvent(new CustomEvent('hhs:browser:bootstrap-error', {
    detail: { classification: 'HHS_P176_BROWSER_BOOTSTRAP_FAILED', message: error?.message || String(error) },
  }));
});
