from __future__ import annotations

from copy import deepcopy
import pytest

import hhs_backend.runtime.hhs_pass214_iteration8_terminal_freeze_v1 as i8


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
                **({"reason": "no accelerator configured"} if stage == "A9" else {"semantic_equal": True}),
            }
            for stage in i8.REQUIRED_STAGES
        },
        "ablations": {
            layer: {"state": "MEASURED", "semantic_equal": True}
            for layer in i8.MANDATORY_ABLATIONS
        },
        "workloads": {
            family: {"state": "MEASURED", "semantic_equal": True, "modes": list(modes)}
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


def live() -> dict:
    return {
        "admission_root_hash216": h("9"),
        "pass213_closure": i8.PASS213_CLOSURE,
        "iteration6_candidate_set_root_hash216": i8.ITERATION6_CANDIDATE_SET_ROOT,
        "trusted_timestamp_reverified_in_process": True,
        "governed_surface_reverified_in_process": True,
        "native_dispatch_reverified_in_process": True,
    }


def test_readiness_is_fail_closed_without_live_or_benchmark_evidence():
    report = i8.inspect_terminal_readiness(
        census_summary=census(), compatibility_summary=compatibility(),
        authority_reconciliation=None,
        benchmark_bundle=None, pass215_profile=None, live_admission=None,
    )
    assert report["ready"] is False
    assert report["terminal_roots_minted"] is False
    assert report["pass215_authorized"] is False
    assert report["blockers"]


def test_benchmark_requires_multimodal_and_complete_a0_a9_matrix():
    broken = benchmark()
    broken["multimodal_ml_ablation_exercised"] = False
    with pytest.raises(i8.Pass214Iteration8Error, match="MULTIMODAL_ML_ABLATION_REQUIRED"):
        i8.validate_benchmark_bundle(broken)
    broken = benchmark()
    del broken["stages"]["A7"]
    with pytest.raises(i8.Pass214Iteration8Error, match="A0_A9_STAGE_SET_INCOMPLETE"):
        i8.validate_benchmark_bundle(broken)


def test_benchmark_requires_all_ablations_and_workload_modes():
    broken = benchmark()
    del broken["ablations"][i8.MANDATORY_ABLATIONS[0]]
    with pytest.raises(i8.Pass214Iteration8Error, match="MANDATORY_ABLATION_SET_INCOMPLETE"):
        i8.validate_benchmark_bundle(broken)
    broken = benchmark()
    broken["workloads"][i8.REQUIRED_WORKLOAD_FAMILIES[0]]["modes"].remove("cross_process_replay")
    with pytest.raises(i8.Pass214Iteration8Error, match="MODES_INCOMPLETE"):
        i8.validate_benchmark_bundle(broken)


def test_terminal_freeze_mints_exact_eight_roots_only_after_gate(monkeypatch):
    monkeypatch.setattr(i8, "_validate_live_admission", lambda admission: admission)
    record = i8.create_terminal_freeze(
        census_summary=census(), compatibility_summary=compatibility(), authority_reconciliation=None,
        workload_corpus={"schema": "HHS_PASS214_WORKLOAD_CORPUS_V1", "families": list(i8.REQUIRED_WORKLOAD_FAMILIES)},
        benchmark_method={"schema": "HHS_PASS214_BENCHMARK_METHOD_V1", "stages": list(i8.REQUIRED_STAGES)},
        benchmark_bundle=benchmark(), pass215_profile=profile(), live_admission=live(),
        source_commit="a" * 40, source_tree="b" * 40,
    )
    assert tuple(record["terminal_roots"]) == i8.TERMINAL_ROOT_NAMES
    assert record["terminal_roots_minted"] is True
    assert record["authority_promoted"] is True
    assert record["pass215_authorized"] is True
    assert len(record["terminal_receipt_hash72"]) == 72
    assert len(record["authority_reconciliation_root_hash216"]) == 64
    assert i8.validate_terminal_freeze(record)


def test_terminal_record_tamper_is_rejected(monkeypatch):
    monkeypatch.setattr(i8, "_validate_live_admission", lambda admission: admission)
    record = i8.create_terminal_freeze(
        census_summary=census(), compatibility_summary=compatibility(), authority_reconciliation=None,
        workload_corpus={"schema": "HHS_PASS214_WORKLOAD_CORPUS_V1"},
        benchmark_method={"schema": "HHS_PASS214_BENCHMARK_METHOD_V1"},
        benchmark_bundle=benchmark(), pass215_profile=profile(), live_admission=live(),
        source_commit="a" * 40, source_tree="b" * 40,
    )
    tampered = deepcopy(record)
    tampered["terminal_roots"]["PASS214_COMPOUND_EVIDENCE_ROOT_HASH216"] = h("f")
    with pytest.raises(i8.Pass214Iteration8Error, match="TERMINAL_RECEIPT_MISMATCH"):
        i8.validate_terminal_freeze(tampered)


def test_float_canonical_authority_is_rejected():
    broken = benchmark()
    broken["observations"]["bad"] = 1.25
    with pytest.raises(i8.Pass214Iteration8Error, match="FLOAT_CANONICAL_AUTHORITY_FORBIDDEN"):
        i8.validate_benchmark_bundle(broken)
