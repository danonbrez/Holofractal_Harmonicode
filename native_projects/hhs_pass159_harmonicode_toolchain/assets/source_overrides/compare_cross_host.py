#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
files = sorted((root / "dist" / "cross-host").glob("**/P159_CANONICAL_ROOT_*.json"))
reports = [json.loads(path.read_text(encoding="utf-8")) for path in files]
roots = {report["canonical_source_root"] for report in reports}
machines = {report["machine"] for report in reports}
matched = len(reports) >= 2 and len(roots) == 1 and len(machines) >= 2
out = {
    "classification": "HHS159_CROSS_ARCHITECTURE_CANONICAL_ROOT_VERIFIED" if matched else "HHS159_CROSS_ARCHITECTURE_CANONICAL_ROOT_FAILED",
    "matched": matched,
    "reports": reports,
    "root_count": len(roots),
    "machine_count": len(machines),
}
(root / "dist" / "P159_CROSS_ARCHITECTURE_INPUT.json").write_text(
    json.dumps(out, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(json.dumps(out, sort_keys=True))
raise SystemExit(0 if matched else 1)
