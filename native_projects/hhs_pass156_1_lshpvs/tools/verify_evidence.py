from __future__ import annotations

import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
subprocess.run(["make", "-C", str(root), "test"], check=True)
verification = json.loads((root / "dist" / "verification.json").read_text())
required = {
    "contract": "HHS-P156.1-LSHPVS",
    "local_status": "HHS_PASS_156_1_LOCAL_CORE_VERIFIED",
    "complete_nucleus_status": "HHS_PASS_156_1_INCOMPLETE",
    "replay": "MATCH",
}
for key, expected in required.items():
    if verification.get(key) != expected:
        raise SystemExit(
            f"{key}: expected {expected!r}, got {verification.get(key)!r}"
        )
print(
    json.dumps(
        {
            "schema": "HHS_P156_1_EVIDENCE_VERIFICATION_V1",
            "status": "VERIFIED",
            "checks": required,
        },
        sort_keys=True,
    )
)
