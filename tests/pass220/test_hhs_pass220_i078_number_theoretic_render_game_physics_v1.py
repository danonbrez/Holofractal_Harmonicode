from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass220_i078_number_theoretic_render_game_physics_v1 import (
    AUTHORITY_BOUNDARY,
    GLOBAL_RENDER_CLOSURE_TICKS,
    QUARTIC_PROJECTION_PERIOD,
    RSKIP_DENOMINATOR,
    RSKIP_NUMERATOR,
    RSKIP_REDUCED,
    game_projection_state,
    number_theoretic_render_phase,
    render_supercycle_witness,
    self_test,
    validate_render_phase,
)

HTML = Path("examples/ParticleSimulation.html")


def test_i078_rskip_is_exact_phase_bias_not_skip_count():
    assert (RSKIP_NUMERATOR, RSKIP_DENOMINATOR) == (64, 72)
    assert RSKIP_REDUCED == Fraction(8, 9)
    assert AUTHORITY_BOUNDARY["rskip_is_phase_bias"] is True
    assert AUTHORITY_BOUNDARY["rskip_is_skipped_frame_count"] is False


def test_i078_quartic_quantization_and_5184_closure():
    assert QUARTIC_PROJECTION_PERIOD == 4
    assert GLOBAL_RENDER_CLOSURE_TICKS == 5184

    first = number_theoretic_render_phase(0)
    close = number_theoretic_render_phase(5184)

    assert first["coordinates"]["local64"] == 0
    assert first["coordinates"]["phase72"] == 0
    assert first["coordinates"]["vm81"] == 0
    assert first["coordinates"]["quartic4"] == 0

    assert close["coordinates"]["local64"] == 0
    assert close["coordinates"]["phase72"] == 0
    assert close["coordinates"]["vm81"] == 0
    assert close["coordinates"]["quartic4"] == 0
    assert close["coordinates"]["linear5184"] == 0
    assert close["bias_accumulator"]["remainder72"] == 0
    assert close["supercycle"]["high_precision_closure"] is True


def test_i078_no_early_full_precision_closure():
    for tick in range(1, 5184):
        state = number_theoretic_render_phase(tick)
        coords = state["coordinates"]
        assert not (
            coords["local64"] == 0
            and coords["phase72"] == 0
            and coords["vm81"] == 0
            and coords["quartic4"] == 0
        )


def test_i078_supercycle_exhaustive_witness():
    witness = render_supercycle_witness()
    assert all(witness["checks"].values())
    assert witness["quartic_projection_writes"] == 1296
    assert witness["vm81_local64_states"] == 5184
    assert witness["hash72_surface_states"] == 5184
    assert len(witness["bias_remainder_states"]) == 9
    assert witness["closure_ticks"] == 5184


def test_i078_phase_state_replays_exactly_and_tamper_fails():
    state = number_theoretic_render_phase(1771)
    assert validate_render_phase(state)

    tampered = dict(state)
    tampered["tick"] = 1772
    with pytest.raises(Exception):
        validate_render_phase(tampered)


def test_i078_matches_inherited_i041_quartic_gate():
    for tick in (0, 1, 3, 4, 63, 64, 71, 72, 81, 5183, 5184):
        state = game_projection_state(tick, seed="i078-test")
        assert state["same_quartic_projection_decision"] is True
        assert (
            state["scheduler"]["projection"]["quartic_render"]
            == (tick % 4 == 0)
        )
        assert state["i041_quartic_render_gate"]["simulation_tick_continues"] is True


def test_i078_html_preserves_full_i057_physics_and_projection_gate():
    source = HTML.read_text(encoding="utf-8")

    for token in (
        'schema:"HHS_PASS_220_I057_PARTICLE_SIMULATION_ZERO_LOSS_PERF_V1"',
        "const particleCount = 2592;",
        "const LAYER_SPLIT=CORE_N+8*EXC_N;",
        "const BOND_CAP=9600;",
        "function updateSwarmCoupling()",
        "function constructorScan()",
        "function virtualDecay(forceIdx)",
        "function hnanGate(a,b)",
        'MODULES["Pass219GlobalConservation166Test"]',
        'MODULES["QuadraticReciprocityTensorTest"]',
        'MODULES["FractalLayer2Test"]',
        "simulationLogicRemoved:false",
        "receiptLogicRemoved:false",
        "canonicalMutationAuthority:false",
    ):
        assert token in source, token

    assert (
        "for(let s=0;s<steps;s++){ updateSpiralParticles(); "
        "time += simParams.evolutionSpeed * simParams.timeDilationFactor; }"
    ) in source
    assert "renderGate=((renderTick%4)===0);" in source
    assert "syncParticleRenderBatches();" in source
    assert "renderer.render(scene, camera);" in source


def test_i078_html_binds_bigint_phase_scheduler_and_correct_hud_semantics():
    source = HTML.read_text(encoding="utf-8")

    for token in (
        'schema:"HHS_PASS_220_I078_NUMBER_THEORETIC_RENDER_GAME_PHYSICS_V1"',
        "rskipNumerator:64",
        "rskipDenominator:72",
        "rskipReducedNumerator:8",
        "rskipReducedDenominator:9",
        "globalClosureTicks:5184",
        "rskipIsPhaseBias:true",
        "rskipIsSkippedFrameCount:false",
        "function numberTheoreticRenderPhase(tickExact)",
        "let renderPhaseTick=0n;",
        "renderPhaseTick+=1n;",
        "biasRemainder72:Number(scaled%72n)",
        "local64:Number(t%64n)",
        "phase72:Number(t%72n)",
        "vm81:Number(t%81n)",
        "quartic4:Number(t%4n)",
        "closure5184:Number(closure)",
        "highPrecisionClosure:closure===0n",
        'MODULES["NumberTheoreticRenderPhysicsTest"]',
        "rskip=64/72(8/9)",
        "q4=\${lastRenderPhase.quartic4}/4",
        "c5184=\${lastRenderPhase.closure5184}",
    ):
        assert token in source, token

    assert "rskip=64/72(\${renderedFrames}/\${renderTick})" not in source


def test_i078_html_exposes_render_physics_in_state_without_canonical_authority():
    source = HTML.read_text(encoding="utf-8")
    assert "renderPhysics: {" in source
    assert 'reduced:"8/9"' in source
    assert 'meaning:"phase_bias"' in source
    assert "canonicalMutationAuthority:false" in source
    assert "scene.userData.hhsRenderPhase=lastRenderPhase" in source


def test_i078_authority_boundary():
    assert AUTHORITY_BOUNDARY["projection_only"] is True
    assert AUTHORITY_BOUNDARY["physics_tick_always_advances"] is True
    assert AUTHORITY_BOUNDARY["quartic_quantizes_projection_writes"] is True
    assert AUTHORITY_BOUNDARY["global_closure_is_exact_integer_state"] is True
    assert AUTHORITY_BOUNDARY["browser_bigint_scheduler_required"] is True
    assert AUTHORITY_BOUNDARY["gpu_float_is_projection_only"] is True
    assert AUTHORITY_BOUNDARY["canonical_vm81_mutation_authority"] is False
    assert AUTHORITY_BOUNDARY["canonical_hash72_authority"] is False
    assert AUTHORITY_BOUNDARY["canonical_hash216_authority"] is False
    assert AUTHORITY_BOUNDARY["canonical_persistence_authority"] is False


def test_i078_self_test():
    report = self_test()
    assert report["status"] == "PASS"
    assert report["failed"] == []
    assert report["check_count"] == report["pass_count"]
