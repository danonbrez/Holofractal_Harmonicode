#!/usr/bin/env python3
"""Emit deterministic Pass 218 Iteration 21 relational-consumption evidence."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.genesis import ExactDistributionalRelation
from hhs_runtime.pass218.relational_consumption_i21 import (
    Pass218I21CandidateQuery,
    Pass218I21RelationalCandidateConsumer,
)


class EvidenceProvider:
    def exact_neighbors(
        self,
        token: str,
        *,
        top_k: int,
    ) -> tuple[ExactDistributionalRelation, ...]:
        fixtures = {
            "king": (
                ExactDistributionalRelation("queen", 1, 81, 100, "evidence-vector-queen"),
                ExactDistributionalRelation("man", 1, 64, 100, "evidence-vector-man"),
            ),
            "queen": (
                ExactDistributionalRelation("king", 1, 81, 100, "evidence-vector-king"),
                ExactDistributionalRelation("woman", 1, 64, 100, "evidence-vector-woman"),
            ),
        }
        return fixtures.get(token, ())[:top_k]


class EvidenceI20Control:
    def __init__(self) -> None:
        self.provider = EvidenceProvider()
        self.binding_hash72 = hash72_digest(
            {"domain": "HHS-P218-I21-EVIDENCE-I20-BINDING"},
            {"model_id": "pass218-i21-evidence"},
        )

    def status(self) -> dict:
        return {
            "relational_candidate_provider_ready": True,
            "binding_hash72": self.binding_hash72,
            "model_id": "pass218-i21-evidence",
            "canonical_model_root": "1" * 64,
            "index_root": "2" * 64,
            "browser_model_activation_permitted": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "pass165_source_retaining_learning_commit_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }

    def exact_provider(self) -> EvidenceProvider:
        return self.provider


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def main() -> None:
    control = EvidenceI20Control()
    consumer = Pass218I21RelationalCandidateConsumer(control)
    first = consumer.consume(
        Pass218I21CandidateQuery(tokens=("queen", "king", "king"), top_k=2)
    )
    replay = consumer.consume(
        Pass218I21CandidateQuery(tokens=("king", "queen"), top_k=2)
    )
    assert first["batch_hash72"] == replay["batch_hash72"]
    assert first["results"] == replay["results"]
    assert first["truth_promotion"] is False
    assert first["action_authority_minted"] is False
    assert first["canonical_learning_commit_invoked"] is False
    assert first["model_activation_invoked"] is False
    assert first["verbatim_corpus_source_retained"] is False
    assert first["authoritative_float_weights_created"] is False

    payload = {
        "schema": "HHS-P218-I21-EVIDENCE-V1",
        "iteration": 21,
        "i20_binding_hash72": control.binding_hash72,
        "candidate_batch_hash72": first["batch_hash72"],
        "deterministic_replay_equal": True,
        "source_token_count": len(first["results"]),
        "candidate_count": sum(item["candidate_count"] for item in first["results"]),
        "revisable_relational_evidence_only": True,
        "truth_promotion": False,
        "action_authority_minted": False,
        "canonical_learning_commit_invoked": False,
        "model_activation_invoked": False,
        "verbatim_corpus_source_retained": False,
        "authoritative_float_weights_created": False,
    }
    raw = canonical_bytes(payload) + b"\n"
    output_root = Path(".i21-evidence")
    output_root.mkdir(parents=True, exist_ok=True)
    evidence_path = output_root / "pass218_iteration21_evidence.json"
    evidence_path.write_bytes(raw)
    digest = sha256(raw).hexdigest()
    (output_root / "pass218_iteration21_evidence.sha256").write_text(
        digest + "  " + evidence_path.name + "\n",
        encoding="utf-8",
    )
    print(json.dumps({**payload, "evidence_sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
