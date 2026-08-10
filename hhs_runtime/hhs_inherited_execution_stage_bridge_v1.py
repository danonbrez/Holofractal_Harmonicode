"""Bridge proven inherited optimization stages into the Pass 217 composer.

This module does not reimplement the inherited authorities.  It calls their
existing repository-native implementations and converts the resulting observed
receipts into `ACTIVE_IN_PATH` traversal witnesses for the cumulative authority
model.

Checkpoint scope:
- Pass 043 conformance decision cache: already traversed by every composed
  preflight; this bridge exposes its concrete cache-entry witness.
- Pass 044 semantic composition cache: actually load/validate/reuse or store the
  compact dependency-rooted composition entry.
- Pass 111 predictive continuation cache: mechanically `NOT_APPLICABLE` only
  when no continuation contract markers are present.  If markers are present,
  no state is fabricated; reachability remains unresolved and fails closed
  until the real Pass 111 resume path is attached.
"""

from __future__ import annotations

import os
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Mapping, Optional

from hhs_runtime.hhs_cumulative_execution_authority_v1 import (
    build_authority_reachability,
)
from hhs_runtime.hhs_semantic_composition_cache_v1 import (
    SemanticCompositionCache,
    validate_cache_entry as validate_semantic_cache_entry,
)


VERSION = "PASS_217_INHERITED_EXECUTION_STAGE_BRIDGE_V1"
INITIAL_REQUIRED_AUTHORITIES = (
    "conformance_decision_cache",
    "semantic_composition_cache",
    "predictive_continuation_cache",
)

CONTINUATION_MARKERS = frozenset(
    {
        "continuation_cache",
        "continuation_cache_root_hash72",
        "continuation_lease",
        "continuation_lease_root_hash72",
        "suspension_coordinate",
        "pending_step_start",
        "pending_step_end",
        "pre_tail_checkpoint",
        "one_ninth_tail_receipts",
        "resume_admission_root_hash72",
        "maximum_replay_steps",
        "maximum_continuation_steps",
    }
)

_SEMANTIC_LOCK = RLock()
_SEMANTIC_CACHE_SINGLETON: Optional[SemanticCompositionCache] = None


def _default_semantic_cache() -> SemanticCompositionCache:
    global _SEMANTIC_CACHE_SINGLETON
    with _SEMANTIC_LOCK:
        if _SEMANTIC_CACHE_SINGLETON is None:
            path = Path(
                os.environ.get(
                    "HHS_LIVE_SEMANTIC_COMPOSITION_CACHE_PATH",
                    "demo_reports/hhs_live_semantic_composition_cache_pass217.json",
                )
            )
            _SEMANTIC_CACHE_SINGLETON = SemanticCompositionCache(path)
        return _SEMANTIC_CACHE_SINGLETON


def _find_keys(value: Any, targets: frozenset[str], found: set[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            text = str(key)
            if text in targets:
                found.add(text)
            _find_keys(child, targets, found)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _find_keys(child, targets, found)


def continuation_context_facts(payload: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    found: set[str] = set()
    _find_keys(dict(payload or {}), CONTINUATION_MARKERS, found)
    markers = sorted(found)
    return {
        "schema": "HHS_PASS217_CONTINUATION_APPLICABILITY_FACTS_V1",
        "continuation_context_present": bool(markers),
        "observed_markers": markers,
        "marker_count": len(markers),
    }


def conformance_decision_cache_proof(preflight: Mapping[str, Any]) -> Dict[str, Any]:
    lookup = dict(preflight.get("cache") or {})
    entry = dict(lookup.get("entry") or {})
    root = str(entry.get("cache_entry_hash72") or "")
    return {
        "observed": bool(root),
        "path": [
            "kernel_runtime_autocomposer",
            "conformance_decision_cache",
        ],
        "traversal_witness": {
            "schema": lookup.get("schema"),
            "cache_hit": bool(lookup.get("cache_hit")),
            "cache_key_hash72": entry.get("cache_key_hash72"),
            "decision_root_hash72": entry.get("decision_root_hash72"),
            "derivation_complete": entry.get("derivation_complete"),
        },
        "witness_root": root,
    }


def observe_semantic_composition_cache(
    preflight: Mapping[str, Any],
    surface: Mapping[str, Any],
    *,
    semantic_cache: Optional[SemanticCompositionCache] = None,
) -> Dict[str, Any]:
    """Traverse the inherited Pass 044 cache and return its compact witness."""

    plan = dict(preflight.get("composition_plan") or {})
    if not plan:
        raise RuntimeError("REJECT_SEMANTIC_COMPOSITION_CACHE_WITHOUT_PLAN")
    root = str(preflight.get("conformance_root_hash72") or "")
    if not root:
        raise RuntimeError("REJECT_SEMANTIC_COMPOSITION_CACHE_WITHOUT_CONFORMANCE_ROOT")
    surface_map = {
        "schema": "HHS_PASS217_DIRECT_SURFACE_ROOT_VIEW_V1",
        "conformance_root_hash72": root,
        "invariant_registry_root_hash72": root,
        "surface_derivation_root_hash72": surface.get("derivation_hash72"),
    }
    cache = semantic_cache or _default_semantic_cache()

    with _SEMANTIC_LOCK:
        candidate = cache.build_entry(
            plan,
            surface_map,
            created_at_tick=0,
            decay_window_ticks=12,
        )
        key = str(candidate.get("cache_key_hash72") or "")
        data = cache.load()
        existing = next(
            (
                dict(row)
                for row in data.get("records", []) or []
                if row.get("cache_key_hash72") == key
            ),
            None,
        )
        cache_hit = existing is not None
        stale_replaced = False
        if existing is not None:
            validation = validate_semantic_cache_entry(
                existing,
                current_surface_map=surface_map,
                current_tick=0,
            )
            if validation.get("ok"):
                admitted_entry = existing
            else:
                stale_replaced = True
                admitted_entry = cache.store_entry(candidate)
                validation = validate_semantic_cache_entry(
                    admitted_entry,
                    current_surface_map=surface_map,
                    current_tick=0,
                )
        else:
            admitted_entry = cache.store_entry(candidate)
            validation = validate_semantic_cache_entry(
                admitted_entry,
                current_surface_map=surface_map,
                current_tick=0,
            )
        if not validation.get("ok"):
            raise RuntimeError(
                "REJECT_SEMANTIC_COMPOSITION_CACHE_TRAVERSAL:"
                + "|".join(validation.get("reasons", []))
            )

    witness_root = str(admitted_entry.get("cache_entry_hash72") or "")
    return {
        "observed": bool(witness_root),
        "path": [
            "kernel_runtime_autocomposer",
            "semantic_composition_cache",
        ],
        "traversal_witness": {
            "schema": "HHS_PASS217_SEMANTIC_COMPOSITION_CACHE_TRAVERSAL_V1",
            "cache_hit": cache_hit and not stale_replaced,
            "stale_entry_replaced": stale_replaced,
            "cache_key_hash72": admitted_entry.get("cache_key_hash72"),
            "composition_root_hash72": admitted_entry.get(
                "composition_root_hash72"
            ),
            "validation_status": validation.get("status"),
            "expanded_payload_persisted": bool(
                admitted_entry.get("expanded_payload_persisted")
            ),
            "reconstruction_recipe_hash72": (
                admitted_entry.get("reconstruction_recipe") or {}
            ).get("recipe_hash72"),
        },
        "witness_root": witness_root,
    }


def build_initial_inherited_authority_reachability(
    preflight: Mapping[str, Any],
    surface: Mapping[str, Any],
    payload: Optional[Mapping[str, Any]] = None,
    *,
    semantic_cache: Optional[SemanticCompositionCache] = None,
) -> Dict[str, Any]:
    """Build the first production reachability slice from real stage traversals."""

    active = {
        "conformance_decision_cache": conformance_decision_cache_proof(preflight),
        "semantic_composition_cache": observe_semantic_composition_cache(
            preflight,
            surface,
            semantic_cache=semantic_cache,
        ),
    }
    continuation = continuation_context_facts(payload)
    not_applicable: Dict[str, Dict[str, Any]] = {}
    if continuation["continuation_context_present"] is False:
        not_applicable["predictive_continuation_cache"] = {
            "mechanically_proven": True,
            "predicate": "continuation_context_present == false",
            "observed_facts": continuation,
            "reason": (
                "no Pass 111 continuation contract marker is present in the "
                "operation payload"
            ),
        }

    record = build_authority_reachability(
        str(preflight.get("operation") or surface.get("symbol") or "operation"),
        active_in_path=active,
        not_applicable=not_applicable,
        required_authorities=INITIAL_REQUIRED_AUTHORITIES,
    )
    record["continuation_applicability_facts"] = continuation
    record["checkpoint_scope"] = list(INITIAL_REQUIRED_AUTHORITIES)
    return record


__all__ = [
    "VERSION",
    "INITIAL_REQUIRED_AUTHORITIES",
    "CONTINUATION_MARKERS",
    "continuation_context_facts",
    "conformance_decision_cache_proof",
    "observe_semantic_composition_cache",
    "build_initial_inherited_authority_reachability",
]
