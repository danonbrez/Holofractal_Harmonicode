const params = new URLSearchParams(location.search);
const variant = (params.get('variant') || 'B').toUpperCase();
const workflowId = params.get('workflow') || 'code_api';
const sessionId = params.get('session') || `${Date.now()}`;
const app = document.querySelector('#app');
const startedAt = performance.now();
let actionCount = 0;
let contextSwitches = 0;
let result = null;
let workflowData;
let templates;
let currentView = 'assistant';
let activeStage = 0;

function action({context=false}={}) {
  actionCount += 1;
  if (context) contextSwitches += 1;
  updateMetricBadge();
}
function escapeHtml(value='') {
  return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
}
function updateMetricBadge() {
  const el = document.querySelector('#metric-badge');
  if (el) el.textContent = `ACTIONS ${actionCount} · SWITCHES ${contextSwitches}`;
}
function elapsed() { return Math.round(performance.now() - startedAt); }
function finish() {
  const metrics = {variant, workflow_id: workflowId, success: Boolean(result?.ok), action_count: actionCount, context_switches: contextSwitches, completion_ms: elapsed(), backend_elapsed_ms: result?.elapsed_ms ?? null, receipt_sha256: result?.receipt_sha256 ?? null};
  document.body.dataset.completed = metrics.success ? 'true' : 'false';
  document.body.dataset.metrics = JSON.stringify(metrics);
  window.__HHS_UX_METRICS__ = metrics;
  const status = document.querySelector('#completion-state');
  if (status) status.textContent = metrics.success ? 'WORKFLOW VERIFIED' : 'WORKFLOW INCOMPLETE';
  updateMetricBadge();
}
async function runWorkflow() {
  const response = await fetch(`/api/run/${workflowId}`, {method:'POST', headers:{'content-type':'application/json'}, body:JSON.stringify({variant, session_id:sessionId})});
  if (!response.ok) throw new Error(await response.text());
  result = await response.json();
  return result;
}
function topBar(label) {
  return `<header class="topbar">
    <div class="brand"><strong>HHS Visual IDE</strong><span>${variant === 'A' ? 'Object-first baseline' : 'Workflow-first candidate'}</span></div>
    ${variant === 'A' ? '<input class="top-search" aria-label="Search objects" placeholder="Search objects, services, APIs…">' : '<label class="command"><input aria-label="Command palette" placeholder="Search templates, objects, commands…"><span class="kbd">⌘K</span></label>'}
    <div class="top-status"><span class="pill success"><i class="dot"></i>LOCAL VALIDATED</span><span class="pill" style="color:var(--violet)">PROPOSAL ONLY</span></div>
  </header>`;
}
function footer() {
  return `<footer class="footer"><span>${variant === 'A' ? 'AGENT · visual-development-assistant' : `WORKFLOW · ${workflowData.category}`}</span><span>SESSION <code>${escapeHtml(sessionId.slice(0,12))}</code></span><span id="completion-state">IN PROGRESS</span><span>AUTHORITY · CONTROLLED USABILITY LAB</span></footer><div id="metric-badge" class="metric-badge"></div>`;
}
function statusCards() {
  return `<div class="status-grid">
    <article class="card"><span>MODEL</span><strong>gemma4-12b</strong><small>local workflow harness</small></article>
    <article class="card"><span>THREAD</span><strong>${escapeHtml(sessionId.slice(0,10))}</strong><small>bounded development thread</small></article>
    <article class="card"><span>HHS TOOLS</span><strong>8</strong><small>governed categories</small></article>
    <article class="card"><span>AUTHORITY</span><strong>PROPOSAL ONLY</strong><small>no canonical mutation claim</small></article>
  </div>`;
}
function renderA() {
  app.innerHTML = `<div class="variant-a">${topBar()}
    <div class="layout">
      <nav class="pane registry" aria-label="Registered objects">
        <div class="panel-title"><strong>Registry</strong><span class="muted">24 objects</span></div>
        <div class="nav-switch"><button id="a-assistant-home" class="${currentView==='assistant'?'primary':''}">Assistant</button><button id="a-object-workspace" class="${currentView==='objects'?'primary':''}">Object Workspace</button></div>
        <div class="tree-group"><button><span>APPLICATION · 5</span><span>⌄</span></button><div class="tree-items">
          <button id="a-select-task" class="${currentView==='objects'?'active':''}"><i class="dot success"></i><span>${escapeHtml(workflowData.title)}<br><small>${escapeHtml(workflowData.category)}</small></span><small>READY</small></button>
          <button><i class="dot"></i><span>Runtime Console<br><small>hhs:runtime:vm81</small></span><small>READY</small></button>
          <button><i class="dot"></i><span>Receipt Graph<br><small>hhs:graph:receipts</small></span><small>READY</small></button>
        </div></div>
        <div class="tree-group"><button><span>SERVICE · 8</span><span>›</span></button></div><div class="tree-group"><button><span>MODEL · 3</span><span>›</span></button></div><div class="tree-group"><button><span>DIAGNOSTIC · 8</span><span>›</span></button></div>
      </nav>
      <main class="workspace">
        ${currentView === 'api' ? renderAApi() : renderAAssistant()}
      </main>
      <aside class="pane inspector" aria-label="Object inspector"><div class="panel-title"><strong>Inspector</strong><button>Back</button></div><div class="inspector-body">
        <div class="inspect-section"><strong>Overview</strong><pre>${escapeHtml(JSON.stringify({object_id:`workflow:${workflowId}`,type:'APPLICATION',state:result?'VERIFIED':'READY',authority:'VALIDATED_PROJECTION'},null,2))}</pre></div>
        <div class="inspect-section"><strong>Metadata</strong><pre>${escapeHtml(JSON.stringify({goal:workflowData.goal,stages:workflowData.stages,artifacts:workflowData.artifacts},null,2))}</pre></div>
        <div class="inspect-section"><strong>Receipts</strong><pre>${result ? result.receipt_sha256 : 'No workflow receipt yet.'}</pre></div>
      </div></aside>
    </div>${footer()}</div>`;
  wireA(); updateMetricBadge();
}
function renderAAssistant() {
  return `<section><div class="a-hero"><div><span class="eyebrow">${currentView==='objects'?'REGISTERED OBJECT WORKSPACE':'DEFAULT HOME INTERFACE'}</span><h1>${currentView==='objects'?'Unified Multimodal Object Control':'Natural-Language Visual Development Environment'}</h1><p>${escapeHtml(workflowData.goal)} Navigate across the object registry, assistant, API controller, and inspector to complete the task.</p></div><div class="hero-actions"><button>New Thread</button><button>Object Space</button><button id="a-open-api">API Controller</button></div></div>
  ${statusCards()}
  <section class="conversation card"><div class="messages"><article class="message"><div class="eyebrow">HHS ASSISTANT</div><p>Choose the registered application object, return to the assistant, submit the task request, then invoke the API controller to run and verify the workflow.</p></article>${currentView==='assistant' && actionCount>=4 ? `<article class="message user"><div class="eyebrow">USER</div><p>${escapeHtml(workflowData.goal)}</p></article>`:''}${result ? `<article class="message"><div class="eyebrow">HHS ASSISTANT</div><p class="success">Workflow artifacts validated successfully.</p><p class="mono">Receipt ${result.receipt_sha256.slice(0,24)}…</p></article>`:''}</div>
    <div class="composer"><textarea id="a-prompt" aria-label="Prompt" placeholder="Describe what to build, inspect, test, or explain…"></textarea><div class="composer-row"><div class="chips"><button id="a-quick-prompt">${escapeHtml(workflowData.title)}</button><button>Runtime status</button><button>Authority constraints</button></div><button id="a-send" class="primary">Send</button></div></div></section></section>`;
}
function renderAApi() {
  return `<section class="api-console card"><span class="eyebrow">REGISTERED OBJECT SEARCH API</span><h1>API Controller</h1><p class="muted">Invoke the selected workflow object through the controlled local execution surface.</p><input id="a-api-input" value="${escapeHtml(workflowId)}" aria-label="Workflow ID"><button id="a-api-invoke" class="primary">Invoke Workflow</button><pre id="a-api-output">${result ? escapeHtml(JSON.stringify(result,null,2)) : 'No invocation yet.'}</pre>${result ? '<button id="a-complete" class="primary">Review and Complete</button>' : ''}</section>`;
}
function wireA() {
  document.querySelector('#a-object-workspace')?.addEventListener('click',()=>{action({context:true});currentView='objects';renderA();});
  document.querySelector('#a-select-task')?.addEventListener('click',()=>{action();document.querySelector('#a-select-task')?.classList.add('active');});
  document.querySelector('#a-assistant-home')?.addEventListener('click',()=>{action({context:true});currentView='assistant';renderA();});
  document.querySelector('#a-quick-prompt')?.addEventListener('click',()=>{action();document.querySelector('#a-prompt').value=workflowData.goal;});
  document.querySelector('#a-send')?.addEventListener('click',()=>{action();renderA();});
  document.querySelector('#a-open-api')?.addEventListener('click',()=>{action({context:true});currentView='api';renderA();});
  document.querySelector('#a-api-invoke')?.addEventListener('click',async()=>{action();const out=document.querySelector('#a-api-output');out.textContent='Running executable workflow…';result=await runWorkflow();renderA();});
  document.querySelector('#a-complete')?.addEventListener('click',()=>{action({context:true});finish();});
}
function templateIcon(template) { return ({CODE:'λ',API:'↔',DATA:'Σ',DOCUMENT:'¶',IMAGE:'◫',MEDIA:'♫',SPATIAL:'◈',MODEL:'AI'})[template.category] || '◇'; }
function renderB() {
  const selectedTemplate = templates.find(t => categoryMatch(t.category, workflowData.category)) || templates[0];
  app.innerHTML = `<div class="variant-b">${topBar()}
    <div class="layout">
      <nav class="pane template-rail" aria-label="Workflow templates"><div class="panel-title"><strong>Workflows</strong><span class="muted">8 templates</span></div><div class="template-list">${templates.map(t=>`<button class="template ${t.id===selectedTemplate.id?'active':''}" data-template="${t.id}"><span class="template-top"><i class="template-icon">${templateIcon(t)}</i><strong>${escapeHtml(t.title)}</strong></span><small>${escapeHtml(t.outcome)}</small></button>`).join('')}</div></nav>
      <main class="b-workspace">${renderBMain(selectedTemplate)}</main>
      <aside class="pane context" aria-label="Context and evidence"><div class="panel-title"><strong>Context</strong><span class="pill success"><i class="dot"></i>BOUND</span></div><div class="context-body">${renderEvidence()}</div></aside>
    </div>${footer()}</div>`;
  wireB(); updateMetricBadge();
}
function categoryMatch(templateCategory, workflowCategory) {
  if (workflowCategory.includes('CODE') || workflowCategory.includes('API')) return ['CODE','API'].includes(templateCategory);
  if (workflowCategory.includes('DATA')) return templateCategory==='DATA';
  if (workflowCategory.includes('DOCUMENT')) return templateCategory==='DOCUMENT';
  if (workflowCategory.includes('IMAGE') || workflowCategory.includes('SPATIAL')) return ['IMAGE','SPATIAL'].includes(templateCategory);
  return false;
}
function renderBMain(selectedTemplate) {
  return `<section><div class="stage-header"><div><span class="eyebrow">ACTIVE WORKFLOW · ${escapeHtml(workflowData.category)}</span><h1>${escapeHtml(workflowData.title)}</h1><p>${escapeHtml(workflowData.goal)}</p></div><div class="stage-actions"><button>Save Template</button><button id="b-start" class="primary">${activeStage ? 'Resume Workflow' : 'Start Workflow'}</button></div></div>
    <div class="stage-strip">${workflowData.stages.map((s,i)=>`<article class="stage ${i<activeStage?'complete':''} ${i===activeStage?'active':''}"><span>${i<activeStage?'COMPLETE':i===activeStage?'ACTIVE':'QUEUED'}</span><strong>${escapeHtml(s)}</strong></article>`).join('')}</div>
    <div class="focus-grid"><section class="workbench card"><div class="workbench-head"><strong>Execution Plan</strong><span class="pill ${result?'success':''}"><i class="dot"></i>${result?'VALIDATED':'READY'}</span></div><div class="workbench-body"><article class="goal-card"><span class="eyebrow">EXPECTED OUTCOME</span><h2>${escapeHtml(selectedTemplate.outcome)}</h2><p class="muted">The workflow keeps advanced object metadata available in Context while presenting the shortest safe path to completion.</p></article>
      <div class="task-list">${workflowData.stages.map((s,i)=>`<article class="task ${i<activeStage?'done':''}"><span class="num">${i<activeStage?'✓':i+1}</span><div><strong>${escapeHtml(s)}</strong><small>${i===0?'Confirm goal and authority boundary':i===workflowData.stages.length-1?'Inspect files, hashes, and runtime note':'Execute the next governed stage'}</small></div><span class="muted">${i<activeStage?'done':i===activeStage?'next':'queued'}</span></article>`).join('')}</div>
      <div class="run-panel"><div style="display:flex;justify-content:space-between;align-items:center;gap:10px"><strong>Run console</strong><button id="b-run-all" class="primary" ${activeStage===0?'disabled':''}>Run All Stages</button></div><pre id="b-output">${result ? escapeHtml(result.logs.join('\n')+'\n\nReceipt '+result.receipt_sha256) : activeStage ? 'Plan admitted. Ready to execute all bounded stages.' : 'Start the workflow to admit the execution plan.'}</pre>${result?'<button id="b-review" class="primary">Review Evidence and Complete</button>':''}</div>
      <form class="b-composer"><input value="${escapeHtml(selectedTemplate.prompt)}" aria-label="Workflow assistant prompt"><button>Ask Assistant</button></form></div></section><aside class="card evidence-card"><h3>Workflow summary</h3><p class="muted">${escapeHtml(selectedTemplate.prompt)}</p><div class="artifact-list">${workflowData.artifacts.map(name=>`<div class="artifact"><span>${escapeHtml(name)}</span><small>${result?'verified':'planned'}</small></div>`).join('')}</div></aside></div></section>`;
}
function renderEvidence() {
  return `<article class="card evidence-card"><span class="eyebrow">AUTHORITY</span><h3>Controlled local trial</h3><p class="muted">Executable artifact validation is real. It is not presented as a canonical VM81 receipt.</p></article><article class="card evidence-card"><span class="eyebrow">ARTIFACTS</span><div class="artifact-list">${(result?.files||workflowData.artifacts.map(name=>({name,bytes:null,sha256:null}))).map(f=>`<div class="artifact"><span>${escapeHtml(f.name)}</span><small>${f.bytes?`${f.bytes} B`:'planned'}</small></div>`).join('')}</div></article><article class="card evidence-card"><span class="eyebrow">RECEIPT</span><p class="receipt">${result?.receipt_sha256||'Generated after successful validation.'}</p></article>`;
}
function wireB() {
  document.querySelectorAll('[data-template]').forEach(b=>b.addEventListener('click',()=>{action();document.querySelectorAll('[data-template]').forEach(x=>x.classList.toggle('active',x===b));}));
  document.querySelector('#b-start')?.addEventListener('click',()=>{action();activeStage=1;renderB();});
  document.querySelector('#b-run-all')?.addEventListener('click',async()=>{action();document.querySelector('#b-output').textContent='Executing real local artifact builders and validators…';result=await runWorkflow();activeStage=4;renderB();});
  document.querySelector('#b-review')?.addEventListener('click',()=>{action({context:true});activeStage=5;renderB();finish();});
}
async function init() {
  const payload = await (await fetch('/api/workflows')).json();
  workflowData = payload.workflows[workflowId] || payload.workflows.code_api;
  templates = payload.templates;
  document.body.className = `variant-${variant.toLowerCase()}`;
  variant === 'A' ? renderA() : renderB();
}
init().catch(error=>{app.innerHTML=`<pre>${escapeHtml(error.stack||error)}</pre>`;});
