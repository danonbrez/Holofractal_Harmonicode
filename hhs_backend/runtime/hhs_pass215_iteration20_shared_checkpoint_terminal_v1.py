"""Pass 215 Iteration 20 shared-checkpoint terminal closure authority.

Iteration 20 closes the bounded Pass 215 benchmark by extending the validated
Iteration 19 content-addressed checkpoint representation across two sequential
certified-generation checkpoints.  Canonical JSON components are split with a
deterministic content-defined chunker, compressed only for transport, addressed
by SHA-256 over the uncompressed bytes, and stored once in a shared blob store.

Both Iteration 18 checkpoint roots are reconstructed exactly before restore.
The later checkpoint is the exact step-four checkpoint inherited by Iteration
19.  Restore recompiles immutable model bindings but performs no prompt or
generated-token forward replay.  All numerical and selection authority remains
the inherited integer/rational/Hash216 authority; transport compression and
chunk boundaries never become numerical authority.

Pass 216 is a reserved number, not an implementation dependency.  The terminal
handoff therefore names Pass 217 as the next implemented pass while preserving
the reserved boundary explicitly.
"""
from __future__ import annotations

import base64
import binascii
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping, Sequence
import zlib

from hhs_backend.runtime import hhs_pass215_iteration19_content_addressed_checkpoint_v2 as i19

i18 = i19.v1.i18

CONTRACT = "HHS-P215-I20-SHARED-CHECKPOINT-TERMINAL-CLOSURE"
PASS_NUMBER = 215
ITERATION = 20
EVIDENCE_SCHEMA = "HHS_PASS_215_ITERATION_20_SHARED_CHECKPOINT_TERMINAL_EVIDENCE_V1"
VALIDATION_SCHEMA = "HHS_PASS_215_ITERATION_20_SHARED_CHECKPOINT_TERMINAL_VALIDATION_V1"
REPLAY_SCHEMA = "HHS_PASS_215_ITERATION_20_SHARED_CHECKPOINT_TERMINAL_REPLAY_V1"
BUNDLE_SCHEMA = "HHS_PASS_215_ITERATION_20_SHARED_CHECKPOINT_BUNDLE_V1"
MANIFEST_SCHEMA = "HHS_PASS_215_ITERATION_20_SEQUENTIAL_CHECKPOINT_MANIFEST_V1"
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_20_SHARED_CHECKPOINT_TERMINAL_BENCHMARK"

ITERATION19_CLOSURE_HEAD = "04745e6592f2d3bb8f227cc2dec61e25a66145d8"
ITERATION19_CLOSURE_TREE = "4fb5ead812c564b423f7a13155988e5384c53d0e"
ITERATION19_CLOSURE_RUN = 31288268305
ITERATION19_CLOSURE_JOB = 93180913426
ITERATION19_CLOSURE_ARTIFACT_ID = 9030733029
ITERATION19_CLOSURE_ARTIFACT_BYTES = 55246910
ITERATION19_CLOSURE_ARTIFACT_SHA256 = "867159f45a4e22922b858a5ada13bbab25c1a8b400598ebabe5cd6bfcd4106f8"
ITERATION19_COMPACT_CHECKPOINT_ROOT_HASH216 = "e45ffd5dc94d01b4461b65e8d940b53869676ea74e30b9b4f2d83b7d20a85630"
ITERATION19_CONTENT_STORE_ROOT_HASH216 = "a89677a460972945360e1a202b0ba2cf05a96b8a349427d9c03ba7298e043c06"
ITERATION19_COMPACTION_ROOT_HASH216 = "172cc452b779ccd39e693d7d08139015567919511c7fb5e2d11588be907539b3"
ITERATION19_SUITE_ROOT_HASH216 = "99d7efc2c94c0d721658d64a171d615d2f961cb442dd277fca91f78cb9e96e5b"
ITERATION19_EVIDENCE_ROOT_HASH216 = "3d35ca6574aa2dbb5d1b73988dd530cd2445e9d342e229afc40b8e5000323ddc"
ITERATION19_RECEIPT_HASH72 = "aq!(yVgK>!wu2j6D1KWd>tC0l8hgQG*y<NI((gPXvwSFaQBJyGxas7jR1Dg(LEJKhk?tT7Ty"

REAL_MODEL_SHA256 = i19.REAL_MODEL_SHA256
CONTRACTED_PROMPT = i19.CONTRACTED_PROMPT
CERTIFICATION_BITS = i19.CERTIFICATION_BITS
MAX_NEW_TOKENS = i19.MAX_NEW_TOKENS
MAX_CONTEXT_TOKENS = i19.MAX_CONTEXT_TOKENS
FROZEN_SELECTED_TOKEN_IDS = i19.FROZEN_SELECTED_TOKEN_IDS
FROZEN_SELECTED_TOKENS = i19.FROZEN_SELECTED_TOKENS
ITERATION18_STEP4_CHECKPOINT_ROOT_HASH216 = i19.ITERATION18_CHECKPOINT_ROOT_HASH216
ITERATION18_GENERATION_CONTROL_ROOT_HASH216 = i19.ITERATION18_GENERATION_CONTROL_ROOT_HASH216
ITERATION18_SUITE_ROOT_HASH216 = i19.ITERATION18_SUITE_ROOT_HASH216
ITERATION18_TERMINAL_TOKEN_RECEIPT_HASH72 = i19.ITERATION18_TERMINAL_TOKEN_RECEIPT_HASH72

EARLIER_CHECKPOINT_STEPS = 3
LATER_CHECKPOINT_STEPS = 4
COMPONENT_NAMES = tuple(sorted(i19.LARGE_COMPONENT_NAMES))
CHUNK_MIN_BYTES = 262_144
CHUNK_TARGET_BYTES = 1_048_576
CHUNK_MAX_BYTES = 2_097_152
CHUNK_TARGET_MASK = CHUNK_TARGET_BYTES - 1
GEAR_MASK = (1 << 64) - 1
ZLIB_LEVEL = 9

PASS216_STATUS = "RESERVED_NUMBER_NO_PASS"
NEXT_IMPLEMENTED_PASS = 217
OUTPUT_PROJECTION_PRUNING_STATUS = "EVALUATED_NOT_AUTHORIZED"

SOURCE_EARLIER_CHECKPOINT_CANONICAL_BYTES = 413_411_982
SOURCE_LATER_CHECKPOINT_CANONICAL_BYTES = 475_300_933
SOURCE_EARLIER_CHECKPOINT_ROOT_HASH216 = "151113337a143adb29eecfa9cb1f4df41b6458953afb2c5258b97dff5f3643b4"
SOURCE_CHECKPOINT_MANIFEST_ROOTS_HASH216 = (
    "83cbcf30bdc05be09f40936c9ce4cc3e9e36b140bf34a549451cc082742016a0",
    "103f5cb1e412787e68a2f7d4e645a96d9ea54a48861e3adabfe0557e9892c34f",
)
SOURCE_SHARED_CONTENT_STORE_ROOT_HASH216 = "b7a9eb1678f263f20c5b61c0d9d3f01b76b152e2786b7e887ecb8265cbe454da"
SOURCE_SHARED_CHECKPOINT_BUNDLE_ROOT_HASH216 = "14953737a095ee9365386e436706cedd7a77328a04eb4dc3d5e45935cd367c8a"
SOURCE_REUSE_METRICS = {
    "earlier_completed_steps": 3,
    "later_completed_steps": 4,
    "earlier_referenced_chunk_count": 249,
    "later_referenced_chunk_count": 280,
    "earlier_unique_chunk_count": 247,
    "later_unique_chunk_count": 278,
    "reused_unique_chunk_count": 36,
    "incremental_new_unique_chunk_count": 242,
    "shared_store_unique_chunk_count": 489,
    "earlier_standalone_compressed_blob_bytes": 133_299_554,
    "later_standalone_compressed_blob_bytes": 153_886_388,
    "reused_compressed_blob_bytes": 28_375_966,
    "incremental_later_compressed_blob_bytes": 125_510_422,
    "separate_stores_compressed_blob_bytes": 287_185_942,
    "shared_store_compressed_blob_bytes": 258_809_976,
    "shared_store_savings_bytes": 28_375_966,
    "later_incremental_fraction_numerator": 125_510_422,
    "later_incremental_fraction_denominator": 153_886_388,
    "reuse_fraction_numerator": 28_375_966,
    "reuse_fraction_denominator": 153_886_388,
}
SOURCE_SEQUENTIAL_CHECKPOINT_REUSE_ROOT_HASH216 = "52980a2e4b7890d136e549a4812dd859cc75e0ea4f442872dc99392e261ed7c0"
SOURCE_PASS215_TERMINAL_COMPLETION_ROOT_HASH216 = "3dfb034753309c5f45f56f9bec5bf2178b1eb74974264cc306e46c8d6551f76a"
SOURCE_TERMINAL_SUITE_ROOT_HASH216 = "3be955aecac999e945cdf48df63e0be13d2c353de8e20c6869a2364c2ba72234"
SOURCE_EVIDENCE_ROOT_HASH216 = "5a8a17e10b1dc10db2912bc2df40aa67306fc520439716eab47596dc1e8aac1e"
SOURCE_RECEIPT_HASH72 = "rimw6Mf!E(*xCD5DK1/WGTK)*WRAl<RWjBQyi!qSI+rXW>H0L9AtWuu/3Cs5HKZ!B)JCwUTM"


class Pass215Iteration20Error(RuntimeError):
    pass


class Pass215Iteration20ValidationError(Pass215Iteration20Error):
    pass


def _reject_floats(value: Any) -> None:
    try:
        i19.v1._reject_floats(value)
    except i19.Pass215Iteration19ValidationError as exc:
        raise Pass215Iteration20ValidationError(
            str(exc).replace("PASS215_I19", "PASS215_I20")
        ) from exc


def _json_bytes(value: Any) -> bytes:
    _reject_floats(value)
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _hash216(label: str, payload: Mapping[str, Any]) -> str:
    _reject_floats(payload)
    return i18.v1.i17.i4base.hash216(
        label, i18.v1.i17.i4base.canonical_bytes(payload)
    )


GEAR_TABLE = tuple(
    int.from_bytes(
        sha256(b"pass215-i20-content-defined-gear:" + bytes((value,))).digest()[:8],
        "big",
    )
    for value in range(256)
)


def content_defined_chunks(raw: bytes) -> tuple[bytes, ...]:
    """Split bytes deterministically, resynchronizing after inserted regions."""
    if not raw:
        return (b"",)
    chunks: list[bytes] = []
    start = 0
    rolling = 0
    for index, byte in enumerate(raw):
        rolling = ((rolling << 1) + GEAR_TABLE[byte]) & GEAR_MASK
        length = index + 1 - start
        if length < CHUNK_MIN_BYTES:
            continue
        if (rolling & CHUNK_TARGET_MASK) == 0 or length >= CHUNK_MAX_BYTES:
            chunks.append(raw[start:index + 1])
            start = index + 1
            rolling = 0
    if start < len(raw):
        chunks.append(raw[start:])
    return tuple(chunks)


def _chunker_descriptor() -> Mapping[str, Any]:
    return {
        "algorithm": "GEAR64_CONTENT_DEFINED_V1",
        "minimum_bytes": CHUNK_MIN_BYTES,
        "target_bytes": CHUNK_TARGET_BYTES,
        "maximum_bytes": CHUNK_MAX_BYTES,
        "target_mask": CHUNK_TARGET_MASK,
    }


def _blob_metadata(blobs: Mapping[str, Mapping[str, Any]]) -> Mapping[str, Any]:
    return {
        digest: {
            "codec": record["codec"],
            "raw_bytes": int(record["raw_bytes"]),
            "compressed_bytes": int(record["compressed_bytes"]),
            "compressed_sha256": record["compressed_sha256"],
        }
        for digest, record in sorted(blobs.items())
    }


def _decode_validated_blob(
    record: Mapping[str, Any], *, expected_digest: str | None = None
) -> tuple[bytes, bytes]:
    if record.get("codec") != "zlib-9":
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_COMPRESSED_BLOB_CODEC_INVALID"
        )
    encoded = record.get("data_b64")
    if not isinstance(encoded, str):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_COMPRESSED_BLOB_ENCODING_INVALID"
        )
    try:
        compressed = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_COMPRESSED_BLOB_ENCODING_INVALID"
        ) from exc
    if len(compressed) != int(record.get("compressed_bytes", -1)):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_COMPRESSED_BLOB_SIZE_INVALID"
        )
    if sha256(compressed).hexdigest() != record.get("compressed_sha256"):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_COMPRESSED_BLOB_HASH_INVALID"
        )
    raw_bytes = int(record.get("raw_bytes", -1))
    if raw_bytes < 0 or raw_bytes > CHUNK_MAX_BYTES:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_RAW_BLOB_SIZE_INVALID"
        )
    decoder = zlib.decompressobj()
    try:
        raw = decoder.decompress(compressed, raw_bytes + 1)
    except zlib.error as exc:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_COMPRESSED_BLOB_STREAM_INVALID"
        ) from exc
    if len(raw) > raw_bytes or decoder.unconsumed_tail:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_RAW_BLOB_SIZE_INVALID"
        )
    try:
        raw += decoder.flush()
    except zlib.error as exc:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_COMPRESSED_BLOB_STREAM_INVALID"
        ) from exc
    if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_COMPRESSED_BLOB_STREAM_INVALID"
        )
    if len(raw) != raw_bytes:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_RAW_BLOB_SIZE_INVALID"
        )
    if expected_digest is not None and sha256(raw).hexdigest() != expected_digest:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_RAW_BLOB_ADDRESS_INVALID"
        )
    if compressed != zlib.compress(raw, level=ZLIB_LEVEL):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_COMPRESSED_BLOB_CANONICAL_ENCODING_INVALID"
        )
    return compressed, raw


def _validated_compressed_blob(record: Mapping[str, Any]) -> bytes:
    compressed, _ = _decode_validated_blob(record)
    return compressed


def _referenced_digests(manifest: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(
        str(digest)
        for component in manifest["components"]
        for digest in component["chunk_refs"]
    )


def _validate_iteration18_checkpoint(checkpoint: Mapping[str, Any]) -> None:
    _reject_floats(checkpoint)
    if (
        checkpoint.get("schema") != i18.CHECKPOINT_SCHEMA
        or checkpoint.get("contract") != i18.CONTRACT
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_PARENT_CHECKPOINT_SCHEMA_INVALID"
        )
    if int(checkpoint.get("completed_steps", -1)) not in (
        EARLIER_CHECKPOINT_STEPS,
        LATER_CHECKPOINT_STEPS,
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_PARENT_CHECKPOINT_STEP_INVALID"
        )
    body = dict(checkpoint)
    root = body.pop("checkpoint_root_hash216", None)
    expected = _hash216("pass215-i18-generation-checkpoint", body)
    if root != expected:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_PARENT_CHECKPOINT_ROOT_INVALID"
        )


def _encode_checkpoint_manifest(
    checkpoint: Mapping[str, Any],
    shared_blobs: MutableMapping[str, Mapping[str, Any]],
) -> Mapping[str, Any]:
    _validate_iteration18_checkpoint(checkpoint)
    parent_body = dict(checkpoint)
    checkpoint_root = str(parent_body.pop("checkpoint_root_hash216"))
    base_fields = dict(parent_body)
    components: list[Mapping[str, Any]] = []

    for name in COMPONENT_NAMES:
        if name not in base_fields:
            raise Pass215Iteration20ValidationError(
                f"PASS215_I20_PARENT_COMPONENT_MISSING:{name}"
            )
        component_bytes = _json_bytes(base_fields.pop(name))
        chunk_refs: list[str] = []
        referenced_compressed_bytes = 0
        for raw_chunk in content_defined_chunks(component_bytes):
            digest = sha256(raw_chunk).hexdigest()
            compressed = zlib.compress(raw_chunk, level=ZLIB_LEVEL)
            compressed_sha = sha256(compressed).hexdigest()
            record = {
                "codec": "zlib-9",
                "raw_bytes": len(raw_chunk),
                "compressed_bytes": len(compressed),
                "compressed_sha256": compressed_sha,
                "data_b64": base64.b64encode(compressed).decode("ascii"),
            }
            existing = shared_blobs.get(digest)
            if existing is not None:
                if (
                    existing["compressed_sha256"] != compressed_sha
                    or int(existing["raw_bytes"]) != len(raw_chunk)
                ):
                    raise Pass215Iteration20ValidationError(
                        "PASS215_I20_CONTENT_ADDRESS_COLLISION"
                    )
            else:
                shared_blobs[digest] = record
            chunk_refs.append(digest)
            referenced_compressed_bytes += len(compressed)
        components.append(
            {
                "name": name,
                "canonical_bytes": len(component_bytes),
                "canonical_sha256": sha256(component_bytes).hexdigest(),
                "chunk_refs": chunk_refs,
                "referenced_chunk_count": len(chunk_refs),
                "referenced_compressed_bytes": referenced_compressed_bytes,
            }
        )

    referenced = sorted(set(
        digest for component in components for digest in component["chunk_refs"]
    ))
    subset = {digest: shared_blobs[digest] for digest in referenced}
    store_binding = {
        "checkpoint_root_hash216": checkpoint_root,
        "components": components,
        "blob_metadata": _blob_metadata(subset),
    }
    checkpoint_store_root = _hash216(
        "pass215-i20-checkpoint-content-store", store_binding
    )
    manifest: dict[str, Any] = {
        "schema": MANIFEST_SCHEMA,
        "contract": CONTRACT,
        "iteration18_checkpoint_schema": i18.CHECKPOINT_SCHEMA,
        "iteration18_checkpoint_contract": i18.CONTRACT,
        "iteration18_checkpoint_root_hash216": checkpoint_root,
        "completed_steps": int(checkpoint["completed_steps"]),
        "file_sha256": checkpoint["file_sha256"],
        "component_names": list(COMPONENT_NAMES),
        "base_checkpoint_fields": base_fields,
        "chunker": _chunker_descriptor(),
        "transport_codec": "zlib-9",
        "components": components,
        "checkpoint_content_store_root_hash216": checkpoint_store_root,
    }
    manifest["checkpoint_manifest_root_hash216"] = _hash216(
        "pass215-i20-sequential-checkpoint-manifest", manifest
    )
    return manifest


def _reuse_metrics_from_sizes(
    manifests: Sequence[Mapping[str, Any]],
    compressed_sizes: Mapping[str, int],
) -> Mapping[str, Any]:
    if len(manifests) != 2:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_EXACTLY_TWO_CHECKPOINTS_REQUIRED"
        )
    earlier_refs = _referenced_digests(manifests[0])
    later_refs = _referenced_digests(manifests[1])
    earlier_unique = set(earlier_refs)
    later_unique = set(later_refs)
    reused = earlier_unique & later_unique
    incremental = later_unique - earlier_unique
    union = earlier_unique | later_unique

    def compressed_bytes(digests: Iterable[str]) -> int:
        return sum(int(compressed_sizes[digest]) for digest in digests)

    earlier_bytes = compressed_bytes(earlier_unique)
    later_bytes = compressed_bytes(later_unique)
    shared_bytes = compressed_bytes(union)
    reused_bytes = compressed_bytes(reused)
    incremental_bytes = compressed_bytes(incremental)
    separate_bytes = earlier_bytes + later_bytes
    return {
        "earlier_completed_steps": int(manifests[0]["completed_steps"]),
        "later_completed_steps": int(manifests[1]["completed_steps"]),
        "earlier_referenced_chunk_count": len(earlier_refs),
        "later_referenced_chunk_count": len(later_refs),
        "earlier_unique_chunk_count": len(earlier_unique),
        "later_unique_chunk_count": len(later_unique),
        "reused_unique_chunk_count": len(reused),
        "incremental_new_unique_chunk_count": len(incremental),
        "shared_store_unique_chunk_count": len(union),
        "earlier_standalone_compressed_blob_bytes": earlier_bytes,
        "later_standalone_compressed_blob_bytes": later_bytes,
        "reused_compressed_blob_bytes": reused_bytes,
        "incremental_later_compressed_blob_bytes": incremental_bytes,
        "separate_stores_compressed_blob_bytes": separate_bytes,
        "shared_store_compressed_blob_bytes": shared_bytes,
        "shared_store_savings_bytes": separate_bytes - shared_bytes,
        "later_incremental_fraction_numerator": incremental_bytes,
        "later_incremental_fraction_denominator": later_bytes,
        "reuse_fraction_numerator": reused_bytes,
        "reuse_fraction_denominator": later_bytes,
    }


def _reuse_metrics(
    manifests: Sequence[Mapping[str, Any]],
    blobs: Mapping[str, Mapping[str, Any]],
) -> Mapping[str, Any]:
    referenced = {
        digest for manifest in manifests for digest in _referenced_digests(manifest)
    }
    compressed_sizes = {
        digest: len(
            _decode_validated_blob(blobs[digest], expected_digest=digest)[0]
        )
        for digest in referenced
    }
    return _reuse_metrics_from_sizes(manifests, compressed_sizes)


def build_shared_checkpoint_bundle(
    checkpoints: Sequence[Mapping[str, Any]],
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    if len(checkpoints) != 2:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_EXACTLY_TWO_CHECKPOINTS_REQUIRED"
        )
    ordered = sorted(checkpoints, key=lambda value: int(value["completed_steps"]))
    if tuple(int(value["completed_steps"]) for value in ordered) != (
        EARLIER_CHECKPOINT_STEPS,
        LATER_CHECKPOINT_STEPS,
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_CHECKPOINT_SEQUENCE_INVALID"
        )
    shared_blobs: dict[str, Mapping[str, Any]] = {}
    manifests = [
        _encode_checkpoint_manifest(checkpoint, shared_blobs)
        for checkpoint in ordered
    ]
    metrics = _reuse_metrics_from_sizes(
        manifests,
        {
            digest: int(record["compressed_bytes"])
            for digest, record in shared_blobs.items()
        },
    )
    if (
        int(metrics["reused_unique_chunk_count"]) <= 0
        or int(metrics["reused_compressed_blob_bytes"]) <= 0
        or int(metrics["incremental_later_compressed_blob_bytes"])
        >= int(metrics["later_standalone_compressed_blob_bytes"])
        or int(metrics["shared_store_savings_bytes"]) <= 0
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_SHARED_CONTENT_REUSE_NOT_DEMONSTRATED"
        )

    shared_store_binding = {
        "checkpoint_manifest_roots": [
            manifest["checkpoint_manifest_root_hash216"] for manifest in manifests
        ],
        "blob_metadata": _blob_metadata(shared_blobs),
    }
    shared_store_root = _hash216(
        "pass215-i20-shared-checkpoint-content-store", shared_store_binding
    )
    bundle: dict[str, Any] = {
        "schema": BUNDLE_SCHEMA,
        "contract": CONTRACT,
        "checkpoint_manifests": manifests,
        "content_store": {
            "content_address": "SHA256_UNCOMPRESSED_CHUNK_BYTES",
            "transport_codec": "zlib-9",
            "blobs": shared_blobs,
        },
        "reuse_metrics": metrics,
        "shared_content_store_root_hash216": shared_store_root,
    }
    _reject_floats(bundle)
    bundle["shared_checkpoint_bundle_root_hash216"] = _hash216(
        "pass215-i20-shared-checkpoint-bundle", bundle
    )
    return bundle, metrics


def _verify_bundle(
    bundle: Mapping[str, Any],
) -> Mapping[int, Mapping[str, Any]]:
    _reject_floats(bundle)
    if bundle.get("schema") != BUNDLE_SCHEMA or bundle.get("contract") != CONTRACT:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_BUNDLE_SCHEMA_OR_CONTRACT_INVALID"
        )
    content_store = bundle.get("content_store")
    if (
        not isinstance(content_store, Mapping)
        or content_store.get("content_address")
        != "SHA256_UNCOMPRESSED_CHUNK_BYTES"
        or content_store.get("transport_codec") != "zlib-9"
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_CONTENT_STORE_ENCODING_INVALID"
        )
    body = dict(bundle)
    root = body.pop("shared_checkpoint_bundle_root_hash216", None)
    if root != _hash216("pass215-i20-shared-checkpoint-bundle", body):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_SHARED_BUNDLE_ROOT_INVALID"
        )
    manifests = bundle["checkpoint_manifests"]
    if (
        not isinstance(manifests, Sequence)
        or isinstance(manifests, (str, bytes))
        or len(manifests) != 2
        or tuple(int(manifest.get("completed_steps", -1)) for manifest in manifests)
        != (EARLIER_CHECKPOINT_STEPS, LATER_CHECKPOINT_STEPS)
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_CHECKPOINT_SEQUENCE_INVALID"
        )
    for manifest in manifests:
        _validate_checkpoint_manifest(manifest)
    blobs = bundle["content_store"].get("blobs")
    referenced_digests = {
        digest for manifest in manifests for digest in _referenced_digests(manifest)
    }
    if not isinstance(blobs, Mapping) or set(blobs) != referenced_digests:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_CONTENT_STORE_COVERAGE_INVALID"
        )
    shared_binding = {
        "checkpoint_manifest_roots": [
            manifest["checkpoint_manifest_root_hash216"] for manifest in manifests
        ],
        "blob_metadata": _blob_metadata(blobs),
    }
    if bundle["shared_content_store_root_hash216"] != _hash216(
        "pass215-i20-shared-checkpoint-content-store", shared_binding
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_SHARED_CONTENT_STORE_ROOT_INVALID"
        )
    expected_metrics = _reuse_metrics(manifests, blobs)
    if bundle["reuse_metrics"] != expected_metrics:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_REUSE_METRICS_INVALID"
        )
    reconstructed = {
        int(manifest["completed_steps"]): _reconstruct_manifest_checkpoint(
            manifest, blobs
        )
        for manifest in manifests
    }
    return reconstructed


def _validate_manifest_encoding(manifest: Mapping[str, Any]) -> None:
    if (
        manifest.get("chunker") != _chunker_descriptor()
        or manifest.get("transport_codec") != "zlib-9"
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_MANIFEST_ENCODING_INVALID"
        )


def _validate_checkpoint_manifest(manifest: Mapping[str, Any]) -> None:
    if (
        manifest.get("schema") != MANIFEST_SCHEMA
        or manifest.get("contract") != CONTRACT
        or manifest.get("iteration18_checkpoint_schema") != i18.CHECKPOINT_SCHEMA
        or manifest.get("iteration18_checkpoint_contract") != i18.CONTRACT
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_CHECKPOINT_MANIFEST_SCHEMA_INVALID"
        )
    base_fields = manifest.get("base_checkpoint_fields")
    if not isinstance(base_fields, Mapping):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_CHECKPOINT_MANIFEST_BASE_INVALID"
        )
    if (
        int(manifest.get("completed_steps", -1))
        != int(base_fields.get("completed_steps", -2))
        or manifest.get("file_sha256") != base_fields.get("file_sha256")
        or tuple(manifest.get("component_names", ())) != COMPONENT_NAMES
        or tuple(
            component.get("name") for component in manifest.get("components", ())
        )
        != COMPONENT_NAMES
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_CHECKPOINT_MANIFEST_BASE_INVALID"
        )
    _validate_manifest_encoding(manifest)
    manifest_body = dict(manifest)
    manifest_root = manifest_body.pop("checkpoint_manifest_root_hash216", None)
    if manifest_root != _hash216(
        "pass215-i20-sequential-checkpoint-manifest", manifest_body
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_CHECKPOINT_MANIFEST_ROOT_INVALID"
        )


def _decode_manifest_component(
    component: Mapping[str, Any],
    blobs: Mapping[str, Mapping[str, Any]],
) -> bytes:
    chunk_refs = tuple(str(digest) for digest in component["chunk_refs"])
    raw_chunks: list[bytes] = []
    referenced_compressed_bytes = 0
    for digest in chunk_refs:
        record = blobs[digest]
        compressed, raw_chunk = _decode_validated_blob(
            record, expected_digest=digest
        )
        referenced_compressed_bytes += len(compressed)
        raw_chunks.append(raw_chunk)

    raw_component = b"".join(raw_chunks)
    if (
        len(raw_component) != int(component["canonical_bytes"])
        or sha256(raw_component).hexdigest() != component["canonical_sha256"]
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_COMPONENT_IDENTITY_INVALID"
        )

    canonical_chunks = content_defined_chunks(raw_component)
    canonical_refs = tuple(sha256(chunk).hexdigest() for chunk in canonical_chunks)
    if tuple(raw_chunks) != canonical_chunks or chunk_refs != canonical_refs:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_COMPONENT_CHUNK_BOUNDARIES_INVALID"
        )
    if (
        int(component.get("referenced_chunk_count", -1)) != len(canonical_refs)
        or int(component.get("referenced_compressed_bytes", -1))
        != referenced_compressed_bytes
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_COMPONENT_CHUNK_ACCOUNTING_INVALID"
        )
    return raw_component


def _reconstruct_manifest_checkpoint(
    manifest: Mapping[str, Any],
    blobs: Mapping[str, Mapping[str, Any]],
) -> Mapping[str, Any]:
    referenced = sorted(set(_referenced_digests(manifest)))
    subset = {digest: blobs[digest] for digest in referenced if digest in blobs}
    if len(subset) != len(referenced):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_CONTENT_BLOB_MISSING"
        )
    store_binding = {
        "checkpoint_root_hash216": manifest["iteration18_checkpoint_root_hash216"],
        "components": manifest["components"],
        "blob_metadata": _blob_metadata(subset),
    }
    if manifest["checkpoint_content_store_root_hash216"] != _hash216(
        "pass215-i20-checkpoint-content-store", store_binding
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_CHECKPOINT_CONTENT_STORE_ROOT_INVALID"
        )

    components: dict[str, Any] = {}
    for component in manifest["components"]:
        raw_component = _decode_manifest_component(component, blobs)
        components[str(component["name"])] = json.loads(
            raw_component.decode("utf-8")
        )

    parent = dict(manifest["base_checkpoint_fields"])
    parent.update(components)
    parent["checkpoint_root_hash216"] = manifest[
        "iteration18_checkpoint_root_hash216"
    ]
    _validate_iteration18_checkpoint(parent)
    return parent


def reconstruct_iteration18_checkpoints(
    bundle: Mapping[str, Any],
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    reconstructed = _verify_bundle(bundle)
    return (
        reconstructed[EARLIER_CHECKPOINT_STEPS],
        reconstructed[LATER_CHECKPOINT_STEPS],
    )


def reconstruct_iteration18_checkpoint(
    bundle: Mapping[str, Any], completed_steps: int
) -> Mapping[str, Any]:
    completed_steps = int(completed_steps)
    reconstructed = _verify_bundle(bundle)
    if completed_steps not in reconstructed:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_CHECKPOINT_MANIFEST_NOT_UNIQUE"
        )
    return reconstructed[completed_steps]


def _semantic_checkpoint_root(checkpoint: Mapping[str, Any]) -> str:
    body = dict(checkpoint)
    body.pop("checkpoint_root_hash216", None)
    body.pop("resume_count", None)
    return _hash216("pass215-i20-resume-count-neutral-checkpoint-state", body)


def _require_zero_replay(session: Mapping[str, Any], label: str) -> None:
    if (
        int(session["prefix_forward_replays_after_initialization"]) != 0
        or int(session["generated_forward_replays_after_initialization"]) != 0
    ):
        raise Pass215Iteration20ValidationError(
            f"PASS215_I20_FORWARD_REPLAY_DURING_{label}_RESTORE"
        )


def execute_shared_checkpoint_terminal_benchmark(
    raw: bytes,
    *,
    filename: str,
    source: Mapping[str, Any],
    prompt: str = CONTRACTED_PROMPT,
    expected_sha256: str | None = None,
    certification_bits: int = CERTIFICATION_BITS,
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    _reject_floats(source)
    policy = i18.v1._policy()
    session = i18.v1._initialize_session(
        raw,
        filename=filename,
        source=source,
        prompt=prompt,
        expected_sha256=expected_sha256,
        certification_bits=certification_bits,
        policy=policy,
    )
    while len(session["steps"]) < EARLIER_CHECKPOINT_STEPS:
        i18.v1._advance_one(session, raw)
    earlier_checkpoint = i18.v1.snapshot_generation_session(session)
    i18.v1._advance_one(session, raw)
    later_checkpoint = i18.v1.snapshot_generation_session(session)
    if (
        later_checkpoint["checkpoint_root_hash216"]
        != ITERATION18_STEP4_CHECKPOINT_ROOT_HASH216
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_ITERATION19_PARENT_CHECKPOINT_NOT_REPRODUCED"
        )

    bundle, metrics = build_shared_checkpoint_bundle(
        (earlier_checkpoint, later_checkpoint)
    )
    reconstructed_earlier, reconstructed_later = reconstruct_iteration18_checkpoints(
        bundle
    )
    if reconstructed_earlier != earlier_checkpoint:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_EARLIER_CHECKPOINT_RECONSTRUCTION_CHANGED"
        )
    if reconstructed_later != later_checkpoint:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_LATER_CHECKPOINT_RECONSTRUCTION_CHANGED"
        )

    resumed_earlier = i18.restore_generation_session(raw, reconstructed_earlier)
    _require_zero_replay(resumed_earlier, "EARLIER_CHECKPOINT")
    i18.v1._advance_one(resumed_earlier, raw)
    transition_checkpoint = i18.v1.snapshot_generation_session(resumed_earlier)
    if _semantic_checkpoint_root(transition_checkpoint) != _semantic_checkpoint_root(
        later_checkpoint
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_SEQUENTIAL_CHECKPOINT_TRANSITION_CHANGED"
        )

    resumed_later = i18.restore_generation_session(raw, reconstructed_later)
    _require_zero_replay(resumed_later, "LATER_CHECKPOINT")
    while not resumed_later["terminated"]:
        i18.v1._advance_one(resumed_later, raw)
    i18.v1._verify_iteration17_final_state(resumed_later)
    if (
        tuple(int(step["selected_token_id"]) for step in resumed_later["steps"])
        != FROZEN_SELECTED_TOKEN_IDS
        or resumed_later["termination_reason"]
        != i18.TERMINATION_MAX_NEW_TOKENS
        or resumed_later["proof_parent_hash72"]
        != ITERATION18_TERMINAL_TOKEN_RECEIPT_HASH72
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_FROZEN_GENERATION_CHAIN_CHANGED"
        )

    earlier_checkpoint_bytes = len(
        i18.v1.i17.i4base.canonical_bytes(earlier_checkpoint)
    )
    later_checkpoint_bytes = len(
        i18.v1.i17.i4base.canonical_bytes(later_checkpoint)
    )
    reuse_payload = {
        "iteration19_content_store_root_hash216": ITERATION19_CONTENT_STORE_ROOT_HASH216,
        "earlier_checkpoint_root_hash216": earlier_checkpoint["checkpoint_root_hash216"],
        "later_checkpoint_root_hash216": later_checkpoint["checkpoint_root_hash216"],
        "checkpoint_manifest_roots": [
            manifest["checkpoint_manifest_root_hash216"]
            for manifest in bundle["checkpoint_manifests"]
        ],
        "shared_content_store_root_hash216": bundle[
            "shared_content_store_root_hash216"
        ],
        "shared_checkpoint_bundle_root_hash216": bundle[
            "shared_checkpoint_bundle_root_hash216"
        ],
        "reuse_metrics": metrics,
    }
    reuse_root = _hash216(
        "pass215-i20-sequential-checkpoint-reuse", reuse_payload
    )
    pruning_assessment = {
        "status": OUTPUT_PROJECTION_PRUNING_STATUS,
        "complete_vocabulary_candidates": i18.VOCABULARY_SIZE,
        "candidates_pruned": 0,
        "reason": "FULL_VOCABULARY_STRICT_ARGMAX_REQUIRES_ALL_CANDIDATE_INTERVALS_ABSENT_AN_EXACT_EXCLUSION_CERTIFICATE",
        "strict_argmax_authority_preserved": True,
        "canonical_float_authority_introduced": False,
    }
    pass_completion = {
        "pass215_contracted_benchmark_implementation_complete": True,
        "terminal_iteration": ITERATION,
        "implemented_iteration_range": [1, 20],
        "bounded_profile_only": True,
        "broader_generation_authority_promoted": False,
    }
    downstream_transition = {
        "pass216_status": PASS216_STATUS,
        "pass216_implementation_required": False,
        "pass216_execution_required": False,
        "pass216_artifacts_required": False,
        "next_implemented_pass": NEXT_IMPLEMENTED_PASS,
        "pass217_and_pass219_may_consume_pass215_terminal_closure": True,
    }
    completion_root = _hash216(
        "pass215-i20-terminal-completion",
        {
            "reuse_root_hash216": reuse_root,
            "output_projection_pruning_assessment": pruning_assessment,
            "pass_completion": pass_completion,
            "downstream_transition": downstream_transition,
        },
    )

    evidence: dict[str, Any] = {
        "schema": EVIDENCE_SCHEMA,
        "contract": CONTRACT,
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "runtime_classification": RUNTIME_CLASSIFICATION,
        "authority": {
            "pass215_benchmark_authority_active": True,
            "shared_checkpoint_reuse_authority": True,
            "terminal_closure_authority": True,
            "no_float_canonical_authority": True,
            "runtime_mutation_authority_promoted": False,
            "canonical_mutation_authorized": False,
            "migration_active": False,
        },
        "inherits": {
            "iteration19_closure_head": ITERATION19_CLOSURE_HEAD,
            "iteration19_closure_tree": ITERATION19_CLOSURE_TREE,
            "iteration19_closure_run": ITERATION19_CLOSURE_RUN,
            "iteration19_closure_job": ITERATION19_CLOSURE_JOB,
            "iteration19_closure_artifact_id": ITERATION19_CLOSURE_ARTIFACT_ID,
            "iteration19_closure_artifact_sha256": ITERATION19_CLOSURE_ARTIFACT_SHA256,
            "iteration19_compact_checkpoint_root_hash216": ITERATION19_COMPACT_CHECKPOINT_ROOT_HASH216,
            "iteration19_content_store_root_hash216": ITERATION19_CONTENT_STORE_ROOT_HASH216,
            "iteration19_compaction_root_hash216": ITERATION19_COMPACTION_ROOT_HASH216,
            "iteration19_suite_root_hash216": ITERATION19_SUITE_ROOT_HASH216,
            "iteration19_evidence_root_hash216": ITERATION19_EVIDENCE_ROOT_HASH216,
            "iteration19_receipt_hash72": ITERATION19_RECEIPT_HASH72,
        },
        "source": {
            **dict(source),
            "filename": filename,
            "file_size_bytes": len(raw),
            "file_sha256": sha256(raw).hexdigest(),
        },
        "sequential_checkpoints": {
            "earlier_completed_steps": EARLIER_CHECKPOINT_STEPS,
            "later_completed_steps": LATER_CHECKPOINT_STEPS,
            "earlier_checkpoint_canonical_bytes": earlier_checkpoint_bytes,
            "later_checkpoint_canonical_bytes": later_checkpoint_bytes,
            "earlier_checkpoint_root_hash216": earlier_checkpoint[
                "checkpoint_root_hash216"
            ],
            "later_checkpoint_root_hash216": later_checkpoint[
                "checkpoint_root_hash216"
            ],
            "checkpoint_manifest_roots_hash216": [
                manifest["checkpoint_manifest_root_hash216"]
                for manifest in bundle["checkpoint_manifests"]
            ],
            "shared_content_store_root_hash216": bundle[
                "shared_content_store_root_hash216"
            ],
            "shared_checkpoint_bundle_root_hash216": bundle[
                "shared_checkpoint_bundle_root_hash216"
            ],
            "earlier_restore_prefix_forward_replays": 0,
            "earlier_restore_generated_forward_replays": 0,
            "later_restore_prefix_forward_replays": 0,
            "later_restore_generated_forward_replays": 0,
            "resume_count_neutral_transition_exact": True,
            "reuse_metrics": metrics,
            "sequential_checkpoint_reuse_root_hash216": reuse_root,
        },
        "bounded_generation_control": {
            "completed_steps": len(resumed_later["steps"]),
            "selected_token_ids": [
                int(step["selected_token_id"]) for step in resumed_later["steps"]
            ],
            "selected_tokens": [
                str(step["selected_token"]) for step in resumed_later["steps"]
            ],
            "termination_reason": resumed_later["termination_reason"],
            "final_cache_sequence_length": MAX_CONTEXT_TOKENS,
            "terminal_token_receipt_hash72": resumed_later["proof_parent_hash72"],
            "iteration18_generation_control_root_hash216": ITERATION18_GENERATION_CONTROL_ROOT_HASH216,
            "iteration18_suite_root_hash216": ITERATION18_SUITE_ROOT_HASH216,
        },
        "output_projection_pruning_assessment": pruning_assessment,
        "pass_completion": pass_completion,
        "downstream_transition": downstream_transition,
        "claims": {
            "iteration19_closure_inherited_unchanged": True,
            "two_sequential_checkpoints_content_addressed": True,
            "unchanged_chunks_reused_across_generations": True,
            "exact_incremental_checkpoint_bytes_quantified": True,
            "both_iteration18_checkpoint_roots_reconstructed_exactly": True,
            "both_checkpoints_restored_without_prefix_forward_replay": True,
            "both_checkpoints_restored_without_generated_forward_replay": True,
            "seven_step_true_greedy_chain_preserved": True,
            "output_projection_pruning_executed": False,
            "probabilistic_sampling_executed": False,
            "unbounded_or_general_generation_claimed": False,
            "arbitrary_prompt_or_model_generation_claimed": False,
            "canonical_float_interpretation_performed": False,
            "transport_compression_promoted_to_numerical_authority": False,
            "dense_forward_replaced": False,
            "runtime_mutation_authority_promoted": False,
            "canonical_mutation_authorized": False,
            "migration_active": False,
        },
        "pass215_terminal_completion_root_hash216": completion_root,
    }
    suite_payload = {
        "iteration19_suite_root_hash216": ITERATION19_SUITE_ROOT_HASH216,
        "iteration19_evidence_root_hash216": ITERATION19_EVIDENCE_ROOT_HASH216,
        "sequential_checkpoint_reuse_root_hash216": reuse_root,
        "pass215_terminal_completion_root_hash216": completion_root,
        "terminal_token_receipt_hash72": resumed_later["proof_parent_hash72"],
    }
    suite_root = _hash216(
        "pass215-i20-shared-checkpoint-terminal-suite", suite_payload
    )
    evidence["shared_checkpoint_terminal_suite_root_hash216"] = suite_root
    evidence_root = _hash216(
        "pass215-i20-shared-checkpoint-terminal-evidence", evidence
    )
    evidence["evidence_root_hash216"] = evidence_root
    evidence["receipt_hash72"] = i18.v1.i17.i4base.hash72_digest(
        {
            "contract": CONTRACT,
            "event": "PASS215_ITERATION20_SHARED_CHECKPOINT_TERMINAL_CLOSURE",
        },
        {
            "sequence": 20,
            "parent_hash72": ITERATION19_RECEIPT_HASH72,
            "evidence_root_hash216": evidence_root,
            "suite_root_hash216": suite_root,
            "completion_root_hash216": completion_root,
        },
    )
    _reject_floats(evidence)
    return evidence, bundle


def execute_shared_checkpoint_terminal_benchmark_from_path(
    path: str | Path, **kwargs: Any
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    source_path = Path(path)
    return execute_shared_checkpoint_terminal_benchmark(
        source_path.read_bytes(), filename=source_path.name, **kwargs
    )


def validate_shared_checkpoint_terminal_evidence(
    evidence: Mapping[str, Any]
) -> None:
    _reject_floats(evidence)
    if (
        evidence.get("schema") != EVIDENCE_SCHEMA
        or evidence.get("contract") != CONTRACT
        or int(evidence.get("pass", 0)) != PASS_NUMBER
        or int(evidence.get("iteration", 0)) != ITERATION
        or evidence.get("runtime_classification") != RUNTIME_CLASSIFICATION
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_SCHEMA_OR_CONTRACT_INVALID"
        )
    expected_authority = {
        "pass215_benchmark_authority_active": True,
        "shared_checkpoint_reuse_authority": True,
        "terminal_closure_authority": True,
        "no_float_canonical_authority": True,
        "runtime_mutation_authority_promoted": False,
        "canonical_mutation_authorized": False,
        "migration_active": False,
    }
    if evidence.get("authority") != expected_authority:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_AUTHORITY_EVIDENCE_INVALID"
        )
    inherited = evidence.get("inherits", {})
    expected_inherited = {
        "iteration19_closure_head": ITERATION19_CLOSURE_HEAD,
        "iteration19_closure_tree": ITERATION19_CLOSURE_TREE,
        "iteration19_closure_run": ITERATION19_CLOSURE_RUN,
        "iteration19_closure_job": ITERATION19_CLOSURE_JOB,
        "iteration19_closure_artifact_id": ITERATION19_CLOSURE_ARTIFACT_ID,
        "iteration19_closure_artifact_sha256": ITERATION19_CLOSURE_ARTIFACT_SHA256,
        "iteration19_compact_checkpoint_root_hash216": ITERATION19_COMPACT_CHECKPOINT_ROOT_HASH216,
        "iteration19_content_store_root_hash216": ITERATION19_CONTENT_STORE_ROOT_HASH216,
        "iteration19_compaction_root_hash216": ITERATION19_COMPACTION_ROOT_HASH216,
        "iteration19_suite_root_hash216": ITERATION19_SUITE_ROOT_HASH216,
        "iteration19_evidence_root_hash216": ITERATION19_EVIDENCE_ROOT_HASH216,
        "iteration19_receipt_hash72": ITERATION19_RECEIPT_HASH72,
    }
    if inherited != expected_inherited:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_ITERATION19_INHERITANCE_INVALID"
        )
    expected_source = {
        "kind": "public_open_transformer",
        "repo_id": "ggml-org/tiny-llamas",
        "revision": "main",
        "filename": "stories15M-q4_0.gguf",
        "file_size_bytes": 19_077_344,
        "file_sha256": REAL_MODEL_SHA256,
    }
    if evidence.get("source") != expected_source:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_AUTHENTICATED_SOURCE_EVIDENCE_INVALID"
        )
    checkpoints = evidence.get("sequential_checkpoints", {})
    metrics = checkpoints.get("reuse_metrics", {})
    if (
        int(checkpoints.get("earlier_completed_steps", -1))
        != EARLIER_CHECKPOINT_STEPS
        or int(checkpoints.get("later_completed_steps", -1))
        != LATER_CHECKPOINT_STEPS
        or checkpoints.get("later_checkpoint_root_hash216")
        != ITERATION18_STEP4_CHECKPOINT_ROOT_HASH216
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_CHECKPOINT_SEQUENCE_EVIDENCE_INVALID"
        )
    if metrics != SOURCE_REUSE_METRICS:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_REUSE_EVIDENCE_INVALID"
        )
    if (
        int(checkpoints.get("earlier_checkpoint_canonical_bytes", 0))
        != SOURCE_EARLIER_CHECKPOINT_CANONICAL_BYTES
        or int(checkpoints.get("later_checkpoint_canonical_bytes", 0))
        != SOURCE_LATER_CHECKPOINT_CANONICAL_BYTES
        or checkpoints.get("earlier_checkpoint_root_hash216")
        != SOURCE_EARLIER_CHECKPOINT_ROOT_HASH216
        or tuple(checkpoints.get("checkpoint_manifest_roots_hash216", ()))
        != SOURCE_CHECKPOINT_MANIFEST_ROOTS_HASH216
        or checkpoints.get("shared_content_store_root_hash216")
        != SOURCE_SHARED_CONTENT_STORE_ROOT_HASH216
        or checkpoints.get("shared_checkpoint_bundle_root_hash216")
        != SOURCE_SHARED_CHECKPOINT_BUNDLE_ROOT_HASH216
        or checkpoints.get("resume_count_neutral_transition_exact") is not True
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_FROZEN_CHECKPOINT_IDENTITY_INVALID"
        )
    for key in (
        "earlier_restore_prefix_forward_replays",
        "earlier_restore_generated_forward_replays",
        "later_restore_prefix_forward_replays",
        "later_restore_generated_forward_replays",
    ):
        if int(checkpoints.get(key, -1)) != 0:
            raise Pass215Iteration20ValidationError(
                f"PASS215_I20_RESTORE_REPLAY_EVIDENCE_INVALID:{key}"
            )
    reuse_payload = {
        "iteration19_content_store_root_hash216": ITERATION19_CONTENT_STORE_ROOT_HASH216,
        "earlier_checkpoint_root_hash216": checkpoints[
            "earlier_checkpoint_root_hash216"
        ],
        "later_checkpoint_root_hash216": checkpoints[
            "later_checkpoint_root_hash216"
        ],
        "checkpoint_manifest_roots": checkpoints[
            "checkpoint_manifest_roots_hash216"
        ],
        "shared_content_store_root_hash216": checkpoints[
            "shared_content_store_root_hash216"
        ],
        "shared_checkpoint_bundle_root_hash216": checkpoints[
            "shared_checkpoint_bundle_root_hash216"
        ],
        "reuse_metrics": metrics,
    }
    expected_reuse_root = _hash216(
        "pass215-i20-sequential-checkpoint-reuse", reuse_payload
    )
    if (
        checkpoints.get("sequential_checkpoint_reuse_root_hash216")
        != expected_reuse_root
        or expected_reuse_root
        != SOURCE_SEQUENTIAL_CHECKPOINT_REUSE_ROOT_HASH216
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_REUSE_COMMITMENT_INVALID"
        )
    control = evidence.get("bounded_generation_control", {})
    expected_control = {
        "completed_steps": MAX_NEW_TOKENS,
        "selected_token_ids": list(FROZEN_SELECTED_TOKEN_IDS),
        "selected_tokens": list(FROZEN_SELECTED_TOKENS),
        "termination_reason": i18.TERMINATION_MAX_NEW_TOKENS,
        "final_cache_sequence_length": MAX_CONTEXT_TOKENS,
        "terminal_token_receipt_hash72": ITERATION18_TERMINAL_TOKEN_RECEIPT_HASH72,
        "iteration18_generation_control_root_hash216": ITERATION18_GENERATION_CONTROL_ROOT_HASH216,
        "iteration18_suite_root_hash216": ITERATION18_SUITE_ROOT_HASH216,
    }
    if control != expected_control:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_GENERATION_CONTROL_EVIDENCE_INVALID"
        )
    pruning = evidence.get("output_projection_pruning_assessment", {})
    expected_pruning = {
        "status": OUTPUT_PROJECTION_PRUNING_STATUS,
        "complete_vocabulary_candidates": i18.VOCABULARY_SIZE,
        "candidates_pruned": 0,
        "reason": "FULL_VOCABULARY_STRICT_ARGMAX_REQUIRES_ALL_CANDIDATE_INTERVALS_ABSENT_AN_EXACT_EXCLUSION_CERTIFICATE",
        "strict_argmax_authority_preserved": True,
        "canonical_float_authority_introduced": False,
    }
    if pruning != expected_pruning:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_OUTPUT_PROJECTION_ASSESSMENT_INVALID"
        )
    completion = evidence.get("pass_completion", {})
    transition = evidence.get("downstream_transition", {})
    expected_completion = {
        "pass215_contracted_benchmark_implementation_complete": True,
        "terminal_iteration": ITERATION,
        "implemented_iteration_range": [1, 20],
        "bounded_profile_only": True,
        "broader_generation_authority_promoted": False,
    }
    expected_transition = {
        "pass216_status": PASS216_STATUS,
        "pass216_implementation_required": False,
        "pass216_execution_required": False,
        "pass216_artifacts_required": False,
        "next_implemented_pass": NEXT_IMPLEMENTED_PASS,
        "pass217_and_pass219_may_consume_pass215_terminal_closure": True,
    }
    if completion != expected_completion or transition != expected_transition:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_TERMINAL_HANDOFF_INVALID"
        )
    claims = evidence.get("claims", {})
    expected_claims = {
        "iteration19_closure_inherited_unchanged": True,
        "two_sequential_checkpoints_content_addressed": True,
        "unchanged_chunks_reused_across_generations": True,
        "exact_incremental_checkpoint_bytes_quantified": True,
        "both_iteration18_checkpoint_roots_reconstructed_exactly": True,
        "both_checkpoints_restored_without_prefix_forward_replay": True,
        "both_checkpoints_restored_without_generated_forward_replay": True,
        "seven_step_true_greedy_chain_preserved": True,
        "output_projection_pruning_executed": False,
        "probabilistic_sampling_executed": False,
        "unbounded_or_general_generation_claimed": False,
        "arbitrary_prompt_or_model_generation_claimed": False,
        "canonical_float_interpretation_performed": False,
        "transport_compression_promoted_to_numerical_authority": False,
        "dense_forward_replaced": False,
        "runtime_mutation_authority_promoted": False,
        "canonical_mutation_authorized": False,
        "migration_active": False,
    }
    if claims != expected_claims:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_CLAIM_SET_INVALID"
        )

    expected_completion_root = _hash216(
        "pass215-i20-terminal-completion",
        {
            "reuse_root_hash216": expected_reuse_root,
            "output_projection_pruning_assessment": pruning,
            "pass_completion": completion,
            "downstream_transition": transition,
        },
    )
    if (
        evidence.get("pass215_terminal_completion_root_hash216")
        != expected_completion_root
        or expected_completion_root
        != SOURCE_PASS215_TERMINAL_COMPLETION_ROOT_HASH216
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_COMPLETION_COMMITMENT_INVALID"
        )
    expected_suite_root = _hash216(
        "pass215-i20-shared-checkpoint-terminal-suite",
        {
            "iteration19_suite_root_hash216": ITERATION19_SUITE_ROOT_HASH216,
            "iteration19_evidence_root_hash216": ITERATION19_EVIDENCE_ROOT_HASH216,
            "sequential_checkpoint_reuse_root_hash216": expected_reuse_root,
            "pass215_terminal_completion_root_hash216": expected_completion_root,
            "terminal_token_receipt_hash72": control[
                "terminal_token_receipt_hash72"
            ],
        },
    )
    if (
        evidence.get("shared_checkpoint_terminal_suite_root_hash216")
        != expected_suite_root
        or expected_suite_root != SOURCE_TERMINAL_SUITE_ROOT_HASH216
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_SUITE_COMMITMENT_INVALID"
        )
    evidence_body = dict(evidence)
    claimed_receipt = evidence_body.pop("receipt_hash72", None)
    claimed_evidence_root = evidence_body.pop("evidence_root_hash216", None)
    expected_evidence_root = _hash216(
        "pass215-i20-shared-checkpoint-terminal-evidence", evidence_body
    )
    if (
        claimed_evidence_root != expected_evidence_root
        or expected_evidence_root != SOURCE_EVIDENCE_ROOT_HASH216
    ):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_EVIDENCE_COMMITMENT_INVALID"
        )
    expected_receipt = i18.v1.i17.i4base.hash72_digest(
        {
            "contract": CONTRACT,
            "event": "PASS215_ITERATION20_SHARED_CHECKPOINT_TERMINAL_CLOSURE",
        },
        {
            "sequence": 20,
            "parent_hash72": ITERATION19_RECEIPT_HASH72,
            "evidence_root_hash216": expected_evidence_root,
            "suite_root_hash216": expected_suite_root,
            "completion_root_hash216": expected_completion_root,
        },
    )
    if claimed_receipt != expected_receipt or expected_receipt != SOURCE_RECEIPT_HASH72:
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_RECEIPT_COMMITMENT_INVALID"
        )


def compare_shared_checkpoint_terminal_replays(
    left: Mapping[str, Any], right: Mapping[str, Any]
) -> Mapping[str, Any]:
    validate_shared_checkpoint_terminal_evidence(left)
    validate_shared_checkpoint_terminal_evidence(right)
    keys = (
        "pass215_terminal_completion_root_hash216",
        "shared_checkpoint_terminal_suite_root_hash216",
        "evidence_root_hash216",
        "receipt_hash72",
    )
    if any(left.get(key) != right.get(key) for key in keys):
        raise Pass215Iteration20ValidationError(
            "PASS215_I20_TOP_LEVEL_REPLAY_MISMATCH"
        )
    left_checkpoints = left["sequential_checkpoints"]
    right_checkpoints = right["sequential_checkpoints"]
    for key in (
        "earlier_checkpoint_root_hash216",
        "later_checkpoint_root_hash216",
        "checkpoint_manifest_roots_hash216",
        "shared_content_store_root_hash216",
        "shared_checkpoint_bundle_root_hash216",
        "reuse_metrics",
        "sequential_checkpoint_reuse_root_hash216",
    ):
        if left_checkpoints.get(key) != right_checkpoints.get(key):
            raise Pass215Iteration20ValidationError(
                f"PASS215_I20_CHECKPOINT_REPLAY_MISMATCH:{key}"
            )
    return {
        "schema": REPLAY_SCHEMA,
        "contract": CONTRACT,
        "cross_process_replay": True,
        "semantic_exactness": True,
        "shared_content_store_root_hash216": left_checkpoints[
            "shared_content_store_root_hash216"
        ],
        "shared_checkpoint_bundle_root_hash216": left_checkpoints[
            "shared_checkpoint_bundle_root_hash216"
        ],
        "sequential_checkpoint_reuse_root_hash216": left_checkpoints[
            "sequential_checkpoint_reuse_root_hash216"
        ],
        "pass215_terminal_completion_root_hash216": left[
            "pass215_terminal_completion_root_hash216"
        ],
        "suite_root_hash216": left[
            "shared_checkpoint_terminal_suite_root_hash216"
        ],
        "evidence_root_hash216": left["evidence_root_hash216"],
        "receipt_hash72": left["receipt_hash72"],
        "pass216_status": PASS216_STATUS,
        "next_implemented_pass": NEXT_IMPLEMENTED_PASS,
    }
