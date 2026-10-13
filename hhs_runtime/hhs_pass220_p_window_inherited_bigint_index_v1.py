"""Pass 220 P-only consecutive BigInt metadata index into inherited 72^72 lattice.

This read-only locator does not claim to be the entire Lane 5 knowledge graph:
it binds the exact P-1,P,P+1 addresses to the EXISTING 72-glyph CRT serialization.
Out-of-range fixed-depth addresses require an existing higher-depth hydration
path, not silent modulo wrapping or loss of BigInt provenance.
"""
from __future__ import annotations
from hashlib import sha256
import json

from hhs_runtime.pass219.nonary_qudit_bigint_assembly_probe import (
    HASH72_DEPTH, GLYPH_RADIX, HASH72_MANIFOLD_CARDINALITY,
    encode_radix_digits, decode_radix_digits,
)

SCHEMA = "HHS_PASS220_P_WINDOW_INHERITED_BIGINT_INDEX_V1"
WINDOW_ROLES = ("p", "P", "q")


class PWindowIndexError(ValueError):
    pass


def lookup_window(P: int) -> dict:
    if isinstance(P, bool) or not isinstance(P, int):
        raise PWindowIndexError("P_EXACT_BIGINT_REQUIRED")
    addresses = (P-1, P, P+1)
    if not all(0 <= index < HASH72_MANIFOLD_CARDINALITY for index in addresses):
        raise PWindowIndexError("FIXED_DEPTH_OUT_OF_RANGE_DEFER_TO_HYDRATION")
    entries = []
    for role, value in zip(WINDOW_ROLES, addresses):
        digits = decode_radix_digits(value, GLYPH_RADIX, HASH72_DEPTH)
        if encode_radix_digits(digits, GLYPH_RADIX) != value:
            raise PWindowIndexError("INHERITED_RADIX_ROUNDTRIP_FAILED")
        entries.append({
            "role": role,
            "bigint_decimal": str(value),
            "rational_num_decimal": str(value),
            "rational_den_decimal": "1",
            "glyph72": digits,
            "glyph_depth": HASH72_DEPTH,
            "source": "PASS219_INHERITED_NONARY_QUDIT_BIGINT_ASSEMBLY",
        })
    record = {
        "schema": SCHEMA,
        "sole_free_parameter": "P",
        "P_bigint_decimal": str(P),
        "delta_unit": 1,
        "ordered_window": entries,
        "differences": {"P_minus_p": 1, "q_minus_P": 1, "q_minus_p": 2},
        "carrier_positions": 81*64,
        "alternate_lattice_positions": 72*72,
        "lookup_only": True,
        "lean4_native_proof_verified": False,
        "global_hnan_closure_verified": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    record["witness_sha256"] = sha256(json.dumps(
        record, sort_keys=True, separators=(",", ":"),
    ).encode("ascii")).hexdigest()
    return record
