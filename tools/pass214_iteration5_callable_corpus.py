from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hhs_backend.runtime.hhs_pass214_iteration5_callable_corpus_v1 import (
    STATUS_READY,
    build_iteration5_report,
    write_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Pass 214 Iteration 5 callable corpus")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/pass214/iteration5"),
    )
    args = parser.parse_args()
    report = build_iteration5_report()
    write_json(args.output_dir / "PASS_214_ITERATION_5_CALLABLE_CORPUS_REPORT.json", report)
    summary = {
        "status": report["status"],
        "family_count": report["family_count"],
        "completed_consecutive_runs": report["completed_consecutive_runs"],
        "corpus_root_hash216": report["corpus_root_hash216"],
        "receipt_sha256": report["receipt_sha256"],
    }
    write_json(args.output_dir / "iteration5_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if report["status"] == STATUS_READY else 1


if __name__ == "__main__":
    raise SystemExit(main())
