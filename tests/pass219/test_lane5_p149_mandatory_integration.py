from __future__ import annotations

from pathlib import Path

import pytest

from hhs_runtime.pass219.lane5_mandatory_optimization_dispatcher import (
    Lane5MandatoryOptimizationError,
    MANDATORY_CAPABILITY_ROLES,
    MANDATORY_LANE5_LINEAGE,
    P149_CAPABILITY_ID,
    Pass219Lane5LatencyCompositionAgent,
)

ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT / "hhs_runtime" / "builds" / "libhhs_runtime.so"


def test_p149_is_mandatory_and_visible(tmp_path: Path) -> None:
    assert P149_CAPABILITY_ID in MANDATORY_LANE5_LINEAGE
    assert MANDATORY_CAPABILITY_ROLES[P149_CAPABILITY_ID] == (
        "EXACT_PYTHAGOREAN_PHASE_PROJECTION"
    )
    with Pass219Lane5LatencyCompositionAgent(state_root=tmp_path) as agent:
        status = agent.status()
    assert status["lane5_pythagorean_phase_geometry_1_49"] == (
        "LAZY_MANDATORY_NATIVE"
    )


@pytest.mark.parametrize(
    ("pair_kind", "orientation", "phase_slot", "cell", "admissible"),
    [
        ("AB", 0, 0, 0, True),
        ("XY", 1, 18, 2, True),
        ("ZW", 0, 54, 6, True),
        ("PQ", 1, 36, 8, True),
        ("PQ", 0, 0, 1, False),
    ],
)
def test_p149_callable_from_latency_agent(
    tmp_path: Path,
    pair_kind: str,
    orientation: int,
    phase_slot: int,
    cell: int,
    admissible: bool,
) -> None:
    assert LIBRARY.is_file(), f"native runtime required: {LIBRARY}"
    with Pass219Lane5LatencyCompositionAgent(state_root=tmp_path) as agent:
        result = agent.project_pythagorean_phase_geometry_1_49(
            pair_kind=pair_kind,
            orientation=orientation,
            phase_slot=phase_slot,
            lo_shu_cell_index=cell,
            fibonacci_depth=10,
            projected_p4=9,
            library_path=LIBRARY,
        )
    assert result["result"] == "PASS"
    assert result["optimization_selected"] == P149_CAPABILITY_ID
    assert result["mandatory_optimization_dispatch"] is True
    assert result["a2"] == 1
    assert result["b2"] == 2
    assert result["c2"] == 3
    assert result["c4"] == 9
    assert result["phase_involution_verified"] is True
    assert result["pair_involution_verified"] is True
    assert result["lo_shu_complement_verified"] is True
    assert result["collapse_candidate_admissible"] is admissible
    assert result["authority"]["candidate_only"] is True
    assert result["authority"]["canonical_vm81_mutation_authority"] is False
    assert result["authority"]["canonical_hash72_authority"] is False
    assert result["authority"]["canonical_hash216_authority"] is False
    assert result["authority"]["canonical_persistence_authority"] is False


def test_p149_projected_p4_mismatch_is_nonadmitted_not_authority_failure(
    tmp_path: Path,
) -> None:
    with Pass219Lane5LatencyCompositionAgent(state_root=tmp_path) as agent:
        result = agent.project_pythagorean_phase_geometry_1_49(
            pair_kind="PQ",
            orientation=0,
            phase_slot=0,
            lo_shu_cell_index=0,
            projected_p4=1,
            library_path=LIBRARY,
        )
    assert result["finite_phase_anchor_consistent"] is True
    assert result["shared_fourth_power_match"] is False
    assert result["collapse_candidate_admissible"] is False


def test_p149_invalid_phase_fails_closed(tmp_path: Path) -> None:
    with Pass219Lane5LatencyCompositionAgent(state_root=tmp_path) as agent:
        with pytest.raises(
            Lane5MandatoryOptimizationError,
            match="LANE5_P149_MANDATORY_PROJECTION_UNAVAILABLE",
        ):
            agent.project_pythagorean_phase_geometry_1_49(
                pair_kind="AB",
                orientation=0,
                phase_slot=1,
                lo_shu_cell_index=0,
                library_path=LIBRARY,
            )
