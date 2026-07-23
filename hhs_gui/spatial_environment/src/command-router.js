function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

export class CommandRouter extends EventTarget {
  constructor({ bridge, journal, telemetry } = {}) {
    super();
    this.bridge = bridge;
    this.journal = journal;
    this.telemetry = telemetry;
    this.commands = new Map();
    this.history = [];
    this.sequence = 0;
    this.running = new Map();
  }

  register(definition) {
    if (!definition?.id || typeof definition.handler !== "function") {
      throw new Error("INVALID_COMMAND_DEFINITION");
    }
    this.commands.set(definition.id, {
      label: definition.id,
      authority: "PRESENTATION_ONLY",
      category: "local",
      ...definition
    });
    return this;
  }

  registerRuntime(commandName, options = {}) {
    return this.register({
      id: `runtime.${commandName}`,
      label: options.label ?? `Runtime ${commandName}`,
      authority: "GUARDED_BACKEND_REQUEST",
      category: "runtime",
      handler: (args = {}) => this.bridge.execute(commandName, args)
    });
  }

  list() {
    return [...this.commands.values()].map(({ handler, ...definition }) => clone(definition));
  }

  async execute(id, args = {}, context = {}) {
    const command = this.commands.get(id);
    if (!command) {
      throw new Error(`UNKNOWN_ROUTED_COMMAND:${id}`);
    }
    const invocation = {
      id: ++this.sequence,
      command: id,
      label: command.label,
      authority: command.authority,
      category: command.category,
      args: clone(args),
      startedAt: new Date().toISOString(),
      status: "RUNNING"
    };
    const start = performance.now();
    this.running.set(invocation.id, invocation);
    this.emit("command-start", clone(invocation));
    await this.journal?.append("COMMAND_ROUTER_START", invocation, command.authority);

    try {
      const result = await command.handler(args, context);
      invocation.status = "COMPLETED";
      invocation.completedAt = new Date().toISOString();
      invocation.durationMs = performance.now() - start;
      invocation.result = clone(result ?? null);
      this.telemetry?.recordCommand(id, true, invocation.durationMs, command.authority);
      await this.journal?.append("COMMAND_ROUTER_COMPLETE", {
        id: invocation.id,
        command: id,
        durationMs: invocation.durationMs,
        result: invocation.result
      }, command.authority);
      this.finish(invocation);
      this.emit("command-complete", clone(invocation));
      return clone(result);
    } catch (error) {
      invocation.status = "FAILED";
      invocation.completedAt = new Date().toISOString();
      invocation.durationMs = performance.now() - start;
      invocation.error = String(error?.message ?? error);
      this.telemetry?.recordCommand(id, false, invocation.durationMs, command.authority);
      await this.journal?.append("COMMAND_ROUTER_FAILURE", {
        id: invocation.id,
        command: id,
        durationMs: invocation.durationMs,
        error: invocation.error
      }, "ERROR_PROJECTION");
      this.finish(invocation);
      this.emit("command-failure", clone(invocation));
      throw error;
    }
  }

  finish(invocation) {
    this.running.delete(invocation.id);
    this.history.unshift(clone(invocation));
    this.history = this.history.slice(0, 100);
  }

  snapshot() {
    return {
      schema: "HHS_SPATIAL_COMMAND_ROUTER_STATE_V3",
      registered: this.list(),
      running: [...this.running.values()].map(clone),
      history: clone(this.history)
    };
  }

  emit(type, detail) {
    this.dispatchEvent(new CustomEvent(type, { detail }));
  }
}
