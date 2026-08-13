"""Pass 218 Iteration 16 distributed consumption coordinator."""
from __future__ import annotations

import time
from typing import Any, Mapping

from hhs_backend.pass218_execution_i15_control import Pass218ExecutionControlPlane
from hhs_runtime.pass218.distributed_consumption_i16 import (
    PASS218_DISTRIBUTED_CONSUMPTION_VERSION,
    Pass218DistributedConsumptionLedgerProtocol,
    Pass218DistributedConsumptionValidationError,
    migrate_current_fence_local_claims,
    mirror_distributed_claim_to_local,
    synchronize_distributed_claims_to_local,
)
from hhs_runtime.pass218.execution_i15 import (
    Pass218ExecutionValidationError,
    seal_release_claim,
    validate_release_claim,
)


class Pass218DistributedExecutionControlPlane(Pass218ExecutionControlPlane):
    def __init__(
        self,
        i13_control: Any,
        i14_control: Any,
        *,
        state_root: str,
        distributed_ledger: Pass218DistributedConsumptionLedgerProtocol | None,
    ) -> None:
        super().__init__(i13_control, i14_control, state_root=state_root)
        self.distributed_ledger = distributed_ledger
        self.mirrored_count = 0
        self.migrated_count = 0
        self.stale_count = 0
        self.last_i16_error_code: str | None = None

    @staticmethod
    def _code(exc: BaseException) -> str:
        text = str(exc)
        return text.split(":", 1)[0] if text.startswith("P218_") else type(exc).__name__

    def synchronize(self) -> dict[str, Any]:
        if self.distributed_ledger is None:
            return {"distributed_mode": False, "mirrored": 0, "migrated": 0, "stale": 0}
        try:
            mirrored = synchronize_distributed_claims_to_local(self.journal, self.distributed_ledger)
            migration = migrate_current_fence_local_claims(self.journal, self.distributed_ledger)
            self.mirrored_count += mirrored
            self.migrated_count += int(migration["migrated_local_claim_count"])
            self.stale_count = int(migration["stale_unreplicated_local_claim_count"])
            if self.stale_count:
                raise Pass218DistributedConsumptionValidationError(
                    "P218_I16_STALE_UNREPLICATED_LOCAL_CLAIM"
                )
            self.last_i16_error_code = None
            return {
                "distributed_mode": True,
                "mirrored": mirrored,
                "migrated": int(migration["migrated_local_claim_count"]),
                "stale": 0,
            }
        except Exception as exc:
            self.last_i16_error_code = self._code(exc)
            raise

    def _local_claim_hashes(self) -> set[str]:
        result: set[str] = set()
        for path in self.journal.claims.glob("*.json"):
            raw = self.journal._read(path)
            if raw is not None:
                result.add(validate_release_claim(raw)["record_hash72"])
        return result

    def status(self) -> dict[str, Any]:
        base = super().status()
        if self.distributed_ledger is None:
            projection = {
                "distributed_consumption_configured": False,
                "distributed_ledger_entry_count": 0,
                "unmirrored_distributed_claim_count": 0,
                "local_only_claim_count": 0,
                "i16_error_code": None,
            }
        else:
            try:
                entries = self.distributed_ledger.entries()
                remote = {entry["claim_record_hash72"] for entry in entries}
                local = self._local_claim_hashes()
                projection = {
                    "distributed_consumption_configured": True,
                    "distributed_ledger_entry_count": len(entries),
                    "unmirrored_distributed_claim_count": len(remote - local),
                    "local_only_claim_count": len(local - remote),
                    "i16_error_code": self.last_i16_error_code,
                }
            except Exception as exc:
                projection = {
                    "distributed_consumption_configured": True,
                    "distributed_ledger_entry_count": None,
                    "unmirrored_distributed_claim_count": None,
                    "local_only_claim_count": None,
                    "i16_error_code": self._code(exc),
                }
        return {
            **base,
            "schema": "HHS-P218-I16-EXECUTION-CONTROL-STATUS-V1",
            "distributed_consumption_version": PASS218_DISTRIBUTED_CONSUMPTION_VERSION,
            **projection,
            "mirrored_from_distributed_total": self.mirrored_count,
            "migrated_local_claim_total": self.migrated_count,
            "stale_unreplicated_local_claim_count": self.stale_count,
            "distributed_claim_precedes_local_mirror": self.distributed_ledger is not None,
            "canonical_authority_minted": False,
            "canonical_mutation_permitted": False,
            "action_authority_minted": False,
        }

    def claim(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if self.distributed_ledger is None:
            return super().claim(payload)
        self.synchronize()
        release = payload.get("release")
        if not isinstance(release, Mapping):
            raise Pass218ExecutionValidationError("P218_I15_RELEASE_REQUIRED")
        revocations = payload.get("revocation_statements") or []
        if not isinstance(revocations, list):
            raise Pass218ExecutionValidationError("P218_I15_REVOCATIONS_INVALID")
        preflight = self.i14_control.preflight(
            {"release": dict(release), "revocation_statements": revocations}
        )
        claim = seal_release_claim(
            release=release,
            preflight=preflight,
            claimed_epoch_ns=time.time_ns(),
        )
        self.distributed_ledger.consume_claim(claim)
        mirror_distributed_claim_to_local(self.journal, claim)
        return claim

    def attest(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if self.distributed_ledger is not None:
            self.synchronize()
        return super().attest(payload)

    def reconcile(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if self.distributed_ledger is not None:
            self.synchronize()
        return super().reconcile(payload)

    def distributed_status(self) -> dict[str, Any]:
        status = self.status()
        return {
            "schema": "HHS-P218-I16-DISTRIBUTED-CONSUMPTION-PROJECTION-V1",
            "distributed_consumption_version": status["distributed_consumption_version"],
            "distributed_consumption_configured": status["distributed_consumption_configured"],
            "distributed_ledger_entry_count": status["distributed_ledger_entry_count"],
            "unmirrored_distributed_claim_count": status["unmirrored_distributed_claim_count"],
            "local_only_claim_count": status["local_only_claim_count"],
            "stale_unreplicated_local_claim_count": status["stale_unreplicated_local_claim_count"],
            "i16_error_code": status["i16_error_code"],
            "canonical_authority_minted": False,
            "canonical_mutation_permitted": False,
            "action_authority_minted": False,
        }


__all__ = ["Pass218DistributedExecutionControlPlane"]
