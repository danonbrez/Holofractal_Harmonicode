from __future__ import annotations

import json
import unittest

from hhs_pass158 import (
    Context,
    ExactRational,
    HHS158_OP_BIND_EQ,
    HHS158_OP_CHAIN_APPEND,
)


class PythonBindingConformance(unittest.TestCase):
    def test_complete_public_lifecycle(self) -> None:
        with Context() as context:
            definition, definition_receipt = context.register_definition(
                name="PYTHON_SYMBOLIC_CONSTRAINT_APPLICATION",
                constraints="A==B==C; O!=Pi; Delta=P^2-pq",
                symbols="A,B,C,O,Pi,Delta,P,p,q,x,ordered",
                shape=(9, 9),
            )
            self.assertEqual(
                definition_receipt.serialize()["classification"],
                "HHS_P158_NFT_DEFINITION_REGISTERED",
            )
            instance, instance_receipt = definition.instantiate(b"python-binding-instance-0001")
            self.assertEqual(
                instance_receipt.serialize()["classification"],
                "HHS_P158_NFT_INSTANCE_CONSTRUCTED",
            )
            instance.bind_rational("x", ExactRational(2, 6))
            instance.bind_ordered_list("ordered", ["x", "x", "y"])
            validation = instance.validate()
            self.assertEqual(
                validation["classification"],
                "HHS_P158_ABI_APPLICATION_BINDING_VALIDATED",
            )
            capability = instance.capability(commit=True)
            result, receipt = instance.execute(
                capability,
                [
                    (HHS158_OP_BIND_EQ, "A,B"),
                    (HHS158_OP_CHAIN_APPEND, "B,C"),
                ],
                commit=True,
            )
            self.assertEqual(result.classification, "HHS_VM81_TRANSITION_COMMITTED")
            self.assertGreaterEqual(result.vm81_steps, 72)
            serialized_receipt = receipt.serialize()
            self.assertEqual(
                serialized_receipt["classification"],
                "HHS_P158_HASH72_EXECUTION_RECEIPT_CLOSED",
            )
            self.assertEqual(len(serialized_receipt["receipt_id"]), 72)
            self.assertEqual(len(serialized_receipt["object_root"]), 216)
            replay = receipt.replay()
            self.assertTrue(replay["matched"])
            self.assertEqual(
                replay["classification"],
                "HHS_P158_NFT_TRANSITION_REPLAY_VERIFIED",
            )
            serialized_instance = instance.serialize()
            envelope = json.loads(serialized_instance)
            self.assertEqual(envelope["schema"], "HHS158_CANONICAL_V1")
            self.assertEqual(len(envelope["object_hash"]), 216)

    def test_exact_rational_has_no_implicit_float_lane(self) -> None:
        rational = ExactRational(179971179971, 1000000)
        self.assertEqual(rational.numerator, 179971179971)
        self.assertEqual(rational.denominator, 1000000)
        with self.assertRaises(TypeError):
            float(rational)

    def test_negative_denominator_is_rejected_before_ffi(self) -> None:
        with self.assertRaises(ValueError):
            ExactRational(1, -3)

    def test_duplicate_order_is_preserved(self) -> None:
        with Context() as context:
            definition, _ = context.register_definition(
                name="ORDERED_LIST_OBJECT",
                constraints="LIST_ORDERED([x,x,y])",
                symbols="x,y,ordered",
                shape=(1, 3),
            )
            instance, _ = definition.instantiate(b"ordered-list-instance")
            instance.bind_ordered_list("ordered", ["x", "x", "y"])
            payload = instance.serialize().decode("utf-8")
            self.assertIn("payload_hex", payload)


if __name__ == "__main__":
    unittest.main()
