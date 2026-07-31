const API = '/api/runtime/storybook-reel';
const $ = (selector) => document.querySelector(selector);
const canvas = $('#preview');
const context = canvas.getContext('2d');

const COLOR_WHEEL = [
  '#e64150','#eb5e37','#ec8430','#e5b32d','#b5c42f','#4bae5c',
  '#2ca097','#3680cb','#525cbe','#8952ba','#be479f','#da4275',
];
const HARMONIES = [
  [0,4,6,7],[0,3,6,7],[0,5,6,7],[0,3,6,9],[0,4,6,10],[0,3,6,10],
  [0,1,6,11],[0,2,6,9],[0,4,6,11],[0,5,6,10],[0,2,6,8],[0,1,6,7],
];
const CONTROL_SECTIONS = [
  {
    title: 'Typography and 3D motion',
    fields: [
      ['font_face','Font style','select',{0:'Classic',1:'Bold',2:'Serif',3:'Wide',4:'Shadow'}],
      ['font_effect','Animation','select',{0:'Flat',1:'Extruded',2:'Parallax',3:'Orbital',4:'Phase wave'}],
      ['font_scale','Font scale','range',[1,4]],
      ['letter_spacing','Letter spacing','range',[0,8]],
      ['effect_depth','3D depth','range',[0,12]],
      ['effect_speed','Motion speed','range',[1,12]],
      ['effect_amplitude','Motion amount','range',[0,24]],
      ['panel_opacity','Panel opacity','range',[0,255]],
    ],
  },
  {
    title: 'Reciprocal twelve-tone color harmony',
    fields: [
      ['automatic_palette','Automatic compatible x/y/z/w palette','checkbox'],
      ['manual_x','x · tonic','color'],
      ['manual_y','y · harmony','color'],
      ['manual_z','z · reciprocal','color'],
      ['manual_w','w · cadence','color'],
      ['phase_origin','Phase origin','number',[0,71]],
      ['phase_scene_stride','Scene stride','number',[1,71]],
    ],
  },
  {
    title: 'Placement and caption density',
    fields: [
      ['title_x','Title X','range',[0,150]],
      ['title_y','Title Y','range',[0,136]],
      ['caption_x','Caption X','range',[0,150]],
      ['caption_y','Caption Y','range',[0,136]],
      ['title_max_chars','Title characters','range',[8,40]],
      ['caption_chars_per_line','Characters per line','range',[10,40]],
      ['caption_lines','Caption lines','range',[1,4]],
    ],
  },
];

const state = {
  audioId: null,
  audioUrl: null,
  alignment: null,
  defaults: null,
  templates: [],
  templateId: null,
  templateLocked: false,
  style: {},
  previewSecond: 0,
  playing: false,
  motionStarted: performance.now(),
  generationTimer: null,
};

function hashText(text) {
  let value = 2166136261;
  for (let index = 0; index < text.length; index += 1) {
    value ^= text.charCodeAt(index);
    value = Math.imul(value, 16777619);
  }
  return value >>> 0;
}

function hexToRgb(hex) {
  const value = String(hex || '#000000').replace('#','');
  return {
    r: parseInt(value.slice(0,2),16) || 0,
    g: parseInt(value.slice(2,4),16) || 0,
    b: parseInt(value.slice(4,6),16) || 0,
  };
}

function mixHex(first, second, weight) {
  const a = hexToRgb(first);
  const b = hexToRgb(second);
  const p = Math.max(0, Math.min(100, weight)) / 100;
  const channel = (x,y) => Math.round(x * (1-p) + y * p).toString(16).padStart(2,'0');
  return `#${channel(a.r,b.r)}${channel(a.g,b.g)}${channel(a.b,b.b)}`;
}

function automaticPalette(sceneIndex = 0) {
  const source = $('#story').value || 'HHS STORYBOOK';
  const seed = (hashText(source) + Math.imul(sceneIndex + 1, 2654435761)) >>> 0;
  const tonic = (seed + sceneIndex * 5) % 12;
  const harmonyIndex = ((seed >>> 11) + sceneIndex * 7) % HARMONIES.length;
  const harmony = HARMONIES[harmonyIndex];
  const tones = [tonic,(tonic+harmony[1])%12,(tonic+6)%12,(tonic+harmony[3])%12];
  let colors = tones.map((tone) => COLOR_WHEEL[tone]);
  if ((seed >>> 29) & 1) colors = [colors[0],mixHex(colors[1],colors[2],24+sceneIndex%25),colors[2],mixHex(colors[3],colors[0],18+sceneIndex%31)];
  return {
    chromatic_tonic: tonic,
    harmony_class: harmonyIndex,
    phase_planes: {x:tones[0]*6,y:tones[1]*6,z:(tones[0]*6+36)%72,w:tones[3]*6},
    colors: {x:colors[0],y:colors[1],z:colors[2],w:colors[3]},
  };
}

function currentPalette(sceneIndex = 0) {
  if ($('#automatic-palette')?.checked !== false) return automaticPalette(sceneIndex);
  const origin = Number($('#phase-origin')?.value || 0) % 72;
  return {
    chromatic_tonic: Math.floor(origin / 6),
    harmony_class: -1,
    phase_planes: {x:origin,y:(origin+24)%72,z:(origin+36)%72,w:(origin+42)%72},
    colors: {
      x: $('#manual-x')?.value || '#e64150',
      y: $('#manual-y')?.value || '#b5c42f',
      z: $('#manual-z')?.value || '#2ca097',
      w: $('#manual-w')?.value || '#3680cb',
    },
  };
}

function buildControls() {
  const root = $('#controls');
  root.replaceChildren();
  for (const section of CONTROL_SECTIONS) {
    const wrapper = document.createElement('section');
    wrapper.className = 'control-section';
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.innerHTML = `<span>${section.title}</span><span>⌄</span>`;
    const body = document.createElement('div');
    body.className = 'control-body';
    toggle.onclick = () => body.hidden = !body.hidden;
    wrapper.append(toggle, body);
    for (const [key,label,type,options] of section.fields) {
      const field = document.createElement('label');
      field.textContent = label;
      if (type === 'checkbox') field.className = 'wide switch';
      const input = document.createElement(type === 'select' ? 'select' : 'input');
      input.id = key.replaceAll('_','-');
      if (type === 'select') {
        for (const [value,name] of Object.entries(options)) input.add(new Option(name,value));
      } else {
        input.type = type;
        if (Array.isArray(options)) {
          input.min = options[0];
          input.max = options[1];
        }
        if (type === 'checkbox') input.checked = true;
      }
      input.addEventListener('input', () => {
        if (key === 'automatic_palette') updatePaletteControls();
        readStyle();
        renderPreview();
      });
      field.prepend(input);
      body.append(field);
    }
    root.append(wrapper);
  }
}

function styleElement(key) {
  return $(`#${key.replaceAll('_','-')}`);
}

function setStyleValue(key, value) {
  const input = styleElement(key);
  if (!input) return;
  if (input.type === 'checkbox') input.checked = Boolean(value);
  else input.value = value;
}

function readStyle() {
  const style = {};
  for (const section of CONTROL_SECTIONS) {
    for (const [key,,type] of section.fields) {
      const input = styleElement(key);
      if (!input) continue;
      if (key === 'automatic_palette') continue;
      if (type === 'color') style[key] = input.value;
      else style[key] = Number(input.value);
    }
  }
  style.palette_mode = $('#automatic-palette').checked ? 0 : 2;
  style.phase_origin = $('#automatic-palette').checked ? 4294967295 : Number($('#phase-origin').value || 0);
  state.style = style;
  return style;
}

function updatePaletteControls() {
  const automatic = $('#automatic-palette').checked;
  for (const key of ['manual-x','manual-y','manual-z','manual-w','phase-origin']) $( `#${key}` ).disabled = automatic;
}

function applyPalette(palette) {
  for (const plane of ['x','y','z','w']) {
    const input = $(`#manual-${plane}`);
    if (input) input.value = palette.colors[plane];
  }
  if ($('#phase-origin')) $('#phase-origin').value = palette.phase_planes.x;
  renderPlanes(palette);
}

function renderPlanes(palette) {
  const root = $('#planes');
  root.innerHTML = '';
  for (const plane of ['x','y','z','w']) {
    const card = document.createElement('div');
    card.className = 'plane-card';
    card.style.setProperty('--plane',palette.colors[plane]);
    card.innerHTML = `<b>${plane}</b><span>phase ${palette.phase_planes[plane]}</span><small>${palette.colors[plane]}</small>`;
    root.append(card);
  }
}

function applyTemplate(templateId, {lock = true} = {}) {
  const template = state.templates.find((item) => item.id === templateId);
  if (!template) return;
  state.templateId = templateId;
  state.templateLocked = lock;
  $('#template').value = templateId;
  $('#template-description').textContent = template.description || '';
  for (const [key,value] of Object.entries(template)) {
    if (styleElement(key)) setStyleValue(key,value);
  }
  $('#automatic-palette').checked = Number(template.palette_mode ?? 0) !== 2;
  updatePaletteControls();
  if ($('#automatic-palette').checked) applyPalette(automaticPalette(Math.floor(state.previewSecond / 6)));
  document.querySelectorAll('.template-card').forEach((card) => card.classList.toggle('active',card.dataset.template === templateId));
  readStyle();
  renderPreview();
}

function renderTemplateGallery() {
  const select = $('#template');
  const gallery = $('#template-gallery');
  select.replaceChildren();
  gallery.replaceChildren();
  for (const template of state.templates) {
    select.add(new Option(template.label,template.id));
    const card = document.createElement('button');
    card.type = 'button';
    card.className = 'template-card';
    card.dataset.template = template.id;
    card.innerHTML = `<strong>${template.label}</strong><small>${template.description}</small>`;
    card.onclick = () => applyTemplate(template.id);
    gallery.append(card);
  }
  select.onchange = () => applyTemplate(select.value);
}

async function requestDefaults({forceTemplate = false} = {}) {
  const text = $('#story').value;
  try {
    const response = await fetch(`${API}/defaults`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});
    if (!response.ok) throw new Error(await response.text());
    const payload = await response.json();
    state.defaults = payload;
    state.templates = payload.available_templates || state.templates;
    if (!$('#template').options.length && state.templates.length) renderTemplateGallery();
    if (forceTemplate || !state.templateLocked) applyTemplate(payload.template_id,{lock:false});
    if ($('#automatic-palette').checked) applyPalette(payload.palette || automaticPalette());
    $('#default-reason').textContent = `Context: ${payload.reason === 'keyword_context' ? 'story theme selected' : 'stable story-hash selection'} · chromatic tonic ${payload.palette?.chromatic_tonic ?? 0}`;
  } catch (error) {
    $('#default-reason').textContent = `Contextual defaults unavailable: ${error.message}`;
    if (!state.templates.length) {
      state.templates = [{id:'reciprocal_storybook',label:'Reciprocal Storybook',description:'Native reciprocal storybook defaults',font_face:4,font_effect:1,font_scale:1,letter_spacing:1,effect_depth:3,effect_speed:1,effect_amplitude:3,palette_mode:0,phase_origin:4294967295,phase_scene_stride:6,title_x:12,title_y:12,caption_x:12,caption_y:106,title_max_chars:20,caption_chars_per_line:22,caption_lines:2,panel_opacity:214}];
      renderTemplateGallery();
      applyTemplate('reciprocal_storybook',{lock:false});
    }
  }
}

function storySegments() {
  const text = $('#story').value.trim();
  if (!text) return ['Paste matching narration text'];
  const sentences = text.match(/[^.!?\n]+[.!?]?/g)?.map((value) => value.trim()).filter(Boolean) || [text];
  const parts = [];
  for (const sentence of sentences) {
    if (sentence.length <= 72) parts.push(sentence);
    else for (let offset = 0; offset < sentence.length; offset += 64) parts.push(sentence.slice(offset,offset+64));
  }
  return parts;
}

function wrapText(text, max) {
  const words = text.split(/\s+/).filter(Boolean);
  const lines = [];
  let line = '';
  for (const word of words) {
    if (`${line} ${word}`.trim().length > max && line) { lines.push(line); line = word; }
    else line = `${line} ${word}`.trim();
  }
  if (line) lines.push(line);
  return lines;
}

function drawPixelWorld(palette, second) {
  const {x,y,z,w} = palette.colors;
  const gradient = context.createLinearGradient(0,0,540,960);
  gradient.addColorStop(0,mixHex(z,'#08070b',58));
  gradient.addColorStop(.45,mixHex(x,'#120b11',62));
  gradient.addColorStop(1,mixHex(w,'#07070a',70));
  context.fillStyle = gradient;
  context.fillRect(0,0,540,960);
  const drift = Math.sin(second * .35) * 42;
  context.globalAlpha = .28;
  context.fillStyle = y;
  for (let index = 0; index < 18; index += 1) {
    const px = ((index * 71 + second * 13) % 650) - 55;
    const py = 120 + (index * 47) % 520;
    context.fillRect(px,py,8+(index%3)*4,8+(index%4)*3);
  }
  context.globalAlpha = .38;
  context.fillStyle = x;
  context.beginPath();context.arc(110+drift,300,78,0,Math.PI*2);context.fill();
  context.fillStyle = z;context.beginPath();context.arc(405-drift*.6,390,96,0,Math.PI*2);context.fill();
  context.fillStyle = w;context.beginPath();context.arc(270+drift*.25,520,64,0,Math.PI*2);context.fill();
  context.globalAlpha = 1;
  context.fillStyle = mixHex(z,'#000000',50);
  context.fillRect(0,690,540,270);
  context.fillStyle = mixHex(y,'#20150d',48);
  for (let xPos = -30; xPos < 570; xPos += 46) {
    const height = 34 + ((xPos / 46 + Math.floor(second)) % 4) * 12;
    context.fillRect(xPos,690-height,42,height);
  }
  const playerX = 80 + ((second * 47) % 390);
  const bounce = Math.abs(Math.sin(second * 2.2)) * 34;
  context.fillStyle = w;context.fillRect(playerX,640-bounce,34,48);
  context.fillStyle = y;context.fillRect(playerX+8,632-bounce,18,14);
  context.fillStyle = '#100b0b';context.fillRect(playerX+21,638-bounce,5,5);
}

function drawTextEffect(text,x,y,palette,settings,second,{title=false}={}) {
  const scale = Number(settings.font_scale || 1);
  const size = (title ? 25 : 19) + scale * 5;
  const faces = ['ui-sans-serif','ui-sans-serif','Georgia','Arial Black','ui-sans-serif'];
  context.font = `${Number(settings.font_face)===1 ? '800' : '700'} ${size}px ${faces[Number(settings.font_face)] || faces[0]}`;
  context.textBaseline = 'top';
  context.textAlign = 'left';
  const effect = Number(settings.font_effect || 0);
  const amplitude = Number(settings.effect_amplitude || 0) * 1.5;
  const phase = second * Number(settings.effect_speed || 1) * .7;
  let dx = 0,dy = 0;
  if (effect === 2) {dx=Math.sin(phase)*amplitude;dy=Math.cos(phase*.7)*amplitude*.4;}
  if (effect === 3) {dx=Math.sin(phase)*amplitude;dy=Math.cos(phase)*amplitude;}
  if (effect === 4) dy=Math.sin(phase + x*.02)*amplitude;
  const depth = Math.min(18,Number(settings.effect_depth || 0)*2);
  for (let layer = depth; layer > 0; layer -= 1) {
    context.fillStyle = mixHex(palette.colors.z,palette.colors.w,Math.round(layer/depth*70));
    context.globalAlpha = .72;
    context.fillText(text,x+dx+layer,y+dy+layer);
  }
  context.globalAlpha = 1;
  if (Number(settings.font_face) === 4) {
    context.fillStyle = 'rgba(0,0,0,.72)';context.fillText(text,x+dx+4,y+dy+5);
  }
  context.fillStyle = palette.colors.y;
  context.fillText(text,x+dx,y+dy);
  if (Number(settings.font_face) === 2) {
    const width = context.measureText(text).width;
    context.fillStyle = palette.colors.w;context.fillRect(x+dx,y+dy-2,width,2);context.fillRect(x+dx,y+dy+size+2,width,2);
  }
}

function renderPreview() {
  const settings = readStyle();
  const second = state.previewSecond;
  const scene = Math.floor(second / 6) % 15;
  const palette = currentPalette(scene);
  renderPlanes(palette);
  drawPixelWorld(palette,second);
  const panelAlpha = Math.max(0,Math.min(255,Number(settings.panel_opacity || 214))) / 255;
  context.fillStyle = `rgba(12,8,10,${panelAlpha*.86})`;
  context.fillRect(28,42,484,95);
  context.fillRect(28,730,484,154);
  context.strokeStyle = palette.colors.x;context.lineWidth=5;context.strokeRect(18,18,504,924);
  context.strokeStyle = palette.colors.z;context.lineWidth=2;context.strokeRect(26,26,488,908);
  const nativeScale = 540/160;
  const titleX = Math.min(455,Number(settings.title_x || 12)*nativeScale);
  const titleY = Math.min(850,Number(settings.title_y || 12)*nativeScale);
  const captionX = Math.min(455,Number(settings.caption_x || 12)*nativeScale);
  const captionY = Math.min(865,Number(settings.caption_y || 106)*nativeScale + 350);
  const title = $('#title').value.toUpperCase().slice(0,Number(settings.title_max_chars || 20));
  drawTextEffect(title,titleX,titleY,palette,settings,second,{title:true});
  const segments = storySegments();
  const caption = segments[Math.floor(second / 90 * segments.length) % segments.length];
  const lines = wrapText(caption.toUpperCase(),Number(settings.caption_chars_per_line || 22)).slice(0,Number(settings.caption_lines || 2));
  lines.forEach((line,index) => drawTextEffect(line,captionX,captionY+index*(42+Number(settings.effect_depth||0)),palette,settings,second));
  context.fillStyle = 'rgba(5,3,4,.75)';context.fillRect(45,910,450,8);
  context.fillStyle = palette.colors.w;context.fillRect(45,910,450*(second/90),8);
  context.font='700 16px ui-monospace,monospace';context.fillStyle=palette.colors.x;context.fillText(`PAGE ${String(scene+1).padStart(2,'0')} · VM81`,42,682);
  $('#time').textContent = `${formatTime(second)} / 01:30`;
  $('#scrub').value = Math.min(89,Math.floor(second));
}

function formatTime(value) {
  const seconds = Math.max(0,Math.min(90,Math.floor(value)));
  return `${String(Math.floor(seconds/60)).padStart(2,'0')}:${String(seconds%60).padStart(2,'0')}`;
}

function animationLoop(now) {
  if (state.playing && $('#audio-preview').paused) {
    state.previewSecond = ((now - state.motionStarted) / 1000) % 90;
    renderPreview();
  }
  requestAnimationFrame(animationLoop);
}

function updateReadiness() {
  $('#count').textContent = $('#story').value.length;
  $('#generate').disabled = !(state.audioId && $('#story').value.trim());
}

async function uploadAudio(file) {
  if (!file) return;
  hideError();
  $('#audio-card').hidden = false;
  $('#audio-name').textContent = file.name;
  $('#audio-meta').textContent = 'Uploading and inspecting narration…';
  if (state.audioUrl) URL.revokeObjectURL(state.audioUrl);
  state.audioUrl = URL.createObjectURL(file);
  $('#audio-preview').src = state.audioUrl;
  try {
    const response = await fetch(`${API}/audio`,{method:'POST',headers:{'Content-Type':file.type || 'application/octet-stream','X-HHS-Filename':file.name},body:file});
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail?.reason || payload.detail || 'Audio upload failed');
    state.audioId = payload.audio_id;
    $('#audio-meta').textContent = `${payload.duration_seconds}s · ${payload.codec_name || 'audio'} · upload verified`;
  } catch (error) {
    state.audioId = null;
    $('#audio-meta').textContent = 'Upload failed';
    showError(error.message);
  }
  updateReadiness();
}

function showError(message) { $('#error').hidden=false; $('#error').textContent=message; }
function hideError() { $('#error').hidden=true; $('#error').textContent=''; }

async function loadRuntime() {
  try {
    const response = await fetch(`${API}/status`);
    const payload = await response.json();
    if (!response.ok) throw new Error('Runtime unavailable');
    $('#runtime').textContent = payload.native_cli_ready ? 'Native reel ABI ready' : 'Native reel ABI builds on first generation';
    $('#runtime').className = 'ready';
    if (payload.templates?.length) { state.templates=payload.templates; renderTemplateGallery(); }
  } catch (error) {
    $('#runtime').textContent = error.message;
    $('#runtime').className = 'error';
  }
}

function generationStages() {
  const stages = ['Validating narration and timing…','Rendering native platformer and sprite frames…','Applying reciprocal color planes and 3D captions…','Normalizing narration to 90 seconds…','Encoding H.264/AAC vertical MP4…','Packaging source, media, receipts, and evidence…'];
  let index=0;
  $('#stage').textContent=stages[0];
  clearInterval(state.generationTimer);
  state.generationTimer=setInterval(()=>{$('#stage').textContent=stages[Math.min(++index,stages.length-1)];},12000);
}

async function generate() {
  hideError();
  $('#result').hidden=true;
  $('#progress').hidden=false;
  $('#generate').disabled=true;
  generationStages();
  const style = readStyle();
  const payload = {
    audio_id: state.audioId,
    text: $('#story').value,
    title: $('#title').value,
    template_id: state.templateId,
    style,
    alignment: state.alignment,
  };
  try {
    const response = await fetch(`${API}/generate`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail?.reason || result.detail || 'Reel generation failed');
    $('#result-video').src=result.video_url;
    $('#download').href=result.download_url;
    $('#result-meta').textContent=`${result.duration_seconds}s · ${result.width}×${result.height} · ${result.template_label} · ${result.timing_source}`;
    $('#receipt').textContent=result.receipt_hash72;
    $('#result').hidden=false;
    $('#result').scrollIntoView({behavior:'smooth',block:'nearest'});
  } catch (error) {
    showError(error.message);
  } finally {
    clearInterval(state.generationTimer);
    $('#progress').hidden=true;
    updateReadiness();
  }
}

function bindEvents() {
  let defaultsTimer;
  $('#story').addEventListener('input',()=>{
    updateReadiness();renderPreview();clearTimeout(defaultsTimer);defaultsTimer=setTimeout(()=>requestDefaults(),650);
  });
  $('#title').addEventListener('input',renderPreview);
  $('#defaults').onclick=()=>{state.templateLocked=false;requestDefaults({forceTemplate:true});};
  $('#choose-audio').onclick=(event)=>{event.stopPropagation();$('#audio-input').click();};
  $('#audio-drop').onclick=()=>$('#audio-input').click();
  $('#audio-input').onchange=()=>uploadAudio($('#audio-input').files[0]);
  $('#audio-drop').ondragover=(event)=>{event.preventDefault();$('#audio-drop').classList.add('drag');};
  $('#audio-drop').ondragleave=()=>$('#audio-drop').classList.remove('drag');
  $('#audio-drop').ondrop=(event)=>{event.preventDefault();$('#audio-drop').classList.remove('drag');uploadAudio(event.dataTransfer.files[0]);};
  $('#alignment-input').onchange=async()=>{
    const file=$('#alignment-input').files[0];
    if(!file)return;
    try{const parsed=JSON.parse(await file.text());state.alignment=parsed.alignment||parsed.normalized_alignment||parsed;$('#alignment-state').textContent=`Exact alignment loaded · ${file.name}`;}
    catch(error){state.alignment=null;$('#alignment-state').textContent='Invalid JSON; automatic duration fit retained';showError(error.message);}
  };
  $('#play').onclick=async()=>{
    state.playing=!state.playing;
    $('#play').textContent=state.playing?'❚❚ Pause':'▶ Motion';
    if(state.playing){state.motionStarted=performance.now()-state.previewSecond*1000;if($('#audio-preview').src){try{await $('#audio-preview').play();}catch{}}}
    else $('#audio-preview').pause();
  };
  $('#scrub').oninput=()=>{
    state.previewSecond=Number($('#scrub').value);state.motionStarted=performance.now()-state.previewSecond*1000;
    const audio=$('#audio-preview');if(audio.duration)audio.currentTime=state.previewSecond/90*audio.duration;renderPreview();
  };
  $('#audio-preview').ontimeupdate=()=>{
    const audio=$('#audio-preview');if(audio.duration){state.previewSecond=Math.min(90,audio.currentTime/audio.duration*90);renderPreview();}
  };
  $('#audio-preview').onpause=()=>{if(!state.playing)return;};
  $('#audio-preview').onended=()=>{state.playing=false;$('#play').textContent='▶ Motion';};
  $('#generate').onclick=generate;
}

buildControls();
bindEvents();
updatePaletteControls();
updateReadiness();
loadRuntime();
requestDefaults({forceTemplate:true});
renderPreview();
requestAnimationFrame(animationLoop);
