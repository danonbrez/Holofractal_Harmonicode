from __future__ import annotations

from pathlib import Path

import pytest

from hhs_runtime.pass219.lane5_mandatory_optimization_dispatcher import (
    Lane5MandatoryOptimizationError,
    Pass219Lane5LatencyCompositionAgent,
    RML20_CAPABILITY_ID,
)

ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT / "hhs_runtime" / "builds" / "libhhs_runtime.so"


def _raw_frame() -> bytes:
    return bytes(((index * 131 + 17) & 0xFF) for index in range(648))


def test_rml20_is_mandatory_and_visible(tmp_path: Path) -> None:
    with Pass219Lane5LatencyCompositionAgent(state_root=tmp_path) as agent:
        status = agent.status()
        assert RML20_CAPABILITY_ID in status["mandatory_lineage"]
        assert status["mandatory_capability_roles"][RML20_CAPABILITY_ID] == (
            "EXACT_RML17_RNA_VM5184_TRANSPORT"
        )
        assert status["rml20_rna_vm5184_transport"] == "LAZY_MANDATORY"


def test_rml20_is_callable_through_production_agent(tmp_path: Path) -> None:
    assert LIBRARY.is_file(), f"native runtime required: {LIBRARY}"
    with Pass219Lane5LatencyCompositionAgent(state_root=tmp_path) as agent:
        result = agent.route_rml20_candidate(
            _raw_frame(),
            373247,
            "operation_forward",
            library_path=LIBRARY,
        )
    assert result["result"] == "PASS"
    assert result["mandatory_optimization_dispatch"] is True
    assert result["optimization_selected"] == RML20_CAPABILITY_ID
    assert result["fresh_recomputation_forced"] is False
    assert all(result["parity"].values())
    assert result["authority"]["candidate_only"] is True
    assert result["authority"]["exact_integer_only"] is True
    assert result["authority"]["canonical_vm81_mutation_authority"] is False
    assert result["authority"]["canonical_hash72_mint_authority"] is False
    assert result["authority"]["canonical_hash216_persistence_authority"] is False
    assert result["authority"]["canonical_persistence_authority"] is False
    assert result["authority"]["floating_point_authority"] is False


def test_rml20_agent_fails_closed_on_bad_carrier(tmp_path: Path) -> None:
    with Pass219Lane5LatencyCompositionAgent(state_root=tmp_path) as agent:
        with pytest.raises(
            Lane5MandatoryOptimizationError,
            match="RML20_MANDATORY_TRANSPORT_UNAVAILABLE:.*EXACT_648_BYTES_REQUIRED",
        ):
            agent.route_rml20_candidate(
                bytes(647),
                0,
                "operation_forward",
                library_path=LIBRARY,
            )
