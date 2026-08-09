const MOBILE_QUERY = '(max-width: 980px)';
const mobile = globalThis.matchMedia?.(MOBILE_QUERY) ?? { matches: false };
const body = document.body;
const ideView = document.querySelector('#ide-view');
const ideLayout = document.querySelector('#ide-layout');
const registry = document.querySelector('#registry-nav');
const inspector = document.querySelector('#inspector');
const navToggle = document.querySelector('#nav-toggle');
const inspectToggle = document.querySelector('#inspect-toggle');

body.classList.add('visual-ide-active', 'hhs-mobile-first-paint');
if (ideLayout && !ideLayout.dataset.mobilePane) ideLayout.dataset.mobilePane = 'editor';

const style = document.createElement('style');
style.id = 'hhs-mobile-first-paint-style';
style.textContent = `
@media (max-width: 980px) {
  body.visual-ide-active .workflow-mobile-tabs {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
  }
  body.visual-ide-active #registry-nav:not(.open),
  body.visual-ide-active #inspector:not(.open) {
    visibility: hidden;
    pointer-events: none;
  }
  body.visual-ide-active #registry-nav.open,
  body.visual-ide-active #inspector.open {
    visibility: visible;
    pointer-events: auto;
  }
  body.visual-ide-active .ide-mobile-dock {
    transition: opacity 140ms ease, transform 140ms ease;
  }
  body.visual-ide-active.mobile-explorer-open .ide-mobile-dock,
  body.visual-ide-active.mobile-inspector-open .ide-mobile-dock {
    opacity: 0;
    pointer-events: none;
    transform: translateY(120%);
  }
  body.visual-ide-active .ide-menu-bar {
    position: relative;
    z-index: 2;
  }
}
`;
if (!document.querySelector(`#${style.id}`)) document.head.append(style);

function suppressLegacyMobileTabs() {
  let suppressed = 0;
  document.querySelectorAll('.workflow-mobile-tabs').forEach((tabs) => {
    suppressed += 1;
    if (!tabs.hidden) tabs.hidden = true;
    if (!tabs.inert) tabs.inert = true;
    if (tabs.getAttribute('aria-hidden') !== 'true') tabs.setAttribute('aria-hidden', 'true');
  });
  return suppressed;
}

function setExplorerOpen(open) {
  const next = Boolean(open && mobile.matches);
  registry?.classList.toggle('open', next);
  body.classList.toggle('mobile-explorer-open', next);
  if (next) {
    inspector?.classList.remove('open');
    body.classList.remove('mobile-inspector-open', 'advanced-open');
  }
  if (navToggle?.getAttribute('aria-expanded') !== String(next)) {
    navToggle?.setAttribute('aria-expanded', String(next));
  }
}

function setInspectorOpen(open) {
  const next = Boolean(open && mobile.matches);
  inspector?.classList.toggle('open', next);
  body.classList.toggle('mobile-inspector-open', next);
  if (next) {
    registry?.classList.remove('open');
    body.classList.remove('mobile-explorer-open');
  }
  if (inspectToggle?.getAttribute('aria-expanded') !== String(next)) {
    inspectToggle?.setAttribute('aria-expanded', String(next));
  }
}

function enforceInitialVisualIdeSurface() {
  if (ideView?.hidden) ideView.hidden = false;
  for (const selector of ['#assistant-view', '#workspace-view', '#spatial-view', '#api-view']) {
    const view = document.querySelector(selector);
    if (view && !view.hidden) view.hidden = true;
  }
}

// This module owns first paint only. Canonical interaction ownership belongs to
// gui-reliability.mjs and visual-ide.mjs after their listeners are installed.
// Do not intercept clicks here: capture-phase stopImmediatePropagation previously
// prevented those canonical handlers from running while still allowing CSS active
// state changes, producing highlighted controls with no completed action.
enforceInitialVisualIdeSurface();

let legacyTabObserver = null;
if (!suppressLegacyMobileTabs()) {
  let observerScheduled = false;
  legacyTabObserver = new MutationObserver(() => {
    if (observerScheduled) return;
    observerScheduled = true;
    queueMicrotask(() => {
      observerScheduled = false;
      if (suppressLegacyMobileTabs() > 0) {
        legacyTabObserver?.disconnect();
        legacyTabObserver = null;
      }
    });
  });
  legacyTabObserver.observe(body, { subtree: true, childList: true });
  window.setTimeout(() => {
    legacyTabObserver?.disconnect();
    legacyTabObserver = null;
  }, 15_000);
}

const handleViewportChange = () => {
  if (!mobile.matches) {
    setExplorerOpen(false);
    setInspectorOpen(false);
  }
};
mobile.addEventListener?.('change', handleViewportChange);

window.HHSMobileFirstPaintFix = Object.freeze({
  schema: 'HHS_MOBILE_FIRST_PAINT_AND_OVERLAY_OWNERSHIP_V1',
  interactive_input_owner: false,
  setExplorerOpen,
  setInspectorOpen,
  enforceInitialVisualIdeSurface,
  suppressLegacyMobileTabs,
});
