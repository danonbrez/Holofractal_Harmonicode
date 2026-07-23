import assert from "node:assert/strict";
import { SpatialWorldModel, LOSHU_LAYOUT } from "../src/world-model.js";
import { ProjectionJournal } from "../src/projection-journal.js";
import { THEMES } from "../src/theme-registry.js";
import { TEMPLATES } from "../src/template-registry.js";
import { FEATURES, MODES } from "../src/feature-registry.js";
import { APPLICATIONS } from "../src/application-registry.js";
import { SessionStore } from "../src/session-store.js";
import { SpatialWorkspaceManager } from "../src/spatial-workspace-manager.js";
import { ReplayController } from "../src/replay-controller.js";
import { TelemetryStore } from "../src/telemetry-store.js";
import { CommandRouter } from "../src/command-router.js";
import { extractRuntimeSummary, RuntimeBridge, RUNTIME_COMMANDS } from "../src/runtime-bridge.js";

class MemoryStorage {
  constructor() { this.map = new Map(); }
  getItem(key) { return this.map.get(key) ?? null; }
  setItem(key, value) { this.map.set(key, String(value)); }
  removeItem(key) { this.map.delete(key); }
}

assert.equal(THEMES.length, 7);
assert.equal(TEMPLATES.length, 9);
assert.equal(FEATURES.length, 12);
assert.equal(MODES.length, 5);
assert.equal(APPLICATIONS.length, 22);
assert.equal(Object.keys(RUNTIME_COMMANDS).length, 12);
assert.deepEqual(LOSHU_LAYOUT, [4, 9, 2, 3, 5, 7, 8, 1, 6]);

const world = new SpatialWorldModel();
assert.equal(world.cells.length, 81);
assert.equal(world.cells[0].loshu, 4);
assert.equal(world.cells[40].loshu, 5);
assert.equal(world.cells[80].loshu, 6);
assert.deepEqual(world.cells[40].neighbors.sort((a, b) => a - b), [31, 39, 41, 49]);
world.bindRuntime({ step: 82, state: "CLOSED", opcode: "OP_CLOSE81", receipt: "abc" });
assert.equal(world.activeCell, 1);
assert.equal(world.cells[1].opcode, "OP_CLOSE81");
assert.equal(world.cells[1].activationCount, 1);
assert.equal(world.select(40).index, 41);
assert.equal(world.togglePin(40).pinned, true);
assert.equal(world.snapshot().selectedCell, 40);

const journal = new ProjectionJournal();
const first = await journal.append("A", { x: 1 });
const second = await journal.append("B", { y: 2 });
assert.equal(second.previous, first.digest);
assert.notEqual(first.digest, second.digest);
assert.equal((await journal.verify()).valid, true);
assert.equal(journal.export().classification, "NON_AUTHORITATIVE_PRESENTATION_JOURNAL");

const storage = new MemoryStorage();
const sessions = new SessionStore({ storage });
assert.equal(sessions.list().length, 1);
const created = sessions.create("Analysis Room", { activeTheme: "violet-magenta" });
assert.equal(sessions.activeSessionId, created.id);
sessions.update({ activeFeature: "metrics" });
const snapshot = sessions.saveSnapshot("A", { selectedCell: 40 });
assert.deepEqual(sessions.restoreSnapshot(snapshot.id), { selectedCell: 40 });
const exportedSessions = sessions.export();
assert.equal(exportedSessions.schema, "HHS_SPATIAL_SESSION_EXPORT_V3");
const importedStore = new SessionStore({ storage: new MemoryStorage() });
importedStore.import(exportedSessions, { merge: false });
assert.equal(importedStore.list().length, 2);

const workspace = new SpatialWorkspaceManager({ viewportProvider: () => ({ width: 1200, height: 800 }) });
const app = APPLICATIONS[0];
const surface = workspace.open(app);
assert.equal(workspace.surfaces.length, 1);
workspace.move(surface.id, 100, 120);
workspace.resize(surface.id, 600, 400);
workspace.dock(surface.id, "left");
assert.equal(workspace.get(surface.id).dock, "left");
workspace.arrange("grid");
assert.equal(workspace.get(surface.id).dock, null);
assert.equal(workspace.snapshot().schema, "HHS_SPATIAL_SURFACE_LAYOUT_V3");

const replay = new ReplayController({ tickMs: 5 });
replay.load(journal.timeline());
assert.equal(replay.snapshot().total, 2);
assert.equal(replay.seek(1).type, "B");
replay.setSpeed(4);
assert.equal(replay.snapshot().speed, 4);

const telemetry = new TelemetryStore({ limit: 10 });
telemetry.recordRenderer({ fps: 60, nodes: 8181, backend: "canvas2d", selectedCell: 40, activeCell: 1 });
telemetry.recordRenderer({ fps: 58, nodes: 8181, backend: "canvas2d", selectedCell: 40, activeCell: 1 });
assert.equal(telemetry.numericSummary("renderer.fps").mean, 59);

const fakeFetch = async () => ({ ok: true, status: 200, text: async () => JSON.stringify({ runtime: { step: 7 } }) });
const bridge = new RuntimeBridge({ fetchImpl: fakeFetch, WebSocketImpl: null });
const router = new CommandRouter({ bridge, journal, telemetry });
router.registerRuntime("state");
router.register({ id: "local.echo", handler: ({ value }) => ({ value }) });
assert.deepEqual(await router.execute("local.echo", { value: 9 }), { value: 9 });
assert.equal((await router.execute("runtime.state")).runtime.step, 7);
assert.equal(router.snapshot().history.length, 2);

const summary = extractRuntimeSummary({ payload: { runtime: { step: 7, active_opcode: "OP_QGU", receipt_hash72: "r" } } });
assert.equal(summary.step, 7);
assert.equal(summary.opcode, "OP_QGU");
assert.equal(summary.receipt, "r");

console.log("MODULE_CONTRACT_PASSED");
console.log("cells=81");
console.log("applications=22");
console.log("themes=7");
console.log("sessions=2");
console.log("runtime_commands=12");
