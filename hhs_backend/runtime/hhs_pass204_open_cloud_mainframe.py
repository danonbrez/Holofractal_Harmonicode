"""Production projection for Pass 204 open cloud execution."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any, Dict, Mapping

import hhs_backend.runtime.hhs_pass204_open_cloud_mainframe_v1 as _v1
from hhs_backend.runtime.hhs_pass203_hydrated_mainframe_v1 import InvocationRejectedError
from hhs_backend.runtime.hhs_pass204_open_cloud_mainframe_v1 import (
    CLASSIFICATION,
    CONTRACT,
    OPEN_CLOUD_PREFIX,
    PUBLIC_PREFIX,
    SANDBOX_POLICY,
    VERSION,
    OpenCloudMainframe as _V1OpenCloudMainframe,
)

KERNEL_CONSTRAINT_MANIFEST = {
    "schema": "HHS_PASS_204_IMMUTABLE_KERNEL_CONSTRAINT_MANIFEST_V1",
    "integrated_modular_system": True,
    "higher_dimensional_tensor_algebra_constraints": True,
    "noncommutative_entanglement_constraints": True,
    "error_correction_functions_integrated": True,
    "nft_crypto_state_machine": True,
    "native_machine_learning_optimization": True,
    "thermodynamic_agentic_information_geometry_economy": True,
    "opcode_interrupt_scope": "DISPOSABLE_SANDBOX_HARDWARE_PROJECTION",
    "admitted_history_mutable": False,
    "constraint_authority_mutable": False,
    "caller_adjustable_internal_parameters": False,
}

HOST_TRUST_BOUNDARY = {
    "schema": "HHS_PASS_204_CLOUD_HOST_TRUST_BOUNDARY_V1",
    "weakest_external_operational_layer": "CLOUD_SERVER_HARDWARE_ENVIRONMENT",
    "external_components": [
        "physical_cpu",
        "memory",
        "storage_device",
        "firmware",
        "hypervisor",
        "host_kernel",
        "network_fabric",
        "power_and_thermal_environment",
    ],
    "harmonicode_history_authority_inside_boundary": True,
    "host_fault_can_rewrite_admitted_hash_history": False,
    "host_fault_can_mutate_constraint_contract": False,
    "host_fault_may_interrupt_availability": True,
    "host_fault_may_damage_uncommitted_physical_execution": True,
    "recovery_source": "CONTENT_ADDRESSED_LAYERED_SNAPSHOT_AND_RECEIPT_CHAIN",
    "capability_state_recovered": False,
}


class OpenCloudMainframe(_V1OpenCloudMainframe):
    """Production authority with strict invalid-call separation and kernel roots."""

    @staticmethod
    def _overlay_record(record: Mapping[str, Any]) -> Dict[str, Any]:
        item = _V1OpenCloudMainframe._overlay_record(record)
        item["kernel_constraint_manifest_sha256"] = _v1._sha256(KERNEL_CONSTRAINT_MANIFEST)
        item["host_trust_boundary_sha256"] = _v1._sha256(HOST_TRUST_BOUNDARY)
        item["opcode_interrupt_can_rewrite_history"] = False
        item["valid_call_http_error"] = False
        item["descriptor_sha256"] = _v1._sha256(item)
        return item

    def status(self) -> Dict[str, Any]:
        payload = super().status()
        payload["kernel_constraint_manifest"] = dict(KERNEL_CONSTRAINT_MANIFEST)
        payload["kernel_constraint_manifest_sha256"] = _v1._sha256(KERNEL_CONSTRAINT_MANIFEST)
        payload["host_trust_boundary"] = dict(HOST_TRUST_BOUNDARY)
        payload["host_trust_boundary_sha256"] = _v1._sha256(HOST_TRUST_BOUNDARY)
        payload["all_declarations_executable"] = (
            payload["catalog_count"] == payload["callable_count"] == payload["hydrated_count"]
            and payload["unbound_internal_count"] == 0
        )
        payload["status_hash72"] = _v1.hash72("HHS_PASS_204_OPEN_CLOUD_MAINFRAME_STATUS_V1", payload)
        return payload

    def _invoke_sandbox(self, detail: Mapping[str, Any], arguments: Mapping[str, Any], timeout: int) -> Dict[str, Any]:
        request = self._worker_request(detail, arguments, timeout)
        request["kernel_constraint_manifest"] = KERNEL_CONSTRAINT_MANIFEST
        request["host_trust_boundary"] = HOST_TRUST_BOUNDARY
        environment = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONPATH": str(self.repo_root),
            "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "HHS_PASS204_SANDBOX": "1",
        }
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "hhs_backend.runtime.hhs_pass204_sandbox_worker"],
                cwd=str(self.repo_root),
                env=environment,
                input=_v1._canonical(request),
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return {
                "execution_status": "CONTINUATION_REQUIRED",
                "outcome": "SANDBOX_TIME_SLICE_EXHAUSTED",
                "continuation": {"reason": "TIME_SLICE_EXHAUSTED", "timeout_seconds": timeout},
                "worker_stderr": str(exc),
            }
        try:
            response = json.loads(completed.stdout.strip() or "{}")
        except json.JSONDecodeError:
            response = {
                "execution_status": "CONTINUATION_REQUIRED",
                "outcome": "WORKER_RESPONSE_REQUIRES_REPLAY",
                "continuation": {"reason": "NON_JSON_WORKER_RESPONSE"},
                "worker_stdout": completed.stdout[-4096:],
                "worker_stderr": completed.stderr[-4096:],
            }
        if response.get("invalid_call") or response.get("execution_status") == "INVALID_CALL":
            raise InvocationRejectedError(str(response.get("reason") or "invalid function arguments"))
        if "execution_status" not in response:
            response["execution_status"] = "COMPLETED" if response.get("ok") else "CONTINUATION_REQUIRED"
        return response

    def _persist_snapshot(self, **kwargs: Any) -> Dict[str, Any]:
        snapshot = super()._persist_snapshot(**kwargs)
        snapshot["kernel_constraint_manifest"] = dict(KERNEL_CONSTRAINT_MANIFEST)
        snapshot["kernel_constraint_manifest_sha256"] = _v1._sha256(KERNEL_CONSTRAINT_MANIFEST)
        snapshot["host_trust_boundary"] = dict(HOST_TRUST_BOUNDARY)
        snapshot["host_trust_boundary_sha256"] = _v1._sha256(HOST_TRUST_BOUNDARY)
        snapshot["integrated_system_state"] = {
            "catalog_sha256": _v1._sha256(self.catalog()),
            "sandbox_policy_sha256": _v1._sha256(SANDBOX_POLICY),
            "kernel_constraint_manifest_sha256": snapshot["kernel_constraint_manifest_sha256"],
            "host_trust_boundary_sha256": snapshot["host_trust_boundary_sha256"],
            "pass190_runtime": _v1._safe(self._pass190().execution_runtime_report()),
            "pass_inheritance": "PASS_204_INHERITS_ALL_PRIOR_PASSES_AS_ONE_INTEGRATED_SYSTEM",
            "history_rewrite_permitted": False,
            "capability_state_persisted": False,
        }
        snapshot["snapshot_root"] = _v1.hash72("HHS_PASS_204_LAYERED_SESSION_SNAPSHOT_V2", snapshot)
        snapshot["recall_token"] = f"recall:{snapshot['session_id']}:{snapshot['snapshot_root']}"
        with self._connect() as connection:
            connection.execute(
                "UPDATE sessions SET snapshot_root=?, recall_token=?, snapshot_json=? WHERE session_id=?",
                (snapshot["snapshot_root"], snapshot["recall_token"], _v1._canonical(snapshot), snapshot["session_id"]),
            )
        return snapshot


PASS204_MAINFRAME = OpenCloudMainframe()
_v1.PASS204_MAINFRAME = PASS204_MAINFRAME

__all__ = [
    "CLASSIFICATION",
    "CONTRACT",
    "HOST_TRUST_BOUNDARY",
    "KERNEL_CONSTRAINT_MANIFEST",
    "OPEN_CLOUD_PREFIX",
    "OpenCloudMainframe",
    "PASS204_MAINFRAME",
    "PUBLIC_PREFIX",
    "SANDBOX_POLICY",
    "VERSION",
]
