"""Pass 218 Iteration 10 cross-host Runtime-OS canonical lifecycle.

This append-only lifecycle preserves the complete Iteration-9 process-local
ownership fence and requires a second etcd-backed distributed lease/fence before
opening Pass-218 ingress. The distributed checkpoint is the cross-host canonical
replica. A replacement host restores that I7 checkpoint into its own local I7
store before ingestion can reopen.

If distributed authority is lost between local I6/I7 commit and etcd CAS
publication, the local target is rolled back to the last distributed checkpoint,
the local replica is repaired to that state, and ingress remains fail-closed.
The I5 authorization journal remains retryable because I6 consumption is proven
by the target receipt rather than mutating the journal itself.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from hhs_runtime.pass218.commit_boundary import (
    AuthorizationJournalProtocol,
    Pass217VM81CanonicalTarget,
    PreparedCanonicalAdmission,
    _copy,
    _reject_retained_source_surface,
)
from hhs_runtime.pass218.distributed_ownership import (
    DISTRIBUTED_AUTHORITY_SCOPE,
    PASS218_DISTRIBUTED_OWNERSHIP_VERSION,
    Pass218DistributedAuthorityProtocol,
    Pass218DistributedOwnershipError,
    target_from_distributed_checkpoint,
)
from hhs_runtime.pass218.lifecycle import (
    Pass218RuntimeLifecycleError,
    Pass218RuntimeLifecycleNotReady,
)
from hhs_runtime.pass218.lifecycle_i9 import Pass218MultiprocessRuntimeLifecycle

PASS218_DISTRIBUTED_LIFECYCLE_VERSION = "HHS-P218-DISTRIBUTED-RUNTIME-LIFECYCLE-I10-V1"
DISTRIBUTED_LIFECYCLE_STATUS_SCHEMA = "HHS-P218-I10-DISTRIBUTED-LIFECYCLE-STATUS-V1"


class Pass218DistributedRuntimeLifecycle(Pass218MultiprocessRuntimeLifecycle):
    """Require exact local I9 and distributed I10 fencing for canonical work."""

    def __init__(
        self,
        store_root: str | Path,
        *,
        distributed_authority: Pass218DistributedAuthorityProtocol,
        target: Pass217VM81CanonicalTarget | None = None,
        owner_id: str | None = None,
    ) -> None:
        super().__init__(store_root, target=target, owner_id=owner_id)
        self.distributed = distributed_authority
        self._distributed_state = "UNACQUIRED"
        self._distributed_error_code: str | None = None
        self._distributed_checkpoint_sha256: str | None = None
        self._distributed_checkpoint_hash72: str | None = None
        self._distributed_checkpoint_root_hash72: str | None = None
        self._distributed_restore_state: str | None = None

    @staticmethod
    def _error_code(exc: BaseException) -> str:
        text = str(exc)
        if text.startswith("P218_"):
            return text.split(":", 1)[0]
        return type(exc).__name__

    @property
    def keepalive_interval_seconds(self) -> int:
        return max(1, int(self.distributed.lease_ttl_seconds) // 3)

    def status(self) -> dict[str, Any]:
        record = super().status()
        distributed_record = self.distributed.record
        distributed_held = self.distributed.held
        effective_ingestion = bool(record["ingestion_enabled"]) and distributed_held and (
            self._distributed_state == "PRIMARY"
        )
        record.update(
            {
                "schema": DISTRIBUTED_LIFECYCLE_STATUS_SCHEMA,
                "lifecycle_version": PASS218_DISTRIBUTED_LIFECYCLE_VERSION,
                "ingestion_enabled": effective_ingestion,
                "ingestion_gate_ready": record["startup_complete"] and effective_ingestion,
                "authority_ready": record["startup_complete"] and effective_ingestion,
                "distributed_ownership_version": PASS218_DISTRIBUTED_OWNERSHIP_VERSION,
                "distributed_state": self._distributed_state,
                "distributed_writer_authority": distributed_held,
                "distributed_backend": self.distributed.backend_name,
                "distributed_authority_scope": self.distributed.authority_scope,
                "distributed_expected_scope": DISTRIBUTED_AUTHORITY_SCOPE,
                "distributed_owner_id": (
                    None if distributed_record is None else distributed_record["owner_id"]
                ),
                "distributed_host_id": (
                    None if distributed_record is None else distributed_record["host_id"]
                ),
                "distributed_fence_epoch": (
                    None if distributed_record is None else distributed_record["fence_epoch"]
                ),
                "distributed_ownership_hash72": (
                    None
                    if distributed_record is None
                    else distributed_record["ownership_hash72"]
                ),
                "distributed_lease_ttl_seconds": self.distributed.lease_ttl_seconds,
                "distributed_keepalive_interval_seconds": self.keepalive_interval_seconds,
                "distributed_checkpoint_sha256": self._distributed_checkpoint_sha256,
                "distributed_checkpoint_hash72": self._distributed_checkpoint_hash72,
                "distributed_checkpoint_root_hash72": self._distributed_checkpoint_root_hash72,
                "distributed_restore_state": self._distributed_restore_state,
                "distributed_error_code": self._distributed_error_code,
                "cross_host_failover_permitted": True,
                "split_brain_writer_permitted": False,
                "canonical_learning_commit_invoked": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "verbatim_source_retained": False,
                "pass165_source_retaining_path_invoked": False,
            }
        )
        _reject_retained_source_surface(record)
        return record

    def _fail_closed_locked(self, *, error_code: str, state: str) -> None:
        self._ingestion_enabled = False
        self._durability_ready = False
        self._state = state
        self._last_error_code = error_code
        self._distributed_error_code = error_code
        self._distributed_state = "LOST"

    def _set_distributed_checkpoint(self, record: dict[str, Any] | None) -> None:
        if record is None:
            self._distributed_checkpoint_sha256 = None
            self._distributed_checkpoint_hash72 = None
            self._distributed_checkpoint_root_hash72 = None
            return
        self._distributed_checkpoint_sha256 = str(record["checkpoint_sha256"])
        self._distributed_checkpoint_hash72 = str(record["checkpoint_hash72"])
        self._distributed_checkpoint_root_hash72 = str(record["canonical_root_hash72"])

    def _remove_local_manifest_for_empty_rollback_locked(self) -> None:
        manifest = self.store.manifest_path
        if not manifest.exists():
            return
        manifest.unlink()
        try:
            directory_fd = os.open(str(manifest.parent), os.O_RDONLY)
        except OSError:
            return
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)

    def _sync_local_replica_locked(self, target: Pass217VM81CanonicalTarget) -> None:
        self.target = target
        if self.target.record()["canonical_commit_count"] == 0:
            self._remove_local_manifest_for_empty_rollback_locked()
            return
        self.store.checkpoint(self.target)

    def _reconcile_distributed_checkpoint_locked(self) -> None:
        remote = self.distributed.read_checkpoint(require_current=True)
        if remote is None:
            if self.target.record()["canonical_commit_count"] == 0:
                self._set_distributed_checkpoint(None)
                self._distributed_restore_state = "NO_DISTRIBUTED_CANONICAL_GENERATION"
                return
            local_result = self.store.checkpoint(self.target)
            checkpoint = local_result["checkpoint"]
            published = self.distributed.publish_checkpoint(
                checkpoint,
                expected_previous_checkpoint_sha256=None,
            )
            self._set_distributed_checkpoint(published)
            self._distributed_restore_state = "BOOTSTRAPPED_FROM_VALIDATED_I9_CANONICAL_STATE"
            return

        remote_target = target_from_distributed_checkpoint(remote)
        self._sync_local_replica_locked(remote_target)
        self._set_distributed_checkpoint(remote)
        self._distributed_restore_state = "RESTORED_DISTRIBUTED_CANONICAL_CHECKPOINT"

    def startup(self) -> dict[str, Any]:
        base = super().startup()
        with self._lock:
            self._ingestion_enabled = False
            if not self.ownership.held:
                self._distributed_state = "LOCAL_STANDBY"
                self._distributed_error_code = "P218_I10_LOCAL_I9_OWNERSHIP_REQUIRED"
                self._state = "LOCAL_OWNERSHIP_STANDBY"
                return self.status()

        try:
            acquired = self.distributed.acquire()
        except Pass218DistributedOwnershipError as exc:
            with self._lock:
                self._fail_closed_locked(
                    error_code=self._error_code(exc),
                    state="DISTRIBUTED_AUTHORITY_UNAVAILABLE",
                )
                return self.status()
        if acquired is None:
            with self._lock:
                self._distributed_state = "STANDBY"
                self._distributed_error_code = "P218_I10_DISTRIBUTED_OWNERSHIP_BUSY"
                self._state = "DISTRIBUTED_OWNERSHIP_STANDBY"
                return self.status()

        with self._lock:
            self._distributed_state = "PRIMARY"
            self._distributed_error_code = None
            try:
                self.distributed.assert_current()
                self._reconcile_distributed_checkpoint_locked()
            except Exception as exc:
                self._fail_closed_locked(
                    error_code=self._error_code(exc),
                    state="DISTRIBUTED_RECOVERY_BLOCKED",
                )
                try:
                    self.distributed.release()
                finally:
                    return self.status()

            if (
                base.get("state") == "STARTUP_RECOVERY_BLOCKED"
                and self._distributed_checkpoint_sha256 is None
            ):
                self._fail_closed_locked(
                    error_code="P218_I10_NO_DISTRIBUTED_RECOVERY_FOR_INVALID_LOCAL_STATE",
                    state="DISTRIBUTED_RECOVERY_BLOCKED",
                )
                self.distributed.release()
                return self.status()

            self._startup_complete = True
            self._durability_ready = True
            self._durability_pending = False
            self._ingestion_enabled = True
            self._last_error_code = None
            self._state = (
                "DISTRIBUTED_EMPTY_READY"
                if self.target.record()["canonical_commit_count"] == 0
                else "DISTRIBUTED_RESTORED_READY"
            )
            return self.status()

    def attempt_ownership_takeover(self) -> dict[str, Any]:
        if self.distributed.held and self.ownership.held:
            try:
                self.require_ingestion_ready()
                return self.status()
            except Pass218RuntimeLifecycleNotReady:
                pass
        return self.startup()

    def renew_distributed_authority(self) -> dict[str, Any]:
        try:
            self.distributed.renew()
        except Pass218DistributedOwnershipError as exc:
            with self._lock:
                self._fail_closed_locked(
                    error_code=self._error_code(exc),
                    state="DISTRIBUTED_LEASE_LOST",
                )
            raise Pass218RuntimeLifecycleNotReady(
                "P218_I10_DISTRIBUTED_LEASE_REQUIRED"
            ) from exc
        return self.status()

    def require_ingestion_ready(self) -> None:
        try:
            self.distributed.assert_current()
        except Pass218DistributedOwnershipError as exc:
            with self._lock:
                self._fail_closed_locked(
                    error_code=self._error_code(exc),
                    state="DISTRIBUTED_AUTHORITY_LOST",
                )
            raise Pass218RuntimeLifecycleNotReady(
                "P218_I10_DISTRIBUTED_OWNERSHIP_REQUIRED"
            ) from exc
        super().require_ingestion_ready()

    def _assert_remote_root_exact_locked(self) -> dict[str, Any] | None:
        remote = self.distributed.read_checkpoint(require_current=True)
        local_record = self.target.record()
        local_root = self.target.root_hash72()
        if remote is None:
            if local_record["canonical_commit_count"] != 0:
                raise Pass218RuntimeLifecycleError(
                    "P218_I10_DISTRIBUTED_CHECKPOINT_MISSING_FOR_LOCAL_CANONICAL_STATE"
                )
            return None
        if remote["canonical_root_hash72"] != local_root:
            raise Pass218RuntimeLifecycleError(
                "P218_I10_LOCAL_DISTRIBUTED_ROOT_DIVERGENCE"
            )
        return remote

    def checkpoint_current(self) -> dict[str, Any]:
        with self._lock:
            self.require_ingestion_ready()
            try:
                before = self._assert_remote_root_exact_locked()
                result = super().checkpoint_current()
                after = self._assert_remote_root_exact_locked()
            except Exception as exc:
                self._fail_closed_locked(
                    error_code=self._error_code(exc),
                    state="DISTRIBUTED_CHECKPOINT_VALIDATION_BLOCKED",
                )
                raise Pass218RuntimeLifecycleError(
                    "P218_I10_CHECKPOINT_DISTRIBUTED_AUTHORITY_FAILED"
                ) from exc
            if (before is None) != (after is None):
                raise Pass218RuntimeLifecycleError(
                    "P218_I10_CHECKPOINT_DISTRIBUTED_IDENTITY_CHANGED"
                )
            self._ingestion_enabled = True
            self._distributed_state = "PRIMARY"
            return result

    def _rollback_to_remote_locked(
        self,
        remote_before: dict[str, Any] | None,
    ) -> None:
        rollback_target = (
            Pass217VM81CanonicalTarget()
            if remote_before is None
            else target_from_distributed_checkpoint(remote_before)
        )
        self._sync_local_replica_locked(rollback_target)
        self._set_distributed_checkpoint(remote_before)

    def commit_prepared(
        self,
        prepared: PreparedCanonicalAdmission,
        *,
        authorization_journal: AuthorizationJournalProtocol,
        fail_before_atomic_swap: bool = False,
        fail_before_manifest_swap: bool = False,
    ) -> dict[str, Any]:
        """Commit locally, then atomically publish the sealed I7 checkpoint globally."""
        with self._lock:
            self.require_ingestion_ready()
            remote_before = self._assert_remote_root_exact_locked()
            expected_previous_sha256 = (
                None if remote_before is None else str(remote_before["checkpoint_sha256"])
            )
            expected_root = (
                Pass217VM81CanonicalTarget().root_hash72()
                if remote_before is None
                else str(remote_before["canonical_root_hash72"])
            )
            if prepared.target_root_before_hash72 != expected_root:
                raise Pass218RuntimeLifecycleError(
                    "P218_I10_PREPARED_ROOT_NOT_DISTRIBUTED_HEAD"
                )

            try:
                local_receipt = super().commit_prepared(
                    prepared,
                    authorization_journal=authorization_journal,
                    fail_before_atomic_swap=fail_before_atomic_swap,
                    fail_before_manifest_swap=fail_before_manifest_swap,
                )
                local_restore = self.store.restore(allow_previous_generation=True)
                if local_restore.target.root_hash72() != self.target.root_hash72():
                    raise Pass218RuntimeLifecycleError(
                        "P218_I10_LOCAL_DURABLE_ROOT_MISMATCH"
                    )
                checkpoint = local_restore.checkpoint
                published = self.distributed.publish_checkpoint(
                    checkpoint,
                    expected_previous_checkpoint_sha256=expected_previous_sha256,
                )
            except Exception as exc:
                try:
                    self._rollback_to_remote_locked(remote_before)
                except Exception as rollback_exc:
                    self._fail_closed_locked(
                        error_code=self._error_code(rollback_exc),
                        state="DISTRIBUTED_ROLLBACK_BLOCKED",
                    )
                    try:
                        self.distributed.release()
                    finally:
                        raise Pass218RuntimeLifecycleError(
                            "P218_I10_DISTRIBUTED_COMMIT_ROLLBACK_FAILED"
                        ) from rollback_exc
                self._fail_closed_locked(
                    error_code=self._error_code(exc),
                    state="DISTRIBUTED_PUBLICATION_BLOCKED",
                )
                self.distributed.release()
                raise Pass218RuntimeLifecycleError(
                    "P218_I10_DISTRIBUTED_CANONICAL_PUBLICATION_FAILED"
                ) from exc

            self._set_distributed_checkpoint(published)
            self._distributed_restore_state = "DISTRIBUTED_CANONICAL_CHECKPOINT_PUBLISHED"
            self._distributed_state = "PRIMARY"
            self._distributed_error_code = None
            self._ingestion_enabled = True
            self._durability_ready = True
            self._durability_pending = False
            self._state = "CANONICAL_COMMITTED_DISTRIBUTED_READY"
            result = {
                "schema": "HHS-P218-I10-DISTRIBUTED-COMMIT-DURABILITY-RECEIPT-V1",
                "lifecycle_version": PASS218_DISTRIBUTED_LIFECYCLE_VERSION,
                "state": self._state,
                "canonical_receipt": _copy(local_receipt["canonical_receipt"]),
                "local_checkpoint_sha256": local_receipt["checkpoint_sha256"],
                "local_checkpoint_hash72": local_receipt["checkpoint_hash72"],
                "distributed_checkpoint_sha256": published["checkpoint_sha256"],
                "distributed_checkpoint_hash72": published["checkpoint_hash72"],
                "distributed_checkpoint_seal_hash72": published[
                    "distributed_checkpoint_hash72"
                ],
                "canonical_root_hash72": self.target.root_hash72(),
                "distributed_fence_epoch": published["fence_epoch"],
                "distributed_owner_id": published["owner_id"],
                "distributed_host_id": published["host_id"],
                "ingestion_enabled": True,
                "durability_pending": False,
                "distributed_canonical_publication": True,
                "restart_new_authorization_minted": False,
                "restart_new_canonical_mutation_invoked": False,
                "canonical_learning_commit_invoked": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "verbatim_source_retained": False,
                "pass165_source_retaining_path_invoked": False,
            }
            _reject_retained_source_surface(result)
            return result

    def shutdown(self) -> dict[str, Any]:
        with self._lock:
            self._ingestion_enabled = False
            if self.distributed.held:
                try:
                    self.distributed.assert_current()
                except Pass218DistributedOwnershipError:
                    self.ownership.release()
                    self.distributed.release()
                    self._ownership_state = "RELEASED"
                    self._distributed_state = "RELEASED_AFTER_LOSS"
                    self._state = "DISTRIBUTED_LOST_SHUTDOWN"
                    self._shutdown_state = self._state
                    return self.status()
                try:
                    result = super().shutdown()
                finally:
                    self.distributed.release()
                    self._distributed_state = "RELEASED"
                return self.status() if result is not None else self.status()

            if self.ownership.held:
                self.ownership.release()
            self._ownership_state = "RELEASED"
            self._distributed_state = "RELEASED"
            self._state = "DISTRIBUTED_STANDBY_SHUTDOWN"
            self._shutdown_state = self._state
            return self.status()


__all__ = [
    "DISTRIBUTED_LIFECYCLE_STATUS_SCHEMA",
    "PASS218_DISTRIBUTED_LIFECYCLE_VERSION",
    "Pass218DistributedRuntimeLifecycle",
]
