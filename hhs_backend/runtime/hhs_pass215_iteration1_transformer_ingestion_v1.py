"""Pass 215 Iteration 1: exact quantized-transformer ingestion incidence.

This layer measures, without canonical floating point, how many source bytes in
quantized transformer tensors are admitted by the inherited Pass 212 full-
hydration codec.  It is a measurement layer only: it cannot promote runtime
mutation authority or authorize canonical mutation.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import gcd, prod
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass212_full_hydration_recovery_v1 import (
    FULL_FRAME_COUNT,
    FULL_HYDRATION_BYTES,
    FullHydrationRecoveryRuntime,
)
from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import canonical_bytes, hash216
from hhs_runtime.core.hash72_digest_v1 import hash72_digest

CONTRACT = "HHS-P215-I1-EXACT-QUANTIZED-TRANSFORMER-INGESTION-ADMISSION-INCIDENCE"
PASS_NUMBER = 215
ITERATION = 1
CONTRACT_VERSION = "1.0.0-iteration1"
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_1_TRANSFORMER_INGESTION_INCIDENCE"
MANIFEST_SCHEMA = "HHS_PASS_215_QUANTIZED_TRANSFORMER_MANIFEST_V1"
EVIDENCE_SCHEMA = "HHS_PASS_215_ITERATION_1_INCIDENCE_EVIDENCE_V1"

PASS214_MAIN_CLOSURE_COMMIT = "063bcc1426b5bba106e139cb7dba1c540df090df"
PASS214_MAIN_CLOSURE_TREE = "9b21320cc72f3c77c79a9d76b083fe8b0c97f9d5"
PASS214_AUTHORITY_ROOT_HASH216 = "c1d7875acd45f02da75101f5953541b6e1ce8ea3bb2cac39645004ab2509aeb8"
PASS215_BENCHMARK_PROFILE_ROOT_HASH216 = "a3079f0f0b94d9fb485970662455482d4dab86e01802ca5bfdef6af3fbb6d85e"
PASS213_GATE_PRESERVATION_ROOT_HASH216 = "214106621723b579ffe4813c74d5df98a7e14387293b8ecc3e1edc81bf066092"
PASS214_TERMINAL_RECEIPT_HASH72 = "!(KTNH1zFC/ikVVJ1qCp8OKfOX8IoP<O8-/Df(NcNLYbY<<i+ICL5g2luJlws)AOvyX9XvJD"
FROZEN_PROFILE_GIT_BLOB_SHA1 = "b458d674a75a4cfc64a32b9203dd693e3603576e"

TIER_1 = "TIER_1_GENERATOR_SEED_EXACT"
TIER_2 = "TIER_2_GENERATOR_PLUS_EXCEPTIONS"
TIER_3 = "TIER_3_RAW_FALLBACK"
ZERO_HASH72 = "0" * 72

_DTYPE_BITS = {
    "qint4": 4,
    "quint4": 4,
    "int8": 8,
    "uint8": 8,
    "int16": 16,
    "uint16": 16,
    "int32": 32,
    "uint32": 32,
}


class Pass215Iteration1Error(RuntimeError):
    """Base Iteration 1 failure."""


class Pass215Iteration1ValidationError(Pass215Iteration1Error):
    """Raised when canonical ingestion/evidence invariants are violated."""


def _reject_floats(value: Any, path: str = "$" ) -> None:
    if isinstance(value, float):
        raise Pass215Iteration1ValidationError(f"PASS215_I1_FLOAT_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_floats(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_floats(child, f"{path}[{index}]")


def _exact_fraction(numerator: int, denominator: int) -> Mapping[str, int]:
    numerator = int(numerator)
    denominator = int(denominator)
    if numerator < 0 or denominator <= 0:
        raise Pass215Iteration1ValidationError("PASS215_I1_FRACTION_INVALID")
    divisor = gcd(numerator, denominator)
    return {
        "numerator": numerator // divisor,
        "denominator": denominator // divisor,
    }


def _sha256_bytes(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def expected_tensor_bytes(dtype: str, shape: Sequence[int]) -> int:
    if dtype not in _DTYPE_BITS:
        raise Pass215Iteration1ValidationError(f"PASS215_I1_DTYPE_UNSUPPORTED:{dtype}")
    if not shape:
        raise Pass215Iteration1ValidationError("PASS215_I1_SHAPE_EMPTY")
    dimensions: list[int] = []
    for index, dimension in enumerate(shape):
        if isinstance(dimension, bool) or not isinstance(dimension, int) or dimension <= 0:
            raise Pass215Iteration1ValidationError(f"PASS215_I1_SHAPE_INVALID:{index}")
        dimensions.append(dimension)
    bits = prod(dimensions) * _DTYPE_BITS[dtype]
    return (bits + 7) // 8


def validate_manifest(manifest: Mapping[str, Any]) -> Mapping[str, Any]:
    _reject_floats(manifest)
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise Pass215Iteration1ValidationError("PASS215_I1_MANIFEST_SCHEMA_INVALID")
    model_id = manifest.get("model_id")
    if not isinstance(model_id, str) or not model_id.strip():
        raise Pass215Iteration1ValidationError("PASS215_I1_MODEL_ID_INVALID")
    tensors = manifest.get("tensors")
    if not isinstance(tensors, list) or not tensors:
        raise Pass215Iteration1ValidationError("PASS215_I1_TENSOR_SET_EMPTY")
    names: set[str] = set()
    validated: list[dict[str, Any]] = []
    for index, tensor in enumerate(tensors):
        if not isinstance(tensor, Mapping):
            raise Pass215Iteration1ValidationError(f"PASS215_I1_TENSOR_INVALID:{index}")
        name = tensor.get("name")
        if not isinstance(name, str) or not name or name in names:
            raise Pass215Iteration1ValidationError(f"PASS215_I1_TENSOR_NAME_INVALID:{index}")
        names.add(name)
        dtype = str(tensor.get("dtype", ""))
        shape = tensor.get("shape")
        if not isinstance(shape, list):
            raise Pass215Iteration1ValidationError(f"PASS215_I1_TENSOR_SHAPE_INVALID:{name}")
        expected = expected_tensor_bytes(dtype, shape)
        path = tensor.get("path")
        if not isinstance(path, str) or not path:
            raise Pass215Iteration1ValidationError(f"PASS215_I1_TENSOR_PATH_INVALID:{name}")
        offset = tensor.get("offset_bytes", 0)
        length = tensor.get("length_bytes", expected)
        if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
            raise Pass215Iteration1ValidationError(f"PASS215_I1_TENSOR_OFFSET_INVALID:{name}")
        if isinstance(length, bool) or not isinstance(length, int) or length != expected:
            raise Pass215Iteration1ValidationError(f"PASS215_I1_TENSOR_LENGTH_INVALID:{name}")
        digest = tensor.get("sha256")
        if digest is not None:
            if not isinstance(digest, str) or len(digest) != 64:
                raise Pass215Iteration1ValidationError(f"PASS215_I1_TENSOR_SHA256_INVALID:{name}")
            try:
                int(digest, 16)
            except ValueError as exc:
                raise Pass215Iteration1ValidationError(f"PASS215_I1_TENSOR_SHA256_INVALID:{name}") from exc
        validated.append({
            "name": name,
            "dtype": dtype,
            "shape": list(shape),
            "path": path,
            "offset_bytes": offset,
            "length_bytes": length,
            "sha256": digest,
        })
    normalized = dict(manifest)
    normalized["tensors"] = validated
    canonical_bytes(normalized)
    return normalized


def load_tensor_bytes(base_directory: Path, tensor: Mapping[str, Any]) -> bytes:
    base = Path(base_directory).resolve()
    target = (base / str(tensor["path"])).resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise Pass215Iteration1ValidationError(
            f"PASS215_I1_TENSOR_PATH_ESCAPE:{tensor['name']}"
        ) from exc
    offset = int(tensor["offset_bytes"])
    length = int(tensor["length_bytes"])
    with target.open("rb") as handle:
        handle.seek(offset)
        raw = handle.read(length)
    if len(raw) != length:
        raise Pass215Iteration1ValidationError(
            f"PASS215_I1_TENSOR_SOURCE_TRUNCATED:{tensor['name']}"
        )
    expected_digest = tensor.get("sha256")
    actual_digest = _sha256_bytes(raw)
    if expected_digest is not None and actual_digest != expected_digest:
        raise Pass215Iteration1ValidationError(
            f"PASS215_I1_TENSOR_SHA256_MISMATCH:{tensor['name']}"
        )
    return raw


@dataclass(frozen=True)
class TensorIncidence:
    name: str
    dtype: str
    shape: tuple[int, ...]
    source_bytes: int
    source_sha256: str
    full_hydration_window_count: int
    tail_fallback_bytes: int
    tier_1_bytes: int
    tier_2_bytes: int
    tier_3_bytes: int
    admitted_bytes: int
    codec_payload_bytes: int
    protected_storage_bytes: int
    generator_seed_units: int
    exception_units: int
    raw_fallback_units: int
    windows: tuple[Mapping[str, Any], ...]
    tensor_root_hash216: str

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "name": self.name,
            "dtype": self.dtype,
            "shape": list(self.shape),
            "source_bytes": self.source_bytes,
            "source_sha256": self.source_sha256,
            "full_hydration_window_count": self.full_hydration_window_count,
            "tail_fallback_bytes": self.tail_fallback_bytes,
            "tier_1_bytes": self.tier_1_bytes,
            "tier_2_bytes": self.tier_2_bytes,
            "tier_3_bytes": self.tier_3_bytes,
            "admitted_bytes": self.admitted_bytes,
            "codec_payload_bytes": self.codec_payload_bytes,
            "protected_storage_bytes": self.protected_storage_bytes,
            "generator_seed_units": self.generator_seed_units,
            "exception_units": self.exception_units,
            "raw_fallback_units": self.raw_fallback_units,
            "incidence_fraction_exact": _exact_fraction(self.admitted_bytes, self.source_bytes),
            "physical_ratio_exact": _exact_fraction(self.source_bytes, self.protected_storage_bytes),
            "windows": list(self.windows),
            "tensor_root_hash216": self.tensor_root_hash216,
        }


def measure_tensor(
    tensor: Mapping[str, Any],
    raw: bytes,
    *,
    runtime: FullHydrationRecoveryRuntime | None = None,
) -> TensorIncidence:
    runtime = runtime or FullHydrationRecoveryRuntime()
    if len(raw) != int(tensor["length_bytes"]):
        raise Pass215Iteration1ValidationError(
            f"PASS215_I1_TENSOR_BYTE_LENGTH_MISMATCH:{tensor['name']}"
        )
    full_count, tail = divmod(len(raw), FULL_HYDRATION_BYTES)
    tier_1 = tier_2 = tier_3 = 0
    codec_payload = 0
    protected_storage = 0
    seed_units = 0
    exception_units = 0
    raw_units = 0
    windows: list[Mapping[str, Any]] = []
    for window_index in range(full_count):
        start = window_index * FULL_HYDRATION_BYTES
        state = raw[start : start + FULL_HYDRATION_BYTES]
        package = runtime.encode(state)
        recovered = runtime.decode(package)
        if recovered != state:
            raise Pass215Iteration1ValidationError(
                f"PASS215_I1_SEMANTIC_RECONSTRUCTION_FAILED:{tensor['name']}:{window_index}"
            )
        physical = int(package.metrics["protected_storage_bytes"])
        if package.codec == "AFFINE_9720_LEAF_SEEDS_PLUS_SPARSE_XOR":
            if package.exception_count == 0:
                tier = TIER_1
                tier_1 += FULL_HYDRATION_BYTES
            else:
                tier = TIER_2
                tier_2 += FULL_HYDRATION_BYTES
            seed_units += FULL_FRAME_COUNT
            exception_units += int(package.exception_count)
        elif package.codec == "RAW_PACKED_FALLBACK":
            tier = TIER_3
            tier_3 += FULL_HYDRATION_BYTES
            raw_units += FULL_HYDRATION_BYTES
        else:
            raise Pass215Iteration1ValidationError("PASS215_I1_INHERITED_CODEC_UNKNOWN")
        codec_payload += int(package.compressed_payload_bytes)
        protected_storage += physical
        windows.append({
            "window_index": window_index,
            "byte_offset": start,
            "source_bytes": FULL_HYDRATION_BYTES,
            "source_sha256": _sha256_bytes(state),
            "tier": tier,
            "codec": package.codec,
            "exception_count": int(package.exception_count),
            "codec_payload_bytes": int(package.compressed_payload_bytes),
            "protected_storage_bytes": physical,
            "package_root216": package.package_root216,
            "package_receipt_hash72": package.package_receipt_hash72,
            "semantic_exactness": True,
        })
    if tail:
        tier_3 += tail
        raw_units += tail
        codec_payload += tail
        protected_storage += tail
        windows.append({
            "window_index": full_count,
            "byte_offset": full_count * FULL_HYDRATION_BYTES,
            "source_bytes": tail,
            "source_sha256": _sha256_bytes(raw[-tail:]),
            "tier": TIER_3,
            "codec": "INCOMPLETE_HYDRATION_TAIL_RAW_FALLBACK",
            "exception_count": 0,
            "codec_payload_bytes": tail,
            "protected_storage_bytes": tail,
            "package_root216": None,
            "package_receipt_hash72": None,
            "semantic_exactness": True,
        })
    admitted = tier_1 + tier_2
    root_payload = {
        "name": tensor["name"],
        "dtype": tensor["dtype"],
        "shape": tensor["shape"],
        "source_bytes": len(raw),
        "source_sha256": _sha256_bytes(raw),
        "windows": windows,
    }
    tensor_root = hash216("pass215-i1-tensor-incidence", canonical_bytes(root_payload))
    return TensorIncidence(
        name=str(tensor["name"]),
        dtype=str(tensor["dtype"]),
        shape=tuple(int(item) for item in tensor["shape"]),
        source_bytes=len(raw),
        source_sha256=_sha256_bytes(raw),
        full_hydration_window_count=full_count,
        tail_fallback_bytes=tail,
        tier_1_bytes=tier_1,
        tier_2_bytes=tier_2,
        tier_3_bytes=tier_3,
        admitted_bytes=admitted,
        codec_payload_bytes=codec_payload,
        protected_storage_bytes=protected_storage,
        generator_seed_units=seed_units,
        exception_units=exception_units,
        raw_fallback_units=raw_units,
        windows=tuple(windows),
        tensor_root_hash216=tensor_root,
    )


def build_incidence_evidence(
    manifest: Mapping[str, Any],
    *,
    base_directory: Path,
    frozen_profile_blob_sha1: str,
) -> Mapping[str, Any]:
    normalized = validate_manifest(manifest)
    if frozen_profile_blob_sha1 != FROZEN_PROFILE_GIT_BLOB_SHA1:
        raise Pass215Iteration1ValidationError("PASS215_I1_FROZEN_PROFILE_BLOB_MISMATCH")
    results: list[Mapping[str, Any]] = []
    for tensor in normalized["tensors"]:
        raw = load_tensor_bytes(base_directory, tensor)
        results.append(measure_tensor(tensor, raw).to_dict())
    source_bytes = sum(int(item["source_bytes"]) for item in results)
    tier_1 = sum(int(item["tier_1_bytes"]) for item in results)
    tier_2 = sum(int(item["tier_2_bytes"]) for item in results)
    tier_3 = sum(int(item["tier_3_bytes"]) for item in results)
    admitted = tier_1 + tier_2
    protected = sum(int(item["protected_storage_bytes"]) for item in results)
    if source_bytes <= 0 or protected <= 0 or tier_1 + tier_2 + tier_3 != source_bytes:
        raise Pass215Iteration1ValidationError("PASS215_I1_AGGREGATE_ACCOUNTING_INVALID")
    manifest_root = hash216("pass215-i1-transformer-manifest", canonical_bytes(normalized))
    aggregate = {
        "tensor_count": len(results),
        "source_bytes": source_bytes,
        "full_hydration_window_count": sum(int(item["full_hydration_window_count"]) for item in results),
        "tail_fallback_bytes": sum(int(item["tail_fallback_bytes"]) for item in results),
        "tier_1_bytes": tier_1,
        "tier_2_bytes": tier_2,
        "tier_3_bytes": tier_3,
        "admitted_bytes": admitted,
        "codec_payload_bytes": sum(int(item["codec_payload_bytes"]) for item in results),
        "protected_storage_bytes": protected,
        "generator_seed_units": sum(int(item["generator_seed_units"]) for item in results),
        "exception_units": sum(int(item["exception_units"]) for item in results),
        "raw_fallback_units": sum(int(item["raw_fallback_units"]) for item in results),
        "incidence_fraction_exact": _exact_fraction(admitted, source_bytes),
        "tier_1_fraction_exact": _exact_fraction(tier_1, source_bytes),
        "tier_2_fraction_exact": _exact_fraction(tier_2, source_bytes),
        "tier_3_fraction_exact": _exact_fraction(tier_3, source_bytes),
        "physical_ratio_exact": _exact_fraction(source_bytes, protected),
        "semantic_exactness": True,
    }
    authority = {
        "pass214_main_closure_commit": PASS214_MAIN_CLOSURE_COMMIT,
        "pass214_main_closure_tree": PASS214_MAIN_CLOSURE_TREE,
        "pass214_authority_root_hash216": PASS214_AUTHORITY_ROOT_HASH216,
        "pass215_benchmark_profile_root_hash216": PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
        "pass213_gate_preservation_root_hash216": PASS213_GATE_PRESERVATION_ROOT_HASH216,
        "pass214_terminal_receipt_hash72": PASS214_TERMINAL_RECEIPT_HASH72,
        "frozen_profile_git_blob_sha1": frozen_profile_blob_sha1,
        "benchmark_authority_promoted": True,
        "pass215_authorized": True,
        "pass213_gates_preserved": True,
        "runtime_mutation_authority_promoted": False,
        "canonical_mutation_authorized": False,
        "migration_active": False,
        "pass213_live_admission_required_before_canonical_mutation": True,
    }
    evidence_without_root = {
        "schema": EVIDENCE_SCHEMA,
        "contract": CONTRACT,
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "runtime_classification": RUNTIME_CLASSIFICATION,
        "model_id": normalized["model_id"],
        "manifest_root_hash216": manifest_root,
        "authority": authority,
        "aggregate": aggregate,
        "tensors": results,
        "claim_boundary": {
            "real_open_transformer_measured": False,
            "fifty_billion_desktop_feasibility_claimed": False,
            "dense_forward_replaced": False,
            "exact_nonlinear_transformer_operators_implemented": False,
            "arbitrary_compression_claimed": False,
        },
    }
    evidence_root = hash216(
        "pass215-i1-incidence-evidence",
        canonical_bytes(evidence_without_root),
    )
    receipt = hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION1_INCIDENCE_COMMIT"},
        {"sequence": 1, "parent_hash72": ZERO_HASH72, "evidence_root_hash216": evidence_root},
    )
    evidence = {
        **evidence_without_root,
        "evidence_root_hash216": evidence_root,
        "receipt_hash72": receipt,
    }
    validate_incidence_evidence(evidence)
    return evidence


def validate_incidence_evidence(evidence: Mapping[str, Any]) -> None:
    _reject_floats(evidence)
    if evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("contract") != CONTRACT:
        raise Pass215Iteration1ValidationError("PASS215_I1_EVIDENCE_SCHEMA_INVALID")
    authority = evidence.get("authority")
    if not isinstance(authority, Mapping):
        raise Pass215Iteration1ValidationError("PASS215_I1_AUTHORITY_MISSING")
    expected_authority = {
        "pass214_authority_root_hash216": PASS214_AUTHORITY_ROOT_HASH216,
        "pass215_benchmark_profile_root_hash216": PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
        "pass213_gate_preservation_root_hash216": PASS213_GATE_PRESERVATION_ROOT_HASH216,
        "frozen_profile_git_blob_sha1": FROZEN_PROFILE_GIT_BLOB_SHA1,
    }
    for key, expected in expected_authority.items():
        if authority.get(key) != expected:
            raise Pass215Iteration1ValidationError(f"PASS215_I1_AUTHORITY_BINDING_MISMATCH:{key}")
    if authority.get("benchmark_authority_promoted") is not True or authority.get("pass215_authorized") is not True:
        raise Pass215Iteration1ValidationError("PASS215_I1_BENCHMARK_AUTHORITY_NOT_AUTHORIZED")
    for key in ("runtime_mutation_authority_promoted", "canonical_mutation_authorized", "migration_active"):
        if authority.get(key) is not False:
            raise Pass215Iteration1ValidationError(f"PASS215_I1_MUTATION_BOUNDARY_VIOLATION:{key}")
    aggregate = evidence.get("aggregate")
    tensors = evidence.get("tensors")
    if not isinstance(aggregate, Mapping) or not isinstance(tensors, list) or not tensors:
        raise Pass215Iteration1ValidationError("PASS215_I1_EVIDENCE_CONTENT_INVALID")
    source = sum(int(item["source_bytes"]) for item in tensors)
    tier_1 = sum(int(item["tier_1_bytes"]) for item in tensors)
    tier_2 = sum(int(item["tier_2_bytes"]) for item in tensors)
    tier_3 = sum(int(item["tier_3_bytes"]) for item in tensors)
    if source != int(aggregate["source_bytes"]) or source != tier_1 + tier_2 + tier_3:
        raise Pass215Iteration1ValidationError("PASS215_I1_TIER_ACCOUNTING_MISMATCH")
    if int(aggregate["admitted_bytes"]) != tier_1 + tier_2:
        raise Pass215Iteration1ValidationError("PASS215_I1_ADMITTED_ACCOUNTING_MISMATCH")
    if aggregate.get("semantic_exactness") is not True:
        raise Pass215Iteration1ValidationError("PASS215_I1_SEMANTIC_EXACTNESS_FAILED")
    root_payload = dict(evidence)
    evidence_root = str(root_payload.pop("evidence_root_hash216", ""))
    receipt = str(root_payload.pop("receipt_hash72", ""))
    expected_root = hash216("pass215-i1-incidence-evidence", canonical_bytes(root_payload))
    if evidence_root != expected_root:
        raise Pass215Iteration1ValidationError("PASS215_I1_EVIDENCE_ROOT_MISMATCH")
    expected_receipt = hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION1_INCIDENCE_COMMIT"},
        {"sequence": 1, "parent_hash72": ZERO_HASH72, "evidence_root_hash216": evidence_root},
    )
    if receipt != expected_receipt:
        raise Pass215Iteration1ValidationError("PASS215_I1_RECEIPT_MISMATCH")


def load_manifest(path: Path) -> Mapping[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise Pass215Iteration1ValidationError("PASS215_I1_MANIFEST_TOP_LEVEL_INVALID")
    return validate_manifest(value)


__all__ = [
    "CONTRACT",
    "PASS_NUMBER",
    "ITERATION",
    "CONTRACT_VERSION",
    "RUNTIME_CLASSIFICATION",
    "MANIFEST_SCHEMA",
    "EVIDENCE_SCHEMA",
    "FROZEN_PROFILE_GIT_BLOB_SHA1",
    "TIER_1",
    "TIER_2",
    "TIER_3",
    "Pass215Iteration1Error",
    "Pass215Iteration1ValidationError",
    "TensorIncidence",
    "expected_tensor_bytes",
    "validate_manifest",
    "load_tensor_bytes",
    "measure_tensor",
    "build_incidence_evidence",
    "validate_incidence_evidence",
    "load_manifest",
]
