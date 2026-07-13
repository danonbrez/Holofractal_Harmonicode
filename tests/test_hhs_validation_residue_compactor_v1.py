from hhs_runtime.hhs_validation_residue_compactor_v1 import (
    compact_validation_residue,
    evict_expanded_metadata,
    summarize_compaction_gain,
    validation_residue_compactor_self_test,
    verify_residue_reconstruction,
)


def test_compactor_self_test_passes():
    assert validation_residue_compactor_self_test()["ok"] is True


def test_compacted_residue_has_recipe_and_no_payload():
    expanded = {"schema": "TEST_EXPANDED", "surfaces": [{"surface_id": "s"}], "edges": [1, 2, 3]}
    residue = evict_expanded_metadata(compact_validation_residue(expanded, source_id="test"))
    assert residue["reconstruction_recipe"]["schema"] == "HHS_RECONSTRUCTION_RECIPE_V1"
    assert residue["expanded_payload_retained"] is False
    assert residue["expanded_payload"] is None
    assert verify_residue_reconstruction(residue, expanded)["ok"] is True


def test_compaction_gain_report_is_bounded():
    expanded = {"schema": "TEST_EXPANDED", "surfaces": list(range(50)), "edges": list(range(100))}
    residue = evict_expanded_metadata(compact_validation_residue(expanded, source_id="test"))
    gain = summarize_compaction_gain(expanded, residue)
    assert gain["expanded_payload_persisted"] is False
    assert gain["compact_bytes"] > 0
