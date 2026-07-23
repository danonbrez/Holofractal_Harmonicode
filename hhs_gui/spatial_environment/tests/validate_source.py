#!/usr/bin/env python3
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "index.html", "styles.css", "src/main.js", "src/spatial-renderer.js", "src/runtime-bridge.js",
    "src/ui-shell.js", "src/world-model.js", "src/projection-journal.js", "src/theme-registry.js",
    "src/template-registry.js", "src/feature-registry.js", "src/application-registry.js",
    "src/session-store.js", "src/spatial-workspace-manager.js", "src/replay-controller.js",
    "src/telemetry-store.js", "src/command-router.js", "src/project-store.js",
    "src/entity-scene-graph.js", "src/asset-registry.js", "src/world-router.js",
    "src/simulation-engine.js", "integration/SpatialEnvironmentPanel.tsx",
    "README.md", "INTEGRATION_CONTRACT.md", "STAGE_004_CHANGELOG.md",
    "tests/run_all.sh", "IMPLEMENTATION_MANIFEST.json"
]
errors: list[str] = []
for rel in REQUIRED:
    path = ROOT / rel
    if not path.is_file() or path.stat().st_size == 0:
        errors.append(f"missing_or_empty:{rel}")

html = (ROOT / "index.html").read_text()
for target in [
    "spatial-canvas", "runtime-status", "theme-grid", "template-select", "dock", "command-palette",
    "cell-inspector", "mode-switcher", "workspace-file-input", "surface-layer", "application-library",
    "session-select", "replay-range", "telemetry-summary", "journal-integrity"
]:
    if f'id="{target}"' not in html:
        errors.append(f"missing_html_target:{target}")

bridge = (ROOT / "src/runtime-bridge.js").read_text()
for route in [
    "/api/runtime/state", "/api/runtime/step", "/api/runtime/receipt/commit", "/api/runtime/halt",
    "/api/runtime/manifold/execution/propagate", "/api/runtime/manifold/execution/revalidate",
    "/api/runtime/authority/topology/reciprocal/status", "/api/runtime/services/status",
    "/api/runtime/pass152/status", "/api/runtime/pass152/capabilities",
    "/api/runtime/pass152/latest", "/api/runtime/pass152/execute"
]:
    if route not in bridge:
        errors.append(f"missing_runtime_route:{route}")
for channel in ["/ws/runtime", "/ws/replay", "/ws/graph", "/ws/transport"]:
    if channel not in bridge:
        errors.append(f"missing_websocket_channel:{channel}")

renderer = (ROOT / "src/spatial-renderer.js").read_text()
for token in ["const particles=8100,anchors=81", "canvas2d", "cell-select", "focusCell", "snapshotCamera", "setReplayPhase"]:
    if token not in renderer:
        errors.append(f"renderer_invariant_missing:{token}")
for value in ["41", "42"]:
    if value not in renderer:
        errors.append(f"projection_constant_missing:{value}")

applications = (ROOT / "src/application-registry.js").read_text()
if applications.count('id: "') < 22:
    errors.append("application_registry_incomplete")

checks = {
    "src/project-store.js": ["HHS_SPATIAL_PROJECT_STORE_V4", "VM81_BACKEND_AUTHORITATIVE", "saveWorldSnapshot", "verifyWorldSnapshots"],
    "src/entity-scene-graph.js": ["HHS_ENTITY_SCENE_GRAPH_V4", "MAX_ENTITIES", "SCENE_GRAPH_CYCLE", "async digest"],
    "src/asset-registry.js": ["HHS_SPATIAL_ASSET_MANIFEST_V4", "SHA-256", "INERT_TEXT_UNTIL_VALIDATED", "MAX_ASSET_BYTES"],
    "src/world-router.js": ["HHS_SPATIAL_WORLD_ROUTER_V4", "PRESENTATION_NAVIGATION_ONLY", "resolve(from, to)", "DANGLING_WORLD_ROUTE"],
    "src/simulation-engine.js": ["NON_AUTHORITATIVE_PRESENTATION_SIMULATION", "fixedDt", "maximumBatchSteps", "integrate()"]
}
for rel, tokens in checks.items():
    text = (ROOT / rel).read_text()
    for token in tokens:
        if token not in text:
            errors.append(f"stage004_contract_missing:{rel}:{token}")

ui = (ROOT / "src/ui-shell.js").read_text()
for token in ["projectManagerSurface", "entityInspectorSurface", "assetVaultSurface", "worldRouterSurface", "simulationConsoleSurface", "captureProjectState", "elasticClosureSurface", "pass152Execute"]:
    if token not in ui:
        errors.append(f"ui_integration_missing:{token}")

manifest = json.loads((ROOT / "IMPLEMENTATION_MANIFEST.json").read_text())
if manifest.get("stage") not in {"004", "PASS_152"}: errors.append("wrong_stage")
if manifest.get("authority", {}).get("frontend") != "PROJECTION_AND_ORCHESTRATION_ONLY": errors.append("authority_boundary_changed")
if manifest.get("authority", {}).get("runtime") != "VM81_BACKEND_AUTHORITATIVE": errors.append("runtime_authority_changed")
if manifest.get("rendering", {}).get("fallback") != "Canvas2D": errors.append("fallback_missing")
if manifest.get("applications") != 22: errors.append("application_count_mismatch")
if manifest.get("scene_graph", {}).get("maximum_entities") != 2048: errors.append("entity_limit_mismatch")
if manifest.get("asset_registry", {}).get("maximum_asset_bytes") != 67108864: errors.append("asset_limit_mismatch")

error_block = re.search(r"catch \(error\).*?RUNTIME_UNAVAILABLE", bridge, flags=re.S)
if not error_block:
    errors.append("runtime_unavailable_classification_missing")

if errors:
    print("SOURCE_VALIDATION_FAILED")
    for error in errors:
        print(error)
    sys.exit(1)

print("SOURCE_VALIDATION_PASSED")
print(f"required_files={len(REQUIRED)}")
print("runtime_routes=12")
print("websocket_channels=4")
print("projection_nodes=8181")
print("applications=22")
print("project_store=v4")
print("scene_graph=v4")
print("asset_registry=v4")
print("world_router=v4")
print("simulation_engine=v4")
