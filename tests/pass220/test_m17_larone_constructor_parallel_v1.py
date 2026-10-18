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
