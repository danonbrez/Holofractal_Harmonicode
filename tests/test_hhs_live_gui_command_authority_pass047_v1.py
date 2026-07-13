from __future__ import annotations

from pathlib import Path

from hhs_backend.runtime.live_gui_command_contract_v1 import (
    COMMAND_SCHEMA,
    GUI_COMMAND_ADMITTED_RECEIPT_ONLY,
    REJECT_GUI_DIRECT_MUTATION,
    build_gui_command_contract,
    live_gui_command_contract_self_test,
    normalize_gui_command,
    validate_gui_command_envelope,
)
from hhs_backend.runtime.live_gui_command_router_v1 import live_gui_command_router_self_test, list_live_gui_command_routes
from hhs_backend.runtime.live_gui_command_authority_loop_v1 import run_live_gui_command_authority_self_test
from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_composed_preflight
from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


ROOT = Path(__file__).resolve().parents[1]


def test_gui_command_contract_self_test_passes():
    result = live_gui_command_contract_self_test()
    assert result["ok"] is True
    assert result["command"]["schema"] == COMMAND_SCHEMA
    assert result["contract"]["browser_authority"] == "REQUEST_ONLY_NO_DIRECT_MUTATION"


def test_gui_direct_mutation_is_rejected_before_runtime_authority():
    decision = validate_gui_command_envelope({
        "requested_operation": "direct.mutate_runtime_truth",
        "target_surface": "browser.local_runtime_state",
        "contract_schema": "HHS_FORBIDDEN_GUI_DIRECT_MUTATION_V1",
        "payload": {"mutate_runtime_truth_directly": True},
    })
    assert decision["ok"] is False
    assert REJECT_GUI_DIRECT_MUTATION in decision["reasons"]


def test_gui_command_routes_are_declared():
    result = live_gui_command_router_self_test()
    assert result["ok"] is True
    routes = list_live_gui_command_routes()["routes"]
    paths = {route["path"] for route in routes}
    assert "/api/runtime/gui/command" in paths
    assert "/api/runtime/gui/command/status/{command_id}" in paths
    assert "/api/runtime/gui/command/history" in paths


def test_runtime_tick_command_surface_is_kernel_composable():
    command = normalize_gui_command({"requested_operation": "runtime.tick", "client_sequence_id": 1})
    plan = execute_composed_preflight(command["target_surface"], operation=command["requested_operation"])
    assert plan["ok"] is True
    assert plan["composition_plan"]["composition_allowed"] is True
    assert plan["expanded_metadata_persisted"] is False


def test_gui_command_authority_self_test_entrypoint_is_available():
    # The full authority-loop self-test is exercised by the make target as a
    # standalone module to avoid pytest plugin shutdown delays in this packaged
    # environment.  The pytest suite verifies the callable entrypoint and the
    # underlying contract/composition boundaries.
    assert callable(run_live_gui_command_authority_self_test)
    command = normalize_gui_command({"requested_operation": "runtime.tick", "client_sequence_id": 9})
    contract = build_gui_command_contract(command)
    assert contract["required_path"][-2:] == ["websocket_feedback", "gui_projection_update"]
    assert contract["browser_authority"] == "REQUEST_ONLY_NO_DIRECT_MUTATION"


def test_conformance_map_declares_gui_command_api_routes():
    surface_map = build_surface_map()
    surface_ids = {surface["surface_id"] for surface in surface_map["surfaces"]}
    assert "api_route:POST /api/runtime/gui/command" in surface_ids
    assert "api_route:GET /api/runtime/gui/command/status/{command_id}" in surface_ids
    assert "api_route:GET /api/runtime/gui/command/history" in surface_ids
    assert len(surface_map.get("underived_surfaces", [])) == 0


def test_service_registry_exposes_pass047_services():
    registry = make_default_service_registry()
    names = {service["name"] for service in registry.services()}
    assert "live_gui_command_contract.self_test" in names
    assert "live_gui_command_router.self_test" in names
    assert "live_gui_command_authority_loop.self_test" in names


def test_gui_source_mounts_command_panel_and_request_only_client():
    shell = (ROOT / "hhs_gui/runtime_os/core/RuntimeShell.tsx").read_text()
    client = (ROOT / "hhs_gui/runtime_os/core/RuntimeCommandClient.ts").read_text()
    panel = (ROOT / "hhs_gui/runtime_os/core/RuntimeCommandPanel.tsx").read_text()
    assert "RuntimeCommandPanel" in shell
    assert "/api/runtime/gui/command" in client
    assert "HHS_LIVE_GUI_COMMAND_ENVELOPE_V1" in client
    assert "GUI may request; kernel decides" in panel
    assert "runtime-command-panel" in panel
