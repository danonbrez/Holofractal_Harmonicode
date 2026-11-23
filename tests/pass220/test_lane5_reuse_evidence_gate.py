import pytest
from hhs_runtime.pass220.lane5_reuse_evidence_gate import request_reuse_verification
from hhs_runtime.pass220.lane5_structural_reuse_candidate import SCHEMA as S
from hhs_runtime.pass220.lane5_trajectory_constructor_evidence import SCHEMA as E

def data():
    s=dict(schema=S,candidate_only=True,structural_reuse_candidate=True,
       left_contract="audio",right_contract="image",
       native_receipts_verified=False,cross_modality_equivalence_verified=False,
       source_destination_abi_verified=False,canonical_vm81_mutation_authority=False,
       canonical_hash72_mint_authority=False,canonical_hash216_mint_authority=False)
    e=dict(schema=E,candidate_only=True,constructor_id="A",
       source_contract="audio",destination_contract="image",
       claimed_hash216="0"*216,phase_delta_72=[0]*72,observed_elapsed_ns=1,
       native_execution_receipt_verified=False,cross_modality_equivalence_verified=False,
       source_contract_verified=False,destination_contract_verified=False,
       canonical_vm81_mutation_authority=False,canonical_hash72_mint_authority=False,
       canonical_hash216_mint_authority=False)
    return s,e

def test_requests_witnesses_without_claiming_proof():
    s,e=data()
    result=request_reuse_verification(structural=s,evidence=e)
    assert len(result["required_witnesses"])==6
    assert result["admission_authorized"] is False
    assert result["receipt_authenticated"] is False
    assert result["candidate_only"]

@pytest.mark.parametrize("which,key,value",[
    ("s","structural_reuse_candidate",False),
    ("s","left_contract","different"),
    ("s","native_receipts_verified",True),
    ("e","native_execution_receipt_verified",True),
    ("e","source_contract_verified",True),
    ("e","phase_delta_72",[0]*71),
    ("e","observed_elapsed_ns",True),
    ("e","claimed_hash216","short"),
])
def test_fails_closed_on_forged_authority_or_shape(which,key,value):
    s,e=data()
    (s if which=="s" else e)[key]=value
    with pytest.raises(ValueError):
        request_reuse_verification(structural=s,evidence=e)
