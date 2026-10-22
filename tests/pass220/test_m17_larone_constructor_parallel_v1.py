import pytest
from hhs_runtime.pass220_m17_larone_constructor_parallel_v1 import (
    witness, ADDRESSES, REGISTERS, CrosswalkFailure,
)

def test_existing_rml4_gear_synchronizes_exact_sequence():
    w = witness()
    assert w["loop_closed"]
    assert w["phase72"] == REGISTERS
    assert w["addresses"] == ADDRESSES
    assert not w["hash216_minted"]

def test_mutated_source_rejected_and_returned_witness_stable():
    addresses=list(ADDRESSES)
    registers=list(REGISTERS)
    w=witness(addresses,registers)
    addresses[0]="000"
    registers[0]=9
    assert w["addresses"]==ADDRESSES and w["phase72"]==REGISTERS
    with pytest.raises(CrosswalkFailure):
        witness(addresses,registers)

@pytest.mark.parametrize("index,replacement",[(0,"000"),(3,"111"),(7,"HNAN")])
def test_address_forgery_rejected(index,replacement):
    changed=list(ADDRESSES)
    changed[index]=replacement
    with pytest.raises(CrosswalkFailure):
        witness(changed,REGISTERS)

def test_phase_forgery_rejected():
    changed=list(REGISTERS)
    changed[3]=36
    with pytest.raises(CrosswalkFailure):
        witness(ADDRESSES,changed)

def test_parallel_constructor_delegates_to_existing_i071(monkeypatch):
    from hhs_runtime import hhs_pass220_i071_shared_root_phase_gear_loop_closure_v1 as i071
    from hhs_runtime.pass220_m17_larone_constructor_parallel_v1 import parallel_constructor_view
    calls=[]
    def inherited(**kwargs):
        calls.append(kwargs)
        return {"converged":False,"transport_closed":True,"orbit_period":72,
                "final_lineage_hash216":"inherited-only"}
    monkeypatch.setattr(i071,"run_phase_gear_loop",inherited)
    result=parallel_constructor_view(shared_root_sha256="0"*64,nucleus_index=0)
    assert len(calls)==1 and calls[0]["orientation_closed"] is False
    assert calls[0]["constraint_closed"] is False
    assert result["m17"]["phase72"]==REGISTERS
    assert result["i071"]["orbit_period"]==72
    assert not result["canonical_vm81_admitted"]
    assert not result["canonical_hash216_minted"]

def test_inherited_constructor_scope_cannot_be_forged(monkeypatch):
    from hhs_runtime import hhs_pass220_i071_shared_root_phase_gear_loop_closure_v1 as i071
    from hhs_runtime.pass220_m17_larone_constructor_parallel_v1 import parallel_constructor_view
    monkeypatch.setattr(i071,"run_phase_gear_loop",lambda **kwargs:{"converged":True})
    with pytest.raises(CrosswalkFailure):
        parallel_constructor_view(shared_root_sha256="0"*64,nucleus_index=0)
