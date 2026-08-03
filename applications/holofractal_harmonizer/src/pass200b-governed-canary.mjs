const API = '/api/runtime/optimization-canary';
const BUNDLES_API = '/api/runtime/optimization-authority/bundles';
const OBJECT_ID = 'hhs:runtime:pass200b-governed-canary';
const state = { status: null, bundles: [], busy: false, error: null };

const unwrap = (value) => value?.payload && typeof value.payload === 'object'
  ? value.payload
  : value?.result && typeof value.result === 'object'
    ? value.result
    : value;

async function request(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), options.timeoutMs ?? 30000);
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
      throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
    }
    return unwrap(payload);
  } finally {
    clearTimeout(timer);
  }
}

function installStyles() {
  if (document.querySelector('[data-pass200b-style]')) return;
  const node = document.createElement('style');
  node.dataset.pass200bStyle = 'true';
  node.textContent = `
    .p200b{border-top:1px solid rgba(255,255,255,.08);padding:12px;display:grid;gap:10px}
    .p200b header{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}
    .p200b h3{margin:0;font-size:13px}.p200b p{margin:4px 0 0;color:var(--muted,#aaa);font-size:11px;line-height:1.4}
    .p200b-badge{border-radius:999px;padding:5px 8px;font-size:9px;font-weight:800;background:#342b3b;white-space:nowrap}
    .p200b-badge.canary{background:#46370f;color:#ffe58a}.p200b-badge.safe{background:#123c31;color:#83efc0}.p200b-badge.error{background:#4b2027;color:#ff9eaa}
    .p200b-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:7px}
    .p200b-grid div,.p200b-output,.p200b-boundary{padding:8px;border-radius:8px;background:rgba(0,0,0,.25)}
    .p200b-grid span{display:block;color:var(--muted,#aaa);font-size:8px}.p200b-grid strong{display:block;margin-top:4px;font-size:11px;overflow-wrap:anywhere}
    .p200b-controls{display:grid;grid-template-columns:2fr repeat(3,1fr);gap:7px}.p200b-controls label{font-size:9px;color:var(--muted,#aaa)}
    .p200b-controls select,.p200b-controls input{width:100%;box-sizing:border-box;margin-top:4px;border:1px solid rgba(255,255,255,.12);border-radius:7px;padding:7px;background:#18131c;color:#eee}
    .p200b-actions{display:flex;gap:7px;flex-wrap:wrap}.p200b-actions button{border:0;border-radius:8px;padding:8px 10px;font-size:10px;font-weight:750;cursor:pointer}
    .p200b-primary{flex:1 1 190px;background:linear-gradient(135deg,#ffe28b,#f0a14f);color:#17110a}.p200b-secondary{background:#2b2230;color:#e8dff0}.p200b-danger{background:#4b2027;color:#ffbec6}
    .p200b-actions button:disabled{opacity:.45}.p200b-output{margin:0;white-space:pre-wrap;color:#badfee;font-size:9px;line-height:1.45}
    .p200b-boundary{color:#cbbbd4;font-size:9px;line-height:1.45}.p200b-boundary strong{color:#91f3d4}
    @media(max-width:860px){.p200b-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.p200b-controls{grid-template-columns:1fr 1fr}}
  `;
  document.head.append(node);
}

function createPanel() {
  if (document.querySelector('#pass200b-governed-canary')) return;
  const anchor = document.querySelector('#pass200a-proof-carrying-optimization')
    || document.querySelector('#pass199-distributed-calibration')
    || document.querySelector('.lifecycle-control-window');
  if (!anchor) return;
  const node = document.createElement('section');
  node.id = 'pass200b-governed-canary';
  node.className = 'p200b';
  node.innerHTML = `
    <header>
      <div><h3>Pass 200B Governed Canary</h3><p>Admits one proof-carrying bundle behind dual VM81 approvals, exact counters, expiry, and fail-closed reference restoration.</p></div>
      <span id="p200b-badge" class="p200b-badge">REFERENCE</span>
    </header>
    <div class="p200b-grid">
      <div><span>CURRENT MODE</span><strong id="p200b-mode">REFERENCE</strong></div>
      <div><span>INVOCATIONS</span><strong id="p200b-invocations">0</strong></div>
      <div><span>CANDIDATE RETURNS</span><strong id="p200b-candidates">0</strong></div>
      <div><span>REFERENCE RETURNS</span><strong id="p200b-references">0</strong></div>
      <div><span>ROLLBACKS</span><strong id="p200b-rollbacks">0</strong></div>
    </div>
    <div class="p200b-controls">
      <label>Compiler candidate<select id="p200b-bundle"><option value="">No Pass 200A bundle loaded</option></select></label>
      <label>Invocation limit<input id="p200b-limit" type="number" min="1" max="64" value="8"></label>
      <label>Numerator<input id="p200b-numerator" type="number" min="1" max="64" value="1"></label>
      <label>Denominator<input id="p200b-denominator" type="number" min="1" max="64" value="4"></label>
    </div>
    <div class="p200b-actions">
      <button id="p200b-admit" class="p200b-primary">Admit bounded canary</button>
      <button id="p200b-probe" class="p200b-secondary">Run verified probe</button>
      <button id="p200b-rollback" class="p200b-danger">Restore reference frontier</button>
      <button id="p200b-refresh" class="p200b-secondary">Refresh</button>
    </div>
    <div class="p200b-boundary"><strong>Authority boundary:</strong> the server obtains two distinct approvals and a separate singleton activation receipt. The panel cannot manufacture approvals, comparison evidence, counters, or frontier transitions.</div>
    <pre id="p200b-output" class="p200b-output">No Pass 200B state loaded.</pre>`;
  anchor.insertAdjacentElement('afterend', node);
}

const setText = (id, value) => {
  const node = document.querySelector(`#${id}`);
  if (node) node.textContent = String(value ?? '—');
};

function currentFrontier() {
  return state.status?.current_frontier || {};
}

function render(output = null) {
  const value = state.status || {};
  const frontier = currentFrontier();
  const mode = frontier.mode || value.current_mode || 'REFERENCE';
  const badge = document.querySelector('#p200b-badge');
  if (badge) {
    badge.textContent = state.error ? 'ERROR' : mode;
    badge.className = `p200b-badge ${state.error ? 'error' : mode === 'CANARY' ? 'canary' : 'safe'}`;
  }
  setText('p200b-mode', mode);
  setText('p200b-invocations', value.total_invocations ?? 0);
  setText('p200b-candidates', value.candidate_returns ?? 0);
  setText('p200b-references', value.reference_returns ?? 0);
  setText('p200b-rollbacks', value.rollback_frontier_count ?? 0);
  const view = document.querySelector('#p200b-output');
  if (view) {
    view.textContent = output || state.error || [
      `classification=${value.classification || 'HHS_PASS_200B_GOVERNED_CANARY_ADMISSION_VERIFIED'}`,
      `frontier_id=${frontier.frontier_id || '—'}`,
      `frontier_hash72=${frontier.frontier_hash72 || '—'}`,
      `bundle_id=${frontier.bundle_id || '—'}`,
      `counter=${JSON.stringify(frontier.counter || {})}`,
      `event_chain_ok=${value.event_chain?.ok ?? false}`,
      `event_tip=${value.event_chain?.tip_hash72 || '—'}`,
      `candidate_self_authorization=${value.candidate_self_authorization ?? false}`,
      `active_mode_enabled=${value.active_mode_enabled ?? false}`,
      `frozen_constraint_enabled=${value.frozen_constraint_enabled ?? false}`,
      `status_hash72=${value.status_hash72 || '—'}`,
    ].join('\n');
  }
  const isCanary = mode === 'CANARY';
  document.querySelector('#p200b-probe')?.toggleAttribute('disabled', state.busy || !isCanary);
  document.querySelector('#p200b-rollback')?.toggleAttribute('disabled', state.busy || !isCanary);
  document.querySelector('#p200b-admit')?.toggleAttribute('disabled', state.busy || isCanary || !state.bundles.length);
}

function renderBundles() {
  const select = document.querySelector('#p200b-bundle');
  if (!select) return;
  const selected = select.value;
  select.innerHTML = '';
  for (const bundle of state.bundles) {
    const option = document.createElement('option');
    option.value = bundle.bundle_id;
    option.textContent = `${bundle.name || bundle.simplification_id} · ${bundle.bundle_id.slice(0, 12)}`;
    select.append(option);
  }
  if (!state.bundles.length) {
    const option = document.createElement('option');
    option.value = '';
    option.textContent = 'No Pass 200A compiler candidate available';
    select.append(option);
  } else if (state.bundles.some((item) => item.bundle_id === selected)) {
    select.value = selected;
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
            canonical_name: 'HHS_PASS200B_GOVERNED_CANARY_ADMISSION',
            display_name: 'Pass 200B Governed Canary',
            description: 'Dual-approved bounded candidate return with exact metering and fail-closed reference restoration.',
            modality_classes: ['VM81_STATE', 'PROOF_LEDGER', 'COMPILER_VMIR', 'HASH72_RECEIPT'],
            lifecycle_state: 'ACTIVE',
            authority_state: 'VALIDATED_PROJECTION',
            validation_state: 'GOVERNED_CANARY_AVAILABLE',
            capabilities: ['CANARY_STATUS_READ', 'CANARY_ADMISSION_REQUEST', 'CANARY_PROBE_REQUEST', 'CANARY_ROLLBACK_REQUEST'],
            actions: [
              { action_id: 'status', method: 'GET', endpoint: `${API}/status` },
              { action_id: 'admit', method: 'POST', endpoint: `${API}/admit`, requires_authority: true },
              { action_id: 'probe', method: 'POST', endpoint: `${API}/probe`, requires_authority: true },
              { action_id: 'rollback', method: 'POST', endpoint: `${API}/rollback`, requires_authority: true },
              { action_id: 'verify', method: 'GET', endpoint: `${API}/verify` },
            ],
            dependencies: ['hhs:runtime:pass200a-proof-carrying-optimization'],
            metadata: {
              dual_approval_required: true,
              bounded_invocation_limit: 64,
              candidate_self_authorization: false,
              automatic_active_promotion: false,
              automatic_frozen_constraint_promotion: false,
              frontend_is_authority: false,
            },
          }, 'system:pass200b-governed-canary-projection');
        }
      } catch (error) {
        console.warn('[HHS Pass200B projection]', error);
      }
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
}

async function refresh() {
  state.error = null;
  try {
    const [status, bundleResult] = await Promise.all([
      request(`${API}/status`),
      request(BUNDLES_API),
    ]);
    state.status = status;
    state.bundles = bundleResult.bundles || [];
    renderBundles();
    render();
    await project();
  } catch (error) {
    state.error = `${error.name}: ${error.message}`;
    render();
  }
}

async function mutate(action, body, timeoutMs = 120000) {
  state.busy = true;
  state.error = null;
  render();
  try {
    const result = await request(`${API}/${action}`, {
      method: 'POST',
      body: JSON.stringify(body),
      timeoutMs,
    });
    render(JSON.stringify(result, null, 2));
  } catch (error) {
    state.error = `${error.name}: ${error.message}`;
    render();
  } finally {
    state.busy = false;
    await refresh();
  }
}

function admit() {
  const bundleId = document.querySelector('#p200b-bundle')?.value;
  if (!bundleId) return;
  mutate('admit', {
    bundle_id: bundleId,
    invocation_limit: Number(document.querySelector('#p200b-limit')?.value || 8),
    canary_numerator: Number(document.querySelector('#p200b-numerator')?.value || 1),
    canary_denominator: Number(document.querySelector('#p200b-denominator')?.value || 4),
    expires_in_seconds: 900,
  });
}

function probe() {
  const frontierId = currentFrontier().frontier_id;
  if (frontierId) mutate('probe', { frontier_id: frontierId });
}

function rollback() {
  const frontierId = currentFrontier().frontier_id;
  if (frontierId) mutate('rollback', { frontier_id: frontierId, reason: 'VISUAL_OPERATOR_REFERENCE_RESTORE' });
}

installStyles();
createPanel();
document.querySelector('#p200b-admit')?.addEventListener('click', admit);
document.querySelector('#p200b-probe')?.addEventListener('click', probe);
document.querySelector('#p200b-rollback')?.addEventListener('click', rollback);
document.querySelector('#p200b-refresh')?.addEventListener('click', refresh);
refresh();
