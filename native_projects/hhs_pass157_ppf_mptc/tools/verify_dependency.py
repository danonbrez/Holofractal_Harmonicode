from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess

project = Path(__file__).resolve().parents[1]
parent = project.parent / "hhs_pass156_1_lshpvs"
required = os.environ.get("HHS_PASS157_REQUIRE_DEPENDENCY") == "1"

if not parent.exists():
    if required:
        raise SystemExit("required Pass 156.1 source directory is absent")
    result = {
        "schema": "HHS_PASS_157_DEPENDENCY_GATE_V1",
        "pass156_1_source": "LOCAL_FIXTURE_NOT_PRESENT",
        "standalone_status": "NOT_EVALUATED_IN_FIXTURE",
        "pass157_hardened_gate": "VERIFIED_BY_NATIVE_PASS157_TESTS",
    }
else:
    subprocess.run(["make", "-C", str(parent), "verify"], check=True)
    verification_path = parent / "dist" / "verification.json"
    if not verification_path.exists():
        raise SystemExit("Pass 156.1 verification evidence is absent")
    verification = json.loads(verification_path.read_text())
    if verification.get("complete_nucleus_status") != "HHS_PASS_156_1_INCOMPLETE":
        raise SystemExit("Pass 156.1 historical status was improperly promoted")
    native = json.loads((project / "dist" / "native-verification.json").read_text())
    if native.get("replay") != "MATCH" or len(native.get("admission_seal_hash216", "")) != 216:
        raise SystemExit("Pass 157 hardened dependency receipt is invalid")
    result = {
        "schema": "HHS_PASS_157_DEPENDENCY_GATE_V1",
        "pass156_1_source": "PRESENT_AND_EXECUTED",
        "pass156_1_local_status": verification.get("local_status"),
        "standalone_status": verification.get("complete_nucleus_status"),
        "integration_status": "PASS156_1_CONSUMED_THROUGH_PASS157_HARDENED_RECEIPT_GATE",
        "receipt_hash72": native["receipt_hash72"],
        "admission_seal_hash216": native["admission_seal_hash216"],
        "replay": native["replay"],
    }

(project / "dist").mkdir(exist_ok=True)
(project / "dist" / "dependency-gate.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, sort_keys=True))
