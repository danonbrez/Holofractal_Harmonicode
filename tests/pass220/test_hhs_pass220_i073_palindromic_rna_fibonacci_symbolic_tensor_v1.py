from __future__ import annotations

import copy
import subprocess
import unittest

from hhs_runtime.hhs_pass220_i073_palindromic_rna_fibonacci_symbolic_tensor_v1 import (
    AUTHORITY_BOUNDARY,
    DEFAULT_DECIMAL_SOURCE,
    SOURCE_BUNDLE,
    Pass220I073GeneratorError,
    build_generator,
    reconstruct_serialized_state,
    self_test,
    source_bundle_witness,
    validate_generator,
)
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    LO_SHU_FLAT,
    SERIALIZED_CHARACTERS,
    VM81_CELLS,
    deserialize_offsets_5184,
)


class I073PalindromicRNAFibonacciSymbolicTensorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.offsets = tuple(index % 9 for index in range(VM81_CELLS))
        cls.generator = build_generator(
            decimal_text=DEFAULT_DECIMAL_SOURCE,
            offsets=cls.offsets,
            fibonacci_depth=10,
            nucleus_index=0,
            nesting_depth=0,
        )

    def test_repository_source_bundle_blob_identities(self) -> None:
        for row in SOURCE_BUNDLE:
            actual = subprocess.check_output(
                ["git", "hash-object", row["path"]],
                text=True,
            ).strip()
            self.assertEqual(actual, row["git_blob_sha"], row["path"])

    def test_source_bundle_is_unique_and_content_addressed(self) -> None:
        bundle = source_bundle_witness()
        self.assertEqual(bundle["source_count"], len(SOURCE_BUNDLE))
        self.assertTrue(bundle["roles_unique"])
        self.assertTrue(bundle["paths_unique"])
        self.assertEqual(len(bundle["source_bundle_root_sha256"]), 64)

    def test_i072_parent_is_intrinsically_bound(self) -> None:
        parent = self.generator["parent_i072"]
        self.assertEqual(parent["nucleus_index"], 0)
        self.assertEqual(parent["nesting_depth"], 0)
        self.assertEqual(len(parent["theory_constructor_root_sha256"]), 64)
        self.assertEqual(len(parent["binding_hash72"]), 72)
        self.assertEqual(len(parent["theory_hash216"]), 216)

    def test_palindromic_ieee_ingress_preserves_exact_decimal_and_dyadic(self) -> None:
        ingress = self.generator["palindromic_rna_ingress"]
        self.assertEqual(ingress["decimal_source_text"], DEFAULT_DECIMAL_SOURCE)
        self.assertEqual(
            ingress["exact_decimal_rational"],
            {"numerator": 179971179971, "denominator": 1000000},
        )
        self.assertEqual(len(ingress["binary64_bits_hex"]), 16)
        self.assertTrue(ingress["decimal_and_ieee_are_co_resident"])
        self.assertTrue(ingress["ieee_raw_bits_roundtrip"])
        self.assertTrue(ingress["symbol_reciprocal_roundtrip"])
        self.assertTrue(ingress["ieee_binary64_boundary_only"])
        self.assertFalse(ingress["host_float_arithmetic_authority"])

    def test_lossless_bigint_scientific_serialization_compacts_and_reconstructs(self) -> None:
        descriptor = self.generator["palindromic_rna_ingress"][
            "scientific_serialization"
        ]
        self.assertEqual(descriptor["serialized_characters"], 5184)
        self.assertEqual(descriptor["cell_token_characters"], 64)
        self.assertEqual(descriptor["token_count"], 81)
        self.assertEqual(descriptor["unique_token_count"], 9)
        self.assertEqual(len(descriptor["scientific_token_dictionary"]), 9)
        self.assertEqual(len(descriptor["token_ids"]), 81)
        self.assertTrue(descriptor["bigint_roundtrip_exact"])
        self.assertTrue(descriptor["scientific_dictionary_roundtrip_exact"])
        self.assertFalse(descriptor["canonical_serialized_5184_persisted_by_i073"])

        reconstructed = reconstruct_serialized_state(self.generator)
        self.assertEqual(len(reconstructed), SERIALIZED_CHARACTERS)
        self.assertEqual(deserialize_offsets_5184(reconstructed), self.offsets)

    def test_rna_transcription_is_bidirectional_and_phase_locked(self) -> None:
        ingress = self.generator["palindromic_rna_ingress"]
        self.assertEqual(ingress["rna_windows_total"], 1728)
        self.assertTrue(ingress["rna_double_reverse_exact"])
        self.assertEqual(
            tuple(tuple(item) for item in ingress["ordered_xyzw_products"]),
            (("xy", 1), ("yx", -1), ("zw", 1), ("wz", -1)),
        )
        self.assertEqual(len(ingress["rna_witness_receipt_sha256"]), 64)
        self.assertEqual(len(ingress["g3_pipeline_root_hash72"]), 72)
        self.assertEqual(len(ingress["g3_constructor_graph_root_hash72"]), 72)

    def test_fibonacci_compression_uses_single_shared_schedule(self) -> None:
        fib = self.generator["fibonacci_compression"]
        self.assertEqual(fib["depth"], 10)
        self.assertEqual((fib["f_depth"], fib["f_next"]), (144, 233))
        self.assertEqual(
            fib["transition"],
            {"numerator": 144, "denominator": 233},
        )
        self.assertEqual(
            fib["cumulative_scale"],
            {"numerator": 1, "denominator": 144},
        )
        self.assertEqual(fib["membrane_modulus"], 11)
        self.assertEqual(fib["membrane_residue"], 10)
        self.assertEqual(tuple(fib["magnitude_rows"]), (1, 2, 3, 5, 8))
        self.assertEqual(fib["lo_shu_cell_count"], 9)
        self.assertEqual(fib["shared_schedule_count"], 1)
        self.assertEqual(fib["expanded_schedule_count"], 45)
        self.assertEqual(fib["outer_hydration_modulus"], 1259713)
        self.assertEqual(tuple(fib["schedule"][-2:]), (144, 233))
        self.assertTrue(fib["reference_default_closed"])
        self.assertFalse(fib["expanded_45_schedules_persisted"])
        self.assertTrue(fib["reconstructible_from_shared_schedule_and_labels"])

    def test_harmonicode_symbolic_tensor_program_executes_and_replays(self) -> None:
        symbolic = self.generator["symbolic_tensor_program"]
        self.assertEqual(symbolic["source_language"], "HARMONICODE_TYPED_JSON_IR")
        self.assertEqual(symbolic["ordered_tensor_operation"], "tensor_product")
        self.assertEqual(symbolic["tensor_shape"], (5, 9))
        self.assertEqual(symbolic["tensor_elements"], 45)
        values = tuple(symbolic["tensor_values"])
        self.assertEqual(values[:9], tuple(LO_SHU_FLAT))
        self.assertEqual(values[-9:], tuple(8 * value for value in LO_SHU_FLAT))
        self.assertEqual(
            symbolic["equivalence_status"],
            "SYMBOLIC_RUNTIME_EQUIVALENCE_VALIDATED",
        )
        self.assertEqual(len(symbolic["program_root_hash72"]), 72)
        self.assertEqual(len(symbolic["execution_receipt_root_hash72"]), 72)
        self.assertEqual(len(symbolic["equivalence_root_hash72"]), 72)
        self.assertFalse(symbolic["host_eval_used"])
        self.assertFalse(symbolic["float_canonical_authority"])
        self.assertFalse(symbolic["canonical_mutation_authority"])

    def test_hash216_hydration_is_compact_and_roundtrip_bound(self) -> None:
        self.assertEqual(len(self.generator["generator_hash216"]), 216)
        self.assertEqual(len(self.generator["plane_roots"]), 3)
        self.assertEqual(
            tuple(row["role"] for row in self.generator["plane_roots"]),
            ("PREVIOUS", "CHANGE", "RECEIPT"),
        )
        self.assertTrue(all(row["roundtrip_exact"] for row in self.generator["plane_roots"]))
        self.assertTrue(
            all(row["expanded_vertices"] == 5184 for row in self.generator["plane_roots"])
        )

    def test_storage_optimization_omits_reconstructible_expansions(self) -> None:
        storage = self.generator["storage_optimization"]
        self.assertTrue(storage["persist_parent_constructor_root"])
        self.assertTrue(storage["persist_hash216_generator"])
        self.assertTrue(storage["persist_ieee_raw_bits"])
        self.assertTrue(storage["persist_exact_decimal_dyadic_residue"])
        self.assertTrue(storage["persist_scalar_bigint"])
        self.assertTrue(storage["persist_scientific_token_dictionary"])
        self.assertTrue(storage["persist_shared_fibonacci_schedule"])
        self.assertTrue(storage["persist_symbolic_tensor_root"])
        self.assertFalse(storage["persist_full_5184_serialization"])
        self.assertFalse(storage["persist_45_fibonacci_schedule_copies"])
        self.assertFalse(storage["persist_3x5184_hash216_expansion"])
        self.assertTrue(storage["on_demand_exact_reconstruction"])
        self.assertNotIn("bigint_5184", self.generator)
        self.assertNotIn("vertex72_geometry", self.generator)

    def test_generator_is_deterministic(self) -> None:
        again = build_generator(
            decimal_text=DEFAULT_DECIMAL_SOURCE,
            offsets=self.offsets,
            fibonacci_depth=10,
            nucleus_index=0,
            nesting_depth=0,
        )
        self.assertEqual(self.generator, again)
        self.assertTrue(validate_generator(again))

    def test_ingress_fibonacci_and_parent_geometry_change_identity(self) -> None:
        changed_ingress = build_generator(
            decimal_text="179971.179972",
            offsets=self.offsets,
            fibonacci_depth=10,
            nucleus_index=0,
            nesting_depth=0,
        )
        changed_fib = build_generator(
            decimal_text=DEFAULT_DECIMAL_SOURCE,
            offsets=self.offsets,
            fibonacci_depth=9,
            nucleus_index=0,
            nesting_depth=0,
        )
        changed_parent = build_generator(
            decimal_text=DEFAULT_DECIMAL_SOURCE,
            offsets=self.offsets,
            fibonacci_depth=10,
            nucleus_index=8,
            nesting_depth=7,
        )
        for other in (changed_ingress, changed_fib, changed_parent):
            self.assertNotEqual(
                self.generator["generator_root_sha256"],
                other["generator_root_sha256"],
            )
            self.assertNotEqual(
                self.generator["generator_hash216"],
                other["generator_hash216"],
            )

    def test_tampering_fails_closed(self) -> None:
        mutated = copy.deepcopy(self.generator)
        mutated["palindromic_rna_ingress"]["scientific_serialization"][
            "scalar_bigint"
        ] += 1
        with self.assertRaises(Pass220I073GeneratorError):
            validate_generator(mutated)

        mutated = copy.deepcopy(self.generator)
        mutated["fibonacci_compression"]["schedule_root_sha256"] = "0" * 64
        with self.assertRaises(Pass220I073GeneratorError):
            validate_generator(mutated)

        mutated = copy.deepcopy(self.generator)
        original = mutated["generator_hash216"][-1]
        replacement = "0" if original != "0" else "1"
        mutated["generator_hash216"] = mutated["generator_hash216"][:-1] + replacement
        with self.assertRaises(Pass220I073GeneratorError):
            validate_generator(mutated)

    def test_invalid_inputs_fail_closed(self) -> None:
        with self.assertRaises(Pass220I073GeneratorError):
            build_generator(decimal_text="")
        with self.assertRaises(Pass220I073GeneratorError):
            build_generator(offsets=(0,) * 80)
        bad_offsets = list(self.offsets)
        bad_offsets[0] = 9
        with self.assertRaises(Pass220I073GeneratorError):
            build_generator(offsets=bad_offsets)
        with self.assertRaises(Pass220I073GeneratorError):
            build_generator(fibonacci_depth=-1)

    def test_authority_boundary_remains_candidate_only(self) -> None:
        self.assertTrue(AUTHORITY_BOUNDARY["candidate_only"])
        self.assertTrue(AUTHORITY_BOUNDARY["ieee_binary64_boundary_only"])
        self.assertTrue(AUTHORITY_BOUNDARY["exact_decimal_source_preserved"])
        self.assertTrue(AUTHORITY_BOUNDARY["exact_ieee_dyadic_preserved"])
        self.assertTrue(AUTHORITY_BOUNDARY["bigint_serialization_lossless"])
        self.assertTrue(AUTHORITY_BOUNDARY["rna_transcription_read_only"])
        self.assertTrue(AUTHORITY_BOUNDARY["fibonacci_compression_reconstructible"])
        self.assertTrue(AUTHORITY_BOUNDARY["symbolic_tensor_runtime_exact"])
        for key in (
            "host_float_arithmetic_authority",
            "expanded_5184_serialization_persisted",
            "expanded_45_fibonacci_schedules_persisted",
            "expanded_3x5184_hash216_geometry_persisted",
            "canonical_vm81_mutation_authority",
            "canonical_hash72_commit_authority",
            "canonical_hash216_commit_authority",
            "canonical_hash216_persistence_authority",
            "external_egress_authority",
        ):
            self.assertFalse(AUTHORITY_BOUNDARY[key], key)

    def test_self_test_passes(self) -> None:
        result = self_test()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["failed"], [])
        self.assertEqual(result["check_count"], result["pass_count"])


if __name__ == "__main__":
    unittest.main()
