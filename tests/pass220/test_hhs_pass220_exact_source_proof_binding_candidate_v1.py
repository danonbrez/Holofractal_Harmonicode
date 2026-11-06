from hashlib import sha256

import pytest

from hhs_runtime.hhs_pass220_exact_source_proof_binding_candidate_v1 import (
    resolve_candidate,
)
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError


SOURCE = b"AB/-P^4==P^4/-BA"


def entry(source=SOURCE):
    return {
        "source_expression": source.decode("utf-8"),
        "source_sha256": sha256(source).hexdigest(),
        "proof_id": "TEST-EXISTING-PROOF",
        "native_proof_binding_status": "VERIFIED",
        "native_verification_receipt": "test-receipt-reference",
    }


def test_exact_match_candidate_no_authority():
    result = resolve_candidate(SOURCE, [entry()])
    assert result["source_sha256"] == sha256(SOURCE).hexdigest()
    assert result["proof_id"] == "TEST-EXISTING-PROOF"
    assert result["candidate_only"] is True
    assert result["independent_native_receipt_authentication_required"] is True
    assert result["canonical_vm81_mutation_authority"] is False
    assert result["canonical_hash72_mint_authority"] is False
    assert result["canonical_hash216_persistence_authority"] is False


@pytest.mark.parametrize("source", [
    b"AB/-P^4 == P^4/-BA",
    b"P^4/-BA==AB/-P^4",
    b"AB/-P^4==P^4/-BA\n",
])
def test_no_equivalence_or_normalization(source):
    with pytest.raises(ProofCorpusError, match="EXACT_PROOF_BINDING"):
        resolve_candidate(source, [entry()])


def test_reject_duplicate_binding():
    with pytest.raises(ProofCorpusError, match="AMBIGUOUS"):
        resolve_candidate(SOURCE, [entry(), entry()])


def test_reject_registered_digest_drift():
    bad = {**entry(), "source_sha256": "0" * 64}
    with pytest.raises(ProofCorpusError, match="SOURCE_HASH_DRIFT"):
        resolve_candidate(SOURCE, [bad])


def test_reject_unverified_binding():
    bad = {**entry(), "native_proof_binding_status": "UNRESOLVED"}
    with pytest.raises(ProofCorpusError, match="NATIVE_PROOF_BINDING_NOT_ADMITTED"):
        resolve_candidate(SOURCE, [bad])


def test_reject_missing_receipt():
    bad = {**entry(), "native_verification_receipt": ""}
    with pytest.raises(ProofCorpusError, match="NATIVE_RECEIPT"):
        resolve_candidate(SOURCE, [bad])


def test_reject_invalid_utf8():
    with pytest.raises(ProofCorpusError, match="UTF8"):
        resolve_candidate(b"\xff", [entry()])
