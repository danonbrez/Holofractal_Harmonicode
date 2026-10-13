"""Pass 220 exact phase72 antipodal transport with ordered HNAN channels.

Phase identities are proved in the inherited cyclotomic exponent algebra.
The terminal quotient equality remains a typed native closure obligation;
no cancellation or commutation of xy/yx or AB/BA is licensed here.
"""
from __future__ import annotations
from hashlib import sha256
import json

from hhs_runtime.hhs_pass220_schrodinger_firing_order_v1 import Phase72

SCHEMA = "HHS_PASS220_ORDERED_ANTIPODAL_PHASE72_V1"
SOURCE_TERMINAL = "u^(-36)/yx==u^72/xy"
SOURCE_ORIENTATION = "AB/-P^4==P^4/-BA"
SOURCE_SEED = "179971.179971"
SECTOR_COUNT = 6
SECTOR_WIDTH = 12


def phase72_transport_witness() -> dict:
    origin = Phase72(0)
    half = Phase72(-36)
    full = Phase72(72)
    assert half * half == origin
    assert full == origin
    sectors = tuple(tuple(range(k, 72, SECTOR_COUNT)) for k in range(SECTOR_COUNT))
    assert all(len(s) == SECTOR_WIDTH for s in sectors)
    assert sorted(k for sector in sectors for k in sector) == list(range(72))
    record = {
        "schema": SCHEMA,
        "session_seed": SOURCE_SEED,
        "phase_modulus": 72,
        "half_period": 36,
        "full_period": 72,
        "phase_half_exponent": half.exponent,
        "phase_full_exponent": full.exponent,
        "phase_half_square_is_identity": half * half == origin,
        "phase_full_is_identity": full == origin,
        "sectors_mod6": sectors,
        "ordered_terminal_source": SOURCE_TERMINAL,
        "ordered_orientation_source": SOURCE_ORIENTATION,
        "ordered_channel_pairs": (("xy", "yx"), ("AB", "BA")),
        "denominator_constraint": "Delta=1",
        "native_terminal_closure_proven": False,
        "e6_octonion_map_proven": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "candidate_only": True,
    }
    record["candidate_receipt_sha256"] = sha256(
        json.dumps(record, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    return record
