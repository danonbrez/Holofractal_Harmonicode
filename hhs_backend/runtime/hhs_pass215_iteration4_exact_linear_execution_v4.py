"""Pass 215 Iteration 4 frozen-comparison projection v4.

v1 owns execution semantics, v2 serialized-order hardening, and v3 primitive
work accounting.  This layer repair-forwards only the frozen-profile comparison
projection: dense_reference must bind to the actually executed dense exact
rational work record, not the cold compiled-descriptor mode.
"""
from __future__ import annotations

from typing import Any, Mapping

from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as v1
from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v3 as v3
from hhs_backend.runtime.hhs_pass215_iteration4_exact_linear_execution_v3 import *  # noqa: F401,F403

COMPARISON_MAPPING_SCHEMA = "HHS_PASS_215_ITERATION_4_COMPARISON_MAPPING_V1"
COMPARISON_MAPPING_ADDENDUM_GIT_BLOB_SHA1 = "17fc5927c96f944d89a9e06cc2a684ae47e97c56"
REQUIRED_SUITE_OUTPUT_ROOT_HASH216 = "14de39b3b326eb64bbac5d8be829c289c4a5e1f39b842bfdba59b46fea2c9acb"


def _exact_ratio(numerator: int, denominator: int) -> Mapping[str, int]:
    return v1._exact_fraction(int(numerator), int(denominator))


def _comparison_projection(evidence: Mapping[str, Any]) -> Mapping[str, Any]:
    aggregate = evidence["aggregate_execution"]
    modes = evidence["frozen_workload_modes"]
    dense_work = aggregate["dense_reference_work"]
    factored_work = aggregate["factored_reference_work"]
    return {
        "dense_reference": {
            "status": "EXECUTED",
            "candidate": "DENSE_EXACT_RATIONAL_REFERENCE_V1",
            "source": "aggregate_execution.dense_reference_work",
            "executed_work_units_total": int(dense_work["executed_work_units_total"]),
            "semantic_exactness": True,
        },
        "exact_integer_reference": {
            "status": "EXECUTED",
            "candidate": "Q4_0_FACTORED_EXACT_BLOCK_KERNEL_V1_WITH_EXACT_INTEGER_INNER_DOTS",
            "source": "aggregate_execution.factored_reference_work",
            "executed_work_units_total": int(factored_work["executed_work_units_total"]),
            "semantic_exactness": True,
        },
        "pass213_compiled_rom_only": {
            "status": "EXECUTED_BENCHMARK_ANALOG_ONLY",
            "candidate": "IMMUTABLE_COMPILED_BLOCK_DESCRIPTOR_V1_BENCHMARK_ANALOG_ONLY_NO_RUNTIME_AUTHORITY",
            "source": "frozen_workload_modes.warm.work",
            "mode": "warm",
            "runtime_authority": False,
            "executed_work_units_total": int(modes["warm"]["work"]["executed_work_units_total"]),
            "semantic_exactness": True,
        },
        "compiled_rom_plus_cache_layers": {
            "status": "EXECUTED_BENCHMARK_ANALOG_ONLY",
            "candidate": "IMMUTABLE_COMPILED_BLOCK_DESCRIPTOR_V1_PLUS_EXACT_INPUT_OUTPUT_CACHE_V1",
            "source": "frozen_workload_modes.exact_repetition.work",
            "mode": "exact_repetition",
            "runtime_authority": False,
            "executed_work_units_total": int(modes["exact_repetition"]["work"]["executed_work_units_total"]),
            "semantic_exactness": True,
        },
        "compiled_rom_plus_continuation_delta": {
            "status": "EXECUTED_BENCHMARK_ANALOG_ONLY",
            "candidate": "IMMUTABLE_COMPILED_BLOCK_DESCRIPTOR_V1_PLUS_LINEAR_CONTINUATION_DELTA_V1",
            "source": "frozen_workload_modes.single_region_mutation.work",
            "mode": "single_region_mutation",
            "runtime_authority": False,
            "executed_work_units_total": int(modes["single_region_mutation"]["work"]["executed_work_units_total"]),
            "semantic_exactness": True,
        },
        "compiled_rom_plus_multimodal_ml": {
            "status": "NOT_APPLICABLE",
            "reason": "SINGLE_TEXT_TRANSFORMER_LINEAR_OPERATOR_SLICE_NO_MULTIMODAL_INPUT_OR_LEARNING",
        },
        "complete_inherited_hhs_stack": {
            "status": "PARTIAL_ITERATION4_SUBSET_ONLY",
            "reason": "PASS215_TERMINAL_COMPLETE_STACK_NOT_YET_CLAIMED",
        },
        "complete_stack_with_ablations": {
            "status": "EXECUTED_ITERATION4_SUBSET_ABLATIONS",
            "modes": [
                "no_reuse_control",
                "warm",
                "exact_repetition",
                "single_region_mutation",
                "multi_region_mutation",
            ],
        },
    }


def _mapping_record() -> Mapping[str, Any]:
    return {
        "schema": COMPARISON_MAPPING_SCHEMA,
        "addendum_git_blob_sha1": COMPARISON_MAPPING_ADDENDUM_GIT_BLOB_SHA1,
        "first_primitive_work_green_run": 31221568421,
        "prior_evidence_preserved": True,
        "post_hoc_candidate_redefinition": False,
        "dense_reference_source": "aggregate_execution.dense_reference_work",
        "exact_integer_reference_source": "aggregate_execution.factored_reference_work",
    }


def build_execution_evidence(*args, **kwargs):
    evidence = dict(v3.build_execution_evidence(*args, **kwargs))
    evidence.pop("evidence_root_hash216", None)
    evidence.pop("receipt_hash72", None)
    if evidence["suite_output_root_hash216"] != REQUIRED_SUITE_OUTPUT_ROOT_HASH216:
        raise v1.Pass215Iteration4ValidationError("PASS215_I4_SUITE_OUTPUT_ROOT_CHANGED_DURING_COMPARISON_REPAIR")
    evidence["frozen_profile_comparisons"] = _comparison_projection(evidence)
    aggregate = dict(evidence["aggregate_execution"])
    dense_total = int(aggregate["dense_reference_work"]["executed_work_units_total"])
    factored_total = int(aggregate["factored_reference_work"]["executed_work_units_total"])
    aggregate["dense_to_factored_total_primitive_work_ratio_exact"] = _exact_ratio(dense_total, factored_total)
    aggregate["primitive_work_units_avoided_by_factoring"] = dense_total - factored_total
    evidence["aggregate_execution"] = aggregate
    evidence["comparison_mapping"] = _mapping_record()
    evidence_root = v1.hash216("pass215-i4-execution-evidence", v1.canonical_bytes(evidence))
    receipt = v1.hash72_digest(
        {"contract": v1.CONTRACT, "event": "PASS215_ITERATION4_EXACT_LINEAR_EXECUTION"},
        {
            "sequence": 4,
            "parent_hash72": v1.ITERATION3_RECEIPT_HASH72,
            "evidence_root_hash216": evidence_root,
            "suite_output_root_hash216": evidence["suite_output_root_hash216"],
        },
    )
    return {**evidence, "evidence_root_hash216": evidence_root, "receipt_hash72": receipt}


def build_execution_evidence_from_path(path, *, source, expected_sha256=None, frozen_profile_blob_sha1=v1.FROZEN_PROFILE_GIT_BLOB_SHA1):
    target = v1.Path(path)
    return build_execution_evidence(
        target.read_bytes(),
        filename=target.name,
        source=source,
        expected_sha256=expected_sha256,
        frozen_profile_blob_sha1=frozen_profile_blob_sha1,
    )


def validate_execution_evidence(evidence: Mapping[str, Any]) -> None:
    mapping = evidence.get("comparison_mapping")
    if mapping != _mapping_record():
        raise v1.Pass215Iteration4ValidationError("PASS215_I4_COMPARISON_MAPPING_BINDING_INVALID")
    if evidence.get("suite_output_root_hash216") != REQUIRED_SUITE_OUTPUT_ROOT_HASH216:
        raise v1.Pass215Iteration4ValidationError("PASS215_I4_SUITE_OUTPUT_ROOT_MISMATCH")
    aggregate = evidence.get("aggregate_execution")
    comparisons = evidence.get("frozen_profile_comparisons")
    if not isinstance(aggregate, Mapping) or not isinstance(comparisons, Mapping):
        raise v1.Pass215Iteration4ValidationError("PASS215_I4_COMPARISON_MAPPING_RECORD_MISSING")
    dense_total = int(aggregate["dense_reference_work"]["executed_work_units_total"])
    factored_total = int(aggregate["factored_reference_work"]["executed_work_units_total"])
    if comparisons["dense_reference"].get("source") != "aggregate_execution.dense_reference_work" or int(comparisons["dense_reference"].get("executed_work_units_total", -1)) != dense_total:
        raise v1.Pass215Iteration4ValidationError("PASS215_I4_DENSE_COMPARISON_BINDING_INVALID")
    if comparisons["exact_integer_reference"].get("source") != "aggregate_execution.factored_reference_work" or int(comparisons["exact_integer_reference"].get("executed_work_units_total", -1)) != factored_total:
        raise v1.Pass215Iteration4ValidationError("PASS215_I4_EXACT_INTEGER_COMPARISON_BINDING_INVALID")
    expected_ratio = _exact_ratio(dense_total, factored_total)
    if aggregate.get("dense_to_factored_total_primitive_work_ratio_exact") != expected_ratio:
        raise v1.Pass215Iteration4ValidationError("PASS215_I4_TOTAL_PRIMITIVE_WORK_RATIO_INVALID")
    v3.validate_execution_evidence(evidence)


__all__ = list(v3.__all__) + [
    "COMPARISON_MAPPING_SCHEMA",
    "COMPARISON_MAPPING_ADDENDUM_GIT_BLOB_SHA1",
    "REQUIRED_SUITE_OUTPUT_ROOT_HASH216",
    "build_execution_evidence",
    "build_execution_evidence_from_path",
    "validate_execution_evidence",
]
