"""Pass220 Q81 phase ingress/egress candidate projection regression tests."""
from __future__ import annotations

from copy import deepcopy
import unittest

from hhs_runtime.hhs_pass220_q81_binary_phase_hnan_projection_v1 import (
    Q81PhaseProjectionError,
    decode_candidate,
    encode_candidate,
    verify_receipt,
)


def fixture():
    binary = tuple(
        tuple((row + col) % 2 for col in range(9))
        for row in range(9)
    )
    orientation = tuple(
        tuple((row // 3 + col) % 2 for col in range(9))
        for row in range(9)
    )
    context = {
        "orientation": orientation,
        "source_identity": "source:ordered-hnan-phase:fixture",
        "provenance": {
            "address": "HNAN",
            "swap": ["xy", "yx", "zw", "wz"],
            "residue": ["N", "Q", "radical"],
            "phase": 17,
            "curvature": "kappa",
            "return": "original-carrier",
        },
    }
    return binary, context


class Q81PhaseProjectionTests(unittest.TestCase):
    def test_complete_81_roundtrip_and_context(self):
        binary, context = fixture()
        native = decode_candidate(binary, context=context)
        receipt = encode_candidate(native)
        self.assertTrue(verify_receipt(receipt))
        self.assertEqual(receipt["binary"], binary)
        self.assertEqual(receipt["context"], context)
        self.assertTrue(receipt["native_roundtrip_exact"])
        self.assertEqual(len(native["native_ordered_pairs"]), 9)

    def test_all_four_phase_cases(self):
        binary, context = fixture()
        native = decode_candidate(binary, context=context)
        for row in range(9):
            for col in range(9):
                phase = native["native_ordered_pairs"][row][col]
                bit = binary[row][col]
                direction = context["orientation"][row][col]
                expected = (((0, 1), (1, 0)), ((-1, 1), (1, -1)))
                self.assertEqual(phase, expected[bit][direction])

    def test_missing_context_is_rejected(self):
        binary, _ = fixture()
        with self.assertRaises(Q81PhaseProjectionError):
            decode_candidate(binary, context={})

    def test_missing_source_identity_is_rejected(self):
        binary, context = fixture()
        context.pop("source_identity")
        with self.assertRaises(Q81PhaseProjectionError):
            decode_candidate(binary, context=context)

    def test_orientation_tamper_is_rejected(self):
        binary, context = fixture()
        native = decode_candidate(binary, context=context)
        tampered = deepcopy(native)
        orientation = [list(row) for row in native["orientation"]]
        orientation[0][0] ^= 1
        tampered["orientation"] = orientation
        with self.assertRaisesRegex(Q81PhaseProjectionError, "ORIENTATION_WITNESS_MISMATCH"):
            encode_candidate(tampered)

    def test_false_authority_is_rejected(self):
        binary, context = fixture()
        receipt = encode_candidate(decode_candidate(binary, context=context))
        tampered = deepcopy(receipt)
        tampered["canonical_vm81_mutation_authority"] = True
        with self.assertRaisesRegex(Q81PhaseProjectionError, "RECEIPT_AUTHORITY"):
            verify_receipt(tampered)

    def test_loss_of_provenance_is_detected(self):
        binary, context = fixture()
        receipt = encode_candidate(decode_candidate(binary, context=context))
        tampered = deepcopy(receipt)
        del tampered["context"]["provenance"]
        with self.assertRaises(Q81PhaseProjectionError):
            verify_receipt(tampered)

    def test_binary_bit_tamper_changes_native(self):
        binary, context = fixture()
        native = decode_candidate(binary, context=context)
        wrong = [list(row) for row in binary]
        wrong[4][4] ^= 1
        changed = decode_candidate(wrong, context=context)
        self.assertNotEqual(changed["native_ordered_pairs"], native["native_ordered_pairs"])

    def test_bool_and_ragged_inputs_rejected(self):
        binary, context = fixture()
        wrong = [list(row) for row in binary]
        wrong[0][0] = True
        with self.assertRaises(Q81PhaseProjectionError):
            decode_candidate(wrong, context=context)
        with self.assertRaises(Q81PhaseProjectionError):
            decode_candidate([[0]], context=context)

    def test_unknown_phase_pair_rejected(self):
        binary, context = fixture()
        native = decode_candidate(binary, context=context)
        tampered = deepcopy(native)
        changed = [list(row) for row in native["native_ordered_pairs"]]
        changed[0][0] = (1, 1)
        tampered["native_ordered_pairs"] = changed
        with self.assertRaisesRegex(Q81PhaseProjectionError, "PAIR_DOMAIN"):
            encode_candidate(tampered)


if __name__ == "__main__":
    unittest.main()
