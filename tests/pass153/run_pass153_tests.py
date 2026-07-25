from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports/pass153/HHS_PASS_153_VALIDATION_REPORT.json"


def main() -> int:
    command = [sys.executable, "-m", "pytest", "-q", "tests/pass153/test_pass153_environment.py"]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    status = "PASSED" if result.returncode == 0 else "FAILED"
    report = {
        "schema": "HHS_PASS_153_VALIDATION_REPORT_V1",
        "contract_id": "HHS-P153-LITERT-OPEN-MODEL-AGENT",
        "pass_number": 153,
        "status": status,
        "command": command,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "terminal_classification": "HHS_PASS_153_LITERT_OPEN_MODEL_AGENT_ENVIRONMENT_VERIFIED" if status == "PASSED" else None,
        "authority": {"model": "ADVISORY", "execution": "VM81", "receipt": "Hash72", "identity": "Hash216"},
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
