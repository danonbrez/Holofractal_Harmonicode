"""Focused candidate bridge tests; run from repository root."""
import unittest

from hhs_runtime.pass220.genesis_color_qudit_candidate_v1 import (
    GENESIS, INVERSION, phase_color_candidate,
)


class GenesisColorQuditCandidateTests(unittest.TestCase):
    def test_full_address_bijection(self):
        addresses = set()
        for cell in range(81):
            for op in range(64):
                result = phase_color_candidate(
                    cell=cell, operation64=op, phase72=(64*cell+op)%72,
                    residue=0.5, probability=0.5,
                )
                addresses.add(result["linear5184"])
                self.assertFalse(result["vm81_admitted"])
                self.assertFalse(result["hnan_gate_verified"])
        self.assertEqual(addresses, set(range(5184)))

    def test_center_lo_shu_reference(self):
        item = phase_color_candidate(
            cell=40, operation64=0, phase72=0,
            residue=0.0, probability=1.0,
        )
        self.assertEqual(item["symbol"], 5)
        self.assertEqual(item["g41_class"], 41)
        self.assertEqual(item["local_bigint"], "0")

    def test_endpoints_remain_unverified(self):
        args = dict(cell=40, operation64=0, phase72=0,
                    residue=0.0, probability=1.0)
        white = phase_color_candidate(**args, classification=GENESIS)
        black = phase_color_candidate(**args, classification=INVERSION)
        self.assertEqual(white["rgb8"], (255, 255, 255))
        self.assertEqual(black["rgb8"], (0, 0, 0))
        self.assertFalse(white["classification_verified"])
        self.assertFalse(black["classification_verified"])

    def test_reject_invalid_coordinates_and_ieee(self):
        args = dict(cell=0, operation64=0, phase72=0,
                    residue=0.0, probability=1.0)
        for changes in (
            dict(cell=81), dict(operation64=64), dict(phase72=72),
            dict(cell=True), dict(residue=float("nan")),
            dict(probability=float("inf")), dict(residue=-0.01),
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                phase_color_candidate(**(args | changes))


if __name__ == "__main__":
    unittest.main()
