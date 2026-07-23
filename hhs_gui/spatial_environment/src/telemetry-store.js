const DEFAULT_LIMIT = 360;

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function now() {
  return new Date().toISOString();
}

export class TelemetryStore extends EventTarget {
  constructor({ limit = DEFAULT_LIMIT } = {}) {
    super();
    this.limit = limit;
    this.series = new Map();
    this.latest = {};
    this.counters = {
      rendererSamples: 0,
      runtimeEvents: 0,
      commandResults: 0,
      commandErrors: 0,
      channelTransitions: 0
    };
  }

  record(name, value, metadata = {}) {
    const sample = {
      time: now(),
      value: typeof value === "number" && Number.isFinite(value) ? value : value ?? null,
      metadata: clone(metadata)
    };
    const values = this.series.get(name) ?? [];
    values.push(sample);
    if (values.length > this.limit) {
      values.splice(0, values.length - this.limit);
    }
    this.series.set(name, values);
    this.latest[name] = sample;
    this.dispatchEvent(new CustomEvent("sample", { detail: { name, sample: clone(sample) } }));
    return clone(sample);
  }

  recordRenderer(metrics = {}) {
    this.counters.rendererSamples += 1;
    for (const key of ["fps", "nodes", "selectedCell", "activeCell"]) {
      if (metrics[key] !== undefined) {
        this.record(`renderer.${key}`, metrics[key], { backend: metrics.backend });
      }
    }
    this.record("renderer.backend", metrics.backend ?? "unavailable");
  }

  recordRuntime(summary = {}, source = "runtime") {
    this.counters.runtimeEvents += 1;
    for (const key of ["step", "entropy", "coherence"]) {
      if (summary[key] !== undefined && summary[key] !== null) {
        this.record(`runtime.${key}`, summary[key], { source });
      }
    }
    if (summary.state !== undefined) {
      this.record("runtime.state", summary.state, { source });
    }
    if (summary.opcode !== undefined) {
      this.record("runtime.opcode", summary.opcode, { source });
    }
    if (summary.receipt !== undefined) {
      this.record("runtime.receipt", summary.receipt, { source });
    }
  }

  recordChannel(channel, status) {
    this.counters.channelTransitions += 1;
    this.record(`channel.${channel}`, status);
  }

  recordCommand(command, ok, durationMs, classification) {
    if (ok) {
      this.counters.commandResults += 1;
    } else {
      this.counters.commandErrors += 1;
    }
    this.record(`command.${command}.durationMs`, durationMs, { ok, classification });
    this.record(`command.${command}.status`, ok ? "ok" : "error", { classification });
  }

  getSeries(name, limit = this.limit) {
    const values = this.series.get(name) ?? [];
    return clone(values.slice(-limit));
  }

  numericSummary(name) {
    const values = (this.series.get(name) ?? [])
      .map((sample) => Number(sample.value))
      .filter(Number.isFinite);
    if (!values.length) {
      return { count: 0, min: null, max: null, mean: null, latest: null };
    }
    const total = values.reduce((sum, value) => sum + value, 0);
    return {
      count: values.length,
      min: Math.min(...values),
      max: Math.max(...values),
      mean: total / values.length,
      latest: values.at(-1)
    };
  }

  snapshot() {
    return {
      schema: "HHS_SPATIAL_TELEMETRY_SNAPSHOT_V3",
      generatedAt: now(),
      counters: { ...this.counters },
      latest: clone(this.latest),
      series: Object.fromEntries([...this.series.entries()].map(([name, values]) => [name, clone(values)]))
    };
  }

  clear() {
    this.series.clear();
    this.latest = {};
    this.counters = {
      rendererSamples: 0,
      runtimeEvents: 0,
      commandResults: 0,
      commandErrors: 0,
      channelTransitions: 0
    };
    this.dispatchEvent(new CustomEvent("cleared"));
  }
}
