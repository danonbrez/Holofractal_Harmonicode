"""V163 course crosswalk preserves both immutable identities and fail-closed admission."""
from __future__ import annotations

import pytest

from hhs_runtime.hhs_pass220_v163_course_module_crosswalk_v1 import (
    V163CourseCrosswalkError, _sections, FROZEN_HEADER,
    CURRENT_HEADER, inspect_crosswalk, require_frozen_equivalence,
)


def test_crosswalk_reconciles_indices_without_equivalence_claim():
    report = inspect_crosswalk()
    assert report["frozen_git_blob_sha"] == "2744e9ecf1f260ff9a5a02870320698ee2d7dcaf"
    assert report["current_git_blob_sha"] == "968735b21bb0fda42f9c944ae6987099e624e7a7"
    assert report["frozen_module_count"] == 13
    assert report["current_numbered_module_count"] >= 15
    assert len(report["overlap"]) == 13
    assert [row["module_index"] for row in report["overlap"]] == list(range(13))
    assert all(row["index_correspondence_only"] for row in report["overlap"])
    assert all(row["typed_equivalence_verified"] is False for row in report["overlap"])
    assert all(row["native_proof_executed"] is False for row in report["overlap"])
    assert report["source_integrity_gate_satisfied"] is False
    assert report["course_equivalence_verified"] is False
    assert report["vm81_admission_authority"] is False
    assert report["hash72_hash216_minted"] is False


def test_crosswalk_cannot_promote_by_matching_indices():
    with pytest.raises(V163CourseCrosswalkError, match="TYPED_EQUIVALENCE_WITNESS_REQUIRED"):
        require_frozen_equivalence()


def test_duplicate_module_indices_fail_closed():
    with pytest.raises(V163CourseCrosswalkError, match="DUPLICATE_MODULE_INDEX"):
        _sections(b"MODULE 0 \xe2\x80\x94 First\nMODULE 0 \xe2\x80\x94 Second\n", FROZEN_HEADER)
    with pytest.raises(V163CourseCrosswalkError, match="DUPLICATE_MODULE_INDEX"):
        _sections(b"# Module 0 \xe2\x80\x94 First\n# Module 0 \xe2\x80\x94 Second\n", CURRENT_HEADER)
