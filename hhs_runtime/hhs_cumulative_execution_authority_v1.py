"""Fail-closed inherited execution-authority reachability for Pass 217.

This module converts the Pass 214/215 optimization profile from a capability
inventory into a per-operation utilization gate.  A REQUIRED inherited runtime
optimization authority has no accepted "available but optional" state.

For every operation, every inherited core authority must prove exactly one of:

* ACTIVE_IN_PATH         -- a concrete traversal witness was observed;
* NOT_APPLICABLE        -- mechanical facts prove the authority irrelevant;
* EXPLICITLY_SUPERSEDED -- a later pass explicitly replaces it and proves the
                           replacement against the inherited semantic contract.

Missing, malformed, ambiguous, or OPTIONAL_AVAILABLE dispositions fail closed.
The module does not infer irrelevance from absence and does not invent traversal
witnesses for code that has not actually executed the inherited layer.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness


VERSION = "PASS_217_CUMULATIVE_EXECUTION_AUTHORITY_REACHABILITY_V1"
SCHEMA = "HHS_CUMULATIVE_EXECUTION_AUTHORITY_REACHABILITY_V1"
DECISION_SCHEMA = "HHS_CUMULATIVE_EXECUTION_AUTHORITY_DECISION_V1"
PROFILE_SCHEMA = "HHS_PASS_215_BENCHMARK_PROFILE_V1"
PROFILE_SOURCE_PASS = 214
PROFILE_PATH = (
    Path(__file__).resolve().parents[1]
    / "contracts"
    / "pass215"
    / "PASS_215_BENCHMARK_PROFILE.json"
)

ACTIVE_IN_PATH = "ACTIVE_IN_PATH"
NOT_APPLICABLE = "NOT_APPLICABLE"
EXPLICITLY_SUPERSEDED = "EXPLICITLY_SUPERSEDED"
OPTIONAL_AVAILABLE = "OPTIONAL_AVAILABLE"
ACCEPTED_STATES = frozenset(
    {ACTIVE_IN_PATH, NOT_APPLICABLE, EXPLICITLY_SUPERSEDED}
)

# These are semantic/reference comparison controls, not runtime optimization
# stages that every production operation is expected to traverse.
REFERENCE_COMPARISON_CLASSES = frozenset({"dense_reference", "exact_integer_reference"})


class HHSCumulativeExecutionAuthorityError(RuntimeError):
    """Raised when inherited execution-authority utilization is not proven."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise HHSCumulativeExecutionAuthorityError(
            "REJECT_FLOAT_IN_CUMULATIVE_EXECUTION_AUTHORITY"
        )
    if isinstance(value, Mapping):
        for child in value.values():
            _reject_float(child)
    elif isinstance(value, (list, tuple, set, frozenset)):
        for child in value:
            _reject_float(child)


def _contains_forbidden_optional_available(value: Any) -> bool:
    if value == OPTIONAL_AVAILABLE:
        return True
    if isinstance(value, Mapping):
        return any(
            _contains_forbidden_optional_available(key)
            or _contains_forbidden_optional_available(child)
            for key, child in value.items()
        )
    if isinstance(value, (list, tuple, set, frozenset)):
        return any(_contains_forbidden_optional_available(child) for child in value)
    return False


def _profile_path(profile_path: Optional[Path | str] = None) -> Path:
    return Path(profile_path).resolve() if profile_path is not None else PROFILE_PATH


def load_inherited_core_authorities(
    profile_path: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """Load REQUIRED runtime optimization classes from the frozen Pass 215 profile."""

    path = _profile_path(profile_path)
    raw = path.read_bytes()
    profile = json.loads(raw.decode("utf-8"))
    _reject_float(profile)
    if profile.get("schema") != PROFILE_SCHEMA:
        raise HHSCumulativeExecutionAuthorityError(
            "REJECT_PASS215_OPTIMIZATION_PROFILE_SCHEMA"
        )
    classes = profile.get("optimization_classes")
    if not isinstance(classes, Mapping) or not classes:
        raise HHSCumulativeExecutionAuthorityError(
            "REJECT_PASS215_OPTIMIZATION_CLASSES_MISSING"
        )

    required = sorted(
        str(authority_id)
        for authority_id, disposition in classes.items()
        if disposition == "REQUIRED"
        and authority_id not in REFERENCE_COMPARISON_CLASSES
    )
    if not required:
        raise HHSCumulativeExecutionAuthorityError(
            "REJECT_INHERITED_CORE_AUTHORITY_SET_EMPTY"
        )

    authorities = [
        {
            "authority_id": authority_id,
            "source_profile_class": "REQUIRED",
            "source_profile_pass": PROFILE_SOURCE_PASS,
            "runtime_utilization_required": True,
        }
        for authority_id in required
    ]
    payload = {
        "schema": "HHS_INHERITED_CORE_EXECUTION_AUTHORITY_INVENTORY_V1",
        "version": VERSION,
        "source_profile_schema": PROFILE_SCHEMA,
        "source_profile_path": str(path.relative_to(path.parents[2]))
        if len(path.parents) >= 3
        else path.name,
        "source_profile_sha256": sha256(raw).hexdigest(),
        "authority_count": len(authorities),
        "authorities": authorities,
        "reference_comparison_classes_excluded": sorted(
            REFERENCE_COMPARISON_CLASSES
        ),
        "optional_profile_classes_promoted_to_core": False,
        "experimental_profile_classes_promoted_to_core": False,
    }
    witness = make_hash72_kernel_witness(
        "HHS_INHERITED_CORE_EXECUTION_AUTHORITY_INVENTORY_V1",
        payload,
        width=72,
    )
    payload["inventory_root_hash72"] = witness.digest
    return payload


def _normalize_authority_ids(
    required_authorities: Optional[Iterable[str | Mapping[str, Any]]] = None,
) -> tuple[str, ...]:
    if required_authorities is None:
        inventory = load_inherited_core_authorities()
        return tuple(
            row["authority_id"] for row in inventory.get("authorities", [])
        )
    out = []
    for row in required_authorities:
        authority_id = (
            str(row.get("authority_id"))
            if isinstance(row, Mapping)
            else str(row)
        ).strip()
        if authority_id:
            out.append(authority_id)
    return tuple(sorted(dict.fromkeys(out)))


def _active_decision(authority_id: str, proof: Mapping[str, Any]) -> Dict[str, Any]:
    path = list(proof.get("path") or [])
    witness = proof.get("traversal_witness")
    root = str(proof.get("witness_root") or "").strip()
    observed = proof.get("observed") is True
    reasons = []
    if not observed:
        reasons.append("REJECT_ACTIVE_AUTHORITY_NOT_OBSERVED")
    if not path or authority_id not in path:
        reasons.append("REJECT_ACTIVE_AUTHORITY_PATH_MISSING_AUTHORITY")
    if not isinstance(witness, Mapping) or not witness:
        reasons.append("REJECT_ACTIVE_AUTHORITY_TRAVERSAL_WITNESS_MISSING")
    if not root:
        reasons.append("REJECT_ACTIVE_AUTHORITY_WITNESS_ROOT_MISSING")
    return {
        "authority_id": authority_id,
        "state": ACTIVE_IN_PATH if not reasons else None,
        "accepted": not reasons,
        "proof": dict(proof),
        "reasons": reasons,
    }


def _not_applicable_decision(
    authority_id: str,
    proof: Mapping[str, Any],
) -> Dict[str, Any]:
    predicate = str(proof.get("predicate") or "").strip()
    facts = proof.get("observed_facts")
    reason = str(proof.get("reason") or "").strip()
    mechanical = proof.get("mechanically_proven") is True
    reasons = []
    if not mechanical:
        reasons.append("REJECT_NOT_APPLICABLE_NOT_MECHANICALLY_PROVEN")
    if not predicate:
        reasons.append("REJECT_NOT_APPLICABLE_PREDICATE_MISSING")
    if not isinstance(facts, Mapping) or not facts:
        reasons.append("REJECT_NOT_APPLICABLE_OBSERVED_FACTS_MISSING")
    if not reason:
        reasons.append("REJECT_NOT_APPLICABLE_REASON_MISSING")
    return {
        "authority_id": authority_id,
        "state": NOT_APPLICABLE if not reasons else None,
        "accepted": not reasons,
        "proof": dict(proof),
        "reasons": reasons,
    }


def _superseded_decision(
    authority_id: str,
    proof: Mapping[str, Any],
) -> Dict[str, Any]:
    later_pass = proof.get("later_pass")
    replacement = str(proof.get("replacement_authority") or "").strip()
    validation_root = str(proof.get("validation_root") or "").strip()
    explicit_contract = str(proof.get("explicit_contract") or "").strip()
    equality = proof.get("semantic_equality_proven") is True
    reasons = []
    if not isinstance(later_pass, int) or isinstance(later_pass, bool):
        reasons.append("REJECT_SUPERSESSION_LATER_PASS_INVALID")
    elif later_pass <= PROFILE_SOURCE_PASS:
        reasons.append("REJECT_SUPERSESSION_NOT_LATER_THAN_INHERITED_PROFILE")
    if not replacement or replacement == authority_id:
        reasons.append("REJECT_SUPERSESSION_REPLACEMENT_INVALID")
    if not validation_root:
        reasons.append("REJECT_SUPERSESSION_VALIDATION_ROOT_MISSING")
    if not explicit_contract:
        reasons.append("REJECT_SUPERSESSION_EXPLICIT_CONTRACT_MISSING")
    if not equality:
        reasons.append("REJECT_SUPERSESSION_SEMANTIC_EQUALITY_UNPROVEN")
    return {
        "authority_id": authority_id,
        "state": EXPLICITLY_SUPERSEDED if not reasons else None,
        "accepted": not reasons,
        "proof": dict(proof),
        "reasons": reasons,
    }


def build_authority_reachability(
    operation_id: str,
    *,
    active_in_path: Optional[Mapping[str, Mapping[str, Any]]] = None,
    not_applicable: Optional[Mapping[str, Mapping[str, Any]]] = None,
    explicitly_superseded: Optional[Mapping[str, Mapping[str, Any]]] = None,
    required_authorities: Optional[Iterable[str | Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    """Build a fail-closed per-operation inherited-authority utilization record."""

    active = dict(active_in_path or {})
    irrelevant = dict(not_applicable or {})
    superseded = dict(explicitly_superseded or {})
    _reject_float({"active": active, "irrelevant": irrelevant, "superseded": superseded})
    if _contains_forbidden_optional_available(
        {"active": active, "irrelevant": irrelevant, "superseded": superseded}
    ):
        raise HHSCumulativeExecutionAuthorityError(
            "REJECT_OPTIONAL_AVAILABLE_IN_INHERITED_CORE_EXECUTION_PATH"
        )

    authority_ids = _normalize_authority_ids(required_authorities)
    decisions = []
    blockers = []
    for authority_id in authority_ids:
        present = [
            name
            for name, mapping in (
                (ACTIVE_IN_PATH, active),
                (NOT_APPLICABLE, irrelevant),
                (EXPLICITLY_SUPERSEDED, superseded),
            )
            if authority_id in mapping
        ]
        if len(present) == 0:
            decision = {
                "authority_id": authority_id,
                "state": None,
                "accepted": False,
                "proof": {},
                "reasons": ["REJECT_INHERITED_AUTHORITY_DISPOSITION_MISSING"],
            }
        elif len(present) > 1:
            decision = {
                "authority_id": authority_id,
                "state": None,
                "accepted": False,
                "proof": {},
                "reasons": ["REJECT_INHERITED_AUTHORITY_DISPOSITION_AMBIGUOUS"],
            }
        elif present[0] == ACTIVE_IN_PATH:
            decision = _active_decision(authority_id, active[authority_id])
        elif present[0] == NOT_APPLICABLE:
            decision = _not_applicable_decision(
                authority_id, irrelevant[authority_id]
            )
        else:
            decision = _superseded_decision(
                authority_id, superseded[authority_id]
            )
        decisions.append(decision)
        blockers.extend(
            f"{authority_id}:{reason}" for reason in decision.get("reasons", [])
        )

    unknown = sorted(
        (set(active) | set(irrelevant) | set(superseded)) - set(authority_ids)
    )
    blockers.extend(f"{authority_id}:REJECT_UNKNOWN_CORE_AUTHORITY" for authority_id in unknown)

    accepted_counts = {
        state: sum(1 for row in decisions if row.get("state") == state)
        for state in sorted(ACCEPTED_STATES)
    }
    admitted = not blockers and len(decisions) == len(authority_ids)
    body = {
        "schema": SCHEMA,
        "version": VERSION,
        "operation_id": str(operation_id),
        "required_authority_count": len(authority_ids),
        "decisions": decisions,
        "accepted_state_counts": accepted_counts,
        "unknown_authority_ids": unknown,
        "optional_available_forbidden": True,
        "all_required_authorities_disposed": admitted,
        "admitted": admitted,
        "status": (
            "ADMIT_CUMULATIVE_INHERITED_EXECUTION_PATH"
            if admitted
            else "REJECT_CUMULATIVE_INHERITED_EXECUTION_PATH"
        ),
        "blockers": sorted(dict.fromkeys(blockers)),
    }
    witness = make_hash72_kernel_witness(
        "HHS_CUMULATIVE_EXECUTION_AUTHORITY_REACHABILITY_V1",
        body,
        width=72,
    )
    body["reachability_root_hash72"] = witness.digest
    body["hash72_kernel_witness"] = witness.to_dict()
    return body


def validate_authority_reachability(record: Mapping[str, Any]) -> Dict[str, Any]:
    """Independently validate that the record contains no fourth accepted state."""

    _reject_float(record)
    reasons = []
    if record.get("schema") != SCHEMA:
        reasons.append("REJECT_CUMULATIVE_AUTHORITY_SCHEMA")
    if _contains_forbidden_optional_available(record):
        reasons.append("REJECT_OPTIONAL_AVAILABLE_IN_INHERITED_CORE_EXECUTION_PATH")
    decisions = record.get("decisions")
    if not isinstance(decisions, Sequence) or isinstance(decisions, (str, bytes)):
        reasons.append("REJECT_CUMULATIVE_AUTHORITY_DECISIONS_MISSING")
        decisions = []
    seen = set()
    for row in decisions:
        if not isinstance(row, Mapping):
            reasons.append("REJECT_CUMULATIVE_AUTHORITY_DECISION_NOT_MAPPING")
            continue
        authority_id = str(row.get("authority_id") or "")
        if not authority_id:
            reasons.append("REJECT_CUMULATIVE_AUTHORITY_ID_MISSING")
        elif authority_id in seen:
            reasons.append(f"REJECT_DUPLICATE_CUMULATIVE_AUTHORITY:{authority_id}")
        seen.add(authority_id)
        state = row.get("state")
        if state not in ACCEPTED_STATES:
            reasons.append(
                f"REJECT_UNPROVEN_CUMULATIVE_AUTHORITY_STATE:{authority_id}:{state}"
            )
        if row.get("accepted") is not True:
            reasons.append(f"REJECT_CUMULATIVE_AUTHORITY_NOT_ACCEPTED:{authority_id}")
    required_count = record.get("required_authority_count")
    if not isinstance(required_count, int) or isinstance(required_count, bool):
        reasons.append("REJECT_REQUIRED_AUTHORITY_COUNT_INVALID")
    elif required_count != len(decisions):
        reasons.append("REJECT_REQUIRED_AUTHORITY_COUNT_MISMATCH")
    if record.get("all_required_authorities_disposed") is not True:
        reasons.append("REJECT_REQUIRED_AUTHORITY_COVERAGE_INCOMPLETE")
    if record.get("admitted") is not True:
        reasons.append("REJECT_CUMULATIVE_EXECUTION_PATH_NOT_ADMITTED")
    return {
        "schema": DECISION_SCHEMA,
        "version": VERSION,
        "ok": not reasons,
        "status": (
            "ADMIT_CUMULATIVE_EXECUTION_AUTHORITY_RECORD"
            if not reasons
            else "REJECT_CUMULATIVE_EXECUTION_AUTHORITY_RECORD"
        ),
        "operation_id": record.get("operation_id"),
        "reachability_root_hash72": record.get("reachability_root_hash72"),
        "reasons": sorted(dict.fromkeys(reasons)),
    }


def assert_authority_reachability(record: Mapping[str, Any]) -> Mapping[str, Any]:
    decision = validate_authority_reachability(record)
    if not decision.get("ok"):
        raise HHSCumulativeExecutionAuthorityError(
            "CUMULATIVE_EXECUTION_AUTHORITY_REJECTED:"
            + "|".join(decision.get("reasons", []))
        )
    return record


def cumulative_execution_authority_self_test() -> Dict[str, Any]:
    required = ("conformance_decision_cache", "predictive_continuation_cache")
    active = {
        "conformance_decision_cache": {
            "observed": True,
            "path": ["kernel_runtime_autocomposer", "conformance_decision_cache"],
            "traversal_witness": {"cache_hit": True},
            "witness_root": "self-test-conformance-cache-root",
        }
    }
    irrelevant = {
        "predictive_continuation_cache": {
            "mechanically_proven": True,
            "predicate": "operation_has_predecessor_state == false",
            "observed_facts": {"operation_has_predecessor_state": False},
            "reason": "no predecessor state exists for this self-test operation",
        }
    }
    record = build_authority_reachability(
        "self_test",
        active_in_path=active,
        not_applicable=irrelevant,
        required_authorities=required,
    )
    decision = validate_authority_reachability(record)
    missing = build_authority_reachability(
        "missing_test",
        active_in_path=active,
        required_authorities=required,
    )
    return {
        "schema": "HHS_CUMULATIVE_EXECUTION_AUTHORITY_SELF_TEST_V1",
        "version": VERSION,
        "ok": decision.get("ok") is True and missing.get("admitted") is False,
        "admitted": record,
        "decision": decision,
        "missing_rejected": missing,
    }


if __name__ == "__main__":
    print(cumulative_execution_authority_self_test())
