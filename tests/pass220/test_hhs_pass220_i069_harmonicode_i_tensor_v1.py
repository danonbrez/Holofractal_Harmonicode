from __future__ import annotations

import copy
import unittest

from hhs_runtime.hhs_pass220_i069_harmonicode_i_tensor_v1 import (
    AUTHORITY_BOUNDARY,
    E_VECTOR,
    EXPECTED_A,
    EXPECTED_B,
    EXPECTED_C,
    LO_SHU,
    Pass220I069TensorError,
    VERBATIM_SOURCE,
    generator_descriptor,
    lo_shu_route,
    materialize_projection,
    matrix_a,
    matrix_b,
    matrix_c,
    phase_kernel,
    self_test,
    validate_projection,
)


class I069HarmonicodeITensorTests(unittest.TestCase):
    def test_verbatim_source_preserves_native_surface(self) -> None:
        self.assertIn("MatrixTimes", VERBATIM_SOURCE)
        self.assertIn(
            "E==List(8,24,40,56,72,16,32,48,64)",
            VERBATIM_SOURCE,
        )
        self.assertIn("MatrixTimes(x*y", VERBATIM_SOURCE)
        self.assertNotIn("MatrixTimes(y*x", VERBATIM_SOURCE)
        self.assertIn("u^72", VERBATIM_SOURCE)

    def test_phase_kernel_generates_a_without_matrix_literal_dependency(self) -> None:
        self.assertEqual(
            phase_kernel(),
            ((8, 1, 3), (1, 3, 5), (3, 5, 7)),
        )
        self.assertEqual(matrix_a(), EXPECTED_A)

    def test_b_is_exact_mod72_reciprocal_complement(self) -> None:
        a = matrix_a()
        b = matrix_b()
        self.assertEqual(b, EXPECTED_B)
        for row in range(3):
            for col in range(3):
                self.assertEqual(a[row][col] + b[row][col], 72)
                self.assertEqual((-a[row][col]) % 72, b[row][col])
                self.assertEqual((-b[row][col]) % 72, a[row][col])

    def test_c_is_e_vector_routed_by_flattened_lo_shu(self) -> None:
        self.assertEqual(LO_SHU, ((4, 9, 2), (3, 5, 7), (8, 1, 6)))
        self.assertEqual(lo_shu_route(), (4, 9, 2, 3, 5, 7, 8, 1, 6))
        self.assertEqual(matrix_c(), EXPECTED_C)
        self.assertEqual(
            sorted(value // 8 for row in matrix_c() for value in row),
            list(range(1, 10)),
        )
        self.assertEqual(matrix_c()[1][1], 72)
        self.assertEqual(matrix_c()[1][1] % 72, 0)

    def test_generator_descriptor_contains_no_redundant_matrix_constants(self) -> None:
        descriptor = generator_descriptor()
        self.assertNotIn("matrix_a", descriptor)
        self.assertNotIn("matrix_b", descriptor)
        self.assertNotIn("matrix_c", descriptor)
        self.assertEqual(descriptor["e_vector"], list(E_VECTOR))
        self.assertEqual(descriptor["lo_shu_route"], list(lo_shu_route()))
        self.assertEqual(descriptor["phase_modulus"], 9)
        self.assertEqual(descriptor["residue_modulus"], 72)

    def test_projection_has_exact_determinants_and_216_receipt(self) -> None:
        projection = materialize_projection()
        self.assertEqual(projection["determinants"], [-18432, 18432, 32256])
        self.assertEqual(projection["normalized_determinants"], [-36, 36, 63])
        self.assertEqual(len(projection["source_hash72"]), 72)
        self.assertEqual(len(projection["generator_hash72"]), 72)
        self.assertEqual(len(projection["proof_hash72"]), 72)
        self.assertEqual(len(projection["receipt_hash216"]), 216)
        self.assertEqual(
            projection["receipt_hash216"],
            projection["source_hash72"]
            + projection["generator_hash72"]
            + projection["proof_hash72"],
        )

    def test_projection_roundtrip_is_deterministic(self) -> None:
        first = materialize_projection()
        second = materialize_projection()
        self.assertEqual(first, second)
        self.assertTrue(validate_projection(first))

    def test_mutated_matrix_fails_closed(self) -> None:
        projection = copy.deepcopy(materialize_projection())
        projection["matrix_a"][0][0] = 63
        with self.assertRaises(Pass220I069TensorError):
            validate_projection(projection)

    def test_mutated_e_route_fails_closed(self) -> None:
        with self.assertRaises(Pass220I069TensorError):
            matrix_c(E_VECTOR, (4, 9, 2, 3, 5, 7, 8, 1, 1))

    def test_float_in_projection_fails_closed(self) -> None:
        projection = copy.deepcopy(materialize_projection())
        projection["generator"]["scale"] = 8.0
        with self.assertRaises(Pass220I069TensorError):
            validate_projection(projection)

    def test_authority_boundary_remains_projection_only(self) -> None:
        self.assertTrue(AUTHORITY_BOUNDARY["formal_projection_only"])
        self.assertTrue(AUTHORITY_BOUNDARY["verbatim_source_authoritative"])
        self.assertTrue(AUTHORITY_BOUNDARY["ordered_matrix_times_preserved"])
        self.assertTrue(AUTHORITY_BOUNDARY["ordered_xy_preserved"])
        self.assertTrue(AUTHORITY_BOUNDARY["e_membrane_not_host_boolean_division"])
        self.assertFalse(AUTHORITY_BOUNDARY["floating_point_authority"])
        self.assertFalse(AUTHORITY_BOUNDARY["canonical_vm81_mutation_authority"])
        self.assertFalse(AUTHORITY_BOUNDARY["canonical_hash72_commit_authority"])
        self.assertFalse(AUTHORITY_BOUNDARY["canonical_hash216_commit_authority"])
        self.assertFalse(AUTHORITY_BOUNDARY["canonical_persistence_authority"])

    def test_self_test_closes(self) -> None:
        report = self_test()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["pass_count"], report["check_count"])
        self.assertEqual(report["failed"], [])


if __name__ == "__main__":
    unittest.main()
