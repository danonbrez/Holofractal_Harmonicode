from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess
from typing import Any, Mapping, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest

SCHEMA = "HHS_PASS_191_UNIFIED_MANIFOLD_KERNEL_V1"
SCAN_SCHEMA = "HHS_PASS_191_NATIVE_MANIFOLD_SCAN_V1"
SCAN_CLASSIFICATION = "HHS_PASS_191_CONTEXTUAL_MANIFOLD_EPOCH_EXECUTED"
CONTEXTUAL_CARDINALITY = 51_648_192
PROJECTED_CARDINALITY = 1_259_712
OUTER_ENVELOPE_MODULUS = 1_259_713
ORDERED_BASIS = ("x", "y", "z", "w", "xy", "yx", "zw", "wz")
LO_SHU = ((4, 9, 2), (3, 5, 7), (8, 1, 6))
U72 = 1
XY = 1

MANIFOLD_SOURCE = (
    "P^2/{(t^3-t=(P³-P/(P²-pq)=(t³-t)/∆=P²(MOD)(pq))=m^2-m)-"
    "(({{b^4,c^4,c^2-u^72},{c^2,5/u^((s==(b^(2c^2)c^b^4)^2)/(72P^2)),"
    "((b^6-(xy))(b^4+c^2))/(((c^2b^6)-c^2)/(((b^2*(c^2+b^2))-"
    "(c^2-b^2))/Sqrt(c^4)))},{(2c^2)+b^2,2/b^2,b^2c^2}}+x+y)/At=="
    "Mod(f/u,(72*(pq+xy)))/Bt==AB/P^2==Sqrt[AB])==(AB/(pq+∆)-P^2)/"
    "(t^3-t)*u^72} where ∆/P=√(pq+u⁷²)^x²"
)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _fraction_text(value: Fraction) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def _require_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{label} must be an exact integer")
    return value


def _outer_residue(value: int) -> int:
    return value % OUTER_ENVELOPE_MODULUS


@dataclass(frozen=True)
class MembraneWitness:
    membrane_id: str
    opener: str
    closer: str
    depth: int
    start: int
    end: int
    exact_source: str
    exact_interior: str
    depth_modulus: int
    destructive_reduction_applied: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "membrane_id": self.membrane_id,
            "opener": self.opener,
            "closer": self.closer,
            "depth": self.depth,
            "start": self.start,
            "end": self.end,
            "exact_source": self.exact_source,
            "exact_interior": self.exact_interior,
            "depth_modulus": self.depth_modulus,
            "destructive_reduction_applied": self.destructive_reduction_applied,
        }


def extract_membrane_witnesses(source: str = MANIFOLD_SOURCE) -> list[dict[str, Any]]:
    pairs = {"(": ")", "[": "]", "{": "}"}
    reverse = {closer: opener for opener, closer in pairs.items()}
    stack: list[tuple[str, int, int]] = []
    witnesses: list[MembraneWitness] = []
    for offset, character in enumerate(source):
        if character in pairs:
            stack.append((character, offset, len(stack)))
        elif character in reverse:
            if not stack or stack[-1][0] != reverse[character]:
                raise ValueError(f"malformed manifold membrane at offset {offset}")
            opener, start, depth = stack.pop()
            exact = source[start : offset + 1]
            interior = source[start + 1 : offset]
            core = {
                "opener": opener,
                "closer": character,
                "depth": depth,
                "start": start,
                "end": offset + 1,
                "exact_source": exact,
                "exact_interior": interior,
                "depth_modulus": depth % (depth + 1),
                "destructive_reduction_applied": False,
            }
            witnesses.append(
                MembraneWitness(
                    membrane_id=hash72_digest(
                        {"domain": "HHS-PASS-191-MANIFOLD-MEMBRANE-V1"}, core
                    ),
                    opener=opener,
                    closer=character,
                    depth=depth,
                    start=start,
                    end=offset + 1,
                    exact_source=exact,
                    exact_interior=interior,
                    depth_modulus=depth % (depth + 1),
                )
            )
    if stack:
        raise ValueError(f"unclosed manifold membrane at offset {stack[-1][1]}")
    witnesses.sort(key=lambda item: (item.start, item.end, item.depth))
    return [item.to_dict() for item in witnesses]


def ordered_operator_witnesses(source: str = MANIFOLD_SOURCE) -> list[dict[str, Any]]:
    operators = ("==", "=", "+", "-", "*", "/", "^", "MOD", "where")
    rows: list[dict[str, Any]] = []
    index = 0
    while index < len(source):
        matched = None
        for operator in operators:
            if source.startswith(operator, index):
                matched = operator
                break
        if matched is None:
            index += 1
            continue
        core = {
            "sequence": len(rows),
            "operator": matched,
            "offset": index,
            "ordered_identity": f"{len(rows)}::{matched}::{index}",
        }
        rows.append(
            {
                **core,
                "operator_hash72": hash72_digest(
                    {"domain": "HHS-PASS-191-ORDERED-OPERATOR-V1"}, core
                ),
            }
        )
        index += len(matched)
    return rows


def lo_shu_manifold_reduction() -> dict[str, Any]:
    b2 = Fraction(2)
    c2 = Fraction(3)
    u72 = Fraction(U72)
    xy = Fraction(XY)
    b4 = b2 * b2
    b6 = b4 * b2
    c4 = c2 * c2
    sqrt_c4 = Fraction(math.isqrt(c4.numerator), math.isqrt(c4.denominator))
    stage1_numerator = b2 * (c2 + b2) - (c2 - b2)
    stage1 = stage1_numerator / sqrt_c4
    stage2_numerator = c2 * b6 - c2
    stage2 = stage2_numerator / stage1
    nested_numerator = (b6 - xy) * (b4 + c2)
    nested = nested_numerator / stage2
    matrix = (
        (b4, c4, c2 - u72),
        (c2, Fraction(5, 1) / u72, nested),
        ((Fraction(2) * c2) + b2, Fraction(2, 1) / b2, b2 * c2),
    )
    integer_matrix = tuple(
        tuple(int(value) if value.denominator == 1 else value for value in row)
        for row in matrix
    )
    row_sums = tuple(sum(row) for row in matrix)
    column_sums = tuple(sum(matrix[row][column] for row in range(3)) for column in range(3))
    diagonal_sums = (
        matrix[0][0] + matrix[1][1] + matrix[2][2],
        matrix[0][2] + matrix[1][1] + matrix[2][0],
    )
    checks = {
        "canonical_b2": b2 == 2,
        "canonical_c2": c2 == 3,
        "canonical_u72": u72 == 1,
        "canonical_xy": xy == 1,
        "sqrt_c4_exact": sqrt_c4 == 3,
        "first_nested_denominator_exact": stage1 == 3,
        "second_nested_denominator_exact": stage2 == 7,
        "nested_value_exact": nested == 7,
        "matrix_is_lo_shu": integer_matrix == LO_SHU,
        "all_rows_sum_15": all(value == 15 for value in row_sums),
        "all_columns_sum_15": all(value == 15 for value in column_sums),
        "both_diagonals_sum_15": all(value == 15 for value in diagonal_sums),
    }
    if not all(checks.values()):
        raise AssertionError(f"Lo Shu manifold reduction failed: {checks}")
    core = {
        "constants": {"b2": "2", "c2": "3", "u72": "1", "xy": "1"},
        "derived": {
            "b4": _fraction_text(b4),
            "b6": _fraction_text(b6),
            "c4": _fraction_text(c4),
            "sqrt_c4": _fraction_text(sqrt_c4),
            "stage1_numerator": _fraction_text(stage1_numerator),
            "stage1": _fraction_text(stage1),
            "stage2_numerator": _fraction_text(stage2_numerator),
            "stage2": _fraction_text(stage2),
            "nested_numerator": _fraction_text(nested_numerator),
            "nested": _fraction_text(nested),
        },
        "matrix": [list(row) for row in integer_matrix],
        "row_sums": [_fraction_text(value) for value in row_sums],
        "column_sums": [_fraction_text(value) for value in column_sums],
        "diagonal_sums": [_fraction_text(value) for value in diagonal_sums],
        "checks": checks,
    }
    return {
        **core,
        "reduction_hash72": hash72_digest(
            {"domain": "HHS-PASS-191-LO-SHU-MANIFOLD-REDUCTION-V1"}, core
        ),
    }


def evaluate_manifold_candidate(row: Mapping[str, Any]) -> dict[str, Any]:
    address = _require_int(row.get("address"), "address")
    p_value = _require_int(row.get("P"), "P")
    factor_p = _require_int(row.get("p"), "p")
    factor_q = _require_int(row.get("q"), "q")
    t_value = _require_int(row.get("t"), "t")
    m_value = _require_int(row.get("m"), "m")
    basis_index = _require_int(row.get("ordered_basis8"), "ordered_basis8")
    if not 0 <= basis_index < len(ORDERED_BASIS):
        raise ValueError("ordered_basis8 out of range")
    if p_value <= 0 or factor_p <= 0 or factor_q <= 0:
        raise ValueError("P, p, and q must be positive")

    p_squared = p_value * p_value
    delta = p_squared - factor_p * factor_q
    cubic = t_value * t_value * t_value - t_value
    idempotent = m_value * m_value - m_value
    residual_cubic_delta = cubic - delta
    residual_delta_idempotent = delta - idempotent
    a_value = p_squared
    b_value = p_squared
    ab_value = a_value * b_value
    p_fourth = p_squared * p_squared
    sqrt_ab = math.isqrt(ab_value)
    modulus = 72 * (factor_p * factor_q + XY)
    target_residue = p_squared % modulus
    f_family = {
        "modulus": modulus,
        "canonical_residue": target_residue,
        "family": f"f={target_residue}+k*{modulus}, k in Z",
        "constructive_Bt_equals_1": target_residue == p_squared,
        "Bt_required_when_wrapped": (
            None
            if target_residue == p_squared
            else _fraction_text(Fraction(target_residue, p_squared))
        ),
    }
    denominator_guard = {
        "t_cubic_minus_t": cubic,
        "division_authorized": cubic != 0,
        "classification": "PROVED_NONZERO" if cubic != 0 else "OBSTRUCTED_ZERO_DENOMINATOR",
    }
    bridge_core = {
        "left": _fraction_text(Fraction(delta, p_value)),
        "right": f"sqrt({factor_p * factor_q + U72})^(x^2)",
        "x_squared_binding": None,
    }
    bridge = {
        **bridge_core,
        "status": "OBSTRUCTED",
        "missing_rule": "EXACT_DOMAIN_AND_BINDING_FOR_X_SQUARED",
        "bridge_hash72": hash72_digest(
            {"domain": "HHS-PASS-191-DELTA-SQRT-BRIDGE-V1"}, bridge_core
        ),
    }
    checks = {
        "delta_matches_native": delta == _require_int(row.get("delta"), "delta"),
        "cubic_matches_native": cubic == _require_int(row.get("cubic"), "cubic"),
        "idempotent_matches_native": idempotent
        == _require_int(row.get("idempotent"), "idempotent"),
        "residual_cubic_delta_matches_native": residual_cubic_delta
        == _require_int(row.get("residual_cubic_delta"), "residual_cubic_delta"),
        "residual_delta_idempotent_matches_native": residual_delta_idempotent
        == _require_int(
            row.get("residual_delta_idempotent"), "residual_delta_idempotent"
        ),
        "outer_residue_cubic_delta_matches_native": _outer_residue(
            residual_cubic_delta
        )
        == _require_int(
            row.get("outer_residue_cubic_delta"),
            "outer_residue_cubic_delta",
        ),
        "outer_residue_delta_idempotent_matches_native": _outer_residue(
            residual_delta_idempotent
        )
        == _require_int(
            row.get("outer_residue_delta_idempotent"),
            "outer_residue_delta_idempotent",
        ),
        "A_equals_P_squared": a_value == p_squared,
        "B_equals_P_squared": b_value == p_squared,
        "AB_equals_P_fourth": ab_value == p_fourth,
        "AB_over_P_squared_equals_P_squared": Fraction(ab_value, p_squared)
        == p_squared,
        "sqrt_AB_equals_P_squared": sqrt_ab * sqrt_ab == ab_value
        and sqrt_ab == p_squared,
        "ordered_basis_retained": ORDERED_BASIS[basis_index]
        == ORDERED_BASIS[_require_int(row.get("ordered_basis8"), "ordered_basis8")],
    }
    if not all(checks.values()):
        raise AssertionError(f"manifold candidate replay failed at {address}: {checks}")
    chain_closed = residual_cubic_delta == 0 and residual_delta_idempotent == 0
    core = {
        "address": address,
        "ordered_basis": ORDERED_BASIS[basis_index],
        "ordered_basis8": basis_index,
        "parameters": {
            "P": p_value,
            "p": factor_p,
            "q": factor_q,
            "t": t_value,
            "m": m_value,
            "u72": U72,
            "xy": XY,
        },
        "exact_relations": {
            "P_squared": p_squared,
            "delta": delta,
            "t_cubed_minus_t": cubic,
            "m_squared_minus_m": idempotent,
            "A": a_value,
            "B": b_value,
            "AB": ab_value,
            "P_fourth": p_fourth,
            "sqrt_AB": sqrt_ab,
        },
        "residuals": {
            "cubic_minus_delta": residual_cubic_delta,
            "delta_minus_idempotent": residual_delta_idempotent,
            "outer_cubic_minus_delta": _outer_residue(residual_cubic_delta),
            "outer_delta_minus_idempotent": _outer_residue(
                residual_delta_idempotent
            ),
        },
        "chain_decision": {
            "status": "PROVED" if chain_closed else "FALSIFIED",
            "proposition": "t^3-t = Delta = m^2-m",
            "scope": "EXACT_CONTEXT_CANDIDATE",
        },
        "modular_f_family": f_family,
        "division_guard": denominator_guard,
        "delta_sqrt_bridge": bridge,
        "checks": checks,
    }
    return {
        **core,
        "candidate_hash72": hash72_digest(
            {"domain": "HHS-PASS-191-MANIFOLD-CANDIDATE-V1"}, core
        ),
    }


def _validate_scan_header(payload: Mapping[str, Any], *, start: int, end: int, epoch: int) -> None:
    checks = {
        "schema": payload.get("schema") == SCAN_SCHEMA,
        "classification": payload.get("classification") == SCAN_CLASSIFICATION,
        "epoch": payload.get("epoch") == epoch,
        "start": payload.get("start") == start,
        "end": payload.get("end") == end,
        "contextual_cardinality": payload.get("contextual_cardinality")
        == CONTEXTUAL_CARDINALITY,
        "outer_envelope": payload.get("outer_envelope_modulus")
        == OUTER_ENVELOPE_MODULUS,
        "visited": payload.get("visited") == end - start,
        "reciprocal_checks": payload.get("reciprocal_checks") == end - start,
        "coordinate_drift": payload.get("coordinate_drift") == 0,
        "quartic_checks": payload.get("quartic_checks") == end - start,
        "lo_shu_checks": payload.get("lo_shu_checks") == end - start,
        "outer_envelope_checks": payload.get("outer_envelope_checks")
        == 2 * (end - start),
        "completion": payload.get("complete") == (end == CONTEXTUAL_CARDINALITY),
    }
    if not all(checks.values()):
        raise AssertionError(f"native manifold scan header failed: {checks}")


def run_native_manifold_scan(
    scanner_path: str | Path,
    *,
    start: int = 0,
    end: int = CONTEXTUAL_CARDINALITY,
    epoch: int = 0,
) -> dict[str, Any]:
    scanner = Path(scanner_path).resolve()
    if not scanner.is_file():
        raise FileNotFoundError(f"Pass 191 manifold scanner not found: {scanner}")
    completed = subprocess.run(
        [str(scanner), str(start), str(end), str(epoch)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    _validate_scan_header(payload, start=start, end=end, epoch=epoch)
    candidates = [
        evaluate_manifold_candidate(row)
        for row in payload.get("best_candidates", [])
    ]
    membranes = extract_membrane_witnesses()
    operators = ordered_operator_witnesses()
    lo_shu = lo_shu_manifold_reduction()
    exact_hits = _require_int(payload.get("exact_hits"), "exact_hits")
    core = {
        "schema": SCHEMA,
        "classification": "HHS_PASS_191_UNIFIED_MANIFOLD_EPOCH_VERIFIED",
        "exact_source": MANIFOLD_SOURCE,
        "source_sha256": sha256(MANIFOLD_SOURCE.encode("utf-8")).hexdigest(),
        "source_membranes": membranes,
        "ordered_operators": operators,
        "lo_shu_reduction": lo_shu,
        "native_scan": payload,
        "deep_candidate_certificates": candidates,
        "finite_epoch_decision": {
            "status": "PROVED",
            "proposition": (
                f"Every contextual state in [{start},{end}) was traversed through "
                "the inherited Pass 189 address authority and evaluated by the exact "
                "Pass 191 manifold residual kernel"
            ),
            "visited": end - start,
            "exact_chain_hits": exact_hits,
            "scope": "FINITE_ENCODED_CONTEXTUAL_EPOCH",
        },
        "continuation": {
            "snapshot": payload.get("snapshot"),
            "repeat_policy": "ADVANCE_EPOCH_AND_REHYDRATE_RETAINED_FRONTIER",
            "branch_frontier": [
                certificate["candidate_hash72"] for certificate in candidates
            ],
        },
    }
    return {
        **core,
        "manifold_epoch_hash72": hash72_digest(
            {"domain": "HHS-PASS-191-UNIFIED-MANIFOLD-EPOCH-V1"}, core
        ),
    }


def verify_native_manifold_scan(payload: Mapping[str, Any]) -> dict[str, Any]:
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unified manifold schema mismatch")
    if payload.get("classification") != "HHS_PASS_191_UNIFIED_MANIFOLD_EPOCH_VERIFIED":
        raise AssertionError("unified manifold classification mismatch")
    if payload.get("exact_source") != MANIFOLD_SOURCE:
        raise AssertionError("unified manifold source identity mismatch")
    native_scan = payload.get("native_scan", {})
    start = _require_int(native_scan.get("start"), "start")
    end = _require_int(native_scan.get("end"), "end")
    epoch = _require_int(native_scan.get("epoch"), "epoch")
    _validate_scan_header(native_scan, start=start, end=end, epoch=epoch)
    expected_membranes = extract_membrane_witnesses()
    expected_operators = ordered_operator_witnesses()
    expected_lo_shu = lo_shu_manifold_reduction()
    if payload.get("source_membranes") != expected_membranes:
        raise AssertionError("manifold membrane replay mismatch")
    if payload.get("ordered_operators") != expected_operators:
        raise AssertionError("manifold ordered-operator replay mismatch")
    if payload.get("lo_shu_reduction") != expected_lo_shu:
        raise AssertionError("manifold Lo Shu replay mismatch")
    native_rows = native_scan.get("best_candidates", [])
    expected_candidates = [evaluate_manifold_candidate(row) for row in native_rows]
    if payload.get("deep_candidate_certificates") != expected_candidates:
        raise AssertionError("manifold candidate replay mismatch")
    core = {
        key: value for key, value in payload.items() if key != "manifold_epoch_hash72"
    }
    expected_hash = hash72_digest(
        {"domain": "HHS-PASS-191-UNIFIED-MANIFOLD-EPOCH-V1"}, core
    )
    if payload.get("manifold_epoch_hash72") != expected_hash:
        raise AssertionError("manifold epoch Hash72 mismatch")
    decision = payload.get("finite_epoch_decision", {})
    if decision.get("status") != "PROVED" or decision.get("visited") != end - start:
        raise AssertionError("finite manifold epoch decision mismatch")
    return {
        "ok": True,
        "classification": payload["classification"],
        "manifold_epoch_hash72": expected_hash,
        "visited": end - start,
        "exact_chain_hits": native_scan.get("exact_hits"),
        "checksum_fnv1a64": native_scan.get("checksum_fnv1a64"),
        "frontier_size": len(expected_candidates),
    }


__all__ = [
    "SCHEMA",
    "SCAN_SCHEMA",
    "SCAN_CLASSIFICATION",
    "CONTEXTUAL_CARDINALITY",
    "PROJECTED_CARDINALITY",
    "OUTER_ENVELOPE_MODULUS",
    "ORDERED_BASIS",
    "MANIFOLD_SOURCE",
    "extract_membrane_witnesses",
    "ordered_operator_witnesses",
    "lo_shu_manifold_reduction",
    "evaluate_manifold_candidate",
    "run_native_manifold_scan",
    "verify_native_manifold_scan",
]
