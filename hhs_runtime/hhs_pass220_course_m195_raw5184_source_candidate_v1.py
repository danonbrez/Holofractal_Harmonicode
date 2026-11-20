"""Read-only Module 195 5184-cell candidate bound to exact source and C11 ABI.

This is a candidate producer membrane, NOT Pass219 I157 equivalence,
Lane5_BIOS approval, a VM81 transition, or a Hash72/Hash216 mint.
"""
from __future__ import annotations

import ctypes
from hashlib import sha256
from pathlib import Path
import subprocess

from hhs_runtime.hhs_pass220_course_m195_spectral_tensor_witness_v1 import (
    SOURCE, evaluate,
)
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError
from hhs_runtime.hhs_pass220_course_passthrough_native_witness_binding_v1 import Witness

SCHEMA = "HHS_PASS220_M195_EXACT_5184_NATIVE_CANDIDATE_V1"
DOC = "docs/pass220/HARMONICODE_ALGEBRA_COURSE_MODULE_195_SPECTRAL_TENSOR.md"
# Pinned Module 195 note/source objects, separate from legacy whitepaper freeze.
DOC_GIT_BLOB = "c73fab968e8a76a7efb658701333ccafc66c4c8c"
SOURCE_GIT_BLOB = "d45f4d25b6e7ffe56c495c6354274649bd3e6757"
RAW5184 = 5184
PHASE_WIDTH = 72


class GaussianDecision(ctypes.Structure):
    _fields_ = [
        ("denominator_real", ctypes.c_int64),
        ("denominator_imag", ctypes.c_int64),
        ("exact_guard_evaluated", ctypes.c_uint32),
        ("denominator_zero", ctypes.c_uint32),
        ("inherited_c_passthrough_invoked", ctypes.c_uint32),
        ("canonical_admission", ctypes.c_uint32),
    ]


def _source_git_blob(root: Path, path: str) -> str:
    result = subprocess.run(
        ["git", "hash-object", "--", path], cwd=root,
        check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def source_bound_candidate(
    native_library: str, x_real: int, x_imag: int, *,
    typed_m_register: bytes, raw5184_carrier: bytes,
    phase72: bytes, root: Path = Path("."),
) -> dict:
    """Fail closed before direct native HNAN execution or status promotion."""
    root = root.resolve()
    if (_source_git_blob(root, DOC) != DOC_GIT_BLOB
        or _source_git_blob(
            root, "hhs_runtime/hhs_pass220_course_m195_spectral_tensor_witness_v1.py"
        ) != SOURCE_GIT_BLOB):
        raise ProofCorpusError("M195_CANDIDATE_SOURCE_BLOB_DRIFT")
    if SOURCE not in (root / DOC).read_text("utf-8"):
        raise ProofCorpusError("M195_ORIGINAL_ORDERED_SOURCE_NOT_IN_COURSE_NOTE")
    spectral = evaluate()
    if spectral["source_sha256"] != sha256(SOURCE.encode("utf-8")).hexdigest():
        raise ProofCorpusError("M195_SOURCE_FINGERPRINT_DRIFT")
    if (type(x_real) is not int or type(x_imag) is not int
        or type(typed_m_register) is not bytes
        or not typed_m_register or type(raw5184_carrier) is not bytes
        or len(raw5184_carrier) != RAW5184
        or type(phase72) is not bytes or len(phase72) != PHASE_WIDTH):
        raise ProofCorpusError("M195_TYPED_5184_CANDIDATE_INPUT_REQUIRED")
    if not native_library or not Path(native_library).is_file():
        raise ProofCorpusError("M195_NATIVE_LIBRARY_REQUIRED")
    lib = ctypes.CDLL(native_library)
    fn = lib.hhs220_m195_gaussian_hnan_candidate
    fn.argtypes = [
        ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p,
        ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t,
        ctypes.c_void_p, ctypes.c_void_p,
        ctypes.POINTER(Witness), ctypes.POINTER(GaussianDecision),
    ]
    fn.restype = ctypes.c_int
    # Integers must fit ABI and the native exact proof-safe range.
    if abs(x_real) > 100000 or abs(x_imag) > 100000:
        raise ProofCorpusError("M195_GAUSSIAN_INPUT_OUT_OF_PROOF_RANGE")
    carrier = ctypes.create_string_buffer(raw5184_carrier, RAW5184)
    phase = ctypes.create_string_buffer(phase72, PHASE_WIDTH)
    carrier_out = ctypes.create_string_buffer(RAW5184)
    phase_out = ctypes.create_string_buffer(PHASE_WIDTH)
    receipt = Witness()
    decision = GaussianDecision()
    status = fn(
        x_real, x_imag, carrier, RAW5184, phase, PHASE_WIDTH,
        carrier_out, phase_out, ctypes.byref(receipt), ctypes.byref(decision),
    )
    # Valid nonzero D is NOT a HNAN bypass; reject without promotion.
    if not decision.exact_guard_evaluated or not decision.denominator_zero:
        if status != 0 or decision.inherited_c_passthrough_invoked:
            raise ProofCorpusError("M195_NONZERO_DENOMINATOR_BYPASS_FORBIDDEN")
        raise ProofCorpusError("M195_DENOMINATOR_NONZERO_NON_HNAN_ROUTE_REQUIRED")
    if (status != 1 or not decision.inherited_c_passthrough_invoked
        or receipt.decision != 1 or receipt.bypass_applied != 1
        or (receipt.gain_numerator, receipt.gain_denominator) != (1, 1)
        or receipt.phase_writes != 0 or receipt.canonical_admission != 0
        or carrier_out.raw != raw5184_carrier or phase_out.raw != phase72):
        raise ProofCorpusError("M195_NATIVE_5184_PASSTHROUGH_REJECTED")
    return {
        "schema": SCHEMA, "module": 195,
        "original_ordered_source_sha256": spectral["source_sha256"],
        "document_blob_sha": DOC_GIT_BLOB,
        "spectral_witness_blob_sha": SOURCE_GIT_BLOB,
        "typed_m_register_sha256": sha256(typed_m_register).hexdigest(),
        "m_register_semantic_proof": "OUTSTANDING",
        "raw5184_carrier_sha256": sha256(raw5184_carrier).hexdigest(),
        "phase72_sha256": sha256(phase72).hexdigest(),
        "x_exact_gaussian": [x_real, x_imag],
        "native_exact_denominator": [
            decision.denominator_real, decision.denominator_imag
        ],
        "native_source_derived_zero_guard": True,
        "inherited_c11_passthrough_executed": True,
        "raw5184_bytes_preserved": True, "phase72_bytes_preserved": True,
        "native_gain": "1/1", "native_phase_writes": 0,
        "source_bound_candidate_only": True,
        "legacy_frozen_course_graph_admitted": False,
        "pass219_i157_typed_equivalence_proved": False,
        "lane5_bios_producer_verified": False,
        "typed_m_equality_admitted": False,
        "vm81_admission": False,
        "hash72_minted": False, "hash216_minted": False,
    }
