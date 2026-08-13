"""Pass 218 Iteration 9 multi-process Runtime-OS canonical lifecycle.

This append-only layer composes Iteration 8 with the Iteration 9 process-shared
ownership fence. Only the process holding the current kernel flock and durable
fence epoch may open Pass-218 ingestion or invoke canonical durability paths.
Other workers remain diagnostic-only standbys. A replacement process can take
over after the prior process exits, advancing the fencing epoch before restoring
the exact Iteration-7 durable target.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from hhs_runtime.pass218.commit_boundary import Pass217VM81CanonicalTarget, _reject_retained_source_surface
from hhs_runtime.pass218.lifecycle import (
    Pass218RuntimeLifecycle,
    Pass218RuntimeLifecycleError,
    Pass218RuntimeLifecycleNotReady,
)
from hhs_runtime.pass218.ownership import (
    Pass218CanonicalOwnershipLease,
    Pass218OwnershipError,
)

PASS218_MULTIPROCESS_LIFECYCLE_VERSION = "HHS-P218-MULTIPROCESS-RUNTIME-LIFECYCLE-I9-V1"
MULTIPROCESS_LIFECYCLE_STATUS_SCHEMA = "HHS-P218-I9-MULTIPROCESS-LIFECYCLE-STATUS-V1"


class Pass218MultiprocessRuntimeLifecycle(Pass218RuntimeLifecycle):
    """Iteration-8 lifecycle guarded by one process-shared writer fence."""

    def __init__(
        self,
        store_root: str | Path,
        *,
        target: Pass217VM81CanonicalTarget | None = None,
        owner_id: str | None = None,
    ) -> None:
        super().__init__(store_root, target=target)
        self.ownership = Pass218CanonicalOwnershipLease(self.store_root, owner_id=owner_id)
        self._ownership_state = "UNACQUIRED"
        self._ownership_error_code: str | None = None

    def status(self) -> dict[str, Any]:
        record = super().status()
        ownership_record = self.ownership.record
        record.update(
            {
                "schema": MULTIPROCESS_LIFECYCLE_STATUS_SCHEMA,
                "lifecycle_version": PASS218_MULTIPROCESS_LIFECYCLE_VERSION,
                "ownership_state": self._ownership_state,
                "ownership_lock_held": self.ownership.held,
                "ownership_writer_authority": self.ownership.held,
                "ownership_owner_id": (
                    None if ownership_record is None else ownership_record["owner_id"]
                ),
                "ownership_fence_epoch": (
                    None if ownership_record is None else ownership_record["fence_epoch"]
                ),
                "ownership_hash72": (
                    None if ownership_record is None else ownership_record["ownership_hash72"]
                ),
                "ownership_error_code": self._ownership_error_code,
                "ownership_scope": "LOCK_COHERENT_POSIX_FILESYSTEM",
                "split_brain_writer_permitted": False,
            }
        )
        _reject_retained_source_surface(record)
        return record

    def _standby_status(self, *, error_code: str) -> dict[str, Any]:
        with self._lock:
            self.target = Pass217VM81CanonicalTarget()
            self._state = "OWNERSHIP_STANDBY"
            self._startup_complete = True
            self._ingestion_enabled = False
            self._durability_ready = False
            self._durability_pending = False
            self._restore_state = "OWNERSHIP_NOT_ACQUIRED"
            self._restore_hash72 = None
            self._restored_checkpoint_sha256 = None
            self._last_error_code = error_code
            self._ownership_state = "STANDBY"
            self._ownership_error_code = error_code
            return self.status()

    def startup(self) -> dict[str, Any]:
        if not self.ownership.held:
            try:
                acquired = self.ownership.acquire(blocking=False)
            except Pass218OwnershipError as exc:
                return self._standby_status(error_code=str(exc).split(":", 1)[0])
            if acquired is None:
                return self._standby_status(error_code="P218_I9_OWNERSHIP_BUSY")
        try:
            self.ownership.assert_current()
        except Pass218OwnershipError as exc:
            return self._standby_status(error_code=str(exc).split(":", 1)[0])

        self._ownership_state = "PRIMARY"
        self._ownership_error_code = None
        base = super().startup()
        if not base["ingestion_enabled"]:
            self._ownership_state = "PRIMARY_RECOVERY_BLOCKED"
        return self.status()

    def attempt_ownership_takeover(self) -> dict[str, Any]:
        """Attempt a non-blocking standby-to-primary transition."""
        if self.ownership.held:
            self.ownership.assert_current()
            return self.status()
        return self.startup()

    def require_ingestion_ready(self) -> None:
        try:
            self.ownership.assert_current()
        except Pass218OwnershipError as exc:
            raise Pass218RuntimeLifecycleNotReady(
                "P218_I9_OWNERSHIP_FENCE_REQUIRED"
            ) from exc
        super().require_ingestion_ready()

    def checkpoint_current(self) -> dict[str, Any]:
        try:
            self.ownership.assert_current()
        except Pass218OwnershipError as exc:
            raise Pass218RuntimeLifecycleError(
                "P218_I9_CHECKPOINT_OWNERSHIP_FENCE_REQUIRED"
            ) from exc
        return super().checkpoint_current()

    def shutdown(self) -> dict[str, Any]:
        if not self.ownership.held:
            with self._lock:
                self._ingestion_enabled = False
                self._state = "STANDBY_SHUTDOWN"
                self._shutdown_state = self._state
                self._ownership_state = "RELEASED"
                return self.status()
        try:
            self.ownership.assert_current()
            super().shutdown()
        finally:
            self.ownership.release()
            self._ownership_state = "RELEASED"
        return self.status()


__all__ = [
    "MULTIPROCESS_LIFECYCLE_STATUS_SCHEMA",
    "PASS218_MULTIPROCESS_LIFECYCLE_VERSION",
    "Pass218MultiprocessRuntimeLifecycle",
]
