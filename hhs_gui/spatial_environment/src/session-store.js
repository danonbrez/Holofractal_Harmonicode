const STORAGE_KEY = "hhs-spatial-session-store-v3";
const MAX_SESSIONS = 24;
const MAX_SNAPSHOTS_PER_SESSION = 20;

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function makeId(prefix = "session") {
  const random = globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  return `${prefix}-${random}`;
}

function now() {
  return new Date().toISOString();
}

function defaultSession() {
  const time = now();
  return {
    id: "default-session",
    name: "Default Workspace",
    createdAt: time,
    modifiedAt: time,
    activeTemplate: "operator-default",
    activeTheme: "cyan-blue",
    activeMode: "overview",
    activeFeature: "dashboard",
    selectedCell: null,
    surfaces: [],
    camera: null,
    parameters: { modulus: 19, curiosity: 0.42, rigidity: 0.81 },
    snapshots: []
  };
}

function normalizeSession(input) {
  const base = defaultSession();
  const session = input && typeof input === "object" ? input : {};
  return {
    ...base,
    ...clone(session),
    id: typeof session.id === "string" && session.id ? session.id : makeId(),
    name: typeof session.name === "string" && session.name.trim() ? session.name.trim().slice(0, 80) : "Untitled Workspace",
    surfaces: Array.isArray(session.surfaces) ? clone(session.surfaces).slice(0, 48) : [],
    snapshots: Array.isArray(session.snapshots) ? clone(session.snapshots).slice(-MAX_SNAPSHOTS_PER_SESSION) : [],
    parameters: {
      ...base.parameters,
      ...(session.parameters && typeof session.parameters === "object" ? session.parameters : {})
    }
  };
}

export class SessionStore extends EventTarget {
  constructor({ storage = globalThis.localStorage } = {}) {
    super();
    this.storage = storage;
    this.sessions = [];
    this.activeSessionId = null;
    this.load();
  }

  load() {
    let parsed = null;
    try {
      const raw = this.storage?.getItem(STORAGE_KEY);
      parsed = raw ? JSON.parse(raw) : null;
    } catch {
      parsed = null;
    }

    const sessions = Array.isArray(parsed?.sessions)
      ? parsed.sessions.map(normalizeSession).slice(0, MAX_SESSIONS)
      : [defaultSession()];

    this.sessions = sessions.length ? sessions : [defaultSession()];
    this.activeSessionId = this.sessions.some((session) => session.id === parsed?.activeSessionId)
      ? parsed.activeSessionId
      : this.sessions[0].id;
    this.persist();
    this.emit("loaded", this.snapshot());
  }

  persist() {
    try {
      this.storage?.setItem(STORAGE_KEY, JSON.stringify({
        schema: "HHS_SPATIAL_SESSION_STORE_V3",
        activeSessionId: this.activeSessionId,
        sessions: this.sessions
      }));
    } catch (error) {
      this.emit("storage-error", { error: String(error) });
    }
  }

  get activeSession() {
    return this.sessions.find((session) => session.id === this.activeSessionId) ?? this.sessions[0];
  }

  list() {
    return this.sessions.map(({ snapshots, ...session }) => ({
      ...clone(session),
      snapshotCount: snapshots.length
    }));
  }

  create(name = "Untitled Workspace", seed = {}) {
    if (this.sessions.length >= MAX_SESSIONS) {
      throw new Error("SESSION_LIMIT_REACHED");
    }
    const time = now();
    const session = normalizeSession({
      ...seed,
      id: makeId(),
      name,
      createdAt: time,
      modifiedAt: time,
      snapshots: []
    });
    this.sessions.push(session);
    this.activeSessionId = session.id;
    this.persist();
    this.emit("session-created", clone(session));
    this.emit("session-selected", clone(session));
    return clone(session);
  }

  select(id) {
    const session = this.sessions.find((candidate) => candidate.id === id);
    if (!session) {
      throw new Error(`UNKNOWN_SESSION:${id}`);
    }
    this.activeSessionId = id;
    this.persist();
    this.emit("session-selected", clone(session));
    return clone(session);
  }

  rename(id, name) {
    const session = this.sessions.find((candidate) => candidate.id === id);
    if (!session) {
      throw new Error(`UNKNOWN_SESSION:${id}`);
    }
    const normalized = String(name ?? "").trim().slice(0, 80);
    if (!normalized) {
      throw new Error("SESSION_NAME_REQUIRED");
    }
    session.name = normalized;
    session.modifiedAt = now();
    this.persist();
    this.emit("session-updated", clone(session));
    return clone(session);
  }

  update(patch = {}, { emit = true } = {}) {
    const session = this.activeSession;
    if (!session) {
      throw new Error("ACTIVE_SESSION_UNAVAILABLE");
    }
    const protectedKeys = new Set(["id", "createdAt", "snapshots"]);
    for (const [key, value] of Object.entries(patch)) {
      if (!protectedKeys.has(key)) {
        session[key] = clone(value);
      }
    }
    session.modifiedAt = now();
    this.persist();
    if (emit) {
      this.emit("session-updated", clone(session));
    }
    return clone(session);
  }

  saveSnapshot(label = "Manual snapshot", state = {}) {
    const session = this.activeSession;
    if (!session) {
      throw new Error("ACTIVE_SESSION_UNAVAILABLE");
    }
    const snapshot = {
      id: makeId("snapshot"),
      label: String(label || "Snapshot").slice(0, 100),
      createdAt: now(),
      state: clone(state)
    };
    session.snapshots.push(snapshot);
    session.snapshots = session.snapshots.slice(-MAX_SNAPSHOTS_PER_SESSION);
    session.modifiedAt = snapshot.createdAt;
    this.persist();
    this.emit("snapshot-created", { sessionId: session.id, snapshot: clone(snapshot) });
    return clone(snapshot);
  }

  restoreSnapshot(snapshotId) {
    const session = this.activeSession;
    const snapshot = session?.snapshots.find((candidate) => candidate.id === snapshotId);
    if (!snapshot) {
      throw new Error(`UNKNOWN_SNAPSHOT:${snapshotId}`);
    }
    this.emit("snapshot-restored", { sessionId: session.id, snapshot: clone(snapshot) });
    return clone(snapshot.state);
  }

  delete(id) {
    if (this.sessions.length === 1) {
      throw new Error("CANNOT_DELETE_LAST_SESSION");
    }
    const index = this.sessions.findIndex((candidate) => candidate.id === id);
    if (index < 0) {
      throw new Error(`UNKNOWN_SESSION:${id}`);
    }
    const [removed] = this.sessions.splice(index, 1);
    if (this.activeSessionId === id) {
      this.activeSessionId = this.sessions[Math.max(0, index - 1)].id;
    }
    this.persist();
    this.emit("session-deleted", clone(removed));
    this.emit("session-selected", clone(this.activeSession));
    return clone(removed);
  }

  export() {
    return {
      schema: "HHS_SPATIAL_SESSION_EXPORT_V3",
      classification: "PRESENTATION_STATE_ONLY",
      exportedAt: now(),
      activeSessionId: this.activeSessionId,
      sessions: clone(this.sessions)
    };
  }

  import(payload, { merge = true } = {}) {
    if (!payload || payload.schema !== "HHS_SPATIAL_SESSION_EXPORT_V3" || !Array.isArray(payload.sessions)) {
      throw new Error("INVALID_SESSION_EXPORT");
    }
    const incoming = payload.sessions.map(normalizeSession);
    if (!merge) {
      this.sessions = incoming.slice(0, MAX_SESSIONS);
    } else {
      const byId = new Map(this.sessions.map((session) => [session.id, session]));
      for (const session of incoming) {
        byId.set(session.id, session);
      }
      this.sessions = [...byId.values()].slice(0, MAX_SESSIONS);
    }
    if (!this.sessions.length) {
      this.sessions = [defaultSession()];
    }
    this.activeSessionId = this.sessions.some((session) => session.id === payload.activeSessionId)
      ? payload.activeSessionId
      : this.sessions[0].id;
    this.persist();
    this.emit("imported", this.snapshot());
    this.emit("session-selected", clone(this.activeSession));
    return this.snapshot();
  }

  snapshot() {
    return {
      schema: "HHS_SPATIAL_SESSION_STORE_SNAPSHOT_V3",
      activeSessionId: this.activeSessionId,
      activeSession: clone(this.activeSession),
      sessionCount: this.sessions.length,
      sessions: this.list()
    };
  }

  emit(type, detail) {
    this.dispatchEvent(new CustomEvent(type, { detail }));
  }
}

export const SESSION_STORAGE_KEY = STORAGE_KEY;
