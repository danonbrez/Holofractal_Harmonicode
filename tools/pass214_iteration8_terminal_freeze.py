#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass214_iteration7_live_admission_ablation_v1 import create_live_admission
from hhs_backend.runtime.hhs_pass214_iteration8_terminal_freeze_v1 import (
    create_terminal_freeze,
    inspect_terminal_readiness,
    validate_terminal_freeze,
)


def load(path: str | None):
    return None if not path else json.loads(Path(path).read_text(encoding="utf-8"))


def write(path: str | None, payload) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
    print(text, end="")


def main() -> int:
    parser = argparse.ArgumentParser(description="Pass 214 Iteration 8 terminal freeze authority")
    parser.add_argument("--mode", choices=("inspect", "finalize", "validate"), default="inspect")
    parser.add_argument("--census-summary")
    parser.add_argument("--compatibility-summary")
    parser.add_argument("--authority-reconciliation")
    parser.add_argument("--workload-corpus")
    parser.add_argument("--benchmark-method")
    parser.add_argument("--benchmark-bundle")
    parser.add_argument("--pass215-profile")
    parser.add_argument("--trusted-anchor-json")
    parser.add_argument("--verifier-bundle-json")
    parser.add_argument("--trust-bundle")
    parser.add_argument("--terminal-record")
    parser.add_argument("--source-commit")
    parser.add_argument("--source-tree")
    parser.add_argument("--nonce", default="pass214-iteration8-terminal-freeze")
    parser.add_argument("--timestamp-ns", type=int)
    parser.add_argument("--output")
    args = parser.parse_args()

    if args.mode == "validate":
        if not args.terminal_record:
            parser.error("--terminal-record is required for --mode validate")
        record = load(args.terminal_record)
        validate_terminal_freeze(record)
        write(args.output, {
            "schema": "HHS_PASS_214_ITERATION_8_TERMINAL_VALIDATION_V1",
            "valid": True,
            "authority_root_hash216": record["terminal_roots"]["PASS214_AUTHORITY_ROOT_HASH216"],
            "pass215_profile_root_hash216": record["terminal_roots"]["PASS215_BENCHMARK_PROFILE_ROOT_HASH216"],
        })
        return 0

    census = load(args.census_summary)
    compatibility = load(args.compatibility_summary)
    reconciliation = load(args.authority_reconciliation)
    benchmark = load(args.benchmark_bundle)
    profile = load(args.pass215_profile)

    if args.mode == "inspect":
        write(args.output, inspect_terminal_readiness(
            census_summary=census,
            compatibility_summary=compatibility,
            authority_reconciliation=reconciliation,
            benchmark_bundle=benchmark,
            pass215_profile=profile,
            live_admission=None,
        ))
        return 0

    required = {
        "--census-summary": args.census_summary,
        "--compatibility-summary": args.compatibility_summary,
        "--authority-reconciliation": args.authority_reconciliation,
        "--workload-corpus": args.workload_corpus,
        "--benchmark-method": args.benchmark_method,
        "--benchmark-bundle": args.benchmark_bundle,
        "--pass215-profile": args.pass215_profile,
        "--trusted-anchor-json": args.trusted_anchor_json,
        "--verifier-bundle-json": args.verifier_bundle_json,
        "--trust-bundle": args.trust_bundle,
        "--source-commit": args.source_commit,
        "--source-tree": args.source_tree,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        parser.error("--mode finalize missing required arguments: " + ", ".join(missing))

    from hhs_backend.runtime.hhs_pass213_governed_surface_v2 import get_default_pass213_surface
    from hhs_backend.runtime.hhs_pass213_native_dispatch_authority_v1 import get_default_native_dispatch_service

    live_admission = create_live_admission(
        surface=get_default_pass213_surface(),
        dispatch_service=get_default_native_dispatch_service(),
        trusted_anchor_mapping=load(args.trusted_anchor_json),
        verifier_bundle_mapping=load(args.verifier_bundle_json),
        trust_bundle_path=args.trust_bundle,
        nonce=args.nonce,
        requested_timestamp_ns=args.timestamp_ns or time.time_ns(),
    )
    record = create_terminal_freeze(
        census_summary=census,
        compatibility_summary=compatibility,
        authority_reconciliation=reconciliation,
        workload_corpus=load(args.workload_corpus),
        benchmark_method=load(args.benchmark_method),
        benchmark_bundle=benchmark,
        pass215_profile=profile,
        live_admission=live_admission,
        source_commit=args.source_commit,
        source_tree=args.source_tree,
    )
    validate_terminal_freeze(record)
    write(args.output, record)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
