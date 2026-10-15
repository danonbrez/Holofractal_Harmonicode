"""Bind exact Course Module 9 to an independent native passthrough witness.

Only validates byte-exact identity for the zero-divisor branch. Does not
verify every theorem gate or re-prove the established native HNAN phase gate.
"""
from __future__ import annotations
import ctypes
from pathlib import Path
from hhs_runtime.hhs_pass220_course_hnan_passthrough_evidence_v1 import course_hnan_proof_obligations
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError

class Witness(ctypes.Structure):
    _fields_=[(name,ctypes.c_uint32) for name in (
        "decision","bypass_applied","gain_numerator","gain_denominator",
        "phase_writes","carrier_preserved","phase_preserved","canonical_admission")]

def execute_course_passthrough_native_witness(library:str,carrier:bytes,phase:bytes)->dict:
    obligations=course_hnan_proof_obligations()
    if not library or not Path(library).is_file() or not carrier or not phase:
        raise ProofCorpusError("PASSTHROUGH_NATIVE_INPUT_REQUIRED")
    lib=ctypes.CDLL(library)
    fn=lib.hhs220_course_passthrough_execute
    fn.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,
                 ctypes.c_uint32,ctypes.c_void_p,ctypes.c_void_p,ctypes.POINTER(Witness)]
    fn.restype=ctypes.c_int
    ca=ctypes.create_string_buffer(carrier,len(carrier))
    pa=ctypes.create_string_buffer(phase,len(phase))
    co=ctypes.create_string_buffer(len(carrier))
    po=ctypes.create_string_buffer(len(phase))
    receipt=Witness()
    ok=fn(ca,len(carrier),pa,len(phase),1,co,po,ctypes.byref(receipt))
    if (ok!=1 or co.raw!=carrier or po.raw!=phase or receipt.decision!=1
        or receipt.bypass_applied!=1 or
        (receipt.gain_numerator,receipt.gain_denominator)!=(1,1)
        or receipt.phase_writes!=0 or receipt.carrier_preserved!=1
        or receipt.phase_preserved!=1 or receipt.canonical_admission!=0):
        raise ProofCorpusError("NATIVE_COURSE_BYPASS_WITNESS_REJECTED")
    return {"course_module_sha256":obligations["course_module_sha256"],
            "course_source_sha256":obligations["course_sha256"],
            "independent_passthrough_native_witness_executed":True,
            "carrier_preserved":True,"phase_preserved":True,
            "gain_exact":"1/1","phase_writes":0,
            "native_hnan_gate_inherited_unchanged":True,
            "complete_course_theorem_proved":False,
            "canonical_vm81_admission":False,"hash216_minted":False}
