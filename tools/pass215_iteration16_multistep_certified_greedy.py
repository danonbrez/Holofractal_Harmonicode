#!/usr/bin/env python3
"""CLI for Pass 215 Iteration 16 multi-step certified greedy evidence."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime import hhs_pass215_iteration16_multistep_certified_greedy_v1 as i16


def _write(path: str, payload: object) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--container")
    parser.add_argument("--prompt", default=i16.CONTRACTED_PROMPT)
    parser.add_argument("--source-kind", default="public_open_transformer")
    parser.add_argument("--repo-id", default="ggml-org/tiny-llamas")
    parser.add_argument("--revision", default="main")
    parser.add_argument("--expected-sha256")
    parser.add_argument("--certification-bits", type=int, default=i16.CERTIFICATION_BITS)
    parser.add_argument("--greedy-steps", type=int, default=i16.CERTIFIED_GREEDY_STEP_COUNT)
    parser.add_argument("--validate")
    parser.add_argument("--compare-replay", nargs=2, metavar=("LEFT", "RIGHT"))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    if args.validate:
        evidence = json.loads(Path(args.validate).read_text(encoding="utf-8"))
        i16.validate_multistep_certified_greedy_evidence(evidence)
        _write(args.output, {
            "schema": i16.VALIDATION_SCHEMA,
            "contract": i16.CONTRACT,
            "valid": True,
            "selected_token_ids": evidence["multistep_certified_greedy"]["selected_token_ids"],
            "chain_root_hash216": evidence["multistep_certified_greedy"]["chain_root_hash216"],
            "suite_root_hash216": evidence["multistep_certified_greedy_suite_root_hash216"],
            "evidence_root_hash216": evidence["evidence_root_hash216"],
            "receipt_hash72": evidence["receipt_hash72"],
        })
        return 0

    if args.compare_replay:
        left = json.loads(Path(args.compare_replay[0]).read_text(encoding="utf-8"))
        right = json.loads(Path(args.compare_replay[1]).read_text(encoding="utf-8"))
        _write(args.output, i16.compare_multistep_certified_greedy_replays(left, right))
        return 0

    if not args.container:
        parser.error("--container is required for evidence generation")
    source = {
        "kind": args.source_kind,
        "repo_id": args.repo_id,
        "revision": args.revision,
    }
    evidence = i16.build_multistep_certified_greedy_evidence_from_path(
        args.container,
        source=source,
        prompt=args.prompt,
        expected_sha256=args.expected_sha256,
        certification_bits=args.certification_bits,
        greedy_steps=args.greedy_steps,
    )
    _write(args.output, evidence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
