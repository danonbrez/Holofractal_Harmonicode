import test from "node:test";
import assert from "node:assert/strict";

import {
  DEFAULT_LOD_THRESHOLDS,
  cameraDistance,
  selectLod,
  validateLodThresholds,
} from "../src/render/lod.js";

test("LOD thresholds contain valid hysteresis gaps", () => {
  assert.equal(validateLodThresholds(DEFAULT_LOD_THRESHOLDS).valid, true);
});

test("LOD uses camera-relative rather than world-origin distance", () => {
  assert.equal(cameraDistance([100, 0, 0], [99, 0, 0]), 1);
  assert.equal(selectLod("LOD3", 1), "LOD2");
});

test("LOD hysteresis prevents boundary oscillation", () => {
  assert.equal(selectLod("LOD0", DEFAULT_LOD_THRESHOLDS.D01_IN + 1), "LOD0");
  assert.equal(selectLod("LOD1", DEFAULT_LOD_THRESHOLDS.D01_IN + 1), "LOD1");
  assert.equal(selectLod("LOD1", DEFAULT_LOD_THRESHOLDS.D01_IN - 1), "LOD0");
  assert.equal(selectLod("LOD0", DEFAULT_LOD_THRESHOLDS.D01_OUT + 1), "LOD1");
});

test("invalid LOD thresholds are rejected", () => {
  const invalid = { ...DEFAULT_LOD_THRESHOLDS, D01_OUT: DEFAULT_LOD_THRESHOLDS.D01_IN };
  assert.equal(validateLodThresholds(invalid).valid, false);
  assert.throws(() => selectLod("LOD0", 1, invalid), /INVALID_LOD_THRESHOLDS/);
});
