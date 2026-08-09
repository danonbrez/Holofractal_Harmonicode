#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime import (  # noqa: E402
    hhs_pass215_iteration20_shared_checkpoint_terminal_v1 as i20,
)


def write(path: str, payload: object) -> None:
    Path(path).write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--container")
    parser.add_argument("--prompt", default=i20.CONTRACTED_PROMPT)
    parser.add_argument("--source-kind", default="public_open_transformer")
    parser.add_argument("--repo-id", default="ggml-org/tiny-llamas")
    parser.add_argument("--revision", default="main")
    parser.add_argument("--expected-sha256")
    parser.add_argument(
        "--certification-bits", type=int, default=i20.CERTIFICATION_BITS
    )
    parser.add_argument("--bundle-output")
    parser.add_argument("--validate")
    parser.add_argument("--compare-replay", nargs=2)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    if args.validate:
        evidence = json.loads(Path(args.validate).read_text())
        i20.validate_shared_checkpoint_terminal_evidence(evidence)
        checkpoints = evidence["sequential_checkpoints"]
        write(
            args.output,
            {
                "schema": i20.VALIDATION_SCHEMA,
                "contract": i20.CONTRACT,
                "valid": True,
                "earlier_checkpoint_root_hash216": checkpoints[
                    "earlier_checkpoint_root_hash216"
                ],
                "later_checkpoint_root_hash216": checkpoints[
                    "later_checkpoint_root_hash216"
                ],
                "shared_content_store_root_hash216": checkpoints[
                    "shared_content_store_root_hash216"
                ],
                "shared_checkpoint_bundle_root_hash216": checkpoints[
                    "shared_checkpoint_bundle_root_hash216"
                ],
                "sequential_checkpoint_reuse_root_hash216": checkpoints[
                    "sequential_checkpoint_reuse_root_hash216"
                ],
                "pass215_terminal_completion_root_hash216": evidence[
                    "pass215_terminal_completion_root_hash216"
                ],
                "suite_root_hash216": evidence[
                    "shared_checkpoint_terminal_suite_root_hash216"
                ],
                "evidence_root_hash216": evidence["evidence_root_hash216"],
                "receipt_hash72": evidence["receipt_hash72"],
                "pass216_status": evidence["downstream_transition"][
                    "pass216_status"
                ],
                "next_implemented_pass": evidence["downstream_transition"][
                    "next_implemented_pass"
                ],
            },
        )
        return 0

    if args.compare_replay:
        left = json.loads(Path(args.compare_replay[0]).read_text())
        right = json.loads(Path(args.compare_replay[1]).read_text())
        write(
            args.output,
            i20.compare_shared_checkpoint_terminal_replays(left, right),
        )
        return 0

    if not args.container:
        parser.error("--container required")
    evidence, bundle = i20.execute_shared_checkpoint_terminal_benchmark_from_path(
        args.container,
        source={
            "kind": args.source_kind,
            "repo_id": args.repo_id,
            "revision": args.revision,
        },
        prompt=args.prompt,
        expected_sha256=args.expected_sha256,
        certification_bits=args.certification_bits,
    )
    write(args.output, evidence)
    if args.bundle_output:
        write(args.bundle_output, bundle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
