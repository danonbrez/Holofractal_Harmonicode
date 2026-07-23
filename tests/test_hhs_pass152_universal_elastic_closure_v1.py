from __future__ import annotations

from pathlib import Path

from hhs_backend.api.pass152_elastic_closure_routes import (
    Pass152ExecuteRequest,
    pass152_capabilities,
    pass152_execute,
    pass152_latest,
    pass152_status,
)
from hhs_backend.server import app
from hhs_runtime.pass152 import DeterministicVM81TestAuthority, delayed_closure_workload


def test_pass152_delayed_closure_and_recursive_control(tmp_path: Path) -> None:
    result = delayed_closure_workload(
        tmp_path / "receipts",
        DeterministicVM81TestAuthority().admit,
        delay_seconds=0.001,
        workers=4,
    )
    assert result["proof"]["omega_closure"] is True
    assert result["proof"]["recursive_control"]["history_valid"] is True
    assert result["commit"]["history_extended_not_rewritten"] is True
    assert result["replay"]["replay_status"] == "MATCH"
    assert result["metrics"]["max_concurrent_workers_observed"] >= 2


def test_pass152_status_and_capability_surfaces() -> None:
    status = pass152_status()
    capabilities = pass152_capabilities()
    assert status["status"] == "IMPLEMENTED_EXECUTION_VERIFIED"
    assert status["authority"]["semantic_commit"] == "VM81"
    assert "branch_priority" in capabilities["admissible_control_vectors"]
    assert "committed_state" in capabilities["prohibited_control_mutations"]


def test_pass152_guarded_api_execution() -> None:
    response = pass152_execute(Pass152ExecuteRequest(delay_ms=0, workers=2))
    assert response["classification"] == "HHS_PASS_152_UNIVERSAL_ELASTIC_CLOSURE_INVARIANT_VERIFIED"
    assert response["commit"]["vm81_admitted"] is True
    assert response["commit"]["hash72_receipt"]
    assert response["replay"]["replay_status"] == "MATCH"
    assert pass152_latest()["available"] is True


def test_pass152_routes_are_reachable_from_canonical_server() -> None:
    paths = {route.path for route in app.routes}
    assert "/api/runtime/pass152/status" in paths
    assert "/api/runtime/pass152/capabilities" in paths
    assert "/api/runtime/pass152/latest" in paths
    assert "/api/runtime/pass152/execute" in paths


def test_spatial_environment_exposes_pass152_surface() -> None:
    root = Path(__file__).resolve().parents[1]
    registry = (root / "hhs_gui/spatial_environment/src/application-registry.js").read_text(encoding="utf-8")
    bridge = (root / "hhs_gui/spatial_environment/src/runtime-bridge.js").read_text(encoding="utf-8")
    shell = (root / "hhs_gui/spatial_environment/src/ui-shell.js").read_text(encoding="utf-8")
    assert 'id: "elastic-closure"' in registry
    assert 'pass152Execute' in bridge
    assert 'elasticClosureSurface()' in shell
    assert 'higher layers optimize policy, never lower-layer truth' in shell.lower()
