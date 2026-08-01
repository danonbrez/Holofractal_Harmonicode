#!/usr/bin/env python3
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
repo = PROJECT if (PROJECT / "hhs_gui").exists() else Path(__file__).resolve().parents[3]
surface = (repo / "hhs_gui/runtime_apps/pass190/Pass190OperationFabricSurface.tsx").read_text(encoding="utf-8")
checks = {
    "periodic_refresh": "setInterval" in surface and "refreshAuthority" in surface,
    "event_refresh": "void refreshAuthority().catch" in surface,
    "lease_transitions": "lease_transition_count" in surface and "last_transition" in surface,
    "lease_state": "lease_state" in surface,
    "atomic_snapshot": "atomic_snapshot_verified" in surface,
    "lease_chain": "lease_receipt_chain_verified" in surface,
    "kernel_authority": "kernel_authority_verified" in surface and "kernel_authority_hash72" in surface,
    "kernel_action": "Invoke through kernel authority" in surface,
}
failed = [name for name, value in checks.items() if not value]
if failed:
    raise SystemExit("Pass 190 Iteration 5 GUI verification failed: " + ", ".join(failed))
print("Pass 190 Iteration 5 GUI verification: PASS")
