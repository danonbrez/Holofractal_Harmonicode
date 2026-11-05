"""Read-only Pass 205 lineage binding for inherited native HNAN branch traces.

This uses the already-authoritative continuation snapshot, verification, and
replay interfaces and the Pass 220 all-branch native ABI inspector. It does not
submit mutations or treat branch verdicts as a cross-tensor consensus proof.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from hhs_runtime.pass220.hnan_all_branch_native_trace_v1 import (
    inspect_all_native_hnan_branches,
)

SCHEMA = "HHS_PASS220_HNAN_PASS205_READONLY_LINEAGE_BINDING_V1"


class HNANContinuationBindingRejected(ValueError):
    pass


def bind_hnan_trace_to_pass205_parent(
    continuation_runtime: Any,
    branches: Sequence[Mapping[str, object]], *,
    parent_root216: str,
    expected_parent_receipt_hash72: str,
    native_library: str,
) -> dict:
    """Bind candidate branch verdicts to a *verified, replayed* Pass 205 parent.

    No Pass 205 advance/branch/admit call is permitted in this binding. Neither
    VERIFIED native rules nor a replayable parent imply cross-tensor closure.
    """
    if not isinstance(parent_root216, str) or len(parent_root216) != 216:
        raise HNANContinuationBindingRejected("PARENT_ROOT216_REQUIRED")
    if (not isinstance(expected_parent_receipt_hash72, str)
        or len(expected_parent_receipt_hash72) != 72):
        raise HNANContinuationBindingRejected("PARENT_HASH72_REQUIRED")

    # No fallback, synthetic root, or auto-creation of a committed parent.
    parent = continuation_runtime.snapshot(parent_root216, include_payloads=False)
    if (parent.get("continuation_root216") != parent_root216
        or parent.get("receipt_hash72") != expected_parent_receipt_hash72):
        raise HNANContinuationBindingRejected("PARENT_IDENTITY_OR_RECEIPT_MISMATCH")

    verification = continuation_runtime.verify(parent_root216)
    if (verification.get("ok") is not True
        or verification.get("continuation_root216") != parent_root216):
        raise HNANContinuationBindingRejected("PARENT_NATIVE_VERIFICATION_REQUIRED")

    replay = continuation_runtime.replay(parent_root216)
    roots = replay.get("ordered_roots216")
    receipts = replay.get("ordered_receipts_hash72")
    if (replay.get("ok") is not True
        or replay.get("target_root216") != parent_root216
        or not isinstance(roots, list) or not roots
        or roots[-1] != parent_root216
        or not isinstance(receipts, list) or len(receipts) != len(roots)
        or receipts[-1] != expected_parent_receipt_hash72):
        raise HNANContinuationBindingRejected("PARENT_REPLAY_REQUIRED")

    trace = inspect_all_native_hnan_branches(
        branches,
        native_library=native_library,
        parent_root216=parent_root216,
        parent_receipt_hash72=expected_parent_receipt_hash72,
    )
    if (trace.get("parent_root216") != parent_root216
        or trace.get("parent_receipt_hash72") != expected_parent_receipt_hash72
        or trace.get("candidate_only") is not True
        or trace.get("canonical_vm81_admission") is not False
        or trace.get("hash72_minted") is not False
        or trace.get("hash216_minted") is not False):
        raise HNANContinuationBindingRejected("CANDIDATE_TRACE_AUTHORITY_OR_PARENT_DRIFT")

    result = {
        "schema": SCHEMA,
        "parent_root216": parent_root216,
        "parent_receipt_hash72": expected_parent_receipt_hash72,
        "parent_constraint_root216": parent.get("constraint_root216"),
        "parent_schema_root216": parent.get("schema_root216"),
        "parent_verified": True,
        "parent_replay_verified": True,
        "parent_replay_generation_count": len(roots),
        "parent_replay_terminal_root216": roots[-1],
        "branch_trace_sha256": trace["trace_sha256"],
        "native_global_signature64": trace["native_global_signature64"],
        "branches": trace["branches"],
        "branch_count": trace["branch_count"],
        "has_rejected": trace["has_rejected"],
        "has_unresolved": trace["has_unresolved"],
        "all_native_rules_verified": trace["all_native_rules_verified"],
        "candidate_only": True,
        "cross_tensor_consensus_proved": False,
        "pass205_continuation_created": False,
        "canonical_vm81_admission": False,
        "hash72_minted": False,
        "hash216_minted": False,
    }
    result["binding_sha256"] = sha256(json.dumps(
        result, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")).hexdigest()
    return result
