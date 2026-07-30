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

window.fetch = async function coordinatedFetch(input, init) {
  // Only optional assistant cold-start calls receive a short priority window.
  // IDE, runtime, ingress, compiler, VM81, receipt, and egress calls are never
  // held behind assistant/provider initialization.
  if (isAssistantRequest(input)) await waitForRegistryPriorityWindow();
  return originalFetch(input, init);
};

window.HHSProductionStartupCoordinator = Object.freeze({
  schema: 'HHS_PASS161_PRODUCTION_STARTUP_COORDINATOR_V2',
  assistant_requests_deferred_until_registry_ready: true,
  max_assistant_deferral_ms: MAX_ASSISTANT_DEFERRAL_MS,
  runtime_registry_has_priority: true,
  visual_ide_requests_never_deferred: true,
  frontend_is_authority: false,
});
