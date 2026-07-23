from pathlib import Path
import pytest

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_bifurcation_calibration.hhs_pass091_collatz_prime_tensor_decay_entanglement_v1 import (
    TERMINAL_POLICY,
    default_workload,
    load_pass089_prime_sources,
    negative_cases,
    run,
    verify_replay,
    workload_registry,
)

R = Path(__file__).resolve().parents[1]


def test_pass089_prime_provenance_is_consumed():
    sources = load_pass089_prime_sources(R)
    assert [s["prime"] for s in sources[:11]] == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    assert len(sources) == 553
    assert all(s["prime_receipt_root_hash72"] for s in sources)


def test_preserves_declared_cycle_and_exact_integer_history():
    result = run(R, default_workload(R, workload_id="T91", prime_count=4))
    assert all(lane["terminal_policy"] == TERMINAL_POLICY for lane in result["lane_receipts"])
    assert all(lane["ordered_states"][-4:] == [4, 2, 1, 4] for lane in result["lane_receipts"])
    assert all(isinstance(value, int) for lane in result["lane_receipts"] for value in lane["ordered_states"])


def test_ordered_words_and_histories_are_identity_bearing():
    result = run(R, default_workload(R, workload_id="T91:history", prime_count=8))
    roots = [lane["ordered_history_root_hash72"] for lane in result["lane_receipts"]]
    assert len(roots) == len(set(roots))
    assert all(len(lane["operation_word"]) == lane["transition_count"] for lane in result["lane_receipts"])


def test_shared_suffix_preserves_distinct_prefixes():
    result = run(R, default_workload(R, workload_id="T91:merge", prime_count=11))
    assert result["entanglement_receipts"]
    assert all(edge["branch_identity_preserved"] for edge in result["entanglement_receipts"])
    assert all(not edge["merge_erases_ancestry"] for edge in result["entanglement_receipts"])
    assert all(edge["prefix_roots_distinct"] for edge in result["entanglement_receipts"])


def test_tensor_addresses_keep_prime_value_position_state_and_phase_distinct():
    result = run(R, default_workload(R, workload_id="T91:tensor", prime_count=11))
    cells = [lane["vm81_cell"] for lane in result["lane_receipts"]]
    lane_ids = [lane["lane_id"] for lane in result["lane_receipts"]]
    assert len(cells) == len(set(cells))
    assert len(lane_ids) == len(set(lane_ids))
    assert all(0 <= lane["u72_offset"] < 72 for lane in result["lane_receipts"])


def test_resource_bound_is_typed_not_theorem():
    result = run(R, default_workload(R, workload_id="T91:bounded", prime_count=4, max_steps=1))
    assert result["status"] == "RESOURCE_BOUNDED"
    assert result["theorem_claimed"] is False
    assert result["bounded_results_only"] is True


def test_full_graph_replay_is_exact():
    replay = verify_replay(R, default_workload(R, workload_id="T91:replay", prime_count=11))
    assert replay["deterministic_replay_verified"]
    assert replay["initial"]["entanglement_graph"]["graph_root_hash72"] == replay["replay"]["entanglement_graph"]["graph_root_hash72"]


def test_replay_graph_mutation_is_rejected():
    workload = default_workload(R, workload_id="NEG:graph", prime_count=4)
    workload["alter_merge_graph_on_replay"] = True
    with pytest.raises(ContractError, match="REJECT_COLLATZ_ENTANGLEMENT_REPLAY_MISMATCH"):
        verify_replay(R, workload)


def test_negative_cases_all_pass():
    assert all(case["passed"] for case in negative_cases(R))


def test_registry_has_w91_01_through_w91_12():
    workloads = workload_registry(R)
    assert len(workloads) == 12
    assert workloads[0]["workload_id"].startswith("W91-01")
    assert workloads[-1]["workload_id"].startswith("W91-12")
