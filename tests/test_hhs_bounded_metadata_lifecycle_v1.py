from hhs_runtime.hhs_bounded_metadata_lifecycle_v1 import (
    bounded_metadata_lifecycle_self_test,
    transition_expanded_to_validated,
    transition_validated_to_compacted,
    persist_compact_root,
    validate_metadata_lifecycle,
)


def test_bounded_metadata_lifecycle_self_test_passes():
    assert bounded_metadata_lifecycle_self_test()["ok"] is True


def test_persistence_stores_root_not_expanded_payload():
    expanded = {"schema": "EXPANDED", "edges": list(range(10))}
    validated = transition_expanded_to_validated(expanded, expanded_state_id="x", source_surface_id="s", tick=1, decay_window_ticks=2)
    compacted = transition_validated_to_compacted(validated, expanded)
    persisted = persist_compact_root(compacted)
    assert persisted["expanded_payload_retained"] is False
    assert validate_metadata_lifecycle(persisted)["ok"] is True
