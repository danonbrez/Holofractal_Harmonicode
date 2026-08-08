from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hhs_backend.runtime.hhs_pass214_iteration6_candidate_binding_v1 import (
    STATUS_BLOCKED,
    build_report,
    validate_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Pass 214 Iteration 6 candidate bindings")
    parser.add_argument("--output", type=Path, default=Path("artifacts/pass214/iteration6/PASS_214_ITERATION_6_CANDIDATE_BINDING_REPORT.json"))
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "family_count": report["family_count"],
        "candidate_set_root_hash216": report["candidate_set_root_hash216"],
        "report_root_hash216": report["report_root_hash216"],
        "receipt_sha256": report["receipt_sha256"],
    }, indent=2, sort_keys=True))
    return 0 if report["status"] == STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())
