const API = '/api/runtime/storybook-reel';
const state = { catalog: null, presets: null, resolved: null };

const $ = (selector) => document.querySelector(selector);
const field = (id) => document.querySelector(`#${id}`);

function unwrap(value) {
  return value?.payload && typeof value.payload === 'object' ? value.payload : value;
}

async function jsonRequest(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { Accept: 'application/json', ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...(options.headers || {}) },
  });
  const payload = await response.json();
  if (!response.ok) {
    const detail = payload.detail || payload;
    throw new Error([detail.reason, detail.remediation].filter(Boolean).join('\n') || JSON.stringify(detail));
  }
  return unwrap(payload);
}

function installStyles() {
  const style = document.createElement('style');
  style.textContent = `
    .pass203-render{border:1px solid #4a3b66;border-radius:12px;background:linear-gradient(145deg,#171321,#101826);padding:12px;margin-top:12px;display:grid;gap:10px}
    .pass203-render h3{margin:0;font-size:14px}.pass203-render p{margin:2px 0;color:#b8abc7;font-size:10px;line-height:1.45}.pass203-render-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.pass203-render label{display:grid;gap:4px;font-size:9px;color:#cabddd}.pass203-render input,.pass203-render select{width:100%;box-sizing:border-box;border:1px solid #544664;border-radius:7px;padding:7px;background:#0c1019;color:#f6eefc}.pass203-native{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:5px}.pass203-native label{display:flex;align-items:center;gap:7px;padding:6px;border-radius:7px;background:#0b111a}.pass203-native input{width:auto}.pass203-catalog{white-space:pre-wrap;max-height:150px;overflow:auto;background:#090c12;border-radius:8px;padding:8px;font:8px/1.45 ui-monospace,monospace;color:#b8d8ec}.pass203-actions{display:flex;gap:7px;flex-wrap:wrap}.pass203-actions button{width:auto;padding:8px 10px}.pass203-profile{color:#8ff0d0;font-weight:800}@media(max-width:700px){.pass203-render-grid,.pass203-native{grid-template-columns:1fr}}
  `;
  document.head.append(style);
}

const renderFields = [
  ['output_width', 'Output width', 'number'],
  ['output_height', 'Output height', 'number'],
  ['fit_mode', 'Composition', 'select'],
  ['scale_filter', 'Scale filter', 'select'],
  ['background_blur', 'Background blur', 'number'],
  ['background_color', 'Background color', 'color'],
  ['foreground_width', 'Foreground width', 'number'],
  ['foreground_height', 'Foreground height', 'number'],
  ['contrast', 'Contrast', 'number'],
  ['saturation', 'Saturation', 'number'],
  ['brightness', 'Brightness', 'number'],
  ['gamma', 'Gamma', 'number'],
  ['sharpen_luma', 'Luma sharpen', 'number'],
  ['vignette_strength', 'Vignette', 'number'],
  ['video_preset', 'Encoder preset', 'select'],
  ['crf', 'Video CRF', 'number'],
  ['pixel_format', 'Pixel format', 'select'],
  ['audio_bitrate', 'Audio bitrate', 'text'],
];
const textureLayers = ['field', 'midground', 'materials', 'semantic', 'player'];
const spriteLayers = ['atmosphere', 'phase', 'glows', 'vignette', 'hud'];

function optionValues(name) {
  const options = state.catalog?.render_parameters?.[name]?.enum
    || state.catalog?.enums?.[name]
    || state.catalog?.[`${name}s`]
    || [];
  return Array.isArray(options) ? options : Object.keys(options || {});
}

function createControl(name, label, type) {
  const wrapper = document.createElement('label');
  wrapper.textContent = label;
  let input;
  if (type === 'select') {
    input = document.createElement('select');
    for (const value of optionValues(name)) input.add(new Option(String(value), String(value)));
  } else {
    input = document.createElement('input');
    input.type = type;
    if (type === 'number') input.step = ['contrast','saturation','brightness','gamma','sharpen_luma','vignette_strength'].includes(name) ? '0.01' : '1';
  }
  input.id = `pass203-${name.replaceAll('_','-')}`;
  input.dataset.renderName = name;
  wrapper.append(input);
  return wrapper;
}

function createLayer(name, group) {
  const wrapper = document.createElement('label');
  const input = document.createElement('input');
  input.type = 'checkbox';
  input.checked = true;
  input.dataset.layerName = name;
  input.dataset.layerGroup = group;
  wrapper.append(input, document.createTextNode(`${group === 'texture' ? 'Texture' : 'Sprite'} · ${name}`));
  return wrapper;
}

function mount() {
  const design = document.querySelector('.design-panel');
  if (!design || $('#pass203-high-fidelity-render')) return;
  const panel = document.createElement('section');
  panel.id = 'pass203-high-fidelity-render';
  panel.className = 'pass203-render';
  panel.innerHTML = `
    <div><h3>Pass 203 High-Fidelity Native Render Authority</h3><p>The 160×144 VM81 frame is an exact source layer, not the delivery ceiling. Production output uses a configurable high-resolution compositor while preserving frame and receipt identity.</p></div>
    <label>Quality profile<select id="pass203-quality-profile"></select><small id="pass203-profile-description" class="pass203-profile"></small></label>
    <div id="pass203-render-grid" class="pass203-render-grid"></div>
    <div><h3>Native shader and sprite layers</h3><p>Every governed texture and sprite-overlay bit is selectable through the API.</p></div>
    <div id="pass203-native-layers" class="pass203-native"></div>
    <div class="pass203-actions"><button id="pass203-resolve" type="button" class="secondary">Validate and resolve parameters</button><button id="pass203-show-catalog" type="button" class="secondary">Show complete parameter catalog</button></div>
    <pre id="pass203-catalog" class="pass203-catalog" hidden></pre>`;
  const generate = $('#generate');
  design.insertBefore(panel, generate || null);
  const grid = $('#pass203-render-grid');
  for (const definition of renderFields) grid.append(createControl(...definition));
  const layers = $('#pass203-native-layers');
  for (const name of textureLayers) layers.append(createLayer(name, 'texture'));
  for (const name of spriteLayers) layers.append(createLayer(name, 'sprite'));
  $('#pass203-resolve').onclick = resolve;
  $('#pass203-show-catalog').onclick = () => {
    const output = $('#pass203-catalog');
    output.hidden = !output.hidden;
    output.textContent = JSON.stringify(state.catalog, null, 2);
  };
  $('#pass203-quality-profile').onchange = applyProfile;
}

function currentParameters() {
  const render = {};
  document.querySelectorAll('[data-render-name]').forEach((input) => {
    const name = input.dataset.renderName;
    if (!input.value) return;
    render[name] = input.type === 'number' ? Number(input.value) : input.value;
  });
  const native_layers = { texture: {}, sprite: {} };
  document.querySelectorAll('[data-layer-name]').forEach((input) => {
    native_layers[input.dataset.layerGroup][input.dataset.layerName] = input.checked;
  });
  return {
    quality_profile: $('#pass203-quality-profile')?.value || 'production_vertical_1080',
    render,
    native_layers,
  };
}

function setRender(values = {}) {
  for (const [name, value] of Object.entries(values)) {
    const input = $(`#pass203-${name.replaceAll('_','-')}`);
    if (input && value !== undefined && value !== null) input.value = value;
  }
}

function applyProfile() {
  const id = $('#pass203-quality-profile').value;
  const profile = state.presets?.quality_profiles?.[id]
    || state.presets?.profiles?.[id]
    || state.catalog?.quality_profiles?.[id]
    || {};
  setRender(profile);
  $('#pass203-profile-description').textContent = profile.description || profile.label || id;
}

async function resolve() {
  const source = currentParameters();
  const payload = {
    text: $('#story')?.value || '',
    title: $('#title')?.value || 'HHS STORYBOOK',
    template_id: $('#template')?.value || undefined,
    style: window.HHSStorybookStudioState?.style || {},
    ...source,
  };
  try {
    state.resolved = await jsonRequest(`${API}/resolve`, { method: 'POST', body: JSON.stringify(payload) });
    $('#pass203-catalog').hidden = false;
    $('#pass203-catalog').textContent = JSON.stringify(state.resolved, null, 2);
  } catch (error) {
    $('#pass203-catalog').hidden = false;
    $('#pass203-catalog').textContent = error.message;
  }
}

async function load() {
  installStyles();
  mount();
  try {
    [state.catalog, state.presets] = await Promise.all([
      jsonRequest(`${API}/parameters`),
      jsonRequest(`${API}/presets`),
    ]);
    const select = $('#pass203-quality-profile');
    const profiles = state.presets?.quality_profiles || state.presets?.profiles || state.catalog?.quality_profiles || {};
    for (const [id, profile] of Object.entries(profiles)) select.add(new Option(profile.label || id, id));
    select.value = profiles.production_vertical_1080 ? 'production_vertical_1080' : Object.keys(profiles)[0] || '';
    for (const [name] of renderFields) {
      const input = $(`#pass203-${name.replaceAll('_','-')}`);
      if (input?.tagName === 'SELECT' && !input.options.length) {
        const fallback = name === 'fit_mode' ? ['cinematic_blur','soft_storybook','full_bleed_crop','contain','native_integer']
          : name === 'scale_filter' ? ['lanczos','spline','bicubic','bilinear','neighbor']
          : name === 'video_preset' ? ['veryslow','slower','slow','medium','fast']
          : name === 'pixel_format' ? ['yuv420p','yuv422p','yuv444p'] : [];
        for (const value of fallback) input.add(new Option(value, value));
      }
    }
    applyProfile();
  } catch (error) {
    $('#pass203-catalog').hidden = false;
    $('#pass203-catalog').textContent = `Parameter catalog unavailable: ${error.message}`;
  }
}

// Preserve the existing studio workflow while injecting the full governed
// render request into its native generation call.
const originalFetch = window.fetch.bind(window);
window.fetch = async function pass203StorybookFetch(input, init = {}) {
  const raw = typeof input === 'string' ? input : input?.url || '';
  let url;
  try { url = new URL(raw, window.location.href); } catch { return originalFetch(input, init); }
  if (url.origin === window.location.origin && url.pathname === `${API}/generate` && String(init.method || 'GET').toUpperCase() === 'POST') {
    try {
      const body = JSON.parse(init.body || '{}');
      const parameters = currentParameters();
      init = { ...init, body: JSON.stringify({ ...body, ...parameters }) };
    } catch { /* existing request validation will report malformed JSON */ }
  }
  return originalFetch(input, init);
};

load();
window.HHSPass203HighFidelityRenderer = Object.freeze({
  schema: 'HHS_PASS_203_HIGH_FIDELITY_RENDER_STUDIO_V1',
  parameters: currentParameters,
  resolve,
  frontend_is_authority: false,
});
