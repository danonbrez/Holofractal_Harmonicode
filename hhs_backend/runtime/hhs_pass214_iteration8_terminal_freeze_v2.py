"""Pass 214 Iteration 8 terminal benchmark/profile freeze authority, repair v2.

Pass 214 executes and freezes its repository-wide benchmark authority before the
Pass 213 terminal runtime gate.  The inherited Pass 213 authorities remain
mandatory for canonical mutation, but an operational RFC 3161 admission is not
an input to the Pass 214 benchmark authority itself.

This module supersedes the pre-merge v1 terminal ordering without deleting it.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_backend.runtime import hhs_pass214_iteration8_terminal_freeze_v1 as _v1

PASS_NUMBER = 214
ITERATION = 8
SCHEMA = "HHS_PASS_214_ITERATION_8_TERMINAL_FREEZE_V2"
INSPECTION_SCHEMA = "HHS_PASS_214_ITERATION_8_READINESS_INSPECTION_V2"
PASS215_PROFILE_SCHEMA = _v1.PASS215_PROFILE_SCHEMA
CLASSIFICATION = "HHS_PASS_214_TERMINAL_BENCHMARK_AUTHORITY_FROZEN"
BLOCKED_CLASSIFICATION = "HHS_PASS_214_ITERATION_8_TERMINAL_FREEZE_BLOCKED"
AUTHORITY_SCOPE = "PASS214_BENCHMARK_AUTHORITY_ONLY"
GATE_PRESERVATION_SCHEMA = "HHS_PASS_214_PASS_213_GATE_PRESERVATION_V1"

PASS213_CLOSURE = _v1.PASS213_CLOSURE
ITERATION6_CANDIDATE_SET_ROOT = _v1.ITERATION6_CANDIDATE_SET_ROOT
TERMINAL_ROOT_NAMES = _v1.TERMINAL_ROOT_NAMES
REQUIRED_STAGES = _v1.REQUIRED_STAGES
MANDATORY_ABLATIONS = _v1.MANDATORY_ABLATIONS
REQUIRED_WORKLOAD_FAMILIES = _v1.REQUIRED_WORKLOAD_FAMILIES
REQUIRED_PASS215_COMPARISONS = _v1.REQUIRED_PASS215_COMPARISONS
ALLOWED_PROFILE_CLASSES = _v1.ALLOWED_PROFILE_CLASSES
Pass214Iteration8Error = _v1.Pass214Iteration8Error

PASS213_REQUIRED_AUTHORITIES = (
    "correction_before_interpretation_or_execution",
    "immutable_compiled_rom_identity",
    "protected_native_memory_and_zeroization",
    "exact_and_dependency_scoped_parametric_admission",
    "persistent_inventory_tombstones_recovery_and_continuity",
    "post_quantum_checkpoint_enclosure",
    "rfc3161_trusted_timestamp_lineage",
    "exact_moving_tensor_routing",
    "capability_governed_api_cli",
    "singleton_vm81_native_dispatch",
    "deterministic_hash216_hash72_successor_receipts",
    "authenticated_execution_ledgers",
    "full_hydration_recovery_and_resumable_replay",
)

canonical_bytes = _v1.canonical_bytes
_reject_float = _v1._reject_float
hash216 = _v1.hash216
_mapping = _v1._mapping
_hash = _v1._hash
_root = _v1._root
validate_benchmark_bundle = _v1.validate_benchmark_bundle
validate_pass215_profile = _v1.validate_pass215_profile
_validate_reconciliation_for_compatibility = _v1._validate_reconciliation_for_compatibility


def pass213_gate_preservation_record() -> dict[str, Any]:
    unsigned = {
        "schema": GATE_PRESERVATION_SCHEMA,
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "pass213_closure": PASS213_CLOSURE,
        "required_authorities": list(PASS213_REQUIRED_AUTHORITIES),
        "pass213_gates_preserved": True,
        "execution_order": "PASS214_BENCHMARK_BEFORE_PASS213_TERMINAL_RUNTIME_GATE",
        "pass214_benchmark_may_execute_before_live_runtime_admission": True,
        "pass214_benchmark_is_canonical_mutation": False,
        "canonical_mutation_requires_pass213_live_admission": True,
        "runtime_mutation_authority_promoted": False,
        "migration_active": False,
    }
    return {
        **unsigned,
        "gate_preservation_root_hash216": _root(
            "pass214-pass213-gate-preservation", unsigned
        ),
    }


def validate_pass213_gate_preservation(record: Mapping[str, Any]) -> Mapping[str, Any]:
    record = _mapping(record, "PASS213_GATE_PRESERVATION")
    _reject_float(record)
    expected = pass213_gate_preservation_record()
    if dict(record) != expected:
        raise Pass214Iteration8Error("PASS214_I8_PASS213_GATE_PRESERVATION_MISMATCH")
    return record


def readiness_blockers(
    *,
    census_summary: Any,
    compatibility_summary: Any,
    authority_reconciliation: Any = None,
    benchmark_bundle: Any = None,
    pass215_profile: Any = None,
    live_admission: Any = None,
) -> list[str]:
    """Return Pass 214 benchmark-authority blockers only.

    live_admission is accepted for call compatibility with v1 but intentionally
    does not participate in Pass 214 readiness.  Pass 213 live admission is a
    downstream canonical-mutation gate.
    """
    del live_admission
    blockers: list[str] = []
    try:
        census = _mapping(census_summary, "CENSUS_SUMMARY")
        coverage = _mapping(census.get("coverage"), "CENSUS_COVERAGE")
        if coverage.get("classification_complete") is not True:
            blockers.append("PASS214_I8_REPOSITORY_CENSUS_INCOMPLETE")
        if coverage.get("static_scan_errors") != 0:
            blockers.append("PASS214_I8_STATIC_SCAN_ERRORS_PRESENT")
    except (Pass214Iteration8Error, TypeError) as exc:
        blockers.append(str(exc))

    try:
        compat = _mapping(compatibility_summary, "COMPATIBILITY_SUMMARY")
        coverage = _mapping(compat.get("coverage"), "COMPATIBILITY_COVERAGE")
        if int(coverage.get("active_unresolved", 0)) != 0:
            blockers.append("PASS214_I8_ACTIVE_CALLABLES_UNRESOLVED")
        _validate_reconciliation_for_compatibility(compat, authority_reconciliation)
    except (Pass214Iteration8Error, TypeError, ValueError) as exc:
        blockers.append(str(exc))

    for validator, value in (
        (validate_benchmark_bundle, benchmark_bundle),
        (validate_pass215_profile, pass215_profile),
    ):
        try:
            validator(value)
        except (Pass214Iteration8Error, TypeError) as exc:
            blockers.append(str(exc))

    try:
        validate_pass213_gate_preservation(pass213_gate_preservation_record())
    except (Pass214Iteration8Error, TypeError) as exc:
        blockers.append(str(exc))

    return sorted(set(blockers))


def inspect_terminal_readiness(**kwargs: Any) -> dict[str, Any]:
    blockers = readiness_blockers(**kwargs)
    preservation = pass213_gate_preservation_record()
    return {
        "schema": INSPECTION_SCHEMA,
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "classification": CLASSIFICATION if not blockers else BLOCKED_CLASSIFICATION,
        "ready": not blockers,
        "blockers": blockers,
        "pass213_gates_preserved": True,
        "pass213_gate_preservation_root_hash216": preservation[
            "gate_preservation_root_hash216"
        ],
        "terminal_roots_minted": False,
        "authority_promoted": False,
        "benchmark_authority_promoted": False,
        "runtime_mutation_authority_promoted": False,
        "canonical_mutation_authorized": False,
        "migration_active": False,
        "pass215_authorized": False,
        "pass213_live_admission_required_before_canonical_mutation": True,
    }


def create_terminal_freeze(
    *,
    census_summary: Mapping[str, Any],
    compatibility_summary: Mapping[str, Any],
    authority_reconciliation: Mapping[str, Any] | None,
    workload_corpus: Mapping[str, Any],
    benchmark_method: Mapping[str, Any],
    benchmark_bundle: Mapping[str, Any],
    pass215_profile: Mapping[str, Any],
    source_commit: str,
    source_tree: str,
    live_admission: Any = None,
) -> dict[str, Any]:
    """Mint Pass 214 benchmark authority without promoting runtime mutation.

    live_admission is ignored for compatibility with v1 callers.  Runtime
    mutation remains blocked until the separate Pass 213 gate succeeds.
    """
    del live_admission
    blockers = readiness_blockers(
        census_summary=census_summary,
        compatibility_summary=compatibility_summary,
        authority_reconciliation=authority_reconciliation,
        benchmark_bundle=benchmark_bundle,
        pass215_profile=pass215_profile,
    )
    if blockers:
        raise Pass214Iteration8Error(
            "PASS214_I8_TERMINAL_FREEZE_BLOCKED:" + "|".join(blockers)
        )

    bundle = validate_benchmark_bundle(benchmark_bundle)
    profile = validate_pass215_profile(pass215_profile)
    reconciliation = _validate_reconciliation_for_compatibility(
        compatibility_summary, authority_reconciliation
    )
    preservation = validate_pass213_gate_preservation(
        pass213_gate_preservation_record()
    )

    if (
        census_summary.get("source_commit") != source_commit
        or compatibility_summary.get("source_commit") != source_commit
    ):
        raise Pass214Iteration8Error("PASS214_I8_SOURCE_COMMIT_MISMATCH")
    if (
        census_summary.get("source_tree") != source_tree
        or compatibility_summary.get("source_tree") != source_tree
    ):
        raise Pass214Iteration8Error("PASS214_I8_SOURCE_TREE_MISMATCH")

    census_roots = _mapping(census_summary.get("roots"), "CENSUS_ROOTS")
    compat_roots = _mapping(
        compatibility_summary.get("roots"), "COMPATIBILITY_ROOTS"
    )
    roots = {
        TERMINAL_ROOT_NAMES[0]: _hash(
            census_roots.get("repository_tree_root_hash216"), "REPOSITORY_SCAN"
        ),
        TERMINAL_ROOT_NAMES[1]: _hash(
            census_roots.get("optimization_registry_root_hash216"),
            "OPTIMIZATION_REGISTRY",
        ),
        TERMINAL_ROOT_NAMES[2]: _hash(
            compat_roots.get("compatibility_graph_root_hash216")
            or compat_roots.get("iteration2_semantic_root_hash216"),
            "COMPATIBILITY_GRAPH",
        ),
        TERMINAL_ROOT_NAMES[3]: _root("pass214-workload-corpus", workload_corpus),
        TERMINAL_ROOT_NAMES[4]: _root("pass214-benchmark-method", benchmark_method),
        TERMINAL_ROOT_NAMES[5]: _root("pass214-compound-evidence", bundle),
        TERMINAL_ROOT_NAMES[7]: _root("pass215-benchmark-profile", profile),
    }
    reconciliation_root = (
        _hash(
            reconciliation.get("reconciliation_root_hash216"),
            "AUTHORITY_RECONCILIATION",
        )
        if reconciliation is not None
        else _root(
            "pass214-authority-reconciliation-empty",
            {"candidate_conflict_count": 0},
        )
    )

    bindings = {
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "authority_scope": AUTHORITY_SCOPE,
        "pass213_closure": PASS213_CLOSURE,
        "iteration6_candidate_set_root_hash216": ITERATION6_CANDIDATE_SET_ROOT,
        "pass213_gate_preservation_root_hash216": preservation[
            "gate_preservation_root_hash216"
        ],
        "source_commit": source_commit,
        "source_tree": source_tree,
        "authority_reconciliation_root_hash216": reconciliation_root,
        "repository_scan_root_hash216": roots[TERMINAL_ROOT_NAMES[0]],
        "optimization_registry_root_hash216": roots[TERMINAL_ROOT_NAMES[1]],
        "compatibility_graph_root_hash216": roots[TERMINAL_ROOT_NAMES[2]],
        "workload_corpus_root_hash216": roots[TERMINAL_ROOT_NAMES[3]],
        "benchmark_method_root_hash216": roots[TERMINAL_ROOT_NAMES[4]],
        "compound_evidence_root_hash216": roots[TERMINAL_ROOT_NAMES[5]],
        "pass215_benchmark_profile_root_hash216": roots[TERMINAL_ROOT_NAMES[7]],
    }
    roots[TERMINAL_ROOT_NAMES[6]] = _root(
        "pass214-terminal-benchmark-authority", bindings
    )
    ordered_roots = {name: roots[name] for name in TERMINAL_ROOT_NAMES}
    receipt_payload = {
        "schema": SCHEMA,
        "classification": CLASSIFICATION,
        "source_commit": source_commit,
        "source_tree": source_tree,
        "terminal_roots": ordered_roots,
    }
    result = {
        **receipt_payload,
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "authority_scope": AUTHORITY_SCOPE,
        "pass213_closure": PASS213_CLOSURE,
        "iteration6_candidate_set_root_hash216": ITERATION6_CANDIDATE_SET_ROOT,
        "pass213_gate_preservation": deepcopy(preservation),
        "pass213_gate_preservation_root_hash216": preservation[
            "gate_preservation_root_hash216"
        ],
        "authority_reconciliation_root_hash216": reconciliation_root,
        "terminal_receipt_hash72": hash72_digest(
            {"domain": "HHS-P214-ITERATION8-TERMINAL-RECEIPT-V2"},
            receipt_payload,
        ),
        "acceptance_gates_passed": True,
        "terminal_roots_minted": True,
        "authority_promoted": True,
        "benchmark_authority_promoted": True,
        "runtime_mutation_authority_promoted": False,
        "canonical_mutation_authorized": False,
        "pass213_gates_preserved": True,
        "pass213_live_admission_required_before_canonical_mutation": True,
        "migration_active": False,
        "pass215_authorized": True,
        "authority_bindings": deepcopy(bindings),
        "pass215_profile": deepcopy(profile),
    }
    _reject_float(result)
    return result


def validate_terminal_freeze(record: Mapping[str, Any]) -> bool:
    record = _mapping(record, "TERMINAL_RECORD")
    _reject_float(record)
    if record.get("schema") != SCHEMA or record.get("classification") != CLASSIFICATION:
        raise Pass214Iteration8Error(
            "PASS214_I8_TERMINAL_SCHEMA_OR_CLASSIFICATION_INVALID"
        )
    if record.get("authority_scope") != AUTHORITY_SCOPE:
        raise Pass214Iteration8Error("PASS214_I8_AUTHORITY_SCOPE_INVALID")

    roots = _mapping(record.get("terminal_roots"), "TERMINAL_ROOTS")
    if tuple(roots.keys()) != TERMINAL_ROOT_NAMES:
        raise Pass214Iteration8Error("PASS214_I8_TERMINAL_ROOT_SET_OR_ORDER_INVALID")
    for name in TERMINAL_ROOT_NAMES:
        _hash(roots.get(name), name)

    expected_receipt = hash72_digest(
        {"domain": "HHS-P214-ITERATION8-TERMINAL-RECEIPT-V2"},
        {
            "schema": record["schema"],
            "classification": record["classification"],
            "source_commit": record["source_commit"],
            "source_tree": record["source_tree"],
            "terminal_roots": dict(roots),
        },
    )
    if record.get("terminal_receipt_hash72") != expected_receipt:
        raise Pass214Iteration8Error("PASS214_I8_TERMINAL_RECEIPT_MISMATCH")

    if (
        record.get("acceptance_gates_passed") is not True
        or record.get("terminal_roots_minted") is not True
    ):
        raise Pass214Iteration8Error("PASS214_I8_ACCEPTANCE_GATES_NOT_PASSED")
    if (
        record.get("authority_promoted") is not True
        or record.get("benchmark_authority_promoted") is not True
        or record.get("pass215_authorized") is not True
    ):
        raise Pass214Iteration8Error("PASS214_I8_BENCHMARK_AUTHORITY_NOT_PROMOTED")
    if (
        record.get("runtime_mutation_authority_promoted") is not False
        or record.get("canonical_mutation_authorized") is not False
        or record.get("migration_active") is not False
        or record.get("pass213_gates_preserved") is not True
        or record.get("pass213_live_admission_required_before_canonical_mutation")
        is not True
    ):
        raise Pass214Iteration8Error("PASS214_I8_PASS213_GATE_BYPASS_DETECTED")

    profile = validate_pass215_profile(record.get("pass215_profile"))
    if roots[TERMINAL_ROOT_NAMES[7]] != _root(
        "pass215-benchmark-profile", profile
    ):
        raise Pass214Iteration8Error("PASS214_I8_PASS215_PROFILE_ROOT_MISMATCH")

    preservation = validate_pass213_gate_preservation(
        _mapping(record.get("pass213_gate_preservation"), "PASS213_GATE_PRESERVATION")
    )
    preservation_root = preservation["gate_preservation_root_hash216"]
    if record.get("pass213_gate_preservation_root_hash216") != preservation_root:
        raise Pass214Iteration8Error("PASS214_I8_PASS213_GATE_ROOT_MISMATCH")

    bindings = _mapping(record.get("authority_bindings"), "AUTHORITY_BINDINGS")
    if bindings.get("authority_scope") != AUTHORITY_SCOPE:
        raise Pass214Iteration8Error("PASS214_I8_AUTHORITY_BINDING_SCOPE_MISMATCH")
    if (
        bindings.get("source_commit") != record.get("source_commit")
        or bindings.get("source_tree") != record.get("source_tree")
    ):
        raise Pass214Iteration8Error("PASS214_I8_AUTHORITY_BINDING_SOURCE_MISMATCH")
    if bindings.get("pass213_closure") != PASS213_CLOSURE:
        raise Pass214Iteration8Error("PASS214_I8_PASS213_CLOSURE_MISMATCH")
    if (
        bindings.get("pass213_gate_preservation_root_hash216")
        != preservation_root
    ):
        raise Pass214Iteration8Error(
            "PASS214_I8_PASS213_GATE_BINDING_ROOT_MISMATCH"
        )
    if (
        bindings.get("authority_reconciliation_root_hash216")
        != record.get("authority_reconciliation_root_hash216")
    ):
        raise Pass214Iteration8Error(
            "PASS214_I8_AUTHORITY_RECONCILIATION_BINDING_MISMATCH"
        )
    _hash(
        record.get("authority_reconciliation_root_hash216"),
        "AUTHORITY_RECONCILIATION",
    )

    for key, terminal in (
        ("repository_scan_root_hash216", TERMINAL_ROOT_NAMES[0]),
        ("optimization_registry_root_hash216", TERMINAL_ROOT_NAMES[1]),
        ("compatibility_graph_root_hash216", TERMINAL_ROOT_NAMES[2]),
        ("workload_corpus_root_hash216", TERMINAL_ROOT_NAMES[3]),
        ("benchmark_method_root_hash216", TERMINAL_ROOT_NAMES[4]),
        ("compound_evidence_root_hash216", TERMINAL_ROOT_NAMES[5]),
        ("pass215_benchmark_profile_root_hash216", TERMINAL_ROOT_NAMES[7]),
    ):
        if bindings.get(key) != roots[terminal]:
            raise Pass214Iteration8Error(
                f"PASS214_I8_AUTHORITY_BINDING_ROOT_MISMATCH:{key}"
            )

    if roots[TERMINAL_ROOT_NAMES[6]] != _root(
        "pass214-terminal-benchmark-authority", bindings
    ):
        raise Pass214Iteration8Error("PASS214_I8_AUTHORITY_ROOT_MISMATCH")
    return True


__all__ = [
    "PASS_NUMBER",
    "ITERATION",
    "SCHEMA",
    "INSPECTION_SCHEMA",
    "PASS215_PROFILE_SCHEMA",
    "CLASSIFICATION",
    "BLOCKED_CLASSIFICATION",
    "AUTHORITY_SCOPE",
    "GATE_PRESERVATION_SCHEMA",
    "PASS213_CLOSURE",
    "ITERATION6_CANDIDATE_SET_ROOT",
    "TERMINAL_ROOT_NAMES",
    "REQUIRED_STAGES",
    "MANDATORY_ABLATIONS",
    "REQUIRED_WORKLOAD_FAMILIES",
    "REQUIRED_PASS215_COMPARISONS",
    "ALLOWED_PROFILE_CLASSES",
    "PASS213_REQUIRED_AUTHORITIES",
    "Pass214Iteration8Error",
    "canonical_bytes",
    "hash216",
    "validate_benchmark_bundle",
    "validate_pass215_profile",
    "pass213_gate_preservation_record",
    "validate_pass213_gate_preservation",
    "readiness_blockers",
    "inspect_terminal_readiness",
    "create_terminal_freeze",
    "validate_terminal_freeze",
]
