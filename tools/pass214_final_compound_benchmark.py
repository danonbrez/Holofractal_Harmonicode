#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass214_final_compound_benchmark_v1 import (
    build_final_benchmark_bundle,
    validate_final_benchmark_bundle,
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_value(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute the frozen Pass 214 final compound benchmark")
    parser.add_argument("--workload-corpus", type=Path, default=ROOT / "contracts/pass214/PASS_214_WORKLOAD_CORPUS.json")
    parser.add_argument("--benchmark-method", type=Path, default=ROOT / "contracts/pass214/PASS_214_FINAL_BENCHMARK_METHOD.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--validate", type=Path)
    args = parser.parse_args()

    if args.validate:
        bundle = load(args.validate)
        validate_final_benchmark_bundle(bundle)
        print(json.dumps({"valid": True, "compound_evidence_root_hash216": bundle["compound_evidence_root_hash216"], "receipt_hash72": bundle["receipt_hash72"]}, sort_keys=True))
        return 0

    bundle = build_final_benchmark_bundle(
        source_commit=git_value("rev-parse", "HEAD"),
        source_tree=git_value("rev-parse", "HEAD^{tree}"),
        workload_corpus=load(args.workload_corpus),
        benchmark_method=load(args.benchmark_method),
    )
    validate_final_benchmark_bundle(bundle)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": bundle["status"],
        "source_commit": bundle["source_commit"],
        "source_tree": bundle["source_tree"],
        "workload_family_count": len(bundle["workloads"]),
        "ablation_count": len(bundle["ablations"]),
        "compound_evidence_root_hash216": bundle["compound_evidence_root_hash216"],
        "receipt_hash72": bundle["receipt_hash72"],
    }, indent=2, sort_keys=True))
    print("PASS214_FINAL_COMPOUND_BENCHMARK_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
