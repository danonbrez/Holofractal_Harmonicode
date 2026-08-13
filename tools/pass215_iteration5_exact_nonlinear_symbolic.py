#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass215_iteration5_exact_nonlinear_symbolic_v1 import (
    REAL_MODEL_SHA256,
    VALIDATION_SCHEMA,
    build_nonlinear_evidence_from_path,
    compare_replay,
    validate_nonlinear_evidence,
)


def _write(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _read(path: str | Path) -> Mapping[str, Any]:
    value = json.loads(Path(path).read_text())
    if not isinstance(value, dict):
        raise SystemExit("evidence must be a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Pass 215 Iteration 5 exact nonlinear symbolic benchmark")
    parser.add_argument("--container")
    parser.add_argument("--source-kind", default="public_open_transformer")
    parser.add_argument("--repo-id", default="ggml-org/tiny-llamas")
    parser.add_argument("--revision", default="main")
    parser.add_argument("--expected-sha256", default=REAL_MODEL_SHA256)
    parser.add_argument("--validate")
    parser.add_argument("--compare-replay", nargs=2, metavar=("LEFT", "RIGHT"))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    selected = sum(bool(value) for value in (args.container, args.validate, args.compare_replay))
    if selected != 1:
        parser.error("choose exactly one of --container, --validate, or --compare-replay")

    if args.container:
        evidence = build_nonlinear_evidence_from_path(
            args.container,
            source={
                "kind": args.source_kind,
                "repo_id": args.repo_id,
                "revision": args.revision,
            },
            expected_sha256=args.expected_sha256,
        )
        _write(args.output, evidence)
        return 0

    if args.validate:
        evidence = _read(args.validate)
        validate_nonlinear_evidence(evidence)
        result = {
            "schema": VALIDATION_SCHEMA,
            "valid": True,
            "semantic_exactness": True,
            "nonlinear_suite_root_hash216": evidence["nonlinear_suite_root_hash216"],
            "evidence_root_hash216": evidence["evidence_root_hash216"],
            "receipt_hash72": evidence["receipt_hash72"],
        }
        _write(args.output, result)
        return 0

    left = _read(args.compare_replay[0])
    right = _read(args.compare_replay[1])
    _write(args.output, compare_replay(left, right))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
