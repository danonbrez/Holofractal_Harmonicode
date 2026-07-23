"""Canonical Pass 133 BigInt envelope."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import json

from .canonical import (
    CanonicalEncodingError,
    bigint_to_bytes,
    bytes_to_bigint,
    canonical_bytes,
    decode_tlv,
    encode_tlv,
    int_to_min_bytes,
    min_bytes_to_int,
    pack_int_sequence,
    unpack_int_sequence,
)

MAGIC = b"HHS-P133-BK\x01"

TAG_VERSION = 1
TAG_MODE = 2
TAG_PRIME_BITS = 3
TAG_ALPHABET_OR_SEED = 4
TAG_TOPOLOGY = 5
TAG_NONCE = 6
TAG_ORDER = 7
TAG_NORMALIZATION = 8
TAG_RECONSTRUCTION = 9
TAG_PARENT_ROOT = 10
TAG_COUNTERS = 11
TAG_CONTEXT = 12


@dataclass(frozen=True)
class BigIntEnvelope:
    version: str
    mode: str
    prime_bits: int
    alphabet_or_seed: bytes
    topology: int
    nonce: bytes
    order: list[int]
    normalization: dict[str, Any]
    reconstruction: dict[str, Any]
    parent_root: str
    counters: list[int]
    context: dict[str, Any]

    def encode_bytes(self) -> bytes:
        fields = [
            (TAG_VERSION, self.version.encode()),
            (TAG_MODE, self.mode.encode()),
            (TAG_PRIME_BITS, int_to_min_bytes(self.prime_bits)),
            (TAG_ALPHABET_OR_SEED, self.alphabet_or_seed),
            (TAG_TOPOLOGY, int_to_min_bytes(self.topology)),
            (TAG_NONCE, self.nonce),
            (TAG_ORDER, bytes(self.order)),
            (TAG_NORMALIZATION, canonical_bytes(self.normalization)),
            (TAG_RECONSTRUCTION, canonical_bytes(self.reconstruction)),
            (TAG_PARENT_ROOT, self.parent_root.encode()),
            (TAG_COUNTERS, pack_int_sequence(self.counters)),
            (TAG_CONTEXT, canonical_bytes(self.context)),
        ]
        return encode_tlv(fields, magic=MAGIC)

    def to_bigint(self) -> int:
        return bytes_to_bigint(self.encode_bytes())

    @classmethod
    def decode_bytes(cls, raw: bytes) -> "BigIntEnvelope":
        f = decode_tlv(raw, magic=MAGIC)
        required = set(range(1,13))
        if set(f) != required:
            raise CanonicalEncodingError(f"BigInt envelope tags mismatch: {sorted(f)}")
        order = list(f[TAG_ORDER])
        if len(order) != 81 or sorted(order) != list(range(81)):
            raise CanonicalEncodingError("invalid VM81 order")
        return cls(
            version=f[TAG_VERSION].decode(),
            mode=f[TAG_MODE].decode(),
            prime_bits=min_bytes_to_int(f[TAG_PRIME_BITS]),
            alphabet_or_seed=f[TAG_ALPHABET_OR_SEED],
            topology=min_bytes_to_int(f[TAG_TOPOLOGY]),
            nonce=f[TAG_NONCE],
            order=order,
            normalization=json.loads(f[TAG_NORMALIZATION].decode()),
            reconstruction=json.loads(f[TAG_RECONSTRUCTION].decode()),
            parent_root=f[TAG_PARENT_ROOT].decode(),
            counters=unpack_int_sequence(f[TAG_COUNTERS]),
            context=json.loads(f[TAG_CONTEXT].decode()),
        )

    @classmethod
    def from_bigint(cls, value: int) -> "BigIntEnvelope":
        return cls.decode_bytes(bigint_to_bytes(value))


def encode_explicit_primes(primes: list[int]) -> bytes:
    return pack_int_sequence(primes)


def decode_explicit_primes(raw: bytes) -> list[int]:
    return unpack_int_sequence(raw)
