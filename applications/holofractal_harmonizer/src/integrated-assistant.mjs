const $ = (selector) => document.querySelector(selector);

let assistantOpen = false;
let initialized = false;
let providerObserver = null;
let providerTimer = null;
let focusTimer = null;
let refreshPromise = null;
let lastRefreshAt = 0;
const REFRESH_COOLDOWN_MS = 5000;

function syncCommandState() {
  const state = $('#ide-assistant-command-state');
  const provider = $('#provider-status');
  if (!state) return;
  const label = provider?.textContent || '';
  const ready = Boolean(window.HHSAssistant && !/OFFLINE|DEGRADED|ERROR/i.test(label));
  state.textContent = ready ? 'READY' : window.HHSAssistant ? 'DEGRADED' : 'BOOT';
  state.dataset.state = ready ? 'ready' : 'degraded';
}

function focusPrompt() {
  if (focusTimer !== null) window.clearTimeout(focusTimer);
  focusTimer = window.setTimeout(() => {
    focusTimer = null;
    $('#prompt-input')?.focus();
  }, 80);
}

function refreshAssistantStatusBounded() {
  const refresh = window.HHSAssistant?.refreshStatus;
  if (typeof refresh !== 'function') return null;
  const now = Date.now();
  if (refreshPromise || now - lastRefreshAt < REFRESH_COOLDOWN_MS) return refreshPromise;
  lastRefreshAt = now;
  refreshPromise = Promise.resolve()
    .then(() => refresh.call(window.HHSAssistant))
    .catch((error) => {
      window.dispatchEvent(new CustomEvent('hhs:assistant:status-refresh-error', {
        detail: {
          classification: 'HHS_P176_ASSISTANT_STATUS_REFRESH_DEFERRED',
          message: error?.message || String(error),
        },
      }));
      return null;
    })
    .finally(() => { refreshPromise = null; });
  return refreshPromise;
}

export function openIntegratedAssistant() {
  const view = $('#assistant-view');
  const ide = $('#ide-view');
  if (!view) return;
  assistantOpen = true;
  if (ide) ide.hidden = false;
  view.hidden = false;
  document.body.classList.add('visual-ide-active', 'ide-assistant-open');
  $('#assistant-home')?.classList.add('active');
  $('#ide-menu-assistant')?.classList.add('active');
  $('#ide-assistant-fab')?.classList.add('active');
  syncCommandState();
  void refreshAssistantStatusBounded();
  focusPrompt();
}

export function closeIntegratedAssistant() {
  const view = $('#assistant-view');
  assistantOpen = false;
  if (view) view.hidden = true;
  document.body.classList.remove('ide-assistant-open');
  $('#assistant-home')?.classList.remove('active');
  $('#ide-menu-assistant')?.classList.remove('active');
  $('#ide-assistant-fab')?.classList.remove('active');
  if (focusTimer !== null) {
    window.clearTimeout(focusTimer);
    focusTimer = null;
  }
}

export function toggleIntegratedAssistant() {
  if (assistantOpen) closeIntegratedAssistant();
  else openIntegratedAssistant();
}

function moveAssistantIntoDrawer() {
  const view = $('#assistant-view');
  const shell = $('#harmonizer');
  if (!view || !shell || $('#ide-assistant-drawer')) return;

  const drawer = document.createElement('aside');
  drawer.id = 'ide-assistant-drawer';
  drawer.className = 'ide-assistant-drawer';
  drawer.setAttribute('aria-label', 'Integrated natural-language development assistant');
  drawer.append(view);
  shell.append(drawer);
  view.hidden = true;

  const actions = view.querySelector('.workspace-actions');
  if (actions && !$('#ide-assistant-close')) {
    const close = document.createElement('button');
    close.id = 'ide-assistant-close';
    close.type = 'button';
    close.textContent = 'Close Assistant';
    close.onclick = closeIntegratedAssistant;
    actions.append(close);
  }
}

function mountDesktopCommand() {
  const menu = document.querySelector('.ide-menu-bar');
  const api = $('#open-api');
  if (!menu || !api || $('#ide-menu-assistant')) return;
  const button = document.createElement('button');
  button.id = 'ide-menu-assistant';
  button.type = 'button';
  button.className = 'ide-assistant-command';
  button.innerHTML = '<span>Assistant</span><small id="ide-assistant-command-state" data-state="boot">BOOT</small>';
  button.onclick = toggleIntegratedAssistant;
  menu.insertBefore(button, api);
}

function mountMobileCommand() {
  const dock = document.querySelector('.ide-mobile-dock');
  if (!dock || $('#ide-mobile-assistant')) return;
  const button = document.createElement('button');
  button.id = 'ide-mobile-assistant';
  button.type = 'button';
  button.textContent = 'Assistant';
  button.onclick = toggleIntegratedAssistant;
  dock.insertBefore(button, dock.lastElementChild);
}

function mountPersistentLauncher() {
  if ($('#ide-assistant-fab')) return;
  const button = document.createElement('button');
  button.id = 'ide-assistant-fab';
  button.type = 'button';
  button.className = 'ide-assistant-fab';
  button.setAttribute('aria-label', 'Open integrated HHS development assistant');
  button.innerHTML = '<span>AI</span><small>Assistant</small>';
  button.onclick = toggleIntegratedAssistant;
  document.body.append(button);
}

function rebindExplorerAssistant() {
  const original = $('#assistant-home');
  if (!original || original.dataset.hhsIntegratedAssistantBound === 'true') return;
  const replacement = original.cloneNode(true);
  replacement.dataset.hhsIntegratedAssistantBound = 'true';
  original.replaceWith(replacement);
  replacement.onclick = openIntegratedAssistant;
}

function bindSimpleWorkflowLauncher() {
  document.addEventListener('click', (event) => {
    const launcher = event.target instanceof Element
      ? event.target.closest('#ide-open-assistant-simple')
      : null;
    if (!launcher) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    openIntegratedAssistant();
  }, true);
}

function bindKeyboard() {
  document.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key.toLowerCase() === 'a') {
      event.preventDefault();
      toggleIntegratedAssistant();
    }
    if (event.key === 'Escape' && assistantOpen) closeIntegratedAssistant();
  });
}

function watchProvider() {
  const provider = $('#provider-status');
  providerObserver?.disconnect();
  if (providerTimer !== null) window.clearInterval(providerTimer);
  if (provider) {
    providerObserver = new MutationObserver(syncCommandState);
    providerObserver.observe(provider, { childList: true, characterData: true, subtree: true, attributes: true });
  }
  let checks = 0;
  providerTimer = window.setInterval(() => {
    syncCommandState();
    checks += 1;
    if (window.HHSAssistant || checks >= 40) {
      window.clearInterval(providerTimer);
      providerTimer = null;
    }
  }, 125);
}

export function initIntegratedAssistant() {
  if (initialized && window.HHSIntegratedAssistant) return window.HHSIntegratedAssistant;
  initialized = true;
  moveAssistantIntoDrawer();
  rebindExplorerAssistant();
  mountDesktopCommand();
  mountMobileCommand();
  mountPersistentLauncher();
  bindSimpleWorkflowLauncher();
  bindKeyboard();
  watchProvider();
  syncCommandState();

  window.HHSIntegratedAssistant = Object.freeze({
    open: openIntegratedAssistant,
    close: closeIntegratedAssistant,
    toggle: toggleIntegratedAssistant,
    refreshStatus: refreshAssistantStatusBounded,
    get isOpen() { return assistantOpen; },
    assistant_remains_advisory: true,
    ide_remains_primary_surface: true,
    status_refresh_deduplicated: true,
    status_refresh_cooldown_ms: REFRESH_COOLDOWN_MS,
    simple_workflow_launcher_capture_owned: true,
  });
  return window.HHSIntegratedAssistant;
}
