#!/usr/bin/env python3
"""Generate or verify deterministic Pass 210 HFC completion evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass210_holographic_frame_compression_v1 import (  # noqa: E402
    CONTRACT,
    CONTRACT_CLASSIFICATION,
    REGISTER_LEN,
    RUNTIME_CLASSIFICATION,
    HolographicFrameCompressionRuntime,
    affine_fibonacci_mod2,
    audit_invariants,
    hfc_section,
)

OUTPUT = ROOT / "evidence" / "pass210" / "PASS_210_HFC_REFERENCE_VECTORS.json"
MODALITIES = ("raw", "hash72", "hash216", "phase", "frame")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def corpus() -> dict[str, bytes]:
    rng = random.Random(210)
    return {
        "all_zeros": bytes([0]) * REGISTER_LEN,
        "all_ones": bytes([1]) * REGISTER_LEN,
        "alternating": bytes(index & 1 for index in range(REGISTER_LEN)),
        "prng_seed_210": bytes(rng.randrange(2) for _ in range(REGISTER_LEN)),
    }


def generate() -> dict[str, Any]:
    runtime = HolographicFrameCompressionRuntime()
    vectors: dict[str, Any] = {}
    frames = {}
    for name, raw in corpus().items():
        frame = runtime.frame_encode(raw)
        decoded = runtime.frame_decode(frame)
        if decoded != raw:
            raise RuntimeError(f"round-trip failure for {name}")
        frames[name] = frame
        vectors[name] = {
            "register_sha256": sha256(raw),
            "register_hash216": frame.object_hash216,
            "frame_receipt_hash72": frame.receipt_hash72,
            "snapshot_sha256": [sha256(frame.snapshot_bytes(index)) for index in range(36)],
            "section_audit": all(
                tuple(map(len, hfc_section(frame.snapshot_bytes(index)))) == (89, 55, 89, 55)
                for index in range(36)
            ),
        }

    reference_name = "prng_seed_210"
    reference = corpus()[reference_name]
    reference_frame = frames[reference_name]
    erasures = []
    for lost_index in range(36):
        recovered = runtime.recover(reference_frame, lost_index)
        if recovered != reference:
            raise RuntimeError(f"erasure recovery failure at {lost_index}")
        erasures.append({
            "lost_index": lost_index,
            "witnessing_snapshots": [(lost_index - 1) % 36, (lost_index + 1) % 36],
            "recovered_sha256": sha256(recovered),
            "receipt_hash72": runtime.ledger.head,
        })

    clean = [runtime.project(reference, modality) for modality in MODALITIES]
    clean_verdict = runtime.agree(*clean)
    corruptions = []
    for index, modality in enumerate(MODALITIES):
        cell = 210 + index * 997
        projections = list(clean)
        projections[index] = projections[index].corrupt_cell(cell)
        verdict = runtime.agree(*projections)
        if verdict["agreement"] or cell not in verdict["disagreement_cells"]:
            raise RuntimeError(f"corruption localization failure for {modality}")
        corruptions.append({
            "modality": modality,
            "cell": cell,
            "detected_cells": verdict["disagreement_cells"],
            "surviving_witnesses": verdict["surviving_witnesses"],
            "repair_performed": verdict["repair_performed"],
        })

    view_id = runtime.view_admit(5, 1, 361)
    view = runtime.view(view_id)
    strict_register = affine_fibonacci_mod2(0, 1)
    strict_package = runtime.strict_compress(strict_register)
    strict_round_trip = runtime.strict_decompress(strict_package)
    if strict_round_trip != strict_register:
        raise RuntimeError("strict compression round-trip failure")

    replay_runtime = HolographicFrameCompressionRuntime()
    replay_frame = replay_runtime.frame_encode(reference)
    replay_runtime.frame_decode(replay_frame)
    replay_runtime.view_admit(5, 1, 361)
    replay_runtime.recover(replay_frame, 17)
    replay_receipts = replay_runtime.ledger.export()
    replay_runtime_2 = HolographicFrameCompressionRuntime()
    replay_frame_2 = replay_runtime_2.frame_encode(reference)
    replay_runtime_2.frame_decode(replay_frame_2)
    replay_runtime_2.view_admit(5, 1, 361)
    replay_runtime_2.recover(replay_frame_2, 17)
    if replay_receipts != replay_runtime_2.ledger.export():
        raise RuntimeError("deterministic replay mismatch")

    return {
        "schema": "HHS_PASS_210_HFC_COMPLETION_EVIDENCE_V1",
        "contract": CONTRACT,
        "contract_classification": CONTRACT_CLASSIFICATION,
        "runtime_classification": RUNTIME_CLASSIFICATION,
        "status_distinction": [
            "CONTRACT PRESENT",
            "IMPLEMENTATION PRESENT",
            "IMPLEMENTATION VERIFIED",
        ],
        "canonical_float_authority": False,
        "invariants": audit_invariants(),
        "corpus_vectors": vectors,
        "section_layout": [89, 55, 89, 55],
        "reference_register": {
            "name": reference_name,
            "generator": "python.random.Random(210).randrange(2) x 5184",
            "register_sha256": sha256(reference),
            "register_hash216": reference_frame.object_hash216,
        },
        "clean_multimodal_agreement": clean_verdict,
        "erasure_drills": erasures,
        "corruption_drills": corruptions,
        "reference_affine_view": {
            "view_id": view_id,
            "k": view.k,
            "c": view.c,
            "modulus": view.modulus,
            "inverse_k": view.inverse_k,
            "round_trip_all_residues": all(
                view.decode(view.encode(value)) == value for value in range(361)
            ),
        },
        "strict_compression": {
            "package": strict_package,
            "encoded_json_bytes": len(
                json.dumps(strict_package, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ),
            "canonical_register_bytes": REGISTER_LEN,
            "round_trip_sha256": sha256(strict_round_trip),
        },
        "deterministic_replay_receipts": replay_receipts,
        "full_session_receipt_head_hash72": runtime.ledger.head,
        "full_session_receipt_count": len(runtime.ledger.records()),
    }


def rendered() -> str:
    return json.dumps(generate(), sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = rendered()
    if args.check:
        if not OUTPUT.is_file():
            print(f"missing evidence: {OUTPUT}", file=sys.stderr)
            return 1
        actual = OUTPUT.read_text(encoding="utf-8")
        if actual != expected:
            print("Pass 210 evidence is stale or non-deterministic", file=sys.stderr)
            return 1
        print("PASS210_EVIDENCE_CHECK_OK")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
