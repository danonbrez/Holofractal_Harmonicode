"""V162 source-divergence diagnosis never bypasses frozen corpus admission."""
from __future__ import annotations

import pytest

from hhs_runtime.hhs_pass220_v162_course_source_divergence_v1 import (
    V162CourseSourceError, inspect_divergence, require_frozen_identity,
)


def test_reports_frozen_and_current_git_object_without_mutation():
    info = inspect_divergence()
    assert info["frozen_git_blob_sha"] == "2744e9ecf1f260ff9a5a02870320698ee2d7dcaf"
    assert info["working_git_blob_sha"] == "968735b21bb0fda42f9c944ae6987099e624e7a7"
    assert info["working_tree_matches_head"] is True
    assert info["freeze_matches_head"] is False
    assert info["source_integrity_gate_satisfied"] is False
    assert info["frozen_bytes"] < info["working_bytes"]
    assert info["native_admission_authority"] is False
    assert info["hash72_hash216_minted"] is False


def test_source_freeze_still_rejects_committed_divergence():
    with pytest.raises(V162CourseSourceError, match="V162_COURSE_FREEZE_DIVERGENCE"):
        require_frozen_identity()
