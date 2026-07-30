const INTEGRATION_SCHEMA = 'HHS_PASS161_PRODUCTION_INTEGRATION_V2';
const ACTOR_ID = 'system:production-integration';

const integrationState = {
  phase: 'BOOTSTRAP',
  runtime: null,
  runtimeAuthority: null,
  serviceDescriptors: new Map(),
  serviceObjectIds: new Map(),
  workspaceSession: null,
  installation: null,
  failures: [],
  timings: {},
};

const sleep = (milliseconds) => new Promise((resolve) => window.setTimeout(resolve, milliseconds));
const startedAt = performance.now();
const elapsed = () => Math.round(performance.now() - startedAt);

function recordFailure(surface, error, details = {}) {
  integrationState.failures.push({
    surface,
    error: error instanceof Error ? `${error.name}: ${error.message}` : String(error),
    elapsed_ms: elapsed(),
    ...details,
  });
}

const publicIntegration = {};
Object.defineProperties(publicIntegration, {
  schema: { value: INTEGRATION_SCHEMA, enumerable: true },
  phase: { enumerable: true, get: () => integrationState.phase },
  runtimeAuthority: { enumerable: true, get: () => integrationState.runtimeAuthority },
  serviceCount: { enumerable: true, get: () => integrationState.serviceDescriptors.size },
  workspaceSession: { enumerable: true, get: () => integrationState.workspaceSession },
  installation: { enumerable: true, get: () => integrationState.installation },
  failures: { enumerable: true, get: () => integrationState.failures.map((item) => ({ ...item })) },
  timings: { enumerable: true, get: () => ({ ...integrationState.timings }) },
  frontend_is_authority: { value: false, enumerable: true },
});
publicIntegration.refresh = () => hydrateProductionRegistry();
publicIntegration.dispatch = (serviceName, payload = {}) => dispatchServiceByName(serviceName, payload);
window.HHSProductionIntegration = Object.freeze(publicIntegration);

async function waitForHarmonizer() {
  for (let attempt = 0; attempt < 800; attempt += 1) {
    if (window.HHSHarmonizer?.registry) return window.HHSHarmonizer;
    await sleep(25);
  }
  throw new Error('Pass 161 Harmonizer runtime did not expose its registry');
}

async function requestJson(path, options = {}) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), options.timeoutMs ?? 30_000);
  try {
    const response = await fetch(path, {
      ...options,
      signal: controller.signal,
      headers: {
        Accept: 'application/json',
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...(options.headers || {}),
      },
    });
    const payload = await response.json().catch(() => ({
      ok: false,
      error: `Non-JSON response from ${path}`,
    }));
    if (!response.ok) {
      const detail = payload.detail || payload.error || response.statusText;
      throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
    }
    return payload;
  } finally {
    window.clearTimeout(timeout);
  }
}

async function requestJsonWithRetry(path, options = {}) {
  const attempts = Math.max(1, Number(options.attempts ?? 3));
  let lastError;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      return await requestJson(path, options);
    } catch (error) {
      lastError = error;
      recordFailure(path, error, { attempt, retryable: attempt < attempts });
      if (attempt < attempts) await sleep(Math.min(1000 * attempt, 3000));
    }
  }
  throw lastError;
}

function objectIdForService(name) {
  return `hhs:service:runtime:${encodeURIComponent(String(name))}`;
}

function objectIdForWorkspace(projectId) {
  return `hhs:workspace:project:${encodeURIComponent(String(projectId))}`;
}

function extractReceiptHash(value, depth = 0) {
  if (!value || depth > 8 || typeof value === 'string') return null;
  if (Array.isArray(value)) {
    for (const item of value) {
      const result = extractReceiptHash(item, depth + 1);
      if (result) return result;
    }
    return null;
  }
  if (typeof value !== 'object') return null;
  for (const [key, item] of Object.entries(value)) {
    if (/receipt.*hash72|receipt_hash72|turn_root_hash72/i.test(key) && typeof item === 'string' && item) {
      return item;
    }
  }
  for (const item of Object.values(value)) {
    const result = extractReceiptHash(item, depth + 1);
    if (result) return result;
  }
  return null;
}

function schemaDefaults(schema) {
  if (!schema || typeof schema !== 'object') return {};
  if (schema.default !== undefined) return structuredClone(schema.default);
  if (schema.type === 'array') return [];
  const result = {};
  const properties = schema.properties && typeof schema.properties === 'object'
    ? schema.properties
    : {};
  for (const [name, definition] of Object.entries(properties)) {
    if (definition?.default !== undefined) result[name] = structuredClone(definition.default);
    else if (definition?.type === 'object') result[name] = schemaDefaults(definition);
    else if (definition?.type === 'array') result[name] = [];
    else if (definition?.type === 'boolean') result[name] = false;
    else if (definition?.type === 'number' || definition?.type === 'integer') result[name] = 0;
    else result[name] = '';
  }
  return result;
}

function serviceSchema(descriptor) {
  return descriptor?.schema || descriptor?.runtime_contract?.request_schema || {};
}

async function safeRegister(runtime, object, surface) {
  if (runtime.registry.has(object.object_id)) return runtime.registry.lookup(object.object_id);
  try {
    return await runtime.registry.register(object, ACTOR_ID);
  } catch (error) {
    recordFailure(surface, error, { object_id: object.object_id });
    return null;
  }
}

async function safeRelate(runtime, parentId, childId, relationshipType) {
  if (!runtime.registry.has(parentId) || !runtime.registry.has(childId)) return;
  try {
    await runtime.registry.relate(parentId, childId, relationshipType, ACTOR_ID);
  } catch (error) {
    recordFailure('registry.relate', error, { parent_id: parentId, child_id: childId, relationship_type: relationshipType });
  }
}

function updateRuntimeFooter(status) {
  const validation = document.querySelector('#validation-state');
  const receipt = document.querySelector('#receipt-tip');
  if (validation) {
    validation.textContent = status?.ok
      ? 'RUNTIME AUTHORITY · RECEIPT CLOSED'
      : status?.canonical_runtime_attached
        ? 'RUNTIME AUTHORITY · WARMING'
        : 'RUNTIME AUTHORITY · UNAVAILABLE';
  }
  const receiptHash = status?.receipt_hash72 || status?.runtime?.receipt_hash72;
  if (receipt && receiptHash) receipt.textContent = String(receiptHash).slice(0, 16);
}

async function projectRuntimeAuthority(runtime, status) {
  const objectId = 'hhs:runtime:canonical-authority';
  await safeRegister(runtime, {
    object_id: objectId,
    object_type: 'RUNTIME',
    canonical_name: 'HHS_CANONICAL_RUNTIME_AUTHORITY',
    display_name: 'Canonical Runtime Authority',
    description: 'Live backend-owned VM81, graph, receipt, replay, and guarded service execution authority.',
    modality_classes: ['RUNTIME_STATE', 'GRAPH', 'RECEIPT', 'REPLAY'],
    lifecycle_state: status?.ok ? 'ACTIVE' : status?.canonical_runtime_attached ? 'INITIALIZING' : 'DEGRADED',
    authority_state: 'VALIDATED_PROJECTION',
    validation_state: status?.ok ? 'RECEIPT_CLOSED_ONLINE' : 'AUTHORITY_WARMING',
    capabilities: ['RUNTIME_STATE_READ', 'SERVICE_DISPATCH', 'WORKSPACE_COMMAND', 'RECEIPT_READ'],
    actions: [
      { action_id: 'authority.status', method: 'GET', endpoint: '/api/runtime/authority/status' },
      { action_id: 'services.list', method: 'GET', endpoint: '/api/runtime/services' },
      { action_id: 'services.dispatch', method: 'POST', endpoint: '/api/runtime/services/dispatch' },
    ],
    metadata: {
      schema: status?.schema,
      authority: status?.authority,
      frontend_is_authority: false,
      runtime_state_hash72: status?.runtime_state_hash72,
      receipt_hash72: status?.receipt_hash72,
      live_workflow: status?.live_workflow,
    },
  }, 'runtime.authority');
  await safeRelate(runtime, 'hhs:application:harmonizer', objectId, 'PROJECTS_RUNTIME');
}

function serviceObject(descriptor) {
  return {
    object_id: objectIdForService(descriptor.name),
    object_type: 'SERVICE',
    canonical_name: `HHS_RUNTIME_SERVICE_${String(descriptor.name).toUpperCase().replace(/[^A-Z0-9]+/g, '_')}`,
    display_name: descriptor.name,
    description: descriptor.description || `${descriptor.module}.${descriptor.function}`,
    modality_classes: ['RUNTIME_SERVICE', String(descriptor.service_type || 'runtime').toUpperCase()],
    lifecycle_state: 'READY',
    authority_state: 'VALIDATED_PROJECTION',
    validation_state: descriptor.conformance_decision?.derivation_complete
      ? 'KERNEL_CONFORMANCE_DERIVED'
      : 'GUARDED_REGISTRY_DECLARATION',
    capabilities: ['GUARDED_DISPATCH', ...(descriptor.invariant_ids || []), ...(descriptor.contract_schemas || [])],
    actions: [{
      action_id: 'dispatch',
      method: 'POST',
      endpoint: '/api/runtime/services/dispatch',
      service: descriptor.name,
      requires_authority: descriptor.requires_authority !== false,
    }],
    dependencies: ['hhs:runtime:canonical-authority'],
    metadata: {
      module: descriptor.module,
      function: descriptor.function,
      service_type: descriptor.service_type,
      requires_authority: descriptor.requires_authority !== false,
      request_schema: serviceSchema(descriptor),
      mutation_policy: descriptor.mutation_policy,
      persistence_policy: descriptor.persistence_policy,
      guards: descriptor.guards,
      validators: descriptor.validators,
      rejection_codes: descriptor.rejection_codes,
      runtime_contract: descriptor.runtime_contract,
    },
  };
}

async function projectServices(runtime, descriptors) {
  const tasks = descriptors.map(async (descriptor) => {
    const object = serviceObject(descriptor);
    await safeRegister(runtime, object, `service:${descriptor.name}`);
    await safeRelate(runtime, 'hhs:runtime:canonical-authority', object.object_id, 'REGISTERS_SERVICE');
  });
  await Promise.allSettled(tasks);
}

async function projectWorkspace(runtime, session) {
  const projects = Array.isArray(session?.project_summaries) ? session.project_summaries : [];
  for (const project of projects) {
    if (!project?.project_id) continue;
    const objectId = objectIdForWorkspace(project.project_id);
    await safeRegister(runtime, {
      object_id: objectId,
      object_type: 'WORKSPACE',
      canonical_name: `HHS_WORKSPACE_${String(project.project_id).toUpperCase().replace(/[^A-Z0-9]+/g, '_')}`,
      display_name: project.name || project.project_id,
      description: 'Backend-authoritative workspace project with registered multimodal objects and receipt continuity.',
      modality_classes: ['WORKSPACE', 'MULTIMODAL_OBJECTS'],
      lifecycle_state: project.status === 'ACTIVE' ? 'ACTIVE' : 'READY',
      authority_state: 'VALIDATED_PROJECTION',
      validation_state: 'WORKSPACE_AUTHORITY_BOUND',
      capabilities: ['OBJECT_INGRESS', 'INTERPRET', 'COMPILE', 'EMULATE', 'RECEIPT_READ'],
      actions: [
        { action_id: 'session.read', method: 'GET', endpoint: '/api/runtime/workspace/session' },
        { action_id: 'command.submit', method: 'POST', endpoint: '/api/runtime/workspace/command' },
      ],
      dependencies: ['hhs:runtime:canonical-authority'],
      metadata: project,
    }, `workspace:${project.project_id}`);
    await safeRelate(runtime, 'hhs:application:harmonizer', objectId, 'OPENS_WORKSPACE');
  }
}

async function projectInstallation(runtime, installation) {
  const objectId = 'hhs:diagnostic:installation-status';
  await safeRegister(runtime, {
    object_id: objectId,
    object_type: 'DIAGNOSTIC',
    canonical_name: 'HHS_PASS172_INSTALLATION_STATUS_PROJECTION',
    display_name: 'Installation Status',
    description: 'Read-only Pass 172 installation, profile, dependency, and receipt projection.',
    modality_classes: ['DIAGNOSTIC', 'INSTALLATION'],
    lifecycle_state: installation?.installed ? 'READY' : 'DEGRADED',
    authority_state: 'VALIDATED_PROJECTION',
    validation_state: 'READ_ONLY_NO_HOST_MUTATION',
    capabilities: ['INSTALLATION_STATUS_READ'],
    actions: [
      { action_id: 'status.read', method: 'GET', endpoint: '/api/runtime/installation/status' },
      { action_id: 'health.read', method: 'GET', endpoint: '/api/runtime/installation/health' },
    ],
    metadata: { ...installation, host_mutation_performed: false },
  }, 'installation.status');
  await safeRelate(runtime, 'hhs:application:harmonizer', objectId, 'PROJECTS_DIAGNOSTIC');
}

function refreshRegistryProjection() {
  const search = document.querySelector('#object-search');
  if (search) search.dispatchEvent(new Event('input', { bubbles: true }));
}

function primitiveField(name, definition, initialValue) {
  const label = document.createElement('label');
  label.className = 'service-schema-field';
  const caption = document.createElement('span');
  caption.textContent = name;
  const type = definition?.type || typeof initialValue;
  const input = document.createElement('input');
  if (type === 'boolean') {
    input.type = 'checkbox';
    input.checked = Boolean(initialValue);
  } else if (type === 'number' || type === 'integer') {
    input.type = 'number';
    input.value = String(initialValue ?? 0);
  } else {
    input.type = 'text';
    input.value = initialValue == null ? '' : String(initialValue);
  }
  input.dataset.payloadField = name;
  input.dataset.payloadType = type;
  label.append(caption, input);
  return label;
}

function mergeSchemaFields(container, payload) {
  for (const input of container.querySelectorAll('[data-payload-field]')) {
    const name = input.dataset.payloadField;
    const type = input.dataset.payloadType;
    if (type === 'boolean') payload[name] = input.checked;
    else if (type === 'number' || type === 'integer') payload[name] = Number(input.value || 0);
    else payload[name] = input.value;
  }
  return payload;
}

async function dispatchServiceByName(serviceName, payload = {}) {
  const descriptor = integrationState.serviceDescriptors.get(serviceName);
  if (!descriptor) throw new Error(`Unknown live runtime service: ${serviceName}`);
  return requestJson('/api/runtime/services/dispatch', {
    method: 'POST',
    body: JSON.stringify({ service: descriptor.name, payload }),
    timeoutMs: 120_000,
  });
}

async function dispatchService(descriptor, payload, output, button) {
  button.disabled = true;
  button.textContent = 'Executing through runtime authority…';
  output.textContent = 'Guarded dispatch in progress.';
  try {
    const result = await dispatchServiceByName(descriptor.name, payload);
    output.textContent = JSON.stringify(result, null, 2);
    const receiptHash = extractReceiptHash(result);
    if (receiptHash) document.querySelector('#receipt-tip').textContent = receiptHash.slice(0, 16);
    const validation = document.querySelector('#validation-state');
    if (validation) validation.textContent = `${descriptor.name} · BACKEND RESULT RETURNED`;
    return result;
  } catch (error) {
    output.textContent = JSON.stringify({
      schema: 'HHS_RUNTIME_SERVICE_DISPATCH_CLIENT_ERROR_V1',
      ok: false,
      service: descriptor.name,
      error: error.message,
      frontend_result_fabricated: false,
    }, null, 2);
    const validation = document.querySelector('#validation-state');
    if (validation) validation.textContent = `${descriptor.name} · DISPATCH REJECTED`;
    throw error;
  } finally {
    button.disabled = false;
    button.textContent = 'Execute registered service';
  }
}

function buildServiceExecutor(descriptor, { includeHeading = true } = {}) {
  const section = document.createElement('section');
  section.className = 'service-executor';
  section.dataset.serviceName = descriptor.name;
  if (includeHeading) {
    const heading = document.createElement('h3');
    heading.textContent = 'Guarded Service Execution';
    section.append(heading);
  }
  const identity = document.createElement('p');
  identity.textContent = `${descriptor.name} · ${descriptor.module}.${descriptor.function}`;
  section.append(identity);

  const schema = serviceSchema(descriptor);
  const defaults = schemaDefaults(schema);
  const properties = schema?.properties && typeof schema.properties === 'object' ? schema.properties : {};
  const fields = document.createElement('div');
  fields.className = 'service-schema-fields';
  for (const [name, definition] of Object.entries(properties)) {
    if (['string', 'number', 'integer', 'boolean'].includes(definition?.type)) {
      fields.append(primitiveField(name, definition, defaults[name]));
    }
  }
  if (fields.childElementCount) section.append(fields);

  const label = document.createElement('label');
  label.textContent = 'Raw payload';
  const textarea = document.createElement('textarea');
  textarea.rows = 8;
  textarea.value = JSON.stringify(defaults, null, 2);
  textarea.setAttribute('aria-label', `Payload for ${descriptor.name}`);
  label.append(textarea);

  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'primary-action';
  button.textContent = 'Execute registered service';
  const output = document.createElement('pre');
  output.textContent = 'No runtime dispatch yet.';
  button.addEventListener('click', async () => {
    try {
      const payload = JSON.parse(textarea.value || '{}');
      if (!payload || typeof payload !== 'object' || Array.isArray(payload)) throw new Error('payload must be a JSON object');
      mergeSchemaFields(fields, payload);
      textarea.value = JSON.stringify(payload, null, 2);
      await dispatchService(descriptor, payload, output, button);
    } catch (error) {
      if (output.textContent === 'No runtime dispatch yet.') {
        output.textContent = JSON.stringify({ ok: false, error: error.message }, null, 2);
      }
    }
  });
  section.append(label, button, output);
  return section;
}

function installServiceSelectionHook() {
  if (document.documentElement.dataset.hhsServiceSelectionHook === 'installed') return;
  document.documentElement.dataset.hhsServiceSelectionHook = 'installed';
  document.addEventListener('click', (event) => {
    const target = event.target instanceof Element ? event.target.closest('[data-object-id]') : null;
    const objectId = target?.dataset?.objectId;
    const serviceName = objectId && integrationState.serviceObjectIds.get(objectId);
    const descriptor = serviceName && integrationState.serviceDescriptors.get(serviceName);
    if (!descriptor) return;
    window.setTimeout(() => {
      const inspector = document.querySelector('#inspector-content');
      if (!inspector) return;
      inspector.querySelector('.service-executor-host')?.remove();
      const host = document.createElement('details');
      host.className = 'service-executor-host';
      host.open = true;
      const summary = document.createElement('summary');
      summary.textContent = 'Execute Registered Service';
      host.append(summary, buildServiceExecutor(descriptor, { includeHeading: false }));
      inspector.prepend(host);
    }, 0);
  }, true);
}

function installLiveApiController() {
  const apiView = document.querySelector('#api-view');
  if (!apiView) return;
  document.querySelector('#runtime-service-controller')?.remove();
  const section = document.createElement('section');
  section.id = 'runtime-service-controller';
  section.className = 'conversation-shell';
  const heading = document.createElement('h3');
  heading.textContent = 'Guarded Runtime Service Controller';
  const description = document.createElement('p');
  description.textContent = 'Select a live backend registry entry. Execution flows through zero-bypass interposition, runtime authority, and receipt closure.';
  const select = document.createElement('select');
  select.setAttribute('aria-label', 'Registered runtime service');
  for (const descriptor of [...integrationState.serviceDescriptors.values()].sort((a, b) => a.name.localeCompare(b.name))) {
    const option = document.createElement('option');
    option.value = descriptor.name;
    option.textContent = descriptor.name;
    select.append(option);
  }
  const host = document.createElement('div');
  const render = () => {
    host.replaceChildren();
    const descriptor = integrationState.serviceDescriptors.get(select.value);
    if (descriptor) host.append(buildServiceExecutor(descriptor));
  };
  select.addEventListener('change', render);
  section.append(heading, description, select, host);
  apiView.append(section);
  render();
}

async function hydrateOptionalProjections(runtime) {
  const optional = await Promise.allSettled([
    requestJsonWithRetry('/api/runtime/workspace/session', { timeoutMs: 30_000, attempts: 2 }),
    requestJsonWithRetry('/api/runtime/installation/status', { timeoutMs: 30_000, attempts: 2 }),
  ]);
  if (optional[0].status === 'fulfilled') {
    integrationState.workspaceSession = optional[0].value;
    await projectWorkspace(runtime, optional[0].value);
  }
  if (optional[1].status === 'fulfilled') {
    integrationState.installation = optional[1].value;
    await projectInstallation(runtime, optional[1].value);
  }
  refreshRegistryProjection();
}

async function hydrateProductionRegistry() {
  integrationState.phase = 'WAITING_FOR_PASS161';
  const runtime = await waitForHarmonizer();
  integrationState.runtime = runtime;
  integrationState.timings.pass161_ready_ms = elapsed();
  integrationState.phase = 'HYDRATING_RUNTIME_AUTHORITY';

  const validation = document.querySelector('#validation-state');
  if (validation) validation.textContent = 'P161 · CONNECTING CANONICAL BACKEND';

  const authorityResult = await Promise.allSettled([
    requestJsonWithRetry('/api/runtime/authority/status', { timeoutMs: 60_000, attempts: 3 }),
  ]);
  if (authorityResult[0].status === 'fulfilled') {
    integrationState.runtimeAuthority = authorityResult[0].value;
    updateRuntimeFooter(authorityResult[0].value);
    await projectRuntimeAuthority(runtime, authorityResult[0].value);
  }

  integrationState.phase = 'HYDRATING_SERVICE_REGISTRY';
  const servicePayload = await requestJsonWithRetry('/api/runtime/services', {
    timeoutMs: 60_000,
    attempts: 3,
  });
  const descriptors = Array.isArray(servicePayload?.services) ? servicePayload.services : [];
  if (!descriptors.length) throw new Error('live runtime service registry returned no descriptors');

  for (const descriptor of descriptors) {
    if (!descriptor?.name) continue;
    integrationState.serviceDescriptors.set(descriptor.name, descriptor);
    integrationState.serviceObjectIds.set(objectIdForService(descriptor.name), descriptor.name);
  }
  integrationState.timings.services_received_ms = elapsed();
  installLiveApiController();
  installServiceSelectionHook();
  window.dispatchEvent(new CustomEvent('hhs:production-services-ready', {
    detail: { service_count: integrationState.serviceDescriptors.size },
  }));

  integrationState.phase = 'PROJECTING_SERVICE_OBJECTS';
  await projectServices(runtime, descriptors);
  refreshRegistryProjection();
  integrationState.timings.registry_projected_ms = elapsed();
  integrationState.phase = 'READY';
  if (validation && integrationState.runtimeAuthority?.ok) {
    validation.textContent = 'RUNTIME AUTHORITY · RECEIPT CLOSED';
  }

  void hydrateOptionalProjections(runtime).catch((error) => recordFailure('optional.projections', error));
  return window.HHSProductionIntegration;
}

hydrateProductionRegistry().catch((error) => {
  recordFailure('bootstrap', error);
  integrationState.phase = 'DEGRADED';
  const validation = document.querySelector('#validation-state');
  if (validation) validation.textContent = 'P161 · PRODUCTION INTEGRATION DEGRADED';
  if (integrationState.runtime?.diagnostics) {
    integrationState.runtime.diagnostics.emit({
      diagnostic_id: 'diag:production-integration',
      class: 'APPLICATION',
      severity: 'WARNING',
      object_id: 'hhs:application:harmonizer',
      message: 'Production integration did not complete; exact failures retained on window.HHSProductionIntegration.',
      metrics: { failures: integrationState.failures },
      projection_state: 'VALIDATED_PROJECTION',
    });
  }
  console.error('HHS Pass 161 production integration failed', error, integrationState.failures);
});
