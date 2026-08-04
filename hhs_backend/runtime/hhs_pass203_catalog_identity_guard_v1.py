"""Immutable catalog identity guard for the Pass 203 hosted mainframe.

The V1 mainframe intentionally caches discovery results, but ``catalog()``
returned a shallow list whose descriptor dictionaries remained shared. Hosted
serialization, projections, or diagnostics could therefore retain and mutate a
descriptor after a status hash had been emitted. This guard is installed on the
canonical hosted singleton and provides atomic deep snapshots while preserving
explicit refresh behavior.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from threading import RLock
from types import MethodType
from typing import Any, Dict, List

SCHEMA = "HHS_PASS_203_CATALOG_IDENTITY_GUARD_V1"


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


class Pass203CatalogIdentityGuard:
    """Own one immutable descriptor snapshot for a mainframe instance."""

    def __init__(self, runtime: Any) -> None:
        self.runtime = runtime
        self._lock = RLock()
        self._snapshot: List[Dict[str, Any]] = []
        self._catalog_sha256 = _sha256([])
        self._generation = 0
        self._original_refresh = runtime.refresh
        self._original_catalog = runtime.catalog

    def capture(self) -> Dict[str, Any]:
        with self._lock:
            if getattr(self.runtime, "_catalog", None) is None:
                self._original_refresh()
            records = deepcopy(list(getattr(self.runtime, "_catalog", None) or []))
            self._snapshot = records
            self._catalog_sha256 = _sha256(records)
            self._generation += 1
            return self.status()

    def catalog(self) -> List[Dict[str, Any]]:
        with self._lock:
            if not self._snapshot:
                self.capture()
            return deepcopy(self._snapshot)

    def refresh(self) -> Dict[str, Any]:
        with self._lock:
            report = dict(self._original_refresh())
            self.capture()
            report["catalog_sha256"] = self._catalog_sha256
            report["catalog_identity_guard"] = SCHEMA
            report["catalog_identity_generation"] = self._generation
            return report

    def status(self) -> Dict[str, Any]:
        return {
            "schema": SCHEMA,
            "installed": True,
            "catalog_sha256": self._catalog_sha256,
            "catalog_count": len(self._snapshot),
            "generation": self._generation,
            "deep_snapshot": True,
            "caller_mutation_isolated": True,
        }


def install_pass203_catalog_identity_guard(runtime: Any) -> Pass203CatalogIdentityGuard:
    """Install the guard once and return its stable controller."""

    existing = getattr(runtime, "_pass203_catalog_identity_guard", None)
    if isinstance(existing, Pass203CatalogIdentityGuard):
        return existing

    guard = Pass203CatalogIdentityGuard(runtime)
    guard.capture()

    def guarded_catalog(_runtime: Any) -> List[Dict[str, Any]]:
        return guard.catalog()

    def guarded_refresh(_runtime: Any) -> Dict[str, Any]:
        return guard.refresh()

    runtime.catalog = MethodType(guarded_catalog, runtime)
    runtime.refresh = MethodType(guarded_refresh, runtime)
    runtime._pass203_catalog_identity_guard = guard
    return guard
