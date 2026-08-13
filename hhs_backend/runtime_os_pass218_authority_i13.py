"""Runtime-OS/API binding for Pass 218 Iteration 13 observability.

This module is a diagnostic/operator control plane over an already-installed
Pass 218 lifecycle.  It reads I9-I12 state, persists sealed operator intents and
maintenance-run receipts, and never performs canonical ownership or mutation.
"""
from __future__ import annotations

import calendar
import os
from pathlib import Path
import ssl
import time
from typing import Any, Mapping

from fastapi import Body, HTTPException

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.observability_i13 import (
    Pass218AuthorityObservabilityValidationError,
    Pass218ObservabilityPolicy,
    Pass218OperatorActionRejected,
    Pass218OperatorJournal,
    Pass218OperatorOrchestrator,
    build_authority_observability_status,
    seal_maintenance_run_receipt,
)

PASS218_AUTHORITY_STATUS_PATH = "/api/runtime/pass218/authority/status"
PASS218_AUTHORITY_ALERTS_PATH = "/api/runtime/pass218/authority/alerts"
PASS218_AUTHORITY_ACTION_PREPARE_PATH = "/api/runtime/pass218/authority/actions/prepare"
PASS218_AUTHORITY_RUN_RECORD_PATH = "/api/runtime/pass218/authority/runs/record"
PASS218_AUTHORITY_CONTROL_STATE_KEY = "hhs_pass218_authority_control_plane_i13"


def _positive_env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    value = int(raw)
    if value < 1:
        raise ValueError(name + " must be positive")
    return value


def _optional_nonnegative_env_int(name: str) -> int | None:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return None
    value = int(raw)
    if value < 0:
        raise ValueError(name + " must be nonnegative")
    return value


def _now_epoch_seconds() -> int:
    return time.time_ns() // 1_000_000_000


def _certificate_not_after_epoch(cert_file: str | os.PathLike[str] | None) -> int | None:
    if cert_file is None:
        return None
    path = Path(cert_file)
    if not path.is_file():
        return None
    try:
        decoded = ssl._ssl._test_decode_cert(str(path))  # type: ignore[attr-defined]
        raw = decoded.get("notAfter")
        if not isinstance(raw, str) or not raw.strip():
            return None
        parsed = time.strptime(raw, "%b %d %H:%M:%S %Y %Z")
        return int(calendar.timegm(parsed))
    except Exception:
        return None


def _has_exact_route(app: Any, path: str) -> bool:
    return any(str(getattr(route, "path", "")) == path for route in app.router.routes)


class Pass218AuthorityControlPlane:
    def __init__(
        self,
        lifecycle: Any,
        *,
        state_root: str | os.PathLike[str],
        policy: Pass218ObservabilityPolicy | None = None,
    ) -> None:
        self.lifecycle = lifecycle
        self.state_root = Path(state_root)
        self.policy = policy or Pass218ObservabilityPolicy.build(
            certificate_warning_seconds=_positive_env_int(
                "HHS_PASS218_CERTIFICATE_WARNING_SECONDS",
                2592000,
            ),
            snapshot_max_age_seconds=_positive_env_int(
                "HHS_PASS218_SNAPSHOT_MAX_AGE_SECONDS",
                86400,
            ),
            rehearsal_max_age_seconds=_positive_env_int(
                "HHS_PASS218_REHEARSAL_MAX_AGE_SECONDS",
                604800,
            ),
            max_pending_operator_actions=_positive_env_int(
                "HHS_PASS218_MAX_PENDING_OPERATOR_ACTIONS",
                8,
            ),
        )
        self.journal = Pass218OperatorJournal(
            self.state_root / "i13" / "operator-journal.jsonl"
        )
        self.orchestrator = Pass218OperatorOrchestrator(journal=self.journal)

    def _latest_snapshot_epoch(self) -> int | None:
        explicit = _optional_nonnegative_env_int(
            "HHS_PASS218_LATEST_SNAPSHOT_EPOCH_SECONDS"
        )
        if explicit is not None:
            return explicit
        return self.journal.latest_success_epoch("REQUEST_SNAPSHOT_REHEARSAL")

    def _latest_rehearsal_epoch(self) -> int | None:
        explicit = _optional_nonnegative_env_int(
            "HHS_PASS218_LATEST_REHEARSAL_EPOCH_SECONDS"
        )
        if explicit is not None:
            return explicit
        return self.journal.latest_success_epoch("REQUEST_SNAPSHOT_REHEARSAL")

    def status(self) -> dict[str, Any]:
        lifecycle_status = self.lifecycle.status()
        cert_epoch = _optional_nonnegative_env_int(
            "HHS_PASS218_CLIENT_CERT_NOT_AFTER_EPOCH_SECONDS"
        )
        if cert_epoch is None:
            cert_epoch = _certificate_not_after_epoch(
                os.environ.get("HHS_PASS218_ETCD_CLIENT_CERT_FILE")
            )
        return build_authority_observability_status(
            lifecycle_status=lifecycle_status,
            policy=self.policy,
            now_epoch_seconds=_now_epoch_seconds(),
            certificate_not_after_epoch_seconds=cert_epoch,
            latest_snapshot_epoch_seconds=self._latest_snapshot_epoch(),
            latest_rehearsal_epoch_seconds=self._latest_rehearsal_epoch(),
            pending_operator_actions=self.journal.pending_action_count(),
        )

    def alerts(self) -> dict[str, Any]:
        status = self.status()
        return {
            "schema": "HHS-P218-I13-AUTHORITY-ALERTS-PROJECTION-V1",
            "status_hash72": status["record_hash72"],
            "health": status["health"],
            "alerts": list(status["alerts"]),
            "alert_count": status["alert_count"],
            "diagnostic_only": True,
            "canonical_authority_minted": False,
            "canonical_mutation_permitted": False,
            "action_authority_minted": False,
        }

    def prepare_action(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        status = self.status()
        operator_id = str(payload.get("operator_id") or "").strip()
        action = str(payload.get("action") or "").strip().upper()
        prepared_epoch = _now_epoch_seconds()
        request_id = str(payload.get("request_id") or "").strip()
        if not request_id:
            request_id = "i13-" + hash72_digest(
                {"domain": "HHS-P218-I13-OPERATOR-REQUEST-ID"},
                {
                    "operator_id": operator_id,
                    "action": action,
                    "status_hash72": status["record_hash72"],
                    "prepared_epoch_seconds": prepared_epoch,
                },
            )
        return self.orchestrator.prepare(
            request_id=request_id,
            operator_id=operator_id,
            action=action,
            status=status,
            prepared_epoch_seconds=prepared_epoch,
        )

    def _find_action(self, action_record_hash72: str) -> dict[str, Any] | None:
        for item in reversed(self.journal.records()):
            if item.get("kind") != "OPERATOR_ACTION":
                continue
            record = item.get("record") or {}
            if record.get("record_hash72") == action_record_hash72:
                return record
        return None

    def record_run(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        action_hash = str(payload.get("action_record_hash72") or "").strip()
        action_record = self._find_action(action_hash)
        if action_record is None:
            raise Pass218AuthorityObservabilityValidationError(
                "P218_I13_ACTION_RECORD_NOT_FOUND"
            )
        if any(
            item.get("kind") == "MAINTENANCE_RUN"
            and (item.get("record") or {}).get("action_record_hash72") == action_hash
            for item in self.journal.records()
        ):
            raise Pass218AuthorityObservabilityValidationError(
                "P218_I13_ACTION_ALREADY_COMPLETED"
            )
        after_status = self.status()
        completed_epoch = _now_epoch_seconds()
        started_epoch = payload.get("started_epoch_seconds", action_record["prepared_epoch_seconds"])
        run_id = str(payload.get("run_id") or "").strip()
        if not run_id:
            run_id = "i13-run-" + hash72_digest(
                {"domain": "HHS-P218-I13-RUN-ID"},
                {
                    "action_record_hash72": action_hash,
                    "completed_epoch_seconds": completed_epoch,
                    "after_status_hash72": after_status["record_hash72"],
                },
            )
        receipt = seal_maintenance_run_receipt(
            run_id=run_id,
            action_record_hash72=action_hash,
            operator_id=action_record["operator_id"],
            action=action_record["action"],
            outcome=str(payload.get("outcome") or "").strip().upper(),
            started_epoch_seconds=started_epoch,
            completed_epoch_seconds=completed_epoch,
            before_status_hash72=action_record["status_hash72"],
            after_status_hash72=after_status["record_hash72"],
            external_operation_executed=bool(payload.get("external_operation_executed", False)),
            canonical_target_changed=bool(payload.get("canonical_target_changed", False)),
            authority_minted=bool(payload.get("authority_minted", False)),
        )
        self.journal.append_run_receipt(receipt)
        return receipt


def install_pass218_authority_control_plane(
    app: Any,
    lifecycle: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218AuthorityControlPlane:
    existing = getattr(app.state, PASS218_AUTHORITY_CONTROL_STATE_KEY, None)
    if isinstance(existing, Pass218AuthorityControlPlane):
        return existing

    control = Pass218AuthorityControlPlane(lifecycle, state_root=state_root)
    setattr(app.state, PASS218_AUTHORITY_CONTROL_STATE_KEY, control)

    if not _has_exact_route(app, PASS218_AUTHORITY_STATUS_PATH):
        async def authority_status() -> dict[str, Any]:
            return control.status()

        app.add_api_route(
            PASS218_AUTHORITY_STATUS_PATH,
            authority_status,
            methods=["GET", "HEAD"],
            include_in_schema=True,
            name="hhs-pass218-authority-status-i13",
        )

    if not _has_exact_route(app, PASS218_AUTHORITY_ALERTS_PATH):
        async def authority_alerts() -> dict[str, Any]:
            return control.alerts()

        app.add_api_route(
            PASS218_AUTHORITY_ALERTS_PATH,
            authority_alerts,
            methods=["GET", "HEAD"],
            include_in_schema=True,
            name="hhs-pass218-authority-alerts-i13",
        )

    if not _has_exact_route(app, PASS218_AUTHORITY_ACTION_PREPARE_PATH):
        async def prepare_authority_action(
            payload: dict[str, Any] = Body(...),
        ) -> dict[str, Any]:
            try:
                return control.prepare_action(payload)
            except (Pass218OperatorActionRejected, Pass218AuthorityObservabilityValidationError) as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc

        app.add_api_route(
            PASS218_AUTHORITY_ACTION_PREPARE_PATH,
            prepare_authority_action,
            methods=["POST"],
            include_in_schema=True,
            name="hhs-pass218-authority-action-prepare-i13",
        )

    if not _has_exact_route(app, PASS218_AUTHORITY_RUN_RECORD_PATH):
        async def record_authority_run(
            payload: dict[str, Any] = Body(...),
        ) -> dict[str, Any]:
            try:
                return control.record_run(payload)
            except Pass218AuthorityObservabilityValidationError as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc

        app.add_api_route(
            PASS218_AUTHORITY_RUN_RECORD_PATH,
            record_authority_run,
            methods=["POST"],
            include_in_schema=True,
            name="hhs-pass218-authority-run-record-i13",
        )

    return control


__all__ = [
    "PASS218_AUTHORITY_ACTION_PREPARE_PATH",
    "PASS218_AUTHORITY_ALERTS_PATH",
    "PASS218_AUTHORITY_CONTROL_STATE_KEY",
    "PASS218_AUTHORITY_RUN_RECORD_PATH",
    "PASS218_AUTHORITY_STATUS_PATH",
    "Pass218AuthorityControlPlane",
    "install_pass218_authority_control_plane",
]
