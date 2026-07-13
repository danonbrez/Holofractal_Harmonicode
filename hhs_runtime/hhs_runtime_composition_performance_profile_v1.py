"""
HHS Runtime Composition Performance Profile v1
==============================================

Pass 043 profile for metadata growth control: measure expanded graph size,
compact residue size, cache reuse, and lifecycle/decay behavior.
"""

from __future__ import annotations

from typing import Any, Dict

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_validation_residue_compactor_v1 import canonical_json, compact_validation_residue, evict_expanded_metadata, summarize_compaction_gain
from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_composed_preflight
from hhs_runtime.hhs_expanded_state_decay_lifecycle_v1 import register_expanded_state, self_delete_expired_expanded_state

VERSION = "PASS_043_KERNEL_DERIVED_RUNTIME_AUTOCOMPOSITION_V1"
PROFILE_SCHEMA = "HHS_COMPOSITION_PERFORMANCE_PROFILE_V1"


def _hash72(label: str, payload: Any) -> str:
    return make_hash72_kernel_witness(label, payload, width=72).digest


def profile_expanded_vs_compact(expanded_state: Dict[str, Any]) -> Dict[str, Any]:
    residue = compact_validation_residue(expanded_state, source_id="performance:expanded_state")
    residue = evict_expanded_metadata(residue)
    gain = summarize_compaction_gain(expanded_state, residue)
    profile = {
        "schema": PROFILE_SCHEMA,
        "version": VERSION,
        "expanded_bytes": gain["expanded_bytes"],
        "compact_bytes": gain["compact_bytes"],
        "bytes_saved": gain["bytes_saved"],
        "compression_ratio": gain["compression_ratio"],
        "expanded_payload_persisted": False,
        "residue_root_hash72": residue.get("residue_root_hash72"),
    }
    profile["profile_hash72"] = _hash72(PROFILE_SCHEMA, profile)
    return profile


def profile_cache_reuse(surface_id: str, operation: str, *, surface_map: Dict[str, Any]) -> Dict[str, Any]:
    cache: Dict[str, Dict[str, Any]] = {}
    first = execute_composed_preflight(surface_id, operation=operation, surface_map=surface_map, cache=cache)
    second = execute_composed_preflight(surface_id, operation=operation, surface_map=surface_map, cache=cache)
    return {
        "schema": "HHS_COMPOSITION_CACHE_REUSE_PROFILE_V1",
        "version": VERSION,
        "surface_id": surface_id,
        "operation": operation,
        "first_cache_hit": bool(first.get("cache", {}).get("cache_hit")),
        "second_cache_hit": bool(second.get("cache", {}).get("cache_hit")),
        "cache_entry_count": len(cache),
        "expanded_metadata_persisted": bool(first.get("expanded_metadata_persisted") or second.get("expanded_metadata_persisted")),
    }


def profile_decay_lifecycle() -> Dict[str, Any]:
    expanded = {"schema": "HHS_PROFILE_TEMP_EXPANDED_STATE_V1", "items": list(range(8))}
    handle = register_expanded_state(
        "expanded:profile:decay",
        expanded,
        source_surface_id="service:runtime_composition_performance_profile.self_test",
        created_at_tick=1,
        decay_window_ticks=2,
    )
    decay = self_delete_expired_expanded_state(handle, current_tick=3)
    return {
        "schema": "HHS_DECAY_LIFECYCLE_PERFORMANCE_PROFILE_V1",
        "version": VERSION,
        "registered_root_hash72": handle.get("expanded_payload_root_hash72"),
        "decay_status": decay.get("status"),
        "expanded_payload_persisted_after_decay": bool(decay.get("expanded_payload")),
        "decay_witness_hash72": (decay.get("decay_witness") or {}).get("decay_witness_hash72"),
    }


def build_performance_profile() -> Dict[str, Any]:
    from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map

    surface_map = build_surface_map()
    service = next((s for s in surface_map.get("surfaces", []) if s.get("surface_type") == "SERVICE"), surface_map.get("surfaces", [{}])[0])
    operation = (service.get("declared_operations") or [service.get("symbol") or "self_test"])[0]
    expanded_profile = profile_expanded_vs_compact(surface_map)
    cache_profile = profile_cache_reuse(service.get("surface_id"), operation, surface_map=surface_map)
    decay_profile = profile_decay_lifecycle()
    profile = {
        "schema": "HHS_RUNTIME_COMPOSITION_PERFORMANCE_PROFILE_REPORT_V1",
        "version": VERSION,
        "surface_count": surface_map.get("surface_count"),
        "conformance_edge_count": surface_map.get("conformance_edge_count"),
        "expanded_vs_compact": expanded_profile,
        "cache_reuse": cache_profile,
        "decay_lifecycle": decay_profile,
        "performance_doctrine": "VALIDATION_MAY_EXPAND_PERSISTENCE_MUST_COMPRESS",
        "ok": expanded_profile.get("bytes_saved", 0) >= 0 and cache_profile.get("second_cache_hit") and not decay_profile.get("expanded_payload_persisted_after_decay"),
    }
    profile["performance_root_hash72"] = _hash72("HHS_RUNTIME_COMPOSITION_PERFORMANCE_PROFILE_REPORT_V1", profile)
    return profile


def runtime_composition_performance_profile_self_test() -> Dict[str, Any]:
    return build_performance_profile()


if __name__ == "__main__":
    print(runtime_composition_performance_profile_self_test())
