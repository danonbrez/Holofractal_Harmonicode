#!/usr/bin/env python3
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
repo = PROJECT if (PROJECT / "hhs_gui").exists() else Path(__file__).resolve().parents[3]
surface = (repo / "hhs_gui/runtime_apps/pass190/Pass190OperationFabricSurface.tsx").read_text(encoding="utf-8")
checks = {
    "arbitration_fetch": '/api/pass190/arbitration' in surface,
    "fence_count": "Fence witnesses" in surface,
    "highest_fence": "Highest fence" in surface,
    "lease_status": "Admission lease" in surface,
    "distributed_verified": "distributed_singleton_verified" in surface,
    "fenced_event_display": "event.fencing_token" in surface,
    "signed_capability_preserved": "HHS-Capability" in surface,
    "resume_preserved": "lastSequenceRef.current" in surface,
}
failed = [name for name, value in checks.items() if not value]
if failed:
    raise SystemExit("Pass 190 Iteration 4 GUI verification failed: " + ", ".join(failed))
print("Pass 190 Iteration 4 distributed authority GUI verification: PASS")
