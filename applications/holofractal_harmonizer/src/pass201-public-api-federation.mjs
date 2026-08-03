const API = '/api/public';
const OBJECT_ID = 'hhs:runtime:pass201-public-api-federation';
const state = { status: null, busy: false, error: null };

async function request(path) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 30000);
  try {
    const response = await fetch(path, { signal: controller.signal, headers: { Accept: 'application/json' } });
    const payload = await response.json().catch(() => ({ error: `Non-JSON response from ${path}` }));
    if (!response.ok) throw new Error(payload.detail || payload.error || response.statusText);
    return payload?.payload && typeof payload.payload === 'object' ? payload.payload : payload;
  } finally {
    clearTimeout(timer);
  }
}

function installStyles() {
  if (document.querySelector('[data-pass201-style]')) return;
  const node = document.createElement('style');
  node.dataset.pass201Style = 'true';
  node.textContent = `
    .p201{border-top:1px solid rgba(255,255,255,.08);padding:12px;display:grid;gap:10px}
    .p201 header{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}.p201 h3{margin:0;font-size:13px}.p201 p{margin:4px 0 0;color:var(--muted,#aaa);font-size:11px;line-height:1.4}
    .p201-badge{border-radius:999px;padding:5px 8px;font-size:9px;font-weight:800;background:#31273c;white-space:nowrap}.p201-badge.ready{background:#123c31;color:#83efc0}.p201-badge.error{background:#4b2027;color:#ff9eaa}
    .p201-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px}.p201-grid div,.p201-output,.p201-boundary{padding:8px;border-radius:8px;background:rgba(0,0,0,.25)}
    .p201-grid span{display:block;color:var(--muted,#aaa);font-size:8px}.p201-grid strong{display:block;margin-top:4px;font-size:11px;overflow-wrap:anywhere}
    .p201-actions{display:flex;gap:7px;flex-wrap:wrap}.p201-actions a,.p201-actions button{border:0;border-radius:8px;padding:8px 10px;font-size:10px;font-weight:750;cursor:pointer;text-decoration:none}
    .p201-primary{background:linear-gradient(135deg,#8ce7ff,#7ca5ff);color:#10131a}.p201-secondary{background:#2b2230;color:#e8dff0}.p201-output{margin:0;white-space:pre-wrap;color:#badfee;font-size:9px;line-height:1.45}.p201-boundary{color:#cbbbd4;font-size:9px;line-height:1.45}.p201-boundary strong{color:#91f3d4}
    @media(max-width:860px){.p201-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
  `;
  document.head.append(node);
}

function createPanel() {
  if (document.querySelector('#pass201-public-api-federation')) return;
  const anchor = document.querySelector('#pass200c-guarded-active')
    || document.querySelector('#pass200b-governed-canary')
    || document.querySelector('.lifecycle-control-window');
  if (!anchor) return;
  const node = document.createElement('section');
  node.id = 'pass201-public-api-federation';
  node.className = 'p201';
  node.innerHTML = `
    <header><div><h3>Pass 201 Public API Federation</h3><p>Every registered service route and every repository pass module is indexed through one public catalog.</p></div><span id="p201-badge" class="p201-badge">LOADING</span></header>
    <div class="p201-grid">
      <div><span>PUBLIC ROUTES</span><strong id="p201-routes">0</strong></div>
      <div><span>SERVICES</span><strong id="p201-services">0</strong></div>
      <div><span>PASS MODULES</span><strong id="p201-passes">0</strong></div>
      <div><span>UNEXPOSED</span><strong id="p201-unexposed">0</strong></div>
    </div>
    <div class="p201-actions">
      <a class="p201-primary" href="/docs" target="_blank" rel="noopener">Open Swagger API</a>
      <a class="p201-secondary" href="/api/public/catalog" target="_blank" rel="noopener">Full catalog</a>
      <a class="p201-secondary" href="/api/public/services" target="_blank" rel="noopener">Services</a>
      <a class="p201-secondary" href="/api/public/passes" target="_blank" rel="noopener">Pass modules</a>
      <button id="p201-refresh" class="p201-secondary">Refresh</button>
    </div>
    <div class="p201-boundary"><strong>Execution boundary:</strong> native service routes remain directly callable. The federation publishes discovery and OpenAPI metadata but does not expose arbitrary internal Python execution.</div>
    <pre id="p201-output" class="p201-output">Loading public API registry…</pre>`;
  anchor.insertAdjacentElement('afterend', node);
}

function setText(id, value) {
  const node = document.querySelector(`#${id}`);
  if (node) node.textContent = String(value ?? '—');
}

function render() {
  const value = state.status || {};
  const registration = value.registration || {};
  setText('p201-routes', value.route_count ?? 0);
  setText('p201-services', value.service_count ?? 0);
  setText('p201-passes', value.pass_module_count ?? 0);
  setText('p201-unexposed', registration.unexposed_route_count ?? 0);
  const badge = document.querySelector('#p201-badge');
  if (badge) {
    badge.textContent = state.error ? 'ERROR' : value.closed ? 'FEDERATED' : 'INCOMPLETE';
    badge.className = `p201-badge ${state.error ? 'error' : value.closed ? 'ready' : ''}`;
  }
  const output = document.querySelector('#p201-output');
  if (output) {
    output.textContent = state.error || [
      `classification=${value.classification || 'HHS_PASS_201_PUBLIC_API_FEDERATION_VERIFIED'}`,
      `api_modules=${registration.api_module_count ?? 0}`,
      `routers=${registration.router_count ?? 0}`,
      `attached_routes=${registration.attached_route_count ?? 0}`,
      `existing_routes=${registration.duplicate_route_count ?? 0}`,
      `import_failures=${registration.import_failure_count ?? 0}`,
      `unexposed_routes=${registration.unexposed_route_count ?? 0}`,
      `openapi_missing=${value.openapi_missing_count ?? 0}`,
      `catalog_sha256=${value.catalog_sha256 || '—'}`,
    ].join('\n');
  }
}

async function project() {
  for (let attempt = 0; attempt < 200; attempt += 1) {
    const runtime = window.HHSHarmonizer;
    if (runtime?.registry) {
      try {
        if (!runtime.registry.has(OBJECT_ID)) {
          await runtime.registry.register({
            object_id: OBJECT_ID,
            object_type: 'RUNTIME',
            canonical_name: 'HHS_PASS201_PUBLIC_API_FEDERATION',
            display_name: 'Pass 201 Public API Federation',
            description: 'Public route, service, pass-module, tool, and OpenAPI discovery for all registered routers.',
            modality_classes: ['API_REGISTRY', 'OPENAPI_DOCUMENT', 'SERVICE_CATALOG', 'PASS_MODULE_CATALOG'],
            lifecycle_state: 'ACTIVE',
            authority_state: 'VALIDATED_PROJECTION',
            validation_state: 'PUBLIC_API_FEDERATED',
            capabilities: ['PUBLIC_ROUTE_DISCOVERY', 'PUBLIC_SERVICE_DISCOVERY', 'PUBLIC_PASS_DISCOVERY', 'OPENAPI_DISCOVERY'],
            actions: [
              { action_id: 'status', method: 'GET', endpoint: `${API}/status` },
              { action_id: 'catalog', method: 'GET', endpoint: `${API}/catalog` },
              { action_id: 'services', method: 'GET', endpoint: `${API}/services` },
              { action_id: 'passes', method: 'GET', endpoint: `${API}/passes` },
              { action_id: 'openapi', method: 'GET', endpoint: `${API}/openapi` },
            ],
            dependencies: ['hhs:runtime:pass196-integration'],
            metadata: { all_registered_routers_public: true, arbitrary_python_execution_public: false, frontend_is_authority: false },
          }, 'system:pass201-public-api-projection');
        }
      } catch (error) {
        console.warn('[HHS Pass201 projection]', error);
      }
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
}

async function refresh() {
  state.busy = true;
  state.error = null;
  render();
  try {
    state.status = await request(`${API}/status`);
    await project();
  } catch (error) {
    state.error = `${error.name}: ${error.message}`;
  } finally {
    state.busy = false;
    render();
  }
}

installStyles();
createPanel();
document.querySelector('#p201-refresh')?.addEventListener('click', refresh);
refresh();
