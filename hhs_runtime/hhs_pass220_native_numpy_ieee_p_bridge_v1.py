"""Inherited NumPy1 IEEE binary64 bit-pattern bridge into P indexed Lo Shu carrier.

Bits are a type-tagged P index, not a claim that IEEE numerical values equal
their unsigned integer encodings. Exact roundtrip requires raw bits and finite
NumPy1 dyadic admission. No canonical VM81 or Hash216 mutation.
"""
from __future__ import annotations
from hashlib import sha256
from hhs_runtime.hhs_pass220_cross_modal_p_bridge_search_v1 import (
    Node, BridgeSearchError, find_bridge,
)
from hhs_runtime.hhs_pass220_executed_p_bridge_roundtrip_v1 import (
    _encode_p, _decode_p,
)
from hhs_runtime.hhs_pass220_numpy_harmonicode_array_v1 import (
    HHSNumPyScalar, HHSNumPyCompatibilityError,
)

SCHEMA = "HHS_PASS220_NATIVE_NUMPY_IEEE_P_BRIDGE_V1"
IEEE = "IEEE_BINARY64_BITS"
BIGINT = "BIGINT"
LO_SHU = "LO_SHU_SERIALIZED"


def verify_ieee_p_bridge(bits: int) -> dict:
    if isinstance(bits, bool) or not isinstance(bits, int) or not 0 <= bits < 1 << 64:
        raise BridgeSearchError("IEEE_BINARY64_EXACT_BITS_REQUIRED")
    try:
        scalar = HHSNumPyScalar.from_float64_bits(bits)
    except HHSNumPyCompatibilityError as exc:
        raise BridgeSearchError("IEEE_NUMPY1_BOUNDARY_NOT_ADMITTED") from exc
    carrier = _encode_p(bits)
    if carrier != scalar.bigint_5184 or _decode_p(carrier) != bits:
        raise BridgeSearchError("IEEE_NUMPY1_CARRIER_ROUNDTRIP_DIVERGED")
    nodes = (Node(bits, IEEE), Node(bits, BIGINT), Node(bits, LO_SHU))
    candidate = find_bridge(
        nodes[0], nodes[-1], nodes,
        declared_same_p_bridges=((IEEE, BIGINT), (BIGINT, LO_SHU)),
        max_hops=2,
    )
    if not candidate["found"] or candidate["hops"] != 2:
        raise BridgeSearchError("IEEE_NUMPY1_BRIDGE_ROUTE_MISSING")
    return {
        "schema": SCHEMA,
        "P_decimal": str(bits),
        "raw_ieee_binary64_hex": f"{bits:016x}",
        "exact_dyadic_numerator": str(scalar.exact_value.numerator),
        "exact_dyadic_denominator": str(scalar.exact_value.denominator),
        "native_numpy1_scalar_dtype": scalar.dtype,
        "serialized_5184_sha256": sha256(carrier.encode("ascii")).hexdigest(),
        "path": candidate["path"],
        "edge_kinds": candidate["edge_kinds"],
        "raw_bits_roundtrip_verified": True,
        "type_codec_executed": True,
        "float_numeric_value_is_bit_integer": False,
        "native_admission": False,
        "hash72_minted": False,
        "hash216_persisted": False,
    }
