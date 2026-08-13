#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime import hhs_pass215_iteration12_all_six_block_forward_v1 as i12


def _write(path: str, payload) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Pass 215 Iteration 12 authenticated all-six-block benchmark")
    parser.add_argument("--container")
    parser.add_argument("--prompt", default=i12.CONTRACTED_PROMPT)
    parser.add_argument("--source-kind", default="public_open_transformer")
    parser.add_argument("--repo-id", default="ggml-org/tiny-llamas")
    parser.add_argument("--revision", default="main")
    parser.add_argument("--expected-sha256")
    parser.add_argument("--validate")
    parser.add_argument("--compare-replay", nargs=2, metavar=("LEFT", "RIGHT"))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    if args.compare_replay:
        left = json.loads(Path(args.compare_replay[0]).read_text(encoding="utf-8"))
        right = json.loads(Path(args.compare_replay[1]).read_text(encoding="utf-8"))
        _write(args.output, i12.compare_replay(left, right))
        return 0
    if args.validate:
        evidence = json.loads(Path(args.validate).read_text(encoding="utf-8"))
        i12.validate_all_six_block_evidence(evidence)
        _write(args.output, {
            "schema": i12.VALIDATION_SCHEMA,
            "validated": True,
            "final_block_output_root_hash216": evidence["sequential_all_block_forward"]["final_block_output_root_hash216"],
            "all_block_forward_root_hash216": evidence["sequential_all_block_forward"]["all_block_forward_root_hash216"],
            "evidence_root_hash216": evidence["evidence_root_hash216"],
            "suite_root_hash216": evidence["all_six_block_suite_root_hash216"],
            "receipt_hash72": evidence["receipt_hash72"],
        })
        return 0
    if not args.container:
        parser.error("--container is required unless --validate or --compare-replay is used")
    source = {"kind": args.source_kind, "repo_id": args.repo_id, "revision": args.revision}
    evidence = i12.build_all_six_block_evidence_from_path(
        args.container,
        source=source,
        prompt=args.prompt,
        expected_sha256=args.expected_sha256,
    )
    i12.validate_all_six_block_evidence(evidence)
    _write(args.output, evidence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
