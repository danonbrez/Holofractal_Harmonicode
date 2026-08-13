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

from hhs_backend.runtime.hhs_pass215_iteration9_authenticated_token_ingress_v2 import (
    REAL_MODEL_SHA256,
    VALIDATION_SCHEMA,
    build_authenticated_token_ingress_evidence_from_path,
    compare_replay,
    validate_authenticated_token_ingress_evidence,
)


def _read(path: str | Path) -> Mapping[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit("evidence must be a JSON object")
    return value


def _write(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(payload, indent=2, sort_keys=False, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Pass 215 Iteration 9 authenticated tokenizer/token-embedding ingress")
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
        evidence = build_authenticated_token_ingress_evidence_from_path(
            args.container,
            source={"kind": args.source_kind, "repo_id": args.repo_id, "revision": args.revision},
            expected_sha256=args.expected_sha256,
        )
        _write(args.output, evidence)
        return 0

    if args.validate:
        evidence = _read(args.validate)
        validate_authenticated_token_ingress_evidence(evidence)
        execution = evidence["token_ingress_coordinate_forward"]
        _write(args.output, {
            "schema": VALIDATION_SCHEMA,
            "valid": True,
            "semantic_exactness": True,
            "selected_token_ids": evidence["authenticated_token_ingress"]["selected_token_ids"],
            "tokenizer_vocabulary_root_hash216": evidence["authenticated_tokenizer"]["vocabulary_root_hash216"],
            "embedding_suite_root_hash216": evidence["authenticated_token_ingress"]["embedding_suite_root_hash216"],
            "stage_suite_root_hash216": execution["executed_stage_suite_root_hash216"],
            "causal_attention_root_hash216": execution["causal_attention_root_hash216"],
            "final_output_root_hash216": execution["final_output_root_hash216"],
            "token_ingress_suite_root_hash216": evidence["token_ingress_suite_root_hash216"],
            "evidence_root_hash216": evidence["evidence_root_hash216"],
            "receipt_hash72": evidence["receipt_hash72"],
        })
        return 0

    _write(args.output, compare_replay(_read(args.compare_replay[0]), _read(args.compare_replay[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
