"""Pass 105.3 native-project ownership and consumer closure.

This registry does not hide executable modules. It binds generated artifacts,
schemas, contracts, build tools, verifier tools, and UI assets to concrete
native implementations and production/test consumers.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Optional
import importlib

PROJECTS = {
 "native_projects/pass073_deterministic_transform/": {
  "owner_module":"native_projects.pass073_deterministic_transform.hhs_native_deterministic_transform_v1",
  "owner_test":"tests/test_hhs_pass073_native_deterministic_transform_v1.py"},
 "native_projects/hhs_ide_workspace/": {
  "owner_module":"native_projects.hhs_ide_workspace.hhs_native_workspace_project_v1",
  "owner_test":"tests/test_hhs_pass074_unified_ide_workspace_v1.py"},
 "native_projects/hhs_harmonicode_language/": {
  "owner_module":"native_projects.hhs_harmonicode_language.hhs_harmonicode_language_service_v1",
  "owner_test":"tests/test_hhs_pass075_harmonicode_language_service_v1.py"},
 "native_projects/hhs_harmonicode_interpreter/": {
  "owner_module":"native_projects.hhs_harmonicode_interpreter.hhs_exact_symbolic_interpreter_v1",
  "owner_test":"tests/test_hhs_pass076_interpreter_and_bounded_repair_v1.py"},
 "native_projects/hhs_compiler_artifact_pipeline/": {
  "owner_module":"native_projects.hhs_compiler_artifact_pipeline.hhs_pass077_workspace_runtime_v1",
  "owner_test":"tests/test_hhs_pass077_compiler_artifact_pipeline_v1.py"},
 "native_projects/hhs_vm81_native_exposure/": {
  "owner_module":"native_projects.hhs_vm81_native_exposure.hhs_pass078_vm81_native_exposure_v1",
  "owner_test":"tests/test_hhs_pass078_vm81_native_exposure_v1.py"},
 "native_projects/hhs_exact_recursive_symbolic_runtime/": {
  "owner_module":"native_projects.hhs_exact_recursive_symbolic_runtime.hhs_pass081_runtime_v1",
  "owner_service":"symbolic.pass081.execute",
  "owner_test":"tests/test_hhs_pass081_runtime_v1.py"},
 "native_projects/hhs_bifurcation_calibration/": {
  "owner_module":"native_projects.hhs_bifurcation_calibration.hhs_pass082_bifurcation_benchmark_v1",
  "owner_service":"calibration.pass082.bifurcation",
  "owner_test":"tests/test_hhs_pass082_bifurcation_benchmark_v1.py"},
}

def ownership_for(rel: str) -> Optional[Dict[str, Any]]:
    for prefix, owner in PROJECTS.items():
        if rel.startswith(prefix):
            suffix = rel[len(prefix):]
            if "/artifacts/" in "/"+suffix or suffix.startswith(("artifacts/","contracts/","schemas/","rejections/")):
                kind="OWNED_ARTIFACT"
            elif suffix.startswith("workspace_ui/"):
                kind="GUI_REACHABLE"
            elif Path(rel).name.startswith("build_pass") and rel.endswith(".py"):
                kind="BUILD_REACHABLE"
            elif "/verifier/" in "/"+suffix or suffix.startswith("verifier/"):
                kind="TOOL_REACHABLE"
            else:
                return None
            return {**owner,"status":kind,"project_prefix":prefix}
    return None

def validate_ownership(root: Path, rel: str, owner: Dict[str, Any]) -> Dict[str, Any]:
    module = importlib.import_module(owner["owner_module"])
    test_path = root / owner["owner_test"]
    if not test_path.is_file():
        raise RuntimeError(f"missing owner test for {rel}: {owner['owner_test']}")
    return {"owner_module_imported": module is not None, "owner_test_exists": True}
