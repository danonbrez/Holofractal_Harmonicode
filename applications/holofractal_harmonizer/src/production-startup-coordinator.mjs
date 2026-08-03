import './mobile-first-paint-fix.mjs';
import './theme-bootstrap.mjs';

const originalFetch = window.fetch.bind(window);
const startedAt = performance.now();
const MAX_ASSISTANT_DEFERRAL_MS = 1_500;
const PRODUCTION_REGISTRY_WAIT_LIMIT = 2_400;
const PRODUCTION_REGISTRY_POLL_MS = 25;
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
let deferredProjectionBoot = null;

const sleep = (milliseconds) => new Promise((resolve) => window.setTimeout(resolve, milliseconds));

function isAssistantRequest(input) {
  const raw = typeof input === 'string' ? input : input?.url || '';
  try {
    const url = new URL(raw, window.location.href);
    return url.origin === window.location.origin && url.pathname.startsWith('/api/assistant/');
  } catch {
    return false;
  }
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

function publishProjectionBoot(state, records) {
  window.dispatchEvent(new CustomEvent('hhs:deferred-projection-boot:state', {
    detail: {
      schema: 'HHS_DEFERRED_PROJECTION_BOOT_V1',
      state,
      receipt_closed_before_start: productionRegistryReady(),
      records: records.map((record) => ({ ...record })),
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
  if (isAssistantRequest(input)) await waitForRegistryPriorityWindow();
  return originalFetch(input, init);
};

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', installStorybookReelLauncher, { once: true });
} else {
  installStorybookReelLauncher();
}

window.HHSProductionStartupCoordinator = Object.freeze({
  schema: 'HHS_PASS161_PRODUCTION_STARTUP_COORDINATOR_V14',
  assistant_requests_deferred_until_registry_ready: true,
  max_assistant_deferral_ms: MAX_ASSISTANT_DEFERRAL_MS,
  runtime_registry_has_priority: true,
  visual_ide_requests_never_deferred: true,
  storybook_reel_requests_never_deferred: true,
  mainframe_requests_never_deferred: true,
  storybook_reel_launcher_installed: true,
  deferred_projection_boot: loadDeferredProjectionModules,
  deferred_projection_module_count: DEFERRED_PROJECTION_MODULES.length,
  deferred_projections_require_receipt_closure: true,
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
  .then(({ startPublicBoot }) => {
    const boot = startPublicBoot();
    void loadDeferredProjectionModules();
    return boot;
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
