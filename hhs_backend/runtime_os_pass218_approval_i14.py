"""Runtime OS binding for Pass 218 Iteration 14 multi-party approval."""
from __future__ import annotations

import json
import os
from pathlib import Path
import time
from typing import Any, Mapping

from fastapi import Body, HTTPException

from hhs_runtime.pass218.approval_i14 import (
    Pass218ApprovalPolicy,
    Pass218ApprovalRejected,
    Pass218ApprovalValidationError,
    Pass218OperatorRegistry,
    evaluate_maintenance_release,
    validate_maintenance_release,
    validate_operator_record,
    validate_release_revocations,
)

PASS218_I14_STATUS_PATH = "/api/runtime/pass218/authority/approval/status"
PASS218_I14_EVALUATE_PATH = "/api/runtime/pass218/authority/approval/evaluate"
PASS218_I14_REVOCATION_PATH = "/api/runtime/pass218/authority/approval/revocations/record"
PASS218_I14_PREFLIGHT_PATH = "/api/runtime/pass218/authority/approval/preflight"
PASS218_I14_STATE_KEY = "hhs_pass218_multi_party_approval_i14"


def _now() -> int:
    return time.time_ns() // 1_000_000_000


def _positive_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    value = int(raw)
    if value < 1:
        raise ValueError(name + " must be positive")
    return value


def _has_route(app: Any, path: str) -> bool:
    return any(str(getattr(route, "path", "")) == path for route in app.router.routes)


class Pass218ApprovalControlPlane:
    def __init__(
        self,
        i13_control: Any,
        *,
        state_root: str | os.PathLike[str],
        registry: Pass218OperatorRegistry | None = None,
        policy: Pass218ApprovalPolicy | None = None,
    ) -> None:
        self.i13_control = i13_control
        self.state_root = Path(state_root)
        self.state_root.mkdir(parents=True, exist_ok=True)
        self.policy = policy or Pass218ApprovalPolicy(
            required_distinct_approvers=_positive_env("HHS_PASS218_I14_REQUIRED_APPROVERS", 2),
            approval_ttl_seconds=_positive_env("HHS_PASS218_I14_APPROVAL_TTL_SECONDS", 1800),
            release_ttl_seconds=_positive_env("HHS_PASS218_I14_RELEASE_TTL_SECONDS", 600),
        )
        self.registry_path = Path(
            os.environ.get(
                "HHS_PASS218_I14_OPERATOR_REGISTRY_FILE",
                str(self.state_root / "i14" / "operator-registry.json"),
            )
        )
        self.release_journal = self.state_root / "i14" / "release-journal.jsonl"
        self.revocation_journal = self.state_root / "i14" / "revocation-journal.jsonl"
        self.release_journal.parent.mkdir(parents=True, exist_ok=True)
        self.registry = registry or self._load_registry()

    def _load_registry(self) -> Pass218OperatorRegistry:
        if not self.registry_path.is_file():
            return Pass218OperatorRegistry()
        raw = json.loads(self.registry_path.read_text(encoding="utf-8"))
        records = raw.get("operators") if isinstance(raw, Mapping) else None
        if not isinstance(records, list):
            raise Pass218ApprovalValidationError("P218_I14_OPERATOR_REGISTRY_INVALID")
        return Pass218OperatorRegistry(validate_operator_record(item) for item in records)

    @staticmethod
    def _journal_count(path: Path) -> int:
        if not path.is_file():
            return 0
        return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())

    def status(self) -> dict[str, Any]:
        records = self.registry.records()
        role_counts = {
            role: sum(1 for record in records if role in record["roles"] and record.get("enabled") is True)
            for role in ("PREPARER", "APPROVER", "EXECUTOR")
        }
        preparers = {record["operator_id"] for record in records if "PREPARER" in record["roles"] and record.get("enabled") is True}
        approvers = {record["operator_id"] for record in records if "APPROVER" in record["roles"] and record.get("enabled") is True}
        executors = {record["operator_id"] for record in records if "EXECUTOR" in record["roles"] and record.get("enabled") is True}
        separation_possible = any(
            len(approvers - {preparer, executor}) >= self.policy.required_distinct_approvers
            for preparer in preparers
            for executor in executors
            if executor != preparer
        )
        return {
            "schema": "HHS-P218-I14-APPROVAL-CONTROL-STATUS-V1",
            "policy": self.policy.record(),
            "registry_path": str(self.registry_path),
            "registry_file_present": self.registry_path.is_file(),
            "configured_operator_count": len(records),
            "role_counts": role_counts,
            "approval_threshold": self.policy.required_distinct_approvers,
            "release_possible_from_registry": separation_possible,
            "recorded_release_count": self._journal_count(self.release_journal),
            "recorded_revocation_count": self._journal_count(self.revocation_journal),
            "empty_registry_is_fail_closed": True,
            "self_revocation_only": True,
            "preflight_rechecks_recorded_revocations": True,
            "maintenance_remains_external": True,
            "canonical_authority_minted": False,
            "canonical_mutation_permitted": False,
            "action_authority_minted": False,
        }

    def _find_action(self, action_hash: str) -> dict[str, Any]:
        action = self.i13_control._find_action(action_hash)
        if action is None:
            raise Pass218ApprovalRejected("P218_I14_I13_ACTION_NOT_FOUND")
        return action

    def _append_jsonl(self, path: Path, value: Mapping[str, Any]) -> None:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(dict(value), sort_keys=True, separators=(",", ":")) + "\n")

    def _append_release(self, release: Mapping[str, Any]) -> None:
        self._append_jsonl(self.release_journal, {
            "schema": "HHS-P218-I14-RELEASE-JOURNAL-V1",
            "release": dict(release),
        })

    def _revocations_for_release(self, release_hash: str) -> list[dict[str, Any]]:
        if not self.revocation_journal.is_file():
            return []
        statements: list[dict[str, Any]] = []
        for line in self.revocation_journal.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            if item.get("release_record_hash72") == release_hash and isinstance(item.get("revocation_statement"), Mapping):
                statements.append(dict(item["revocation_statement"]))
        return statements

    def evaluate(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        action_hash = str(payload.get("action_record_hash72") or "").strip()
        action = self._find_action(action_hash)
        release = evaluate_maintenance_release(
            action_record=action,
            current_status=self.i13_control.status(),
            preparer_statement=payload.get("preparer_statement") or {},
            approval_statements=payload.get("approval_statements") or [],
            executor_statement=payload.get("executor_statement") or {},
            revocation_statements=payload.get("revocation_statements") or [],
            registry=self.registry,
            policy=self.policy,
            now_epoch_seconds=_now(),
        )
        self._append_release(release)
        return release

    def record_revocation(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        raw_release = payload.get("release")
        statement = payload.get("revocation_statement")
        if not isinstance(raw_release, Mapping) or not isinstance(statement, Mapping):
            raise Pass218ApprovalValidationError("P218_I14_RELEASE_AND_REVOCATION_REQUIRED")
        release = validate_maintenance_release(raw_release, now_epoch_seconds=_now())
        revoked = validate_release_revocations(
            release=release,
            revocation_statements=[statement],
            registry=self.registry,
            policy=self.policy,
            now_epoch_seconds=_now(),
        )
        target = next(iter(revoked))
        receipt = {
            "schema": "HHS-P218-I14-RECORDED-REVOCATION-V1",
            "release_record_hash72": release["record_hash72"],
            "action_record_hash72": release["action_record_hash72"],
            "revoked_approval_message_hash72": target,
            "revocation_statement": dict(statement),
            "recorded_epoch_seconds": _now(),
            "preflight_invalidation_required": True,
            "maintenance_remains_external": True,
            "canonical_authority_minted": False,
            "canonical_mutation_permitted": False,
            "action_authority_minted": False,
        }
        self._append_jsonl(self.revocation_journal, receipt)
        return {key: value for key, value in receipt.items() if key != "revocation_statement"}

    def preflight(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        raw_release = payload.get("release")
        if not isinstance(raw_release, Mapping):
            raise Pass218ApprovalValidationError("P218_I14_RELEASE_REQUIRED")
        now = _now()
        release = validate_maintenance_release(raw_release, now_epoch_seconds=now)
        current = self.i13_control.status()
        if current.get("health") == "BLOCKED":
            raise Pass218ApprovalRejected("P218_I14_PREFLIGHT_RUNTIME_BLOCKED")
        if current.get("cluster_quorum_ready") is not True or current.get("distributed_authority_held") is not True:
            raise Pass218ApprovalRejected("P218_I14_PREFLIGHT_RUNTIME_NOT_READY")
        if current.get("distributed_fence_epoch") != release.get("distributed_fence_epoch"):
            raise Pass218ApprovalRejected("P218_I14_PREFLIGHT_FENCE_CHANGED")
        action = self._find_action(str(release.get("action_record_hash72") or ""))
        if action.get("action") != release.get("action"):
            raise Pass218ApprovalRejected("P218_I14_PREFLIGHT_ACTION_CHANGED")
        if any(
            item.get("kind") == "MAINTENANCE_RUN"
            and (item.get("record") or {}).get("action_record_hash72") == release.get("action_record_hash72")
            for item in self.i13_control.journal.records()
        ):
            raise Pass218ApprovalRejected("P218_I14_PREFLIGHT_ACTION_ALREADY_COMPLETED")
        revocations = self._revocations_for_release(release["record_hash72"])
        supplied = payload.get("revocation_statements") or []
        if not isinstance(supplied, list):
            raise Pass218ApprovalValidationError("P218_I14_PREFLIGHT_REVOCATIONS_INVALID")
        revocations.extend(item for item in supplied if isinstance(item, Mapping))
        if revocations:
            revoked = validate_release_revocations(
                release=release,
                revocation_statements=revocations,
                registry=self.registry,
                policy=self.policy,
                now_epoch_seconds=now,
            )
            if revoked:
                raise Pass218ApprovalRejected("P218_I14_PREFLIGHT_APPROVAL_REVOKED")
        return {
            "schema": "HHS-P218-I14-MAINTENANCE-PREFLIGHT-V1",
            "ok": True,
            "release_record_hash72": release["record_hash72"],
            "action_record_hash72": release["action_record_hash72"],
            "distributed_fence_epoch": release["distributed_fence_epoch"],
            "current_status_hash72": current["record_hash72"],
            "approval_quorum_satisfied": True,
            "separation_of_duties_satisfied": True,
            "current_quorum_satisfied": True,
            "current_writer_fence_satisfied": True,
            "recorded_revocations_rechecked": True,
            "maintenance_remains_external": True,
            "canonical_authority_minted": False,
            "canonical_mutation_permitted": False,
            "action_authority_minted": False,
        }


def install_pass218_i14_approval_control_plane(
    app: Any,
    i13_control: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218ApprovalControlPlane:
    existing = getattr(app.state, PASS218_I14_STATE_KEY, None)
    if isinstance(existing, Pass218ApprovalControlPlane):
        return existing
    control = Pass218ApprovalControlPlane(i13_control, state_root=state_root)
    setattr(app.state, PASS218_I14_STATE_KEY, control)

    if not _has_route(app, PASS218_I14_STATUS_PATH):
        async def approval_status() -> dict[str, Any]:
            return control.status()
        app.add_api_route(PASS218_I14_STATUS_PATH, approval_status, methods=["GET", "HEAD"], include_in_schema=True, name="hhs-pass218-approval-status-i14")

    if not _has_route(app, PASS218_I14_EVALUATE_PATH):
        async def evaluate_approval(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
            try:
                return control.evaluate(payload)
            except (Pass218ApprovalRejected, Pass218ApprovalValidationError) as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
        app.add_api_route(PASS218_I14_EVALUATE_PATH, evaluate_approval, methods=["POST"], include_in_schema=True, name="hhs-pass218-approval-evaluate-i14")

    if not _has_route(app, PASS218_I14_REVOCATION_PATH):
        async def record_revocation(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
            try:
                return control.record_revocation(payload)
            except (Pass218ApprovalRejected, Pass218ApprovalValidationError) as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
        app.add_api_route(PASS218_I14_REVOCATION_PATH, record_revocation, methods=["POST"], include_in_schema=True, name="hhs-pass218-approval-revocation-i14")

    if not _has_route(app, PASS218_I14_PREFLIGHT_PATH):
        async def approval_preflight(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
            try:
                return control.preflight(payload)
            except (Pass218ApprovalRejected, Pass218ApprovalValidationError) as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
        app.add_api_route(PASS218_I14_PREFLIGHT_PATH, approval_preflight, methods=["POST"], include_in_schema=True, name="hhs-pass218-approval-preflight-i14")

    return control


__all__ = [
    "PASS218_I14_EVALUATE_PATH",
    "PASS218_I14_PREFLIGHT_PATH",
    "PASS218_I14_REVOCATION_PATH",
    "PASS218_I14_STATE_KEY",
    "PASS218_I14_STATUS_PATH",
    "Pass218ApprovalControlPlane",
    "install_pass218_i14_approval_control_plane",
]
