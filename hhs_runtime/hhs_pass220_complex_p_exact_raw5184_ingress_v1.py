"""Exact Gaussian-rational complex-P -> retained VM81 raw carrier.

This is a reversible ingress carrier, not an executable native complex
transition. The inherited I148/HNAN/I074 candidate verifies the actual bytes.
"""
from __future__ import annotations
from fractions import Fraction
import json

WIDTH = 5184
BYTES = WIDTH // 8
PREFIX = b"HHS-P220-CP1\x00"


class ComplexPIngressError(ValueError):
    pass


def _fraction(value):
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise ComplexPIngressError("EXACT_RATIONAL_REQUIRED")
    return Fraction(value)


def _pair(value):
    if not isinstance(value, (tuple, list)) or len(value) != 2:
        raise ComplexPIngressError("EXACT_COMPLEX_PAIR_REQUIRED")
    return tuple(_fraction(x) for x in value)


def encode_complex_p_raw5184(base, scale):
    real, imag = _pair(base)
    n = _fraction(scale)
    if (real, imag) == (0, 0) or n == 0:
        raise ComplexPIngressError("NONZERO_P_AND_SCALE_REQUIRED")
    payload = json.dumps({
        "P_base": [[real.numerator, real.denominator],
                   [imag.numerator, imag.denominator]],
        "n": [n.numerator, n.denominator],
        "type": "EXACT_GAUSSIAN_RATIONAL_P",
    }, sort_keys=True, separators=(",", ":")).encode("ascii")
    if len(payload) > BYTES - len(PREFIX) - 2:
        raise ComplexPIngressError("RAW5184_PAYLOAD_TOO_LARGE")
    frame = PREFIX + len(payload).to_bytes(2, "big") + payload
    return "".join(f"{byte:08b}" for byte in frame.ljust(BYTES, b"\x00"))


def decode_complex_p_raw5184(bits):
    if not isinstance(bits, str) or len(bits) != WIDTH or any(c not in "01" for c in bits):
        raise ComplexPIngressError("RAW5184_FRAME_INVALID")
    frame = bytes(int(bits[i:i+8], 2) for i in range(0, WIDTH, 8))
    if not frame.startswith(PREFIX):
        raise ComplexPIngressError("COMPLEX_P_FRAME_MAGIC")
    count = int.from_bytes(frame[len(PREFIX):len(PREFIX)+2], "big")
    start = len(PREFIX)+2
    if count <= 0 or start + count > BYTES or any(frame[start+count:]):
        raise ComplexPIngressError("COMPLEX_P_FRAME_LENGTH_OR_PADDING")
    try:
        record = json.loads(frame[start:start+count].decode("ascii"))
        if set(record) != {"P_base", "n", "type"} or record["type"] != "EXACT_GAUSSIAN_RATIONAL_P":
            raise ValueError("type")
        base = tuple(Fraction(x[0], x[1]) for x in record["P_base"])
        n = Fraction(*record["n"])
        if len(base) != 2 or base == (0, 0) or n == 0:
            raise ValueError("nonzero")
    except (ValueError, TypeError, IndexError, KeyError, ZeroDivisionError) as exc:
        raise ComplexPIngressError("COMPLEX_P_FRAME_DECODE") from exc
    if encode_complex_p_raw5184(base, n) != bits:
        raise ComplexPIngressError("NONCANONICAL_COMPLEX_P_FRAME")
    return {"P_base": base, "n": n,
            "P_scaled": (base[0]*n, base[1]*n),
            "candidate_only": True,
            "native_transition_authority": False}
