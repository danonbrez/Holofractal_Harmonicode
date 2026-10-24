import unittest
from unittest.mock import patch
from types import SimpleNamespace
from hhs_runtime.hhs_pass220_genesis_pairwise_fingerprint_v1 import derive_genesis_pair, replay_genesis_pair, native_ordered_phase_pair, replay_native_ordered_phase_pair

class GenesisPairTests(unittest.TestCase):
    def setUp(self):
        self.args = dict(index_a=0,index_b=5183,value_a=19,value_b=29,
                         genesis_identity="genesis-test-fixture",genesis_value=0)

    def test_exact_ordered_replay(self):
        witness = derive_genesis_pair(**self.args)
        self.assertEqual(witness,replay_genesis_pair(witness,**self.args))
        self.assertEqual(witness["source"]["coordinate"]["linear_index"],0)
        self.assertEqual(witness["target"]["coordinate"]["linear_index"],5183)
        self.assertFalse(witness["gyroscopic_orientation_native_verified"])
        self.assertFalse(witness["signed_hash216_closure_verified"])

    def test_platonic_phase_pair_replay(self):
        witness=derive_genesis_pair(**self.args)
        g=witness["inherited_platonic_phase_projection"]
        self.assertEqual(g["factorizations"], ((72,72),(64,81),(36,144),(48,108)))
        self.assertTrue(g["pentagon_closure"])
        self.assertTrue(g["dodecahedron_incidence"])
        self.assertEqual((g["forward_step"]+g["reverse_step"])%72,0)
        tampered=dict(witness)
        tampered["inherited_platonic_phase_projection"]=dict(g,forward_step=9)
        with self.assertRaisesRegex(ValueError,"REPLAY_MISMATCH"):
            replay_genesis_pair(tampered,**self.args)

    def test_reverse_direction_is_distinct(self):
        a=derive_genesis_pair(**self.args)
        args=dict(self.args,index_a=5183,index_b=0,value_a=29,value_b=19)
        b=derive_genesis_pair(**args)
        self.assertNotEqual(a["candidate_proof_sha256"],b["candidate_proof_sha256"])

    def test_native_abi_adapter_routes_ordered_products(self):
        class NativeSpy:
            calls = []
            @staticmethod
            def validate():
                return True
            @staticmethod
            def address_decode(index):
                return (index // 64, (index % 64) // 8, index % 8)
            @staticmethod
            def phase_product(left, right):
                NativeSpy.calls.append((left, right))
                return {"left_basis": left, "right_basis": right,
                        "phase": (left + right) % 8, "ordered_tag": left * 8 + right}
        target = "hhs_python.runtime.hhs_exact_ctypes_bridge"
        with patch.dict("sys.modules", {target: SimpleNamespace(HHSExactRuntimeBridge=NativeSpy)}):
            record = native_ordered_phase_pair(**self.args)
            self.assertTrue(record["native_phase_evidence"]["native_exact_phase_abi_verified"])
            self.assertFalse(record["native_phase_evidence"]["native_genesis_ancestry_verified"])
            self.assertEqual(record, replay_native_ordered_phase_pair(record, **self.args))
            tampered = dict(record, candidate_proof_sha256="0" * 64)
            with self.assertRaisesRegex(ValueError, "REPLAY_MISMATCH"):
                replay_native_ordered_phase_pair(tampered, **self.args)
        self.assertEqual(len(NativeSpy.calls), 6)

    def test_tampered_genesis_fails_replay(self):
        witness=derive_genesis_pair(**self.args)
        with self.assertRaisesRegex(ValueError,"REPLAY_MISMATCH"):
            replay_genesis_pair(witness,**dict(self.args,genesis_identity="changed"))

    def test_reject_out_of_range_and_float(self):
        with self.assertRaises(ValueError):
            derive_genesis_pair(**dict(self.args,index_b=5184))
        with self.assertRaises(ValueError):
            derive_genesis_pair(**dict(self.args,value_a=1.0))

if __name__ == "__main__":
    unittest.main()
