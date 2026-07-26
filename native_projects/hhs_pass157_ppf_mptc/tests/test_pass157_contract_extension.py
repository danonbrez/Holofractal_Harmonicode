from __future__ import annotations

import unittest

from hhs_pass157.model import (
    CENTERLINE_LABELS,
    DENOMINATIONS,
    GEAR_WORDS,
    construct_exact,
    construct_exact_radius,
    construct_factorial_ratio_matrix,
    construct_loshu,
    construct_phase_nucleus,
    fibonacci_square_value,
    validate_loshu,
    validate_sudoku_x,
)
from hhs_pass157.parser import compile_membrane, parse_source
from hhs_pass157.public_api import (
    bind_local_hamiltonians,
    bind_vm81,
    commit_hash216,
    expand_fibonacci_square,
    normalize_u72,
    replay_pass157,
    verify_pass157,
)


class Pass157ContractExtensionPositive(unittest.TestCase):
    def test_phase_reciprocal_one_over_zero(self):
        parsed = parse_source("1/0")
        self.assertFalse(parsed.diagnostics)
        self.assertEqual(parsed.tokens[0].kind, "PHASE_RECIPROCAL")

    def test_phase_reciprocal_zero_inverse(self):
        compiled = compile_membrane("0^-1")
        self.assertTrue(compiled["phase_reciprocal_dispatch"])

    def test_centerline_operator(self):
        source = "x+y<zw<x<z<yx<wz<y<w<xy<b^2<c^2"
        compiled = compile_membrane(source)
        self.assertEqual(compiled["centerline_operator"], "CENTER_LINE_PHASE_PRECEDES")

    def test_ordered_gear_words(self):
        parsed = parse_source("xy yx zw wz")
        words = [token.text for token in parsed.tokens if token.kind == "ORDERED_GEAR_WORD"]
        self.assertEqual(tuple(words), GEAR_WORDS)

    def test_modular_normalization_node(self):
        compiled = compile_membrane("P^2(MOD)(pq)")
        nodes = [node for node in compiled["typed_ast"] if node["node"] == "HHS_MODULAR_NORMALIZATION"]
        self.assertTrue(nodes)
        self.assertTrue(any(node.get("authority") == "P^2" for node in nodes))

    def test_phase_nucleus_closure(self):
        nucleus = construct_phase_nucleus(72)
        self.assertTrue(nucleus.rotation_closed)
        self.assertEqual(nucleus.phase_index, 0)
        self.assertNotEqual(nucleus.fold_zero, nucleus.scalar_zero)

    def test_fibonacci_square_sequence(self):
        self.assertEqual(tuple(fibonacci_square_value(i) for i in range(7)), (1, 2, 3, 5, 8, 13, 21))

    def test_exact_radical_carrier(self):
        radical = construct_exact_radius(8)
        self.assertEqual(radical.normalized, "2*sqrt(2)")
        self.assertTrue(radical.authoritative)

    def test_factorial_ratio_matrix(self):
        matrix = construct_factorial_ratio_matrix(8, (3, 3))
        self.assertEqual(len(matrix), 3)
        self.assertTrue(all(cell.denominator == 1 for row in matrix for cell in row))

    def test_loshu_constructor_witnesses(self):
        cells = construct_loshu()
        self.assertEqual(tuple(cell.value for cell in cells), (4, 9, 2, 3, 5, 7, 8, 1, 6))
        self.assertTrue(all(cell.constructor for cell in cells))
        self.assertTrue(validate_loshu(cells))

    def test_diagonal_sudoku(self):
        self.assertTrue(validate_sudoku_x())

    def test_vm81_complete(self):
        vm81 = bind_vm81()
        self.assertTrue(vm81["complete"])
        self.assertEqual(vm81["vm81_cell_count"], 81)
        self.assertEqual({cell["vm81_address"] for cell in vm81["cells"]}, set(range(81)))

    def test_all_denominations_present(self):
        vm81 = bind_vm81()
        self.assertEqual({cell["denomination"] for cell in vm81["cells"]}, set(DENOMINATIONS))

    def test_hamiltonian_binding_complete(self):
        bindings = bind_local_hamiltonians()
        self.assertTrue(bindings["complete"])
        self.assertEqual(bindings["binding_count"], 81)
        self.assertTrue(all(binding["hamiltonian_ref"].startswith("H[") for binding in bindings["bindings"]))

    def test_three_hash72_lanes_form_hash216(self):
        commitment = commit_hash216()
        self.assertEqual(len(commitment["lanes"]), 3)
        self.assertTrue(all(len(lane) == 72 for lane in commitment["lanes"].values()))
        self.assertEqual(len(commitment["hash216"]), 216)

    def test_replay_match(self):
        receipt = verify_pass157()
        replay = replay_pass157(receipt)
        self.assertTrue(replay["match"])
        self.assertEqual(replay["classification"], "PASS157_REPLAY_MATCH")

    def test_complete_exact_state(self):
        exact = construct_exact(
            P=5, p=2, q=3, euclid_m=3, euclid_n=2,
            full_rotation=72, local_modulus=72,
            centerline=tuple(range(1, len(CENTERLINE_LABELS) + 1)),
        )
        self.assertEqual(len(exact.vm81_phase_tensor), 81)
        self.assertEqual(len(exact.hash216_commitment), 216)


class Pass157ContractExtensionNegative(unittest.TestCase):
    def test_generic_zero_denominator_not_promoted(self):
        parsed = parse_source("3/0")
        self.assertTrue(parsed.diagnostics)
        self.assertEqual(parsed.tokens[0].kind, "INVALID_NUMBER")

    def test_centerline_reorder_rejected(self):
        exact = tuple(range(1, len(CENTERLINE_LABELS) + 1))
        bad = list(exact)
        bad[5], bad[6] = bad[6], bad[5]
        with self.assertRaises(ValueError):
            construct_exact(
                P=5, p=2, q=3, euclid_m=3, euclid_n=2,
                full_rotation=72, local_modulus=72, centerline=tuple(bad),
            )

    def test_negative_radical_requires_complex_carrier(self):
        with self.assertRaises(ValueError):
            construct_exact_radius(-1)

    def test_factorial_bound(self):
        with self.assertRaisesRegex(ValueError, "FACTORIAL_BOUNDED"):
            construct_factorial_ratio_matrix(4096, (2, 2))

    def test_bad_matrix_dimensions(self):
        with self.assertRaises(ValueError):
            construct_factorial_ratio_matrix(8, (10, 1))

    def test_replay_mismatch(self):
        replay = replay_pass157({"hash216": "wrong"})
        self.assertFalse(replay["match"])
        self.assertEqual(replay["classification"], "REPLAY_MISMATCH")

    def test_normalize_requires_typed_state(self):
        with self.assertRaises(TypeError):
            normalize_u72("72")

    def test_scalar_pivot_types_do_not_collapse(self):
        nucleus = construct_phase_nucleus(72)
        self.assertNotEqual(nucleus.scalar_zero, nucleus.fold_zero)
        self.assertNotEqual(nucleus.scalar_one, nucleus.renewed_one)


if __name__ == "__main__":
    unittest.main()
