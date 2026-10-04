from __future__ import annotations

import copy
import unittest

from hhs_runtime.hhs_pass220_i069_harmonicode_i_tensor_v1 import (
    materialize_projection,
)
from hhs_runtime.hhs_pass220_i070_i_tensor_lane5_vm81_bridge_v1 import (
    AUTHORITY_BOUNDARY,
    Pass220I070BridgeError,
    build_lane5_vm81_candidate,
    global_vm81_address_witness,
    self_test,
    tensor_cell_witnesses,
    validate_lane5_vm81_candidate,
)
from hhs_runtime.hhs_pass220_quantum_collapse_admission_bridge_v1 import (
    collapse_address,
)


class I070ITensorLane5VM81BridgeTests(unittest.TestCase):
    def test_nucleus_local_cells_preserve_tensor_and_vm81_addressing(self) -> None:
        cells = tensor_cell_witnesses(4)
        self.assertEqual(len(cells), 9)
        self.assertEqual(
            [cell.vm81_cell_id for cell in cells],
            list(range(36, 45)),
        )
        for cell in cells:
            self.assertEqual(cell.phase_a + cell.phase_b, 72)
            self.assertTrue(cell.reciprocal72_closed)
            self.assertTrue(cell.lo_shu_e_route_closed)
            self.assertEqual(cell.product_c, cell.product_e_value)
            self.assertEqual(cell.normalized_a + cell.normalized_b, 9)

    def test_vm81_address_rule_matches_existing_i027_address_surface(self) -> None:
        for nucleus in range(9):
            cells = tensor_cell_witnesses(nucleus)
            for cell in cells:
                inherited = collapse_address(cell.outcome, nucleus)
                self.assertEqual(inherited.vm81_cell_id, cell.vm81_cell_id)
                self.assertEqual(inherited.row, cell.row)
                self.assertEqual(inherited.column, cell.column)
                self.assertEqual(inherited.lo_shu_value, cell.lo_shu_value)

    def test_global_vm81_address_witness_is_exact_0_to_80_bijection(self) -> None:
        witness = global_vm81_address_witness()
        self.assertEqual(witness["address_count"], 81)
        self.assertEqual(witness["unique_address_count"], 81)
        self.assertEqual(witness["minimum"], 0)
        self.assertEqual(witness["maximum"], 80)
        self.assertTrue(witness["exact_cover_0_80"])

    def test_candidate_preserves_i069_source_receipt_and_hydrates_exactly(self) -> None:
        source = materialize_projection()
        candidate = build_lane5_vm81_candidate(0)
        self.assertEqual(
            candidate["source_receipt_hash216"],
            source["receipt_hash216"],
        )
        self.assertTrue(
            candidate["inherited_i069_hydration"]["roundtrip_exact"]
        )
        self.assertTrue(candidate["candidate_hydration"]["roundtrip_exact"])
        self.assertEqual(len(candidate["candidate_hash216"]), 216)
        self.assertEqual(len(candidate["binding_hash72"]), 72)

    def test_candidate_hash216_lane_order_is_previous_change_receipt(self) -> None:
        candidate = build_lane5_vm81_candidate(8)
        self.assertEqual(
            candidate["candidate_hash216"],
            candidate["candidate_previous_hash72"]
            + candidate["candidate_change_hash72"]
            + candidate["candidate_receipt_hash72"],
        )
        roles = [
            plane["role"]
            for plane in candidate["candidate_hydration"]["plane_roots"]
        ]
        self.assertEqual(roles, ["PREVIOUS", "CHANGE", "RECEIPT"])

    def test_root_only_optimization_avoids_persisting_expanded_vertices(self) -> None:
        candidate = build_lane5_vm81_candidate(3)
        optimization = candidate["metadata_optimization"]
        self.assertTrue(optimization["stores_generator_and_plane_roots"])
        self.assertFalse(optimization["stores_expanded_5184_vertices"])
        self.assertTrue(
            optimization["expanded_geometry_reconstructible_on_demand"]
        )
        self.assertFalse(
            optimization["repeated_matrix_literal_storage_required"]
        )
        self.assertFalse(
            optimization["repeated_hash216_vertex_materialization_required"]
        )
        for hydration_key in (
            "inherited_i069_hydration",
            "candidate_hydration",
        ):
            hydration = candidate[hydration_key]
            self.assertEqual(len(hydration["plane_roots"]), 3)
            self.assertNotIn("vertex72_geometry", hydration)

    def test_central_tensor_position_preserves_72_to_residue_zero(self) -> None:
        center = tensor_cell_witnesses(0)[4]
        self.assertEqual(center.outcome, 4)
        self.assertEqual(center.lo_shu_value, 5)
        self.assertEqual(center.product_c, 72)
        self.assertEqual(center.product_c % 72, 0)
        self.assertEqual(center.vm81_cell_id, 4)

    def test_candidate_validation_is_deterministic(self) -> None:
        first = build_lane5_vm81_candidate(5)
        second = build_lane5_vm81_candidate(5)
        self.assertEqual(first, second)
        self.assertTrue(validate_lane5_vm81_candidate(first))

    def test_tampered_cell_fails_closed(self) -> None:
        candidate = copy.deepcopy(build_lane5_vm81_candidate(2))
        candidate["cells"][0]["phase_a"] = 63
        with self.assertRaises(Pass220I070BridgeError):
            validate_lane5_vm81_candidate(candidate)

    def test_tampered_candidate_hash216_fails_closed(self) -> None:
        candidate = copy.deepcopy(build_lane5_vm81_candidate(2))
        candidate["candidate_hash216"] = (
            candidate["candidate_hash216"][:-1]
            + candidate["candidate_hash216"][0]
        )
        with self.assertRaises(Pass220I070BridgeError):
            validate_lane5_vm81_candidate(candidate)

    def test_float_metadata_fails_closed(self) -> None:
        candidate = copy.deepcopy(build_lane5_vm81_candidate(1))
        candidate["metadata_optimization"]["ratio"] = 72.0
        with self.assertRaises(Pass220I070BridgeError):
            validate_lane5_vm81_candidate(candidate)

    def test_invalid_nucleus_fails_closed(self) -> None:
        for value in (-1, 9, True, "0"):
            with self.assertRaises(Pass220I070BridgeError):
                build_lane5_vm81_candidate(value)  # type: ignore[arg-type]

    def test_authority_boundary_remains_candidate_only(self) -> None:
        self.assertTrue(AUTHORITY_BOUNDARY["candidate_only"])
        self.assertTrue(AUTHORITY_BOUNDARY["inherits_i069_verbatim_source"])
        self.assertTrue(AUTHORITY_BOUNDARY["inherits_i065_lossless_hydration"])
        self.assertTrue(AUTHORITY_BOUNDARY["inherits_vm81_address_geometry"])
        self.assertFalse(AUTHORITY_BOUNDARY["floating_point_authority"])
        self.assertFalse(AUTHORITY_BOUNDARY["canonical_vm81_mutation_authority"])
        self.assertFalse(AUTHORITY_BOUNDARY["canonical_hash72_commit_authority"])
        self.assertFalse(AUTHORITY_BOUNDARY["canonical_hash216_commit_authority"])
        self.assertFalse(
            AUTHORITY_BOUNDARY["canonical_hash216_persistence_authority"]
        )

    def test_self_test_closes(self) -> None:
        report = self_test()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["pass_count"], report["check_count"])
        self.assertEqual(report["failed"], [])


if __name__ == "__main__":
    unittest.main()
