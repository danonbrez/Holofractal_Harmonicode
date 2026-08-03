from __future__ import annotations

import unittest

from hhs_backend.runtime.hhs_pass196_gap_partition_v1 import (
    partition_integration_gaps,
)


class Pass196GapPartitionTests(unittest.TestCase):
    def test_partition_preserves_every_raw_gap(self) -> None:
        rows = [
            {"pass_number": 42, "state": "PARTIAL"},
            {"pass_number": 155, "state": "UNRESOLVED"},
            {"pass_number": 194, "state": "PARTIAL"},
            {"pass_number": 198, "state": "CONTRACT_ONLY"},
        ]
        result = partition_integration_gaps(
            rows,
            maximum_discovered_pass=200,
        )
        self.assertEqual(result["legacy_unresolved_count"], 1)
        self.assertEqual(result["bridge_unresolved_count"], 2)
        self.assertEqual(result["current_frontier_unresolved_count"], 1)
        self.assertEqual(result["raw_gap_count_preserved"], len(rows))
        self.assertFalse(result["current_frontier_closed"])
        self.assertFalse(result["pass_layers_closed"])
        self.assertTrue(result["mandatory_surfaces_closed"])
        self.assertFalse(result["global_integration_closed"])
        self.assertFalse(result["classification_mutates_canonical_state"])

    def test_current_frontier_can_close_while_historical_gaps_remain_visible(self) -> None:
        rows = [{"pass_number": 42, "state": "PARTIAL"}]
        result = partition_integration_gaps(
            rows,
            maximum_discovered_pass=200,
        )
        self.assertTrue(result["current_frontier_closed"])
        self.assertFalse(result["global_integration_closed"])
        self.assertEqual(result["legacy_unresolved_passes"], rows)

    def test_missing_mandatory_surface_prevents_global_closure(self) -> None:
        result = partition_integration_gaps(
            [],
            maximum_discovered_pass=200,
            missing_mandatory_surfaces=["api", "visual_ide", "api"],
        )
        self.assertTrue(result["pass_layers_closed"])
        self.assertFalse(result["mandatory_surfaces_closed"])
        self.assertEqual(
            result["missing_mandatory_surfaces"],
            ["api", "visual_ide"],
        )
        self.assertFalse(result["global_integration_closed"])

    def test_global_closure_requires_pass_and_surface_closure(self) -> None:
        result = partition_integration_gaps(
            [],
            maximum_discovered_pass=200,
            missing_mandatory_surfaces=[],
        )
        self.assertTrue(result["pass_layers_closed"])
        self.assertTrue(result["mandatory_surfaces_closed"])
        self.assertTrue(result["global_integration_closed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
