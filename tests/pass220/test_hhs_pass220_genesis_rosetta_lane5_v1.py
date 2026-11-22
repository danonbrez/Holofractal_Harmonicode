"""Exhaustive address and exact candidate regression for the additive Rosetta bridge."""
from hhs_runtime.hhs_pass220_genesis_rosetta_lane5_v1 import (
    Genesis, NativeLayer, NativePhaseTensor, RosettaBoundaryError,
    clock_address, compose_candidate, coordinates,
    from_vm81_bytes, to_vm81_bytes, NUCLEUS_ORDER,
)
import pytest

def test_exhaustive_5184_address_roundtrips():
    seen=set()
    for a in range(5184):
        c=coordinates(a)
        seen.add(c["hash72"])
        for name,radix in (("vm81",64),("hash72",72),("h36",36),("q144",144)):
            q,r=c[name]
            assert radix*q+r==a
        assert c["region"]==a//576
        assert c["nucleus_symbol"]==NUCLEUS_ORDER[a//576]
        assert c["local"]==a%576
    assert len(seen)==5184

@pytest.mark.parametrize("word",[0,1,2**63,2**64-1,0x0123456789ABCDEF])
def test_nine_nucleus_polynomial_roundtrip(word):
    genesis=Genesis.from_words([word]*9)
    assert genesis.words()==(word,)*9
    for nucleus in genesis.nuclei:
        assert len(nucleus.polynomial)==64
        assert sum(bit<<j for j,bit in enumerate(nucleus.polynomial))==word
        assert nucleus.symbol*nucleus.quotient+nucleus.remainder==word
        assert genesis.address(nucleus.symbol,575)["region"]==nucleus.region

def test_native_transport():
    words=tuple((i*0x100001)&((1<<64)-1) for i in range(81))
    raw=to_vm81_bytes(words)
    assert len(raw)==648
    assert from_vm81_bytes(raw)==words
    with pytest.raises(RosettaBoundaryError):
        to_vm81_bytes(range(9))

def test_candidate_preserves_order_and_never_commits():
    tensor=NativePhaseTensor(tuple(range(64)),"native-coupled-phase-source")
    layers=(
        NativeLayer("a","symbolic","symbolic",lambda value,g,t:value+("a",)),
        NativeLayer("b","symbolic","scalar",lambda value,g,t:value+("b",)),
    )
    result=compose_candidate(words=tuple(range(9)),tensor=tensor,
        input_modality="symbolic",output_modality="scalar",
        source=("input",),ingress=lambda x:x,layers=layers,egress=lambda x:x)
    assert result["candidate_output"]==("input","a","b")
    assert result["ordered_layers"]==("a","b")
    assert result["canonical_vm81_mutation_authority"] is False
    assert result["hash216_commit_authority"] is False

def test_exact_two_sweep_clock():
    for frame in (0,1,99):
        for position in (0,2592,5183):
            a=clock_address(frame,0,position)
            b=clock_address(frame,1,position)
            assert a["vm81"]==b["vm81"] and a["hash72"]==b["hash72"]
            assert b["absolute_native_tick"]-a["absolute_native_tick"]==5184

@pytest.mark.parametrize("word",[-1,2**64,1.0,True,"1"])
def test_invalid_words(word):
    with pytest.raises(RosettaBoundaryError):
        Genesis.from_words([word]*9)

def test_missing_phase_and_route_rejected():
    with pytest.raises(RosettaBoundaryError):
        NativePhaseTensor(tuple(range(63)),"id").validate()
    with pytest.raises(RosettaBoundaryError):
        compose_candidate(words=tuple(range(9)),
            tensor=NativePhaseTensor(tuple(range(64)),"id"),
            input_modality="symbolic",output_modality="audio",
            source=0,ingress=lambda x:x,
            layers=(NativeLayer("x","symbolic","scalar",lambda v,g,t:v),),
            egress=lambda x:x)
