from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from hhs_backend.runtime.hhs_pass214_cumulative_operation_census_v1 import (
    BASE20_HEADER,
    FROZEN_RUNTIME,
    FROZEN_RUNTIME_GIT_BLOB,
)
from hhs_backend.runtime.hhs_pass214_cumulative_operation_census_final_v1 import (
    build_final_cumulative_operation_census,
    load_and_validate_final_census,
    write_final_census,
)

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def _result():
    return build_final_cumulative_operation_census(ROOT, source_ref="HEAD")


def test_known_opcode_families_are_all_recovered() -> None:
    result = _result()
    anchors = result["summary"]["known_opcode_family_anchors"]
    assert anchors["all_satisfied"] is True
    assert anchors["observed"] == {
        "VM81_SUBSTRATE_OPCODE": 24,
        "FROZEN_HHS_IR_OPCODE": 20,
        "PASS079_NATIVE_ABI_OPCODE": 29,
        "PASS158_LLABI_NFTC_OPCODE": 36,
        "PASS213_GOVERNED_NATIVE_DISPATCH": 9,
        "VM81_BASE20_NUMERICAL_ABI": 19,
    }
    assert anchors["raw_known_opcode_identity_minimum"] == 137


def test_numerical_abi_is_preserved_as_distinct_exact_projection_family() -> None:
    result = _result()
    numerical = [row for row in result["operations"] if row["family"] == "VM81_BASE20_NUMERICAL_ABI"]
    assert len(numerical) == 19
    assert {row["codepoint"] for row in numerical} == set(range(19))
    assert all(row["path"] == BASE20_HEADER for row in numerical)
    assert all(row["semantic_equivalence"] == "EXACT_PROJECTION_BY_NATIVE_REGISTRY" for row in numerical)
    assert all(str(row["exact_projection"]).startswith("VM81_SUBSTRATE:") for row in numerical)


def test_census_is_repository_wide_and_does_not_auto_collapse_semantics() -> None:
    result = _result()
    summary = result["summary"]
    assert summary["coverage"]["raw_operation_identities"] > 137
    assert summary["coverage"]["components_with_operations"] > 10
    assert summary["coverage"]["pre_pass_or_unnumbered_operations"] > 0
    assert summary["coverage"]["numbered_pass_operations"] > 0
    assert summary["semantic_accounting"]["automatic_semantic_collapse_performed"] is False
    assert summary["semantic_accounting"]["canonical_unique_semantic_operation_count"] is None
    assert result["policy"]["applications_and_native_projects_are_scanned_for_isolated_capabilities"] is True
    assert result["policy"]["name_similarity_never_proves_semantic_equivalence"] is True


def test_deep_language_and_projection_coverage_is_present() -> None:
    result = _result()
    summary = result["summary"]
    manifest = summary["language_coverage_manifest"]
    assert result["policy"]["public_abi_declarations_counted_as_projection_surfaces"] is True
    assert result["policy"]["formal_proof_declarations_separated_from_executable_operations"] is True
    assert result["policy"]["build_tasks_separated_from_runtime_semantics"] is True
    assert "C_HEADER_DECLARATION" in manifest["extractors_used"]
    assert "MAKE" in manifest["extractors_used"]
    assert summary["reuse_accounting"]["abi_declaration_surfaces"] > 0
    for extension in (".rs", ".java", ".lean", ".v"):
        if manifest["tracked_extension_or_special_file_counts"].get(extension, 0):
            assert manifest["supplemental_extractor_file_counts"].get(extension, 0) > 0


def test_python_registry_accounting_is_structural_not_string_sweep() -> None:
    result = _result()
    quality = result["summary"]["quality_controls"]
    manifest = result["summary"]["language_coverage_manifest"]["python_operation_registry"]
    assert quality["broad_python_registry_string_heuristic_removed"] is True
    assert quality["discarded_broad_registry_string_records"] > 0
    assert quality["replacement_python_operation_registry_keys"] > 0
    assert manifest["policy"] == "STRUCTURAL_KEYS_ONLY_STRICT_OPERATION_REGISTRY_NAMES"
    assert not any(row["kind"] == "PYTHON_REGISTRY_ENTRY" for row in result["operations"])


def test_reuse_and_python_exposure_are_accounted() -> None:
    result = _result()
    summary = result["summary"]
    assert summary["reuse_accounting"]["shared_module_records"] > 0
    assert summary["reuse_accounting"]["isolated_implementation_candidates"] > 0
    assert "hhs_runtime_init" in summary["ctypes_bound_native_symbols"]
    assert summary["python_exposure_counts"]["GOVERNED_NATIVE_DISPATCH"] == 9
    assert summary["python_exposure_counts"]["CTYPES_DIRECT_ABI"] > 0


def test_frozen_runtime_blob_is_unchanged() -> None:
    result = _result()
    frozen = result["summary"]["frozen_runtime"]
    assert frozen["path"] == FROZEN_RUNTIME
    assert frozen["git_blob"] == FROZEN_RUNTIME_GIT_BLOB
    assert frozen["preserved"] is True
    assert result["policy"]["runtime_mutation_performed"] is False
    assert result["policy"]["frozen_runtime_modified"] is False


def test_census_receipt_roundtrip(tmp_path: Path) -> None:
    result = _result()
    output = tmp_path / "census.json"
    write_final_census(result, output)
    loaded = load_and_validate_final_census(output)
    assert loaded["census_sha256"] == result["census_sha256"]
    assert loaded["summary"] == result["summary"]
