import pytest

from hhs_runtime.hhs_runtime_constraint_enforcement_binding_v1 import (
    ACCEPTED_STATUS,
    RECLASSIFIED_STATUS,
    make_runtime_enforcement_surface_map,
    runtime_constraint_enforcement_self_test,
)


@pytest.fixture(scope="module")
def self_test_result():
    return runtime_constraint_enforcement_self_test()


def test_surface_map_declares_runtime_boundaries():
    surface_map = make_runtime_enforcement_surface_map()
    assert surface_map["schema"] == "HHS_RUNTIME_ENFORCEMENT_SURFACE_MAP_V1"
    assert "api.runtime.services.dispatch.preflight" in surface_map["bound_surfaces"]
    assert surface_map["policy"]["terminal_output_sufficient"] is False


def test_runtime_constraint_enforcement_runs_all_scenarios(self_test_result):
    summary = self_test_result["summary"]
    assert self_test_result["ok"] is True
    assert summary["decision_count"] == 9
    assert summary["admitted_count"] == 2
    assert summary["rejected_count"] == 7
    assert summary["rejected_executions_allowed"] is False
    assert summary["terminal_value_sufficient"] is False
    assert summary["full_rule_following_bruteforce_reclassified"] is True


def test_canonical_terminal_and_rule_following_statuses(self_test_result):
    statuses = self_test_result["statuses"]
    assert statuses["canonical_full_witness_chain"] == ACCEPTED_STATUS
    assert statuses["terminal_value_only"] == "REJECTED_FORGED_TERMINAL_VALUE"
    assert statuses["full_rule_following_bruteforce_sequence"] == RECLASSIFIED_STATUS
    assert statuses["missing_ledger_receipt"] == "REJECTED_LEDGERLESS_MUTATION"
