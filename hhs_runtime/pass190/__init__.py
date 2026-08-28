"""Pass 190 full-contract completion coordinator.

This package is additive. It reuses the historical Pass 190 Iteration-7
durable authority and the frozen I135 repository hydration runtime instead of
creating another VM81, operation engine, receipt clock, or persistence owner.
"""

from .completion import (
    COMPLETION_CLASSIFICATION,
    CONTRACT_AUTHORIZATION_COMMIT,
    CONTRACT_ID,
    FROZEN_I135,
    Pass190CompletionContext,
)
from .python_compat import (
    PYTHON_COMPAT_SCHEMA,
    PYTHON_COMPAT_VERSION,
    build_python_compatibility_registry,
)

__all__ = [
    "COMPLETION_CLASSIFICATION",
    "CONTRACT_AUTHORIZATION_COMMIT",
    "CONTRACT_ID",
    "FROZEN_I135",
    "Pass190CompletionContext",
    "PYTHON_COMPAT_SCHEMA",
    "PYTHON_COMPAT_VERSION",
    "build_python_compatibility_registry",
]
