"""Execute bounded native C11 exact denominator decision + inherited passthrough.

This test does NOT bypass the frozen-course source-graph rejection, or claim
Lane 5/VM81 admission.
"""
import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path

from hhs_runtime.hhs_pass220_course_passthrough_native_witness_binding_v1 import Witness
from hhs_runtime.hhs_pass220_course_m195_hnan_bridge_v1 import (
    exact_denominator_gaussian,
)

class Decision(ctypes.Structure):
    _fields_ = [
        ("denominator_real", ctypes.c_int64),
        ("denominator_imag", ctypes.c_int64),
        ("exact_guard_evaluated", ctypes.c_uint32),
        ("denominator_zero", ctypes.c_uint32),
        ("inherited_c_passthrough_invoked", ctypes.c_uint32),
        ("canonical_admission", ctypes.c_uint32),
    ]

class TestM195NativeGaussianIngress(unittest.TestCase):
    def test_source_derived_c11_singularity_and_inherited_passthrough(self):
        with tempfile.TemporaryDirectory() as temp:
            so = str(Path(temp) / "libhhs_m195_gaussian.so")
            subprocess.run([
                "cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                "-pedantic", "-shared", "-fPIC", "-Ihhs_runtime/include",
                "hhs_runtime/c/hhs_pass220_course_passthrough_witness.c",
                "hhs_runtime/c/hhs_pass220_course_m195_gaussian_hnan_ingress_v1.c",
                "-o", so,
            ], check=True, timeout=60)
            lib = ctypes.CDLL(so)
            denom = lib.hhs220_m195_gaussian_denominator
            denom.argtypes = [ctypes.c_int32, ctypes.c_int32,
                              ctypes.POINTER(Decision)]
            denom.restype = ctypes.c_int
            gate = lib.hhs220_m195_gaussian_hnan_candidate
            gate.argtypes = [
                ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p,
                ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t,
                ctypes.c_void_p, ctypes.c_void_p,
                ctypes.POINTER(Witness), ctypes.POINTER(Decision),
            ]
            gate.restype = ctypes.c_int
            carrier = bytes(range(256)) * 2 + bytes(range(136))
            phase = bytes(range(72))
            for a, b in ((0,0), (-3,4), (-3,-4), (1,0),
                         (100000,100000), (100001,0), (-100001,0)):
                d=Decision()
                expected=exact_denominator_gaussian(a,b)
                accepted=int(abs(a)<=100000 and abs(b)<=100000)
                self.assertEqual(denom(a,b,ctypes.byref(d)),accepted)
                if accepted:
                    self.assertEqual((d.denominator_real,d.denominator_imag),expected)
                self.assertEqual(d.exact_guard_evaluated,accepted)
                ci=ctypes.create_string_buffer(carrier,len(carrier))
                pi=ctypes.create_string_buffer(phase,len(phase))
                co=ctypes.create_string_buffer(b"q"*len(carrier),len(carrier))
                po=ctypes.create_string_buffer(b"z"*len(phase),len(phase))
                receipt=Witness()
                d=Decision()
                ok=gate(a,b,ci,len(carrier),pi,len(phase),
                        co,po,ctypes.byref(receipt),ctypes.byref(d))
                is_root=accepted and expected==(0,0)
                self.assertEqual(ok,int(is_root))
                self.assertEqual(d.inherited_c_passthrough_invoked,int(is_root))
                self.assertEqual(d.canonical_admission,0)
                if is_root:
                    self.assertEqual(co.raw,carrier)
                    self.assertEqual(po.raw,phase)
                    self.assertEqual((receipt.gain_numerator,
                                      receipt.gain_denominator),(1,1))
                    self.assertEqual(receipt.phase_writes,0)
                    self.assertEqual(receipt.canonical_admission,0)
                else:
                    self.assertEqual(co.raw,b"q"*len(carrier))
                    self.assertEqual(po.raw,b"z"*len(phase))
                    self.assertEqual(receipt.decision,0)

    def test_null_decision_rejected(self):
        self.assertEqual(Decision().canonical_admission,0)

if __name__=="__main__":
    unittest.main()
