from __future__ import annotations

import ast
from copy import deepcopy
from pathlib import Path
import unittest

from hhs_backend.runtime.hhs_pass217_hash72_manifold_nucleus_v1 import (
    CLASSIFICATION,
    DIRECTION_DELTAS,
    EVIDENCE_PATH,
    EXPECTED_CANDIDATE_SHA256,
    EXPECTED_HASH72_MATRIX_ROOT,
    EXPECTED_MANIFOLD_ROOT,
    EXPECTED_NUCLEUS_IDENTITY_ROOT,
    EXPECTED_NUCLEUS_SUPPORT_ROOT,
    NUCLEUS_CELLS,
    Pass217Iteration4Error,
    anchor_orbit_root,
    build_record,
    build_schema,
    direction_order,
    hash72_row,
    nucleus_identity_root,
    validate_hash72_manifold,
    validate_nucleus_bytes,
    validate_record,
)
from hhs_backend.runtime.hhs_pass217_genesis_candidate_v1 import (
    CANDIDATE_PATH,
    build_candidate_bytes,
)

ROOT = Path(__file__).resolve().parents[1]


class Pass217Iteration4Tests(unittest.TestCase):
    def test_record_exact_rebuild(self) -> None:
        result = validate_record(ROOT)
        self.assertEqual(result["classification"], CLASSIFICATION)
        self.assertEqual(
            result["hash72_manifold_root_sha256"], EXPECTED_MANIFOLD_ROOT
        )
        self.assertEqual(
            result["nucleus_support_root_sha256"], EXPECTED_NUCLEUS_SUPPORT_ROOT
        )
        self.assertEqual(result["candidate_sha256"], EXPECTED_CANDIDATE_SHA256)
        self.assertTrue(result["predecessor_reconciliation_complete"])
        self.assertFalse(result["canonical_authority_promoted"])

    def test_schema_exact_rebuild(self) -> None:
        import json
        expected = json.dumps(
            build_schema(),
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8") + b"\n"
        path = ROOT / (
            "contracts/pass217/"
            "PASS_217_ITERATION_4_HASH72_MANIFOLD_NUCLEUS.schema.json"
        )
        self.assertEqual(path.read_bytes(), expected)

    def test_hash72_rows_are_rotations_and_permutations(self) -> None:
        row0 = hash72_row(0)
        self.assertEqual(len(row0), 72)
        self.assertEqual(len(set(row0)), 72)
        for row in range(72):
            observed = hash72_row(row)
            expected = row0[row:] + row0[:row]
            self.assertEqual(observed, expected)
            self.assertEqual(set(observed), set(row0))

    def test_hash72_manifold_exact_roots(self) -> None:
        manifold = validate_hash72_manifold()
        self.assertEqual(
            manifold["matrix_root_sha256"], EXPECTED_HASH72_MATRIX_ROOT
        )
        self.assertEqual(
            manifold["anchor_orbit_root_sha256"], anchor_orbit_root()
        )
        self.assertEqual(
            manifold["manifold_root_sha256"], EXPECTED_MANIFOLD_ROOT
        )
        self.assertEqual(manifold["matrix_positions"], 5184)

    def test_every_direction_is_order_72(self) -> None:
        for direction in DIRECTION_DELTAS:
            self.assertEqual(direction_order(direction), 72)

    def test_invalid_direction_and_row_fail_closed(self) -> None:
        with self.assertRaisesRegex(
            Pass217Iteration4Error, "DIRECTION_INVALID"
        ):
            direction_order("xy")
        with self.assertRaisesRegex(
            Pass217Iteration4Error, "HASH72_ROW_RANGE"
        ):
            hash72_row(72)

    def test_nucleus_identity_and_support(self) -> None:
        image = (ROOT / CANDIDATE_PATH).read_bytes()
        result = validate_nucleus_bytes(image)
        self.assertEqual(
            result["central_cell_indices"], list(NUCLEUS_CELLS)
        )
        self.assertEqual(
            result["identity_root_sha256"], EXPECTED_NUCLEUS_IDENTITY_ROOT
        )
        self.assertEqual(
            result["support_root_sha256"], EXPECTED_NUCLEUS_SUPPORT_ROOT
        )
        self.assertEqual(result["support_bits"], 576)
        self.assertTrue(result["fixed_pointwise"])

    def test_nucleus_mutation_is_rejected(self) -> None:
        image = bytearray(build_candidate_bytes())
        cell = NUCLEUS_CELLS[0]
        image[cell * 8] ^= 1
        with self.assertRaisesRegex(
            Pass217Iteration4Error, "NUCLEUS_SHARD_DRIFT"
        ):
            validate_nucleus_bytes(bytes(image))

    def test_candidate_rebuild_matches_frozen_bytes(self) -> None:
        frozen = (ROOT / CANDIDATE_PATH).read_bytes()
        self.assertEqual(frozen, build_candidate_bytes())
        from hashlib import sha256
        self.assertEqual(sha256(frozen).hexdigest(), EXPECTED_CANDIDATE_SHA256)

    def test_claim_boundary_cannot_be_promoted(self) -> None:
        record = build_record(ROOT)
        tampered = deepcopy(record)
        tampered["claim_boundary"]["canonical_authority_promoted"] = True
        with self.assertRaisesRegex(
            Pass217Iteration4Error, "EVIDENCE_DRIFT"
        ):
            validate_record(ROOT, tampered)

    def test_historical_hold_is_superseded_not_rewritten(self) -> None:
        record = build_record(ROOT)
        gate = record["inheritance_gate"]
        self.assertTrue(gate["predecessor_reconciliation_complete"])
        self.assertTrue(
            gate["historical_iteration1_3_hold_fields_preserved_as_provenance"]
        )
        self.assertFalse(gate["iteration1_3_artifacts_regenerated"])
        self.assertFalse(gate["canonical_promotion_allowed_by_iteration4"])

    def test_runtime_contains_no_float_literals(self) -> None:
        path = ROOT / (
            "hhs_backend/runtime/"
            "hhs_pass217_hash72_manifold_nucleus_v1.py"
        )
        tree = ast.parse(path.read_text("utf-8"))
        floats = [
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        self.assertEqual(floats, [])

    def test_evidence_path_exists(self) -> None:
        self.assertTrue((ROOT / EVIDENCE_PATH).is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
