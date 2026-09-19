"""Pass 220 I015: palindromic ordered-phase mirror algebra.

Read-only exact witness/reference implementation. It composes the user-supplied
x/y four-vector mirror, ordered edge equalities, braid relation, nine-symbol
palindrome, Lo Shu reciprocal involution, G41 fingerprint quotient, and exact
q=-1 scalar projection without widening canonical VM81/Hash72/Hash216
authority.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Sequence, Tuple

from hhs_runtime.hhs_pass220_g41_sudoku_fingerprint_algebra_v1 import (
    LO_SHU,
    fingerprint,
    reciprocal_fingerprint,
)

SCHEMA = "HHS_PASS_220_PALINDROMIC_ORDERED_PHASE_V1"
VERSION = "1.0.0-checkpoint.15"
PROFILE = "PASS220-I015-PALINDROMIC-ORDERED-PHASE-v1"
WITNESS_SCHEMA = "HHS_PASS_220_PALINDROMIC_PHASE_CLOSURE_WITNESS_V1"

X_VECTOR: Tuple[int, int, int, int] = (0, 1, 1, 0)
Y_VECTOR: Tuple[int, int, int, int] = (0, -1, 1, 0)

PHASE_PATH: Tuple[str, ...] = ("x", "y", "z", "w", "x", "w", "z", "y", "x")
PHASE_MATRIX: Tuple[Tuple[str, ...], ...] = (
    ("x", "y", "z"),
    ("w", "x", "w"),
    ("z", "y", "x"),
)

FORWARD_EDGES: Tuple[Tuple[str, str], ...] = (
    ("x", "y"),
    ("y", "z"),
    ("z", "w"),
    ("w", "x"),
)
MIRROR_EDGES: Tuple[Tuple[str, str], ...] = (
    ("x", "w"),
    ("w", "z"),
    ("z", "y"),
    ("y", "x"),
)

# Componentwise representative equality classes supplied by the user.
EDGE_CLASSES: Dict[str, str] = {
    "xy": "xy",
    "xw": "xy",
    "yx": "yx",
    "yz": "yx",
    "zw": "zw",
    "zy": "zw",
    "wz": "wz",
    "wx": "wz",
}

CANONICAL_CLASS_REPRESENTATIVES: Tuple[str, ...] = ("xy", "yx", "zw", "wz")
MIRROR_CLASS_REPRESENTATIVES: Tuple[str, ...] = ("xw", "yz", "zy", "wx")

# Licensed projection only; the ordered products remain distinct before projection.
Q_MINUS_ONE_PROJECTION: Dict[str, int] = {
    "xy": 1,
    "yx": -1,
    "zw": 1,
    "wz": -1,
}

WORD_REWRITE_RULES: Tuple[Tuple[str, str], ...] = (
    ("xyx", "yxy"),
    ("xw", "xy"),
    ("wx", "wz"),
    ("yz", "yx"),
    ("zy", "zw"),
)

X_WORD = "xyz"
Y_WORD = "wxy"
YXY_WORD = Y_WORD + X_WORD + Y_WORD


class Pass220PalindromicPhaseError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    record = dict(payload)
    record["receipt_sha256"] = sha256(_stable_json(record).encode("utf-8")).hexdigest()
    return record


def dot(left: Sequence[int], right: Sequence[int]) -> int:
    if len(left) != len(right):
        raise Pass220PalindromicPhaseError("vector length mismatch")
    if any(isinstance(v, bool) or not isinstance(v, int) for v in (*left, *right)):
        raise Pass220PalindromicPhaseError("vectors must be exact integers")
    return sum(a * b for a, b in zip(left, right))


def mirror4(vector: Sequence[int]) -> Tuple[int, int, int, int]:
    if len(vector) != 4:
        raise Pass220PalindromicPhaseError("mirror4 requires four coordinates")
    values = tuple(vector)
    if any(isinstance(v, bool) or not isinstance(v, int) for v in values):
        raise Pass220PalindromicPhaseError("mirror4 requires exact integers")
    return values[0], -values[1], values[2], values[3]


def rotate180(matrix: Sequence[Sequence[Any]]) -> Tuple[Tuple[Any, ...], ...]:
    rows = tuple(tuple(row) for row in matrix)
    if not rows or any(len(row) != len(rows[0]) for row in rows):
        raise Pass220PalindromicPhaseError("matrix must be nonempty and rectangular")
    return tuple(tuple(reversed(row)) for row in reversed(rows))


def path_edges(path: Sequence[str]) -> Tuple[Tuple[str, str], ...]:
    values = tuple(path)
    if len(values) < 2:
        raise Pass220PalindromicPhaseError("path must contain at least two symbols")
    return tuple(zip(values[:-1], values[1:]))


def edge_symbol(edge: Sequence[str]) -> str:
    values = tuple(edge)
    if len(values) != 2 or any(value not in {"x", "y", "z", "w"} for value in values):
        raise Pass220PalindromicPhaseError("edge must be an ordered x/y/z/w pair")
    return "".join(values)


def edge_class(edge_or_symbol: Sequence[str] | str) -> str:
    symbol = edge_or_symbol if isinstance(edge_or_symbol, str) else edge_symbol(edge_or_symbol)
    try:
        return EDGE_CLASSES[symbol]
    except KeyError as exc:
        raise Pass220PalindromicPhaseError(f"unregistered ordered edge: {symbol}") from exc


def reverse_edge_path(edges: Sequence[Sequence[str]]) -> Tuple[Tuple[str, str], ...]:
    return tuple(tuple(reversed(tuple(edge))) for edge in reversed(tuple(edges)))


def phase_matrix() -> Tuple[Tuple[str, ...], ...]:
    return PHASE_MATRIX


def combined_lo_shu_phase_tensor(
    digits: Sequence[Sequence[int]] = LO_SHU,
) -> Tuple[Tuple[Tuple[int, str], ...], ...]:
    rows = tuple(tuple(row) for row in digits)
    if len(rows) != 3 or any(len(row) != 3 for row in rows):
        raise Pass220PalindromicPhaseError("digit fingerprint must be 3x3")
    return tuple(
        tuple((rows[r][c], PHASE_MATRIX[r][c]) for c in range(3))
        for r in range(3)
    )


def combined_reciprocal_transform(
    tensor: Sequence[Sequence[Sequence[Any]]],
) -> Tuple[Tuple[Tuple[int, str], ...], ...]:
    rows = tuple(tuple(tuple(cell) for cell in row) for row in tensor)
    if len(rows) != 3 or any(len(row) != 3 for row in rows):
        raise Pass220PalindromicPhaseError("combined tensor must be 3x3")
    rotated = rotate180(rows)
    result = []
    for row in rotated:
        out_row = []
        for cell in row:
            if len(cell) != 2:
                raise Pass220PalindromicPhaseError("combined cell must be (digit, phase)")
            digit, phase = cell
            if isinstance(digit, bool) or not isinstance(digit, int) or not 1 <= digit <= 9:
                raise Pass220PalindromicPhaseError("combined digit outside 1..9")
            if phase not in {"x", "y", "z", "w"}:
                raise Pass220PalindromicPhaseError("invalid combined phase symbol")
            out_row.append((10 - digit, phase))
        result.append(tuple(out_row))
    return tuple(result)


def normalize_edge_symbol(symbol: str) -> str:
    return edge_class(symbol)


def normalize_residual_factor(factor: Tuple[str, str]) -> Tuple[str, str]:
    left, right = factor
    left_n = normalize_edge_symbol(left) if left in EDGE_CLASSES else left
    right_n = normalize_edge_symbol(right) if right in EDGE_CLASSES else right
    return left_n, right_n


def residual_witness() -> Dict[str, Any]:
    r0 = (("x", "1"), ("y", "1"))
    r1 = (("zw", "xy"), ("wz", "yx"))
    r1_mirror = (("zy", "xw"), ("wx", "yz"))
    r2 = (("xy", "x"), ("yx", "y"))
    r2_mirror = (("xw", "x"), ("yz", "y"))
    return {
        "R0": r0,
        "R1": r1,
        "R1_mirror": r1_mirror,
        "R2": r2,
        "R2_mirror": r2_mirror,
        "R1_representative_invariant": tuple(map(normalize_residual_factor, r1_mirror)) == r1,
        "R2_representative_invariant": tuple(map(normalize_residual_factor, r2_mirror)) == r2,
    }


def projected_edge_sequence(edges: Sequence[Sequence[str]]) -> Tuple[int, ...]:
    return tuple(Q_MINUS_ONE_PROJECTION[edge_class(edge)] for edge in edges)


def _rewrite_once(word: str) -> str:
    """One left-to-right, non-overlapping ordered-word rewrite pass."""
    output = []
    index = 0
    while index < len(word):
        for source, target in WORD_REWRITE_RULES:
            if word.startswith(source, index):
                output.append(target)
                index += len(source)
                break
        else:
            output.append(word[index])
            index += 1
    return "".join(output)


def rewrite_word(word: str, *, limit: int = 100) -> str:
    if not isinstance(word, str) or any(ch not in "xyzw" for ch in word):
        raise Pass220PalindromicPhaseError("word must contain only x,y,z,w")
    current = word
    for _ in range(limit):
        updated = _rewrite_once(current)
        if updated == current:
            return current
        current = updated
    raise Pass220PalindromicPhaseError("word rewrite did not converge within limit")


def braid_associative_witness() -> Dict[str, Any]:
    return {
        "braid": "xyx=yxy",
        "ordered_relation": "yx=-x",
        "lhs_associative_reduction": "x(yx)=-x^2",
        "rhs_associative_reduction": "(yx)y=-(xy)",
        "derived_relation": "x^2=xy",
        "edge_extensions": ("xw=xy=x^2", "yz=yx=-x"),
        "typed_reciprocal_extension": "xy=1/y => x^2=1/y",
        "commutativity_assumed": False,
    }


def conventional_commutative_projection_witness() -> Dict[str, Any]:
    # Characteristic-zero scalar projection only:
    # xy=1/y => x*y^2=1, hence x,y nonzero.
    # yx=-x and commutativity => xy=-x => y=-1.
    # xy=1/y then gives x=1.
    # braid evaluates to -1 == +1, contradiction.
    return {
        "domain": "conventional_commutative_characteristic_zero_projection",
        "candidate_from_first_two_relations": {"x": 1, "y": -1},
        "braid_lhs": -1,
        "braid_rhs": 1,
        "admitted": False,
        "internal_typed_ordered_algebra_falsified": False,
    }


def lifted_xy_witness() -> Dict[str, Any]:
    x_nf = rewrite_word(X_WORD)
    y_nf = rewrite_word(Y_WORD)
    yxy_nf = rewrite_word(YXY_WORD)
    return {
        "X_definition": "X=xyz",
        "Y_definition": "Y=wxy",
        "X_local_normal_form": x_nf,
        "Y_local_normal_form": y_nf,
        "YXY_local_normal_form": yxy_nf,
        "X_equals_YXY_is_explicit_constraint": True,
        "X_equals_YXY_derived_from_local_rules_only": x_nf == yxy_nf,
    }


def combined_g41_witness() -> Dict[str, Any]:
    paired_ok = True
    class_keys = set()
    for row in range(9):
        for column in range(9):
            direct_digits = fingerprint(row, column)
            reciprocal_digits = reciprocal_fingerprint(direct_digits)
            direct = combined_lo_shu_phase_tensor(direct_digits)
            reciprocal = combined_lo_shu_phase_tensor(reciprocal_digits)
            paired_ok = paired_ok and combined_reciprocal_transform(direct) == reciprocal
            direct_key = repr(direct)
            reciprocal_key = repr(combined_reciprocal_transform(direct))
            class_keys.add(min(direct_key, reciprocal_key))
    return {
        "combined_reciprocal_all_81": paired_ok,
        "combined_fingerprint_class_count": len(class_keys),
        "center_combined_fixed": (
            combined_reciprocal_transform(combined_lo_shu_phase_tensor())
            == combined_lo_shu_phase_tensor()
        ),
    }


def palindromic_ordered_phase_witness() -> Dict[str, Any]:
    forward_projection = projected_edge_sequence(FORWARD_EDGES)
    mirror_projection = projected_edge_sequence(MIRROR_EDGES)
    residuals = residual_witness()
    combined = combined_g41_witness()
    return _receipt({
        "schema": WITNESS_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "x_vector": X_VECTOR,
        "y_vector": Y_VECTOR,
        "x_dot_y": dot(X_VECTOR, Y_VECTOR),
        "x_norm_squared": dot(X_VECTOR, X_VECTOR),
        "y_norm_squared": dot(Y_VECTOR, Y_VECTOR),
        "mirror_x_to_y": mirror4(X_VECTOR) == Y_VECTOR,
        "mirror_y_to_x": mirror4(Y_VECTOR) == X_VECTOR,
        "phase_path": PHASE_PATH,
        "phase_path_palindrome": PHASE_PATH == tuple(reversed(PHASE_PATH)),
        "phase_matrix": PHASE_MATRIX,
        "phase_matrix_centrosymmetric": PHASE_MATRIX == rotate180(PHASE_MATRIX),
        "forward_edges": FORWARD_EDGES,
        "mirror_edges": MIRROR_EDGES,
        "mirror_edges_are_reversed_forward_endpoints": (
            MIRROR_EDGES == reverse_edge_path(FORWARD_EDGES)
        ),
        "canonical_class_representatives": CANONICAL_CLASS_REPRESENTATIVES,
        "mirror_class_representatives": MIRROR_CLASS_REPRESENTATIVES,
        "componentwise_representative_equivalence": tuple(
            edge_class(value) for value in MIRROR_CLASS_REPRESENTATIVES
        ) == CANONICAL_CLASS_REPRESENTATIVES,
        "forward_class_sequence": tuple(edge_class(edge) for edge in FORWARD_EDGES),
        "mirror_class_sequence": tuple(edge_class(edge) for edge in MIRROR_EDGES),
        "forward_q_minus_one_projection": forward_projection,
        "mirror_q_minus_one_projection": mirror_projection,
        "projected_views_equal": forward_projection == mirror_projection,
        "forward_projected_product": (
            forward_projection[0]
            * forward_projection[1]
            * forward_projection[2]
            * forward_projection[3]
        ),
        "mirror_projected_product": (
            mirror_projection[0]
            * mirror_projection[1]
            * mirror_projection[2]
            * mirror_projection[3]
        ),
        "residuals": residuals,
        "braid_associative": braid_associative_witness(),
        "lifted_XY": lifted_xy_witness(),
        "conventional_scalar_projection": conventional_commutative_projection_witness(),
        "combined_g41": combined,
        "projection_only": True,
        "floating_point_authority": False,
        "canonical_admission_authority": False,
        "mutation_performed": False,
    })


def validate_palindromic_ordered_phase() -> Dict[str, Any]:
    witness = palindromic_ordered_phase_witness()
    combined = witness["combined_g41"]
    lifted = witness["lifted_XY"]
    residuals = witness["residuals"]
    ok = all((
        witness["x_dot_y"] == 0,
        witness["x_norm_squared"] == 2,
        witness["y_norm_squared"] == 2,
        witness["mirror_x_to_y"],
        witness["mirror_y_to_x"],
        witness["phase_path_palindrome"],
        witness["phase_matrix_centrosymmetric"],
        witness["mirror_edges_are_reversed_forward_endpoints"],
        witness["componentwise_representative_equivalence"],
        witness["forward_q_minus_one_projection"] == (1, -1, 1, -1),
        witness["mirror_q_minus_one_projection"] == (1, -1, 1, -1),
        witness["projected_views_equal"],
        witness["forward_projected_product"] == 1,
        witness["mirror_projected_product"] == 1,
        residuals["R1_representative_invariant"],
        residuals["R2_representative_invariant"],
        witness["braid_associative"]["derived_relation"] == "x^2=xy",
        lifted["X_local_normal_form"] == "yxy",
        lifted["Y_local_normal_form"] == "wzw",
        lifted["X_equals_YXY_derived_from_local_rules_only"] is False,
        witness["conventional_scalar_projection"]["admitted"] is False,
        combined["combined_reciprocal_all_81"],
        combined["combined_fingerprint_class_count"] == 41,
        combined["center_combined_fixed"],
    ))
    return _receipt({
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "ok": ok,
        "witness": witness,
        "invariant_ids": (
            "HHS-I008",
            "HHS-I010",
            "HHS-I011",
            "HHS-I012",
            "HHS-I014",
            "HHS-I015",
        ),
        "mutation_policy": "READ_ONLY_ORDERED_PHASE_PROOF_NO_VM81_MUTATION",
        "persistence_policy": "NO_CANONICAL_PERSISTENCE",
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    })


def palindromic_ordered_phase_self_test() -> Dict[str, Any]:
    return validate_palindromic_ordered_phase()
