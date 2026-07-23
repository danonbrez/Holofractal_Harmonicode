import pytest

from hhs_runtime.hhs_pass109_gamified_whole_system_pathfinding_v1 import (
    PathfindingError,
    WholeSystemPathGame,
    pass109_self_test,
)


@pytest.fixture(scope="module")
def result():
    return pass109_self_test()


def test_pass109_exercises_complete_current_admitted_graph(result):
    assert result["status"] == "PASS"
    assert result["capability_graph"]["admitted_capability_count"] == 3
    assert result["all_admitted_capabilities_exercised"] is True
    assert all(x["behavioral_coverage_ratio"] == "3/3" for x in result["campaigns"])


def test_pass109_executes_real_serial_and_parallel_paths(result):
    assert result["parallel_and_serial_paths_executed"] is True
    assert all(x["real_backend_execution"] for x in result["campaigns"])
    assert all(x["real_negative_attack_execution"] for x in result["campaigns"])
    assert all(x["real_ordered_composition_execution"] for x in result["campaigns"])


def test_pass109_preserves_one_seed_and_coherence(result):
    assert result["one_canonical_seed_preserved"] is True
    assert result["cross_domain_branch_reconciliation_preserved"] is True
    assert result["unresolved_drift_count"] == 0
    assert all(x["coherence_status"] == "PRESERVED" for x in result["campaigns"])


def test_pass109_selects_safe_genesis_configuration(result):
    config = result["genesis_selection"]
    assert result["safe_genesis_configuration_selected"] is True
    assert config["all_profiles_coherence_equal"] is True
    assert config["universal_optimum_claimed"] is False
    assert config["selected_profile_id"] in {"BALANCED_DEFAULT", "PARALLEL_THROUGHPUT"}
    assert config["immutable_invariants"]["zero_bypass_required"] is True
    assert config["immutable_invariants"]["mocks_prohibited"] is True


def test_pass109_rejects_incompatible_projection():
    game = WholeSystemPathGame()
    graph = {"capability_graph_root_hash72": "g"}
    seed = game.create_seed(graph)
    with pytest.raises(PathfindingError) as exc:
        game.project_seed(seed, "UNSUPPORTED_MODALITY")
    assert exc.value.code == "REJECT_INCOMPATIBLE_FUNCTION_PROJECTION"


def test_pass109_has_no_mock_or_parallel_test_logic(result):
    assert result["mock_components"] == []
    assert result["parallel_test_computation_used"] is False
    assert result["score_has_authority"] is False


def test_pass109_service_registered_and_derived():
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
    registry = make_default_service_registry()
    service = next(x for x in registry.services() if x["name"] == "runtime.gamified_whole_system_pathfinding.pass109")
    assert service["conformance_decision"]["derivation_complete"] is True
    assert "zero_bypass_runtime_interposer" in service["guards"]
    assert "score_has_no_authority" in service["guards"]
