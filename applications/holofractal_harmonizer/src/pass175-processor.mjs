const API = '/api/v1/pass175';

function node(tag, attributes = {}, children = []) {
  const element = document.createElement(tag);
  Object.entries(attributes).forEach(([key, value]) => {
    if (key === 'className') element.className = value;
    else if (key === 'text') element.textContent = value;
    else element.setAttribute(key, value);
  });
  children.forEach((child) => element.append(child));
  return element;
}

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  const payload = await response.json().catch(() => ({ classification: 'NON_JSON_RESPONSE' }));
  if (!response.ok) {
    const detail = payload?.detail || payload;
    throw new Error(detail?.classification || detail?.detail || `HTTP ${response.status}`);
  }
  return payload;
}

function installStyles() {
  if (document.querySelector('[data-pass175-style]')) return;
  const style = node('style', { 'data-pass175-style': 'true' });
  style.textContent = `
    .pass175-processor-window{display:grid;gap:.65rem;padding:.7rem;background:linear-gradient(145deg,rgba(35,48,66,.94),rgba(19,25,38,.96));border:1px solid rgba(109,199,255,.24)}
    .pass175-processor-window header{display:flex;align-items:center;justify-content:space-between;gap:.5rem}.pass175-state{font-size:.68rem;letter-spacing:.08em;color:#9ce8ff}
    .pass175-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.4rem}.pass175-metric{padding:.45rem;border:1px solid rgba(145,182,226,.18);background:rgba(7,12,20,.44);border-radius:.4rem}.pass175-metric span{display:block;font-size:.58rem;opacity:.68}.pass175-metric strong{font-size:.84rem;word-break:break-word}
    .pass175-controls{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.38rem}.pass175-controls button{min-height:2rem}.pass175-address{display:grid;grid-template-columns:1fr 1fr auto;gap:.35rem}.pass175-address input{min-width:0;background:rgba(4,8,14,.7);color:inherit;border:1px solid rgba(145,182,226,.24);padding:.4rem}
    .pass175-result{max-height:11rem;overflow:auto;padding:.55rem;margin:0;background:#090d14;border:1px solid rgba(145,182,226,.16);font-size:.68rem;white-space:pre-wrap}.pass175-result.error{border-color:#d66;color:#ffb1b1}
    @media(max-width:760px){.pass175-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.pass175-address{grid-template-columns:1fr 1fr}.pass175-address button{grid-column:1/-1}}
  `;
  document.head.append(style);
}

export function initPass175Processor() {
  const controlPane = document.querySelector('.ide-control-pane');
  if (!controlPane || document.querySelector('#pass175-processor-window')) return;
  installStyles();

  const state = node('span', { className: 'pass175-state', text: 'CONNECTING' });
  const metrics = node('div', { className: 'pass175-metrics' });
  const result = node('pre', { className: 'pass175-result', text: 'Pass 175 processor status pending.' });
  const stateInput = node('input', { type: 'number', min: '0', max: '5183', value: '0', 'aria-label': 'VM5184 instruction state' });
  const controlInput = node('input', { type: 'number', min: '0', max: '242', value: '0', 'aria-label': 'G243 control' });
  const inspectButton = node('button', { type: 'button', text: 'Inspect address' });

  const windowNode = node('section', { id: 'pass175-processor-window', className: 'ide-window pass175-processor-window', 'aria-label': 'Pass 175 virtual instruction processor' }, [
    node('header', {}, [node('strong', { text: 'Pass 175 Virtual Processor' }), state]),
    metrics,
    node('div', { className: 'pass175-address' }, [stateInput, controlInput, inspectButton]),
  ]);
  const controls = node('div', { className: 'pass175-controls' });
  const actions = [
    ['Hydrate bootstrap', async () => request('/hydrate/bootstrap?seal=true', { method: 'POST' })],
    ['Execute candidates', async () => request('/execute/batch', { method: 'POST', body: JSON.stringify({ max_workers: 4, instructions: [
      { exact_bytes_b64: 'kA==', sequence: 0, thread_id: 0, explicit_delta: { 1: 1 } },
      { exact_bytes_b64: 'D6I=', sequence: 1, thread_id: 1, explicit_delta: { 2: -1 } },
    ] }) })],
    ['Replay commits', async () => request('/replay')],
    ['Refresh status', async () => request('/status')],
  ];
  actions.forEach(([label, action]) => {
    const button = node('button', { type: 'button', text: label });
    button.addEventListener('click', async () => {
      state.textContent = 'RUNNING'; result.classList.remove('error');
      try {
        const payload = await action();
        renderResult(payload);
        await refresh();
      } catch (error) {
        result.textContent = error.message; result.classList.add('error'); state.textContent = 'REJECTED';
      }
    });
    controls.append(button);
  });
  windowNode.append(controls, result);
  controlPane.append(windowNode);

  function renderMetrics(payload) {
    metrics.replaceChildren();
    const entries = [
      ['INSTRUCTIONS', payload.permanent_instruction_count],
      ['CONTROLS', payload.controls_per_instruction],
      ['PROJECTIONS', payload.projected_address_count?.toLocaleString?.() || payload.projected_address_count],
      ['HYDRATED', payload.hydrated_instruction_records],
      ['VM81 AUTHORITY', payload.singleton_vm81_commit_authority ? 'SINGLE' : 'CLOSED'],
      ['HASH72 CLOCKS', payload.hash72_commit_streams],
    ];
    entries.forEach(([label, value]) => metrics.append(node('div', { className: 'pass175-metric' }, [node('span', { text: label }), node('strong', { text: String(value ?? '—') })])));
  }

  function renderResult(payload) {
    const summary = {
      classification: payload.classification,
      candidate_count: payload.candidate_count,
      wave_count: payload.wave_count,
      microcode_store_root_sha256: payload.microcode_store_root_sha256 || payload.root_sha256,
      commit_chain_root_sha256: payload.commit_chain_root_sha256,
      sealed_through_vm81: payload.sealed_through_vm81,
      device_events: payload.waves?.flatMap((wave) => wave.device_events || []),
    };
    result.textContent = JSON.stringify(summary, null, 2);
    result.classList.remove('error');
    state.textContent = payload.classification?.replace('HHS_PASS_175_', '').slice(0, 24) || 'READY';
  }

  async function refresh() {
    const payload = await request('/status');
    renderMetrics(payload);
    state.textContent = payload.singleton_vm81_commit_authority ? 'VM81 SINGLE COMMIT' : 'AUTHORITY CLOSED';
    return payload;
  }

  inspectButton.addEventListener('click', async () => {
    state.textContent = 'INSPECTING';
    try {
      const payload = await request('/address', { method: 'POST', body: JSON.stringify({ state: Number(stateInput.value), control: Number(controlInput.value) }) });
      result.textContent = `State ${payload.address.state}\nCell ${payload.address.cell}\nOperation ${payload.address.operation}\nControl ${payload.control}\nProjected address ${payload.projected}`;
      const instruction = await request(`/instruction/${payload.address.state}`);
      result.textContent += `\nExpression ${instruction.ordered_expression}\nPhase u^${instruction.phase}\nClosure class ${instruction.closure_class ? 'YES' : 'TRANSPORT'}`;
      state.textContent = 'ADDRESS READY';
    } catch (error) {
      result.textContent = error.message; result.classList.add('error'); state.textContent = 'REJECTED';
    }
  });

  window.HHSPass175Processor = Object.freeze({ refresh, request });
  void refresh().catch((error) => { result.textContent = error.message; result.classList.add('error'); state.textContent = 'DEGRADED'; });
}
