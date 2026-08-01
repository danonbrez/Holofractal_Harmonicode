const FRAME_SELECTOR = '#ide-application-frame';
const READY_EVENT = 'hhs:application-preview:ready';
const FAILURE_EVENT = 'hhs:application-preview:failed';
let observer = null;
let initialized = false;

function activeFrame() {
  return document.querySelector(FRAME_SELECTOR);
}

function publish(frame, state, detail = {}) {
  if (!(frame instanceof HTMLIFrameElement)) return;
  frame.dataset.previewState = state;
  frame.dataset.previewReady = state === 'READY' ? 'true' : 'false';
  frame.dataset.previewUpdatedAt = new Date().toISOString();
  const status = document.querySelector('#ide-preview-state');
  if (status) {
    status.dataset.state = state.toLowerCase();
    if (state === 'READY') status.textContent = `RUNNING · ${frame.title.replace(/^Application preview:\s*/, '')}`;
    if (state === 'FAILED') status.textContent = 'PREVIEW FAILED';
  }
  window.dispatchEvent(new CustomEvent(
    state === 'READY' ? READY_EVENT : state === 'FAILED' ? FAILURE_EVENT : 'hhs:application-preview:state',
    {
      detail: {
        schema: 'HHS_APPLICATION_PREVIEW_READINESS_V1',
        state,
        frame_id: frame.id,
        frame_title: frame.title,
        frontend_is_authority: false,
        ...detail,
      },
    },
  ));
}

function bindFrame(frame) {
  if (!(frame instanceof HTMLIFrameElement) || frame.dataset.previewReadinessBound === 'true') return;
  frame.dataset.previewReadinessBound = 'true';
  publish(frame, 'LOADING', { classification: 'HHS_APPLICATION_PREVIEW_LOADING' });
  frame.addEventListener('load', () => {
    if (!frame.isConnected) return;
    frame.dataset.previewDocumentLoaded = 'true';
    frame.dataset.previewLoadedAt = new Date().toISOString();
    if (frame.dataset.previewState !== 'READY' && frame.dataset.previewState !== 'FAILED') {
      publish(frame, 'DOCUMENT_LOADED', { classification: 'HHS_APPLICATION_PREVIEW_DOCUMENT_LOADED' });
    }
  });
}

function scan() {
  const frame = activeFrame();
  if (frame) bindFrame(frame);
}

function onPreviewMessage(event) {
  const frame = activeFrame();
  const payload = event.data;
  if (!(frame instanceof HTMLIFrameElement)) return;
  if (event.source !== frame.contentWindow) return;
  if (!payload || payload.source !== 'hhs-application-preview') return;
  const values = Array.isArray(payload.values) ? payload.values.map(String) : [];
  if (payload.kind === 'ready') {
    publish(frame, 'READY', {
      classification: 'HHS_APPLICATION_PREVIEW_READY',
      values,
    });
  } else if (payload.kind === 'error') {
    publish(frame, 'FAILED', {
      classification: 'HHS_APPLICATION_PREVIEW_RUNTIME_ERROR',
      values,
    });
  }
}

export function initPreviewReadiness() {
  if (initialized) {
    scan();
    return window.HHSApplicationPreviewReadiness;
  }
  initialized = true;
  window.addEventListener('message', onPreviewMessage);
  if (document.body) {
    observer = new MutationObserver(scan);
    observer.observe(document.body, { childList: true, subtree: true });
  }
  scan();
  window.HHSApplicationPreviewReadiness = Object.freeze({
    schema: 'HHS_APPLICATION_PREVIEW_READINESS_V1',
    frame_selector: FRAME_SELECTOR,
    ready_event: READY_EVENT,
    failure_event: FAILURE_EVENT,
    source_window_required: true,
    frontend_is_authority: false,
    status() {
      const frame = activeFrame();
      return frame ? {
        state: frame.dataset.previewState || 'UNBOUND',
        ready: frame.dataset.previewReady === 'true',
        document_loaded: frame.dataset.previewDocumentLoaded === 'true',
      } : { state: 'ABSENT', ready: false, document_loaded: false };
    },
  });
  return window.HHSApplicationPreviewReadiness;
}

initPreviewReadiness();
