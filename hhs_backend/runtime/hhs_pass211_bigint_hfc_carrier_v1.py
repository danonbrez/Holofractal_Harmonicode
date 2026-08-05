"""Pass 211 exact Pass 133 BigInt carrier over Pass 210 HFC shard frames.

The inherited Pass 133 palindromic SECDED carrier remains the canonical BigInt
serialization layer. Pass 211 splits that exact byte envelope into deterministic
648-byte payload shards, expands each byte into the Pass 210 5184-cell Boolean
register, and binds the ordered shard roots into one package-level Hash72 receipt.
No strict-compression claim is made unless Pass 210 admits the individual register
under its declared affine-Fibonacci domain witness.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass210_holographic_frame_compression_v1 import (
    HFCError,
    HFCFrame,
    HFCProjection,
    HolographicFrameCompressionRuntime,
    REGISTER_LEN,
    SNAPSHOT_COUNT,
)
from hhs_runtime.canonical import CanonicalEncodingError, bigint_to_bytes
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.palindromic_ecc import (
    PalindromicCarrier,
    decode_palindromic_carrier,
    protect_encrypted_bigint,
)

CONTRACT = "HHS-P211-P133-BIGINT-HFC-MULTIREGISTER-H72-H216"
PASS_NUMBER = 211
CONTRACT_VERSION = "1.0.0"
CONTRACT_CLASSIFICATION = "HHS_PASS_211_BIGINT_HFC_CARRIER_CONTRACT_FROZEN"
RUNTIME_CLASSIFICATION = "HHS_PASS_211_BIGINT_HFC_CARRIER_RUNTIME_VERIFIED"
PACKAGE_SCHEMA = "HHS_PASS_211_BIGINT_HFC_PACKAGE_V1"
SHARD_SCHEMA = "HHS_PASS_211_BIGINT_HFC_SHARD_V1"
PACKED_SHARD_BYTES = REGISTER_LEN // 8
PACKED_SHARD_BITS = REGISTER_LEN
ZERO_HASH72 = "0" * 72
MAX_SHARDS = 4096


class Pass211Error(RuntimeError):
    """Base fail-closed Pass 211 error."""


class Pass211ValidationError(Pass211Error):
    pass


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _hash216(domain: str, payload: bytes) -> str:
    domain_bytes = domain.encode("utf-8")
    framed = (
        b"HHS-P211-HASH216-SHA256-V1\0"
        + len(domain_bytes).to_bytes(4, "big")
        + domain_bytes
        + len(payload).to_bytes(8, "big")
        + payload
    )
    return sha256(framed).hexdigest()


def _positive_int(value: Any, name: str) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise Pass211ValidationError(f"PASS211_{name.upper()}_INVALID") from exc
    if result <= 0:
        raise Pass211ValidationError(f"PASS211_{name.upper()}_MUST_BE_POSITIVE")
    return result


def packed_bytes_to_register(payload: bytes | bytearray | memoryview) -> bytes:
    """Expand at most 648 bytes into one MSB-first 5184-cell Boolean register."""
    raw = bytes(payload)
    if len(raw) > PACKED_SHARD_BYTES:
        raise Pass211ValidationError("PASS211_SHARD_PAYLOAD_EXCEEDS_648_BYTES")
    padded = raw + b"\x00" * (PACKED_SHARD_BYTES - len(raw))
    register = bytearray(REGISTER_LEN)
    cursor = 0
    for value in padded:
        for shift in range(7, -1, -1):
            register[cursor] = (value >> shift) & 1
            cursor += 1
    if cursor != REGISTER_LEN:
        raise Pass211ValidationError("PASS211_REGISTER_EXPANSION_CLOSURE_FAILURE")
    return bytes(register)


def register_to_packed_bytes(
    register: bytes | bytearray | memoryview,
    payload_bit_length: int,
) -> bytes:
    """Pack a Boolean register and reject any non-zero bit outside the payload."""
    raw = bytes(register)
    if len(raw) != REGISTER_LEN:
        raise Pass211ValidationError("PASS211_REGISTER_LENGTH_INVALID")
    invalid = next((index for index, value in enumerate(raw) if value not in (0, 1)), None)
    if invalid is not None:
        raise Pass211ValidationError(f"PASS211_REGISTER_NON_BOOLEAN_CELL:{invalid}")
    bit_length = int(payload_bit_length)
    if bit_length <= 0 or bit_length > PACKED_SHARD_BITS:
        raise Pass211ValidationError("PASS211_PAYLOAD_BIT_LENGTH_INVALID")
    if any(raw[index] for index in range(bit_length, REGISTER_LEN)):
        raise Pass211ValidationError("PASS211_NONZERO_REGISTER_PADDING")
    byte_length = (bit_length + 7) // 8
    packed = bytearray(PACKED_SHARD_BYTES)
    for byte_index in range(PACKED_SHARD_BYTES):
        value = 0
        start = byte_index * 8
        for offset in range(8):
            value = (value << 1) | raw[start + offset]
        packed[byte_index] = value
    if bit_length % 8:
        unused = 8 - (bit_length % 8)
        if packed[byte_length - 1] & ((1 << unused) - 1):
            raise Pass211ValidationError("PASS211_NONZERO_FINAL_BYTE_PADDING")
    return bytes(packed[:byte_length])


@dataclass(frozen=True)
class Pass211Shard:
    index: int
    count: int
    payload_hex: str
    payload_byte_length: int
    payload_bit_length: int
    payload_hash216: str
    register_hash216: str
    hash72_identity: str
    hash216_identity: str
    phase_identity: str
    frame_identity: str
    frame_receipt_hash72: str
    snapshot_hash216: tuple[str, ...]
    strict_domain_status: str
    strict_domain_detail: str
    shard_root216: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": SHARD_SCHEMA,
            "index": self.index,
            "count": self.count,
            "payload_hex": self.payload_hex,
            "payload_byte_length": self.payload_byte_length,
            "payload_bit_length": self.payload_bit_length,
            "payload_hash216": self.payload_hash216,
            "register_hash216": self.register_hash216,
            "hash72_identity": self.hash72_identity,
            "hash216_identity": self.hash216_identity,
            "phase_identity": self.phase_identity,
            "frame_identity": self.frame_identity,
            "frame_receipt_hash72": self.frame_receipt_hash72,
            "snapshot_hash216": list(self.snapshot_hash216),
            "strict_domain_status": self.strict_domain_status,
            "strict_domain_detail": self.strict_domain_detail,
            "shard_root216": self.shard_root216,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "Pass211Shard":
        if value.get("schema") != SHARD_SCHEMA:
            raise Pass211ValidationError("PASS211_SHARD_SCHEMA_INVALID")
        try:
            snapshot_hashes = tuple(str(item) for item in value["snapshot_hash216"])
            return cls(
                index=int(value["index"]),
                count=int(value["count"]),
                payload_hex=str(value["payload_hex"]),
                payload_byte_length=int(value["payload_byte_length"]),
                payload_bit_length=int(value["payload_bit_length"]),
                payload_hash216=str(value["payload_hash216"]),
                register_hash216=str(value["register_hash216"]),
                hash72_identity=str(value["hash72_identity"]),
                hash216_identity=str(value["hash216_identity"]),
                phase_identity=str(value["phase_identity"]),
                frame_identity=str(value["frame_identity"]),
                frame_receipt_hash72=str(value["frame_receipt_hash72"]),
                snapshot_hash216=snapshot_hashes,
                strict_domain_status=str(value["strict_domain_status"]),
                strict_domain_detail=str(value["strict_domain_detail"]),
                shard_root216=str(value["shard_root216"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise Pass211ValidationError("PASS211_SHARD_RECORD_INVALID") from exc


@dataclass(frozen=True)
class Pass211Package:
    source_ciphertext_bit_length: int
    source_ciphertext_hash216: str
    pass133_hash72_digest: str
    carrier_byte_length: int
    carrier_serialized_bit_length: int
    carrier_bigint_bit_length: int
    carrier_root216: str
    shard_count: int
    final_shard_bit_length: int
    ordered_shard_roots: tuple[str, ...]
    shards: tuple[Pass211Shard, ...]
    package_root216: str
    package_receipt_hash72: str
    metrics: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": PACKAGE_SCHEMA,
            "contract": CONTRACT,
            "pass": PASS_NUMBER,
            "contract_version": CONTRACT_VERSION,
            "source_ciphertext_bit_length": self.source_ciphertext_bit_length,
            "source_ciphertext_hash216": self.source_ciphertext_hash216,
            "pass133_hash72_digest": self.pass133_hash72_digest,
            "carrier_byte_length": self.carrier_byte_length,
            "carrier_serialized_bit_length": self.carrier_serialized_bit_length,
            "carrier_bigint_bit_length": self.carrier_bigint_bit_length,
            "carrier_root216": self.carrier_root216,
            "shard_count": self.shard_count,
            "final_shard_bit_length": self.final_shard_bit_length,
            "ordered_shard_roots": list(self.ordered_shard_roots),
            "shards": [shard.to_dict() for shard in self.shards],
            "package_root216": self.package_root216,
            "package_receipt_hash72": self.package_receipt_hash72,
            "metrics": dict(self.metrics),
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "Pass211Package":
        if value.get("schema") != PACKAGE_SCHEMA or value.get("contract") != CONTRACT:
            raise Pass211ValidationError("PASS211_PACKAGE_SCHEMA_INVALID")
        try:
            shards = tuple(Pass211Shard.from_mapping(item) for item in value["shards"])
            return cls(
                source_ciphertext_bit_length=int(value["source_ciphertext_bit_length"]),
                source_ciphertext_hash216=str(value["source_ciphertext_hash216"]),
                pass133_hash72_digest=str(value["pass133_hash72_digest"]),
                carrier_byte_length=int(value["carrier_byte_length"]),
                carrier_serialized_bit_length=int(value["carrier_serialized_bit_length"]),
                carrier_bigint_bit_length=int(value["carrier_bigint_bit_length"]),
                carrier_root216=str(value["carrier_root216"]),
                shard_count=int(value["shard_count"]),
                final_shard_bit_length=int(value["final_shard_bit_length"]),
                ordered_shard_roots=tuple(str(item) for item in value["ordered_shard_roots"]),
                shards=shards,
                package_root216=str(value["package_root216"]),
                package_receipt_hash72=str(value["package_receipt_hash72"]),
                metrics=dict(value["metrics"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise Pass211ValidationError("PASS211_PACKAGE_RECORD_INVALID") from exc


class Pass211BigIntHFCRuntime:
    """Deterministic package authority over inherited Pass 133 and Pass 210."""

    @staticmethod
    def _projection_set(
        runtime: HolographicFrameCompressionRuntime,
        register: bytes,
    ) -> dict[str, HFCProjection]:
        return {
            modality: runtime.project(register, modality)
            for modality in ("hash72", "hash216", "phase", "frame")
        }

    @staticmethod
    def _strict_probe(register: bytes) -> tuple[str, str]:
        probe = HolographicFrameCompressionRuntime()
        try:
            package = probe.strict_compress(register)
        except HFCError as exc:
            detail = str(exc)
            if "HFC_STRICT_COMPRESSION_DOMAIN_WITNESS_REQUIRED" in detail:
                return "STRICT_DOMAIN_REJECTED", detail
            raise Pass211ValidationError(f"PASS211_STRICT_PROBE_FAILED:{detail}") from exc
        return "STRICT_DOMAIN_ADMITTED", str(package["admissible_domain_witness_hash216"])

    @staticmethod
    def _snapshot_roots(
        runtime: HolographicFrameCompressionRuntime,
        frame: HFCFrame,
    ) -> tuple[str, ...]:
        return tuple(
            _hash216(
                "PASS211_HFC_SNAPSHOT",
                index.to_bytes(2, "big") + runtime.snapshot(frame, index),
            )
            for index in range(SNAPSHOT_COUNT)
        )

    @staticmethod
    def _shard_root_payload(record: Mapping[str, Any]) -> dict[str, Any]:
        return {
            key: record[key]
            for key in (
                "index",
                "count",
                "payload_byte_length",
                "payload_bit_length",
                "payload_hash216",
                "register_hash216",
                "hash72_identity",
                "hash216_identity",
                "phase_identity",
                "frame_identity",
                "frame_receipt_hash72",
                "snapshot_hash216",
                "strict_domain_status",
                "strict_domain_detail",
            )
        }

    @staticmethod
    def _package_root_payload(
        *,
        source_ciphertext_bit_length: int,
        source_ciphertext_hash216: str,
        pass133_hash72_digest: str,
        carrier_byte_length: int,
        carrier_serialized_bit_length: int,
        carrier_bigint_bit_length: int,
        carrier_root216: str,
        shard_count: int,
        final_shard_bit_length: int,
        ordered_shard_roots: Sequence[str],
    ) -> dict[str, Any]:
        return {
            "schema": PACKAGE_SCHEMA,
            "contract": CONTRACT,
            "contract_version": CONTRACT_VERSION,
            "source_ciphertext_bit_length": source_ciphertext_bit_length,
            "source_ciphertext_hash216": source_ciphertext_hash216,
            "pass133_hash72_digest": pass133_hash72_digest,
            "carrier_byte_length": carrier_byte_length,
            "carrier_serialized_bit_length": carrier_serialized_bit_length,
            "carrier_bigint_bit_length": carrier_bigint_bit_length,
            "carrier_root216": carrier_root216,
            "shard_count": shard_count,
            "final_shard_bit_length": final_shard_bit_length,
            "ordered_shard_roots": list(ordered_shard_roots),
        }

    @staticmethod
    def _package_receipt(package_root216: str, ordered_shard_roots: Sequence[str]) -> str:
        return hash72_digest(
            {"contract": CONTRACT, "version": CONTRACT_VERSION, "event": "PASS211_PACKAGE_COMMIT"},
            {
                "sequence": 1,
                "parent_hash72": ZERO_HASH72,
                "package_root216": package_root216,
                "ordered_shard_roots": list(ordered_shard_roots),
            },
        )

    @staticmethod
    def _metrics(source: int, carrier_bytes: int, shard_count: int) -> dict[str, Any]:
        source_bytes = max(1, (int(source).bit_length() + 7) // 8)
        return {
            "source_byte_length": source_bytes,
            "carrier_byte_length": carrier_bytes,
            "carrier_expansion_ratio": {"numerator": carrier_bytes, "denominator": source_bytes},
            "logical_register_occupancy": {
                "numerator": carrier_bytes,
                "denominator": REGISTER_LEN * shard_count,
            },
            "packed_bit_capacity_occupancy": {
                "numerator": carrier_bytes * 8,
                "denominator": REGISTER_LEN * shard_count,
            },
            "canonical_hfc_storage_bytes": REGISTER_LEN * shard_count,
            "native_packed_capacity_bytes": PACKED_SHARD_BYTES * shard_count,
            "single_register_capacity_bytes": PACKED_SHARD_BYTES,
            "multi_register_required": shard_count > 1,
            "strict_compression_claim": "PER_SHARD_ONLY_WHEN_DECLARED_DOMAIN_ADMITTED",
        }

    def encode(self, ciphertext: int) -> Pass211Package:
        try:
            source = int(ciphertext)
        except (TypeError, ValueError) as exc:
            raise Pass211ValidationError("PASS211_CIPHERTEXT_INVALID") from exc
        try:
            protected = protect_encrypted_bigint(source)
        except CanonicalEncodingError as exc:
            raise Pass211ValidationError(f"PASS211_PASS133_ENVELOPE_REJECTED:{exc}") from exc
        if protected.get("status") != "PALINDROMIC_ECC_BIGINT_RECONSTRUCTION_VERIFIED":
            raise Pass211ValidationError("PASS211_PASS133_PROTECTION_NOT_VERIFIED")
        carrier_bigint = int(str(protected["carrier_bigint_hex"]), 16)
        carrier_bytes = bigint_to_bytes(carrier_bigint)
        chunks = [
            carrier_bytes[offset : offset + PACKED_SHARD_BYTES]
            for offset in range(0, len(carrier_bytes), PACKED_SHARD_BYTES)
        ]
        if not chunks or len(chunks) > MAX_SHARDS:
            raise Pass211ValidationError("PASS211_SHARD_COUNT_OUT_OF_RANGE")
        shard_count = len(chunks)
        hfc = HolographicFrameCompressionRuntime()
        shards: list[Pass211Shard] = []
        for index, payload in enumerate(chunks):
            payload_bit_length = len(payload) * 8
            register = packed_bytes_to_register(payload)
            frame = hfc.frame_encode(register)
            projections = self._projection_set(hfc, register)
            snapshot_roots = self._snapshot_roots(hfc, frame)
            strict_status, strict_detail = self._strict_probe(register)
            record: dict[str, Any] = {
                "index": index,
                "count": shard_count,
                "payload_byte_length": len(payload),
                "payload_bit_length": payload_bit_length,
                "payload_hash216": _hash216("PASS211_SHARD_PAYLOAD", payload),
                "register_hash216": frame.object_hash216,
                "hash72_identity": projections["hash72"].identity,
                "hash216_identity": projections["hash216"].identity,
                "phase_identity": projections["phase"].identity,
                "frame_identity": projections["frame"].identity,
                "frame_receipt_hash72": frame.receipt_hash72,
                "snapshot_hash216": list(snapshot_roots),
                "strict_domain_status": strict_status,
                "strict_domain_detail": strict_detail,
            }
            shard_root = _hash216(
                "PASS211_ORDERED_SHARD_ROOT",
                _canonical_bytes(self._shard_root_payload(record)),
            )
            shards.append(
                Pass211Shard(
                    index=index,
                    count=shard_count,
                    payload_hex=payload.hex(),
                    payload_byte_length=len(payload),
                    payload_bit_length=payload_bit_length,
                    payload_hash216=record["payload_hash216"],
                    register_hash216=record["register_hash216"],
                    hash72_identity=record["hash72_identity"],
                    hash216_identity=record["hash216_identity"],
                    phase_identity=record["phase_identity"],
                    frame_identity=record["frame_identity"],
                    frame_receipt_hash72=record["frame_receipt_hash72"],
                    snapshot_hash216=snapshot_roots,
                    strict_domain_status=strict_status,
                    strict_domain_detail=strict_detail,
                    shard_root216=shard_root,
                )
            )
        ordered_roots = tuple(shard.shard_root216 for shard in shards)
        witness = dict(protected["hash72_witness"])
        source_bytes = bigint_to_bytes(source)
        root_payload = self._package_root_payload(
            source_ciphertext_bit_length=source.bit_length(),
            source_ciphertext_hash216=_hash216("PASS211_SOURCE_CIPHERTEXT", source_bytes),
            pass133_hash72_digest=str(witness["digest"]),
            carrier_byte_length=len(carrier_bytes),
            carrier_serialized_bit_length=len(carrier_bytes) * 8,
            carrier_bigint_bit_length=carrier_bigint.bit_length(),
            carrier_root216=_hash216("PASS211_PASS133_CARRIER", carrier_bytes),
            shard_count=shard_count,
            final_shard_bit_length=shards[-1].payload_bit_length,
            ordered_shard_roots=ordered_roots,
        )
        package_root = _hash216("PASS211_PACKAGE_ROOT", _canonical_bytes(root_payload))
        return Pass211Package(
            source_ciphertext_bit_length=root_payload["source_ciphertext_bit_length"],
            source_ciphertext_hash216=root_payload["source_ciphertext_hash216"],
            pass133_hash72_digest=root_payload["pass133_hash72_digest"],
            carrier_byte_length=root_payload["carrier_byte_length"],
            carrier_serialized_bit_length=root_payload["carrier_serialized_bit_length"],
            carrier_bigint_bit_length=root_payload["carrier_bigint_bit_length"],
            carrier_root216=root_payload["carrier_root216"],
            shard_count=shard_count,
            final_shard_bit_length=root_payload["final_shard_bit_length"],
            ordered_shard_roots=ordered_roots,
            shards=tuple(shards),
            package_root216=package_root,
            package_receipt_hash72=self._package_receipt(package_root, ordered_roots),
            metrics=self._metrics(source, len(carrier_bytes), shard_count),
        )

    def _validate_structure(self, package: Pass211Package) -> None:
        if package.shard_count <= 0 or package.shard_count > MAX_SHARDS:
            raise Pass211ValidationError("PASS211_SHARD_COUNT_OUT_OF_RANGE")
        if len(package.shards) != package.shard_count:
            raise Pass211ValidationError("PASS211_MISSING_SHARD")
        indices = [shard.index for shard in package.shards]
        if len(set(indices)) != len(indices):
            raise Pass211ValidationError("PASS211_DUPLICATE_SHARD")
        if indices != list(range(package.shard_count)):
            raise Pass211ValidationError("PASS211_SHARD_ORDER_VIOLATION")
        if len(package.ordered_shard_roots) != package.shard_count:
            raise Pass211ValidationError("PASS211_ORDERED_ROOT_COUNT_MISMATCH")
        if tuple(shard.shard_root216 for shard in package.shards) != package.ordered_shard_roots:
            raise Pass211ValidationError("PASS211_ORDERED_SHARD_ROOT_MISMATCH")
        if not 0 < package.final_shard_bit_length <= REGISTER_LEN:
            raise Pass211ValidationError("PASS211_FINAL_SHARD_BIT_LENGTH_INVALID")
        if package.final_shard_bit_length != package.shards[-1].payload_bit_length:
            raise Pass211ValidationError("PASS211_FINAL_SHARD_BIT_LENGTH_MISMATCH")
        for shard in package.shards[:-1]:
            if shard.payload_bit_length != REGISTER_LEN or shard.payload_byte_length != PACKED_SHARD_BYTES:
                raise Pass211ValidationError("PASS211_NONFINAL_SHARD_NOT_FULL")

    def _verify_shard(
        self,
        runtime: HolographicFrameCompressionRuntime,
        shard: Pass211Shard,
        expected_count: int,
    ) -> tuple[bytes, HFCFrame]:
        if shard.count != expected_count:
            raise Pass211ValidationError("PASS211_SHARD_COUNT_FIELD_MISMATCH")
        try:
            payload = bytes.fromhex(shard.payload_hex)
        except ValueError as exc:
            raise Pass211ValidationError("PASS211_SHARD_PAYLOAD_HEX_INVALID") from exc
        if len(payload) != shard.payload_byte_length or shard.payload_bit_length != len(payload) * 8:
            raise Pass211ValidationError("PASS211_SHARD_PAYLOAD_LENGTH_MISMATCH")
        if not 0 < len(payload) <= PACKED_SHARD_BYTES:
            raise Pass211ValidationError("PASS211_SHARD_PAYLOAD_LENGTH_INVALID")
        if _hash216("PASS211_SHARD_PAYLOAD", payload) != shard.payload_hash216:
            raise Pass211ValidationError("PASS211_SHARD_SUBSTITUTION_DETECTED")
        register = packed_bytes_to_register(payload)
        if register_to_packed_bytes(register, shard.payload_bit_length) != payload:
            raise Pass211ValidationError("PASS211_REGISTER_PACKING_ROUNDTRIP_FAILURE")
        frame = runtime.frame_encode(register)
        projections = self._projection_set(runtime, register)
        checks = {
            "register_hash216": frame.object_hash216 == shard.register_hash216,
            "hash72_identity": projections["hash72"].identity == shard.hash72_identity,
            "hash216_identity": projections["hash216"].identity == shard.hash216_identity,
            "phase_identity": projections["phase"].identity == shard.phase_identity,
            "frame_identity": projections["frame"].identity == shard.frame_identity,
            "frame_receipt_hash72": frame.receipt_hash72 == shard.frame_receipt_hash72,
        }
        if not all(checks.values()):
            failed = ",".join(name for name, ok in checks.items() if not ok)
            raise Pass211ValidationError(f"PASS211_SHARD_ANCHOR_MISMATCH:{failed}")
        snapshot_roots = self._snapshot_roots(runtime, frame)
        if len(shard.snapshot_hash216) != SNAPSHOT_COUNT or snapshot_roots != shard.snapshot_hash216:
            raise Pass211ValidationError("PASS211_SNAPSHOT_WITNESS_MISMATCH")
        strict_status, strict_detail = self._strict_probe(register)
        if (strict_status, strict_detail) != (shard.strict_domain_status, shard.strict_domain_detail):
            raise Pass211ValidationError("PASS211_STRICT_DOMAIN_STATUS_MISMATCH")
        record = shard.to_dict()
        expected_root = _hash216(
            "PASS211_ORDERED_SHARD_ROOT",
            _canonical_bytes(self._shard_root_payload(record)),
        )
        if expected_root != shard.shard_root216:
            raise Pass211ValidationError("PASS211_SHARD_ROOT_MISMATCH")
        return payload, frame

    def decode(self, package: Pass211Package | Mapping[str, Any]) -> dict[str, Any]:
        value = package if isinstance(package, Pass211Package) else Pass211Package.from_mapping(package)
        self._validate_structure(value)
        runtime = HolographicFrameCompressionRuntime()
        carrier_parts: list[bytes] = []
        for shard in value.shards:
            payload, _ = self._verify_shard(runtime, shard, value.shard_count)
            carrier_parts.append(payload)
        carrier_bytes = b"".join(carrier_parts)
        if len(carrier_bytes) != value.carrier_byte_length:
            raise Pass211ValidationError("PASS211_CARRIER_LENGTH_MISMATCH")
        if len(carrier_bytes) * 8 != value.carrier_serialized_bit_length:
            raise Pass211ValidationError("PASS211_CARRIER_SERIALIZED_BIT_LENGTH_MISMATCH")
        if _hash216("PASS211_PASS133_CARRIER", carrier_bytes) != value.carrier_root216:
            raise Pass211ValidationError("PASS211_CARRIER_ROOT_MISMATCH")
        carrier_bigint = int.from_bytes(carrier_bytes, "big")
        if carrier_bigint.bit_length() != value.carrier_bigint_bit_length:
            raise Pass211ValidationError("PASS211_CARRIER_BIGINT_BIT_LENGTH_MISMATCH")
        try:
            carrier = PalindromicCarrier.from_bigint(carrier_bigint)
            decoded = decode_palindromic_carrier(carrier)
        except (CanonicalEncodingError, ValueError) as exc:
            raise Pass211ValidationError(f"PASS211_PASS133_DECODE_REJECTED:{exc}") from exc
        ciphertext = int(str(decoded["ciphertext_hex"]), 16)
        source_bytes = bigint_to_bytes(ciphertext)
        try:
            reprotected = protect_encrypted_bigint(ciphertext)
        except CanonicalEncodingError as exc:
            raise Pass211ValidationError(f"PASS211_PASS133_REPROTECTION_REJECTED:{exc}") from exc
        reproduced_carrier = bigint_to_bytes(int(str(reprotected["carrier_bigint_hex"]), 16))
        if reproduced_carrier != carrier_bytes:
            raise Pass211ValidationError("PASS211_PASS133_CANONICAL_CARRIER_MISMATCH")
        reproduced_witness = dict(reprotected["hash72_witness"])
        if str(reproduced_witness["digest"]) != value.pass133_hash72_digest:
            raise Pass211ValidationError("PASS211_PASS133_HASH72_WITNESS_MISMATCH")
        if ciphertext.bit_length() != value.source_ciphertext_bit_length:
            raise Pass211ValidationError("PASS211_SOURCE_BIT_LENGTH_MISMATCH")
        if _hash216("PASS211_SOURCE_CIPHERTEXT", source_bytes) != value.source_ciphertext_hash216:
            raise Pass211ValidationError("PASS211_SOURCE_HASH_MISMATCH")
        root_payload = self._package_root_payload(
            source_ciphertext_bit_length=value.source_ciphertext_bit_length,
            source_ciphertext_hash216=value.source_ciphertext_hash216,
            pass133_hash72_digest=value.pass133_hash72_digest,
            carrier_byte_length=value.carrier_byte_length,
            carrier_serialized_bit_length=value.carrier_serialized_bit_length,
            carrier_bigint_bit_length=value.carrier_bigint_bit_length,
            carrier_root216=value.carrier_root216,
            shard_count=value.shard_count,
            final_shard_bit_length=value.final_shard_bit_length,
            ordered_shard_roots=value.ordered_shard_roots,
        )
        package_root = _hash216("PASS211_PACKAGE_ROOT", _canonical_bytes(root_payload))
        if package_root != value.package_root216:
            raise Pass211ValidationError("PASS211_PACKAGE_ROOT_MISMATCH")
        expected_receipt = self._package_receipt(package_root, value.ordered_shard_roots)
        if expected_receipt != value.package_receipt_hash72:
            raise Pass211ValidationError("PASS211_PACKAGE_RECEIPT_MISMATCH")
        expected_metrics = self._metrics(ciphertext, value.carrier_byte_length, value.shard_count)
        if dict(value.metrics) != expected_metrics:
            raise Pass211ValidationError("PASS211_METRICS_MISMATCH")
        return {
            "schema": "HHS_PASS_211_BIGINT_HFC_DECODE_RESULT_V1",
            "status": "PASS211_BIGINT_HFC_EXACT_RECONSTRUCTION_VERIFIED",
            "ciphertext_hex": hex(ciphertext),
            "ciphertext_bit_length": ciphertext.bit_length(),
            "carrier_byte_length": value.carrier_byte_length,
            "shard_count": value.shard_count,
            "package_root216": value.package_root216,
            "package_receipt_hash72": value.package_receipt_hash72,
            "pass133_decode": decoded,
            "metrics": dict(value.metrics),
        }

    def recover_shard(
        self,
        package: Pass211Package | Mapping[str, Any],
        shard_index: int,
        lost_snapshot_index: int,
    ) -> dict[str, Any]:
        value = package if isinstance(package, Pass211Package) else Pass211Package.from_mapping(package)
        self._validate_structure(value)
        index = int(shard_index)
        lost = int(lost_snapshot_index)
        if not 0 <= index < value.shard_count:
            raise Pass211ValidationError("PASS211_SHARD_INDEX_OUT_OF_RANGE")
        if not 0 <= lost < SNAPSHOT_COUNT:
            raise Pass211ValidationError("PASS211_SNAPSHOT_INDEX_OUT_OF_RANGE")
        runtime = HolographicFrameCompressionRuntime()
        target_frame: HFCFrame | None = None
        target_payload: bytes | None = None
        for shard in value.shards:
            payload, frame = self._verify_shard(runtime, shard, value.shard_count)
            if shard.index == index:
                target_frame = frame
                target_payload = payload
        if target_frame is None or target_payload is None:
            raise Pass211ValidationError("PASS211_MISSING_SHARD")
        recovered_register = runtime.recover(target_frame, lost)
        recovered_payload = register_to_packed_bytes(
            recovered_register,
            value.shards[index].payload_bit_length,
        )
        if recovered_payload != target_payload:
            raise Pass211ValidationError("PASS211_SHARD_RECOVERY_MISMATCH")
        return {
            "schema": "HHS_PASS_211_BIGINT_HFC_SHARD_RECOVERY_V1",
            "status": "PASS211_SHARD_ERASURE_RECOVERY_VERIFIED",
            "shard_index": index,
            "lost_snapshot_index": lost,
            "payload_hash216": _hash216("PASS211_SHARD_PAYLOAD", recovered_payload),
            "package_root216": value.package_root216,
        }

    def anchored_compare(
        self,
        package: Pass211Package | Mapping[str, Any],
        shard_index: int,
        fresh_payload: bytes | bytearray | memoryview,
    ) -> dict[str, Any]:
        """Compare a fresh read against stored anchors; never fresh against fresh."""
        value = package if isinstance(package, Pass211Package) else Pass211Package.from_mapping(package)
        self._validate_structure(value)
        index = int(shard_index)
        if not 0 <= index < value.shard_count:
            raise Pass211ValidationError("PASS211_SHARD_INDEX_OUT_OF_RANGE")
        shard = value.shards[index]
        expected = bytes.fromhex(shard.payload_hex)
        fresh = bytes(fresh_payload)
        if len(fresh) != len(expected):
            raise Pass211ValidationError("PASS211_FRESH_PAYLOAD_LENGTH_MISMATCH")
        expected_register = packed_bytes_to_register(expected)
        fresh_register = packed_bytes_to_register(fresh)
        disagreement_cells = [
            cell for cell, pair in enumerate(zip(expected_register, fresh_register)) if pair[0] != pair[1]
        ]
        stored_runtime = HolographicFrameCompressionRuntime()
        stored_projections = self._projection_set(stored_runtime, expected_register)
        stored_anchor_validity = {
            "hash72": stored_projections["hash72"].identity == shard.hash72_identity,
            "hash216": stored_projections["hash216"].identity == shard.hash216_identity,
            "phase": stored_projections["phase"].identity == shard.phase_identity,
            "frame": stored_projections["frame"].identity == shard.frame_identity,
        }
        if not all(stored_anchor_validity.values()):
            raise Pass211ValidationError("PASS211_STORED_ANCHOR_INVALID")
        fresh_runtime = HolographicFrameCompressionRuntime()
        fresh_projections = self._projection_set(fresh_runtime, fresh_register)
        anchor_matches = {
            "hash72": fresh_projections["hash72"].identity == shard.hash72_identity,
            "hash216": fresh_projections["hash216"].identity == shard.hash216_identity,
            "phase": fresh_projections["phase"].identity == shard.phase_identity,
            "frame": fresh_projections["frame"].identity == shard.frame_identity,
        }
        fresh_agreement = fresh_runtime.agree(*fresh_projections.values())
        verified = not disagreement_cells and all(anchor_matches.values())
        return {
            "schema": "HHS_PASS_211_ANCHORED_AGREEMENT_V1",
            "status": (
                "ANCHORED_WITNESSES_VERIFIED"
                if verified
                else "ANCHORED_DISAGREEMENT_LOCATED"
            ),
            "shard_index": index,
            "disagreement_cells": disagreement_cells,
            "stored_anchor_validity": stored_anchor_validity,
            "fresh_anchor_matches": anchor_matches,
            "surviving_witnesses": [
                f"stored_{name}" for name, valid in stored_anchor_validity.items() if valid
            ],
            "fresh_projection_agreement": bool(fresh_agreement["agreement"]),
            "repair_performed": False,
            "fresh_projection_self_consistency_is_not_historical_integrity": True,
        }

    @staticmethod
    def status() -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_211_BIGINT_HFC_RUNTIME_STATUS_V1",
            "contract": CONTRACT,
            "pass": PASS_NUMBER,
            "contract_version": CONTRACT_VERSION,
            "contract_classification": CONTRACT_CLASSIFICATION,
            "runtime_classification": RUNTIME_CLASSIFICATION,
            "packed_shard_bytes": PACKED_SHARD_BYTES,
            "packed_shard_bits": PACKED_SHARD_BITS,
            "register_len": REGISTER_LEN,
            "snapshot_count": SNAPSHOT_COUNT,
            "bit_order": "MSB_FIRST_WITHIN_EACH_BYTE",
            "shard_order": "ZERO_BASED_ASCENDING",
            "agreement_semantics": (
                "fresh projections establish contemporaneous consistency only; historical "
                "integrity requires at least one independently retained minted anchor"
            ),
            "strict_compression_boundary": (
                "per-shard strict compression is claimed only when Pass 210 admits the "
                "declared affine-Fibonacci domain witness"
            ),
        }


_RUNTIME = Pass211BigIntHFCRuntime()


def pass211_encode_bigint(ciphertext: int) -> Pass211Package:
    return _RUNTIME.encode(ciphertext)


def pass211_decode_bigint(package: Pass211Package | Mapping[str, Any]) -> dict[str, Any]:
    return _RUNTIME.decode(package)


def pass211_recover_shard(
    package: Pass211Package | Mapping[str, Any],
    shard_index: int,
    lost_snapshot_index: int,
) -> dict[str, Any]:
    return _RUNTIME.recover_shard(package, shard_index, lost_snapshot_index)


def pass211_anchored_compare(
    package: Pass211Package | Mapping[str, Any],
    shard_index: int,
    fresh_payload: bytes | bytearray | memoryview,
) -> dict[str, Any]:
    return _RUNTIME.anchored_compare(package, shard_index, fresh_payload)


def get_pass211_runtime() -> Pass211BigIntHFCRuntime:
    return _RUNTIME


__all__ = [
    "CONTRACT",
    "CONTRACT_CLASSIFICATION",
    "CONTRACT_VERSION",
    "PACKED_SHARD_BITS",
    "PACKED_SHARD_BYTES",
    "PASS_NUMBER",
    "Pass211BigIntHFCRuntime",
    "Pass211Error",
    "Pass211Package",
    "Pass211Shard",
    "Pass211ValidationError",
    "RUNTIME_CLASSIFICATION",
    "get_pass211_runtime",
    "packed_bytes_to_register",
    "pass211_anchored_compare",
    "pass211_decode_bigint",
    "pass211_encode_bigint",
    "pass211_recover_shard",
    "register_to_packed_bytes",
]
