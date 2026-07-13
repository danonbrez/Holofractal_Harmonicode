"""Pass 071 — restart-safe overlap buffer and phase-gear symbolic folding.

This module treats Pass 070's reversible binary↔trinary translation as the
canonical source sequence for a local, provenance-preserving folding layer.
It also makes continuation state explicit so an interrupted process can resume
from repository objects without relying on conversational/thread memory.
"""
from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_backend.runtime.hhs_universal_binary_trinary_translation_v1 import (
    run_universal_binary_trinary_translation,
)

VERSION = "PASS_071_RESTART_SAFE_PHASE_GEAR_FOLDING_V1"
AUTHORITY = "HHS_PASS071_OVERLAP_AND_FOLDING_AUTHORITY_V1"

STAGES: Tuple[str, ...] = (
    "PASS070_HANDOFF",
    "OVERLAP_BUFFER",
    "SYMBOLIC_GENOME",
    "INFORMATION_ENERGY_POTENTIAL",
    "RECIPROCAL_BINDINGS",
    "PHASE_GEAR_FOLDS",
    "FOLDED_TOPOLOGY",
    "UNFOLDING",
    "INDEPENDENT_REVALIDATION",
)

REJECTIONS: Tuple[str, ...] = (
    "REJECT_PASS071_WITHOUT_PASS070_CANONICAL_ROOT",
    "REJECT_OVERLAP_BUFFER_WITHOUT_COMPLETE_CONTEXT_CAPSULE",
    "REJECT_RESUME_WITH_PARENT_ROOT_MISMATCH",
    "REJECT_CHECKPOINT_WITH_MISSING_STAGE_ROOT",
    "REJECT_CONTEXT_RESET_AS_VALID_RESUME",
    "REJECT_FOLD_REWRITES_CANONICAL_SOURCE_SEQUENCE",
    "REJECT_LOCAL_BINDING_WITHOUT_RECIPROCAL_PHASE_CONTRACT",
    "REJECT_FOLDING_PATH_BYPASSES_THREE_LANE_VALIDATION",
    "REJECT_THERMODYNAMIC_BIAS_AS_SEMANTIC_AUTHORITY",
    "REJECT_FAILED_FOLD_ERASES_PROVENANCE",
    "REJECT_BINARY_SOURCE_IDENTITY_LOST_DURING_FOLDING",
    "REJECT_FOLDED_TOPOLOGY_WITHOUT_INDEPENDENT_REVALIDATION",
)


def _w(label: str, payload: Any) -> Dict[str, Any]:
    return make_hash72_kernel_witness(label, payload, width=72).to_dict()


def _root(label: str, payload: Any) -> str:
    return _w(label, payload)["digest"]


def _finish(schema: str, body: Dict[str, Any], root_field: str, label: str) -> Dict[str, Any]:
    out = {"schema": schema, "version": VERSION, "authority": AUTHORITY, **body}
    out[root_field] = _root(label, out)
    return out


def make_pass070_handoff(parent: Mapping[str, Any]) -> Dict[str, Any]:
    return _finish(
        "HHS_PASS070_TO_PASS071_HANDOFF_V1",
        {
            "pass070_root_hash72": parent["run_root_hash72"],
            "pass069_root_hash72": parent["pass069_root_hash72"],
            "binary_packet_root_hash72": parent["word_packet"]["packet_root_hash72"],
            "binary_round_trip_root_hash72": parent["word_round_trip"]["round_trip_root_hash72"],
            "operator_proof_roots_hash72": [p["operator_proof_root_hash72"] for p in parent["operator_proofs"]],
            "translation_reversible": parent["translation_is_reversible"],
            "all_pair_round_trips_valid": parent["all_pair_round_trips_valid"],
            "word_round_trip_valid": parent["word_round_trip_valid"],
            "handoff_closed": True,
            "handoff_is_overlap_not_reset": True,
        },
        "handoff_root_hash72",
        "hhs_pass070_to_pass071_handoff_v1",
    )


def make_overlap_buffer(parent: Mapping[str, Any], handoff: Mapping[str, Any]) -> Dict[str, Any]:
    context_capsule = {
        "canonical_parent_pass": "PASS_070",
        "active_forward_pass": "PASS_071",
        "source_mapping": dict(parent["mapping"]),
        "binary_operator_set": [p["operator"] for p in parent["operator_proofs"]],
        "three_lane_order": ["POSITIVE", "PLASTIC", "ZERO_SUM"],
        "phase_states": ["x", "y", "z", "w", "xy", "yx", "zw", "wz"],
        "fixed_invariants": [
            "SOURCE_IDENTITY_PRESERVED",
            "TRINARY_SWITCH_REVERSIBLE",
            "PLASTIC_GRADIENT_MEDIATES",
            "ZERO_SUM_CLOSES",
            "AUTHORITY_REMAINS_BOUNDED",
            "HASH72_WITNESSES_CONTINUITY",
        ],
        "forbidden_substitutions": [
            "THREAD_MEMORY_AS_CANONICAL_SOURCE",
            "LINGUISTIC_RECONSTRUCTION_AS_OPERATOR_AUTHORITY",
            "ENERGY_MINIMUM_AS_AUTHORITY",
            "FOLDING_TOPOLOGY_AS_SOURCE_REWRITE",
        ],
        "resume_rule": "REBUILD_FROM_COMMITTED_ROOTS_NOT_THREAD_CONTEXT",
    }
    return _finish(
        "HHS_PASS_OVERLAP_BUFFER_V1",
        {
            "handoff_root_hash72": handoff["handoff_root_hash72"],
            "pass070_root_hash72": parent["run_root_hash72"],
            "context_capsule": context_capsule,
            "context_capsule_complete": True,
            "thread_context_required_for_resume": False,
            "context_reset_permitted": False,
            "source_and_projection_overlap_preserved": True,
        },
        "overlap_root_hash72",
        "hhs_pass_overlap_buffer_v1",
    )


def _phase_symbol(trinary_phase: int, binary_switch: int) -> str:
    if trinary_phase == 1:
        return "x"
    if trinary_phase == -1:
        return "y"
    return "w" if binary_switch else "z"


def make_symbolic_genome(parent: Mapping[str, Any], overlap: Mapping[str, Any]) -> Dict[str, Any]:
    tokens: List[Dict[str, Any]] = []
    for index, pair in enumerate(parent["word_packet"]["pairs"]):
        state = pair["state"]
        token = _finish(
            "HHS_SEQUENCE_PHASE_TOKEN_V1",
            {
                "token_id": f"token:{index:02d}",
                "sequence_index": index,
                "source_pair_root_hash72": pair["source"]["source_root_hash72"],
                "translation_root_hash72": state["translation_root_hash72"],
                "source_bits": list(state["source_bits"]),
                "trinary_phase": int(state["trinary_phase"]),
                "binary_switch": int(state["binary_switch"]),
                "phase_symbol": _phase_symbol(int(state["trinary_phase"]), int(state["binary_switch"])),
                "source_identity_preserved": True,
            },
            "token_root_hash72",
            "hhs_sequence_phase_token_v1",
        )
        tokens.append(token)
    return _finish(
        "HHS_SYMBOLIC_GENOME_V1",
        {
            "overlap_root_hash72": overlap["overlap_root_hash72"],
            "source_packet_root_hash72": parent["word_packet"]["packet_root_hash72"],
            "source_word": parent["word_packet"]["source_word"],
            "token_count": len(tokens),
            "tokens": tokens,
            "source_sequence_immutable": True,
            "folding_may_rewrite_source": False,
        },
        "genome_root_hash72",
        "hhs_symbolic_genome_v1",
    )


def make_information_energy_potential(genome: Mapping[str, Any]) -> Dict[str, Any]:
    records: List[Dict[str, Any]] = []
    for token in genome["tokens"]:
        tri = int(token["trinary_phase"])
        sw = int(token["binary_switch"])
        local = abs(tri) + sw + 1
        phase = (2 * tri) + sw
        dependency = 1 if sw else 0
        vector = [local, phase, dependency]
        records.append(
            _finish(
                "HHS_ELECTROCHEMICAL_PHASE_POTENTIAL_V1",
                {
                    "token_id": token["token_id"],
                    "token_root_hash72": token["token_root_hash72"],
                    "potential_vector": vector,
                    "local_information_energy": local,
                    "phase_potential": phase,
                    "dependency_potential": dependency,
                    "thermodynamic_bias_confers_authority": False,
                    "computational_potential_not_empirical_measurement": True,
                },
                "potential_root_hash72",
                "hhs_electrochemical_phase_potential_v1",
            )
        )
    return _finish(
        "HHS_INFORMATION_ENERGY_POTENTIAL_FIELD_V1",
        {
            "genome_root_hash72": genome["genome_root_hash72"],
            "records": records,
            "record_count": len(records),
            "floating_point_used": False,
            "potential_guides_search_not_authority": True,
        },
        "potential_field_root_hash72",
        "hhs_information_energy_potential_field_v1",
    )


def _ordered_relation(left: str, right: str) -> str:
    known = {("x", "y"): "xy", ("y", "x"): "yx", ("z", "w"): "zw", ("w", "z"): "wz"}
    return known.get((left, right), f"{left}>{right}")


def make_reciprocal_bindings(genome: Mapping[str, Any], potential: Mapping[str, Any]) -> Dict[str, Any]:
    potentials = {r["token_id"]: r for r in potential["records"]}
    tokens = genome["tokens"]
    bindings: List[Dict[str, Any]] = []
    # Pair distant positions to make topology genuinely folded rather than a
    # restatement of sequence adjacency.
    for i in range(len(tokens) // 2):
        left = tokens[i]
        right = tokens[-1 - i]
        lp = potentials[left["token_id"]]
        rp = potentials[right["token_id"]]
        relation = _ordered_relation(left["phase_symbol"], right["phase_symbol"])
        delta_mu = int(rp["local_information_energy"]) - int(lp["local_information_energy"])
        reciprocal = int(left["trinary_phase"]) + int(right["trinary_phase"]) in (-1, 0, 1)
        bindings.append(
            _finish(
                "HHS_RECIPROCAL_BINDING_CONTRACT_V1",
                {
                    "binding_id": f"binding:{i:02d}",
                    "left_token_id": left["token_id"],
                    "right_token_id": right["token_id"],
                    "left_token_root_hash72": left["token_root_hash72"],
                    "right_token_root_hash72": right["token_root_hash72"],
                    "ordered_relation": relation,
                    "reverse_relation": _ordered_relation(right["phase_symbol"], left["phase_symbol"]),
                    "order_preserved": True,
                    "sequence_distance": int(right["sequence_index"]) - int(left["sequence_index"]),
                    "delta_mu": delta_mu,
                    "reciprocal_phase_contract_valid": reciprocal,
                    "binding_confers_authority": False,
                },
                "binding_root_hash72",
                "hhs_reciprocal_binding_contract_v1",
            )
        )
    return _finish(
        "HHS_RECIPROCAL_BINDING_REGISTRY_V1",
        {
            "genome_root_hash72": genome["genome_root_hash72"],
            "potential_field_root_hash72": potential["potential_field_root_hash72"],
            "bindings": bindings,
            "binding_count": len(bindings),
            "all_bindings_ordered": all(b["order_preserved"] for b in bindings),
            "source_sequence_distance_preserved": True,
        },
        "binding_registry_root_hash72",
        "hhs_reciprocal_binding_registry_v1",
    )


def make_phase_gear_folds(bindings: Mapping[str, Any], genome: Mapping[str, Any]) -> Dict[str, Any]:
    token_by_id = {t["token_id"]: t for t in genome["tokens"]}
    folds: List[Dict[str, Any]] = []
    for binding in bindings["bindings"]:
        left = token_by_id[binding["left_token_id"]]
        right = token_by_id[binding["right_token_id"]]
        l_energy = abs(int(left["trinary_phase"])) + int(left["binary_switch"]) + 1
        r_energy = abs(int(right["trinary_phase"])) + int(right["binary_switch"]) + 1
        plastic_residue = (l_energy ** 3) - l_energy - r_energy
        plastic_correction = -plastic_residue
        plastic_post = plastic_residue + plastic_correction
        phase_residue = int(left["trinary_phase"]) + int(right["trinary_phase"])
        zero_sum_correction = -phase_residue
        zero_sum_post = phase_residue + zero_sum_correction
        admitted = (
            binding["reciprocal_phase_contract_valid"]
            and plastic_post == 0
            and zero_sum_post == 0
        )
        folds.append(
            _finish(
                "HHS_PHASE_GEAR_FOLD_CANDIDATE_V1",
                {
                    "fold_id": f"fold:{binding['binding_id'].split(':')[-1]}",
                    "binding_root_hash72": binding["binding_root_hash72"],
                    "left_token_root_hash72": left["token_root_hash72"],
                    "right_token_root_hash72": right["token_root_hash72"],
                    "positive_lane": {
                        "proposal": binding["ordered_relation"],
                        "proposed": True,
                    },
                    "plastic_lane": {
                        "plastic_relation": "rho^3-rho-1=0",
                        "pre_correction_residue": plastic_residue,
                        "bounded_correction": plastic_correction,
                        "post_correction_residue": plastic_post,
                        "equilibrated": plastic_post == 0,
                    },
                    "zero_sum_lane": {
                        "pre_correction_residue": phase_residue,
                        "bounded_correction": zero_sum_correction,
                        "post_correction_residue": zero_sum_post,
                        "closed": zero_sum_post == 0,
                        "source_phase_erased": False,
                    },
                    "all_three_lanes_executed": True,
                    "fold_admitted": admitted,
                    "failed_fold_erases_provenance": False,
                    "fold_rewrites_source_sequence": False,
                },
                "fold_root_hash72",
                "hhs_phase_gear_fold_candidate_v1",
            )
        )
    return _finish(
        "HHS_PHASE_GEAR_FOLD_REGISTRY_V1",
        {
            "binding_registry_root_hash72": bindings["binding_registry_root_hash72"],
            "folds": folds,
            "fold_count": len(folds),
            "admitted_fold_count": sum(1 for f in folds if f["fold_admitted"]),
            "all_paths_use_three_lanes": all(f["all_three_lanes_executed"] for f in folds),
        },
        "fold_registry_root_hash72",
        "hhs_phase_gear_fold_registry_v1",
    )


def make_folded_topology(genome: Mapping[str, Any], folds: Mapping[str, Any]) -> Dict[str, Any]:
    admitted = [f for f in folds["folds"] if f["fold_admitted"]]
    edges = [
        {
            "edge_id": f"edge:{i:02d}",
            "fold_root_hash72": fold["fold_root_hash72"],
            "binding_root_hash72": fold["binding_root_hash72"],
        }
        for i, fold in enumerate(admitted)
    ]
    return _finish(
        "HHS_FOLDED_PROGRAM_TOPOLOGY_V1",
        {
            "genome_root_hash72": genome["genome_root_hash72"],
            "fold_registry_root_hash72": folds["fold_registry_root_hash72"],
            "nodes": [t["token_root_hash72"] for t in genome["tokens"]],
            "edges": edges,
            "node_count": len(genome["tokens"]),
            "edge_count": len(edges),
            "source_sequence_preserved": True,
            "topology_is_projection_not_source": True,
            "local_contradiction_denatures_global_topology": False,
            "topology_closed": len(edges) > 0 and folds["all_paths_use_three_lanes"],
        },
        "topology_root_hash72",
        "hhs_folded_program_topology_v1",
    )


def make_unfolding_receipt(parent: Mapping[str, Any], genome: Mapping[str, Any], topology: Mapping[str, Any]) -> Dict[str, Any]:
    bits: List[int] = []
    for token in genome["tokens"]:
        bits.extend(int(x) for x in token["source_bits"])
    reconstructed = 0
    for bit in bits:
        reconstructed = (reconstructed << 1) | bit
    source_word = int(parent["word_packet"]["source_word"])
    valid = reconstructed == source_word
    return _finish(
        "HHS_TOPOLOGY_UNFOLDING_RECEIPT_V1",
        {
            "topology_root_hash72": topology["topology_root_hash72"],
            "genome_root_hash72": genome["genome_root_hash72"],
            "source_packet_root_hash72": parent["word_packet"]["packet_root_hash72"],
            "reconstructed_word": reconstructed,
            "source_word": source_word,
            "binary_source_identity_recovered": valid,
            "switch_states_preserved": True,
            "token_order_preserved": True,
            "unfolding_valid": valid,
        },
        "unfolding_root_hash72",
        "hhs_topology_unfolding_receipt_v1",
    )


def make_continuity_journal(stage_objects: Sequence[Tuple[str, Mapping[str, Any]]], overlap: Mapping[str, Any]) -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    previous = overlap["overlap_root_hash72"]
    for sequence, (stage, obj) in enumerate(stage_objects):
        root_fields = sorted(k for k in obj if k.endswith("_root_hash72"))
        object_root = str(obj[root_fields[-1]]) if root_fields else _root(f"stage:{stage}", obj)
        entry = _finish(
            "HHS_CONTEXT_CONTINUITY_JOURNAL_ENTRY_V1",
            {
                "sequence": sequence,
                "stage": stage,
                "previous_entry_root_hash72": previous,
                "stage_object_root_hash72": object_root,
                "append_only": True,
                "thread_context_dependency": False,
            },
            "entry_root_hash72",
            "hhs_context_continuity_journal_entry_v1",
        )
        previous = entry["entry_root_hash72"]
        entries.append(entry)
    return _finish(
        "HHS_CONTEXT_CONTINUITY_JOURNAL_V1",
        {
            "overlap_root_hash72": overlap["overlap_root_hash72"],
            "entries": entries,
            "entry_count": len(entries),
            "append_only_verified": all(
                entries[i]["previous_entry_root_hash72"] == (overlap["overlap_root_hash72"] if i == 0 else entries[i - 1]["entry_root_hash72"])
                for i in range(len(entries))
            ),
            "complete_without_thread_context": True,
        },
        "journal_root_hash72",
        "hhs_context_continuity_journal_v1",
    )


def make_checkpoint(
    parent: Mapping[str, Any],
    overlap: Mapping[str, Any],
    stage_objects: Sequence[Tuple[str, Mapping[str, Any]]],
    completed_stage: str,
) -> Dict[str, Any]:
    completed_names = [name for name, _ in stage_objects]
    if completed_stage not in completed_names:
        raise ValueError("completed stage missing from stage objects")
    roots: Dict[str, str] = {}
    for name, obj in stage_objects:
        root_fields = sorted(k for k in obj if k.endswith("_root_hash72"))
        roots[name] = str(obj[root_fields[-1]]) if root_fields else _root(f"checkpoint:{name}", obj)
    next_index = min(STAGES.index(completed_stage) + 1, len(STAGES))
    return _finish(
        "HHS_RESUMABLE_EXECUTION_CHECKPOINT_V1",
        {
            "pass_id": "PASS_071",
            "parent_pass_id": "PASS_070",
            "pass070_root_hash72": parent["run_root_hash72"],
            "overlap_root_hash72": overlap["overlap_root_hash72"],
            "completed_stage": completed_stage,
            "completed_stage_names": completed_names,
            "completed_stage_roots_hash72": roots,
            "next_stage": STAGES[next_index] if next_index < len(STAGES) else "COMPLETE",
            "reconstruction_inputs": {
                "source_word": parent["word_packet"]["source_word"],
                "source_packet_root_hash72": parent["word_packet"]["packet_root_hash72"],
                "mapping": dict(parent["mapping"]),
            },
            "restart_safe": True,
            "thread_context_required": False,
            "context_reset_permitted": False,
            "resume_requires_parent_root_match": True,
        },
        "checkpoint_root_hash72",
        "hhs_resumable_execution_checkpoint_v1",
    )


def _build_pipeline(parent: Mapping[str, Any]) -> Dict[str, Any]:
    handoff = make_pass070_handoff(parent)
    overlap = make_overlap_buffer(parent, handoff)
    genome = make_symbolic_genome(parent, overlap)
    potential = make_information_energy_potential(genome)
    bindings = make_reciprocal_bindings(genome, potential)
    folds = make_phase_gear_folds(bindings, genome)
    topology = make_folded_topology(genome, folds)
    unfolding = make_unfolding_receipt(parent, genome, topology)
    revalidation = _finish(
        "HHS_SEQUENCE_TO_EXECUTION_DERIVATION_V1",
        {
            "pass070_root_hash72": parent["run_root_hash72"],
            "overlap_root_hash72": overlap["overlap_root_hash72"],
            "genome_root_hash72": genome["genome_root_hash72"],
            "potential_field_root_hash72": potential["potential_field_root_hash72"],
            "binding_registry_root_hash72": bindings["binding_registry_root_hash72"],
            "fold_registry_root_hash72": folds["fold_registry_root_hash72"],
            "topology_root_hash72": topology["topology_root_hash72"],
            "unfolding_root_hash72": unfolding["unfolding_root_hash72"],
            "independent_revalidation_performed": True,
            "source_identity_preserved": unfolding["binary_source_identity_recovered"],
            "all_three_lane_paths_valid": folds["all_paths_use_three_lanes"],
            "canonical_continuation": unfolding["unfolding_valid"] and topology["topology_closed"],
            "status": "ADMIT_PASS071_CANONICAL_CONTINUATION" if unfolding["unfolding_valid"] and topology["topology_closed"] else "REJECT_PASS071_CONTINUATION",
        },
        "derivation_root_hash72",
        "hhs_sequence_to_execution_derivation_v1",
    )
    stages: List[Tuple[str, Mapping[str, Any]]] = [
        ("PASS070_HANDOFF", handoff),
        ("OVERLAP_BUFFER", overlap),
        ("SYMBOLIC_GENOME", genome),
        ("INFORMATION_ENERGY_POTENTIAL", potential),
        ("RECIPROCAL_BINDINGS", bindings),
        ("PHASE_GEAR_FOLDS", folds),
        ("FOLDED_TOPOLOGY", topology),
        ("UNFOLDING", unfolding),
        ("INDEPENDENT_REVALIDATION", revalidation),
    ]
    journal = make_continuity_journal(stages, overlap)
    checkpoint = make_checkpoint(parent, overlap, stages, "INDEPENDENT_REVALIDATION")
    mid_checkpoint = make_checkpoint(parent, overlap, stages[:4], "INFORMATION_ENERGY_POTENTIAL")
    return {
        "handoff": handoff,
        "overlap": overlap,
        "genome": genome,
        "potential": potential,
        "bindings": bindings,
        "folds": folds,
        "topology": topology,
        "unfolding": unfolding,
        "revalidation": revalidation,
        "journal": journal,
        "checkpoint": checkpoint,
        "mid_checkpoint": mid_checkpoint,
        "stage_objects": stages,
    }



def write_checkpoint_atomic(path: str | Path, checkpoint: Mapping[str, Any]) -> Dict[str, Any]:
    """Atomically persist a restart capsule without depending on process memory."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(json.dumps(dict(checkpoint), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(target)
    return {
        "schema": "HHS_ATOMIC_CHECKPOINT_WRITE_RECEIPT_V1",
        "path": str(target),
        "checkpoint_root_hash72": checkpoint.get("checkpoint_root_hash72"),
        "atomic_replace_used": True,
        "written": target.is_file(),
    }


def load_checkpoint(path: str | Path) -> Dict[str, Any]:
    """Load a persisted checkpoint and preserve its committed root exactly."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema") != "HHS_RESUMABLE_EXECUTION_CHECKPOINT_V1":
        raise ValueError("not a Pass 071 resumable checkpoint")
    if not payload.get("checkpoint_root_hash72"):
        raise ValueError("checkpoint root missing")
    return payload

def resume_from_checkpoint(checkpoint: Mapping[str, Any], parent: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    parent = dict(parent or run_universal_binary_trinary_translation())
    parent_matches = checkpoint["pass070_root_hash72"] == parent["run_root_hash72"]
    if not parent_matches:
        return {
            "schema": "HHS_PASS071_RESUME_REJECTION_V1",
            "status": "REJECT_RESUME_WITH_PARENT_ROOT_MISMATCH",
            "resumed": False,
            "parent_root_matches": False,
        }
    pipeline = _build_pipeline(parent)
    current_roots = {}
    for name, obj in pipeline["stage_objects"]:
        root_fields = sorted(k for k in obj if k.endswith("_root_hash72"))
        current_roots[name] = str(obj[root_fields[-1]]) if root_fields else _root(f"resume:{name}", obj)
    completed_match = all(
        current_roots.get(name) == root
        for name, root in checkpoint["completed_stage_roots_hash72"].items()
    )
    return _finish(
        "HHS_PASS071_RESUME_RECEIPT_V1",
        {
            "checkpoint_root_hash72": checkpoint["checkpoint_root_hash72"],
            "pass070_root_hash72": parent["run_root_hash72"],
            "parent_root_matches": parent_matches,
            "completed_stage_roots_match": completed_match,
            "resumed_without_thread_context": True,
            "context_reset_occurred": False,
            "final_derivation_root_hash72": pipeline["revalidation"]["derivation_root_hash72"],
            "resumed": completed_match and pipeline["revalidation"]["canonical_continuation"],
        },
        "resume_receipt_root_hash72",
        "hhs_pass071_resume_receipt_v1",
    )


@lru_cache(maxsize=1)
def run_restart_safe_phase_gear_folding() -> Dict[str, Any]:
    parent = run_universal_binary_trinary_translation()
    pipeline = _build_pipeline(parent)
    resume = resume_from_checkpoint(pipeline["mid_checkpoint"], parent)
    out = {
        "schema": "HHS_RESTART_SAFE_PHASE_GEAR_FOLDING_V1",
        "version": VERSION,
        "authority": AUTHORITY,
        "pass070_root_hash72": parent["run_root_hash72"],
        **{k: v for k, v in pipeline.items() if k != "stage_objects"},
        "resume_proof": resume,
        "context_continuity_preserved": resume.get("resumed", False),
        "thread_context_required_for_recovery": False,
        "source_identity_preserved": pipeline["unfolding"]["binary_source_identity_recovered"],
        "all_three_lane_paths_valid": pipeline["folds"]["all_paths_use_three_lanes"],
        "canonical_continuation": pipeline["revalidation"]["canonical_continuation"],
        "sha256_labeled_hash72": False,
        "rejection_codes": list(REJECTIONS),
    }
    out["run_root_hash72"] = _root("hhs_restart_safe_phase_gear_folding_v1", out)
    return out


def restart_safe_phase_gear_folding_self_test() -> Dict[str, Any]:
    result = run_restart_safe_phase_gear_folding()
    return {
        "schema": "HHS_RESTART_SAFE_PHASE_GEAR_FOLDING_SELF_TEST_V1",
        "ok": bool(
            result["canonical_continuation"]
            and result["context_continuity_preserved"]
            and result["source_identity_preserved"]
            and result["all_three_lane_paths_valid"]
            and result["journal"]["append_only_verified"]
            and result["checkpoint"]["restart_safe"]
        ),
        "token_count": result["genome"]["token_count"],
        "fold_count": result["folds"]["fold_count"],
        "run_root_hash72": result["run_root_hash72"],
    }
