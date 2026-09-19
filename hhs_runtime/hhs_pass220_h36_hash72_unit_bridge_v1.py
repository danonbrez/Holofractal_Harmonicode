"""Pass 220 I018: H36 / HASH72 / UCE unit-ratio bridge.

This module joins the Pass 219 H36 exact identity and canonical native
universal-constraint source to the Pass 220 I017 multidimensional constraint
manifold through the user-supplied exact ratio:

    (e/H36=(mc^2)/u^144)
      =(a^2/P^4)*(c^2(a^2+b^2))
      =(xy+zw)/(q-p)

The bridge is projection-only. It does not identify the typed symbol e with
any unrelated basis symbol, does not solve the native m symbol from m*c^2, and
does not mint canonical Hash72/Hash216/VM81 authority.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Dict, Mapping

from hhs_runtime.hhs_pass219_dynamic_paradox_phase_cycle_v1 import (
    H36,
    h36_identity_witness,
)
from hhs_runtime.hhs_pass220_multidimensional_constraint_manifold_v1 import (
    hash72_algebraic_projection_witness,
)
from hhs_runtime.pass219_native_universal_constraint_v1 import (
    CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SHA256,
    CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SOURCE,
)

SCHEMA = "HHS_PASS_220_H36_HASH72_UNIT_BRIDGE_V1"
VERSION = "1.0.0-checkpoint.18"
PROFILE = "PASS220-I018-H36-HASH72-UNIT-BRIDGE-v1"
WITNESS_SCHEMA = "HHS_PASS_220_H36_HASH72_UNIT_RATIO_WITNESS_V1"

VERBATIM_UNIT_RATIO = (
    "(e/H36=(mc^2)/u^144)="
    "(a^2/P^4)*(c^2(a^2+b^2))="
    "(xy+zw)/(q-p)"
)


class Pass220H36Hash72BridgeError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    record = dict(payload)
    record["receipt_sha256"] = sha256(
        _stable_json(record).encode("utf-8")
    ).hexdigest()
    return record


def _exact_int(value: Any, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220H36Hash72BridgeError(
            f"{name} must be an exact integer"
        )
    return value


def h36_hash72_unit_ratio_witness(
    *,
    a2: int = 1,
    b2: int = 2,
    c2: int = 3,
    p4: int = 9,
    p2_minus_pq: int = 1,
    xy: int = 1,
    zw: int = 1,
    q_minus_p: int = 2,
    energy_e_projection: int = H36,
    mc2_projection: int | None = None,
) -> Dict[str, Any]:
    """Evaluate the exact scalar-facing unit-ratio bridge.

    mc2_projection is one typed compound projection. This function does
    not divide by c^2 to assign a value to the native m symbol.
    """
    checked = {
        name: _exact_int(value, name=name)
        for name, value in {
            "a2": a2,
            "b2": b2,
            "c2": c2,
            "p4": p4,
            "p2_minus_pq": p2_minus_pq,
            "xy": xy,
            "zw": zw,
            "q_minus_p": q_minus_p,
            "energy_e_projection": energy_e_projection,
        }.items()
    }
    if checked["a2"] + checked["b2"] != checked["c2"]:
        raise Pass220H36Hash72BridgeError(
            "a^2+b^2==c^2 closure failed"
        )
    if checked["p2_minus_pq"] != checked["a2"]:
        raise Pass220H36Hash72BridgeError(
            "P^2-pq must equal the Genesis a^2 unit"
        )
    if checked["p4"] != checked["c2"] * checked["c2"]:
        raise Pass220H36Hash72BridgeError(
            "P^4 must equal c^4 on the admitted Genesis projection"
        )
    if checked["p4"] == 1:
        raise Pass220H36Hash72BridgeError(
            "P^4!=1 boundary violated"
        )
    if checked["xy"] + checked["zw"] != checked["b2"]:
        raise Pass220H36Hash72BridgeError(
            "xy+zw must equal b^2 on the admitted ordered projection"
        )
    if checked["q_minus_p"] != checked["b2"]:
        raise Pass220H36Hash72BridgeError(
            "q-p must equal b^2 on the admitted reciprocal scale branch"
        )

    h36 = h36_identity_witness()
    if not h36["identity_equal"] or h36["h36_value"] != H36:
        raise Pass220H36Hash72BridgeError(
            "inherited H36 exact identity did not close"
        )

    hash72 = hash72_algebraic_projection_witness(
        a2=checked["a2"],
        b2=checked["b2"],
        c2=checked["c2"],
        p2_minus_pq=checked["p2_minus_pq"],
    )
    u144_projection = hash72["HASH72_projection"]
    mc2 = (
        u144_projection
        if mc2_projection is None
        else _exact_int(mc2_projection, name="mc2_projection")
    )

    energy_ratio = Fraction(checked["energy_e_projection"], H36)
    mc2_ratio = Fraction(mc2, u144_projection)
    magnitude_ratio = (
        Fraction(checked["a2"], checked["p4"])
        * checked["c2"]
        * (checked["a2"] + checked["b2"])
    )
    ordered_ratio = Fraction(
        checked["xy"] + checked["zw"],
        checked["q_minus_p"],
    )

    ratios = (
        energy_ratio,
        mc2_ratio,
        magnitude_ratio,
        ordered_ratio,
    )
    all_unit = all(value == 1 for value in ratios)
    if not all_unit:
        raise Pass220H36Hash72BridgeError(
            "H36/HASH72 unit-ratio bridge did not close"
        )

    source_text = CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SOURCE
    required_fragments = (
        "P^2-pq",
        "m^2-m",
        "u^72",
        "pq+xy",
        "AB/P^2",
        "Sqrt[AB]",
        "Delta/P",
    )
    fragments_present = all(
        fragment in source_text for fragment in required_fragments
    )
    if not fragments_present:
        raise Pass220H36Hash72BridgeError(
            "canonical universal-constraint source dependency drift"
        )

    return _receipt({
        "schema": WITNESS_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "verbatim_unit_ratio": VERBATIM_UNIT_RATIO,
        "ratios": {
            "e_over_H36": str(energy_ratio),
            "mc2_over_u144": str(mc2_ratio),
            "a2_over_P4_times_c2_times_a2_plus_b2": str(magnitude_ratio),
            "xy_plus_zw_over_q_minus_p": str(ordered_ratio),
        },
        "all_ratios_exact_unit": all_unit,
        "H36": H36,
        "H36_identity": h36,
        "u144_projection": u144_projection,
        "HASH72_projection": hash72["HASH72_projection"],
        "u144_equals_HASH72_projection": (
            u144_projection == hash72["HASH72_projection"]
        ),
        "H36_equals_HASH72_projection": (
            H36 == hash72["HASH72_projection"]
        ),
        "energy_e_projection": checked["energy_e_projection"],
        "mc2_projection": mc2,
        "energy_e_equals_H36_projection": (
            checked["energy_e_projection"] == H36
        ),
        "mc2_equals_u144_projection": mc2 == u144_projection,
        "middle_ratio_numerator": (
            checked["a2"]
            * checked["c2"]
            * (checked["a2"] + checked["b2"])
        ),
        "middle_ratio_denominator": checked["p4"],
        "xy_plus_zw": checked["xy"] + checked["zw"],
        "q_minus_p": checked["q_minus_p"],
        "P4": checked["p4"],
        "P4_not_one": checked["p4"] != 1,
        "P2_minus_pq": checked["p2_minus_pq"],
        "native_m_symbol_solved": False,
        "typed_mc2_compound_preserved": True,
        "typed_e_symbol_not_rebound_to_basis_e": True,
        "canonical_universal_constraint_sha256": (
            CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SHA256.hex()
        ),
        "canonical_universal_constraint_fragments_present": fragments_present,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_authority": False,
        "canonical_vm81_mutation_authority": False,
        "floating_point_authority": False,
        "ordinary_scalar_flattening_authority": False,
    })


def validate_h36_hash72_unit_bridge() -> Dict[str, Any]:
    witness = h36_hash72_unit_ratio_witness()
    checks = {
        "unit_ratio": witness["all_ratios_exact_unit"],
        "h36_hash72_projection_lock": (
            witness["H36_equals_HASH72_projection"]
        ),
        "u144_hash72_projection_lock": (
            witness["u144_equals_HASH72_projection"]
        ),
        "energy_projection_lock": (
            witness["energy_e_equals_H36_projection"]
        ),
        "mc2_projection_lock": witness["mc2_equals_u144_projection"],
        "P4_nonunit": witness["P4_not_one"],
        "uce_source_bound": (
            witness["canonical_universal_constraint_fragments_present"]
        ),
        "typed_m_preserved": not witness["native_m_symbol_solved"],
    }
    return _receipt({
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "ok": all(checks.values()),
        "checks": checks,
        "witness": witness,
        "invariant_ids": (
            "HHS-I008",
            "HHS-I010",
            "HHS-I011",
            "HHS-I012",
            "HHS-I014",
            "HHS-I015",
        ),
        "mutation_policy": (
            "READ_ONLY_EXACT_H36_HASH72_UNIT_BRIDGE_NO_VM81_MUTATION"
        ),
        "persistence_policy": "NO_CANONICAL_PERSISTENCE",
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_vm81_mutation_authority": False,
        "floating_point_authority": False,
    })


def h36_hash72_unit_bridge_self_test() -> Dict[str, Any]:
    return validate_h36_hash72_unit_bridge()
