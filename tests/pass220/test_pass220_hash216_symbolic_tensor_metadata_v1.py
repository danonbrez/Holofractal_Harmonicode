import pytest
from hhs_runtime.hhs_pass220_hash216_symbolic_tensor_metadata_v1 import (
    TensorRef, SymbolicTensorError, compose_metadata,
)

def ref(p,modality="NUMPY",lineage="A"*216,root="global"):
    return TensorRef(p,modality,lineage,root)

def test_exact_lazy_symbolic_metadata_composition():
    a,b=ref(12),ref(144,"IEEE","B"*216)
    mul=compose_metadata("ORDERED_MUL",a,b)
    assert mul["derived_P"]=="1728"
    assert mul["ordered_inputs"][0]["P"]=="12"
    assert mul["ordered_inputs"][1]["P"]=="144"
    assert mul["metadata_link_only"] and not mul["new_canonical_state_minted"]
    assert not mul["vm81_admission"] and not mul["full_tensor_materialized"]
    assert not mul["result_hash216_authoritative"]
    assert mul==compose_metadata("ORDERED_MUL",a,b)
    assert compose_metadata("ADD",a,b)["derived_P"]=="156"
    reverse=compose_metadata("ORDERED_MUL",b,a)
    assert reverse["derived_P"]==mul["derived_P"]
    assert reverse["constructor_witness_sha256"]!=mul["constructor_witness_sha256"]

@pytest.mark.parametrize("p",[-1,True,1.5])
def test_invalid_p_fails_closed(p):
    with pytest.raises(SymbolicTensorError):
        ref(p)

def test_lineage_and_global_constraint_required():
    with pytest.raises(SymbolicTensorError,match="HASH216"):
        ref(4,lineage="a")
    with pytest.raises(SymbolicTensorError,match="ROOT_MISMATCH"):
        compose_metadata("ADD",ref(4),ref(5,root="different"))

def test_unknown_operation_not_silently_scalarized():
    with pytest.raises(SymbolicTensorError,match="UNREGISTERED"):
        compose_metadata("DIV",ref(4),ref(2))
