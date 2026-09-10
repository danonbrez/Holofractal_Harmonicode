"""Pass 219 RML16 bounded cache for deterministic RML12 route bundles.

The validated RML12 selector is a pure/read-only constructor for a complete
request identity: exact source gyroscope state, exact target gyroscope state,
and route id. Repeating that exact request currently rebuilds the same shortest
and complementary routes, Hopf metadata, Clifford metadata, inverse witnesses,
and selection receipt.

RML16 memoizes only those already-computed deterministic bundles. Endpoint
validation still executes before every lookup. The cache is bounded, process
local, non-persistent, and has no VM81/Hash authority. Values are stored and
returned through private deep copies so caller mutation cannot poison a future
cache hit.
"""
from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
from threading import RLock
from typing import Any, Mapping

from hhs_runtime.pass219.reciprocal_route_optimizer import (
    _canonical as _rml12_canonical,
    _require_admissible_state,
    build_and_select_reciprocal_route as _build_and_select_reciprocal_route_uncached,
)

PASS = 219
ITERATION = "RML16_DETERMINISTIC_RECIPROCAL_ROUTE_CACHE"
CACHE_SCHEMA = "HHS_PASS219_RML16_DETERMINISTIC_RECIPROCAL_ROUTE_CACHE_V1"
CACHE_CAPACITY = 256

_CACHE: OrderedDict[bytes, dict[str, Any]] = OrderedDict()
_CACHE_LOCK = RLock()
_CACHE_HITS = 0
_CACHE_MISSES = 0


def _validated_key(
    source: Mapping[str, Any],
    target: Mapping[str, Any],
    route_id: str,
) -> tuple[Mapping[str, Any], Mapping[str, Any], bytes]:
    """Validate with RML12 itself, then form the exact deterministic key."""
    valid_source = _require_admissible_state(source)
    valid_target = _require_admissible_state(target)
    key = _rml12_canonical(
        {
            "source": valid_source,
            "target": valid_target,
            "route_id": str(route_id),
        }
    )
    return valid_source, valid_target, key


def clear_reciprocal_route_cache() -> None:
    """Clear observational cache state; canonical runtime state is untouched."""
    global _CACHE_HITS, _CACHE_MISSES
    with _CACHE_LOCK:
        _CACHE.clear()
        _CACHE_HITS = 0
        _CACHE_MISSES = 0


def reciprocal_route_cache_info() -> dict[str, Any]:
    """Return observational cache counters with an explicit authority boundary."""
    with _CACHE_LOCK:
        return {
            "schema": CACHE_SCHEMA,
            "pass": PASS,
            "iteration": ITERATION,
            "capacity": CACHE_CAPACITY,
            "size": len(_CACHE),
            "hits": _CACHE_HITS,
            "misses": _CACHE_MISSES,
            "process_local": True,
            "persistent_cache": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_mint_authority": False,
            "canonical_hash216_persistence_authority": False,
            "timing_canonical_authority": False,
        }


def build_and_select_reciprocal_route_cached(
    source: Mapping[str, Any],
    target: Mapping[str, Any],
    *,
    route_id: str,
) -> dict[str, Any]:
    """Return the exact RML12 bundle, reusing only an identical prior request.

    Validation intentionally precedes cache lookup. This preserves RML12's
    fail-closed endpoint semantics even when a canonical key was seen before.
    """
    global _CACHE_HITS, _CACHE_MISSES
    valid_source, valid_target, key = _validated_key(source, target, route_id)

    with _CACHE_LOCK:
        try:
            cached = _CACHE.pop(key)
        except KeyError:
            cached = None
        else:
            _CACHE[key] = cached
            _CACHE_HITS += 1
            return deepcopy(cached)
        _CACHE_MISSES += 1

    result = _build_and_select_reciprocal_route_uncached(
        valid_source,
        valid_target,
        route_id=route_id,
    )
    stored = deepcopy(result)

    with _CACHE_LOCK:
        _CACHE[key] = stored
        _CACHE.move_to_end(key)
        while len(_CACHE) > CACHE_CAPACITY:
            _CACHE.popitem(last=False)

    return result


__all__ = [
    "CACHE_CAPACITY",
    "CACHE_SCHEMA",
    "clear_reciprocal_route_cache",
    "reciprocal_route_cache_info",
    "build_and_select_reciprocal_route_cached",
]
