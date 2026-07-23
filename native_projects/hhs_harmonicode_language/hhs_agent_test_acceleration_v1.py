"""Deterministic agent-coordinated test acceleration planning for Pass 075.

This module selects and shards tests. It does not run tests, confer authority,
or convert agent recommendations into canonical evidence.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Sequence

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, product_root, stable
from .hhs_pass075_contracts_v1 import TEST_ACCELERATION_SCHEMA

TEST_CATALOG = (
    {
        "test_id": "test:pass075:language-service",
        "path": "tests/test_hhs_pass075_harmonicode_language_service_v1.py",
        "dimensions": ["PARSER", "TYPED_IR", "SOURCE_SPAN", "LINEAGE", "REPLAY"],
        "priority": 100,
    },
    {
        "test_id": "test:pass074:workspace-protocol",
        "path": "tests/test_hhs_pass074_unified_ide_workspace_v1.py",
        "dimensions": ["UNIFIED_API", "AUTHORITY", "HANDOFF", "REPLAY"],
        "priority": 95,
    },
    {
        "test_id": "test:legacy:harmonicode-interpreter",
        "path": "tests/test_hhs_live_interpreter_v1.py",
        "dimensions": ["PARSER", "CONSTRAINT_GRAPH", "ORDERED_PRODUCT"],
        "priority": 80,
    },
    {
        "test_id": "test:pass062:reciprocal-topology",
        "path": "tests/test_hhs_global_reciprocal_contract_topology_pass062_v1.py",
        "dimensions": ["ORDERED_PRODUCT", "RECIPROCITY"],
        "priority": 70,
    },
    {
        "test_id": "test:pass068:qudit-kernel",
        "path": "tests/test_hhs_three_lane_81_cell_qudit_kernel_pass068_v1.py",
        "dimensions": ["LO_SHU", "THETA15", "QUDIT81"],
        "priority": 60,
    },
)


def test_catalog() -> Dict[str, Any]:
    body = {
        "schema": "HHS_TEST_CAPABILITY_CATALOG_PASS_075_V1",
        "tests": list(TEST_CATALOG),
        "catalog_is_repository_relative": True,
    }
    body["catalog_root_hash72"] = product_root("pass075_test_catalog", body)
    return stable(body)


def _dimensions(typed_ir: Mapping[str, Any]) -> List[str]:
    dimensions = {"PARSER", "TYPED_IR", "SOURCE_SPAN", "LINEAGE", "REPLAY"}
    node_kinds = {str(x.get("node_kind") or "") for x in typed_ir.get("blocks", [])}
    symbols = {str(x.get("spelling") or "") for x in typed_ir.get("symbol_table", [])}
    operand_types = {
        str(t.get("type_id") or "")
        for block in typed_ir.get("blocks", [])
        for t in block.get("operand_types", [])
    }
    if node_kinds & {"ChainEquality", "AssertEquality", "DistinctChain"}:
        dimensions.add("CONSTRAINT_GRAPH")
    if "ORDERED_PRODUCT" in operand_types:
        dimensions.update({"ORDERED_PRODUCT", "RECIPROCITY"})
    if symbols & {"Θ15", "Theta15", "Ω", "Δe", "Ψ"}:
        dimensions.update({"LO_SHU", "THETA15"})
    return sorted(dimensions)


def build_test_acceleration_plan(
    *, plan_id: str, project_id: str, proposal: Mapping[str, Any],
    typed_ir: Mapping[str, Any], coordinating_agents: Sequence[Mapping[str, Any]],
    alignment_decision: Mapping[str, Any], requested_tests: Iterable[str] = (),
) -> Dict[str, Any]:
    if not alignment_decision.get("admitted"):
        raise ContractError("REJECT_TEST_ACCELERATION_FOR_UNALIGNED_PROPOSAL")
    if proposal.get("project_id") != project_id:
        raise ContractError("REJECT_TEST_ACCELERATION_PROJECT_MISMATCH")
    agents = sorted(coordinating_agents, key=lambda x: str(x.get("agent_id") or ""))
    if not agents:
        raise ContractError("REJECT_TEST_ACCELERATION_WITHOUT_REGISTERED_AGENT")
    dimensions = _dimensions(typed_ir)
    selected = [x for x in TEST_CATALOG if set(x["dimensions"]) & set(dimensions)]
    by_path = {x["path"]: dict(x) for x in selected}
    for path in sorted({str(x) for x in requested_tests if str(x)} | set(proposal.get("requested_tests", []))):
        by_path.setdefault(path, {
            "test_id": f"test:requested:{product_root('pass075_requested_test', {'path': path})[-12:]}",
            "path": path,
            "dimensions": ["REQUESTED"],
            "priority": 90,
        })
    ordered = sorted(by_path.values(), key=lambda x: (-int(x["priority"]), x["path"]))
    shards = []
    for index, test in enumerate(ordered):
        agent = agents[index % len(agents)]
        shards.append({
            "shard_id": f"shard:{index + 1}",
            "test": test,
            "assigned_agent_ref": agent["agent_id"],
            "agent_registration_confers_no_test_authority": True,
        })
    negative_cases = [
        "REJECT_TAMPERED_IR_ROOT",
        "REJECT_SOURCE_SPAN_DRIFT",
        "REJECT_UNAUTHORIZED_ORDERED_PRODUCT_COMMUTATION",
        "REJECT_IR_COMMIT_WITHOUT_COMMITTED_SOURCE_LINEAGE",
        "REJECT_TEST_PLAN_WITHOUT_ALIGNED_PROPOSAL",
    ]
    body = {
        "schema": TEST_ACCELERATION_SCHEMA,
        "plan_id": plan_id,
        "project_id": project_id,
        "proposal_ref": proposal.get("proposal_id"),
        "typed_ir_ref": typed_ir.get("ir_id"),
        "alignment_decision_ref": alignment_decision.get("alignment_decision_id"),
        "selection_dimensions": dimensions,
        "selected_tests": ordered,
        "parallel_shards": shards,
        "coordinating_agent_refs": [x["agent_id"] for x in agents],
        "negative_cases": negative_cases,
        "test_execution_performed": False,
        "test_evidence_required_after_execution": True,
        "agent_recommendation_is_not_test_evidence": True,
        "test_plan_confers_no_mutation_authority": True,
        "repository_relative_paths_only": True,
    }
    body["test_plan_root_hash72"] = product_root("pass075_test_acceleration_plan", body)
    return stable(body)
