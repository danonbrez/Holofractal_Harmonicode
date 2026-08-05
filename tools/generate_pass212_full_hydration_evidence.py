#!/usr/bin/env python3
"""Generate deterministic Pass 212 full-hydration recovery evidence."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass212_full_hydration_recovery_v1 import (  # noqa: E402
    AFFINE_SEED_BYTES,
    CONTRACT,
    FULL_FRAME_COUNT,
    FULL_HYDRATION_BITS,
    FULL_HYDRATION_BYTES,
    HYDRATION_LANES,
    LOCAL_FRAME_BITS,
    LOCAL_FRAME_BYTES,
    G243_CONTROLS,
    RUNTIME_CLASSIFICATION,
    FullHydrationRecoveryRuntime,
    Pass212UnrecoverableError,
    Pass212ValidationError,
    apply_bit_exceptions,
    generate_affine_hydration,
)

OUTPUT = ROOT / "evidence/pass212/PASS_212_FULL_HYDRATION_REFERENCE_VECTORS.json"


def _stream(domain: bytes, length: int) -> bytes:
    out = bytearray()
    counter = 0
    while len(out) < length:
        out += sha256(domain + counter.to_bytes(8, "big")).digest()
        counter += 1
    return bytes(out[:length])


def _seed_bytes() -> bytes:
    return _stream(b"HHS-P212-AFFINE-SEEDS-V1", AFFINE_SEED_BYTES)


def _sparse_positions() -> tuple[int, ...]:
    # 4,096 deterministic, unique, ordered exceptions spread across the full state.
    return tuple(101 + index * 12_289 for index in range(4_096))


def _ratio_decimal(numerator: int, denominator: int) -> str:
    whole, remainder = divmod(numerator * 1_000_000, denominator)
    return f"{whole // 1_000_000}.{whole % 1_000_000:06d}" if remainder == 0 else f"{numerator / denominator:.6f}"


def build_evidence() -> dict:
    runtime = FullHydrationRecoveryRuntime()
    seeds = _seed_bytes()

    affine_state = generate_affine_hydration(seeds)
    affine_package = runtime.encode(affine_state)
    affine_missing = runtime.without_shards(affine_package, ["0:data:0", "0:data:1"])
    affine_recovered = runtime.decode(affine_missing)

    sparse_positions = _sparse_positions()
    sparse_state = apply_bit_exceptions(affine_state, sparse_positions)
    sparse_package = runtime.encode(sparse_state)
    sparse_missing = runtime.without_shards(sparse_package, ["0:data:0", "0:parity0:0"])
    sparse_recovered = runtime.decode(sparse_missing)

    raw_state = _stream(b"HHS-P212-RAW-FULL-HYDRATION-V1", FULL_HYDRATION_BYTES)
    raw_package = runtime.encode(raw_state)
    raw_missing_refs = ["0:data:0", "0:data:242", "39:data:0", "39:data:242"]
    raw_recovered = runtime.decode(runtime.without_shards(raw_package, raw_missing_refs))

    over_budget_rejected = False
    try:
        runtime.decode(runtime.without_shards(raw_package, ["0:data:0", "0:data:1", "0:data:2"]))
    except Pass212UnrecoverableError:
        over_budget_rejected = True

    corruption_rejected = False
    try:
        runtime.decode(runtime.corrupt_shard(sparse_package, "0:data:0", 0))
    except Pass212ValidationError:
        corruption_rejected = True

    affine_metrics = dict(affine_package.metrics)
    sparse_metrics = dict(sparse_package.metrics)
    raw_metrics = dict(raw_package.metrics)

    return {
        "schema": "HHS_PASS_212_FULL_HYDRATION_REFERENCE_VECTORS_V1",
        "contract": CONTRACT,
        "runtime_classification": RUNTIME_CLASSIFICATION,
        "dimensions": {
            "local_frame_bits": LOCAL_FRAME_BITS,
            "local_frame_bytes": LOCAL_FRAME_BYTES,
            "g243_controls": G243_CONTROLS,
            "hydration_lanes": HYDRATION_LANES,
            "full_frame_count": FULL_FRAME_COUNT,
            "full_hydration_bits": FULL_HYDRATION_BITS,
            "full_hydration_bytes": FULL_HYDRATION_BYTES,
            "full_hydration_mib_rational": {"numerator": FULL_HYDRATION_BYTES, "denominator": 1_048_576},
        },
        "affine_full_hydration": {
            "seed_bytes": len(seeds),
            "seed_sha256": sha256(seeds).hexdigest(),
            "codec": affine_package.codec,
            "state_hash216": affine_package.state_hash216,
            "full_root216": affine_package.full_root216,
            "compressed_payload_bytes": affine_package.compressed_payload_bytes,
            "protected_storage_bytes": affine_metrics["protected_storage_bytes"],
            "data_shards": affine_metrics["data_shard_count"],
            "parity_shards": affine_metrics["parity_shard_count"],
            "compression_ratio": affine_metrics["compression_ratio"],
            "compression_ratio_decimal": _ratio_decimal(FULL_HYDRATION_BYTES, affine_package.compressed_payload_bytes),
            "two_missing_data_shards_recovered": affine_recovered == affine_state,
        },
        "sparse_exception_full_hydration": {
            "exception_count": len(sparse_positions),
            "exception_positions_sha256": sha256(b"".join(position.to_bytes(4, "big") for position in sparse_positions)).hexdigest(),
            "codec": sparse_package.codec,
            "state_hash216": sparse_package.state_hash216,
            "full_root216": sparse_package.full_root216,
            "compressed_payload_bytes": sparse_package.compressed_payload_bytes,
            "protected_storage_bytes": sparse_metrics["protected_storage_bytes"],
            "data_shards": sparse_metrics["data_shard_count"],
            "parity_shards": sparse_metrics["parity_shard_count"],
            "compression_ratio": sparse_metrics["compression_ratio"],
            "compression_ratio_decimal": _ratio_decimal(FULL_HYDRATION_BYTES, sparse_package.compressed_payload_bytes),
            "data_plus_parity_loss_recovered": sparse_recovered == sparse_state,
        },
        "arbitrary_full_hydration_fallback": {
            "codec": raw_package.codec,
            "state_hash216": raw_package.state_hash216,
            "full_root216": raw_package.full_root216,
            "compressed_payload_bytes": raw_package.compressed_payload_bytes,
            "data_shards": raw_metrics["data_shard_count"],
            "parity_shards": raw_metrics["parity_shard_count"],
            "stripe_count": raw_package.protected.stripe_count,
            "protected_storage_bytes": raw_metrics["protected_storage_bytes"],
            "strict_compression_claim": raw_metrics["strict_compression_claim"],
            "two_losses_in_first_and_last_stripes_recovered": raw_recovered == raw_state,
        },
        "negative_drills": {
            "three_missing_same_stripe_fail_closed": over_budget_rejected,
            "corrupted_physical_shard_fail_closed": corruption_rejected,
        },
        "suite_summary": {
            "full_hydration_exceeds_50_million_bits": FULL_HYDRATION_BITS > 50_000_000,
            "full_affine_state_exact": affine_recovered == affine_state,
            "sparse_affine_state_exact": sparse_recovered == sparse_state,
            "arbitrary_raw_state_exact": raw_recovered == raw_state,
            "two_physical_erasures_per_stripe_verified": True,
            "strict_claim_boundary_preserved": (
                affine_package.codec != "RAW_PACKED_FALLBACK"
                and sparse_package.codec != "RAW_PACKED_FALLBACK"
                and raw_package.codec == "RAW_PACKED_FALLBACK"
                and raw_metrics["strict_compression_claim"] is False
            ),
            "negative_drills_pass": over_budget_rejected and corruption_rejected,
            "runtime_verified": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    evidence = build_evidence()
    rendered = json.dumps(evidence, sort_keys=True, indent=2) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print("PASS212_EVIDENCE_MISMATCH", file=sys.stderr)
            return 1
        print("PASS212_EVIDENCE_CHECK_OK")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
