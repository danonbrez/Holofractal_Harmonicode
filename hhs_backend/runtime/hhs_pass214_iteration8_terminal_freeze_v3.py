"""Pass 214 Iteration 8 terminal authority serialization repair v3.

V2 correctly minted the eight named terminal roots but its validator treated
Python mapping insertion order as an authority invariant. Repository JSON is
written with sorted keys, so a valid record could fail after serialization.
V3 canonicalizes the exact named root set into contract order before invoking
all v2 cryptographic and authority-boundary validation.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from hhs_backend.runtime import hhs_pass214_iteration8_terminal_freeze_v2 as _v2

PASS_NUMBER = _v2.PASS_NUMBER
ITERATION = _v2.ITERATION
SCHEMA = _v2.SCHEMA
INSPECTION_SCHEMA = _v2.INSPECTION_SCHEMA
PASS215_PROFILE_SCHEMA = _v2.PASS215_PROFILE_SCHEMA
CLASSIFICATION = _v2.CLASSIFICATION
BLOCKED_CLASSIFICATION = _v2.BLOCKED_CLASSIFICATION
AUTHORITY_SCOPE = _v2.AUTHORITY_SCOPE
GATE_PRESERVATION_SCHEMA = _v2.GATE_PRESERVATION_SCHEMA
PASS213_CLOSURE = _v2.PASS213_CLOSURE
ITERATION6_CANDIDATE_SET_ROOT = _v2.ITERATION6_CANDIDATE_SET_ROOT
TERMINAL_ROOT_NAMES = _v2.TERMINAL_ROOT_NAMES
REQUIRED_STAGES = _v2.REQUIRED_STAGES
MANDATORY_ABLATIONS = _v2.MANDATORY_ABLATIONS
REQUIRED_WORKLOAD_FAMILIES = _v2.REQUIRED_WORKLOAD_FAMILIES
REQUIRED_PASS215_COMPARISONS = _v2.REQUIRED_PASS215_COMPARISONS
ALLOWED_PROFILE_CLASSES = _v2.ALLOWED_PROFILE_CLASSES
PASS213_REQUIRED_AUTHORITIES = _v2.PASS213_REQUIRED_AUTHORITIES
Pass214Iteration8Error = _v2.Pass214Iteration8Error
canonical_bytes = _v2.canonical_bytes
hash216 = _v2.hash216
validate_benchmark_bundle = _v2.validate_benchmark_bundle
validate_pass215_profile = _v2.validate_pass215_profile
pass213_gate_preservation_record = _v2.pass213_gate_preservation_record
validate_pass213_gate_preservation = _v2.validate_pass213_gate_preservation
readiness_blockers = _v2.readiness_blockers
inspect_terminal_readiness = _v2.inspect_terminal_readiness
create_terminal_freeze = _v2.create_terminal_freeze


def validate_terminal_freeze(record: Mapping[str, Any]) -> bool:
    if not isinstance(record, Mapping):
        raise Pass214Iteration8Error("PASS214_I8_TERMINAL_RECORD_MAPPING_REQUIRED")
    normalized = deepcopy(dict(record))
    roots = normalized.get("terminal_roots")
    if not isinstance(roots, Mapping):
        raise Pass214Iteration8Error("PASS214_I8_TERMINAL_ROOTS_MAPPING_REQUIRED")
    if set(roots) != set(TERMINAL_ROOT_NAMES) or len(roots) != len(TERMINAL_ROOT_NAMES):
        raise Pass214Iteration8Error("PASS214_I8_TERMINAL_ROOT_SET_INVALID")
    normalized["terminal_roots"] = {
        name: roots[name] for name in TERMINAL_ROOT_NAMES
    }
    return _v2.validate_terminal_freeze(normalized)


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
