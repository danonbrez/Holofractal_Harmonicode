#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
dist = root / "dist"
report_path = dist / "P159_FOUNDATION_VALIDATION_REPORT.json"
report = json.loads(report_path.read_text(encoding="utf-8").strip())
files = []
for path in sorted((root / "include").glob("*.h")) + sorted((root / "src").glob("*.c")):
    data = path.read_bytes()
    files.append({"path": str(path.relative_to(root)), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
evidence = {
    "contract": "HHS-P159-VM81-H216-HCI-C11C",
    "classification": "HHS_PASS_159_FOUNDATION_IMPLEMENTED_PENDING_FULL_CLOSURE",
    "terminal_claimed": False,
    "validation": report,
    "artifacts": files,
}
(root / "evidence" / "P159_FOUNDATION_IMPLEMENTATION_REPORT.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(evidence, sort_keys=True))
