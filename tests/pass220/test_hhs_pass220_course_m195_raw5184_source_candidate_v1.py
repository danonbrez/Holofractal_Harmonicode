"""Verify scoped 5184-carrier source-bound native candidate, not VM81."""
import subprocess
import tempfile
import unittest
from pathlib import Path

from hhs_runtime.hhs_pass220_course_m195_raw5184_source_candidate_v1 import (
    source_bound_candidate,
)
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError


class TestM195SourceBoundRaw5184(unittest.TestCase):
    def test_exact_c11_candidate_and_nonroot_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib = str(Path(tmp) / "libm195.so")
            subprocess.run([
                "cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                "-pedantic", "-shared", "-fPIC", "-Ihhs_runtime/include",
                "hhs_runtime/c/hhs_pass220_course_passthrough_witness.c",
                "hhs_runtime/c/hhs_pass220_course_m195_gaussian_hnan_ingress_v1.c",
                "-o", lib
            ], check=True, timeout=60)
            carrier = bytes(range(256)) * 20 + bytes(range(64))
            self.assertEqual(len(carrier), 5184)
            phase = bytes(range(72))
            m = b"typed-m-register|cell-provenance-unadmitted"
            for a,b in ((0,0),(-3,4),(-3,-4)):
                out=source_bound_candidate(
                    lib,a,b,typed_m_register=m,
                    raw5184_carrier=carrier,phase72=phase)
                self.assertEqual(out["native_exact_denominator"],[0,0])
                self.assertTrue(out["native_source_derived_zero_guard"])
                self.assertTrue(out["raw5184_bytes_preserved"])
                self.assertTrue(out["phase72_bytes_preserved"])
                self.assertEqual(out["native_phase_writes"],0)
                self.assertFalse(out["typed_m_equality_admitted"])
                self.assertFalse(out["vm81_admission"])
                self.assertFalse(out["hash216_minted"])
            with self.assertRaisesRegex(ProofCorpusError,"NONZERO_NON_HNAN_ROUTE"):
                source_bound_candidate(
                    lib,1,0,typed_m_register=m,
                    raw5184_carrier=carrier,phase72=phase)
            with self.assertRaisesRegex(ProofCorpusError,"TYPED_5184"):
                source_bound_candidate(
                    lib,0,0,typed_m_register=m,
                    raw5184_carrier=carrier[:-1],phase72=phase)
            with self.assertRaisesRegex(ProofCorpusError,"TYPED_5184"):
                source_bound_candidate(
                    lib,0,0,typed_m_register=b"",
                    raw5184_carrier=carrier,phase72=phase)
            with self.assertRaisesRegex(ProofCorpusError,"OUT_OF_PROOF_RANGE"):
                source_bound_candidate(
                    lib,100001,0,typed_m_register=m,
                    raw5184_carrier=carrier,phase72=phase)


if __name__ == "__main__":
    unittest.main()
