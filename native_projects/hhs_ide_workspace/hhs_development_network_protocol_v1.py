"""Pass 074 native development-agent networking and alignment protocol.

This module is a reusable product-layer protocol. It coordinates human, LLM,
tool, and CI agents through repository-native objects while preserving the
frozen Pass 072 platform boundary.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping, Sequence

from .hhs_workspace_contracts_v1 import (
    FROZEN_PASS072_SYSTEM_ROOT_HASH72,
    ContractError,
    product_root,
    require_identifier,
    stable,
)

DEVELOPMENT_PROTOCOL_SCHEMA = "HHS_OPEN_ENDED_NATIVE_DEVELOPMENT_PROTOCOL_V1"
AGENT_SCHEMA = "HHS_DEVELOPMENT_AGENT_IDENTITY_V1"
CHANGE_PROPOSAL_SCHEMA = "HHS_REPOSITORY_CHANGE_PROPOSAL_V1"
ALIGNMENT_DECISION_SCHEMA = "HHS_POST_FREEZE_ALIGNMENT_DECISION_V1"
TEST_RECORD_SCHEMA = "HHS_TEST_EVIDENCE_RECORD_V1"
HANDOFF_SCHEMA = "HHS_AGENT_HANDOFF_CAPSULE_V1"
HEALING_PLAN_SCHEMA = "HHS_BOUNDED_SELF_HEALING_PLAN_V1"

AGENT_KINDS = {"HUMAN", "LLM", "TOOL", "CI", "HYBRID"}
TEST_STATUSES = {"PASS", "FAIL", "ERROR", "SKIP", "UNAVAILABLE"}


def development_protocol_contract() -> Dict[str, Any]:
    body = {
        "schema": DEVELOPMENT_PROTOCOL_SCHEMA,
        "purpose": (
            "SELF_HEALING_SOFTWARE_DEVELOPMENT_ACCELERATION_ALIGNMENT_"
            "ENFORCEMENT_TESTING_ITERATION_AND_AGENT_REPOSITORY_NETWORKING"
        ),
        "platform_boundary": {
            "frozen_pass": "PASS_072",
            "frozen_total_system_root_hash72": FROZEN_PASS072_SYSTEM_ROOT_HASH72,
            "ordinary_product_development_may_modify_foundation": False,
            "foundation_repair_requires_justified_minimal_witnessed_reversible_alignment_patch": True,
        },
        "product_constraint": {
            "new_orphan_modules_permitted": False,
            "new_modules_must_be_reachable_reusable_runtime_governed_and_capability_bearing": True,
        },
        "open_ended_development": {
            "fixed_terminal_pass": False,
            "future_passes_admissible_while_constraints_hold": True,
            "repository_state_authoritative_over_conversation_state": True,
            "llm_context_window_required": False,
        },
        "agent_classes": sorted(AGENT_KINDS),
        "pass_sequence": {
            "PASS_074": "UNIFIED_WORKSPACE_API_AGENT_EXCHANGE_AND_ALIGNMENT_GATE",
            "PASS_075": "HARMONICODE_TYPED_IR_AND_AGENT_COORDINATED_TEST_ACCELERATION",
            "PASS_076_PLUS": "BOUNDED_SELF_HEALING_INTERPRETER_COMPILER_EMULATOR_AND_OPEN_ENDED_PRODUCTS",
        },
    }
    body["development_protocol_root_hash72"] = product_root("pass074_development_protocol", body)
    return stable(body)


def canonical_agent(payload: Mapping[str, Any], *, project_id: str) -> Dict[str, Any]:
    value = deepcopy(dict(payload))
    agent_id = require_identifier("agent_id", value.get("agent_id"))
    kind = str(value.get("agent_kind") or "")
    if kind not in AGENT_KINDS:
        raise ContractError(f"REJECT_AGENT_KIND:{kind}")
    capabilities = sorted({str(x) for x in value.get("capabilities", []) if str(x)})
    body = {
        "schema": AGENT_SCHEMA,
        "agent_id": agent_id,
        "project_id": project_id,
        "agent_kind": kind,
        "display_name": str(value.get("display_name") or agent_id),
        "provider_or_owner": str(value.get("provider_or_owner") or "UNSPECIFIED"),
        "capabilities": capabilities,
        "transport": str(value.get("transport") or "REPOSITORY_CAPSULE"),
        "authority_is_external_and_must_be_validated_per_operation": True,
        "registration_confers_no_platform_authority": True,
    }
    body["agent_identity_root_hash72"] = product_root("pass074_agent_identity", body)
    return stable(body)


def canonical_change_proposal(
    payload: Mapping[str, Any], *, project_id: str, proposer_agent_ref: str,
    base_workspace_state_root_hash72: str,
) -> Dict[str, Any]:
    value = deepcopy(dict(payload))
    proposal_id = require_identifier("proposal_id", value.get("proposal_id"))
    program_id = require_identifier("program_id", value.get("program_id"))
    affected_paths = sorted({str(x) for x in value.get("affected_product_paths", []) if str(x)})
    foundation_paths = sorted({str(x) for x in value.get("affected_foundation_paths", []) if str(x)})
    capabilities = sorted({str(x) for x in value.get("reusable_capabilities", []) if str(x)})
    body = {
        "schema": CHANGE_PROPOSAL_SCHEMA,
        "proposal_id": proposal_id,
        "project_id": project_id,
        "program_id": program_id,
        "proposer_agent_ref": proposer_agent_ref,
        "base_workspace_state_root_hash72": base_workspace_state_root_hash72,
        "base_platform_root_hash72": FROZEN_PASS072_SYSTEM_ROOT_HASH72,
        "summary": str(value.get("summary") or ""),
        "new_capability_statement": str(value.get("new_capability_statement") or ""),
        "reusable_capabilities": capabilities,
        "reachable_entrypoint": str(value.get("reachable_entrypoint") or ""),
        "affected_product_paths": affected_paths,
        "affected_foundation_paths": foundation_paths,
        "patch_artifact_refs": sorted({str(x) for x in value.get("patch_artifact_refs", []) if str(x)}),
        "requested_tests": sorted({str(x) for x in value.get("requested_tests", []) if str(x)}),
        "reversible_alignment_patch_ref": str(value.get("reversible_alignment_patch_ref") or ""),
        "proposal_does_not_self_authorize": True,
    }
    body["proposal_root_hash72"] = product_root("pass074_change_proposal", body)
    return stable(body)


def evaluate_proposal_alignment(proposal: Mapping[str, Any]) -> Dict[str, Any]:
    reasons = []
    foundation_paths = list(proposal.get("affected_foundation_paths", []))
    reversible_patch_ref = str(proposal.get("reversible_alignment_patch_ref") or "")
    if foundation_paths and not reversible_patch_ref:
        reasons.append("FOUNDATION_CHANGE_WITHOUT_REVERSIBLE_ALIGNMENT_PATCH")
    if not str(proposal.get("new_capability_statement") or "").strip():
        reasons.append("MISSING_NEW_CAPABILITY_STATEMENT")
    if not proposal.get("reusable_capabilities"):
        reasons.append("MISSING_REUSABLE_CAPABILITY")
    if not str(proposal.get("reachable_entrypoint") or "").strip():
        reasons.append("MISSING_REACHABLE_ENTRYPOINT")
    if not proposal.get("affected_product_paths") and not foundation_paths:
        reasons.append("NO_AFFECTED_PATHS_DECLARED")

    admitted = not reasons
    body = {
        "schema": ALIGNMENT_DECISION_SCHEMA,
        "proposal_id": proposal["proposal_id"],
        "project_id": proposal["project_id"],
        "decision": "ADMIT_PROPOSAL_TO_TEST" if admitted else "REJECT_PROPOSAL_ALIGNMENT",
        "admitted": admitted,
        "reasons": reasons,
        "foundation_constraint_satisfied": not foundation_paths or bool(reversible_patch_ref),
        "capability_constraint_satisfied": all(
            [
                bool(str(proposal.get("new_capability_statement") or "").strip()),
                bool(proposal.get("reusable_capabilities")),
                bool(str(proposal.get("reachable_entrypoint") or "").strip()),
            ]
        ),
        "platform_root_checked": FROZEN_PASS072_SYSTEM_ROOT_HASH72,
    }
    body["alignment_decision_root_hash72"] = product_root("pass074_proposal_alignment", body)
    return stable(body)


def canonical_test_record(payload: Mapping[str, Any], *, project_id: str) -> Dict[str, Any]:
    value = deepcopy(dict(payload))
    record_id = require_identifier("test_record_id", value.get("test_record_id"))
    proposal_ref = require_identifier("proposal_ref", value.get("proposal_ref"))
    status = str(value.get("status") or "")
    if status not in TEST_STATUSES:
        raise ContractError(f"REJECT_TEST_STATUS:{status}")
    body = {
        "schema": TEST_RECORD_SCHEMA,
        "test_record_id": record_id,
        "project_id": project_id,
        "proposal_ref": proposal_ref,
        "status": status,
        "passed": int(value.get("passed", 0)),
        "failed": int(value.get("failed", 0)),
        "commands": [str(x) for x in value.get("commands", [])],
        "evidence_refs": [str(x) for x in value.get("evidence_refs", [])],
        "diagnostics": stable(value.get("diagnostics", [])),
        "test_evidence_does_not_self_authorize_mutation": True,
    }
    body["test_record_root_hash72"] = product_root("pass074_test_record", body)
    return stable(body)


def build_handoff_capsule(
    payload: Mapping[str, Any], *, project_id: str, workspace_state_root_hash72: str,
) -> Dict[str, Any]:
    value = deepcopy(dict(payload))
    handoff_id = require_identifier("handoff_id", value.get("handoff_id"))
    body = {
        "schema": HANDOFF_SCHEMA,
        "handoff_id": handoff_id,
        "project_id": project_id,
        "from_agent_ref": require_identifier("from_agent_ref", value.get("from_agent_ref")),
        "to_agent_ref": require_identifier("to_agent_ref", value.get("to_agent_ref")),
        "workspace_state_root_hash72": workspace_state_root_hash72,
        "proposal_refs": [require_identifier("proposal_ref", x) for x in value.get("proposal_refs", [])],
        "test_record_refs": [require_identifier("test_record_ref", x) for x in value.get("test_record_refs", [])],
        "required_actions": [str(x) for x in value.get("required_actions", [])],
        "repository_state_authoritative": True,
        "thread_context_required": False,
        "llm_context_window_required": False,
        "handoff_confers_no_authority": True,
    }
    body["handoff_root_hash72"] = product_root("pass074_agent_handoff", body)
    return stable(body)


def build_bounded_healing_plan(
    *, proposal: Mapping[str, Any], test_record: Mapping[str, Any], requested_by_agent_ref: str,
) -> Dict[str, Any]:
    if test_record.get("proposal_ref") != proposal.get("proposal_id"):
        raise ContractError("REJECT_HEALING_PROPOSAL_TEST_MISMATCH")
    if test_record.get("status") not in {"FAIL", "ERROR"}:
        raise ContractError("REJECT_HEALING_WITHOUT_FAILED_TEST_EVIDENCE")
    if proposal.get("affected_foundation_paths"):
        raise ContractError("REJECT_AUTOMATED_HEALING_OF_FROZEN_FOUNDATION")
    plan_id = f"healing:{proposal['proposal_id']}:{test_record['test_record_id']}"
    body = {
        "schema": HEALING_PLAN_SCHEMA,
        "healing_plan_id": plan_id,
        "project_id": proposal["project_id"],
        "proposal_ref": proposal["proposal_id"],
        "test_record_ref": test_record["test_record_id"],
        "requested_by_agent_ref": requested_by_agent_ref,
        "repair_scope": list(proposal.get("affected_product_paths", [])),
        "bounded_actions": [
            "REPRODUCE_FAILED_TEST",
            "ISOLATE_PRODUCT_LOCAL_CAUSE",
            "PROPOSE_MINIMAL_REVERSIBLE_PATCH",
            "RERUN_REQUESTED_TESTS",
            "EMIT_ITERATION_RECEIPT",
        ],
        "auto_apply": False,
        "foundation_mutation_permitted": False,
        "authority_revalidation_required_before_apply": True,
        "rollback_required": True,
    }
    body["healing_plan_root_hash72"] = product_root("pass074_bounded_healing_plan", body)
    return stable(body)
