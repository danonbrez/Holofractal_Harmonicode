import test from "node:test";
import assert from "node:assert/strict";

import {
  PARTICLE_COUNT,
  createAddressTable,
  mapLinearIndex,
  pairToLinearIndex,
  validateAddressTable,
} from "../src/physics/address_map.js";
import { HHSParticleEngine } from "../src/physics/engine.js";
import { HHSTraceChain } from "../src/trace/chain.js";
import { ACTIONS, createInitialState, reduceApplicationState } from "../src/app/state.js";
import { ExactRatio, HHSExactBridge } from "../src/kernel/exact_bridge.js";

test("all 5,184 Hash72 pair addresses are bijective", () => {
  const table = createAddressTable();
  const proof = validateAddressTable(table);
  assert.equal(table.length, PARTICLE_COUNT);
  assert.equal(proof.valid, true);
  assert.equal(proof.unique_indices, 5184);
  assert.equal(proof.unique_pairs, 5184);
  assert.equal(proof.sector_pairs, 64);
  assert.equal(proof.every_sector_has_vm81, true);
});

test("linear and pair mappings are exact inverses", () => {
  for (const index of [0, 1, 71, 72, 143, 5183]) {
    const particle = mapLinearIndex(index);
    assert.equal(pairToLinearIndex(particle.hash_state_a, particle.hash_state_b), index);
  }
});

test("reciprocal mapping is an involution", () => {
  for (const index of [0, 72, 999, 4096, 5183]) {
    const particle = mapLinearIndex(index);
    assert.equal(mapLinearIndex(particle.reciprocal_index).reciprocal_index, index);
  }
});

test("every sector pair contains each VM81 cell exactly once", () => {
  const table = createAddressTable();
  for (let sectorA = 0; sectorA < 8; sectorA += 1) {
    for (let sectorB = 0; sectorB < 8; sectorB += 1) {
      const cells = table
        .filter((particle) => particle.sector_a === sectorA && particle.sector_b === sectorB)
        .map((particle) => particle.vm81_cell);
      assert.equal(cells.length, 81);
      assert.deepEqual([...new Set(cells)].sort((a, b) => a - b), Array.from({ length: 81 }, (_, index) => index));
    }
  }
});

test("fixed-step particle execution is deterministic", () => {
  const left = new HHSParticleEngine();
  const right = new HHSParticleEngine();
  left.reset(157);
  right.reset(157);
  left.step(3);
  right.step(3);
  assert.equal(left.serialize().state_hash72, right.serialize().state_hash72);
});

test("pause does not change state and single-step advances exactly once", () => {
  const engine = new HHSParticleEngine();
  engine.pause();
  const before = engine.serialize();
  assert.equal(engine.serialize().state_hash72, before.state_hash72);
  const after = engine.step(1);
  assert.equal(after.step_count, 1);
});

test("physics replay reconstructs the same receipt", () => {
  const engine = new HHSParticleEngine();
  engine.reset(9);
  const receipt = engine.step(2);
  const replay = engine.replay(receipt);
  assert.equal(replay.match, true);
  assert.equal(replay.classification, "PASS157_REPLAY_MATCH");
});

test("trace events form an append-only verifiable chain", () => {
  const trace = new HHSTraceChain("test");
  trace.append("APP_BOOT", { pass: 157 });
  trace.append("PARTICLE_FIELD_ADVANCED", { step: 1 });
  assert.equal(trace.verify().valid, true);
  const bundle = trace.seal();
  assert.equal(HHSTraceChain.verifyBundle(bundle).valid, true);
  assert.throws(() => trace.append("MUTATION_AFTER_SEAL"), /TRACE_ALREADY_SEALED/);
});

test("typed state actions cannot promote render values into exact authority", () => {
  const initial = createInitialState();
  const next = reduceApplicationState(initial, {
    type: ACTIONS.LOD_PROFILE_CHANGED,
    payload: { profile: "DESKTOP_HIGH" },
  });
  assert.equal(next.render_projection_state.profile, "DESKTOP_HIGH");
  assert.deepEqual(next.exact_runtime_state, initial.exact_runtime_state);
  assert.equal(next.exact_runtime_state.render_float_is_authority, false);
});

test("exact ratio arithmetic round-trips without floats", () => {
  const result = new ExactRatio(1n, 3n).add(new ExactRatio(2n, 3n));
  assert.equal(result.toString(), "1");
});

test("phase reciprocal is parsed as a typed transition", () => {
  const exact = new HHSExactBridge();
  const parsed = exact.parse("1/0; 0^-1; u^72");
  assert.equal(parsed.nodes.some((node) => node.node === "PHASE_RECIPROCAL"), true);
  assert.equal(parsed.nodes.some((node) => node.node === "PHASE_POWER"), true);
});

test("unregistered substitution is rejected", () => {
  const exact = new HHSExactBridge();
  assert.throws(() => exact.substitute("missing", "Phi^2"), /SUBSTITUTION_UNAUTHORIZED/);
});

test("registered equality produces an auditable proof hash", () => {
  const exact = new HHSExactBridge();
  const link = exact.registerEquality("golden", "Phi^2", "Phi+1");
  const result = exact.substitute("golden", "Phi^2-t");
  assert.equal(link.proof_hash72.length, 72);
  assert.equal(result.result, "(Phi+1)-t");
});

test("invalid inputs are safely classified", () => {
  assert.throws(() => pairToLinearIndex(72, 0), RangeError);
  assert.throws(() => new HHSParticleEngine({ fixedStep: 0 }), /INVALID_FIXED_TIMESTEP/);
  assert.throws(() => new ExactRatio(1n, 0n), /ZERO_DENOMINATOR_REQUIRES_TYPED_PHASE_DISPATCH/);
});
