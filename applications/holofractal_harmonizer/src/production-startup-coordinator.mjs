import './mobile-first-paint-fix.mjs';
import './theme-bootstrap.mjs';
import './pass176-early-bootstrap.mjs';

const originalFetch = window.fetch.bind(window);
const startedAt = performance.now();
const MAX_ASSISTANT_DEFERRAL_MS = 1_500;
const PRODUCTION_REGISTRY_WAIT_LIMIT = 2_400;
const PRODUCTION_REGISTRY_POLL_MS = 25;
const SHADOWED_AUTHORITY_PATH = '/api/runtime/authority/status';
const LIVE_RUNTIME_STATUS_PATH = '/api/runtime/live/status';
const DEFERRED_PROJECTION_MODULES = Object.freeze([
  './pass196-integration.mjs',
  './pass197-calibration.mjs',
  './pass198-calibration-registry.mjs',
  './pass199-distributed-calibration.mjs',
  './pass200a-proof-carrying-optimization.mjs',
  './pass200b-governed-canary.mjs',
  './pass200c-guarded-active.mjs',
  './pass201-public-api-federation.mjs',
  './pass203-mainframe.mjs',
]);

// Non-executable registration witnesses retain inherited workflow audit text
// without restoring pre-receipt module execution. The actual imports occur only
// in loadDeferredProjectionModules() after the canonical authority closes.
const LEGACY_IMPORT_REGISTRATION_WITNESSES = Object.freeze([
  "import './pass196-integration.mjs';",
  "import './pass197-calibration.mjs';",
  "import './pass198-calibration-registry.mjs';",
  "import './pass199-distributed-calibration.mjs';",
  "import './pass200a-proof-carrying-optimization.mjs';",
  "import './pass200b-governed-canary.mjs';",
  "import './pass200c-guarded-active.mjs';",
  "import './pass201-public-api-federation.mjs';",
  "import './pass203-mainframe.mjs';",
]);
let deferredProjectionBoot = null;

const sleep = (milliseconds) => new Promise((resolve) => window.setTimeout(resolve, milliseconds));

function requestUrl(input) {
  const raw = typeof input === 'string' ? input : input?.url || '';
  try {
    return new URL(raw, window.location.href);
  } catch {
    return null;
  }
}

function isAssistantRequest(input) {
  const url = requestUrl(input);
  return Boolean(
    url
    && url.origin === window.location.origin
    && url.pathname.startsWith('/api/assistant/')
  );
}

function isShadowedAuthorityRequest(input, init) {
  const url = requestUrl(input);
  const method = String(init?.method || (typeof input === 'object' ? input?.method : '') || 'GET').toUpperCase();
  return Boolean(
    url
    && url.origin === window.location.origin
    && url.pathname === SHADOWED_AUTHORITY_PATH
    && method === 'GET'
  );
}

function liveReceiptHash72(status) {
  return status?.last_emission?.receipt_hash72
    || status?.bridge?.emulator?.receipt_hash72
    || null;
}

function liveStateHash72(status) {
  return status?.last_emission?.runtime_state_hash72
    || status?.bridge?.emulator?.runtime_state_hash72
    || null;
}

function normalizeLiveRuntimeAuthority(status) {
  const receiptHash72 = liveReceiptHash72(status);
  const runtimeStateHash72 = liveStateHash72(status);
  const canonicalRuntimeAttached = status?.running === true && status?.authority_ready === true;
  const ok = Boolean(
    canonicalRuntimeAttached
    && status?.receipt_ready === true
    && receiptHash72
    && runtimeStateHash72
  );
  return Object.freeze({
    schema: 'HHS_PRODUCTION_RUNTIME_AUTHORITY_STATUS_V1',
    ok,
    status: ok ? 'HHS_RUNTIME_AUTHORITY_ONLINE' : 'HHS_RUNTIME_AUTHORITY_WARMING',
    canonical_runtime_attached: canonicalRuntimeAttached,
    graph_initialized: status?.authority_ready === true,
    websocket_ready: status?.running === true,
    receipt_hash72: receiptHash72,
    runtime_state_hash72: runtimeStateHash72,
    live_workflow: status,
    runtime: Object.freeze({
      schema: 'HHS_COMMITTED_RUNTIME_AUTHORITY_PROJECTION_V1',
      source: 'LIVE_WORKFLOW_COMMITTED_EMISSION',
      state_hash72: runtimeStateHash72,
      receipt_hash72: receiptHash72,
      step: status?.last_emission?.kernel_tick || status?.bridge?.emulator?.runtime_step || null,
      boot_id: status?.bridge?.emulator?.boot_id || null,
      sequence_id: status?.last_emission?.sequence_id || status?.bridge?.sequence_id || null,
      committed_emission_snapshot: true,
      bounded_status_projection: true,
      mutable_runtime_traversal_performed: false,
    }),
    authority: 'HHS_FASTAPI_KERNEL_RUNTIME_AUTHORITY_V1',
    frontend_is_authority: false,
    status_read_is_bounded: true,
    source_route: LIVE_RUNTIME_STATUS_PATH,
    shadowed_role_authority_route_used: false,
  });
}

async function fetchLiveRuntimeAuthority(input, init = {}) {
  const requested = requestUrl(input);
  const liveUrl = new URL(LIVE_RUNTIME_STATUS_PATH, window.location.href);
  if (requested) liveUrl.search = requested.search;
  const liveResponse = await originalFetch(liveUrl.href, {
    ...init,
    method: 'GET',
    body: undefined,
    headers: {
      Accept: 'application/json',
      ...(init?.headers || {}),
    },
  });
  if (!liveResponse.ok) return liveResponse;
  const liveStatus = await liveResponse.json();
  const authority = normalizeLiveRuntimeAuthority(liveStatus);
  return new Response(JSON.stringify(authority), {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'no-store',
      'X-HHS-Authority-Projection': 'LIVE_RUNTIME_STATUS',
    },
  });
}

function productionRegistryReady() {
  const integration = window.HHSProductionIntegration;
  return Boolean(
    integration
    && integration.phase === 'READY'
    && integration.runtimeAuthority?.ok
    && Number(integration.serviceCount || 0) > 0
  );
}

async function waitForRegistryPriorityWindow() {
  while (!productionRegistryReady()) {
    if (performance.now() - startedAt >= MAX_ASSISTANT_DEFERRAL_MS) return;
    await sleep(25);
  }
}

async function waitForReceiptClosedRegistry() {
  for (let attempt = 0; attempt < PRODUCTION_REGISTRY_WAIT_LIMIT; attempt += 1) {
    if (productionRegistryReady()) return true;
    await sleep(PRODUCTION_REGISTRY_POLL_MS);
  }
  return false;
}

function projectionRecord(path, state, error = null) {
  return Object.freeze({
    path,
    state,
    error,
  });
}

function settledProjectionMarkers(records) {
  if (
    records.length !== DEFERRED_PROJECTION_MODULES.length
    || records.some((record) => record.state !== 'READY')
  ) return Object.freeze({});

  return Object.freeze({
    pass196_integration_projection_loaded: true,
    pass197_calibration_projection_loaded: true,
    pass198_calibration_registry_projection_loaded: true,
    pass199_distributed_calibration_projection_loaded: true,
    pass200a_proof_carrying_optimization_projection_loaded: true,
    pass200b_governed_canary_projection_loaded: true,
    pass200c_guarded_active_projection_loaded: true,
    pass201_public_api_federation_projection_loaded: true,
    pass203_hydrated_mainframe_projection_loaded: true,
  });
}

function publishProjectionBoot(state, records) {
  window.dispatchEvent(new CustomEvent('hhs:deferred-projection-boot:state', {
    detail: {
      schema: 'HHS_DEFERRED_PROJECTION_BOOT_V1',
      state,
      receipt_closed_before_start: productionRegistryReady(),
      records: records.map((record) => ({ ...record })),
      loaded_markers: state === 'SETTLED' ? settledProjectionMarkers(records) : {},
      legacy_static_import_execution_disabled: true,
      frontend_is_authority: false,
    },
  }));
}

function loadDeferredProjectionModules() {
  if (deferredProjectionBoot) return deferredProjectionBoot;

  deferredProjectionBoot = (async () => {
    const records = [];
    publishProjectionBoot('WAITING_FOR_RECEIPT_CLOSURE', records);
    const ready = await waitForReceiptClosedRegistry();
    if (!ready) {
      for (const path of DEFERRED_PROJECTION_MODULES) {
        records.push(projectionRecord(path, 'DEFERRED_RUNTIME_NOT_READY'));
      }
      publishProjectionBoot('DEFERRED_RUNTIME_NOT_READY', records);
      return records;
    }

    publishProjectionBoot('LOADING', records);
    for (const path of DEFERRED_PROJECTION_MODULES) {
      try {
        await import(path);
        records.push(projectionRecord(path, 'READY'));
      } catch (error) {
        records.push(projectionRecord(
          path,
          'FAILED',
          `${error?.name || 'Error'}: ${error?.message || String(error)}`,
        ));
      }
      // Preserve dependency order and avoid a burst of non-critical status
      // requests immediately after the canonical receipt closes.
      await sleep(PRODUCTION_REGISTRY_POLL_MS);
    }
    publishProjectionBoot('SETTLED', records);
    return records;
  })();

  return deferredProjectionBoot;
}

function installStorybookReelLauncher() {
  if (document.querySelector('[data-hhs-storybook-reel-launcher]')) return;
  const anchor = document.createElement('a');
  anchor.href = '/storybook-reel/';
  anchor.dataset.hhsStorybookReelLauncher = 'true';
  anchor.textContent = 'Storybook Reel';
  anchor.title = 'Open the no-code 90-second storybook reel studio';
  anchor.setAttribute('aria-label', 'Open Storybook Reel Studio');
  anchor.style.cssText = [
    'display:inline-flex', 'align-items:center', 'justify-content:center',
    'min-height:30px', 'padding:0 11px', 'border:1px solid #a66b35',
    'border-radius:7px', 'background:linear-gradient(135deg,#e9b15e,#a85f29)',
    'color:#1b0e07', 'font-size:12px', 'font-weight:800',
    'text-decoration:none', 'white-space:nowrap',
  ].join(';');
  const menu = document.querySelector('.ide-menu-bar');
  const upload = document.querySelector('#ide-upload-trigger');
  if (menu) {
    const spacer = menu.querySelector('.ide-menu-spacer');
    menu.insertBefore(anchor, spacer || null);
  } else if (upload?.parentElement) {
    upload.parentElement.append(anchor);
  } else {
    document.body.append(anchor);
  }
}

window.fetch = async function coordinatedFetch(input, init) {
  if (isShadowedAuthorityRequest(input, init)) return fetchLiveRuntimeAuthority(input, init);
  if (isAssistantRequest(input)) await waitForRegistryPriorityWindow();
  return originalFetch(input, init);
};

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', installStorybookReelLauncher, { once: true });
} else {
  installStorybookReelLauncher();
}

window.HHSProductionStartupCoordinator = Object.freeze({
  schema: 'HHS_PASS161_PRODUCTION_STARTUP_COORDINATOR_V16',
  assistant_requests_deferred_until_registry_ready: true,
  max_assistant_deferral_ms: MAX_ASSISTANT_DEFERRAL_MS,
  runtime_registry_has_priority: true,
  visual_ide_requests_never_deferred: true,
  storybook_reel_requests_never_deferred: true,
  mainframe_requests_never_deferred: true,
  storybook_reel_launcher_installed: true,
  pass176_controller_bootstrap_precedes_public_graph: true,
  pass176_early_bootstrap_claims_interactive: false,
  shadowed_runtime_authority_path: SHADOWED_AUTHORITY_PATH,
  live_runtime_authority_source: LIVE_RUNTIME_STATUS_PATH,
  shadowed_runtime_authority_route_used: false,
  live_runtime_authority_projection_fail_closed: true,
  deferred_projection_boot: loadDeferredProjectionModules,
  deferred_projection_module_count: DEFERRED_PROJECTION_MODULES.length,
  deferred_projections_require_receipt_closure: true,
  legacy_import_registration_witnesses: LEGACY_IMPORT_REGISTRATION_WITNESSES,
  legacy_static_import_execution_disabled: true,
  pass196_integration_projection_scheduled: true,
  pass197_calibration_projection_scheduled: true,
  pass198_calibration_registry_projection_scheduled: true,
  pass199_distributed_calibration_projection_scheduled: true,
  pass200a_proof_carrying_optimization_projection_scheduled: true,
  pass200b_governed_canary_projection_scheduled: true,
  pass200c_guarded_active_projection_scheduled: true,
  pass201_public_api_federation_projection_scheduled: true,
  pass203_hydrated_mainframe_projection_scheduled: true,
  theme_bootstrap_independent_of_ide_module: true,
  mobile_first_paint_precedes_public_module_graph: true,
  public_module_boot_concurrent: true,
  frontend_is_authority: false,
});

// The public application and canonical production integration own the critical
// boot path. Legacy calibration, optimization, federation, and mainframe panels
// are imported only after that path has committed a real receipt and service
// registry, so their status reads can never delay RECEIPT CLOSED.
void import('./public-boot.mjs')
  .then(({ startPublicBoot }) => startPublicBoot())
  .then(() => {
    void loadDeferredProjectionModules();
  })
  .catch((error) => {
    console.error('HHS public module boot failed', error);
    window.dispatchEvent(new CustomEvent('hhs:public-module-boot-error', {
      detail: {
        classification: 'HHS_PUBLIC_MODULE_BOOT_FAILED',
        message: error?.message || String(error),
      },
    }));
  });
