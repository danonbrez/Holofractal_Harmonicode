from __future__ import annotations

from copy import deepcopy
import json
import pytest

import hhs_backend.runtime.hhs_pass214_iteration8_terminal_freeze_v3 as i8


def h(ch: str) -> str:
    return ch * 64


def census() -> dict:
    return {
        "source_commit": "a" * 40,
        "source_tree": "b" * 40,
        "coverage": {"classification_complete": True, "static_scan_errors": 0},
        "roots": {
            "repository_tree_root_hash216": h("1"),
            "optimization_registry_root_hash216": h("2"),
        },
    }


def compatibility() -> dict:
    return {
        "source_commit": "a" * 40,
        "source_tree": "b" * 40,
        "coverage": {"active_unresolved": 0, "authority_conflict_candidates": 0},
        "roots": {"compatibility_graph_root_hash216": h("3")},
    }


def benchmark() -> dict:
    modes = [
        "cold", "warm", "exact_repetition", "shared_structure",
        "single_region_mutation", "multi_region_mutation", "novel_content",
        "contradictory_content", "no_reuse_control", "interruption_recovery",
        "cross_process_replay",
    ]
    return {
        "schema": "HHS_PASS_214_FINAL_COMPOUND_BENCHMARK_BUNDLE_V1",
        "semantic_observational_separation": True,
        "append_only_result_integrity": True,
        "multimodal_ml_compound_exercised": True,
        "multimodal_ml_ablation_exercised": True,
        "incremental_full_equality": True,
        "recovery_replay_semantic_equality": True,
        "cross_process_replay_semantic_equality": True,
        "negative_controls_fail_closed": True,
        "complete_cost_accounting": True,
        "compression_incidence_complete_physical_accounting": True,
        "stages": {
            stage: {
                "state": "NOT_APPLICABLE" if stage == "A9" else "MEASURED",
                **(
                    {"reason": "no accelerator configured"}
                    if stage == "A9"
                    else {"semantic_equal": True}
                ),
            }
            for stage in i8.REQUIRED_STAGES
        },
        "ablations": {
            layer: {"state": "MEASURED", "semantic_equal": True}
            for layer in i8.MANDATORY_ABLATIONS
        },
        "workloads": {
            family: {
                "state": "MEASURED",
                "semantic_equal": True,
                "modes": list(modes),
            }
            for family in i8.REQUIRED_WORKLOAD_FAMILIES
        },
        "observations": {"elapsed_ns": 123456789},
    }


def profile() -> dict:
    return {
        "schema": i8.PASS215_PROFILE_SCHEMA,
        "required_comparisons": list(i8.REQUIRED_PASS215_COMPARISONS),
        "optimization_classes": {
            "complete_inherited_hhs_stack": "REQUIRED",
            "accelerator_batching": "OPTIONAL",
        },
        "post_hoc_redefinition_forbidden": True,
        "repository_visible_runnable_state": True,
    }


def freeze(**extra) -> dict:
    return i8.create_terminal_freeze(
        census_summary=census(),
        compatibility_summary=compatibility(),
        authority_reconciliation=None,
        workload_corpus={
            "schema": "HHS_PASS214_WORKLOAD_CORPUS_V1",
            "families": list(i8.REQUIRED_WORKLOAD_FAMILIES),
        },
        benchmark_method={
            "schema": "HHS_PASS214_BENCHMARK_METHOD_V1",
            "stages": list(i8.REQUIRED_STAGES),
        },
        benchmark_bundle=benchmark(),
        pass215_profile=profile(),
        source_commit="a" * 40,
        source_tree="b" * 40,
        **extra,
    )


def test_readiness_is_fail_closed_without_benchmark_evidence():
    report = i8.inspect_terminal_readiness(
        census_summary=census(),
        compatibility_summary=compatibility(),
        authority_reconciliation=None,
        benchmark_bundle=None,
        pass215_profile=None,
    )
    assert report["ready"] is False
    assert report["terminal_roots_minted"] is False
    assert report["pass215_authorized"] is False
    assert report["pass213_gates_preserved"] is True
    assert report["blockers"]


def test_complete_pass214_readiness_does_not_require_live_pass213_admission():
    report = i8.inspect_terminal_readiness(
        census_summary=census(),
        compatibility_summary=compatibility(),
        authority_reconciliation=None,
        benchmark_bundle=benchmark(),
        pass215_profile=profile(),
        live_admission=None,
    )
    assert report["ready"] is True
    assert report["blockers"] == []
    assert report["pass213_gates_preserved"] is True
    assert report["pass213_live_admission_required_before_canonical_mutation"] is True


def test_benchmark_requires_multimodal_and_complete_a0_a9_matrix():
    broken = benchmark()
    broken["multimodal_ml_ablation_exercised"] = False
    with pytest.raises(
        i8.Pass214Iteration8Error, match="MULTIMODAL_ML_ABLATION_REQUIRED"
    ):
        i8.validate_benchmark_bundle(broken)
    broken = benchmark()
    del broken["stages"]["A7"]
    with pytest.raises(
        i8.Pass214Iteration8Error, match="A0_A9_STAGE_SET_INCOMPLETE"
    ):
        i8.validate_benchmark_bundle(broken)


def test_benchmark_requires_all_ablations_and_workload_modes():
    broken = benchmark()
    del broken["ablations"][i8.MANDATORY_ABLATIONS[0]]
    with pytest.raises(
        i8.Pass214Iteration8Error, match="MANDATORY_ABLATION_SET_INCOMPLETE"
    ):
        i8.validate_benchmark_bundle(broken)
    broken = benchmark()
    broken["workloads"][i8.REQUIRED_WORKLOAD_FAMILIES[0]]["modes"].remove(
        "cross_process_replay"
    )
    with pytest.raises(i8.Pass214Iteration8Error, match="MODES_INCOMPLETE"):
        i8.validate_benchmark_bundle(broken)


def test_terminal_freeze_mints_eight_benchmark_roots_before_pass213_runtime_gate():
    record = freeze()
    assert tuple(record["terminal_roots"]) == i8.TERMINAL_ROOT_NAMES
    assert record["terminal_roots_minted"] is True
    assert record["authority_promoted"] is True
    assert record["benchmark_authority_promoted"] is True
    assert record["pass215_authorized"] is True
    assert record["pass213_gates_preserved"] is True
    assert record["runtime_mutation_authority_promoted"] is False
    assert record["canonical_mutation_authorized"] is False
    assert record["migration_active"] is False
    assert record["pass213_live_admission_required_before_canonical_mutation"] is True
    assert len(record["terminal_receipt_hash72"]) == 72
    assert len(record["authority_reconciliation_root_hash216"]) == 64
    assert len(record["pass213_gate_preservation_root_hash216"]) == 64
    assert i8.validate_terminal_freeze(record)


def test_sorted_json_round_trip_preserves_terminal_authority():
    record = freeze()
    restored = json.loads(json.dumps(record, sort_keys=True))
    assert list(restored["terminal_roots"]) != list(i8.TERMINAL_ROOT_NAMES)
    assert set(restored["terminal_roots"]) == set(i8.TERMINAL_ROOT_NAMES)
    assert i8.validate_terminal_freeze(restored)


def test_live_admission_input_cannot_redefine_pass214_benchmark_authority():
    without_live = freeze()
    with_untrusted_live = freeze(live_admission={"synthetic": True})
    assert with_untrusted_live["terminal_roots"] == without_live["terminal_roots"]
    assert with_untrusted_live["terminal_receipt_hash72"] == without_live[
        "terminal_receipt_hash72"
    ]
    assert with_untrusted_live["canonical_mutation_authorized"] is False


def test_pass213_gate_preservation_tamper_is_rejected():
    record = freeze()
    tampered = deepcopy(record)
    tampered["pass213_gate_preservation"]["pass213_gates_preserved"] = False
    with pytest.raises(
        i8.Pass214Iteration8Error, match="PASS213_GATE_PRESERVATION_MISMATCH"
    ):
        i8.validate_terminal_freeze(tampered)


def test_terminal_record_tamper_is_rejected():
    record = freeze()
    tampered = deepcopy(record)
    tampered["terminal_roots"]["PASS214_COMPOUND_EVIDENCE_ROOT_HASH216"] = h("f")
    with pytest.raises(i8.Pass214Iteration8Error, match="TERMINAL_RECEIPT_MISMATCH"):
        i8.validate_terminal_freeze(tampered)


def test_runtime_mutation_promotion_is_rejected_before_pass213_gate():
    record = freeze()
    tampered = deepcopy(record)
    tampered["runtime_mutation_authority_promoted"] = True
    with pytest.raises(i8.Pass214Iteration8Error, match="PASS213_GATE_BYPASS_DETECTED"):
        i8.validate_terminal_freeze(tampered)


def test_float_canonical_authority_is_rejected():
    broken = benchmark()
    broken["observations"]["bad"] = 1.25
    with pytest.raises(
        i8.Pass214Iteration8Error, match="FLOAT_CANONICAL_AUTHORITY_FORBIDDEN"
    ):
        i8.validate_benchmark_bundle(broken)
