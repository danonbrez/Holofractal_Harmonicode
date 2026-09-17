#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

RECORD_BYTES = 648
BASE_ITERATIONS = 8
RANKS = 9
PHASES = [
    ("xy", 0, 36),
    ("yx", 36, 0),
    ("zw", 18, 54),
    ("wz", 54, 18),
]
SEED = b"HHS_PASS219_ISOLATED_STACK_NEUTRAL_DATASET_V2"


def record_bytes(index: int) -> bytes:
    out = bytearray()
    block = 0
    while len(out) < RECORD_BYTES:
        h = hashlib.sha256()
        h.update(SEED)
        h.update(index.to_bytes(8, "big"))
        h.update(block.to_bytes(4, "big"))
        out.extend(h.digest())
        block += 1
    return bytes(out[:RECORD_BYTES])


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(f"usage: {sys.argv[0]} DATASET.bin MANIFEST.json")
    dataset_path = pathlib.Path(sys.argv[1])
    manifest_path = pathlib.Path(sys.argv[2])
    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    samples = []
    offset = 0
    with dataset_path.open("wb") as f:
        for rank in range(1, RANKS + 1):
            count = BASE_ITERATIONS << (rank - 1)
            gradient_num = rank - 5
            for phase_index, (phase, slot, inverse) in enumerate(PHASES):
                sample_offset = offset
                for _ in range(count):
                    f.write(record_bytes(offset))
                    offset += 1
                samples.append(
                    {
                        "sample_id": f"r{rank}-{phase}",
                        "rank": rank,
                        "gradient": {"numerator": gradient_num, "denominator": 4},
                        "phase_index": phase_index,
                        "phase": phase,
                        "phase_slot": slot,
                        "inverse_phase_slot": inverse,
                        "offset_records": sample_offset,
                        "count": count,
                    }
                )

    payload = dataset_path.read_bytes()
    manifest = {
        "schema": "HHS_PASS219_ISOLATED_STACK_DATASET_V2",
        "neutral_payload": True,
        "record_bytes": RECORD_BYTES,
        "record_count": offset,
        "dataset_bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "base_iterations": BASE_ITERATIONS,
        "difficulty_ranks": RANKS,
        "samples": samples,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: manifest[k] for k in ("schema", "record_bytes", "record_count", "dataset_bytes", "sha256")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
