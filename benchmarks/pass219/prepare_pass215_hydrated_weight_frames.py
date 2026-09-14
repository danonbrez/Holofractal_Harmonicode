#!/usr/bin/env python3
"""Prepare exact VM81 workload frames from the validated Pass-215 I20 content store.

Every referenced hydrated-checkpoint chunk is address-verified and decoded through
Pass 215 Iteration 20.  Four candidate-only VM81 views are emitted per reference:

* SUMMARY: all raw chunk bytes feed one domain-separated SHA-512 root, expanded
  deterministically to exactly 648 bytes;
* HEAD/MIDDLE/TAIL: exact 648-byte local slices of the decoded chunk.

The summary is intentionally a many-to-one hydration projection, not a lossless
replacement for the source checkpoint.  The source content-address and Pass-215
checkpoint roots remain in every record's transition provenance.
"""
from __future__ import annotations

import argparse
from hashlib import sha256, sha512
import json
from pathlib import Path
import struct
from typing import Any, Mapping

from hhs_backend.runtime import hhs_pass215_iteration20_shared_checkpoint_terminal_v1 as i20

SCHEMA = "HHS_PASS219_PHASE3_PASS215_HYDRATED_WEIGHT_FRAMES_V1"
MAGIC = b"HHS3WGT1"
VERSION = 1
FRAME_BYTES = 648
FRAME_KINDS = ("SUMMARY", "HEAD", "MIDDLE", "TAIL")
HASH72_ALPHABET = b"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?"
EXPECTED_SOURCE_SHA256 = "6151b1929d7f5aa3385d9ddef3393e55587c0a55de661562322bc51dfda93a04"
EXPECTED_EARLIER_ROOT = "151113337a143adb29eecfa9cb1f4df41b6458953afb2c5258b97dff5f3643b4"
EXPECTED_LATER_ROOT = "bff3f18e1324caacdbd610b833b3ebd6ebe35e525821c0ffad349fc81ad9474f"
EXPECTED_SHARED_STORE_ROOT = "b7a9eb1678f263f20c5b61c0d9d3f01b76b152e2786b7e887ecb8265cbe454da"
EXPECTED_BUNDLE_ROOT = "14953737a095ee9365386e436706cedd7a77328a04eb4dc3d5e45935cd367c8a"


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _hash72(material: bytes, label: bytes, length: int) -> str:
    out = bytearray()
    counter = 0
    while len(out) < length:
        block = sha256(
            b"HHS-P219-P3-HASH72-V1\x00" + label + b"\x00" + material + counter.to_bytes(4, "little")
        ).digest()
        out.extend(HASH72_ALPHABET[value % len(HASH72_ALPHABET)] for value in block)
        counter += 1
    return bytes(out[:length]).decode("ascii")


def _summary_frame(raw: bytes) -> bytes:
    root = sha512(b"HHS-P219-P3-ALL-CHUNK-BYTES-V1\x00" + raw).digest()
    out = bytearray()
    counter = 0
    while len(out) < FRAME_BYTES:
        out.extend(
            sha512(
                b"HHS-P219-P3-VM81-EXPAND-V1\x00"
                + root
                + counter.to_bytes(4, "little")
            ).digest()
        )
        counter += 1
    return bytes(out[:FRAME_BYTES])


def _slice_frame(raw: bytes, kind: str) -> bytes:
    if kind == "HEAD":
        start = 0
    elif kind == "MIDDLE":
        start = max(0, (len(raw) - FRAME_BYTES) // 2)
    elif kind == "TAIL":
        start = max(0, len(raw) - FRAME_BYTES)
    else:
        raise ValueError(kind)
    view = raw[start : start + FRAME_BYTES]
    return view + bytes(FRAME_BYTES - len(view))


def _frame_for_kind(raw: bytes, kind: str) -> bytes:
    return _summary_frame(raw) if kind == "SUMMARY" else _slice_frame(raw, kind)


def _transition_fields(
    *,
    checkpoint_root: str,
    manifest_root: str,
    chunk_digest: str,
    frame_kind: str,
    frame: bytes,
) -> tuple[str, str, str, str]:
    frame_digest = sha256(frame).hexdigest()
    base = (
        checkpoint_root.encode("ascii")
        + b"\x00"
        + manifest_root.encode("ascii")
        + b"\x00"
        + chunk_digest.encode("ascii")
        + b"\x00"
        + frame_kind.encode("ascii")
    )
    previous = _hash72(checkpoint_root.encode("ascii"), b"previous", 72)
    change = _hash72(chunk_digest.encode("ascii") + frame_kind.encode("ascii"), b"change", 72)
    receipt = _hash72(frame_digest.encode("ascii") + manifest_root.encode("ascii"), b"receipt", 72)
    identity = _hash72(base + frame_digest.encode("ascii"), b"identity216", 216)
    return previous, change, receipt, identity


def _c_string(value: str, width: int) -> bytes:
    raw = value.encode("ascii")
    if len(raw) + 1 != width:
        raise ValueError((len(raw), width))
    return raw + b"\x00"


def _validate_evidence_and_bundle(evidence: Mapping[str, Any], bundle: Mapping[str, Any]) -> None:
    i20.validate_shared_checkpoint_terminal_evidence(evidence)
    checkpoints = evidence["sequential_checkpoints"]
    if evidence["source"]["file_sha256"] != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("PASS219_P3_PASS215_SOURCE_SHA256_CHANGED")
    if checkpoints["earlier_checkpoint_root_hash216"] != EXPECTED_EARLIER_ROOT:
        raise RuntimeError("PASS219_P3_PASS215_EARLIER_ROOT_CHANGED")
    if checkpoints["later_checkpoint_root_hash216"] != EXPECTED_LATER_ROOT:
        raise RuntimeError("PASS219_P3_PASS215_LATER_ROOT_CHANGED")
    if checkpoints["shared_content_store_root_hash216"] != EXPECTED_SHARED_STORE_ROOT:
        raise RuntimeError("PASS219_P3_PASS215_SHARED_STORE_ROOT_CHANGED")
    if checkpoints["shared_checkpoint_bundle_root_hash216"] != EXPECTED_BUNDLE_ROOT:
        raise RuntimeError("PASS219_P3_PASS215_BUNDLE_ROOT_CHANGED")
    if bundle.get("shared_content_store_root_hash216") != EXPECTED_SHARED_STORE_ROOT:
        raise RuntimeError("PASS219_P3_BUNDLE_SHARED_STORE_ROOT_CHANGED")
    if bundle.get("shared_checkpoint_bundle_root_hash216") != EXPECTED_BUNDLE_ROOT:
        raise RuntimeError("PASS219_P3_BUNDLE_ROOT_CHANGED")
    manifests = bundle.get("checkpoint_manifests")
    if not isinstance(manifests, list) or len(manifests) != 2:
        raise RuntimeError("PASS219_P3_EXACTLY_TWO_CHECKPOINTS_REQUIRED")
    expected_roots = [EXPECTED_EARLIER_ROOT, EXPECTED_LATER_ROOT]
    if [m.get("iteration18_checkpoint_root_hash216") for m in manifests] != expected_roots:
        raise RuntimeError("PASS219_P3_CHECKPOINT_SEQUENCE_CHANGED")
    if [m.get("checkpoint_manifest_root_hash216") for m in manifests] != list(
        checkpoints["checkpoint_manifest_roots_hash216"]
    ):
        raise RuntimeError("PASS219_P3_MANIFEST_ROOTS_CHANGED")
    for manifest in manifests:
        i20._validate_checkpoint_manifest(manifest)


def prepare(bundle_path: Path, evidence_path: Path, output_bin: Path, output_meta: Path) -> Mapping[str, Any]:
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    _validate_evidence_and_bundle(evidence, bundle)

    manifests = bundle["checkpoint_manifests"]
    blobs = bundle["content_store"]["blobs"]
    total_references = sum(
        int(component["referenced_chunk_count"])
        for manifest in manifests
        for component in manifest["components"]
    )
    record_count = total_references * len(FRAME_KINDS)

    output_bin.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_rows: list[dict[str, Any]] = []
    unique_by_checkpoint: list[set[str]] = []
    reference_ordinal = 0
    with output_bin.open("wb") as handle:
        handle.write(MAGIC)
        handle.write(struct.pack("<IIII", VERSION, record_count, len(manifests), len(FRAME_KINDS)))

        for checkpoint_slot, manifest in enumerate(manifests):
            checkpoint_root = str(manifest["iteration18_checkpoint_root_hash216"])
            manifest_root = str(manifest["checkpoint_manifest_root_hash216"])
            unique: set[str] = set()
            referenced_raw_bytes = 0
            per_component: list[dict[str, Any]] = []
            for component_index, component in enumerate(manifest["components"]):
                component_refs = list(component["chunk_refs"])
                component_raw_bytes = 0
                for chunk_ordinal, chunk_digest in enumerate(component_refs):
                    record = blobs[str(chunk_digest)]
                    _compressed, raw = i20._decode_validated_blob(record, expected_digest=str(chunk_digest))
                    unique.add(str(chunk_digest))
                    referenced_raw_bytes += len(raw)
                    component_raw_bytes += len(raw)
                    for frame_kind_id, frame_kind in enumerate(FRAME_KINDS):
                        frame = _frame_for_kind(raw, frame_kind)
                        previous, change, receipt, identity = _transition_fields(
                            checkpoint_root=checkpoint_root,
                            manifest_root=manifest_root,
                            chunk_digest=str(chunk_digest),
                            frame_kind=frame_kind,
                            frame=frame,
                        )
                        handle.write(
                            struct.pack(
                                "<BBBBIII",
                                checkpoint_slot,
                                frame_kind_id,
                                component_index,
                                0,
                                chunk_ordinal,
                                reference_ordinal,
                                len(raw),
                            )
                        )
                        handle.write(str(chunk_digest).encode("ascii"))
                        handle.write(checkpoint_root.encode("ascii"))
                        handle.write(_c_string(previous, 73))
                        handle.write(_c_string(change, 73))
                        handle.write(_c_string(receipt, 73))
                        handle.write(_c_string(identity, 217))
                        handle.write(frame)
                    reference_ordinal += 1
                if component_raw_bytes != int(component["canonical_bytes"]):
                    raise RuntimeError(
                        f"PASS219_P3_COMPONENT_BYTE_ACCOUNTING_CHANGED:{component['name']}"
                    )
                per_component.append(
                    {
                        "name": component["name"],
                        "canonical_bytes": int(component["canonical_bytes"]),
                        "referenced_chunk_count": len(component_refs),
                    }
                )
            unique_by_checkpoint.append(unique)
            checkpoint_rows.append(
                {
                    "checkpoint_slot": checkpoint_slot,
                    "completed_steps": int(manifest["completed_steps"]),
                    "checkpoint_root_hash216": checkpoint_root,
                    "checkpoint_manifest_root_hash216": manifest_root,
                    "referenced_chunk_count": sum(row["referenced_chunk_count"] for row in per_component),
                    "unique_chunk_count": len(unique),
                    "referenced_raw_chunk_bytes": referenced_raw_bytes,
                    "components": per_component,
                }
            )

    if reference_ordinal != total_references:
        raise RuntimeError("PASS219_P3_REFERENCE_COUNT_MISMATCH")
    union = unique_by_checkpoint[0] | unique_by_checkpoint[1]
    reused = unique_by_checkpoint[0] & unique_by_checkpoint[1]
    incremental = unique_by_checkpoint[1] - unique_by_checkpoint[0]
    binary_sha = sha256(output_bin.read_bytes()).hexdigest()
    meta = {
        "schema": SCHEMA,
        "version": VERSION,
        "source_model_sha256": EXPECTED_SOURCE_SHA256,
        "shared_content_store_root_hash216": EXPECTED_SHARED_STORE_ROOT,
        "shared_checkpoint_bundle_root_hash216": EXPECTED_BUNDLE_ROOT,
        "frame_bytes": FRAME_BYTES,
        "frame_kinds": list(FRAME_KINDS),
        "total_chunk_references": total_references,
        "total_frame_records": record_count,
        "shared_store_unique_chunk_count": len(union),
        "reused_unique_chunk_count": len(reused),
        "later_incremental_unique_chunk_count": len(incremental),
        "all_raw_chunk_bytes_feed_summary_frame": True,
        "local_exact_raw_segments_per_reference": 3,
        "summary_projection_is_bijective": False,
        "canonical_authority_promoted": False,
        "checkpoints": checkpoint_rows,
        "binary_path": output_bin.name,
        "binary_sha256": binary_sha,
    }
    if len(union) != int(bundle["reuse_metrics"]["shared_store_unique_chunk_count"]):
        raise RuntimeError("PASS219_P3_SHARED_UNIQUE_COUNT_CHANGED")
    if len(reused) != int(bundle["reuse_metrics"]["reused_unique_chunk_count"]):
        raise RuntimeError("PASS219_P3_REUSED_COUNT_CHANGED")
    if len(incremental) != int(bundle["reuse_metrics"]["incremental_new_unique_chunk_count"]):
        raise RuntimeError("PASS219_P3_INCREMENTAL_COUNT_CHANGED")
    _write_json(output_meta, meta)
    return meta


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output-bin", type=Path, required=True)
    parser.add_argument("--output-meta", type=Path, required=True)
    args = parser.parse_args()
    meta = prepare(args.bundle, args.evidence, args.output_bin, args.output_meta)
    print(json.dumps(meta, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
