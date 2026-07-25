#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports" / "nfv"
REPORT_PATH = REPORT_DIR / "HHS_NFV_CORE_TRANCHE_TEST_REPORT.json"
TESTS = [
    "tests/nfv/test_nfv_core.py",
    "tests/nfv/test_nfv_graph_store_serialization.py",
    "tests/nfv/test_nfv_harmonic_convolution_fourier.py",
]


def main() -> int:
    command = [sys.executable, "-m", "pytest", "-q", *TESTS]
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "HHS_NFV_CORE_TRANCHE_TEST_REPORT_V1",
        "contract_id": "HHS-NFV-CEN-V1",
        "pass_number": 154,
        "classification": "PARTIALLY_IMPLEMENTED",
        "command": command,
        "test_files": TESTS,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "status": "PASSED" if completed.returncode == 0 else "FAILED",
        "terminal_classification_claimed": False,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    print(f"NFV report: {REPORT_PATH.relative_to(ROOT)}")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
