"""Pass 076 native interpreter and bounded repair workspace runtime."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple
import json

from native_projects.hhs_ide_workspace.hhs_development_network_protocol_v1 import canonical_test_record
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import (
    FROZEN_PASS072_SYSTEM_ROOT_HASH72,
    ContractError,
    product_root,
    stable,
)
from native_projects.hhs_harmonicode_language.hhs_pass075_workspace_runtime_v1 import (
    HHSNativeLanguageWorkspaceRuntime,
    operation_registry as pass075_operation_registry,
)

from .hhs_bounded_repair_executor_v1 import (
    apply_exact_replacements,
    build_repair_test_receipt,
    build_repair_transaction,
    build_rollback_capsule,
    validate_healing_plan,
)
from .hhs_exact_symbolic_interpreter_v1 import (
    execute_program,
    execute_step,
    initialize_state,
    replay_execution,
)
from .hhs_executable_ir_v1 import lower_committed_typed_ir, verify_executable_ir
from .hhs_pass076_contracts_v1 import (
    INTERPRETER_REPLAY_SCHEMA,
    PASS_ID,
    PARENT_NATIVE_PASS,
    REPAIR_TRANSACTION_SCHEMA,
    VERSION,
    rooted,
    verify_rooted,
)

BASE_STATE_ATTRS = (
    "projects", "sessions", "buffers", "artifacts", "receipts", "agents",
    "proposals", "alignment_decisions", "test_records", "handoffs", "healing_plans",
)
PASS075_STATE_ATTRS = (
    "language_documents", "typed_ir_objects", "language_validations", "test_acceleration_plans",
)
PASS076_STATE_ATTRS = (
    "executable_ir_objects", "interpreter_states", "execution_plans", "execution_runs",
    "execution_step_receipts", "execution_replays", "interpreter_test_executions",
    "repair_transactions", "repair_rollbacks", "repair_test_receipts", "rollback_executions",
)


def operation_registry() -> Dict[str, Any]:
    registry = deepcopy(pass075_operation_registry())
    registry.pop("operation_registry_root_hash72", None)
    registry["version"] = VERSION
    registry["parent_operation_registry_root_hash72"] = pass075_operation_registry()["operation_registry_root_hash72"]
    operations = []
    for item in registry["operations"]:
        current = deepcopy(item)
        if current["operation_id"] == "workspace.interpreter.execute":
            current.update({
                "description": "Execute committed validated HHS_TYPED_IR_V1 through exact bounded micro-steps and witnessed state receipts",
                "implemented": True,
                "runtime_authority_required": True,
            })
        operations.append(current)
    operations.extend([
        {
            "operation_id": "workspace.interpreter.lower", "operation_class": "EXECUTE",
            "description": "Deterministically lower committed validated typed IR to HHS_EXECUTABLE_IR_V1 without effects",
            "implemented": True, "unified_api_only": True, "private_authority_path": False,
        },
        {
            "operation_id": "workspace.interpreter.step", "operation_class": "EXECUTE",
            "description": "Advance one exact interpreter micro-step under runtime authority",
            "implemented": True, "unified_api_only": True, "private_authority_path": False,
            "runtime_authority_required": True,
        },
        {
            "operation_id": "workspace.interpreter.state.get", "operation_class": "QUERY",
            "description": "Project an interpreter state without mutating it",
            "implemented": True, "unified_api_only": True, "private_authority_path": False,
        },
        {
            "operation_id": "workspace.interpreter.replay", "operation_class": "EXECUTE",
            "description": "Replay a completed execution and compare the exact execution root",
            "implemented": True, "unified_api_only": True, "private_authority_path": False,
        },
        {
            "operation_id": "workspace.tests.execute", "operation_class": "EXECUTE",
            "description": "Execute deterministic interpreter tests from a Pass 075 acceleration plan",
            "implemented": True, "unified_api_only": True, "private_authority_path": False,
            "runtime_authority_required": True,
        },
        {
            "operation_id": "workspace.repair.execute", "operation_class": "MUTATE",
            "description": "Apply a bounded exact product-local repair with validation, execution, rollback, and receipt closure",
            "implemented": True, "unified_api_only": True, "private_authority_path": False,
        },
        {
            "operation_id": "workspace.repair.rollback", "operation_class": "MUTATE",
            "description": "Create a new witnessed source continuation from a repair rollback capsule",
            "implemented": True, "unified_api_only": True, "private_authority_path": False,
        },
    ])
    registry["operations"] = operations
    registry["operation_registry_root_hash72"] = product_root("pass076_operation_registry", registry)
    return stable(registry)


class HHSNativeInterpreterWorkspaceRuntime(HHSNativeLanguageWorkspaceRuntime):
    def __init__(self, *, initial_state: Optional[Mapping[str, Any]] = None) -> None:
        super().__init__(initial_state=None)
        self.registry = operation_registry()
        self.executable_ir_objects: Dict[str, Dict[str, Any]] = {}
        self.interpreter_states: Dict[str, Dict[str, Any]] = {}
        self.execution_plans: Dict[str, list[Dict[str, Any]]] = {}
        self.execution_runs: Dict[str, Dict[str, Any]] = {}
        self.execution_step_receipts: Dict[str, Dict[str, Any]] = {}
        self.execution_replays: Dict[str, Dict[str, Any]] = {}
        self.interpreter_test_executions: Dict[str, Dict[str, Any]] = {}
        self.repair_transactions: Dict[str, Dict[str, Any]] = {}
        self.repair_rollbacks: Dict[str, Dict[str, Any]] = {}
        self.repair_test_receipts: Dict[str, Dict[str, Any]] = {}
        self.rollback_executions: Dict[str, Dict[str, Any]] = {}
        if initial_state:
            self._restore_pass076(initial_state)

    def _state_payload(self) -> Dict[str, Any]:
        payload = super()._state_payload()
        payload.update({
            "schema": "HHS_NATIVE_INTERPRETER_WORKSPACE_RUNTIME_STATE_V1",
            "version": VERSION,
            "pass_id": PASS_ID,
            "parent_native_pass": PARENT_NATIVE_PASS,
            "executable_ir_objects": stable(self.executable_ir_objects),
            "interpreter_states": stable(self.interpreter_states),
            "execution_plans": stable(self.execution_plans),
            "execution_runs": stable(self.execution_runs),
            "execution_step_receipts": stable(self.execution_step_receipts),
            "execution_replays": stable(self.execution_replays),
            "interpreter_test_executions": stable(self.interpreter_test_executions),
            "repair_transactions": stable(self.repair_transactions),
            "repair_rollbacks": stable(self.repair_rollbacks),
            "repair_test_receipts": stable(self.repair_test_receipts),
            "rollback_executions": stable(self.rollback_executions),
            "interpreter_execution_available": True,
            "bounded_product_repair_available": True,
            "compiler_execution_available": False,
            "emulator_execution_available": False,
            "foundation_repair_available": False,
        })
        return payload

    def snapshot(self) -> Dict[str, Any]:
        payload = self._state_payload()
        payload["workspace_state_root_hash72"] = product_root("pass076_interpreter_workspace_state", payload)
        return stable(payload)

    def _restore_pass076(self, state: Mapping[str, Any]) -> None:
        supplied = deepcopy(dict(state))
        expected = str(supplied.pop("workspace_state_root_hash72", ""))
        if expected != product_root("pass076_interpreter_workspace_state", supplied):
            raise ContractError("REJECT_PASS076_WORKSPACE_STATE_ROOT_MISMATCH")
        if supplied.get("pass_id") != PASS_ID:
            raise ContractError("REJECT_PASS076_STATE_ID_MISMATCH")
        if supplied.get("frozen_platform_root_hash72") != FROZEN_PASS072_SYSTEM_ROOT_HASH72:
            raise ContractError("REJECT_FROZEN_PLATFORM_ROOT_MISMATCH")
        if supplied.get("operation_registry_root_hash72") != self.registry["operation_registry_root_hash72"]:
            raise ContractError("REJECT_PASS076_OPERATION_REGISTRY_ROOT_MISMATCH")
        self.sequence = int(supplied.get("sequence", 0))
        for attr in BASE_STATE_ATTRS:
            setattr(self, attr, deepcopy(supplied.get(attr, {})))
        self.events = deepcopy(supplied.get("events", []))
        for attr in (*PASS075_STATE_ATTRS, *PASS076_STATE_ATTRS):
            setattr(self, attr, deepcopy(supplied.get(attr, {})))

    def _require_runtime_authority(self, request: Mapping[str, Any]) -> None:
        if not self._authority_ok(request):
            raise ContractError("REJECT_INTERPRETER_EXECUTION_WITHOUT_AUTHORITY_AND_LEASE")

    def _typed_ir_inputs(self, typed_ir_artifact_ref: str) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        artifact = self.artifacts.get(typed_ir_artifact_ref)
        if not artifact or artifact.get("schema") != "HHS_TYPED_IR_ARTIFACT_V1":
            raise ContractError("REJECT_COMMITTED_TYPED_IR_ARTIFACT_NOT_FOUND")
        source_ref = str(artifact.get("source_artifact_ref") or "")
        source = self.artifacts.get(source_ref)
        if not source:
            raise ContractError("REJECT_TYPED_IR_SOURCE_ARTIFACT_NOT_FOUND")
        validation_ref = str(artifact.get("validation_ref") or "")
        validation = self.language_validations.get(validation_ref)
        if not validation:
            raise ContractError("REJECT_TYPED_IR_VALIDATION_NOT_FOUND")
        return deepcopy(artifact), deepcopy(source), deepcopy(validation)

    def _lower_internal(self, *, typed_ir_artifact_ref: str, executable_ir_id: str) -> Dict[str, Any]:
        artifact, source, validation = self._typed_ir_inputs(typed_ir_artifact_ref)
        executable = lower_committed_typed_ir(
            executable_ir_id=executable_ir_id,
            typed_ir_artifact=artifact,
            source_artifact=source,
            validation=validation,
        )
        self.executable_ir_objects[executable_ir_id] = executable
        return executable

    def _store_run(self, run: Mapping[str, Any]) -> None:
        run_id = str(run.get("run_id"))
        self.execution_runs[run_id] = stable(run)
        state_ref = f"interpreter-state:{run_id}"
        self.interpreter_states[state_ref] = stable(run["final_state"])
        for receipt in run.get("step_receipts", []):
            self.execution_step_receipts[str(receipt["step_receipt_root_hash72"])] = stable(receipt)

    def _op_workspace_interpreter_lower(self, request: Mapping[str, Any]):
        self._require_project(request["project_id"])
        typed_ref = str(request["payload"].get("typed_ir_artifact_ref") or "")
        executable_id = str(request["payload"].get("executable_ir_id") or f"executable-ir:{request['request_id']}")
        executable = self._lower_internal(typed_ir_artifact_ref=typed_ref, executable_ir_id=executable_id)
        self._append_project_object(request["project_id"], executable_id)
        return {"executable_ir": executable, "execution_attempted": False}, [typed_ref, executable_id], []

    def _resolve_executable(self, request: Mapping[str, Any]) -> Dict[str, Any]:
        executable_ref = str(request["payload"].get("executable_ir_ref") or "")
        if executable_ref:
            executable = self.executable_ir_objects.get(executable_ref)
            if not executable or not verify_executable_ir(executable):
                raise ContractError("REJECT_EXECUTABLE_IR_NOT_FOUND_OR_INVALID")
            return executable
        typed_ref = str(request["payload"].get("typed_ir_artifact_ref") or "")
        if not typed_ref:
            raise ContractError("REJECT_INTERPRETER_INPUT_NOT_SPECIFIED")
        executable_id = str(request["payload"].get("executable_ir_id") or f"executable-ir:{request['request_id']}")
        return self._lower_internal(typed_ir_artifact_ref=typed_ref, executable_ir_id=executable_id)

    def _op_workspace_interpreter_execute(self, request: Mapping[str, Any]):
        self._require_runtime_authority(request)
        executable = self._resolve_executable(request)
        run_id = str(request["payload"].get("run_id") or f"execution:{request['request_id']}")
        run = execute_program(run_id=run_id, executable_ir=executable, max_steps=int(request["payload"].get("max_steps", 256)))
        self._store_run(run)
        for ref in (str(executable["executable_ir_id"]), run_id, f"interpreter-state:{run_id}"):
            self._append_project_object(request["project_id"], ref)
        return {
            "execution_run": run,
            "execution_closed": run["closed"],
            "console_projection": {
                "status": run["status"],
                "step_count": run["step_count"],
                "console_output_is_not_execution_receipt": True,
            },
        }, [str(executable["executable_ir_id"]), run_id, f"interpreter-state:{run_id}"], []

    def _op_workspace_interpreter_step(self, request: Mapping[str, Any]):
        self._require_runtime_authority(request)
        state_ref = str(request["payload"].get("state_ref") or "")
        if state_ref:
            state = self.interpreter_states.get(state_ref)
            if not state:
                raise ContractError("REJECT_INTERPRETER_STATE_NOT_FOUND")
            executable_ref = str(state.get("executable_ir_ref") or "")
            executable = self.executable_ir_objects.get(executable_ref)
            plan = self.execution_plans.get(executable_ref)
            if not executable or plan is None:
                raise ContractError("REJECT_INTERPRETER_STEP_PLAN_NOT_FOUND")
        else:
            executable = self._resolve_executable(request)
            run_id = str(request["payload"].get("run_id") or f"execution-step:{request['request_id']}")
            state, plan = initialize_state(run_id, executable)
            executable_ref = str(executable["executable_ir_id"])
            self.execution_plans[executable_ref] = stable(plan)
            state_ref = f"interpreter-state:{run_id}"
        prior_receipts = [
            value for value in self.execution_step_receipts.values()
            if value.get("run_id") == state.get("run_id")
        ]
        prior_receipts.sort(key=lambda value: int(value.get("step_index", 0)))
        previous_receipt_root = prior_receipts[-1]["step_receipt_root_hash72"] if prior_receipts else "GENESIS"
        next_state, receipt = execute_step(state, plan, previous_step_receipt_root_hash72=previous_receipt_root)
        self.interpreter_states[state_ref] = next_state
        self.execution_step_receipts[str(receipt["step_receipt_root_hash72"])] = receipt
        self._append_project_object(request["project_id"], state_ref)
        return {"interpreter_state": next_state, "step_receipt": receipt}, [state_ref, executable_ref], []

    def _op_workspace_interpreter_state_get(self, request: Mapping[str, Any]):
        state_ref = str(request["payload"].get("state_ref") or "")
        state = self.interpreter_states.get(state_ref)
        if not state:
            raise ContractError("REJECT_INTERPRETER_STATE_NOT_FOUND")
        return {"interpreter_state": deepcopy(state)}, [state_ref], []

    def _op_workspace_interpreter_replay(self, request: Mapping[str, Any]):
        run_ref = str(request["payload"].get("execution_run_ref") or "")
        run = self.execution_runs.get(run_ref)
        if not run:
            raise ContractError("REJECT_EXECUTION_RUN_NOT_FOUND")
        executable = self.executable_ir_objects.get(str(run.get("executable_ir_ref") or ""))
        if not executable:
            raise ContractError("REJECT_REPLAY_EXECUTABLE_IR_NOT_FOUND")
        replay = replay_execution(run, executable)
        replay_id = str(request["payload"].get("replay_id") or f"replay:{run_ref}")
        replay = stable({**replay, "replay_id": replay_id})
        self.execution_replays[replay_id] = replay
        self._append_project_object(request["project_id"], replay_id)
        return {"replay_verification": replay}, [run_ref, str(executable["executable_ir_id"]), replay_id], []

    def _op_workspace_tests_execute(self, request: Mapping[str, Any]):
        self._require_runtime_authority(request)
        plan_ref = str(request["payload"].get("test_plan_ref") or "")
        plan = self.test_acceleration_plans.get(plan_ref)
        if not plan:
            raise ContractError("REJECT_INTERPRETER_TEST_PLAN_NOT_FOUND")
        executable = self._resolve_executable(request)
        run_id = str(request["payload"].get("run_id") or f"test-execution:{request['request_id']}")
        run = execute_program(run_id=run_id, executable_ir=executable)
        self._store_run(run)
        test_id = str(request["payload"].get("test_execution_id") or f"interpreter-tests:{request['request_id']}")
        body = {
            "schema": "HHS_INTERPRETER_TEST_EXECUTION_V1",
            "test_execution_id": test_id,
            "test_plan_ref": plan_ref,
            "test_plan_root_hash72": plan.get("test_plan_root_hash72"),
            "executable_ir_ref": executable.get("executable_ir_id"),
            "execution_run_ref": run_id,
            "execution_run_root_hash72": run.get("execution_run_root_hash72"),
            "status": "PASS" if run.get("closed") else "FAIL",
            "passed": 1 if run.get("closed") else 0,
            "failed": 0 if run.get("closed") else 1,
            "this_execution_is_evidence_candidate_not_mutation_authority": True,
        }
        test_execution = rooted("pass076_interpreter_test_execution", body, "test_execution_root_hash72")
        self.interpreter_test_executions[test_id] = test_execution
        self._append_project_object(request["project_id"], test_id)
        return {"test_execution": test_execution, "execution_run": run}, [plan_ref, str(executable["executable_ir_id"]), run_id, test_id], []

    def _new_source_artifact(self, *, artifact_id: str, project_id: str, name: str, content: str, parent_ref: str, source_buffer_ref: str) -> Dict[str, Any]:
        artifact = {
            "schema": "HHS_COMMITTED_SOURCE_ARTIFACT_V1",
            "artifact_id": artifact_id,
            "project_id": project_id,
            "source_buffer_ref": source_buffer_ref,
            "source_buffer_revision": 0,
            "name": name,
            "content": content,
            "lineage": {"parent_artifact_ref": parent_ref},
            "compiled_artifact_self_authorizes": False,
        }
        artifact["artifact_root_hash72"] = product_root("pass074_source_artifact", artifact)
        return stable(artifact)

    def _derive_language_chain(self, *, project_id: str, source_artifact: Mapping[str, Any], prefix: str) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        document_id = f"language-doc:{prefix}"
        ir_id = f"typed-ir:{prefix}"
        parsed = self.language_service.parse(
            str(source_artifact.get("content") or ""),
            document_id=document_id,
            ir_id=ir_id,
            source_ref=str(source_artifact["artifact_id"]),
            source_kind="COMMITTED_SOURCE_ARTIFACT",
            source_root_hash72=str(source_artifact["artifact_root_hash72"]),
        )
        validation_id = f"validation:{ir_id}"
        validation = stable({**parsed["validation"], "validation_id": validation_id})
        typed_artifact_id = f"artifact:{ir_id}"
        typed_artifact = {
            "schema": "HHS_TYPED_IR_ARTIFACT_V1",
            "artifact_id": typed_artifact_id,
            "project_id": project_id,
            "typed_ir_ref": ir_id,
            "typed_ir_root_hash72": parsed["typed_ir"]["ir_root_hash72"],
            "source_artifact_ref": source_artifact["artifact_id"],
            "source_artifact_root_hash72": source_artifact["artifact_root_hash72"],
            "validation_ref": validation_id,
            "validation_root_hash72": validation["validation_root_hash72"],
            "content": parsed["typed_ir"],
            "execution_authority": False,
            "compiled_artifact_self_authorizes": False,
        }
        typed_artifact["artifact_root_hash72"] = product_root("pass075_typed_ir_artifact", typed_artifact)
        return parsed["document"], parsed["typed_ir"], validation, stable(typed_artifact)

    def _op_workspace_repair_execute(self, request: Mapping[str, Any]):
        plan_ref = str(request["payload"].get("healing_plan_ref") or "")
        plan = self.healing_plans.get(plan_ref)
        if not plan:
            raise ContractError("REJECT_REPAIR_HEALING_PLAN_NOT_FOUND")
        pre_ref = str(request["payload"].get("target_artifact_ref") or "")
        pre = self.artifacts.get(pre_ref)
        if not pre or pre.get("schema") != "HHS_COMMITTED_SOURCE_ARTIFACT_V1":
            raise ContractError("REJECT_REPAIR_SOURCE_ARTIFACT_NOT_FOUND")
        target_path = validate_healing_plan(plan, target_path=str(request["payload"].get("target_path") or pre.get("name") or ""))
        expected_pre_root = str(request["payload"].get("expected_pre_artifact_root_hash72") or "")
        if expected_pre_root and expected_pre_root != pre.get("artifact_root_hash72"):
            raise ContractError("REJECT_REPAIR_STALE_PRECONDITION_ROOT")
        repaired_text, replacement_receipts = apply_exact_replacements(str(pre.get("content") or ""), request["payload"].get("replacements", []))
        transaction_id = str(request["payload"].get("transaction_id") or f"repair:{request['request_id']}")
        post_id = str(request["payload"].get("post_artifact_id") or f"artifact:{transaction_id}:source")
        post = self._new_source_artifact(
            artifact_id=post_id, project_id=request["project_id"], name=target_path,
            content=repaired_text, parent_ref=pre_ref, source_buffer_ref=f"repair-buffer:{transaction_id}",
        )
        document, typed_ir, validation, typed_artifact = self._derive_language_chain(project_id=request["project_id"], source_artifact=post, prefix=transaction_id)
        executable = lower_committed_typed_ir(
            executable_ir_id=f"executable-ir:{transaction_id}", typed_ir_artifact=typed_artifact,
            source_artifact=post, validation=validation,
        )
        execution = execute_program(run_id=f"execution:{transaction_id}", executable_ir=executable)
        rollback = build_rollback_capsule(transaction_id=transaction_id, pre_artifact=pre, post_artifact=post, target_path=target_path)
        repair_test = build_repair_test_receipt(transaction_id=transaction_id, validation=validation, execution_run=execution)
        transaction = build_repair_transaction(
            transaction_id=transaction_id, plan=plan, target_path=target_path,
            pre_artifact=pre, post_artifact=post, replacement_receipts=replacement_receipts,
            rollback=rollback, validation=validation, execution_run=execution,
            repair_test_receipt=repair_test,
        )
        self.repair_transactions[transaction_id] = transaction
        self.repair_test_receipts[str(repair_test["repair_test_receipt_root_hash72"])] = repair_test
        if not repair_test["passed"]:
            return {"repair_transaction": transaction, "repair_test_receipt": repair_test, "mutation_applied": False}, [plan_ref, pre_ref, transaction_id], []
        self.artifacts[post_id] = post
        self.language_documents[document["document_id"]] = document
        self.typed_ir_objects[typed_ir["ir_id"]] = typed_ir
        self.language_validations[validation["validation_id"]] = validation
        self.artifacts[typed_artifact["artifact_id"]] = typed_artifact
        self.executable_ir_objects[executable["executable_ir_id"]] = executable
        self._store_run(execution)
        self.repair_rollbacks[rollback["rollback_id"]] = rollback
        project = self._require_project(request["project_id"])
        for artifact_id in (post_id, typed_artifact["artifact_id"]):
            if artifact_id not in project["artifact_ids"]:
                project["artifact_ids"].append(artifact_id)
        refs = [
            transaction_id, rollback["rollback_id"], document["document_id"], typed_ir["ir_id"],
            validation["validation_id"], executable["executable_ir_id"], execution["run_id"],
        ]
        for ref in refs:
            self._append_project_object(request["project_id"], ref)
        return {
            "repair_transaction": transaction,
            "rollback_capsule": rollback,
            "repair_test_receipt": repair_test,
            "repaired_execution": execution,
            "mutation_applied": True,
        }, [plan_ref, pre_ref, *refs], [post_id, typed_artifact["artifact_id"]]

    def _op_workspace_repair_rollback(self, request: Mapping[str, Any]):
        transaction_ref = str(request["payload"].get("transaction_ref") or "")
        transaction = self.repair_transactions.get(transaction_ref)
        if not transaction or transaction.get("schema") != REPAIR_TRANSACTION_SCHEMA:
            raise ContractError("REJECT_REPAIR_TRANSACTION_NOT_FOUND")
        if not verify_rooted("pass076_repair_transaction", transaction, "repair_transaction_root_hash72"):
            raise ContractError("REJECT_REPAIR_TRANSACTION_ROOT")
        rollback_ref = str(request["payload"].get("rollback_ref") or transaction.get("rollback_ref") or "")
        rollback = self.repair_rollbacks.get(rollback_ref)
        if not rollback or not verify_rooted("pass076_repair_rollback_capsule", rollback, "rollback_root_hash72"):
            raise ContractError("REJECT_REPAIR_ROLLBACK_NOT_FOUND_OR_INVALID")
        current_ref = str(transaction.get("post_artifact_ref") or "")
        current = self.artifacts.get(current_ref)
        if not current or current.get("artifact_root_hash72") != transaction.get("post_artifact_root_hash72"):
            raise ContractError("REJECT_ROLLBACK_CURRENT_ARTIFACT_MISMATCH")
        rollback_execution_id = str(request["payload"].get("rollback_execution_id") or f"rollback-execution:{transaction_ref}")
        restored_id = str(request["payload"].get("restored_artifact_id") or f"artifact:{rollback_execution_id}:source")
        restored = self._new_source_artifact(
            artifact_id=restored_id, project_id=request["project_id"], name=str(rollback["target_path"]),
            content=str(rollback["rollback_content"]), parent_ref=current_ref, source_buffer_ref=f"rollback-buffer:{rollback_execution_id}",
        )
        body = {
            "schema": "HHS_PRODUCT_REPAIR_ROLLBACK_EXECUTION_V1",
            "rollback_execution_id": rollback_execution_id,
            "transaction_ref": transaction_ref,
            "rollback_ref": rollback_ref,
            "from_artifact_ref": current_ref,
            "restored_artifact_ref": restored_id,
            "restored_artifact_root_hash72": restored["artifact_root_hash72"],
            "matches_original_pre_artifact_content": restored["content"] == rollback["rollback_content"],
            "history_erased": False,
            "new_continuation_created": True,
            "foundation_mutated": False,
        }
        execution = rooted("pass076_repair_rollback_execution", body, "rollback_execution_root_hash72")
        self.artifacts[restored_id] = restored
        self.rollback_executions[rollback_execution_id] = execution
        project = self._require_project(request["project_id"])
        if restored_id not in project["artifact_ids"]:
            project["artifact_ids"].append(restored_id)
        self._append_project_object(request["project_id"], rollback_execution_id)
        return {"rollback_execution": execution, "restored_artifact": restored}, [transaction_ref, rollback_ref, rollback_execution_id], [restored_id]


def build_pass076_demo(runtime: Optional[HHSNativeInterpreterWorkspaceRuntime] = None) -> Dict[str, Any]:
    from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import make_request

    rt = runtime or HHSNativeInterpreterWorkspaceRuntime()
    project_id = "project:pass076-demo"
    session_id = "session:pass076-demo"
    authority = {
        "role_contract_ref": "role:interpreter-repair-developer",
        "task_assignment_ref": "task:pass076-interpreter-repair",
        "capability_lease_ref": "lease:pass076-interpreter-repair",
    }
    failing_source = """PHASE_GATE := {
  x==1/y;
  z==1/w;
  xy≠yx;
  Δe=0;
  Ψ=0;
  Θ15=true;
  Ω=false
}
PHASE_GATE
"""
    def req(rid: str, cls: str, op: str, payload: Mapping[str, Any] | None = None, auth: bool = False):
        return make_request(request_id=rid, project_id=project_id, session_id=session_id, operation_class=cls, operation_id=op, payload=payload or {}, **(authority if auth else {}), client_surface="REPLAY")
    requests = [
        req("req:076:project", "INGRESS", "workspace.project.create", {"name": "Pass 076 Interpreter and Bounded Repair"}),
        req("req:076:session", "INGRESS", "workspace.session.open"),
        req("req:076:agent:human", "INGRESS", "workspace.agent.register", {"agent_id": "agent:human:repair-reviewer", "agent_kind": "HUMAN", "capabilities": ["repair.review", "authority.revalidate"]}),
        req("req:076:agent:llm", "INGRESS", "workspace.agent.register", {"agent_id": "agent:llm:repair-builder", "agent_kind": "LLM", "capabilities": ["interpreter.execute", "repair.propose"]}),
        req("req:076:buffer", "INGRESS", "workspace.buffer.open", {"buffer_id": "buffer:pass076:main", "name": "native_projects/hhs_harmonicode_interpreter/demo/main.hhs", "text": failing_source}),
        req("req:076:source", "MUTATE", "workspace.source.commit", {"buffer_id": "buffer:pass076:main", "artifact_id": "artifact:pass076:source:failing"}, True),
        req("req:076:parse", "EXECUTE", "workspace.language.parse", {"artifact_id": "artifact:pass076:source:failing", "document_id": "language-doc:pass076:failing", "ir_id": "typed-ir:pass076:failing"}),
        req("req:076:ir", "MUTATE", "workspace.language.ir.commit", {"typed_ir_ref": "typed-ir:pass076:failing", "validation_ref": "validation:typed-ir:pass076:failing", "artifact_id": "artifact:pass076:typed-ir:failing"}, True),
        req("req:076:lower", "EXECUTE", "workspace.interpreter.lower", {"typed_ir_artifact_ref": "artifact:pass076:typed-ir:failing", "executable_ir_id": "executable-ir:pass076:failing"}),
        req("req:076:execute:failing", "EXECUTE", "workspace.interpreter.execute", {"executable_ir_ref": "executable-ir:pass076:failing", "run_id": "execution:pass076:failing"}, True),
        req("req:076:proposal", "INGRESS", "workspace.change.propose", {
            "proposal_id": "proposal:pass076:repair", "program_id": "program:hhs-harmonicode-interpreter",
            "proposer_agent_ref": "agent:llm:repair-builder", "summary": "Repair product-local invariant fixture",
            "new_capability_statement": "Execute exact Harmonicode IR and apply bounded reversible product-local repairs",
            "reusable_capabilities": ["interpreter.execute", "repair.execute", "repair.rollback"],
            "reachable_entrypoint": "workspace.interpreter.execute",
            "affected_product_paths": ["native_projects/hhs_harmonicode_interpreter/demo"],
            "requested_tests": ["tests/test_hhs_pass076_interpreter_and_bounded_repair_v1.py"],
        }),
        req("req:076:alignment", "EXECUTE", "workspace.alignment.evaluate", {"proposal_ref": "proposal:pass076:repair"}),
        req("req:076:test:fail", "MUTATE", "workspace.test.record", {
            "test_record_id": "test-record:pass076:failure", "proposal_ref": "proposal:pass076:repair", "status": "FAIL",
            "passed": 0, "failed": 1, "commands": ["workspace.interpreter.execute"], "evidence_refs": ["execution:pass076:failing"],
        }, True),
        req("req:076:healing", "EXECUTE", "workspace.healing.plan", {
            "proposal_ref": "proposal:pass076:repair", "test_record_ref": "test-record:pass076:failure", "requested_by_agent_ref": "agent:llm:repair-builder",
        }),
        req("req:076:repair", "MUTATE", "workspace.repair.execute", {
            "healing_plan_ref": "healing:proposal:pass076:repair:test-record:pass076:failure",
            "target_artifact_ref": "artifact:pass076:source:failing",
            "target_path": "native_projects/hhs_harmonicode_interpreter/demo/main.hhs",
            "expected_pre_artifact_root_hash72": "__FILL__",
            "replacements": [{"old": "Ω=false", "new": "Ω=true", "expected_count": 1}],
            "transaction_id": "repair:pass076:omega", "post_artifact_id": "artifact:pass076:source:repaired",
        }, True),
    ]
    responses = []
    for request in requests:
        if request["request_id"] == "req:076:repair":
            payload = deepcopy(request)
            payload["payload"]["expected_pre_artifact_root_hash72"] = rt.artifacts["artifact:pass076:source:failing"]["artifact_root_hash72"]
            payload.pop("request_root_hash72", None)
            from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import canonical_request
            request = canonical_request(payload)
        responses.append(rt.dispatch(request))
    return {"runtime": rt, "requests": requests, "responses": responses, "snapshot": rt.snapshot()}


def build_pass076_release_bundle() -> Dict[str, Any]:
    demo = build_pass076_demo()
    snapshot = demo["snapshot"]
    registry = operation_registry()
    transaction = snapshot["repair_transactions"]["repair:pass076:omega"]
    repaired_run = snapshot["execution_runs"]["execution:repair:pass076:omega"]
    executable = snapshot["executable_ir_objects"]["executable-ir:repair:pass076:omega"]
    body = {
        "schema": "HHS_PASS_076_INTERPRETER_AND_REPAIR_RELEASE_BUNDLE_V1",
        "pass_id": PASS_ID,
        "version": VERSION,
        "parent_native_pass": PARENT_NATIVE_PASS,
        "platform_dependency": {"pass_id": "PASS_072", "total_system_root_hash72": FROZEN_PASS072_SYSTEM_ROOT_HASH72, "foundation_modified": False},
        "workspace_dependencies": {"pass_074_modified": False, "pass_075_modified": False},
        "operation_registry": registry,
        "executable_ir_root_hash72": executable["executable_ir_root_hash72"],
        "repaired_execution_root_hash72": repaired_run["execution_run_root_hash72"],
        "repair_transaction_root_hash72": transaction["repair_transaction_root_hash72"],
        "workspace_state": snapshot,
        "interpreter_execution_available": True,
        "bounded_product_repair_available": True,
        "compiler_execution_available": False,
        "emulator_execution_available": False,
        "new_orphan_modules": 0,
        "thread_context_required": False,
        "llm_context_window_required": False,
        "host_path_required": False,
    }
    body["product_root_hash72"] = product_root("pass076_release_bundle", body)
    return stable(body)


def write_release_artifacts(root: Optional[str | Path] = None) -> Dict[str, Any]:
    repo = Path(root).resolve() if root else Path(__file__).resolve().parents[2]
    out = repo / "native_projects/hhs_harmonicode_interpreter/artifacts"
    out.mkdir(parents=True, exist_ok=True)
    bundle = build_pass076_release_bundle()
    state = bundle["workspace_state"]
    artifacts = {
        "HHS_PASS_076_INTERPRETER_AND_REPAIR_RELEASE_BUNDLE.json": bundle,
        "PASS_076_INTERPRETER_WORKSPACE_STATE.json": state,
        "PASS_076_API_OPERATION_REGISTRY.json": bundle["operation_registry"],
        "PASS_076_EXECUTABLE_IR.json": state["executable_ir_objects"]["executable-ir:repair:pass076:omega"],
        "PASS_076_INTERPRETER_EXECUTION_RUN.json": state["execution_runs"]["execution:repair:pass076:omega"],
        "PASS_076_REPAIR_TRANSACTION.json": state["repair_transactions"]["repair:pass076:omega"],
        "PASS_076_REPAIR_ROLLBACK_CAPSULE.json": state["repair_rollbacks"]["rollback:repair:pass076:omega"],
        "PASS_076_REPAIR_TEST_RECEIPT.json": next(iter(state["repair_test_receipts"].values())),
    }
    for name, value in artifacts.items():
        (out / name).write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return bundle


if __name__ == "__main__":
    print(json.dumps(write_release_artifacts(), indent=2, sort_keys=True, ensure_ascii=False))
