"""Tests of the P/t/m native sweep handoff and exact output receipt.

The fixture executor below is intentionally synthetic: it verifies adapter
transport and comparison behavior, NOT HARMONICODE native evaluation.
"""
from __future__ import annotations

from fractions import Fraction
from hhs_runtime.pass220 import pass220_ptm_native_sweep_adapter_v1 as adapter
from hhs_runtime.pass220 import pass220_ptm_exact_generator_witness_v1 as reference
import unittest


class TestPtmSweepAdapter(unittest.TestCase):
    @staticmethod
    def fixture(source: str, P: str, t: int, m: int):
        assert source == reference.GENERATOR_SOURCE
        assert P == "Sqrt(3)"
        return tuple(tuple(cell + Fraction(t-25,100) + Fraction(m-248,1000)
                           for cell in row) for row in reference.REFERENCE)

    def test_requires_native_executor(self):
        with self.assertRaisesRegex(adapter.PtmExecutionError, "NOT_BOUND"):
            adapter.sweep(None)

    def test_source_identity_and_complete_parameter_grid(self):
        receipt = adapter.sweep(self.fixture)
        self.assertEqual(receipt["state_count"],9)
        self.assertEqual(tuple((row["t"],row["m"]) for row in receipt["outputs"]),adapter.SWEEP)
        self.assertEqual(receipt["source_sha256"],reference.witness()["generator_sha256"])

    def test_reference_coordinates(self):
        receipt=adapter.sweep(self.fixture)
        center=next(row for row in receipt["outputs"] if (row["t"],row["m"]) == (25,248))
        self.assertEqual(center["matrix"], reference.REFERENCE)
        self.assertEqual(center["ratios_to_supplied_reference"][1][1],None)
        self.assertEqual(center["ratios_to_supplied_reference"][0][0],"1")

    def test_exact_receipt_serialization(self):
        serialized=adapter.serialize_exact(adapter.sweep(self.fixture))
        self.assertEqual(serialized["state_count"],9)
        self.assertEqual(serialized["outputs"][4]["matrix"][0][0],"-1012501/6250")
        self.assertEqual(serialized["native_evaluation"],"EXECUTOR_SUPPLIED")

    def test_rejects_inexact_or_wrong_shape(self):
        for result in ([[1.,2.,3.],[4.,5.,6.],[7.,8.,9.]],
                       [[Fraction(1)]],
                       [[1,2,3],[4,5,6],[7,8,9]]):
            with self.subTest(result=result):
                with self.assertRaises(adapter.PtmExecutionError):
                    adapter.sweep(lambda source,P,t,m:result)

    def test_does_not_divide_zero_reference_center(self):
        probe=adapter.ratios(reference.REFERENCE,reference.REFERENCE)
        self.assertIsNone(probe[1][1])
        self.assertTrue(all(
            probe[i][j]=="1" for i in range(3) for j in range(3) if (i,j)!=(1,1)
        ))


if __name__ == "__main__":
    unittest.main()
