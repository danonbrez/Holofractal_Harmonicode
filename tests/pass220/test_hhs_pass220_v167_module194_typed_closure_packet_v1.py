"""Pass220 V167 typed HNAN packet and real C order-rejection regressions."""
from __future__ import annotations

import pytest
import hhs_runtime.hhs_pass220_v167_module194_typed_closure_packet_v1 as v
from test_hhs_pass220_v161_module194_inherited_hnan_witness_v1 import source_fixture


def test_exact_input_packet_and_inherited_native_negative_guards():
    from hhs_python.runtime import hhs_exact_ctypes_bridge as native
    result = v.inspect_typed_closure(
        source_fixture(), native._RUNTIME_LIB, require_upload_identity=False)
    assert result["source_leaf_count"] == 81
    assert result["typed_operands_distinct"] is True
    assert result["ordered_relations_preserved"] is True
    assert [p["rule_id"] for p in result["native_order_guard_probes"]] == [12,13]
    assert all(p["reverse_not_accepted"] and p["commutation_not_accepted"]
               for p in result["native_order_guard_probes"])
    for name in (
        "input_specific_ab_ba_proof_executed",
        "hnan_interior_outer_closure_proof_executed",
        "complete_course_proof_binding_verified",
        "module194_force_equivalence_verified",
        "canonical_vm81_admission", "hash72_hash216_minted",
    ):
        assert result[name] is False


def test_original_order_and_typed_identity_are_distinct():
    p = v.typed_packet()
    assert len(p["A"][2]) == 81
    assert p["A"][1] == "A_LHS"
    assert p["B"][1] == "B_RHS"
    rhs = p["B"][2][1]
    assert rhs[0] == "OrderedEquality" and rhs[1] == "0"
    assert rhs[2] == ("List",
        ("OrderedQuotient", "t^11", "a^2"),
        ("OrderedQuotient", "t^8", ("OrderedProduct", "2", "a^2")),
        ("OrderedQuotient", "t^9", "a^2"))
    assert ("OrderedProduct", ("A","B"), "+P^4") in p["relations"]
    assert ("OrderedProduct", ("B","A"), "-P^4") in p["relations"]
    assert ("Primitive", "e", (0,1)) in p["relations"]
    assert ("Trinary", "phase", (-1,0,1)) in p["relations"]
    assert len(v.validate_packet(p)) == 64


def test_swapped_ab_ba_and_typed_boundary_are_rejected():
    p = v.typed_packet()
    bad = {**p, "relations": p["relations"][:3] +
           (("OrderedProduct", ("B","A"), "+P^4"),) +
           p["relations"][4:]}
    with pytest.raises(v.V167TypedClosureError, match="TYPED_ORDER_OR_RELATION_DRIFT"):
        v.validate_packet(bad)
    bad = {**p, "B": p["A"]}
    with pytest.raises(v.V167TypedClosureError, match="TYPED_ORDER_OR_RELATION_DRIFT"):
        v.validate_packet(bad)


def test_source_address_duplication_or_tamper_rejected(monkeypatch):
    import hhs_runtime.hhs_pass220_v167_module194_typed_closure_packet_v1 as module
    original = module.flattened_source_tensor
    def duplicate():
        entries = list(original())
        entries[-1] = entries[0]
        return tuple(entries)
    monkeypatch.setattr(module, "flattened_source_tensor", duplicate)
    with pytest.raises(v.V167TypedClosureError, match="DUPLICATE_SOURCE_ADDRESS"):
        v.typed_packet()


def test_untrusted_native_library_and_source_rejected():
    with pytest.raises(ValueError, match="NATIVE_LIBRARY_REQUIRED"):
        v.inspect_typed_closure(
            source_fixture(), None, require_upload_identity=False)
    with pytest.raises(ValueError, match="UPLOAD_SOURCE_IDENTITY_MISMATCH"):
        v.inspect_typed_closure(source_fixture(), None)
