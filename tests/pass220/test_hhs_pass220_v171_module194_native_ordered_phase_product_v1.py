"""V171: execute the inherited C phase-product ABI, no false Module194 closure."""
from __future__ import annotations
import ctypes as C
import pytest

import hhs_runtime.hhs_pass220_v171_module194_native_ordered_phase_product_v1 as v
from test_hhs_pass220_v161_module194_inherited_hnan_witness_v1 import source_fixture


def test_native_ordered_products_real_c_abi():
    from hhs_python.runtime import hhs_exact_ctypes_bridge as exact
    out=v.inspect_native_ordered_products(
        source_fixture(),exact._RUNTIME_LIB,require_upload_identity=False)
    products=out["native_ordered_phase_products"]
    assert [x["channel"] for x in products]==["xy","yx","zw","wz"]
    assert [x["phase72"] for x in products]==[0,36,0,36]
    assert [x["orientation"] for x in products]==[1,2,1,2]
    assert [x["ordered_tag"] for x in products]==[
        0x5859,0x5958,0x5A57,0x575A]
    assert out["module194_source_group_addresses"]==81
    assert out["inherited_native_phase_product_executed"] is True
    assert len(out["observation_sha256"])==64
    for key in (
        "native_module194_AB_value_identified",
        "native_module194_BA_value_identified",
        "native_basis_to_module194_operand_equivalence_proved",
        "lean_input_specific_product_certificate_constructed",
        "module194_hnan_interior_outer_closure_proved",
        "physical_force_equivalence_verified",
        "canonical_vm81_admission","hash72_hash216_minted",
    ):
        assert out[key] is False


def test_missing_library_and_source_identity_fail_closed():
    with pytest.raises(ValueError,match="NATIVE_LIBRARY_REQUIRED"):
        v.inspect_native_ordered_products(
            source_fixture(),None,require_upload_identity=False)
    with pytest.raises(ValueError,match="UPLOAD_SOURCE_IDENTITY_MISMATCH"):
        v.inspect_native_ordered_products(source_fixture(),None)


def test_caller_supplied_fake_native_cannot_replace_c_abi():
    with pytest.raises(ValueError,match="NATIVE_CDLL_REQUIRED"):
        v.inspect_native_ordered_products(
            source_fixture(),object(),require_upload_identity=False)


def test_corrupt_expected_phase_rejected(monkeypatch):
    from hhs_python.runtime import hhs_exact_ctypes_bridge as exact
    monkeypatch.setattr(
        v,"ORDERED_BASIS",(
            ("xy",0,1,1,1,0x5859),
            ("yx",1,0,36,2,0x5958),
            ("zw",2,3,0,1,0x5A57),
            ("wz",3,2,36,2,0x575A),
        )
    )
    with pytest.raises(v.V171NativeProductError,match="NATIVE_ORDERED_PRODUCT_REJECTED"):
        v.inspect_native_ordered_products(
            source_fixture(),exact._RUNTIME_LIB,require_upload_identity=False)
