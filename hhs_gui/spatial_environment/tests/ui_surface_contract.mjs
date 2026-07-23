import assert from "node:assert/strict";
import { UIShell } from "../src/ui-shell.js";
import { ProjectStore } from "../src/project-store.js";
import { EntitySceneGraph } from "../src/entity-scene-graph.js";
import { AssetRegistry } from "../src/asset-registry.js";
import { WorldRouter } from "../src/world-router.js";
import { SimulationEngine } from "../src/simulation-engine.js";

class MemoryStorage {
  constructor() { this.map = new Map(); }
  getItem(key) { return this.map.get(key) ?? null; }
  setItem(key, value) { this.map.set(key, String(value)); }
}

const shell = Object.create(UIShell.prototype);
shell.projects = new ProjectStore({ storage: new MemoryStorage() });
shell.scene = new EntitySceneGraph();
shell.assets = new AssetRegistry();
shell.routes = new WorldRouter();
shell.routes.syncWorlds(shell.projects.activeProject.worlds);
shell.simulation = new SimulationEngine({ scene: shell.scene });
shell.workspace = { surfaces: [{ id: "surface-1", title: "Test", width: 400, height: 300, dock: null }] };

shell.scene.createPrimitive("orb", { name: "Visible Orb" });
const projectHTML = shell.projectManagerSurface();
const composerHTML = shell.sceneComposerSurface();
const inspectorHTML = shell.entityInspectorSurface();
const assetHTML = shell.assetVaultSurface();
const routeHTML = shell.worldRouterSurface();
const simulationHTML = shell.simulationConsoleSurface();

assert.match(projectHTML, /Project|World Snapshot|Verify Chain/);
assert.match(composerHTML, /ENTITY SCENE GRAPH|Visible Orb/);
assert.match(inspectorHTML, /Apply Position|Add Motion/);
assert.match(assetHTML, /IMPORT LOCAL ASSETS|SHA-256/);
assert.match(routeHTML, /Current world|Connect First Pair/);
assert.match(simulationHTML, /NON_AUTHORITATIVE_PRESENTATION_SIMULATION|Fixed/);

console.log("UI_SURFACE_CONTRACT_PASSED");
console.log("stage004_surfaces=6");
