"""
HHS Dependency Audit v1
======================

Ensures required data and runtime files exist before execution proceeds.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from hhs_runtime.hhs_repo_paths_v1 import repo_root


REQUIRED_PATHS = [
    "data",
    "data/runtime",
    "hhs_runtime",
]


def run_dependency_audit() -> Dict[str, Any]:
    root = repo_root()
    missing: List[str] = []
    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            missing.append(rel)
    return {
        "status": "DEPENDENCIES_OK" if not missing else "DEPENDENCIES_MISSING",
        "ok": not missing,
        "missing": missing,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_dependency_audit(), indent=2))
