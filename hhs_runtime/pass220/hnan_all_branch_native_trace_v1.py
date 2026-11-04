"""All-branch, candidate-only trace over the inherited native HNAN 1.63 ABI.

Unlike the first-failure aggregate ABI, this inspector independently invokes
the existing native per-claim resolver for every supplied ordered branch. It
does NOT change acceptance, prove cross-branch consensus, or mint VM81 state.
"""
from __future__ import annotations

import ctypes as C
from hashlib import sha256
import json
from pathlib import Path
from typing import Mapping, Sequence

from hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1 import (
    Claim, Resolution, GlobalReceipt, VERSION, MASK,
)

SCHEMA = "HHS_PASS220_HNAN_ALL_BRANCH_NATIVE_TRACE_V1"
DECISIONS = {1: "VERIFIED", 2: "REJECTED", 3: "UNRESOLVED"}
FIELDS = ("rule_id", "lhs_node", "rhs_node", "relation")
FLAGS = (
    "source_order_preserved", "typed_identity_preserved",
    "scalar_substitution_requested", "delta_cancellation_requested",
    "floating_infinity_requested", "commutation_requested",
    "emptyset_cancellation_requested", "equality_reversal_requested",
)


class NativeBranchTraceRejected(ValueError):
    pass


def _exact_uint32(value: object, key: str) -> int:
    if type(value) is not int or value < 0 or value > 0xFFFFFFFF:
        raise NativeBranchTraceRejected(f"INVALID_UINT32_{key}")
    return value


def _branch_claim(row: Mapping[str, object]) -> Claim:
    if not isinstance(row, Mapping) or set(row) != set(FIELDS) | set(FLAGS):
        raise NativeBranchTraceRejected("BRANCH_CLAIM_SHAPE")
    claim = Claim()
    claim.struct_size = C.sizeof(Claim)
    claim.version = VERSION
    for key in FIELDS:
        setattr(claim, key, _exact_uint32(row[key], key))
    for key in FLAGS:
        value = _exact_uint32(row[key], key)
        if value > 1:
            raise NativeBranchTraceRejected(f"INVALID_FLAG_{key}")
        setattr(claim, key, value)
    return claim


def inspect_all_native_hnan_branches(
    branches: Sequence[Mapping[str, object]], *, native_library: str,
    parent_receipt_hash72: str, parent_root216: str,
) -> dict:
    """Return all indexed native verdicts without selecting a favored Tensor.

    Each branch must include: unique 'branch_id', source-preserving 'tensor'
    string, and one existing ABI 'claim' structure as a mapping. Branch IDs
    and source strings are evidence carriers, not canonical state identifiers.
    """
    if not isinstance(branches, (tuple, list)) or not branches:
        raise NativeBranchTraceRejected("BRANCHES_REQUIRED")
    if not isinstance(parent_receipt_hash72, str) or len(parent_receipt_hash72) != 72:
        raise NativeBranchTraceRejected("PARENT_RECEIPT_REQUIRED")
    if not isinstance(parent_root216, str) or len(parent_root216) != 216:
        raise NativeBranchTraceRejected("PARENT_ROOT216_REQUIRED")
    if not isinstance(native_library, str) or not Path(native_library).is_file():
        raise NativeBranchTraceRejected("EXISTING_NATIVE_HNAN_LIBRARY_REQUIRED")

    prepared = []
    seen = set()
    for index, branch in enumerate(branches):
        if not isinstance(branch, Mapping) or set(branch) != {"branch_id", "tensor", "claim"}:
            raise NativeBranchTraceRejected("BRANCH_RECORD_SHAPE")
        identifier, tensor = branch["branch_id"], branch["tensor"]
        if not isinstance(identifier, str) or not identifier or identifier in seen:
            raise NativeBranchTraceRejected("DUPLICATE_OR_EMPTY_BRANCH_ID")
        if not isinstance(tensor, str) or not tensor:
            raise NativeBranchTraceRejected("TENSOR_SOURCE_REQUIRED")
        seen.add(identifier)
        prepared.append((index, identifier, tensor, _branch_claim(branch["claim"])))

    lib = C.CDLL(native_library)
    global_verify = lib.hhs_exact_pass219_hnan_global_system_verify
    global_verify.argtypes = [C.POINTER(GlobalReceipt)]
    global_verify.restype = C.c_int
    receipt = GlobalReceipt()
    receipt.struct_size = C.sizeof(GlobalReceipt)
    status = global_verify(C.byref(receipt))
    if (status != 0 or receipt.version != VERSION or receipt.decision != 1
        or receipt.required_rule_mask != MASK or receipt.verified_rule_mask != MASK
        or receipt.canonical_vm81_mutation_authority != 0
        or receipt.canonical_hash72_authority != 0
        or receipt.canonical_hash216_authority != 0):
        raise NativeBranchTraceRejected("HNAN_GLOBAL_PREFLIGHT_REJECTED")

    resolve = lib.hhs_exact_pass219_hnan_resolve
    resolve.argtypes = [C.POINTER(Claim), C.POINTER(Resolution)]
    resolve.restype = C.c_int
    rows = []
    for index, identifier, tensor, claim in prepared:
        output = Resolution()
        output.struct_size = C.sizeof(Resolution)
        status = resolve(C.byref(claim), C.byref(output))
        if status != 0 or output.decision not in DECISIONS:
            raise NativeBranchTraceRejected(f"NATIVE_BRANCH_ABI_FAILURE_{index}")
        if (output.rule_id, output.lhs_node, output.rhs_node, output.relation) != (
            claim.rule_id, claim.lhs_node, claim.rhs_node, claim.relation
        ):
            raise NativeBranchTraceRejected(f"NATIVE_BRANCH_IDENTITY_DRIFT_{index}")
        rows.append({
            "index": index, "branch_id": identifier,
            "source_utf8_sha256": sha256(tensor.encode("utf-8")).hexdigest(),
            "source_text": tensor,
            "native_rule_id": claim.rule_id,
            "native_lhs_node": claim.lhs_node,
            "native_rhs_node": claim.rhs_node,
            "native_relation": claim.relation,
            "decision": DECISIONS[output.decision],
            "native_reason_code": output.reason,
            "exact_rule_match": bool(output.exact_rule_match),
        })

    # A verified local rule is still only a candidate: no admission/commit.
    result = {
        "schema": SCHEMA,
        "parent_receipt_hash72": parent_receipt_hash72,
        "parent_root216": parent_root216,
        "native_global_signature64": str(receipt.system_signature64),
        "branch_count": len(rows),
        "branches": rows,
        "has_unresolved": any(x["decision"] == "UNRESOLVED" for x in rows),
        "has_rejected": any(x["decision"] == "REJECTED" for x in rows),
        "all_native_rules_verified": all(x["decision"] == "VERIFIED" for x in rows),
        "candidate_only": True,
        "cross_tensor_consensus_proved": False,
        "canonical_vm81_admission": False,
        "hash72_minted": False,
        "hash216_minted": False,
    }
    result["trace_sha256"] = sha256(json.dumps(
        result, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    return result
