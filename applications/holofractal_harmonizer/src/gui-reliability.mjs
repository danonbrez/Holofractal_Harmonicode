const STYLE_ID = 'hhs-gui-reliability-style';
const MOBILE_QUERY = '(max-width: 980px)';
const PANE_STORAGE_KEY = 'hhs.visualIde.mobilePane.v2';
const VALID_PANES = new Set(['editor', 'lifecycle', 'terminal', 'spatial']);

function $(selector, root = document) {
  return root.querySelector(selector);
}

function $$(selector, root = document) {
  return [...root.querySelectorAll(selector)];
}

function loadReliabilityStyle() {
  if (document.getElementById(STYLE_ID)) return;
  const link = document.createElement('link');
  link.id = STYLE_ID;
  link.rel = 'stylesheet';
  link.href = './src/gui-reliability.css';
  document.head.append(link);
}

loadReliabilityStyle();

const ready = () => new Promise((resolve) => {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', resolve, { once: true });
  } else {
    resolve();
  }
});

await ready();

const surfaces = {
  command: () => $('#workflow-command-palette'),
  explorer: () => $('#registry-nav'),
  inspector: () => $('#inspector'),
};

const state = {
  activeSurface: null,
  returnFocus: null,
  historyMarked: false,
  suppressNextPop: false,
};

function isMobile() {
  return window.matchMedia(MOBILE_QUERY).matches;
}

function isSurfaceOpen(name) {
  const element = surfaces[name]?.();
  if (!element) return false;
  if (name === 'command') return !element.hidden;
  return isMobile() && element.classList.contains('open');
}

function setSurfaceOpen(name, open) {
  const element = surfaces[name]?.();
  if (!element) return;
  if (name === 'command') element.hidden = !open;
  else {
    if (!isMobile()) return;
    element.classList.toggle('open', open);
  }
  element.setAttribute('aria-hidden', String(!open));
  if (open) {
    element.setAttribute('aria-modal', 'true');
    element.setAttribute('role', name === 'command' ? 'dialog' : 'region');
  } else {
    element.removeAttribute('aria-modal');
  }
}

function syncScrim() {
  const open = Boolean(state.activeSurface && isSurfaceOpen(state.activeSurface));
  const scrim = $('#hhs-mobile-scrim');
  if (scrim) scrim.hidden = !open;
  document.body.classList.toggle('hhs-transient-open', open);
  document.documentElement.dataset.hhsActiveSurface = open ? state.activeSurface : 'none';
}

function markHistory(name) {
  if (state.historyMarked || history.state?.hhsTransientSurface) return;
  history.pushState({ ...(history.state || {}), hhsTransientSurface: name }, '');
  state.historyMarked = true;
}

function clearHistoryMarker() {
  if (!state.historyMarked || !history.state?.hhsTransientSurface) {
    state.historyMarked = false;
    return;
  }
  state.historyMarked = false;
  state.suppressNextPop = true;
  history.back();
}

function focusFirst(surface) {
  const target = surface?.querySelector(
    '[autofocus], input:not([disabled]), textarea:not([disabled]), select:not([disabled]), button:not([disabled]), [tabindex]:not([tabindex="-1"])',
  );
  target?.focus({ preventScroll: true });
}

function closeAll({ restoreFocus = true, fromPopState = false } = {}) {
  for (const name of Object.keys(surfaces)) setSurfaceOpen(name, false);
  const priorFocus = state.returnFocus;
  state.activeSurface = null;
  state.returnFocus = null;
  syncScrim();
  if (!fromPopState) clearHistoryMarker();
  if (restoreFocus && priorFocus instanceof HTMLElement && priorFocus.isConnected) {
    window.setTimeout(() => priorFocus.focus({ preventScroll: true }), 0);
  }
}

function activateSurface(name, { focus = true } = {}) {
  if (!surfaces[name]?.()) return;
  if (!state.activeSurface) {
    state.returnFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null;
  }
  for (const other of Object.keys(surfaces)) setSurfaceOpen(other, other === name);
  state.activeSurface = name;
  markHistory(name);
  syncScrim();
  if (focus) window.setTimeout(() => focusFirst(surfaces[name]()), 0);
}

function reconcileSurfaceState(preferred = null) {
  const openNames = Object.keys(surfaces).filter(isSurfaceOpen);
  if (!openNames.length) {
    if (state.activeSurface) closeAll({ restoreFocus: false });
    return;
  }
  const selected = preferred && openNames.includes(preferred)
    ? preferred
    : openNames.includes('command')
      ? 'command'
      : openNames.at(-1);
  activateSurface(selected, { focus: false });
}

function createCloseButton(label, className = 'hhs-surface-close') {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = className;
  button.setAttribute('aria-label', label);
  button.title = label;
  button.textContent = '×';
  button.addEventListener('click', (event) => {
    event.preventDefault();
    event.stopPropagation();
    closeAll();
  });
  return button;
}

function installCommandPaletteChrome() {
  const overlay = surfaces.command();
  const card = overlay?.querySelector('.workflow-command-card');
  if (!overlay || !card || card.querySelector('.hhs-command-toolbar')) return;
  overlay.dataset.hhsTransientSurface = 'command';
  overlay.setAttribute('aria-label', 'IDE command palette');
  const toolbar = document.createElement('div');
  toolbar.className = 'hhs-command-toolbar';
  const title = document.createElement('div');
  title.className = 'hhs-command-title';
  title.innerHTML = '<strong>Command Center</strong><small>Workflows, files, objects, and services</small>';
  toolbar.append(title, createCloseButton('Close command center'));
  card.prepend(toolbar);
}

function installSheetClose(selector, label) {
  const sheet = $(selector);
  const heading = sheet?.querySelector('.panel-heading');
  if (!sheet || !heading || heading.querySelector('.hhs-surface-close')) return;
  sheet.dataset.hhsTransientSurface = selector === '#registry-nav' ? 'explorer' : 'inspector';
  heading.append(createCloseButton(label));
}

function installScrim() {
  if ($('#hhs-mobile-scrim')) return;
  const scrim = document.createElement('button');
  scrim.id = 'hhs-mobile-scrim';
  scrim.type = 'button';
  scrim.hidden = true;
  scrim.tabIndex = -1;
  scrim.setAttribute('aria-label', 'Close open panel');
  scrim.addEventListener('click', () => closeAll());
  document.body.append(scrim);
}

function currentPane() {
  const stored = localStorage.getItem(PANE_STORAGE_KEY);
  return VALID_PANES.has(stored) ? stored : 'editor';
}

function selectMobilePane(pane, { persist = true } = {}) {
  if (!VALID_PANES.has(pane)) return;
  const layout = $('#ide-layout');
  if (!layout) return;
  layout.dataset.mobilePane = pane;
  $$('.ide-mobile-dock [data-mobile-pane]').forEach((button) => {
    const selected = button.dataset.mobilePane === pane;
    button.classList.toggle('active', selected);
    button.setAttribute('aria-current', selected ? 'page' : 'false');
    button.setAttribute('aria-pressed', String(selected));
  });
  if (persist) localStorage.setItem(PANE_STORAGE_KEY, pane);
  closeAll({ restoreFocus: false });
}

function installMobilePaneController() {
  const layout = $('#ide-layout');
  const dock = $('.ide-mobile-dock');
  if (!layout || !dock) return;
  dock.setAttribute('role', 'tablist');
  $$('.ide-mobile-dock [data-mobile-pane]').forEach((button) => {
    button.setAttribute('role', 'tab');
    button.addEventListener('click', () => {
      const pane = button.dataset.mobilePane;
      window.queueMicrotask(() => {
        if (pane === 'explorer') {
          activateSurface('explorer');
          return;
        }
        selectMobilePane(pane);
      });
    }, true);
  });
  window.requestAnimationFrame(() => selectMobilePane(currentPane(), { persist: false }));
}

function setViewportHeight() {
  const height = window.visualViewport?.height || window.innerHeight;
  document.documentElement.style.setProperty('--hhs-app-height', `${Math.round(height)}px`);
}

function trapFocus(event) {
  if (event.key !== 'Tab' || !state.activeSurface) return;
  const surface = surfaces[state.activeSurface]?.();
  if (!surface) return;
  const focusable = $$('[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])', surface)
    .filter((element) => !element.hidden && element.getClientRects().length > 0);
  if (!focusable.length) return;
  const first = focusable[0];
  const last = focusable.at(-1);
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

installScrim();
installCommandPaletteChrome();
installSheetClose('#registry-nav', 'Close explorer');
installSheetClose('#inspector', 'Close inspector');
installMobilePaneController();
setViewportHeight();

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && state.activeSurface) {
    event.preventDefault();
    event.stopImmediatePropagation();
    closeAll();
    return;
  }
  trapFocus(event);
}, true);

document.addEventListener('click', (event) => {
  const target = event.target instanceof Element ? event.target : null;
  if (!target) return;
  if (target.closest('#nav-toggle, [data-mobile-pane="explorer"]')) {
    window.queueMicrotask(() => reconcileSurfaceState('explorer'));
    return;
  }
  if (target.closest('#inspect-toggle')) {
    window.queueMicrotask(() => reconcileSurfaceState('inspector'));
    return;
  }
  if (isMobile() && target.closest('#registry-nav .ide-file-item, #registry-nav [data-object-id]')) {
    window.queueMicrotask(() => closeAll({ restoreFocus: false }));
  }
}, true);

document.addEventListener('focusin', (event) => {
  if (event.target === $('#object-search')) {
    window.setTimeout(() => reconcileSurfaceState('command'), 0);
  }
}, true);

window.addEventListener('popstate', () => {
  if (state.suppressNextPop) {
    state.suppressNextPop = false;
    return;
  }
  state.historyMarked = false;
  if (state.activeSurface) closeAll({ fromPopState: true });
});

const media = window.matchMedia(MOBILE_QUERY);
const handleMediaChange = () => {
  if (!media.matches) {
    $('#registry-nav')?.classList.remove('open');
    $('#inspector')?.classList.remove('open');
    closeAll({ restoreFocus: false });
  } else selectMobilePane(currentPane(), { persist: false });
  setViewportHeight();
};
media.addEventListener?.('change', handleMediaChange);
window.addEventListener('resize', setViewportHeight, { passive: true });
window.addEventListener('orientationchange', setViewportHeight, { passive: true });
window.visualViewport?.addEventListener('resize', setViewportHeight, { passive: true });

const observer = new MutationObserver(() => {
  installCommandPaletteChrome();
  window.queueMicrotask(() => reconcileSurfaceState());
});
for (const name of Object.keys(surfaces)) {
  const element = surfaces[name]?.();
  if (element) observer.observe(element, { attributes: true, attributeFilter: ['class', 'hidden'] });
}

document.documentElement.dataset.hhsGuiReliability = 'ready';
window.HHSGUIReliability = Object.freeze({
  schema: 'HHS_GUI_RELIABILITY_OVERLAY_MANAGER_V1',
  closeAll,
  activateSurface,
  selectMobilePane,
  get activeSurface() { return state.activeSurface; },
  get mobilePane() { return $('#ide-layout')?.dataset.mobilePane || 'editor'; },
});
