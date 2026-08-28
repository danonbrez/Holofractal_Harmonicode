from __future__ import annotations

import json
from pathlib import Path

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_integrated_manifold_engine_v2 import (
    verify_integrated_manifold_search,
)

ROOT = Path(__file__).resolve().parents[2]
PASS191_DIR = (
    ROOT
    / "native_projects"
    / "hhs_pass191_dyadic_quartic_phase_lattice"
    / "evidence"
)
PASS191_EVIDENCE = PASS191_DIR / "PASS_191_INTEGRATED_PROOF_SEARCH.json"
PASS191_COMPLETION = PASS191_DIR / "PASS_191_INTEGRATED_COMPLETION_RECEIPT.json"

EXPECTED_HYDRATION_CHECK_KEYS = {
    "permanent_instruction_fabric_5184",
    "projected_address_space_1259712",
    "cold_hydration_sealed_through_vm81",
    "frontier_candidate_batch_committed",
    "all_frontier_candidates_committed",
    "all_candidates_have_hash216",
    "singleton_vm81_authority",
    "deterministic_replay_verified",
    "reciprocal_order_retained",
    "hash72_single_commit_stream",
}


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_inherited_hydration_requires_complete_named_check_set() -> None:
    payload = _load(PASS191_EVIDENCE)
    hydration = payload["vm81_hash216_frontier_hydration"]
    checks = hydration["checks"]

    assert set(checks) == EXPECTED_HYDRATION_CHECK_KEYS
    assert all(checks[key] is True for key in EXPECTED_HYDRATION_CHECK_KEYS)


def test_inherited_completion_receipt_hash72_continuity_is_closed() -> None:
    integrated = _load(PASS191_EVIDENCE)
    completion = _load(PASS191_COMPLETION)

    verified = verify_integrated_manifold_search(integrated)
    assert verified["ok"] is True

    completion_core = {
        key: value
        for key, value in completion.items()
        if key != "completion_hash72"
    }
    expected_completion_hash72 = hash72_digest(
        {"domain": "HHS-PASS-191-UNIFIED-MANIFOLD-COMPLETION-V2"},
        completion_core,
    )

    assert completion["completion_hash72"] == expected_completion_hash72
    assert (
        completion["integrated_manifold_search_hash72"]
        == integrated["integrated_manifold_search_hash72"]
    )
    assert (
        completion["manifold_epoch_hash72"]
        == integrated["unified_manifold_epoch"]["manifold_epoch_hash72"]
    )
