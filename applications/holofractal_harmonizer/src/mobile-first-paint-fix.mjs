const MOBILE_QUERY = '(max-width: 980px)';
const mobile = globalThis.matchMedia?.(MOBILE_QUERY) ?? { matches: false };
const body = document.body;
const ideView = document.querySelector('#ide-view');
const ideLayout = document.querySelector('#ide-layout');
const registry = document.querySelector('#registry-nav');
const inspector = document.querySelector('#inspector');
const navToggle = document.querySelector('#nav-toggle');
const inspectToggle = document.querySelector('#inspect-toggle');
const mobileDock = document.querySelector('.ide-mobile-dock');

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
  document.querySelectorAll('.workflow-mobile-tabs').forEach((tabs) => {
    if (!tabs.hidden) tabs.hidden = true;
    if (!tabs.inert) tabs.inert = true;
    if (tabs.getAttribute('aria-hidden') !== 'true') tabs.setAttribute('aria-hidden', 'true');
  });
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

function enforceVisualIdeSurface() {
  if (!body.classList.contains('visual-ide-active')) return;
  if (ideView?.hidden) ideView.hidden = false;
  for (const selector of ['#assistant-view', '#workspace-view', '#spatial-view', '#api-view']) {
    const view = document.querySelector(selector);
    if (view && !view.hidden) view.hidden = true;
  }
}

navToggle?.addEventListener('click', (event) => {
  event.preventDefault();
  event.stopImmediatePropagation();
  setExplorerOpen(!registry?.classList.contains('open'));
}, { capture: true });

inspectToggle?.addEventListener('click', (event) => {
  event.preventDefault();
  event.stopImmediatePropagation();
  setInspectorOpen(!inspector?.classList.contains('open'));
}, { capture: true });

mobileDock?.addEventListener('click', (event) => {
  const button = event.target.closest('button[data-mobile-pane]');
  if (!button) return;
  event.preventDefault();
  event.stopImmediatePropagation();

  const pane = button.dataset.mobilePane || 'editor';
  mobileDock.querySelectorAll('button[data-mobile-pane]').forEach((candidate) => {
    candidate.classList.toggle('active', candidate === button);
  });

  if (pane === 'explorer') {
    setExplorerOpen(true);
    return;
  }

  setExplorerOpen(false);
  setInspectorOpen(false);
  if (ideLayout) ideLayout.dataset.mobilePane = pane;
}, { capture: true });

document.addEventListener('click', (event) => {
  if (!mobile.matches) return;
  if (event.target.closest('.ide-file-item, .ide-editor-tab, #ide-new-file')) {
    queueMicrotask(() => setExplorerOpen(false));
  }
}, { capture: true });

document.addEventListener('keydown', (event) => {
  if (event.key !== 'Escape') return;
  setExplorerOpen(false);
  setInspectorOpen(false);
});

let observerScheduled = false;
const observer = new MutationObserver(() => {
  if (observerScheduled) return;
  observerScheduled = true;
  queueMicrotask(() => {
    observerScheduled = false;
    suppressLegacyMobileTabs();
    enforceVisualIdeSurface();
  });
});
observer.observe(body, {
  subtree: true,
  childList: true,
  attributes: true,
  attributeFilter: ['class', 'hidden'],
});

const handleViewportChange = () => {
  if (!mobile.matches) {
    setExplorerOpen(false);
    setInspectorOpen(false);
  }
};
mobile.addEventListener?.('change', handleViewportChange);

suppressLegacyMobileTabs();
enforceVisualIdeSurface();

window.HHSMobileFirstPaintFix = Object.freeze({
  schema: 'HHS_MOBILE_FIRST_PAINT_AND_OVERLAY_OWNERSHIP_V1',
  setExplorerOpen,
  setInspectorOpen,
  enforceVisualIdeSurface,
  suppressLegacyMobileTabs,
});
