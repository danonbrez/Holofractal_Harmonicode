#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime import hhs_pass215_iteration13_terminal_model_head_v1 as i13


def _write(path: str, payload) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Pass 215 Iteration 13 authenticated terminal model head benchmark")
    parser.add_argument("--container")
    parser.add_argument("--prompt", default=i13.CONTRACTED_PROMPT)
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
        _write(args.output, i13.compare_replay(left, right))
        return 0
    if args.validate:
        evidence = json.loads(Path(args.validate).read_text(encoding="utf-8"))
        i13.validate_terminal_model_head_evidence(evidence)
        forward = evidence["terminal_model_head_forward"]
        _write(args.output, {
            "schema": i13.VALIDATION_SCHEMA,
            "validated": True,
            "terminal_norm_root_hash216": forward["terminal_norm_root_hash216"],
            "logits_root_hash216": forward["logits_root_hash216"],
            "full_model_forward_root_hash216": forward["full_model_forward_root_hash216"],
            "evidence_root_hash216": evidence["evidence_root_hash216"],
            "suite_root_hash216": evidence["terminal_model_head_suite_root_hash216"],
            "receipt_hash72": evidence["receipt_hash72"],
        })
        return 0
    if not args.container:
        parser.error("--container is required unless --validate or --compare-replay is used")
    source = {"kind": args.source_kind, "repo_id": args.repo_id, "revision": args.revision}
    evidence = i13.build_terminal_model_head_evidence_from_path(
        args.container,
        source=source,
        prompt=args.prompt,
        expected_sha256=args.expected_sha256,
    )
    i13.validate_terminal_model_head_evidence(evidence)
    _write(args.output, evidence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
