"""Pass 215 Iteration 4 primitive executed-work accounting v3.

Execution semantics and candidates remain those of v1.  Serialized validation
hardening remains v2.  This layer applies the repository-frozen accounting
addendum so descriptive capacity/coverage fields and attribution aliases are
not double-counted as primitive executed operations.
"""
from __future__ import annotations

from typing import Any, Mapping

from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as v1
from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v2 as v2
from hhs_backend.runtime.hhs_pass215_iteration4_exact_linear_execution_v1 import *  # noqa: F401,F403

WORK_ACCOUNTING_SCHEMA = "HHS_PASS_215_ITERATION_4_PRIMITIVE_WORK_ACCOUNTING_V1"
WORK_ACCOUNTING_ADDENDUM_GIT_BLOB_SHA1 = "0a2f1448f565fb3eebfb50845c44404b68e93b8b"
PRIMITIVE_EXECUTED_WORK_UNIT_KEYS = (
    "block_decodes",
    "quant_integer_products",
    "quant_integer_additions",
    "exact_rational_scale_multiplications",
    "exact_rational_accumulation_additions",
    "compiled_descriptor_builds",
    "compiled_descriptor_hits",
    "exact_output_cache_hits",
    "exact_output_cache_misses",
    "changed_input_coordinates",
    "delta_output_accumulations",
    "recovery_work_units",
)
EXCLUDED_CAPACITY_OR_ATTRIBUTION_KEYS = (
    "source_tensor_bytes",
    "source_quantization_blocks",
    "logical_weights",
    "delta_weight_products",
    "full_output_rows_recomputed",
    "continuation_output_rows_updated",
    "semantic_compare_count",
    "checkpoint_bytes",
)


def primitive_executed_work_units(record: Mapping[str, int]) -> int:
    return sum(int(record.get(key, 0)) for key in PRIMITIVE_EXECUTED_WORK_UNIT_KEYS)


# v1._work_record resolves this module-global function at call time.  Patch only
# the aggregate formula; all raw counters and execution algorithms are retained.
v1._executed_work_units = primitive_executed_work_units


def _accounting_record() -> Mapping[str, Any]:
    return {
        "schema": WORK_ACCOUNTING_SCHEMA,
        "addendum_git_blob_sha1": WORK_ACCOUNTING_ADDENDUM_GIT_BLOB_SHA1,
        "first_green_pre_repair_run": 31221256596,
        "pre_repair_evidence_preserved": True,
        "primitive_executed_work_unit_keys": list(PRIMITIVE_EXECUTED_WORK_UNIT_KEYS),
        "excluded_capacity_or_attribution_keys": list(EXCLUDED_CAPACITY_OR_ATTRIBUTION_KEYS),
        "raw_work_counters_retained": True,
        "post_hoc_candidate_redefinition": False,
    }


def build_execution_evidence(*args, **kwargs):
    evidence = dict(v1.build_execution_evidence(*args, **kwargs))
    evidence.pop("evidence_root_hash216", None)
    evidence.pop("receipt_hash72", None)
    evidence["work_accounting"] = _accounting_record()
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
    accounting = evidence.get("work_accounting")
    if accounting != _accounting_record():
        raise v1.Pass215Iteration4ValidationError("PASS215_I4_WORK_ACCOUNTING_BINDING_INVALID")
    v2.validate_execution_evidence(evidence)


def validate_primitive_work_record(record: Mapping[str, int]) -> None:
    expected = primitive_executed_work_units(record)
    if int(record.get("executed_work_units_total", -1)) != expected:
        raise v1.Pass215Iteration4ValidationError("PASS215_I4_PRIMITIVE_WORK_TOTAL_MISMATCH")


__all__ = list(v1.__all__) + [
    "WORK_ACCOUNTING_SCHEMA",
    "WORK_ACCOUNTING_ADDENDUM_GIT_BLOB_SHA1",
    "PRIMITIVE_EXECUTED_WORK_UNIT_KEYS",
    "EXCLUDED_CAPACITY_OR_ATTRIBUTION_KEYS",
    "primitive_executed_work_units",
    "validate_primitive_work_record",
    "build_execution_evidence",
    "build_execution_evidence_from_path",
    "validate_execution_evidence",
]
