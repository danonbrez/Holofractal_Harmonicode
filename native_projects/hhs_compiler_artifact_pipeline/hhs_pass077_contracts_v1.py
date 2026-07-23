"""Canonical product-local contracts for Pass 077.

Compilation is a verified semantic projection. These roots are product-local
commitment witnesses and never claim frozen Pass 072 foundation authority.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping, Sequence
import hashlib

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import (
    FROZEN_PASS072_SYSTEM_ROOT_HASH72,
    ContractError,
    product_root,
    product_witness,
    sha256,
    stable,
)

PASS_ID = "PASS_077"
VERSION = "PASS_077_COMPILER_AND_ARTIFACT_LINEAGE_PIPELINE_V1"
PARENT_NATIVE_PASS = "PASS_076"

TARGET_CONTRACT_SCHEMA = "HHS_COMPILER_TARGET_CONTRACT_V1"
REGISTERED_TARGET_CONTRACT_SCHEMA = "HHS_REGISTERED_COMPILER_TARGET_CONTRACT_V1"
COMPILATION_REQUEST_SCHEMA = "HHS_COMPILATION_REQUEST_V1"
COMPILATION_PLAN_SCHEMA = "HHS_COMPILATION_PLAN_V1"
TARGET_IR_SCHEMA = "HHS_TARGET_IR_V1"
OPTIMIZATION_PROOF_SCHEMA = "HHS_OPTIMIZATION_PROOF_V1"
COMPILED_ARTIFACT_SCHEMA = "HHS_COMPILED_ARTIFACT_V1"
COMPILED_EXECUTION_SCHEMA = "HHS_PORTABLE_BYTECODE_EXECUTION_V1"
SEMANTIC_PROJECTION_SCHEMA = "HHS_CANONICAL_PROGRAM_SEMANTIC_PROJECTION_V1"
EQUIVALENCE_RECEIPT_SCHEMA = "HHS_INTERPRETER_COMPILER_EQUIVALENCE_RECEIPT_V1"
LINEAGE_CERTIFICATE_SCHEMA = "HHS_ARTIFACT_LINEAGE_CERTIFICATE_V1"
ARTIFACT_MANIFEST_SCHEMA = "HHS_ARTIFACT_MANIFEST_V1"
EXPORT_PACKAGE_SCHEMA = "HHS_DETERMINISTIC_PACKAGE_V1"
DELTA_SCHEMA = "HHS_EXACT_ARTIFACT_DELTA_V1"
DELTA_RECEIPT_SCHEMA = "HHS_DELTA_RECONSTRUCTION_RECEIPT_V1"
FOREIGN_NUMERIC_BOUNDARY_SCHEMA = "HHS_FOREIGN_NUMERIC_BOUNDARY_V1"
REPLAY_CAPSULE_SCHEMA = "HHS_PASS_077_COMPILER_REPLAY_CAPSULE_V1"
PROGRAM_GRAPH_SCHEMA = "HHS_NATIVE_PROGRAM_REACHABILITY_GRAPH_V1"

TARGET_ID = "HHS_PORTABLE_BYTECODE_V1"
TARGET_VERSION = "0.1.0"
BYTECODE_MAGIC = b"HHSBC1\n"
MAX_BYTECODE_INSTRUCTIONS = 256
MAX_ARTIFACT_BYTES = 2_000_000

ARTIFACT_STATUSES = {"CANDIDATE", "VALIDATED", "ADMITTED", "REJECTED", "REVOKED"}
SEMANTIC_FIELDS = (
    "output_values",
    "symbolic_relations",
    "ordered_products",
    "reciprocal_bindings",
    "gate_results",
    "zero_sum_closure",
    "required_invariants",
    "declared_effects",
    "authority_scope",
    "source_identity",
)
REQUIRED_COMPILATION_LINEAGE_FIELDS = (
    "requirement_root_hash72",
    "source_artifact_root_hash72",
    "typed_ir_root_hash72",
    "executable_ir_root_hash72",
    "compilation_plan_root_hash72",
)
SUPPORTED_TARGET_OPERATIONS = (
    "GATE_DECLARE",
    "GATE_INVOKE",
    "RELATION_EQUAL",
    "ORDERED_DISTINCT",
    "EXPRESSION_EVAL",
)
UNSUPPORTED_TARGET_OPERATIONS = (
    "UNDECLARED_SYSCALL",
    "RANDOM",
    "FLOAT_OPERATION",
    "WALL_CLOCK_TIME",
    "FILESYSTEM",
    "NETWORK",
    "UNDECLARED_FOREIGN_CALL",
)


def rooted(label: str, payload: Mapping[str, Any], root_field: str) -> Dict[str, Any]:
    body = stable(dict(payload))
    body[root_field] = product_root(label, body)
    return stable(body)


def verify_rooted(label: str, payload: Mapping[str, Any], root_field: str) -> bool:
    body = deepcopy(dict(payload))
    supplied = str(body.pop(root_field, ""))
    return bool(supplied) and supplied == product_root(label, body)


def target_contract_body() -> Dict[str, Any]:
    return stable({
        "schema": TARGET_CONTRACT_SCHEMA,
        "target_id": TARGET_ID,
        "target_version": TARGET_VERSION,
        "source_ir_schema": "HHS_EXECUTABLE_IR_V1",
        "target_ir_schema": TARGET_IR_SCHEMA,
        "artifact_schema": COMPILED_ARTIFACT_SCHEMA,
        "semantic_preservation_invariant": "COMPILATION_CHANGES_REPRESENTATION_NOT_ADMITTED_MEANING",
        "required_compilation_request_fields": list(REQUIRED_COMPILATION_LINEAGE_FIELDS),
        "semantic_projection": {
            "schema": SEMANTIC_PROJECTION_SCHEMA,
            "required_fields": list(SEMANTIC_FIELDS),
            "comparison": "EXACT_CANONICAL_PROJECTION_ROOT_EQUALITY",
        },
        "semantic_identity_gate": {
            "rejection_code": "REJECT_INTERPRETER_COMPILER_SEMANTIC_DIVERGENCE",
            "receipt_schema": EQUIVALENCE_RECEIPT_SCHEMA,
            "fallback": "NONE",
            "artifact_status_on_failure": "REJECTED",
            "canonical_continuation_on_failure": False,
        },
        "permitted_representation_changes": [
            "INSTRUCTION_ENCODING",
            "REGISTER_ASSIGNMENT",
            "CONTROL_FLOW_LAYOUT",
            "CONSTANT_FOLDING_WITH_EQUIVALENCE_WITNESS",
            "DEAD_CODE_ELIMINATION_WITH_EFFECT_AND_REACHABILITY_PROOF",
        ],
        "forbidden_semantic_changes": [
            "ORDERED_PRODUCT_REORDERING",
            "RECIPROCAL_RELATION_REMOVAL",
            "GATE_SEMANTIC_MUTATION",
            "EXACT_NUMERIC_MUTATION",
            "AUTHORITY_SCOPE_MUTATION",
            "SOURCE_IDENTITY_SUBSTITUTION",
            "PROVENANCE_OBFUSCATION",
        ],
        "numeric_model": {
            "integer": "EXACT",
            "rational": "EXACT",
            "float": "FORBIDDEN",
            "foreign_numeric_boundary_schema": FOREIGN_NUMERIC_BOUNDARY_SCHEMA,
        },
        "effect_model": "DECLARED_ONLY",
        "deterministic": True,
        "reference_interpreter_required": True,
        "differential_validation_required": True,
        "supported_operations": list(SUPPORTED_TARGET_OPERATIONS),
        "unsupported_operations": list(UNSUPPORTED_TARGET_OPERATIONS),
        "required_export_evidence": [
            "HHS_COMPILATION_RECEIPT_V1",
            "HHS_TEST_EVIDENCE_RECORD_V1",
            EQUIVALENCE_RECEIPT_SCHEMA,
            LINEAGE_CERTIFICATE_SCHEMA,
        ],
        "independent_verification_required": True,
        "embedded_validator_self_authorizes": False,
    })


def registered_portable_bytecode_contract() -> Dict[str, Any]:
    contract = target_contract_body()
    root = product_root("pass077_compiler_target_contract", contract)
    return stable({
        "schema": REGISTERED_TARGET_CONTRACT_SCHEMA,
        "contract": contract,
        "contract_root_hash72": root,
        "witness": product_witness("pass077_compiler_target_contract", contract),
        "registration_authority": "PASS_077_NATIVE_PRODUCT_CONTRACT_REGISTRY",
        "foundation_modified": False,
    })


def validate_registered_target_contract(value: Mapping[str, Any]) -> Dict[str, Any]:
    item = stable(value)
    if item.get("schema") != REGISTERED_TARGET_CONTRACT_SCHEMA:
        raise ContractError("REJECT_TARGET_CONTRACT_REGISTRATION_SCHEMA")
    contract = item.get("contract")
    if not isinstance(contract, dict) or contract.get("schema") != TARGET_CONTRACT_SCHEMA:
        raise ContractError("REJECT_TARGET_CONTRACT_SCHEMA")
    observed = product_root("pass077_compiler_target_contract", contract)
    if item.get("contract_root_hash72") != observed:
        raise ContractError("REJECT_TARGET_CONTRACT_ROOT_MISMATCH")
    semantic = contract.get("semantic_projection", {})
    if contract.get("semantic_identity_gate", {}).get("rejection_code") != "REJECT_INTERPRETER_COMPILER_SEMANTIC_DIVERGENCE":
        raise ContractError("REJECT_TARGET_CONTRACT_MISSING_SEMANTIC_GATE")
    fields = semantic.get("required_fields", [])
    unknown = sorted(set(fields) - set(SEMANTIC_FIELDS))
    missing = sorted(set(SEMANTIC_FIELDS) - set(fields))
    if unknown:
        raise ContractError("REJECT_TARGET_CONTRACT_UNKNOWN_SEMANTIC_FIELD:" + ",".join(unknown))
    if missing:
        raise ContractError("REJECT_TARGET_CONTRACT_MISSING_SEMANTIC_FIELD:" + ",".join(missing))
    numeric = contract.get("numeric_model", {})
    if numeric.get("integer") != "EXACT" or numeric.get("rational") != "EXACT" or numeric.get("float") != "FORBIDDEN":
        raise ContractError("REJECT_TARGET_CONTRACT_NONEXACT_NUMERIC_MODEL")
    if contract.get("embedded_validator_self_authorizes") is not False:
        raise ContractError("REJECT_EMBEDDED_VALIDATOR_SELF_AUTHORIZATION")
    if contract.get("source_ir_schema") != "HHS_EXECUTABLE_IR_V1":
        raise ContractError("REJECT_TARGET_CONTRACT_SOURCE_IR_SCHEMA")
    if contract.get("target_id") != TARGET_ID:
        raise ContractError("REJECT_UNKNOWN_COMPILER_TARGET")
    return item


def semantic_divergence_rejection() -> Dict[str, Any]:
    body = {
        "schema": "HHS_REJECTION_PRIMITIVE_V1",
        "rejection_code": "REJECT_INTERPRETER_COMPILER_SEMANTIC_DIVERGENCE",
        "category": "SEMANTIC_IDENTITY_VIOLATION",
        "trigger": "INTERPRETER_AND_COMPILED_CANONICAL_SEMANTIC_PROJECTION_ROOTS_DIFFER",
        "artifact_status": "REJECTED",
        "canonical_continuation": False,
        "receipt_schema": EQUIVALENCE_RECEIPT_SCHEMA,
        "execution_roots_expected_to_match": False,
        "semantic_projection_roots_required_to_match": True,
        "fallback": "NONE",
    }
    return rooted("pass077_semantic_divergence_rejection", body, "rejection_primitive_root_hash72")


def validate_compilation_request_fields(value: Mapping[str, Any], *, plan_may_be_pending: bool = False) -> None:
    required: Sequence[str] = REQUIRED_COMPILATION_LINEAGE_FIELDS
    for field in required:
        if plan_may_be_pending and field == "compilation_plan_root_hash72":
            continue
        if not str(value.get(field) or ""):
            raise ContractError(f"REJECT_COMPILATION_REQUEST_MISSING_LINEAGE_ROOT:{field}")


def validate_foreign_numeric_boundary(value: Mapping[str, Any]) -> Dict[str, Any]:
    item = stable(value)
    if item.get("schema") != FOREIGN_NUMERIC_BOUNDARY_SCHEMA:
        raise ContractError("REJECT_UNLABELED_FLOAT_CONVERSION")
    required = (
        "input_exact_value", "conversion_rule", "rounding_mode", "target_width",
        "overflow_behavior", "nan_inf_policy", "resulting_foreign_value",
        "loss_classification", "reconstruction_limits", "untrusted_status",
    )
    if any(field not in item for field in required):
        raise ContractError("REJECT_INCOMPLETE_FOREIGN_NUMERIC_BOUNDARY")
    if item.get("untrusted_status") is not True:
        raise ContractError("REJECT_FOREIGN_NUMERIC_BOUNDARY_TRUST_ESCALATION")
    return item


def artifact_transport_identity(data: bytes) -> Dict[str, Any]:
    if len(data) > MAX_ARTIFACT_BYTES:
        raise ContractError("REJECT_ARTIFACT_EXCEEDS_SIZE_BOUND")
    return {"artifact_content_sha256": hashlib.sha256(data).hexdigest(), "artifact_size_bytes": len(data)}
