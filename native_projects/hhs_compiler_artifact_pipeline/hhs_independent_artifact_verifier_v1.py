"""Repository adapter for the zero-dependency package verifier."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
from typing import Any, Dict, Mapping

from .hhs_artifact_lineage_pipeline_v1 import package_bytes


def verifier_source() -> str:
    return (Path(__file__).resolve().parent / "verifier/verify_artifact.py").read_text(encoding="utf-8")


def _load_verifier():
    path = Path(__file__).resolve().parent / "verifier/verify_artifact.py"
    spec = importlib.util.spec_from_file_location("hhs_pass077_standalone_verifier", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def verify_package_object(package: Mapping[str, Any]) -> Dict[str, Any]:
    data = package_bytes(package)
    with tempfile.TemporaryDirectory(prefix="hhs-pass077-verifier-") as directory:
        path = Path(directory) / "artifact.hhspkg"
        path.write_bytes(data)
        return _load_verifier().verify_package(path)
