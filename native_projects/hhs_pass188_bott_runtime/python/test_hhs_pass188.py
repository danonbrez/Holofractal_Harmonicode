#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

import hhs_pass188 as h


class Pass188Tests(unittest.TestCase):
    def test_transition_table(self) -> None:
        self.assertEqual([h.bott_step(i) for i in range(8)], [1, 0, 0, 0, 0, 0, 7, 6])

    def test_negative_range(self) -> None:
        for invalid in (-1, h.HYDRATED_STATES, True, 1.5):
            with self.assertRaises(h.Pass188Error):
                h.decode_projected(invalid)  # type: ignore[arg-type]

    def test_boundary_roundtrip(self) -> None:
        for address in (0, 1, 242, 243, h.HYDRATED_STATES - 1):
            transition = h.transition_projected(address)
            self.assertEqual(transition.input.g243, transition.output.g243)
            self.assertEqual(transition.input.vm81_cell, transition.output.vm81_cell)
            self.assertEqual(transition.input.operation_class8, transition.output.operation_class8)
            receipt = h.receipt_dict(transition)
            self.assertTrue(h.replay_receipt(receipt))
            altered = copy.deepcopy(receipt)
            altered["output"]["projected_address"] += 1
            self.assertFalse(h.replay_receipt(altered))

    def test_hash_widths(self) -> None:
        transition = h.transition_projected(0)
        self.assertEqual(len(transition.predecessor_hash72), 72)
        self.assertEqual(len(transition.successor_hash72), 72)
        self.assertEqual(len(transition.combined_hash216), 216)

    def test_full_hydration(self) -> None:
        summary = h.hydrate()
        self.assertEqual(summary["hydrated_states"], h.HYDRATED_STATES)
        self.assertEqual(summary["active_period_two_states"], 629_856)
        self.assertEqual(summary["asymmetric_collapse_states"], 629_856)
        self.assertEqual(summary["gear_preserved_states"], h.HYDRATED_STATES)
        self.assertEqual(summary["coordinate_drift_states"], 0)
        self.assertEqual(summary["deterministic_checksum_u64"], "11e3bbf0214751c3")
        self.assertTrue(summary["checksum_matches_pass187"])


if __name__ == "__main__":
    unittest.main()
