from __future__ import annotations
import copy
from typing import Any
from .common import sha256_json


class DeterministicVM81TestAuthority:
    """A strict VM81-shaped admission adapter for isolated pass tests.

    It accepts only a complete closure proof and generates a deterministic
    Hash72-compatible test receipt from the admitted candidate. It is clearly
    marked TEST_AUTHORITY and is never used by production API routes.
    """
    def __init__(self):
        self.sequence = 0

    def admit(self, candidate: dict[str, Any], proof: dict[str, Any]) -> dict[str, Any]:
        if not proof.get("omega_closure"):
            return {"admitted": False}
        self.sequence += 1
        digest = sha256_json({"sequence": self.sequence, "candidate": candidate, "proof": proof})
        return {
            "admitted": True,
            "authoritative_state": {
                "cycle": self.sequence,
                "status": "COMMITTED",
                "candidate_digest": sha256_json(candidate),
            },
            "hash72_receipt": {
                "schema": "HHS_PASS152_TEST_HASH72_RECEIPT_V1",
                "receipt_hash72": digest,
                "sequence": self.sequence,
                "authority_classification": "DETERMINISTIC_VM81_TEST_AUTHORITY",
            },
            "authority_audit": {"authorized": True, "source": "DeterministicVM81TestAuthority"},
        }


class HHSRuntimeControllerAuthority:
    """Production adapter for the inherited HHSRuntimeController public API."""
    def __init__(self, runtime_controller):
        self.runtime_controller = runtime_controller

    def admit(self, candidate: dict[str, Any], proof: dict[str, Any]) -> dict[str, Any]:
        if not proof.get("omega_closure"):
            return {"admitted": False, "reason": "CLOSURE_INCOMPLETE"}
        result = self.runtime_controller.authorized_tick(source="HHS-P152-ElasticClosure")
        return {
            "admitted": True,
            "authoritative_state": copy.deepcopy(result["runtime"]),
            "hash72_receipt": copy.deepcopy(result["receipt"]),
            "authority_audit": copy.deepcopy(result["authority_audit"]),
            "candidate_binding": {
                "candidate_digest": sha256_json(candidate),
                "closure_proof_digest": sha256_json(proof),
                "binding_type": "PRECOMPUTATION_TO_VM81_AUTHORIZED_TICK",
            },
        }
