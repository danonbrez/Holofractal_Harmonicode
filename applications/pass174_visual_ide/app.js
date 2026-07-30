(() => {
  const api = '/api/v1/pass174';
  const state = {
    frame: new Uint8Array(648),
    bits: new Uint8Array(5184),
    phase: { phase64: 0, phase72: 0, phase81: 0, phase5184: 0, full_phase_lock: false },
    yaw: -0.55,
    pitch: 0.48,
    zoom: 95,
    autoRotate: true,
    selectedCell: null,
    pointer: null,
    hash216: ''.padEnd(216, '0'),
  };

  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const consoleView = $('#console');
  const receiptView = $('#receiptView');

  function toast(message, error = false) {
    const node = document.createElement('div');
    node.className = `toast${error ? ' error' : ''}`;
    node.textContent = message;
    $('#toasts').append(node);
    setTimeout(() => node.remove(), 4200);
  }

  function writeConsole(value) {
    consoleView.textContent = typeof value === 'string' ? value : JSON.stringify(value, null, 2);
    consoleView.scrollTop = consoleView.scrollHeight;
  }

  async function request(path, options = {}) {
    const response = await fetch(`${api}${path}`, {
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options,
    });
    const payload = await response.json().catch(() => ({ classification: 'NON_JSON_RESPONSE' }));
    if (!response.ok) {
      const message = payload?.detail?.classification || payload?.classification || `HTTP ${response.status}`;
      throw new Error(message);
    }
    return payload;
  }

  function setText(id, value) {
    const node = document.getElementById(id);
    if (node) node.textContent = value;
  }

  function decodeFrame(encoded) {
    const binary = atob(encoded);
    state.frame = Uint8Array.from(binary, character => character.charCodeAt(0));
    state.bits = new Uint8Array(5184);
    state.frame.forEach((byte, byteIndex) => {
      for (let bit = 0; bit < 8; bit += 1) {
        state.bits[byteIndex * 8 + bit] = (byte >> (7 - bit)) & 1;
      }
    });
  }

  function applyPhase(phase) {
    state.phase = phase;
    setText('phase64', phase.phase64);
    setText('phase72', phase.phase72);
    setText('phase81', phase.phase81);
    setText('phase5184', phase.phase5184);
    setText('phaseLock', phase.full_phase_lock ? 'LOCKED' : 'OPEN');
    $('#phaseLock').style.color = phase.full_phase_lock ? 'var(--good)' : 'var(--warn)';
  }

  function fillHash216(value) {
    state.hash216 = value || ''.padEnd(216, '0');
    const grid = $('#hash216Grid');
    grid.innerHTML = '';
    [...state.hash216].forEach((character, index) => {
      const cell = document.createElement('i');
      cell.title = `${index}: ${character}`;
      if (character !== '0') cell.classList.add('hot');
      grid.append(cell);
    });
  }

  async function refresh() {
    const [status, frame] = await Promise.all([request('/status'), request('/frame')]);
    setText('bootClass', status.classification);
    setText('stateHash72', frame.state_hash72);
    setText('vectorObjects', status.vector_objects);
    setText('legacySpecs', status.legacy_foundation.specification_count);
    applyPhase(status.phase);
    decodeFrame(frame.snapshot_b64);
    drawManifold();
    return { status, frame };
  }

  const canvas = $('#manifold');
  const ctx = canvas.getContext('2d');

  function resizeCanvas() {
    const rect = canvas.getBoundingClientRect();
    const scale = window.devicePixelRatio || 1;
    canvas.width = Math.max(1, Math.floor(rect.width * scale));
    canvas.height = Math.max(1, Math.floor(rect.height * scale));
    ctx.setTransform(scale, 0, 0, scale, 0, 0);
  }

  function rotatePoint(x, y, z) {
    const cy = Math.cos(state.yaw);
    const sy = Math.sin(state.yaw);
    const cp = Math.cos(state.pitch);
    const sp = Math.sin(state.pitch);
    const x1 = x * cy - z * sy;
    const z1 = x * sy + z * cy;
    const y1 = y * cp - z1 * sp;
    const z2 = y * sp + z1 * cp;
    return [x1, y1, z2];
  }

  function cellPoint(index) {
    const row = Math.floor(index / 9) - 4;
    const col = (index % 9) - 4;
    const ring = ((index * 8) % 72) / 72 * Math.PI * 2;
    const z = Math.sin(ring) * 1.4 + ((index % 3) - 1) * 0.22;
    return [col * 0.8, row * 0.8, z];
  }

  function cellWord(index) {
    let value = 0n;
    for (let thread = 0; thread < 64; thread += 1) {
      value = (value << 1n) | BigInt(state.bits[index * 64 + thread] || 0);
    }
    return value;
  }

  function projectedCells() {
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    const scale = state.zoom;
    return Array.from({ length: 81 }, (_, index) => {
      const [x, y, z] = rotatePoint(...cellPoint(index));
      const perspective = 1 / (1 + (z + 8) * 0.025);
      return {
        index,
        z,
        x: width / 2 + x * scale * perspective,
        y: height / 2 + y * scale * perspective,
        r: Math.max(4, 10 * perspective),
        word: cellWord(index),
      };
    }).sort((left, right) => left.z - right.z);
  }

  function drawManifold() {
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    ctx.clearRect(0, 0, width, height);
    const cells = projectedCells();
    ctx.lineWidth = 1;
    ctx.strokeStyle = 'rgba(90,160,230,.18)';
    const byIndex = new Map(cells.map(cell => [cell.index, cell]));
    cells.forEach(cell => {
      const row = Math.floor(cell.index / 9);
      const col = cell.index % 9;
      [[row, col + 1], [row + 1, col]].forEach(([targetRow, targetColumn]) => {
        if (targetRow < 9 && targetColumn < 9) {
          const other = byIndex.get(targetRow * 9 + targetColumn);
          ctx.beginPath();
          ctx.moveTo(cell.x, cell.y);
          ctx.lineTo(other.x, other.y);
          ctx.stroke();
        }
      });
    });
    cells.forEach(cell => {
      const active = cell.word !== 0n;
      const selected = state.selectedCell === cell.index;
      const gradient = ctx.createRadialGradient(cell.x - 2, cell.y - 2, 1, cell.x, cell.y, cell.r * 1.3);
      gradient.addColorStop(0, selected ? '#fff' : active ? '#8cf7ff' : '#42658f');
      gradient.addColorStop(1, selected ? '#ad8cff' : active ? '#247e9c' : '#17243a');
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(cell.x, cell.y, selected ? cell.r * 1.3 : cell.r, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = selected ? '#fff' : 'rgba(180,220,255,.35)';
      ctx.stroke();
    });
  }

  function animate() {
    if (state.autoRotate && !state.pointer) state.yaw += 0.0018;
    drawManifold();
    requestAnimationFrame(animate);
  }

  canvas.addEventListener('pointerdown', event => {
    canvas.setPointerCapture(event.pointerId);
    state.pointer = { id: event.pointerId, x: event.clientX, y: event.clientY, yaw: state.yaw, pitch: state.pitch, moved: false };
  });
  canvas.addEventListener('pointermove', event => {
    if (!state.pointer || state.pointer.id !== event.pointerId) return;
    const dx = event.clientX - state.pointer.x;
    const dy = event.clientY - state.pointer.y;
    if (Math.abs(dx) + Math.abs(dy) > 3) state.pointer.moved = true;
    state.yaw = state.pointer.yaw + dx * 0.008;
    state.pitch = Math.max(-1.3, Math.min(1.3, state.pointer.pitch + dy * 0.008));
  });
  canvas.addEventListener('pointerup', event => {
    if (!state.pointer || state.pointer.id !== event.pointerId) return;
    if (!state.pointer.moved) {
      const rect = canvas.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      const nearest = projectedCells().reduce((best, cell) => {
        const distance = Math.hypot(cell.x - x, cell.y - y);
        return !best || distance < best.distance ? { cell, distance } : best;
      }, null);
      if (nearest && nearest.distance < 28) {
        state.selectedCell = nearest.cell.index;
        $('#cellInspector').textContent = `VM81 cell ${nearest.cell.index} · 64-bit word 0x${nearest.cell.word.toString(16).padStart(16, '0')} · phase ${(nearest.cell.index * 8) % 72}`;
      }
    }
    state.pointer = null;
  });
  canvas.addEventListener('wheel', event => {
    event.preventDefault();
    state.zoom = Math.max(45, Math.min(180, state.zoom - event.deltaY * 0.08));
    $('#zoom').value = state.zoom;
  }, { passive: false });

  $('#zoom').addEventListener('input', event => { state.zoom = Number(event.target.value); });
  $$('[data-view]').forEach(button => button.addEventListener('click', () => {
    if (button.dataset.view === 'reset') Object.assign(state, { yaw: -0.55, pitch: 0.48, zoom: 95 });
    if (button.dataset.view === 'rotate') state.autoRotate = !state.autoRotate;
  }));

  async function executeStep() {
    const positions = state.selectedCell == null ? [0, 8, 72] : [state.selectedCell];
    const writes = Object.fromEntries(positions.map(position => [position, 1]));
    const result = await request('/execute', { method: 'POST', body: JSON.stringify({ thread: 0, writes, prefer_retrieval: true }) });
    receiptView.textContent = JSON.stringify(result.receipt, null, 2);
    fillHash216(result.object?.hash216?.combined);
    writeConsole(result);
    toast(result.classification);
    await refresh();
  }

  async function runPipeline() {
    const stages = $$('#pipeline [data-stage]');
    stages.forEach(node => node.classList.remove('active', 'complete'));
    for (const stage of stages) {
      stage.classList.add('active');
      await new Promise(resolve => setTimeout(resolve, 90));
      stage.classList.remove('active');
    }
    const result = await request('/sdlc/run', {
      method: 'POST',
      body: JSON.stringify({ project_id: 'visual-ide', source_name: 'main.hhs', source_modality: 'CODE', source_payload: $('#sourceEditor').value, requested_output: 'VALIDATED_ARTIFACT', thread: 0 }),
    });
    result.stages.forEach(stage => $(`#pipeline [data-stage="${stage.stage}"]`)?.classList.add('complete'));
    receiptView.textContent = JSON.stringify(result.execution.receipt, null, 2);
    fillHash216(result.execution.object?.hash216?.combined);
    writeConsole(result);
    toast(result.classification);
    await refresh();
  }

  async function compileGate() {
    const result = await request('/harmonic/compile', {
      method: 'POST',
      body: JSON.stringify({ connectors: ['+', '*', 'Or', '=='], phase_offsets: [0, 8, 9, 36], exact_weights: ['1/4', '1/4', '1/4', '1/4'], additive_endpoint: 'x+y', multiplicative_endpoint: 'xy' }),
    });
    writeConsole(result);
    receiptView.textContent = JSON.stringify(result.receipt, null, 2);
    toast('Harmonic gate compiled');
  }

  async function runAudit() {
    const challenge = `${Date.now()}:${crypto.getRandomValues(new Uint32Array(2)).join('-')}`;
    const result = await request('/audit', { method: 'POST', body: JSON.stringify({ challenge, sample_limit: 16, deep: false }) });
    writeConsole(result);
    receiptView.textContent = JSON.stringify(result.receipt, null, 2);
    toast(result.classification);
  }

  async function runReplay() {
    const result = await request('/replay');
    writeConsole(result);
    toast(result.classification);
  }

  async function showEfficiency() {
    const result = await request('/efficiency/report');
    writeConsole(result);
  }

  $('#stepFrame').addEventListener('click', () => executeStep().catch(error => { writeConsole(error.stack); toast(error.message, true); }));
  $('#runPipeline').addEventListener('click', () => runPipeline().catch(error => { writeConsole(error.stack); toast(error.message, true); }));
  $('#compileGate').addEventListener('click', () => compileGate().catch(error => toast(error.message, true)));
  $('#runAudit').addEventListener('click', () => runAudit().catch(error => toast(error.message, true)));
  $('#runReplay').addEventListener('click', () => runReplay().catch(error => toast(error.message, true)));
  $('#showEfficiency').addEventListener('click', () => showEfficiency().catch(error => toast(error.message, true)));
  $('#refreshStatus').addEventListener('click', () => refresh().catch(error => toast(error.message, true)));

  const menu = $('#systemMenu');
  $('#systemMenuButton').addEventListener('click', () => {
    menu.hidden = !menu.hidden;
    $('#systemMenuButton').setAttribute('aria-expanded', String(!menu.hidden));
  });
  $('#menuSearch').addEventListener('input', event => {
    const query = event.target.value.toLowerCase();
    $$('#systemMenu button[data-operation]').forEach(button => { button.hidden = !button.textContent.toLowerCase().includes(query); });
  });
  $$('#systemMenu button[data-operation]').forEach(button => button.addEventListener('click', async () => {
    menu.hidden = true;
    const operation = button.dataset.operation;
    try {
      if (operation === 'status' || operation === 'frame') writeConsole(await request(`/${operation}`));
      if (operation === 'audit') await runAudit();
      if (operation === 'replay') await runReplay();
      if (operation === 'efficiency') await showEfficiency();
    } catch (error) {
      toast(error.message, true);
    }
  }));

  $$('[data-collapse]').forEach(button => button.addEventListener('click', () => button.closest('.panel').classList.toggle('collapsed')));

  let draggedStage = null;
  $$('#pipeline [draggable]').forEach(stage => {
    stage.addEventListener('dragstart', () => { draggedStage = stage; });
    stage.addEventListener('dragover', event => event.preventDefault());
    stage.addEventListener('drop', event => {
      event.preventDefault();
      if (draggedStage && draggedStage !== stage) stage.before(draggedStage);
    });
  });

  const dropZone = $('#fileDropZone');
  function ingestFiles(files) {
    [...files].forEach(file => {
      const row = document.createElement('div');
      row.textContent = `${file.name} · ${file.type || 'binary'} · ${file.size} bytes`;
      $('#ingressList').append(row);
      if (file.type.startsWith('text/') || /\.(js|ts|py|md|txt|json|hhs)$/i.test(file.name)) {
        file.text().then(text => { $('#sourceEditor').value = text; });
      }
    });
  }
  ['dragenter', 'dragover'].forEach(type => dropZone.addEventListener(type, event => {
    event.preventDefault();
    dropZone.classList.add('drag-over');
  }));
  ['dragleave', 'drop'].forEach(type => dropZone.addEventListener(type, event => {
    event.preventDefault();
    dropZone.classList.remove('drag-over');
  }));
  dropZone.addEventListener('drop', event => ingestFiles(event.dataTransfer.files));
  dropZone.addEventListener('click', () => $('#fileInput').click());
  $('#fileInput').addEventListener('change', event => ingestFiles(event.target.files));
  $$('.tree-item').forEach(item => item.addEventListener('dragstart', event => event.dataTransfer.setData('text/plain', item.dataset.source)));
  $('#sourceEditor').addEventListener('dragover', event => event.preventDefault());
  $('#sourceEditor').addEventListener('drop', event => {
    event.preventDefault();
    const source = event.dataTransfer.getData('text/plain');
    if (source) $('#sourceEditor').value += `\nuse ${source}`;
  });

  window.addEventListener('resize', () => {
    resizeCanvas();
    drawManifold();
  });
  fillHash216();
  resizeCanvas();
  animate();
  refresh()
    .then(({ status }) => toast(`${status.classification} · ${status.legacy_foundation.specification_count} inherited specifications`))
    .catch(error => {
      setText('bootClass', `OFFLINE: ${error.message}`);
      toast(error.message, true);
    });
})();
