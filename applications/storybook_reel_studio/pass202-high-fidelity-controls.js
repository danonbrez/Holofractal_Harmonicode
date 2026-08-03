const PASS202_API = '/api/runtime/storybook-reel';

const pass202State = {
  catalog: null,
  presets: [],
  qualityProfile: 'production_vertical_1080',
  render: {},
  nativeLayers: {
    texture: {field:true,midground:true,materials:true,semantic:true,player:true},
    sprite: {atmosphere:true,phase:true,glows:true,vignette:true,hud:true},
  },
};

const originalFetch = window.fetch.bind(window);

function isGenerateRequest(input, init) {
  const raw = typeof input === 'string' ? input : input?.url || '';
  const url = new URL(raw, window.location.href);
  return url.origin === window.location.origin
    && url.pathname === `${PASS202_API}/generate`
    && String(init?.method || 'GET').toUpperCase() === 'POST';
}

window.fetch = async function pass202Fetch(input, init = {}) {
  if (!isGenerateRequest(input, init) || typeof init.body !== 'string') {
    return originalFetch(input, init);
  }
  const payload = JSON.parse(init.body);
  payload.quality_profile = pass202State.qualityProfile;
  payload.render = {...pass202State.render};
  payload.native_layers = JSON.parse(JSON.stringify(pass202State.nativeLayers));
  return originalFetch(input, {...init, body: JSON.stringify(payload)});
};

function element(tag, attributes = {}, text = '') {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attributes)) {
    if (key === 'className') node.className = value;
    else if (key === 'checked') node.checked = Boolean(value);
    else node.setAttribute(key, value);
  }
  if (text) node.textContent = text;
  return node;
}

function fieldLabel(label, input, note = '') {
  const wrapper = element('label', {className:'pass202-field'});
  wrapper.append(element('span', {}, label), input);
  if (note) wrapper.append(element('small', {}, note));
  return wrapper;
}

function setRender(name, value) {
  pass202State.render[name] = value;
  void resolveProjection();
}

function numericInput(name, value, min, max, step = '1') {
  const input = element('input', {type:'number', value:String(value), min:String(min), max:String(max), step:String(step)});
  input.addEventListener('input', () => setRender(name, step === '1' ? Number(input.value) : input.value));
  return input;
}

function rangeInput(name, value, min, max, step = '1') {
  const row = element('div', {className:'pass202-range'});
  const input = element('input', {type:'range', value:String(value), min:String(min), max:String(max), step:String(step)});
  const output = element('output', {}, String(value));
  input.addEventListener('input', () => {
    output.value = input.value;
    setRender(name, step === '1' ? Number(input.value) : input.value);
  });
  row.append(input, output);
  return row;
}

function selectInput(name, value, values) {
  const select = element('select');
  for (const optionValue of values) {
    const option = element('option', {value:optionValue}, optionValue.replaceAll('_',' '));
    option.selected = optionValue === value;
    select.append(option);
  }
  select.addEventListener('change', () => setRender(name, select.value));
  return select;
}

function colorInput(name, value) {
  const input = element('input', {type:'color', value});
  input.addEventListener('input', () => setRender(name, input.value));
  return input;
}

function layerToggle(group, name, enabled) {
  const label = element('label', {className:'pass202-toggle'});
  const input = element('input', {type:'checkbox', checked:enabled});
  input.addEventListener('change', () => {
    pass202State.nativeLayers[group][name] = input.checked;
    void resolveProjection();
  });
  label.append(input, element('span', {}, name.replaceAll('_',' ')));
  return label;
}

function applyPreset(presetId) {
  const preset = pass202State.presets.find((entry) => entry.id === presetId);
  if (!preset) return;
  pass202State.qualityProfile = presetId;
  pass202State.render = Object.fromEntries(
    Object.entries(preset).filter(([key]) => !['id','label','description'].includes(key)),
  );
  renderPass202Controls();
  void resolveProjection();
}

async function resolveProjection() {
  const output = document.querySelector('#pass202-resolution');
  if (!output) return;
  try {
    const response = await originalFetch(`${PASS202_API}/parameters/resolve`, {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        text:document.querySelector('#story')?.value || '',
        template_id:document.querySelector('#template')?.value || undefined,
        quality_profile:pass202State.qualityProfile,
        render:pass202State.render,
        native_layers:pass202State.nativeLayers,
      }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail?.reason || 'Parameter resolution failed');
    output.textContent = [
      `${payload.render.output_width}×${payload.render.output_height}`,
      payload.quality_profile,
      payload.render.fit_mode,
      payload.render.scale_filter,
      `texture mask ${payload.native_layers.texture_flags}`,
      `sprite mask ${payload.native_layers.sprite_overlay_flags}`,
      `Hash72 ${payload.resolution_hash72}`,
    ].join(' · ');
    output.dataset.ok = 'true';
  } catch (error) {
    output.textContent = error.message;
    output.dataset.ok = 'false';
  }
}

function renderPass202Controls() {
  const root = document.querySelector('#pass202-controls');
  if (!root) return;
  root.replaceChildren();

  const presetSelect = element('select');
  for (const preset of pass202State.presets) {
    const option = element('option', {value:preset.id}, preset.label);
    option.selected = preset.id === pass202State.qualityProfile;
    presetSelect.append(option);
  }
  presetSelect.addEventListener('change', () => applyPreset(presetSelect.value));
  root.append(fieldLabel('Quality profile', presetSelect, 'Production profiles use a derived full-frame background and high-quality native foreground composition.'));

  const dimensions = element('div', {className:'pass202-grid'});
  dimensions.append(
    fieldLabel('Output width', numericInput('output_width', pass202State.render.output_width, 160, 2160, '2')),
    fieldLabel('Output height', numericInput('output_height', pass202State.render.output_height, 144, 3840, '2')),
    fieldLabel('Foreground width', numericInput('foreground_width', pass202State.render.foreground_width, 160, 2160, '2')),
    fieldLabel('Foreground height', numericInput('foreground_height', pass202State.render.foreground_height, 144, 3840, '2')),
    fieldLabel('Fit mode', selectInput('fit_mode', pass202State.render.fit_mode, ['cinematic_blur','soft_storybook','full_bleed_crop','contain','native_integer'])),
    fieldLabel('Scale filter', selectInput('scale_filter', pass202State.render.scale_filter, ['lanczos','spline','bicubic','bilinear','neighbor'])),
  );
  root.append(dimensions);

  const treatment = element('details', {open:''});
  treatment.append(element('summary', {}, 'Compositing and color treatment'));
  const treatmentGrid = element('div', {className:'pass202-grid'});
  treatmentGrid.append(
    fieldLabel('Background blur', rangeInput('background_blur', pass202State.render.background_blur, 0, 80)),
    fieldLabel('Background color', colorInput('background_color', pass202State.render.background_color)),
    fieldLabel('Contrast', rangeInput('contrast', pass202State.render.contrast, .5, 2, '.01')),
    fieldLabel('Saturation', rangeInput('saturation', pass202State.render.saturation, 0, 3, '.01')),
    fieldLabel('Brightness', rangeInput('brightness', pass202State.render.brightness, -1, 1, '.01')),
    fieldLabel('Gamma', rangeInput('gamma', pass202State.render.gamma, .1, 10, '.01')),
    fieldLabel('Sharpen', rangeInput('sharpen_luma', pass202State.render.sharpen_luma, 0, 2, '.01')),
    fieldLabel('Vignette', rangeInput('vignette_strength', pass202State.render.vignette_strength, 0, 1, '.01')),
  );
  treatment.append(treatmentGrid);
  root.append(treatment);

  const layers = element('details', {open:''});
  layers.append(element('summary', {}, 'Native shader, texture, and sprite-map layers'));
  const texture = element('fieldset');
  texture.append(element('legend', {}, 'Texture shader layers'));
  for (const [name, enabled] of Object.entries(pass202State.nativeLayers.texture)) texture.append(layerToggle('texture', name, enabled));
  const sprite = element('fieldset');
  sprite.append(element('legend', {}, 'Sprite overlay layers'));
  for (const [name, enabled] of Object.entries(pass202State.nativeLayers.sprite)) sprite.append(layerToggle('sprite', name, enabled));
  layers.append(texture, sprite);
  root.append(layers);

  const codec = element('details');
  codec.append(element('summary', {}, 'Codec and transport'));
  const codecGrid = element('div', {className:'pass202-grid'});
  codecGrid.append(
    fieldLabel('Video codec', selectInput('video_codec', pass202State.render.video_codec, ['libx264'])),
    fieldLabel('Encoder preset', selectInput('video_preset', pass202State.render.video_preset, ['veryslow','slower','slow','medium','fast'])),
    fieldLabel('CRF', numericInput('crf', pass202State.render.crf, 0, 51)),
    fieldLabel('Pixel format', selectInput('pixel_format', pass202State.render.pixel_format, ['yuv420p','yuv422p','yuv444p'])),
    fieldLabel('Audio bitrate', selectInput('audio_bitrate', pass202State.render.audio_bitrate, ['128k','160k','192k','224k','256k','320k'])),
  );
  codec.append(codecGrid);
  root.append(codec);

  root.append(element('p', {id:'pass202-resolution', className:'pass202-resolution'}, 'Resolving exact render parameters…'));
}

function installStyles() {
  const style = element('style');
  style.textContent = `
    .pass202-authority{margin-top:16px;padding:14px;border:1px solid rgba(233,177,94,.34);border-radius:12px;background:rgba(15,10,14,.56)}
    .pass202-authority>header{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:12px}
    .pass202-authority h3{margin:0;font-size:15px}.pass202-authority header p{margin:4px 0 0;font-size:12px;opacity:.72}
    #pass202-controls{display:grid;gap:12px}.pass202-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
    .pass202-field{display:grid;gap:5px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.04em}
    .pass202-field small{font-weight:400;text-transform:none;letter-spacing:0;opacity:.68}
    .pass202-field input,.pass202-field select{width:100%;box-sizing:border-box}
    .pass202-range{display:grid;grid-template-columns:1fr 48px;align-items:center;gap:8px}.pass202-range output{text-align:right;font-family:ui-monospace,monospace}
    .pass202-authority details{border-top:1px solid rgba(255,255,255,.09);padding-top:8px}.pass202-authority summary{cursor:pointer;font-weight:800;font-size:12px;margin-bottom:9px}
    .pass202-authority fieldset{display:flex;flex-wrap:wrap;gap:8px;border:1px solid rgba(255,255,255,.08);border-radius:8px;margin:8px 0;padding:9px}
    .pass202-authority legend{font-size:11px;font-weight:800;padding:0 5px}.pass202-toggle{display:inline-flex;align-items:center;gap:6px;font-size:11px;text-transform:capitalize}
    .pass202-resolution{margin:0;padding:9px;border-radius:7px;background:rgba(0,0,0,.28);font:10px/1.5 ui-monospace,monospace;overflow-wrap:anywhere}
    .pass202-resolution[data-ok="false"]{outline:1px solid #d46868}.pass202-candidates{margin-top:8px;font-size:11px;line-height:1.5;opacity:.8}
    @media(max-width:720px){.pass202-grid{grid-template-columns:1fr}}
  `;
  document.head.append(style);
}

async function loadPass202() {
  installStyles();
  const design = document.querySelector('.design-panel');
  const generateButton = document.querySelector('#generate');
  if (!design || !generateButton) return;
  const authority = element('section', {className:'pass202-authority'});
  const header = element('header');
  const copy = element('div');
  copy.append(
    element('h3', {}, 'Pass 202 · High-fidelity native render authority'),
    element('p', {}, 'Every native shader layer and presentation parameter is explicit. The logical VM81 frame remains exact evidence, not the output-quality ceiling.'),
  );
  const docs = element('a', {href:'/api/runtime/storybook-reel/parameters', target:'_blank', rel:'noreferrer'}, 'Parameter catalog');
  header.append(copy, docs);
  authority.append(header, element('div', {id:'pass202-controls'}));
  design.insertBefore(authority, generateButton);

  try {
    const [catalogResponse, presetsResponse] = await Promise.all([
      originalFetch(`${PASS202_API}/parameters`),
      originalFetch(`${PASS202_API}/presets`),
    ]);
    const catalog = await catalogResponse.json();
    const presets = await presetsResponse.json();
    if (!catalogResponse.ok || !presetsResponse.ok) throw new Error('Pass 202 parameter authority unavailable');
    pass202State.catalog = catalog;
    pass202State.presets = presets.presets || [];
    applyPreset(presets.default_profile || 'production_vertical_1080');
  } catch (error) {
    authority.append(element('p', {className:'error'}, error.message));
  }

  const story = document.querySelector('#story');
  story?.addEventListener('input', () => void resolveProjection());
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', loadPass202, {once:true});
} else {
  void loadPass202();
}

window.HHSPass202HighFidelityRender = Object.freeze({
  schema:'HHS_PASS_202_HIGH_FIDELITY_RENDER_CONTROLS_V1',
  state:pass202State,
  resolve:resolveProjection,
  all_native_layers_user_selectable:true,
  fixed_neighbor_black_pad_default:false,
  frontend_is_authority:false,
});
