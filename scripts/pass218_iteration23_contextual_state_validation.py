#!/usr/bin/env python3
"""Emit deterministic Pass 218 Iteration 23 contextual-state evidence."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from hhs_runtime.pass218.contextual_state_i23 import (
    Pass218I23ContextQuery,
    Pass218I23ContextualStateHydrator,
)
from hhs_runtime.pass218.semantic_graph_i22 import (
    Pass218I22GraphQuery,
    Pass218I22SemanticGraphCandidateAssembler,
    Pass218I22WordNetPriorProvider,
)
from scripts.pass218_iteration22_semantic_graph_validation import EvidenceI21Control


class I22EvidenceAdapter:
    def __init__(self, repository_root: Path) -> None:
        self.i21 = EvidenceI21Control()
        self.lexical = Pass218I22WordNetPriorProvider(repository_root)
        self.assembler = Pass218I22SemanticGraphCandidateAssembler(
            self.i21,
            self.lexical,
        )

    def status(self) -> dict:
        return self.assembler.status()

    def assemble(self, payload: dict) -> dict:
        return self.assembler.assemble(
            Pass218I22GraphQuery(
                tokens=tuple(payload["tokens"]),
                top_k=int(payload["top_k"]),
            )
        )


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
    i22 = I22EvidenceAdapter(repository_root)
    hydrator = Pass218I23ContextualStateHydrator(i22)

    first = hydrator.hydrate(
        Pass218I23ContextQuery(
            tokens=("queen", "king", "king"),
            context_id="royal succession",
            attention_tokens=("king",),
            top_k=2,
            attention_radius=1,
            max_hydrated_nodes=12,
        )
    )
    replay = hydrator.hydrate(
        Pass218I23ContextQuery(
            tokens=("king", "queen"),
            context_id="royal succession",
            attention_tokens=("king",),
            top_k=2,
            attention_radius=1,
            max_hydrated_nodes=12,
        )
    )
    alternate = hydrator.hydrate(
        Pass218I23ContextQuery(
            tokens=("king", "queen"),
            context_id="royal succession",
            attention_tokens=("queen",),
            top_k=2,
            attention_radius=1,
            max_hydrated_nodes=12,
        )
    )

    assert first == replay
    assert first["contextual_state_hash72"] == replay["contextual_state_hash72"]
    assert first["contextual_state_hash72"] != alternate["contextual_state_hash72"]
    assert first["retrieved_node_count"] >= first["hydrated_node_count"] >= 1
    assert first["attention_active_count"] >= 1
    assert first["contextual_hydration_candidate_ready"] is True
    assert first["narrative_beat_integration_invoked"] is False
    assert first["perspective_hydration_invoked"] is False
    assert first["grounded_relational_manifold_ready"] is False
    assert first["formal_analogical_typing_invoked"] is False
    assert first["authoritative_semantic_compression_ready"] is False
    assert first["truth_promotion"] is False
    assert first["action_authority_minted"] is False
    assert first["canonical_learning_commit_invoked"] is False
    assert first["model_activation_invoked"] is False
    assert first["verbatim_corpus_source_retained"] is False
    assert first["authoritative_float_weights_created"] is False

    payload = {
        "schema": "HHS-P218-I23-EVIDENCE-V1",
        "iteration": 23,
        "i20_binding_hash72": first["i20_binding_hash72"],
        "i21_batch_hash72": first["i21_batch_hash72"],
        "i22_graph_hash72": first["i22_graph_hash72"],
        "wordnet_asset_manifest_hash72": first["wordnet_asset_manifest_hash72"],
        "context_configuration_hash72": first["context_configuration_hash72"],
        "contextual_state_hash72": first["contextual_state_hash72"],
        "deterministic_replay_equal": True,
        "context_change_produces_distinct_state": True,
        "retrieved_node_count": first["retrieved_node_count"],
        "hydrated_node_count": first["hydrated_node_count"],
        "hydrated_edge_count": first["hydrated_edge_count"],
        "attention_active_count": first["attention_active_count"],
        "candidate_influential_count": first["candidate_influential_count"],
        "revisable_contextual_state_candidate": True,
        "contextual_hydration_candidate_ready": True,
        "narrative_beat_integration_invoked": False,
        "perspective_hydration_invoked": False,
        "grounded_relational_manifold_ready": False,
        "formal_analogical_typing_invoked": False,
        "authoritative_semantic_compression_ready": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "canonical_learning_commit_invoked": False,
        "model_activation_invoked": False,
        "verbatim_corpus_source_retained": False,
        "authoritative_float_weights_created": False,
    }
    raw = canonical_bytes(payload) + b"\n"
    output_root = Path(".i23-evidence")
    output_root.mkdir(parents=True, exist_ok=True)
    evidence_path = output_root / "pass218_iteration23_evidence.json"
    evidence_path.write_bytes(raw)
    digest = sha256(raw).hexdigest()
    (output_root / "pass218_iteration23_evidence.sha256").write_text(
        digest + "  " + evidence_path.name + "\n",
        encoding="utf-8",
    )
    print(json.dumps({**payload, "evidence_sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
