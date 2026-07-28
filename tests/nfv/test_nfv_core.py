from fractions import Fraction
import pytest

from hhs_runtime.nfv import LocalizedModulus, LocalizedRational, NFVError, NFVObject, TransitionPackage


def admit_all(_obj, _candidate):
    return True


def reject_all(_obj, _candidate):
    return False


def test_centered_modulus_exact_reconstruction():
    state = LocalizedModulus.normalize(179971179971, 20, centered=True)
    assert state.exact == 179971179971
    assert -10 <= state.residue < 10


def test_noncentered_modulus_exact_reconstruction():
    state = LocalizedModulus.normalize(-41, 9, centered=False)
    assert state.exact == -41
    assert 0 <= state.residue < 9


def test_localized_arithmetic_preserves_complete_value():
    a = LocalizedModulus.normalize(12345678901234567890, 72)
    b = LocalizedModulus.normalize(-999999999999999999, 72)
    assert a.add(b).exact == a.exact + b.exact
    assert a.subtract(b).exact == a.exact - b.exact
    assert a.multiply(b).exact == a.exact * b.exact


def test_chart_conflict_fails_closed():
    a = LocalizedModulus.normalize(10, 9)
    b = LocalizedModulus.normalize(10, 20)
    with pytest.raises(NFVError, match="NFV_MODULUS_CHART_CONFLICT"):
        a.add(b)


def test_rebase_is_witnessed_by_exact_reconstruction():
    original = LocalizedModulus.normalize(987654321, 72, loshu_orientation=4)
    rebased = original.rebase(81, loshu_orientation=9)
    assert rebased.exact == original.exact
    assert rebased.modulus == 81
    assert rebased.loshu_orientation == 9


def test_recursive_carry_promotion_preserves_carry_value():
    child = LocalizedModulus.normalize(999999, 20)
    local, parent = child.promote_carry(9)
    assert local.carry == 0
    assert parent.exact == child.carry


def test_exact_rational_localization():
    state = LocalizedRational.localize(14, 21, numerator_modulus=9, denominator_modulus=20)
    assert state.exact == Fraction(2, 3)


def test_zero_denominator_rejected():
    with pytest.raises(NFVError, match="NFV_ZERO_DENOMINATOR"):
        LocalizedRational.localize(1, 0, numerator_modulus=9, denominator_modulus=9)


def test_nonfungible_identity_includes_history_and_authority():
    a = NFVObject("STATE_VECTOR", {"value": 5}, ("value>=0",), (), "VM81-A")
    b = NFVObject("STATE_VECTOR", {"value": 5}, ("value>=0",), (), "VM81-B")
    assert a.object_index != b.object_index


def test_atomic_commit_requires_vm81_admission_and_hash72_receipt():
    original = NFVObject("STATE_VECTOR", {"value": 5}, ("value>=0",), (), "VM81-A")
    package = TransitionPackage.prepare(original, "NORMALIZE_LOCAL", {"value": 25})
    with pytest.raises(NFVError, match="NFV_VM81_REJECTED"):
        package.commit(original, vm81_admit=reject_all)
    committed, closed = package.commit(original, vm81_admit=admit_all)
    assert original.state == {"value": 5}
    assert committed.state == {"value": 25}
    assert committed.version == original.version + 1
    assert closed.status == "COMMITTED"
    assert committed.receipt_head == closed.receipt


def test_exact_reversal_uses_committed_evidence():
    original = NFVObject("STATE_VECTOR", {"value": 5}, (), (), "VM81-A")
    package = TransitionPackage.prepare(original, "INVOKE", {"value": 8})
    committed, closed = package.commit(original, vm81_admit=admit_all)
    restored = closed.reverse(committed, vm81_admit=admit_all)
    assert restored.state == original.state
    assert restored.version == committed.version + 1


def test_stale_package_rejected():
    original = NFVObject("STATE_VECTOR", {"value": 1}, (), (), "VM81-A")
    package = TransitionPackage.prepare(original, "INVOKE", {"value": 2})
    different = NFVObject("STATE_VECTOR", {"value": 3}, (), (), "VM81-A")
    with pytest.raises(NFVError, match="NFV_STALE_OR_INVALID_PACKAGE"):
        package.commit(different, vm81_admit=admit_all)
