"""Pass 214 deterministic authority-conflict reconciliation.

Iteration 2 deliberately emits conservative *candidates* whenever distinct
callables share a normalized entrypoint inside an authority domain.  This
module resolves those candidates without merging implementations or inventing
semantic equivalence: module/path namespaces remain distinct and canonical
mutation ownership remains the inherited Pass 213 governed VM81/native-dispatch
chain.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

PASS_NUMBER = 214
SCHEMA = "HHS_PASS_214_AUTHORITY_CONFLICT_RECONCILIATION_V1"
RECORD_SCHEMA = "HHS_PASS_214_AUTHORITY_CONFLICT_RESOLUTION_RECORD_V1"
CANONICAL_MUTATION_AUTHORITY = "PASS213_GOVERNED_VM81_NATIVE_DISPATCH"
PASS213_CLOSURE = "86ec461818682fc87232740758769602e8f9fe05"


class Pass214AuthorityReconciliationError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def hash216(domain: str, value: Any) -> str:
    raw = canonical_bytes(value)
    return sha256(domain.encode("utf-8") + b"\0" + len(raw).to_bytes(8, "big") + raw).hexdigest()


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_FLOAT_FORBIDDEN")
    if isinstance(value, Mapping):
        for child in value.values():
            _reject_float(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _reject_float(child)


def _record_index(callable_records: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    index: dict[str, Mapping[str, Any]] = {}
    for record in callable_records:
        symbol = record.get("symbol_hash216")
        if not isinstance(symbol, str) or len(symbol) != 64:
            raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_SYMBOL_HASH_INVALID")
        if symbol in index:
            raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_DUPLICATE_SYMBOL")
        index[symbol] = record
    return index


def _resolution_class(conflict: Mapping[str, Any]) -> str:
    if conflict.get("interface_compatible") is not True:
        return "NAMESPACE_SEPARATED_DISTINCT_INTERFACES"
    implementations = tuple(conflict.get("implementation_hashes", ()))
    if len(set(implementations)) > 1:
        return "NAMESPACE_SEPARATED_DISTINCT_IMPLEMENTATIONS"
    return "IDENTICAL_IMPLEMENTATION_RETAINED_WITHOUT_AUTHORITY_MERGE"


def reconcile_authority_conflicts(
    *,
    authority_conflicts: Sequence[Mapping[str, Any]],
    callable_records: Sequence[Mapping[str, Any]],
    compatibility_summary: Mapping[str, Any],
) -> dict[str, Any]:
    _reject_float(authority_conflicts)
    _reject_float(callable_records)
    _reject_float(compatibility_summary)
    if compatibility_summary.get("pass") != PASS_NUMBER:
        raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_PASS_MISMATCH")
    coverage = compatibility_summary.get("coverage")
    roots = compatibility_summary.get("roots")
    if not isinstance(coverage, Mapping) or not isinstance(roots, Mapping):
        raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_SUMMARY_INVALID")
    expected_count = int(coverage.get("authority_conflict_candidates", -1))
    if expected_count != len(authority_conflicts):
        raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_CONFLICT_COUNT_MISMATCH")
    source_commit = compatibility_summary.get("source_commit")
    source_tree = compatibility_summary.get("source_tree")
    if not isinstance(source_commit, str) or not isinstance(source_tree, str):
        raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_SOURCE_BINDING_MISSING")
    index = _record_index(callable_records)
    resolutions: list[dict[str, Any]] = []
    for conflict in authority_conflicts:
        member_ids = tuple(conflict.get("member_symbol_hash216", ()))
        if len(member_ids) < 2:
            raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_MEMBER_SET_INVALID")
        try:
            members = [index[symbol] for symbol in member_ids]
        except KeyError as exc:
            raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_MEMBER_NOT_FOUND") from exc
        member_paths = tuple(str(member.get("path")) for member in members)
        if len(set(member_paths)) != len(member_paths):
            raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_MEMBER_NAMESPACE_COLLISION")
        inherited_candidates = tuple(
            sorted(
                member["symbol_hash216"]
                for member in members
                if member.get("mutation_authority") == "INHERITED_VM81_OR_GOVERNED_AUTHORITY_CANDIDATE"
            )
        )
        resolution = {
            "schema": RECORD_SCHEMA,
            "authority_conflict_hash216": conflict.get("authority_conflict_hash216"),
            "authority_domain": conflict.get("authority_domain"),
            "normalized_entrypoint": conflict.get("normalized_entrypoint"),
            "member_symbol_hash216": list(member_ids),
            "member_paths": list(member_paths),
            "resolution_class": _resolution_class(conflict),
            "semantic_equivalence_claimed": False,
            "automatic_merger_authorized": False,
            "member_namespaces_preserved": True,
            "direct_member_authority_promotion": False,
            "governed_authority_candidate_members": list(inherited_candidates),
            "canonical_mutation_authority": CANONICAL_MUTATION_AUTHORITY,
            "pass213_closure": PASS213_CLOSURE,
            "effect_rule": "MEMBER_EFFECTS_REQUIRE_EXISTING_GOVERNED_VM81_ADMISSION",
            "pass215_default_classification": "OPTIONAL",
            "resolved": True,
        }
        resolution["resolution_root_hash216"] = hash216("pass214-authority-conflict-resolution", resolution)
        resolutions.append(resolution)
    resolutions.sort(key=lambda record: (str(record["authority_domain"]), str(record["normalized_entrypoint"]), str(record["authority_conflict_hash216"])))
    summary = {
        "schema": SCHEMA,
        "pass": PASS_NUMBER,
        "source_commit": source_commit,
        "source_tree": source_tree,
        "pass213_closure": PASS213_CLOSURE,
        "canonical_mutation_authority": CANONICAL_MUTATION_AUTHORITY,
        "iteration2_authority_conflict_root_hash216": roots.get("authority_conflict_root_hash216"),
        "candidate_conflict_count": len(authority_conflicts),
        "resolution_count": len(resolutions),
        "unresolved_conflict_count": 0,
        "automatic_merge_count": 0,
        "semantic_equivalence_inferred_count": 0,
        "all_conflicts_reconciled": len(resolutions) == len(authority_conflicts),
        "single_mutation_authority_preserved": True,
        "resolutions": resolutions,
    }
    summary["reconciliation_root_hash216"] = hash216(
        "pass214-authority-conflict-reconciliation",
        {key: value for key, value in summary.items() if key != "reconciliation_root_hash216"},
    )
    return summary


def validate_authority_reconciliation(
    report: Mapping[str, Any],
    *,
    compatibility_summary: Mapping[str, Any] | None = None,
) -> bool:
    _reject_float(report)
    if report.get("schema") != SCHEMA or report.get("pass") != PASS_NUMBER:
        raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_SCHEMA_INVALID")
    if report.get("pass213_closure") != PASS213_CLOSURE:
        raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_PASS213_CLOSURE_MISMATCH")
    if report.get("canonical_mutation_authority") != CANONICAL_MUTATION_AUTHORITY:
        raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_MUTATION_AUTHORITY_MISMATCH")
    if report.get("all_conflicts_reconciled") is not True:
        raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_INCOMPLETE")
    if int(report.get("unresolved_conflict_count", -1)) != 0 or int(report.get("automatic_merge_count", -1)) != 0:
        raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_UNSAFE_RESOLUTION")
    if report.get("single_mutation_authority_preserved") is not True:
        raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_SINGLE_AUTHORITY_VIOLATION")
    resolutions = report.get("resolutions")
    if not isinstance(resolutions, list) or len(resolutions) != int(report.get("candidate_conflict_count", -1)):
        raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_RECORD_COUNT_MISMATCH")
    for record in resolutions:
        if record.get("resolved") is not True or record.get("automatic_merger_authorized") is not False:
            raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_RECORD_UNSAFE")
        if record.get("semantic_equivalence_claimed") is not False or record.get("member_namespaces_preserved") is not True:
            raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_RECORD_SEMANTIC_OVERREACH")
        rooted = {key: value for key, value in record.items() if key != "resolution_root_hash216"}
        if record.get("resolution_root_hash216") != hash216("pass214-authority-conflict-resolution", rooted):
            raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_RECORD_ROOT_MISMATCH")
    rooted_report = {key: value for key, value in report.items() if key != "reconciliation_root_hash216"}
    if report.get("reconciliation_root_hash216") != hash216("pass214-authority-conflict-reconciliation", rooted_report):
        raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_ROOT_MISMATCH")
    if compatibility_summary is not None:
        coverage = compatibility_summary.get("coverage", {})
        roots = compatibility_summary.get("roots", {})
        if report.get("source_commit") != compatibility_summary.get("source_commit") or report.get("source_tree") != compatibility_summary.get("source_tree"):
            raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_SOURCE_MISMATCH")
        if int(report.get("candidate_conflict_count", -1)) != int(coverage.get("authority_conflict_candidates", -2)):
            raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_SUMMARY_COUNT_MISMATCH")
        if report.get("iteration2_authority_conflict_root_hash216") != roots.get("authority_conflict_root_hash216"):
            raise Pass214AuthorityReconciliationError("PASS214_AUTHORITY_RECONCILIATION_ITERATION2_ROOT_MISMATCH")
    return True
