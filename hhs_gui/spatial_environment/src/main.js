import { SpatialRenderer } from "./spatial-renderer.js";
import { RuntimeBridge } from "./runtime-bridge.js";
import { UIShell } from "./ui-shell.js";
import { SpatialWorldModel } from "./world-model.js";
import { ProjectionJournal } from "./projection-journal.js";
import { SessionStore } from "./session-store.js";
import { SpatialWorkspaceManager } from "./spatial-workspace-manager.js";
import { ReplayController } from "./replay-controller.js";
import { TelemetryStore } from "./telemetry-store.js";
import { CommandRouter } from "./command-router.js";
import { ProjectStore } from "./project-store.js";
import { EntitySceneGraph } from "./entity-scene-graph.js";
import { AssetRegistry } from "./asset-registry.js";
import { WorldRouter } from "./world-router.js";
import { SimulationEngine } from "./simulation-engine.js";

const smokeMode = new URLSearchParams(location.search).has("smoke");
const canvas = document.getElementById("spatial-canvas");
let renderer;

try {
  renderer = new SpatialRenderer(canvas);
  renderer.start();
} catch (error) {
  document.getElementById("renderer-status").className = "status-chip offline";
  document.getElementById("renderer-status").innerHTML = "<i></i> RENDERER UNAVAILABLE";
  document.getElementById("event-log").innerHTML = `<li class="error"><strong>RENDERER FAILURE</strong>${String(error.message || error)}</li>`;
  throw error;
}

const bridge = globalThis.HHS_RUNTIME_BRIDGE ?? new RuntimeBridge();
const world = new SpatialWorldModel();
const journal = new ProjectionJournal();
const sessions = new SessionStore();
const workspace = new SpatialWorkspaceManager();
const replay = new ReplayController();
const telemetry = new TelemetryStore();
const commands = new CommandRouter({ bridge, journal, telemetry });
const projects = new ProjectStore();
const scene = new EntitySceneGraph();
const assets = new AssetRegistry();
const routes = new WorldRouter();
const simulation = new SimulationEngine({ scene });

const ui = new UIShell({
  renderer,
  bridge,
  world,
  journal,
  sessions,
  workspace,
  replay,
  telemetry,
  commands,
  projects,
  scene,
  assets,
  routes,
  simulation
});

if (!smokeMode) {
  bridge.connectAll();
} else {
  setTimeout(() => {
    renderer.stop();
    simulation.pause();
    bridge.disconnectAll();
    document.documentElement.dataset.smoke = "ready";
  }, 900);
}

window.addEventListener("beforeunload", () => {
  bridge.disconnectAll?.();
  replay.pause();
  simulation.pause();
  renderer.stop();
});

window.HHS_SPATIAL_ENVIRONMENT = Object.freeze({
  stage: "004",
  classification: "PROJECT_SCENE_AUTHORING_AND_APPLICATION_RUNTIME",
  authority: "PROJECTION_AND_ORCHESTRATION_ONLY",
  renderer,
  bridge,
  world,
  journal,
  sessions,
  workspace,
  replay,
  telemetry,
  commands,
  projects,
  scene,
  assets,
  routes,
  simulation,
  ui
});
