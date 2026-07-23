import copy
from fractions import Fraction
import pytest

from hhs_runtime.hhs_pass129_invariant_delta_rational_projection_algebra_v1 import *


def canonical(P=4):
    return canonical_pass129_request(center_P=P)


def test_full_even_composite_center_closure():
    e, req = canonical(4)
    proof = e.prove(req)
    assert proof["status"] == "INVARIANT_DELTA_RATIONAL_PROJECTION_ALGEBRA_PROVED"
    assert proof["derived"]["p"] == {"numerator": 3, "denominator": 1}
    assert proof["derived"]["q"] == {"numerator": 5, "denominator": 1}
    assert proof["derived"]["magic_sum"] == 34


@pytest.mark.parametrize("P", [4, 6, 8, 10, 12, 14, 100, 1024])
def test_all_sampled_even_composites(P):
    e, req = canonical(P)
    proof = e.prove(req)
    assert proof["derived"]["P_squared_minus_pq"] == {"numerator": 1, "denominator": 1}


def test_prime_center_also_closes_but_is_not_required():
    e, req = canonical(5)
    proof = e.prove(req)
    assert proof["derived"]["p"]["numerator"] == 4
    assert proof["derived"]["q"]["numerator"] == 6


def test_fractional_center_is_exact():
    e, req = canonical(Fraction(9, 2))
    proof = e.prove(req)
    assert proof["derived"]["p"] == {"numerator": 7, "denominator": 2}
    assert proof["derived"]["q"] == {"numerator": 11, "denominator": 2}


def test_zero_delta_rejected():
    e = InvariantDeltaProjectionAlgebra()
    with pytest.raises(Pass129Error) as z:
        e.make_request(delta=0, center_P=4, relation_values={})
    assert z.value.code == "REJECT_ZERO_INVARIANT_DENOMINATOR"


def test_float_rejected():
    e = InvariantDeltaProjectionAlgebra()
    with pytest.raises(Pass129Error) as z:
        e.make_request(delta=1.0, center_P=4, relation_values={})
    assert z.value.code == "REJECT_FLOAT_AS_EXACT_AUTHORITY"


def test_base_symbol_solution_rejected():
    e = InvariantDeltaProjectionAlgebra()
    vals = {name: 1 for name in e.REQUIRED_RESIDUES}
    vals["x"] = 1
    with pytest.raises(Pass129Error) as z:
        e.make_request(delta=1, center_P=4, relation_values=vals)
    assert z.value.code == "REJECT_BASE_SYMBOL_SOLVED_INSIDE_NATIVE_ALGEBRA"


def test_nonrational_native_projection_rejected():
    e = InvariantDeltaProjectionAlgebra()
    vals = {name: 1 for name in e.REQUIRED_RESIDUES}
    vals["XY_PRODUCT"] = {"symbolic": "i"}
    with pytest.raises(Pass129Error) as z:
        e.make_request(delta=1, center_P=4, relation_values=vals)
    assert z.value.code == "REJECT_NONRATIONAL_NATIVE_VALUE"


def test_missing_relation_rejected():
    e = InvariantDeltaProjectionAlgebra()
    vals = {name: 1 for name in e.REQUIRED_RESIDUES if name != "XY_PRODUCT"}
    req = e.make_request(delta=1, center_P=4, relation_values=vals)
    with pytest.raises(Pass129Error) as z:
        e.prove(req)
    assert z.value.code == "REJECT_MISSING_REQUIRED_RELATION"


def test_residue_mismatch_rejected():
    e = InvariantDeltaProjectionAlgebra()
    vals = {name: 1 for name in e.REQUIRED_RESIDUES}
    vals["M_QUADRATIC_DIFFERENCE"] = 2
    req = e.make_request(delta=1, center_P=4, relation_values=vals)
    with pytest.raises(Pass129Error) as z:
        e.prove(req)
    assert z.value.code == "REJECT_RELATION_VALUE_MISMATCH"


def test_nonunit_delta_rejected_by_idempotence():
    e = InvariantDeltaProjectionAlgebra()
    vals = {name: 2 for name in e.REQUIRED_RESIDUES}
    req = e.make_request(delta=2, center_P=6, relation_values=vals, zw_product=2, xyzw_sum=0)
    with pytest.raises(Pass129Error) as z:
        e.prove(req)
    assert z.value.code == "REJECT_DIFFERENCE_OF_SQUARES_MISMATCH"


def test_membrane_sum_tamper_rejected():
    e, req = canonical(4)
    bad = copy.deepcopy(req)
    bad["xyzw_sum"] = {"numerator": 1, "denominator": 1}
    body = dict(bad); body.pop("request_root_hash72")
    from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
    bad["request_root_hash72"] = _hash("hhs_pass129_request_v1", body)
    with pytest.raises(Pass129Error) as z:
        e.prove(bad)
    assert z.value.code == "REJECT_MEMBRANE_CLOSURE_MISMATCH"


def test_zw_tamper_rejected():
    e, req = canonical(4)
    bad = copy.deepcopy(req)
    bad["zw_product"] = {"numerator": 2, "denominator": 1}
    body = dict(bad); body.pop("request_root_hash72")
    from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
    bad["request_root_hash72"] = _hash("hhs_pass129_request_v1", body)
    with pytest.raises(Pass129Error) as z:
        e.prove(bad)
    assert z.value.code == "REJECT_MEMBRANE_CLOSURE_MISMATCH"


def test_typed_successor_mismatch_rejected():
    e = InvariantDeltaProjectionAlgebra()
    vals = {name: 1 for name in e.REQUIRED_RESIDUES}
    req = e.make_request(delta=1, center_P=4, relation_values=vals, zw_product=1, xyzw_sum=0,
                         typed_successor_relations=[{"operator":"m","input":"b^2","output":"999"}])
    with pytest.raises(Pass129Error) as z:
        e.prove(req)
    assert z.value.code == "REJECT_TYPED_SUCCESSOR_MISMATCH"


def test_external_projection_is_non_authoritative():
    e, req = canonical(4); proof = e.prove(req)
    receipt = e.external_projection_receipt(proof, projection_name="PLASTIC_GOLDEN_EULER", description="projection")
    assert receipt["projection_only"] is True and receipt["native_proof_authority"] is False
    with pytest.raises(Pass129Error) as z:
        e.reject_projection_as_proof(receipt)
    assert z.value.code == "REJECT_EXTERNAL_PROJECTION_AS_PROOF"


def test_tampered_request_root_rejected():
    e, req = canonical(4); req["center_P"]["numerator"] = 8
    with pytest.raises(Pass129Error) as z:
        e.prove(req)
    assert z.value.code == "REJECT_PROOF_ROOT_MISMATCH"


def test_tampered_proof_rejected():
    e, req = canonical(4); proof = e.prove(req); proof["derived"]["magic_sum"] = 33
    with pytest.raises(Pass129Error) as z:
        e.validate(req, proof)
    assert z.value.code == "REJECT_PROOF_ROOT_MISMATCH"


def test_deterministic_replay():
    e, req = canonical(4); proof = e.prove(req)
    assert e.replay(req, proof)["status"] == "PASS_129_DETERMINISTIC_REPLAY_VALIDATED"


def test_resource_bound_rejected():
    e, req = canonical(4)
    bad = copy.deepcopy(req); bad["resource_contract"] = {"max_steps": 1}
    body = dict(bad); body.pop("request_root_hash72")
    from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
    bad["request_root_hash72"] = _hash("hhs_pass129_request_v1", body)
    with pytest.raises(Pass129Error) as z:
        e.prove(bad)
    assert z.value.code == "REJECT_RESOURCE_CONTRACT_EXCEEDED"


def test_self_test():
    result = pass129_self_test()
    assert result["status"] == "PASS"
    assert result["base_symbols_solved"] is False
