from __future__ import annotations

from fractions import Fraction

import pytest

from hhs_runtime.pass219.lane5_self_solving_tbridge_optimizer import (
    Lane5SelfSolvingOptimizerError,
    cumulative_energy_band_from_verified_envelopes,
    energy_defect_membrane,
    genesis_root_certificate,
    genesis_root_polynomial,
    halving_class_transport,
    self_solving_optimization_receipt,
)


def test_genesis_root_certificate_is_exact_and_unique_on_positive_branch() -> None:
    receipt = genesis_root_certificate()
    assert receipt["status"] == "PASS"
    assert all(receipt["checks"].values())
    assert receipt["cubic_in_u"] == "2*u^3+3*u^2-8*u-16=0"
    assert receipt["sextic_in_a_with_u_a2"] == (
        "2*a^6+3*a^4-8*a^2-16=0"
    )
    assert genesis_root_polynomial(2) == -4
    assert genesis_root_polynomial(3) == 41

    low = Fraction(*receipt["isolation_interval"]["low"])
    high = Fraction(*receipt["isolation_interval"]["high"])
    assert genesis_root_polynomial(low) < 0
    assert genesis_root_polynomial(high) > 0
    assert 2 < low < high < 3


def test_exact_energy_defect_membrane_circular_h_quarter_is_positive() -> None:
    receipt = energy_defect_membrane(
        alpha=0,
        beta=Fraction(1, 16),
        gamma=Fraction(1, 16),
    )
    assert receipt["status"] == "PASS"
    assert receipt["sgn3_local_energy_defect"] == 1
    assert receipt["taylor_remainder_required"] is False
    assert receipt["zero_membrane"] == "F=0"


def test_exact_energy_defect_membrane_eccentric_h_quarter_is_negative() -> None:
    receipt = energy_defect_membrane(
        alpha=0,
        beta=Fraction(1, 16),
        gamma=Fraction(1, 25),
    )
    assert receipt["status"] == "PASS"
    assert receipt["sgn3_local_energy_defect"] == -1


def test_halving_class_transport_has_no_silent_flip() -> None:
    circular = halving_class_transport(
        alpha=0,
        beta=Fraction(1, 16),
        gamma=Fraction(1, 16),
    )
    eccentric = halving_class_transport(
        alpha=0,
        beta=Fraction(1, 16),
        gamma=Fraction(1, 25),
    )
    assert circular["status"] == "PASS"
    assert eccentric["status"] == "PASS"
    assert circular["decision"] == "SAME_CLASS"
    assert eccentric["decision"] == "SAME_CLASS"
    assert circular["silent_class_flip_authorized"] is False
    assert eccentric["silent_class_flip_authorized"] is False


def test_membrane_admission_fails_closed_when_A_or_R2_invalid() -> None:
    # alpha=2,beta=0 gives A=-1 and is outside the admitted sign proof.
    receipt = energy_defect_membrane(alpha=2, beta=0, gamma=0)
    assert receipt["status"] == "UNRESOLVED"
    assert receipt["sgn3_local_energy_defect"] is None


def test_float_inputs_are_rejected() -> None:
    with pytest.raises(Lane5SelfSolvingOptimizerError, match="exact"):
        energy_defect_membrane(alpha=0.1, beta=0, gamma=0)


def test_lane5_self_solving_optimizer_uses_guarded_plan_and_stays_candidate_only() -> None:
    receipt = self_solving_optimization_receipt()
    assert receipt["status"] == "PASS"
    assert all(receipt["checks"].values())
    assert receipt["legacy_self_solving_direct_execution_used"] is False
    assert receipt["candidate_only"] is True
    assert receipt["canonical_vm81_mutation_authority"] is False
    assert receipt["canonical_hash72_authority"] is False
    assert receipt["canonical_hash216_authority"] is False
    assert receipt["canonical_persistence_authority"] is False
    assert receipt["floating_point_canonical_authority"] is False

    plan = receipt["self_solving_capability_plan"]
    assert plan["safe_invocation_plan"]["direct_execution_authorized"] is False
    assert receipt["proof_preserving_optimizer"]["classification"] == (
        "PROOF_PRESERVING_READ_ONLY_OPTIMIZATION_ACTIVATED"
    )


def test_cumulative_band_sums_verified_exact_enclosures() -> None:
    receipt = cumulative_energy_band_from_verified_envelopes(
        [
            {
                "enclosure_verified": True,
                "source_receipt_sha256": "a" * 64,
                "mu_over_r_upper": Fraction(2),
                "abs_F_upper": Fraction(1, 100),
                "R_lower": Fraction(9, 10),
                "A_lower": Fraction(4, 5),
            },
            {
                "enclosure_verified": True,
                "source_receipt_sha256": "b" * 64,
                "mu_over_r_upper": Fraction(3, 2),
                "abs_F_upper": Fraction(1, 200),
                "R_lower": Fraction(19, 20),
                "A_lower": Fraction(9, 10),
            },
        ]
    )
    assert receipt["status"] == "PASS"
    assert receipt["step_count"] == 2
    assert receipt["trajectory_enclosures_generated_here"] is False
    assert receipt["floating_point_authority"] is False


def test_cumulative_band_rejects_unverified_enclosure() -> None:
    with pytest.raises(Lane5SelfSolvingOptimizerError, match="not verified"):
        cumulative_energy_band_from_verified_envelopes(
            [
                {
                    "enclosure_verified": False,
                    "source_receipt_sha256": "c" * 64,
                    "mu_over_r_upper": 1,
                    "abs_F_upper": 1,
                    "R_lower": 1,
                    "A_lower": 1,
                }
            ]
        )
