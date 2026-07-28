import pytest

from hhs_runtime.nfv.audio import ExactScalar, HarmonicField, HarmonicLane, RationalCenterChannel
from hhs_runtime.nfv.convolution import (
    ConvolutionKernel,
    ConvolutionKernelBank,
    refresh_kernel_bank,
    render_convolution_chamber,
)
from hhs_runtime.nfv.core import NFVError
from hhs_runtime.nfv.fourier import (
    GaussianRational,
    classify_phase_interaction,
    decompose_frequency_register,
    dft4,
    inverse_dft4,
)


def lane(lane_id, samples, *, phase=(0, 1), frequency=(1, 1), lock="LOCK"):
    return HarmonicLane(
        lane_id,
        tuple(ExactScalar(*value) if isinstance(value, tuple) else ExactScalar(value) for value in samples),
        ExactScalar(*phase),
        ExactScalar(*frequency),
        lock,
    )


def field(receipt="R72-A"):
    return HarmonicField(
        lane("x", [1, 2]),
        lane("y", [-1, -2], phase=(1, 4)),
        lane("z", [2, 1], phase=(1, 2)),
        lane("w", [-2, -1], phase=(3, 4)),
        RationalCenterChannel((ExactScalar(7), ExactScalar(8)), ExactScalar(440)),
        receipt,
    )


def kernel_bank(receipt="R72-A", coefficient=1):
    return ConvolutionKernelBank(
        ConvolutionKernel("x", (ExactScalar(coefficient),), receipt),
        ConvolutionKernel("y", (ExactScalar(coefficient),), receipt),
        ConvolutionKernel("z", (ExactScalar(coefficient),), receipt),
        ConvolutionKernel("w", (ExactScalar(coefficient),), receipt),
        ConvolutionKernel("c", (ExactScalar(coefficient),), receipt),
        receipt,
    )


def test_four_lane_field_preserves_order_ring_crosslinks_and_center_independence():
    harmonic = field()
    assert tuple(lane.lane_id for lane in harmonic.surround_lanes) == ("x", "y", "z", "w")
    assert harmonic.surround_sum(0) == ExactScalar(0)
    assert harmonic.center.samples[0] == ExactScalar(7)
    candidate = harmonic.encode_vm81_candidate(0)
    assert candidate["authoritative"] is False
    assert candidate["requires_vm81_admission"] is True
    assert [entry["lane"] for entry in candidate["surround"]] == ["x", "y", "z", "w"]
    assert candidate["center"]["lane"] == "c"


def test_harmonic_length_and_phase_lock_conflicts_fail_closed():
    with pytest.raises(NFVError, match="NFV_AUDIO_LENGTH_MISMATCH"):
        HarmonicField(
            lane("x", [1]),
            lane("y", [1, 2]),
            lane("z", [1]),
            lane("w", [1]),
            RationalCenterChannel((ExactScalar(1),), ExactScalar(1)),
            "R72",
        )
    with pytest.raises(NFVError, match="NFV_AUDIO_PHASE_UNLOCKED"):
        HarmonicField(
            lane("x", [1], lock="A"),
            lane("y", [1], lock="B"),
            lane("z", [1], lock="A"),
            lane("w", [1], lock="A"),
            RationalCenterChannel((ExactScalar(1),), ExactScalar(1)),
            "R72",
        )


def test_receipt_synchronous_convolution_is_exact():
    harmonic = field()
    chamber = render_convolution_chamber(harmonic, kernel_bank())
    assert chamber == (ExactScalar(7), ExactScalar(8))


def test_kernel_refresh_requires_vm81_and_new_receipt():
    current = kernel_bank("R72-A")
    candidate = kernel_bank("R72-B", 2)
    with pytest.raises(NFVError, match="NFV_VM81_KERNEL_REFRESH_REJECTED"):
        refresh_kernel_bank(current, candidate, vm81_authorized=False)
    assert refresh_kernel_bank(current, candidate, vm81_authorized=True) == candidate
    with pytest.raises(NFVError, match="NFV_STALE_KERNEL_RECEIPT"):
        refresh_kernel_bank(current, kernel_bank("R72-A", 2), vm81_authorized=True)


def test_convolution_rejects_receipt_mismatch():
    with pytest.raises(NFVError, match="NFV_INTERACTION_RECEIPT_MISMATCH"):
        render_convolution_chamber(field("R72-A"), kernel_bank("R72-B"))


def test_exact_dft4_round_trip():
    samples = (ExactScalar(1), ExactScalar(2), ExactScalar(3), ExactScalar(4))
    coefficients = dft4(samples)
    assert inverse_dft4(coefficients) == samples


def test_phase_interaction_classification():
    a = GaussianRational(ExactScalar(1), ExactScalar(0))
    assert classify_phase_interaction(a, a) == "CONSTRUCTIVE_RESONANCE"
    assert classify_phase_interaction(a, a.negate()) == "DESTRUCTIVE_CANCELLATION"
    assert classify_phase_interaction(a, GaussianRational(ExactScalar(0), ExactScalar(1))) == "ORTHOGONAL_PHASE_LOCK"
    zero = GaussianRational(ExactScalar(0), ExactScalar(0))
    assert classify_phase_interaction(zero, zero) == "ZERO_SUM_CROSSING"


def test_frequency_register_preserves_octave_carry_and_exact_ratio():
    register = decompose_frequency_register(ExactScalar(3, 8))
    assert register.octave_carry == -2
    assert register.normalized_ratio == ExactScalar(3, 2)
    assert register.reconstructed_ratio == ExactScalar(3, 8)


def test_invalid_frequency_ratio_rejected():
    with pytest.raises(NFVError, match="NFV_INVALID_RELATIVE_FREQUENCY"):
        decompose_frequency_register(ExactScalar(0))
