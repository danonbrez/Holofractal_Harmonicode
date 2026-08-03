import './mobile-first-paint-fix.mjs';
import './theme-bootstrap.mjs';
import './pass196-integration.mjs';
import './pass197-calibration.mjs';
import './pass198-calibration-registry.mjs';
import './pass199-distributed-calibration.mjs';
import './pass200a-proof-carrying-optimization.mjs';
import './pass200b-governed-canary.mjs';
import './pass200c-guarded-active.mjs';
import './pass201-public-api-federation.mjs';
import './pass203-mainframe.mjs';

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
  schema: 'HHS_PASS161_PRODUCTION_STARTUP_COORDINATOR_V13',
  assistant_requests_deferred_until_registry_ready: true,
  max_assistant_deferral_ms: MAX_ASSISTANT_DEFERRAL_MS,
  runtime_registry_has_priority: true,
  visual_ide_requests_never_deferred: true,
  storybook_reel_requests_never_deferred: true,
  mainframe_requests_never_deferred: true,
  storybook_reel_launcher_installed: true,
  pass196_integration_projection_loaded: true,
  pass197_calibration_projection_loaded: true,
  pass198_calibration_registry_projection_loaded: true,
  pass199_distributed_calibration_projection_loaded: true,
  pass200a_proof_carrying_optimization_projection_loaded: true,
  pass200b_governed_canary_projection_loaded: true,
  pass200c_guarded_active_projection_loaded: true,
  pass201_public_api_federation_projection_loaded: true,
  pass203_hydrated_mainframe_projection_loaded: true,
  theme_bootstrap_independent_of_ide_module: true,
  mobile_first_paint_precedes_public_module_graph: true,
  public_module_boot_concurrent: true,
  frontend_is_authority: false,
});

void import('./public-boot.mjs')
  .then(({ startPublicBoot }) => startPublicBoot())
  .catch((error) => {
    console.error('HHS public module boot failed', error);
    window.dispatchEvent(new CustomEvent('hhs:public-module-boot-error', {
      detail: {
        classification: 'HHS_PUBLIC_MODULE_BOOT_FAILED',
        message: error?.message || String(error),
      },
    }));
  });
