#!/usr/bin/env python3
"""Audit and repair recoverable unified Hash72 journal transition metadata."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from hhs_runtime.hhs_unified_hash72_ledger_recovery_v1 import (  # noqa: E402
    UnifiedLedgerRecoveryError,
    inspect_transition_metadata_recovery,
    repair_transition_metadata,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--backup-root", required=True)
    parser.add_argument("--receipt")
    parser.add_argument("--inspect-only", action="store_true")
    parser.add_argument("--require-repair", action="store_true")
    args = parser.parse_args()

    try:
        if args.inspect_only:
            result = inspect_transition_metadata_recovery(Path(args.ledger))
        else:
            result = repair_transition_metadata(
                Path(args.ledger),
                backup_root=Path(args.backup_root),
                receipt_path=Path(args.receipt) if args.receipt else None,
                require_repair=args.require_repair,
            )
    except UnifiedLedgerRecoveryError as exc:
        print(json.dumps({"schema": "HHS_UNIFIED_HASH72_TRANSITION_RECOVERY_V1", "result": "REFUSED", "error": str(exc)}, sort_keys=True))
        return 2

    print(json.dumps(result, sort_keys=True, default=str))
    if result.get("status") == "REPAIRED_TRANSITION_METADATA":
        print("HHS_UNIFIED_LEDGER_TRANSITION_RECOVERY_VERIFIED=1")
    elif result.get("status") == "VALID_NO_REPAIR_REQUIRED":
        print("HHS_UNIFIED_LEDGER_ALREADY_VALID=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
