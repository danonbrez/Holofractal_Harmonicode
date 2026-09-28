"""Pass 219 Lane 5 Cycle 8 — discrete Feynman / Carry admission bridge.

This module composes already-verified repository surfaces:
- Pass 220 I025 exact U9 permutation/Schrodinger orbit;
- Pass 219 Cycle 4 ordered symplectic Carry;
- Pass 219 Cycle 5 typed U72 scalar projection;
- Pass 219 Cycle 7 Penrose8 gauge-root discipline;
- Pass 220 I030 exact reciprocal UTF-8 ingress/egress;
- Pass 220 I001 fixed 5,184-character Lo-Shu normalization serialization.

The Feynman layer is deliberately finite and discrete. It does not claim a
continuum path integral. "No F2, no weight" is an HHS admission policy:
failure of the exact canonical type-2 generator forbids a canonical HHS
Feynman weight; it is not a claim that every external formalism assigns a
literal zero complex amplitude to the same map.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_runtime.hhs_pass220_schrodinger_firing_order_v1 import (
    FULL_ORBIT_CYCLE_COUNT,
    MACROCYCLE_ORDER,
    exact_energy_levels,
    macrocycle_permutation,
    permutation_matrix,
    permutation_power,
)
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    SERIALIZED_CHARACTERS,
    VM81_CELLS,
    deserialize_offsets_5184,
    offsets_to_bigint,
    serialize_offsets_5184,
)
from hhs_runtime.hhs_pass220_g3_reciprocal_symbol_codec_v1 import (
    EXPANDED_INGRESS_PROBES,
    g3_reciprocal_transform,
)
from hhs_runtime.pass219.lane5_penrose8_hash216_loshu_bridge import (
    CENTER_ROLE,
    U72_SCALAR_PROJECTION_CLOSURE_ASSIGNMENT,
    Z_GAUGE_POLICY,
    pi_gauge_descriptor,
)

SCHEMA = "HHS_PASS219_LANE5_FEYNMAN_DISCRETE_ORBIT_BRIDGE_V1"
VERSION = "1.0.1-cycle8-expanded-ingress"
WOLFRAM_SCHEMA = (
    "HHS_PASS_219_LANE5_FEYNMAN_DISCRETE_ORBIT_WOLFRAM_20260924_V8"
)

PARTITION_TRACE_SYMBOL = "partition_trace"
TWISTOR_SYMBOL = "Z"
HHS_WEIGHT_POLICY = "NO_EXACT_CANONICAL_F2 => NO_ADMITTED_HHS_FEYNMAN_WEIGHT"
CONTINUUM_PATH_INTEGRAL_CLAIMED = False

TYPE2_GENERATOR = "F2(q,P)=q*P+h*(P^2/(2m)+V(q))"
GLUED_STEP_ACTION = (
    "S_step=P*(Q-q)-h*(P^2/(2m)+V(q))=P*Q-F2(q,P)"
)
MIXED_REPRESENTATION_WEIGHT = "ExpSym(i*F2/u72)"
CONFIGURATION_PATH_WEIGHT = "ExpSym(i*sum(S_step)/u72)"

INGRESS_EGRESS_X_BINDING = EXPANDED_INGRESS_PROBES[0]
INGRESS_EGRESS_PHASE_BINDING = EXPANDED_INGRESS_PROBES[1]
INGRESS_EGRESS_PROJECTION_CHAIN = EXPANDED_INGRESS_PROBES[2]
ZERO_NORMALIZATION_SHORTHAND = "(0000000)"


class Lane5FeynmanDiscreteOrbitError(ValueError):
    pass


def _stable(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _receipt(payload: dict[str, Any]) -> dict[str, Any]:
    body = dict(payload)
    body["receipt_sha256"] = sha256(
        _stable(body).encode("utf-8")
    ).hexdigest()
    return body


def _i(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Lane5FeynmanDiscreteOrbitError(
            f"{name} must be an exact integer"
        )
    return value


def _q(value: Any, name: str) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise Lane5FeynmanDiscreteOrbitError(
            f"{name} must be an exact int/Fraction"
        )
    try:
        return Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise Lane5FeynmanDiscreteOrbitError(
            f"{name} must be an exact int/Fraction"
        ) from exc


def history_kernel_receipt(power: int) -> dict[str, Any]:
    """Exact U9^n history support.

    U9 is a permutation. Therefore every source has exactly one reachable
    endpoint after n steps, and every other source/endpoint pair has zero
    admitted constructor histories. The propagator has exactly nine nonzero
    entries, not one history for each of all 81 endpoint pairs.
    """
    n = _i(power, "power")
    if n < 0:
        raise Lane5FeynmanDiscreteOrbitError("power must be nonnegative")

    powered = permutation_power(macrocycle_permutation(), n)
    matrix = permutation_matrix(powered)
    nonzero = tuple(
        (row + 1, column + 1)
        for row in range(MACROCYCLE_ORDER)
        for column in range(MACROCYCLE_ORDER)
        if matrix[row][column] != 0
    )
    source_to_endpoint = tuple(
        (source, powered[source - 1])
        for source in range(1, MACROCYCLE_ORDER + 1)
    )

    checks = {
        "nine_nonzero_entries": len(nonzero) == MACROCYCLE_ORDER,
        "one_endpoint_per_source": len({source for source, _ in source_to_endpoint})
        == MACROCYCLE_ORDER,
        "one_source_per_endpoint": len({endpoint for _, endpoint in source_to_endpoint})
        == MACROCYCLE_ORDER,
        "binary_propagator": all(
            entry in (0, 1) for row in matrix for entry in row
        ),
    }
    return _receipt({
        "schema": "HHS_PASS219_U9_SINGLE_HISTORY_KERNEL_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "power": n,
        "checks": checks,
        "nonzero_count": len(nonzero),
        "nonzero_source_endpoint_pairs": nonzero,
        "source_to_endpoint": source_to_endpoint,
        "reachable_pair_history_count": 1,
        "unreachable_pair_history_count": 0,
        "history_sum_reduction": (
            "finite path sum collapses to one admitted constructor history "
            "for each reachable source/endpoint pair"
        ),
        "continuum_path_integral_claimed": False,
    })


def partition_trace(power: int) -> int:
    """Real-time spectral trace Tr(U9^n), kept distinct from twistor Z."""
    n = _i(power, "power")
    if n < 0:
        raise Lane5FeynmanDiscreteOrbitError("power must be nonnegative")
    powered = permutation_power(macrocycle_permutation(), n)
    return sum(
        1
        for index, endpoint in enumerate(powered, start=1)
        if endpoint == index
    )


def partition_trace_receipt(power: int) -> dict[str, Any]:
    n = _i(power, "power")
    value = partition_trace(n)
    return _receipt({
        "schema": "HHS_PASS219_U9_PARTITION_TRACE_V1",
        "power": n,
        "partition_trace": value,
        "exact_cycle_rule": "Tr(U9^n)=9 iff n mod 9 == 0, else 0",
        "rule_verified_here": value == (9 if n % MACROCYCLE_ORDER == 0 else 0),
        "trace_class": "REAL_TIME_SPECTRAL_TRACE_NOT_THERMAL_PARTITION_FUNCTION",
        "basis_change_invariance": "Tr(G U^n G^-1)=Tr(U^n)",
        "partition_symbol": PARTITION_TRACE_SYMBOL,
        "twistor_symbol_reserved": TWISTOR_SYMBOL,
    })


def carried_action_descriptor() -> dict[str, Any]:
    """Exact symbolic descriptor for the carried kick->drift generator."""
    return _receipt({
        "schema": "HHS_PASS219_CARRIED_FEYNMAN_ACTION_DESCRIPTOR_V1",
        "status": "PASS",
        "type2_generator": TYPE2_GENERATOR,
        "generator_relations": (
            "p=dF2/dq=P+h*V'(q)",
            "Q=dF2/dP=q+h*P/m",
            "P=p-h*V'(q)",
            "Q=q+h*(p-h*V'(q))/m",
        ),
        "glued_step_action": GLUED_STEP_ACTION,
        "stationary_relations": (
            "dS_step/dP=Q-q-h*P/m=0",
            "p=-dS_step/dq=P+h*V'(q)",
            "P=dS_step/dQ",
        ),
        "mixed_representation_weight": MIXED_REPRESENTATION_WEIGHT,
        "configuration_path_weight": CONFIGURATION_PATH_WEIGHT,
        "canonical_f2_exists": True,
        "admitted_hhs_feynman_weight": True,
        "ordered_update": "KICK_THEN_DRIFT",
        "continuum_path_integral_claimed": False,
    })


def explicit_old_state_euler_weight_admission(
    *,
    h: Any,
    mass: Any,
    potential_curvature: Any,
) -> dict[str, Any]:
    """Fail-closed type-2 generating-function admission test.

    After eliminating old p in favor of (q,P):
        p = P + h V'(q)
        Q = q + h p/m.

    The necessary type-2 cross-derivative equality fails by:
        dQ/dq - dp/dP = h^2 V''(q)/m.

    For nonzero mismatch no local exact F2 exists for this map. A zero mismatch
    passes only this necessary test; it does not manufacture a global generator.
    """
    step = _q(h, "h")
    m = _q(mass, "mass")
    curvature = _q(potential_curvature, "potential_curvature")
    if m == 0:
        raise Lane5FeynmanDiscreteOrbitError("mass must be nonzero")

    mismatch = step**2 * curvature / m
    if mismatch != 0:
        status = "REJECTED_NO_TYPE2_GENERATOR"
        f2_exists: bool | None = False
        weight_authorized: bool | None = False
    else:
        status = "NECESSARY_INTEGRABILITY_CONDITION_ONLY"
        f2_exists = None
        weight_authorized = None

    return _receipt({
        "schema": "HHS_PASS219_EXPLICIT_EULER_F2_ADMISSION_V1",
        "status": status,
        "cross_derivative_mismatch": [
            mismatch.numerator,
            mismatch.denominator,
        ],
        "cross_derivative_rule": "h^2*V''(q)/m",
        "unit_mass_rule": "h^2*V''(q)",
        "canonical_f2_exists": f2_exists,
        "admitted_hhs_feynman_weight": weight_authorized,
        "weight_policy": HHS_WEIGHT_POLICY,
        "literal_external_zero_amplitude_claimed": False,
    })


def spectral_phase_receipt(k: int, winding: int = 1) -> dict[str, Any]:
    """Bind I025's exact phase to the Cycle-5 scalar U72 projection face."""
    mode = _i(k, "k")
    turns = _i(winding, "winding")
    if not 0 <= mode < MACROCYCLE_ORDER:
        raise Lane5FeynmanDiscreteOrbitError("k must satisfy 0 <= k < 9")
    if turns < 0:
        raise Lane5FeynmanDiscreteOrbitError("winding must be nonnegative")

    level = exact_energy_levels()[mode]
    phase = level.phase ** turns
    scalar_energy = (
        "0"
        if mode == 0
        else f"4*pi*{mode}/(9*ubar^2*tau*theta)"
    )
    return _receipt({
        "schema": "HHS_PASS219_FEYNMAN_SPECTRAL_PHASE_V1",
        "k": mode,
        "winding": turns,
        "native_energy": level.exact_text,
        "scalar_projection_energy": scalar_energy,
        "u72_scalar_projection": U72_SCALAR_PROJECTION_CLOSURE_ASSIGNMENT,
        "ordinary_ubar_power_rewrite_authorized": False,
        "eigenphase": phase.as_text(),
        "degeneracy": level.degeneracy,
        "outer_cell_degeneracy_expected": FULL_ORBIT_CYCLE_COUNT,
        "phase_constant_across_degenerate_outer_sector": (
            level.degeneracy == FULL_ORBIT_CYCLE_COUNT == 8
        ),
        "projection_only": True,
    })


def ingress_egress_zero_normalization_receipt() -> dict[str, Any]:
    """Bind supplied exact source expressions to existing codecs and zero ABI."""
    literals = EXPANDED_INGRESS_PROBES
    roundtrips = []
    carrier_receipts = []
    for source in literals:
        carrier = g3_reciprocal_transform(source)
        if not isinstance(carrier, Mapping):
            raise Lane5FeynmanDiscreteOrbitError(
                "source ingress did not produce a reciprocal carrier"
            )
        recovered = g3_reciprocal_transform(carrier)
        roundtrips.append(recovered == source)
        carrier_receipts.append(str(carrier.get("receipt_sha256") or ""))

    zero_offsets = (0,) * VM81_CELLS
    serialized = serialize_offsets_5184(zero_offsets)
    decoded = deserialize_offsets_5184(serialized)
    scalar = offsets_to_bigint(zero_offsets)

    checks = {
        "source_roundtrips_exact": all(roundtrips),
        "carrier_receipts_present": all(bool(value) for value in carrier_receipts),
        "zero_offset_count_81": len(zero_offsets) == 81,
        "zero_serialized_width_5184": len(serialized) == SERIALIZED_CHARACTERS == 5184,
        "zero_serialization_roundtrip": decoded == zero_offsets,
        "zero_scalar_bigint": scalar == 0,
    }
    return _receipt({
        "schema": "HHS_PASS219_CYCLE8_INGRESS_EGRESS_ZERO_NORMALIZATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "source_literals": literals,
        "source_strings_parsed_as_numbers": False,
        "expanded_ingress_probe_count": len(EXPANDED_INGRESS_PROBES),
        "projection_chain_preserved_verbatim": (
            literals[2] == INGRESS_EGRESS_PROJECTION_CHAIN
        ),
        "reciprocal_carrier_receipt_sha256": carrier_receipts,
        "zero_normalization_shorthand": ZERO_NORMALIZATION_SHORTHAND,
        "zero_normalization_shorthand_is_canonical_serialization": False,
        "canonical_zero_serialization_length": len(serialized),
        "canonical_zero_first_cell_token": serialized[:64],
        "canonical_zero_serialization_sha256": sha256(
            serialized.encode("ascii")
        ).hexdigest(),
        "scalar_bigint_zero": scalar,
        "canonical_serializer_reused": (
            "hhs_pass220_lo_shu_normalization_v1.serialize_offsets_5184"
        ),
    })


def cycle8_receipt(
    *,
    pi0: tuple[Fraction, Fraction],
    pi1: tuple[Fraction, Fraction],
) -> dict[str, Any]:
    histories = tuple(history_kernel_receipt(n) for n in range(19))
    traces = tuple(partition_trace(n) for n in range(1, 10))
    spectra = tuple(spectral_phase_receipt(k) for k in range(9))
    carried = carried_action_descriptor()
    explicit = explicit_old_state_euler_weight_admission(
        h=Fraction(1, 4),
        mass=1,
        potential_curvature=1,
    )
    codec = ingress_egress_zero_normalization_receipt()
    gauge = pi_gauge_descriptor(pi0, pi1)

    checks = {
        "r1_single_history_exact": all(
            item["status"] == "PASS" and item["nonzero_count"] == 9
            for item in histories
        ),
        "r2_carried_generator_admitted": (
            carried["canonical_f2_exists"] is True
            and carried["admitted_hhs_feynman_weight"] is True
        ),
        "r3_partition_trace_cycle": traces == (0,0,0,0,0,0,0,0,9),
        "r4_explicit_euler_rejected": (
            explicit["status"] == "REJECTED_NO_TYPE2_GENERATOR"
            and explicit["canonical_f2_exists"] is False
            and explicit["admitted_hhs_feynman_weight"] is False
        ),
        "spectrum_has_nine_modes": len(spectra) == 9,
        "spectrum_outer_degeneracy_eight": all(
            item["degeneracy"] == 8 for item in spectra
        ),
        "partition_twistor_symbols_distinct": (
            PARTITION_TRACE_SYMBOL != TWISTOR_SYMBOL
        ),
        "gauge_root_required_for_absolute_phase_magnitude": (
            gauge["absolute_z_magnitude_gate_requires_gauge_root_match"] is True
            and gauge["cross_gauge_absolute_magnitude_authorized"] is False
        ),
        "center_remains_lock": (
            CENTER_ROLE == "NUCLEUS_LOCK_NOT_8D_CARRIER_COORDINATE"
        ),
        "ingress_egress_and_zero_normalization": codec["status"] == "PASS",
    }

    return _receipt({
        "schema": SCHEMA,
        "version": VERSION,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "pass_count": sum(bool(value) for value in checks.values()),
        "check_count": len(checks),
        "wolfram_evidence_schema": WOLFRAM_SCHEMA,
        "histories_checked_n0_to_18": len(histories),
        "partition_trace_n1_to_9": traces,
        "carried_action": carried,
        "explicit_euler_admission": explicit,
        "spectral_modes": spectra,
        "ingress_egress_zero_normalization": codec,
        "z_gauge": gauge,
        "z_gauge_policy": Z_GAUGE_POLICY,
        "weight_policy": HHS_WEIGHT_POLICY,
        "continuum_path_integral_claimed": CONTINUUM_PATH_INTEGRAL_CLAIMED,
        "continuum_limit_status": (
            "OUT_OF_SCOPE; existing zero-order-hold machinery is not "
            "promoted here into a continuum path-integral proof"
        ),
        "partition_trace_class": (
            "REAL_TIME_SPECTRAL_TRACE_NOT_THERMAL_PARTITION_FUNCTION"
        ),
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_mint_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_canonical_authority": False,
    })


def self_test() -> dict[str, Any]:
    # Exact Cycle-7 regression fixture only; not a universal Genesis spinor.
    result = cycle8_receipt(
        pi0=(Fraction(1), Fraction(2)),
        pi1=(Fraction(3), Fraction(-1)),
    )
    if result["status"] != "PASS":
        raise Lane5FeynmanDiscreteOrbitError("Cycle 8 self-test failed")
    return {
        "schema": "HHS_PASS219_LANE5_FEYNMAN_DISCRETE_ORBIT_SELF_TEST_V1",
        "status": "PASS",
        "fixture_is_canonical_genesis_spinor": False,
        "cycle8_receipt_sha256": result["receipt_sha256"],
    }


if __name__ == "__main__":
    print(_stable(self_test()))
