"""Pass 219 RML19 exact route/composition conservation acceleration.

RML19 is an additive, transparent optimization over the frozen RML18 membrane.
It does not alter RML17 or RML18.  It removes repeated route/composition audit
work only when the complete typed candidate identity is exactly equal to an
already admitted candidate and the frozen RML18 parent nucleus still verifies.

The admission contract remains owned by RML18:
    1001/1000 == "1.001" -> ADMITTED
    anything else          -> NULL/UNDEFINED, Omega=true

No rejected record is cached.  Cache lookup uses exact immutable Python tokens,
not a probabilistic digest.  SHA-256 values exposed by cache_stats are
observational receipts only and do not participate in cache authority.
"""
from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
import hashlib
from pathlib import Path
from threading import RLock
from typing import Any, Mapping, Sequence

from hhs_runtime.pass219 import rml18_transport_conservation_acceleration as rml18

PASS = 219
ITERATION = "RML19_ROUTE_COMPOSITION_CONSERVATION_ACCELERATION"
SCHEMA = "HHS_PASS219_RML19_ROUTE_COMPOSITION_CONSERVATION_ACCELERATION_V1"
NULL_UNDEFINED = rml18.NULL_UNDEFINED
ADMITTED = rml18.ADMITTED

FROZEN_RML18_PARENT_COMMIT = "76cd6f995668dac3f1bfb10ae25a8301b2233237"
FROZEN_RML18_TREE_SHA = "3e1b1e3844cfa7757e49cc2112886fd09c9d40cd"
FROZEN_RML18_MODULE_GIT_BLOB_SHA1 = "d7c38ce7807f8bff386a765fdb37cbc254b6cd49"
FROZEN_RML18_MODULE_PATH = Path(rml18.__file__).resolve()

# 5184 is the fixed VM81 81x64 addressable operation capacity.  This is only a
# memory bound for the optimization cache; eviction cannot change semantics
# because every miss delegates to the frozen RML18 authority surface.
MAX_ROUTE_CERTIFICATES = 5184
MAX_COMPOSITION_CERTIFICATES = 5184

_LOCK = RLock()
_ROUTE_CERTIFICATES: OrderedDict[tuple[Any, ...], dict[str, Any]] = OrderedDict()
_COMPOSITION_CERTIFICATES: OrderedDict[tuple[Any, ...], dict[str, Any]] = OrderedDict()
_STATS = {
    "route_hits": 0,
    "route_misses": 0,
    "route_rejections": 0,
    "route_evictions": 0,
    "composition_hits": 0,
    "composition_misses": 0,
    "composition_rejections": 0,
    "composition_evictions": 0,
}


class RML19ExactKeyError(TypeError):
    """Raised internally when a candidate cannot form an exact cache key."""


def _git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _exact_token(value: Any, *, path: str = "$") -> tuple[Any, ...]:
    """Freeze supported values without scalar coercion or float admission."""
    if value is None:
        return ("none",)
    if isinstance(value, bool):
        return ("bool", value)
    if isinstance(value, int):
        return ("int", value)
    if isinstance(value, float):
        raise RML19ExactKeyError(f"RML19_FLOAT_REJECTED:{path}")
    if isinstance(value, str):
        return ("str", value)
    if isinstance(value, bytes):
        return ("bytes", value)
    if isinstance(value, Mapping):
        items: list[tuple[str, tuple[Any, ...]]] = []
        for key, child in value.items():
            if not isinstance(key, str):
                raise RML19ExactKeyError(f"RML19_NONSTRING_KEY_REJECTED:{path}")
            items.append((key, _exact_token(child, path=f"{path}.{key}")))
        items.sort(key=lambda pair: pair[0])
        return ("mapping", tuple(items))
    if isinstance(value, list):
        return (
            "list",
            tuple(_exact_token(child, path=f"{path}[{index}]") for index, child in enumerate(value)),
        )
    if isinstance(value, tuple):
        return (
            "tuple",
            tuple(_exact_token(child, path=f"{path}[{index}]") for index, child in enumerate(value)),
        )
    raise RML19ExactKeyError(
        f"RML19_UNSUPPORTED_EXACT_KEY_TYPE:{path}:{type(value).__name__}"
    )


def _rml18_parent_ready() -> tuple[bool, str, str | None]:
    """Revalidate the frozen RML18 module plus its inherited RML17 nucleus."""
    try:
        module_bytes = FROZEN_RML18_MODULE_PATH.read_bytes()
    except OSError:
        return False, "RML18_MODULE_MISSING", None
    observed_blob = _git_blob_sha1(module_bytes)
    if observed_blob != FROZEN_RML18_MODULE_GIT_BLOB_SHA1:
        return False, "RML18_MODULE_BLOB_MISMATCH", observed_blob

    parent_certificate = rml18.accelerated_address_manifold_certificate()
    parent_ok = (
        parent_certificate.get("status") == ADMITTED
        and parent_certificate.get("defined") is True
        and parent_certificate.get("omega_closure") is True
        and parent_certificate.get("rml17_equality_baseline_match") is True
        and rml18.exact_invariant_1001(parent_certificate.get("invariant"))
        and parent_certificate.get("canonical_vm81_mutation_authority") is False
        and parent_certificate.get("canonical_hash72_mint_authority") is False
        and parent_certificate.get("canonical_hash216_persistence_authority") is False
        and parent_certificate.get("floating_point_authority") is False
        and parent_certificate.get("scalar_projection_substitution_authority") is False
        and parent_certificate.get("route_selection_authority") is False
    )
    if not parent_ok:
        return False, "RML18_PARENT_CERTIFICATE_NOT_EXACT_1_001", observed_blob
    return True, "RML18_PARENT_EXACT", observed_blob


def _undefined(surface: str, reason: str, **context: Any) -> dict[str, Any]:
    result = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "surface": surface,
        "status": NULL_UNDEFINED,
        "defined": False,
        "omega_closure": True,
        "invariant": None,
        "rml17_equality_baseline_match": False,
        "reason": reason,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_authority": False,
        "scalar_projection_substitution_authority": False,
        "route_selection_authority": False,
        "cache_authority": False,
    }
    result.update(context)
    return result


def _exact_admitted_parent_record(record: Mapping[str, Any]) -> bool:
    return (
        record.get("status") == ADMITTED
        and record.get("defined") is True
        and record.get("omega_closure") is True
        and record.get("rml17_equality_baseline_match") is True
        and rml18.exact_invariant_1001(record.get("invariant"))
        and record.get("canonical_vm81_mutation_authority") is False
        and record.get("canonical_hash72_mint_authority") is False
        and record.get("canonical_hash216_persistence_authority") is False
        and record.get("floating_point_authority") is False
        and record.get("scalar_projection_substitution_authority") is False
        and record.get("route_selection_authority") is False
    )


def _cache_get(
    cache: OrderedDict[tuple[Any, ...], dict[str, Any]],
    key: tuple[Any, ...],
    *,
    hit_field: str,
    miss_field: str,
) -> dict[str, Any] | None:
    with _LOCK:
        record = cache.get(key)
        if record is None:
            _STATS[miss_field] += 1
            return None
        cache.move_to_end(key)
        _STATS[hit_field] += 1
        return deepcopy(record)


def _cache_put(
    cache: OrderedDict[tuple[Any, ...], dict[str, Any]],
    key: tuple[Any, ...],
    record: Mapping[str, Any],
    *,
    capacity: int,
    eviction_field: str,
) -> None:
    with _LOCK:
        cache[key] = deepcopy(dict(record))
        cache.move_to_end(key)
        while len(cache) > capacity:
            cache.popitem(last=False)
            _STATS[eviction_field] += 1


def _route_key(
    source: Mapping[str, Any],
    target: Mapping[str, Any],
    *,
    route_id: str,
) -> tuple[Any, ...]:
    return (
        "RML19_ROUTE_CERTIFICATE_V1",
        FROZEN_RML18_PARENT_COMMIT,
        FROZEN_RML18_TREE_SHA,
        FROZEN_RML18_MODULE_GIT_BLOB_SHA1,
        _exact_token(str(route_id)),
        _exact_token(source),
        _exact_token(target),
    )


def _composition_key(
    states: Sequence[Mapping[str, Any]],
    *,
    composition_id: str,
) -> tuple[Any, ...]:
    return (
        "RML19_COMPOSITION_CERTIFICATE_V1",
        FROZEN_RML18_PARENT_COMMIT,
        FROZEN_RML18_TREE_SHA,
        FROZEN_RML18_MODULE_GIT_BLOB_SHA1,
        _exact_token(str(composition_id)),
        _exact_token(list(states)),
    )


def clear_rml19_certificate_cache() -> None:
    """Clear optimization state only; canonical runtime state is untouched."""
    with _LOCK:
        _ROUTE_CERTIFICATES.clear()
        _COMPOSITION_CERTIFICATES.clear()
        for field in _STATS:
            _STATS[field] = 0


def cache_stats() -> dict[str, Any]:
    """Return observational cache counters and frozen-parent identity."""
    with _LOCK:
        counters = dict(_STATS)
        route_entries = len(_ROUTE_CERTIFICATES)
        composition_entries = len(_COMPOSITION_CERTIFICATES)
    return {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "frozen_rml18_parent_commit": FROZEN_RML18_PARENT_COMMIT,
        "frozen_rml18_tree_sha": FROZEN_RML18_TREE_SHA,
        "frozen_rml18_module_git_blob_sha1": FROZEN_RML18_MODULE_GIT_BLOB_SHA1,
        "route_entries": route_entries,
        "composition_entries": composition_entries,
        "max_route_certificates": MAX_ROUTE_CERTIFICATES,
        "max_composition_certificates": MAX_COMPOSITION_CERTIFICATES,
        **counters,
        "timing_participates_in_admission": False,
        "digest_participates_in_cache_lookup": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_authority": False,
        "scalar_projection_substitution_authority": False,
        "route_selection_authority": False,
        "cache_authority": False,
    }


def verify_frozen_rml18_parent() -> dict[str, Any]:
    ready, reason, observed_blob = _rml18_parent_ready()
    if not ready:
        return _undefined(
            "RML18_PARENT",
            reason,
            observed_rml18_module_git_blob_sha1=observed_blob,
        )
    return {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "surface": "RML18_PARENT",
        "status": ADMITTED,
        "defined": True,
        "omega_closure": True,
        "invariant": {
            "numerator": rml18.INVARIANT_NUMERATOR,
            "denominator": rml18.INVARIANT_DENOMINATOR,
            "decimal": rml18.INVARIANT_DECIMAL,
            "binary_floating_point_used": False,
        },
        "rml17_equality_baseline_match": True,
        "frozen_rml18_parent_commit": FROZEN_RML18_PARENT_COMMIT,
        "frozen_rml18_tree_sha": FROZEN_RML18_TREE_SHA,
        "frozen_rml18_module_git_blob_sha1": observed_blob,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_authority": False,
        "scalar_projection_substitution_authority": False,
        "route_selection_authority": False,
        "cache_authority": False,
    }


def gate_route_candidate(
    source: Mapping[str, Any],
    target: Mapping[str, Any],
    *,
    route_id: str,
) -> dict[str, Any]:
    """Return the byte-for-byte RML18 route record, reusing only exact admissions."""
    ready, reason, observed_blob = _rml18_parent_ready()
    if not ready:
        return _undefined(
            "ROUTE",
            reason,
            observed_rml18_module_git_blob_sha1=observed_blob,
        )

    try:
        key = _route_key(source, target, route_id=route_id)
    except (RML19ExactKeyError, TypeError, ValueError):
        # Unsupported/malformed inputs are delegated to the frozen fail-closed
        # membrane and are never candidates for optimization reuse.
        with _LOCK:
            _STATS["route_rejections"] += 1
        return rml18.gate_route_candidate(source, target, route_id=route_id)

    cached = _cache_get(
        _ROUTE_CERTIFICATES,
        key,
        hit_field="route_hits",
        miss_field="route_misses",
    )
    if cached is not None:
        return cached

    record = rml18.gate_route_candidate(source, target, route_id=route_id)
    if _exact_admitted_parent_record(record):
        _cache_put(
            _ROUTE_CERTIFICATES,
            key,
            record,
            capacity=MAX_ROUTE_CERTIFICATES,
            eviction_field="route_evictions",
        )
    else:
        with _LOCK:
            _STATS["route_rejections"] += 1
    return record


def gate_composed_route_candidate(
    states: Sequence[Mapping[str, Any]],
    *,
    composition_id: str,
) -> dict[str, Any]:
    """Return the exact RML18 composition record, reusing only exact admissions."""
    ready, reason, observed_blob = _rml18_parent_ready()
    if not ready:
        return _undefined(
            "ROUTE_COMPOSITION",
            reason,
            observed_rml18_module_git_blob_sha1=observed_blob,
        )

    try:
        key = _composition_key(states, composition_id=composition_id)
    except (RML19ExactKeyError, TypeError, ValueError):
        with _LOCK:
            _STATS["composition_rejections"] += 1
        return rml18.gate_composed_route_candidate(
            states,
            composition_id=composition_id,
        )

    cached = _cache_get(
        _COMPOSITION_CERTIFICATES,
        key,
        hit_field="composition_hits",
        miss_field="composition_misses",
    )
    if cached is not None:
        return cached

    record = rml18.gate_composed_route_candidate(
        states,
        composition_id=composition_id,
    )
    if _exact_admitted_parent_record(record):
        _cache_put(
            _COMPOSITION_CERTIFICATES,
            key,
            record,
            capacity=MAX_COMPOSITION_CERTIFICATES,
            eviction_field="composition_evictions",
        )
    else:
        with _LOCK:
            _STATS["composition_rejections"] += 1
    return record


__all__ = [
    "ADMITTED",
    "FROZEN_RML18_MODULE_GIT_BLOB_SHA1",
    "FROZEN_RML18_PARENT_COMMIT",
    "FROZEN_RML18_TREE_SHA",
    "ITERATION",
    "MAX_COMPOSITION_CERTIFICATES",
    "MAX_ROUTE_CERTIFICATES",
    "NULL_UNDEFINED",
    "RML19ExactKeyError",
    "SCHEMA",
    "cache_stats",
    "clear_rml19_certificate_cache",
    "gate_composed_route_candidate",
    "gate_route_candidate",
    "verify_frozen_rml18_parent",
]
