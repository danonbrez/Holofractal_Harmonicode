const API = '/api/runtime/optimization-active';
const BUNDLES_API = '/api/runtime/optimization-authority/bundles';
const OBJECT_ID = 'hhs:runtime:pass200c-guarded-active';
const state = { status: null, bundles: [], evidence: null, busy: false, error: null };

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
  if (document.querySelector('[data-pass200c-style]')) return;
  const node = document.createElement('style');
  node.dataset.pass200cStyle = 'true';
  node.textContent = `
    .p200c{border-top:1px solid rgba(255,255,255,.08);padding:12px;display:grid;gap:10px}
    .p200c header{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}
    .p200c h3{margin:0;font-size:13px}.p200c p{margin:4px 0 0;color:var(--muted,#aaa);font-size:11px;line-height:1.4}
    .p200c-badge{border-radius:999px;padding:5px 8px;font-size:9px;font-weight:800;background:#342b3b;white-space:nowrap}
    .p200c-badge.active{background:#123c31;color:#83efc0}.p200c-badge.safe{background:#263448;color:#b9dcff}.p200c-badge.error{background:#4b2027;color:#ff9eaa}
    .p200c-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:7px}
    .p200c-grid div,.p200c-output,.p200c-boundary{padding:8px;border-radius:8px;background:rgba(0,0,0,.25)}
    .p200c-grid span{display:block;color:var(--muted,#aaa);font-size:8px}.p200c-grid strong{display:block;margin-top:4px;font-size:11px;overflow-wrap:anywhere}
    .p200c-controls{display:grid;grid-template-columns:2fr 1fr;gap:7px}.p200c-controls label{font-size:9px;color:var(--muted,#aaa)}
    .p200c-controls select,.p200c-controls input{width:100%;box-sizing:border-box;margin-top:4px;border:1px solid rgba(255,255,255,.12);border-radius:7px;padding:7px;background:#18131c;color:#eee}
    .p200c-actions{display:flex;gap:7px;flex-wrap:wrap}.p200c-actions button{border:0;border-radius:8px;padding:8px 10px;font-size:10px;font-weight:750;cursor:pointer}
    .p200c-primary{flex:1 1 210px;background:linear-gradient(135deg,#8ff0d0,#73b8ff);color:#0b1215}.p200c-secondary{background:#2b2230;color:#e8dff0}.p200c-danger{background:#4b2027;color:#ffbec6}
    .p200c-actions button:disabled{opacity:.45}.p200c-output{margin:0;white-space:pre-wrap;color:#badfee;font-size:9px;line-height:1.45}
    .p200c-boundary{color:#cbbbd4;font-size:9px;line-height:1.45}.p200c-boundary strong{color:#91f3d4}
    @media(max-width:900px){.p200c-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.p200c-controls{grid-template-columns:1fr}}
  `;
  document.head.append(node);
}

function createPanel() {
  if (document.querySelector('#pass200c-guarded-active')) return;
  const anchor = document.querySelector('#pass200b-governed-canary')
    || document.querySelector('#pass200a-proof-carrying-optimization')
    || document.querySelector('.lifecycle-control-window');
  if (!anchor) return;
  const node = document.createElement('section');
  node.id = 'pass200c-guarded-active';
  node.className = 'p200c';
  node.innerHTML = `
    <header>
      <div><h3>Pass 200C Guarded Active</h3><p>Promotes completed canary evidence into an exact-guarded active lease. The candidate becomes the default return only after every result, witness, and replay check passes.</p></div>
      <span id="p200c-badge" class="p200c-badge">REFERENCE</span>
    </header>
    <div class="p200c-grid">
      <div><span>CURRENT MODE</span><strong id="p200c-mode">REFERENCE</strong></div>
      <div><span>CANARY EVIDENCE</span><strong id="p200c-evidence">0 / 2</strong></div>
      <div><span>CANARY INVOCATIONS</span><strong id="p200c-canary-invocations">0 / 12</strong></div>
      <div><span>ACTIVE INVOCATIONS</span><strong id="p200c-invocations">0</strong></div>
      <div><span>CANDIDATE RETURNS</span><strong id="p200c-candidates">0</strong></div>
      <div><span>ROLLBACKS</span><strong id="p200c-rollbacks">0</strong></div>
    </div>
    <div class="p200c-controls">
      <label>Qualified compiler candidate<select id="p200c-bundle"><option value="">No bundle loaded</option></select></label>
      <label>Active lease invocations<input id="p200c-limit" type="number" min="1" max="64" value="16"></label>
    </div>
    <div class="p200c-actions">
      <button id="p200c-check" class="p200c-secondary">Check canary evidence</button>
      <button id="p200c-admit" class="p200c-primary">Admit guarded active lease</button>
      <button id="p200c-probe" class="p200c-secondary">Run exact active probe</button>
      <button id="p200c-rollback" class="p200c-danger">Restore reference frontier</button>
      <button id="p200c-refresh" class="p200c-secondary">Refresh</button>
    </div>
    <div class="p200c-boundary"><strong>Authority boundary:</strong> the server obtains compiler, runtime, operations, and singleton activation receipts. The exact guard executes on every active invocation. This panel cannot create evidence or freeze a permanent constraint.</div>
    <pre id="p200c-output" class="p200c-output">No Pass 200C state loaded.</pre>`;
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
  const badge = document.querySelector('#p200c-badge');
  if (badge) {
    badge.textContent = state.error ? 'ERROR' : mode;
    badge.className = `p200c-badge ${state.error ? 'error' : mode === 'ACTIVE_GUARDED' ? 'active' : 'safe'}`;
  }
  setText('p200c-mode', mode);
  setText('p200c-evidence', `${state.evidence?.successful_canary_count ?? 0} / 2`);
  setText('p200c-canary-invocations', `${state.evidence?.total_canary_invocations ?? 0} / 12`);
  setText('p200c-invocations', value.total_invocations ?? 0);
  setText('p200c-candidates', value.candidate_returns ?? 0);
  setText('p200c-rollbacks', value.rollback_frontier_count ?? 0);
  const view = document.querySelector('#p200c-output');
  if (view) {
    view.textContent = output || state.error || [
      `classification=${value.classification || 'HHS_PASS_200C_GUARDED_ACTIVE_ADMISSION_VERIFIED'}`,
      `frontier_id=${frontier.frontier_id || '—'}`,
      `frontier_hash72=${frontier.frontier_hash72 || '—'}`,
      `bundle_id=${frontier.bundle_id || '—'}`,
      `counter=${JSON.stringify(frontier.counter || {})}`,
      `evidence_hash72=${state.evidence?.evidence_hash72 || '—'}`,
      `guard_every_active_invocation=${value.guard_every_active_invocation ?? true}`,
      `event_chain_ok=${value.event_chain?.ok ?? false}`,
      `event_tip=${value.event_chain?.tip_hash72 || '—'}`,
      `candidate_self_authorization=${value.candidate_self_authorization ?? false}`,
      `frozen_constraint_enabled=${value.frozen_constraint_enabled ?? false}`,
      `status_hash72=${value.status_hash72 || '—'}`,
    ].join('\n');
  }
  const active = mode === 'ACTIVE_GUARDED';
  document.querySelector('#p200c-probe')?.toggleAttribute('disabled', state.busy || !active);
  document.querySelector('#p200c-rollback')?.toggleAttribute('disabled', state.busy || !active);
  document.querySelector('#p200c-admit')?.toggleAttribute('disabled', state.busy || active || !state.evidence);
  document.querySelector('#p200c-check')?.toggleAttribute('disabled', state.busy || !state.bundles.length);
}

function renderBundles() {
  const select = document.querySelector('#p200c-bundle');
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
            canonical_name: 'HHS_PASS200C_GUARDED_ACTIVE_ADMISSION',
            display_name: 'Pass 200C Guarded Active',
            description: 'Canary-evidence active admission with three approvals, exact guards, bounded leases, and reference rollback.',
            modality_classes: ['VM81_STATE', 'PROOF_LEDGER', 'COMPILER_VMIR', 'HASH72_RECEIPT'],
            lifecycle_state: 'ACTIVE',
            authority_state: 'VALIDATED_PROJECTION',
            validation_state: 'GUARDED_ACTIVE_AVAILABLE',
            capabilities: ['ACTIVE_STATUS_READ', 'ACTIVE_EVIDENCE_REQUEST', 'ACTIVE_ADMISSION_REQUEST', 'ACTIVE_PROBE_REQUEST', 'ACTIVE_ROLLBACK_REQUEST'],
            actions: [
              { action_id: 'status', method: 'GET', endpoint: `${API}/status` },
              { action_id: 'evidence', method: 'GET', endpoint: `${API}/evidence/{bundle_id}`, requires_authority: true },
              { action_id: 'admit', method: 'POST', endpoint: `${API}/admit`, requires_authority: true },
              { action_id: 'probe', method: 'POST', endpoint: `${API}/probe`, requires_authority: true },
              { action_id: 'rollback', method: 'POST', endpoint: `${API}/rollback`, requires_authority: true },
              { action_id: 'verify', method: 'GET', endpoint: `${API}/verify` },
            ],
            dependencies: ['hhs:runtime:pass200b-governed-canary'],
            metadata: {
              successful_canaries_required: 2,
              minimum_canary_invocations: 12,
              three_approvals_required: true,
              guard_every_active_invocation: true,
              candidate_self_authorization: false,
              automatic_frozen_constraint_promotion: false,
              frontend_is_authority: false,
            },
          }, 'system:pass200c-guarded-active-projection');
        }
      } catch (error) {
        console.warn('[HHS Pass200C projection]', error);
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

async function checkEvidence() {
  const bundleId = document.querySelector('#p200c-bundle')?.value;
  if (!bundleId) return;
  state.busy = true;
  state.error = null;
  render();
  try {
    state.evidence = await request(`${API}/evidence/${encodeURIComponent(bundleId)}`, { timeoutMs: 120000 });
    render(JSON.stringify(state.evidence, null, 2));
  } catch (error) {
    state.evidence = null;
    state.error = `${error.name}: ${error.message}`;
    render();
  } finally {
    state.busy = false;
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
  const bundleId = document.querySelector('#p200c-bundle')?.value;
  if (!bundleId || !state.evidence) return;
  mutate('admit', {
    bundle_id: bundleId,
    lease_invocation_limit: Number(document.querySelector('#p200c-limit')?.value || 16),
    expires_in_seconds: 1800,
  });
}

function probe() {
  const frontierId = currentFrontier().frontier_id;
  if (frontierId) mutate('probe', { frontier_id: frontierId });
}

function rollback() {
  const frontierId = currentFrontier().frontier_id;
  if (frontierId) mutate('rollback', { frontier_id: frontierId, reason: 'VISUAL_OPERATOR_ACTIVE_REFERENCE_RESTORE' });
}

installStyles();
createPanel();
document.querySelector('#p200c-check')?.addEventListener('click', checkEvidence);
document.querySelector('#p200c-admit')?.addEventListener('click', admit);
document.querySelector('#p200c-probe')?.addEventListener('click', probe);
document.querySelector('#p200c-rollback')?.addEventListener('click', rollback);
document.querySelector('#p200c-refresh')?.addEventListener('click', refresh);
refresh();
