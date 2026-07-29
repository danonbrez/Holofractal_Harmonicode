"""Shared Pass 166 identities, exact numeric rules, and immutable records."""
from __future__ import annotations

from base64 import b64encode
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json
import os
import struct
from typing import Any, Mapping
from urllib.parse import urlparse

SCHEMA = "HHS_PASS_166_WORD2VEC_SERVICE_V1"
CONTRACT_ID = "HHS-P166-W2V-LMVS-MAIS"
RUNTIME_VERSION = "HHS-P166-W2V-RUNTIME-1.0.0"
IMPORT_PROFILE = "HHS-P166-STRICT-IMPORT-1.0.0"
QUANTIZATION_PROFILE = "HHS-P166-Q16_16-HALF_EVEN-1.0.0"
PROJECTION_VERSION = "HHS-P166-5184-PROJECTION-1.0.0"
INDEX_VERSION = "HHS-P166-EXACT-INDEX-1.0.0"
QUANTIZATION_SCALE = 1 << 16
SNAPSHOT_BYTES = 648
COORDINATES = 5184
MAX_PACKAGE_BYTES = 2 * 1024 * 1024 * 1024
MAX_EXTRACTED_BYTES = 4 * 1024 * 1024 * 1024
MAX_VOCABULARY = 5_000_000
MAX_DIMENSION = 4096
ZERO_HASH216 = "0" * 64
SUPPORTED_FORMATS = {"WORD2VEC_TEXT", "WORD2VEC_BINARY"}
SUPPORTED_ARCHIVES = {"NONE", "ZIP", "TAR", "TAR_GZ"}
NORMALIZATION_PROFILES = {"VERBATIM", "UNICODE_NFC", "UNICODE_NFKC", "CASE_FOLDED"}


class Word2VecError(ValueError):
    def __init__(self, classification: str, detail: str | None = None) -> None:
        super().__init__(classification if detail is None else f"{classification}:{detail}")
        self.classification = classification
        self.detail = detail


class SimulatedInterruption(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str).encode("utf-8")


def root(domain: bytes, value: Any) -> str:
    return sha256(domain + canonical_bytes(value)).hexdigest()


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def round_half_even(value: Fraction, scale: int = QUANTIZATION_SCALE) -> int:
    if value == 0:
        return 0
    sign = -1 if value < 0 else 1
    quotient, remainder = divmod(abs(value.numerator) * scale, value.denominator)
    doubled = remainder * 2
    if doubled > value.denominator or (doubled == value.denominator and quotient % 2):
        quotient += 1
    result = sign * quotient
    if not -(1 << 31) <= result < (1 << 31):
        raise Word2VecError("P166_NUMERIC_OVERFLOW")
    return result


def decimal_fraction(raw: str) -> Fraction:
    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise Word2VecError("P166_MALFORMED_NUMERIC_VALUE", raw) from exc
    if not value.is_finite():
        raise Word2VecError("P166_NONFINITE_VALUE", raw)
    return Fraction(value)


def float32_fraction(raw: bytes) -> Fraction:
    if len(raw) != 4:
        raise Word2VecError("P166_TRUNCATED_VECTOR_COMPONENT")
    bits = struct.unpack("<I", raw)[0]
    sign = -1 if bits >> 31 else 1
    exponent = (bits >> 23) & 0xFF
    mantissa = bits & 0x7FFFFF
    if exponent == 0xFF:
        raise Word2VecError("P166_NONFINITE_VALUE")
    if exponent == 0:
        value = Fraction(0, 1) if mantissa == 0 else Fraction(mantissa, 1 << 149)
    else:
        significand = (1 << 23) | mantissa
        shift = exponent - 150
        value = Fraction(significand << shift, 1) if shift >= 0 else Fraction(significand, 1 << -shift)
    return sign * value


def safe_member(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if not name or path.is_absolute() or ".." in path.parts or any(part in ("", ".") for part in path.parts):
        raise Word2VecError("P166_ARCHIVE_TRAVERSAL", name)
    return path


@dataclass(frozen=True)
class Word2VecPackageManifest:
    package_id: str
    display_name: str
    provider: str
    source_uri: str
    source_version: str
    license_id: str
    license_uri: str
    expected_byte_length: int
    expected_sha256: str
    archive_type: str
    vector_format: str
    vector_dimension: int
    vocabulary_size: int
    character_encoding: str = "utf-8"
    normalization_profile: str = "UNICODE_NFC"
    import_profile: str = IMPORT_PROFILE
    quantization_profile: str = QUANTIZATION_PROFILE
    projection_version: str = PROJECTION_VERSION
    index_version: str = INDEX_VERSION
    artifact_path: str | None = None
    allowed_redirect_hosts: tuple[str, ...] = ()
    compatibility_requirements: tuple[str, ...] = ("PASS165", "VM81", "HASH72", "HASH216")

    def validate(self) -> None:
        if not self.package_id or not self.display_name or not self.provider:
            raise Word2VecError("P166_MANIFEST_FIELD_REQUIRED")
        if not self.license_id or not self.license_uri:
            raise Word2VecError("P166_LICENSE_IDENTITY_REQUIRED")
        if not 0 < self.expected_byte_length <= MAX_PACKAGE_BYTES:
            raise Word2VecError("P166_PACKAGE_SIZE_BOUND")
        digest = self.expected_sha256.lower()
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise Word2VecError("P166_INVALID_EXPECTED_DIGEST")
        if self.archive_type not in SUPPORTED_ARCHIVES:
            raise Word2VecError("P166_UNSUPPORTED_ARCHIVE", self.archive_type)
        if self.vector_format not in SUPPORTED_FORMATS:
            raise Word2VecError("P166_UNSUPPORTED_VECTOR_FORMAT", self.vector_format)
        if not 1 <= self.vector_dimension <= MAX_DIMENSION:
            raise Word2VecError("P166_DIMENSION_BOUND")
        if not 1 <= self.vocabulary_size <= MAX_VOCABULARY:
            raise Word2VecError("P166_VOCABULARY_BOUND")
        if self.normalization_profile not in NORMALIZATION_PROFILES:
            raise Word2VecError("P166_UNSUPPORTED_NORMALIZATION_PROFILE")
        if self.quantization_profile != QUANTIZATION_PROFILE:
            raise Word2VecError("P166_UNSUPPORTED_QUANTIZATION_PROFILE")
        if urlparse(self.source_uri).scheme not in ("file", "https"):
            raise Word2VecError("P166_UNPINNED_OR_UNSUPPORTED_SOURCE", self.source_uri)

    @property
    def manifest_root(self) -> str:
        return root(b"HHS-P166-MANIFEST-V1\0", asdict(self))


@dataclass(frozen=True)
class CanonicalVector:
    source_token_b64: str
    decoded_token: str
    source_row: int
    dimension: int
    source_numeric_encoding: str
    source_vector_digest: str
    canonical_values: tuple[int, ...]
    denominator: int
    canonical_vector_digest: str

    @classmethod
    def create(cls, token: bytes, decoded: str, row: int, values: list[Fraction], encoding: str) -> "CanonicalVector":
        quantized = tuple(round_half_even(value) for value in values)
        source_digest = sha256(token + b"\0" + b"|".join(f"{v.numerator}/{v.denominator}".encode() for v in values)).hexdigest()
        body = {"token_b64": b64encode(token).decode("ascii"), "row": row, "dimension": len(quantized), "denominator": QUANTIZATION_SCALE, "values": quantized}
        return cls(body["token_b64"], decoded, row, len(quantized), encoding, source_digest, quantized, QUANTIZATION_SCALE, root(b"HHS-P166-CANONICAL-VECTOR-V1\0", body))


@dataclass(frozen=True)
class LanguageVectorObject:
    lexical_object_id: str
    source_token_identity: str
    decoded_token: str
    normalized_aliases: tuple[str, ...]
    canonical_vector_identity: str
    dimensionality: int
    source_model_identity: str
    projection_5184_b64: str
    projection_5184_root: str
    relation_index_root: str
    provenance_root: str


@dataclass(frozen=True)
class InstalledModel:
    model_id: str
    package_id: str
    manifest_root: str
    package_digest: str
    source_format: str
    dimension: int
    vocabulary_size: int
    canonical_model_root: str
    index_root: str
    idempotence_key: str
    lifecycle_state: str
    active: bool
    vectors: tuple[CanonicalVector, ...]
    objects: tuple[LanguageVectorObject, ...]
    aliases: Mapping[str, tuple[str, ...]]
    terminal_receipt: Mapping[str, Any]

    def serializable(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id, "package_id": self.package_id, "manifest_root": self.manifest_root,
            "package_digest": self.package_digest, "source_format": self.source_format, "dimension": self.dimension,
            "vocabulary_size": self.vocabulary_size, "canonical_model_root": self.canonical_model_root,
            "index_root": self.index_root, "idempotence_key": self.idempotence_key,
            "lifecycle_state": self.lifecycle_state, "active": self.active,
            "vectors": [asdict(item) for item in self.vectors], "objects": [asdict(item) for item in self.objects],
            "aliases": {key: list(value) for key, value in self.aliases.items()}, "terminal_receipt": dict(self.terminal_receipt),
        }

    @classmethod
    def from_serializable(cls, raw: Mapping[str, Any]) -> "InstalledModel":
        return cls(
            model_id=str(raw["model_id"]), package_id=str(raw["package_id"]), manifest_root=str(raw["manifest_root"]),
            package_digest=str(raw["package_digest"]), source_format=str(raw["source_format"]), dimension=int(raw["dimension"]),
            vocabulary_size=int(raw["vocabulary_size"]), canonical_model_root=str(raw["canonical_model_root"]),
            index_root=str(raw["index_root"]), idempotence_key=str(raw["idempotence_key"]), lifecycle_state=str(raw["lifecycle_state"]),
            active=bool(raw["active"]), vectors=tuple(CanonicalVector(**item) for item in raw["vectors"]),
            objects=tuple(LanguageVectorObject(**item) for item in raw["objects"]),
            aliases={str(key): tuple(value) for key, value in raw["aliases"].items()}, terminal_receipt=dict(raw["terminal_receipt"]),
        )
