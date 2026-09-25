"""Pass 219 Lane 5 — Cycle 9 proof-preserving tick transport.

This module makes the admitted P/p/q tick symmetry executable without
re-solving or scalarizing the carried HHS state.

The exact scalar projection used here is already licensed by the repository:

    P^2 - p*q = 1
    q - p = 2
    (q-p)*P = p+q

with the simultaneous transport

    T(P,p,q) = (P+1,p+1,q+1).

All non-coordinate fields are opaque carried state.  In particular Qe/Q_e,
K_delta/D_delta, ordered provenance, address history, Hash72 block material and
Hash216 lineage are transported byte-for-byte at the Python value level.  This
module does not authorize cross-projection substitution, close the T_BRIDGE-01B
workload interval certificate, or mint canonical VM81/Hash72/Hash216 state.
"""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Mapping

SCHEMA = "HHS_PASS219_LANE5_CYCLE9_TICK_TRANSPORT_V1"
VERSION = "1.0.0-cycle9"
BASE_P0 = Fraction(2133185666641251, 10**15)
SOURCE_BLOCK_COUNT = 72


class Cycle9TransportError(ValueError):
    pass


def _q(value: Any, name: str) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise Cycle9TransportError(f"{name} must be exact int/Fraction")
    try:
        return Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise Cycle9TransportError(f"{name} must be exact int/Fraction") from exc


def _stable(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _digest(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def coordinate(P: Any, p: Any, q: Any) -> dict[str, Fraction]:
    return {"P": _q(P, "P"), "p": _q(p, "p"), "q": _q(q, "q")}


def canonical_coordinate_from_P(P: Any) -> dict[str, Fraction]:
    pivot = _q(P, "P")
    return {"P": pivot, "p": pivot - 1, "q": pivot + 1}


def constraint_residuals(state: Mapping[str, Any]) -> tuple[Fraction, Fraction, Fraction]:
    P = _q(state["P"], "P")
    p = _q(state["p"], "p")
    q = _q(state["q"], "q")
    return (
        P * P - p * q - 1,
        q - p - 2,
        (q - p) * P - (p + q),
    )


def rational_bridge_residual(state: Mapping[str, Any]) -> Fraction:
    P = _q(state["P"], "P")
    p = _q(state["p"], "p")
    q = _q(state["q"], "q")
    denominator = p + q
    if denominator == 0:
        raise Cycle9TransportError("licensed rational bridge denominator is zero")
    return P * P - (p * q + ((q - p) * P) / denominator)


def admitted_coordinate(state: Mapping[str, Any]) -> bool:
    try:
        return all(value == 0 for value in constraint_residuals(state)) and (
            rational_bridge_residual(state) == 0
        )
    except (KeyError, Cycle9TransportError):
        return False


def tick_coordinate(state: Mapping[str, Any]) -> dict[str, Fraction]:
    if not admitted_coordinate(state):
        raise Cycle9TransportError("source coordinate is not admitted")
    return {
        "P": _q(state["P"], "P") + 1,
        "p": _q(state["p"], "p") + 1,
        "q": _q(state["q"], "q") + 1,
    }


def untick_coordinate(state: Mapping[str, Any]) -> dict[str, Fraction]:
    if not admitted_coordinate(state):
        raise Cycle9TransportError("source coordinate is not admitted")
    return {
        "P": _q(state["P"], "P") - 1,
        "p": _q(state["p"], "p") - 1,
        "q": _q(state["q"], "q") - 1,
    }


def _opaque_fields(state: Mapping[str, Any]) -> dict[str, Any]:
    return {key: deepcopy(value) for key, value in state.items() if key not in {"P", "p", "q"}}


def transport_state(state: Mapping[str, Any], *, direction: int = 1) -> dict[str, Any]:
    if direction not in (-1, 1):
        raise Cycle9TransportError("direction must be +1 or -1")
    if not admitted_coordinate(state):
        raise Cycle9TransportError("source state is not admitted")

    carried = _opaque_fields(state)
    carried_before = _digest(carried)
    next_coordinate = tick_coordinate(state) if direction == 1 else untick_coordinate(state)
    out: dict[str, Any] = {**next_coordinate, **deepcopy(carried)}
    carried_after = _digest(_opaque_fields(out))
    if carried_before != carried_after:
        raise Cycle9TransportError("opaque carried-state digest changed")
    if not admitted_coordinate(out):
        raise Cycle9TransportError("transported coordinate left the admitted manifold")

    qe_keys = tuple(key for key in ("qe", "Qe", "Q_e") if key in carried)
    delta_keys = tuple(key for key in ("K_delta", "D_delta", "K_Δ", "D_Δ") if key in carried)
    checks = {
        "source_coordinate_admitted": True,
        "transported_coordinate_admitted": True,
        "opaque_state_digest_preserved": carried_before == carried_after,
        "qe_carried_if_present": all(out.get(key) == state.get(key) for key in qe_keys),
        "kernel_delta_material_carried_if_present": all(
            out.get(key) == state.get(key) for key in delta_keys
        ),
        "ordered_provenance_carried_if_present": (
            "ordered_provenance" not in carried
            or out.get("ordered_provenance") == state.get("ordered_provenance")
        ),
        "address_history_carried_if_present": (
            "address_history" not in carried
            or out.get("address_history") == state.get("address_history")
        ),
        "constraint_history_carried_if_present": (
            "constraint_history" not in carried
            or out.get("constraint_history") == state.get("constraint_history")
        ),
        "hash72_block_carried_if_present": (
            "hash72_block" not in carried
            or out.get("hash72_block") == state.get("hash72_block")
        ),
        "hash216_lineage_carried_if_present": (
            "hash216_lineage" not in carried
            or out.get("hash216_lineage") == state.get("hash216_lineage")
        ),
    }
    if not all(checks.values()):
        raise Cycle9TransportError(f"transport carry invariant failed: {checks}")

    out["_cycle9_transport"] = {
        "schema": SCHEMA,
        "version": VERSION,
        "direction": direction,
        "opaque_state_sha256_before": carried_before,
        "opaque_state_sha256_after": carried_after,
        "checks": checks,
        "cross_projection_substitution_authorized": False,
        "t_bridge_workload_interval_inferred": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_mint_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_authority": False,
    }
    return out


def prove_72_block_transport(
    *,
    base_P: Any = BASE_P0,
    carried_state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    base = canonical_coordinate_from_P(base_P)
    carried = deepcopy(dict(carried_state or {}))
    state: dict[str, Any] = {**base, **carried}

    if not admitted_coordinate(state):
        raise Cycle9TransportError("base state is not admitted")

    source_blocks: list[dict[str, Any]] = []
    transitions: list[dict[str, Any]] = []
    endpoints: list[dict[str, Fraction]] = [
        {key: _q(state[key], key) for key in ("P", "p", "q")}
    ]

    for index in range(SOURCE_BLOCK_COUNT):
        if not admitted_coordinate(state):
            raise Cycle9TransportError(f"source block {index} is not admitted")
        source_blocks.append(
            {
                "block_index": index,
                "coordinate": {
                    key: _fraction_record(_q(state[key], key))
                    for key in ("P", "p", "q")
                },
                "constraint_residuals": [
                    _fraction_record(value) for value in constraint_residuals(state)
                ],
                "rational_bridge_residual": _fraction_record(
                    rational_bridge_residual(state)
                ),
            }
        )
        next_state = transport_state(state, direction=1)
        transitions.append(
            {
                "transition_index": index,
                "source_P": _fraction_record(_q(state["P"], "P")),
                "target_P": _fraction_record(_q(next_state["P"], "P")),
                "opaque_state_sha256": next_state["_cycle9_transport"][
                    "opaque_state_sha256_after"
                ],
            }
        )
        next_state.pop("_cycle9_transport", None)
        state = next_state
        endpoints.append(
            {key: _q(state[key], key) for key in ("P", "p", "q")}
        )

    expected_final = canonical_coordinate_from_P(_q(base_P, "base_P") + SOURCE_BLOCK_COUNT)
    inverse = untick_coordinate(state)
    previous = endpoints[-2]

    checks = {
        "base_admitted": admitted_coordinate({**base, **carried}),
        "source_block_count_72": len(source_blocks) == 72,
        "forward_transition_count_72": len(transitions) == 72,
        "endpoint_state_count_73": len(endpoints) == 73,
        "all_source_blocks_zero_residual": all(
            all(record["numerator"] == 0 for record in row["constraint_residuals"])
            for row in source_blocks
        ),
        "all_source_blocks_bridge_zero": all(
            row["rational_bridge_residual"]["numerator"] == 0
            for row in source_blocks
        ),
        "final_endpoint_exact_plus_72": all(
            _q(state[key], key) == expected_final[key] for key in ("P", "p", "q")
        ),
        "inverse_recovers_previous_endpoint": all(
            inverse[key] == previous[key] for key in ("P", "p", "q")
        ),
        "opaque_carried_state_preserved": _digest(_opaque_fields(state)) == _digest(carried),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    core = {
        "schema": SCHEMA,
        "version": VERSION,
        "status": status,
        "proof_scope": "EXACT_72_BLOCK_P_P_Q_TICK_TRANSPORT",
        "base_P0": _fraction_record(_q(base_P, "base_P")),
        "source_block_count": len(source_blocks),
        "forward_transition_count": len(transitions),
        "endpoint_state_count": len(endpoints),
        "final_endpoint": {
            key: _fraction_record(_q(state[key], key)) for key in ("P", "p", "q")
        },
        "checks": checks,
        "per_step_algebraic_readmission_required": False,
        "proof_transport_rule": (
            "base admission + exact tick/inverse ideal symmetry -> inherited "
            "lattice admission; runtime receipts/provenance remain carried state"
        ),
        "cross_projection_sigma_delta_bridge_closed": False,
        "cross_projection_substitution_authorized": False,
        "t_bridge_01b_workload_interval_certificate_closed": False,
        "qe_semantic_resolution_inferred": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_mint_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_authority": False,
    }
    core["receipt_sha256"] = _digest(core)
    return core


def self_test() -> dict[str, Any]:
    carried = {
        "Q_e": 1,
        "K_delta": {"transport": "full_tuple", "kind": "exact"},
        "D_delta": {"domain": "exact", "nonzero": True},
        "ordered_provenance": ["P0", "constraint-ideal", "tick"],
        "address_history": ["genesis", "lane5"],
        "constraint_history": ["P2-pq-1", "q-p-2", "(q-p)P-(p+q)"],
        "hash72_block": "opaque-hash72-material",
        "hash216_lineage": {
            "previous72": "opaque-prev",
            "next72": "opaque-next",
            "receipt72": "opaque-receipt",
        },
    }
    receipt = prove_72_block_transport(carried_state=carried)
    if receipt["status"] != "PASS":
        raise Cycle9TransportError("Cycle 9 self-test failed")
    return {
        "schema": "HHS_PASS219_LANE5_CYCLE9_TICK_TRANSPORT_SELF_TEST_V1",
        "status": "PASS",
        "receipt_sha256": receipt["receipt_sha256"],
    }


if __name__ == "__main__":
    print(_stable(self_test()))
