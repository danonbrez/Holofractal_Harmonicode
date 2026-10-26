"""Pass 220 exact source identity -> inherited proof binding (read-only).

This module never proves an equation, interprets operators, or authorizes
VM81 admission. Records must originate from an independently audited registry;
a matching digest is only a source locator, not theorem evidence.
"""
from __future__ import annotations

from hashlib import sha256
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import (
    ProofCorpusError,
    require_native_proof_binding,
)

SCHEMA = "HHS_PASS220_EXACT_SOURCE_PROOF_BINDING_CANDIDATE_V1"


def resolve_candidate(
    source: bytes,
    registered: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Locate exactly one byte-identical existing proof record, or fail closed.

    A registry record must contain verbatim UTF-8 source_expression,
    source_sha256, nonempty proof_id and receipt identity. No normalization,
    algebraic equivalence, similarity matching, or source rewriting occurs.
    """
    if not isinstance(source, bytes) or not source:
        raise ProofCorpusError("EXACT_SOURCE_BYTES_REQUIRED")
    try:
        source.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProofCorpusError("EXACT_SOURCE_UTF8_REQUIRED") from exc
    digest = sha256(source).hexdigest()
    matches = []
    for entry in registered:
        expression = entry.get("source_expression")
        if not isinstance(expression, str):
            continue
        raw = expression.encode("utf-8")
        if sha256(raw).hexdigest() != digest or raw != source:
            continue
        if entry.get("source_sha256") != digest:
            raise ProofCorpusError("REGISTERED_SOURCE_HASH_DRIFT")
        if not isinstance(entry.get("proof_id"), str) or not entry["proof_id"]:
            raise ProofCorpusError("REGISTERED_PROOF_ID_MISSING")
        if not isinstance(entry.get("native_verification_receipt"), str) or not entry["native_verification_receipt"]:
            raise ProofCorpusError("NATIVE_RECEIPT_IDENTITY_MISSING")
        matches.append(entry)
    if len(matches) != 1:
        raise ProofCorpusError("EXACT_PROOF_BINDING_MISSING_OR_AMBIGUOUS")
    bound = matches[0]
    # The inherited gate checks explicit status and receipt presence; it does
    # NOT authenticate a caller-supplied receipt. The returned result remains
    # a read-only candidate requiring separately trusted native verification.
    require_native_proof_binding(
        {"native_proof_binding_status": bound.get("native_proof_binding_status")},
        {"native_verification_receipt": bound["native_verification_receipt"]},
    )
    return {
        "schema": SCHEMA,
        "source_sha256": digest,
        "source_length_bytes": len(source),
        "proof_id": bound["proof_id"],
        "native_verification_receipt_reference": bound["native_verification_receipt"],
        "independent_native_receipt_authentication_required": True,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
