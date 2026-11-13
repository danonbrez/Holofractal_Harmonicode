"""Source-bound u^72 gyroscope recurrence witness for Pass 220.

Exercise inherited RML4/RML5 ordered reciprocal quarter-turn geometry using
exact integer phase steps; retain separate candidate phase and full global
proof authority. No arbitrary 648-byte VM81 frame -> rotor-channel mapping is
introduced here. A toroidal-looking projection does not itself prove closure.
"""
from __future__ import annotations

from math import gcd, lcm

import pytest

from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    CHANNELS, PHASE_MODULUS, PRODUCT_RELATIONS,
    advance_gyroscope, build_gyroscope_state, expected_product_phase,
)
from hhs_runtime.pass219.gyroscope_admission_membrane import (
    build_chirality_polarity_witness, certify_reciprocal_transition,
)

SIGNS = {"xy": 1, "yx": -1, "zw": 1, "wz": -1}
SEED = {"x": 3, "y": 21, "z": 14, "w": 40}


def make_state() -> dict:
    phases = dict(SEED)
    for product, relation in PRODUCT_RELATIONS.items():
        phases[product] = expected_product_phase(
            phases[relation["generator"]], SIGNS[product]
        )
    return build_gyroscope_state(phases, SIGNS, state_id="PASS220_U72_SOURCE_GYRO")


def coupled_steps(x: int, y: int, z: int, w: int) -> dict[str, int]:
    primitive = {"x": x, "y": y, "z": z, "w": w}
    steps = dict(primitive)
    for product, relation in PRODUCT_RELATIONS.items():
        steps[product] = primitive[relation["generator"]]
    return {channel: steps[channel] for channel in CHANNELS}


@pytest.mark.parametrize("rates", [
    (1, -1, 2, -2),
    (3, -3, 5, -5),
    (7, -7, 9, -9),
])
def test_coupled_reciprocal_gyroscope_exact_period_and_inverse(rates) -> None:
    current = make_state()
    initial = dict(current["phases"])
    steps = coupled_steps(*rates)
    assert current["admissible_product_geometry"]
    assert build_chirality_polarity_witness(current)["all_chiral_pairs_opposed"]
    period = lcm(*(PHASE_MODULUS // gcd(PHASE_MODULUS, abs(rate))
                   for rate in rates))
    assert 1 <= period <= PHASE_MODULUS
    seen = {tuple(current["phases"].values())}
    for tick in range(1, period + 1):
        transition = advance_gyroscope(
            current, steps, transition_id=f"coupled:{rates}:{tick}"
        )
        certificate = certify_reciprocal_transition(transition)
        assert certificate["phase_transition_is_bijective"]
        assert certificate["restored_product_geometry_admissible"]
        current = transition["next_state"]
        assert current["admissible_product_geometry"]
        assert build_chirality_polarity_witness(current)["all_chiral_pairs_opposed"]
        coordinates = tuple(current["phases"].values())
        if tick < period:
            assert coordinates not in seen
            seen.add(coordinates)
        else:
            assert current["phases"] == initial


def test_non_coupled_step_rejected_as_geometric_closure() -> None:
    initial = make_state()
    steps = {channel: 0 for channel in CHANNELS}
    steps["x"] = 1  # xy must rotate with its generator
    transition = advance_gyroscope(initial, steps, transition_id="broken:xy")
    assert not transition["next_state"]["admissible_product_geometry"]
    assert any(
        row["product"] == "xy" and not row["satisfied"]
        for row in transition["next_state"]["product_constraints"]["relations"]
    )


def test_phase_identity_not_promoted_to_native_delta_or_global_proof() -> None:
    state = make_state()
    steps = coupled_steps(1, -1, 2, -2)
    assert PHASE_MODULUS == 72
    assert state["scalar_projection_substitution_authority"] is False
    assert state["canonical_vm81_mutation_authority"] is False
    assert state["canonical_hash72_mint_authority"] is False
    for _ in range(PHASE_MODULUS):
        state = advance_gyroscope(state, steps, transition_id="phase72")["next_state"]
    assert state["phases"] == make_state()["phases"]
    assert state["canonical_vm81_mutation_authority"] is False
    # The native frame's typed phase projection and global lemma closure
    # remain separate obligations from this source-bound rotor orbit.
