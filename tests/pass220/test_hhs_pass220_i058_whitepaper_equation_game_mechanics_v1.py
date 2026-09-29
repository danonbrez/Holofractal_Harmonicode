from copy import deepcopy
from fractions import Fraction
import inspect
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass220_whitepaper_equation_game_mechanics_v1 import (
    EQUATION_MANIFEST,
    FRAME_SCHEMA,
    SCHEMA,
    STATUS_CANONICAL_VERBATIM,
    STATUS_EXECUTED_EXACT,
    STATUS_HHS_NATIVE_SEMANTIC,
    STATUS_REFERENCE_ONLY,
    Pass220I058GameMechanicsError,
    build_whitepaper_game_frame,
    equation_manifest,
    gfe_reciprocal_residual,
    integer_translation_pair,
    macro_reciprocal_projection,
    phase_radius_projection,
    reference_relativistic_projection_descriptor,
    transition_witness216,
    validate_whitepaper_game_frame,
    whitepaper_game_mechanics_self_test,
    whitepaper_game_mechanics_witness,
)
from hhs_runtime.hhs_pass220_holofractal_relativistic_game_engine_v1 import (
    HASH72_ALPHABET,
)
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


ROOT = Path(__file__).resolve().parents[2]
COMPENDIUM = ROOT / "docs/whitepapers/HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md"
FROZEN_HTML = ROOT / "examples/ParticleSimulation.html"


def test_i058_manifest_preserves_whitepaper_status_boundaries():
    manifest = equation_manifest()
    rows = {row["id"]: row for row in manifest["equations"]}

    assert rows["BOUNDARY_B"]["status"] == STATUS_CANONICAL_VERBATIM
    assert rows["BOUNDARY_B"]["runtime_lowering"] is False
    assert rows["REFERENCE_RELATIVITY"]["status"] == STATUS_REFERENCE_ONLY
    assert rows["REFERENCE_RELATIVITY"]["runtime_lowering"] is False

    assert rows["CARDINALITY_5184"]["status"] == STATUS_EXECUTED_EXACT
    assert rows["INTEGER_TRANSLATION_PAIR"]["status"] == STATUS_EXECUTED_EXACT
    assert rows["GFE_RECIPROCAL_RESIDUAL"]["status"] == STATUS_EXECUTED_EXACT
    assert rows["MACRO_RECIPROCAL_PROJECTION"]["status"] == STATUS_HHS_NATIVE_SEMANTIC
    assert rows["PHASE_RADIUS"]["status"] == STATUS_HHS_NATIVE_SEMANTIC

    assert "BOUNDARY_B" in manifest["protected_nonlowered_surfaces"]
    assert "REFERENCE_RELATIVITY" in manifest["protected_nonlowered_surfaces"]
    assert manifest["cross_status_substitution_authority"] is False
    assert manifest["host_float_arithmetic_used"] is False
    assert manifest["canonical_mutation_authority"] is False


def test_i058_manifest_equations_are_present_in_authoritative_compendium():
    source = COMPENDIUM.read_text(encoding="utf-8")

    for token in (
        "CANONICAL_VERBATIM",
        "EXECUTED_EXACT",
        "HHS_NATIVE_SEMANTIC",
        "REFERENCE_ONLY",
        "P² = pq + 2P/(p+q)",
        "P² - pq = 1",
        "5184 = 72*72",
        "5184 = 81*64",
        "m²-m = m_pass",
        "m_pos + m_neg = 1",
        "Phi(G)+Phi(G^-1)",
        "rho² = 1-kappa",
        "ds² = -c² dt² + dx² + dy² + dz²",
    ):
        assert token in source, token


def test_macro_reciprocal_projection_closes_exactly_without_float():
    row = macro_reciprocal_projection(Fraction(3, 1))

    assert row["P"] == {"numerator": 3, "denominator": 1}
    assert row["p"] == {"numerator": 2, "denominator": 1}
    assert row["q"] == {"numerator": 4, "denominator": 1}
    assert row["pq"] == {"numerator": 8, "denominator": 1}
    assert row["p_plus_q"] == {"numerator": 6, "denominator": 1}
    assert row["P_squared_minus_pq"] == {"numerator": 1, "denominator": 1}
    assert row["correction_2P_over_p_plus_q"] == {
        "numerator": 1,
        "denominator": 1,
    }
    assert row["host_float_arithmetic_used"] is False

    with pytest.raises(Pass220I058GameMechanicsError):
        macro_reciprocal_projection(0)
    with pytest.raises(Pass220I058GameMechanicsError):
        macro_reciprocal_projection(3.0)


def test_integer_translation_pair_uses_exact_odd_square_discriminant():
    row = integer_translation_pair(6)
    assert row["discriminant"] == 25
    assert row["sqrt_discriminant"] == 5
    assert row["m_pos"] == 3
    assert row["m_neg"] == -2
    assert row["pair_sum"] == 1

    with pytest.raises(Pass220I058GameMechanicsError):
        integer_translation_pair(5)


def test_gfe_calibration_5_over_4_closes_to_1_over_20():
    row = gfe_reciprocal_residual(Fraction(5, 4))
    assert row["alpha"] == {"numerator": 5, "denominator": 4}
    assert row["alpha_inverse"] == {"numerator": 4, "denominator": 5}
    assert row["residual"] == {"numerator": 1, "denominator": 20}
    assert row["rationalized_residual"] == row["residual"]
    assert row["logarithmic_terms_cancel_symbolically"] is True
    assert row["physical_energy_authority"] is False

    fixed = gfe_reciprocal_residual(1)
    assert fixed["residual"] == {"numerator": 0, "denominator": 1}
    assert fixed["fixed_point_alpha_1"] is True


def test_phase_radius_preserves_exact_rho_squared_and_trinary_branch():
    inside = phase_radius_projection(Fraction(3, 4))
    boundary = phase_radius_projection(1)
    outside = phase_radius_projection(Fraction(5, 4))

    assert inside["rho_squared"] == {"numerator": 1, "denominator": 4}
    assert inside["trinary_branch"] == 1
    assert boundary["rho_squared"] == {"numerator": 0, "denominator": 1}
    assert boundary["trinary_branch"] == 0
    assert outside["rho_squared"] == {"numerator": -1, "denominator": 4}
    assert outside["trinary_branch"] == -1
    assert inside["sqrt_evaluated"] is False


def test_reference_relativity_cannot_promote_itself_to_canonical_physics():
    row = reference_relativistic_projection_descriptor()
    assert row["status"] == STATUS_REFERENCE_ONLY
    assert row["exact_typed_lowering_performed"] is False
    assert row["gameplay_projection_allowed"] is True
    assert row["canonical_physics_authority"] is False
    assert row["canonical_mutation_authority"] is False


def test_transition_witness216_is_three_ordered_hash72_surfaces_candidate_only():
    a = HASH72_ALPHABET[0] * 72
    b = HASH72_ALPHABET[1] * 72
    c = HASH72_ALPHABET[2] * 72
    row = transition_witness216(a, b, c)

    assert row["witness216"] == a + b + c
    assert row["length"] == 216
    assert row["candidate_only"] is True
    assert row["canonical_hash216_authority"] is False

    with pytest.raises(Pass220I058GameMechanicsError):
        transition_witness216("x", b, c)


def test_whitepaper_game_frame_drives_exact_mechanics_on_one_tick():
    frame = build_whitepaper_game_frame(
        143,
        seed="i058-test-seed",
        P=3,
        m_pass=6,
        alpha=Fraction(5, 4),
        kappa=Fraction(3, 4),
    )
    result = validate_whitepaper_game_frame(frame)

    assert frame["schema"] == FRAME_SCHEMA
    assert result["ok"] is True
    assert frame["q144"] == 143
    assert frame["linear5184"] == 143
    assert frame["mechanics"]["world_address"]["coordinate"]["linear5184"] == 143
    assert frame["mechanics"]["phase_clock"]["q144"] == 143
    assert frame["mechanics"]["phase_clock"]["reciprocal_q144"] == 71
    assert frame["mechanics"]["reciprocal_actor_pair"]["unit_closure"] == {
        "numerator": 1,
        "denominator": 1,
    }
    assert frame["mechanics"]["translation_spawn_pair"] == {
        "m_pos": 3,
        "m_neg": -2,
        "sum": 1,
    }
    assert frame["mechanics"]["reciprocal_potential"]["exact_residual"] == {
        "numerator": 1,
        "denominator": 20,
    }
    assert frame["mechanics"]["phase_region"]["rho_squared"] == {
        "numerator": 1,
        "denominator": 4,
    }
    assert frame["frozen_renderer_baseline"] == (
        "HHS_PASS_220_I057_PARTICLE_SIMULATION_ZERO_LOSS_PERF_V1"
    )
    assert frame["host_float_arithmetic_used_by_exact_frame"] is False
    assert frame["probability_used"] is False
    assert frame["canonical_vm81_mutation_authority"] is False
    assert frame["canonical_hash72_authority"] is False
    assert frame["canonical_hash216_authority"] is False


def test_frame_receipt_tampering_fails_closed():
    frame = build_whitepaper_game_frame(4, seed="tamper-seed")
    tampered = deepcopy(frame)
    tampered["q144"] = 5
    with pytest.raises(Pass220I058GameMechanicsError, match="receipt mismatch"):
        validate_whitepaper_game_frame(tampered)


def test_i058_does_not_modify_frozen_i057_html_baseline():
    source = FROZEN_HTML.read_text(encoding="utf-8")
    assert 'schema:"HHS_PASS_220_I057_PARTICLE_SIMULATION_ZERO_LOSS_PERF_V1"' in source
    assert "HHS_PASS_220_I058_WHITEPAPER_EQUATION_GAME_MECHANICS_V1" not in source


def test_witness_and_self_test_close():
    witness = whitepaper_game_mechanics_witness()
    assert witness["ok"] is True
    assert witness["canonical_authority_escalation"] is False

    result = whitepaper_game_mechanics_self_test()
    assert result["schema"] == SCHEMA
    assert result["ok"] is True


def test_service_registry_declares_i058_equation_mechanics_constructor():
    source = inspect.getsource(make_default_service_registry)
    assert "pass220.whitepaper_equation_game_mechanics.self_test" in source
    assert "hhs_pass220_whitepaper_equation_game_mechanics_v1" in source
