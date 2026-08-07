"""Pass 214 final compound benchmark authority, contract-ordering repair v2.

The v1 executor measured the correct fixed corpus but labeled a completed Pass 214
benchmark as awaiting live Pass 213 admission.  The frozen Pass 214 contract does
not make deployment-local live admission a benchmark prerequisite.  This wrapper
preserves every v1 measurement and exactness gate, changes only the authority
status/ordering metadata, and recomputes the bundle Hash216/Hash72 identities.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from hhs_backend.runtime import hhs_pass214_final_compound_benchmark_v1 as _v1

PASS_NUMBER = 214
SCHEMA = _v1.SCHEMA
STATUS_COMPLETE = "FINAL_BENCHMARK_COMPLETE_READY_FOR_PASS214_TERMINAL_FREEZE"
Pass214FinalBenchmarkError = _v1.Pass214FinalBenchmarkError
FAMILY_SAMPLES = _v1.FAMILY_SAMPLES
MANDATORY_ABLATIONS = _v1.MANDATORY_ABLATIONS
REQUIRED_MODES = _v1.REQUIRED_MODES
hash216 = _v1.hash216
receipt72 = _v1.receipt72
_reject_float = _v1._reject_float


def _reroot(bundle: Mapping[str, Any]) -> dict[str, Any]:
    repaired = deepcopy(dict(bundle))
    repaired["status"] = STATUS_COMPLETE
    governance = dict(repaired.get("governance_accounting", {}))
    governance.update(
        {
            "pass214_benchmark_complete": 1,
            "pass214_terminal_freeze_ready": 1,
            "production_live_admission_claimed": 0,
            "canonical_mutation_authorized": 0,
        }
    )
    repaired["governance_accounting"] = governance

    for layer in ("moving_tensor_routing", "native_dispatch", "parametric_admission"):
        record = dict(repaired["ablations"][layer])
        if record.get("state") == "SUPERSEDED":
            record["reason"] = (
                "Runtime-effect authority remains downstream behind the inherited "
                "Pass 213 canonical-mutation gates; the completed Pass 214 benchmark "
                "does not promote deployment runtime authority"
            )
            repaired["ablations"][layer] = record

    repaired.pop("compound_evidence_root_hash216", None)
    repaired.pop("receipt_hash72", None)
    repaired["compound_evidence_root_hash216"] = hash216(
        "pass214-final-compound-evidence", repaired
    )
    repaired["receipt_hash72"] = receipt72(
        "HHS-P214-FINAL-COMPOUND-BENCHMARK-V2", repaired
    )
    _reject_float(repaired)
    return repaired


def build_final_benchmark_bundle(
    *,
    source_commit: str,
    source_tree: str,
    workload_corpus: Mapping[str, Any],
    benchmark_method: Mapping[str, Any],
) -> dict[str, Any]:
    measured = _v1.build_final_benchmark_bundle(
        source_commit=source_commit,
        source_tree=source_tree,
        workload_corpus=workload_corpus,
        benchmark_method=benchmark_method,
    )
    _v1.validate_final_benchmark_bundle(measured)
    repaired = _reroot(measured)
    validate_final_benchmark_bundle(repaired)
    return repaired


def validate_final_benchmark_bundle(bundle: Mapping[str, Any]) -> bool:
    _reject_float(bundle)
    if bundle.get("schema") != SCHEMA or bundle.get("status") != STATUS_COMPLETE:
        raise Pass214FinalBenchmarkError(
            "PASS214_FINAL_BENCHMARK_V2_SCHEMA_OR_STATUS_INVALID"
        )
    for key in (
        "semantic_observational_separation",
        "append_only_result_integrity",
        "multimodal_ml_compound_exercised",
        "multimodal_ml_ablation_exercised",
        "incremental_full_equality",
        "recovery_replay_semantic_equality",
        "cross_process_replay_semantic_equality",
        "negative_controls_fail_closed",
        "complete_cost_accounting",
        "compression_incidence_complete_physical_accounting",
    ):
        if bundle.get(key) is not True:
            raise Pass214FinalBenchmarkError(
                f"PASS214_FINAL_BENCHMARK_V2_GATE_FAILED:{key}"
            )
    if set(bundle.get("workloads", {})) != set(FAMILY_SAMPLES):
        raise Pass214FinalBenchmarkError(
            "PASS214_FINAL_BENCHMARK_V2_WORKLOAD_SET_INVALID"
        )
    if set(bundle.get("ablations", {})) != set(MANDATORY_ABLATIONS):
        raise Pass214FinalBenchmarkError(
            "PASS214_FINAL_BENCHMARK_V2_ABLATION_SET_INVALID"
        )
    if set(bundle.get("stages", {})) != {f"A{i}" for i in range(10)}:
        raise Pass214FinalBenchmarkError(
            "PASS214_FINAL_BENCHMARK_V2_STAGE_SET_INVALID"
        )
    governance = bundle.get("governance_accounting", {})
    if (
        governance.get("pass214_benchmark_complete") != 1
        or governance.get("pass214_terminal_freeze_ready") != 1
        or governance.get("production_live_admission_claimed") != 0
        or governance.get("canonical_mutation_authorized") != 0
    ):
        raise Pass214FinalBenchmarkError(
            "PASS214_FINAL_BENCHMARK_V2_GOVERNANCE_BOUNDARY_INVALID"
        )

    rooted = {
        key: value
        for key, value in bundle.items()
        if key not in {"compound_evidence_root_hash216", "receipt_hash72"}
    }
    expected_root = hash216("pass214-final-compound-evidence", rooted)
    if bundle.get("compound_evidence_root_hash216") != expected_root:
        raise Pass214FinalBenchmarkError(
            "PASS214_FINAL_BENCHMARK_V2_ROOT_MISMATCH"
        )
    expected_receipt = receipt72(
        "HHS-P214-FINAL-COMPOUND-BENCHMARK-V2",
        {**rooted, "compound_evidence_root_hash216": expected_root},
    )
    if bundle.get("receipt_hash72") != expected_receipt:
        raise Pass214FinalBenchmarkError(
            "PASS214_FINAL_BENCHMARK_V2_RECEIPT_MISMATCH"
        )
    return True


__all__ = [
    "PASS_NUMBER",
    "SCHEMA",
    "STATUS_COMPLETE",
    "Pass214FinalBenchmarkError",
    "build_final_benchmark_bundle",
    "validate_final_benchmark_bundle",
]
