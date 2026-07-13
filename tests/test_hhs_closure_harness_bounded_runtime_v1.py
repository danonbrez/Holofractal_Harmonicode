from hhs_runtime.hhs_closure_harness_bounded_runtime_v1 import (
    ADMIT_BOUNDED_CLOSURE_RUNTIME,
    ADMIT_BOUNDED_LEDGER_SUMMARY,
    REJECT_CLOSURE_HARNESS_DETAILS_EXPANSION,
    REJECT_CLOSURE_HARNESS_UNBOUNDED_CYCLES,
    REJECT_CLOSURE_HARNESS_UNBOUNDED_STEPS,
    bounded_verify_unified_ledger,
    closure_harness_bounded_runtime_self_test,
    validate_closure_harness_budget,
)


def _assert_hash72(value):
    assert isinstance(value, str)
    assert len(value) == 72


def test_closure_harness_budget_admits_bounded_run():
    result = validate_closure_harness_budget(cycles=2, max_steps=2)
    assert result["ok"] is True
    assert result["status"] == ADMIT_BOUNDED_CLOSURE_RUNTIME
    _assert_hash72(result["budget_root_hash72"])
    assert result["include_details"] is False


def test_closure_harness_budget_rejects_unbounded_expansion():
    assert validate_closure_harness_budget(cycles=4, max_steps=2)["status"] == REJECT_CLOSURE_HARNESS_UNBOUNDED_CYCLES
    assert validate_closure_harness_budget(cycles=1, max_steps=17)["status"] == REJECT_CLOSURE_HARNESS_UNBOUNDED_STEPS
    assert validate_closure_harness_budget(cycles=1, max_steps=1, include_details=True)["status"] == REJECT_CLOSURE_HARNESS_DETAILS_EXPANSION


def test_bounded_ledger_summary_is_hash72_witnessed():
    summary = bounded_verify_unified_ledger()
    assert summary["ok"] is True
    assert summary["status"] == ADMIT_BOUNDED_LEDGER_SUMMARY
    assert summary["verification_mode"] == "bounded_edge_summary_not_full_recompute"
    _assert_hash72(summary["summary_root_hash72"])


def test_closure_harness_bounded_runtime_self_test_passes():
    result = closure_harness_bounded_runtime_self_test()
    assert result["ok"] is True
    assert result["admitted_status"] == ADMIT_BOUNDED_CLOSURE_RUNTIME
    assert result["bounded_ledger_status"] == ADMIT_BOUNDED_LEDGER_SUMMARY
