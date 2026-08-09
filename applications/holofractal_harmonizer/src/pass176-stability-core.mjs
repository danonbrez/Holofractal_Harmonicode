export const PASS176_BOOT_STAGES = Object.freeze([
  'DOCUMENT_READY',
  'STATIC_THEME_READY',
  'CORE_WORKSPACE_READY',
  'PROJECT_STATE_RESTORED',
  'EDITOR_READY',
  'PREVIEW_READY',
  'ASSISTANT_READY',
  'BACKEND_CAPABILITY_CHECKED',
  'OPTIONAL_REGISTRY_HISTORY_DIAGNOSTICS_LOADING',
  'INTERACTIVE',
]);

export class Pass176Error extends Error {
  constructor(classification, detail = '') {
    super(detail ? `${classification}: ${detail}` : classification);
    this.name = 'Pass176Error';
    this.classification = classification;
    this.detail = detail;
  }
}

export class BootStateMachine {
  #stages;
  #index = -1;
  #records = new Map();
  #startedAt;
  #completedAt = null;

  constructor(stages = PASS176_BOOT_STAGES, now = () => Date.now()) {
    if (!Array.isArray(stages) || stages.length === 0 || new Set(stages).size !== stages.length) {
      throw new Pass176Error('HHS_P176_INVALID_BOOT_STAGES');
    }
    this.#stages = Object.freeze([...stages]);
    this.now = now;
    this.#startedAt = now();
  }

  mark(stage, metadata = {}) {
    const requested = this.#stages.indexOf(stage);
    if (requested < 0) throw new Pass176Error('HHS_P176_UNKNOWN_BOOT_STAGE', stage);
    const existing = this.#records.get(stage);
    if (existing) return existing;
    if (requested !== this.#index + 1) {
      throw new Pass176Error(
        'HHS_P176_BOOT_STAGE_ORDER_VIOLATION',
        `${stage} expected ${this.#stages[this.#index + 1] || 'none'}`,
      );
    }
    const at = this.now();
    const record = Object.freeze({
      stage,
      at,
      elapsedMs: Math.max(0, at - this.#startedAt),
      metadata: Object.freeze({ ...metadata }),
    });
    this.#records.set(stage, record);
    this.#index = requested;
    if (stage === this.#stages.at(-1)) this.#completedAt = at;
    return record;
  }

  has(stage) {
    return this.#records.has(stage);
  }

  get stage() {
    return this.#index >= 0 ? this.#stages[this.#index] : 'NOT_STARTED';
  }

  get interactive() {
    return this.stage === this.#stages.at(-1);
  }

  snapshot() {
    return Object.freeze({
      schema: 'HHS_PASS_176_BOOT_STATE_V1',
      stage: this.stage,
      interactive: this.interactive,
      startedAt: this.#startedAt,
      completedAt: this.#completedAt,
      records: this.#stages.filter((stage) => this.#records.has(stage)).map((stage) => this.#records.get(stage)),
      remaining: this.#stages.slice(this.#index + 1),
    });
  }
}

export class GenerationGate {
  #generations = new Map();

  next(scope) {
    const generation = (this.#generations.get(scope) || 0) + 1;
    this.#generations.set(scope, generation);
    return Object.freeze({ scope, generation });
  }

  current(scope) {
    return this.#generations.get(scope) || 0;
  }

  isCurrent(token) {
    return Boolean(token) && this.current(token.scope) === token.generation;
  }

  assertCurrent(token) {
    if (!this.isCurrent(token)) {
      throw new Pass176Error('HHS_P176_STALE_ASYNC_RESPONSE', `${token?.scope || 'unknown'}:${token?.generation || 0}`);
    }
    return true;
  }

  invalidate(scope) {
    return this.next(scope);
  }

  snapshot() {
    return Object.fromEntries([...this.#generations.entries()].sort(([left], [right]) => left.localeCompare(right)));
  }
}

export class ResourceLedger {
  #resources = new Map();
  #sequence = 0;

  own(kind, disposer, metadata = {}) {
    if (typeof disposer !== 'function') throw new Pass176Error('HHS_P176_RESOURCE_DISPOSER_REQUIRED', kind);
    const id = `${kind}:${++this.#sequence}`;
    this.#resources.set(id, { id, kind, disposer, metadata: { ...metadata }, disposed: false });
    return Object.freeze({
      id,
      dispose: () => this.dispose(id),
    });
  }

  dispose(id) {
    const resource = this.#resources.get(id);
    if (!resource || resource.disposed) return false;
    resource.disposed = true;
    try {
      resource.disposer();
    } finally {
      this.#resources.delete(id);
    }
    return true;
  }

  disposeKind(kind) {
    let count = 0;
    for (const resource of [...this.#resources.values()]) {
      if (resource.kind === kind && this.dispose(resource.id)) count += 1;
    }
    return count;
  }

  disposeAll() {
    const errors = [];
    let disposed = 0;
    for (const resource of [...this.#resources.values()].reverse()) {
      try {
        if (this.dispose(resource.id)) disposed += 1;
      } catch (error) {
        errors.push({ id: resource.id, message: error?.message || String(error) });
      }
    }
    return Object.freeze({ disposed, errors });
  }

  snapshot() {
    const counts = {};
    for (const resource of this.#resources.values()) counts[resource.kind] = (counts[resource.kind] || 0) + 1;
    return Object.freeze({
      schema: 'HHS_PASS_176_RESOURCE_LEDGER_V1',
      total: this.#resources.size,
      counts: Object.freeze(counts),
      resources: [...this.#resources.values()].map(({ id, kind, metadata }) => Object.freeze({ id, kind, metadata: { ...metadata } })),
    });
  }
}

function abortError(reason = 'HHS_P176_JOB_ABORTED') {
  const error = new Pass176Error(reason);
  error.name = 'AbortError';
  return error;
}

const defaultSetTimer = (...args) => globalThis.setTimeout(...args);
const defaultClearTimer = (...args) => globalThis.clearTimeout(...args);

export class BoundedJobManager {
  #jobs = new Map();
  #sequence = 0;

  constructor({ setTimer = defaultSetTimer, clearTimer = defaultClearTimer, now = () => Date.now() } = {}) {
    this.setTimer = setTimer;
    this.clearTimer = clearTimer;
    this.now = now;
  }

  run(name, executor, options = {}) {
    if (!name || typeof executor !== 'function') throw new Pass176Error('HHS_P176_INVALID_JOB');
    const key = String(options.key || name);
    const existing = this.#jobs.get(key);
    if (existing && options.dedupe !== false) return existing.promise;
    if (existing) existing.controller.abort('HHS_P176_JOB_SUPERSEDED');

    const controller = new AbortController();
    const timeoutMs = Math.max(1, Number(options.timeoutMs || 120_000));
    const id = `${key}:${++this.#sequence}`;
    const startedAt = this.now();
    let timer = null;
    let removeAbortListener = () => {};
    const job = {
      id,
      key,
      name,
      controller,
      startedAt,
      timeoutMs,
      progress: 0,
      stage: 'RUNNING',
      detail: '',
      promise: null,
    };
    const update = (progress, stage = job.stage, detail = '') => {
      job.progress = Math.max(0, Math.min(1, Number(progress) || 0));
      job.stage = String(stage || 'RUNNING');
      job.detail = String(detail || '');
      options.onProgress?.(Object.freeze(this.describe(job)));
    };

    job.promise = Promise.resolve().then(async () => {
      timer = this.setTimer(() => controller.abort('HHS_P176_JOB_TIMEOUT'), timeoutMs);
      const abortPromise = new Promise((_, reject) => {
        const rejectAbort = () => reject(abortError(String(controller.signal.reason || 'HHS_P176_JOB_ABORTED')));
        controller.signal.addEventListener('abort', rejectAbort, { once: true });
        removeAbortListener = () => controller.signal.removeEventListener('abort', rejectAbort);
        if (controller.signal.aborted) rejectAbort();
      });
      const executionPromise = Promise.resolve().then(() => executor({
        id,
        name,
        signal: controller.signal,
        update,
        startedAt,
      }));
      try {
        const result = await Promise.race([executionPromise, abortPromise]);
        if (controller.signal.aborted) throw abortError(String(controller.signal.reason || 'HHS_P176_JOB_ABORTED'));
        job.stage = 'COMPLETE';
        job.progress = 1;
        return result;
      } catch (error) {
        job.stage = controller.signal.aborted ? 'CANCELLED' : 'FAILED';
        if (controller.signal.aborted && error?.name !== 'AbortError') {
          throw abortError(String(controller.signal.reason || 'HHS_P176_JOB_ABORTED'));
        }
        throw error;
      } finally {
        removeAbortListener();
        if (timer !== null) this.clearTimer(timer);
        if (this.#jobs.get(key) === job) this.#jobs.delete(key);
        options.onSettled?.(Object.freeze(this.describe(job)));
      }
    });
    this.#jobs.set(key, job);
    options.onStart?.(Object.freeze(this.describe(job)));
    return job.promise;
  }

  describe(job) {
    return {
      id: job.id,
      key: job.key,
      name: job.name,
      startedAt: job.startedAt,
      elapsedMs: Math.max(0, this.now() - job.startedAt),
      timeoutMs: job.timeoutMs,
      progress: job.progress,
      stage: job.stage,
      detail: job.detail,
      aborted: job.controller.signal.aborted,
    };
  }

  cancel(name, reason = 'HHS_P176_USER_CANCELLED') {
    const job = this.#jobs.get(name) || [...this.#jobs.values()].find((candidate) => candidate.name === name);
    if (!job) return false;
    job.controller.abort(reason);
    return true;
  }

  cancelAll(reason = 'HHS_P176_DISPOSED') {
    let count = 0;
    for (const job of [...this.#jobs.values()]) {
      if (!job.controller.signal.aborted) {
        job.controller.abort(reason);
        count += 1;
      }
    }
    return count;
  }

  currentSignal() {
    const active = [...this.#jobs.values()].at(-1);
    return active?.controller.signal || null;
  }

  snapshot() {
    return Object.freeze({
      schema: 'HHS_PASS_176_BOUNDED_JOBS_V1',
      active: [...this.#jobs.values()].map((job) => Object.freeze(this.describe(job))),
    });
  }
}

export class AtomicRecoveryStore {
  constructor(storage, { key = 'hhs.pass176.recovery.v1', version = 1 } = {}) {
    if (!storage || typeof storage.getItem !== 'function' || typeof storage.setItem !== 'function') {
      throw new Pass176Error('HHS_P176_STORAGE_ADAPTER_REQUIRED');
    }
    this.storage = storage;
    this.key = key;
    this.pendingKey = `${key}.pending`;
    this.version = version;
  }

  save(payload, metadata = {}) {
    const envelope = {
      schema: 'HHS_PASS_176_RECOVERY_ENVELOPE_V1',
      version: this.version,
      savedAt: Date.now(),
      metadata: { ...metadata },
      payload,
    };
    const serialized = JSON.stringify(envelope);
    try {
      this.storage.setItem(this.pendingKey, serialized);
      this.storage.setItem(this.key, serialized);
      this.storage.removeItem?.(this.pendingKey);
      return envelope;
    } catch {
      return null;
    }
  }

  load() {
    const candidates = [];
    for (const [key, pending] of [[this.key, false], [this.pendingKey, true]]) {
      try {
        const raw = this.storage.getItem(key);
        if (raw) candidates.push({ raw, pending });
      } catch { /* unavailable storage must not block boot */ }
    }
    let selected = null;
    for (const candidate of candidates) {
      try {
        const parsed = JSON.parse(candidate.raw);
        if (parsed?.schema !== 'HHS_PASS_176_RECOVERY_ENVELOPE_V1' || parsed.version !== this.version) continue;
        const record = { ...parsed, pending: candidate.pending };
        if (!selected || Number(record.savedAt || 0) > Number(selected.savedAt || 0) || (Number(record.savedAt || 0) === Number(selected.savedAt || 0) && record.pending && !selected.pending)) selected = record;
      } catch {
        // Malformed recovery records are ignored rather than blocking the editor.
      }
    }
    return selected;
  }

  clear() {
    try { this.storage.removeItem?.(this.key); } catch { /* best effort */ }
    try { this.storage.removeItem?.(this.pendingKey); } catch { /* best effort */ }
  }
}
