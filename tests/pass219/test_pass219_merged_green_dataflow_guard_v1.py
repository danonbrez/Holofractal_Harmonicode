from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GUARD_PATH = ROOT / "tools/pass219/pass219_merged_green_dataflow_guard_v1.py"
MANIFEST_PATH = ROOT / "contracts/pass219/PASS_219_MERGED_GREEN_DATAFLOW_NONREGRESSION_V1.json"

spec = importlib.util.spec_from_file_location("pass219_merged_green_guard", GUARD_PATH)
assert spec is not None and spec.loader is not None
guard = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = guard
spec.loader.exec_module(guard)

MANIFEST = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _invariants() -> dict[str, bool]:
    return {key: True for key in MANIFEST["mandatory_invariants"]}


def _proof(mode: str, merge_base: str, row: dict) -> dict:
    return {
        "schema": MANIFEST["proof_schema"],
        "mode": mode,
        "merge_base": merge_base,
        "defect_or_iteration": "test successor",
        "receipt_continuity": "preserved",
        "rollback_plan": "restore predecessor blob",
        "invariants": _invariants(),
        "validation_profiles": list(MANIFEST["mandatory_validation_profiles"]),
        "regression_tests": ["tests/pass219/test_pass219_merged_green_dataflow_guard_v1.py"],
        "negative_tests": ["tests/pass219/test_pass219_merged_green_dataflow_guard_v1.py"],
        "protected_changes": [row],
    }


def test_pass219_and_upstream_paths_are_protected() -> None:
    assert guard.is_protected_path(
        "hhs_runtime/c/hhs_pass219_example.inc", MANIFEST, status="M"
    )
    assert guard.is_protected_path(
        "tests/pass206/test_pass206_cumulative_enforcement_v1.py",
        MANIFEST,
        status="M",
    )
    assert guard.is_protected_path(
        "hhs_runtime/include/hhs_receipt.h", MANIFEST, status="M"
    )


def test_pass220_path_is_not_inherited_by_ceiling_alone() -> None:
    assert not guard.is_protected_path(
        "tests/pass220/test_new_pass220_surface.py", MANIFEST, status="M"
    )


def test_new_successor_proof_is_not_recursively_proof_gated() -> None:
    path = (
        "artifacts/pass219/merged_green_successor_proofs/"
        "EXAMPLE_SUCCESSOR_PROOF.json"
    )
    assert not guard.is_protected_path(path, MANIFEST, status="A")
    assert guard.is_protected_path(path, MANIFEST, status="M")
    assert guard.is_protected_path(path, MANIFEST, status="D")


def test_identifier_extraction_preserves_native_and_python_surface() -> None:
    native = """
    HHS_EXACT_API HHSExactStatus hhs_exact_demo(HHSExactThing *thing);
    #define HHS_EXACT_DEMO_VERSION 1
    """
    ids = guard.extract_identifiers(native, "demo.h")
    assert "hhs_exact_demo" in ids
    assert "HHSExactStatus" in ids
    assert "HHSExactThing" in ids
    assert "HHS_EXACT_DEMO_VERSION" in ids

    py = """
class StableSurface:
    pass

def stable_route():
    return 1
"""
    py_ids = guard.extract_identifiers(py, "demo.py")
    assert {"StableSurface", "stable_route"} <= py_ids


def test_backward_compatible_iteration_rejects_removed_identifier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = "hhs_runtime/include/hhs_pass219_demo.h"
    change = guard.Change(status="M", old_path=None, path=path)
    impacted = {path: change}

    monkeypatch.setattr(
        guard,
        "git_blob",
        lambda ref, p: "oldblob" if ref == "base" else "newblob",
    )
    monkeypatch.setattr(
        guard,
        "git_text",
        lambda ref, p: (
            "HHS_EXACT_API int hhs_exact_old_route(void);"
            if ref == "base"
            else "HHS_EXACT_API int hhs_exact_new_route(void);"
        ),
    )
    monkeypatch.setattr(guard, "git_path_exists", lambda ref, p: True)

    row = {
        "path": path,
        "change_status": "M",
        "predecessor_blob": "oldblob",
        "successor_blob": "newblob",
        "preserved_identifiers": [],
        "superseded_identifiers": [],
        "replacement_paths": [],
    }
    proof = _proof("BACKWARD_COMPATIBLE_ITERATION", "merge", row)

    errors, covered = guard.validate_proof_document(
        "proof.json",
        proof,
        actual_merge_base="merge",
        base="base",
        head="head",
        manifest=MANIFEST,
        impacted=impacted,
    )
    assert path in covered
    assert any("BACKWARD_COMPAT_REMOVED_IDENTIFIERS" in error for error in errors)


def test_repair_forward_requires_and_accepts_explicit_adapter_mapping(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = "hhs_runtime/include/hhs_pass219_demo.h"
    replacement_path = "hhs_runtime/include/hhs_pass219_demo_v2.h"
    change = guard.Change(status="D", old_path=None, path=path)
    impacted = {path: change}

    def fake_blob(ref: str, p: str) -> str | None:
        if ref == "base" and p == path:
            return "oldblob"
        if ref == "head" and p == path:
            return None
        if ref == "head" and p == replacement_path:
            return "replacementblob"
        if ref == "head" and p.startswith("tests/"):
            return "testblob"
        return None

    def fake_text(ref: str, p: str) -> str | None:
        if ref == "base" and p == path:
            return "HHS_EXACT_API int hhs_exact_old_route(void);"
        if ref == "head" and p == replacement_path:
            return (
                "HHS_EXACT_API int hhs_exact_new_route(void);\n"
                "HHS_EXACT_API int hhs_exact_old_route_compat_adapter(void);"
            )
        return None

    monkeypatch.setattr(guard, "git_blob", fake_blob)
    monkeypatch.setattr(guard, "git_text", fake_text)
    monkeypatch.setattr(guard, "git_path_exists", lambda ref, p: fake_blob(ref, p) is not None)

    row = {
        "path": path,
        "change_status": "D",
        "predecessor_blob": "oldblob",
        "successor_blob": "DELETED",
        "preserved_identifiers": [],
        "replacement_paths": [replacement_path],
        "superseded_identifiers": [
            {
                "identifier": "hhs_exact_old_route",
                "replacement_identifier": "hhs_exact_new_route",
                "compatibility_adapter": "hhs_exact_old_route_compat_adapter",
            }
        ],
    }
    proof = _proof("REPAIR_FORWARD_REFINEMENT", "merge", row)

    errors, covered = guard.validate_proof_document(
        "proof.json",
        proof,
        actual_merge_base="merge",
        base="base",
        head="head",
        manifest=MANIFEST,
        impacted=impacted,
    )
    assert path in covered
    assert errors == []


def test_proof_blob_mismatch_is_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    path = "hhs_runtime/c/hhs_pass219_demo.inc"
    change = guard.Change(status="M", old_path=None, path=path)
    impacted = {path: change}

    monkeypatch.setattr(
        guard,
        "git_blob",
        lambda ref, p: "actual-old" if ref == "base" else "actual-new",
    )
    monkeypatch.setattr(
        guard,
        "git_text",
        lambda ref, p: "int stable_identifier(void) { return 1; }",
    )
    monkeypatch.setattr(guard, "git_path_exists", lambda ref, p: True)

    row = {
        "path": path,
        "change_status": "M",
        "predecessor_blob": "wrong-old",
        "successor_blob": "wrong-new",
        "preserved_identifiers": [],
        "replacement_paths": [],
        "superseded_identifiers": [],
    }
    proof = _proof("BACKWARD_COMPATIBLE_ITERATION", "merge", row)

    errors, _ = guard.validate_proof_document(
        "proof.json",
        proof,
        actual_merge_base="merge",
        base="base",
        head="head",
        manifest=MANIFEST,
        impacted=impacted,
    )
    assert "proof.json:hhs_runtime/c/hhs_pass219_demo.inc:PREDECESSOR_BLOB_MISMATCH" in errors
    assert "proof.json:hhs_runtime/c/hhs_pass219_demo.inc:SUCCESSOR_BLOB_MISMATCH" in errors


def test_policy_manifest_cannot_weaken_protection() -> None:
    weaker = copy.deepcopy(MANIFEST)
    weaker["protected_pass_ceiling"] = 218
    weaker["sensitive_symbols"] = weaker["sensitive_symbols"][1:]
    errors = guard.manifest_monotonicity_errors(MANIFEST, weaker)
    assert "POLICY_PROTECTED_PASS_CEILING_DECREASED" in errors
    assert any(
        error.startswith("POLICY_MONOTONIC_SET_SHRANK:sensitive_symbols:")
        for error in errors
    )


def test_policy_manifest_may_only_strengthen_monotonically() -> None:
    stronger = copy.deepcopy(MANIFEST)
    stronger["protected_roots"] = list(stronger["protected_roots"]) + ["new_protected_root"]
    stronger["sensitive_symbols"] = list(stronger["sensitive_symbols"]) + [
        "hhs_exact_future_sensitive_surface"
    ]
    errors = guard.manifest_monotonicity_errors(MANIFEST, stronger)
    assert errors == []
