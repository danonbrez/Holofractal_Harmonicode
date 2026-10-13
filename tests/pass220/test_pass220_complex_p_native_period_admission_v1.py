"""Pass 220: exact complex-P scaling, native cycle admission boundary.

Deliberately rejects a false bridge: the Pass 219 paradox guard's finite
unsigned-rational option ABI is not a complex tensor/VM81 transition API.
A native closure period must be witnessed by native ordered trajectories.
"""
from fractions import Fraction
import pytest

from hhs_runtime.hhs_pass219_dynamic_paradox_phase_cycle_registration_v1 import (
    manifest, surface_declaration,
)
from hhs_runtime.pass219.hnan_4x4_recursive_gate_v1 import (
    hnan_loshu_resolution_receipt,
)
from tests.pass220.test_pass220_complex_p_rational_scaling_v1 import (
    BASE, SCALES, ONE, ZERO, add, mul, neg, divide,
)


def native_period_admission(*, state_type, trajectory=None, receipt=None):
    """Read-only admission guard. Never synthesizes native trajectory data."""
    if state_type != "VM81_ORDERED_COMPLEX_TENSOR":
        raise ValueError("COMPLEX_NATIVE_STATE_TYPE_REQUIRED")
    if not trajectory or len(trajectory) < 2:
        raise ValueError("NATIVE_ORDERED_TRAJECTORY_REQUIRED")
    if not isinstance(receipt, dict) or receipt.get("signed_vm81_admitted") is not True:
        raise ValueError("SIGNED_VM81_ADMISSION_REQUIRED")
    if receipt.get("hash216_lineage_verified") is not True:
        raise ValueError("HASH216_LINEAGE_REQUIRED")
    if receipt.get("hnan_gate_verified") is not True:
        raise ValueError("HNAN_GATE_REQUIRED")
    # Even with flags, only source-authoritative cycle validator can establish
    # period. This boundary has no native transition call, so do not infer one.
    raise ValueError("AUTHORITATIVE_NATIVE_CYCLE_VALIDATOR_REQUIRED")


@pytest.mark.parametrize("base", BASE)
@pytest.mark.parametrize("scale", SCALES)
def test_exact_complex_projection_is_not_a_native_period(base, scale):
    P = mul(base, (scale, Fraction(0)))
    p, q = add(P, neg(ONE)), add(P, ONE)
    assert add(mul(P, P), neg(mul(p, q))) == ONE
    assert divide(mul(add(q, neg(p)), P), add(p, q)) == ONE
    assert mul(divide(p, q), divide(q, p)) == ONE
    assert divide(P, base) == (scale, Fraction(0))
    with pytest.raises(ValueError, match="COMPLEX_NATIVE_STATE_TYPE_REQUIRED"):
        native_period_admission(state_type="GAUSSIAN_RATIONAL_SCALAR_PROJECTION")


def test_existing_finite_cycle_guard_has_different_domain():
    guard = manifest()
    surface = surface_declaration()
    assert guard["cycle_semantics"] == "FINITE_ORDERED_TRAJECTORY"
    assert guard["canonical_mutation_authority"] is False
    assert guard["canonical_hash72_authority"] is False
    assert guard["canonical_persistence_authority"] is False
    assert surface["symbol"] == "hhs_exact_pass219_paradox_analyze"
    assert "finite_state_cycle_detection" in surface["guards"]
    assert "ordered_trajectory_witness" in surface["guards"]
    # Guard supports bounded rational options, not a complex VM81 transition.
    with pytest.raises(ValueError, match="NATIVE_ORDERED_TRAJECTORY_REQUIRED"):
        native_period_admission(state_type="VM81_ORDERED_COMPLEX_TENSOR")


def test_untrusted_flags_cannot_invent_native_period():
    fake = dict(signed_vm81_admitted=True, hash216_lineage_verified=True,
                hnan_gate_verified=True)
    with pytest.raises(ValueError, match="AUTHORITATIVE_NATIVE_CYCLE_VALIDATOR_REQUIRED"):
        native_period_admission(state_type="VM81_ORDERED_COMPLEX_TENSOR",
                                trajectory=("state_A", "state_A"), receipt=fake)


def test_inherited_hnan_center_not_redefined():
    receipt = hnan_loshu_resolution_receipt()
    assert receipt["status"] == "PASS"
    assert receipt["terminal_source"] == "xy+epsilon"
