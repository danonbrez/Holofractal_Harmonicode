const API = '/api/runtime/calibration';
const OBJECT_ID = 'hhs:runtime:pass197-ab-hydration-calibration';
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
  if (document.querySelector('[data-pass197-style]')) return;
  const node = document.createElement('style');
  node.dataset.pass197Style = 'true';
  node.textContent = `
    .p197{border-top:1px solid rgba(255,255,255,.08);padding:12px;display:grid;gap:10px}
    .p197 header{display:flex;justify-content:space-between;gap:10px}.p197 h3{margin:0;font-size:13px}
    .p197 p{margin:4px 0 0;color:var(--muted,#aaa);font-size:11px;line-height:1.4}
    .p197-badge{border-radius:999px;padding:5px 8px;font-size:9px;font-weight:800;background:#332c38}
    .p197-badge.ready{background:#123c31;color:#83efc0}.p197-badge.error{background:#4b2027;color:#ff9eaa}
    .p197-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px}
    .p197-grid div,.p197-output{padding:8px;border-radius:8px;background:rgba(0,0,0,.25)}
    .p197-grid span{display:block;color:var(--muted,#aaa);font-size:8px}.p197-grid strong{display:block;margin-top:4px;font-size:11px;overflow-wrap:anywhere}
    .p197-actions{display:flex;gap:7px;flex-wrap:wrap}.p197-actions button{border:0;border-radius:8px;padding:8px 10px;font-size:10px;font-weight:750;cursor:pointer}
    .p197-run{flex:1 1 190px;background:linear-gradient(135deg,#8ce3ff,#d8a2ff);color:#101015}.p197-secondary{background:#2b2230;color:#e8dff0}
    .p197-actions button:disabled{opacity:.45}.p197-output{margin:0;white-space:pre-wrap;color:#badfee;font-size:9px;line-height:1.45}
    @media(max-width:760px){.p197-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
  `;
  document.head.append(node);
}

function createPanel() {
  if (document.querySelector('#pass197-calibration')) return;
  const anchor = document.querySelector('#pass196-integration') || document.querySelector('.lifecycle-control-window');
  if (!anchor) return;
  const node = document.createElement('section');
  node.id = 'pass197-calibration';
  node.className = 'p197';
  node.innerHTML = `
    <header><div><h3>Pass 197 A/B Hydration Calibration</h3><p>Exact original-versus-factorized gate trees across 81 VM81 cells × 64 lanes, with replay and lossless simplification witnesses.</p></div><span id="p197-badge" class="p197-badge">NOT RUN</span></header>
    <div class="p197-grid">
      <div><span>PARAMETER STATES</span><strong id="p197-states">—</strong></div>
      <div><span>USEFUL / ADMITTED</span><strong id="p197-useful">—</strong></div>
      <div><span>ADDRESS COMPARISONS</span><strong id="p197-addresses">—</strong></div>
      <div><span>LOSSLESS SAVINGS</span><strong id="p197-savings">—</strong></div>
    </div>
    <div class="p197-actions"><button id="p197-run" class="p197-run">Run full exact A/B tree</button><button id="p197-report" class="p197-secondary">Show receipt summary</button></div>
    <pre id="p197-output" class="p197-output">No calibration receipt is loaded in this process.</pre>`;
  anchor.insertAdjacentElement('afterend', node);
}

const setText = (id, value) => {
  const node = document.querySelector(`#${id}`);
  if (node) node.textContent = String(value ?? '—');
};

function summaryOf(value) {
  return value?.summary || value?.status?.summary || {};
}

function render(value = {}, output = null) {
  state.status = value;
  const summary = summaryOf(value);
  const closed = Boolean(value.closed);
  const badge = document.querySelector('#p197-badge');
  if (badge) {
    badge.textContent = state.error ? 'ERROR' : closed ? 'CLOSED' : value.scanned ? 'INCOMPLETE' : 'NOT RUN';
    badge.className = `p197-badge ${state.error ? 'error' : closed ? 'ready' : ''}`;
  }
  setText('p197-states', summary.evaluated_parameter_states ?? '—');
  setText('p197-useful', summary.useful_parameter_states == null ? '—' : `${summary.useful_parameter_states} / ${summary.admitted_parameter_states}`);
  setText('p197-addresses', summary.address_comparisons?.toLocaleString?.() ?? summary.address_comparisons ?? '—');
  const saved = summary.saved_fraction;
  setText('p197-savings', saved ? `${saved.numerator}/${saved.denominator}` : '—');
  const view = document.querySelector('#p197-output');
  if (view) {
    view.textContent = output || state.error || (value.scanned || value.report_hash72
      ? [
          `closed=${closed}`,
          `mismatches=${summary.mismatch_parameter_states ?? '—'}`,
          `singular_states=${summary.singular_parameter_states ?? '—'}`,
          `domain_rejections=${summary.domain_rejected_parameter_states ?? '—'}`,
          `replay_deterministic=${value.replay?.deterministic ?? 'see report'}`,
          `report_hash72=${value.report_hash72 || '—'}`,
        ].join('\n')
      : view.textContent);
  }
  const button = document.querySelector('#p197-run');
  if (button) {
    button.disabled = state.busy;
    button.textContent = state.busy ? 'Hydrating 405 parameter states…' : 'Run full exact A/B tree';
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
            canonical_name: 'HHS_PASS197_AB_HYDRATION_CALIBRATION',
            display_name: 'Pass 197 A/B Hydration Calibration',
            description: 'Exact parameter-tree calibration, 5,184-address gate verification, replay, and lossless simplification admission.',
            modality_classes: ['VM81_STATE', 'PARAMETER_TREE', 'CALIBRATION_LEDGER', 'HASH72_RECEIPT'],
            lifecycle_state: value.closed ? 'ACTIVE' : value.scanned ? 'DEGRADED' : 'INITIALIZING',
            authority_state: 'VALIDATED_PROJECTION',
            validation_state: value.closed ? 'EXACT_AB_CLOSURE_VERIFIED' : 'CALIBRATION_PENDING',
            capabilities: ['CALIBRATION_STATUS_READ', 'CALIBRATION_RUN_REQUEST', 'CALIBRATION_REPORT_READ'],
            actions: [
              { action_id: 'status', method: 'GET', endpoint: `${API}/status` },
              { action_id: 'run', method: 'POST', endpoint: `${API}/run`, requires_authority: true },
              { action_id: 'report', method: 'GET', endpoint: `${API}/report` },
            ],
            dependencies: ['hhs:runtime:pass196-integrated-environment'],
            metadata: { contract: value.contract, report_hash72: value.report_hash72, frontend_is_authority: false },
          }, 'system:pass197-calibration-projection');
        }
      } catch (error) {
        console.warn('[HHS Pass197 projection]', error);
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
    const report = await request(`${API}/run`, {
      method: 'POST',
      body: JSON.stringify({ include_domain_rejections: true, full_replay: true, resume: true }),
      timeoutMs: 300000,
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
    const summary = report.summary || {};
    render(report, [
      `parameter_states=${summary.evaluated_parameter_states ?? '—'}`,
      `useful_states=${summary.useful_parameter_states ?? '—'}`,
      `address_comparisons=${summary.address_comparisons ?? '—'}`,
      `lossless_simplifications=${summary.lossless_simplifications_admitted ?? false}`,
      `saved_leaf_evaluations=${summary.saved_leaf_evaluations ?? '—'}`,
      `replay_deterministic=${report.replay?.deterministic ?? false}`,
      `report_hash72=${report.report_hash72 || '—'}`,
    ].join('\n'));
  } catch (error) {
    state.error = `${error.name}: ${error.message}`;
    render(state.status || {});
  }
}

installStyles();
createPanel();
document.querySelector('#p197-run')?.addEventListener('click', run);
document.querySelector('#p197-report')?.addEventListener('click', showReport);
refresh();
