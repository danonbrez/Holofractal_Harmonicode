"""
HHS Validation Residue Compactor v1
===================================

Pass 043 performance authority: expanded validation metadata may be large while
it is being evaluated, but persistent state must compact to a bounded residue
root plus reconstruction recipe once validation has completed.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, Mapping, Optional
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness

VERSION = "PASS_043_KERNEL_DERIVED_RUNTIME_AUTOCOMPOSITION_V1"
COMPACTION_SCHEMA = "HHS_VALIDATION_RESIDUE_COMPACTION_V1"
RESIDUE_SCHEMA = "HHS_COMPACT_CONFORMANCE_RESIDUE_V1"
RECIPE_SCHEMA = "HHS_RECONSTRUCTION_RECIPE_V1"
EVICTION_SCHEMA = "HHS_EXPANDED_METADATA_EVICTION_RECORD_V1"

REJECT_RESIDUE_WITHOUT_RECONSTRUCTION_RECIPE = "REJECT_RESIDUE_WITHOUT_RECONSTRUCTION_RECIPE"
REJECT_COMPACTION_BREAKS_HASH72_WITNESS = "REJECT_COMPACTION_BREAKS_HASH72_WITNESS"
REJECT_COMPACTION_BREAKS_SURFACE_DERIVATION = "REJECT_COMPACTION_BREAKS_SURFACE_DERIVATION"
REJECT_UNBOUNDED_METADATA_PERSISTENCE = "REJECT_UNBOUNDED_METADATA_PERSISTENCE"
REJECT_VALIDATED_METADATA_DUPLICATION = "REJECT_VALIDATED_METADATA_DUPLICATION"


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _hash72(label: str, payload: Any) -> str:
    return make_hash72_kernel_witness(label, payload, width=72).digest


def _bounded_summary(expanded_state: Mapping[str, Any]) -> Dict[str, Any]:
    surfaces = expanded_state.get("surfaces") or []
    edges = expanded_state.get("edges") or []
    decisions = expanded_state.get("decisions") or expanded_state.get("conformance_decisions") or []
    return {
        "schema": "HHS_BOUNDED_METADATA_SUMMARY_V1",
        "source_schema": str(expanded_state.get("schema", "UNKNOWN")),
        "source_version": str(expanded_state.get("version", "UNKNOWN")),
        "surface_count": int(expanded_state.get("surface_count", len(surfaces)) or 0),
        "edge_count": int(expanded_state.get("conformance_edge_count", len(edges)) or 0),
        "decision_count": int(expanded_state.get("decision_count", len(decisions)) or 0),
        "underived_surface_count": len(expanded_state.get("underived_surfaces", []) or []),
        "root_hint": expanded_state.get("conformance_root_hash72") or expanded_state.get("root_hash72") or "",
    }


def build_reconstruction_recipe(expanded_state: Mapping[str, Any], *, source_id: str = "expanded:validation") -> Dict[str, Any]:
    """Return a deterministic recipe, not a duplicate of the expanded payload."""

    source_schema = str(expanded_state.get("schema", "UNKNOWN"))
    recipe = {
        "schema": RECIPE_SCHEMA,
        "version": VERSION,
        "source_id": source_id,
        "source_schema": source_schema,
        "source_root_hash72": _hash72("HHS_EXPANDED_VALIDATION_SOURCE_V1", expanded_state),
        "reconstruction_mode": "VERIFY_OR_REBUILD_FROM_CANONICAL_GENERATORS",
        "canonical_generators": [
            "hhs_kernel_invariant_registry_v1.build_default_invariant_registry",
            "hhs_kernel_conformance_surface_map_v1.build_surface_map",
            "hhs_kernel_runtime_autocomposer_v1.compose_surface_pipeline",
        ],
        "retained_fields": [
            "schema", "version", "source_id", "source_schema", "source_root_hash72",
            "residue_root_hash72", "bounded_summary", "kernel_authority",
        ],
    }
    recipe["recipe_hash72"] = _hash72(RECIPE_SCHEMA, recipe)
    return recipe


def build_residue_root(expanded_state: Mapping[str, Any], recipe: Mapping[str, Any]) -> str:
    payload = {
        "schema": RESIDUE_SCHEMA,
        "source_root_hash72": recipe.get("source_root_hash72"),
        "recipe_hash72": recipe.get("recipe_hash72"),
        "bounded_summary": _bounded_summary(expanded_state),
    }
    return _hash72(RESIDUE_SCHEMA, payload)


def compact_validation_residue(expanded_state: Mapping[str, Any], *, source_id: str = "expanded:validation", retain_expanded: bool = False) -> Dict[str, Any]:
    recipe = build_reconstruction_recipe(expanded_state, source_id=source_id)
    residue_root = build_residue_root(expanded_state, recipe)
    residue = {
        "schema": RESIDUE_SCHEMA,
        "version": VERSION,
        "source_id": source_id,
        "source_schema": recipe["source_schema"],
        "source_root_hash72": recipe["source_root_hash72"],
        "residue_root_hash72": residue_root,
        "bounded_summary": _bounded_summary(expanded_state),
        "reconstruction_recipe": recipe,
        "expanded_payload_retained": bool(retain_expanded),
        "expanded_payload": deepcopy(dict(expanded_state)) if retain_expanded else None,
        "kernel_authority": "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1",
    }
    witness_payload = {k: v for k, v in residue.items() if k not in {"expanded_payload"}}
    residue["hash72_kernel_witness"] = make_hash72_kernel_witness(COMPACTION_SCHEMA, witness_payload, width=72).to_dict()
    return residue


def verify_residue_reconstruction(residue: Mapping[str, Any], expanded_state: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    reasons = []
    recipe = residue.get("reconstruction_recipe") or {}
    if not recipe:
        reasons.append(REJECT_RESIDUE_WITHOUT_RECONSTRUCTION_RECIPE)
    if residue.get("expanded_payload_retained"):
        reasons.append(REJECT_VALIDATED_METADATA_DUPLICATION)
    if recipe and residue.get("residue_root_hash72"):
        if expanded_state is not None:
            expected = build_residue_root(expanded_state, recipe)
            if expected != residue.get("residue_root_hash72"):
                reasons.append(REJECT_COMPACTION_BREAKS_HASH72_WITNESS)
        if not (residue.get("bounded_summary") or {}).get("source_schema"):
            reasons.append(REJECT_COMPACTION_BREAKS_SURFACE_DERIVATION)
    return {
        "schema": "HHS_VALIDATION_RESIDUE_RECONSTRUCTION_DECISION_V1",
        "version": VERSION,
        "ok": not reasons,
        "status": "ADMIT_COMPACT_RESIDUE_RECONSTRUCTABLE" if not reasons else "REJECT_INVALID_COMPACT_RESIDUE",
        "reasons": reasons,
        "residue_root_hash72": residue.get("residue_root_hash72"),
        "recipe_hash72": recipe.get("recipe_hash72"),
    }


def evict_expanded_metadata(residue: Mapping[str, Any]) -> Dict[str, Any]:
    compact = dict(residue)
    had_expanded = bool(compact.get("expanded_payload") is not None or compact.get("expanded_payload_retained"))
    compact["expanded_payload"] = None
    compact["expanded_payload_retained"] = False
    eviction = {
        "schema": EVICTION_SCHEMA,
        "version": VERSION,
        "source_id": compact.get("source_id"),
        "residue_root_hash72": compact.get("residue_root_hash72"),
        "had_expanded_payload": had_expanded,
        "eviction_status": "EXPANDED_METADATA_EVICTED_AFTER_COMPACTION",
        "retained_residue_only": True,
    }
    eviction["eviction_hash72"] = _hash72(EVICTION_SCHEMA, eviction)
    compact["eviction_record"] = eviction
    return compact


def summarize_compaction_gain(expanded_state: Mapping[str, Any], residue: Mapping[str, Any]) -> Dict[str, Any]:
    expanded_bytes = len(canonical_json(expanded_state).encode("utf-8"))
    compact_payload = {k: v for k, v in residue.items() if k != "expanded_payload"}
    compact_bytes = len(canonical_json(compact_payload).encode("utf-8"))
    saved = max(0, expanded_bytes - compact_bytes)
    return {
        "schema": "HHS_COMPACTION_GAIN_SUMMARY_V1",
        "version": VERSION,
        "expanded_bytes": expanded_bytes,
        "compact_bytes": compact_bytes,
        "bytes_saved": saved,
        "compression_ratio": (expanded_bytes / compact_bytes) if compact_bytes else None,
        "expanded_payload_persisted": bool(residue.get("expanded_payload_retained")),
    }


def validation_residue_compactor_self_test() -> Dict[str, Any]:
    from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map

    expanded = build_surface_map()
    residue = compact_validation_residue(expanded, source_id="pass043:surface_map")
    residue = evict_expanded_metadata(residue)
    reconstruction = verify_residue_reconstruction(residue, expanded)
    gain = summarize_compaction_gain(expanded, residue)
    return {
        "schema": "HHS_VALIDATION_RESIDUE_COMPACTOR_SELF_TEST_V1",
        "version": VERSION,
        "ok": reconstruction.get("ok") and not residue.get("expanded_payload_retained"),
        "residue": residue,
        "reconstruction": reconstruction,
        "gain": gain,
    }


if __name__ == "__main__":
    print(validation_residue_compactor_self_test())
