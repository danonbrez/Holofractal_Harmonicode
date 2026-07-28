import { HarmonizerRuntime, selectPerformanceProfile } from './core.mjs';

const runtime = await new HarmonizerRuntime().bootstrap();
const $ = (selector) => document.querySelector(selector);
const ASSISTANT_THREAD_KEY = 'hhs.pass161.assistant.thread';
const assistantState = {
  threadId: null,
  sending: false,
  providerOnline: false,
};

const registry = $('#registry-tree');
const grid = $('#object-grid');
const inspector = $('#inspector-content');
const lineage = $('#lineage');

async function registerAssistantObjects() {
  const objects = [
    {
      object_id: 'hhs:model:litert-lm:gemma4',
      object_type: 'MODEL',
      canonical_name: 'LITERT_LM_GEMMA4_NATIVE_MODEL',
      display_name: 'LiteRT-LM Gemma 4',
      description: 'Repository-native edge language model served through the governed HHS provider interface.',
      modality_classes: ['TEXT', 'CODE', 'TOOL_CALL'],
      lifecycle_state: 'READY',
      authority_state: 'ADVISORY',
      validation_state: 'PROVIDER_RESULT_INGRESS_REQUIRED',
      capabilities: ['TEXT_GENERATION', 'FUNCTION_CALLING', 'DEVELOPMENT_ASSISTANCE'],
      metadata: {
        provider_id: 'provider:hhs.litert_lm.gemma4',
        default_model_alias: 'gemma4-12b',
        endpoint: '/api/assistant',
        direct_vm81_mutation_allowed: false,
      },
    },
    {
      object_id: 'hhs:agent:visual-development-assistant',
      object_type: 'AGENT',
      canonical_name: 'HHS_VISUAL_DEVELOPMENT_ASSISTANT',
      display_name: 'Visual Development Assistant',
      description: 'Default natural-language interface for inspecting and developing the HHS visual object environment.',
      modality_classes: ['TEXT', 'CODE', 'GRAPH', 'VISUAL_UI'],
      lifecycle_state: 'ACTIVE',
      authority_state: 'VALIDATED_PROJECTION',
      validation_state: 'PASS161_BOUND',
      capabilities: ['OBJECT_INSPECTION', 'READ_ONLY_HHS_TOOLS', 'DEVELOPMENT_PROPOSALS'],
      dependencies: ['hhs:model:litert-lm:gemma4', 'hhs:application:harmonizer'],
      metadata: {
        home_interface: true,
        mutating_model_tool_execution_allowed: false,
        per_thread_request_serialization: true,
      },
    },
    {
      object_id: 'hhs:api:assistant-chat',
      object_type: 'API',
      canonical_name: 'HHS_LITERT_LM_ASSISTANT_CHAT_API',
      display_name: 'Assistant Chat API',
      description: 'Threaded LiteRT-LM chat surface with provider receipts and governed HHS tool execution.',
      lifecycle_state: 'READY',
      authority_state: 'VALIDATED_PROJECTION',
      validation_state: 'ROUTED',
      capabilities: ['THREAD_CREATE', 'MESSAGE_SEND', 'HEALTH_READ', 'TOOL_REGISTRY_READ'],
      metadata: {
        base_path: '/api/assistant',
        websocket_path: '/api/assistant/ws/{thread_id}',
      },
    },
  ];

  for (const object of objects) {
    if (!runtime.registry.has(object.object_id)) {
      await runtime.registry.register(object, 'system:pass161:assistant-home');
    }
  }

  const relationships = [
    ['hhs:application:harmonizer', 'hhs:agent:visual-development-assistant', 'HOSTS'],
    ['hhs:agent:visual-development-assistant', 'hhs:model:litert-lm:gemma4', 'USES_MODEL'],
    ['hhs:agent:visual-development-assistant', 'hhs:api:assistant-chat', 'USES_API'],
  ];
  for (const [parent, child, type] of relationships) {
    if (runtime.registry.has(parent) && runtime.registry.has(child)) {
      try {
        await runtime.registry.relate(parent, child, type, 'system:pass161:assistant-home');
      } catch {
        // Existing relations or inherited registry restrictions are safe to retain.
      }
    }
  }
}

await registerAssistantObjects();

const group = (objects) => objects.reduce((groups, object) => {
  (groups[object.object_type] ??= []).push(object);
  return groups;
}, {});

function objectButton(object, className) {
  const button = document.createElement('button');
  button.className = className;
  button.dataset.objectId = object.object_id;
  if (className === 'registry-item') {
    const dot = document.createElement('span');
    dot.className = 'dot';
    const label = document.createElement('span');
    label.append(object.display_name, document.createElement('br'));
    const id = document.createElement('small');
    id.textContent = object.object_id;
    label.append(id);
    const state = document.createElement('small');
    state.textContent = object.lifecycle_state;
    button.append(dot, label, state);
  } else {
    const meta = document.createElement('span');
    meta.className = 'meta';
    const type = document.createElement('span');
    type.textContent = object.object_type;
    const state = document.createElement('span');
    state.textContent = object.lifecycle_state;
    meta.append(type, state);
    const heading = document.createElement('h2');
    heading.textContent = object.display_name;
    const description = document.createElement('p');
    description.textContent = object.description;
    button.append(meta, heading, description);
  }
  button.addEventListener('click', () => selectObject(object.object_id));
  return button;
}

function renderObjects(objects = runtime.registry.list()) {
  registry.replaceChildren();
  grid.replaceChildren();
  for (const [type, items] of Object.entries(group(objects)).sort()) {
    const details = document.createElement('details');
    details.open = ['AGENT', 'APPLICATION', 'MODEL', 'RUNTIME', 'SERVICE', 'WORKSPACE'].includes(type);
    const summary = document.createElement('summary');
    summary.textContent = `${type.replaceAll('_', ' ')} · ${items.length}`;
    details.append(summary, ...items.map((object) => objectButton(object, 'registry-item')));
    registry.append(details);
  }
  grid.append(...objects.map((object) => objectButton(object, 'object-card')));
  $('#object-count').textContent = `${objects.length} objects`;
}

function inspectObject(object) {
  const panels = [
    'Overview', 'Metadata', 'Capabilities', 'Relationships', 'Diagnostics',
    'Authority', 'Receipts', 'Visual Face', 'Spatial Projection', 'Raw Schema',
  ];
  inspector.replaceChildren(...panels.map((name, index) => {
    const details = document.createElement('details');
    details.open = index < 2;
    const summary = document.createElement('summary');
    summary.textContent = name;
    const content = document.createElement('pre');
    const key = name.toLowerCase().replaceAll(' ', '_');
    const value = name === 'Visual Face'
      ? runtime.faces.resolve(object.object_id)
      : name === 'Spatial Projection'
        ? runtime.spatial.select(object.object_id)
        : name === 'Diagnostics'
          ? runtime.diagnostics.list({ object_id: object.object_id })
          : object[key] ?? object;
    content.textContent = JSON.stringify(value, null, 2);
    details.append(summary, content);
    return details;
  }));
}

async function selectObject(id) {
  const object = runtime.registry.lookup(id);
  try {
    await runtime.panels.open(id);
  } catch {
    runtime.panels.reset();
    await runtime.panels.open(id);
  }
  $('#selected-object').textContent = `${object.object_type} · ${object.object_id}`;
  inspectObject(object);
  lineage.replaceChildren(...runtime.panels.path().map((entry, index) => {
    const span = document.createElement('span');
    span.textContent = `${index ? '› ' : ''}${entry.object_id}`;
    return span;
  }));
  $('#receipt-tip').textContent = runtime.ledger.tip.slice(0, 16);
  if (matchMedia('(max-width:980px)').matches) $('#inspector').classList.add('open');
}

function showView(name) {
  const views = {
    assistant: $('#assistant-view'),
    workspace: $('#workspace-view'),
    spatial: $('#spatial-view'),
    api: $('#api-view'),
  };
  for (const [viewName, element] of Object.entries(views)) {
    element.hidden = viewName !== name;
  }
  $('#assistant-home').classList.toggle('active', name === 'assistant');
  $('#object-workspace').classList.toggle('active', name === 'workspace');
}

function setProviderStatus(online, label) {
  assistantState.providerOnline = online;
  const element = $('#provider-status');
  element.classList.toggle('verified', online);
  element.classList.toggle('degraded', !online);
  element.classList.remove('pending');
  element.textContent = label;
}

async function requestJson(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      Accept: 'application/json',
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(options.headers || {}),
    },
  });
  let payload = {};
  try {
    payload = await response.json();
  } catch {
    payload = { ok: false, error: `Non-JSON response from ${path}` };
  }
  if (!response.ok) {
    const detail = payload.detail || payload.error || response.statusText;
    const error = new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
    error.status = response.status;
    error.payload = payload;
    throw error;
  }
  return payload;
}

function appendMessage(role, content, metadata = {}) {
  const article = document.createElement('article');
  article.className = `message ${role === 'user' ? 'user-message' : 'assistant-message'}`;
  const roleLabel = document.createElement('div');
  roleLabel.className = 'message-role';
  roleLabel.textContent = role === 'user' ? 'YOU' : 'HHS ASSISTANT';
  const body = document.createElement('div');
  body.className = 'message-content';
  body.textContent = String(content || '');
  article.append(roleLabel, body);

  const entries = Object.entries(metadata).filter(([, value]) => value !== undefined && value !== null && value !== '');
  if (entries.length) {
    const meta = document.createElement('div');
    meta.className = 'message-meta';
    meta.textContent = entries.map(([key, value]) => `${key}: ${value}`).join(' · ');
    article.append(meta);
  }
  $('#conversation').append(article);
  article.scrollIntoView({ block: 'end', behavior: 'smooth' });
  return article;
}

function renderThread(thread) {
  const messages = Array.isArray(thread?.messages) ? thread.messages : [];
  const conversation = $('#conversation');
  conversation.replaceChildren();
  if (!messages.length) {
    appendMessage('assistant', 'The native LiteRT-LM development thread is ready. Describe an HHS object, interface, test, or implementation operation to inspect or propose.');
  } else {
    for (const message of messages) {
      if (!['user', 'assistant'].includes(message.role)) continue;
      appendMessage(message.role, message.content, {
        hash72: message.message_root_hash72?.slice(0, 16),
      });
    }
  }
  $('#message-count').textContent = `${thread?.message_count ?? messages.length} messages`;
}

function updateThreadIdentity(thread) {
  assistantState.threadId = thread.thread_id;
  localStorage.setItem(ASSISTANT_THREAD_KEY, thread.thread_id);
  $('#thread-label').textContent = thread.title || 'HHS Assistant';
  $('#active-thread').textContent = thread.thread_id.slice(0, 20);
  $('#message-count').textContent = `${thread.message_count ?? 0} messages`;
}

async function createThread() {
  const payload = await requestJson('/api/assistant/threads', {
    method: 'POST',
    body: JSON.stringify({
      project_id: 'project:holofractal-harmonizer',
      title: 'HHS Visual Development',
      metadata: {
        interface: 'HHS-P161-HHUMOCE',
        default_home_page: true,
      },
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
    $('#model-id').textContent = status.model_id || status.request_model_id || 'gemma4-12b';
    $('#backend-id').textContent = `${status.execution_backend || 'local'} backend · ${status.provider_id || 'LiteRT-LM'}`;
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
    if (result.thread) {
      updateThreadIdentity(result.thread);
      $('#message-count').textContent = `${result.thread.message_count ?? 0} messages`;
    }
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
$('#inspector-back').addEventListener('click', () => runtime.panels.back());
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
document.querySelectorAll('[data-close-view]').forEach((button) => button.addEventListener('click', () => showView('assistant')));
document.querySelectorAll('.spatial-node').forEach((node) => node.addEventListener('click', () => selectObject(node.dataset.objectId)));

$('#api-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const query = new FormData(event.currentTarget).get('query');
  $('#api-output').textContent = JSON.stringify(
    await runtime.apis.invoke('hhs:api:object-search', 'human:owner', { query }),
    null,
    2,
  );
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

renderObjects();
showView('assistant');
await selectObject('hhs:agent:visual-development-assistant');
await Promise.allSettled([refreshAssistantStatus(), restoreOrCreateThread()]);
window.HHSHarmonizer = runtime;
window.HHSAssistant = Object.freeze({
  get threadId() { return assistantState.threadId; },
  refreshStatus: refreshAssistantStatus,
  newThread: createThread,
  send: sendAssistantMessage,
});
