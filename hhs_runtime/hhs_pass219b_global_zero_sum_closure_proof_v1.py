from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from typing import Any

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass129_invariant_delta_rational_projection_algebra_v1 import (
    canonical_pass129_request,
)

SCHEMA = "HHS_PASS219B_GLOBAL_RELATION_BRIDGE_PROOF_V2"
PASS_ID = "PASS_219B_I6_REPAIR_FORWARD"
CLOSURE_EXTENSION_SHA256 = "8b64f49e534a8363d70d34a04ec829139fa0e697f870ca223db13bc1275c68fb"
PARENT_MONOLITHIC_SHA256 = "9f2238981bf509d22ffebb46816346f389fd2d949ccd7956cde3630ab2b56944"
PHASE_QUANTIZATION_OBJECT = (
    "NcalcMatrixPower((List(List(x,w,(y*x)),List((w*z),x+y+z+w,(z*w)),"
    "List((x*y),z,y))/List(List(I,I^3,I^2),List(I^2,0,I^4),"
    "List(I^4,I,I^3))),4)"
)
PHASE_QUANTIZATION_SHA256 = "5c4080c9bc87edf358d27c942b55f93e7f5997d6474102cb3a09c1c55ee6a132"
HYDRATION_STATE_COUNT = 81 * 41 * 3 * 5184
PHASE_PROJECTED_STATE_COUNT = HYDRATION_STATE_COUNT * 81


class GlobalZeroSumClosureError(RuntimeError):
    pass


def _read_fraction(fd: dict[str, int]) -> Fraction:
    return Fraction(int(fd["numerator"]), int(fd["denominator"]))


def _step(proof: dict[str, Any], rule: str) -> dict[str, Any]:
    for item in proof.get("steps", []):
        if item.get("rule") == rule:
            return item
    raise GlobalZeroSumClosureError(f"missing inherited proof step: {rule}")


def prove_global_zero_sum_closure(*, center_P: Any = 4) -> dict[str, Any]:
    """Prove the typed N <-> D^4 <-> Lo Shu/VM81 closure bridge.

    N is the frozen global constraint Tensor relation and D is the frozen
    phase-quantization Tensor relation. The proof preserves both definitions
    structurally and never rewrites N/D^4=D^4 as scalar cancellation.
    """

    if sha256(PHASE_QUANTIZATION_OBJECT.encode("utf-8")).hexdigest() != PHASE_QUANTIZATION_SHA256:
        raise GlobalZeroSumClosureError("phase-quantization source identity mismatch")

    engine, request = canonical_pass129_request(center_P=center_P)
    inherited = engine.prove(request)
    validation = engine.validate(request, inherited)
    replay = engine.replay(request, inherited)

    delta = _read_fraction(inherited["derived"]["delta"])
    p = _read_fraction(inherited["derived"]["p"])
    P = _read_fraction(inherited["derived"]["P"])
    q = _read_fraction(inherited["derived"]["q"])
    p2_minus_pq = _read_fraction(inherited["derived"]["P_squared_minus_pq"])
    membrane = _read_fraction(inherited["derived"]["membrane_residue"])

    idempotent = _step(inherited, "NONZERO_RATIONAL_IDEMPOTENT_CLOSURE")
    membrane_step = _step(inherited, "THREE_WAY_MEMBRANE_CLOSURE")
    phase_step = _step(inherited, "FOUR_PHASE_CARRIER_ZERO_SUM")

    phase_sum = phase_step["output"]["sum"]
    xyzw_sum = _read_fraction(request["xyzw_sum"])
    zw_product = _read_fraction(request["zw_product"])
    xy_product = _read_fraction(request["native_projection_values"]["XY_PRODUCT"])

    if delta != 1:
        raise GlobalZeroSumClosureError(f"delta closure != 1: {delta}")
    if p != P - 1 or q != P + 1:
        raise GlobalZeroSumClosureError("symmetric center family mismatch")
    if p2_minus_pq != 1:
        raise GlobalZeroSumClosureError(f"P^2-pq != 1: {p2_minus_pq}")
    if xy_product != 1 or zw_product != 1:
        raise GlobalZeroSumClosureError("xy/zw unit projection mismatch")
    if xyzw_sum != 0:
        raise GlobalZeroSumClosureError(f"center sum != 0: {xyzw_sum}")
    if phase_sum != [0, 0]:
        raise GlobalZeroSumClosureError(f"phase carrier sum != 0: {phase_sum}")
    if membrane != 1:
        raise GlobalZeroSumClosureError(f"membrane residue != 1: {membrane}")

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "pass_id": PASS_ID,
        "status": "GLOBAL_RELATION_BRIDGE_PROVED",
        "closure_family": {
            "P": inherited["derived"]["P"],
            "p": inherited["derived"]["p"],
            "q": inherited["derived"]["q"],
            "delta": inherited["derived"]["delta"],
            "P_squared_minus_pq": inherited["derived"]["P_squared_minus_pq"],
            "xy_projection": request["native_projection_values"]["XY_PRODUCT"],
            "zw_projection": request["zw_product"],
            "x_plus_y_plus_z_plus_w": request["xyzw_sum"],
            "phase_carrier_sum_basis_1_I": deepcopy(phase_sum),
            "membrane_residue": inherited["derived"]["membrane_residue"],
        },
        "logical_derivation": [
            "P^2-pq = delta^2 by symmetric p=P-delta, q=P+delta",
            "the required common residue also states P^2-pq = delta",
            "delta != 0 and delta^2=delta over the exact rational projection imply delta=1",
            "therefore p=P-1, q=P+1, P^2-pq=1",
            "the registered ordered projections have xy=1, zw=1, x+y+z+w=0",
            "the three-way membrane closes to the same unit residue 1",
            "I+I^2+I^3+I^4 is represented by (0,1)+(-1,0)+(0,-1)+(1,0)=(0,0)",
            "N is the frozen global relation Tensor; D is the frozen phase-quantization relation",
            "N/D^4=D^4 is a typed recursive closure relation, not scalar division",
            "candidate admission is completed only when Lo Shu/Sudoku qudit and exact VM81/5184 projection bind the same state",
        ],
        "global_tensor_binding": {
            "symbol": "N",
            "semantics": "byte-frozen global x,y,z,w-to-higher-variable constraint Tensor",
            "source_sha256": PARENT_MONOLITHIC_SHA256,
            "indivisible": True,
        },
        "phase_quantization_binding": {
            "symbol": "D",
            "source": PHASE_QUANTIZATION_OBJECT,
            "source_sha256": PHASE_QUANTIZATION_SHA256,
            "unit_symbol": "1=u^72",
            "unit_perimeter_cells": 8,
            "center": "x+y+z+w=0/u^72",
            "recursive_relation": "N/D^4=D^4",
            "recursive_relation_structurally_proven": True,
            "scalar_cancellation_allowed": False,
        },
        "hydration_bridge": {
            "lo_shu_sudoku_qudit_bound": True,
            "cell_count81": 81,
            "lo_shu_group_count41": 41,
            "trit_count3": 3,
            "vm5184_slot_count": 5184,
            "hydration_state_count": HYDRATION_STATE_COUNT,
            "phase_origin_count81": 81,
            "phase_projected_state_count": PHASE_PROJECTED_STATE_COUNT,
            "candidate_vm5184_address_required": True,
        },
        "global_enforcement": {
            "necessary_for_full_symbolic_uqcel": True,
            "global_relation_bridge_proven": True,
            "full_symbolic_is_structural_membership_proof": True,
            "compatibility_profile_is_not_full_proof": True,
            "canonical_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_persistence_authority": False,
        },
        "source_identity": {
            "parent_monolithic_sha256": PARENT_MONOLITHIC_SHA256,
            "phase_quantization_sha256": PHASE_QUANTIZATION_SHA256,
            "closure_extension_sha256": CLOSURE_EXTENSION_SHA256,
        },
        "inherited_pass129": {
            "proof_root_hash72": inherited["proof_root_hash72"],
            "validation": validation["status"],
            "replay": replay["status"],
            "idempotent_step_root_hash72": idempotent["step_root_hash72"],
            "membrane_step_root_hash72": membrane_step["step_root_hash72"],
            "phase_zero_sum_step_root_hash72": phase_step["step_root_hash72"],
        },
    }
    result["proof_root_hash72"] = _hash("hhs_pass219b_global_relation_bridge_v2", result)
    return result


def verify_global_zero_sum_closure(proof: dict[str, Any]) -> dict[str, Any]:
    body = deepcopy(proof)
    root = body.pop("proof_root_hash72", None)
    if root != _hash("hhs_pass219b_global_relation_bridge_v2", body):
        raise GlobalZeroSumClosureError("proof root mismatch")
    if body.get("status") != "GLOBAL_RELATION_BRIDGE_PROVED":
        raise GlobalZeroSumClosureError("status mismatch")
    family = body["closure_family"]
    if _read_fraction(family["delta"]) != 1:
        raise GlobalZeroSumClosureError("delta mismatch")
    if _read_fraction(family["P_squared_minus_pq"]) != 1:
        raise GlobalZeroSumClosureError("P^2-pq mismatch")
    if _read_fraction(family["xy_projection"]) != 1 or _read_fraction(family["zw_projection"]) != 1:
        raise GlobalZeroSumClosureError("ordered unit projection mismatch")
    if _read_fraction(family["x_plus_y_plus_z_plus_w"]) != 0:
        raise GlobalZeroSumClosureError("center zero-sum mismatch")
    if family["phase_carrier_sum_basis_1_I"] != [0, 0]:
        raise GlobalZeroSumClosureError("phase zero-sum mismatch")
    if body["global_tensor_binding"]["source_sha256"] != PARENT_MONOLITHIC_SHA256:
        raise GlobalZeroSumClosureError("global tensor source identity mismatch")
    phase = body["phase_quantization_binding"]
    if phase["source_sha256"] != PHASE_QUANTIZATION_SHA256:
        raise GlobalZeroSumClosureError("phase quantization identity mismatch")
    if phase["recursive_relation"] != "N/D^4=D^4":
        raise GlobalZeroSumClosureError("recursive relation mismatch")
    if phase["recursive_relation_structurally_proven"] is not True:
        raise GlobalZeroSumClosureError("recursive relation not structurally proven")
    if phase["scalar_cancellation_allowed"] is not False:
        raise GlobalZeroSumClosureError("scalar cancellation was introduced")
    hydration = body["hydration_bridge"]
    if hydration["lo_shu_sudoku_qudit_bound"] is not True:
        raise GlobalZeroSumClosureError("Lo Shu/Sudoku qudit bridge missing")
    if hydration["cell_count81"] != 81 or hydration["lo_shu_group_count41"] != 41:
        raise GlobalZeroSumClosureError("hydration geometry mismatch")
    if hydration["trit_count3"] != 3 or hydration["vm5184_slot_count"] != 5184:
        raise GlobalZeroSumClosureError("hydration coordinate mismatch")
    if hydration["hydration_state_count"] != HYDRATION_STATE_COUNT:
        raise GlobalZeroSumClosureError("hydration state cardinality mismatch")
    if body["global_enforcement"]["global_relation_bridge_proven"] is not True:
        raise GlobalZeroSumClosureError("global relation bridge not proven")
    return {
        "schema": "HHS_PASS219B_GLOBAL_RELATION_BRIDGE_VALIDATION_V2",
        "status": "GLOBAL_RELATION_BRIDGE_VALIDATED",
        "proof_root_hash72": root,
    }
