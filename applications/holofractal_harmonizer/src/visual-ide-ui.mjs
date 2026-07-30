import { $, $$, TEXT_MODALITIES, state, activeFile, persist, setText, base64ToBytes, bytesToBase64, mediaTypeFor, log } from './visual-ide-state.mjs';

export function showIde() {
  ['#assistant-view', '#workspace-view', '#spatial-view', '#api-view'].forEach((selector) => { if ($(selector)) $(selector).hidden = true; });
  $('#ide-view').hidden = false;
  document.body.classList.add('visual-ide-active');
  $('#ide-home')?.classList.add('active');
  $('#assistant-home')?.classList.remove('active');
  $('#object-workspace')?.classList.remove('active');
}
export function showOther(name) {
  $('#ide-view').hidden = true;
  document.body.classList.remove('visual-ide-active');
  const views = { assistant: '#assistant-view', workspace: '#workspace-view', spatial: '#spatial-view', api: '#api-view' };
  Object.values(views).forEach((selector) => { if ($(selector)) $(selector).hidden = selector !== views[name]; });
}
export function renderFiles() {
  const tree = $('#ide-file-tree');
  const tabs = $('#ide-editor-tabs');
  tree?.replaceChildren(); tabs?.replaceChildren();
  state.files.forEach((file) => {
    const item = document.createElement('button');
    item.type = 'button'; item.draggable = true; item.dataset.path = file.path;
    item.className = `ide-file-item ${file.path === state.activePath ? 'active' : ''}`;
    item.style.setProperty('--tree-depth', Math.max(0, file.path.split('/').length - 1));
    item.innerHTML = `<span class="ide-file-icon">${file.bytesB64 ? '◆' : '▱'}</span><span>${file.name}</span><small>${file.dirty ? '●' : file.mediaType}</small>`;
    item.onclick = () => activateFile(file.path);
    tree?.append(item);
    const tab = document.createElement('button');
    tab.type = 'button'; tab.className = `ide-editor-tab ${file.path === state.activePath ? 'active' : ''}`;
    tab.textContent = `${file.name}${file.dirty ? ' ●' : ''}`;
    tab.onclick = () => activateFile(file.path);
    tabs?.append(tab);
  });
}
export function activateFile(path) {
  const prior = activeFile();
  const editor = $('#ide-source-editor');
  if (prior && editor && !prior.bytesB64) prior.content = editor.value;
  state.activePath = path;
  const file = activeFile();
  setText('#ide-active-file', file.name);
  setText('#selected-object', `FILE · ${file.path}`);
  setText('#ide-language-mode', file.mediaType);
  editor.readOnly = Boolean(file.bytesB64 && !TEXT_MODALITIES.has(file.mediaType));
  editor.value = editor.readOnly ? `[Preserved ${file.mediaType} source]\nname=${file.name}\nbytes=${base64ToBytes(file.bytesB64).length}` : (file.content || '');
  updateLineNumbers(); renderFiles(); persist();
}
export function updateLineNumbers() {
  const editor = $('#ide-source-editor');
  setText('#ide-line-numbers', Array.from({ length: Math.max(1, editor.value.split('\n').length) }, (_, index) => index + 1).join('\n'));
  const before = editor.value.slice(0, editor.selectionStart).split('\n');
  setText('#ide-cursor-state', `Ln ${before.length}, Col ${before.at(-1).length + 1}`);
}
export function saveFile() {
  const file = activeFile();
  if (!file.bytesB64) {
    file.content = $('#ide-source-editor').value;
    file.dirty = false;
    persist(); renderFiles(); setText('#ide-editor-state', 'SAVED');
  }
  log(`Saved ${file.path}; runtime truth is unchanged until admitted execution.`);
}
export function createFile() {
  let number = 1;
  let path = 'src/untitled.hhs';
  while (state.files.some((file) => file.path === path)) path = `src/untitled-${++number}.hhs`;
  state.files.push({ path, name: path.split('/').at(-1), mediaType: 'SOURCE_CODE', content: '', dirty: true });
  activateFile(path); $('#ide-source-editor').focus();
}
export async function addBrowserFiles(files, onIngress) {
  for (const file of files) {
    const bytes = new Uint8Array(await file.arrayBuffer());
    const type = mediaTypeFor(file.name, file.type);
    const entry = { path: `ingress/${Date.now()}-${file.name}`, name: file.name, mediaType: type, dirty: false };
    if (TEXT_MODALITIES.has(type)) entry.content = new TextDecoder().decode(bytes);
    else entry.bytesB64 = bytesToBase64(bytes);
    state.files.push(entry); state.activePath = entry.path;
  }
  activateFile(state.activePath);
  await onIngress();
}
export function renderSnapshot(snapshot) {
  const bytes = base64ToBytes(snapshot.projection_b64 || bytesToBase64(new Uint8Array(648)));
  const grid = $('#ide-vm-grid');
  const spatial = $('#ide-3d-snapshot');
  grid?.replaceChildren(); spatial?.replaceChildren();
  for (let cell = 0; cell < 81; cell += 1) {
    const lane = bytes.slice(cell * 8, cell * 8 + 8);
    const bits = [...lane].map((value) => value.toString(2).padStart(8, '0')).join('');
    const popcount = [...bits].filter((bit) => bit === '1').length;
    const button = document.createElement('button');
    button.type = 'button'; button.className = 'ide-vm-cell'; button.textContent = cell + 1;
    button.style.setProperty('--vm-density', popcount / 64);
    button.onclick = () => setText('#ide-vm-cell-detail', `cell=${cell + 1} lane64=${bits} popcount=${popcount} byte_offset=${cell * 8}`);
    grid?.append(button);
    const node = document.createElement('div');
    node.className = `ide-3d-bit ${popcount ? 'active' : ''}`;
    node.style.opacity = .18 + (popcount / 64) * .82;
    spatial?.append(node);
  }
  setText('#ide-vm-root', snapshot.projection_hash72?.slice(0, 16) || 'GENESIS');
}
export function renderHash216(snapshot) {
  const positions = snapshot.ingestion_positions_hash216 || [];
  const host = $('#ide-hash216-lanes'); host?.replaceChildren();
  for (let laneIndex = 0; laneIndex < 3; laneIndex += 1) {
    const section = document.createElement('section'); section.className = 'ide-hash-lane';
    section.innerHTML = `<strong>HASH216 LANE ${laneIndex + 1} · 72 POSITIONS</strong>`;
    const dots = document.createElement('div'); dots.className = 'ide-hash-dots';
    for (let index = 0; index < 72; index += 1) {
      const value = positions[laneIndex * 72 + index];
      const dot = document.createElement('span'); dot.className = `ide-hash-dot ${value ? 'populated' : ''}`; dot.title = value || `position ${index + 1}`; dots.append(dot);
    }
    section.append(dots); host?.append(section);
  }
  setText('#ide-hash216-output', JSON.stringify({ operation_root_hash216: snapshot.ingestion_operation_hash216, position_count: positions.length, positions }, null, 2));
}
export function openBottomTab(name) {
  $$('.ide-bottom-tabs button').forEach((button) => button.classList.toggle('active', button.dataset.bottomTab === name));
  $$('.ide-bottom-panel').forEach((panel) => panel.classList.toggle('active', panel.dataset.bottomPanel === name));
}
export function bind3d() {
  const viewport = $('#ide-3d-viewport'); const scene = $('#ide-3d-scene');
  const apply = () => { scene.style.transform = `rotateX(${state.scene.x}deg) rotateZ(${state.scene.z}deg) scale(${state.scene.scale})`; };
  viewport.onpointerdown = (event) => { state.scene.pointer = event.pointerId; state.scene.px = event.clientX; state.scene.py = event.clientY; viewport.setPointerCapture(event.pointerId); viewport.classList.add('dragging'); };
  viewport.onpointermove = (event) => { if (state.scene.pointer !== event.pointerId) return; state.scene.z += (event.clientX - state.scene.px) * .35; state.scene.x = Math.max(12, Math.min(82, state.scene.x - (event.clientY - state.scene.py) * .25)); state.scene.px = event.clientX; state.scene.py = event.clientY; apply(); };
  viewport.onpointerup = viewport.onpointercancel = (event) => { if (state.scene.pointer === event.pointerId) { state.scene.pointer = null; viewport.classList.remove('dragging'); } };
  viewport.onwheel = (event) => { event.preventDefault(); state.scene.scale = Math.max(.45, Math.min(1.35, state.scene.scale - event.deltaY * .001)); apply(); };
  apply();
}
