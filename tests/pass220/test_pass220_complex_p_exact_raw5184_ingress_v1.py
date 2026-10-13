from fractions import Fraction
from hashlib import sha256
import pytest
from hhs_runtime.hhs_pass220_complex_p_exact_raw5184_ingress_v1 import (
    encode_complex_p_raw5184, decode_complex_p_raw5184, ComplexPIngressError
)
from hhs_runtime.hhs_pass220_hnan_lane5_i074_candidate_binding_v1 import (
    execute_candidate,
)
from hhs_runtime.hhs_pass220_i074_full_tensor_hnan_closure_hydration_v1 import (
    build_candidate,
)

CASES = [
    ((Fraction(0), Fraction(1,4)), Fraction(1,2)),
    ((Fraction(1,3), Fraction(1,4)), Fraction(17,5)),
    ((Fraction(-1,2), Fraction(1,3)), Fraction(1000)),
]

@pytest.mark.parametrize("base,n", CASES)
def test_lossless_exact_ingress(base,n):
    bits = encode_complex_p_raw5184(base,n)
    assert len(bits) == 5184
    recovered = decode_complex_p_raw5184(bits)
    assert recovered["P_base"] == base
    assert recovered["n"] == n
    assert recovered["P_scaled"] == (base[0]*n,base[1]*n)
    assert not recovered["native_transition_authority"]

def test_distinct_exact_states_have_distinct_carrier_identity():
    frames = [encode_complex_p_raw5184(b,n) for b,n in CASES]
    assert len(set(frames)) == len(CASES)
    assert len({sha256(x.encode("ascii")).hexdigest() for x in frames}) == len(CASES)

def test_actual_inherited_candidate_receipts(monkeypatch):
    import hhs_runtime.hhs_pass220_hnan_lane5_i074_candidate_binding_v1 as binding
    inherited = build_candidate()
    monkeypatch.setattr(binding,"build_i074_candidate",lambda: inherited)
    records = []
    for base,n in CASES:
        raw = encode_complex_p_raw5184(base,n)
        record = execute_candidate(raw)
        assert record["raw5184_sha256"] == sha256(raw.encode("ascii")).hexdigest()
        assert record["vm81_cells"] == 81
        assert record["raw_roundtrip_exact"]
        assert record["hnan_gate_inherited"]
        assert record["hnan_terminal_source"] == "xy+epsilon"
        assert record["candidate_only"] is True
        assert record["canonical_vm81_mutation_authority"] is False
        assert record["canonical_hash216_persistence_authority"] is False
        assert record["i074_hash216"] == (record["i074_previous_hash72"] +
                                         record["i074_change_hash72"] +
                                         record["i074_receipt_hash72"])
        records.append(record["raw5184_sha256"])
    assert len(set(records)) == len(CASES)

def test_negative_canonicality_and_types():
    raw = encode_complex_p_raw5184((Fraction(1,3),Fraction(1,4)),Fraction(2))
    with pytest.raises(ComplexPIngressError):
        decode_complex_p_raw5184(raw[:-1]+"1")
    with pytest.raises(ComplexPIngressError):
        encode_complex_p_raw5184((0,0), 2)
    with pytest.raises(ComplexPIngressError):
        encode_complex_p_raw5184((1,2), .5)
    with pytest.raises(ComplexPIngressError):
        decode_complex_p_raw5184("0"*5184)
