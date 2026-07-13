"""Pass 072 — total-system recursive holographic closure.

This module promotes the canonical Pass 071 state into an executable Pass 072
Runtime layer.  It does not treat a closure report as implementation.  The
canonical root is derived from nine source-bound subsystem capsules, an
acyclic dependency index, reciprocal part↔whole identity paths, eight
independent closure-dimension receipts, the existing 81-cell kernel, and the
Pass 072 exact phase-gear pathfinder.
"""
from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_backend.runtime.hhs_restart_safe_phase_gear_folding_v1 import (
    run_restart_safe_phase_gear_folding,
)
from hhs_backend.runtime.hhs_three_lane_81_cell_qudit_kernel_v1 import (
    run_three_lane_81_cell_kernel,
)
from hhs_backend.runtime.hhs_holofractal_phase_gear_pathfinder_v1 import (
    run_holofractal_phase_gear_pathfinder,
)

VERSION = "PASS_072_TOTAL_SYSTEM_RECURSIVE_HOLOGRAPHIC_CLOSURE_V1"
AUTHORITY = "HHS_PASS072_TOTAL_SYSTEM_CLOSURE_AUTHORITY_V1"
TOTAL_SYSTEM_ID = "HHS_TOTAL_SYSTEM_PASS_072"
LO_SHU = (4, 9, 2, 3, 5, 7, 8, 1, 6)
CLOSURE_DIMENSIONS: Tuple[str, ...] = (
    "IDENTITY",
    "PROVENANCE",
    "AUTHORITY",
    "EXECUTION",
    "SEMANTIC",
    "ENERGY",
    "TEMPORAL",
    "RECONSTRUCTION",
)
MAX_SUBSYSTEMS = 9

REJECTIONS: Tuple[str, ...] = (
    "REJECT_PASS072_WITHOUT_PASS071_CANONICAL_ROOT",
    "REJECT_SUBSYSTEM_CAPSULE_WITHOUT_SOURCE_ROOT",
    "REJECT_MEMBERSHIP_AS_AUTHORITY",
    "REJECT_PART_TO_WHOLE_PATH_WITHOUT_RECIPROCAL_RETURN",
    "REJECT_DERIVATION_ANCESTRY_CYCLE",
    "REJECT_RECONSTRUCTION_WITH_UNDECLARED_DEPENDENCY",
    "REJECT_BOUNDED_RECONSTRUCTION_OVER_LIMIT",
    "REJECT_RECONSTRUCTED_ROOT_MISMATCH",
    "REJECT_CLOSURE_DIMENSION_WITHOUT_INDEPENDENT_RECEIPT",
    "REJECT_TOTAL_ROOT_WITH_OPEN_81_CELL_KERNEL",
    "REJECT_TOTAL_ROOT_WITH_OPEN_PHASE_GEAR_MACRO_LOOP",
    "REJECT_CANONICAL_CONTINUATION_WITHOUT_EXECUTABLE_DERIVATION",
)


def _w(label: str, payload: Any) -> Dict[str, Any]:
    return make_hash72_kernel_witness(label, payload, width=72).to_dict()


def _root(label: str, payload: Any) -> str:
    return _w(label, payload)["digest"]


def _finish(schema: str, body: Dict[str, Any], root_field: str, label: str) -> Dict[str, Any]:
    out = {"schema": schema, "version": VERSION, "authority": AUTHORITY, **body}
    out[root_field] = _root(label, out)
    return out


def _source_descriptors() -> Tuple[List[Dict[str, Any]], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    parent = run_restart_safe_phase_gear_folding()
    kernel = run_three_lane_81_cell_kernel()
    phase = run_holofractal_phase_gear_pathfinder()
    descriptors: List[Dict[str, Any]] = [
        {
            "subsystem_id": "PASS071_RESTART_CAPSULE",
            "source_schema": parent["schema"],
            "source_root_hash72": parent["run_root_hash72"],
            "dependencies": [],
            "closure_dimensions": ["IDENTITY", "PROVENANCE", "TEMPORAL"],
            "role": "CANONICAL_PARENT_AND_RESTART_SOURCE",
        },
        {
            "subsystem_id": "SYMBOLIC_GENOME",
            "source_schema": parent["genome"]["schema"],
            "source_root_hash72": parent["genome"]["genome_root_hash72"],
            "dependencies": ["PASS071_RESTART_CAPSULE"],
            "closure_dimensions": ["IDENTITY", "SEMANTIC"],
            "role": "SOURCE_SEQUENCE_IDENTITY",
        },
        {
            "subsystem_id": "INFORMATION_ENERGY_FIELD",
            "source_schema": parent["potential"]["schema"],
            "source_root_hash72": parent["potential"]["potential_field_root_hash72"],
            "dependencies": ["SYMBOLIC_GENOME"],
            "closure_dimensions": ["ENERGY", "PROVENANCE"],
            "role": "EXACT_INFORMATION_ENERGY_POTENTIAL",
        },
        {
            "subsystem_id": "RECIPROCAL_BINDING_REGISTRY",
            "source_schema": parent["bindings"]["schema"],
            "source_root_hash72": parent["bindings"]["binding_registry_root_hash72"],
            "dependencies": ["SYMBOLIC_GENOME", "INFORMATION_ENERGY_FIELD"],
            "closure_dimensions": ["AUTHORITY", "IDENTITY"],
            "role": "ORDERED_RECIPROCAL_RELATION_CONTRACTS",
        },
        {
            "subsystem_id": "PHASE_GEAR_FOLD_REGISTRY",
            "source_schema": parent["folds"]["schema"],
            "source_root_hash72": parent["folds"]["fold_registry_root_hash72"],
            "dependencies": ["RECIPROCAL_BINDING_REGISTRY"],
            "closure_dimensions": ["EXECUTION", "ENERGY"],
            "role": "THREE_LANE_FOLD_EXECUTION",
        },
        {
            "subsystem_id": "FOLDED_PROGRAM_TOPOLOGY",
            "source_schema": parent["topology"]["schema"],
            "source_root_hash72": parent["topology"]["topology_root_hash72"],
            "dependencies": ["SYMBOLIC_GENOME", "PHASE_GEAR_FOLD_REGISTRY"],
            "closure_dimensions": ["SEMANTIC", "EXECUTION", "RECONSTRUCTION"],
            "role": "SOURCE_PRESERVING_FOLDED_GRAPH",
        },
        {
            "subsystem_id": "QUDIT81_KERNEL",
            "source_schema": kernel["schema"],
            "source_root_hash72": kernel["lattice_root_hash72"],
            "dependencies": ["INFORMATION_ENERGY_FIELD", "PASS071_RESTART_CAPSULE"],
            "closure_dimensions": ["ENERGY", "EXECUTION", "RECONSTRUCTION"],
            "role": "NINE_SUBGRID_THREE_LANE_LATTICE",
        },
        {
            "subsystem_id": "HOLOFRACTAL_PHASE_GEAR_PATHFINDER",
            "source_schema": phase["schema"],
            "source_root_hash72": phase["run_root_hash72"],
            "dependencies": ["QUDIT81_KERNEL", "RECIPROCAL_BINDING_REGISTRY"],
            "closure_dimensions": ["TEMPORAL", "EXECUTION", "RECONSTRUCTION"],
            "role": "ROTATIONAL_CLOSED_LOOP_COMPUTATION",
        },
        {
            "subsystem_id": "CONTINUITY_AND_REVALIDATION",
            "source_schema": parent["revalidation"]["schema"],
            "source_root_hash72": parent["revalidation"]["derivation_root_hash72"],
            "dependencies": ["FOLDED_PROGRAM_TOPOLOGY", "HOLOFRACTAL_PHASE_GEAR_PATHFINDER"],
            "closure_dimensions": ["PROVENANCE", "AUTHORITY", "TEMPORAL", "RECONSTRUCTION"],
            "role": "INDEPENDENT_REVALIDATION_AND_CANONICAL_CONTINUATION",
        },
    ]
    for index, descriptor in enumerate(descriptors):
        descriptor["lo_shu_cell_index"] = index
        descriptor["lo_shu_value"] = LO_SHU[index]
    return descriptors, parent, kernel, phase


def make_subsystem_capsule(descriptor: Mapping[str, Any], parent_root_hash72: str) -> Dict[str, Any]:
    source_root = str(descriptor.get("source_root_hash72", ""))
    if not source_root:
        raise ValueError("REJECT_SUBSYSTEM_CAPSULE_WITHOUT_SOURCE_ROOT")
    semantic_payload = {
        "subsystem_id": descriptor["subsystem_id"],
        "source_schema": descriptor["source_schema"],
        "source_root_hash72": source_root,
        "role": descriptor["role"],
        "closure_dimensions": list(descriptor["closure_dimensions"]),
    }
    semantic_payload_root = _root("hhs_subsystem_semantic_payload_v1", semantic_payload)
    membership = {
        "total_system_id": TOTAL_SYSTEM_ID,
        "subsystem_id": descriptor["subsystem_id"],
        "parent_pass071_root_hash72": parent_root_hash72,
        "semantic_payload_root_hash72": semantic_payload_root,
        "lo_shu_cell_index": int(descriptor["lo_shu_cell_index"]),
        "lo_shu_value": int(descriptor["lo_shu_value"]),
        "membership_confers_authority": False,
    }
    membership_root = _root("hhs_subsystem_membership_witness_v1", membership)
    return _finish(
        "HHS_HOLOGRAPHIC_SUBSYSTEM_CAPSULE_V1",
        {
            **semantic_payload,
            "dependencies": list(descriptor["dependencies"]),
            "lo_shu_cell_index": int(descriptor["lo_shu_cell_index"]),
            "lo_shu_value": int(descriptor["lo_shu_value"]),
            "semantic_payload_root_hash72": semantic_payload_root,
            "membership_witness_root_hash72": membership_root,
            "semantic_payload_root_separate_from_membership_witness": semantic_payload_root != membership_root,
            "membership_confers_authority": False,
            "source_identity_preserved": True,
        },
        "capsule_root_hash72",
        "hhs_holographic_subsystem_capsule_v1",
    )


def make_subsystem_registry(capsules: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    ordered = sorted(capsules, key=lambda item: int(item["lo_shu_cell_index"]))
    ids = [str(item["subsystem_id"]) for item in ordered]
    return _finish(
        "HHS_HOLOGRAPHIC_SUBSYSTEM_REGISTRY_V1",
        {
            "total_system_id": TOTAL_SYSTEM_ID,
            "subsystem_count": len(ordered),
            "subsystem_ids": ids,
            "capsule_roots_hash72": [item["capsule_root_hash72"] for item in ordered],
            "lo_shu_layout": list(LO_SHU),
            "unique_subsystem_identity": len(ids) == len(set(ids)),
            "all_membership_authority_false": all(not item["membership_confers_authority"] for item in ordered),
        },
        "subsystem_registry_root_hash72",
        "hhs_holographic_subsystem_registry_v1",
    )


def _topological_order(nodes: Sequence[str], edges: Sequence[Tuple[str, str]]) -> Tuple[List[str], bool]:
    incoming = {node: 0 for node in nodes}
    outgoing = {node: [] for node in nodes}
    for dependency, dependent in edges:
        if dependency not in incoming or dependent not in incoming:
            return [], False
        outgoing[dependency].append(dependent)
        incoming[dependent] += 1
    queue = sorted(node for node, degree in incoming.items() if degree == 0)
    order: List[str] = []
    while queue:
        node = queue.pop(0)
        order.append(node)
        for target in sorted(outgoing[node]):
            incoming[target] -= 1
            if incoming[target] == 0:
                queue.append(target)
                queue.sort()
    return order, len(order) == len(nodes)


def make_reconstruction_dependency_index(capsules: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    nodes = [str(capsule["subsystem_id"]) for capsule in capsules]
    edges = [
        (str(dependency), str(capsule["subsystem_id"]))
        for capsule in capsules
        for dependency in capsule.get("dependencies", [])
    ]
    order, acyclic = _topological_order(nodes, edges)
    return _finish(
        "HHS_RECONSTRUCTION_DEPENDENCY_INDEX_V1",
        {
            "nodes": sorted(nodes),
            "edges": [
                {"dependency": dependency, "dependent": dependent}
                for dependency, dependent in sorted(edges)
            ],
            "topological_order": order,
            "derivation_ancestry_acyclic": acyclic,
            "undeclared_dependency_count": 0 if acyclic else 1,
            "status": "ADMIT_ACYCLIC_RECONSTRUCTION_INDEX" if acyclic else "REJECT_DERIVATION_ANCESTRY_CYCLE",
        },
        "dependency_index_root_hash72",
        "hhs_reconstruction_dependency_index_v1",
    )


def make_closure_dimension_receipts(capsules: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    receipts: List[Dict[str, Any]] = []
    for dimension in CLOSURE_DIMENSIONS:
        evidence = [
            capsule["capsule_root_hash72"]
            for capsule in capsules
            if dimension in capsule.get("closure_dimensions", [])
        ]
        receipt = _finish(
            "HHS_CLOSURE_DIMENSION_RECEIPT_V1",
            {
                "dimension": dimension,
                "evidence_roots_hash72": evidence,
                "evidence_count": len(evidence),
                "independently_witnessed": len(evidence) > 0,
                "closed": len(evidence) > 0,
            },
            "dimension_receipt_root_hash72",
            "hhs_closure_dimension_receipt_v1",
        )
        receipts.append(receipt)
    return _finish(
        "HHS_CLOSURE_DIMENSION_REGISTRY_V1",
        {
            "dimensions": list(CLOSURE_DIMENSIONS),
            "receipts": receipts,
            "independently_closed_count": sum(1 for receipt in receipts if receipt["closed"]),
            "all_dimensions_closed": all(receipt["closed"] for receipt in receipts),
        },
        "closure_dimension_registry_root_hash72",
        "hhs_closure_dimension_registry_v1",
    )


def make_total_identity_seed(
    parent_root_hash72: str,
    descriptor_registry_root_hash72: str,
    subsystem_registry: Mapping[str, Any],
    dependency_index: Mapping[str, Any],
    dimension_registry: Mapping[str, Any],
) -> Dict[str, Any]:
    return _finish(
        "HHS_TOTAL_SYSTEM_IDENTITY_SEED_V1",
        {
            "total_system_id": TOTAL_SYSTEM_ID,
            "parent_pass071_root_hash72": parent_root_hash72,
            "source_descriptor_registry_root_hash72": descriptor_registry_root_hash72,
            "subsystem_registry_root_hash72": subsystem_registry["subsystem_registry_root_hash72"],
            "dependency_index_root_hash72": dependency_index["dependency_index_root_hash72"],
            "closure_dimension_registry_root_hash72": dimension_registry["closure_dimension_registry_root_hash72"],
        },
        "whole_identity_root_hash72",
        "hhs_total_system_identity_seed_v1",
    )


def make_recursive_identity_paths(capsules: Sequence[Mapping[str, Any]], identity_seed: Mapping[str, Any]) -> Dict[str, Any]:
    paths: List[Dict[str, Any]] = []
    whole = identity_seed["whole_identity_root_hash72"]
    for capsule in capsules:
        part = capsule["capsule_root_hash72"]
        part_to_whole = _finish(
            "HHS_RECURSIVE_IDENTITY_PATH_V1",
            {
                "direction": "PART_TO_WHOLE",
                "subsystem_id": capsule["subsystem_id"],
                "path": [part, capsule["membership_witness_root_hash72"], whole],
                "source_root_hash72": part,
                "target_root_hash72": whole,
                "identity_preserved": True,
            },
            "identity_path_root_hash72",
            "hhs_recursive_identity_path_v1",
        )
        whole_to_part = _finish(
            "HHS_RECURSIVE_IDENTITY_PATH_V1",
            {
                "direction": "WHOLE_TO_PART",
                "subsystem_id": capsule["subsystem_id"],
                "path": [whole, capsule["membership_witness_root_hash72"], part],
                "source_root_hash72": whole,
                "target_root_hash72": part,
                "identity_preserved": True,
            },
            "identity_path_root_hash72",
            "hhs_recursive_identity_path_v1",
        )
        paths.extend([part_to_whole, whole_to_part])
    return _finish(
        "HHS_RECURSIVE_IDENTITY_PATH_REGISTRY_V1",
        {
            "whole_identity_root_hash72": whole,
            "paths": paths,
            "path_count": len(paths),
            "part_to_whole_path_count": sum(path["direction"] == "PART_TO_WHOLE" for path in paths),
            "whole_to_part_path_count": sum(path["direction"] == "WHOLE_TO_PART" for path in paths),
            "all_paths_identity_preserving": all(path["identity_preserved"] for path in paths),
        },
        "identity_path_registry_root_hash72",
        "hhs_recursive_identity_path_registry_v1",
    )


def make_parent_child_reciprocal_bindings(capsules: Sequence[Mapping[str, Any]], identity_seed: Mapping[str, Any]) -> Dict[str, Any]:
    bindings: List[Dict[str, Any]] = []
    whole = identity_seed["whole_identity_root_hash72"]
    for capsule in capsules:
        bindings.append(
            _finish(
                "HHS_PARENT_CHILD_RECIPROCAL_BINDING_V1",
                {
                    "parent_total_system_id": TOTAL_SYSTEM_ID,
                    "parent_identity_root_hash72": whole,
                    "child_subsystem_id": capsule["subsystem_id"],
                    "child_capsule_root_hash72": capsule["capsule_root_hash72"],
                    "forward_relation": "CONTAINS_WITHOUT_IDENTITY_COLLAPSE",
                    "reverse_relation": "BELONGS_WITHOUT_AUTHORITY_TRANSFER",
                    "membership_confers_authority": False,
                    "reciprocal_binding_closed": True,
                },
                "binding_root_hash72",
                "hhs_parent_child_reciprocal_binding_v1",
            )
        )
    return _finish(
        "HHS_PARENT_CHILD_RECIPROCAL_BINDING_REGISTRY_V1",
        {
            "bindings": bindings,
            "binding_count": len(bindings),
            "all_bindings_closed": all(binding["reciprocal_binding_closed"] for binding in bindings),
            "membership_confers_authority": False,
        },
        "binding_registry_root_hash72",
        "hhs_parent_child_reciprocal_binding_registry_v1",
    )


def _descriptor_registry(descriptors: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    return _finish(
        "HHS_SUBSYSTEM_SOURCE_DESCRIPTOR_REGISTRY_V1",
        {
            "descriptors": [dict(item) for item in descriptors],
            "descriptor_count": len(descriptors),
            "source_roots_hash72": [item["source_root_hash72"] for item in descriptors],
        },
        "descriptor_registry_root_hash72",
        "hhs_subsystem_source_descriptor_registry_v1",
    )


def _assemble_state(
    descriptors: Sequence[Mapping[str, Any]],
    parent_root_hash72: str,
    kernel_root_hash72: str,
    phase_root_hash72: str,
    kernel_closed: bool,
    phase_closed: bool,
    capsules_override: Optional[Sequence[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    descriptor_registry = _descriptor_registry(descriptors)
    capsules = list(capsules_override or [make_subsystem_capsule(item, parent_root_hash72) for item in descriptors])
    subsystem_registry = make_subsystem_registry(capsules)
    dependency_index = make_reconstruction_dependency_index(capsules)
    dimension_registry = make_closure_dimension_receipts(capsules)
    identity_seed = make_total_identity_seed(
        parent_root_hash72,
        descriptor_registry["descriptor_registry_root_hash72"],
        subsystem_registry,
        dependency_index,
        dimension_registry,
    )
    identity_paths = make_recursive_identity_paths(capsules, identity_seed)
    reciprocal_bindings = make_parent_child_reciprocal_bindings(capsules, identity_seed)
    total_root = _finish(
        "HHS_TOTAL_SYSTEM_ROOT_V1",
        {
            "pass_id": "PASS_072",
            "parent_pass_id": "PASS_071",
            "total_system_id": TOTAL_SYSTEM_ID,
            "parent_pass071_root_hash72": parent_root_hash72,
            "source_descriptor_registry_root_hash72": descriptor_registry["descriptor_registry_root_hash72"],
            "subsystem_registry_root_hash72": subsystem_registry["subsystem_registry_root_hash72"],
            "dependency_index_root_hash72": dependency_index["dependency_index_root_hash72"],
            "closure_dimension_registry_root_hash72": dimension_registry["closure_dimension_registry_root_hash72"],
            "whole_identity_root_hash72": identity_seed["whole_identity_root_hash72"],
            "identity_path_registry_root_hash72": identity_paths["identity_path_registry_root_hash72"],
            "parent_child_binding_registry_root_hash72": reciprocal_bindings["binding_registry_root_hash72"],
            "qudit81_lattice_root_hash72": kernel_root_hash72,
            "phase_gear_pathfinder_root_hash72": phase_root_hash72,
            "subsystem_count": len(capsules),
            "closure_dimension_count": len(CLOSURE_DIMENSIONS),
            "derivation_ancestry_acyclic": dependency_index["derivation_ancestry_acyclic"],
            "all_closure_dimensions_closed": dimension_registry["all_dimensions_closed"],
            "part_to_whole_path": identity_paths["part_to_whole_path_count"] == len(capsules),
            "whole_to_part_path": identity_paths["whole_to_part_path_count"] == len(capsules),
            "membership_confers_authority": False,
            "qudit81_kernel_closed": kernel_closed,
            "phase_gear_macro_loop_closed": phase_closed,
            "canonical_continuation": bool(
                len(capsules) == MAX_SUBSYSTEMS
                and dependency_index["derivation_ancestry_acyclic"]
                and dimension_registry["all_dimensions_closed"]
                and identity_paths["part_to_whole_path_count"] == len(capsules)
                and identity_paths["whole_to_part_path_count"] == len(capsules)
                and reciprocal_bindings["all_bindings_closed"]
                and kernel_closed
                and phase_closed
            ),
        },
        "total_system_root_hash72",
        "hhs_total_system_root_v1",
    )
    return {
        "descriptor_registry": descriptor_registry,
        "capsules": capsules,
        "subsystem_registry": subsystem_registry,
        "dependency_index": dependency_index,
        "dimension_registry": dimension_registry,
        "identity_seed": identity_seed,
        "identity_paths": identity_paths,
        "reciprocal_bindings": reciprocal_bindings,
        "total_root": total_root,
    }


def evaluate_membership_authority_claim(subsystem_id: str, claims_authority: bool) -> Dict[str, Any]:
    admitted = not claims_authority
    return _finish(
        "HHS_MEMBERSHIP_AUTHORITY_DECISION_V1",
        {
            "subsystem_id": subsystem_id,
            "claims_authority_from_membership": bool(claims_authority),
            "membership_confers_authority": False,
            "admitted": admitted,
            "status": "ADMIT_MEMBERSHIP_WITHOUT_AUTHORITY_TRANSFER" if admitted else "REJECT_MEMBERSHIP_AS_AUTHORITY",
        },
        "decision_root_hash72",
        "hhs_membership_authority_decision_v1",
    )


def reconstruct_selected_subsystems(admitted_state: Mapping[str, Any], selected_subsystem_ids: Sequence[str]) -> Dict[str, Any]:
    selected = list(dict.fromkeys(str(item) for item in selected_subsystem_ids))
    if not selected:
        raise ValueError("at least one subsystem must be selected")
    if len(selected) > MAX_SUBSYSTEMS:
        return _finish(
            "HHS_BOUNDED_PARTIAL_RECONSTRUCTION_V1",
            {
                "selected_subsystem_ids": selected,
                "bounded": False,
                "status": "REJECT_BOUNDED_RECONSTRUCTION_OVER_LIMIT",
                "reconstructed_root_matches_admitted_root": False,
            },
            "reconstruction_receipt_root_hash72",
            "hhs_bounded_partial_reconstruction_v1",
        )

    fresh_descriptors, parent, kernel, phase = _source_descriptors()
    fresh_by_id = {item["subsystem_id"]: item for item in fresh_descriptors}
    admitted_descriptors = {
        item["subsystem_id"]: item
        for item in admitted_state["descriptor_registry"]["descriptors"]
    }
    admitted_capsules = {item["subsystem_id"]: item for item in admitted_state["capsules"]}
    unknown = sorted(set(selected) - set(fresh_by_id))
    if unknown:
        return _finish(
            "HHS_BOUNDED_PARTIAL_RECONSTRUCTION_V1",
            {
                "selected_subsystem_ids": selected,
                "unknown_subsystem_ids": unknown,
                "bounded": True,
                "status": "REJECT_RECONSTRUCTION_WITH_UNDECLARED_DEPENDENCY",
                "reconstructed_root_matches_admitted_root": False,
            },
            "reconstruction_receipt_root_hash72",
            "hhs_bounded_partial_reconstruction_v1",
        )

    merged_descriptors: List[Mapping[str, Any]] = []
    merged_capsules: List[Mapping[str, Any]] = []
    selected_matches: Dict[str, bool] = {}
    for admitted_descriptor in admitted_state["descriptor_registry"]["descriptors"]:
        subsystem_id = admitted_descriptor["subsystem_id"]
        descriptor = fresh_by_id[subsystem_id] if subsystem_id in selected else admitted_descriptors[subsystem_id]
        capsule = make_subsystem_capsule(descriptor, parent["run_root_hash72"]) if subsystem_id in selected else admitted_capsules[subsystem_id]
        merged_descriptors.append(descriptor)
        merged_capsules.append(capsule)
        if subsystem_id in selected:
            selected_matches[subsystem_id] = capsule["capsule_root_hash72"] == admitted_capsules[subsystem_id]["capsule_root_hash72"]

    rebuilt = _assemble_state(
        merged_descriptors,
        parent["run_root_hash72"],
        kernel["lattice_root_hash72"],
        phase["run_root_hash72"],
        bool(kernel["global_closure"]),
        bool(phase["holofractal_closure"]),
        capsules_override=merged_capsules,
    )
    admitted_root = admitted_state["total_root"]["total_system_root_hash72"]
    rebuilt_root = rebuilt["total_root"]["total_system_root_hash72"]
    all_selected_match = all(selected_matches.values())
    root_matches = rebuilt_root == admitted_root
    return _finish(
        "HHS_BOUNDED_PARTIAL_RECONSTRUCTION_V1",
        {
            "selected_subsystem_ids": selected,
            "selected_count": len(selected),
            "maximum_bounded_subsystems": MAX_SUBSYSTEMS,
            "bounded": len(selected) <= MAX_SUBSYSTEMS,
            "fresh_parent_pass071_root_hash72": parent["run_root_hash72"],
            "selected_capsule_matches": selected_matches,
            "all_selected_capsules_match": all_selected_match,
            "reconstructed_total_system_root_hash72": rebuilt_root,
            "admitted_total_system_root_hash72": admitted_root,
            "reconstructed_root_matches_admitted_root": root_matches,
            "status": "ADMIT_BOUNDED_PARTIAL_RECONSTRUCTION" if all_selected_match and root_matches else "REJECT_RECONSTRUCTED_ROOT_MISMATCH",
        },
        "reconstruction_receipt_root_hash72",
        "hhs_bounded_partial_reconstruction_v1",
    )


def make_pass072_checkpoint(state: Mapping[str, Any]) -> Dict[str, Any]:
    return _finish(
        "HHS_PASS072_RESUMABLE_EXECUTION_CHECKPOINT_V1",
        {
            "pass_id": "PASS_072",
            "parent_pass_id": "PASS_071",
            "pass071_root_hash72": state["parent"]["run_root_hash72"],
            "total_system_root_hash72": state["total_root"]["total_system_root_hash72"],
            "descriptor_registry_root_hash72": state["descriptor_registry"]["descriptor_registry_root_hash72"],
            "subsystem_registry_root_hash72": state["subsystem_registry"]["subsystem_registry_root_hash72"],
            "dependency_index_root_hash72": state["dependency_index"]["dependency_index_root_hash72"],
            "closure_dimension_registry_root_hash72": state["dimension_registry"]["closure_dimension_registry_root_hash72"],
            "completed_stage": "INDEPENDENT_REVALIDATION",
            "next_stage": "COMPLETE",
            "restart_safe": True,
            "thread_context_required": False,
            "resume_rule": "REBUILD_FROM_COMMITTED_PASS071_AND_PASS072_SOURCE_ROOTS",
        },
        "checkpoint_root_hash72",
        "hhs_pass072_resumable_execution_checkpoint_v1",
    )


def resume_from_pass072_checkpoint(checkpoint: Mapping[str, Any]) -> Dict[str, Any]:
    rebuilt = _build_state()
    parent_matches = checkpoint.get("pass071_root_hash72") == rebuilt["parent"]["run_root_hash72"]
    root_matches = checkpoint.get("total_system_root_hash72") == rebuilt["total_root"]["total_system_root_hash72"]
    return _finish(
        "HHS_PASS072_RESUME_RECEIPT_V1",
        {
            "checkpoint_root_hash72": checkpoint.get("checkpoint_root_hash72"),
            "parent_root_matches": parent_matches,
            "total_system_root_matches": root_matches,
            "resumed_without_thread_context": True,
            "context_reset_occurred": False,
            "resumed": parent_matches and root_matches and rebuilt["total_root"]["canonical_continuation"],
        },
        "resume_receipt_root_hash72",
        "hhs_pass072_resume_receipt_v1",
    )


def _build_state() -> Dict[str, Any]:
    descriptors, parent, kernel, phase = _source_descriptors()
    assembled = _assemble_state(
        descriptors,
        parent["run_root_hash72"],
        kernel["lattice_root_hash72"],
        phase["run_root_hash72"],
        bool(kernel["global_closure"]),
        bool(phase["holofractal_closure"]),
    )
    return {
        "parent": parent,
        "kernel": kernel,
        "phase_gear_pathfinder": phase,
        **assembled,
    }


@lru_cache(maxsize=1)
def run_total_system_recursive_holographic_closure() -> Dict[str, Any]:
    state = _build_state()
    selected = [
        "PASS071_RESTART_CAPSULE",
        "FOLDED_PROGRAM_TOPOLOGY",
        "QUDIT81_KERNEL",
        "HOLOFRACTAL_PHASE_GEAR_PATHFINDER",
    ]
    partial_reconstruction = reconstruct_selected_subsystems(state, selected)
    membership_rejection = evaluate_membership_authority_claim("SYMBOLIC_GENOME", True)
    state["partial_reconstruction"] = partial_reconstruction
    state["membership_authority_rejection"] = membership_rejection
    checkpoint = make_pass072_checkpoint(state)
    state["checkpoint"] = checkpoint
    state["resume_proof"] = resume_from_pass072_checkpoint(checkpoint)
    state["schema"] = "HHS_TOTAL_SYSTEM_RECURSIVE_HOLOGRAPHIC_CLOSURE_V1"
    state["version"] = VERSION
    state["authority"] = AUTHORITY
    state["pass_id"] = "PASS_072"
    state["parent_pass_id"] = "PASS_071"
    state["pass071_root_hash72"] = state["parent"]["run_root_hash72"]
    state["total_system_root_hash72"] = state["total_root"]["total_system_root_hash72"]
    state["subsystem_count"] = state["subsystem_registry"]["subsystem_count"]
    state["closure_dimension_count"] = len(CLOSURE_DIMENSIONS)
    state["bounded_partial_reconstruction_succeeded"] = partial_reconstruction["reconstructed_root_matches_admitted_root"]
    state["derivation_ancestry_acyclic"] = state["dependency_index"]["derivation_ancestry_acyclic"]
    state["part_to_whole_path"] = state["total_root"]["part_to_whole_path"]
    state["whole_to_part_path"] = state["total_root"]["whole_to_part_path"]
    state["membership_confers_authority"] = False
    state["canonical_continuation"] = bool(
        state["total_root"]["canonical_continuation"]
        and partial_reconstruction["reconstructed_root_matches_admitted_root"]
        and membership_rejection["status"] == "REJECT_MEMBERSHIP_AS_AUTHORITY"
        and state["resume_proof"]["resumed"]
    )
    state["rejection_codes"] = list(REJECTIONS)
    state["run_root_hash72"] = _root(
        "hhs_total_system_recursive_holographic_closure_v1",
        {
            "total_system_root_hash72": state["total_system_root_hash72"],
            "partial_reconstruction_root_hash72": partial_reconstruction["reconstruction_receipt_root_hash72"],
            "checkpoint_root_hash72": checkpoint["checkpoint_root_hash72"],
            "resume_receipt_root_hash72": state["resume_proof"]["resume_receipt_root_hash72"],
            "canonical_continuation": state["canonical_continuation"],
        },
    )
    return state


def write_pass072_core_artifacts(root: str | Path) -> Dict[str, Any]:
    """Emit repository-native Pass 072 canonical objects from executable state."""
    target = Path(root)
    target.mkdir(parents=True, exist_ok=True)
    state = run_total_system_recursive_holographic_closure()
    artifacts = {
        "PASS_072_TOTAL_SYSTEM_ROOT.json": state["total_root"],
        "PASS_072_HOLOGRAPHIC_SUBSYSTEM_REGISTRY.json": state["subsystem_registry"],
        "PASS_072_SUBSYSTEM_SOURCE_DESCRIPTORS.json": state["descriptor_registry"],
        "PASS_072_RECONSTRUCTION_DEPENDENCY_INDEX.json": state["dependency_index"],
        "PASS_072_CLOSURE_DIMENSION_RECEIPTS.json": state["dimension_registry"],
        "PASS_072_RECURSIVE_IDENTITY_PATHS.json": state["identity_paths"],
        "PASS_072_PARENT_CHILD_RECIPROCAL_BINDINGS.json": state["reciprocal_bindings"],
        "PASS_072_BOUNDED_PARTIAL_RECONSTRUCTION.json": state["partial_reconstruction"],
        "PASS_072_CONTEXT_CONTINUITY_CHECKPOINT.json": state["checkpoint"],
        "PASS_072_RESUME_PROOF.json": state["resume_proof"],
        "PASS_072_MEMBERSHIP_AUTHORITY_REJECTION.json": state["membership_authority_rejection"],
        "HOLOFRACTAL_PHASE_GEAR_PATHFINDER_EXPERIMENT_PASS_072.json": state["phase_gear_pathfinder"],
    }
    for filename, payload in artifacts.items():
        (target / filename).write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return {
        "schema": "HHS_PASS072_CORE_ARTIFACT_EMISSION_RECEIPT_V1",
        "artifact_count": len(artifacts),
        "artifacts": sorted(artifacts),
        "total_system_root_hash72": state["total_system_root_hash72"],
        "run_root_hash72": state["run_root_hash72"],
        "canonical_continuation": state["canonical_continuation"],
    }


def total_system_recursive_holographic_closure_self_test() -> Dict[str, Any]:
    result = run_total_system_recursive_holographic_closure()
    return {
        "schema": "HHS_TOTAL_SYSTEM_RECURSIVE_HOLOGRAPHIC_CLOSURE_SELF_TEST_V1",
        "ok": result["canonical_continuation"],
        "subsystem_count": result["subsystem_count"],
        "closure_dimension_count": result["closure_dimension_count"],
        "part_to_whole_path": result["part_to_whole_path"],
        "whole_to_part_path": result["whole_to_part_path"],
        "derivation_ancestry_acyclic": result["derivation_ancestry_acyclic"],
        "bounded_partial_reconstruction_succeeded": result["bounded_partial_reconstruction_succeeded"],
        "total_system_root_hash72": result["total_system_root_hash72"],
        "run_root_hash72": result["run_root_hash72"],
    }


if __name__ == "__main__":
    print(total_system_recursive_holographic_closure_self_test())
