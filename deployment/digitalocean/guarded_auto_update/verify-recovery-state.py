#!/usr/bin/env python3
"""Fail-closed recovery classifier for interrupted HHS production promotion."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Iterable

RECEIPT_SCHEMA = "HHS_GUARDED_UPDATE_RECEIPT_V2"
WARM_BOOT_SCHEMA = "HHS_PASS_220_I046_WARM_HYDRATED_VM_BOOT_V1"
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


def _validate_legacy_warm_boot_proof(
    proof: dict[str, Any],
    *,
    current_head: str,
) -> dict[str, Any]:
    head = _sha(current_head, field="current_head")
    if proof.get("schema") != WARM_BOOT_SCHEMA:
        raise RecoveryStateError("HHS_RECOVERY_LEGACY_WARM_BOOT_SCHEMA_MISMATCH")
    if str(proof.get("repository_sha") or "").lower() != head:
        raise RecoveryStateError(
            "HHS_RECOVERY_LEGACY_WARM_BOOT_REPOSITORY_SHA_MISMATCH"
        )
    required_true = (
        "native_runtime_adopted",
        "runtime_os_adopted",
        "persistent_state_adopted",
    )
    for field in required_true:
        if proof.get(field) is not True:
            raise RecoveryStateError(
                f"HHS_RECOVERY_LEGACY_WARM_BOOT_{field.upper()}_NOT_PROVEN"
            )
    required_false = (
        "compile_on_restart",
        "rehydrate_from_empty_on_restart",
        "canonical_state_authority",
        "new_vm81_authority",
    )
    for field in required_false:
        if proof.get(field) is not False:
            raise RecoveryStateError(
                f"HHS_RECOVERY_LEGACY_WARM_BOOT_{field.upper()}_UNSAFE"
            )
    manifest = str(proof.get("manifest") or "")
    if not manifest:
        raise RecoveryStateError("HHS_RECOVERY_LEGACY_WARM_BOOT_MANIFEST_MISSING")
    return proof


def _run_legacy_warm_boot_verifier(
    *,
    verifier: Path,
    manifest_root: Path,
    repository_root: str,
    current_head: str,
) -> dict[str, Any]:
    if not verifier.is_file():
        raise RecoveryStateError(
            f"HHS_RECOVERY_LEGACY_WARM_BOOT_VERIFIER_MISSING:{verifier}"
        )
    if not manifest_root.is_dir():
        raise RecoveryStateError(
            f"HHS_RECOVERY_LEGACY_WARM_BOOT_MANIFEST_ROOT_MISSING:{manifest_root}"
        )
    env = dict(os.environ)
    env["HHS_DISABLE_C_AUTOBUILD"] = "1"
    completed = subprocess.run(
        [
            sys.executable,
            str(verifier),
            "verify",
            "--repo-root",
            repository_root,
            "--manifest-root",
            str(manifest_root),
        ],
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    if completed.returncode != 0:
        detail = (completed.stdout + completed.stderr).strip()
        raise RecoveryStateError(
            "HHS_RECOVERY_LEGACY_WARM_BOOT_VERIFY_FAILED"
            + (f":{detail}" if detail else "")
        )
    lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    if not lines:
        raise RecoveryStateError("HHS_RECOVERY_LEGACY_WARM_BOOT_VERIFY_EMPTY")
    try:
        proof = json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        raise RecoveryStateError(
            "HHS_RECOVERY_LEGACY_WARM_BOOT_VERIFY_MALFORMED"
        ) from exc
    if not isinstance(proof, dict):
        raise RecoveryStateError("HHS_RECOVERY_LEGACY_WARM_BOOT_VERIFY_MALFORMED")
    return _validate_legacy_warm_boot_proof(proof, current_head=current_head)


def classify_recovery(
    records: Iterable[dict[str, Any]],
    *,
    current_head: str,
    repository_root: str,
    branch: str,
    legacy_warm_boot_proof: dict[str, Any] | None = None,
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
            "legacy_warm_boot_boundary_verified": False,
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
        if promoted is not None:
            return {
                "schema": "HHS_PRODUCTION_RECOVERY_STATE_V1",
                "recovery_allowed": True,
                "classification": "VALIDATED_PREPROMOTION_INTERRUPTION",
                "current_head": head,
                "rollback_boundary_sha": previous,
                "interrupted_candidate_sha": candidate,
                "interrupted_bundle_sha": bundle,
                "prior_promoted_boundary_verified": True,
                "legacy_warm_boot_boundary_verified": False,
                "service_restart_before_new_promotion_required": True,
            }

        if legacy_warm_boot_proof is None:
            raise RecoveryStateError(
                "HHS_RECOVERY_VALIDATED_PREVIOUS_SHA_NOT_PROVEN_PROMOTED"
            )
        _validate_legacy_warm_boot_proof(
            legacy_warm_boot_proof,
            current_head=head,
        )
        return {
            "schema": "HHS_PRODUCTION_RECOVERY_STATE_V1",
            "recovery_allowed": True,
            "classification": "VALIDATED_PREPROMOTION_INTERRUPTION_LEGACY_WARM_BOOT",
            "current_head": head,
            "rollback_boundary_sha": previous,
            "interrupted_candidate_sha": candidate,
            "interrupted_bundle_sha": bundle,
            "prior_promoted_boundary_verified": False,
            "legacy_warm_boot_boundary_verified": True,
            "legacy_warm_boot_manifest": legacy_warm_boot_proof["manifest"],
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
    warm_boot_verifier: Path | None = None,
    warm_boot_manifest_root: Path | None = None,
) -> dict[str, Any]:
    rows = _records(receipt_log)
    try:
        return classify_recovery(
            rows,
            current_head=current_head,
            repository_root=repository_root,
            branch=branch,
        )
    except RecoveryStateError as exc:
        if str(exc) != "HHS_RECOVERY_VALIDATED_PREVIOUS_SHA_NOT_PROVEN_PROMOTED":
            raise
        if warm_boot_verifier is None and warm_boot_manifest_root is None:
            raise
        if warm_boot_verifier is None or warm_boot_manifest_root is None:
            raise RecoveryStateError(
                "HHS_RECOVERY_LEGACY_WARM_BOOT_PROOF_ARGUMENTS_INCOMPLETE"
            ) from exc

    proof = _run_legacy_warm_boot_verifier(
        verifier=warm_boot_verifier,
        manifest_root=warm_boot_manifest_root,
        repository_root=repository_root,
        current_head=current_head,
    )
    return classify_recovery(
        rows,
        current_head=current_head,
        repository_root=repository_root,
        branch=branch,
        legacy_warm_boot_proof=proof,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt-log", required=True, type=Path)
    parser.add_argument("--current-head", required=True)
    parser.add_argument("--repository-root", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--warm-boot-verifier", type=Path)
    parser.add_argument("--warm-boot-manifest-root", type=Path)
    args = parser.parse_args()
    try:
        report = verify_recovery(
            args.receipt_log,
            current_head=args.current_head,
            repository_root=args.repository_root,
            branch=args.branch,
            warm_boot_verifier=args.warm_boot_verifier,
            warm_boot_manifest_root=args.warm_boot_manifest_root,
        )
    except RecoveryStateError as exc:
        print(str(exc))
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
