"""I088/I089 guarded successor proof projection over inherited Pass 219 exact witness.

Only a candidate constraint-fold input. Native C++ stage execution, complete
global proof admission, VM81 mutation and persisted Hash216 remain inherited
authorities; neither is synthesized by this adapter.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_runtime.pass219_native_universal_constraint_v1 import (
    build_integer_symmetric_witness,
)


class I088UnprovenClosure(ValueError):
    pass


SCHEMA = "HHS_PASS220_I088_I089_GUARDED_SUCCESSOR_PROOF_REUSE_V1"


def _digest(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def prepare_successor_constraint_witness(
    *, P: int, inherited_proof_sha256: str, required_constraints: tuple[str, ...]
) -> dict[str, Any]:
    """Capture exact known successor and ordered obligations, not a closure receipt."""
    if type(P) is not int or P < 4 or P % 2:
        raise I088UnprovenClosure("inherited positive odd p/q projection requires even P >= 4")
    if (not isinstance(inherited_proof_sha256, str)
        or len(inherited_proof_sha256) != 64
        or any(c not in "0123456789abcdef" for c in inherited_proof_sha256)):
        raise I088UnprovenClosure("exact inherited proof root required")
    if (type(required_constraints) is not tuple or not required_constraints
        or any(not isinstance(c, str) or not c for c in required_constraints)
        or len(set(required_constraints)) != len(required_constraints)):
        raise I088UnprovenClosure("unique ordered applicable constraints required")
    p, q = P - 1, P + 1
    native = build_integer_symmetric_witness(P, p, q)
    if not native.exact_core_valid():
        raise I088UnprovenClosure("inherited exact UCE core failed")
    result = {
        "schema": SCHEMA,
        "P": P, "p": p, "q": q,
        "inherited_proof_sha256": inherited_proof_sha256,
        "ordered_required_constraints": required_constraints,
        "inherited_exact_core": asdict(native),
        "unresolved_symbolic_obligations": native.symbolic_residuals,
        "fold_executed": False,
        "all_global_constraints_proven": False,
        "vm81_admitted": False,
        "hash216_minted": False,
        "persistent_reuse_authorized": False,
        "candidate_only": True,
    }
    result["witness_sha256"] = _digest(result)
    return result


def require_globally_admitted_reuse(candidate: Mapping[str, Any]) -> None:
    """Fail closed until inherited trusted native fold and admission are verified."""
    if not isinstance(candidate, Mapping):
        raise I088UnprovenClosure("candidate must be an inherited witness")
    if candidate.get("schema") != SCHEMA:
        raise I088UnprovenClosure("candidate schema mismatch")
    if candidate.get("witness_sha256") != _digest({
        key: value for key, value in candidate.items() if key != "witness_sha256"
    }):
        raise I088UnprovenClosure("candidate witness drift")
    raise I088UnprovenClosure("trusted native global fold and VM81 admission required")
