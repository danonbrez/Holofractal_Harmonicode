"""Pass 077 unified workspace compiler and artifact-lineage runtime."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import (
    FROZEN_PASS072_SYSTEM_ROOT_HASH72,
    ContractError,
    product_root,
    stable,
)
from native_projects.hhs_harmonicode_interpreter.hhs_pass076_workspace_runtime_v1 import (
    BASE_STATE_ATTRS,
    PASS075_STATE_ATTRS,
    PASS076_STATE_ATTRS,
    HHSNativeInterpreterWorkspaceRuntime,
    build_pass076_demo,
    operation_registry as pass076_operation_registry,
)

from .hhs_artifact_lineage_pipeline_v1 import (
    admit_export,
    build_export_package,
    build_lineage_certificate,
    transition_artifact_status,
)
from .hhs_exact_artifact_delta_v1 import apply_delta, create_delta
from .hhs_independent_artifact_verifier_v1 import verifier_source, verify_package_object
from .hhs_interpreter_compiler_equivalence_gate_v1 import build_equivalence_receipt, enforce_equivalence
from .hhs_pass077_contracts_v1 import (
    PASS_ID,
    PARENT_NATIVE_PASS,
    TARGET_ID,
    VERSION,
    registered_portable_bytecode_contract,
    rooted,
    semantic_divergence_rejection,
    validate_registered_target_contract,
)
from .hhs_portable_bytecode_v1 import (
    build_compilation_plan,
    emit_candidate_artifact,
    execute_bytecode,
    lower_to_target_ir,
    optimize_target_ir,
    replay_compiled_execution,
)

PASS077_STATE_ATTRS = (
    "compiler_target_contracts", "compilation_requests", "compilation_plans", "target_ir_objects",
    "optimization_proofs", "compiled_artifacts", "compiled_executions", "semantic_projections",
    "equivalence_receipts", "compiler_test_receipts", "lineage_certificates", "export_packages",
    "external_verifications", "admitted_artifact_registry", "artifact_deltas", "delta_receipts",
    "compiler_replays",
)


def operation_registry() -> Dict[str, Any]:
    registry = deepcopy(pass076_operation_registry())
    registry.pop("operation_registry_root_hash72", None)
    registry["version"] = VERSION
    registry["parent_operation_registry_root_hash72"] = pass076_operation_registry()["operation_registry_root_hash72"]
    operations = []
    for item in registry["operations"]:
        current = deepcopy(item)
        if current["operation_id"] == "workspace.compiler.compile":
            current.update({
                "description": "Reserved convenience pipeline; Pass 077 exposes explicit verified compiler stages",
                "implemented": False,
            })
        operations.append(current)
    definitions = [
        ("workspace.compiler.plan", "COMPILE", "Bind a compilation request to the registered target contract and complete lineage roots"),
        ("workspace.compiler.lower", "COMPILE", "Deterministically project HHS_EXECUTABLE_IR_V1 to HHS_TARGET_IR_V1"),
        ("workspace.compiler.optimize", "COMPILE", "Apply only registered bounded rewrites with an executable equivalence obligation"),
        ("workspace.compiler.emit", "COMPILE", "Emit reproducible HHS portable bytecode as an unadmitted candidate"),
        ("workspace.compiler.validate", "COMPILE", "Run interpreter and bytecode paths and enforce exact canonical semantic projection equality"),
        ("workspace.compiler.replay", "COMPILE", "Replay compiled execution and compare its exact execution root"),
        ("workspace.lineage.record", "MUTATE", "Record complete genesis-or-parent artifact derivation lineage"),
        ("workspace.lineage.get", "QUERY", "Read one lineage certificate"),
        ("workspace.lineage.trace", "QUERY", "Trace artifact lineage to requirement, source, IR, tests, compiler, and evidence"),
        ("workspace.artifact.package", "MUTATE", "Create a deterministic evidence-bearing package without self-authorization"),
        ("workspace.artifact.verify", "MUTATE", "Independently reexecute package-contained interpreter and bytecode evidence"),
        ("workspace.artifact.export", "MUTATE", "Admit only an independently verified package to the product registry"),
        ("workspace.artifact.delta.create", "MUTATE", "Create an exact ordered byte-range delta bound to base and target lineage"),
        ("workspace.artifact.delta.apply", "MUTATE", "Apply a delta only to the exact base and verify target byte reconstruction"),
    ]
    for operation_id, operation_class, description in definitions:
        operations.append({
            "operation_id": operation_id,
            "operation_class": operation_class,
            "description": description,
            "implemented": True,
            "unified_api_only": True,
            "private_authority_path": False,
            "runtime_authority_required": operation_class in {"COMPILE", "MUTATE"},
        })
    registry["operations"] = operations
    registry["operation_registry_root_hash72"] = product_root("pass077_operation_registry", registry)
    return stable(registry)


class HHSCompilerArtifactWorkspaceRuntime(HHSNativeInterpreterWorkspaceRuntime):
    def __init__(self, *, initial_state: Optional[Mapping[str, Any]] = None) -> None:
        super().__init__(initial_state=None)
        self.registry = operation_registry()
        self.compiler_target_contracts: Dict[str, Dict[str, Any]] = {TARGET_ID: registered_portable_bytecode_contract()}
        self.compilation_requests: Dict[str, Dict[str, Any]] = {}
        self.compilation_plans: Dict[str, Dict[str, Any]] = {}
        self.target_ir_objects: Dict[str, Dict[str, Any]] = {}
        self.optimization_proofs: Dict[str, Dict[str, Any]] = {}
        self.compiled_artifacts: Dict[str, Dict[str, Any]] = {}
        self.compiled_executions: Dict[str, Dict[str, Any]] = {}
        self.semantic_projections: Dict[str, Dict[str, Any]] = {}
        self.equivalence_receipts: Dict[str, Dict[str, Any]] = {}
        self.compiler_test_receipts: Dict[str, Dict[str, Any]] = {}
        self.lineage_certificates: Dict[str, Dict[str, Any]] = {}
        self.export_packages: Dict[str, Dict[str, Any]] = {}
        self.external_verifications: Dict[str, Dict[str, Any]] = {}
        self.admitted_artifact_registry: Dict[str, Dict[str, Any]] = {}
        self.artifact_deltas: Dict[str, Dict[str, Any]] = {}
        self.delta_receipts: Dict[str, Dict[str, Any]] = {}
        self.compiler_replays: Dict[str, Dict[str, Any]] = {}
        if initial_state:
            self._restore_pass077(initial_state)

    def _state_payload(self) -> Dict[str, Any]:
        payload = super()._state_payload()
        payload.update({
            "schema": "HHS_NATIVE_COMPILER_ARTIFACT_WORKSPACE_RUNTIME_STATE_V1",
            "version": VERSION,
            "pass_id": PASS_ID,
            "parent_native_pass": PARENT_NATIVE_PASS,
            **{attr: stable(getattr(self, attr)) for attr in PASS077_STATE_ATTRS},
            "compiler_execution_available": True,
            "portable_bytecode_target_available": True,
            "lineage_packaging_available": True,
            "independent_verification_available": True,
            "delta_packaging_available": True,
            "emulator_execution_available": False,
            "compiler_authority_narrower_than_interpreter_semantic_judgment": True,
            "foundation_repair_available": False,
        })
        return payload

    def snapshot(self) -> Dict[str, Any]:
        payload = self._state_payload()
        payload["workspace_state_root_hash72"] = product_root("pass077_compiler_workspace_state", payload)
        return stable(payload)

    def _restore_pass077(self, state: Mapping[str, Any]) -> None:
        supplied = deepcopy(dict(state)); expected = str(supplied.pop("workspace_state_root_hash72", ""))
        if expected != product_root("pass077_compiler_workspace_state", supplied):
            raise ContractError("REJECT_PASS077_WORKSPACE_STATE_ROOT_MISMATCH")
        if supplied.get("pass_id") != PASS_ID:
            raise ContractError("REJECT_PASS077_STATE_ID_MISMATCH")
        if supplied.get("frozen_platform_root_hash72") != FROZEN_PASS072_SYSTEM_ROOT_HASH72:
            raise ContractError("REJECT_FROZEN_PLATFORM_ROOT_MISMATCH")
        if supplied.get("operation_registry_root_hash72") != self.registry["operation_registry_root_hash72"]:
            raise ContractError("REJECT_PASS077_OPERATION_REGISTRY_ROOT_MISMATCH")
        self.sequence = int(supplied.get("sequence", 0))
        for attr in BASE_STATE_ATTRS:
            setattr(self, attr, deepcopy(supplied.get(attr, {})))
        self.events = deepcopy(supplied.get("events", []))
        for attr in (*PASS075_STATE_ATTRS, *PASS076_STATE_ATTRS, *PASS077_STATE_ATTRS):
            setattr(self, attr, deepcopy(supplied.get(attr, {})))

    def _contract(self, request: Mapping[str, Any]) -> Dict[str, Any]:
        ref = str(request["payload"].get("target_contract_ref") or TARGET_ID)
        contract = self.compiler_target_contracts.get(ref)
        if not contract:
            raise ContractError("REJECT_COMPILER_TARGET_CONTRACT_NOT_FOUND")
        contract = validate_registered_target_contract(contract)
        supplied = str(request["payload"].get("target_contract_root_hash72") or "")
        if supplied != contract["contract_root_hash72"]:
            raise ContractError("REJECT_COMPILATION_REQUEST_CONTRACT_ROOT_MISMATCH")
        return contract

    def _op_workspace_compiler_plan(self, request: Mapping[str, Any]):
        contract = self._contract(request)
        executable_ref = str(request["payload"].get("executable_ir_ref") or "")
        executable = self.executable_ir_objects.get(executable_ref)
        if not executable:
            raise ContractError("REJECT_COMPILATION_EXECUTABLE_IR_NOT_FOUND")
        compilation_id = str(request["payload"].get("compilation_id") or f"compilation:{request['request_id']}")
        compilation_request, plan = build_compilation_plan(
            compilation_id=compilation_id,
            executable_ir=executable,
            target_contract=contract,
            requirement_root_hash72=str(request["payload"].get("requirement_root_hash72") or ""),
            source_artifact_root_hash72=str(request["payload"].get("source_artifact_root_hash72") or ""),
            typed_ir_root_hash72=str(request["payload"].get("typed_ir_root_hash72") or ""),
            test_receipt_root_hash72=str(request["payload"].get("test_receipt_root_hash72") or ""),
        )
        self.compilation_requests[compilation_id] = compilation_request
        self.compilation_plans[compilation_id] = plan
        self._append_project_object(request["project_id"], compilation_id)
        return {"compilation_request": compilation_request, "compilation_plan": plan}, [compilation_id], []

    def _op_workspace_compiler_lower(self, request: Mapping[str, Any]):
        compilation_ref = str(request["payload"].get("compilation_ref") or "")
        plan = self.compilation_plans.get(compilation_ref); compilation_request = self.compilation_requests.get(compilation_ref)
        if not plan or not compilation_request:
            raise ContractError("REJECT_COMPILATION_PLAN_NOT_FOUND")
        executable = next((value for value in self.executable_ir_objects.values() if value.get("executable_ir_root_hash72") == plan.get("executable_ir_root_hash72")), None)
        if not executable:
            raise ContractError("REJECT_COMPILATION_EXECUTABLE_IR_NOT_FOUND")
        contract = self.compiler_target_contracts[TARGET_ID]
        target_ir_id = str(request["payload"].get("target_ir_id") or f"target-ir:{compilation_ref}")
        target_ir = lower_to_target_ir(target_ir_id=target_ir_id, executable_ir=executable, compilation_plan=plan, target_contract=contract)
        self.target_ir_objects[target_ir_id] = target_ir
        self._append_project_object(request["project_id"], target_ir_id)
        return {"target_ir": target_ir}, [target_ir_id, compilation_ref], []

    def _op_workspace_compiler_optimize(self, request: Mapping[str, Any]):
        target_ir_ref = str(request["payload"].get("target_ir_ref") or "")
        target_ir = self.target_ir_objects.get(target_ir_ref)
        if not target_ir:
            raise ContractError("REJECT_TARGET_IR_NOT_FOUND")
        optimization_id = str(request["payload"].get("optimization_id") or f"optimization:{target_ir_ref}")
        optimized, proof = optimize_target_ir(optimization_id=optimization_id, target_ir=target_ir, optimization=str(request["payload"].get("optimization") or "IDENTITY_CANONICALIZATION"))
        self.target_ir_objects[target_ir_ref] = optimized
        self.optimization_proofs[optimization_id] = proof
        self._append_project_object(request["project_id"], optimization_id)
        return {"target_ir": optimized, "optimization_proof": proof}, [target_ir_ref, optimization_id], []

    def _op_workspace_compiler_emit(self, request: Mapping[str, Any]):
        target_ir_ref = str(request["payload"].get("target_ir_ref") or "")
        proof_ref = str(request["payload"].get("optimization_proof_ref") or "")
        target_ir = self.target_ir_objects.get(target_ir_ref); proof = self.optimization_proofs.get(proof_ref)
        if not target_ir or not proof:
            raise ContractError("REJECT_EMIT_MISSING_TARGET_IR_OR_OPTIMIZATION_PROOF")
        artifact_id = str(request["payload"].get("artifact_id") or f"artifact:compiled:{target_ir_ref}")
        artifact = emit_candidate_artifact(artifact_id=artifact_id, target_ir=target_ir, optimization_proof=proof)
        self.compiled_artifacts[artifact_id] = artifact; self.artifacts[artifact_id] = artifact
        project = self._require_project(request["project_id"])
        if artifact_id not in project["artifact_ids"]: project["artifact_ids"].append(artifact_id)
        return {"compiled_artifact": artifact}, [target_ir_ref, proof_ref], [artifact_id]

    def _op_workspace_compiler_validate(self, request: Mapping[str, Any]):
        artifact_ref = str(request["payload"].get("artifact_ref") or "")
        execution_ref = str(request["payload"].get("interpreter_execution_ref") or "")
        executable_ref = str(request["payload"].get("executable_ir_ref") or "")
        artifact = self.compiled_artifacts.get(artifact_ref); interpreter_run = self.execution_runs.get(execution_ref); executable = self.executable_ir_objects.get(executable_ref)
        if not artifact or not interpreter_run or not executable:
            raise ContractError("REJECT_COMPILER_VALIDATION_INPUT_NOT_FOUND")
        compiled_run_id = str(request["payload"].get("compiled_run_id") or f"compiled-execution:{artifact_ref}")
        compiled_run = execute_bytecode(run_id=compiled_run_id, artifact=artifact)
        receipt_id = str(request["payload"].get("equivalence_receipt_id") or f"equivalence:{artifact_ref}")
        receipt, interpreter_projection, compiled_projection = build_equivalence_receipt(
            receipt_id=receipt_id,
            target_contract=self.compiler_target_contracts[TARGET_ID],
            executable_ir=executable,
            compiled_artifact=artifact,
            interpreter_execution=interpreter_run,
            compiled_execution=compiled_run,
        )
        self.compiled_executions[compiled_run_id] = compiled_run
        self.equivalence_receipts[receipt_id] = receipt
        self.semantic_projections[f"semantic:interpreter:{artifact_ref}"] = interpreter_projection
        self.semantic_projections[f"semantic:compiled:{artifact_ref}"] = compiled_projection
        test_body = {
            "schema": "HHS_COMPILER_VALIDATION_TEST_RECEIPT_V1",
            "test_receipt_id": f"compiler-test:{artifact_ref}",
            "artifact_ref": artifact_ref,
            "interpreter_execution_ref": execution_ref,
            "compiled_execution_ref": compiled_run_id,
            "equivalence_receipt_ref": receipt_id,
            "checks": {
                "artifact_bytes_verified": True,
                "interpreter_reference_closed": interpreter_run.get("closed") is True,
                "compiled_execution_closed": compiled_run.get("closed") is True,
                "semantic_projection_roots_match": receipt.get("semantic_projection_roots_match") is True,
                "all_contract_fields_match": receipt.get("all_contract_fields_match") is True,
            },
            "status": "PASS" if receipt.get("artifact_admission_permitted") else "FAIL",
            "passed": receipt.get("artifact_admission_permitted") is True,
            "compiled_success_is_not_semantic_correctness": True,
        }
        test_receipt = rooted("pass077_compiler_test_receipt", test_body, "test_receipt_root_hash72")
        self.compiler_test_receipts[test_body["test_receipt_id"]] = test_receipt
        if receipt.get("artifact_admission_permitted") is not True:
            rejected = transition_artifact_status(artifact, status="REJECTED", equivalence_receipt_root_hash72=receipt["receipt_root_hash72"])
            self.compiled_artifacts[artifact_ref] = rejected; self.artifacts[artifact_ref] = rejected
            enforce_equivalence(receipt)
        validated = transition_artifact_status(artifact, status="VALIDATED", equivalence_receipt_root_hash72=receipt["receipt_root_hash72"])
        self.compiled_artifacts[artifact_ref] = validated; self.artifacts[artifact_ref] = validated
        for ref in (compiled_run_id, receipt_id, test_body["test_receipt_id"]): self._append_project_object(request["project_id"], ref)
        return {
            "compiled_artifact": validated,
            "compiled_execution": compiled_run,
            "equivalence_receipt": receipt,
            "interpreter_semantic_projection": interpreter_projection,
            "compiled_semantic_projection": compiled_projection,
            "compiler_test_receipt": test_receipt,
        }, [compiled_run_id, receipt_id, test_body["test_receipt_id"]], [artifact_ref]

    def _op_workspace_compiler_replay(self, request: Mapping[str, Any]):
        execution_ref = str(request["payload"].get("compiled_execution_ref") or "")
        artifact_ref = str(request["payload"].get("artifact_ref") or "")
        run = self.compiled_executions.get(execution_ref); artifact = self.compiled_artifacts.get(artifact_ref)
        if not run or not artifact: raise ContractError("REJECT_COMPILED_REPLAY_INPUT_NOT_FOUND")
        replay = replay_compiled_execution(execution=run, artifact=artifact)
        replay_id = str(request["payload"].get("replay_id") or f"compiled-replay:{execution_ref}")
        self.compiler_replays[replay_id] = replay; self._append_project_object(request["project_id"], replay_id)
        return {"compiled_replay": replay}, [replay_id, execution_ref], []

    def _op_workspace_lineage_record(self, request: Mapping[str, Any]):
        artifact_ref = str(request["payload"].get("artifact_ref") or "")
        compilation_ref = str(request["payload"].get("compilation_ref") or "")
        equivalence_ref = str(request["payload"].get("equivalence_receipt_ref") or "")
        test_ref = str(request["payload"].get("test_receipt_ref") or "")
        artifact = self.compiled_artifacts.get(artifact_ref); plan = self.compilation_plans.get(compilation_ref); equivalence = self.equivalence_receipts.get(equivalence_ref); test = self.compiler_test_receipts.get(test_ref)
        if not artifact or not plan or not equivalence or not test:
            raise ContractError("REJECT_LINEAGE_INPUT_NOT_FOUND")
        certificate_id = str(request["payload"].get("certificate_id") or f"lineage:{artifact_ref}")
        compiled_execution_ref = str(test.get("compiled_execution_ref") or "")
        interpreter_execution_ref = str(test.get("interpreter_execution_ref") or "")
        certificate = build_lineage_certificate(
            certificate_id=certificate_id, artifact=artifact,
            project_root_hash72=self.projects[request["project_id"]]["project_root_hash72"],
            requirement_root_hash72=plan["requirement_root_hash72"],
            source_artifact_root_hash72=plan["source_artifact_root_hash72"],
            typed_ir_root_hash72=plan["typed_ir_root_hash72"], executable_ir_root_hash72=plan["executable_ir_root_hash72"],
            compilation_plan_root_hash72=plan["compilation_plan_root_hash72"], target_contract_root_hash72=plan["target_contract_root_hash72"],
            interpreter_reference_execution_root_hash72=self.execution_runs[interpreter_execution_ref]["execution_run_root_hash72"],
            compiled_execution_root_hash72=self.compiled_executions[compiled_execution_ref]["compiled_execution_root_hash72"],
            semantic_equivalence_receipt_root_hash72=equivalence["receipt_root_hash72"], test_receipt_root_hash72=test["test_receipt_root_hash72"],
            genesis_source_root_hash72=request["payload"].get("genesis_source_root_hash72"),
            parent_artifact_root_hash72=request["payload"].get("parent_artifact_root_hash72"),
        )
        self.lineage_certificates[certificate_id] = certificate; self._append_project_object(request["project_id"], certificate_id)
        return {"lineage_certificate": certificate}, [certificate_id, artifact_ref], []

    def _op_workspace_lineage_get(self, request: Mapping[str, Any]):
        ref = str(request["payload"].get("certificate_ref") or ""); value = self.lineage_certificates.get(ref)
        if not value: raise ContractError("REJECT_LINEAGE_CERTIFICATE_NOT_FOUND")
        return {"lineage_certificate": value}, [ref], []

    def _op_workspace_lineage_trace(self, request: Mapping[str, Any]):
        ref = str(request["payload"].get("certificate_ref") or ""); cert = self.lineage_certificates.get(ref)
        if not cert: raise ContractError("REJECT_LINEAGE_CERTIFICATE_NOT_FOUND")
        trace = {
            "schema": "HHS_ARTIFACT_LINEAGE_TRACE_V1", "certificate_ref": ref,
            "requirement_root_hash72": cert["requirement_root_hash72"], "source_artifact_root_hash72": cert["source_artifact_root_hash72"],
            "typed_ir_root_hash72": cert["typed_ir_root_hash72"], "executable_ir_root_hash72": cert["executable_ir_root_hash72"],
            "compilation_plan_root_hash72": cert["compilation_plan_root_hash72"], "target_contract_root_hash72": cert["target_contract_root_hash72"],
            "test_receipt_root_hash72": cert["test_receipt_root_hash72"], "semantic_equivalence_receipt_root_hash72": cert["semantic_equivalence_receipt_root_hash72"],
            "compiler_identity": cert["compiler_identity"], "complete": True,
        }
        trace["trace_root_hash72"] = product_root("pass077_lineage_trace", trace)
        return {"lineage_trace": trace}, [ref], []

    def _op_workspace_artifact_package(self, request: Mapping[str, Any]):
        p = request["payload"]
        artifact_ref, cert_ref, compilation_ref = str(p.get("artifact_ref") or ""), str(p.get("certificate_ref") or ""), str(p.get("compilation_ref") or "")
        equivalence_ref, test_ref = str(p.get("equivalence_receipt_ref") or ""), str(p.get("test_receipt_ref") or "")
        artifact, cert, plan = self.compiled_artifacts.get(artifact_ref), self.lineage_certificates.get(cert_ref), self.compilation_plans.get(compilation_ref)
        request_obj, equivalence, test = self.compilation_requests.get(compilation_ref), self.equivalence_receipts.get(equivalence_ref), self.compiler_test_receipts.get(test_ref)
        if not all((artifact, cert, plan, request_obj, equivalence, test)): raise ContractError("REJECT_PACKAGE_INPUT_NOT_FOUND")
        target_ir = next((x for x in self.target_ir_objects.values() if x.get("compilation_plan_root_hash72") == plan.get("compilation_plan_root_hash72")), None)
        proof = next((x for x in self.optimization_proofs.values() if x.get("input_target_ir_root_hash72") == target_ir.get("target_ir_root_hash72")), None) if target_ir else None
        compiled_run = next((x for x in self.compiled_executions.values() if x.get("compiled_artifact_root_hash72") == artifact.get("artifact_payload_root_hash72")), None)
        if not target_ir or not proof or not compiled_run: raise ContractError("REJECT_PACKAGE_DERIVED_INPUT_NOT_FOUND")
        interpreter_run = next((x for x in self.execution_runs.values() if x.get("execution_run_root_hash72") == cert.get("interpreter_reference_execution_root_hash72")), None)
        executable = next((x for x in self.executable_ir_objects.values() if x.get("executable_ir_root_hash72") == plan.get("executable_ir_root_hash72")), None)
        if not interpreter_run or not executable: raise ContractError("REJECT_PACKAGE_REFERENCE_INPUT_NOT_FOUND")
        package_id = str(p.get("package_id") or f"package:{artifact_ref}")
        package, _, _ = build_export_package(
            package_id=package_id, artifact=artifact, lineage_certificate=cert, target_contract=self.compiler_target_contracts[TARGET_ID],
            compilation_request=request_obj, compilation_plan=plan, target_ir=target_ir, optimization_proof=proof,
            equivalence_receipt=equivalence, test_receipt=test, executable_ir=executable, interpreter_execution=interpreter_run,
            compiled_execution=compiled_run, interpreter_projection=self.semantic_projections[f"semantic:interpreter:{artifact_ref}"],
            compiled_projection=self.semantic_projections[f"semantic:compiled:{artifact_ref}"], verifier_source=verifier_source(),
        )
        self.export_packages[package_id] = package; self._append_project_object(request["project_id"], package_id)
        return {"export_package": package}, [package_id, cert_ref, equivalence_ref], []

    def _op_workspace_artifact_verify(self, request: Mapping[str, Any]):
        package_ref = str(request["payload"].get("package_ref") or ""); package = self.export_packages.get(package_ref)
        if not package: raise ContractError("REJECT_EXPORT_PACKAGE_NOT_FOUND")
        verification = verify_package_object(package)
        verification_id = str(request["payload"].get("verification_id") or f"external-verification:{package_ref}")
        self.external_verifications[verification_id] = verification; self._append_project_object(request["project_id"], verification_id)
        if verification.get("status") != "REEXECUTED_SEMANTIC_EQUIVALENCE": raise ContractError("REJECT_INDEPENDENT_ARTIFACT_VERIFICATION")
        return {"external_verification": verification}, [verification_id, package_ref], []

    def _op_workspace_artifact_export(self, request: Mapping[str, Any]):
        package_ref, artifact_ref, verification_ref = (str(request["payload"].get(k) or "") for k in ("package_ref", "artifact_ref", "verification_ref"))
        package, artifact, verification = self.export_packages.get(package_ref), self.compiled_artifacts.get(artifact_ref), self.external_verifications.get(verification_ref)
        if not package or not artifact or not verification: raise ContractError("REJECT_EXPORT_INPUT_NOT_FOUND")
        admitted_artifact, result = admit_export(package=package, artifact=artifact, external_verification=verification)
        admitted_package, registry_entry = result["package"], result["registry_entry"]
        self.export_packages[package_ref] = admitted_package; self.compiled_artifacts[artifact_ref] = admitted_artifact; self.artifacts[artifact_ref] = admitted_artifact
        self.admitted_artifact_registry[artifact_ref] = registry_entry; self._append_project_object(request["project_id"], registry_entry["registry_entry_root_hash72"])
        return {"admitted_artifact": admitted_artifact, "admitted_package": admitted_package, "registry_entry": registry_entry}, [artifact_ref, package_ref, verification_ref], [artifact_ref]

    def _op_workspace_artifact_delta_create(self, request: Mapping[str, Any]):
        base_ref, target_ref, lineage_ref = (str(request["payload"].get(k) or "") for k in ("base_artifact_ref", "target_artifact_ref", "target_lineage_ref"))
        base, target, lineage = self.compiled_artifacts.get(base_ref), self.compiled_artifacts.get(target_ref), self.lineage_certificates.get(lineage_ref)
        if not base or not target or not lineage: raise ContractError("REJECT_DELTA_INPUT_NOT_FOUND")
        delta_id = str(request["payload"].get("delta_id") or f"delta:{base_ref}:{target_ref}")
        delta = create_delta(delta_id=delta_id, base_artifact=base, target_artifact=target, target_lineage=lineage)
        self.artifact_deltas[delta_id] = delta; self._append_project_object(request["project_id"], delta_id)
        return {"artifact_delta": delta}, [delta_id, base_ref, target_ref, lineage_ref], []

    def _op_workspace_artifact_delta_apply(self, request: Mapping[str, Any]):
        base_ref, delta_ref = str(request["payload"].get("base_artifact_ref") or ""), str(request["payload"].get("delta_ref") or "")
        base, delta = self.compiled_artifacts.get(base_ref), self.artifact_deltas.get(delta_ref)
        if not base or not delta: raise ContractError("REJECT_DELTA_INPUT_NOT_FOUND")
        reconstructed, receipt = apply_delta(base_artifact=base, delta=delta)
        receipt_id = str(request["payload"].get("receipt_id") or f"delta-receipt:{delta_ref}")
        self.delta_receipts[receipt_id] = receipt; self._append_project_object(request["project_id"], receipt_id)
        return {"delta_reconstruction_receipt": receipt}, [receipt_id, delta_ref, base_ref], []


def build_pass077_demo(runtime: Optional[HHSCompilerArtifactWorkspaceRuntime] = None) -> Dict[str, Any]:
    from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import make_request
    rt = runtime or HHSCompilerArtifactWorkspaceRuntime()
    build_pass076_demo(rt)
    project_id, session_id = "project:pass076-demo", "session:pass076-demo"
    authority = {"role_contract_ref": "role:pass077-compiler", "task_assignment_ref": "task:pass077-verified-projection", "capability_lease_ref": "lease:pass077-compiler"}
    contract = rt.compiler_target_contracts[TARGET_ID]
    executable = rt.executable_ir_objects["executable-ir:repair:pass076:omega"]
    upstream_test = next(iter(rt.repair_test_receipts.values()))
    requirement_root = product_root("pass077_requirement", {"axiom": "COMPILATION_CHANGES_REPRESENTATION_NOT_ADMITTED_MEANING", "pass": PASS_ID})
    def req(rid, cls, op, payload):
        return make_request(request_id=rid, project_id=project_id, session_id=session_id, operation_class=cls, operation_id=op, payload=payload, client_surface="REPLAY", **authority)
    calls = [
        req("req:077:plan", "COMPILE", "workspace.compiler.plan", {"executable_ir_ref": executable["executable_ir_id"], "compilation_id": "compilation:pass077:portable", "target_contract_ref": TARGET_ID, "target_contract_root_hash72": contract["contract_root_hash72"], "requirement_root_hash72": requirement_root, "source_artifact_root_hash72": executable["source_artifact_root_hash72"], "typed_ir_root_hash72": executable["typed_ir_root_hash72"], "test_receipt_root_hash72": upstream_test["repair_test_receipt_root_hash72"]}),
        req("req:077:lower", "COMPILE", "workspace.compiler.lower", {"compilation_ref": "compilation:pass077:portable", "target_ir_id": "target-ir:pass077:portable"}),
        req("req:077:optimize", "COMPILE", "workspace.compiler.optimize", {"target_ir_ref": "target-ir:pass077:portable", "optimization_id": "optimization:pass077:identity"}),
        req("req:077:emit", "COMPILE", "workspace.compiler.emit", {"target_ir_ref": "target-ir:pass077:portable", "optimization_proof_ref": "optimization:pass077:identity", "artifact_id": "artifact:pass077:portable"}),
        req("req:077:validate", "COMPILE", "workspace.compiler.validate", {"artifact_ref": "artifact:pass077:portable", "interpreter_execution_ref": "execution:repair:pass076:omega", "executable_ir_ref": "executable-ir:repair:pass076:omega", "compiled_run_id": "compiled-execution:pass077:portable", "equivalence_receipt_id": "equivalence:pass077:portable"}),
        req("req:077:lineage", "MUTATE", "workspace.lineage.record", {"artifact_ref": "artifact:pass077:portable", "compilation_ref": "compilation:pass077:portable", "equivalence_receipt_ref": "equivalence:pass077:portable", "test_receipt_ref": "compiler-test:artifact:pass077:portable", "certificate_id": "lineage:pass077:portable", "genesis_source_root_hash72": executable["source_artifact_root_hash72"]}),
        req("req:077:package", "MUTATE", "workspace.artifact.package", {"artifact_ref": "artifact:pass077:portable", "certificate_ref": "lineage:pass077:portable", "compilation_ref": "compilation:pass077:portable", "equivalence_receipt_ref": "equivalence:pass077:portable", "test_receipt_ref": "compiler-test:artifact:pass077:portable", "package_id": "package:pass077:portable"}),
        req("req:077:verify", "MUTATE", "workspace.artifact.verify", {"package_ref": "package:pass077:portable", "verification_id": "external-verification:pass077:portable"}),
        req("req:077:export", "MUTATE", "workspace.artifact.export", {"package_ref": "package:pass077:portable", "artifact_ref": "artifact:pass077:portable", "verification_ref": "external-verification:pass077:portable"}),
        req("req:077:replay", "COMPILE", "workspace.compiler.replay", {"compiled_execution_ref": "compiled-execution:pass077:portable", "artifact_ref": "artifact:pass077:portable", "replay_id": "compiled-replay:pass077:portable"}),
    ]
    responses = [rt.dispatch(call) for call in calls]
    if any(response["status"] != "ADMITTED" for response in responses):
        failed = [(calls[i]["payload"]["operation_id"], response) for i, response in enumerate(responses) if response["status"] != "ADMITTED"]
        raise RuntimeError(f"PASS077_DEMO_FAILED:{failed}")
    return {"runtime": rt, "responses": responses, "snapshot": rt.snapshot(), "requirement_root_hash72": requirement_root}


def build_pass077_release_bundle() -> Dict[str, Any]:
    demo = build_pass077_demo(); state = demo["snapshot"]
    body = {
        "schema": "HHS_PASS_077_COMPILER_ARTIFACT_PIPELINE_RELEASE_BUNDLE_V1",
        "pass_id": PASS_ID, "version": VERSION, "parent_native_pass": PARENT_NATIVE_PASS,
        "platform_dependency": {"pass_id": "PASS_072", "total_system_root_hash72": FROZEN_PASS072_SYSTEM_ROOT_HASH72, "foundation_modified": False},
        "parent_product_modified": False,
        "operation_registry": operation_registry(),
        "registered_target_contract": state["compiler_target_contracts"][TARGET_ID],
        "rejection_primitive": semantic_divergence_rejection(),
        "requirement_root_hash72": demo["requirement_root_hash72"],
        "workspace_state": state,
        "compiler_execution_available": True,
        "portable_bytecode_target_available": True,
        "independent_verification_available": True,
        "embedded_validator_self_authorizes": False,
        "new_orphan_modules": 0,
        "thread_context_required": False,
        "llm_context_window_required": False,
        "host_path_required": False,
    }
    body["product_root_hash72"] = product_root("pass077_release_bundle", body)
    return stable(body)


def write_release_artifacts(root: Optional[str | Path] = None) -> Dict[str, Any]:
    repo = Path(root).resolve() if root else Path(__file__).resolve().parents[2]
    out = repo / "native_projects/hhs_compiler_artifact_pipeline/artifacts"; out.mkdir(parents=True, exist_ok=True)
    bundle = build_pass077_release_bundle(); state = bundle["workspace_state"]
    values = {
        "HHS_PASS_077_COMPILER_ARTIFACT_PIPELINE_RELEASE_BUNDLE.json": bundle,
        "PASS_077_COMPILER_WORKSPACE_STATE.json": state,
        "PASS_077_API_OPERATION_REGISTRY.json": bundle["operation_registry"],
        "PASS_077_REGISTERED_TARGET_CONTRACT.json": bundle["registered_target_contract"],
        "PASS_077_SEMANTIC_DIVERGENCE_REJECTION.json": bundle["rejection_primitive"],
        "PASS_077_COMPILATION_REQUEST.json": state["compilation_requests"]["compilation:pass077:portable"],
        "PASS_077_COMPILATION_PLAN.json": state["compilation_plans"]["compilation:pass077:portable"],
        "PASS_077_TARGET_IR.json": state["target_ir_objects"]["target-ir:pass077:portable"],
        "PASS_077_OPTIMIZATION_PROOF.json": state["optimization_proofs"]["optimization:pass077:identity"],
        "PASS_077_COMPILED_ARTIFACT.json": state["compiled_artifacts"]["artifact:pass077:portable"],
        "PASS_077_COMPILED_EXECUTION.json": state["compiled_executions"]["compiled-execution:pass077:portable"],
        "PASS_077_EQUIVALENCE_RECEIPT.json": state["equivalence_receipts"]["equivalence:pass077:portable"],
        "PASS_077_LINEAGE_CERTIFICATE.json": state["lineage_certificates"]["lineage:pass077:portable"],
        "PASS_077_EXPORT_PACKAGE.json": state["export_packages"]["package:pass077:portable"],
        "PASS_077_EXTERNAL_VERIFICATION.json": state["external_verifications"]["external-verification:pass077:portable"],
        "PASS_077_ADMITTED_ARTIFACT_REGISTRY_ENTRY.json": state["admitted_artifact_registry"]["artifact:pass077:portable"],
        "PASS_077_COMPILER_REPLAY.json": state["compiler_replays"]["compiled-replay:pass077:portable"],
    }
    for name, value in values.items():
        (out / name).write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    package = state["export_packages"]["package:pass077:portable"]
    import base64
    (out / "PASS_077_ADMITTED_ARTIFACT_PACKAGE.hhspkg").write_bytes(base64.b64decode(package["package_bytes_base64"]))
    return bundle

if __name__ == "__main__":
    print(json.dumps(write_release_artifacts(), indent=2, sort_keys=True, ensure_ascii=False))
