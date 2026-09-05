"""Pass 219 I167 terminal gate hardening for Pass169.

I167 closes the canonical-corpus provenance gap by requiring an exact byte-for-
byte copy of the sealed 632-byte I162/I163 source lineage plus a structured
preservation receipt.  It also fixes a masked I165 terminal-gate defect: the
public algebra surface is reachable but still deliberately blocks canonical
operations until a real general Runtime ABI binding exists.  Therefore corpus
presence alone can never mint Pass169 terminal authority.
"""
from __future__ import annotations

from hashlib import sha1, sha256
import json
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.pass219.pass169_terminal_reconciliation import (
    FIXED_RESOLUTION,
    PASS169_CANONICAL_CORPUS_PATH,
    PASS169_CONTRACT_ID,
    PASS169_TERMINAL_CLASSIFICATION,
    build_i164_pass169_terminal_reconciliation,
)

PASS = 219
ITERATION = "I167"
BASE_MAIN = "177e774f676d57708df0cba7459bf1b6d4835b8e"

CANONICAL_CORPUS_RECEIPT_PATH = Path("HHS_PASS_169_CANONICAL_CORPUS_RECEIPT.json")
RUNTIME_BINDING_RECEIPT_PATH = Path("HHS_PASS_169_RUNTIME_BINDING_RECEIPT.json")
AUTHORITATIVE_SOURCE_PATH = Path(
    "contracts/pass219/PASS_219_COMBINED_QUOTIENT_MATRIX_POWER_NATIVE_1_21_8.harmonicode"
)
I162_EVIDENCE_PATH = Path("evidence/pass219/PASS_219_I162_FEATURE_VALIDATION_33836940374.json")
I163_EVIDENCE_PATH = Path("evidence/pass219/PASS_219_I163_FEATURE_VALIDATION_33866718853.json")

CANONICAL_SOURCE_BYTES = 632
CANONICAL_SOURCE_SHA256 = "3315641c8d6aa9fc4f3918eccda8e3a40c8445cc417a65e5dea683f68020cf53"
CANONICAL_SOURCE_GIT_BLOB_SHA1 = "5ef1e3dbcd107666b1f30269d4579afb246de3f5"


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return sha1(header + data).hexdigest()


def _canonical_corpus_provenance(repo_root: str | Path = ".") -> Dict[str, Any]:
    root = Path(repo_root).resolve()
    source_path = root / AUTHORITATIVE_SOURCE_PATH
    canonical_path = root / PASS169_CANONICAL_CORPUS_PATH
    receipt_path = root / CANONICAL_CORPUS_RECEIPT_PATH
    i162_path = root / I162_EVIDENCE_PATH
    i163_path = root / I163_EVIDENCE_PATH

    result: Dict[str, Any] = {
        "verified": False,
        "source_path": AUTHORITATIVE_SOURCE_PATH.as_posix(),
        "canonical_path": PASS169_CANONICAL_CORPUS_PATH.as_posix(),
        "receipt_path": CANONICAL_CORPUS_RECEIPT_PATH.as_posix(),
        "expected_bytes": CANONICAL_SOURCE_BYTES,
        "expected_sha256": CANONICAL_SOURCE_SHA256,
        "expected_git_blob_sha1": CANONICAL_SOURCE_GIT_BLOB_SHA1,
        "partial_fixture_concatenation_authorized": False,
        "source_rewriting_authorized": False,
    }
    if not all(path.is_file() for path in (source_path, canonical_path, receipt_path, i162_path, i163_path)):
        return result

    source = source_path.read_bytes()
    canonical = canonical_path.read_bytes()
    receipt = _load_json(receipt_path)
    i162 = _load_json(i162_path)
    i163 = _load_json(i163_path)

    source_exact = bool(
        len(source) == CANONICAL_SOURCE_BYTES
        and sha256(source).hexdigest() == CANONICAL_SOURCE_SHA256
        and _git_blob_sha1(source) == CANONICAL_SOURCE_GIT_BLOB_SHA1
    )
    copy_exact = bool(
        canonical == source
        and len(canonical) == CANONICAL_SOURCE_BYTES
        and sha256(canonical).hexdigest() == CANONICAL_SOURCE_SHA256
        and _git_blob_sha1(canonical) == CANONICAL_SOURCE_GIT_BLOB_SHA1
    )

    i162_source = i162.get("source", {})
    i162_runtime = i162.get("runtime_execution", {})
    i162_verified = bool(
        i162.get("result", "PASS") == "PASS"
        and i162_source.get("path") == AUTHORITATIVE_SOURCE_PATH.as_posix()
        and i162_source.get("byte_length") == CANONICAL_SOURCE_BYTES
        and i162_source.get("sha256") == CANONICAL_SOURCE_SHA256
        and i162_source.get("identity_verified") is True
        and i162_runtime.get("source_reconstruction_verified") is True
        and i162_runtime.get("pass169_sealed_candidate_authority_verified") is True
        and i162_runtime.get("exact_vm81_admission_verified") is True
        and i162_runtime.get("atomic_commit_verified") is True
    )

    i163_source = i163.get("source", {})
    i163_reverse = i163.get("reverse_model", {})
    i163_cross = i163.get("cross_architecture", {})
    i163_verified = bool(
        i163_source.get("path") == AUTHORITATIVE_SOURCE_PATH.as_posix()
        and i163_source.get("bytes") == CANONICAL_SOURCE_BYTES
        and i163_source.get("sha256") == CANONICAL_SOURCE_SHA256
        and i163_reverse.get("pass159_reverse_transition_receipt_verified") is True
        and i163_reverse.get("vm81_prior_transaction_state_restore_verified") is True
        and i163_cross.get("records_identical") is True
        and i163.get("authority", {}).get("interpreter_compiler_equality_verified") is True
    )

    receipt_verified = bool(
        receipt.get("schema") == "HHS_PASS169_CANONICAL_CORPUS_RECEIPT_V1"
        and receipt.get("contract_id") == PASS169_CONTRACT_ID
        and receipt.get("fixed_resolution") == FIXED_RESOLUTION
        and receipt.get("canonical_path") == PASS169_CANONICAL_CORPUS_PATH.as_posix()
        and receipt.get("authoritative_source_path") == AUTHORITATIVE_SOURCE_PATH.as_posix()
        and receipt.get("source_bytes") == CANONICAL_SOURCE_BYTES
        and receipt.get("source_sha256") == CANONICAL_SOURCE_SHA256
        and receipt.get("source_git_blob_sha1") == CANONICAL_SOURCE_GIT_BLOB_SHA1
        and receipt.get("canonical_git_blob_sha1") == CANONICAL_SOURCE_GIT_BLOB_SHA1
        and receipt.get("byte_for_byte_copy_verified") is True
        and receipt.get("source_path_blob_equals_canonical_path_blob") is True
        and receipt.get("source_rewriting_used") is False
        and receipt.get("partial_fixture_concatenation_used") is False
        and receipt.get("canonicalization_basis") == "SEALED_FULL_COMBINED_SOURCE_LINEAGE"
        and receipt.get("canonical_repository_source_of_record_established") is True
        and receipt.get("floating_point_canonical_authority") is False
    )

    verified = bool(source_exact and copy_exact and i162_verified and i163_verified and receipt_verified)
    result.update(
        {
            "verified": verified,
            "source_exact": source_exact,
            "byte_for_byte_copy_verified": copy_exact,
            "receipt_verified": receipt_verified,
            "i162_source_identity_verified": i162_verified,
            "i163_reverse_crossarch_identity_verified": i163_verified,
            "actual_bytes": len(canonical),
            "actual_sha256": sha256(canonical).hexdigest(),
            "actual_git_blob_sha1": _git_blob_sha1(canonical),
            "original_external_prompt_byte_identity_claimed": receipt.get(
                "original_external_prompt_byte_identity_claimed"
            ) is True,
        }
    )
    return result


def _runtime_binding_receipt_valid(receipt: Dict[str, Any]) -> bool:
    required_operations = {
        "tokens", "ast", "constraints", "typecheck", "normalize", "prove",
        "evaluate-candidate", "admit", "commit", "receipt", "replay", "reverse",
    }
    operations = set(receipt.get("verified_operations", []))
    return bool(
        receipt.get("schema") == "HHS_PASS169_GENERAL_RUNTIME_BINDING_RECEIPT_V1"
        and receipt.get("contract_id") == PASS169_CONTRACT_ID
        and receipt.get("fixed_resolution") == FIXED_RESOLUTION
        and receipt.get("canonical_source_sha256") == CANONICAL_SOURCE_SHA256
        and receipt.get("verified") is True
        and receipt.get("live_runtime_abi_verified") is True
        and receipt.get("canonical_computation_through_runtime_abi") is True
        and receipt.get("single_vm81_commit_authority") is True
        and receipt.get("hash72_receipts_verified") is True
        and receipt.get("hash216_identities_verified") is True
        and receipt.get("deterministic_replay_verified") is True
        and receipt.get("reverse_restores_prior_state_verified") is True
        and receipt.get("interpreter_compiler_equality_verified") is True
        and receipt.get("fallback_used") is False
        and receipt.get("floating_point_canonical_authority") is False
        and required_operations.issubset(operations)
    )


def build_i167_pass169_terminal_gate(repo_root: str | Path = ".") -> Dict[str, Any]:
    root = Path(repo_root).resolve()
    report = build_i164_pass169_terminal_reconciliation(root)
    corpus = _canonical_corpus_provenance(root)

    runtime_receipt_path = root / RUNTIME_BINDING_RECEIPT_PATH
    runtime_receipt: Dict[str, Any] | None = None
    runtime_verified = False
    if runtime_receipt_path.is_file():
        try:
            runtime_receipt = _load_json(runtime_receipt_path)
            runtime_verified = _runtime_binding_receipt_valid(runtime_receipt)
        except (json.JSONDecodeError, OSError):
            runtime_receipt = None

    blockers = list(report.get("blockers", []))
    if corpus["verified"]:
        blockers = [
            blocker for blocker in blockers
            if blocker not in {
                "PASS169_CANONICAL_CORPUS_ABSENT",
                "PASS169_REQUIRED_ARTIFACT_SET_INCOMPLETE",
            }
        ]
    elif (root / PASS169_CANONICAL_CORPUS_PATH).is_file():
        if "PASS169_CANONICAL_CORPUS_PROVENANCE_INVALID" not in blockers:
            blockers.append("PASS169_CANONICAL_CORPUS_PROVENANCE_INVALID")

    if not runtime_verified and "PASS169_GENERAL_RUNTIME_BINDING_NOT_VERIFIED" not in blockers:
        blockers.append("PASS169_GENERAL_RUNTIME_BINDING_NOT_VERIFIED")

    terminal_conditions = dict(report.get("terminal_conditions", {}))
    terminal_conditions["canonical_corpus_provenance_verified"] = corpus["verified"]
    terminal_conditions["general_runtime_binding_verified"] = runtime_verified

    terminal_verified = bool(
        not blockers
        and all(terminal_conditions.values())
        and corpus["verified"]
        and runtime_verified
        and report.get("contract", {}).get("terminal_classification") == PASS169_TERMINAL_CLASSIFICATION
    )

    report.update(
        {
            "schema": "HHS_PASS219_I167_PASS169_TERMINAL_GATE_V1",
            "iteration": ITERATION,
            "base_main": BASE_MAIN,
            "canonical_corpus": {
                **report.get("canonical_corpus", {}),
                "present": (root / PASS169_CANONICAL_CORPUS_PATH).is_file(),
                "provenance": corpus,
            },
            "general_runtime_binding": {
                "receipt_path": RUNTIME_BINDING_RECEIPT_PATH.as_posix(),
                "receipt_present": runtime_receipt_path.is_file(),
                "verified": runtime_verified,
            },
            "terminal_conditions": terminal_conditions,
            "blockers": blockers,
            "pass169_terminal_contract_verified": terminal_verified,
            "next_boundary": (
                "PASS169_TERMINAL_CLOSURE_VERIFIED"
                if terminal_verified
                else "PASS169_GENERAL_RUNTIME_BINDING_CLOSURE"
            ),
        }
    )
    return report


def i167_pass169_terminal_gate_self_test(repo_root: str | Path = ".") -> Dict[str, Any]:
    report = build_i167_pass169_terminal_gate(repo_root)
    if not report["canonical_corpus"]["provenance"]["verified"]:
        raise AssertionError("Pass169 canonical corpus provenance is not verified")
    if report["authority"]["floating_point_canonical_authority"]:
        raise AssertionError("floating-point canonical authority introduced")
    if report["general_runtime_binding"]["verified"] is False and report["pass169_terminal_contract_verified"]:
        raise AssertionError("Pass169 terminal status bypassed general Runtime ABI binding")
    return report


__all__ = [
    "AUTHORITATIVE_SOURCE_PATH",
    "BASE_MAIN",
    "CANONICAL_CORPUS_RECEIPT_PATH",
    "CANONICAL_SOURCE_BYTES",
    "CANONICAL_SOURCE_GIT_BLOB_SHA1",
    "CANONICAL_SOURCE_SHA256",
    "RUNTIME_BINDING_RECEIPT_PATH",
    "build_i167_pass169_terminal_gate",
    "i167_pass169_terminal_gate_self_test",
]
