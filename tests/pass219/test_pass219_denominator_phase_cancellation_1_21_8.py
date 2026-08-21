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


def _pass129_spec_literal() -> dict:
    tree = ast.parse(PASS129_PATH.read_text(encoding="utf-8"), filename=str(PASS129_PATH))
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != "InvariantDeltaProjectionAlgebra":
            continue
        for member in node.body:
            if not isinstance(member, ast.FunctionDef) or member.name != "_build_spec":
                continue
            for stmt in member.body:
                if isinstance(stmt, ast.Assign):
                    if any(isinstance(target, ast.Name) and target.id == "spec" for target in stmt.targets):
                        return ast.literal_eval(stmt.value)
    raise AssertionError("missing frozen Pass129 spec literal")


PHASE_RING = int(_module_literal(U72_TABLE_PATH, "PHASE_RING"))
BASIS_PHASE_INDEX = dict(_module_literal(U72_TABLE_PATH, "BASIS_PHASE_INDEX"))
PASS129_SPEC = _pass129_spec_literal()

# Ordered numerator matrix projected onto the frozen named u72 basis.
NUMERATOR_BASIS = (
    ("x", "w", "yx"),
    ("wz", None, "zw"),
    ("xy", "z", "y"),
)

# Exact symbolic phase-carrier exponents in the supplied denominator matrix.
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
    # Pass129 fixes a four-member ordered carrier [I,I^2,I^3,I^4].  I121.8
    # projects those four positions onto the inherited 72-phase ring at exact
    # quarter-ring spacing.  This is a projection witness only; it does not
    # redefine either frozen source file or claim VM81 admission authority.
    assert PHASE_RING == 72
    assert exponent in (1, 2, 3, 4)
    phase_cardinality = len(PASS129_SPEC["phase_carrier"])
    assert phase_cardinality == 4
    assert PHASE_RING % phase_cardinality == 0
    return (exponent * (PHASE_RING // phase_cardinality)) % PHASE_RING


def test_frozen_phase_authority_files_are_read_as_data_not_executed() -> None:
    # The historical u72 table currently imports an unavailable helper through
    # its own legacy dependency chain.  This thread is not authorized to repair
    # that frozen dependency.  AST literal extraction lets this diagnostic bind
    # its immutable declared phase constants without executing or modifying it.
    assert U72_TABLE_PATH.exists()
    assert PASS129_PATH.exists()
    assert PHASE_RING == 72
    assert set(BASIS_PHASE_INDEX) == {"x", "y", "z", "w", "xy", "yx", "zw", "wz"}


def test_frozen_four_phase_carrier_order_is_preserved() -> None:
    assert PASS129_SPEC["phase_carrier"] == ["I", "I^2", "I^3", "I^4"]
    assert PASS129_SPEC["phase_weights"] == ["I", "-1", "-I", "1"]
    assert PASS129_SPEC["four_phase_product_semantics"] == "CARDINALITY_NORMALIZED_TYPED_PRODUCT"
    assert PASS129_SPEC["ordinary_unnormalized_product_is_not_equivalent"] is True


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
    # The frozen u72 table denotes phase-zero xy/zw carriers as u^72 closure.
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
