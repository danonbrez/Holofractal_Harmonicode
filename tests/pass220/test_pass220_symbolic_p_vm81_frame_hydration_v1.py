from unittest.mock import patch
import pytest
from hhs_runtime.hhs_pass220_hash216_symbolic_tensor_metadata_v1 import TensorRef, SymbolicTensorError
from hhs_runtime.hhs_pass220_symbolic_p_vm81_frame_hydration_v1 import hydrate_symbolic_p_frame

def ref(P):
    return TensorRef(P,"NUMPY","a"*216,"constraint")

def fake_binding(operation, left, right, raw5184, *, candidate=None):
    assert len(raw5184)==5184
    assert set(raw5184) <= {"0","1"}
    return {"derived_P":str(left.P*right.P if operation=="ORDERED_MUL" else left.P+right.P),
            "candidate_receipt_sha256":"c"*64}

def test_exact_inherited_native_frame_generation_and_hnan_handoff():
    with patch("hhs_runtime.hhs_pass220_symbolic_p_vm81_frame_hydration_v1.bind_symbolic_to_inherited_hnan",side_effect=fake_binding) as gate:
        r=hydrate_symbolic_p_frame("ORDERED_MUL",ref(12),ref(144))
    assert gate.call_count==1
    assert r["derived_P"]=="1728"
    assert r["inherited_vm81_raw_bits"]==5184
    assert r["raw_frame_generated_from_symbolic_P"]
    assert r["native_hnan_candidate_binding_executed"]
    assert not r["vm81_mutation_authority"]
    assert not r["global_symbolic_operator_closure_proved"]

def test_metadata_addition_and_deterministic_native_frame():
    with patch("hhs_runtime.hhs_pass220_symbolic_p_vm81_frame_hydration_v1.bind_symbolic_to_inherited_hnan",side_effect=fake_binding):
        a=hydrate_symbolic_p_frame("ADD",ref(3),ref(4))
        b=hydrate_symbolic_p_frame("ADD",ref(3),ref(4))
    assert a==b
    assert a["derived_P"]=="7"

def test_inherited_depth_overflow_is_not_modulo_aliased():
    with pytest.raises(SymbolicTensorError,match="RECURSIVE_HIGHER_DEPTH"):
        hydrate_symbolic_p_frame("ADD",ref(72**72),ref(0))

def test_invalid_native_lane_fails_closed():
    with pytest.raises(SymbolicTensorError,match="SIX_LANE"):
        hydrate_symbolic_p_frame("ADD",ref(1),ref(2),lane_index=12)

def test_constraint_mismatch_prevents_gate_execution():
    right=TensorRef(2,"NUMPY","a"*216,"another")
    with patch("hhs_runtime.hhs_pass220_symbolic_p_vm81_frame_hydration_v1.bind_symbolic_to_inherited_hnan") as gate:
        with pytest.raises(SymbolicTensorError,match="ROOT_MISMATCH"):
            hydrate_symbolic_p_frame("ADD",ref(1),right)
        gate.assert_not_called()
