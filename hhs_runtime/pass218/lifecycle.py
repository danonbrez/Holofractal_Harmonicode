"""Pass 218 Iteration 8 Runtime-OS lifecycle and durability gate.

The lifecycle composes the validated Iteration-6 canonical commit boundary with
the Iteration-7 durable store. Service startup must restore or recover the most
recent admissible canonical generation before Pass-218 ingestion is enabled.
A canonical commit temporarily closes ingestion until that committed target is
durably checkpointed. Restart is receipt replay only: it never mints a new
Iteration-5 authorization and never replays a canonical mutation.
"""
from __future__ import annotations

from pathlib import Path
from threading import RLock
from typing import Any, Mapping

from hhs_runtime.pass218.commit_boundary import (
    AuthorizationJournalProtocol,
    Pass217VM81CanonicalTarget,
    Pass218CanonicalCommitBoundary,
    PreparedCanonicalAdmission,
    _copy,
    _reject_retained_source_surface,
)
from hhs_runtime.pass218.persistence_compat import (
    Pass218DurableCanonicalStore,
    Pass218PersistenceError,
)

PASS218_RUNTIME_LIFECYCLE_VERSION = "HHS-P218-RUNTIME-OS-LIFECYCLE-I8-V1"
RUNTIME_LIFECYCLE_STATUS_SCHEMA = "HHS-P218-I8-RUNTIME-LIFECYCLE-STATUS-V1"


class Pass218RuntimeLifecycleError(RuntimeError):
    pass


class Pass218RuntimeLifecycleNotReady(Pass218RuntimeLifecycleError):
    pass


def _error_code(exc: BaseException) -> str:
    text = str(exc)
    if text.startswith("P218_"):
        return text.split(":", 1)[0]
    return type(exc).__name__


class Pass218RuntimeLifecycle:
    """Own the production Pass-218 target, persistence, and ingestion gate."""

    def __init__(
        self,
        store_root: str | Path,
        *,
        target: Pass217VM81CanonicalTarget | None = None,
    ) -> None:
        self.store = Pass218DurableCanonicalStore(store_root)
        self.target = target or Pass217VM81CanonicalTarget()
        self._lock = RLock()
        self._state = "CREATED"
        self._startup_complete = False
        self._ingestion_enabled = False
        self._durability_ready = False
        self._durability_pending = False
        self._restore_state: str | None = None
        self._restore_hash72: str | None = None
        self._restored_checkpoint_sha256: str | None = None
        self._last_checkpoint_state: str | None = None
        self._last_checkpoint_sha256: str | None = None
        self._last_checkpoint_hash72: str | None = None
        self._last_error_code: str | None = None
        self._shutdown_state: str | None = None

    @property
    def store_root(self) -> Path:
        return self.store.root

    @property
    def ingestion_enabled(self) -> bool:
        with self._lock:
            return self._ingestion_enabled

    @property
    def durability_pending(self) -> bool:
        with self._lock:
            return self._durability_pending

    def _target_record(self) -> dict[str, Any]:
        return self.target.record()

    def status(self) -> dict[str, Any]:
        with self._lock:
            target_record = self._target_record()
            canonical_present = target_record["canonical_commit_count"] > 0
            record = {
                "schema": RUNTIME_LIFECYCLE_STATUS_SCHEMA,
                "lifecycle_version": PASS218_RUNTIME_LIFECYCLE_VERSION,
                "state": self._state,
                "startup_complete": self._startup_complete,
                "ingestion_enabled": self._ingestion_enabled,
                "ingestion_gate_ready": self._startup_complete and self._ingestion_enabled,
                "canonical_authority_present": canonical_present,
                "authority_ready": self._startup_complete and self._ingestion_enabled,
                "durability_ready": self._durability_ready,
                "durability_pending": self._durability_pending,
                "canonical_root_hash72": self.target.root_hash72(),
                "canonical_entry_count": target_record["canonical_entry_count"],
                "canonical_commit_count": target_record["canonical_commit_count"],
                "vm81_snapshot_hash72": target_record["vm81_snapshot_hash72"],
                "vm81_state_hash72": target_record["vm81_state_hash72"],
                "restore_state": self._restore_state,
                "restore_hash72": self._restore_hash72,
                "restored_checkpoint_sha256": self._restored_checkpoint_sha256,
                "last_checkpoint_state": self._last_checkpoint_state,
                "last_checkpoint_sha256": self._last_checkpoint_sha256,
                "last_checkpoint_hash72": self._last_checkpoint_hash72,
                "last_error_code": self._last_error_code,
                "shutdown_state": self._shutdown_state,
                "restart_new_authorization_minted": False,
                "restart_new_canonical_mutation_invoked": False,
                "canonical_learning_commit_invoked": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "verbatim_source_retained": False,
                "pass165_source_retaining_path_invoked": False,
            }
            _reject_retained_source_surface(record)
            return record

    def startup(self) -> dict[str, Any]:
        """Restore durable authority before opening the Pass-218 ingress gate.

        A missing manifest is a valid first-boot condition. A present but
        invalid/unrecoverable manifest is fail-closed for ingestion while the
        surrounding web service may remain available for diagnostics.
        """
        with self._lock:
            self._state = "STARTUP_RESTORE_REQUIRED"
            self._startup_complete = False
            self._ingestion_enabled = False
            self._durability_ready = False
            self._durability_pending = False
            self._last_error_code = None
            self._shutdown_state = None

            if not self.store.manifest_path.exists():
                self.target = Pass217VM81CanonicalTarget()
                self._state = "EMPTY_READY"
                self._startup_complete = True
                self._ingestion_enabled = True
                self._durability_ready = True
                self._restore_state = "NO_DURABLE_CANONICAL_GENERATION"
                self._restore_hash72 = None
                self._restored_checkpoint_sha256 = None
                return self.status()

            try:
                restored = self.store.restore(allow_previous_generation=True)
            except Exception as exc:
                self.target = Pass217VM81CanonicalTarget()
                self._state = "STARTUP_RECOVERY_BLOCKED"
                self._startup_complete = True
                self._ingestion_enabled = False
                self._durability_ready = False
                self._restore_state = "RESTORE_REJECTED"
                self._restore_hash72 = None
                self._restored_checkpoint_sha256 = None
                self._last_error_code = _error_code(exc)
                return self.status()

            self.target = restored.target
            self._restore_state = restored.state
            self._restore_hash72 = restored.restore_hash72
            self._restored_checkpoint_sha256 = restored.checkpoint["checkpoint_sha256"]
            self._last_checkpoint_state = "RESTORED_DURABLE_CHECKPOINT"
            self._last_checkpoint_sha256 = restored.checkpoint["checkpoint_sha256"]
            self._last_checkpoint_hash72 = restored.checkpoint["checkpoint_hash72"]
            self._state = (
                "RECOVERED_PREVIOUS_READY"
                if restored.recovered_previous_generation
                else "RESTORED_READY"
            )
            self._startup_complete = True
            self._ingestion_enabled = True
            self._durability_ready = True
            return self.status()

    def require_ingestion_ready(self) -> None:
        with self._lock:
            if not self._startup_complete or not self._ingestion_enabled:
                raise Pass218RuntimeLifecycleNotReady(
                    "P218_I8_INGESTION_GATE_CLOSED"
                )

    def canonical_boundary(self) -> Pass218CanonicalCommitBoundary:
        self.require_ingestion_ready()
        return Pass218CanonicalCommitBoundary(target=self.target)

    def _checkpoint_target_locked(self) -> dict[str, Any]:
        target_record = self._target_record()
        if target_record["canonical_commit_count"] == 0:
            self._last_checkpoint_state = "NO_CANONICAL_COMMIT_TO_CHECKPOINT"
            self._last_checkpoint_sha256 = None
            self._last_checkpoint_hash72 = None
            self._durability_ready = True
            self._durability_pending = False
            return {
                "state": "NO_CANONICAL_COMMIT_TO_CHECKPOINT",
                "idempotent_replay": True,
                "checkpoint": None,
                "manifest": None,
            }
        result = self.store.checkpoint(self.target)
        checkpoint = result["checkpoint"]
        self._last_checkpoint_state = result["state"]
        self._last_checkpoint_sha256 = checkpoint["checkpoint_sha256"]
        self._last_checkpoint_hash72 = checkpoint["checkpoint_hash72"]
        self._durability_ready = True
        self._durability_pending = False
        self._last_error_code = None
        return result

    def checkpoint_current(self) -> dict[str, Any]:
        with self._lock:
            previous_ingress = self._ingestion_enabled
            self._ingestion_enabled = False
            self._state = "CHECKPOINTING_CANONICAL_TARGET"
            try:
                result = self._checkpoint_target_locked()
            except Exception as exc:
                self._durability_ready = False
                self._durability_pending = self._target_record()["canonical_commit_count"] > 0
                self._ingestion_enabled = False
                self._state = "DURABILITY_CHECKPOINT_BLOCKED"
                self._last_error_code = _error_code(exc)
                raise Pass218RuntimeLifecycleError(
                    "P218_I8_DURABILITY_CHECKPOINT_FAILED"
                ) from exc
            self._state = (
                "EMPTY_READY"
                if self._target_record()["canonical_commit_count"] == 0
                else "DURABLE_READY"
            )
            self._ingestion_enabled = previous_ingress or self._startup_complete
            return result

    def commit_prepared(
        self,
        prepared: PreparedCanonicalAdmission,
        *,
        authorization_journal: AuthorizationJournalProtocol,
        fail_before_atomic_swap: bool = False,
        fail_before_manifest_swap: bool = False,
    ) -> dict[str, Any]:
        """Commit through I6, then close the gate until I7 durability succeeds."""
        with self._lock:
            self.require_ingestion_ready()
            self._ingestion_enabled = False
            self._state = "CANONICAL_COMMIT_IN_PROGRESS"
            boundary = Pass218CanonicalCommitBoundary(target=self.target)
            try:
                receipt = boundary.commit(
                    prepared,
                    authorization_journal=authorization_journal,
                    fail_before_atomic_swap=fail_before_atomic_swap,
                )
            except Exception:
                self._state = "COMMIT_REJECTED_READY"
                self._ingestion_enabled = True
                raise

            self._durability_ready = False
            self._durability_pending = True
            self._state = "CANONICAL_COMMITTED_DURABILITY_PENDING"
            try:
                if fail_before_manifest_swap:
                    result = self.store.checkpoint(
                        self.target,
                        fail_before_manifest_swap=True,
                    )
                else:
                    result = self.store.checkpoint(self.target)
            except Exception as exc:
                self._state = "CANONICAL_COMMITTED_DURABILITY_BLOCKED"
                self._ingestion_enabled = False
                self._durability_ready = False
                self._durability_pending = True
                self._last_error_code = _error_code(exc)
                raise Pass218RuntimeLifecycleError(
                    "P218_I8_COMMIT_DURABILITY_CHECKPOINT_FAILED"
                ) from exc

            checkpoint = result["checkpoint"]
            self._last_checkpoint_state = result["state"]
            self._last_checkpoint_sha256 = checkpoint["checkpoint_sha256"]
            self._last_checkpoint_hash72 = checkpoint["checkpoint_hash72"]
            self._durability_ready = True
            self._durability_pending = False
            self._ingestion_enabled = True
            self._state = "CANONICAL_COMMITTED_DURABLE_READY"
            self._last_error_code = None
            return {
                "schema": "HHS-P218-I8-COMMIT-DURABILITY-RECEIPT-V1",
                "lifecycle_version": PASS218_RUNTIME_LIFECYCLE_VERSION,
                "state": self._state,
                "canonical_receipt": _copy(receipt),
                "checkpoint_state": result["state"],
                "checkpoint_sha256": checkpoint["checkpoint_sha256"],
                "checkpoint_hash72": checkpoint["checkpoint_hash72"],
                "canonical_root_hash72": self.target.root_hash72(),
                "ingestion_enabled": True,
                "durability_pending": False,
                "restart_new_authorization_minted": False,
                "restart_new_canonical_mutation_invoked": False,
                "canonical_learning_commit_invoked": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "verbatim_source_retained": False,
                "pass165_source_retaining_path_invoked": False,
            }

    def retry_pending_durability(self) -> dict[str, Any]:
        with self._lock:
            if not self._durability_pending:
                return {
                    "state": "NO_PENDING_DURABILITY",
                    "canonical_root_hash72": self.target.root_hash72(),
                    "ingestion_enabled": self._ingestion_enabled,
                }
        result = self.checkpoint_current()
        with self._lock:
            self._state = "CANONICAL_COMMITTED_DURABLE_READY"
            self._ingestion_enabled = True
            return result

    def shutdown(self) -> dict[str, Any]:
        """Close ingress first and persist the latest committed target."""
        with self._lock:
            self._ingestion_enabled = False
            self._state = "CLEAN_SHUTDOWN_CHECKPOINTING"
            try:
                result = self._checkpoint_target_locked()
            except Exception as exc:
                self._state = "CLEAN_SHUTDOWN_CHECKPOINT_FAILED"
                self._shutdown_state = self._state
                self._durability_ready = False
                self._durability_pending = self._target_record()["canonical_commit_count"] > 0
                self._last_error_code = _error_code(exc)
                return self.status()
            self._shutdown_state = (
                "CLEAN_SHUTDOWN_EMPTY"
                if result["checkpoint"] is None
                else "CLEAN_SHUTDOWN_DURABLE"
            )
            self._state = self._shutdown_state
            self._durability_ready = True
            self._durability_pending = False
            return self.status()


__all__ = [
    "PASS218_RUNTIME_LIFECYCLE_VERSION",
    "RUNTIME_LIFECYCLE_STATUS_SCHEMA",
    "Pass218RuntimeLifecycle",
    "Pass218RuntimeLifecycleError",
    "Pass218RuntimeLifecycleNotReady",
]
