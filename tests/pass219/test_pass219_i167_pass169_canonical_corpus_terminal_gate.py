from __future__ import annotations

import json
from pathlib import Path

from hhs_runtime.pass169.public_service import Pass169AlgebraService, Pass169PublicSurfaceError
from hhs_runtime.pass219.pass169_terminal_gate_i167 import (
    AUTHORITATIVE_SOURCE_PATH,
    CANONICAL_CORPUS_RECEIPT_PATH,
    CANONICAL_SOURCE_BYTES,
    CANONICAL_SOURCE_GIT_BLOB_SHA1,
    CANONICAL_SOURCE_SHA256,
    RUNTIME_BINDING_RECEIPT_PATH,
    _canonical_corpus_provenance,
    _runtime_binding_receipt_valid,
    build_i167_pass169_terminal_gate,
    i167_pass169_terminal_gate_self_test,
)
from hhs_runtime.pass219.pass169_terminal_reconciliation import PASS169_CANONICAL_CORPUS_PATH

ROOT = Path(__file__).resolve().parents[2]


def test_i167_canonical_corpus_is_exact_sealed_source_copy() -> None:
    source = (ROOT / AUTHORITATIVE_SOURCE_PATH).read_bytes()
    canonical = (ROOT / PASS169_CANONICAL_CORPUS_PATH).read_bytes()
    assert source == canonical
    assert len(canonical) == CANONICAL_SOURCE_BYTES
    provenance = _canonical_corpus_provenance(ROOT)
    assert provenance["verified"] is True
    assert provenance["actual_bytes"] == CANONICAL_SOURCE_BYTES
    assert provenance["actual_sha256"] == CANONICAL_SOURCE_SHA256
    assert provenance["actual_git_blob_sha1"] == CANONICAL_SOURCE_GIT_BLOB_SHA1
    assert provenance["byte_for_byte_copy_verified"] is True
    assert provenance["receipt_verified"] is True
    assert provenance["i162_source_identity_verified"] is True
    assert provenance["i163_reverse_crossarch_identity_verified"] is True


def test_i167_corpus_receipt_never_claims_unavailable_external_prompt_bytes() -> None:
    receipt = json.loads((ROOT / CANONICAL_CORPUS_RECEIPT_PATH).read_text())
    assert receipt["original_external_prompt_byte_identity_claimed"] is False
    assert receipt["canonical_repository_source_of_record_established"] is True
    assert receipt["source_rewriting_used"] is False
    assert receipt["partial_fixture_concatenation_used"] is False


def test_i167_hardened_gate_has_exact_remaining_runtime_blocker() -> None:
    report = i167_pass169_terminal_gate_self_test(ROOT)
    assert report["canonical_corpus"]["present"] is True
    assert report["canonical_corpus"]["provenance"]["verified"] is True
    assert report["pass168_parent"]["resolved"] is True
    assert report["required_artifacts"]["complete"] is True
    assert report["public_surfaces"]["cli"]["complete"] is True
    assert report["public_surfaces"]["http"]["complete"] is True
    assert report["general_runtime_binding"]["receipt_present"] is False
    assert report["general_runtime_binding"]["verified"] is False
    assert report["blockers"] == ["PASS169_GENERAL_RUNTIME_BINDING_NOT_VERIFIED"]
    assert report["pass169_terminal_contract_verified"] is False
    assert report["next_boundary"] == "PASS169_GENERAL_RUNTIME_BINDING_CLOSURE"


def test_i167_public_service_status_uses_hardened_gate() -> None:
    status = Pass169AlgebraService(ROOT).status()
    assert status["canonical_corpus_present"] is True
    assert status["pass169_terminal_contract_verified"] is False
    assert status["blockers"] == ["PASS169_GENERAL_RUNTIME_BINDING_NOT_VERIFIED"]
    source = Pass169AlgebraService(ROOT).get_source()
    assert source["source"]["canonical_pass169_corpus"] is True
    assert source["source"]["sha256"] == CANONICAL_SOURCE_SHA256
    assert source["source"]["byte_length"] == CANONICAL_SOURCE_BYTES


def test_i167_canonical_operations_remain_fail_closed_without_general_binding() -> None:
    service = Pass169AlgebraService(ROOT)
    for operation in ("tokens", "ast", "constraints", "typecheck", "normalize", "prove", "evaluate-candidate", "admit", "commit", "receipt", "replay", "reverse"):
        try:
            service.dispatch(operation)
        except Pass169PublicSurfaceError as exc:
            assert exc.code == "PASS169_GENERAL_RUNTIME_BINDING_NOT_YET_VERIFIED"
        else:
            raise AssertionError(f"{operation} unexpectedly bypassed general Runtime ABI gate")


def test_i167_runtime_receipt_validator_rejects_partial_or_forged_receipts() -> None:
    assert not (ROOT / RUNTIME_BINDING_RECEIPT_PATH).exists()
    assert _runtime_binding_receipt_valid({"verified": True}) is False
    candidate = {
        "schema": "HHS_PASS169_GENERAL_RUNTIME_BINDING_RECEIPT_V1",
        "contract_id": "HHS-P169-HSAE-VM81-ESCPR",
        "fixed_resolution": "72^42=5184^21",
        "canonical_source_sha256": CANONICAL_SOURCE_SHA256,
        "verified": True,
        "live_runtime_abi_verified": True,
        "canonical_computation_through_runtime_abi": True,
        "single_vm81_commit_authority": True,
        "hash72_receipts_verified": True,
        "hash216_identities_verified": True,
        "deterministic_replay_verified": True,
        "reverse_restores_prior_state_verified": True,
        "interpreter_compiler_equality_verified": True,
        "fallback_used": False,
        "floating_point_canonical_authority": False,
        "verified_operations": [
            "tokens", "ast", "constraints", "typecheck", "normalize", "prove",
            "evaluate-candidate", "admit", "commit", "receipt", "replay", "reverse",
        ],
    }
    assert _runtime_binding_receipt_valid(candidate) is True
    for field in (
        "live_runtime_abi_verified", "single_vm81_commit_authority",
        "hash72_receipts_verified", "deterministic_replay_verified", "fallback_used",
    ):
        forged = dict(candidate)
        forged[field] = not candidate[field]
        assert _runtime_binding_receipt_valid(forged) is False
    missing_op = dict(candidate)
    missing_op["verified_operations"] = candidate["verified_operations"][:-1]
    assert _runtime_binding_receipt_valid(missing_op) is False


def test_i167_introduces_no_new_authority() -> None:
    report = build_i167_pass169_terminal_gate(ROOT)
    authority = report["authority"]
    assert authority["new_vm81_mutation_authority"] is False
    assert authority["new_hash72_mint_authority"] is False
    assert authority["hash216_persistence_authority"] is False
    assert authority["floating_point_canonical_authority"] is False
