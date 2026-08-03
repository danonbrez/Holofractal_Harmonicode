const API = '/api/runtime/mainframe';
const OBJECT_ID = 'hhs:runtime:pass203-hydrated-mainframe';
const state = { status: null, functions: [], current: null, busy: false, error: null };

const unwrap = (value) => value?.payload && typeof value.payload === 'object'
  ? value.payload
  : value?.result && typeof value.result === 'object'
    ? value.result
    : value;

async function request(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), options.timeoutMs ?? 60000);
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
    const payload = await response.json().catch(() => ({ error: `Non-JSON response from ${path}` }));
    if (!response.ok) {
      const detail = payload.detail || payload.error || response.statusText;
      const message = typeof detail === 'string'
        ? detail
        : [detail.reason, detail.remediation].filter(Boolean).join('\n') || JSON.stringify(detail);
      throw new Error(message);
    }
    return unwrap(payload);
  } finally {
    clearTimeout(timer);
  }
}

function installStyles() {
  if (document.querySelector('[data-pass203-mainframe-style]')) return;
  const node = document.createElement('style');
  node.dataset.pass203MainframeStyle = 'true';
  node.textContent = `
    .p203{border-top:1px solid rgba(255,255,255,.09);padding:13px;display:grid;gap:10px;background:linear-gradient(180deg,rgba(14,24,40,.35),rgba(17,12,27,.2))}
    .p203 header{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}.p203 h3{margin:0;font-size:14px}.p203 p{margin:4px 0 0;color:var(--muted,#aaa);font-size:10px;line-height:1.45}
    .p203-badge{border-radius:999px;padding:5px 8px;font-size:9px;font-weight:800;background:#23304a;color:#b8d5ff}.p203-badge.ready{background:#123c31;color:#8df1c8}.p203-badge.error{background:#4b2027;color:#ffabb5}
    .p203-stats{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:7px}.p203-stats div,.p203-detail,.p203-output{padding:8px;border-radius:8px;background:rgba(0,0,0,.28)}
    .p203-stats span{display:block;color:var(--muted,#aaa);font-size:8px}.p203-stats strong{display:block;margin-top:4px;font-size:11px;overflow-wrap:anywhere}
    .p203-controls{display:grid;grid-template-columns:2fr 1fr auto;gap:7px}.p203 input,.p203 select,.p203 textarea{width:100%;box-sizing:border-box;border:1px solid rgba(255,255,255,.13);border-radius:7px;padding:8px;background:#111827;color:#eef4ff;font:inherit}.p203 label{font-size:9px;color:var(--muted,#aaa)}
    .p203-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px;max-height:210px;overflow:auto}.p203-function{border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:8px;background:#101622;color:#eef4ff;text-align:left;cursor:pointer}.p203-function b,.p203-function small{display:block}.p203-function small{margin-top:3px;color:#91a6c4;font-size:8px}.p203-function.active{border-color:#81e5c7;background:#142a2a}
    .p203-editor{display:grid;grid-template-columns:1fr 1fr;gap:8px}.p203 textarea{min-height:112px;resize:vertical;font-family:ui-monospace,monospace;font-size:9px}.p203-actions{display:flex;gap:7px;flex-wrap:wrap}.p203-actions button,.p203-open{border:0;border-radius:8px;padding:8px 10px;font-size:10px;font-weight:800;cursor:pointer;text-decoration:none}.p203-primary{background:linear-gradient(135deg,#8ff0d0,#73b8ff);color:#071216}.p203-secondary{background:#2a2636;color:#ece6f5}.p203-open{background:#25344c;color:#cfe2ff}.p203-actions button:disabled{opacity:.45}.p203-detail,.p203-output{margin:0;white-space:pre-wrap;overflow:auto;color:#c2dded;font-size:8px;line-height:1.4;max-height:190px}
    @media(max-width:900px){.p203-stats{grid-template-columns:repeat(2,minmax(0,1fr))}.p203-controls,.p203-editor{grid-template-columns:1fr}.p203-list{grid-template-columns:1fr}}
  `;
  document.head.append(node);
}

function createPanel() {
  if (document.querySelector('#pass203-hydrated-mainframe')) return;
  const anchor = document.querySelector('#pass201-public-api-federation')
    || document.querySelector('#pass200c-guarded-active')
    || document.querySelector('.lifecycle-control-window');
  if (!anchor) return;
  const node = document.createElement('section');
  node.id = 'pass203-hydrated-mainframe';
  node.className = 'p203';
  node.innerHTML = `
    <header><div><h3>Pass 203 Hydrated Mainframe</h3><p>Unified interpreter, compiler, ABI, workspace, artifact, job, graphics, and runtime function authority. Every hydrated function is callable and receipted; unbound declarations remain visible and fail closed.</p></div><span id="p203-badge" class="p203-badge">LOADING</span></header>
    <div class="p203-stats">
      <div><span>DISCOVERED</span><strong id="p203-total">—</strong></div>
      <div><span>HYDRATED</span><strong id="p203-hydrated">—</strong></div>
      <div><span>OPERATIONS</span><strong id="p203-operations">—</strong></div>
      <div><span>PYTHON</span><strong id="p203-python">—</strong></div>
      <div><span>NATIVE ABI</span><strong id="p203-abi">—</strong></div>
    </div>
    <div class="p203-controls">
      <label>Search<input id="p203-query" placeholder="interpreter, compiler, workspace, graphics…"></label>
      <label>Family<select id="p203-family"><option value="">All families</option><option>interpreter</option><option>compiler</option><option>workspace</option><option>artifact</option><option>job</option><option>graphics</option><option>storybook</option><option>game</option><option>abi</option><option>runtime</option></select></label>
      <button id="p203-search" class="p203-secondary">Search</button>
    </div>
    <div id="p203-list" class="p203-list"></div>
    <div class="p203-editor">
      <pre id="p203-detail" class="p203-detail">Select a hydrated function.</pre>
      <textarea id="p203-arguments" spellcheck="false">{}</textarea>
    </div>
    <div class="p203-actions">
      <button id="p203-invoke" class="p203-primary" disabled>Invoke through VM81 authority</button>
      <button id="p203-refresh" class="p203-secondary">Refresh catalog</button>
      <a class="p203-open" href="/api/runtime/mainframe/studio" target="_blank" rel="noopener">Open full mainframe studio</a>
    </div>
    <pre id="p203-output" class="p203-output">No invocation yet.</pre>`;
  anchor.insertAdjacentElement('afterend', node);
}

const text = (id, value) => {
  const node = document.querySelector(`#${id}`);
  if (node) node.textContent = String(value ?? '—');
};

function renderStatus() {
  const status = state.status || {};
  const badge = document.querySelector('#p203-badge');
  if (badge) {
    badge.textContent = state.error ? 'ERROR' : status.ok ? 'MAINFRAME READY' : 'DEGRADED';
    badge.className = `p203-badge ${state.error ? 'error' : status.ok ? 'ready' : ''}`;
  }
  text('p203-total', status.catalog_count);
  text('p203-hydrated', status.hydrated_count);
  text('p203-operations', status.kind_counts?.GOVERNED_OPERATION);
  text('p203-python', status.kind_counts?.PYTHON_FUNCTION);
  text('p203-abi', status.kind_counts?.NATIVE_ABI);
}

function renderFunctions() {
  const root = document.querySelector('#p203-list');
  if (!root) return;
  root.replaceChildren();
  for (const fn of state.functions) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `p203-function ${state.current?.function_id === fn.function_id ? 'active' : ''}`;
    button.innerHTML = `<b>${fn.name}</b><small>${fn.kind} · ${fn.family} · ${fn.execution_mode}</small>`;
    button.onclick = () => {
      state.current = fn;
      document.querySelector('#p203-detail').textContent = JSON.stringify(fn, null, 2);
      document.querySelector('#p203-invoke').disabled = !fn.callable || state.busy;
      renderFunctions();
    };
    root.append(button);
  }
  if (!state.functions.length) root.textContent = 'No hydrated functions matched the current query.';
}

async function loadFunctions() {
  state.error = null;
  const query = encodeURIComponent(document.querySelector('#p203-query')?.value || '');
  const family = encodeURIComponent(document.querySelector('#p203-family')?.value || '');
  try {
    const [status, result] = await Promise.all([
      request(`${API}/status`),
      request(`${API}/functions?hydrated_only=true&callable_only=true&limit=300&query=${query}&family=${family}`),
    ]);
    state.status = status;
    state.functions = result.functions || [];
    renderStatus();
    renderFunctions();
    await project();
  } catch (error) {
    state.error = `${error.name}: ${error.message}`;
    text('p203-output', state.error);
    renderStatus();
  }
}

async function invoke() {
  if (!state.current) return;
  let args;
  try {
    args = JSON.parse(document.querySelector('#p203-arguments')?.value || '{}');
  } catch (error) {
    text('p203-output', `Invalid JSON: ${error.message}`);
    return;
  }
  state.busy = true;
  document.querySelector('#p203-invoke').disabled = true;
  text('p203-output', `Invoking ${state.current.name}…`);
  try {
    const result = await request(`${API}/invoke`, {
      method: 'POST',
      body: JSON.stringify({ function_id: state.current.function_id, arguments: args }),
      timeoutMs: 900000,
    });
    text('p203-output', JSON.stringify(result, null, 2));
  } catch (error) {
    text('p203-output', `${error.name}: ${error.message}`);
  } finally {
    state.busy = false;
    document.querySelector('#p203-invoke').disabled = !state.current?.callable;
  }
}

async function refresh() {
  state.busy = true;
  text('p203-output', 'Refreshing complete hydrated function inventory…');
  try {
    const result = await request(`${API}/refresh`, { method: 'POST', body: '{}' , timeoutMs: 300000 });
    text('p203-output', JSON.stringify(result, null, 2));
    await loadFunctions();
  } catch (error) {
    text('p203-output', `${error.name}: ${error.message}`);
  } finally {
    state.busy = false;
  }
}

async function project() {
  for (let attempt = 0; attempt < 200; attempt += 1) {
    const runtime = window.HHSHarmonizer;
    if (runtime?.registry) {
      try {
        if (!runtime.registry.has(OBJECT_ID)) {
          await runtime.registry.register({
            object_id: OBJECT_ID,
            object_type: 'RUNTIME',
            canonical_name: 'HHS_PASS203_UNIVERSAL_HYDRATED_FUNCTION_MAINFRAME',
            display_name: 'Pass 203 Hydrated Mainframe',
            description: 'Complete function inventory and governed execution surface for interpreter, compiler, ABI, workspace, artifacts, jobs, graphics, and complex agent plans.',
            modality_classes: ['VM81_STATE', 'COMPILER_VMIR', 'HASH72_RECEIPT', 'SOURCE_CODE', 'APPLICATION_WORKFLOW', 'MULTIMODAL_ARTIFACT'],
            lifecycle_state: 'ACTIVE',
            authority_state: 'VM81_GOVERNED',
            validation_state: 'HYDRATED_FUNCTION_FEDERATION',
            capabilities: ['FUNCTION_CATALOG_READ', 'FUNCTION_INVOKE_REQUEST', 'OPERATION_INVOKE_REQUEST', 'PLAN_VALIDATE_REQUEST', 'PLAN_EXECUTE_REQUEST', 'RECEIPT_REPLAY_REQUEST'],
            actions: [
              { action_id: 'status', method: 'GET', endpoint: `${API}/status` },
              { action_id: 'functions', method: 'GET', endpoint: `${API}/functions` },
              { action_id: 'invoke', method: 'POST', endpoint: `${API}/invoke`, requires_authority: true },
              { action_id: 'operations', method: 'GET', endpoint: `${API}/operations` },
              { action_id: 'operation-invoke', method: 'POST', endpoint: `${API}/operations/invoke`, requires_authority: true },
              { action_id: 'plan-validate', method: 'POST', endpoint: `${API}/plans/validate`, requires_authority: true },
              { action_id: 'plan-execute', method: 'POST', endpoint: `${API}/plans/execute`, requires_authority: true },
              { action_id: 'jobs', method: 'GET', endpoint: `${API}/jobs/runtime` },
            ],
            dependencies: ['hhs:runtime:pass201-public-api-federation'],
            metadata: {
              cumulative_version: 203,
              all_prior_passes_inherited: true,
              every_hydrated_function_callable: true,
              unbound_functions_cataloged: true,
              arbitrary_host_eval_available: false,
              unrestricted_subprocess_available: false,
              frontend_is_authority: false,
            },
          }, 'system:pass203-mainframe-projection');
        }
      } catch (error) {
        console.warn('[HHS Pass203 projection]', error);
      }
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
}

installStyles();
createPanel();
document.querySelector('#p203-search')?.addEventListener('click', loadFunctions);
document.querySelector('#p203-invoke')?.addEventListener('click', invoke);
document.querySelector('#p203-refresh')?.addEventListener('click', refresh);
document.querySelector('#p203-query')?.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') loadFunctions();
});
loadFunctions();

window.HHSPass203Mainframe = Object.freeze({
  schema: 'HHS_PASS_203_MAINFRAME_VISUAL_PROJECTION_V1',
  api: API,
  refresh: loadFunctions,
  frontend_is_authority: false,
});
