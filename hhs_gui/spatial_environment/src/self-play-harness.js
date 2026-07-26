import { V1_PROMPT_CONTRACTS, V1_SCOPE } from "./prompt-contracts.js";

function nowIso() {
  return new Date().toISOString();
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function classifyError(error) {
  const text = String(error?.message ?? error ?? "UNKNOWN_ERROR");
  if (text.includes("TIMEOUT")) return "timeout";
  if (text.includes("UNAVAILABLE")) return "unavailable";
  if (text.includes("HTTP_")) return "http";
  return "execution";
}

function promptClarityProxy(prompt) {
  const text = String(prompt ?? "");
  const lower = text.toLowerCase();
  const ambiguityMarkers = ["maybe", "somehow", "thing", "stuff", "probably"];
  const ambiguityPenalty = ambiguityMarkers.reduce((score, token) => score + (lower.includes(token) ? 12 : 0), 0);
  const lengthPenalty = Math.max(0, Math.ceil((text.length - 110) / 28)) * 3;
  return Math.max(0, Math.min(100, 100 - ambiguityPenalty - lengthPenalty));
}

function summarizeCalls(calls) {
  const total = calls.length;
  const succeeded = calls.filter((call) => call.ok).length;
  const failed = total - succeeded;
  const retries = calls.reduce((sum, call) => sum + (call.attempt - 1), 0);
  const durations = calls.map((call) => call.durationMs).filter(Number.isFinite);
  const meanDurationMs = durations.length ? durations.reduce((sum, value) => sum + value, 0) / durations.length : 0;
  return { total, succeeded, failed, retries, meanDurationMs };
}

function makeCoverage(calls) {
  const coverage = {};
  for (const call of calls) {
    const current = coverage[call.command] ?? { attempts: 0, succeeded: 0, failed: 0, meanDurationMs: 0, samples: 0 };
    current.attempts += 1;
    if (call.ok) current.succeeded += 1;
    if (!call.ok) current.failed += 1;
    current.samples += 1;
    current.meanDurationMs = ((current.meanDurationMs * (current.samples - 1)) + call.durationMs) / current.samples;
    coverage[call.command] = current;
  }
  for (const stats of Object.values(coverage)) {
    delete stats.samples;
  }
  return coverage;
}

function rankFriction(contracts) {
  return contracts
    .map((contract) => {
      const failureWeight = contract.passed ? 0 : 100;
      const retryWeight = contract.summary.retries * 10;
      const latencyWeight = contract.summary.meanDurationMs > 0 ? Math.round(contract.summary.meanDurationMs / 50) : 0;
      const clarityWeight = Math.max(0, 75 - contract.promptClarity);
      const score = failureWeight + retryWeight + latencyWeight + clarityWeight;
      return {
        contractId: contract.id,
        score,
        passed: contract.passed,
        meanDurationMs: contract.summary.meanDurationMs,
        retries: contract.summary.retries,
        promptClarity: contract.promptClarity,
        primaryIssue: contract.passed ? "latency_or_clarity" : "execution_failure"
      };
    })
    .sort((a, b) => b.score - a.score);
}

function improvePrompt(prompt) {
  return String(prompt ?? "")
    .replace(/\bmaybe\b/gi, "")
    .replace(/\bprobably\b/gi, "")
    .replace(/\s+/g, " ")
    .trim();
}

function optimizeContracts(contracts, friction) {
  const frictionIds = new Set(friction.slice(0, 2).map((item) => item.contractId));
  return contracts.map((contract) => (
    frictionIds.has(contract.id)
      ? { ...contract, developerPrompt: improvePrompt(contract.developerPrompt), runtimePrompt: improvePrompt(contract.runtimePrompt) }
      : { ...contract }
  ));
}

function compareSuites(baseline, replay) {
  return {
    completionDelta: replay.summary.completionRate - baseline.summary.completionRate,
    meanLatencyDeltaMs: replay.summary.meanDurationMs - baseline.summary.meanDurationMs,
    errorDelta: replay.summary.failures - baseline.summary.failures,
    clarityDelta: replay.summary.meanPromptClarity - baseline.summary.meanPromptClarity
  };
}

export class AgenticSelfPlayHarness {
  constructor({ executeRuntimeCommand, extractRuntimeSummary, telemetry } = {}) {
    this.executeRuntimeCommand = executeRuntimeCommand;
    this.extractRuntimeSummary = extractRuntimeSummary;
    this.telemetry = telemetry;
  }

  async runSuite({ contracts = V1_PROMPT_CONTRACTS, maxRetries = V1_SCOPE.successCriteria.maxPromptRetriesPerContract } = {}) {
    if (typeof this.executeRuntimeCommand !== "function") {
      throw new Error("SELF_PLAY_EXECUTOR_UNAVAILABLE");
    }
    const startedAt = nowIso();
    const contractResults = [];
    const allCalls = [];

    for (const contract of contracts) {
      const calls = [];
      let passed = true;
      const maxAttempts = Math.max(1, Number(maxRetries) + 1);

      for (const expectedCall of contract.expectedCalls) {
        let callCompleted = false;
        for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
          const start = performance.now();
          let payload = null;
          let ok = false;
          let error = null;
          try {
            payload = await this.executeRuntimeCommand(expectedCall.command, expectedCall.args ?? {});
            ok = true;
            callCompleted = true;
          } catch (caught) {
            error = {
              message: String(caught?.message ?? caught),
              class: classifyError(caught)
            };
          }
          const durationMs = performance.now() - start;
          const runtimeSummary = this.extractRuntimeSummary?.(payload) ?? {};
          const call = {
            contractId: contract.id,
            command: expectedCall.command,
            args: clone(expectedCall.args ?? {}),
            attempt,
            ok,
            error,
            durationMs,
            runtimeSummary,
            completedAt: nowIso()
          };
          calls.push(call);
          allCalls.push(call);
          this.telemetry?.recordSelfPlayCall(contract.id, call);
          if (ok) break;
        }
        if (!callCompleted) {
          passed = false;
        }
      }

      const observedSummaries = calls.map((call) => call.runtimeSummary ?? {}).filter((value) => value && typeof value === "object");
      const hasSignal = (signal) => observedSummaries.some((summary) => summary[signal] !== undefined && summary[signal] !== null);
      const signalsSatisfied = (contract.expectedSignals ?? []).every((signal) => hasSignal(signal));
      passed = passed && signalsSatisfied;
      const summary = summarizeCalls(calls);
      const promptClarity = Math.round((promptClarityProxy(contract.developerPrompt) + promptClarityProxy(contract.runtimePrompt)) / 2);
      const result = {
        id: contract.id,
        passed,
        promptClarity,
        signalsSatisfied,
        expectedSignals: clone(contract.expectedSignals ?? []),
        summary,
        calls: clone(calls)
      };
      contractResults.push(result);
      this.telemetry?.recordPromptContract(result);
    }

    const completionRate = contractResults.length
      ? contractResults.filter((contract) => contract.passed).length / contractResults.length
      : 0;
    const totalDurationMs = allCalls.reduce((sum, call) => sum + call.durationMs, 0);
    const meanDurationMs = allCalls.length ? totalDurationMs / allCalls.length : 0;
    const failures = allCalls.filter((call) => !call.ok).length;
    const summary = {
      contracts: contractResults.length,
      completionRate,
      failures,
      meanDurationMs,
      meanPromptClarity: contractResults.length
        ? contractResults.reduce((sum, contract) => sum + contract.promptClarity, 0) / contractResults.length
        : 0
    };
    const coverage = makeCoverage(allCalls);
    const friction = rankFriction(contractResults);
    const report = {
      schema: "HHS_AGENTIC_SELF_PLAY_REPORT_V1",
      scope: clone(V1_SCOPE),
      startedAt,
      completedAt: nowIso(),
      summary,
      contracts: contractResults,
      apiCoverage: coverage,
      friction
    };
    this.telemetry?.recordSelfPlaySuite(report);
    return report;
  }

  async runCapabilityLoop({ contracts = V1_PROMPT_CONTRACTS } = {}) {
    const baseline = await this.runSuite({ contracts });
    const optimizedContracts = optimizeContracts(contracts, baseline.friction);
    const replay = await this.runSuite({ contracts: optimizedContracts });
    const delta = compareSuites(baseline, replay);
    const report = {
      schema: "HHS_AGENTIC_CAPABILITY_LOOP_V1",
      baseline,
      replay,
      delta,
      optimizedContracts: optimizedContracts.map((contract) => ({ id: contract.id, developerPrompt: contract.developerPrompt, runtimePrompt: contract.runtimePrompt }))
    };
    this.telemetry?.recordCapabilityLoop(report);
    return report;
  }
}

