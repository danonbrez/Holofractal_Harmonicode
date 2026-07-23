const CHANNELS = Object.freeze({
  runtime: "/ws/runtime",
  replay: "/ws/replay",
  graph: "/ws/graph",
  transport: "/ws/transport"
});

const COMMANDS = Object.freeze({
  state: { path: "/api/runtime/state", method: "GET" },
  step: { path: "/api/runtime/step", method: "POST", body: { steps: 1 } },
  commit: { path: "/api/runtime/receipt/commit", method: "POST" },
  halt: { path: "/api/runtime/halt", method: "POST" },
  propagate: { path: "/api/runtime/manifold/execution/propagate", method: "POST" },
  revalidate: { path: "/api/runtime/manifold/execution/revalidate", method: "POST" },
  reciprocal: { path: "/api/runtime/authority/topology/reciprocal/status", method: "GET" },
  services: { path: "/api/runtime/services/status", method: "GET" },
  pass152Status: { path: "/api/runtime/pass152/status", method: "GET" },
  pass152Capabilities: { path: "/api/runtime/pass152/capabilities", method: "GET" },
  pass152Latest: { path: "/api/runtime/pass152/latest", method: "GET" },
  pass152Execute: { path: "/api/runtime/pass152/execute", method: "POST", body: { delay_ms: 5, workers: 4 } }
});

function clone(value) {
  return value === undefined ? undefined : JSON.parse(JSON.stringify(value));
}

export class RuntimeBridge extends EventTarget {
  constructor({ fetchImpl = globalThis.fetch?.bind(globalThis), WebSocketImpl = globalThis.WebSocket } = {}) {
    super();
    this.fetchImpl = fetchImpl;
    this.WebSocketImpl = WebSocketImpl;
    this.sockets = {};
    this.retries = {};
    this.status = Object.fromEntries(Object.keys(CHANNELS).map((name) => [name, "disconnected"]));
    this.pollTimer = null;
    this.closed = false;
    this.requestSequence = 0;
    this.inflight = new Map();
    this.lastPayload = null;
  }

  websocketUrl(path) {
    const protocol = location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${location.host}${path}`;
  }

  connectAll() {
    this.closed = false;
    for (const name of Object.keys(CHANNELS)) {
      this.connect(name);
    }
    this.startPolling();
  }

  connect(name) {
    if (!Object.prototype.hasOwnProperty.call(CHANNELS, name)) {
      throw new Error(`UNKNOWN_CHANNEL:${name}`);
    }
    if (!this.WebSocketImpl) {
      this.setStatus(name, "unsupported");
      return;
    }
    const current = this.sockets[name];
    if (current && (current.readyState === 0 || current.readyState === 1)) {
      return;
    }

    this.setStatus(name, "connecting");
    let socket;
    try {
      socket = new this.WebSocketImpl(this.websocketUrl(CHANNELS[name]));
    } catch (error) {
      this.setStatus(name, "error");
      this.emit("bridge-error", { channel: name, error: String(error) });
      return;
    }

    this.sockets[name] = socket;
    socket.addEventListener("open", () => {
      this.retries[name] = 0;
      this.setStatus(name, "connected");
    });
    socket.addEventListener("message", (event) => {
      let payload = event.data;
      try {
        payload = JSON.parse(event.data);
      } catch {
        // Preserve non-JSON payloads verbatim.
      }
      this.lastPayload = payload;
      this.emit("runtime-event", { channel: name, payload, receivedAt: new Date().toISOString() });
    });
    socket.addEventListener("error", () => this.setStatus(name, "error"));
    socket.addEventListener("close", () => {
      this.setStatus(name, "disconnected");
      if (!this.closed) {
        const attempt = (this.retries[name] || 0) + 1;
        this.retries[name] = attempt;
        setTimeout(() => this.connect(name), Math.min(15000, 800 * 2 ** Math.min(attempt, 4)));
      }
    });
  }

  disconnectAll() {
    this.closed = true;
    this.stopPolling();
    for (const socket of Object.values(this.sockets)) {
      try {
        socket.close();
      } catch {
        // Shutdown is best-effort.
      }
    }
    this.sockets = {};
    for (const name of Object.keys(CHANNELS)) {
      this.setStatus(name, "disconnected");
    }
    for (const request of this.inflight.values()) {
      request.controller.abort();
    }
    this.inflight.clear();
  }

  startPolling(intervalMs = 5000) {
    if (this.pollTimer) {
      return;
    }
    const poll = async () => {
      if (this.status.runtime !== "connected") {
        try {
          const payload = await this.request("state", { emitResult: false, timeoutMs: 2200 });
          this.lastPayload = payload;
          this.emit("runtime-event", { channel: "poll", payload, receivedAt: new Date().toISOString() });
        } catch {
          // Poll failures remain represented by request classification.
        }
      }
    };
    poll();
    this.pollTimer = setInterval(poll, intervalMs);
  }

  stopPolling() {
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
  }

  async execute(commandName, options = {}) {
    return this.request(commandName, {
      emitResult: true,
      timeoutMs: options.timeoutMs ?? 6500,
      body: options.body,
      query: options.query
    });
  }

  cancel(requestId) {
    const request = this.inflight.get(requestId);
    if (!request) {
      return false;
    }
    request.controller.abort();
    return true;
  }

  async request(commandName, { emitResult = true, timeoutMs = 5000, body, query } = {}) {
    const command = COMMANDS[commandName];
    if (!command) {
      throw new Error(`UNKNOWN_COMMAND:${commandName}`);
    }
    if (!this.fetchImpl) {
      throw new Error("FETCH_UNAVAILABLE");
    }

    const requestId = ++this.requestSequence;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);
    const requestBody = body === undefined ? command.body : body;
    const queryString = query && typeof query === "object"
      ? `?${new URLSearchParams(Object.entries(query).map(([key, value]) => [key, String(value)]))}`
      : "";
    const startedAt = performance.now();
    this.inflight.set(requestId, { command: commandName, controller, startedAt });
    this.emit("request-start", { requestId, command: commandName, path: command.path, method: command.method });

    try {
      const response = await this.fetchImpl(`${command.path}${queryString}`, {
        method: command.method,
        headers: requestBody !== undefined ? { "Content-Type": "application/json" } : undefined,
        body: requestBody !== undefined ? JSON.stringify(requestBody) : undefined,
        signal: controller.signal
      });
      const text = await response.text();
      let payload = text;
      try {
        payload = text ? JSON.parse(text) : null;
      } catch {
        // Preserve text payloads.
      }
      if (!response.ok) {
        const error = new Error(`HTTP_${response.status}`);
        error.payload = payload;
        throw error;
      }
      this.lastPayload = payload;
      const detail = {
        requestId,
        command: commandName,
        payload,
        durationMs: performance.now() - startedAt,
        receivedAt: new Date().toISOString()
      };
      if (emitResult) {
        this.emit("command-result", detail);
      }
      return payload;
    } catch (error) {
      const normalized = error?.name === "AbortError"
        ? "RUNTIME_REQUEST_TIMEOUT_OR_CANCELLED"
        : `RUNTIME_UNAVAILABLE:${error?.message ?? error}`;
      const detail = {
        requestId,
        command: commandName,
        error: normalized,
        payload: error?.payload ?? null,
        durationMs: performance.now() - startedAt,
        receivedAt: new Date().toISOString()
      };
      if (emitResult) {
        this.emit("command-error", detail);
      }
      throw new Error(normalized);
    } finally {
      clearTimeout(timeout);
      this.inflight.delete(requestId);
      this.emit("request-end", { requestId, command: commandName });
    }
  }

  capabilities() {
    return {
      schema: "HHS_SPATIAL_RUNTIME_BRIDGE_CAPABILITIES_V4",
      commands: Object.keys(COMMANDS),
      channels: Object.keys(CHANNELS),
      statuses: { ...this.status },
      fetchAvailable: Boolean(this.fetchImpl),
      webSocketAvailable: Boolean(this.WebSocketImpl),
      inflight: this.inflight.size
    };
  }

  setStatus(name, status) {
    this.status[name] = status;
    this.emit("channel-status", { channel: name, status, statuses: { ...this.status } });
  }

  emit(type, detail) {
    this.dispatchEvent(new CustomEvent(type, { detail }));
  }
}

export function extractRuntimeSummary(payload) {
  const envelope = payload && typeof payload === "object" ? payload : {};
  const candidates = [
    envelope.runtime,
    envelope.payload?.runtime,
    envelope.data?.runtime,
    envelope.payload,
    envelope.data,
    envelope
  ].filter((value) => value && typeof value === "object");
  const find = (...keys) => {
    for (const object of candidates) {
      for (const key of keys) {
        if (Object.prototype.hasOwnProperty.call(object, key)) {
          return object[key];
        }
      }
    }
    return undefined;
  };
  return {
    step: find("step", "runtime_step", "sequence"),
    state: find("state", "status", "closure_state"),
    receipt: find("receipt_hash72", "hash72", "receipt_hash"),
    opcode: find("opcode", "active_opcode", "operation"),
    entropy: find("entropy", "system_entropy"),
    coherence: find("coherence", "lattice_coherence")
  };
}

export const RUNTIME_COMMANDS = Object.freeze({ ...COMMANDS });
export const RUNTIME_CHANNELS = Object.freeze({ ...CHANNELS });
