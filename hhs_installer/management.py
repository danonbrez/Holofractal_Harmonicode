from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable
import json
import os
import shutil
import time

from .canonical import hash216, stable
from .journal import atomic_write_json
from .receipts import ReceiptChain, ReceiptError


class ManagementError(ValueError):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(f"{code}:{message}")
        self.code = code
        self.message = message
        self.details = dict(details or {})

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


def installation_status(home: str | Path) -> dict[str, Any]:
    root = Path(home).expanduser().resolve()
    pointer = root / "current.json"
    receipt_path = root / "install" / "receipts" / "installation-receipts.jsonl"
    active: dict[str, Any] | None = None
    pointer_error: str | None = None
    if pointer.exists():
        try:
            active = json.loads(pointer.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            pointer_error = f"{type(exc).__name__}:{exc}"
    receipt: dict[str, Any]
    try:
        chain = ReceiptChain(receipt_path)
        receipt = {"valid": True, "count": len(chain.receipts), "tip": chain.tip}
    except ReceiptError as exc:
        receipt = {"valid": False, "count": 0, "tip": None, "error": str(exc)}
    active_version = None if active is None else active.get("active_version")
    active_path = None if not active_version else root / "versions" / str(active_version)
    result = {
        "schema": "HHS_PASS_172_INSTALLATION_STATUS_V1",
        "hhs_home": str(root),
        "installed": bool(active and active_path and active_path.is_dir()),
        "active": active,
        "active_path": None if active_path is None else str(active_path),
        "pointer_error": pointer_error,
        "receipt_chain": receipt,
        "state_paths": {
            "workspaces": str(root / "state" / "workspaces"),
            "ledgers": str(root / "state" / "ledgers"),
            "receipts": str(root / "state" / "receipts"),
            "databases": str(root / "state" / "databases"),
        },
        "host_mutation_performed": False,
    }
    result["status_identity"] = hash216(result, domain="HHS-P172-INSTALLATION-STATUS-V1")
    return result


def doctor(home: str | Path) -> dict[str, Any]:
    status = installation_status(home)
    findings: list[dict[str, Any]] = []
    root = Path(home).expanduser().resolve()
    if status["pointer_error"]:
        findings.append({"classification": "P172_ACTIVE_POINTER_CORRUPT", "repairable": True})
    if status["active"] and not status["installed"]:
        findings.append({"classification": "P172_ACTIVE_VERSION_MISSING", "repairable": True})
    for relative in ("install/journals", "install/locks", "install/receipts", "install/quarantine", "logs"):
        path = root / relative
        if not path.exists():
            findings.append({"classification": "P172_MANAGED_DIRECTORY_MISSING", "path": relative, "repairable": True})
    if not status["receipt_chain"]["valid"]:
        findings.append({"classification": "P172_RECEIPT_CHAIN_INVALID", "repairable": False})
    payload = {
        "schema": "HHS_PASS_172_DOCTOR_RESULT_V1",
        "mode": "read_only",
        "status": status,
        "findings": findings,
        "repair_required": bool(findings),
        "host_mutation_performed": False,
    }
    payload["doctor_identity"] = hash216(payload, domain="HHS-P172-DOCTOR-V1")
    return payload


def repair(home: str | Path, *, authorized: bool) -> dict[str, Any]:
    root = Path(home).expanduser().resolve()
    report = doctor(root)
    plan: list[dict[str, Any]] = []
    for finding in report["findings"]:
        if finding["classification"] == "P172_MANAGED_DIRECTORY_MISSING":
            plan.append({"operation": "mkdir", "path": finding["path"]})
        elif finding["classification"] == "P172_ACTIVE_VERSION_MISSING":
            plan.append({"operation": "restore_previous_pointer"})
    plan_identity = hash216(plan, domain="HHS-P172-REPAIR-PLAN-V1")
    if not authorized:
        return {
            "status": "BLOCKED",
            "classification": "P172_REPAIR_AUTHORIZATION_REQUIRED",
            "plan": plan,
            "plan_identity": plan_identity,
            "host_mutation_performed": False,
            "next_action": "review the repair plan and rerun with --authorize",
        }
    applied: list[dict[str, Any]] = []
    for item in plan:
        if item["operation"] == "mkdir":
            (root / item["path"]).mkdir(parents=True, exist_ok=True)
            applied.append(item)
        elif item["operation"] == "restore_previous_pointer":
            pointer = root / "current.json"
            try:
                payload = json.loads(pointer.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            previous = payload.get("previous_version")
            if previous and (root / "versions" / str(previous)).is_dir():
                atomic_write_json(
                    pointer,
                    {
                        "schema": "HHS_PASS_172_ACTIVE_VERSION_V1",
                        "active_version": previous,
                        "previous_version": payload.get("active_version"),
                    },
                )
                applied.append(item)
    return {
        "status": "SUCCESS",
        "classification": "P172_REPAIR_APPLIED",
        "plan_identity": plan_identity,
        "applied": applied,
        "host_mutation_performed": bool(applied),
        "post_repair": doctor(root),
    }


def rollback(home: str | Path, *, authorized: bool) -> dict[str, Any]:
    root = Path(home).expanduser().resolve()
    pointer = root / "current.json"
    if not pointer.exists():
        raise ManagementError("P172_ROLLBACK_POINTER_MISSING", "no active installation pointer exists")
    payload = json.loads(pointer.read_text(encoding="utf-8"))
    previous = payload.get("previous_version")
    if not previous:
        raise ManagementError("P172_ROLLBACK_TARGET_MISSING", "no prior version is recorded")
    target = root / "versions" / str(previous)
    if not target.is_dir():
        raise ManagementError("P172_ROLLBACK_TARGET_CORRUPT", "prior version directory is unavailable", {"target": str(target)})
    plan = {
        "operation": "rollback",
        "from": payload.get("active_version"),
        "to": previous,
        "affected_paths": ["current.json"],
        "preserved_paths": ["state/workspaces", "state/ledgers", "state/receipts", "state/databases"],
    }
    if not authorized:
        return {
            "status": "BLOCKED",
            "classification": "P172_ROLLBACK_AUTHORIZATION_REQUIRED",
            "plan": plan,
            "plan_identity": hash216(plan, domain="HHS-P172-ROLLBACK-PLAN-V1"),
            "host_mutation_performed": False,
            "next_action": "review the rollback plan and rerun with --authorize",
        }
    atomic_write_json(
        pointer,
        {
            "schema": "HHS_PASS_172_ACTIVE_VERSION_V1",
            "active_version": previous,
            "previous_version": payload.get("active_version"),
        },
    )
    return {
        "status": "SUCCESS",
        "classification": "P172_ROLLBACK_APPLIED",
        "plan": plan,
        "host_mutation_performed": True,
        "post_rollback": installation_status(root),
    }


def uninstall(home: str | Path, *, authorized: bool, delete_user_data: bool = False) -> dict[str, Any]:
    root = Path(home).expanduser().resolve()
    managed_paths = [root / "versions", root / "runtime", root / "bin", root / "current.json"]
    preserved_paths = [
        root / "state" / "workspaces",
        root / "state" / "ledgers",
        root / "state" / "receipts",
        root / "state" / "databases",
    ]
    if delete_user_data:
        managed_paths.extend(preserved_paths)
        preserved_paths = []
    plan = {
        "delete": [str(path) for path in managed_paths if path.exists()],
        "preserve": [str(path) for path in preserved_paths],
        "delete_user_data": delete_user_data,
    }
    if not authorized:
        return {
            "status": "BLOCKED",
            "classification": "P172_UNINSTALL_AUTHORIZATION_REQUIRED",
            "plan": plan,
            "plan_identity": hash216(plan, domain="HHS-P172-UNINSTALL-PLAN-V1"),
            "host_mutation_performed": False,
            "next_action": "review the deletion manifest and rerun with --authorize",
        }
    deleted: list[str] = []
    for path in managed_paths:
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
            deleted.append(str(path))
        elif path.exists() or path.is_symlink():
            path.unlink()
            deleted.append(str(path))
    return {
        "status": "SUCCESS",
        "classification": "P172_UNINSTALL_COMPLETED",
        "deleted": deleted,
        "preserved": [str(path) for path in preserved_paths],
        "host_mutation_performed": bool(deleted),
    }


def receipt_status(home: str | Path) -> dict[str, Any]:
    root = Path(home).expanduser().resolve()
    path = root / "install" / "receipts" / "installation-receipts.jsonl"
    try:
        chain = ReceiptChain(path)
    except ReceiptError as exc:
        return {"valid": False, "classification": str(exc), "count": 0, "tip": None}
    return {
        "valid": True,
        "classification": "P172_INSTALLATION_RECEIPT_CHAIN_VALID",
        "count": len(chain.receipts),
        "tip": chain.tip,
        "receipt_classes": [receipt.receipt_class for receipt in chain.receipts],
    }
