#!/usr/bin/env python3
"""Final Iteration 5 runtime classes with bounded SQLite lock waits."""
from __future__ import annotations

import os
import threading
import time
import uuid
from pathlib import Path
from typing import Callable

from hhs_pass190 import DEFAULT_REGISTRY, HHSAuthorityContext
from hhs_pass190_iteration2 import PersistentStoreError
from hhs_pass190_iteration3_hardening import DEFAULT_DATABASE
from hhs_pass190_iteration4 import DEFAULT_LEASE_TTL_NS, DEFAULT_LEASE_WAIT_NS
from hhs_pass190_iteration5 import CorrectedAuthorityContext, CorrectedAuthorityStore

SQLITE_LOCK_SLICE_MS = 25


class AtomicKernelAuthorityStore(CorrectedAuthorityStore):
    """Corrected store whose SQLite calls cannot hide a one-second lock wait."""

    def __init__(
        self,
        path: Path | str,
        *,
        clock_ns: Callable[[], int] = time.time_ns,
        sleeper: Callable[[float], None] = time.sleep,
    ):
        super().__init__(path, clock_ns=clock_ns, sleeper=sleeper)
        self._connection.execute(f"PRAGMA busy_timeout={SQLITE_LOCK_SLICE_MS}")


class AtomicKernelAuthorityContext(CorrectedAuthorityContext):
    """Production Iteration 5 context using bounded lock slices."""

    def __init__(
        self,
        database_path: Path | str = DEFAULT_DATABASE,
        registry_path: Path = DEFAULT_REGISTRY,
        *,
        holder_id: str | None = None,
        lease_ttl_ns: int = DEFAULT_LEASE_TTL_NS,
        lease_wait_ns: int = DEFAULT_LEASE_WAIT_NS,
        clock_ns: Callable[[], int] = time.time_ns,
        sleeper: Callable[[float], None] = time.sleep,
    ):
        self.holder_id = holder_id or f"{os.getpid()}:{uuid.uuid4().hex}"
        self.lease_ttl_ns = lease_ttl_ns
        self.lease_wait_ns = lease_wait_ns
        self.store = AtomicKernelAuthorityStore(database_path, clock_ns=clock_ns, sleeper=sleeper)
        HHSAuthorityContext.__init__(self, registry_path)
        self.store.restore_into(self)


_CONTEXT: AtomicKernelAuthorityContext | None = None
_CONTEXT_LOCK = threading.Lock()
_CONTEXT_PATH: Path | None = None


def get_iteration5_runtime(database_path: Path | str | None = None) -> AtomicKernelAuthorityContext:
    global _CONTEXT, _CONTEXT_PATH
    requested = Path(database_path or DEFAULT_DATABASE)
    if _CONTEXT is None:
        with _CONTEXT_LOCK:
            if _CONTEXT is None:
                _CONTEXT = AtomicKernelAuthorityContext(requested)
                _CONTEXT_PATH = requested
    elif _CONTEXT_PATH != requested:
        raise PersistentStoreError("process authority context already bound to another database")
    return _CONTEXT
