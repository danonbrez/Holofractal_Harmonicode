"""Pass 220 V164: execute inherited Pass219 native C HNAN 1.63 gates.

Only checks the scoped native relation graph against a V160-audited Module 194
source. This does NOT verify the 81-address fractalization equivalence or
the broken frozen-course provenance, nor does it authorize physics mutation.
"""
from __future__ import annotations

import ctypes as C
from typing import Any

from hhs_runtime.hhs_pass220_v160_module194_source_address_preflight_v1 import audit_source
from hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1 import (
    GlobalReceipt, Claim, Resolution, VERSION, MASK,
)

SCHEMA = "HHS_PASS_220_V164_MODULE194_INHERITED_NATIVE_HNAN_163_V1"
CLAIMS = ((10, 15, 16, 7), (11, 17, 16, 8), (12, 18, 19, 9),
          (13, 20, 21, 9))


class V164NativeHNANError(ValueError):
    pass


def execute_module194_native_hnan_scope(
    source: bytes, native_library: Any, *, require_upload_identity: bool = True,
) -> dict:
    """Call existing C ABI; require its actual verified typed decisions."""
    audited = audit_source(source, require_upload_identity=require_upload_identity)
    if native_library is None:
        raise V164NativeHNANError("V164_NATIVE_LIBRARY_REQUIRED")
    try:
        version = native_library.hhs_exact_pass219_hnan_global_version
        version.argtypes = []
        version.restype = C.c_uint32
        global_verify = native_library.hhs_exact_pass219_hnan_global_system_verify
        global_verify.argtypes = [C.POINTER(GlobalReceipt)]
        global_verify.restype = C.c_int
        resolve = native_library.hhs_exact_pass219_hnan_resolve
        resolve.argtypes = [C.POINTER(Claim), C.POINTER(Resolution)]
        resolve.restype = C.c_int
        if version() != VERSION:
            raise V164NativeHNANError("V164_NATIVE_ABI_VERSION")
        global_receipt = GlobalReceipt()
        global_receipt.struct_size = C.sizeof(GlobalReceipt)
        status = global_verify(C.byref(global_receipt))
        flags = (
            "jordan_depth2_verified", "minimal_polynomial_degree4_verified",
            "degree4_recurrence_verified", "hnan_channel_order_preserved",
            "ordered_zero_closure_preserved", "global_delta_denominator_preserved",
            "delta_cancellation_forbidden", "xy_yx_distinct", "zw_wz_distinct",
        )
        if (status != 0 or global_receipt.version != VERSION
                or global_receipt.decision != 1
                or global_receipt.required_rule_mask != MASK
                or global_receipt.verified_rule_mask != MASK
                or any(getattr(global_receipt, key) != 1 for key in flags)
                or global_receipt.candidate_only != 1
                or any(getattr(global_receipt, key) for key in (
                    "canonical_vm81_mutation_authority",
                    "canonical_hash72_authority", "canonical_hash216_authority",
                    "floating_point_canonical_authority"))):
            raise V164NativeHNANError("V164_NATIVE_GLOBAL_GATE_REJECTED")
        resolved = []
        for rule_id, lhs, rhs, relation in CLAIMS:
            claim = Claim()
            claim.struct_size = C.sizeof(Claim)
            claim.version = VERSION
            claim.rule_id, claim.lhs_node = rule_id, lhs
            claim.rhs_node, claim.relation = rhs, relation
            claim.source_order_preserved = 1
            claim.typed_identity_preserved = 1
            decision = Resolution()
            decision.struct_size = C.sizeof(Resolution)
            if (resolve(C.byref(claim), C.byref(decision)) != 0
                    or decision.decision != 1 or decision.reason != 0
                    or (decision.rule_id, decision.lhs_node, decision.rhs_node,
                        decision.relation) != (rule_id, lhs, rhs, relation)
                    or decision.exact_rule_match != 1
                    or decision.source_order_preserved != 1
                    or decision.typed_identity_preserved != 1
                    or any(getattr(decision, key) for key in (
                        "scalar_substitution_authority",
                        "commutation_authority", "delta_cancellation_authority",
                        "emptyset_cancellation_authority",
                        "equality_reversal_authority"))):
                raise V164NativeHNANError(f"V164_NATIVE_ORDERED_RULE_{rule_id}_REJECTED")
            resolved.append(rule_id)
    except (AttributeError, TypeError, OSError) as exc:
        raise V164NativeHNANError("V164_NATIVE_ABI_UNAVAILABLE") from exc
    return {
        "schema": SCHEMA,
        "module194_source_sha256": audited["source_sha256"],
        "module194_groups": audited["groups"],
        "module194_reciprocal_pairs": audited["reciprocal_pairs"],
        "native_hnan_system_signature64": str(global_receipt.system_signature64),
        "native_mandatory_rule_mask": global_receipt.verified_rule_mask,
        "native_ordered_hnan_rule_ids_verified": resolved,
        "native_inherited_global_hnan_gate_executed": True,
        "module194_81_tensor_native_equivalence_verified": False,
        "course_source_freeze_verified": False,
        "course_module4_full_proof_executed": False,
        "module194_physical_producer_verified": False,
        "lean_module194_checker_executed": False,
        "canonical_vm81_admission": False,
        "hash72_hash216_minted": False,
    }
