const API = '/api/v1/pass175/terminal';

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === 'className') node.className = value;
    else if (key === 'text') node.textContent = value;
    else node.setAttribute(key, value);
  }
  for (const child of children) node.append(child);
  return node;
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

function installStyle() {
  if (document.querySelector('[data-pass175-terminal-style]')) return;
  const style = el('style', { 'data-pass175-terminal-style': 'true' });
  style.textContent = `
    .pass175-terminal-window{display:grid;gap:.65rem;padding:.7rem;background:linear-gradient(145deg,rgba(40,31,54,.96),rgba(17,23,34,.98));border:1px solid rgba(214,168,255,.28)}
    .pass175-terminal-window header{display:flex;justify-content:space-between;align-items:center;gap:.5rem}
    .pass175-terminal-state{font-size:.64rem;letter-spacing:.08em;color:#e4bfff}
    .pass175-terminal-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.38rem}
    .pass175-terminal-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.35rem}
    .pass175-terminal-metric{padding:.42rem;border:1px solid rgba(214,168,255,.18);background:rgba(7,9,16,.48);border-radius:.35rem}
    .pass175-terminal-metric span{display:block;font-size:.56rem;opacity:.68}.pass175-terminal-metric strong{font-size:.75rem;word-break:break-word}
    .pass175-terminal-form{display:grid;grid-template-columns:1fr auto;gap:.35rem}.pass175-terminal-form input{min-width:0;background:#090d14;color:inherit;border:1px solid rgba(214,168,255,.24);padding:.4rem}
    .pass175-terminal-output{margin:0;max-height:12rem;overflow:auto;white-space:pre-wrap;background:#080b12;border:1px solid rgba(214,168,255,.16);padding:.55rem;font-size:.66rem}
    .pass175-terminal-output.error{color:#ffb4b4;border-color:#d66}
    @media(max-width:760px){.pass175-terminal-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.pass175-terminal-grid{grid-template-columns:1fr}}
  `;
  document.head.append(style);
}

export function initPass175TerminalProcessor() {
  const pane = document.querySelector('.ide-control-pane');
  if (!pane || document.querySelector('#pass175-terminal-window')) return;
  installStyle();

  const state = el('span', { className: 'pass175-terminal-state', text: 'CONNECTING' });
  const metrics = el('div', { className: 'pass175-terminal-metrics' });
  const output = el('pre', { className: 'pass175-terminal-output', text: 'Terminal Pass 175 status pending.' });
  const bytesInput = el('input', {
    value: 'kA==',
    'aria-label': 'Exact x86_64 instruction bytes in base64',
    placeholder: 'Exact x86_64 bytes (base64)',
  });
  const decodeButton = el('button', { type: 'button', text: 'Decode exact bytes' });

  const windowNode = el('section', {
    id: 'pass175-terminal-window',
    className: 'ide-window pass175-terminal-window',
    'aria-label': 'Terminal Pass 175 processor completion controls',
  }, [
    el('header', {}, [
      el('strong', { text: 'Pass 175 Terminal Hardware' }),
      state,
    ]),
    metrics,
    el('div', { className: 'pass175-terminal-grid' }),
    el('div', { className: 'pass175-terminal-form' }, [bytesInput, decodeButton]),
    output,
  ]);

  const controls = windowNode.querySelector('.pass175-terminal-grid');
  const actions = [
    ['Cold hydrate + seal', () => request('/hydrate?seal=true', { method: 'POST' })],
    ['Boot firmware', () => request('/boot', { method: 'POST' })],
    ['Verify terminal pass', () => request('/verify', {
      method: 'POST',
      body: JSON.stringify({ require_boot: true }),
    })],
    ['Replay all commits', () => request('/replay')],
    ['Serial console test', () => request('/device', {
      method: 'POST',
      body: JSON.stringify({
        device: 'SERIAL',
        operation: 'WRITE',
        payload: { data_b64: 'SEhTIFAxNzUK' },
      }),
    })],
    ['Refresh terminal status', () => request('/status')],
  ];

  function summarize(payload) {
    return {
      classification: payload.classification,
      terminal_pass175_completion: payload.terminal_pass175_completion,
      checks: payload.checks,
      secure_store_root_sha256:
        payload.secure_store?.store_root_sha256 ||
        payload.secure_store_root_sha256,
      firmware_image_root_sha256:
        payload.firmware?.image_root_sha256 ||
        payload.firmware_image_root_sha256,
      boot_root_sha256: payload.boot_root_sha256 || payload.boot?.boot_root_sha256,
      device_root_sha256:
        payload.device_root_sha256 ||
        payload.device_fabric?.root_sha256,
      native_artifact_set: payload.native_artifacts?.complete,
      external_deployment_quota_required:
        payload.external_deployment_quota_required ?? false,
    };
  }

  function render(payload) {
    output.classList.remove('error');
    output.textContent = JSON.stringify(summarize(payload), null, 2);
    state.textContent = payload.terminal_pass175_completion
      ? 'TERMINAL VERIFIED'
      : (payload.classification || 'READY').replace('HHS_PASS_175_', '').slice(0, 28);
  }

  async function refresh() {
    const payload = await request('/status');
    metrics.replaceChildren();
    const values = [
      ['SECURE RECORDS', payload.secure_store?.record_count],
      ['POSITIONAL INDEXES', payload.secure_store?.positional_index_count],
      ['STORE SEALED', payload.secure_store?.sealed ? 'YES' : 'NO'],
      ['FIRMWARE', payload.firmware_image_root_sha256 ? 'HYDRATED' : 'COLD'],
      ['VM81 AUTHORITY', payload.singleton_vm81_admission ? 'SINGLE' : 'CLOSED'],
      ['HASH72 CLOCKS', payload.hash72_commit_streams],
    ];
    for (const [label, value] of values) {
      metrics.append(el('div', { className: 'pass175-terminal-metric' }, [
        el('span', { text: label }),
        el('strong', { text: String(value ?? '—') }),
      ]));
    }
    state.textContent = payload.singleton_vm81_admission ? 'VM81 SINGLE COMMIT' : 'AUTHORITY CLOSED';
    return payload;
  }

  for (const [label, action] of actions) {
    const button = el('button', { type: 'button', text: label });
    button.addEventListener('click', async () => {
      state.textContent = 'RUNNING';
      output.classList.remove('error');
      try {
        const payload = await action();
        render(payload);
        await refresh();
      } catch (error) {
        output.textContent = error.message;
        output.classList.add('error');
        state.textContent = 'REJECTED';
      }
    });
    controls.append(button);
  }

  decodeButton.addEventListener('click', async () => {
    state.textContent = 'DECODING';
    try {
      const payload = await request('/decode', {
        method: 'POST',
        body: JSON.stringify({
          exact_bytes_b64: bytesInput.value.trim(),
          decoder_mode: 'LONG_64',
        }),
      });
      const instruction = payload.instruction;
      output.textContent = JSON.stringify({
        mnemonic: instruction.mnemonic,
        exact_bytes_sha256: instruction.exact_bytes_sha256,
        retained_encoding_identity_sha256: instruction.retained_encoding_identity_sha256,
        prefix_kinds: instruction.prefix_kinds,
        opcode_map: instruction.opcode_map,
        ordered_operands: instruction.ordered_operands,
        read_set: instruction.read_set,
        write_set: instruction.write_set,
        privilege_class: instruction.privilege_class,
        exception_class: instruction.exception_class,
        micro_operations: instruction.micro_operations,
      }, null, 2);
      output.classList.remove('error');
      state.textContent = 'EXACT DECODE READY';
    } catch (error) {
      output.textContent = error.message;
      output.classList.add('error');
      state.textContent = 'REJECTED';
    }
  });

  pane.append(windowNode);
  window.HHSPass175Terminal = Object.freeze({ request, refresh });
  void refresh().catch((error) => {
    output.textContent = error.message;
    output.classList.add('error');
    state.textContent = 'DEGRADED';
  });
}
