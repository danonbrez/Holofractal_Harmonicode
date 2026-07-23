"""CLI projection for Pass 077 native compiler and artifact pipeline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .hhs_independent_artifact_verifier_v1 import _load_verifier
from .hhs_pass077_replay_runner_v1 import replay_compiler_workspace
from .hhs_pass077_workspace_runtime_v1 import build_pass077_demo


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="hhs-pass077")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo")
    sub.add_parser("replay")
    verify = sub.add_parser("verify-package")
    verify.add_argument("path")
    args = parser.parse_args(argv)
    if args.command == "demo":
        demo = build_pass077_demo()
        result = {
            "status": "PASS",
            "workspace_state_root_hash72": demo["snapshot"]["workspace_state_root_hash72"],
            "artifact_status": demo["snapshot"]["compiled_artifacts"]["artifact:pass077:portable"]["status"],
        }
    elif args.command == "replay":
        result = replay_compiler_workspace()
    else:
        result = _load_verifier().verify_package(Path(args.path))
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if result.get("status") in {"PASS", "REEXECUTED_SEMANTIC_EQUIVALENCE"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
