import assert from "node:assert/strict";
import { EntitySceneGraph } from "../src/entity-scene-graph.js";
import { AssetRegistry, classifyAsset } from "../src/asset-registry.js";
import { WorldRouter } from "../src/world-router.js";
import { SimulationEngine } from "../src/simulation-engine.js";
import { ProjectStore } from "../src/project-store.js";
import { APPLICATIONS } from "../src/application-registry.js";

class MemoryStorage {
  constructor() { this.map = new Map(); }
  getItem(key) { return this.map.get(key) ?? null; }
  setItem(key, value) { this.map.set(key, String(value)); }
  removeItem(key) { this.map.delete(key); }
}

assert.equal(APPLICATIONS.length, 22);
assert.equal(classifyAsset("ship.glb", ""), "MODEL");
assert.equal(classifyAsset("field.wgsl", "text/plain"), "SHADER_TEXT");

const scene = new EntitySceneGraph();
const orb = scene.createPrimitive("orb", { name: "Test Orb" });
const portal = scene.createPrimitive("portal", { parentId: orb.id });
assert.equal(scene.list().length, 3);
assert.equal(scene.get(portal.id).parentId, orb.id);
scene.setComponent(orb.id, "Kinematics", { velocity: [1, 0, 0], acceleration: [0, 0, 0], damping: 0 });
const beforeDigest = await scene.digest();
scene.translate(orb.id, [1, 2, 3]);
const afterDigest = await scene.digest();
assert.notEqual(beforeDigest, afterDigest);
assert.deepEqual(scene.get(orb.id).components.Transform.position, [1, 2, 3]);

const assets = new AssetRegistry({ maxAssetBytes: 1024 });
const asset = await assets.ingest({ name: "material.wgsl", type: "text/plain", bytes: new TextEncoder().encode("@fragment fn main() {}") });
assert.equal(asset.category, "SHADER_TEXT");
assert.equal(asset.executionPolicy, "INERT_TEXT_UNTIL_VALIDATED");
const duplicate = await assets.ingest({ name: "duplicate.wgsl", type: "text/plain", bytes: new TextEncoder().encode("@fragment fn main() {}") });
assert.equal(duplicate.duplicate, true);
assert.equal(assets.list().length, 1);
assets.bind(asset.id, orb.id);
assert.deepEqual(assets.get(asset.id).bindings, [orb.id]);

const router = new WorldRouter();
router.syncWorlds([{ id: "world-a", name: "A" }, { id: "world-b", name: "B" }, { id: "world-c", name: "C" }]);
router.addRoute({ from: "world-a", to: "world-b", label: "A/B" });
router.addRoute({ from: "world-b", to: "world-c", label: "B/C" });
assert.deepEqual(router.resolve("world-a", "world-c"), ["world-a", "world-b", "world-c"]);
assert.equal(router.navigate("world-c").to, "world-c");

const simulationScene = new EntitySceneGraph();
const mover = simulationScene.createPrimitive("orb");
simulationScene.setComponent(mover.id, "Kinematics", { velocity: [1, 0, 0], acceleration: [0, 0, 0], damping: 0 });
const simulation = new SimulationEngine({ scene: simulationScene, fixedDt: 0.5 });
simulation.step(2);
assert.equal(simulation.snapshot().tick, 2);
assert.deepEqual(simulationScene.get(mover.id).components.Transform.position, [1, 0, 0]);
assert.equal(simulation.snapshot().classification, "NON_AUTHORITATIVE_PRESENTATION_SIMULATION");

const projects = new ProjectStore({ storage: new MemoryStorage() });
assert.equal(projects.list().length, 1);
const createdProject = projects.create("Authoring Test");
assert.equal(projects.activeProjectId, createdProject.id);
const secondWorld = projects.addWorld("Second World");
assert.equal(projects.activeWorld.id, secondWorld.id);
projects.saveWorldState({ scene: scene.snapshot(), routes: router.snapshot().routes });
projects.saveAssets(assets.export());
const worldSnapshot = await projects.saveWorldSnapshot("Closure", { scene: scene.snapshot(), routes: router.snapshot() });
assert.equal((await projects.verifyWorldSnapshots()).valid, true);
assert.equal((await projects.restoreWorldSnapshot(worldSnapshot.id)).scene.schema, "HHS_ENTITY_SCENE_GRAPH_V4");
const exported = projects.export();
const imported = new ProjectStore({ storage: new MemoryStorage() });
imported.import(exported, { merge: false });
assert.equal(imported.list().length, 2);
assert.equal(imported.activeProject.manifest.runtimeAuthority, "VM81_BACKEND_AUTHORITATIVE");

console.log("STAGE_004_CONTRACT_PASSED");
console.log("applications=22");
console.log("scene_entities=3");
console.log("asset_digest_verified=true");
console.log("world_route_length=3");
console.log("simulation_ticks=2");
console.log("world_snapshot_chain=valid");
