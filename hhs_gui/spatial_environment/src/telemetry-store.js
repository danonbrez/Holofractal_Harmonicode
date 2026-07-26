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
      channelTransitions: 0,
      promptContracts: 0,
      promptPasses: 0,
      promptFailures: 0,
      selfPlayRuns: 0,
      capabilityLoops: 0
    };
    this.selfPlay = {
      lastSuite: null,
      lastLoop: null,
      promptContracts: [],
      callTrace: [],
      apiCoverage: {}
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

  recordSelfPlayCall(contractId, call) {
    this.callTracePush({
      contractId,
      command: call.command,
      ok: call.ok,
      attempt: call.attempt,
      durationMs: call.durationMs,
      errorClass: call.error?.class ?? null,
      completedAt: call.completedAt
    });
  }

  recordPromptContract(contract) {
    this.counters.promptContracts += 1;
    if (contract.passed) {
      this.counters.promptPasses += 1;
    } else {
      this.counters.promptFailures += 1;
    }
    this.selfPlay.promptContracts.unshift(clone({
      id: contract.id,
      passed: contract.passed,
      promptClarity: contract.promptClarity,
      retries: contract.summary?.retries ?? 0,
      meanDurationMs: contract.summary?.meanDurationMs ?? 0,
      signalsSatisfied: contract.signalsSatisfied
    }));
    this.selfPlay.promptContracts = this.selfPlay.promptContracts.slice(0, 120);
    this.record("selfplay.prompt.pass", contract.passed ? 1 : 0, { contractId: contract.id });
    this.record("selfplay.prompt.clarity", contract.promptClarity ?? null, { contractId: contract.id });
  }

  recordSelfPlaySuite(suiteReport) {
    this.counters.selfPlayRuns += 1;
    this.selfPlay.lastSuite = clone(suiteReport);
    this.selfPlay.apiCoverage = clone(suiteReport.apiCoverage ?? {});
    this.record("selfplay.completionRate", suiteReport.summary?.completionRate ?? 0);
    this.record("selfplay.meanDurationMs", suiteReport.summary?.meanDurationMs ?? 0);
  }

  recordCapabilityLoop(loopReport) {
    this.counters.capabilityLoops += 1;
    this.selfPlay.lastLoop = clone(loopReport);
    this.record("selfplay.loop.completionDelta", loopReport.delta?.completionDelta ?? 0);
    this.record("selfplay.loop.meanLatencyDeltaMs", loopReport.delta?.meanLatencyDeltaMs ?? 0);
  }

  callTracePush(sample) {
    this.selfPlay.callTrace.unshift(clone(sample));
    this.selfPlay.callTrace = this.selfPlay.callTrace.slice(0, this.limit);
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
      series: Object.fromEntries([...this.series.entries()].map(([name, values]) => [name, clone(values)])),
      selfPlay: clone(this.selfPlay)
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
      channelTransitions: 0,
      promptContracts: 0,
      promptPasses: 0,
      promptFailures: 0,
      selfPlayRuns: 0,
      capabilityLoops: 0
    };
    this.selfPlay = {
      lastSuite: null,
      lastLoop: null,
      promptContracts: [],
      callTrace: [],
      apiCoverage: {}
    };
    this.dispatchEvent(new CustomEvent("cleared"));
  }
}
