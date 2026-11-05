"""Pass 220 I048: exact Lo Shu integer-ratio A/B hydration candidate.

This module preserves the supplied HARMONICODE relations as exact integer/tensor
objects. Arm A recomputes base-9 Lo Shu addresses for each evaluation. Arm B
hydrates the exact same address payload once and reuses it. Neither arm has
canonical VM81/Hash72/Hash216 mutation authority.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

SCHEMA = "HHS_PASS_220_I048_LOSHU_INTEGER_RATIO_AB_V1"
WOLFRAM_SCHEMA = "HHS_PASS_220_I048_LOSHU_INTEGER_RATIO_AB_WOLFRAM_V1"
WOLFRAM_MATERIAL_SHA256 = "7430d595151de3e32ada1a20b4f0e1b28b0647c51efed8b9115d9311550c63c7"
GLOBAL_INVARIANT = "AB=P^4=c^4=(a^2+b^2)^2=9/Delta"
RECIPROCAL_TENSOR = "(p/q)=(q/p)^-1"

LO_SHU = ((4, 9, 2), (3, 5, 7), (8, 1, 6))
TRIPLES: dict[str, tuple[int, int, int]] = {
    "A": (1, 2, 3),
    "B": (2, 3, 5),
    "C": (3, 5, 8),
    "D": (4, 7, 11),
    "E": (5, 8, 13),
    "F": (3, 6, 9),
    "G": (2, 4, 6),
    "H": (7, 11, 18),
}
EXPECTED_RESIDUES: dict[str, tuple[int, int, int]] = {
    "A": (1, 2, 3),
    "B": (2, 3, 5),
    "C": (3, 5, 8),
    "D": (4, 7, 2),
    "E": (5, 8, 4),
    "F": (3, 6, 0),
    "G": (2, 4, 6),
    "H": (7, 2, 0),
}
EXPECTED_CELL_LABELS: dict[str, tuple[int, int, int]] = {
    **{key: value for key, value in EXPECTED_RESIDUES.items() if key not in {"F", "H"}},
    "F": (3, 6, 9),
    "H": (7, 2, 9),
}


class Pass220I048Error(ValueError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass220I048Error(f"floating value forbidden at {path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def canonical_bytes(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _validate_triple(name: str, values: Sequence[int]) -> tuple[int, int, int]:
    if len(values) != 3:
        raise Pass220I048Error(f"{name} must contain exactly three positions")
    if not all(isinstance(value, int) and not isinstance(value, bool) for value in values):
        raise Pass220I048Error(f"{name} must contain whole integers only")
    return int(values[0]), int(values[1]), int(values[2])


def mod9_residue(value: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise Pass220I048Error("mod9 input must be a whole integer")
    return value % 9


def lo_shu_cell_label(residue: int) -> int:
    if not isinstance(residue, int) or isinstance(residue, bool) or not 0 <= residue <= 8:
        raise Pass220I048Error("Lo Shu residue must be an integer in 0..8")
    return 9 if residue == 0 else residue


def geometry_payload(
    triples: Mapping[str, Sequence[int]] | None = None,
) -> dict[str, Any]:
    source = TRIPLES if triples is None else triples
    if tuple(source.keys()) != tuple(TRIPLES.keys()):
        raise Pass220I048Error("ratio triple identity/order mismatch")

    normalized = {name: _validate_triple(name, source[name]) for name in TRIPLES}
    residues = {
        name: tuple(mod9_residue(value) for value in values)
        for name, values in normalized.items()
    }
    labels = {
        name: tuple(lo_shu_cell_label(value) for value in values)
        for name, values in residues.items()
    }

    checks = {
        "C_equals_A_plus_B": normalized["C"] == tuple(a + b for a, b in zip(normalized["A"], normalized["B"])),
        "D_equals_A_plus_C": normalized["D"] == tuple(a + c for a, c in zip(normalized["A"], normalized["C"])),
        "E_equals_B_plus_C": normalized["E"] == tuple(b + c for b, c in zip(normalized["B"], normalized["C"])),
        "G_equals_2A": normalized["G"] == tuple(2 * a for a in normalized["A"]),
        "F_equals_3A": normalized["F"] == tuple(3 * a for a in normalized["A"]),
        "H_equals_B_plus_E": normalized["H"] == tuple(b + e for b, e in zip(normalized["B"], normalized["E"])),
        "base9_residues_expected": residues == EXPECTED_RESIDUES,
        "lo_shu_cell_labels_expected": labels == EXPECTED_CELL_LABELS,
    }
    if not all(checks.values()):
        failed = sorted(key for key, value in checks.items() if not value)
        raise Pass220I048Error("integer-ratio geometry failed: " + ",".join(failed))

    payload = {
        "schema": SCHEMA + "_GEOMETRY",
        "triples": {name: list(values) for name, values in normalized.items()},
        "base9_residues": {name: list(values) for name, values in residues.items()},
        "lo_shu_cell_labels": {name: list(values) for name, values in labels.items()},
        "lo_shu": [list(row) for row in LO_SHU],
        "global_invariant_verbatim": GLOBAL_INVARIANT,
        "reciprocal_tensor_verbatim": RECIPROCAL_TENSOR,
        "checks": checks,
    }
    payload["geometry_sha256"] = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    return payload


def verify_wolfram_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    _reject_float(receipt)
    checks = receipt.get("checks", {})
    if receipt.get("schema") != WOLFRAM_SCHEMA:
        raise Pass220I048Error("Wolfram schema mismatch")
    if receipt.get("status") != "PASS":
        raise Pass220I048Error("Wolfram formalization did not pass")
    if receipt.get("check_count") != 28 or receipt.get("pass_count") != 28:
        raise Pass220I048Error("Wolfram check count mismatch")
    if len(checks) != 28 or not all(checks.values()):
        raise Pass220I048Error("Wolfram receipt contains failed checks")
    if receipt.get("material_sha256") != WOLFRAM_MATERIAL_SHA256:
        raise Pass220I048Error("Wolfram material identity mismatch")
    if receipt.get("global_invariant_verbatim") != GLOBAL_INVARIANT:
        raise Pass220I048Error("global invariant text drift")
    if receipt.get("reciprocal_tensor_verbatim") != RECIPROCAL_TENSOR:
        raise Pass220I048Error("reciprocal tensor text drift")
    if receipt.get("native_hash216_authority") is not False:
        raise Pass220I048Error("Wolfram receipt exposes forbidden Hash216 authority")
    if receipt.get("canonical_transition_ready") is not False:
        raise Pass220I048Error("Wolfram receipt overclaims canonical readiness")
    return dict(receipt)


def run_ab_cycle(repeats: int = 81) -> dict[str, Any]:
    if not isinstance(repeats, int) or isinstance(repeats, bool) or repeats < 1:
        raise Pass220I048Error("repeats must be a positive whole integer")

    arm_a_payloads = [geometry_payload() for _ in range(repeats)]
    hydrated = geometry_payload()
    arm_b_payloads = [hydrated for _ in range(repeats)]

    arm_a_digest = hashlib.sha256(canonical_bytes(arm_a_payloads)).hexdigest()
    arm_b_digest = hashlib.sha256(canonical_bytes(arm_b_payloads)).hexdigest()
    if arm_a_digest != arm_b_digest:
        raise Pass220I048Error("A/B exact payload mismatch")

    tuple_width = sum(len(values) for values in TRIPLES.values())
    arm_a_mod_operations = repeats * tuple_width
    arm_b_mod_operations = tuple_width

    return {
        "schema": SCHEMA + "_AB_RECEIPT",
        "status": "PASS",
        "repeats": repeats,
        "arm_A": {
            "strategy": "DIRECT_EXACT_MOD9_RECOMPUTE",
            "payload_sha256": arm_a_digest,
            "mod_operations": arm_a_mod_operations,
        },
        "arm_B": {
            "strategy": "HYDRATED_EXACT_MOD9_REUSE",
            "payload_sha256": arm_b_digest,
            "mod_operations": arm_b_mod_operations,
        },
        "exact_payload_equal": True,
        "mod_operation_reduction": arm_a_mod_operations - arm_b_mod_operations,
        "optimization_metric": "COUNTED_MOD9_OPERATIONS_ONLY",
        "wall_clock_speed_claimed": False,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_canonical_authority": False,
    }


def validate_contract(contract: Mapping[str, Any], wolfram_receipt: Mapping[str, Any]) -> dict[str, Any]:
    _reject_float(contract)
    verify_wolfram_receipt(wolfram_receipt)
    if contract.get("schema") != SCHEMA:
        raise Pass220I048Error("contract schema mismatch")
    if contract.get("global_invariant_verbatim") != GLOBAL_INVARIANT:
        raise Pass220I048Error("contract global invariant drift")
    if contract.get("reciprocal_tensor_verbatim") != RECIPROCAL_TENSOR:
        raise Pass220I048Error("contract reciprocal tensor drift")
    if contract.get("wolfram_material_sha256") != WOLFRAM_MATERIAL_SHA256:
        raise Pass220I048Error("contract Wolfram material mismatch")
    authority = contract.get("authority", {})
    forbidden = (
        "canonical_vm81_mutation_authority",
        "canonical_hash72_authority",
        "canonical_hash216_authority",
        "canonical_persistence_authority",
        "floating_point_canonical_authority",
    )
    if authority.get("candidate_only") is not True:
        raise Pass220I048Error("contract must remain candidate-only")
    if any(bool(authority.get(key)) for key in forbidden):
        raise Pass220I048Error("contract exposes forbidden canonical authority")
    cycle = run_ab_cycle(int(contract.get("ab_repeats", 81)))
    return {
        "schema": SCHEMA + "_CONTRACT_RECEIPT",
        "status": "PASS",
        "geometry": geometry_payload(),
        "ab": cycle,
        "wolfram_material_sha256": WOLFRAM_MATERIAL_SHA256,
        "candidate_only": True,
    }
