import assert from "node:assert/strict";
import { EntitySceneGraph } from "../src/entity-scene-graph.js";
import { AssetRegistry } from "../src/asset-registry.js";
import { WorldRouter } from "../src/world-router.js";
import { SimulationEngine } from "../src/simulation-engine.js";
import { ProjectStore } from "../src/project-store.js";

class MemoryStorage {
  constructor() { this.map = new Map(); }
  getItem(key) { return this.map.get(key) ?? null; }
  setItem(key, value) { this.map.set(key, String(value)); }
}

const scene = new EntitySceneGraph({ maxEntities: 3 });
const parent = scene.createPrimitive("orb");
const child = scene.createPrimitive("portal", { parentId: parent.id });
assert.throws(() => scene.createPrimitive("panel"), /ENTITY_LIMIT_REACHED/);
assert.throws(() => scene.removeEntity("world-root"), /WORLD_ROOT_IMMUTABLE/);
assert.throws(() => scene.reparent(parent.id, child.id), /SCENE_GRAPH_CYCLE/);
assert.throws(() => scene.removeComponent(parent.id, "Transform"), /TRANSFORM_COMPONENT_REQUIRED/);

const assets = new AssetRegistry({ maxAssetBytes: 4 });
await assert.rejects(() => assets.ingest({ name: "big.bin", bytes: new Uint8Array(5) }), /ASSET_SIZE_LIMIT_REACHED/);
await assert.rejects(() => assets.ingest({ name: "none.bin" }), /ASSET_BYTES_UNAVAILABLE/);

const router = new WorldRouter({ maxRoutes: 1 });
router.syncWorlds([{ id: "a" }, { id: "b" }, { id: "c" }]);
assert.throws(() => router.addRoute({ from: "a", to: "a" }), /SELF_ROUTE_REJECTED/);
router.addRoute({ from: "a", to: "b" });
assert.throws(() => router.addRoute({ from: "b", to: "c" }), /ROUTE_LIMIT_REACHED/);
assert.throws(() => router.navigate("c"), /WORLD_ROUTE_UNREACHABLE/);
assert.throws(() => router.load({ worlds: [{ id: "a" }], routes: [{ id: "r", from: "a", to: "missing" }] }), /DANGLING_WORLD_ROUTE/);

const simulation = new SimulationEngine({ scene: new EntitySceneGraph(), maximumBatchSteps: 2 });
simulation.step(100);
assert.equal(simulation.snapshot().tick, 2);

const projects = new ProjectStore({ storage: new MemoryStorage() });
assert.throws(() => projects.delete(projects.activeProjectId), /CANNOT_DELETE_LAST_PROJECT/);
assert.throws(() => projects.import({ schema: "BAD" }), /INVALID_PROJECT_EXPORT/);
const snapshot = await projects.saveWorldSnapshot("A", { value: 1 });
projects.activeWorld.snapshots[0].payload.value = 2;
assert.equal((await projects.verifyWorldSnapshots()).valid, false);
await assert.rejects(() => projects.restoreWorldSnapshot(snapshot.id), /WORLD_SNAPSHOT_CHAIN_INVALID/);

console.log("STAGE_004_NEGATIVE_CONTRACT_PASSED");
console.log("entity_guards=4");
console.log("asset_guards=2");
console.log("route_guards=4");
console.log("simulation_batch_bounded=true");
console.log("snapshot_tamper_detected=true");
