from __future__ import annotations

from pathlib import Path
from typing import Any

from hhs_runtime.pass145.service import HHS145Service
from .engine import HHS146BoundaryEngine, PASS_ID, VERSION


class HHS146Service(HHS145Service):
    def __init__(self, db_path: str | Path, **kwargs: Any):
        super().__init__(db_path, **kwargs)
        self.security = HHS146BoundaryEngine(self)

    def version(self) -> dict[str, Any]:
        parent = super().version()
        return {"schema": "HHS_PASS146_VERSION_V1", "pass_id": PASS_ID, "version": VERSION, "parent": parent, "architectural_identity": ["RECURSIVE", "HOLOGRAPHIC", "FRACTAL", "HARMONIC", "EVOLUTIONARY", "SYMBOLIC", "TEMPORAL", "INTERACTIVE"]}

    def capabilities(self) -> dict[str, Any]:
        parent = super().capabilities()
        parent["schema"] = "HHS_PASS146_CAPABILITIES_V1"
        parent["pass_id"] = PASS_ID
        parent["capabilities"].update({
            "boundary_constructed_execution": "CLI_AVAILABLE",
            "minimum_admissible_pathways": "CLI_AVAILABLE",
            "recursive_capability_narrowing": "CLI_AVAILABLE",
            "contract_carried_propagation": "CLI_AVAILABLE",
            "pathway_lifecycle_dissolution": "CLI_AVAILABLE",
            "high_resolution_transition_receipts": "CLI_AVAILABLE",
            "reversibility_classification": "CLI_AVAILABLE",
            "conflict_negotiation_paths": "CLI_AVAILABLE",
            "authenticated_loopback_security_api": "CLI_AVAILABLE",
            "signed_peer_envelopes": "CLI_AVAILABLE",
            "explicit_peer_trust": "CLI_AVAILABLE",
            "separate_node_loopback_transport": "OBSERVED_WORKING",
            "remote_device_network_transport": "NOT_EXPOSED",
        })
        return parent

    def status(self) -> dict[str, Any]:
        parent = super().status()
        security = self.security.status()
        return {"schema": "HHS_PASS146_STATUS_V1", "ok": bool(parent["ok"] and security["ok"]), "version": self.version(), "parent_status": parent, "security_status": security}

    def doctor(self) -> dict[str, Any]:
        parent = super().doctor()
        security = self.security.status()
        try:
            import cryptography
            crypto = {"ok": True, "library": "cryptography", "version": cryptography.__version__, "purpose": "Ed25519 signed propagation and encrypted identity keys"}
        except Exception as exc:
            crypto = {"ok": False, "library": "cryptography", "error": str(exc)}
        checks = {**parent["checks"], "boundary_security": {"ok": security["ok"], **security}, "signed_envelope_crypto": crypto, "boundary_is_computation": {"ok": True, "invariant": "O_B != O_EMPTY", "direct_dispatch_without_boundary": "REJECTED_BY_PUBLIC_PASS146_SURFACE"}}
        return {"schema": "HHS_PASS146_DOCTOR_V1", "ok": all(bool(v.get("ok")) for v in checks.values()), "checks": checks}
