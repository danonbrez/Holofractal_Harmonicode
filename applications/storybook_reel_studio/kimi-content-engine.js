const API = '/api/runtime/content-engine/kimi-k3';
const byId = (id) => document.getElementById(id);

function unwrap(payload) {
  if (payload && typeof payload === 'object') {
    if (payload.result && typeof payload.result === 'object') return payload.result;
    if (payload.payload && typeof payload.payload === 'object') return payload.payload;
    if (payload.data && typeof payload.data === 'object' && !Array.isArray(payload.data)) return payload.data;
  }
  return payload;
}

function injectStyles() {
  const style = document.createElement('style');
  style.textContent = `
    .kimi-engine { margin-top: 14px; border: 1px solid rgba(118,204,255,.28); border-radius: 14px; padding: 14px; background: linear-gradient(145deg,rgba(24,42,54,.78),rgba(26,17,34,.82)); }
    .kimi-engine header { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; margin-bottom:10px; }
    .kimi-engine h3 { margin:0; font-size:15px; letter-spacing:.02em; }
    .kimi-engine p { margin:4px 0 0; font-size:12px; color:var(--muted,#b5abbc); line-height:1.4; }
    .kimi-status { border-radius:999px; padding:5px 8px; font-size:10px; font-weight:800; letter-spacing:.08em; white-space:nowrap; background:#332c38; color:#d7cbdc; }
    .kimi-status.ready { background:#123c31; color:#83efc0; }
    .kimi-status.error { background:#4b2027; color:#ff9eaa; }
    .kimi-grid { display:grid; grid-template-columns:1fr 1fr; gap:9px; }
    .kimi-grid label { display:grid; gap:5px; font-size:11px; color:var(--muted,#b5abbc); }
    .kimi-grid .wide { grid-column:1/-1; }
    .kimi-grid select,.kimi-grid textarea { width:100%; box-sizing:border-box; border:1px solid rgba(255,255,255,.14); border-radius:9px; background:#110d15; color:#f8f3fa; padding:9px; font:inherit; }
    .kimi-grid textarea { min-height:76px; resize:vertical; line-height:1.45; }
    .kimi-actions { display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; }
    .kimi-actions button,.kimi-actions a { border:0; border-radius:9px; padding:9px 11px; font-weight:750; font-size:11px; cursor:pointer; text-decoration:none; text-align:center; }
    .kimi-generate { flex:1 1 190px; color:#101015; background:linear-gradient(135deg,#8ce3ff,#d8a2ff); }
    .kimi-secondary { color:#e8dff0; background:#2b2230; }
    .kimi-actions button:disabled { opacity:.45; cursor:not-allowed; }
    .kimi-result { margin-top:10px; padding:10px; border-radius:10px; background:rgba(7,10,15,.68); border:1px solid rgba(255,255,255,.09); }
    .kimi-result[hidden] { display:none; }
    .kimi-result strong { display:block; font-size:12px; }
    .kimi-result span { display:block; margin-top:4px; color:var(--muted,#b5abbc); font-size:11px; line-height:1.4; }
    .kimi-result code { display:block; margin-top:7px; overflow-wrap:anywhere; color:#9eddf5; font-size:10px; }
    @media (max-width:720px) { .kimi-grid { grid-template-columns:1fr; } .kimi-grid .wide { grid-column:auto; } }
  `;
  document.head.append(style);
}

function createPanel() {
  const anchor = byId('default-reason') || byId('defaults');
  if (!anchor || byId('kimi-engine')) return null;
  const panel = document.createElement('section');
  panel.id = 'kimi-engine';
  panel.className = 'kimi-engine';
  panel.innerHTML = `
    <header>
      <div><h3>Kimi K3 content engine</h3><p>Creates governed storyboards, sprite-atlas plans, shader handoffs, and native MP4 training manifests. HHS remains the renderer and execution authority.</p></div>
      <span id="kimi-status" class="kimi-status">CHECKING</span>
    </header>
    <div class="kimi-grid">
      <label>Generation scope
        <select id="kimi-operation">
          <option value="complete_pipeline">Complete visual pipeline</option>
          <option value="storyboard">Storyboard</option>
          <option value="sprite_map">Sprite maps</option>
          <option value="native_mp4_training">Native MP4 training</option>
        </select>
      </label>
      <label>Target
        <select id="kimi-target">
          <option value="vertical">90s vertical reel · 1080×1920</option>
          <option value="game">Game scene · 1920×1080</option>
          <option value="sprite">Sprite production · 1024×1024</option>
        </select>
      </label>
      <label class="wide">Art direction
        <textarea id="kimi-art-direction" maxlength="32768">Polished cinematic sprite-map graphics with readable silhouettes, harmonic reciprocal color planes, layered parallax, deterministic transitions, and shader-ready channels.</textarea>
      </label>
    </div>
    <div class="kimi-actions">
      <button id="kimi-generate" class="kimi-generate" type="button" disabled>Generate governed visual plan</button>
      <button id="kimi-apply" class="kimi-secondary" type="button" disabled>Apply native handoff</button>
      <a id="kimi-download" class="kimi-secondary" href="#" download="hhs-kimi-k3-content-plan.json" hidden>Download JSON</a>
    </div>
    <div id="kimi-result" class="kimi-result" hidden>
      <strong id="kimi-result-title">Plan ready</strong>
      <span id="kimi-result-summary"></span>
      <code id="kimi-result-hash"></code>
    </div>
  `;
  anchor.insertAdjacentElement('afterend', panel);
  return panel;
}

function targetGeometry() {
  const target = byId('kimi-target')?.value || 'vertical';
  if (target === 'game') return { duration_seconds: 30, fps: 60, width: 1920, height: 1080 };
  if (target === 'sprite') return { duration_seconds: 12, fps: 12, width: 1024, height: 1024 };
  return { duration_seconds: 90, fps: 30, width: 1080, height: 1920 };
}

function dispatch(input) {
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
}

function applyNativeHandoff(plan) {
  const handoff = plan?.hhs_native_handoff;
  if (!handoff) throw new Error('The content plan has no native handoff.');
  const title = byId('title');
  const story = byId('story');
  if (title && handoff.title) { title.value = handoff.title; dispatch(title); }
  if (story && handoff.story_text) { story.value = handoff.story_text; dispatch(story); }
  const style = handoff.style_overrides || {};
  for (const [key, value] of Object.entries(style)) {
    const input = byId(key.replaceAll('_', '-'));
    if (!input || key === 'template_id') continue;
    input.value = value;
    dispatch(input);
  }
  const template = byId('template');
  if (template && style.template_id && [...template.options].some((option) => option.value === style.template_id)) {
    template.value = style.template_id;
    dispatch(template);
  }
  byId('kimi-result-summary').textContent = 'Native handoff applied to the Storybook Studio controls. Review the preview, upload narration, then run the existing HHS native MP4 generator.';
}

function exposeDownload(plan) {
  const link = byId('kimi-download');
  if (!link) return;
  if (link.dataset.objectUrl) URL.revokeObjectURL(link.dataset.objectUrl);
  const blob = new Blob([`${JSON.stringify(plan, null, 2)}\n`], { type: 'application/json' });
  const objectUrl = URL.createObjectURL(blob);
  link.href = objectUrl;
  link.dataset.objectUrl = objectUrl;
  link.hidden = false;
}

async function checkStatus() {
  const badge = byId('kimi-status');
  const button = byId('kimi-generate');
  try {
    const response = await fetch(`${API}/status`, { cache: 'no-store' });
    const payload = unwrap(await response.json());
    const configured = Boolean(payload?.configured && payload?.enabled);
    badge.textContent = configured ? 'CONFIGURED' : 'KEY REQUIRED';
    badge.className = `kimi-status ${configured ? 'ready' : 'error'}`;
    button.disabled = !configured;
    if (!configured) button.title = 'Configure HHS_KIMI_K3_API_KEY or MOONSHOT_API_KEY on the server.';
  } catch (error) {
    badge.textContent = 'OFFLINE';
    badge.className = 'kimi-status error';
    button.disabled = true;
    button.title = error.message;
  }
}

async function generatePlan() {
  const button = byId('kimi-generate');
  const resultBox = byId('kimi-result');
  const resultTitle = byId('kimi-result-title');
  const resultSummary = byId('kimi-result-summary');
  const resultHash = byId('kimi-result-hash');
  const sourceText = byId('story')?.value?.trim() || '';
  if (!sourceText) {
    resultBox.hidden = false;
    resultTitle.textContent = 'Source text required';
    resultSummary.textContent = 'Enter the story or visual brief before generating a plan.';
    return;
  }
  button.disabled = true;
  button.textContent = 'Generating Kimi K3 plan…';
  resultBox.hidden = false;
  resultTitle.textContent = 'Provider proposal running';
  resultSummary.textContent = 'Kimi K3 is producing a strict structured proposal. No native asset or MP4 is claimed until HHS executes the handoff.';
  resultHash.textContent = '';
  try {
    const geometry = targetGeometry();
    const response = await fetch(`${API}/plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        operation: byId('kimi-operation').value,
        project_id: 'project:storybook-reel',
        title: byId('title')?.value || 'HHS Storyboard',
        source_text: sourceText,
        art_direction: byId('kimi-art-direction').value,
        ...geometry,
        constraints: [
          'Preserve exact source meaning',
          'Use HHS x/y/z/w reciprocal phase planes',
          'Use deterministic integer frame ranges',
          'HHS native renderer and VM81 remain authoritative',
          'External model output is proposal-only',
        ],
      }),
    });
    const raw = await response.json();
    if (!response.ok) {
      const reason = raw?.detail?.reason || raw?.detail || raw?.error || response.statusText;
      throw new Error(typeof reason === 'string' ? reason : JSON.stringify(reason));
    }
    const payload = unwrap(raw);
    if (!payload?.plan) throw new Error('The provider returned no admitted plan.');
    window.HHS_KIMI_K3_CONTENT_PLAN = payload.plan;
    const scenes = payload.plan.storyboard?.scenes?.length || 0;
    const atlases = payload.plan.sprite_maps?.length || 0;
    const examples = payload.plan.training_manifest?.examples?.length || 0;
    resultTitle.textContent = 'Governed visual plan ready';
    resultSummary.textContent = `${scenes} storyboard scenes · ${atlases} sprite atlases · ${examples} training examples. Apply the native handoff to stage the plan in the existing Storybook Studio.`;
    resultHash.textContent = payload.plan.plan_root_hash72 || payload.result_root_hash72 || '';
    byId('kimi-apply').disabled = false;
    exposeDownload(payload.plan);
  } catch (error) {
    resultTitle.textContent = 'Kimi K3 generation failed';
    resultSummary.textContent = error.message;
    resultHash.textContent = '';
  } finally {
    button.disabled = false;
    button.textContent = 'Generate governed visual plan';
  }
}

function initialize() {
  injectStyles();
  if (!createPanel()) return;
  byId('kimi-generate').addEventListener('click', generatePlan);
  byId('kimi-apply').addEventListener('click', () => {
    try {
      applyNativeHandoff(window.HHS_KIMI_K3_CONTENT_PLAN);
    } catch (error) {
      byId('kimi-result').hidden = false;
      byId('kimi-result-title').textContent = 'Native handoff unavailable';
      byId('kimi-result-summary').textContent = error.message;
    }
  });
  checkStatus();
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize, { once: true });
else initialize();
