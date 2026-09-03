import './mobile-first-paint-fix.mjs';
import './theme-bootstrap.mjs';
import { startPublicBoot } from './public-boot.mjs';

const deferredProjectionState = {
  pass196_integration_projection_loaded: false,
  pass197_calibration_projection_loaded: false,
  pass198_calibration_registry_projection_loaded: false,
  pass199_distributed_calibration_projection_loaded: false,
  pass200a_proof_carrying_optimization_projection_loaded: false,
  pass200b_governed_canary_projection_loaded: false,
  pass200c_guarded_active_projection_loaded: false,
  pass201_public_api_federation_projection_loaded: false,
  pass203_hydrated_mainframe_projection_loaded: false,
};

const DEFERRED_PROJECTION_READY_COMPAT = Object.freeze({
  pass196_integration_projection_loaded: true,
  pass197_calibration_projection_loaded: true,
  pass198_calibration_registry_projection_loaded: true,
  pass199_distributed_calibration_projection_loaded: true,
  pass200a_proof_carrying_optimization_projection_loaded: true,
  pass200b_governed_canary_projection_loaded: true,
  pass200c_guarded_active_projection_loaded: true,
  pass201_public_api_federation_projection_loaded: true,
  pass203_hydrated_mainframe_projection_loaded: true,
  frontend_is_authority: false,
});

const DEFERRED_PROJECTION_MODULES = Object.freeze([
  ['pass196_integration_projection_loaded', './pass196-integration.mjs'],
  ['pass197_calibration_projection_loaded', './pass197-calibration.mjs'],
  ['pass198_calibration_registry_projection_loaded', './pass198-calibration-registry.mjs'],
  ['pass199_distributed_calibration_projection_loaded', './pass199-distributed-calibration.mjs'],
  ['pass200a_proof_carrying_optimization_projection_loaded', './pass200a-proof-carrying-optimization.mjs'],
  ['pass200b_governed_canary_projection_loaded', './pass200b-governed-canary.mjs'],
  ['pass200c_guarded_active_projection_loaded', './pass200c-guarded-active.mjs'],
  ['pass201_public_api_federation_projection_loaded', './pass201-public-api-federation.mjs'],
  ['pass203_hydrated_mainframe_projection_loaded', './pass203-mainframe.mjs'],
]);

async function loadDeferredProjections() {
  const results = await Promise.allSettled(
    DEFERRED_PROJECTION_MODULES.map(async ([flag, modulePath]) => {
      await import(modulePath);
      deferredProjectionState[flag] = true;
      return modulePath;
    }),
  );
  window.dispatchEvent(new CustomEvent('hhs:deferred-projections:settled', {
    detail: {
      schema: 'HHS_DEFERRED_PROJECTION_BOOT_V1',
      results: results.map((result, index) => ({
        module: DEFERRED_PROJECTION_MODULES[index][1],
        state: result.status === 'fulfilled' ? 'READY' : 'FAILED',
        error: result.status === 'rejected'
          ? `${result.reason?.name || 'Error'}: ${result.reason?.message || String(result.reason)}`
          : null,
      })),
      frontend_is_authority: false,
    },
  }));
  return results;
}

const originalFetch = window.fetch.bind(window);
const startedAt = performance.now();
const MAX_ASSISTANT_DEFERRAL_MS = 1_500;

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
  return Boolean(window.HHSProductionIntegration && Number(window.HHSProductionIntegration.serviceCount || 0) > 0);
}

async function waitForRegistryPriorityWindow() {
  while (!productionRegistryReady()) {
    if (performance.now() - startedAt >= MAX_ASSISTANT_DEFERRAL_MS) return;
    await new Promise((resolve) => window.setTimeout(resolve, 25));
  }
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
  schema: 'HHS_PASS161_PRODUCTION_STARTUP_COORDINATOR_V15',
  assistant_requests_deferred_until_registry_ready: true,
  max_assistant_deferral_ms: MAX_ASSISTANT_DEFERRAL_MS,
  runtime_registry_has_priority: true,
  visual_ide_requests_never_deferred: true,
  storybook_reel_requests_never_deferred: true,
  mainframe_requests_never_deferred: true,
  storybook_reel_launcher_installed: true,
  get pass196_integration_projection_loaded() { return deferredProjectionState.pass196_integration_projection_loaded; },
  get pass197_calibration_projection_loaded() { return deferredProjectionState.pass197_calibration_projection_loaded; },
  get pass198_calibration_registry_projection_loaded() { return deferredProjectionState.pass198_calibration_registry_projection_loaded; },
  get pass199_distributed_calibration_projection_loaded() { return deferredProjectionState.pass199_distributed_calibration_projection_loaded; },
  get pass200a_proof_carrying_optimization_projection_loaded() { return deferredProjectionState.pass200a_proof_carrying_optimization_projection_loaded; },
  get pass200b_governed_canary_projection_loaded() { return deferredProjectionState.pass200b_governed_canary_projection_loaded; },
  get pass200c_guarded_active_projection_loaded() { return deferredProjectionState.pass200c_guarded_active_projection_loaded; },
  get pass201_public_api_federation_projection_loaded() { return deferredProjectionState.pass201_public_api_federation_projection_loaded; },
  get pass203_hydrated_mainframe_projection_loaded() { return deferredProjectionState.pass203_hydrated_mainframe_projection_loaded; },
  deferred_projection_boot: true,
  deferred_projection_ready_compat: DEFERRED_PROJECTION_READY_COMPAT,
  deferred_projection_boot_waits_for_public_graph: true,
  theme_bootstrap_independent_of_ide_module: true,
  mobile_first_paint_precedes_public_module_graph: true,
  public_module_boot_concurrent: true,
  synchronous_public_boot_handoff: true,
  frontend_is_authority: false,
});

try {
  const publicBoot = startPublicBoot();
  void publicBoot.allSettled.finally(() => {
    void loadDeferredProjections();
  });
} catch (error) {
  console.error('HHS public module boot failed', error);
  window.dispatchEvent(new CustomEvent('hhs:public-module-boot-error', {
    detail: {
      classification: 'HHS_PUBLIC_MODULE_BOOT_FAILED',
      message: error?.message || String(error),
    },
  }));
}
