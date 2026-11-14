"""Pass 220 V167: Module194 typed closure packet and native forbidden-transform probes.

The 81-entry A=LHS fractalization tensor and B=RHS outer HNAN boundary
are DISTINCT typed entities even with the same P^2 magnitude. Native
Pass219 1.63 checks ordered phase *transport rules*; this does not assert
an input-specific proof of AB=P^4 or BA=-P^4.

No independent gate, hash receipt or VM81 mutation is constructed.
"""
from __future__ import annotations

import ctypes as C
from hashlib import sha256
import json
from typing import Any

from hhs_runtime.hhs_pass220_v166_module194_exact_polynomial_projection_v1 import (
    inspect_exact_projection,
)
from hhs_runtime.hhs_pass220_v165_module194_ordered_fractal_tensor_v1 import (
    flattened_source_tensor,
)
from hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1 import (
    Claim, Resolution, VERSION,
)

SCHEMA = "HHS_PASS220_V167_MODULE194_TYPED_CLOSURE_PACKET_V1"
# Original user-specified directed relations: statements are proof
# obligations, never scalar rewrite permissions or certified truths.
EXPECTED_RELATIONS = (
    ("TypedMagnitude", "A", "P^2"),
    ("TypedMagnitude", "B", "P^2"),
    ("OrderedNormalization", "A", "eM/Delta=P^2"),
    ("DistinctIdentity", "A", "B"),
    ("OrderedProduct", ("A", "B"), "+P^4"),
    ("OrderedProduct", ("B", "A"), "-P^4"),
    ("Primitive", "e", (0, 1)),
    ("Trinary", "phase", (-1, 0, 1)),
    ("Interior", "Deltae*A", "(-1,0,+1)*B/Delta=P^2/Delta"),
    ("InteriorRoot", "Deltae", "Sqrt(AB)"),
    ("OuterBoundary", "t^3-t-1", "Deltae=0"),
)
# Native rule 12 and 13 are noncommutative distinction rules; swapping
# source/target must not be accepted as an implied reverse equality.
PROBES = ((12, 18, 19, 9), (13, 20, 21, 9))


class V167TypedClosureError(ValueError):
    pass


def _digest(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode("utf-8")).hexdigest()


def typed_packet() -> dict:
    entries = flattened_source_tensor()
    if len(entries) != 81:
        raise V167TypedClosureError("V167_81_SOURCE_ADDRESS_REQUIRED")
    leaves = []
    for i, j, r, k, term in entries:
        address = (i, j, r, k)
        if any(type(v) is not int or not 0 <= v < 3 for v in address):
            raise V167TypedClosureError("V167_SOURCE_ADDRESS_RANGE")
        leaves.append(("A_LHS", address, term))
    if len({leaf[1] for leaf in leaves}) != 81:
        raise V167TypedClosureError("V167_DUPLICATE_SOURCE_ADDRESS")
    return {
        "A": ("TypedTensor", "A_LHS", tuple(leaves)),
        "B": ("TypedBoundary", "B_RHS",
              ("HNAN_Modulus",
               ("OrderedEquality", "0",
                ("List",
                 ("OrderedQuotient", "t^11", "a^2"),
                 ("OrderedQuotient", "t^8", ("OrderedProduct", "2", "a^2")),
                 ("OrderedQuotient", "t^9", "a^2"))))),
        "relations": EXPECTED_RELATIONS,
    }


def validate_packet(packet: dict) -> str:
    expected = typed_packet()
    if type(packet) is not dict or set(packet) != set(expected):
        raise V167TypedClosureError("V167_PACKET_SHAPE_REJECTED")
    if packet != expected:
        raise V167TypedClosureError("V167_TYPED_ORDER_OR_RELATION_DRIFT")
    # Different typed objects, independently retained, despite both
    # carrying the designated P^2 magnitude in the relation inventory.
    if packet["A"][1] == packet["B"][1]:
        raise V167TypedClosureError("V167_OPERAND_IDENTITY_COLLAPSE")
    return _digest(packet)


def _native_ordered_negative_probes(lib: C.CDLL) -> list[dict]:
    if not isinstance(lib, C.CDLL):
        raise V167TypedClosureError("V167_REAL_NATIVE_CDLL_REQUIRED")
    resolve = lib.hhs_exact_pass219_hnan_resolve
    resolve.argtypes = [C.POINTER(Claim), C.POINTER(Resolution)]
    resolve.restype = C.c_int
    output = []
    for rule, lhs, rhs, rel in PROBES:
        def execute(left: int, right: int, *, commutation: int = 0) -> int:
            c = Claim()
            c.struct_size = C.sizeof(Claim)
            c.version = VERSION
            c.rule_id, c.lhs_node, c.rhs_node, c.relation = rule, left, right, rel
            c.source_order_preserved, c.typed_identity_preserved = 1, 1
            c.commutation_requested = commutation
            d = Resolution()
            d.struct_size = C.sizeof(Resolution)
            if resolve(C.byref(c), C.byref(d)) != 0:
                raise V167TypedClosureError("V167_NATIVE_RESOLVE_CALL_FAILED")
            return int(d.decision)
        forward = execute(lhs, rhs)
        reversed_result = execute(rhs, lhs)
        commuted = execute(lhs, rhs, commutation=1)
        if forward != 1 or reversed_result == 1 or commuted == 1:
            raise V167TypedClosureError(f"V167_NATIVE_ORDER_GUARD_{rule}_FAILED")
        output.append({
            "rule_id": rule,
            "ordered_forward_verified": True,
            "reverse_not_accepted": True,
            "commutation_not_accepted": True,
            "reverse_decision": reversed_result,
            "commutation_decision": commuted,
        })
    return output


def inspect_typed_closure(source: bytes, native_library: C.CDLL, *,
                          require_upload_identity: bool = True) -> dict:
    inherited = inspect_exact_projection(
        source, native_library, require_upload_identity=require_upload_identity
    )
    if (inherited.get("exact_polynomial_projection_entries_verified") != 81
        or inherited.get("vm81_admission") is not False
        or inherited.get("native_ab_ba_closure_for_input_proved") is not False):
        raise V167TypedClosureError("V167_INHERITED_SCOPE_REJECTED")
    packet = typed_packet()
    digest = validate_packet(packet)
    native_probes = _native_ordered_negative_probes(native_library)
    return {
        "schema": SCHEMA,
        "module194_source_sha256": inherited["module194_source_sha256"],
        "ordered_tensor_ast_sha256": inherited["original_ordered_tensor_ast_sha256"],
        "exact_projection_sha256": inherited["exact_projection_coefficient_sha256"],
        "typed_packet_sha256": digest,
        "source_leaf_count": len(packet["A"][2]),
        "typed_operands_distinct": True,
        "ordered_relations_preserved": True,
        "native_order_guard_probes": native_probes,
        "native_inherited_hnan_signature64":
            inherited["inherited_native_hnan_system_signature64"],
        "input_specific_ab_ba_proof_executed": False,
        "hnan_interior_outer_closure_proof_executed": False,
        "complete_course_proof_binding_verified": False,
        "module194_force_equivalence_verified": False,
        "canonical_vm81_admission": False,
        "hash72_hash216_minted": False,
    }
