"""Fail-closed native HNAN binding tests; no fabricated native execution."""
import unittest
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

from hhs_runtime.hhs_pass220_course_m195_hnan_bridge_v1 import (
    bind_m195_hnan_boundary, bind_m195_source_derived_singular_route,
    exact_denominator_gaussian, SINGULAR_ROOTS,
)
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError


class TestM195HNANBridge(unittest.TestCase):
    def test_singular_spectrum_retained(self):
        self.assertEqual(SINGULAR_ROOTS, ("0", "-3+4I", "-3-4I"))

    def test_actual_compiled_native_zero_divisor_passthrough(self):
        # Execute the inherited C code, not a mocked success receipt.
        # Exact Gaussian integer arithmetic proves that each labelled root
        # zeroes D; the inherited native ABI receives an explicit zero flag.
        roots = ((0, 0), (-3, 4), (-3, -4))
        with tempfile.TemporaryDirectory() as folder:
            library = str(Path(folder) / "libcourse_passthrough.so")
            subprocess.run([
                "cc", "-std=c11", "-O2", "-fPIC", "-shared",
                "-Wall", "-Wextra", "-Werror", "-pedantic",
                "-Ihhs_runtime/include",
                "hhs_runtime/c/hhs_pass220_course_passthrough_witness.c",
                "-o", library,
            ], check=True, timeout=60)
            for real, imaginary in roots:
                self.assertEqual(exact_denominator_gaussian(real, imaginary), (0, 0))
                carrier = (f"M195|x={real},{imaginary}|".encode("ascii")
                           * 64)[:648].ljust(648, bytes([0]))
                phase = bytes(range(72))
                evidence = bind_m195_source_derived_singular_route(
                    library, real, imaginary, carrier, phase)
                self.assertEqual(evidence["module"], 195)
                self.assertEqual(evidence["singularity_decision"], "EXACT_D_ZERO")
                self.assertEqual(evidence["singularity_decision_location"],
                                 "M195_PYTHON_ADAPTER_NOT_LANE5")
                self.assertTrue(evidence["native_zero_divisor_passthrough_executed"])
                self.assertEqual(evidence["gain"], "1/1")
                self.assertEqual(evidence["phase_writes"], 0)
                self.assertFalse(evidence["original_typed_equality_admitted"])
                self.assertFalse(evidence["lane5_5184_hydration_verified"])
                self.assertFalse(evidence["canonical_vm81_admission"])
                self.assertFalse(evidence["hash72_minted"])
                self.assertFalse(evidence["hash216_minted"])

    def test_nonroot_cannot_trigger_native_bypass(self):
        self.assertEqual(exact_denominator_gaussian(1, 0), (32, 0))
        with patch(
            "hhs_runtime.hhs_pass220_course_m195_hnan_bridge_v1."
            "bind_m195_hnan_boundary"
        ) as inherited:
            with self.assertRaisesRegex(
                ProofCorpusError, "COURSE_M195_DENOMINATOR_NONZERO_NO_HNAN_BYPASS"
            ):
                bind_m195_source_derived_singular_route(
                    "irrelevant", 1, 0, b"carrier", b"phase")
            inherited.assert_not_called()

    def test_exact_guard_rejects_float_coercion(self):
        with self.assertRaisesRegex(ProofCorpusError, "EXACT_GAUSSIAN_INTEGER"):
            exact_denominator_gaussian(-3.0, 4)

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
