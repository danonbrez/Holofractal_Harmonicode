"""Domain-separated canonical Hash72(D || S) construction.

Hash72 is a 72-symbol receipt/state identity over the repository's canonical
72-symbol alphabet. SHAKE-256 supplies an extendable cryptographic stream.
Rejection sampling removes modulo bias before mapping bytes to the alphabet.
"""
from __future__ import annotations

from hashlib import shake_256
import hmac
import json
from typing import Any

from .hash72_validator_v1 import (
    HASH72_ALPHABET,
    HASH72_SYMBOL_COUNT,
    validate_hash72,
)

DOMAIN = b"HHS-HASH72-DIGEST-V1\0"
MAX_ACCEPTED_BYTE = (256 // len(HASH72_ALPHABET)) * len(HASH72_ALPHABET)


def canonical_bytes(value: Any) -> bytes:
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, memoryview):
        return value.tobytes()
    if isinstance(value, str):
        return value.encode("utf-8")
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _frame(value: Any) -> bytes:
    raw = canonical_bytes(value)
    return len(raw).to_bytes(8, "big") + raw


def hash72_digest(dictionary: Any, snapshot: Any) -> str:
    """Return the canonical 72-symbol digest for framed ``D || S``."""
    seed = DOMAIN + _frame(dictionary) + _frame(snapshot)
    symbols: list[str] = []
    block = 0
    while len(symbols) < HASH72_SYMBOL_COUNT:
        stream = shake_256(seed + block.to_bytes(8, "big")).digest(128)
        block += 1
        for value in stream:
            if value >= MAX_ACCEPTED_BYTE:
                continue
            symbols.append(HASH72_ALPHABET[value % len(HASH72_ALPHABET)])
            if len(symbols) == HASH72_SYMBOL_COUNT:
                break
    digest = "".join(symbols)
    if not validate_hash72(digest):
        raise RuntimeError("HASH72_INTERNAL_FORMAT_FAILURE")
    return digest


def verify_hash72(receipt: str, dictionary: Any, snapshot: Any) -> bool:
    return validate_hash72(receipt) and hmac.compare_digest(
        receipt,
        hash72_digest(dictionary, snapshot),
    )


def projection_receipt_hash72(projection_root_hash216: str) -> str:
    """Canonical Hash72 receipt for a Pass 158/163 Hash216 projection root."""
    if (
        not isinstance(projection_root_hash216, str)
        or len(projection_root_hash216) != 64
        or any(ch not in "0123456789abcdef" for ch in projection_root_hash216)
    ):
        raise ValueError("HASH216_PROJECTION_ROOT_INVALID")
    dictionary = {"domain": "HHS-P158-P163-PROJECTION-RECEIPT-V1"}
    return hash72_digest(dictionary, bytes.fromhex(projection_root_hash216))


def verify_projection_receipt_hash72(
    receipt: str,
    projection_root_hash216: str,
) -> bool:
    try:
        expected = projection_receipt_hash72(projection_root_hash216)
    except ValueError:
        return False
    return validate_hash72(receipt) and hmac.compare_digest(receipt, expected)
