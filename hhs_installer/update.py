from __future__ import annotations

from pathlib import Path
from typing import Any

from .canonical import hash216
from .management import installation_status


def update_proposal(hhs_home: str | Path, target_source_identity: str) -> dict[str, Any]:
    status = installation_status(hhs_home)
    plan = {
        "operation": "update",
        "current": None if not status.get("active") else status["active"].get("active_version"),
        "target_source_identity": target_source_identity,
        "steps": [
            "verify current installation",
            "acquire and verify target",
            "calculate migration plan",
            "stage target",
            "run dependency-scoped validation",
            "activate atomically",
            "verify active target",
            "retain rollback pointer",
            "close update receipt",
        ],
        "user_state_preserved": True,
        "authorization_required": True,
    }
    return {
        "status": "BLOCKED",
        "classification": "P172_UPDATE_AUTHORIZATION_REQUIRED",
        "plan": plan,
        "plan_identity": hash216(plan, domain="HHS-P172-UPDATE-PLAN-V1"),
        "host_mutation_performed": False,
        "next_action": "review the update plan and execute through the canonical Pass 172 transaction",
    }
