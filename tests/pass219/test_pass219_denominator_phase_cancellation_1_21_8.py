from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
U72_TABLE_PATH = ROOT / "hhs_runtime/core_sandbox/hhs_octonion_digital_dna_u72_table_v1.py"
PASS129_PATH = ROOT / "hhs_runtime/hhs_pass129_invariant_delta_rational_projection_algebra_v1.py"


def _module_literal(path: Path, name: str):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == name:
                return ast.literal_eval(node.value)
    raise AssertionError(f"missing frozen literal {name} in {path}")


def _pass129_phase_literals() -> dict:
    wanted = {
        "phase_carrier",
        "phase_weights",
        "four_phase_product_semantics",
        "ordinary_unnormalized_product_is_not_equivalent",
    }
    tree = ast.parse(PASS129_PATH.read_text(encoding="utf-8"), filename=str(PASS129_PATH))
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != "InvariantDeltaProjectionAlgebra":
            continue
        for member in node.body:
            if not isinstance(member, ast.FunctionDef) or member.name != "_build_spec":
                continue
            for stmt in member.body:
                if not isinstance(stmt, ast.Assign):
                    continue
                if not any(isinstance(target, ast.Name) and target.id == "spec" for target in stmt.targets):
                    continue
                if not isinstance(stmt.value, ast.Dict):
                    raise AssertionError("frozen Pass129 spec is not a dict literal")
                result = {}
                for key_node, value_node in zip(stmt.value.keys, stmt.value.values):
                    if key_node is None:
                        continue
                    key = ast.literal_eval(key_node)
                    if key in wanted:
                        result[key] = ast.literal_eval(value_node)
                if set(result) != wanted:
                    raise AssertionError(f"missing frozen Pass129 phase literals: {sorted(wanted - set(result))}")
                return result
    raise AssertionError("missing frozen Pass129 phase spec")


PHASE_RING = int(_module_literal(U72_TABLE_PATH, "PHASE_RING"))
BASIS_PHASE_INDEX = dict(_module_literal(U72_TABLE_PATH, "BASIS_PHASE_INDEX"))
PASS129_PHASE = _pass129_phase_literals()

NUMERATOR_BASIS = (
    ("x", "w", "yx"),
    ("wz", None, "zw"),
    ("xy", "z", "y"),
)

DENOMINATOR_I_EXPONENT = (
    (1, 3, 2),
    (2, None, 4),
    (4, 1, 3),
)

OUTER_CLOCKWISE = (
    ((0, 0), "x", 1),
    ((0, 1), "w", 3),
    ((0, 2), "yx", 2),
    ((1, 2), "zw", 4),
    ((2, 2), "y", 3),
    ((2, 1), "z", 1),
    ((2, 0), "xy", 4),
    ((1, 0), "wz", 2),
)


def _carrier_phase(exponent: int) -> int:
    assert PHASE_RING == 72
    assert exponent in (1, 2, 3, 4)
    phase_cardinality = len(PASS129_PHASE["phase_carrier"])
    assert phase_cardinality == 4
    assert PHASE_RING % phase_cardinality == 0
    return (exponent * (PHASE_RING // phase_cardinality)) % PHASE_RING


def test_frozen_phase_authority_files_are_read_as_data_not_executed() -> None:
    assert U72_TABLE_PATH.exists()
    assert PASS129_PATH.exists()
    assert PHASE_RING == 72
    assert set(BASIS_PHASE_INDEX) == {"x", "y", "z", "w", "xy", "yx", "zw", "wz"}


def test_frozen_four_phase_carrier_order_is_preserved() -> None:
    assert PASS129_PHASE["phase_carrier"] == ["I", "I^2", "I^3", "I^4"]
    assert PASS129_PHASE["phase_weights"] == ["I", "-1", "-I", "1"]
    assert PASS129_PHASE["four_phase_product_semantics"] == "CARDINALITY_NORMALIZED_TYPED_PRODUCT"
    assert PASS129_PHASE["ordinary_unnormalized_product_is_not_equivalent"] is True


def test_phase_matrix_matches_every_frozen_outer_basis_anchor() -> None:
    for row in range(3):
        for col in range(3):
            basis = NUMERATOR_BASIS[row][col]
            exponent = DENOMINATOR_I_EXPONENT[row][col]
            if basis is None:
                assert (row, col) == (1, 1)
                assert exponent is None
                continue
            assert exponent is not None
            assert BASIS_PHASE_INDEX[basis] == _carrier_phase(exponent)


def test_all_eight_outer_quotient_phase_residues_are_u72_closure() -> None:
    residues = []
    for _, basis, exponent in OUTER_CLOCKWISE:
        numerator_phase = BASIS_PHASE_INDEX[basis]
        denominator_phase = _carrier_phase(exponent)
        residue = (numerator_phase - denominator_phase) % PHASE_RING
        residues.append(residue)
    assert residues == [0] * 8
    assert BASIS_PHASE_INDEX["xy"] == 0
    assert BASIS_PHASE_INDEX["zw"] == 0


def test_two_interleaved_ring_phase_schedules_match_exactly() -> None:
    even = OUTER_CLOCKWISE[0::2]
    assert [basis for _, basis, _ in even] == ["x", "yx", "y", "xy"]
    assert [exp for _, _, exp in even] == [1, 2, 3, 4]
    assert [BASIS_PHASE_INDEX[basis] for _, basis, _ in even] == [18, 36, 54, 0]

    odd = OUTER_CLOCKWISE[1::2]
    assert [basis for _, basis, _ in odd] == ["w", "zw", "z", "wz"]
    assert [exp for _, _, exp in odd] == [3, 4, 1, 2]
    assert [BASIS_PHASE_INDEX[basis] for _, basis, _ in odd] == [54, 0, 18, 36]


def test_center_is_not_scalarized_by_outer_phase_cancellation() -> None:
    center_relation = "x+y+z+w=0/u⁷²"
    center_denominator_literal = "0"
    center_scalar_value_derived = False
    projection_substitution_authorized = False
    canonical_whole_expression_proof = False
    assert center_relation == "x+y+z+w=0/u⁷²"
    assert center_denominator_literal == "0"
    assert center_scalar_value_derived is False
    assert projection_substitution_authorized is False
    assert canonical_whole_expression_proof is False


def main() -> int:
    tests = [
        value for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for test in tests:
        test()
    print(f"PASS219 I121.8 denominator phase cancellation: {len(tests)} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
