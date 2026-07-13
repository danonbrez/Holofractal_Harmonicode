from __future__ import annotations

from pathlib import Path
import json
import shutil

import pytest

from native_projects.pass073_deterministic_transform import (
    FROZEN_PASS072_SYSTEM_ROOT_HASH72,
    Hash72Surface,
    native_transform_self_test,
    replay_native_transform,
    resume_project_from_capsule,
    run_native_transform_product,
    verify_development_capsule,
)
from native_projects.pass073_deterministic_transform.hhs_native_deterministic_transform_v1 import (
    ArtifactIntegrityError,
    CANONICAL_INPUT_MANIFEST_RELATIVE_PATH,
    _normalize_bits,
)


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_FILES = (
    "PASS_072_TOTAL_SYSTEM_ROOT.json",
    "UNIVERSAL_BINARY_TRINARY_TRANSLATION_PASS_070.json",
    "BINARY_TRINARY_ROUND_TRIP_PASS_070.json",
    "ZERO_SUM_SWITCHING_CLOSURE_PASS_070.json",
    "THREE_LANE_81_CELL_QUDIT_KERNEL_PASS_068.json",
)
SOURCE_FILES = (
    "native_projects/pass073_deterministic_transform/__init__.py",
    "native_projects/pass073_deterministic_transform/hhs_native_deterministic_transform_v1.py",
    "native_projects/pass073_deterministic_transform/hhs_context_independent_project_runner_v1.py",
    "tests/test_hhs_pass073_native_deterministic_transform_v1.py",
    CANONICAL_INPUT_MANIFEST_RELATIVE_PATH,
)


def _minimal_repo(destination: Path) -> Path:
    for relative in (*CANONICAL_FILES, *SOURCE_FILES):
        source = ROOT / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return destination


def test_pass073_treats_pass072_root_as_immutable_dependency():
    result = run_native_transform_product(resolution_mode="COMMITTED_ARTIFACT")
    baseline = result["alpha_release_baseline"]
    assert baseline["canonical_pass"] == "PASS_072"
    assert baseline["foundation_frozen"] is True
    assert baseline["total_system_root_hash72"] == FROZEN_PASS072_SYSTEM_ROOT_HASH72
    assert baseline["system_root_matches_frozen_release"] is True
    assert baseline["ordinary_workload_may_mutate_foundation"] is False


def test_project_product_execution_roots_are_distinct_from_system_root():
    result = run_native_transform_product(resolution_mode="COMMITTED_ARTIFACT")
    system_root = result["alpha_release_baseline"]["total_system_root_hash72"]
    release = result["product_release_manifest"]
    assert result["project"]["project_root_hash72"] != system_root
    assert result["product_artifact"]["product_artifact_root_hash72"] != system_root
    assert result["execution_receipt"]["execution_root_hash72"] != system_root
    assert result["product_artifact"]["product_artifact_root_hash72"] != result["execution_receipt"]["execution_root_hash72"]
    assert all(release["root_distinctions"].values())


def test_native_product_generates_authenticated_pass068_bound_artifact():
    result = run_native_transform_product(
        {"sequence": "1011001110001111", "width": 16},
        resolution_mode="COMMITTED_ARTIFACT",
    )
    artifact = result["product_artifact"]
    derived = artifact["derived_artifact"]
    assert artifact["schema"] == "HHS_PROJECT_SOURCE_ARTIFACT_V2"
    assert derived["canonical_bits"] == "1011001110001111"
    assert len(derived["trinary_lane_vector"]) == 8
    assert len(derived["lo_shu_schedule"]) == 8
    assert derived["round_trip_valid"] is True
    assert derived["zero_sum_closed"] is True
    assert artifact["lo_shu_schedule"]["pass068_kernel_explicitly_consumed"] is True
    assert artifact["pass068_kernel_binding"]["cell_count"] == 81
    assert artifact["pass068_kernel_binding"]["subgrid_count"] == 9
    assert artifact["pass068_kernel_binding"]["lo_shu_cycle"] == [8, 1, 6, 3, 5, 7, 4, 9, 2]


def test_native_test_plan_covers_strict_input_reconstruction_and_kernel_binding():
    result = run_native_transform_product(resolution_mode="COMMITTED_ARTIFACT")
    test_plan = result["test_plan"]
    cases = {item["case"] for item in test_plan["tests"]}
    assert {
        "positive_round_trip",
        "negative_invalid_width_rejected",
        "negative_non_binary_rejected",
        "negative_whitespace_rejected",
        "reconstruction_case",
        "pass068_kernel_binding",
    } <= cases
    assert test_plan["all_tests_passed"] is True


def test_same_mode_replay_reproduces_same_product_root():
    result = run_native_transform_product(resolution_mode="COMMITTED_ARTIFACT")
    replay = replay_native_transform(result, resolution_mode="COMMITTED_ARTIFACT")
    assert replay["product_root_matches"] is True
    assert replay["reconstruction_verified"] is True
    assert replay["replayed_product_root_hash72"] == result["product_artifact"]["product_artifact_root_hash72"]


def test_cross_mode_semantic_product_root_is_stable():
    fallback = run_native_transform_product(resolution_mode="COMMITTED_ARTIFACT")
    automatic = run_native_transform_product(resolution_mode="AUTO")
    assert fallback["product_artifact"]["product_artifact_root_hash72"] == automatic["product_artifact"]["product_artifact_root_hash72"]
    replay = replay_native_transform(fallback, resolution_mode="AUTO")
    assert replay["product_root_matches"] is True
    assert replay["cross_mode_semantic_replay_supported"] is True


def test_mode_specific_execution_envelope_is_not_product_identity():
    fallback = run_native_transform_product(resolution_mode="COMMITTED_ARTIFACT")
    automatic = run_native_transform_product(resolution_mode="AUTO")
    assert fallback["product_artifact"]["product_artifact_root_hash72"] == automatic["product_artifact"]["product_artifact_root_hash72"]
    if automatic["execution_environment"]["execution_mode"] == "LIVE_RUNTIME":
        assert fallback["execution_receipt"]["execution_root_hash72"] != automatic["execution_receipt"]["execution_root_hash72"]


def test_pass073_does_not_add_foundational_services_surfaces_or_authority():
    result = run_native_transform_product(resolution_mode="COMMITTED_ARTIFACT")
    release = result["product_release_manifest"]
    assert release["foundation_delta"] == {"services": 0, "surfaces": 0, "authority": 0}
    assert release["product_verified"] is True
    assert release["deterministic_replay"] is True


def test_native_transform_self_test_reports_context_independent_ok():
    result = native_transform_self_test(resolution_mode="COMMITTED_ARTIFACT")
    assert result["ok"] is True
    assert result["deterministic_replay"] is True
    assert result["portable_cross_mode_semantic_replay"] is True
    assert result["foundation_delta"] == {"services": 0, "surfaces": 0, "authority": 0}
    assert result["thread_context_required"] is False


def test_recorded_witness_identity_never_changes_with_live_verification():
    fallback_witness = Hash72Surface(resolution_mode="COMMITTED_ARTIFACT").resolve_witness("01").to_dict()
    auto_witness = Hash72Surface(resolution_mode="AUTO").resolve_witness("01").to_dict()
    assert fallback_witness == auto_witness
    assert fallback_witness["witness_source"] == "COMMITTED_CANONICAL_ARTIFACT"
    assert fallback_witness["recorded_witness_not_new_kernel_witness"] is True
    assert fallback_witness["execution_mode_does_not_reclassify_witness"] is True


def test_fallback_artifact_tampering_is_rejected(tmp_path: Path):
    repo = _minimal_repo(tmp_path / "tampered")
    path = repo / "BINARY_TRINARY_ROUND_TRIP_PASS_070.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["pair_records"][3]["state"]["translation_root_hash72"] = "TAMPERED_TRANSLATION_ROOT"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(ArtifactIntegrityError, match="DIGEST_MISMATCH"):
        Hash72Surface(repo, resolution_mode="COMMITTED_ARTIFACT")


def test_manifest_tampering_is_rejected(tmp_path: Path):
    repo = _minimal_repo(tmp_path / "manifest-tampered")
    path = repo / CANONICAL_INPUT_MANIFEST_RELATIVE_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["foundation_mutation_allowed"] = True
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(ArtifactIntegrityError, match="MANIFEST_DIGEST_MISMATCH"):
        Hash72Surface(repo, resolution_mode="COMMITTED_ARTIFACT")


def test_canonical_roots_are_independent_of_extraction_path(tmp_path: Path):
    repo_a = _minimal_repo(tmp_path / "a")
    repo_b = _minimal_repo(tmp_path / "different" / "nested" / "b")
    a = run_native_transform_product(root=repo_a, resolution_mode="COMMITTED_ARTIFACT")
    b = run_native_transform_product(root=repo_b, resolution_mode="COMMITTED_ARTIFACT")
    assert a["alpha_release_baseline"]["system_baseline_root_hash72"] == b["alpha_release_baseline"]["system_baseline_root_hash72"]
    assert a["requirement"]["requirement_root_hash72"] == b["requirement"]["requirement_root_hash72"]
    assert a["specification"]["specification_root_hash72"] == b["specification"]["specification_root_hash72"]
    assert a["plan"]["plan_root_hash72"] == b["plan"]["plan_root_hash72"]
    assert a["project"]["project_root_hash72"] == b["project"]["project_root_hash72"]
    assert a["product_artifact"]["product_artifact_root_hash72"] == b["product_artifact"]["product_artifact_root_hash72"]


def test_strict_binary_input_rejects_lossy_normalization():
    for sequence in ("10abc01", "10-01", "10 01", " 1001", "1001\n"):
        with pytest.raises(ValueError, match="REJECT_UNDECLARED_NON_BINARY_CHARACTERS"):
            _normalize_bits(sequence, 8)
    receipt = _normalize_bits("1001", 8)
    assert receipt["canonical_bits"] == "00001001"
    assert receipt["normalization_operation"] == "LEFT_ZERO_PAD_TO_DECLARED_WIDTH"
    assert receipt["undeclared_characters_removed"] is False
    assert receipt["source_identity_preserved"] is True


def test_runtime_probe_is_read_only_and_does_not_auto_build(tmp_path: Path):
    repo = _minimal_repo(tmp_path / "no-runtime")
    build_dir = repo / "hhs_runtime" / "builds"
    assert not build_dir.exists()
    surface = Hash72Surface(repo, resolution_mode="AUTO")
    assert surface.mode == "COMMITTED_ARTIFACT"
    assert not build_dir.exists()
    capabilities = surface.capabilities().to_dict()
    assert capabilities["implicit_build_authorized"] is False
    assert capabilities["foundation_modified"] is False


def test_compiler_capability_is_observed_not_hardcoded():
    capabilities = Hash72Surface(resolution_mode="COMMITTED_ARTIFACT").capabilities().to_dict()
    observed = bool(capabilities["compiler_observation"]["cc"])
    assert capabilities["compiler_available"] is observed


def test_canonical_state_contains_no_absolute_paths():
    state = Hash72Surface(resolution_mode="COMMITTED_ARTIFACT").load_canonical_state().to_dict()
    rendered = json.dumps(state, sort_keys=True)
    assert str(ROOT) not in rendered
    assert state["host_path_committed"] is False
    assert all(not Path(binding["relative_path"]).is_absolute() for binding in state["artifact_bindings"].values())


def test_context_independent_development_capsule_is_restart_safe():
    bundle = run_native_transform_product(resolution_mode="COMMITTED_ARTIFACT")
    capsule = bundle["context_independent_development_capsule"]
    assert capsule["restart_safe"] is True
    assert capsule["thread_context_required"] is False
    assert capsule["llm_context_window_required"] is False
    assert capsule["host_path_required"] is False
    assert capsule["repository_state_is_authoritative"] is True
    assert len(capsule["source_bindings"]) == 5
    assert all(not Path(item["relative_path"]).is_absolute() for item in capsule["source_bindings"])


def test_hash72_surface_declares_authenticated_fallback_without_minting_authority():
    surface = Hash72Surface(resolution_mode="COMMITTED_ARTIFACT")
    capabilities = surface.capabilities().to_dict()
    verification = surface.verify_committed_root().to_dict()
    witness = surface.resolve_witness("01").to_dict()
    assert capabilities["hash72_surface_mode"] == "COMMITTED_ARTIFACT"
    assert capabilities["live_c_runtime_available"] is False
    assert capabilities["canonical_artifact_access"] is True
    assert capabilities["committed_artifact_integrity_verified"] is True
    assert capabilities["new_kernel_witness_generation"] is False
    assert capabilities["status"] == "ADMIT_CONSTRAINED_NATIVE_WORKLOAD_FROM_AUTHENTICATED_ARTIFACTS"
    assert capabilities["context_window_required"] is False
    assert verification["committed_root_verified"] is True
    assert verification["artifact_integrity_verified"] is True
    assert witness["recorded_witness_not_new_kernel_witness"] is True


def test_context_independent_runner_verifies_and_resumes_without_conversation():
    run_native_transform_product(write_artifacts=True, resolution_mode="COMMITTED_ARTIFACT")
    verification = verify_development_capsule()
    assert verification["ok"] is True
    assert verification["thread_context_required"] is False
    receipt = resume_project_from_capsule(resolution_mode="AUTO")
    assert receipt["ok"] is True
    assert receipt["product_root_matches"] is True
    assert receipt["thread_context_used"] is False
    assert receipt["host_path_used_as_identity"] is False
    assert receipt["foundation_delta"] == {"services": 0, "surfaces": 0, "authority": 0}
