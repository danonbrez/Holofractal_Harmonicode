import './theme-bootstrap.mjs';
import { startPublicBoot } from './public-boot.mjs';

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
  return Boolean(
    window.HHSProductionIntegration
    && Number(window.HHSProductionIntegration.serviceCount || 0) > 0
  );
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
    'display:inline-flex',
    'align-items:center',
    'justify-content:center',
    'min-height:30px',
    'padding:0 11px',
    'border:1px solid #a66b35',
    'border-radius:7px',
    'background:linear-gradient(135deg,#e9b15e,#a85f29)',
    'color:#1b0e07',
    'font-size:12px',
    'font-weight:800',
    'text-decoration:none',
    'white-space:nowrap',
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
  // Only optional assistant cold-start calls receive a short priority window.
  // IDE, runtime, ingress, compiler, VM81, receipt, egress, and storybook-reel
  // calls are never held behind assistant/provider initialization.
  if (isAssistantRequest(input)) await waitForRegistryPriorityWindow();
  return originalFetch(input, init);
};

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', installStorybookReelLauncher, { once: true });
} else {
  installStorybookReelLauncher();
}

window.HHSProductionStartupCoordinator = Object.freeze({
  schema: 'HHS_PASS161_PRODUCTION_STARTUP_COORDINATOR_V4',
  assistant_requests_deferred_until_registry_ready: true,
  max_assistant_deferral_ms: MAX_ASSISTANT_DEFERRAL_MS,
  runtime_registry_has_priority: true,
  visual_ide_requests_never_deferred: true,
  storybook_reel_requests_never_deferred: true,
  storybook_reel_launcher_installed: true,
  theme_bootstrap_independent_of_ide_module: true,
  public_module_boot_concurrent: true,
  frontend_is_authority: false,
});

// This is the first public entry module. Launch the browser runtime,
// production registry integration, and visual IDE independently now, before
// any unresolved legacy module can serialize the remaining deferred scripts.
startPublicBoot();
