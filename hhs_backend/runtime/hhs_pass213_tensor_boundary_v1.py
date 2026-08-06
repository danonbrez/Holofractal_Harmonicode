"""Trusted timestamp boundary and derived floating projection for Iteration 8."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hmac
import struct
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    CONTRACT,
    canonical_bytes,
    hash216,
)
from hhs_backend.runtime.hhs_pass213_tensor_geometry_v1 import AXIS_MODULI
from hhs_backend.runtime.hhs_pass213_trusted_timestamp_v1 import (
    TrustedTimestampAnchorRecord,
)

ITERATION = 8


class Pass213TensorBoundaryError(RuntimeError):
    pass


def require_hash216(value: str, code: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise Pass213TensorBoundaryError(code)
    try:
        int(value, 16)
    except ValueError as exc:
        raise Pass213TensorBoundaryError(code) from exc
    return value


@dataclass(frozen=True)
class TensorAnchorBinding:
    anchor_sequence: int
    signed_sequence: int
    anchor_root_hash216: str
    signed_checkpoint_root_hash216: str
    verifier_bundle_root_hash216: str
    hash216_lineage_root: str
    requested_timestamp_ns: int
    timestamp_evidence_root_hash216: str
    tsa_serial_hex: str
    gen_time_utc: str
    boundary_root_hash216: str

    @classmethod
    def from_trusted_anchor(cls, record: TrustedTimestampAnchorRecord) -> "TensorAnchorBinding":
        record.intent.validate()
        record.evidence.validate_structure(record.intent)
        expected_anchor = hash216(
            "trusted-external-timestamp-anchor", canonical_bytes(record.rooted_payload())
        )
        if not hmac.compare_digest(expected_anchor, record.anchor_root_hash216):
            raise Pass213TensorBoundaryError("PASS213_TENSOR_ANCHOR_ROOT_MISMATCH")
        signed_root = str(record.signed_checkpoint.get("signed_checkpoint_root_hash216", ""))
        bundle_root = str(record.signed_checkpoint.get("verifier_bundle_root_hash216", ""))
        signed_sequence = int(record.signed_checkpoint.get("signed_sequence", -1))
        if (
            signed_root != record.intent.signed_checkpoint_root_hash216
            or bundle_root != record.intent.verifier_bundle_root_hash216
            or signed_sequence != record.intent.signed_sequence
        ):
            raise Pass213TensorBoundaryError("PASS213_TENSOR_SIGNED_CHECKPOINT_BINDING_MISMATCH")
        unsigned = {
            "schema": "HHS_PASS_213_TENSOR_ANCHOR_BINDING_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "anchor_sequence": record.intent.anchor_sequence,
            "signed_sequence": record.intent.signed_sequence,
            "anchor_root_hash216": record.anchor_root_hash216,
            "signed_checkpoint_root_hash216": signed_root,
            "verifier_bundle_root_hash216": bundle_root,
            "hash216_lineage_root": record.intent.hash216_lineage_root,
            "requested_timestamp_ns": record.intent.requested_timestamp_ns,
            "timestamp_evidence_root_hash216": record.evidence.evidence_root_hash216,
            "tsa_serial_hex": record.evidence.tsa_serial_hex,
            "gen_time_utc": record.evidence.gen_time_utc,
        }
        binding = cls(
            record.intent.anchor_sequence,
            record.intent.signed_sequence,
            record.anchor_root_hash216,
            signed_root,
            bundle_root,
            record.intent.hash216_lineage_root,
            record.intent.requested_timestamp_ns,
            record.evidence.evidence_root_hash216,
            record.evidence.tsa_serial_hex,
            record.evidence.gen_time_utc,
            hash216("moving-tensor-anchor-boundary", canonical_bytes(unsigned)),
        )
        binding.validate()
        return binding

    def unsigned_payload(self) -> Mapping[str, Any]:
        return {
            "schema": "HHS_PASS_213_TENSOR_ANCHOR_BINDING_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "anchor_sequence": self.anchor_sequence,
            "signed_sequence": self.signed_sequence,
            "anchor_root_hash216": self.anchor_root_hash216,
            "signed_checkpoint_root_hash216": self.signed_checkpoint_root_hash216,
            "verifier_bundle_root_hash216": self.verifier_bundle_root_hash216,
            "hash216_lineage_root": self.hash216_lineage_root,
            "requested_timestamp_ns": self.requested_timestamp_ns,
            "timestamp_evidence_root_hash216": self.timestamp_evidence_root_hash216,
            "tsa_serial_hex": self.tsa_serial_hex,
            "gen_time_utc": self.gen_time_utc,
        }

    def to_mapping(self) -> dict[str, Any]:
        return {**self.unsigned_payload(), "boundary_root_hash216": self.boundary_root_hash216}

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "TensorAnchorBinding":
        binding = cls(
            int(value["anchor_sequence"]), int(value["signed_sequence"]),
            str(value["anchor_root_hash216"]), str(value["signed_checkpoint_root_hash216"]),
            str(value["verifier_bundle_root_hash216"]), str(value["hash216_lineage_root"]),
            int(value["requested_timestamp_ns"]), str(value["timestamp_evidence_root_hash216"]),
            str(value["tsa_serial_hex"]), str(value["gen_time_utc"]),
            str(value["boundary_root_hash216"]),
        )
        binding.validate()
        return binding

    def validate(self) -> None:
        if self.anchor_sequence < 1 or self.anchor_sequence != self.signed_sequence:
            raise Pass213TensorBoundaryError("PASS213_TENSOR_ANCHOR_SEQUENCE_INVALID")
        for value, code in (
            (self.anchor_root_hash216, "PASS213_TENSOR_ANCHOR_HASH_INVALID"),
            (self.signed_checkpoint_root_hash216, "PASS213_TENSOR_SIGNED_ROOT_INVALID"),
            (self.verifier_bundle_root_hash216, "PASS213_TENSOR_BUNDLE_ROOT_INVALID"),
            (self.hash216_lineage_root, "PASS213_TENSOR_LINEAGE_ROOT_INVALID"),
            (self.timestamp_evidence_root_hash216, "PASS213_TENSOR_EVIDENCE_ROOT_INVALID"),
        ):
            require_hash216(value, code)
        if self.requested_timestamp_ns < 0 or not self.tsa_serial_hex.startswith("0x") or not self.gen_time_utc.endswith("Z"):
            raise Pass213TensorBoundaryError("PASS213_TENSOR_TIMESTAMP_BOUNDARY_INVALID")
        expected = hash216("moving-tensor-anchor-boundary", canonical_bytes(self.unsigned_payload()))
        if not hmac.compare_digest(expected, self.boundary_root_hash216):
            raise Pass213TensorBoundaryError("PASS213_TENSOR_BOUNDARY_ROOT_MISMATCH")


@dataclass(frozen=True)
class FloatingTensorProjection:
    format: str
    endianness: str
    rounding: str
    fused_operation_policy: str
    nan_policy: str
    subnormal_policy: str
    source_tensor_root_hash216: str
    exact_ratios: tuple[tuple[int, int], ...]
    binary64_hex: tuple[str, ...]
    projection_root_hash216: str

    @classmethod
    def derive(cls, tensor_root_hash216: str, phase: Sequence[int]) -> "FloatingTensorProjection":
        require_hash216(tensor_root_hash216, "PASS213_TENSOR_FLOAT_SOURCE_INVALID")
        ratios = tuple((int(value), AXIS_MODULI[index]) for index, value in enumerate(phase))
        bits = tuple(struct.pack(">d", numerator / denominator).hex() for numerator, denominator in ratios)
        unsigned = {
            "format": "IEEE-754-binary64", "endianness": "big", "rounding": "nearest-even",
            "fused_operation_policy": "forbidden", "nan_policy": "forbidden",
            "subnormal_policy": "preserve", "source_tensor_root_hash216": tensor_root_hash216,
            "exact_ratios": ratios, "binary64_hex": bits,
        }
        projection = cls(**unsigned, projection_root_hash216=hash216(
            "moving-tensor-floating-projection", canonical_bytes(unsigned)
        ))
        projection.validate()
        return projection

    def to_mapping(self) -> dict[str, Any]:
        return asdict(self)

    def validate(self) -> None:
        if (
            self.format != "IEEE-754-binary64" or self.endianness != "big"
            or self.rounding != "nearest-even" or self.fused_operation_policy != "forbidden"
            or self.nan_policy != "forbidden"
        ):
            raise Pass213TensorBoundaryError("PASS213_TENSOR_FLOAT_PROFILE_INVALID")
        bits = tuple(struct.pack(">d", n / d).hex() for n, d in self.exact_ratios)
        if bits != self.binary64_hex:
            raise Pass213TensorBoundaryError("PASS213_TENSOR_FLOAT_BITS_MISMATCH")
        unsigned = {key: value for key, value in asdict(self).items() if key != "projection_root_hash216"}
        expected = hash216("moving-tensor-floating-projection", canonical_bytes(unsigned))
        if not hmac.compare_digest(expected, self.projection_root_hash216):
            raise Pass213TensorBoundaryError("PASS213_TENSOR_FLOAT_PROJECTION_ROOT_MISMATCH")
