#!/usr/bin/env python3
"""Emit deterministic Pass 218 Iteration 22 semantic-graph evidence."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.semantic_graph_i22 import (
    Pass218I22GraphQuery,
    Pass218I22SemanticGraphCandidateAssembler,
    Pass218I22WordNetPriorProvider,
)


class EvidenceI21Control:
    def __init__(self) -> None:
        self.binding_hash72 = hash72_digest(
            {"domain": "HHS-P218-I22-EVIDENCE-I20-BINDING"},
            {"model_id": "pass218-i22-evidence"},
        )

    def status(self) -> dict:
        return {
            "candidate_consumption_ready": True,
            "i20_binding_hash72": self.binding_hash72,
            "candidate_semantics": "REVISABLE_RELATIONAL_EVIDENCE",
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }

    def consume(self, payload: dict) -> dict:
        tokens = tuple(payload["tokens"])
        top_k = int(payload["top_k"])
        results = []
        for token in tokens:
            target = "queen" if token == "king" else "king"
            candidate_body = {
                "source_token": token,
                "rank": 1,
                "target": target,
                "relation_type": "DISTRIBUTIONAL_NEIGHBOR",
                "status": 1,
                "similarity_squared": {"numerator": 81, "denominator": 100},
                "vector_identity": "i22-evidence-vector-" + target,
                "provenance": "PASS166_EXACT_WORD2VEC_VIA_I20",
                "revisable_candidate": True,
                "empirical_truth_authority": False,
                "action_authority": False,
                "canonical_learning_commit": False,
            }
            candidate = {
                **candidate_body,
                "candidate_hash72": hash72_digest(
                    {"domain": "HHS-P218-I22-EVIDENCE-I21-CANDIDATE"},
                    candidate_body,
                ),
            }
            results.append(
                {
                    "source_token": token,
                    "candidate_count": 1,
                    "candidates": [candidate][:top_k],
                }
            )
        body = {
            "i20_binding_hash72": self.binding_hash72,
            "candidate_semantics": "REVISABLE_RELATIONAL_EVIDENCE",
            "query": {"tokens": list(tokens), "top_k": top_k},
            "results": results,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }
        return {
            **body,
            "batch_hash72": hash72_digest(
                {"domain": "HHS-P218-I22-EVIDENCE-I21-BATCH"},
                body,
            ),
        }


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def main() -> None:
    repository_root = Path.cwd().resolve()
    i21 = EvidenceI21Control()
    lexical = Pass218I22WordNetPriorProvider(repository_root)
    assembler = Pass218I22SemanticGraphCandidateAssembler(i21, lexical)

    first = assembler.assemble(
        Pass218I22GraphQuery(tokens=("queen", "king", "king"), top_k=2)
    )
    replay = assembler.assemble(
        Pass218I22GraphQuery(tokens=("king", "queen"), top_k=2)
    )
    assert first["graph_hash72"] == replay["graph_hash72"]
    assert first["nodes"] == replay["nodes"]
    assert first["edges"] == replay["edges"]
    assert first["truth_promotion"] is False
    assert first["action_authority_minted"] is False
    assert first["canonical_learning_commit_invoked"] is False
    assert first["model_activation_invoked"] is False
    assert first["verbatim_corpus_source_retained"] is False
    assert first["authoritative_float_weights_created"] is False
    assert first["candidate_semantic_compression_input_ready"] is True
    assert first["authoritative_semantic_compression_ready"] is False

    payload = {
        "schema": "HHS-P218-I22-EVIDENCE-V1",
        "iteration": 22,
        "i20_binding_hash72": first["i20_binding_hash72"],
        "i21_batch_hash72": first["i21_batch_hash72"],
        "wordnet_asset_manifest_hash72": first["wordnet_asset_manifest_hash72"],
        "semantic_graph_hash72": first["graph_hash72"],
        "deterministic_replay_equal": True,
        "node_count": first["node_count"],
        "edge_count": first["edge_count"],
        "evidence_bundle_count": first["evidence_bundle_count"],
        "mixed_polarity_pair_count": first["mixed_polarity_pair_count"],
        "revisable_semantic_graph_candidate": True,
        "candidate_semantic_compression_input_ready": True,
        "authoritative_semantic_compression_ready": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "canonical_learning_commit_invoked": False,
        "model_activation_invoked": False,
        "verbatim_corpus_source_retained": False,
        "authoritative_float_weights_created": False,
    }
    raw = canonical_bytes(payload) + b"\n"
    output_root = Path(".i22-evidence")
    output_root.mkdir(parents=True, exist_ok=True)
    evidence_path = output_root / "pass218_iteration22_evidence.json"
    evidence_path.write_bytes(raw)
    digest = sha256(raw).hexdigest()
    (output_root / "pass218_iteration22_evidence.sha256").write_text(
        digest + "  " + evidence_path.name + "\n",
        encoding="utf-8",
    )
    print(json.dumps({**payload, "evidence_sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
