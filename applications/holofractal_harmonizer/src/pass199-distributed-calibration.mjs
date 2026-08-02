const API = '/api/runtime/distributed-calibration';
const OBJECT_ID = 'hhs:runtime:pass199-distributed-calibration';
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
  if (document.querySelector('[data-pass199-style]')) return;
  const node = document.createElement('style');
  node.dataset.pass199Style = 'true';
  node.textContent = `
    .p199{border-top:1px solid rgba(255,255,255,.08);padding:12px;display:grid;gap:10px}
    .p199 header{display:flex;justify-content:space-between;gap:10px}.p199 h3{margin:0;font-size:13px}
    .p199 p{margin:4px 0 0;color:var(--muted,#aaa);font-size:11px;line-height:1.4}
    .p199-badge{border-radius:999px;padding:5px 8px;font-size:9px;font-weight:800;background:#332c38}
    .p199-badge.ready{background:#123c31;color:#83efc0}.p199-badge.error{background:#4b2027;color:#ff9eaa}
    .p199-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px}
    .p199-grid div,.p199-output{padding:8px;border-radius:8px;background:rgba(0,0,0,.25)}
    .p199-grid span{display:block;color:var(--muted,#aaa);font-size:8px}.p199-grid strong{display:block;margin-top:4px;font-size:11px;overflow-wrap:anywhere}
    .p199-controls{display:grid;grid-template-columns:minmax(120px,.5fr) 1fr;gap:7px}.p199-controls label{font-size:9px;color:var(--muted,#aaa)}
    .p199-controls select{width:100%;margin-top:4px;border:1px solid rgba(255,255,255,.12);border-radius:7px;padding:7px;background:#18131c;color:#eee}
    .p199-actions{display:flex;gap:7px;flex-wrap:wrap}.p199-actions button{border:0;border-radius:8px;padding:8px 10px;font-size:10px;font-weight:750;cursor:pointer}
    .p199-run{flex:1 1 210px;background:linear-gradient(135deg,#81efd3,#a6b7ff);color:#0e1115}.p199-secondary{background:#2b2230;color:#e8dff0}
    .p199-actions button:disabled{opacity:.45}.p199-output{margin:0;white-space:pre-wrap;color:#badfee;font-size:9px;line-height:1.45}
    @media(max-width:760px){.p199-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.p199-controls{grid-template-columns:1fr}}
  `;
  document.head.append(node);
}

function createPanel() {
  if (document.querySelector('#pass199-distributed-calibration')) return;
  const anchor = document.querySelector('#pass198-calibration-registry')
    || document.querySelector('#pass197-calibration')
    || document.querySelector('.lifecycle-control-window');
  if (!anchor) return;
  const node = document.createElement('section');
  node.id = 'pass199-distributed-calibration';
  node.className = 'p199';
  node.innerHTML = `
    <header><div><h3>Pass 199 Durable Calibration Fabric</h3><p>810 exact branch jobs, immutable candidates outside authority, 64 durable claim slots, and one VM81 tree commit.</p></div><span id="p199-badge" class="p199-badge">NOT RUN</span></header>
    <div class="p199-grid">
      <div><span>PARAMETER STATES</span><strong id="p199-states">—</strong></div>
      <div><span>DURABLE JOBS</span><strong id="p199-jobs">—</strong></div>
      <div><span>WORKER SLOTS</span><strong id="p199-slots">—</strong></div>
      <div><span>CANONICAL COMMITS</span><strong id="p199-commits">—</strong></div>
    </div>
    <div class="p199-controls"><label>Compute workers<select id="p199-workers"><option>4</option><option selected>8</option><option>16</option><option>32</option></select></label><div></div></div>
    <div class="p199-actions"><button id="p199-run" class="p199-run">Run durable 405-state tree</button><button id="p199-report" class="p199-secondary">Show durable receipt</button></div>
    <pre id="p199-output" class="p199-output">No Pass 199 distributed receipt is loaded in this process.</pre>`;
  anchor.insertAdjacentElement('afterend', node);
}

const setText = (id, value) => {
  const node = document.querySelector(`#${id}`);
  if (node) node.textContent = String(value ?? '—');
};

function render(value = {}, output = null) {
  state.status = value;
  const summary = value.summary || {};
  const worker = value.worker_fabric || {};
  const closed = Boolean(value.closed);
  const badge = document.querySelector('#p199-badge');
  if (badge) {
    badge.textContent = state.error ? 'ERROR' : closed ? 'CLOSED' : value.scanned ? 'INCOMPLETE' : 'NOT RUN';
    badge.className = `p199-badge ${state.error ? 'error' : closed ? 'ready' : ''}`;
  }
  setText('p199-states', summary.evaluated_parameter_states ?? '—');
  setText('p199-jobs', summary.branch_job_count ?? worker.completed_job_count ?? '—');
  setText('p199-slots', worker.durable_worker_slot_count ?? '—');
  setText('p199-commits', value.singleton_commit?.canonical_commit_operation_count ?? '—');
  const view = document.querySelector('#p199-output');
  if (view) {
    view.textContent = output || state.error || (value.report_hash72
      ? [
          `closed=${closed}`,
          `admitted=${summary.admitted_parameter_states ?? '—'}`,
          `domain_rejections=${summary.domain_rejected_parameter_states ?? '—'}`,
          `address_comparisons=${summary.address_comparisons ?? '—'}`,
          `claim_batches=${worker.claim_batch_count ?? '—'}`,
          `completion_batches=${worker.completion_batch_count ?? '—'}`,
          `replay_deterministic=${value.replay?.deterministic ?? false}`,
          `commit_receipt=${value.singleton_commit?.receipt_hash72 || '—'}`,
          `report_hash72=${value.report_hash72}`,
        ].join('\n')
      : view.textContent);
  }
  const button = document.querySelector('#p199-run');
  if (button) {
    button.disabled = state.busy;
    button.textContent = state.busy ? 'Executing durable branch jobs…' : 'Run durable 405-state tree';
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
            canonical_name: 'HHS_PASS199_DISTRIBUTED_CALIBRATION_FABRIC',
            display_name: 'Pass 199 Durable Calibration Fabric',
            description: 'Pass 198 parameter trees executed as Pass 190 durable jobs with immutable worker candidates and one singleton VM81 commit.',
            modality_classes: ['VM81_STATE', 'DURABLE_JOB_TREE', 'CALIBRATION_LEDGER', 'HASH72_RECEIPT'],
            lifecycle_state: value.closed ? 'ACTIVE' : value.scanned ? 'DEGRADED' : 'INITIALIZING',
            authority_state: 'VALIDATED_PROJECTION',
            validation_state: value.closed ? 'DISTRIBUTED_TREE_CLOSURE_VERIFIED' : 'DISTRIBUTED_CALIBRATION_PENDING',
            capabilities: ['DISTRIBUTED_CALIBRATION_STATUS_READ', 'DISTRIBUTED_CALIBRATION_RUN_REQUEST', 'DISTRIBUTED_CALIBRATION_REPORT_READ'],
            actions: [
              { action_id: 'status', method: 'GET', endpoint: `${API}/status` },
              { action_id: 'prepare', method: 'POST', endpoint: `${API}/prepare`, requires_authority: true },
              { action_id: 'run', method: 'POST', endpoint: `${API}/run`, requires_authority: true },
              { action_id: 'report', method: 'GET', endpoint: `${API}/report` },
            ],
            dependencies: ['hhs:runtime:pass198-operation-calibration-registry'],
            metadata: { contract: value.contract, report_hash72: value.report_hash72, candidate_workers_are_authority: false, frontend_is_authority: false },
          }, 'system:pass199-distributed-calibration-projection');
        }
      } catch (error) {
        console.warn('[HHS Pass199 projection]', error);
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

async function run() {
  state.busy = true;
  state.error = null;
  render(state.status || {});
  try {
    const workers = Number(document.querySelector('#p199-workers')?.value || 8);
    const report = await request(`${API}/run`, {
      method: 'POST',
      body: JSON.stringify({ operation_id: 'pass197.reciprocal_matrix_gate', config: {}, worker_count: workers, resume: true, full_replay: true }),
      timeoutMs: 600000,
    });
    render(report);
    await project(report);
  } catch (error) {
    state.error = `${error.name}: ${error.message}`;
    render(state.status || {});
  } finally {
    state.busy = false;
    render(state.status || {});
  }
}

async function showReport() {
  state.error = null;
  try {
    const report = await request(`${API}/report`, { timeoutMs: 60000 });
    render(report);
  } catch (error) {
    state.error = `${error.name}: ${error.message}`;
    render(state.status || {});
  }
}

installStyles();
createPanel();
document.querySelector('#p199-run')?.addEventListener('click', run);
document.querySelector('#p199-report')?.addEventListener('click', showReport);
refresh();
