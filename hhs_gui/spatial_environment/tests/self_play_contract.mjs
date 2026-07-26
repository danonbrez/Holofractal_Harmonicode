import assert from "node:assert/strict";
import { AgenticSelfPlayHarness } from "../src/self-play-harness.js";
import { TelemetryStore } from "../src/telemetry-store.js";
import { V1_PROMPT_CONTRACTS, V1_SCOPE } from "../src/prompt-contracts.js";

const responses = {
  state: [
    { runtime: { step: 10, state: "OPEN", receipt_hash72: "r10" } },
    { runtime: { step: 11, state: "OPEN", receipt_hash72: "r11" } },
    { runtime: { step: 12, state: "OPEN", receipt_hash72: "r12" } },
    { runtime: { step: 13, state: "OPEN", receipt_hash72: "r13" } },
    { runtime: { step: 14, state: "OPEN", receipt_hash72: "r14" } },
    { runtime: { step: 15, state: "OPEN", receipt_hash72: "r15" } }
  ],
  step: [{ runtime: { step: 11, state: "OPEN", receipt_hash72: "r11" } }, { runtime: { step: 12, state: "OPEN", receipt_hash72: "r12" } }],
  commit: [{ runtime: { step: 12, state: "OPEN", receipt_hash72: "r12" } }, { runtime: { step: 13, state: "OPEN", receipt_hash72: "r13" } }]
};

const indexes = { state: 0, step: 0, commit: 0 };

const executeRuntimeCommand = async (command) => {
  const bucket = responses[command];
  assert.ok(bucket, `Unknown command in test stub: ${command}`);
  const index = Math.min(indexes[command], bucket.length - 1);
  indexes[command] += 1;
  return bucket[index];
};

const extractRuntimeSummary = (payload) => ({
  step: payload?.runtime?.step,
  state: payload?.runtime?.state,
  receipt: payload?.runtime?.receipt_hash72
});

const telemetry = new TelemetryStore({ limit: 20 });
const harness = new AgenticSelfPlayHarness({ executeRuntimeCommand, extractRuntimeSummary, telemetry });

const suite = await harness.runSuite({ contracts: V1_PROMPT_CONTRACTS, maxRetries: 1 });
assert.equal(suite.scope.id, V1_SCOPE.id);
assert.equal(suite.contracts.length, 3);
assert.equal(suite.summary.contracts, 3);
assert.equal(suite.summary.failures, 0);
assert.equal(suite.summary.completionRate, 1);
assert.ok(suite.apiCoverage.state);
assert.ok(suite.apiCoverage.step);
assert.ok(suite.apiCoverage.commit);
assert.ok(Array.isArray(suite.friction));
assert.ok(suite.friction.length >= 1);
assert.equal(telemetry.counters.selfPlayRuns, 1);
assert.equal(telemetry.counters.promptPasses, 3);
assert.equal(telemetry.counters.promptFailures, 0);

const loop = await harness.runCapabilityLoop({ contracts: V1_PROMPT_CONTRACTS });
assert.equal(loop.schema, "HHS_AGENTIC_CAPABILITY_LOOP_V1");
assert.ok(loop.baseline.summary.contracts >= 1);
assert.ok(loop.replay.summary.contracts >= 1);
assert.ok(Object.prototype.hasOwnProperty.call(loop.delta, "completionDelta"));
assert.equal(telemetry.counters.capabilityLoops, 1);
assert.equal(telemetry.selfPlay.lastLoop.schema, "HHS_AGENTIC_CAPABILITY_LOOP_V1");

console.log("SELF_PLAY_CONTRACT_PASSED");
console.log(`contracts=${suite.summary.contracts}`);
console.log(`coverage=${Object.keys(suite.apiCoverage).length}`);
