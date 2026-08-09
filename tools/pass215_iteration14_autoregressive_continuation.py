#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime import hhs_pass215_iteration14_autoregressive_continuation_v1 as i14


def _write(path: str, payload) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Pass 215 Iteration 14 exact autoregressive continuation benchmark")
    parser.add_argument("--container")
    parser.add_argument("--prompt", default=i14.CONTRACTED_PROMPT)
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
        _write(args.output, i14.compare_replay(left, right))
        return 0
    if args.validate:
        evidence = json.loads(Path(args.validate).read_text(encoding="utf-8"))
        i14.validate_autoregressive_continuation_evidence(evidence)
        continuation = evidence["generated_continuation"]
        _write(args.output, {
            "schema": i14.VALIDATION_SCHEMA,
            "validated": True,
            "generated_token_ids": continuation["generated_token_ids"],
            "continuation_root_hash216": continuation["continuation_root_hash216"],
            "final_symbolic_dag_root_hash216": continuation["final_symbolic_dag"]["ordered_node_root_hash216"],
            "suite_root_hash216": evidence["autoregressive_continuation_suite_root_hash216"],
            "evidence_root_hash216": evidence["evidence_root_hash216"],
            "receipt_hash72": evidence["receipt_hash72"],
        })
        return 0
    if not args.container:
        parser.error("--container is required unless --validate or --compare-replay is used")
    source = {"kind": args.source_kind, "repo_id": args.repo_id, "revision": args.revision}
    evidence = i14.build_autoregressive_continuation_evidence_from_path(
        args.container,
        source=source,
        prompt=args.prompt,
        expected_sha256=args.expected_sha256,
    )
    i14.validate_autoregressive_continuation_evidence(evidence)
    _write(args.output, evidence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
