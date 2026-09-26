from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass220_lane5_global_tool_hydration_v1 import (
    CPP_SURFACE_SYMBOL,
    CPP_SURFACE_VERSION,
    GLOBAL_CONSTRAINTS,
    build_pass219_220_warm_tool_graph,
    cpp_manifest_lines,
    discover_merged_pass219_220_pull_requests,
    discover_registered_pass219_220_services,
    public_tool_graph,
    warm_pass219_220_tool_vector_store,
)
from hhs_backend.runtime_os_pass220_lane5_tool_hydration import (
    PASS220_LANE5_TOOL_GRAPH_PATH,
    PASS220_LANE5_TOOL_STATUS_PATH,
    Pass220Lane5ToolWarmLifecycle,
)

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def graph() -> dict:
    return build_pass219_220_warm_tool_graph(ROOT)


def test_inventory_contains_registered_services_and_authoritative_merged_prs() -> None:
    services = discover_registered_pass219_220_services(ROOT)
    prs = discover_merged_pass219_220_pull_requests(ROOT)
    assert services
    assert prs
    assert any(219 in item["pass_scopes"] for item in services)
    assert any(220 in item["pass_scopes"] for item in services)
    assert any(219 in item["pass_scopes"] for item in prs)
    assert any(220 in item["pass_scopes"] for item in prs)
    assert len({item["name"] for item in services}) == len(services)
    assert len({item["pr_number"] for item in prs}) == len(prs)


def test_every_tool_is_exact_5184_hash216_cpp_bound_and_candidate_only(graph: dict) -> None:
    public = public_tool_graph(graph)
    assert public["projection_bits"] == 5184
    assert public["parent_multimodal_graph_schema"] == (
        "HHS_PASS_220_I042_MULTIMODAL_KNOWLEDGE_GRAPH_V1"
    )
    assert public["tool_count"] == (
        public["registered_service_count"] + public["merged_pull_request_count"]
    )
    assert all(public["coverage"].values())
    assert public["authority"] == {
        "lane5_route_selection_changed": False,
        "vector_store_is_source_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
    }

    for node in public["nodes"]:
        assert len(node["hash216"]) == 216
        assert len(node["previous_hash72"]) == 72
        assert len(node["current_hash72"]) == 72
        assert len(node["receipt_hash72"]) == 72
        assert node["hash216"] == (
            node["previous_hash72"] + node["current_hash72"] + node["receipt_hash72"]
        )
        assert node["projection_bits"] == 5184
        assert node["projection_bytes"] == 648
        assert len(node["projection_sha256"]) == 64
        assert node["i042_shared_root_sha256"] == public["i042_shared_root_sha256"]
        assert node["cpp_surface_symbol"] == CPP_SURFACE_SYMBOL
        assert node["cpp_surface_version"] == CPP_SURFACE_VERSION
        assert node["candidate_only"] is True
        assert node["lane5_selection_unchanged"] is True
        assert node["canonical_vm81_mutation_authority"] is False
        assert node["canonical_hash72_authority"] is False
        assert node["canonical_hash216_authority"] is False
        assert node["canonical_persistence_authority"] is False
        assert node["floating_point_canonical_authority"] is False


def test_cpp_manifest_covers_every_tool_once(graph: dict) -> None:
    public = public_tool_graph(graph)
    lines = cpp_manifest_lines(graph)
    assert len(lines) == public["tool_count"]
    assert len(set(lines)) == len(lines)
    for line in lines:
        fields = line.split("|")
        assert len(fields) == 6
        assert len(fields[0]) == 64
        assert fields[1] in {"1", "2"}
        assert fields[2] in {"0", "1"}
        assert fields[3] in {"0", "1"}
        assert fields[2] == "1" or fields[3] == "1"
        assert len(fields[4]) == 216
        assert len(fields[5]) == 64


def test_warm_vector_store_is_complete_and_restart_reuses_every_tool(
    tmp_path: Path,
) -> None:
    key = bytes(range(32))
    first = warm_pass219_220_tool_vector_store(
        ROOT,
        tmp_path,
        vector_key=key,
    )
    assert first["all_tools_warmed"] is True
    assert first["newly_admitted_count"] == first["warmed_tool_count"]
    assert first["reused_count"] == 0
    assert first["lane5_selection_changed"] is False
    assert first["canonical_vm81_mutation_authority"] is False
    assert first["canonical_hash72_authority"] is False
    assert first["canonical_hash216_authority"] is False
    assert first["canonical_persistence_authority"] is False

    second = warm_pass219_220_tool_vector_store(
        ROOT,
        tmp_path,
        vector_key=key,
    )
    assert second["all_tools_warmed"] is True
    assert second["newly_admitted_count"] == 0
    assert second["reused_count"] == second["warmed_tool_count"]
    assert second["graph"]["graph_root_sha256"] == first["graph"]["graph_root_sha256"]
    assert second["vector_store"]["objects"] == second["warmed_tool_count"]


def test_global_constraint_explicitly_preserves_lane5_selection() -> None:
    assert "LANE5_ROUTE_SELECTION_ALGORITHM_UNCHANGED" in GLOBAL_CONSTRAINTS
    assert (
        "CIRCULAR_PHASE_FIBER_IS_GLOBAL_CONSTRAINT_NOT_SELECTOR_REPLACEMENT"
        in GLOBAL_CONSTRAINTS
    )
    source = inspect.getsource(
        __import__(
            "hhs_runtime.hhs_pass220_lane5_global_tool_hydration_v1",
            fromlist=["*"],
        )
    )
    assert "hhs_exact_pass219_lane5_direct_witness_route_optimize" not in source
    assert "hhs_exact_pass219_lane5_unbounded" not in source


def test_service_registry_and_runtime_os_startup_are_wired() -> None:
    registry_source = (ROOT / "hhs_runtime/hhs_service_registry_v1.py").read_text("utf-8")
    assert "pass220.lane5_global_tool_hydration.self_test" in registry_source
    assert "hhs_pass220_lane5_global_tool_hydration_v1" in registry_source

    for relative in (
        "hhs_backend/runtime_os_visual_server.py",
        "hhs_backend/runtime_os_application_server_full.py",
    ):
        source = (ROOT / relative).read_text("utf-8")
        assert "install_pass220_lane5_tool_warm_hydration" in source
        assert "PASS220_LANE5_TOOL_WARM_LIFECYCLE" in source

    assert PASS220_LANE5_TOOL_STATUS_PATH.endswith("/warm-status")
    assert PASS220_LANE5_TOOL_GRAPH_PATH.endswith("/graph")


def test_warm_lifecycle_failure_is_non_authoritative_and_fail_closed(tmp_path: Path) -> None:
    lifecycle = Pass220Lane5ToolWarmLifecycle(
        repository_root=tmp_path / "missing-repository",
        state_root=tmp_path / "state",
    )
    status = lifecycle.startup()
    assert status["state"] == "FAIL_CLOSED_UNAVAILABLE"
    assert status["available_to_lane5"] is False
    assert status["lane5_selection_changed"] is False
    assert status["candidate_only"] is True
    with pytest.raises(RuntimeError, match="GRAPH_NOT_WARM"):
        lifecycle.graph()
