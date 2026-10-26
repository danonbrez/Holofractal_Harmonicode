"""Existing HARMONICODE tokenizer receives additive HNAN proof metadata."""
import unittest
from dataclasses import replace
from hhs_runtime.hhs_loshu_phase_embedding_v1 import (
    embed_token, exact_identity_token_witness,
)

class TestExistingTokenizerHNAN(unittest.TestCase):
    def test_same_token_and_existing_receipt(self):
        state = embed_token("t^3-t", 2, 0, 72)
        before = state.to_dict()
        witness = exact_identity_token_witness(
            state, ordered_operator="AB", left_source="A",
            right_source="B", quartic_source="P^4",
        )
        self.assertEqual(state.to_dict(), before)
        self.assertEqual(witness["existing_receipt"], state.receipt_hash72)
        self.assertEqual(witness["lo_shu_cell_index"], state.lo_shu.cell_index)
        self.assertFalse(witness["native_quartic_closure_certified"])
        self.assertFalse(witness["canonical_vm81_mutation_authority"])
        self.assertTrue(witness["candidate_only"])

    def test_opposite_order_preserved(self):
        state = embed_token("AB", 1, 1, 72)
        args = dict(left_source="A", right_source="B", quartic_source="P^4")
        ab = exact_identity_token_witness(state, ordered_operator="AB", **args)
        ba = exact_identity_token_witness(state, ordered_operator="BA", **args)
        self.assertNotEqual(ab["ordered_operator"], ba["ordered_operator"])
        self.assertEqual(ab["existing_receipt"], ba["existing_receipt"])

    def test_reject_phase_tampering(self):
        state = embed_token("xy", 0, 0, 72)
        tampered = replace(state, reciprocal_phase_index=(state.reciprocal_phase_index + 1) % 72)
        with self.assertRaisesRegex(ValueError, "RECIPROCAL_PHASE_DRIFT"):
            exact_identity_token_witness(tampered, ordered_operator="AB", left_source="A", right_source="B", quartic_source="P^4")

    def test_reject_opaque_missing_operand(self):
        state = embed_token("xy", 0, 0, 72)
        with self.assertRaisesRegex(ValueError, "EXACT_SOURCE_REQUIRED"):
            exact_identity_token_witness(state, ordered_operator="AB", left_source="", right_source="B", quartic_source="P^4")

if __name__ == "__main__":
    unittest.main()
