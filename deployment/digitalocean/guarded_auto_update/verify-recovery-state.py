#!/usr/bin/env python3
"""Fail-closed recovery classifier for interrupted HHS production promotion."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable

RECEIPT_SCHEMA = "HHS_GUARDED_UPDATE_RECEIPT_V2"
SHA40 = re.compile(r"^[0-9a-f]{40}$")


class RecoveryStateError(RuntimeError):
    pass


def _records(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise RecoveryStateError("HHS_RECOVERY_RECEIPT_LOG_MISSING")
    rows: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            rows.append(value)
    if not rows:
        raise RecoveryStateError("HHS_RECOVERY_RECEIPT_LOG_EMPTY")
    return rows


def _same_boundary(record: dict[str, Any], *, repository_root: str, branch: str) -> bool:
    return (
        record.get("schema") == RECEIPT_SCHEMA
        and record.get("repository_root") == repository_root
        and record.get("branch") == branch
    )


def _sha(value: Any, *, field: str) -> str:
    text = str(value or "").lower()
    if not SHA40.fullmatch(text):
        raise RecoveryStateError(f"HHS_RECOVERY_{field.upper()}_INVALID")
    return text


def classify_recovery(
    records: Iterable[dict[str, Any]],
    *,
    current_head: str,
    repository_root: str,
    branch: str,
) -> dict[str, Any]:
    rows = list(records)
    if not rows:
        raise RecoveryStateError("HHS_RECOVERY_RECEIPT_LOG_EMPTY")
    head = _sha(current_head, field="current_head")
    latest = rows[-1]
    if not _same_boundary(latest, repository_root=repository_root, branch=branch):
        raise RecoveryStateError("HHS_RECOVERY_LATEST_BOUNDARY_MISMATCH")

    previous = _sha(latest.get("previous_sha"), field="previous_sha")
    candidate = _sha(latest.get("candidate_sha"), field="candidate_sha")
    bundle = _sha(latest.get("runtime_os_bundle_sha"), field="runtime_os_bundle_sha")

    if head != previous:
        raise RecoveryStateError(
            f"HHS_RECOVERY_LIVE_HEAD_NOT_ROLLBACK_BOUNDARY:{head}:{previous}"
        )

    phase = latest.get("phase")
    outcome = latest.get("outcome")

    if phase == "rollback" and outcome == "ROLLBACK_HEALTH_FAILED":
        return {
            "schema": "HHS_PRODUCTION_RECOVERY_STATE_V1",
            "recovery_allowed": True,
            "classification": "ROLLBACK_HEALTH_FAILED",
            "current_head": head,
            "rollback_boundary_sha": previous,
            "interrupted_candidate_sha": candidate,
            "interrupted_bundle_sha": bundle,
            "prior_promoted_boundary_verified": False,
            "service_restart_before_new_promotion_required": True,
        }

    if phase == "validation" and outcome == "VALIDATED":
        if candidate != bundle:
            raise RecoveryStateError(
                "HHS_RECOVERY_VALIDATED_CANDIDATE_BUNDLE_IDENTITY_MISMATCH"
            )
        promoted = None
        for record in reversed(rows[:-1]):
            if not _same_boundary(record, repository_root=repository_root, branch=branch):
                continue
            if (
                record.get("phase") == "promotion"
                and record.get("outcome") == "PROMOTED"
                and str(record.get("candidate_sha") or "").lower() == previous
                and str(record.get("runtime_os_bundle_sha") or "").lower() == previous
            ):
                promoted = record
                break
        if promoted is None:
            raise RecoveryStateError(
                "HHS_RECOVERY_VALIDATED_PREVIOUS_SHA_NOT_PROVEN_PROMOTED"
            )
        return {
            "schema": "HHS_PRODUCTION_RECOVERY_STATE_V1",
            "recovery_allowed": True,
            "classification": "VALIDATED_PREPROMOTION_INTERRUPTION",
            "current_head": head,
            "rollback_boundary_sha": previous,
            "interrupted_candidate_sha": candidate,
            "interrupted_bundle_sha": bundle,
            "prior_promoted_boundary_verified": True,
            "service_restart_before_new_promotion_required": True,
        }

    raise RecoveryStateError(
        f"HHS_RECOVERY_TERMINAL_RECEIPT_NOT_ADMISSIBLE:{phase}:{outcome}"
    )


def verify_recovery(
    receipt_log: Path,
    *,
    current_head: str,
    repository_root: str,
    branch: str,
) -> dict[str, Any]:
    return classify_recovery(
        _records(receipt_log),
        current_head=current_head,
        repository_root=repository_root,
        branch=branch,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt-log", required=True, type=Path)
    parser.add_argument("--current-head", required=True)
    parser.add_argument("--repository-root", required=True)
    parser.add_argument("--branch", required=True)
    args = parser.parse_args()
    try:
        report = verify_recovery(
            args.receipt_log,
            current_head=args.current_head,
            repository_root=args.repository_root,
            branch=args.branch,
        )
    except RecoveryStateError as exc:
        print(str(exc))
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
