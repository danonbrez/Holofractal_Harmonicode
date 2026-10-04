from __future__ import annotations

import copy
import subprocess
import unittest

from hhs_runtime.hhs_pass220_i072_theory_constructor_hash216_hydration_v1 import (
    AUTHORITY_BOUNDARY,
    FULL_ATTACHED_COMPONENTS,
    SOURCE_BUNDLE,
    Pass220I072TheoryHydrationError,
    build_theory_constructor,
    hydrate_theory_constructor,
    self_test,
    theory_source_bundle,
    validate_theory_constructor,
)


class I072TheoryConstructorHash216HydrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.constructor = build_theory_constructor(
            nucleus_index=4,
            nesting_depth=3,
        )

    def test_repository_source_bundle_blob_identities(self) -> None:
        for row in SOURCE_BUNDLE:
            actual = subprocess.check_output(
                ["git", "hash-object", row["path"]],
                text=True,
            ).strip()
            self.assertEqual(actual, row["git_blob_sha"], row["path"])

    def test_source_bundle_is_content_addressed_and_unique(self) -> None:
        bundle = theory_source_bundle()
        self.assertEqual(bundle["source_count"], len(SOURCE_BUNDLE))
        self.assertTrue(bundle["roles_unique"])
        self.assertTrue(bundle["paths_unique"])
        self.assertEqual(len(bundle["source_bundle_root_sha256"]), 64)

    def test_constructor_binds_i039_shared_root(self) -> None:
        binding = self.constructor["shared_root_binding"]
        self.assertEqual(
            binding["schema"],
            "HHS_PASS_220_I072_THEORY_CONSTRUCTOR_HASH216_HYDRATION_V1"
            "_SHARED_ROOT_BINDING_V1",
        )
        self.assertEqual(len(binding["shared_state_root_sha256"]), 64)
        self.assertTrue(binding["phase_orbit_shared"])
        self.assertTrue(binding["palindromic_return_gate_closed"])
        self.assertFalse(binding["canonical_admission_authority"])

    def test_constructor_binds_lean_theorem_and_dependency_before_hash216(self) -> None:
        formal = self.constructor["formal_proof_identity"]
        self.assertEqual(
            formal["lean_inherited_via"],
            "PASS_220_I061_UNIFIED_SCIENTIFIC_PHYSICS_SYNTHESIS",
        )
        self.assertEqual(len(formal["lean_theorem_identity_hash72"]), 72)
        self.assertEqual(len(formal["lean_dependency_identity_hash72"]), 72)
        self.assertEqual(formal["wolfram_parent_exact_checks"], 12)
        self.assertEqual(formal["wolfram_i072_exact_checks"], 42)
        self.assertTrue(formal["formal_validity_only"])
        self.assertFalse(formal["empirical_correspondence_claimed"])

    def test_i071_phase_loop_is_bound_as_exact_constructor_input(self) -> None:
        phase = self.constructor["phase_loop_binding"]
        self.assertEqual(phase["orbit_period"], 72)
        self.assertEqual(phase["phase_lock_period"], 5184)
        self.assertTrue(phase["geometry_returned"])
        self.assertTrue(phase["lineage_advanced"])
        self.assertTrue(phase["converged"])
        self.assertEqual(len(phase["phase_loop_receipt_hash72"]), 72)
        self.assertEqual(len(phase["final_lineage_hash216"]), 216)

    def test_theory_hash216_is_three_ordered_hash72_lanes(self) -> None:
        word = self.constructor["theory_hash216"]
        self.assertEqual(len(word), 216)
        lanes = (word[:72], word[72:144], word[144:])
        self.assertEqual(len(lanes), 3)
        self.assertTrue(all(len(lane) == 72 for lane in lanes))
        roots = self.constructor["plane_roots"]
        self.assertEqual(
            tuple(row["role"] for row in roots),
            ("PREVIOUS", "CHANGE", "RECEIPT"),
        )
        self.assertEqual(
            tuple(row["generator_hash72"] for row in roots),
            lanes,
        )

    def test_i065_on_demand_hydration_roundtrips(self) -> None:
        hydrated = hydrate_theory_constructor(self.constructor)
        self.assertTrue(hydrated["roundtrip_exact"])
        self.assertEqual(hydrated["hash216_positions"], 216)
        self.assertEqual(hydrated["three_dimensional_vertex_count"], 72)
        self.assertEqual(hydrated["components_per_vertex"], 3)
        self.assertEqual(
            hydrated["full_attached_components"],
            FULL_ATTACHED_COMPONENTS,
        )
        self.assertEqual(FULL_ATTACHED_COMPONENTS, 15552)
        self.assertEqual(len(hydrated["planes"]), 3)
        self.assertEqual(len(hydrated["vertex72_geometry"]), 72)

    def test_compact_constructor_does_not_persist_expanded_geometry(self) -> None:
        storage = self.constructor["storage"]
        self.assertTrue(storage["stores_constructor_root"])
        self.assertTrue(storage["stores_theory_hash216"])
        self.assertTrue(storage["stores_generator_and_plane_roots"])
        self.assertFalse(storage["stores_expanded_3x5184_geometry"])
        self.assertTrue(storage["expanded_geometry_reconstructible_on_demand"])
        self.assertEqual(
            storage["fully_hydrated_attached_components_if_materialized"],
            15552,
        )
        self.assertNotIn("vertex72_geometry", self.constructor)
        self.assertFalse(
            any("vertex72_geometry" in root for root in self.constructor["plane_roots"])
        )

    def test_constructor_is_deterministic(self) -> None:
        a = build_theory_constructor(nucleus_index=4, nesting_depth=3)
        b = build_theory_constructor(nucleus_index=4, nesting_depth=3)
        self.assertEqual(a, b)
        self.assertTrue(validate_theory_constructor(a))

    def test_depth_is_provenance_and_changes_constructor_identity(self) -> None:
        shallow = build_theory_constructor(nucleus_index=4, nesting_depth=0)
        deep = build_theory_constructor(nucleus_index=4, nesting_depth=7)
        self.assertEqual(
            shallow["shared_root_binding"]["shared_state_root_sha256"],
            deep["shared_root_binding"]["shared_state_root_sha256"],
        )
        self.assertEqual(
            shallow["phase_loop_binding"]["orbit_period"],
            deep["phase_loop_binding"]["orbit_period"],
        )
        self.assertNotEqual(
            shallow["theory_constructor_root_sha256"],
            deep["theory_constructor_root_sha256"],
        )
        self.assertNotEqual(
            shallow["theory_hash216"],
            deep["theory_hash216"],
        )

    def test_nucleus_is_part_of_constructor_identity(self) -> None:
        a = build_theory_constructor(nucleus_index=0, nesting_depth=1)
        b = build_theory_constructor(nucleus_index=8, nesting_depth=1)
        self.assertNotEqual(
            a["phase_loop_binding"]["phase_loop_receipt_hash72"],
            b["phase_loop_binding"]["phase_loop_receipt_hash72"],
        )
        self.assertNotEqual(
            a["theory_constructor_root_sha256"],
            b["theory_constructor_root_sha256"],
        )

    def test_tampered_constructor_fails_closed(self) -> None:
        mutated = copy.deepcopy(self.constructor)
        mutated["storage"]["stores_expanded_3x5184_geometry"] = True
        with self.assertRaises(Pass220I072TheoryHydrationError):
            validate_theory_constructor(mutated)

        mutated = copy.deepcopy(self.constructor)
        mutated["theory_hash216"] = mutated["theory_hash216"][:-1] + "0"
        with self.assertRaises(Pass220I072TheoryHydrationError):
            validate_theory_constructor(mutated)

        mutated = copy.deepcopy(self.constructor)
        mutated["phase_loop_binding"]["orbit_period"] = 71
        with self.assertRaises(Pass220I072TheoryHydrationError):
            validate_theory_constructor(mutated)

    def test_invalid_inputs_fail_closed(self) -> None:
        with self.assertRaises(Pass220I072TheoryHydrationError):
            build_theory_constructor(nucleus_index=True)
        with self.assertRaises(Pass220I072TheoryHydrationError):
            build_theory_constructor(nucleus_index=9)
        with self.assertRaises(Pass220I072TheoryHydrationError):
            build_theory_constructor(nesting_depth=-1)

    def test_authority_boundary_does_not_widen(self) -> None:
        self.assertTrue(AUTHORITY_BOUNDARY["candidate_only"])
        self.assertTrue(AUTHORITY_BOUNDARY["theory_constructor_is_projection"])
        self.assertTrue(AUTHORITY_BOUNDARY["formal_validity_not_empirical_validation"])
        self.assertFalse(AUTHORITY_BOUNDARY["expanded_geometry_persisted"])
        self.assertTrue(AUTHORITY_BOUNDARY["hydrate_on_demand"])
        for key in (
            "floating_point_authority",
            "canonical_vm81_mutation_authority",
            "canonical_hash72_commit_authority",
            "canonical_hash216_commit_authority",
            "canonical_hash216_persistence_authority",
            "empirical_claim_authority",
            "external_egress_authority",
        ):
            self.assertFalse(AUTHORITY_BOUNDARY[key], key)

    def test_self_test_passes(self) -> None:
        report = self_test()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["failed"], [])
        self.assertEqual(report["check_count"], report["pass_count"])


if __name__ == "__main__":
    unittest.main()
