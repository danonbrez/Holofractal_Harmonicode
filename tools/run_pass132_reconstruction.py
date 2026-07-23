from __future__ import annotations
import json
from pathlib import Path
from hhs_runtime.hhs_pass132_reconstructed_replay_v1 import pass132_reconstructed_self_test

root = Path(__file__).resolve().parents[1]
report = pass132_reconstructed_self_test()
out = root / "release_artifacts" / "pass132_reconstruction" / "PASS_132_RECONSTRUCTION_EXECUTION_REPORT.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({"ok": report["ok"], "workloads": report["workload_count"], "report": str(out)}))
