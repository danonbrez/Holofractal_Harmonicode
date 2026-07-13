import pytest

from hhs_runtime.hhs_zero_bypass_runtime_interposer_v1 import (
    ADMITTED_STATUS,
    MISSING_INTERPOSITION_STATUS,
    RECLASSIFIED_INTERPOSITION_STATUS,
    SURFACE_MISMATCH_STATUS,
    guarded_surface_propagation,
    interpose_runtime_surface,
    make_runtime_surface_interposition_map,
    verify_interposition_token,
    zero_bypass_runtime_interposer_self_test,
)


@pytest.fixture(scope="module")
def self_test_result():
    return zero_bypass_runtime_interposer_self_test()


def test_surface_map_declares_all_propagation_surfaces():
    surface_map = make_runtime_surface_interposition_map()
    surfaces = surface_map["propagation_surfaces"]
    assert surface_map["schema"] == "HHS_RUNTIME_SURFACE_INTERPOSITION_MAP_V1"
    assert len(surfaces) == 10
    assert "service_registry.dispatch" in surfaces
    assert "websocket.broadcast" in surfaces
    assert "persistence.write" in surfaces


def test_uninterposed_surface_rejected_without_execution():
    result = guarded_surface_propagation(
        surface="service_registry.dispatch",
        attempted_operation="direct_dispatch_without_interposer",
        payload={"schema": "HHS_DIRECT_BYPASS_TEST_V1"},
    )
    assert result["status"] == MISSING_INTERPOSITION_STATUS
    assert result["propagation_allowed"] is False
    assert result["execution_allowed"] is False
    assert result["mutation_allowed"] is False
    assert result["bypass_attempt"] is True


def test_terminal_value_interposition_is_rejected():
    result = interpose_runtime_surface(
        surface="service_registry.dispatch",
        request_class="terminal_value_only",
        payload={"schema": "HHS_TERMINAL_VALUE_ONLY_CLAIM_V1", "terminal_value": "179971.179971"},
    )
    assert result["propagation_allowed"] is False
    assert result["status"] == "REJECTED_FORGED_TERMINAL_VALUE"
    assert result["interposition_token"] == {}


def test_canonical_interposition_token_allows_matching_surface():
    interposition = interpose_runtime_surface(
        surface="service_registry.dispatch",
        request_class="canonical_full_witness_chain",
        payload={"schema": "HHS_CANONICAL_INTERPOSITION_TEST_V1"},
    )
    assert interposition["status"] == ADMITTED_STATUS
    token = interposition["interposition_token"]
    assert verify_interposition_token(token, surface="service_registry.dispatch")["ok"] is True
    propagation = guarded_surface_propagation(
        surface="service_registry.dispatch",
        attempted_operation="guarded_dispatch",
        payload={"schema": "HHS_GUARDED_DISPATCH_TEST_V1"},
        interposition_token=token,
    )
    assert propagation["propagation_allowed"] is True
    assert propagation["status"] == "PROPAGATION_ALLOWED_BY_ZERO_BYPASS_INTERPOSER"


def test_interposition_token_is_surface_scoped():
    interposition = interpose_runtime_surface(
        surface="service_registry.dispatch",
        request_class="canonical_full_witness_chain",
    )
    wrong_surface = guarded_surface_propagation(
        surface="websocket.broadcast",
        attempted_operation="wrong_surface_token_attempt",
        interposition_token=interposition["interposition_token"],
    )
    assert wrong_surface["status"] == SURFACE_MISMATCH_STATUS
    assert wrong_surface["propagation_allowed"] is False


def test_rule_following_bruteforce_is_reclassified_and_allowed():
    interposition = interpose_runtime_surface(
        surface="plugin_adapter.invocation",
        request_class="full_rule_following_bruteforce_sequence",
        brute_force_claim=True,
    )
    assert interposition["status"] == RECLASSIFIED_INTERPOSITION_STATUS
    assert interposition["propagation_allowed"] is True
    propagation = guarded_surface_propagation(
        surface="plugin_adapter.invocation",
        attempted_operation="guarded_plugin_invocation",
        interposition_token=interposition["interposition_token"],
    )
    assert propagation["propagation_allowed"] is True


def test_zero_bypass_self_test_summary(self_test_result):
    assert self_test_result["ok"] is True
    summary = self_test_result["summary"]
    assert summary["surface_count"] == 10
    assert summary["scenario_count"] == 12
    assert summary["direct_bypass_rejections"] == 6
    assert summary["allowed_count"] == 4
    assert summary["rejected_count"] == 8
    assert summary["wrong_surface_token_rejected"] is True
    assert summary["any_uninterposed_propagation_allowed"] is False
