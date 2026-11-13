"""Module 195 adapter to the inherited, independent native HNAN passthrough witness.

This bridge executes the existing Module 9 native zero-divisor checker ONLY.
It does not verify Module 195 typed m equality or assert VM81 admission.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path

from hhs_runtime.hhs_pass220_course_m195_spectral_tensor_witness_v1 import evaluate
from hhs_runtime.hhs_pass220_course_hnan_passthrough_graph_binding_v1 import (
    bind_executed_course_passthrough,
)
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError

SCHEMA = "HHS_PASS220_COURSE_M195_INHERITED_HNAN_BRIDGE_V1"
SINGULAR_ROOTS = ("0", "-3+4I", "-3-4I")


def bind_m195_hnan_boundary(native_library: str, carrier: bytes, phase: bytes,
                            root: Path = Path(".")) -> dict:
    """Request real inherited C native witness; fail closed if unavailable.

    Returning a scoped success means only the zero-divisor passthrough ran.
    The separate original typed equality remains an outstanding obligation.
    """
    spectral = evaluate()
    if (spectral["spectral_roots"] != ["0", "-3+4I", "-3-4I"]
        or spectral["canonical_vm81_admission"] is not False
        or spectral["ordered_typed_equality"] !=
            "OUTSTANDING_NATIVE_PROOF_OBLIGATION"):
        raise ProofCorpusError("COURSE_M195_SPECTRAL_SOURCE_OR_STATUS_DRIFT")
    if not isinstance(carrier, bytes) or not isinstance(phase, bytes):
        raise ProofCorpusError("COURSE_M195_NATIVE_BYTE_CARRIER_REQUIRED")
    # Never fabricate a native result or treat a file name as executed proof.
    native = bind_executed_course_passthrough(
        native_library, carrier, phase, root=root)
    if (native.get("native_execution_witness_verified") is not True
        or native.get("canonical_vm81_admission") is not False
        or native.get("hash216_minted") is not False
        or native.get("witness_scope") !=
            "ZERO_DIVISOR_BYTE_IDENTICAL_CARRIER_AND_PHASE_GAIN_ONE"):
        raise ProofCorpusError("COURSE_M195_NATIVE_HNAN_SCOPE_REJECTED")
    return {
        "schema": SCHEMA, "module": 195,
        "spectral_candidate_sha256": spectral["candidate_sha256"],
        "original_source_sha256": spectral["source_sha256"],
        "singular_denominator_roots": list(SINGULAR_ROOTS),
        "native_passthrough_parent_schema": native["schema"],
        "native_passthrough_parent_candidate_sha256":
            native["candidate_receipt_sha256"],
        "carrier_sha256": sha256(carrier).hexdigest(),
        "phase_sha256": sha256(phase).hexdigest(),
        "native_zero_divisor_passthrough_executed": True,
        "gain": "1/1", "phase_writes": 0,
        "original_typed_equality_admitted": False,
        "lane5_5184_hydration_verified": False,
        "canonical_vm81_admission": False,
        "hash72_minted": False, "hash216_minted": False,
    }
