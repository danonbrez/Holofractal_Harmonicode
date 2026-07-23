from __future__ import annotations

import base64
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, make_request, product_root, stable
from native_projects.hhs_compiler_artifact_pipeline.hhs_artifact_lineage_pipeline_v1 import (
    build_export_package,
    build_lineage_certificate,
    package_bytes,
    transition_artifact_status,
    verify_lineage_certificate,
)
from native_projects.hhs_compiler_artifact_pipeline.hhs_canonical_semantic_projection_v1 import canonical_semantic_projection
from native_projects.hhs_compiler_artifact_pipeline.hhs_exact_artifact_delta_v1 import apply_delta, create_delta
from native_projects.hhs_compiler_artifact_pipeline.hhs_independent_artifact_verifier_v1 import verifier_source, verify_package_object
from native_projects.hhs_compiler_artifact_pipeline.hhs_interpreter_compiler_equivalence_gate_v1 import build_equivalence_receipt, enforce_equivalence
from native_projects.hhs_compiler_artifact_pipeline.hhs_pass077_contracts_v1 import (
    TARGET_ID,
    artifact_transport_identity,
    registered_portable_bytecode_contract,
    semantic_divergence_rejection,
    validate_compilation_request_fields,
    validate_foreign_numeric_boundary,
    validate_registered_target_contract,
    verify_rooted,
)
from native_projects.hhs_compiler_artifact_pipeline.hhs_pass077_program_graph_v1 import build_program_graph
from native_projects.hhs_compiler_artifact_pipeline.hhs_pass077_replay_runner_v1 import replay_compiler_workspace, verify_capsule
from native_projects.hhs_compiler_artifact_pipeline.hhs_pass077_workspace_runtime_v1 import (
    HHSCompilerArtifactWorkspaceRuntime,
    build_pass077_demo,
    build_pass077_release_bundle,
    operation_registry,
)
from native_projects.hhs_compiler_artifact_pipeline.hhs_portable_bytecode_v1 import (
    artifact_bytes,
    build_compilation_plan,
    emit_candidate_artifact,
    execute_bytecode,
    lower_to_target_ir,
    optimize_target_ir,
    replay_compiled_execution,
    verify_target_ir,
)


@pytest.fixture(scope="module")
def release():
    return build_pass077_release_bundle()


@pytest.fixture()
def demo():
    return build_pass077_demo()


def objects(release):
    state = release["workspace_state"]
    return {
        "state": state,
        "contract": state["compiler_target_contracts"][TARGET_ID],
        "executable": state["executable_ir_objects"]["executable-ir:repair:pass076:omega"],
        "interpreter": state["execution_runs"]["execution:repair:pass076:omega"],
        "plan": state["compilation_plans"]["compilation:pass077:portable"],
        "request": state["compilation_requests"]["compilation:pass077:portable"],
        "target_ir": state["target_ir_objects"]["target-ir:pass077:portable"],
        "proof": state["optimization_proofs"]["optimization:pass077:identity"],
        "artifact": state["compiled_artifacts"]["artifact:pass077:portable"],
        "compiled": state["compiled_executions"]["compiled-execution:pass077:portable"],
        "equivalence": state["equivalence_receipts"]["equivalence:pass077:portable"],
        "lineage": state["lineage_certificates"]["lineage:pass077:portable"],
        "package": state["export_packages"]["package:pass077:portable"],
        "verification": state["external_verifications"]["external-verification:pass077:portable"],
    }


def reroot(label, value, field):
    body = deepcopy(value); body.pop(field, None); body[field] = product_root(label, body); return stable(body)


def test_registered_target_contract_is_valid_and_rooted():
    contract = validate_registered_target_contract(registered_portable_bytecode_contract())
    assert contract["contract"]["target_id"] == TARGET_ID
    assert contract["contract"]["numeric_model"] == {"integer": "EXACT", "rational": "EXACT", "float": "FORBIDDEN", "foreign_numeric_boundary_schema": "HHS_FOREIGN_NUMERIC_BOUNDARY_V1"}


def test_contract_missing_semantic_gate_is_rejected():
    item = registered_portable_bytecode_contract(); del item["contract"]["semantic_identity_gate"]
    item["contract_root_hash72"] = product_root("pass077_compiler_target_contract", item["contract"])
    with pytest.raises(ContractError, match="REJECT_TARGET_CONTRACT_MISSING_SEMANTIC_GATE"):
        validate_registered_target_contract(item)


def test_contract_unknown_semantic_field_is_rejected():
    item = registered_portable_bytecode_contract(); item["contract"]["semantic_projection"]["required_fields"].append("invented_field")
    item["contract_root_hash72"] = product_root("pass077_compiler_target_contract", item["contract"])
    with pytest.raises(ContractError, match="REJECT_TARGET_CONTRACT_UNKNOWN_SEMANTIC_FIELD"):
        validate_registered_target_contract(item)


def test_contract_self_authorization_is_rejected():
    item = registered_portable_bytecode_contract(); item["contract"]["embedded_validator_self_authorizes"] = True
    item["contract_root_hash72"] = product_root("pass077_compiler_target_contract", item["contract"])
    with pytest.raises(ContractError, match="REJECT_EMBEDDED_VALIDATOR_SELF_AUTHORIZATION"):
        validate_registered_target_contract(item)


def test_rejection_primitive_requires_distinct_execution_but_equal_semantics():
    rejection = semantic_divergence_rejection()
    assert rejection["execution_roots_expected_to_match"] is False
    assert rejection["semantic_projection_roots_required_to_match"] is True
    assert verify_rooted("pass077_semantic_divergence_rejection", rejection, "rejection_primitive_root_hash72")


def test_compilation_request_missing_lineage_root_is_rejected():
    with pytest.raises(ContractError, match="REJECT_COMPILATION_REQUEST_MISSING_LINEAGE_ROOT"):
        validate_compilation_request_fields({"requirement_root_hash72": "r"})


def test_plan_binds_exact_registered_contract_and_complete_lineage(release):
    o = objects(release)
    assert o["request"]["compilation_plan_root_hash72"] == o["plan"]["compilation_plan_root_hash72"]
    assert o["plan"]["target_contract_root_hash72"] == o["contract"]["contract_root_hash72"]
    assert o["plan"]["executable_ir_root_hash72"] == o["executable"]["executable_ir_root_hash72"]


def test_unsupported_operation_is_rejected_before_lowering(release):
    o = objects(release); executable = deepcopy(o["executable"])
    statement = executable["statements"][1]; statement["operation"] = "UNDECLARED_SYSCALL"
    executable["statements"][1] = reroot("pass076_executable_statement", statement, "statement_root_hash72")
    executable = reroot("pass076_executable_ir", executable, "executable_ir_root_hash72")
    with pytest.raises(ContractError, match="REJECT_TARGET_INVOKES_UNSUPPORTED_OPERATION"):
        build_compilation_plan(compilation_id="bad", executable_ir=executable, target_contract=o["contract"], requirement_root_hash72="req", source_artifact_root_hash72=executable["source_artifact_root_hash72"], typed_ir_root_hash72=executable["typed_ir_root_hash72"], test_receipt_root_hash72="test")


def test_target_ir_is_deterministic_and_preserves_instruction_order(release):
    o = objects(release)
    left = lower_to_target_ir(target_ir_id="target:det", executable_ir=o["executable"], compilation_plan=o["plan"], target_contract=o["contract"])
    right = lower_to_target_ir(target_ir_id="target:det", executable_ir=o["executable"], compilation_plan=o["plan"], target_contract=o["contract"])
    assert left == right
    assert verify_target_ir(left)
    assert [x["instruction_index"] for x in left["instructions"]] == list(range(1, left["instruction_count"] + 1))


def test_optimization_requires_registered_rewrite(release):
    o = objects(release)
    with pytest.raises(ContractError, match="REJECT_UNREGISTERED_OPTIMIZATION"):
        optimize_target_ir(optimization_id="bad", target_ir=o["target_ir"], optimization="UNWITNESSED_REORDER")


def test_identity_optimization_proof_declares_every_preservation_obligation(release):
    proof = objects(release)["proof"]
    assert proof["preserved_semantics"] and proof["preserved_ordering"] and proof["preserved_effects"] and proof["preserved_invariants"]
    assert proof["equivalence_test_passed"] is True


def test_artifact_bytes_are_reproducible(release):
    o = objects(release)
    candidate1 = emit_candidate_artifact(artifact_id="artifact:repro", target_ir=o["target_ir"], optimization_proof=o["proof"])
    candidate2 = emit_candidate_artifact(artifact_id="artifact:repro", target_ir=o["target_ir"], optimization_proof=o["proof"])
    assert artifact_bytes(candidate1) == artifact_bytes(candidate2)
    assert candidate1["artifact_content_sha256"] == candidate2["artifact_content_sha256"]


def test_sha256_is_raw_byte_integrity_not_hash72(release):
    data = artifact_bytes(objects(release)["artifact"])
    identity = artifact_transport_identity(data)
    assert identity["artifact_content_sha256"] == hashlib.sha256(data).hexdigest()
    assert len(identity["artifact_content_sha256"]) == 64


def test_interpreter_and_compiled_execution_roots_differ_but_semantic_roots_match(release):
    o = objects(release)
    assert o["interpreter"]["execution_run_root_hash72"] != o["compiled"]["compiled_execution_root_hash72"]
    assert o["equivalence"]["semantic_projection_roots_match"] is True
    assert o["equivalence"]["status"] == "SEMANTIC_IDENTITY_VERIFIED"


def malicious_compiled_run(o, field, mutate):
    run = deepcopy(o["compiled"])
    for receipt in run["step_receipts"]:
        outcome = receipt.get("outcome", {})
        if field == "ordered_products" and receipt["operation"] == "ORDERED_DISTINCT":
            mutate(outcome["observations"][0]); break
        if field in {"reciprocal_bindings", "output_values"} and receipt["operation"] == "RELATION_EQUAL":
            obs = outcome.get("observations", [])[0]
            if field == "reciprocal_bindings" and obs["left_text"] == "x": mutate(obs); break
            if field == "output_values" and obs["left_text"] == "Δe": mutate(obs); run["final_state"]["bindings"]["Δe"] = obs["left_value"]; break
    run = reroot("pass077_portable_bytecode_execution", run, "compiled_execution_root_hash72")
    return run


def test_changed_ordered_product_history_triggers_semantic_divergence(release):
    o = objects(release)
    bad = malicious_compiled_run(o, "ordered_products", lambda obs: obs.update({"right_text": "xy", "right_value": obs["left_value"], "distinct": False}))
    receipt, _, _ = build_equivalence_receipt(receipt_id="eq:ordered", target_contract=o["contract"], executable_ir=o["executable"], compiled_artifact=o["artifact"], interpreter_execution=o["interpreter"], compiled_execution=bad)
    assert "REJECT_OPTIMIZATION_ORDERED_PRODUCT_CHANGE" in receipt["field_rejection_codes"]
    with pytest.raises(ContractError, match="REJECT_INTERPRETER_COMPILER_SEMANTIC_DIVERGENCE"): enforce_equivalence(receipt)


def test_dropped_reciprocal_binding_triggers_semantic_divergence(release):
    o = objects(release)
    bad = malicious_compiled_run(o, "reciprocal_bindings", lambda obs: obs.update({"right_value": {"type": "SYMBOL", "name": "y"}, "left_value": {"type": "SYMBOL", "name": "y"}}))
    receipt, _, _ = build_equivalence_receipt(receipt_id="eq:reciprocal", target_contract=o["contract"], executable_ir=o["executable"], compiled_artifact=o["artifact"], interpreter_execution=o["interpreter"], compiled_execution=bad)
    assert "REJECT_OPTIMIZATION_RECIPROCAL_DROP" in receipt["field_rejection_codes"]


def test_changed_exact_rational_result_triggers_semantic_divergence(release):
    o = objects(release)
    bad = malicious_compiled_run(o, "output_values", lambda obs: obs.update({"left_value": {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 2}, "right_value": {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 2}}))
    receipt, _, _ = build_equivalence_receipt(receipt_id="eq:rational", target_contract=o["contract"], executable_ir=o["executable"], compiled_artifact=o["artifact"], interpreter_execution=o["interpreter"], compiled_execution=bad)
    assert "REJECT_OPTIMIZATION_RATIONAL_MISMATCH" in receipt["field_rejection_codes"]


def test_authority_scope_mutation_is_rejected(release):
    o = objects(release); executable = deepcopy(o["executable"])
    executable["statements"][0]["authority_requirements"] = ["authority:invented"]
    executable["statements"][0] = reroot("pass076_executable_statement", executable["statements"][0], "statement_root_hash72")
    executable = reroot("pass076_executable_ir", executable, "executable_ir_root_hash72")
    # The compiler artifact remains bound to the original executable identity.
    with pytest.raises(ContractError, match="REJECT_EQUIVALENCE_EXECUTABLE_IR_MISMATCH"):
        build_equivalence_receipt(receipt_id="eq:authority", target_contract=o["contract"], executable_ir=executable, compiled_artifact=o["artifact"], interpreter_execution=o["interpreter"], compiled_execution=o["compiled"])


def test_source_identity_substitution_is_rejected(release):
    o = objects(release); artifact = deepcopy(o["artifact"]); artifact["executable_ir_root_hash72"] = "substituted"
    artifact = reroot("pass077_compiled_artifact", artifact, "artifact_root_hash72")
    with pytest.raises(ContractError, match="REJECT_EQUIVALENCE_EXECUTABLE_IR_MISMATCH"):
        build_equivalence_receipt(receipt_id="eq:source", target_contract=o["contract"], executable_ir=o["executable"], compiled_artifact=artifact, interpreter_execution=o["interpreter"], compiled_execution=o["compiled"])


def test_artifact_tampering_after_certification_is_rejected(release):
    artifact = deepcopy(objects(release)["artifact"])
    data = bytearray(base64.b64decode(artifact["artifact_bytes_base64"])); data[-1] ^= 1
    artifact["artifact_bytes_base64"] = base64.b64encode(bytes(data)).decode("ascii")
    artifact = reroot("pass077_compiled_artifact", artifact, "artifact_root_hash72")
    with pytest.raises(ContractError, match="REJECT_ARTIFACT_TAMPERED"):
        artifact_bytes(artifact)


def test_lineage_requires_genesis_or_parent_but_not_both(release):
    o = objects(release); validated = transition_artifact_status(emit_candidate_artifact(artifact_id="artifact:lineage", target_ir=o["target_ir"], optimization_proof=o["proof"]), status="VALIDATED", equivalence_receipt_root_hash72=o["equivalence"]["receipt_root_hash72"])
    kwargs = dict(certificate_id="lineage:test", artifact=validated, project_root_hash72="project", requirement_root_hash72="requirement", source_artifact_root_hash72=o["executable"]["source_artifact_root_hash72"], typed_ir_root_hash72=o["executable"]["typed_ir_root_hash72"], executable_ir_root_hash72=o["executable"]["executable_ir_root_hash72"], compilation_plan_root_hash72=o["plan"]["compilation_plan_root_hash72"], target_contract_root_hash72=o["contract"]["contract_root_hash72"], interpreter_reference_execution_root_hash72=o["interpreter"]["execution_run_root_hash72"], compiled_execution_root_hash72=o["compiled"]["compiled_execution_root_hash72"], semantic_equivalence_receipt_root_hash72=o["equivalence"]["receipt_root_hash72"], test_receipt_root_hash72="test")
    with pytest.raises(ContractError, match="REJECT_LINEAGE_REQUIRES_EXACTLY_ONE_GENESIS_OR_PARENT"): build_lineage_certificate(**kwargs)
    with pytest.raises(ContractError, match="REJECT_LINEAGE_REQUIRES_EXACTLY_ONE_GENESIS_OR_PARENT"): build_lineage_certificate(**kwargs, genesis_source_root_hash72="g", parent_artifact_root_hash72="p")
    cert = build_lineage_certificate(**kwargs, genesis_source_root_hash72="g")
    assert verify_lineage_certificate(cert)


def test_lineage_resolves_requirement_source_ir_tests_and_compiler(release):
    cert = objects(release)["lineage"]
    for field in ("requirement_root_hash72", "source_artifact_root_hash72", "typed_ir_root_hash72", "executable_ir_root_hash72", "compilation_plan_root_hash72", "target_contract_root_hash72", "test_receipt_root_hash72", "compiler_identity"):
        assert cert[field]


def test_independent_package_verifier_reexecutes_both_paths(release):
    verification = verify_package_object(objects(release)["package"])
    assert verification["status"] == "REEXECUTED_SEMANTIC_EQUIVALENCE"
    assert verification["interpreter_execution_replayed"] is True
    assert verification["compiled_execution_replayed"] is True
    assert verification["originating_repository_required"] is False


def test_package_tampering_is_rejected(release):
    package = deepcopy(objects(release)["package"]); data = bytearray(package_bytes(package)); data[-10] ^= 1
    package["package_bytes_base64"] = base64.b64encode(bytes(data)).decode("ascii")
    package = reroot("pass077_export_package", package, "package_root_hash72")
    with pytest.raises(ContractError, match="REJECT_EXPORT_PACKAGE_TAMPERED"): package_bytes(package)


def test_embedded_verifier_is_zero_dependency_standard_library_only():
    source = verifier_source()
    forbidden = ("native_projects.", "hhs_runtime", "requests", "fastapi", "numpy")
    assert not any(token in source for token in forbidden)
    compile(source, "verify_artifact.py", "exec")


def test_external_verifier_cli_works_on_package_file(tmp_path, release):
    package_path = tmp_path / "program.hhspkg"; package_path.write_bytes(package_bytes(objects(release)["package"]))
    script = Path(__file__).parents[1] / "native_projects/hhs_compiler_artifact_pipeline/verifier/verify_artifact.py"
    completed = subprocess.run([sys.executable, str(script), str(package_path)], text=True, capture_output=True, check=False)
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["status"] == "REEXECUTED_SEMANTIC_EQUIVALENCE"


def base_candidate(o, target_id="target:delta-base"):
    target = lower_to_target_ir(target_ir_id=target_id, executable_ir=o["executable"], compilation_plan=o["plan"], target_contract=o["contract"])
    _, proof = optimize_target_ir(optimization_id="optimization:delta-base", target_ir=target)
    return emit_candidate_artifact(artifact_id="artifact:delta-base", target_ir=target, optimization_proof=proof)


def test_delta_reconstructs_exact_target_bytes(release):
    o = objects(release); base = base_candidate(o); delta = create_delta(delta_id="delta:test", base_artifact=base, target_artifact=o["artifact"], target_lineage=o["lineage"])
    reconstructed, receipt = apply_delta(base_artifact=base, delta=delta)
    assert reconstructed == artifact_bytes(o["artifact"])
    assert receipt["exact_target_bytes_reconstructed"] is True


def test_delta_rejects_wrong_base(release):
    o = objects(release); base = base_candidate(o); other = base_candidate(o, "target:other")
    delta = create_delta(delta_id="delta:test", base_artifact=base, target_artifact=o["artifact"], target_lineage=o["lineage"])
    with pytest.raises(ContractError, match="REJECT_DELTA_BASE_ROOT_MISMATCH"): apply_delta(base_artifact=other, delta=delta)


def test_delta_requires_target_lineage(release):
    o = objects(release); base = base_candidate(o)
    with pytest.raises(ContractError, match="REJECT_DELTA_WITHOUT_TARGET_LINEAGE"):
        create_delta(delta_id="delta:no-lineage", base_artifact=base, target_artifact=o["artifact"], target_lineage={})


def test_unlabeled_float_conversion_is_rejected():
    with pytest.raises(ContractError, match="REJECT_UNLABELED_FLOAT_CONVERSION"):
        validate_foreign_numeric_boundary({"input_exact_value": "1/3"})


def test_complete_foreign_numeric_boundary_remains_untrusted():
    value = validate_foreign_numeric_boundary({"schema":"HHS_FOREIGN_NUMERIC_BOUNDARY_V1","input_exact_value":{"numerator":1,"denominator":2},"conversion_rule":"IEEE754","rounding_mode":"NEAREST_EVEN","target_width":64,"overflow_behavior":"REJECT","nan_inf_policy":"FORBID","resulting_foreign_value":"0.5","loss_classification":"EXACT_FOR_VALUE","reconstruction_limits":"VALUE_ONLY","untrusted_status":True})
    assert value["untrusted_status"] is True


def test_operation_registry_has_no_private_compiler_path():
    definitions = {x["operation_id"]: x for x in operation_registry()["operations"]}
    for operation in ("workspace.compiler.plan","workspace.compiler.lower","workspace.compiler.optimize","workspace.compiler.emit","workspace.compiler.validate","workspace.compiler.replay","workspace.artifact.package","workspace.artifact.verify","workspace.artifact.export"):
        assert definitions[operation]["implemented"] is True
        assert definitions[operation]["private_authority_path"] is False
        assert definitions[operation]["unified_api_only"] is True


def test_compiler_operation_requires_authority_and_lease():
    rt = HHSCompilerArtifactWorkspaceRuntime()
    # A well-formed request still fails before semantic work because COMPILE is authority-gated.
    request = make_request(request_id="req:noauth", project_id="project:noauth", session_id="session:noauth", operation_class="COMPILE", operation_id="workspace.compiler.plan", payload={})
    response = rt.dispatch(request)
    assert response["status"] == "REJECTED"
    assert response["diagnostics"][0]["code"] == "REJECT_MUTATION_WITHOUT_AUTHORITY_AND_LEASE"


def test_rejected_candidate_never_enters_artifact_registry(demo):
    rt = demo["runtime"]; target = deepcopy(rt.target_ir_objects["target-ir:pass077:portable"])
    instruction = next(x for x in target["instructions"] if x["opcode"] == "ORDERED_DISTINCT")
    instruction["operands"] = ["xy", "xy"]
    instruction = reroot("pass077_target_instruction", instruction, "instruction_root_hash72")
    target["instructions"] = [instruction if x["instruction_index"] == instruction["instruction_index"] else x for x in target["instructions"]]
    target = reroot("pass077_target_ir", target, "target_ir_root_hash72")
    rt.target_ir_objects["target-ir:malicious"] = target
    _, proof = optimize_target_ir(optimization_id="optimization:malicious", target_ir=target)
    rt.optimization_proofs["optimization:malicious"] = proof
    candidate = emit_candidate_artifact(artifact_id="artifact:malicious", target_ir=target, optimization_proof=proof)
    rt.compiled_artifacts["artifact:malicious"] = candidate; rt.artifacts["artifact:malicious"] = candidate
    request = make_request(request_id="req:malicious", project_id="project:pass076-demo", session_id="session:pass076-demo", operation_class="COMPILE", operation_id="workspace.compiler.validate", payload={"artifact_ref":"artifact:malicious","interpreter_execution_ref":"execution:repair:pass076:omega","executable_ir_ref":"executable-ir:repair:pass076:omega","compiled_run_id":"compiled:malicious","equivalence_receipt_id":"equivalence:malicious"}, role_contract_ref="role:x", task_assignment_ref="task:x", capability_lease_ref="lease:x")
    response = rt.dispatch(request)
    assert response["status"] == "REJECTED"
    assert rt.compiled_artifacts["artifact:malicious"]["status"] == "REJECTED"
    assert "artifact:malicious" not in rt.admitted_artifact_registry


def test_compiled_replay_is_exact(release):
    o = objects(release); replay = replay_compiled_execution(execution=o["compiled"], artifact=o["artifact"])
    assert replay["matches"] is True


def test_program_graph_has_zero_orphans_and_all_modules_reusable():
    graph = build_program_graph()
    assert graph["orphan_native_module_count"] == 0
    assert graph["native_module_count"] == graph["reachable_native_module_count"]
    assert graph["all_new_modules_reusable"] is True


def test_release_bundle_preserves_parent_and_foundation(release):
    assert release["platform_dependency"]["foundation_modified"] is False
    assert release["parent_product_modified"] is False
    assert release["workspace_state"]["pass_id"] == "PASS_077"
    assert release["workspace_state"]["compiled_artifacts"]["artifact:pass077:portable"]["status"] == "ADMITTED"


def test_context_independent_replay_uses_repository_state_only():
    result = replay_compiler_workspace()
    assert result["status"] == "PASS"
    assert result["thread_context_used"] is False
    assert result["llm_context_window_used"] is False
    assert all(result["comparisons"].values())
