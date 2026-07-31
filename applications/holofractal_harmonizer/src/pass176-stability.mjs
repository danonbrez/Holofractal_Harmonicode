import {
  AtomicRecoveryStore,
  BootStateMachine,
  BoundedJobManager,
  GenerationGate,
  PASS176_BOOT_STAGES,
  Pass176Error,
  ResourceLedger,
} from './pass176-stability-core.mjs';

const INSTANCE = Symbol.for('hhs.pass176.stability.instance');
const STYLE_ID = 'hhs-pass176-stability-style';
const RECOVERY_KEY = 'hhs.pass176.projectRecovery.v1';
const PROFILE_KEY = 'hhs.pass176.performanceProfile.v1';
const MAX_ERROR_RECORDS = 40;
const DRAG_THRESHOLD_PX = 8;

function ready() {
  if (document.readyState !== 'loading') return Promise.resolve();
  return new Promise((resolve) => document.addEventListener('DOMContentLoaded', resolve, { once: true }));
}

function storageAdapter() {
  try {
    const storage = window.localStorage;
    storage.getItem(PROFILE_KEY);
    return storage;
  } catch {
    const memory = new Map();
    return {
      getItem: (key) => memory.has(key) ? memory.get(key) : null,
      setItem: (key, value) => memory.set(key, String(value)),
      removeItem: (key) => memory.delete(key),
    };
  }
}

function loadStyle() {
  if (document.getElementById(STYLE_ID)) return;
  const link = document.createElement('link');
  link.id = STYLE_ID;
  link.rel = 'stylesheet';
  link.href = './src/pass176-stability.css';
  document.head.append(link);
}

function copyProjectState(state) {
  return {
    projectId: state.projectId || null,
    activePath: state.activePath || null,
    files: Array.isArray(state.files)
      ? state.files.map((file) => ({
          path: String(file.path || ''),
          name: String(file.name || ''),
          mediaType: String(file.mediaType || 'BINARY_OBJECT'),
          content: typeof file.content === 'string' ? file.content : undefined,
          bytesB64: typeof file.bytesB64 === 'string' ? file.bytesB64 : undefined,
          dirty: Boolean(file.dirty),
        }))
      : [],
    selectedBuildTarget: state.selectedBuildTarget || null,
    selectedCompilerTarget: state.selectedCompilerTarget || null,
    previewEntrypoint: state.previewEntrypoint || null,
    workflowState: state.lifecycle?.ok ? 'COMPLETE' : state.busy ? 'RUNNING' : 'READY',
  };
}

function validateRecoveryPayload(payload) {
  if (!payload || !Array.isArray(payload.files) || payload.files.length > 4096) return false;
  const paths = new Set();
  for (const file of payload.files) {
    if (!file || typeof file.path !== 'string' || !file.path) return false;
    const normalizedPath = file.path.replaceAll('\\', '/');
    if (normalizedPath.startsWith('/') || normalizedPath.split('/').includes('..')) return false;
    if (paths.has(normalizedPath)) return false;
    paths.add(normalizedPath);
    if (typeof file.content === 'string' && file.content.length > 16 * 1024 * 1024) return false;
    if (typeof file.bytesB64 === 'string' && file.bytesB64.length > 24 * 1024 * 1024) return false;
  }
  return true;
}

function makeStatusSurface() {
  const existing = document.querySelector('#pass176-stability-status');
  if (existing) return existing;
  const surface = document.createElement('aside');
  surface.id = 'pass176-stability-status';
  surface.className = 'pass176-stability-status';
  surface.setAttribute('aria-live', 'polite');
  surface.setAttribute('aria-label', 'Pass 176 IDE reliability status');
  surface.innerHTML = `
    <div class="pass176-stability-summary">
      <span class="pass176-stability-light" aria-hidden="true"></span>
      <strong>IDE stabilizing</strong>
      <span data-pass176-stage>DOCUMENT READY</span>
      <button type="button" data-pass176-cancel hidden>Cancel task</button>
      <button type="button" data-pass176-recover hidden>Restore recovery</button>
      <button type="button" data-pass176-dismiss hidden>Dismiss error</button>
    </div>
    <div class="pass176-stability-detail" data-pass176-detail>Preserving the accepted workspace while services initialize.</div>
  `;
  const anchor = document.querySelector('.ide-control-pane, .ide-system-bar, #ide-layout');
  (anchor?.parentElement || document.body).insertBefore(surface, anchor || null);
  return surface;
}

function classifyError(value) {
  const error = value instanceof Error ? value : new Error(String(value));
  return {
    classification: error.classification || error.name || 'HHS_P176_BROWSER_ERROR',
    message: error.message || String(error),
    stack: error.stack || null,
    at: new Date().toISOString(),
  };
}

class Pass176BrowserController {
  constructor({ state, activeFile, persist, ensureProject, log } = {}) {
    this.state = state || {};
    this.activeFile = typeof activeFile === 'function' ? activeFile : () => null;
    this.persist = typeof persist === 'function' ? persist : () => {};
    this.ensureProject = typeof ensureProject === 'function' ? ensureProject : async () => null;
    this.log = typeof log === 'function' ? log : () => {};
    this.storage = storageAdapter();
    this.bootState = new BootStateMachine();
    this.generations = new GenerationGate();
    this.resources = new ResourceLedger();
    this.jobs = new BoundedJobManager();
    this.recovery = new AtomicRecoveryStore(this.storage, { key: RECOVERY_KEY });
    this.errors = [];
    this.longTasks = [];
    this.bootPromise = null;
    this.disposed = false;
    this.recoveryEnvelope = null;
    this.authorityEvidence = null;
    this.surface = makeStatusSurface();
    this.profile = this.storage.getItem(PROFILE_KEY) || 'BALANCED';
    document.documentElement.dataset.hhsPerformanceProfile = this.profile;
    this.drag = null;
    this.#installGlobalBoundaries();
    this.#installRecovery();
    this.#installInteractionSafety();
    this.#installPerformanceObservation();
    this.#bindSurfaceActions();
    this.mark('DOCUMENT_READY', { readyState: document.readyState });
    this.#render('IDE boot started.', 'running');
  }

  #listen(target, type, listener, options) {
    target.addEventListener(type, listener, options);
    return this.resources.own('listener', () => target.removeEventListener(type, listener, options), { type });
  }

  #bindSurfaceActions() {
    const cancel = this.surface.querySelector('[data-pass176-cancel]');
    const recover = this.surface.querySelector('[data-pass176-recover]');
    const dismiss = this.surface.querySelector('[data-pass176-dismiss]');
    this.#listen(cancel, 'click', () => {
      const active = this.jobs.snapshot().active.at(-1);
      if (active) this.jobs.cancel(active.key || active.name);
    });
    this.#listen(recover, 'click', () => {
      const restored = this.applyRecovery();
      this.#render(restored ? 'Recovered unsaved project state.' : 'No valid recovery state was applied.', restored ? 'ready' : 'error');
    });
    this.#listen(dismiss, 'click', () => {
      this.surface.classList.remove('has-error');
      dismiss.hidden = true;
      this.#render(this.bootState.interactive ? 'Workspace remains interactive.' : 'IDE boot continues.', 'ready');
    });
  }

  #installGlobalBoundaries() {
    this.#listen(window, 'error', (event) => {
      this.recordError(event.error || event.message, { source: 'window.error' });
    }, true);
    this.#listen(window, 'unhandledrejection', (event) => {
      this.recordError(event.reason, { source: 'unhandledrejection' });
      event.preventDefault();
    });
    this.#listen(window, 'offline', () => this.#render('Network unavailable. Local editing and recoverable storage remain active.', 'degraded'));
    this.#listen(window, 'online', () => this.#render('Network restored. Backend workflows may be retried.', 'ready'));
    this.#listen(window, 'pagehide', () => this.flushRecovery('pagehide'));
  }

  #installRecovery() {
    const restored = this.recovery.load();
    if (restored && validateRecoveryPayload(restored.payload)) {
      this.recoveryEnvelope = restored;
      const recoverButton = this.surface.querySelector('[data-pass176-recover]');
      if (recoverButton) recoverButton.hidden = false;
    }
    let timer = null;
    const schedule = () => {
      if (timer !== null) clearTimeout(timer);
      timer = window.setTimeout(() => {
        timer = null;
        this.flushRecovery('debounced-autosave');
      }, 350);
    };
    this.resources.own('timer-owner', () => {
      if (timer !== null) clearTimeout(timer);
    });
    this.#listen(document, 'input', (event) => {
      if (event.target?.matches?.('#ide-source-editor, [data-project-source]')) schedule();
    }, true);
    this.#listen(document, 'change', (event) => {
      if (event.target?.closest?.('#ide-layout, #registry-nav, .application-studio')) schedule();
    }, true);
    this.#listen(document, 'visibilitychange', () => {
      if (document.visibilityState === 'hidden') this.flushRecovery('background');
    });
    this.#listen(window, 'beforeunload', () => this.flushRecovery('beforeunload'));
  }

  #installInteractionSafety() {
    this.#listen(document, 'pointerdown', (event) => {
      if (event.button !== 0) return;
      const owner = event.target instanceof Element
        ? event.target.closest('[draggable="true"], [data-hhs-draggable], .ide-file-item')
        : null;
      if (!owner) return;
      this.drag = { pointerId: event.pointerId, x: event.clientX, y: event.clientY, owner, active: false };
    }, true);
    this.#listen(document, 'pointermove', (event) => {
      if (!this.drag || this.drag.pointerId !== event.pointerId) return;
      const distance = Math.hypot(event.clientX - this.drag.x, event.clientY - this.drag.y);
      if (!this.drag.active && distance >= DRAG_THRESHOLD_PX) {
        this.drag.active = true;
        this.drag.owner.dataset.hhsDragging = 'true';
        document.documentElement.dataset.hhsPointerOwner = 'drag';
      }
    }, true);
    const release = (event) => {
      if (!this.drag || (event?.pointerId !== undefined && this.drag.pointerId !== event.pointerId)) return;
      delete this.drag.owner.dataset.hhsDragging;
      delete document.documentElement.dataset.hhsPointerOwner;
      try {
        if (this.drag.owner.hasPointerCapture?.(this.drag.pointerId)) this.drag.owner.releasePointerCapture(this.drag.pointerId);
      } catch {
        // Pointer capture can already be released by the browser.
      }
      this.drag = null;
    };
    this.#listen(document, 'pointerup', release, true);
    this.#listen(document, 'pointercancel', release, true);
    this.#listen(window, 'blur', release, true);
    this.#listen(document, 'keydown', (event) => {
      if (event.key === 'Escape' && this.drag) {
        event.preventDefault();
        release();
      }
    }, true);
  }

  #installPerformanceObservation() {
    if (!('PerformanceObserver' in window)) return;
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.longTasks.push({ startTime: Math.round(entry.startTime), duration: Math.round(entry.duration) });
          if (this.longTasks.length > 100) this.longTasks.shift();
        }
      });
      observer.observe({ type: 'longtask', buffered: true });
      this.resources.own('observer', () => observer.disconnect(), { type: 'longtask' });
    } catch {
      // Long-task observation is optional and must not block the editor.
    }
  }

  mark(stage, metadata = {}) {
    const record = this.bootState.mark(stage, metadata);
    document.documentElement.dataset.hhsPass176Stage = stage;
    const label = this.surface.querySelector('[data-pass176-stage]');
    if (label) label.textContent = stage.replaceAll('_', ' ');
    this.surface.classList.toggle('interactive', this.bootState.interactive);
    window.dispatchEvent(new CustomEvent('hhs:pass176:boot-stage', { detail: record }));
    return record;
  }

  async step(stage, operation, { optional = false } = {}) {
    if (this.bootState.has(stage)) return { stage, duplicate: true };
    try {
      const result = typeof operation === 'function' ? await operation() : operation;
      this.mark(stage, { optional, ok: true });
      return result;
    } catch (error) {
      this.recordError(error, { stage, optional });
      if (!optional) throw error;
      this.mark(stage, { optional, ok: false, error: error?.message || String(error) });
      return null;
    }
  }

  boot(steps) {
    if (this.bootPromise) return this.bootPromise;
    this.bootPromise = (async () => {
      for (const step of steps) {
        await this.step(step.stage, step.run, { optional: Boolean(step.optional) });
      }
      if (!this.bootState.interactive) throw new Pass176Error('HHS_P176_BOOT_DID_NOT_REACH_INTERACTIVE');
      this.#render('Workspace interactive. Optional services continue without blocking editing.', 'ready');
      return this.status();
    })().catch((error) => {
      this.recordError(error, { stage: this.bootState.stage, terminalBootFailure: true });
      throw error;
    });
    return this.bootPromise;
  }

  runAction(name, operation, { timeoutMs = 120_000, detail = name, key = name, dedupe = true } = {}) {
    return this.jobs.run(name, async (job) => {
      this.#render(detail, 'running');
      const cancel = this.surface.querySelector('[data-pass176-cancel]');
      if (cancel) cancel.hidden = false;
      const result = await operation(job);
      this.#render(`${detail} complete.`, 'ready');
      return result;
    }, {
      key,
      dedupe,
      timeoutMs,
      onSettled: (job) => {
        const cancel = this.surface.querySelector('[data-pass176-cancel]');
        if (cancel) cancel.hidden = this.jobs.snapshot().active.length === 0;
        if (job.stage === 'FAILED' || job.stage === 'CANCELLED') {
          this.#render(`${detail} ${job.stage.toLowerCase()}. Project recovery remains available.`, 'error');
        }
      },
    });
  }

  currentSignal() {
    return this.jobs.currentSignal();
  }

  generation(scope) {
    return this.generations.next(scope);
  }

  accept(token, value) {
    this.generations.assertCurrent(token);
    return value;
  }

  flushRecovery(reason = 'manual') {
    if (this.disposed || !validateRecoveryPayload(copyProjectState(this.state))) return null;
    const envelope = this.recovery.save(copyProjectState(this.state), {
      reason,
      activeFile: this.activeFile()?.path || null,
      authoritativeBackendDurabilityClaimed: false,
    });
    if (envelope) this.recoveryEnvelope = envelope;
    return envelope;
  }

  applyRecovery() {
    const envelope = this.recoveryEnvelope || this.recovery.load();
    if (!envelope || !validateRecoveryPayload(envelope.payload)) return false;
    const payload = envelope.payload;
    this.state.projectId = payload.projectId || this.state.projectId || null;
    this.state.files = payload.files.map((file) => ({ ...file }));
    this.state.activePath = payload.activePath && payload.files.some((file) => file.path === payload.activePath)
      ? payload.activePath
      : payload.files[0]?.path || null;
    this.persist();
    this.recoveryEnvelope = null;
    window.dispatchEvent(new CustomEvent('hhs:pass176:recovery-applied', { detail: { savedAt: envelope.savedAt, activePath: this.state.activePath } }));
    const recoverButton = this.surface.querySelector('[data-pass176-recover]');
    if (recoverButton) recoverButton.hidden = true;
    return true;
  }

  setAuthorityEvidence(evidence = {}) {
    const productHealth = evidence.productHealth || null;
    const pass175 = evidence.pass175 || null;
    const runtime = productHealth?.runtime || null;
    const vm81AuthorityPreserved = Boolean(
      runtime?.ok === true &&
      runtime?.canonical_runtime_attached === true &&
      pass175?.singleton_vm81_commit_authority === true
    );
    const hash72CommitStreams = vm81AuthorityPreserved && Number(pass175?.hash72_commit_streams) === 1 ? 1 : 0;
    this.authorityEvidence = Object.freeze({
      schema: 'HHS_PASS_176_BACKEND_AUTHORITY_EVIDENCE_V1',
      observedAt: new Date().toISOString(),
      productHealthSchema: productHealth?.schema || null,
      runtimeStatus: runtime?.status || null,
      runtimeReceiptHash72: runtime?.receipt_hash72 || null,
      pass175Schema: pass175?.schema || null,
      pass175Classification: pass175?.classification || null,
      singletonVm81CommitAuthority: pass175?.singleton_vm81_commit_authority === true,
      vm81AuthorityPreserved,
      hash72CommitStreams,
    });
    return this.authorityEvidence;
  }

  setProfile(profile) {
    const allowed = new Set(['MOBILE_SAFE', 'BALANCED', 'DESKTOP_HIGH', 'HIGH_REFRESH', 'DIAGNOSTIC']);
    if (!allowed.has(profile)) throw new Pass176Error('HHS_P176_UNKNOWN_PERFORMANCE_PROFILE', profile);
    this.profile = profile;
    this.storage.setItem(PROFILE_KEY, profile);
    document.documentElement.dataset.hhsPerformanceProfile = profile;
    return profile;
  }

  recordError(value, context = {}) {
    const record = { ...classifyError(value), context: { ...context } };
    this.errors.push(record);
    if (this.errors.length > MAX_ERROR_RECORDS) this.errors.shift();
    this.surface.classList.add('has-error');
    const dismiss = this.surface.querySelector('[data-pass176-dismiss]');
    if (dismiss) dismiss.hidden = false;
    this.#render(record.message, 'error');
    this.log(`Pass 176 recoverable error: ${record.message}`, record);
    window.dispatchEvent(new CustomEvent('hhs:pass176:error', { detail: record }));
    return record;
  }

  #render(detail, state) {
    this.surface.dataset.state = state;
    const node = this.surface.querySelector('[data-pass176-detail]');
    if (node) node.textContent = String(detail || '');
    const summary = this.surface.querySelector('strong');
    if (summary) summary.textContent = state === 'error'
      ? 'Action needs attention'
      : this.bootState.interactive
        ? 'IDE ready'
        : 'IDE stabilizing';
  }

  own(kind, disposer, metadata = {}) {
    return this.resources.own(kind, disposer, metadata);
  }

  trackObjectUrl(url) {
    return this.resources.own('object-url', () => URL.revokeObjectURL(url), { url });
  }

  status() {
    return Object.freeze({
      schema: 'HHS_PASS_176_FROZEN_IDE_STABILITY_STATUS_V1',
      classification: this.bootState.interactive
        ? 'HHS_PASS_176_IDE_INTERACTIVE_RECOVERABLE'
        : 'HHS_PASS_176_IDE_BOOTING',
      boot: this.bootState.snapshot(),
      jobs: this.jobs.snapshot(),
      resources: this.resources.snapshot(),
      generations: this.generations.snapshot(),
      errors: [...this.errors],
      longTasks: [...this.longTasks],
      recoveryAvailable: Boolean(this.recoveryEnvelope || this.recovery.load()),
      profile: this.profile,
      canonicalFrontendAuthority: false,
      vm81AuthorityPreserved: this.authorityEvidence?.vm81AuthorityPreserved === true,
      hash72CommitStreams: this.authorityEvidence?.hash72CommitStreams || 0,
      authorityEvidence: this.authorityEvidence ? { ...this.authorityEvidence } : null,
    });
  }

  dispose() {
    if (this.disposed) return false;
    this.flushRecovery('dispose');
    this.disposed = true;
    this.jobs.cancelAll();
    this.resources.disposeAll();
    this.surface.remove();
    return true;
  }
}

export async function initPass176Stability(options = {}) {
  await ready();
  loadStyle();
  if (window[INSTANCE]) return window[INSTANCE];
  const controller = new Pass176BrowserController(options);
  window[INSTANCE] = controller;
  window.HHSPass176 = Object.freeze({
    schema: 'HHS_PASS_176_BROWSER_CONTROL_V1',
    status: () => controller.status(),
    boot: (steps) => controller.boot(steps),
    mark: (stage, metadata) => controller.mark(stage, metadata),
    runAction: (name, operation, actionOptions) => controller.runAction(name, operation, actionOptions),
    cancel: (name) => controller.jobs.cancel(name),
    currentSignal: () => controller.currentSignal(),
    generation: (scope) => controller.generation(scope),
    accept: (token, value) => controller.accept(token, value),
    flushRecovery: (reason) => controller.flushRecovery(reason),
    applyRecovery: () => controller.applyRecovery(),
    setAuthorityEvidence: (evidence) => controller.setAuthorityEvidence(evidence),
    setProfile: (profile) => controller.setProfile(profile),
    own: (kind, disposer, metadata) => controller.own(kind, disposer, metadata),
    trackObjectUrl: (url) => controller.trackObjectUrl(url),
    dispose: () => controller.dispose(),
    stages: PASS176_BOOT_STAGES,
    controller,
  });
  return controller;
}
