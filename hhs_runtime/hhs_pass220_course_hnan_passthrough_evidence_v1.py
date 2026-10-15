"""Separate the course HNAN passthrough theorem from inherited native gate proof.

This is a source-bound theorem obligation and exact phase-preservation
interface contract, not a replacement HNAN implementation or a proof mint.
"""
from __future__ import annotations
from hashlib import sha256
from hhs_runtime.hhs_pass220_course_module_gate_provenance_v1 import (
    course_module_gate_inventory, HNAN_PASSTHROUGH_THEOREM,
    HNAN_RUNTIME_PHASE_GATE,
)
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError

PASSTHROUGH_SENTENCE="The HNAN bypass — divisor vanishes → gain exactly 1, no phase write"
PASSTHROUGH_CONDITIONS=("divisor vanishes","gain exactly 1","no phase write")
PHASE_GATE_INHERITED="hhs_exact_pass219_hnan_global_system_verify"

def course_hnan_proof_obligations()->dict:
    inventory=course_module_gate_inventory()
    section=inventory["ordered_modules"][9]
    if PASSTHROUGH_SENTENCE not in section["source_section"]:
        raise ProofCorpusError("COURSE_HNAN_PASSTHROUGH_THEOREM_DRIFT")
    return {
        "course_sha256":inventory["source_sha256"],
        "course_module_index":9,
        "course_module_sha256":section["byte_sha256"],
        "course_passthrough_theorem_id":HNAN_PASSTHROUGH_THEOREM,
        "course_theorem_excerpt_sha256":sha256(PASSTHROUGH_SENTENCE.encode("utf-8")).hexdigest(),
        "course_passthrough_obligations":list(PASSTHROUGH_CONDITIONS),
        "course_passthrough_executable_proof":"UNBOUND",
        "native_phase_gate_id":HNAN_RUNTIME_PHASE_GATE,
        "inherited_native_checker":PHASE_GATE_INHERITED,
        "native_gate_proof_status":"INHERITED_SEPARATE",
        "passthrough_implied_by_native_phase_gate":False,
        "native_gate_implied_by_passthrough":False,
        "new_native_gate_proof_required":False,
        "canonical_admission":False,
        "hash216_minted":False,
    }

def require_course_passthrough_checker(evidence:dict)->None:
    # No new theorem verification can be created from a declared receipt.
    # A trusted executor must be registered and its native output independently
    # validated before permitting closure. This is deliberately fail-closed.
    raise ProofCorpusError("COURSE_PASSTHROUGH_EXECUTABLE_CHECKER_NOT_BOUND")
