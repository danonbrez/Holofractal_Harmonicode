"""Q81 symbolic-P -> VM81 RNA frame -> HNAN/I074 candidate, unmocked."""
from __future__ import annotations
import unittest

from hhs_runtime.hhs_pass220_hash216_symbolic_tensor_metadata_v1 import (
    TensorRef, SymbolicTensorError,
)
from hhs_runtime.hhs_pass220_i074_full_tensor_hnan_closure_hydration_v1 import (
    build_candidate,
)
from hhs_runtime.hhs_pass220_q81_symbolic_p_phase_source_binding_v1 import (
    Q81SymbolicSourceError, bind_symbolic_candidate,
)
from hhs_runtime.hhs_pass220_q81_binary_phase_hnan_projection_v1 import (
    verify_receipt,
)

PAIRS = tuple(tuple(
    ((0,1),(1,0),(-1,1),(1,-1))[(9*i+j)%4]
    for j in range(9)
) for i in range(9))


class TestQ81SymbolicPSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.i074=build_candidate()
        cls.lineage=cls.i074["candidate_hash216"]

    def ref(self,p,*,lineage=None,root="q81-global"):
        return TensorRef(P=p,modality="symbolic",hash216_lineage=(
            lineage if lineage is not None else self.lineage
        ),constraint_root=root)

    def test_inherited_symbolic_vm81_and_q81_phase_receipt(self):
        receipt=bind_symbolic_candidate(
            "ADD",self.ref(1),self.ref(2),PAIRS,
            inherited_i074_candidate=self.i074,
            lane_index=0,
        )
        self.assertEqual(receipt["derived_P"],"3")
        self.assertTrue(receipt["symbolic_p_to_raw_frame_checked"])
        self.assertTrue(verify_receipt(receipt["q81_candidate"]["binary_phase_receipt"]))
        self.assertEqual(receipt["i074_hash216"],self.lineage)
        self.assertFalse(receipt["ordered_phase_pairs_proven_by_symbolic_solver"])
        self.assertFalse(receipt["native_hnan_closure_proven"])
        self.assertFalse(receipt["vm81_admission_invoked"])

    def test_reject_wrong_lineage(self):
        with self.assertRaisesRegex(Q81SymbolicSourceError,"SYMBOLIC_I074_LINEAGE_MISMATCH"):
            bind_symbolic_candidate(
                "ADD",self.ref(1,lineage="X"*216),self.ref(2),PAIRS,
                inherited_i074_candidate=self.i074,
            )

    def test_reject_mismatched_global_roots(self):
        with self.assertRaises(SymbolicTensorError):
            bind_symbolic_candidate(
                "ADD",self.ref(1,root="left"),self.ref(2,root="right"),
                PAIRS,inherited_i074_candidate=self.i074,
            )

    def test_reject_invalid_lane_and_unregistered_op(self):
        with self.assertRaisesRegex(Q81SymbolicSourceError,"RNA_LANE_INDEX"):
            bind_symbolic_candidate(
                "ADD",self.ref(1),self.ref(2),PAIRS,
                inherited_i074_candidate=self.i074,lane_index=True,
            )
        with self.assertRaises(SymbolicTensorError):
            bind_symbolic_candidate(
                "COMMUTED_MUL",self.ref(1),self.ref(2),PAIRS,
                inherited_i074_candidate=self.i074,
            )


if __name__=="__main__":
    unittest.main()
