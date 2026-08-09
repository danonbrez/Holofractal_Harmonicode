"""Pass 215 Iteration 19 content-addressed checkpoint compaction authority.

Iteration 19 preserves the exact bounded-generation semantics frozen by
Iteration 18 while replacing its 475,300,933-byte self-contained JSON
checkpoint representation with a deterministic content-addressed form.

Large checkpoint components are encoded together after lossless repeated-string
interning, split into fixed-size chunks, compressed with deterministic zlib,
and addressed by SHA-256 over the *uncompressed* chunk bytes.  The compact
manifest and blob metadata are additionally Hash216-bound.  Restore verifies
all addresses, reverses interning, reconstructs the original Iteration-18
checkpoint byte-for-byte at the canonical-object level, verifies the frozen
Iteration-18 checkpoint root, and only then invokes the already validated
TerminalHeadSymbolicDAG restore path.  No prompt or generated-token forward
replay is permitted.

Compression is a transport/storage representation only.  It does not become
canonical numerical authority and introduces no floating-point operations.
"""
from __future__ import annotations

import base64
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Sequence
import zlib

from hhs_backend.runtime import hhs_pass215_iteration18_bounded_generation_control_v2 as i18

CONTRACT = "HHS-P215-I19-CONTENT-ADDRESSED-CHECKPOINT-COMPACTION"
PASS_NUMBER = 215
ITERATION = 19
EVIDENCE_SCHEMA = "HHS_PASS_215_ITERATION_19_CONTENT_ADDRESSED_CHECKPOINT_EVIDENCE_V1"
VALIDATION_SCHEMA = "HHS_PASS_215_ITERATION_19_CONTENT_ADDRESSED_CHECKPOINT_VALIDATION_V1"
REPLAY_SCHEMA = "HHS_PASS_215_ITERATION_19_CONTENT_ADDRESSED_CHECKPOINT_REPLAY_V1"
CHECKPOINT_SCHEMA = "HHS_PASS_215_ITERATION_19_CONTENT_ADDRESSED_CHECKPOINT_V1"
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_19_CONTENT_ADDRESSED_CHECKPOINT_BENCHMARK"

ITERATION18_CLOSURE_HEAD = "d89919b1010df0dda46e18cb43b4a6ef913a5615"
ITERATION18_CLOSURE_TREE = "2a74f697278e754b44998df4d5a3598750643a4a"
ITERATION18_CLOSURE_RUN = 31285341551
ITERATION18_CLOSURE_JOB = 93172972694
ITERATION18_CLOSURE_ARTIFACT_ID = 9029742719
ITERATION18_CLOSURE_ARTIFACT_SHA256 = "bf3908e7000a72f96416f469a76415b0a73d48591eaa03d170265aacc7e69297"
ITERATION18_CHECKPOINT_CANONICAL_BYTES = 475300933
ITERATION18_CHECKPOINT_ROOT_HASH216 = "bff3f18e1324caacdbd610b833b3ebd6ebe35e525821c0ffad349fc81ad9474f"
ITERATION18_GENERATION_CONTROL_ROOT_HASH216 = "309a4e102b6f78338a63c086f536f4d3d62429c77709fa4f9fa9b25d3a6ac509"
ITERATION18_SUITE_ROOT_HASH216 = "bccf558e206bc996d4647533cf310838e1f13cec1322f98c5f22ab5c1ad190d1"
ITERATION18_EVIDENCE_ROOT_HASH216 = "b89fd35e60428680ac785fa5637f64a2027e4e5c0a1f17f32b88521c7cfb75f9"
ITERATION18_RECEIPT_HASH72 = "!ZRAyYb(82+PgZuXyX3!zi4J514L3O+!EUr+aX4ID3tIWThWjg!qa+t)(EPnSk1taEz5!mH5"
ITERATION18_TERMINAL_TOKEN_RECEIPT_HASH72 = "cGF-Ca!gMbH75Px9aQG3Qm1)dC)wsS!!2jTWNu!(2BkEeX+Qn3p3/KYB5hGKvgMB(G>t1lfj"
ITERATION18_TOKEN_PROOF_ROOTS = (
    "58005dd4a6308a290a2aecf80d6eb2df34b25eb98fc29bdd0e84d52fc9f2978c",
    "3e5df3e1cfdd1eefc5f1c7baf12282e259640eb6d98020e29d3b6bdecc737603",
    "7dadc585ff4b9ad00de1d65bfd8490366e192c2025bb2b4e5ca189a703c305e1",
    "facaec23d59b2e0dbdd4e0d46f1fabbab6f8a7b014c0eaab08502d48ea409d93",
    "8d1815f573d6d9cb422d0920b001c07a55cac70269ce4197f7ab8965ac83e7cb",
    "e49ca11ba07579f1ce0eba155b8f1f29ea155d637b78e4898243bfcef5ff6089",
    "aeb16bff69406410fc8549853aff7359c7eebdab36003c98758c8c6ab019e608",
)

REAL_MODEL_SHA256 = i18.REAL_MODEL_SHA256
CONTRACTED_PROMPT = i18.CONTRACTED_PROMPT
CERTIFICATION_BITS = i18.CERTIFICATION_BITS
MAX_NEW_TOKENS = i18.MAX_NEW_TOKENS
MAX_CONTEXT_TOKENS = i18.MAX_CONTEXT_TOKENS
RESUME_AFTER_STEPS = i18.RESUME_AFTER_STEPS
FROZEN_SELECTED_TOKEN_IDS = i18.ITERATION17_SELECTED_TOKEN_IDS
FROZEN_SELECTED_TOKENS = i18.ITERATION17_SELECTED_TOKENS

LARGE_COMPONENT_NAMES = (
    "symbolic_dag",
    "symbolic_cache",
    "interval_cache",
    "interval_context",
    "current_interval_logits",
    "current_symbolic_logits",
)
CHUNK_BYTES = 1_048_576
ZLIB_LEVEL = 9
INTERN_MIN_UTF8_BYTES = 16
INTERN_MIN_OCCURRENCES = 2
MIN_REQUIRED_COMPACTION_FACTOR_NUMERATOR = 2


class Pass215Iteration19Error(RuntimeError):
    pass


class Pass215Iteration19ValidationError(Pass215Iteration19Error):
    pass


def _reject_floats(value: Any) -> None:
    try:
        i18.v1._reject_floats(value)
    except i18.Pass215Iteration18ValidationError as exc:
        raise Pass215Iteration19ValidationError(str(exc).replace("PASS215_I18", "PASS215_I19")) from exc


def _json_bytes(value: Any) -> bytes:
    _reject_floats(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _collect_strings(value: Any, counter: Counter[str]) -> None:
    if isinstance(value, str):
        counter[value] += 1
    elif isinstance(value, Mapping):
        for key, child in value.items():
            _collect_strings(str(key), counter)
            _collect_strings(child, counter)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _collect_strings(child, counter)


def _intern_table(components: Mapping[str, Any]) -> tuple[list[str], Counter[str]]:
    counts: Counter[str] = Counter()
    _collect_strings(components, counts)
    table = sorted(
        value for value, count in counts.items()
        if count >= INTERN_MIN_OCCURRENCES and len(value.encode("utf-8")) >= INTERN_MIN_UTF8_BYTES
    )
    return table, counts


def _encode_interned(value: Any, indexes: Mapping[str, int]) -> Any:
    if isinstance(value, str):
        if value in indexes:
            return "$I" + str(indexes[value])
        if value.startswith("$"):
            return "$L" + value
        return value
    if isinstance(value, Mapping):
        return {
            _encode_interned(str(key), indexes): _encode_interned(child, indexes)
            for key, child in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_encode_interned(child, indexes) for child in value]
    return value


def _decode_interned_string(value: str, table: Sequence[str]) -> str:
    if value.startswith("$L"):
        return value[2:]
    if value.startswith("$I") and value[2:].isdigit():
        index = int(value[2:])
        if index < 0 or index >= len(table):
            raise Pass215Iteration19ValidationError("PASS215_I19_STRING_TABLE_INDEX_INVALID")
        return str(table[index])
    return value


def _decode_interned(value: Any, table: Sequence[str]) -> Any:
    if isinstance(value, str):
        return _decode_interned_string(value, table)
    if isinstance(value, Mapping):
        return {
            _decode_interned_string(str(key), table): _decode_interned(child, table)
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [_decode_interned(child, table) for child in value]
    return value


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


def compact_iteration18_checkpoint(checkpoint: Mapping[str, Any]) -> Mapping[str, Any]:
    _reject_floats(checkpoint)
    if checkpoint.get("schema") != i18.CHECKPOINT_SCHEMA or checkpoint.get("contract") != i18.CONTRACT:
        raise Pass215Iteration19ValidationError("PASS215_I19_PARENT_CHECKPOINT_SCHEMA_INVALID")
    parent_root = checkpoint.get("checkpoint_root_hash216")
    if parent_root != ITERATION18_CHECKPOINT_ROOT_HASH216:
        raise Pass215Iteration19ValidationError("PASS215_I19_PARENT_CHECKPOINT_ROOT_CHANGED")

    parent_body = dict(checkpoint)
    parent_body.pop("checkpoint_root_hash216", None)
    expected_parent_root = i18.v1.i17.i4base.hash216(
        "pass215-i18-generation-checkpoint", i18.v1.i17.i4base.canonical_bytes(parent_body)
    )
    if expected_parent_root != parent_root:
        raise Pass215Iteration19ValidationError("PASS215_I19_PARENT_CHECKPOINT_ROOT_INVALID")

    base_fields = dict(parent_body)
    components: dict[str, Any] = {}
    for name in LARGE_COMPONENT_NAMES:
        if name not in base_fields:
            raise Pass215Iteration19ValidationError(f"PASS215_I19_PARENT_COMPONENT_MISSING:{name}")
        components[name] = base_fields.pop(name)

    table, counts = _intern_table(components)
    indexes = {value: index for index, value in enumerate(table)}
    encoded_components = _encode_interned(components, indexes)
    packed_payload = {"string_table": table, "components": encoded_components}
    packed_bytes = _json_bytes(packed_payload)

    chunk_refs: list[str] = []
    blobs: dict[str, Mapping[str, Any]] = {}
    referenced_raw_bytes = 0
    referenced_compressed_bytes = 0
    for offset in range(0, len(packed_bytes), CHUNK_BYTES):
        raw_chunk = packed_bytes[offset:offset + CHUNK_BYTES]
        digest = sha256(raw_chunk).hexdigest()
        compressed = zlib.compress(raw_chunk, level=ZLIB_LEVEL)
        compressed_digest = sha256(compressed).hexdigest()
        chunk_refs.append(digest)
        referenced_raw_bytes += len(raw_chunk)
        referenced_compressed_bytes += len(compressed)
        existing = blobs.get(digest)
        if existing is not None:
            if existing["compressed_sha256"] != compressed_digest:
                raise Pass215Iteration19ValidationError("PASS215_I19_CONTENT_ADDRESS_COLLISION")
            continue
        blobs[digest] = {
            "codec": "zlib-9",
            "raw_bytes": len(raw_chunk),
            "compressed_bytes": len(compressed),
            "compressed_sha256": compressed_digest,
            "data_b64": base64.b64encode(compressed).decode("ascii"),
        }

    interned_occurrences = sum(int(counts[value]) for value in table)
    interned_utf8_bytes_avoided = sum(
        (int(counts[value]) - 1) * len(value.encode("utf-8")) for value in table
    )
    manifest = {
        "chunk_bytes": CHUNK_BYTES,
        "codec": "zlib-9",
        "zlib_level": ZLIB_LEVEL,
        "packed_payload_bytes": len(packed_bytes),
        "packed_payload_sha256": sha256(packed_bytes).hexdigest(),
        "chunk_refs": chunk_refs,
        "referenced_chunk_count": len(chunk_refs),
        "unique_chunk_count": len(blobs),
        "referenced_raw_bytes": referenced_raw_bytes,
        "unique_raw_bytes": sum(int(record["raw_bytes"]) for record in blobs.values()),
        "referenced_compressed_bytes": referenced_compressed_bytes,
        "unique_compressed_bytes": sum(int(record["compressed_bytes"]) for record in blobs.values()),
        "string_table_entries": len(table),
        "interned_occurrences": interned_occurrences,
        "interned_utf8_bytes_avoided": interned_utf8_bytes_avoided,
    }
    store_binding = {"manifest": manifest, "blob_metadata": _blob_metadata(blobs)}
    store_root = i18.v1.i17.i4base.hash216(
        "pass215-i19-content-addressed-checkpoint-store",
        i18.v1.i17.i4base.canonical_bytes(store_binding),
    )
    compact: dict[str, Any] = {
        "schema": CHECKPOINT_SCHEMA,
        "contract": CONTRACT,
        "iteration18_checkpoint_schema": i18.CHECKPOINT_SCHEMA,
        "iteration18_checkpoint_contract": i18.CONTRACT,
        "iteration18_checkpoint_root_hash216": parent_root,
        "file_sha256": checkpoint["file_sha256"],
        "component_names": list(LARGE_COMPONENT_NAMES),
        "base_checkpoint_fields": base_fields,
        "content_store": {"manifest": manifest, "blobs": blobs},
        "content_store_root_hash216": store_root,
    }
    _reject_floats(compact)
    compact["compact_checkpoint_root_hash216"] = i18.v1.i17.i4base.hash216(
        "pass215-i19-content-addressed-checkpoint", i18.v1.i17.i4base.canonical_bytes(compact)
    )
    return compact


def reconstruct_iteration18_checkpoint(compact_checkpoint: Mapping[str, Any]) -> Mapping[str, Any]:
    _reject_floats(compact_checkpoint)
    if compact_checkpoint.get("schema") != CHECKPOINT_SCHEMA or compact_checkpoint.get("contract") != CONTRACT:
        raise Pass215Iteration19ValidationError("PASS215_I19_CHECKPOINT_SCHEMA_INVALID")
    body = dict(compact_checkpoint)
    compact_root = body.pop("compact_checkpoint_root_hash216", None)
    expected_compact_root = i18.v1.i17.i4base.hash216(
        "pass215-i19-content-addressed-checkpoint", i18.v1.i17.i4base.canonical_bytes(body)
    )
    if compact_root != expected_compact_root:
        raise Pass215Iteration19ValidationError("PASS215_I19_COMPACT_CHECKPOINT_ROOT_INVALID")

    store = compact_checkpoint["content_store"]
    manifest = store["manifest"]
    blobs = store["blobs"]
    store_binding = {"manifest": manifest, "blob_metadata": _blob_metadata(blobs)}
    expected_store_root = i18.v1.i17.i4base.hash216(
        "pass215-i19-content-addressed-checkpoint-store",
        i18.v1.i17.i4base.canonical_bytes(store_binding),
    )
    if expected_store_root != compact_checkpoint["content_store_root_hash216"]:
        raise Pass215Iteration19ValidationError("PASS215_I19_CONTENT_STORE_ROOT_INVALID")

    chunks: list[bytes] = []
    for digest in manifest["chunk_refs"]:
        if digest not in blobs:
            raise Pass215Iteration19ValidationError("PASS215_I19_CONTENT_BLOB_MISSING")
        record = blobs[digest]
        compressed = base64.b64decode(record["data_b64"], validate=True)
        if sha256(compressed).hexdigest() != record["compressed_sha256"]:
            raise Pass215Iteration19ValidationError("PASS215_I19_COMPRESSED_BLOB_HASH_INVALID")
        raw_chunk = zlib.decompress(compressed)
        if len(raw_chunk) != int(record["raw_bytes"]):
            raise Pass215Iteration19ValidationError("PASS215_I19_RAW_BLOB_SIZE_INVALID")
        if sha256(raw_chunk).hexdigest() != digest:
            raise Pass215Iteration19ValidationError("PASS215_I19_RAW_BLOB_ADDRESS_INVALID")
        chunks.append(raw_chunk)
    packed_bytes = b"".join(chunks)
    if len(packed_bytes) != int(manifest["packed_payload_bytes"]):
        raise Pass215Iteration19ValidationError("PASS215_I19_PACKED_PAYLOAD_SIZE_INVALID")
    if sha256(packed_bytes).hexdigest() != manifest["packed_payload_sha256"]:
        raise Pass215Iteration19ValidationError("PASS215_I19_PACKED_PAYLOAD_HASH_INVALID")

    packed = json.loads(packed_bytes.decode("utf-8"))
    _reject_floats(packed)
    table = [str(value) for value in packed["string_table"]]
    if len(table) != int(manifest["string_table_entries"]):
        raise Pass215Iteration19ValidationError("PASS215_I19_STRING_TABLE_SIZE_INVALID")
    components = _decode_interned(packed["components"], table)
    if tuple(components) != LARGE_COMPONENT_NAMES:
        raise Pass215Iteration19ValidationError("PASS215_I19_COMPONENT_ORDER_INVALID")

    parent = dict(compact_checkpoint["base_checkpoint_fields"])
    parent.update(components)
    parent["checkpoint_root_hash216"] = compact_checkpoint["iteration18_checkpoint_root_hash216"]
    if parent.get("schema") != i18.CHECKPOINT_SCHEMA or parent.get("contract") != i18.CONTRACT:
        raise Pass215Iteration19ValidationError("PASS215_I19_RECONSTRUCTED_PARENT_SCHEMA_INVALID")
    parent_body = dict(parent)
    parent_root = parent_body.pop("checkpoint_root_hash216")
    expected_parent_root = i18.v1.i17.i4base.hash216(
        "pass215-i18-generation-checkpoint", i18.v1.i17.i4base.canonical_bytes(parent_body)
    )
    if parent_root != expected_parent_root or parent_root != ITERATION18_CHECKPOINT_ROOT_HASH216:
        raise Pass215Iteration19ValidationError("PASS215_I19_RECONSTRUCTED_PARENT_ROOT_INVALID")
    return parent


def restore_compacted_generation_session(raw: bytes, compact_checkpoint: Mapping[str, Any]) -> MutableMapping[str, Any]:
    if sha256(raw).hexdigest() != compact_checkpoint.get("file_sha256"):
        raise Pass215Iteration19ValidationError("PASS215_I19_CHECKPOINT_MODEL_MISMATCH")
    parent = reconstruct_iteration18_checkpoint(compact_checkpoint)
    session = i18.restore_generation_session(raw, parent)
    if session["prefix_forward_replays_after_initialization"] != 0:
        raise Pass215Iteration19ValidationError("PASS215_I19_PREFIX_FORWARD_REPLAY_DURING_RESTORE")
    if session["generated_forward_replays_after_initialization"] != 0:
        raise Pass215Iteration19ValidationError("PASS215_I19_GENERATED_FORWARD_REPLAY_DURING_RESTORE")
    session["content_addressed_restore"] = True
    session["content_store_root_hash216"] = compact_checkpoint["content_store_root_hash216"]
    return session


def _verify_iteration18_semantic_roots(session: Mapping[str, Any], parent_checkpoint_root: str) -> Mapping[str, str]:
    steps = session["steps"]
    proof_roots = [step["proof_root_hash216"] for step in steps]
    if tuple(proof_roots) != ITERATION18_TOKEN_PROOF_ROOTS:
        raise Pass215Iteration19ValidationError("PASS215_I19_ITERATION18_TOKEN_PROOF_ROOTS_CHANGED")
    receipts = [step["proof_receipt_hash72"] for step in steps]
    control_payload = {
        "iteration17_chain_root_hash216": i18.ITERATION17_CHAIN_ROOT_HASH216,
        "checkpoint_root_hash216": parent_checkpoint_root,
        "step_proof_roots": proof_roots,
        "step_receipts": receipts,
        "termination_reason": session["termination_reason"],
        "final_cache_sequence_length": MAX_CONTEXT_TOKENS,
    }
    control_root = i18.v1.i17.i4base.hash216(
        "pass215-i18-bounded-generation-control", i18.v1.i17.i4base.canonical_bytes(control_payload)
    )
    if control_root != ITERATION18_GENERATION_CONTROL_ROOT_HASH216:
        raise Pass215Iteration19ValidationError("PASS215_I19_ITERATION18_CONTROL_ROOT_CHANGED")
    suite_payload = {
        "iteration17_suite_root_hash216": i18.ITERATION17_SUITE_ROOT_HASH216,
        "generation_control_root_hash216": control_root,
        "checkpoint_root_hash216": parent_checkpoint_root,
        "terminal_step_receipt_hash72": session["proof_parent_hash72"],
    }
    suite_root = i18.v1.i17.i4base.hash216(
        "pass215-i18-bounded-generation-control-suite", i18.v1.i17.i4base.canonical_bytes(suite_payload)
    )
    if suite_root != ITERATION18_SUITE_ROOT_HASH216:
        raise Pass215Iteration19ValidationError("PASS215_I19_ITERATION18_SUITE_ROOT_CHANGED")
    if session["proof_parent_hash72"] != ITERATION18_TERMINAL_TOKEN_RECEIPT_HASH72:
        raise Pass215Iteration19ValidationError("PASS215_I19_ITERATION18_TERMINAL_RECEIPT_CHANGED")
    return {"generation_control_root_hash216": control_root, "suite_root_hash216": suite_root}


def execute_content_addressed_checkpoint_benchmark(
    raw: bytes, *, filename: str, source: Mapping[str, Any], prompt: str = CONTRACTED_PROMPT,
    expected_sha256: str | None = None, certification_bits: int = CERTIFICATION_BITS,
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    actual_sha = sha256(raw).hexdigest()
    if expected_sha256 is not None and actual_sha != expected_sha256:
        raise Pass215Iteration19ValidationError("PASS215_I19_SOURCE_SHA256_MISMATCH")
    if source.get("kind") == "public_open_transformer" and actual_sha != REAL_MODEL_SHA256:
        raise Pass215Iteration19ValidationError("PASS215_I19_AUTHENTICATED_MODEL_IDENTITY_MISMATCH")
    if prompt != CONTRACTED_PROMPT or int(certification_bits) != CERTIFICATION_BITS:
        raise Pass215Iteration19ValidationError("PASS215_I19_INPUT_OUTSIDE_CONTRACT")

    policy = i18.v1._policy()
    session = i18.v1._initialize_session(
        raw, filename=filename, source=source, prompt=prompt,
        expected_sha256=expected_sha256, certification_bits=certification_bits, policy=policy,
    )
    while len(session["steps"]) < RESUME_AFTER_STEPS:
        i18.v1._advance_one(session, raw)
    parent_checkpoint = i18.snapshot_generation_session(session)
    if parent_checkpoint["checkpoint_root_hash216"] != ITERATION18_CHECKPOINT_ROOT_HASH216:
        raise Pass215Iteration19ValidationError("PASS215_I19_ITERATION18_CHECKPOINT_NOT_REPRODUCED")
    parent_bytes = len(i18.v1.i17.i4base.canonical_bytes(parent_checkpoint))
    if parent_bytes != ITERATION18_CHECKPOINT_CANONICAL_BYTES:
        raise Pass215Iteration19ValidationError("PASS215_I19_ITERATION18_CHECKPOINT_SIZE_CHANGED")

    compact = compact_iteration18_checkpoint(parent_checkpoint)
    compact_bytes = len(i18.v1.i17.i4base.canonical_bytes(compact))
    if compact_bytes * MIN_REQUIRED_COMPACTION_FACTOR_NUMERATOR > parent_bytes:
        raise Pass215Iteration19ValidationError("PASS215_I19_COMPACTION_FACTOR_BELOW_CONTRACT")
    reconstructed = reconstruct_iteration18_checkpoint(compact)
    reconstructed_bytes = len(i18.v1.i17.i4base.canonical_bytes(reconstructed))
    if reconstructed_bytes != parent_bytes:
        raise Pass215Iteration19ValidationError("PASS215_I19_RECONSTRUCTED_PARENT_SIZE_CHANGED")

    session = restore_compacted_generation_session(raw, compact)
    if session.get("content_addressed_restore") is not True:
        raise Pass215Iteration19ValidationError("PASS215_I19_CONTENT_ADDRESSED_RESTORE_NOT_ACTIVE")
    while not session["terminated"]:
        i18.v1._advance_one(session, raw)
    if len(session["steps"]) != MAX_NEW_TOKENS or session["termination_reason"] != i18.TERMINATION_MAX_NEW_TOKENS:
        raise Pass215Iteration19ValidationError("PASS215_I19_TERMINATION_NOT_CONTRACTED")
    i18.v1._verify_iteration17_final_state(session)
    inherited_roots = _verify_iteration18_semantic_roots(session, parent_checkpoint["checkpoint_root_hash216"])

    manifest = compact["content_store"]["manifest"]
    compaction_payload = {
        "iteration18_checkpoint_root_hash216": ITERATION18_CHECKPOINT_ROOT_HASH216,
        "compact_checkpoint_root_hash216": compact["compact_checkpoint_root_hash216"],
        "content_store_root_hash216": compact["content_store_root_hash216"],
        "iteration18_checkpoint_canonical_bytes": parent_bytes,
        "compact_checkpoint_canonical_bytes": compact_bytes,
        "packed_payload_bytes": int(manifest["packed_payload_bytes"]),
        "unique_compressed_blob_bytes": int(manifest["unique_compressed_bytes"]),
        "string_table_entries": int(manifest["string_table_entries"]),
        "interned_occurrences": int(manifest["interned_occurrences"]),
        "interned_utf8_bytes_avoided": int(manifest["interned_utf8_bytes_avoided"]),
        "restore_prefix_forward_replays": 0,
        "restore_generated_forward_replays": 0,
    }
    compaction_root = i18.v1.i17.i4base.hash216(
        "pass215-i19-checkpoint-compaction", i18.v1.i17.i4base.canonical_bytes(compaction_payload)
    )
    evidence: dict[str, Any] = {
        "schema": EVIDENCE_SCHEMA,
        "contract": CONTRACT,
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "runtime_classification": RUNTIME_CLASSIFICATION,
        "authority": {
            "pass215_benchmark_authority_active": True,
            "content_addressed_checkpoint_authority": True,
            "transport_compression_only": True,
            "no_float_canonical_authority": True,
            "runtime_mutation_authority_promoted": False,
            "canonical_mutation_authorized": False,
            "migration_active": False,
        },
        "inherits": {
            "iteration18_closure_head": ITERATION18_CLOSURE_HEAD,
            "iteration18_closure_tree": ITERATION18_CLOSURE_TREE,
            "iteration18_closure_run": ITERATION18_CLOSURE_RUN,
            "iteration18_closure_job": ITERATION18_CLOSURE_JOB,
            "iteration18_closure_artifact_id": ITERATION18_CLOSURE_ARTIFACT_ID,
            "iteration18_closure_artifact_sha256": ITERATION18_CLOSURE_ARTIFACT_SHA256,
            "iteration18_checkpoint_root_hash216": ITERATION18_CHECKPOINT_ROOT_HASH216,
            "iteration18_generation_control_root_hash216": ITERATION18_GENERATION_CONTROL_ROOT_HASH216,
            "iteration18_suite_root_hash216": ITERATION18_SUITE_ROOT_HASH216,
            "iteration18_evidence_root_hash216": ITERATION18_EVIDENCE_ROOT_HASH216,
            "iteration18_receipt_hash72": ITERATION18_RECEIPT_HASH72,
        },
        "source": {**dict(source), "filename": filename, "file_size_bytes": len(raw), "file_sha256": actual_sha},
        "content_addressed_checkpoint": {
            **compaction_payload,
            "checkpoint_after_completed_steps": RESUME_AFTER_STEPS,
            "chunk_bytes": int(manifest["chunk_bytes"]),
            "referenced_chunk_count": int(manifest["referenced_chunk_count"]),
            "unique_chunk_count": int(manifest["unique_chunk_count"]),
            "unique_raw_blob_bytes": int(manifest["unique_raw_bytes"]),
            "referenced_raw_blob_bytes": int(manifest["referenced_raw_bytes"]),
            "referenced_compressed_blob_bytes": int(manifest["referenced_compressed_bytes"]),
            "compaction_ratio_numerator": parent_bytes,
            "compaction_ratio_denominator": compact_bytes,
            "reconstructed_iteration18_checkpoint_canonical_bytes": reconstructed_bytes,
            "compaction_root_hash216": compaction_root,
        },
        "bounded_generation_control": {
            "completed_steps": len(session["steps"]),
            "selected_token_ids": [int(step["selected_token_id"]) for step in session["steps"]],
            "selected_tokens": [str(step["selected_token"]) for step in session["steps"]],
            "termination_reason": session["termination_reason"],
            "final_cache_sequence_length": MAX_CONTEXT_TOKENS,
            "final_interval_suite_root_hash216": session["current_interval_suite_root"],
            "final_symbolic_dag_root_hash216": session["dag"].manifest()["ordered_node_root_hash216"],
            "terminal_token_receipt_hash72": session["proof_parent_hash72"],
        },
        "iteration18_semantic_reproduction": {
            "exact": True,
            "checkpoint_root_hash216": parent_checkpoint["checkpoint_root_hash216"],
            **inherited_roots,
            "evidence_root_hash216": ITERATION18_EVIDENCE_ROOT_HASH216,
            "receipt_hash72": ITERATION18_RECEIPT_HASH72,
            "selected_token_ids": list(FROZEN_SELECTED_TOKEN_IDS),
            "token_proof_roots": list(ITERATION18_TOKEN_PROOF_ROOTS),
        },
        "claims": {
            "iteration18_checkpoint_root_reconstructed_exactly": True,
            "iteration18_generation_control_root_reproduced_exactly": True,
            "content_addressed_checkpoint_executed": True,
            "repeated_symbolic_strings_interned_losslessly": True,
            "fixed_chunk_sha256_addressing_executed": True,
            "deterministic_zlib_transport_compression_executed": True,
            "compact_checkpoint_at_least_two_times_smaller": True,
            "checkpoint_restored_without_prefix_forward_replay": True,
            "checkpoint_restored_without_generated_forward_replay": True,
            "seven_step_certified_true_greedy_chain_reproduced": True,
            "probabilistic_sampling_executed": False,
            "unbounded_or_general_generation_claimed": False,
            "canonical_float_interpretation_performed": False,
            "dense_forward_replaced": False,
            "runtime_mutation_authority_promoted": False,
            "canonical_mutation_authorized": False,
            "migration_active": False,
        },
    }
    suite_payload = {
        "iteration18_suite_root_hash216": ITERATION18_SUITE_ROOT_HASH216,
        "iteration18_checkpoint_root_hash216": ITERATION18_CHECKPOINT_ROOT_HASH216,
        "compact_checkpoint_root_hash216": compact["compact_checkpoint_root_hash216"],
        "content_store_root_hash216": compact["content_store_root_hash216"],
        "compaction_root_hash216": compaction_root,
        "terminal_token_receipt_hash72": session["proof_parent_hash72"],
    }
    suite_root = i18.v1.i17.i4base.hash216(
        "pass215-i19-content-addressed-checkpoint-suite", i18.v1.i17.i4base.canonical_bytes(suite_payload)
    )
    evidence["content_addressed_checkpoint_suite_root_hash216"] = suite_root
    evidence_root = i18.v1.i17.i4base.hash216(
        "pass215-i19-content-addressed-checkpoint-evidence", i18.v1.i17.i4base.canonical_bytes(evidence)
    )
    evidence["evidence_root_hash216"] = evidence_root
    evidence["receipt_hash72"] = i18.v1.i17.i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION19_CONTENT_ADDRESSED_CHECKPOINT"},
        {"sequence": 19, "parent_hash72": ITERATION18_RECEIPT_HASH72,
         "evidence_root_hash216": evidence_root, "suite_root_hash216": suite_root,
         "compaction_root_hash216": compaction_root},
    )
    _reject_floats(evidence)
    return evidence, compact


def execute_content_addressed_checkpoint_benchmark_from_path(path: str | Path, **kwargs: Any) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    source_path = Path(path)
    return execute_content_addressed_checkpoint_benchmark(source_path.read_bytes(), filename=source_path.name, **kwargs)


def validate_content_addressed_checkpoint_evidence(evidence: Mapping[str, Any]) -> None:
    _reject_floats(evidence)
    if evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("contract") != CONTRACT:
        raise Pass215Iteration19ValidationError("PASS215_I19_SCHEMA_OR_CONTRACT_INVALID")
    compact = evidence.get("content_addressed_checkpoint", {})
    if compact.get("iteration18_checkpoint_root_hash216") != ITERATION18_CHECKPOINT_ROOT_HASH216:
        raise Pass215Iteration19ValidationError("PASS215_I19_PARENT_CHECKPOINT_ROOT_EVIDENCE_INVALID")
    parent_bytes = int(compact.get("iteration18_checkpoint_canonical_bytes", 0))
    compact_bytes = int(compact.get("compact_checkpoint_canonical_bytes", 0))
    if parent_bytes != ITERATION18_CHECKPOINT_CANONICAL_BYTES or compact_bytes <= 0:
        raise Pass215Iteration19ValidationError("PASS215_I19_CHECKPOINT_SIZE_EVIDENCE_INVALID")
    if compact_bytes * MIN_REQUIRED_COMPACTION_FACTOR_NUMERATOR > parent_bytes:
        raise Pass215Iteration19ValidationError("PASS215_I19_COMPACTION_FACTOR_INVALID")
    if int(compact.get("restore_prefix_forward_replays", -1)) != 0 or int(compact.get("restore_generated_forward_replays", -1)) != 0:
        raise Pass215Iteration19ValidationError("PASS215_I19_RESTORE_REPLAY_EVIDENCE_INVALID")
    control = evidence.get("bounded_generation_control", {})
    if tuple(control.get("selected_token_ids", [])) != FROZEN_SELECTED_TOKEN_IDS:
        raise Pass215Iteration19ValidationError("PASS215_I19_SELECTED_TOKEN_CHAIN_INVALID")
    if control.get("termination_reason") != i18.TERMINATION_MAX_NEW_TOKENS:
        raise Pass215Iteration19ValidationError("PASS215_I19_TERMINATION_INVALID")
    inherited = evidence.get("iteration18_semantic_reproduction", {})
    if inherited.get("exact") is not True:
        raise Pass215Iteration19ValidationError("PASS215_I19_ITERATION18_REPRODUCTION_NOT_EXACT")
    if inherited.get("generation_control_root_hash216") != ITERATION18_GENERATION_CONTROL_ROOT_HASH216:
        raise Pass215Iteration19ValidationError("PASS215_I19_ITERATION18_CONTROL_ROOT_EVIDENCE_INVALID")
    if inherited.get("suite_root_hash216") != ITERATION18_SUITE_ROOT_HASH216:
        raise Pass215Iteration19ValidationError("PASS215_I19_ITERATION18_SUITE_ROOT_EVIDENCE_INVALID")
    claims = evidence.get("claims", {})
    for key in (
        "iteration18_checkpoint_root_reconstructed_exactly",
        "content_addressed_checkpoint_executed",
        "repeated_symbolic_strings_interned_losslessly",
        "fixed_chunk_sha256_addressing_executed",
        "compact_checkpoint_at_least_two_times_smaller",
        "checkpoint_restored_without_prefix_forward_replay",
        "checkpoint_restored_without_generated_forward_replay",
    ):
        if claims.get(key) is not True:
            raise Pass215Iteration19ValidationError(f"PASS215_I19_REQUIRED_CLAIM_FALSE:{key}")
    for key in (
        "probabilistic_sampling_executed",
        "unbounded_or_general_generation_claimed",
        "canonical_float_interpretation_performed",
        "dense_forward_replaced",
        "runtime_mutation_authority_promoted",
        "canonical_mutation_authorized",
        "migration_active",
    ):
        if claims.get(key) is not False:
            raise Pass215Iteration19ValidationError(f"PASS215_I19_FORBIDDEN_CLAIM_TRUE:{key}")


def compare_content_addressed_checkpoint_replays(left: Mapping[str, Any], right: Mapping[str, Any]) -> Mapping[str, Any]:
    validate_content_addressed_checkpoint_evidence(left)
    validate_content_addressed_checkpoint_evidence(right)
    keys = (
        "compact_checkpoint_root_hash216",
        "content_store_root_hash216",
        "compaction_root_hash216",
        "compact_checkpoint_canonical_bytes",
    )
    lc = left["content_addressed_checkpoint"]
    rc = right["content_addressed_checkpoint"]
    if any(lc[key] != rc[key] for key in keys):
        raise Pass215Iteration19ValidationError("PASS215_I19_COMPACT_REPLAY_MISMATCH")
    if left["content_addressed_checkpoint_suite_root_hash216"] != right["content_addressed_checkpoint_suite_root_hash216"]:
        raise Pass215Iteration19ValidationError("PASS215_I19_SUITE_REPLAY_MISMATCH")
    if left["evidence_root_hash216"] != right["evidence_root_hash216"] or left["receipt_hash72"] != right["receipt_hash72"]:
        raise Pass215Iteration19ValidationError("PASS215_I19_EVIDENCE_REPLAY_MISMATCH")
    return {
        "schema": REPLAY_SCHEMA,
        "contract": CONTRACT,
        "cross_process_replay": True,
        "semantic_exactness": True,
        "compact_checkpoint_root_hash216": lc["compact_checkpoint_root_hash216"],
        "content_store_root_hash216": lc["content_store_root_hash216"],
        "compaction_root_hash216": lc["compaction_root_hash216"],
        "suite_root_hash216": left["content_addressed_checkpoint_suite_root_hash216"],
        "evidence_root_hash216": left["evidence_root_hash216"],
        "receipt_hash72": left["receipt_hash72"],
    }
