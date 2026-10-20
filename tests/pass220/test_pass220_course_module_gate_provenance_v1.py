from copy import deepcopy
import pytest
from hhs_runtime.hhs_pass220_course_module_gate_provenance_v1 import (
    course_module_gate_inventory,require_executed_module_proof,
)
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError

def test_course_modules_zero_through_twenty_six_preserve_exact_section_identity():
    index=course_module_gate_inventory()
    assert index["module_count"]==27
    assert [m["index"] for m in index["ordered_modules"]]==list(range(27))
    assert all(len(m["byte_sha256"])==64 for m in index["ordered_modules"])
    assert not index["whole_course_proved"]
    assert index["verified_native_modules"]==0
    assert not index["hash216_minted"]
    assert index==course_module_gate_inventory()
    assert "The Master Chain" in index["ordered_modules"][0]["title"]
    assert "Receipt Discipline" in index["ordered_modules"][14]["title"]
    assert "Conditional secure agentic egress" in index["ordered_modules"][26]["title"]
    assert index["legacy_source_module_count"]==15
    assert all(x["source_path"]==index["source"] for x in index["ordered_modules"][:15])
    assert all(x["source_path"]==index["continuation_source"] for x in index["ordered_modules"][15:])

def test_course_module_proof_untrusted_receipts_fail_closed():
    inventory=course_module_gate_inventory()
    with pytest.raises(ProofCorpusError,match="EXECUTED_COURSE_MODULE_PROOF_REQUIRED"):
        require_executed_module_proof(inventory,0,{})
    forged={"source_sha256":inventory["source_sha256"],
            "module_sha256":inventory["ordered_modules"][0]["byte_sha256"],
            "native_verified":True}
    with pytest.raises(ProofCorpusError,match="TRUSTED_NATIVE_RECEIPT_VERIFIER_NOT_REGISTERED"):
        require_executed_module_proof(inventory,0,forged)
    with pytest.raises(ProofCorpusError,match="UNKNOWN_COURSE_MODULE"):
        require_executed_module_proof(inventory,27,forged)

def test_hnan_course_passthrough_is_not_runtime_phase_gate_proof():
    inventory=course_module_gate_inventory()
    obligations=inventory["independent_hnan_proof_obligations"]
    assert len(obligations)==2
    assert obligations[0]!=obligations[1]
    for module in inventory["ordered_modules"]:
        assert module["hnan_passthrough_proof"]=="NOT_VERIFIED"
        assert module["runtime_hnan_phase_gate"]=="NOT_VERIFIED"


def test_continuation_forged_receipt_fails_closed():
    inventory=course_module_gate_inventory()
    latest=inventory["ordered_modules"][26]
    forged={"source_sha256":latest["source_sha256"],
            "module_sha256":latest["byte_sha256"],"native_verified":True}
    with pytest.raises(ProofCorpusError,match="TRUSTED_NATIVE_RECEIPT_VERIFIER_NOT_REGISTERED"):
        require_executed_module_proof(inventory,26,forged)
