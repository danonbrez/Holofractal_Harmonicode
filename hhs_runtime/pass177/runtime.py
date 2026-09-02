from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from hhs_runtime.hash72_checkpoint import make_hash72_witness
from hhs_runtime.pass163.vmrc import VMRCRuntime, VMRCError
from hhs_runtime.pass165.ingestion import DEFAULT_MULTIMODAL_LEARNING_SERVICE


class Pass177AuthorityError(RuntimeError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass177AuthorityError(f"P177_FLOAT_CANONICAL_AUTHORITY_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_float(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_float(item, f"{path}[{index}]")


def _canonical(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _hash216(domain: str, payload: Mapping[str, Any]) -> str:
    lanes = [
        make_hash72_witness(f"{domain}:previous", payload, width=72).digest,
        make_hash72_witness(f"{domain}:change", payload, width=72).digest,
        make_hash72_witness(f"{domain}:receipt", payload, width=72).digest,
    ]
    value = "".join(lanes)
    if len(value) != 216:
        raise Pass177AuthorityError("P177_HASH216_LENGTH")
    return value


class Pass177WorkflowAuthority:
    def __init__(self, *, vm81: VMRCRuntime | None) -> None:
        self._vm81 = vm81
        self._projects: dict[str, dict[str, Any]] = {}
        self._checkpoints: dict[str, dict[str, Any]] = {}

    def status(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_177_AUTHORITY_STATUS_V1",
            "contract": "HHS-P177-UMACCT-WA-CEC-PD",
            "classification": "HHS_PASS177_HISTORICAL_WORKFLOW_AUTHORITY_RECONCILED_NONTERMINAL",
            "vm81_authority_bound": self._vm81 is not None,
            "singleton_vm81_authority": True,
            "independent_vm81_authority": False,
            "independent_hash72_commit_authority": False,
            "hash216_mutation_authority": False,
            "browser_hash216_is_candidate_identity_only": True,
            "memory_checkpoint_is_canonical_authority": False,
            "external_tool_success_may_be_fabricated": False,
            "registered_project_count": len(self._projects),
            "registered_checkpoint_count": len(self._checkpoints),
            "terminal_pass177_completion": False,
            "repair_forward_required": True,
            "remaining_terminal_categories": [
                "COMPLETE_REQUIRED_APPLICATION_TEMPLATE_FAMILIES",
                "COMPLETE_REQUIRED_CREATIVE_CONTENT_FAMILIES",
                "VERSIONED_ENVIRONMENT_ADAPTER_REGISTRY",
                "VERIFIED_TOOLCHAIN_PROVISIONING",
                "REAL_MULTI_TARGET_COMPILATION_TRANSFORMATION",
                "FORMAT_APPROPRIATE_MEDIA_OUTPUT_VALIDATION",
                "PROJECT_VISIBLE_DURABLE_CHECKPOINT_STORE",
                "ASSISTANT_TYPED_MUTATION_PARITY",
                "EXPLICIT_DEPLOYMENT_EXECUTION_AND_REVISION_EVIDENCE",
                "NOVICE_EXPERT_BROWSER_USABILITY",
                "PERFORMANCE_SCALE_AND_RESOURCE_EVIDENCE",
                "AUTHORITATIVE_MAIN_AND_DEPLOYED_REVISION_CLOSURE",
            ],
        }

    def _vm81_commit(self, transition: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        if self._vm81 is None:
            raise Pass177AuthorityError("P177_VM81_ADMISSION_AUTHORITY_REQUIRED")
        material = _canonical({"transition": transition, "payload": payload})
        digest = hashlib.sha256(material).digest()
        writes: dict[int, int] = {}
        for byte in digest[:24]:
            writes[int(byte % 81)] = 1 if byte & 1 else -1
        try:
            candidate = self._vm81.submit_candidate(
                thread=57,
                writes=writes,
                operation="VMRC_COMMIT",
                expected_input_hash72=self._vm81.state_hash72,
                dependency_root=hashlib.sha256(
                    b"HHS-P177-WORKFLOW-VM81\0" + material
                ).hexdigest(),
                capability_scope="P177_PROJECT_WORKFLOW_CANONICAL_MUTATION",
                source_architecture="P177_UNIVERSAL_CREATION_WORKFLOW",
                target_architecture="VM81",
            )
            result = self._vm81.execute(candidate)
        except VMRCError as error:
            raise Pass177AuthorityError(f"P177_VM81_ADMISSION_REJECTED:{error}") from error
        commit = result.get("commit") or {}
        receipt = commit.get("receipt") or {}
        validated = (result.get("validation") or {}).get("validated") or {}
        if commit.get("classification") != "HHS_PASS_163_COMMIT_ADMITTED":
            raise Pass177AuthorityError("P177_VM81_ADMISSION_NOT_COMMITTED")
        if not receipt.get("receipt_hash72") or not receipt.get("operation_hash216"):
            raise Pass177AuthorityError("P177_VM81_RECEIPT_INCOMPLETE")
        return {
            "classification": "HHS_PASS177_VM81_WORKFLOW_ADMISSION_VERIFIED",
            "candidate_id": candidate.candidate_id,
            "receipt_hash72": str(receipt["receipt_hash72"]),
            "operation_hash216": str(receipt["operation_hash216"]),
            "output_hash72": str(receipt.get("output_hash72") or ""),
            "vm81_epoch": self._vm81.epoch,
            "singleton_authority": True,
            "independent_vm81_authority": False,
            "validation_mutation_authority": bool(validated.get("mutation_authority", False)),
        }

    @staticmethod
    def _validate_project(project: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
        _reject_float(project)
        if project.get("schema") != "hhs.pass177.generated-project/v1":
            raise Pass177AuthorityError("P177_PROJECT_SCHEMA")
        manifest = project.get("manifest")
        files = project.get("files")
        if not isinstance(manifest, Mapping) or manifest.get("schema") != "hhs.pass177.project/v1":
            raise Pass177AuthorityError("P177_PROJECT_MANIFEST_SCHEMA")
        if not isinstance(files, list) or not files:
            raise Pass177AuthorityError("P177_PROJECT_FILES_REQUIRED")
        project_id = str(manifest.get("id") or "")
        if not project_id:
            raise Pass177AuthorityError("P177_PROJECT_ID_REQUIRED")
        identity = manifest.get("identity")
        if not isinstance(identity, Mapping):
            raise Pass177AuthorityError("P177_BROWSER_CANDIDATE_IDENTITY_REQUIRED")
        if identity.get("vm81EchoRequired") is not True:
            raise Pass177AuthorityError("P177_BROWSER_IDENTITY_VM81_ECHO_REQUIRED")
        return project_id, dict(manifest)

    def admit_project(self, project: Mapping[str, Any]) -> dict[str, Any]:
        project_id, manifest = self._validate_project(project)
        canonical = {
            "schema": project["schema"],
            "manifest": manifest,
            "files": project["files"],
        }
        project_sha256 = hashlib.sha256(_canonical(canonical)).hexdigest()
        prior = self._projects.get(project_id)
        if prior is not None and prior["project_sha256"] != project_sha256:
            raise Pass177AuthorityError("P177_PROJECT_ID_IMMUTABLE_CONFLICT")
        browser_identity = manifest["identity"]
        admission = self._vm81_commit(
            "PROJECT_ADMIT",
            {
                "project_id": project_id,
                "project_sha256": project_sha256,
                "browser_candidate_root": str(browser_identity.get("root") or ""),
                "template": manifest.get("template"),
                "workflow": manifest.get("workflow"),
            },
        )
        evidence_payload = {
            "project_id": project_id,
            "project_sha256": project_sha256,
            "browser_candidate_root": str(browser_identity.get("root") or ""),
            "vm81_receipt_hash72": admission["receipt_hash72"],
            "vm81_output_hash72": admission["output_hash72"],
        }
        record = {
            "schema": "HHS_PASS_177_ADMITTED_PROJECT_V1",
            "project_id": project_id,
            "project_sha256": project_sha256,
            "browser_candidate_identity": dict(browser_identity),
            "browser_identity_authoritative": False,
            "vm81_admission": admission,
            "post_vm81_hash72_evidence": make_hash72_witness(
                "pass177:project:post-vm81-evidence",
                evidence_payload,
                width=72,
            ).digest,
            "project_hash216": _hash216("pass177:project:archive", evidence_payload),
            "canonical_mutation_authority": "INHERITED_VM81_ONLY",
            "hash72_commit_authority": False,
            "hash216_mutation_authority": False,
        }
        self._projects[project_id] = record
        return record

    @staticmethod
    def _validate_checkpoint(run: Mapping[str, Any]) -> tuple[str, int]:
        _reject_float(run)
        if run.get("schema") != "hhs.pass177.workflow-run/v1":
            raise Pass177AuthorityError("P177_WORKFLOW_RUN_SCHEMA")
        run_id = str(run.get("runId") or "")
        checkpoint = run.get("checkpoint")
        if not run_id or not isinstance(checkpoint, int) or isinstance(checkpoint, bool) or checkpoint < 1:
            raise Pass177AuthorityError("P177_WORKFLOW_CHECKPOINT_ID")
        if run.get("status") not in {"running", "succeeded", "failed", "cancelled"}:
            raise Pass177AuthorityError("P177_WORKFLOW_STATUS")
        return run_id, checkpoint

    def admit_workflow_checkpoint(
        self,
        *,
        project_id: str,
        run: Mapping[str, Any],
    ) -> dict[str, Any]:
        project = self._projects.get(project_id)
        if project is None:
            raise Pass177AuthorityError("P177_PROJECT_NOT_ADMITTED")
        run_id, checkpoint = self._validate_checkpoint(run)
        key = f"{project_id}:{run_id}"
        prior = self._checkpoints.get(key)
        if prior is not None and checkpoint < prior["checkpoint"]:
            raise Pass177AuthorityError("P177_STALE_WORKFLOW_CHECKPOINT")
        checkpoint_sha256 = hashlib.sha256(_canonical(run)).hexdigest()
        admission = self._vm81_commit(
            "WORKFLOW_CHECKPOINT_ADMIT",
            {
                "project_id": project_id,
                "project_hash216": project["project_hash216"],
                "run_id": run_id,
                "checkpoint": checkpoint,
                "checkpoint_sha256": checkpoint_sha256,
                "status": run["status"],
            },
        )
        evidence_payload = {
            "project_id": project_id,
            "project_hash216": project["project_hash216"],
            "run_id": run_id,
            "checkpoint": checkpoint,
            "checkpoint_sha256": checkpoint_sha256,
            "status": run["status"],
            "vm81_receipt_hash72": admission["receipt_hash72"],
            "vm81_output_hash72": admission["output_hash72"],
        }
        record = {
            "schema": "HHS_PASS_177_ADMITTED_WORKFLOW_CHECKPOINT_V1",
            "project_id": project_id,
            "run_id": run_id,
            "checkpoint": checkpoint,
            "status": run["status"],
            "checkpoint_sha256": checkpoint_sha256,
            "vm81_admission": admission,
            "post_vm81_hash72_evidence": make_hash72_witness(
                "pass177:workflow:post-vm81-evidence",
                evidence_payload,
                width=72,
            ).digest,
            "checkpoint_hash216": _hash216(
                "pass177:workflow-checkpoint:archive",
                evidence_payload,
            ),
            "memory_checkpoint_authoritative": False,
            "canonical_mutation_authority": "INHERITED_VM81_ONLY",
            "hash72_commit_authority": False,
            "hash216_mutation_authority": False,
        }
        self._checkpoints[key] = record
        return record


PASS177_WORKFLOW_AUTHORITY = Pass177WorkflowAuthority(
    vm81=DEFAULT_MULTIMODAL_LEARNING_SERVICE._vm81,
)
