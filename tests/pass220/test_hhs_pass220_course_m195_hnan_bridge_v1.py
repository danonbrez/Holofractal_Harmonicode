"""Fail-closed native HNAN binding tests; no fabricated native execution."""
import unittest
from unittest.mock import patch

from hhs_runtime.hhs_pass220_course_m195_hnan_bridge_v1 import (
    bind_m195_hnan_boundary, SINGULAR_ROOTS,
)
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError


class TestM195HNANBridge(unittest.TestCase):
    def test_singular_spectrum_retained(self):
        self.assertEqual(SINGULAR_ROOTS, ("0", "-3+4I", "-3-4I"))

    def test_missing_native_library_rejected(self):
        with self.assertRaises(ProofCorpusError):
            bind_m195_hnan_boundary(
                "/no/such/native_hnan_library.so", b"carrier", b"phase")

    def test_untyped_carriers_rejected(self):
        with self.assertRaises(ProofCorpusError):
            bind_m195_hnan_boundary("missing.so", "carrier", b"phase")

    def test_declared_native_result_is_not_enough(self):
        # A forged positive status with no independently valid inherited
        # scope is rejected, not upgraded to a Module 195 proof.
        with patch(
            "hhs_runtime.hhs_pass220_course_m195_hnan_bridge_v1."
            "bind_executed_course_passthrough",
            return_value={"native_execution_witness_verified": True,
                          "canonical_vm81_admission": False,
                          "hash216_minted": False,
                          "witness_scope": "UNRELATED"}
        ):
            with self.assertRaisesRegex(ProofCorpusError,
                                        "COURSE_M195_NATIVE_HNAN_SCOPE_REJECTED"):
                bind_m195_hnan_boundary("not-invoked", b"carrier", b"phase")


if __name__ == "__main__":
    unittest.main()
