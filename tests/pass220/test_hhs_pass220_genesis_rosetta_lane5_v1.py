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


def test_native_cell_wall_route_requires_frozen_abi_witness():
    from hhs_runtime.hhs_pass220_genesis_rosetta_lane5_v1 import (
        lower_via_native_rna_cell_wall, validate_native_cell_wall_candidate,
        NATIVE_LOWERING_SYMBOL,
    )
    valid = {
        "surface_linux_api_abi_ingress": 1,
        "lane5_zero_bypass_interposer": 1,
        "cpp_rna_cell_wall_routed": 1,
        "holo4_evidence_equivalent": 1,
        "pqc_firewall_required_for_canonical_admission": 1,
        "signed_environmental_vm81_required": 1,
        "direct_environmental_opcode_canonical_authority": 0,
        "direct_abi_canonical_authority": 0,
        "direct_vm81_bypass_authority": 0,
        "canonical_admission_invoked": 0,
        "external_egress_authority": 0,
        "rna_prepared": {"struct_size": 1},
        "rna_decision": {"struct_size": 1},
        "g3_candidate": {"struct_size": 1},
    }
    genesis=Genesis.from_words(range(9))
    tensor=NativePhaseTensor(tuple(range(64)),"native-matrix-expression")
    calls=[]
    def ffi(request):
        calls.append(request)
        return dict(valid)
    candidate=lower_via_native_rna_cell_wall(
        genome=genesis,phase_tensor=tensor,native_bridge=ffi,
        native_request={"native": "C_ABI_INPUTS"})
    assert calls==[{"native":"C_ABI_INPUTS"}]
    assert candidate["native_lowering_symbol"]==NATIVE_LOWERING_SYMBOL
    assert candidate["candidate_only"] is True
    assert candidate["external_egress_authority"] is False
    for field in ("cpp_rna_cell_wall_routed","holo4_evidence_equivalent",
                  "signed_environmental_vm81_required"):
        invalid=dict(valid)
        invalid[field]=0
        with pytest.raises(RosettaBoundaryError):
            validate_native_cell_wall_candidate(invalid)
    invalid=dict(valid)
    invalid["canonical_admission_invoked"]=1
    with pytest.raises(RosettaBoundaryError):
        validate_native_cell_wall_candidate(invalid)
    with pytest.raises(RosettaBoundaryError):
        lower_via_native_rna_cell_wall(genome=genesis,phase_tensor=tensor,
                                      native_bridge=None,native_request={})


def test_inherited_palindromic_rna_5184_exact_reconstruction():
    from hhs_runtime.hhs_pass220_genesis_rosetta_lane5_v1 import (
        inherited_palindromic_rna_transcription,
    )
    from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
        deserialize_offsets_5184,
    )
    offsets=tuple(i%9 for i in range(81))
    witness=inherited_palindromic_rna_transcription(
        decimal_text="179971.179971",offsets=offsets)
    assert witness["inherited_i073_validation"] is True
    assert len(witness["reconstructed_5184"])==5184
    assert deserialize_offsets_5184(witness["reconstructed_5184"])==offsets
    assert witness["candidate_only"] is True
    assert witness["canonical_vm81_mutation_authority"] is False
    ingress=witness["inherited_i073_generator"]["palindromic_rna_ingress"]
    assert ingress["ieee_binary64_boundary_only"] is True
    assert ingress["host_float_arithmetic_authority"] is False
    assert ingress["rna_double_reverse_exact"] is True

def test_inherited_rna_rejects_wrong_offsets():
    from hhs_runtime.hhs_pass220_genesis_rosetta_lane5_v1 import (
        inherited_palindromic_rna_transcription,
    )
    with pytest.raises(RosettaBoundaryError):
        inherited_palindromic_rna_transcription(decimal_text="1",offsets=(0,)*80)
    with pytest.raises(RosettaBoundaryError):
        inherited_palindromic_rna_transcription(decimal_text="1",offsets=(9,)*81)
