from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass192.runtime import (
    CANONICAL_SOURCE,
    LO_SHU,
    MAGNITUDES,
    SEED_WITNESSES,
    Pass192Error,
    Pass192Runtime,
    cumulative_fibonacci_scale,
    fibonacci_ratio,
    source_invariants,
)


def authority(index: int) -> dict[str, object]:
    state = hash72_digest({"domain": "P192_TEST_STATE"}, {"index": index})
    receipt = hash72_digest({"domain": "P192_TEST_RECEIPT"}, {"index": index})
    return {
        "runtime": {"state_hash72": state},
        "receipt": {"state_hash72": state, "receipt_hash72": receipt},
        "authority_audit": {
            "ok": True,
            "state_hash72": state,
            "receipt_hash72": receipt,
        },
    }


class Pass192RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.runtime = Pass192Runtime(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_source_and_lo_shu_are_exact(self) -> None:
        self.assertTrue(all(source_invariants().values()))
        self.assertIn("1+3==4==2+2==2^2", CANONICAL_SOURCE)
        self.assertEqual(tuple(MAGNITUDES), (1, 2, 3, 5, 8))
        self.assertEqual(SEED_WITNESSES[3], "1+3==4==2+2==2^2")
        self.assertEqual(LO_SHU, ((4, 9, 2), (3, 5, 7), (8, 1, 6)))

    def test_nine_cells_have_distinct_canonical_identities(self) -> None:
        ids = set()
        for row in range(3):
            for column in range(3):
                tensor = self.runtime.create_tensor(
                    row, column, authority_execution=authority(row * 3 + column)
                )
                ids.add(tensor["tensor_id"])
                self.assertEqual(tensor["lo_shu_cell_value"], LO_SHU[row][column])
                self.assertEqual(len(tensor["hash216_identity"]), 216)
                self.assertTrue(self.runtime.validate_tensor(tensor["tensor_id"])["ok"])
        self.assertEqual(len(ids), 9)

    def test_exact_ratio_and_cumulative_scale(self) -> None:
        self.assertEqual(fibonacci_ratio(0).numerator, 1)
        self.assertEqual(fibonacci_ratio(0).denominator, 2)
        self.assertEqual(
            (fibonacci_ratio(8).numerator, fibonacci_ratio(8).denominator),
            (55, 89),
        )
        self.assertEqual(
            (
                cumulative_fibonacci_scale(8).numerator,
                cumulative_fibonacci_scale(8).denominator,
            ),
            (1, 55),
        )

    def test_bounded_materialization_preserves_parent_and_membrane_chains(self) -> None:
        tensor = self.runtime.create_tensor(0, 0, authority_execution=authority(1))
        materialized = self.runtime.materialize_prefix(
            tensor["tensor_id"], 3, authority_execution=authority(2)
        )
        self.assertEqual(materialized["node_count"], 100)
        self.assertFalse(materialized["outer_modulus_applied_locally"])
        self.assertTrue(
            self.runtime.validate_materialization(materialized["materialization_id"])["ok"]
        )
        lane = [
            node
            for node in materialized["nodes"]
            if node["magnitude_row_index"] == 0 and node["seed_column_index"] == 0
        ]
        lane.sort(key=lambda node: node["nesting_depth"])
        self.assertEqual(lane[0]["parent_id"], tensor["tensor_id"])
        self.assertEqual(lane[1]["parent_id"], lane[0]["tensor_id"])
        self.assertEqual(
            (
                lane[3]["membrane_witness"]["modulus"],
                lane[3]["membrane_witness"]["residue"],
            ),
            (4, 3),
        )
        self.assertEqual(len(lane[3]["inherited_membrane_ids"]), 3)

    def test_bounds_and_cancellation_fail_closed(self) -> None:
        tensor = self.runtime.create_tensor(1, 1, authority_execution=authority(1))
        with self.assertRaises(Pass192Error):
            self.runtime.materialize_prefix(
                tensor["tensor_id"],
                4,
                materialization_bounds={"max_depth": 3},
                authority_execution=authority(2),
            )
        with self.assertRaises(Pass192Error):
            self.runtime.materialize_prefix(
                tensor["tensor_id"],
                2,
                cancelled=True,
                authority_execution=authority(3),
            )

    def test_invalid_authority_does_not_persist(self) -> None:
        with self.assertRaises(Pass192Error):
            self.runtime.create_tensor(0, 2, authority_execution={})
        self.assertEqual(self.runtime.status()["tensors"], 0)
        self.assertEqual(self.runtime.receipts_for(), [])

    def test_receipt_replay_is_deterministic(self) -> None:
        tensor = self.runtime.create_tensor(2, 2, authority_execution=authority(1))
        materialized = self.runtime.materialize_prefix(
            tensor["tensor_id"], 1, authority_execution=authority(2)
        )
        replay = self.runtime.replay()
        self.assertTrue(replay["ok"])
        self.assertEqual(replay["records"], 2)
        self.assertEqual(len(replay["last_receipt_hash72"]), 72)
        self.assertTrue(self.runtime.replay(materialized["materialization_id"])["ok"])


if __name__ == "__main__":
    unittest.main()
