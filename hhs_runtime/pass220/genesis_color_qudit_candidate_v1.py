"""Read-only phase-color candidate adapter over existing G41/operation64 services.
No HNAN closure claim, VM81 mutation, or canonical Hash72/Hash216 receipt.
"""
from __future__ import annotations
import colorsys
import math
from hashlib import sha256
import json

from hhs_runtime.hhs_pass220_g41_sudoku_fingerprint_algebra_v1 import (
    SUDOKU81, fingerprint, fingerprint_class_id,
    encode_anchor_reachability, local_bigint_projection,
)
from hhs_runtime.hhs_pass220_rna_hash72_dna_qudit_phase_lock_v1 import (
    operation64_rna_triplet,
)

GENESIS = "GENESIS_ZERO_SUM_CERTIFIED"
INVERSION = "HNAN_GLOBAL_INVERSION_ZERO_MAGNITUDE"
LOCAL = "LOCAL_PHASE_CANDIDATE"


def phase_color_candidate(*, cell: int, operation64: int, phase72: int,
                          residue: float, probability: float,
                          classification: str = LOCAL) -> dict:
    """Compose inherited addresses into a nonauthoritative visual candidate.

    Genesis/black classification is caller-supplied; it is NOT a closure proof.
    """
    for name, value, maximum in (
        ("cell", cell, 80),
        ("operation64", operation64, 63),
        ("phase72", phase72, 71),
    ):
        if type(value) is not int or not 0 <= value <= maximum:
            raise ValueError(f"{name} must be an exact integer in 0..{maximum}")
    for name, value in (("residue", residue), ("probability", probability)):
        if type(value) is not float or not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError(f"{name} must be a finite IEEE float in [0,1]")
    if classification not in (LOCAL, GENESIS, INVERSION):
        raise ValueError("unknown candidate classification")
    row, col = divmod(cell, 9)
    local = fingerprint(row, col)
    if classification == GENESIS:
        rgb = (255, 255, 255)
        alpha = 1.0
    elif classification == INVERSION:
        rgb = (0, 0, 0)
        alpha = 1.0
    else:
        rgb = tuple(round(255 * c) for c in colorsys.hsv_to_rgb(
            phase72 / 72, residue, 1.0))
        alpha = probability
    result = {
        "schema": "HHS_PASS220_GENESIS_COLOR_QUDIT_CANDIDATE_V1",
        "linear5184": 64 * cell + operation64,
        "cell": cell,
        "operation64": operation64,
        "phase72": phase72,
        "symbol": SUDOKU81[row][col],
        "fingerprint9": local,
        "g41_class": fingerprint_class_id(row, col),
        "g41_address": encode_anchor_reachability(row, col),
        "local_bigint": str(local_bigint_projection(local)),
        "rna_operation64": operation64_rna_triplet(operation64),
        "ieee_residue_hex": residue.hex(),
        "ieee_probability_hex": probability.hex(),
        "classification": classification,
        "rgb8": rgb,
        "alpha": alpha,
        "classification_verified": False,
        "hnan_gate_verified": False,
        "vm81_admitted": False,
        "canonical_receipt": False,
    }
    result["candidate_sha256"] = sha256(json.dumps(
        result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result
