#!/usr/bin/env python3
"""Hydrate main-admitted PR invariant/contract logic into the inherited Hash216 store."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from hhs_runtime.pass191.main_history_hash216_hydration import (
    HydrationBounds,
    hydrate_main_history,
)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument("--repository-root", default=".")
    value.add_argument("--ref", default="HEAD")
    value.add_argument("--state-root", required=True)
    value.add_argument("--vector-database", required=True)
    value.add_argument("--vector-key", required=True)
    value.add_argument("--max-commits", type=int, default=100_000)
    value.add_argument("--max-artifact-bytes", type=int, default=4 * 1024 * 1024)
    value.add_argument("--max-total-logic-bytes", type=int, default=256 * 1024 * 1024)
    value.add_argument("--max-frames", type=int, default=500_000)
    value.add_argument("--max-manifest-bytes", type=int, default=128 * 1024 * 1024)
    return value


def main() -> int:
    args = parser().parse_args()
    report = hydrate_main_history(
        repository_root=Path(args.repository_root),
        ref=args.ref,
        state_root=Path(args.state_root),
        vector_database=Path(args.vector_database),
        vector_key=Path(args.vector_key),
        bounds=HydrationBounds(
            max_commits=args.max_commits,
            max_artifact_bytes=args.max_artifact_bytes,
            max_total_logic_bytes=args.max_total_logic_bytes,
            max_frames=args.max_frames,
            max_manifest_bytes=args.max_manifest_bytes,
        ),
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
