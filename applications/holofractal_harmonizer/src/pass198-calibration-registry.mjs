const API = '/api/runtime/calibration-registry';
const OPERATION_ID = 'pass197.reciprocal_matrix_gate';
const OBJECT_ID = 'hhs:runtime:pass198-operation-calibration-registry';
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
  if (document.querySelector('[data-pass198-style]')) return;
  const node = document.createElement('style');
  node.dataset.pass198Style = 'true';
  node.textContent = `
    .p198{border-top:1px solid rgba(255,255,255,.08);padding:12px;display:grid;gap:10px}
    .p198 header{display:flex;justify-content:space-between;gap:10px}.p198 h3{margin:0;font-size:13px}
    .p198 p{margin:4px 0 0;color:var(--muted,#aaa);font-size:11px;line-height:1.4}
    .p198-badge{border-radius:999px;padding:5px 8px;font-size:9px;font-weight:800;background:#332c38}
    .p198-badge.ready{background:#123c31;color:#83efc0}.p198-badge.error{background:#4b2027;color:#ff9eaa}
    .p198-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px}
    .p198-grid div,.p198-output{padding:8px;border-radius:8px;background:rgba(0,0,0,.25)}
    .p198-grid span{display:block;color:var(--muted,#aaa);font-size:8px}.p198-grid strong{display:block;margin-top:4px;font-size:11px;overflow-wrap:anywhere}
    .p198-actions{display:flex;gap:7px;flex-wrap:wrap}.p198-actions button{border:0;border-radius:8px;padding:8px 10px;font-size:10px;font-weight:750;cursor:pointer}
    .p198-run{flex:1 1 190px;background:linear-gradient(135deg,#8ce3ff,#d8a2ff);color:#101015}.p198-secondary{background:#2b2230;color:#e8dff0}
    .p198-actions button:disabled{opacity:.45}.p198-output{margin:0;max-height:180px;overflow:auto;white-space:pre-wrap;color:#badfee;font-size:9px;line-height:1.45}
    @media(max-width:760px){.p198-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
  `;
  document.head.append(node);
}

function createPanel() {
  if (document.querySelector('#pass198-calibration-registry')) return;
  const anchor = document.querySelector('#pass197-calibration') || document.querySelector('#pass196-integration') || document.querySelector('.lifecycle-control-window');
  if (!anchor) return;
  const node = document.createElement('section');
  node.id = 'pass198-calibration-registry';
  node.className = 'p198';
  node.innerHTML = `
    <header><div><h3>Pass 198 Operation Calibration Registry</h3><p>Registered operations · deterministic parameter trees · proof-carrying simplifications · fail-closed promotion.</p></div><span id="p198-badge" class="p198-badge">LOADING</span></header>
    <div class="p198-grid">
      <div><span>OPERATIONS</span><strong id="p198-operations">—</strong></div>
      <div><span>RECORDED RUNS</span><strong id="p198-runs">—</strong></div>
      <div><span>ENVELOPE VERIFIED</span><strong id="p198-verified">—</strong></div>
      <div><span>COMPILER CANDIDATES</span><strong id="p198-candidates">—</strong></div>
    </div>
    <div class="p198-actions">
      <button id="p198-run" class="p198-run">Run registered envelope</button>
      <button id="p198-tree" class="p198-secondary">Build parameter tree</button>
      <button id="p198-proofs" class="p198-secondary">Show proof records</button>
    </div>
    <pre id="p198-output" class="p198-output">Loading persistent operation-calibration registry.</pre>`;
  anchor.insertAdjacentElement('afterend', node);
}

const setText = (id, value) => {
  const node = document.querySelector(`#${id}`);
  if (node) node.textContent = String(value ?? '—');
};

function render(status = {}, output = null) {
  state.status = status;
  const counts = status.simplification_counts || {};
  const badge = document.querySelector('#p198-badge');
  if (badge) {
    badge.textContent = state.error ? 'ERROR' : status.ok ? 'READY' : 'DEGRADED';
    badge.className = `p198-badge ${state.error ? 'error' : status.ok ? 'ready' : ''}`;
  }
  setText('p198-operations', status.operation_count ?? '—');
  setText('p198-runs', status.run_count ?? '—');
  setText('p198-verified', counts.ENVELOPE_VERIFIED ?? 0);
  setText('p198-candidates', counts.COMPILER_CANDIDATE ?? 0);
  const view = document.querySelector('#p198-output');
  if (view) {
    view.textContent = output || state.error || [
      `registry_ok=${Boolean(status.ok)}`,
      `event_chain_ok=${Boolean(status.event_chain?.ok)}`,
      `event_count=${status.event_chain?.event_count ?? '—'}`,
      `compiler_auto_promotion=${Boolean(status.compiler_auto_promotion)}`,
      `runtime_auto_admission=${Boolean(status.runtime_auto_admission)}`,
      `status_hash72=${status.registry_status_hash72 || '—'}`,
    ].join('\n');
  }
  for (const id of ['p198-run', 'p198-tree', 'p198-proofs']) {
    const button = document.querySelector(`#${id}`);
    if (button) button.disabled = state.busy;
  }
  const run = document.querySelector('#p198-run');
  if (run) run.textContent = state.busy ? 'Executing through VM81 authority…' : 'Run registered envelope';
}

async function project(status) {
  for (let attempt = 0; attempt < 200; attempt += 1) {
    const runtime = window.HHSHarmonizer;
    if (runtime?.registry) {
      try {
        if (!runtime.registry.has(OBJECT_ID)) {
          await runtime.registry.register({
            object_id: OBJECT_ID,
            object_type: 'RUNTIME',
            canonical_name: 'HHS_PASS198_OPERATION_CALIBRATION_REGISTRY',
            display_name: 'Pass 198 Operation Calibration Registry',
            description: 'Persistent calibratable-operation definitions, deterministic parameter trees, proof-carrying simplifications, promotion gates, revocation, and replay evidence.',
            modality_classes: ['OPERATION_REGISTRY', 'PARAMETER_TREE', 'SIMPLIFICATION_PROOF', 'VM81_STATE', 'HASH72_RECEIPT'],
            lifecycle_state: status.ok ? 'ACTIVE' : 'DEGRADED',
            authority_state: 'VALIDATED_PROJECTION',
            validation_state: status.ok ? 'REGISTRY_CHAIN_VERIFIED' : 'REGISTRY_REQUIRES_ATTENTION',
            capabilities: ['REGISTRY_STATUS_READ', 'PARAMETER_TREE_BUILD', 'CALIBRATION_RUN_REQUEST', 'SIMPLIFICATION_PROOF_READ'],
            actions: [
              { action_id: 'status', method: 'GET', endpoint: `${API}/status` },
              { action_id: 'parameter-tree', method: 'POST', endpoint: `${API}/parameter-tree` },
              { action_id: 'run', method: 'POST', endpoint: `${API}/run`, requires_authority: true },
              { action_id: 'simplifications', method: 'GET', endpoint: `${API}/simplifications` },
            ],
            dependencies: ['hhs:runtime:pass197-ab-hydration-calibration'],
            metadata: { contract: status.contract, registry_status_hash72: status.registry_status_hash72, frontend_is_authority: false, auto_promotion: false },
          }, 'system:pass198-calibration-registry-projection');
        }
      } catch (error) {
        console.warn('[HHS Pass198 projection]', error);
      }
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
}

async function refresh(output = null) {
  state.error = null;
  try {
    const status = await request(`${API}/status`);
    render(status, output);
    await project(status);
  } catch (error) {
    state.error = `${error.name}: ${error.message}`;
    render(state.status || {});
  }
}

async function runEnvelope() {
  state.busy = true;
  state.error = null;
  render(state.status || {});
  try {
    const run = await request(`${API}/run`, {
      method: 'POST',
      body: JSON.stringify({ operation_id: OPERATION_ID, config: {}, resume: true }),
      timeoutMs: 300000,
    });
    await refresh([
      `run_id=${run.run_id}`,
      `status=${run.status}`,
      `parameter_states=${run.summary?.evaluated_parameter_states ?? '—'}`,
      `address_comparisons=${run.summary?.address_comparisons ?? '—'}`,
      `mismatches=${run.summary?.mismatch_parameter_states ?? '—'}`,
      `report_hash72=${run.report_hash72 || '—'}`,
    ].join('\n'));
  } catch (error) {
    state.error = `${error.name}: ${error.message}`;
    render(state.status || {});
  } finally {
    state.busy = false;
    render(state.status || {});
  }
}

async function showTree() {
  state.error = null;
  try {
    const tree = await request(`${API}/parameter-tree`, {
      method: 'POST',
      body: JSON.stringify({ operation_id: OPERATION_ID, overrides: {} }),
      timeoutMs: 60000,
    });
    render(state.status || {}, [
      `operation=${tree.operation_id}`,
      `states=${tree.state_count}`,
      `eligible=${tree.eligible_state_count}`,
      `domain_rejected=${tree.rejected_state_count}`,
      `tree_hash72=${tree.tree_hash72}`,
    ].join('\n'));
  } catch (error) {
    state.error = `${error.name}: ${error.message}`;
    render(state.status || {});
  }
}

async function showProofs() {
  state.error = null;
  try {
    const result = await request(`${API}/simplifications?operation_id=${encodeURIComponent(OPERATION_ID)}`, { timeoutMs: 60000 });
    const lines = (result.simplifications || []).map((item) => [
      item.name,
      `  status=${item.status}`,
      `  runs=${item.verification_run_count}`,
      `  saved=${item.cost?.saved_fraction?.numerator ?? '—'}/${item.cost?.saved_fraction?.denominator ?? '—'}`,
      `  proof=${item.proof_hash72 || '—'}`,
    ].join('\n'));
    render(state.status || {}, lines.length ? lines.join('\n\n') : 'No simplification proof records yet. Run the registered envelope first.');
  } catch (error) {
    state.error = `${error.name}: ${error.message}`;
    render(state.status || {});
  }
}

installStyles();
createPanel();
document.querySelector('#p198-run')?.addEventListener('click', runEnvelope);
document.querySelector('#p198-tree')?.addEventListener('click', showTree);
document.querySelector('#p198-proofs')?.addEventListener('click', showProofs);
refresh();
