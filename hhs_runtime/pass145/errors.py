from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Pass145Error(RuntimeError):
    code: str
    message: str
    phase: str = "UNKNOWN"
    object_id: str | None = None
    mutated: bool = False
    rollback_status: str = "TRANSACTION_NOT_STARTED"
    details: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        RuntimeError.__init__(self, f"{self.code}: {self.message}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": False,
            "error_code": self.code,
            "description": self.message,
            "phase": self.phase,
            "affected_object": self.object_id,
            "state_mutated": self.mutated,
            "rollback_status": self.rollback_status,
            "details": self.details or {},
        }
