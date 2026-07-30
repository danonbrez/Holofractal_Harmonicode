const $ = (selector) => document.querySelector(selector);

let assistantOpen = false;
let providerObserver = null;

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
  window.setTimeout(() => $('#prompt-input')?.focus(), 80);
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
  void window.HHSAssistant?.refreshStatus?.();
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
  if (!original) return;
  const replacement = original.cloneNode(true);
  original.replaceWith(replacement);
  replacement.onclick = openIntegratedAssistant;
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
  if (provider) {
    providerObserver = new MutationObserver(syncCommandState);
    providerObserver.observe(provider, { childList: true, characterData: true, subtree: true, attributes: true });
  }
  let checks = 0;
  const timer = window.setInterval(() => {
    syncCommandState();
    checks += 1;
    if (window.HHSAssistant || checks >= 40) window.clearInterval(timer);
  }, 125);
}

export function initIntegratedAssistant() {
  moveAssistantIntoDrawer();
  rebindExplorerAssistant();
  mountDesktopCommand();
  mountMobileCommand();
  mountPersistentLauncher();
  bindKeyboard();
  watchProvider();
  syncCommandState();

  window.HHSIntegratedAssistant = Object.freeze({
    open: openIntegratedAssistant,
    close: closeIntegratedAssistant,
    toggle: toggleIntegratedAssistant,
    get isOpen() { return assistantOpen; },
    assistant_remains_advisory: true,
    ide_remains_primary_surface: true,
  });
}
