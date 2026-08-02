const API = '/api/runtime/integration';
const OBJECT_ID = 'hhs:runtime:pass196-integrated-environment';
const state = { status: null, busy: false, error: null };

const unwrap = (value) => value?.payload && typeof value.payload === 'object' ? value.payload : value?.result && typeof value.result === 'object' ? value.result : value;

async function request(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), options.timeoutMs ?? 120000);
  try {
    const response = await fetch(path, {
      ...options,
      signal: controller.signal,
      headers: { Accept: 'application/json', ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...(options.headers || {}) },
    });
    const payload = await response.json().catch(() => ({ error: `Non-JSON response from ${path}` }));
    if (!response.ok) throw new Error(typeof (payload.detail || payload.error) === 'string' ? payload.detail || payload.error : JSON.stringify(payload.detail || payload.error || response.statusText));
    return unwrap(payload);
  } finally { clearTimeout(timer); }
}

function styles() {
  if (document.querySelector('[data-pass196-style]')) return;
  const node = document.createElement('style');
  node.dataset.pass196Style = 'true';
  node.textContent = `
    .p196{border-top:1px solid rgba(255,255,255,.08);padding:12px;display:grid;gap:10px}.p196 header{display:flex;justify-content:space-between;gap:10px}.p196 h3{margin:0;font-size:13px}.p196 p{margin:4px 0 0;color:var(--muted,#aaa);font-size:11px;line-height:1.4}.p196-badge{border-radius:999px;padding:5px 8px;font-size:9px;font-weight:800;background:#332c38}.p196-badge.ready{background:#123c31;color:#83efc0}.p196-badge.degraded{background:#4b3420;color:#ffd08a}.p196-badge.error{background:#4b2027;color:#ff9eaa}.p196-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px}.p196-grid div,.p196-output{padding:8px;border-radius:8px;background:rgba(0,0,0,.25)}.p196-grid span{display:block;color:var(--muted,#aaa);font-size:8px}.p196-grid strong{display:block;margin-top:4px;font-size:11px;overflow-wrap:anywhere}.p196-actions{display:flex;gap:7px;flex-wrap:wrap}.p196-actions button{border:0;border-radius:8px;padding:8px 10px;font-size:10px;font-weight:750;cursor:pointer}.p196-scan{flex:1 1 180px;background:linear-gradient(135deg,#8ce3ff,#d8a2ff);color:#101015}.p196-secondary{background:#2b2230;color:#e8dff0}.p196-actions button:disabled{opacity:.45}.p196-output{margin:0;max-height:140px;overflow:auto;white-space:pre-wrap;color:#badfee;font-size:9px;line-height:1.45}@media(max-width:760px){.p196-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
  `;
  document.head.append(node);
}

function createPanel() {
  if (document.querySelector('#pass196-integration')) return;
  const anchor = document.querySelector('.lifecycle-control-window');
  if (!anchor) return;
  const node = document.createElement('section');
  node.id = 'pass196-integration';
  node.className = 'p196';
  node.innerHTML = `
    <header><div><h3>Pass 196 Integrated Environment</h3><p>Genesis-to-current scan · VM81 admission · encrypted Hash216 vector memory · Linux/API-tool/IDE projection.</p></div><span id="p196-badge" class="p196-badge">UNSCANNED</span></header>
    <div class="p196-grid"><div><span>PASSES</span><strong id="p196-passes">—</strong></div><div><span>INTEGRATED</span><strong id="p196-integrated">—</strong></div><div><span>FILES</span><strong id="p196-files">—</strong></div><div><span>VECTOR</span><strong id="p196-vector">—</strong></div></div>
    <div class="p196-actions"><button id="p196-scan" class="p196-scan">Run deep integration scan</button><button id="p196-gaps" class="p196-secondary">Show gaps</button><button id="p196-tools" class="p196-secondary">API tools</button></div>
    <pre id="p196-output" class="p196-output">Repository integration authority has not been scanned in this process.</pre>`;
  anchor.insertAdjacentElement('afterend', node);
}

const setText = (id, value) => { const node = document.querySelector(`#${id}`); if (node) node.textContent = String(value ?? '—'); };
const passSummary = (status) => {
  const counts = status?.pass_state_counts || {};
  const maximum = Number(status?.maximum_discovered_pass || 0);
  const integrated = Number(counts.INTEGRATED || 0);
  const unresolved = Number(counts.PARTIAL || 0) + Number(counts.CONTRACT_ONLY || 0) + Number(counts.UNRESOLVED || 0);
  return { maximum, integrated, unresolved };
};

function render(status = {}, output = null) {
  state.status = status;
  const summary = passSummary(status);
  const badge = document.querySelector('#p196-badge');
  if (badge) {
    badge.textContent = state.error ? 'ERROR' : status.integration_closed ? 'CLOSED' : status.scanned ? 'DEGRADED' : 'UNSCANNED';
    badge.className = `p196-badge ${state.error ? 'error' : status.integration_closed ? 'ready' : status.scanned ? 'degraded' : ''}`;
  }
  setText('p196-passes', summary.maximum || '—');
  setText('p196-integrated', status.scanned ? `${summary.integrated} / ${summary.maximum}` : '—');
  setText('p196-files', status.file_count ?? '—');
  setText('p196-vector', status.vector?.persisted ? 'AES-GCM' : status.scanned ? 'NOT PERSISTED' : '—');
  const view = document.querySelector('#p196-output');
  if (view) view.textContent = output ? (typeof output === 'string' ? output : JSON.stringify(output, null, 2)) : state.error || (status.scanned ? [`phase=${status.phase}`, `integration_closed=${Boolean(status.integration_closed)}`, `global_surfaces_operational=${Boolean(status.operational)}`, `unresolved_pass_layers=${summary.unresolved}`, `manifest_hash72=${status.manifest_hash72 || '—'}`, `vector_object=${status.vector?.vector_object_id || '—'}`].join('\n') : view.textContent);
  const button = document.querySelector('#p196-scan');
  if (button) { button.disabled = state.busy; button.textContent = state.busy ? 'Scanning through VM81 authority…' : 'Run deep integration scan'; }
  const validation = document.querySelector('#validation-state');
  if (validation && status.scanned) validation.textContent = status.integration_closed ? 'PASS 196 · FULL PASS-LAYER INTEGRATION CLOSED' : `PASS 196 · DEGRADED · ${summary.unresolved} PASS LAYERS REQUIRE JOIN`;
}

async function project(status) {
  for (let attempt = 0; attempt < 200; attempt += 1) {
    const runtime = window.HHSHarmonizer;
    if (runtime?.registry) {
      try {
        if (!runtime.registry.has(OBJECT_ID)) await runtime.registry.register({
          object_id: OBJECT_ID,
          object_type: 'RUNTIME',
          canonical_name: 'HHS_PASS196_SERIALIZED_PARALLEL_INTEGRATED_ENVIRONMENT',
          display_name: 'Pass 196 Integrated Environment',
          description: 'Repository pass integration scan, VM81 admission, encrypted Hash216 vector memory, Linux API-tool server, and visual IDE projection.',
          modality_classes: ['REPOSITORY_GRAPH', 'VM81_STATE', 'ENCRYPTED_VECTOR_MEMORY', 'LINUX_ENVIRONMENT', 'API_TOOL_SERVER', 'VISUAL_IDE'],
          lifecycle_state: status.integration_closed ? 'ACTIVE' : status.scanned ? 'DEGRADED' : 'INITIALIZING',
          authority_state: 'VALIDATED_PROJECTION',
          validation_state: status.integration_closed ? 'PASS_LAYER_CLOSURE_VERIFIED' : 'PASS_LAYER_GAPS_EXPLICIT',
          capabilities: ['INTEGRATION_STATUS_READ', 'INTEGRATION_SCAN_REQUEST', 'INTEGRATION_GAP_READ', 'API_TOOL_DISCOVERY'],
          actions: [
            { action_id: 'status', method: 'GET', endpoint: `${API}/status` },
            { action_id: 'scan', method: 'POST', endpoint: `${API}/scan`, requires_authority: true },
            { action_id: 'gaps', method: 'GET', endpoint: `${API}/gaps` },
            { action_id: 'tools', method: 'GET', endpoint: `${API}/tools` },
          ],
          dependencies: ['hhs:runtime:canonical-authority'],
          metadata: { contract: status.contract, phase: status.phase, manifest_hash72: status.manifest_hash72, pass_state_counts: status.pass_state_counts, vector: status.vector, frontend_is_authority: false },
        }, 'system:pass196-integration-projection');
      } catch (error) { console.warn('[HHS Pass196 projection]', error); }
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
}

async function refresh() {
  state.error = null;
  try { const status = await request(`${API}/status`, { timeoutMs: 30000 }); render(status); await project(status); }
  catch (error) { state.error = `${error.name}: ${error.message}`; render(state.status || {}); }
}

async function scan() {
  state.busy = true; state.error = null; render(state.status || {});
  try { const status = await request(`${API}/scan`, { method: 'POST', body: JSON.stringify({ persist_vector: true }), timeoutMs: 300000 }); render(status); await project(status); }
  catch (error) { state.error = `${error.name}: ${error.message}`; render(state.status || {}); }
  finally { state.busy = false; render(state.status || {}); }
}

async function show(name) {
  state.error = null;
  try { render(state.status || {}, await request(`${API}/${name}`, { timeoutMs: 60000 })); }
  catch (error) { state.error = `${error.name}: ${error.message}`; render(state.status || {}); }
}

styles();
createPanel();
document.querySelector('#p196-scan')?.addEventListener('click', scan);
document.querySelector('#p196-gaps')?.addEventListener('click', () => show('gaps'));
document.querySelector('#p196-tools')?.addEventListener('click', () => show('tools'));
refresh();
