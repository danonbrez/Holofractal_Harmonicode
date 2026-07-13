from hhs_runtime.hhs_constraint_stack_security_harness_v1 import (
    ACCEPTED_STATUS,
    RECLASSIFIED_STATUS,
    evaluate_constraint_stack_candidate,
    make_terminal_value_only_claim,
    run_constraint_stack_security_harness,
    constraint_stack_security_harness_self_test,
)
from hhs_runtime.hhs_reality_to_manifold_translation_v1 import translate_reality_to_manifold


def test_terminal_value_only_is_rejected_as_forgery():
    result = evaluate_constraint_stack_candidate(
        "terminal_value_only",
        make_terminal_value_only_claim(),
        expected_status="REJECTED_FORGED_TERMINAL_VALUE",
    )
    assert result["status"] == "REJECTED_FORGED_TERMINAL_VALUE"
    assert result["accepted"] is False
    assert result["terminal_value_sufficient"] is False
    assert result["execution_performed"] is False
    assert result["failure_record"]["reason_code"] == "FORGED_TERMINAL_VALUE"


def test_complete_witness_chain_is_admissible():
    canonical = translate_reality_to_manifold(accept=True)
    result = evaluate_constraint_stack_candidate(
        "canonical_full_witness_chain",
        canonical,
        expected_status=ACCEPTED_STATUS,
    )
    assert result["status"] == ACCEPTED_STATUS
    assert result["accepted"] is True
    assert result["witness_chain_complete"] is True
    assert result["expected_match"] is True


def test_missing_ledger_receipt_is_rejected():
    canonical = translate_reality_to_manifold(accept=True)
    canonical.pop("ledger", None)
    result = evaluate_constraint_stack_candidate(
        "missing_ledger_receipt",
        canonical,
        expected_status="REJECTED_LEDGERLESS_MUTATION",
    )
    assert result["status"] == "REJECTED_LEDGERLESS_MUTATION"
    assert "ledger_receipt" in result["missing_layers"]
    assert result["execution_performed"] is False


def test_full_rule_following_bruteforce_is_reclassified_not_bypass():
    canonical = translate_reality_to_manifold(accept=True)
    result = evaluate_constraint_stack_candidate(
        "full_rule_following_bruteforce_sequence",
        canonical,
        expected_status=RECLASSIFIED_STATUS,
        brute_force_claim=True,
    )
    assert result["status"] == RECLASSIFIED_STATUS
    assert result["accepted"] is True
    assert result["reclassified_as_valid_propagation"] is True
    assert result["reason_code"] == "RULE_FOLLOWING_EQUIVALENCE"


def test_security_harness_runs_all_invariant_scenarios():
    manifest = run_constraint_stack_security_harness()
    summary = manifest["summary"]
    assert summary["scenario_count"] == 9
    assert summary["rejected_count"] == 7
    assert summary["accepted_or_reclassified_count"] == 2
    assert summary["all_expected_statuses_matched"] is True
    assert summary["rejected_scenarios_executed"] is False
    assert summary["full_rule_following_bruteforce_reclassified"] is True


def test_constraint_stack_security_harness_self_test_generates_artifacts():
    result = constraint_stack_security_harness_self_test()
    assert result["ok"] is True
    assert result["service"] == "constraint_stack_security_harness.self_test"
    assert result["summary"]["terminal_value_sufficient"] is False
