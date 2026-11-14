"""V172 inherited native octonion/VM81 projection, no input-specific promotion."""
from __future__ import annotations
import pytest
import hhs_runtime.hhs_pass220_v172_module194_vm81_octonion_projection_v1 as v
from test_hhs_pass220_v161_module194_inherited_hnan_witness_v1 import source_fixture


def frame_fixture()->tuple[int,...]:
    # Read-only test frame, not an admitted source-derived VM81 state.
    return tuple((i*37+5) for i in range(81))


def test_octonion_projection_and_native_surface_agreement():
    from hhs_python.runtime import hhs_exact_ctypes_bridge as native
    r=v.observe_vm81_octonion(
        source_fixture(),native._RUNTIME_LIB,frame_fixture(),(0,1,2,3),
        require_upload_identity=False)
    assert r["selected_group_cells"]==[0,1,2,3]
    assert r["selected_lo_shu_weights"]==[4,4,4,4]
    assert r["native_octonion_product_count"]==64
    assert len(r["native_phase_channels"])==8
    assert [x["channel"] for x in r["native_ordered_products"]]==[
        "xy","yx","zw","wz"]
    assert [x["orientation"] for x in r["native_ordered_products"]]==[
        1,2,1,2]
    assert r["native_vm81_octonion_projection_executed"] is True
    assert len(r["observation_sha256"])==64
    for key in (
        "input_frame_is_canonical_admitted_vm81",
        "source_81_tensor_to_frame_equivalence_proved",
        "phase_word_fold_is_reversible",
        "module194_AB_BA_multiplication_proved",
        "input_specific_lean_certificate_constructed",
        "physics_force_equivalence_proved",
        "canonical_vm81_admission","hash72_hash216_minted",
    ):
        assert r[key] is False


@pytest.mark.parametrize("words",[
    tuple(range(80)),
    tuple([0]*80+[-1]),
    tuple([0]*80+[1<<64]),
    tuple([0]*80+[True]),
])
def test_invalid_exact_frame_rejected(words):
    from hhs_python.runtime import hhs_exact_ctypes_bridge as native
    with pytest.raises(v.V172OctonionError,match="EXACT_81_WORD_FRAME_REQUIRED"):
        v.observe_vm81_octonion(
            source_fixture(),native._RUNTIME_LIB,words,(0,1,2,3),
            require_upload_identity=False)


@pytest.mark.parametrize("cells",[
    (0,1,2,2), (0,1,2,81), (0,1,2,-1), (True,1,2,3),
])
def test_invalid_group_addresses_rejected(cells):
    from hhs_python.runtime import hhs_exact_ctypes_bridge as native
    with pytest.raises(v.V172OctonionError,match="FOUR_DISTINCT_GROUP_ADDRESSES_REQUIRED"):
        v.observe_vm81_octonion(
            source_fixture(),native._RUNTIME_LIB,frame_fixture(),cells,
            require_upload_identity=False)


def test_source_identity_and_real_native_library_required():
    from hhs_python.runtime import hhs_exact_ctypes_bridge as native
    with pytest.raises(ValueError,match="UPLOAD_SOURCE_IDENTITY_MISMATCH"):
        v.observe_vm81_octonion(
            source_fixture(),native._RUNTIME_LIB,frame_fixture(),(0,1,2,3))
    with pytest.raises(ValueError,match="NATIVE_LIBRARY_REQUIRED"):
        v.observe_vm81_octonion(
            source_fixture(),None,frame_fixture(),(0,1,2,3),
            require_upload_identity=False)
