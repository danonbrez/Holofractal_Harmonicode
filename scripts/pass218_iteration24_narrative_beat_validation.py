#!/usr/bin/env python3
"""Emit deterministic Pass 218 Iteration 24 narrative-beat candidate evidence."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.contextual_state_i23 import (
    Pass218I23ContextQuery,
    Pass218I23ContextualStateHydrator,
)
from hhs_runtime.pass218.narrative_beat_i24 import (
    Pass218I24BeatRequest,
    Pass218I24NarrativeBeatAssembler,
)
from scripts.pass218_iteration23_contextual_state_validation import I22EvidenceAdapter


class I23EvidenceAdapter:
    def __init__(self, repository_root: Path) -> None:
        self.i22 = I22EvidenceAdapter(repository_root)
        self.hydrator = Pass218I23ContextualStateHydrator(self.i22)

    def status(self) -> dict:
        return self.hydrator.status()

    def hydrate(self, payload: dict) -> dict:
        return self.hydrator.hydrate(
            Pass218I23ContextQuery(
                tokens=tuple(payload["tokens"]),
                context_id=str(payload["context_id"]),
                attention_tokens=tuple(payload.get("attention_tokens", [])),
                top_k=int(payload.get("top_k", 8)),
                attention_radius=int(payload.get("attention_radius", 1)),
                max_hydrated_nodes=int(payload.get("max_hydrated_nodes", 24)),
                allowed_relation_families=tuple(
                    payload.get("allowed_relation_families", [])
                ),
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
    source_path = repository_root / "HHS_PASS_218_APPEND_ONLY_ALIGNMENT_NARRATIVE_TRUTH_AGENTIC_AMENDMENT_2_1_0.md"
    source_sha256 = sha256(source_path.read_bytes()).hexdigest()
    curriculum_identity_hash72 = hash72_digest(
        {"domain": "HHS-P218-I24-EVIDENCE-CURRICULUM-CLAIM-V1"},
        {
            "source_sha256": source_sha256,
            "curriculum_position": 24,
            "authoritative_curriculum_advance": False,
        },
    )
    evidence_payload_hash72 = hash72_digest(
        {"domain": "HHS-P218-I24-EVIDENCE-PAYLOAD-V1"},
        {
            "source_sha256": source_sha256,
            "observation": "NARRATIVE_BEAT_CONTRACT_PRESENT",
            "verbatim_retained": False,
        },
    )

    i23 = I23EvidenceAdapter(repository_root)
    assembler = Pass218I24NarrativeBeatAssembler(i23)

    request = Pass218I24BeatRequest(
        tokens=("state", "narrative", "narrative"),
        context_id="pass218 narrative beat contract",
        curriculum_identity_hash72=curriculum_identity_hash72,
        curriculum_position=24,
        source_id=source_path.name,
        source_checksum_sha256=source_sha256,
        source_authority="REPOSITORY_NATIVE_CONTRACT_AUTHORITY",
        rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
        evidence_id="pass218-i24-contract-observation",
        evidence_type="REPOSITORY_CONTRACT_OBSERVATION",
        evidence_epistemic_status="OBSERVED",
        evidence_payload_hash72=evidence_payload_hash72,
        attention_tokens=("narrative",),
        top_k=2,
        attention_radius=1,
        max_hydrated_nodes=12,
    )
    first = assembler.assemble(request)
    replay = assembler.assemble(
        Pass218I24BeatRequest(
            tokens=("narrative", "state"),
            context_id="pass218 narrative beat contract",
            curriculum_identity_hash72=curriculum_identity_hash72,
            curriculum_position=24,
            source_id=source_path.name,
            source_checksum_sha256=source_sha256,
            source_authority="REPOSITORY_NATIVE_CONTRACT_AUTHORITY",
            rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
            evidence_id="pass218-i24-contract-observation",
            evidence_type="REPOSITORY_CONTRACT_OBSERVATION",
            evidence_epistemic_status="OBSERVED",
            evidence_payload_hash72=evidence_payload_hash72,
            attention_tokens=("narrative",),
            top_k=2,
            attention_radius=1,
            max_hydrated_nodes=12,
        )
    )
    alternate = assembler.assemble(
        Pass218I24BeatRequest(
            tokens=("narrative", "state"),
            context_id="pass218 narrative beat contract alternate",
            curriculum_identity_hash72=curriculum_identity_hash72,
            curriculum_position=24,
            source_id=source_path.name,
            source_checksum_sha256=source_sha256,
            source_authority="REPOSITORY_NATIVE_CONTRACT_AUTHORITY",
            rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
            evidence_id="pass218-i24-contract-observation",
            evidence_type="REPOSITORY_CONTRACT_OBSERVATION",
            evidence_epistemic_status="OBSERVED",
            evidence_payload_hash72=evidence_payload_hash72,
            attention_tokens=("narrative",),
            top_k=2,
            attention_radius=1,
            max_hydrated_nodes=12,
        )
    )

    assert first == replay
    assert first["narrative_beat_hash72"] == replay["narrative_beat_hash72"]
    assert first["narrative_beat_hash72"] != alternate["narrative_beat_hash72"]
    assert first["narrative_beat_candidate_ready"] is True
    assert first["admitted_predecessor_state"] is False
    assert first["predecessor_root_semantics"] == "I23_REVISABLE_CONTEXTUAL_STATE_CANDIDATE"
    assert first["optional_narrative_projection"] is None
    assert first["natural_language_projection_generated"] is False
    assert first["narrative_beat_integration_invoked"] is False
    assert first["perspective_hydration_invoked"] is False
    assert first["grounded_relational_manifold_ready"] is False
    assert first["hash216_continuation_verified"] is False
    assert first["vm81_authorization_invoked"] is False
    assert first["authoritative_semantic_compression_ready"] is False
    assert first["truth_promotion"] is False
    assert first["action_authority_minted"] is False
    assert first["canonical_learning_commit_invoked"] is False
    assert first["model_activation_invoked"] is False
    assert first["verbatim_corpus_source_retained"] is False
    assert first["authoritative_float_weights_created"] is False
    assert first["validation_receipt"]["candidate_structure_validated"] is True
    assert first["validation_receipt"]["canonical_mutation_permitted"] is False

    payload = {
        "schema": "HHS-P218-I24-EVIDENCE-V1",
        "iteration": 24,
        "frozen_i23_predecessor_hash72": first["i23_contextual_state_hash72"],
        "beat_id_hash72": first["beat_id"],
        "narrative_beat_hash72": first["narrative_beat_hash72"],
        "successor_candidate_root": first["successor_candidate_root"],
        "validation_receipt_hash72": first["validation_receipt"][
            "validation_receipt_hash72"
        ],
        "source_sha256": source_sha256,
        "curriculum_identity_hash72": curriculum_identity_hash72,
        "evidence_payload_hash72": evidence_payload_hash72,
        "deterministic_replay_equal": True,
        "context_change_produces_distinct_beat": True,
        "candidate_relation_count": len(first["candidate_relations"]),
        "contradiction_candidate_count": len(first["contradiction_changes"]),
        "hydrated_node_count": first["hydrated_relational_neighborhood"][
            "hydrated_node_count"
        ],
        "attention_active_count": first["hydrated_relational_neighborhood"][
            "attention_active_count"
        ],
        "revisable_narrative_beat_candidate": True,
        "admitted_predecessor_state": False,
        "natural_language_projection_generated": False,
        "perspective_hydration_invoked": False,
        "grounded_relational_manifold_ready": False,
        "hash216_continuation_verified": False,
        "vm81_authorization_invoked": False,
        "authoritative_semantic_compression_ready": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "canonical_learning_commit_invoked": False,
        "model_activation_invoked": False,
        "verbatim_corpus_source_retained": False,
        "authoritative_float_weights_created": False,
    }
    raw = canonical_bytes(payload) + b"\n"
    output_root = Path(".i24-evidence")
    output_root.mkdir(parents=True, exist_ok=True)
    evidence_path = output_root / "pass218_iteration24_evidence.json"
    evidence_path.write_bytes(raw)
    digest = sha256(raw).hexdigest()
    (output_root / "pass218_iteration24_evidence.sha256").write_text(
        digest + "  " + evidence_path.name + "\n",
        encoding="utf-8",
    )
    print(json.dumps({**payload, "evidence_sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
