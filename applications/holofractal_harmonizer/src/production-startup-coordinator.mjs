import './theme-bootstrap.mjs';
import { initPreviewReadiness } from './preview-readiness.mjs';
import { startApplicationExperience } from './application-experience.mjs';
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

function installApplicationStudioLauncherInterposition() {
  document.addEventListener('click', (event) => {
    const element = event.target instanceof Element ? event.target : null;
    const commit = element?.closest('#ide-create-application-project');
    if (commit) {
      const requested = String(document.querySelector('#ide-application-name')?.value || '').trim();
      if (requested) {
        const identity = Object.freeze({
          schema: 'HHS_APPLICATION_PROJECT_IDENTITY_V1',
          name: requested,
          requested_at: new Date().toISOString(),
          source: 'APPLICATION_STUDIO_COMMIT',
          frontend_is_authority: false,
        });
        window.HHSPendingApplicationProjectIdentity = identity;
        const input = document.querySelector('#ide-project-name');
        if (input instanceof HTMLInputElement) {
          input.value = requested;
          input.dataset.hhsApplicationStudioOwned = 'true';
        }
        window.dispatchEvent(new CustomEvent('hhs:application-project:identity-requested', { detail: identity }));
      }
      return;
    }

    const target = element?.closest('#ide-new-app');
    if (!target) return;
    const studio = window.HHSApplicationStudio;
    if (!studio || typeof studio.open !== 'function') return;
    event.preventDefault();
    event.stopImmediatePropagation();
    studio.ensurePrimaryControl?.();
    studio.open();
  }, true);
}

window.fetch = async function coordinatedFetch(input, init) {
  if (isAssistantRequest(input)) await waitForRegistryPriorityWindow();
  return originalFetch(input, init);
};

initPreviewReadiness();
installApplicationStudioLauncherInterposition();

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', installStorybookReelLauncher, { once: true });
} else {
  installStorybookReelLauncher();
}

window.HHSProductionStartupCoordinator = Object.freeze({
  schema: 'HHS_PASS161_PRODUCTION_STARTUP_COORDINATOR_V9',
  assistant_requests_deferred_until_registry_ready: true,
  max_assistant_deferral_ms: MAX_ASSISTANT_DEFERRAL_MS,
  runtime_registry_has_priority: true,
  visual_ide_requests_never_deferred: true,
  application_experience_is_awaited_entry_dependency: true,
  application_studio_launcher_capture_interposition: true,
  application_project_identity_captured_before_hydration: true,
  application_preview_readiness_bound_before_hydration: true,
  application_preview_source_window_required: true,
  storybook_reel_requests_never_deferred: true,
  storybook_reel_launcher_installed: true,
  theme_bootstrap_independent_of_ide_module: true,
  public_module_boot_serialized_after_critical_surface: true,
  frontend_is_authority: false,
});

async function startProductionSurface() {
  const applicationExperience = await startApplicationExperience();
  if (!applicationExperience || applicationExperience.state !== 'INTERACTIVE') {
    throw new Error('HHS_PRODUCTION_APPLICATION_EXPERIENCE_NOT_INTERACTIVE');
  }
  const publicBoot = startPublicBoot();
  await publicBoot.applicationExperience;
  await publicBoot.allSettled;
  await startApplicationExperience();
  initPreviewReadiness();
  installStorybookReelLauncher();
  return Object.freeze({
    schema: 'HHS_PRODUCTION_SURFACE_READY_V3',
    application_experience: 'INTERACTIVE',
    public_boot: publicBoot.schema,
    preview_readiness: window.HHSApplicationPreviewReadiness?.schema || null,
    project_identity: window.HHSPendingApplicationProjectIdentity?.schema || null,
    critical_surface_reasserted: true,
    frontend_is_authority: false,
  });
}

const startupReady = startProductionSurface().then((record) => {
  window.HHSProductionSurfaceReady = record;
  window.dispatchEvent(new CustomEvent('hhs:production-surface:ready', { detail: record }));
  return record;
}).catch((error) => {
  const detail = {
    schema: 'HHS_PRODUCTION_SURFACE_FAILURE_V1',
    error: `${error?.name || 'Error'}: ${error?.message || String(error)}`,
    frontend_is_authority: false,
  };
  window.HHSProductionSurfaceFailure = Object.freeze(detail);
  window.dispatchEvent(new CustomEvent('hhs:production-surface:error', { detail }));
  console.error('HHS_PRODUCTION_SURFACE_FAILED', detail);
  throw error;
});

window.HHSProductionStartupReady = startupReady;
