#!/usr/bin/env python3
"""Classify whether an inactive production service is safely restartable.

This classifier is deliberately side-effect free. It binds the latest valid
HHS guarded-update receipt to the exact live checkout SHA and emits one
machine-readable recovery class. The caller remains responsible for checking
port ownership, normalizing permissions, restarting systemd, and proving
health before any new promotion.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")


class RecoveryStateError(ValueError):
    pass


@dataclass(frozen=True)
class RecoveryState:
    classification: str
    outcome: str
    live_sha: str
    previous_sha: str
    candidate_sha: str
    runtime_os_bundle_sha: str

    def as_dict(self) -> dict[str, str]:
        return {
            "classification": self.classification,
            "outcome": self.outcome,
            "live_sha": self.live_sha,
            "previous_sha": self.previous_sha,
            "candidate_sha": self.candidate_sha,
            "runtime_os_bundle_sha": self.runtime_os_bundle_sha,
        }


def _require_sha(name: str, value: Any) -> str:
    text = str(value or "")
    if not _SHA40.fullmatch(text):
        raise RecoveryStateError(f"{name} must be an exact 40-hex commit SHA, found {value!r}")
    return text.lower()


def load_latest_receipt(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RecoveryStateError(f"guarded-update receipt log does not exist: {path}")
    latest: dict[str, Any] | None = None
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RecoveryStateError(f"invalid JSON receipt at line {number}: {exc}") from exc
        if not isinstance(value, dict):
            raise RecoveryStateError(f"receipt at line {number} is not an object")
        latest = value
    if latest is None:
        raise RecoveryStateError("guarded-update receipt log contains no receipts")
    return latest


def classify_recovery(receipt: dict[str, Any], live_sha: str) -> RecoveryState:
    live = _require_sha("live_sha", live_sha)
    outcome = str(receipt.get("outcome") or "")
    previous = _require_sha("previous_sha", receipt.get("previous_sha"))
    candidate = _require_sha("candidate_sha", receipt.get("candidate_sha"))
    bundle = _require_sha("runtime_os_bundle_sha", receipt.get("runtime_os_bundle_sha"))

    if outcome == "VALIDATED":
        if live != previous:
            raise RecoveryStateError(
                f"VALIDATED recovery requires live checkout {previous}, found {live}"
            )
        if candidate == previous:
            raise RecoveryStateError("VALIDATED recovery requires a distinct candidate SHA")
        if bundle != candidate:
            raise RecoveryStateError(
                f"VALIDATED recovery requires bundle SHA {candidate}, found {bundle}"
            )
        classification = "INTERRUPTED_AFTER_VALIDATION_BEFORE_TERMINAL_PROMOTION"
    elif outcome == "ROLLBACK_HEALTH_FAILED":
        if live != previous:
            raise RecoveryStateError(
                f"ROLLBACK_HEALTH_FAILED recovery requires live checkout {previous}, found {live}"
            )
        classification = "ROLLBACK_BOUNDARY_RESTART_REQUIRED"
    else:
        raise RecoveryStateError(
            "inactive-service recovery accepts only VALIDATED interrupted transactions or "
            f"ROLLBACK_HEALTH_FAILED rollback boundaries; found outcome {outcome!r}"
        )

    return RecoveryState(
        classification=classification,
        outcome=outcome,
        live_sha=live,
        previous_sha=previous,
        candidate_sha=candidate,
        runtime_os_bundle_sha=bundle,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt-log", required=True, type=Path)
    parser.add_argument("--live-sha", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        state = classify_recovery(load_latest_receipt(args.receipt_log), args.live_sha)
    except RecoveryStateError as exc:
        print(f"HHS_GUARDED_UPDATE_RECOVERY_REFUSED={exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(state.as_dict(), sort_keys=True, separators=(",", ":")))
    else:
        print(f"HHS_GUARDED_UPDATE_RECOVERY_CLASS={state.classification}")
        print(f"HHS_GUARDED_UPDATE_RECOVERY_RECEIPT_OUTCOME={state.outcome}")
        print(f"HHS_GUARDED_UPDATE_RECOVERY_LIVE_SHA={state.live_sha}")
        print(f"HHS_GUARDED_UPDATE_RECOVERY_PREVIOUS_SHA={state.previous_sha}")
        print(f"HHS_GUARDED_UPDATE_RECOVERY_CANDIDATE_SHA={state.candidate_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
