"""Pass 219 I11 bridge from native five-lane addresses to Pass 133/211.

I11 does not define a new integer serialization. Native C++ emits the canonical
minimal unsigned big-endian source BigInt bytes inherited from Pass 133. This
module validates the complete I11 mixed-radix namespace before proving that
exact source through the existing Pass 133 palindromic SECDED carrier and Pass
211 HFC multi-register framing runtime.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass211_bigint_hfc_carrier_v1 import (
    Pass211BigIntHFCRuntime,
    Pass211Package,
    Pass211ValidationError,
)
from hhs_runtime.canonical import CanonicalEncodingError, bigint_to_bytes

SCHEMA = "HHS_PASS219_I11_FIVE_LANE_BIGINT_ADDRESS_V1"
MAX_SOURCE_BYTES = 384
I11_NAMESPACE = 0x21911
CELL_RADIX = 81
HASH216_RADIX = 216
HOLO4_LANE_COUNT = 4
PRIME_FIBRES = (
    5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
    67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131,
    137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197,
    199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271,
    277, 281, 283, 293, 307, 311, 313, 317, 331,
)


class Pass219I11AddressError(ValueError):
    """Fail-closed I11 address/serialization boundary."""


@dataclass(frozen=True)
class Pass219I11FramedAddress:
    source_hex: str
    source_byte_length: int
    source_bit_length: int
    pass211_shard_count: int
    pass211_carrier_byte_length: int
    pass211_package_root216: str
    pass211_package_receipt_hash72: str
    package: Pass211Package

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "source_hex": self.source_hex,
            "source_byte_length": self.source_byte_length,
            "source_bit_length": self.source_bit_length,
            "pass211_shard_count": self.pass211_shard_count,
            "pass211_carrier_byte_length": self.pass211_carrier_byte_length,
            "pass211_package_root216": self.pass211_package_root216,
            "pass211_package_receipt_hash72": self.pass211_package_receipt_hash72,
            "package": self.package.to_dict(),
        }


def _consume_u64_be(source: int) -> tuple[int, int]:
    value = 0
    octets = [0] * 8
    for index in range(7, -1, -1):
        source, octets[index] = divmod(source, 256)
    for octet in octets:
        value = (value << 8) | octet
    return source, value


def _validate_i11_mixed_radix(source: int) -> None:
    """Consume every I11 digit and require the exact namespace residue."""
    value = source

    for prime in reversed(PRIME_FIBRES):
        value, closure = divmod(value, 2)
        if closure not in (0, 1):
            raise Pass219I11AddressError("PASS219_I11_ADDRESS_INVALID_CLOSURE")
        # Reverse of cell residue, u, v, rho, magic-sum residue, closure.
        for _ in range(5):
            value, digit = divmod(value, prime)
            if digit < 0 or digit >= prime:
                raise Pass219I11AddressError("PASS219_I11_ADDRESS_INVALID_PRIME_DIGIT")

    for _ in range(HOLO4_LANE_COUNT):
        value, position = divmod(value, HASH216_RADIX)
        if position < 0 or position >= HASH216_RADIX:
            raise Pass219I11AddressError("PASS219_I11_ADDRESS_INVALID_HASH216_POSITION")

    value, cell81 = divmod(value, CELL_RADIX)
    if cell81 < 0 or cell81 >= CELL_RADIX:
        raise Pass219I11AddressError("PASS219_I11_ADDRESS_INVALID_CELL")

    # local_signature64, fingerprint_signature64, tensor_signature64 were
    # appended in that order after the namespace and therefore unwind in the
    # reverse order here. Their values are witnesses, not new authority.
    value, _local_signature64 = _consume_u64_be(value)
    value, _fingerprint_signature64 = _consume_u64_be(value)
    value, _tensor_signature64 = _consume_u64_be(value)

    if value != I11_NAMESPACE:
        raise Pass219I11AddressError("PASS219_I11_ADDRESS_NAMESPACE_MISMATCH")


def _canonical_native_bytes(address_bytes_be: bytes | bytearray | memoryview) -> bytes:
    raw = bytes(address_bytes_be)
    if not raw:
        raise Pass219I11AddressError("PASS219_I11_ADDRESS_EMPTY")
    if len(raw) > MAX_SOURCE_BYTES:
        raise Pass219I11AddressError("PASS219_I11_ADDRESS_SOURCE_BOUND_EXCEEDED")
    if raw[0] == 0:
        raise Pass219I11AddressError("PASS219_I11_ADDRESS_NONCANONICAL_LEADING_ZERO")
    source = int.from_bytes(raw, "big", signed=False)
    if source <= 0:
        raise Pass219I11AddressError("PASS219_I11_ADDRESS_MUST_BE_POSITIVE")
    try:
        canonical = bigint_to_bytes(source)
    except CanonicalEncodingError as exc:
        raise Pass219I11AddressError("PASS219_I11_PASS133_CANONICAL_REJECTED") from exc
    if canonical != raw:
        raise Pass219I11AddressError("PASS219_I11_PASS133_BYTE_VARIANCE")
    _validate_i11_mixed_radix(source)
    return raw


def frame_native_address(
    address_bytes_be: bytes | bytearray | memoryview,
) -> Pass219I11FramedAddress:
    """Round-trip one structurally valid native I11 source through Pass 133/211."""
    raw = _canonical_native_bytes(address_bytes_be)
    source = int.from_bytes(raw, "big", signed=False)
    runtime = Pass211BigIntHFCRuntime()
    try:
        package = runtime.encode(source)
        decoded = runtime.decode(package)
    except Pass211ValidationError as exc:
        raise Pass219I11AddressError(f"PASS219_I11_PASS211_REJECTED:{exc}") from exc
    if str(decoded.get("ciphertext_hex")) != hex(source):
        raise Pass219I11AddressError("PASS219_I11_PASS211_SOURCE_VARIANCE")
    recovered = bigint_to_bytes(int(str(decoded["ciphertext_hex"]), 16))
    if recovered != raw:
        raise Pass219I11AddressError("PASS219_I11_PASS211_BYTE_VARIANCE")
    _canonical_native_bytes(recovered)
    return Pass219I11FramedAddress(
        source_hex=hex(source),
        source_byte_length=len(raw),
        source_bit_length=source.bit_length(),
        pass211_shard_count=package.shard_count,
        pass211_carrier_byte_length=package.carrier_byte_length,
        pass211_package_root216=package.package_root216,
        pass211_package_receipt_hash72=package.package_receipt_hash72,
        package=package,
    )


def decode_framed_address(package: Pass211Package | Mapping[str, Any]) -> bytes:
    """Recover and revalidate the exact I11 source bytes from a Pass 211 package."""
    runtime = Pass211BigIntHFCRuntime()
    try:
        decoded = runtime.decode(package)
    except Pass211ValidationError as exc:
        raise Pass219I11AddressError(f"PASS219_I11_PASS211_REJECTED:{exc}") from exc
    try:
        source = int(str(decoded["ciphertext_hex"]), 16)
        raw = bigint_to_bytes(source)
    except (KeyError, TypeError, ValueError, CanonicalEncodingError) as exc:
        raise Pass219I11AddressError("PASS219_I11_PASS133_RECOVERY_REJECTED") from exc
    return _canonical_native_bytes(raw)
