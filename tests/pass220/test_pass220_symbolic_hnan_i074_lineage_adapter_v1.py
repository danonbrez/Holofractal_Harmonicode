from unittest.mock import patch
import pytest
from hhs_runtime.hhs_pass220_hash216_symbolic_tensor_metadata_v1 import (
    TensorRef, SymbolicTensorError,
)
from hhs_runtime.hhs_pass220_hnan_lane5_i074_candidate_binding_v1 import (
    Lane5HNANBindingError,
)
from hhs_runtime.hhs_pass220_symbolic_hnan_i074_lineage_adapter_v1 import (
    bind_symbolic_to_inherited_hnan,
)

LINEAGE = "a"*72+"b"*72+"c"*72

def ref(P,lineage=LINEAGE,root="one"):
    return TensorRef(P,"NUMPY",lineage,root)

def inherited():
    return {
        "raw_roundtrip_exact": True,
        "hnan_gate_inherited": True,
        "three_binary_perspectives_retained": True,
        "i074_hash216": LINEAGE,
        "i074_candidate_root_sha256": "f"*64,
        "raw5184_sha256": "e"*64,
    }

def test_ordered_symbolic_metadata_binds_executed_inherited_gate():
    with patch("hhs_runtime.hhs_pass220_symbolic_hnan_i074_lineage_adapter_v1.execute_candidate",return_value=inherited()) as gate:
        forward=bind_symbolic_to_inherited_hnan("ORDERED_MUL",ref(12),ref(144),"0"*5184)
        reverse=bind_symbolic_to_inherited_hnan("ORDERED_MUL",ref(144),ref(12),"0"*5184)
    assert gate.call_count == 2
    assert forward["derived_P"]=="1728"
    assert forward["ordered_inputs"] != reverse["ordered_inputs"]
    assert forward["candidate_receipt_sha256"] != reverse["candidate_receipt_sha256"]
    assert forward["hnan_inherited_gate_executed"]
    assert forward["same_ancestry_lineage_verified"]
    assert not forward["symbolic_P_to_raw5184_constructor_proved"]
    assert not forward["global_hnan_closure_for_symbolic_operation_proved"]
    assert not forward["canonical_vm81_mutation_authority"]

def test_unbound_ancestry_fails_closed():
    with patch("hhs_runtime.hhs_pass220_symbolic_hnan_i074_lineage_adapter_v1.execute_candidate",return_value=inherited()):
        with pytest.raises(SymbolicTensorError,match="LINEAGE_NOT_BOUND"):
            bind_symbolic_to_inherited_hnan("ADD",ref(3,"x"*216),ref(4),"0"*5184)

def test_hnan_gate_fail_closed():
    bad=inherited()
    bad["hnan_gate_inherited"]=False
    with patch("hhs_runtime.hhs_pass220_symbolic_hnan_i074_lineage_adapter_v1.execute_candidate",return_value=bad):
        with pytest.raises(Lane5HNANBindingError,match="INHERITED_HNAN_GATE_REQUIRED"):
            bind_symbolic_to_inherited_hnan("ADD",ref(2),ref(4),"0"*5184)

def test_global_root_must_match_before_native_candidate_execution():
    with patch("hhs_runtime.hhs_pass220_symbolic_hnan_i074_lineage_adapter_v1.execute_candidate") as gate:
        with pytest.raises(SymbolicTensorError,match="ROOT_MISMATCH"):
            bind_symbolic_to_inherited_hnan("ADD",ref(2),ref(4,root="other"),"0"*5184)
        gate.assert_not_called()
