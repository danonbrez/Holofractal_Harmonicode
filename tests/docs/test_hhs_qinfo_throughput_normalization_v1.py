from __future__ import annotations

from decimal import Decimal
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "hhs_qinfo_throughput_normalize_v1.py"
PAPER = ROOT / "docs" / "whitepapers" / "HHS_QUANTUM_INFORMATION_THROUGHPUT_NORMALIZATION_V1.md"

spec = importlib.util.spec_from_file_location("hhs_qinfo", SCRIPT)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def sample_native() -> dict:
    return {
        "result": "PASS",
        "full_manifold_address_bytes": 56,
        "stream_state_bytes": 568,
        "scale_candidates": 1_000_000,
        "elapsed_ns": 3_791_766_778,
        "candidates_per_second_floor": 263_727,
        "materialized_intermediate_states": 0,
        "count_saturation_continues": True,
    }


def test_exact_state_space_and_binary_embedding() -> None:
    assert mod.LOGICAL_DIMENSION == 72**72
    assert mod.BINARY_EMBEDDING_BITS == 445
    qbits = mod.QUBIT_EQUIVALENT_ADDRESS_BITS
    assert qbits > Decimal("444.2346001038464")
    assert qbits < Decimal("444.2346001038465")


def test_sealed_148_normalized_metrics() -> None:
    result = mod.normalize(sample_native(), hardware={"test": True})
    density = result["complexity_density"]
    assert result["result"] == "PASS"
    assert result["logical_state_space"]["qudit_dimension"] == 72
    assert result["logical_state_space"]["qudit_count"] == 72
    assert result["logical_state_space"]["binary_embedding_bits"] == 445
    assert result["physical_runner_observation"]["candidate_rate_floor_per_second"] == 263_727
    assert density["qudit_coordinate_symbols_per_second"] == 18_988_344
    assert density["vm5184_block_coordinates_per_second"] == 9_494_172
    basis = Decimal(density["basis_coordinate_information_rate_bits_equivalent_per_second"])
    route = Decimal(density["route_address_capacity_rate_bits_equivalent_per_second"])
    assert basis > Decimal("117156658.3815")
    assert basis < Decimal("117156658.3817")
    assert route == basis * 4
    assert Decimal(density["candidate_rate_per_provisioned_vcpu"]) == Decimal("65931.75")


def test_authority_and_quantum_terms_are_qualified() -> None:
    result = mod.normalize(sample_native(), hardware={"test": True})
    authority = result["authority"]
    terms = result["terminology"]
    assert authority["observational_only"] is True
    assert authority["physical_quantum_hardware_claim"] is False
    assert authority["canonical_vm81_mutation_authority"] is False
    assert authority["canonical_hash216_authority"] is False
    assert "not physical quantum-state fidelity" in terms["replay_fidelity"]
    assert "not physical coherence time" in terms["coherence_equivalent"]
    assert "reserved" in terms["quantum_volume"]


def test_paper_contains_uniform_language_and_formulas() -> None:
    text = PAPER.read_text(encoding="utf-8")
    for needle in (
        "D_HHS = 72^72",
        "72 qudits",
        "444.23460010384645 bits-equivalent",
        "445 bits",
        "117.157 Mbit-equivalent/s",
        "468.627 Mbit-equivalent/s",
        "18,988,344",
        "9,494,172",
        "chi(D,T,C) = C*log2(D)/T",
        "quantum volume",
        "circuit depth",
        "gate rate",
    ):
        assert needle in text, needle
