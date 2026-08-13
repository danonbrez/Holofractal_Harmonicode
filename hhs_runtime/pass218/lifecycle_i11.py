"""Pass 218 Iteration 11 quorum-gated Runtime-OS lifecycle.

The I10 lifecycle remains the canonical cross-host authority. This subclass adds
an operational gate: the configured etcd cluster must present a consistent
member identity, a reachable majority, a leader, and a successful linearizable
read before I10 ownership can be acquired or retained.

Operational probes are diagnostic-only. They never mint authorization, mutate a
canonical target, or change the I10 fencing/checkpoint protocol. Loss of quorum
closes ingestion and releases distributed writer authority fail-closed.
"""
from __future__ import annotations

from typing import Any

from hhs_runtime.pass218.commit_boundary import (
    AuthorizationJournalProtocol,
    PreparedCanonicalAdmission,
    _copy,
    _reject_retained_source_surface,
)
from hhs_runtime.pass218.distributed_ownership import Pass218DistributedOwnershipError
from hhs_runtime.pass218.lifecycle import (
    Pass218RuntimeLifecycleError,
    Pass218RuntimeLifecycleNotReady,
)
from hhs_runtime.pass218.lifecycle_i9 import Pass218MultiprocessRuntimeLifecycle
from hhs_runtime.pass218.lifecycle_i10 import Pass218DistributedRuntimeLifecycle
from hhs_runtime.pass218.operational_hardening_i11 import (
    OPERATIONAL_AUTHORITY_SCOPE,
    PASS218_OPERATIONAL_HARDENING_VERSION,
    Pass218EtcdClusterMonitor,
    Pass218OperationalHardeningError,
)

PASS218_OPERATIONAL_LIFECYCLE_VERSION = "HHS-P218-DISTRIBUTED-OPERATIONAL-LIFECYCLE-I11-V1"
OPERATIONAL_LIFECYCLE_STATUS_SCHEMA = "HHS-P218-I11-DISTRIBUTED-OPERATIONAL-LIFECYCLE-STATUS-V1"


class Pass218OperationallyHardenedRuntimeLifecycle(Pass218DistributedRuntimeLifecycle):
    """Require I9 + I10 authority and an independently proven etcd quorum."""

    def __init__(
        self,
        store_root,
        *,
        distributed_authority,
        cluster_monitor: Pass218EtcdClusterMonitor,
        target=None,
        owner_id: str | None = None,
    ) -> None:
        super().__init__(
            store_root,
            distributed_authority=distributed_authority,
            target=target,
            owner_id=owner_id,
        )
        self.cluster_monitor = cluster_monitor
        self._operational_state = "UNPROBED"
        self._operational_error_code: str | None = None
        self._last_cluster_probe: dict[str, Any] | None = None
        self._quorum_loss_count = 0
        self._quorum_recovery_count = 0

    @staticmethod
    def _operational_error(exc: BaseException) -> str:
        text = str(exc)
        if text.startswith("P218_"):
            return text.split(":", 1)[0]
        return type(exc).__name__

    def _set_probe_locked(self, probe: dict[str, Any]) -> None:
        previous_ready = bool(
            self._last_cluster_probe is not None
            and self._last_cluster_probe.get("quorum_ready") is True
        )
        current_ready = probe.get("quorum_ready") is True
        if previous_ready and not current_ready:
            self._quorum_loss_count += 1
        if not previous_ready and current_ready and self._last_cluster_probe is not None:
            self._quorum_recovery_count += 1
        self._last_cluster_probe = _copy(probe)
        self._operational_state = "QUORUM_READY" if current_ready else "QUORUM_BLOCKED"
        self._operational_error_code = None if current_ready else "P218_I11_ETCD_QUORUM_UNAVAILABLE"

    def status(self) -> dict[str, Any]:
        record = super().status()
        probe = self._last_cluster_probe
        quorum_ready = bool(probe is not None and probe.get("quorum_ready") is True)
        effective_ingestion = bool(record["ingestion_enabled"]) and quorum_ready
        record.update(
            {
                "schema": OPERATIONAL_LIFECYCLE_STATUS_SCHEMA,
                "lifecycle_version": PASS218_OPERATIONAL_LIFECYCLE_VERSION,
                "operational_hardening_version": PASS218_OPERATIONAL_HARDENING_VERSION,
                "operational_authority_scope": OPERATIONAL_AUTHORITY_SCOPE,
                "operational_state": self._operational_state,
                "operational_error_code": self._operational_error_code,
                "ingestion_enabled": effective_ingestion,
                "ingestion_gate_ready": record["startup_complete"] and effective_ingestion,
                "authority_ready": record["startup_complete"] and effective_ingestion,
                "cluster_quorum_ready": quorum_ready,
                "cluster_identity_consistent": (
                    False if probe is None else bool(probe["identity_consistent"])
                ),
                "cluster_linearizable_read_ready": (
                    False if probe is None else bool(probe["linearizable_read_ready"])
                ),
                "cluster_name": (
                    self.cluster_monitor.config.cluster_name
                    if probe is None
                    else probe["cluster_name"]
                ),
                "cluster_expected_member_count": self.cluster_monitor.config.member_count,
                "cluster_quorum_size": self.cluster_monitor.config.quorum_size,
                "cluster_reachable_member_count": (
                    0 if probe is None else probe["reachable_member_count"]
                ),
                "cluster_unavailable_member_count": (
                    self.cluster_monitor.config.member_count
                    if probe is None
                    else probe["unavailable_member_count"]
                ),
                "cluster_id": None if probe is None else probe["cluster_id"],
                "cluster_member_ids": [] if probe is None else list(probe["member_ids"]),
                "cluster_leader_ids": [] if probe is None else list(probe["leader_ids"]),
                "cluster_probe_hash72": None if probe is None else probe["probe_hash72"],
                "quorum_loss_count": self._quorum_loss_count,
                "quorum_recovery_count": self._quorum_recovery_count,
                "tls_server_verification_required": True,
                "client_certificate_authentication_required": True,
                "disaster_recovery_requires_new_fence": True,
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

    def probe_cluster(self, *, fail_closed: bool = True) -> dict[str, Any]:
        try:
            probe = self.cluster_monitor.probe()
        except Exception as exc:
            with self._lock:
                self._operational_state = "QUORUM_BLOCKED"
                self._operational_error_code = self._operational_error(exc)
                self._ingestion_enabled = False
                self._durability_ready = False
            if fail_closed and self.distributed.held:
                self.distributed.release()
            raise Pass218RuntimeLifecycleNotReady(
                "P218_I11_OPERATIONAL_QUORUM_REQUIRED"
            ) from exc

        with self._lock:
            self._set_probe_locked(probe)
            if probe["quorum_ready"] is not True:
                self._ingestion_enabled = False
                self._durability_ready = False
                self._state = "DISTRIBUTED_OPERATIONAL_QUORUM_BLOCKED"
        if probe["quorum_ready"] is not True and fail_closed:
            if self.distributed.held:
                self.distributed.release()
            raise Pass218RuntimeLifecycleNotReady(
                "P218_I11_OPERATIONAL_QUORUM_REQUIRED"
            )
        return probe

    def startup(self) -> dict[str, Any]:
        try:
            self.cluster_monitor.require_quorum_ready()
        except Pass218OperationalHardeningError as exc:
            base = Pass218MultiprocessRuntimeLifecycle.startup(self)
            with self._lock:
                self._last_cluster_probe = self.cluster_monitor.last_probe
                self._operational_state = "QUORUM_BLOCKED"
                self._operational_error_code = self._operational_error(exc)
                self._ingestion_enabled = False
                self._durability_ready = False
                self._state = "DISTRIBUTED_OPERATIONAL_QUORUM_BLOCKED"
                if not base.get("startup_complete"):
                    self._startup_complete = bool(base.get("startup_complete"))
                return self.status()

        result = super().startup()
        try:
            probe = self.cluster_monitor.require_quorum_ready()
        except Pass218OperationalHardeningError as exc:
            with self._lock:
                self._operational_state = "QUORUM_BLOCKED"
                self._operational_error_code = self._operational_error(exc)
                self._ingestion_enabled = False
                self._durability_ready = False
                self._state = "DISTRIBUTED_OPERATIONAL_QUORUM_BLOCKED"
            if self.distributed.held:
                self.distributed.release()
            return self.status()
        with self._lock:
            self._set_probe_locked(probe)
            if result.get("ingestion_enabled") is True:
                self._operational_state = "QUORUM_READY"
                self._operational_error_code = None
            return self.status()

    def renew_distributed_authority(self) -> dict[str, Any]:
        try:
            probe = self.cluster_monitor.require_quorum_ready()
        except Pass218OperationalHardeningError as exc:
            with self._lock:
                self._operational_state = "QUORUM_BLOCKED"
                self._operational_error_code = self._operational_error(exc)
                self._ingestion_enabled = False
                self._durability_ready = False
                self._state = "DISTRIBUTED_OPERATIONAL_QUORUM_LOST"
            if self.distributed.held:
                self.distributed.release()
            raise Pass218RuntimeLifecycleNotReady(
                "P218_I11_OPERATIONAL_QUORUM_REQUIRED"
            ) from exc
        with self._lock:
            self._set_probe_locked(probe)
        result = super().renew_distributed_authority()
        with self._lock:
            self._operational_state = "QUORUM_READY"
            self._operational_error_code = None
            return self.status() if result is not None else self.status()

    def require_ingestion_ready(self) -> None:
        try:
            probe = self.cluster_monitor.require_quorum_ready()
        except Pass218OperationalHardeningError as exc:
            with self._lock:
                self._operational_state = "QUORUM_BLOCKED"
                self._operational_error_code = self._operational_error(exc)
                self._ingestion_enabled = False
                self._durability_ready = False
                self._state = "DISTRIBUTED_OPERATIONAL_QUORUM_LOST"
            if self.distributed.held:
                self.distributed.release()
            raise Pass218RuntimeLifecycleNotReady(
                "P218_I11_OPERATIONAL_QUORUM_REQUIRED"
            ) from exc
        with self._lock:
            self._set_probe_locked(probe)
        super().require_ingestion_ready()

    def checkpoint_current(self) -> dict[str, Any]:
        self.require_ingestion_ready()
        result = super().checkpoint_current()
        try:
            probe = self.cluster_monitor.require_quorum_ready()
        except Pass218OperationalHardeningError as exc:
            with self._lock:
                self._operational_state = "QUORUM_BLOCKED"
                self._operational_error_code = self._operational_error(exc)
                self._ingestion_enabled = False
                self._durability_ready = False
                self._state = "DISTRIBUTED_OPERATIONAL_QUORUM_LOST_AFTER_CHECKPOINT"
            if self.distributed.held:
                self.distributed.release()
            raise Pass218RuntimeLifecycleError(
                "P218_I11_POST_CHECKPOINT_QUORUM_VALIDATION_FAILED"
            ) from exc
        with self._lock:
            self._set_probe_locked(probe)
        return result

    def commit_prepared(
        self,
        prepared: PreparedCanonicalAdmission,
        *,
        authorization_journal: AuthorizationJournalProtocol,
        fail_before_atomic_swap: bool = False,
        fail_before_manifest_swap: bool = False,
    ) -> dict[str, Any]:
        self.require_ingestion_ready()
        result = super().commit_prepared(
            prepared,
            authorization_journal=authorization_journal,
            fail_before_atomic_swap=fail_before_atomic_swap,
            fail_before_manifest_swap=fail_before_manifest_swap,
        )
        try:
            probe = self.cluster_monitor.require_quorum_ready()
        except Pass218OperationalHardeningError as exc:
            # The I10 publication is already canonical. Do not roll it back.
            # Close ingress and force a new fenced owner after quorum recovers.
            with self._lock:
                self._operational_state = "QUORUM_BLOCKED"
                self._operational_error_code = self._operational_error(exc)
                self._ingestion_enabled = False
                self._durability_ready = False
                self._state = "DISTRIBUTED_OPERATIONAL_QUORUM_LOST_AFTER_COMMIT"
            if self.distributed.held:
                self.distributed.release()
            raise Pass218RuntimeLifecycleError(
                "P218_I11_POST_COMMIT_QUORUM_VALIDATION_FAILED"
            ) from exc
        with self._lock:
            self._set_probe_locked(probe)
            self._operational_state = "QUORUM_READY"
            self._operational_error_code = None
            self._ingestion_enabled = True
            self._durability_ready = True
        return result


__all__ = [
    "OPERATIONAL_LIFECYCLE_STATUS_SCHEMA",
    "PASS218_OPERATIONAL_LIFECYCLE_VERSION",
    "Pass218OperationallyHardenedRuntimeLifecycle",
]
