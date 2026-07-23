import assert from "node:assert/strict";

globalThis.window = { devicePixelRatio: 1, addEventListener() {} };
const ctx = {
  setTransform() {}, clearRect() {}, beginPath() {}, moveTo() {}, lineTo() {}, stroke() {}, arc() {}, fill() {},
  set globalCompositeOperation(value) { this._g = value; }, get globalCompositeOperation() { return this._g; },
  set lineWidth(value) { this._l = value; }, set strokeStyle(value) { this._s = value; }, set fillStyle(value) { this._f = value; }
};
const listeners = {};
const canvas = {
  clientWidth: 1200, clientHeight: 800, width: 0, height: 0,
  getContext(type) { return type === "2d" ? ctx : null; },
  addEventListener(name, fn) { listeners[name] = fn; },
  setPointerCapture() {}
};
const { SpatialRenderer } = await import("../src/spatial-renderer.js");
const renderer = new SpatialRenderer(canvas);
assert.equal(renderer.backend, "canvas2d");
assert.equal(renderer.pointCount, 8181);
assert.equal(renderer.anchorPositions.length, 81);
assert.equal(renderer.lineSegments.length, 440);
renderer.setActiveCell(40);
renderer.focusCell(40);
assert.equal(renderer.activeCell, 40);
assert.equal(renderer.selectedCell, 40);
assert.deepEqual(renderer.camera.center, renderer.anchorPositions[40]);
renderer.setExplore(true);
assert.equal(renderer.explore, true);
renderer.setParameters({ modulus: 42, curiosity: 0.5, rigidity: 0.9 });
assert.equal(renderer.parameters.modulus, 42);
renderer.setMode("creator");
renderer.setReplayPhase(0.5);
assert.equal(renderer.mode, "creator");
assert.equal(renderer.replayPhase, 0.5);
const camera = renderer.snapshotCamera();
renderer.loadCamera({ ...camera, distance: 9 });
assert.equal(renderer.camera.distance, 9);
renderer.updateMatrices();
const projected = renderer.projectPoint(renderer.anchorPositions[40]);
assert.equal(Boolean(projected), true);
console.log("RENDERER_CONTRACT_PASSED");
console.log("backend=canvas2d");
console.log("projection_nodes=8181");
console.log(`line_segments=${renderer.lineSegments.length}`);
