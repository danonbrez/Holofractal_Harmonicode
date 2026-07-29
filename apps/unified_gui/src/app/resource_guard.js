const MAX_ATTEMPTS = 120;
let attempts = 0;

function enforceStepOnlyDiagnostic() {
  const app = globalThis.HHSApp;
  if (!app?.physics) return false;

  app._stopPhysicsClock?.();
  app.physics.pause();

  const toggle = document.querySelector("#physics-toggle");
  if (toggle) {
    toggle.textContent = "Paused · use Step";
    toggle.disabled = true;
    toggle.setAttribute("aria-disabled", "true");
    toggle.title = "Continuous animation is disabled in hosted diagnostic mode.";
  }

  const status = document.querySelector("#boot-status");
  if (status) status.textContent = "READY · STEP-ONLY DIAGNOSTIC";

  app.refreshDiagnostics?.();
  return true;
}

const timer = window.setInterval(() => {
  attempts += 1;
  if (enforceStepOnlyDiagnostic() || attempts >= MAX_ATTEMPTS) {
    window.clearInterval(timer);
  }
}, 25);

document.addEventListener("visibilitychange", () => {
  if (document.hidden) globalThis.HHSApp?._stopPhysicsClock?.();
});
