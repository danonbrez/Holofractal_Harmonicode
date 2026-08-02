const API = '/api/runtime/optimization-authority';
const OBJECT_ID = 'hhs:runtime:pass200a-proof-carrying-optimization';
const state = { status: null, busy: false, error: null };

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
  if (document.querySelector('[data-pass200a-style]')) return;
  const node = document.createElement('style');
  node.dataset.pass200aStyle = 'true';
  node.textContent = `
    .p200a{border-top:1px solid rgba(255,255,255,.08);padding:12px;display:grid;gap:10px}
    .p200a header{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
    .p200a h3{margin:0;font-size:13px}.p200a p{margin:4px 0 0;color:var(--muted,#aaa);font-size:11px;line-height:1.4}
    .p200a-badge{border-radius:999px;padding:5px 8px;font-size:9px;font-weight:800;background:#342b3b;white-space:nowrap}
    .p200a-badge.ready{background:#123c31;color:#83efc0}.p200a-badge.error{background:#4b2027;color:#ff9eaa}
    .p200a-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:7px}
    .p200a-grid div,.p200a-output,.p200a-boundary{padding:8px;border-radius:8px;background:rgba(0,0,0,.25)}
    .p200a-grid span{display:block;color:var(--muted,#aaa);font-size:8px}.p200a-grid strong{display:block;margin-top:4px;font-size:11px;overflow-wrap:anywhere}
    .p200a-controls{display:grid;grid-template-columns:minmax(120px,.4fr) 1fr;gap:7px}.p200a-controls label{font-size:9px;color:var(--muted,#aaa)}
    .p200a-controls select{width:100%;margin-top:4px;border:1px solid rgba(255,255,255,.12);border-radius:7px;padding:7px;background:#18131c;color:#eee}
    .p200a-actions{display:flex;gap:7px;flex-wrap:wrap}.p200a-actions button{border:0;border-radius:8px;padding:8px 10px;font-size:10px;font-weight:750;cursor:pointer}
    .p200a-primary{flex:1 1 190px;background:linear-gradient(135deg,#e7a4ff,#88d9ff);color:#11131a}.p200a-secondary{background:#2b2230;color:#e8dff0}
    .p200a-actions button:disabled{opacity:.45}.p200a-output{margin:0;white-space:pre-wrap;color:#badfee;font-size:9px;line-height:1.45}
    .p200a-boundary{color:#cbbbd4;font-size:9px;line-height:1.45}.p200a-boundary strong{color:#91f3d4}
    @media(max-width:860px){.p200a-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.p200a-controls{grid-template-columns:1fr}}
  `;
  document.head.append(node);
}

function createPanel() {
  if (document.querySelector('#pass200a-proof-carrying-optimization')) return;
  const anchor = document.querySelector('#pass199-distributed-calibration')
    || document.querySelector('#pass198-calibration-registry')
    || document.querySelector('.lifecycle-control-window');
  if (!anchor) return;
  const node = document.createElement('section');
  node.id = 'pass200a-proof-carrying-optimization';
  node.className = 'p200a';
  node.innerHTML = `
    <header>
      <div><h3>Pass 200A Proof-Carrying Optimization</h3><p>Qualifies independent exact envelopes, creates immutable compiler candidates, and compares them in shadow mode while returning the reference path.</p></div>
      <span id="p200a-badge" class="p200a-badge">IN PROGRESS</span>
    </header>
    <div class="p200a-grid">
      <div><span>HOLDOUT ENVELOPES</span><strong id="p200a-envelopes">0 / 4</strong></div>
      <div><span>IMMUTABLE BUNDLES</span><strong id="p200a-bundles">0 / 4</strong></div>
      <div><span>SHADOW MATCHES</span><strong id="p200a-matches">0 / 4</strong></div>
      <div><span>REFERENCE RETURNS</span><strong id="p200a-reference">—</strong></div>
      <div><span>CANDIDATE ACTIVATIONS</span><strong id="p200a-activations">0</strong></div>
    </div>
    <div class="p200a-controls"><label>Compute workers<select id="p200a-workers"><option>4</option><option selected>8</option><option>16</option><option>32</option></select></label><div></div></div>
    <div class="p200a-actions">
      <button id="p200a-holdouts" class="p200a-primary">Qualify four exact holdouts</button>
      <button id="p200a-shadows" class="p200a-secondary">Run compiler shadow suite</button>
      <button id="p200a-refresh" class="p200a-secondary">Refresh status</button>
    </div>
    <div class="p200a-boundary"><strong>Authority boundary:</strong> SHADOW only. The reference lane is returned. Candidate commit, canary, active return, runtime admission, and frozen constraints are disabled.</div>
    <pre id="p200a-output" class="p200a-output">No Pass 200A proof authority state is loaded in this process.</pre>`;
  anchor.insertAdjacentElement('afterend', node);
}

const setText = (id, value) => {
  const node = document.querySelector(`#${id}`);
  if (node) node.textContent = String(value ?? '—');
};

function render(value = {}, output = null) {
  state.status = value;
  const closed = Boolean(value.closed);
  const badge = document.querySelector('#p200a-badge');
  if (badge) {
    badge.textContent = state.error ? 'ERROR' : closed ? 'SHADOW VERIFIED' : 'IN PROGRESS';
    badge.className = `p200a-badge ${state.error ? 'error' : closed ? 'ready' : ''}`;
  }
  setText('p200a-envelopes', `${value.independent_envelope_count ?? 0} / 4`);
  setText('p200a-bundles', `${value.bundle_count ?? 0} / 4`);
  setText('p200a-matches', `${value.shadow_match_count ?? 0} / 4`);
  setText('p200a-reference', value.reference_return_count ?? (value.shadow_match_count ? value.shadow_match_count : '—'));
  setText('p200a-activations', value.candidate_activation_count ?? 0);
  const view = document.querySelector('#p200a-output');
  if (view) {
    view.textContent = output || state.error || [
      `classification=${value.classification || 'HHS_PASS_200A_IN_PROGRESS'}`,
      `compiler_mode=${value.compiler_mode || 'SHADOW'}`,
      `event_chain_ok=${value.event_chain?.ok ?? false}`,
      `event_count=${value.event_chain?.event_count ?? 0}`,
      `event_tip=${value.event_chain?.tip_hash72 || '—'}`,
      `reference_result_authoritative=${value.reference_result_remains_authoritative ?? true}`,
      `candidate_execution_authority=${value.candidate_execution_is_authority ?? false}`,
      `canary_enabled=${value.canary_enabled ?? false}`,
      `active_enabled=${value.active_enabled ?? false}`,
      `frozen_constraint_enabled=${value.frozen_constraint_enabled ?? false}`,
      `status_hash72=${value.status_hash72 || '—'}`,
    ].join('\n');
  }
  for (const id of ['p200a-holdouts', 'p200a-shadows']) {
    const button = document.querySelector(`#${id}`);
    if (button) button.disabled = state.busy;
  }
}

async function project(value) {
  for (let attempt = 0; attempt < 200; attempt += 1) {
    const runtime = window.HHSHarmonizer;
    if (runtime?.registry) {
      try {
        if (!runtime.registry.has(OBJECT_ID)) {
          await runtime.registry.register({
            object_id: OBJECT_ID,
            object_type: 'RUNTIME',
            canonical_name: 'HHS_PASS200A_PROOF_CARRYING_OPTIMIZATION',
            display_name: 'Pass 200A Proof-Carrying Optimization',
            description: 'Independent exact holdouts, immutable optimization bundles, and reference-authoritative compiler shadow execution.',
            modality_classes: ['VM81_STATE', 'PROOF_LEDGER', 'COMPILER_HIR', 'COMPILER_VMIR', 'HASH72_RECEIPT'],
            lifecycle_state: value.closed ? 'ACTIVE' : 'INITIALIZING',
            authority_state: 'VALIDATED_PROJECTION',
            validation_state: value.closed ? 'COMPILER_SHADOW_VERIFIED' : 'HOLDOUT_QUALIFICATION_PENDING',
            capabilities: ['OPTIMIZATION_STATUS_READ', 'HOLDOUT_QUALIFICATION_REQUEST', 'COMPILER_SHADOW_REQUEST', 'OPTIMIZATION_BUNDLE_READ'],
            actions: [
              { action_id: 'status', method: 'GET', endpoint: `${API}/status` },
              { action_id: 'run_holdouts', method: 'POST', endpoint: `${API}/holdouts/run`, requires_authority: true },
              { action_id: 'list_bundles', method: 'GET', endpoint: `${API}/bundles` },
              { action_id: 'run_shadows', method: 'POST', endpoint: `${API}/compiler/shadow/run`, requires_authority: true },
              { action_id: 'verify', method: 'GET', endpoint: `${API}/verify` },
            ],
            dependencies: ['hhs:runtime:pass199-distributed-calibration'],
            metadata: {
              contract: value.contract,
              compiler_mode: 'SHADOW',
              reference_result_remains_authoritative: true,
              candidate_execution_is_authority: false,
              canary_enabled: false,
              active_enabled: false,
              frozen_constraint_enabled: false,
              frontend_is_authority: false,
            },
          }, 'system:pass200a-proof-carrying-optimization-projection');
        }
      } catch (error) {
        console.warn('[HHS Pass200A projection]', error);
      }
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
}

async function refresh() {
  state.error = null;
  try {
    const status = await request(`${API}/status`);
    render(status);
    await project(status);
  } catch (error) {
    state.error = `${error.name}: ${error.message}`;
    render(state.status || {});
  }
}

async function runHoldouts() {
  state.busy = true;
  state.error = null;
  render(state.status || {});
  try {
    const workers = Number(document.querySelector('#p200a-workers')?.value || 8);
    const result = await request(`${API}/holdouts/run`, {
      method: 'POST',
      body: JSON.stringify({ worker_count: workers }),
      timeoutMs: 900000,
    });
    render({
      ...state.status,
      ...result,
      shadow_match_count: state.status?.shadow_match_count || 0,
      candidate_activation_count: 0,
    }, [
      `qualification_closed=${result.closed}`,
      `independent_envelopes=${result.independent_envelope_count}`,
      `compiler_candidate_bundles=${result.bundle_count}`,
      `automatic_promotions=${result.automatic_promotion_count}`,
      `qualification_hash72=${result.qualification_hash72}`,
    ].join('\n'));
  } catch (error) {
    state.error = `${error.name}: ${error.message}`;
    render(state.status || {});
  } finally {
    state.busy = false;
    await refresh();
  }
}

async function runShadows() {
  state.busy = true;
  state.error = null;
  render(state.status || {});
  try {
    const workers = Number(document.querySelector('#p200a-workers')?.value || 8);
    const result = await request(`${API}/compiler/shadow/run`, {
      method: 'POST',
      body: JSON.stringify({ worker_count: workers, config: {} }),
      timeoutMs: 900000,
    });
    render({ ...state.status, ...result }, [
      `shadow_closed=${result.closed}`,
      `shadow_matches=${result.shadow_match_count}`,
      `reference_returns=${result.reference_return_count}`,
      `candidate_activations=${result.candidate_activation_count}`,
      `state_root_hash72=${result.state_root_hash72}`,
      `shadow_suite_hash72=${result.shadow_suite_hash72}`,
    ].join('\n'));
  } catch (error) {
    state.error = `${error.name}: ${error.message}`;
    render(state.status || {});
  } finally {
    state.busy = false;
    await refresh();
  }
}

installStyles();
createPanel();
document.querySelector('#p200a-holdouts')?.addEventListener('click', runHoldouts);
document.querySelector('#p200a-shadows')?.addEventListener('click', runShadows);
document.querySelector('#p200a-refresh')?.addEventListener('click', refresh);
refresh();
