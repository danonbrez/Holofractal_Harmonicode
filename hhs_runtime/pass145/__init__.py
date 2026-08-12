"""HHS Pass 145 Android/local knowledge platform.

The package is a thin governed orchestration layer over inherited HHS source,
claim, Hash72, receipt, and runtime components. It deliberately keeps source
evidence, parser output, interpretations, and canonical transactions separate.

Package exports are resolved lazily so importing a focused storage submodule does
not activate the full document-ingestion/service ancestry or predictive
continuation machinery. Public import compatibility is preserved.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .errors import Pass145Error

if TYPE_CHECKING:
    from .database import HHS145Database as HHS145Database
    from .service import HHS145Service as HHS145Service

__all__ = ["HHS145Service", "HHS145Database", "Pass145Error"]


def __getattr__(name: str) -> Any:
    if name == "HHS145Database":
        from .database import HHS145Database

        return HHS145Database
    if name == "HHS145Service":
        from .service import HHS145Service

        return HHS145Service
    if name == "Pass145Error":
        return Pass145Error
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
