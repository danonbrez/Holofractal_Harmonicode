from pathlib import Path
from native_projects.hhs_vm81_native_exposure.hhs_pass078_1_native_abi_reconciliation_v1 import *

ROOT = Path(__file__).resolve().parents[1]

def test_exactly_fifteen_declarations_are_dispositioned():
    m = reconcile_native_abi(ROOT)
    assert m["unresolved_abi_declarations_total"] == 15
    assert m["unresolved_abi_declarations_dispositioned"] == 15

def test_each_declaration_has_exactly_one_allowed_disposition_and_root():
    m = reconcile_native_abi(ROOT)
    assert all(r["disposition"] in ALLOWED for r in m["declarations"])
    assert all(r["disposition_root_hash72"] for r in m["declarations"])

def test_no_false_callable_or_fabricated_implementation_claims():
    m = reconcile_native_abi(ROOT)
    assert m["false_callable_claims"] == 0
    assert m["fabricated_native_implementations"] == 0
    assert all(not r["callable_after_reconciliation"] for r in m["declarations"])

def test_operational_resemblance_is_not_semantic_equivalence():
    m = reconcile_native_abi(ROOT)
    init = next(r for r in m["declarations"] if r["declared_symbol"] == "hhs_vm_init")
    assert init["candidate_native_primitive"]
    assert init["semantic_equivalence_status"] == "UNPROVEN_REPRESENTATION_AND_CONTRACT_EQUIVALENCE"
    assert init["disposition"] == "RETAIN_AS_TYPED_UNRESOLVED"

def test_no_unproven_mapping_is_admitted():
    m = reconcile_native_abi(ROOT)
    assert m["semantic_equivalence_unproven_mappings"] == 0

def test_all_typed_unresolved_are_explicitly_justified():
    m = reconcile_native_abi(ROOT)
    assert m["remaining_typed_unresolved"] == 15
    assert all(r["rationale"] and r["architectural_revision_required"] for r in m["declarations"])

def test_reconciliation_is_deterministic():
    assert reconcile_native_abi(ROOT) == reconcile_native_abi(ROOT)
    assert build_release(ROOT) == build_release(ROOT)
