"""Pass 218 Iteration 14 multi-party maintenance approval policy."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

PASS218_MULTI_PARTY_APPROVAL_VERSION = "HHS-P218-MULTI-PARTY-MAINTENANCE-APPROVAL-I14-V1"


class Pass218ApprovalError(RuntimeError):
    pass


@dataclass(frozen=True)
class Pass218ApprovalPolicy:
    required_distinct_approvers: int = 2
    approval_ttl_seconds: int = 1800
    release_ttl_seconds: int = 600

    def __post_init__(self) -> None:
        for value in (self.required_distinct_approvers, self.approval_ttl_seconds, self.release_ttl_seconds):
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise Pass218ApprovalError("P218_I14_POSITIVE_INTEGER_REQUIRED")
        if self.release_ttl_seconds > self.approval_ttl_seconds:
            raise Pass218ApprovalError("P218_I14_RELEASE_TTL_EXCEEDS_APPROVAL_TTL")

    def record(self) -> dict[str, Any]:
        return {
            "schema": "HHS-P218-I14-APPROVAL-POLICY-V1",
            "version": PASS218_MULTI_PARTY_APPROVAL_VERSION,
            "required_distinct_approvers": self.required_distinct_approvers,
            "approval_ttl_seconds": self.approval_ttl_seconds,
            "release_ttl_seconds": self.release_ttl_seconds,
            "preparer_counts_as_approver": False,
            "executor_counts_as_approver": False,
            "fence_epoch_binding_required": True,
            "quorum_required": True,
            "maintenance_remains_external": True,
            "canonical_authority_minted": False,
            "canonical_mutation_permitted": False,
            "action_authority_minted": False,
        }
