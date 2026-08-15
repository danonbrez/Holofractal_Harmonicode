#!/usr/bin/env python3
"""Emit deterministic Pass 218 Iteration 33 authoritative curriculum evidence."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from hhs_backend.runtime_os_pass218_narrative_beat_i24 import (
    Pass218I24RuntimeNarrativeBeatControl,
)
from hhs_backend.runtime_os_pass218_perspective_context_i25 import (
    Pass218I25RuntimePerspectiveContextControl,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.atomic_semantic_promotion_i30 import (
    PASS218_I30_TARGET_SCOPE,
    Pass218I30AtomicSemanticPromoter,
    Pass218I30PromotionRequest,
)
from hhs_runtime.pass218.curriculum import (
    CurriculumCursor,
    CurriculumSource,
    CurriculumStage,
    build_curriculum_manifest,
)
from hhs_runtime.pass218.curriculum_advance_i33 import (
    PASS218_I33_COMPLETE_STATUS,
    Pass218I33CurriculumAdvancer,
    Pass218I33CurriculumAuthority,
    Pass218I33CurriculumBindingError,
)
from hhs_runtime.pass218.formal_analogical_differentiation_i27 import (
    Pass218I27DifferentiationRequest,
    Pass218I27FormalAnalogicalDifferentiator,
)
from hhs_runtime.pass218.grounded_manifold_i26 import (
    Pass218I26GroundedRelationalManifold,
    Pass218I26ManifoldRequest,
)
from hhs_runtime.pass218.hash216_vm5184_transition_i28 import (
    Pass218I28Hash216VM5184Transition,
    Pass218I28TransitionRequest,
)
from hhs_runtime.pass218.hash216_vm5184_validation_i29 import (
    Pass218I29Hash216VM5184Validator,
    Pass218I29ValidationRequest,
)
from hhs_runtime.pass218.lifecycle_i9 import Pass218MultiprocessRuntimeLifecycle
from hhs_runtime.pass218.narrative_beat_i24 import Pass218I24BeatRequest
from hhs_runtime.pass218.perspective_context_i25 import (
    Pass218I25PerspectiveProfile,
    Pass218I25PerspectiveRequest,
    Pass218I25PerspectiveRule,
)
from hhs_runtime.pass218.source_closure_i32 import (
    PASS218_I32_CLOSURE_SCOPE,
    Pass218I32ClosureRequest,
    Pass218I32SourceCloser,
)
from hhs_runtime.pass218.verbatim_purge_i31 import (
    PASS218_I31_PURGE_SCOPE,
    Pass218I31PurgeRequest,
    Pass218I31VerbatimPurger,
)
from scripts.pass218_iteration24_narrative_beat_validation import I23EvidenceAdapter
from scripts.pass218_iteration31_verbatim_purge_validation import (
    FROZEN_I29_VALIDATED_HASH216,
    FROZEN_I29_VALIDATION_HASH72,
    build_frozen_chain,
    make_purge_request,
    promote_exact_i30,
)
from scripts.pass218_iteration32_source_closure_validation import (
    FROZEN_I31_PURGE_GATE_ROOT_HASH72,
    FROZEN_I31_PURGE_HASH216,
    FROZEN_I31_PURGE_RECEIPT_HASH72,
    FROZEN_I31_PURGE_VALIDATION_HASH72,
    SOURCE_NAME,
    make_closure_request,
)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def build_authority(repository_root: Path, source_sha256: str):
    manifest = build_curriculum_manifest(
        hash72_digest(
            {"domain": "HHS-P218-I33-EVIDENCE-GENESIS-V1"},
            {"repository": repository_root.name, "source": SOURCE_NAME},
        ),
        (
            CurriculumSource(
                source_id=SOURCE_NAME,
                stage=CurriculumStage.EXPOSITORY,
                locator=SOURCE_NAME,
                checksum_sha256=source_sha256,
                rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
                source_authority="REPOSITORY_NATIVE_CONTRACT_AUTHORITY",
                media_type="text/markdown",
            ),
        ),
    )
    return Pass218I33CurriculumAuthority(
        manifest=manifest,
        initial_cursor=CurriculumCursor.for_manifest(manifest),
    ).validated()


def build_authoritative_chain(
    repository_root: Path,
    *,
    curriculum_identity_hash72: str,
    source_sha256: str,
):
    evidence_payload_hash72 = hash72_digest(
        {"domain": "HHS-P218-I33-EVIDENCE-PAYLOAD-V1"},
        {
            "source_sha256": source_sha256,
            "observation": "AUTHORITATIVE_CURRICULUM_ADVANCE_CONTRACT_PRESENT",
            "verbatim_retained": False,
        },
    )
    rule_payload_hash72 = hash72_digest(
        {"domain": "HHS-P218-I33-EVIDENCE-PERSPECTIVE-RULE-V1"},
        {
            "principle": "ADVANCE_ONLY_AFTER_AUTHORITATIVE_CURRICULUM_MATCH",
            "manifest_match_required": True,
            "cursor_match_required": True,
            "stage_advance_deferred": True,
        },
    )

    i23 = I23EvidenceAdapter(repository_root)
    i24 = Pass218I24RuntimeNarrativeBeatControl(i23)
    i25 = Pass218I25RuntimePerspectiveContextControl(i24)
    i26 = Pass218I26GroundedRelationalManifold(i25)
    i27 = Pass218I27FormalAnalogicalDifferentiator(i26)
    i28 = Pass218I28Hash216VM5184Transition(i27)
    i29 = Pass218I29Hash216VM5184Validator(i28, i27)

    beat_request = Pass218I24BeatRequest(
        tokens=("relational", "grounding", "context"),
        context_id="pass218 authoritative curriculum advancement",
        curriculum_identity_hash72=curriculum_identity_hash72,
        curriculum_position=0,
        source_id=SOURCE_NAME,
        source_checksum_sha256=source_sha256,
        source_authority="REPOSITORY_NATIVE_CONTRACT_AUTHORITY",
        rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
        evidence_id="pass218-i33-authoritative-curriculum-observation",
        evidence_type="REPOSITORY_CONTRACT_OBSERVATION",
        evidence_epistemic_status="OBSERVED",
        evidence_payload_hash72=evidence_payload_hash72,
        attention_tokens=("relational", "grounding"),
        top_k=2,
        attention_radius=1,
        max_hydrated_nodes=16,
    ).validated()
    profile = Pass218I25PerspectiveProfile(
        profile_id="repository-native-authoritative-curriculum-perspective",
        profile_version="i33-v1",
        profile_origin="USER_AUTHORED",
        rules=(
            Pass218I25PerspectiveRule(
                rule_id="organize-authoritative-curriculum-salience",
                rule_payload_hash72=rule_payload_hash72,
                salience_delta=5,
            ),
        ),
    ).validated()
    perspective = Pass218I25PerspectiveRequest(beat_request, profile).validated()
    manifold = Pass218I26ManifoldRequest(perspective).validated()
    differentiation = Pass218I27DifferentiationRequest(manifold).validated()
    transition = Pass218I28TransitionRequest(differentiation).validated()
    validation_request = Pass218I29ValidationRequest(transition).validated()
    validation = i29.validate(validation_request)
    assert validation["pass218_validated_hash216"][:72] == curriculum_identity_hash72

    grantor_authority_hash72 = hash72_digest(
        {"domain": "HHS-P218-I33-EVIDENCE-PROMOTION-AUTHORITY-V1"},
        {
            "source_sha256": source_sha256,
            "i29_validation_hash72": validation["hash216_vm5184_validation_hash72"],
            "validated_hash216": validation["pass218_validated_hash216"],
            "target_scope": PASS218_I30_TARGET_SCOPE,
            "grant_sequence": 33,
        },
    )
    promotion_request = Pass218I30PromotionRequest(
        validation_request=validation_request,
        grantor_authority_hash72=grantor_authority_hash72,
        grant_sequence=33,
        expected_i29_validation_hash72=validation["hash216_vm5184_validation_hash72"],
        expected_validated_hash216=validation["pass218_validated_hash216"],
        target_scope=PASS218_I30_TARGET_SCOPE,
    ).validated()
    return i27, i29, promotion_request, validation


def positive_path(repository_root: Path, source_sha256: str, authority):
    i27, i29, promotion_request, validation = build_authoritative_chain(
        repository_root,
        curriculum_identity_hash72=authority.manifest.curriculum_identity_hash72,
        source_sha256=source_sha256,
    )
    with TemporaryDirectory(prefix="hhs-pass218-i33-authoritative-") as temporary:
        state_root = Path(temporary) / "pass218-state"
        lifecycle = Pass218MultiprocessRuntimeLifecycle(state_root)
        startup = lifecycle.startup()
        assert startup["ingestion_enabled"] is True
        assert startup["ownership_writer_authority"] is True
        try:
            promoter = Pass218I30AtomicSemanticPromoter(
                i29,
                i27,
                lifecycle=lifecycle,
                store_root=state_root / "cognition" / "atomic-semantic-promotion-i30",
            )
            promotion = promoter.promote(promotion_request)
            purger = Pass218I31VerbatimPurger(
                lifecycle=lifecycle,
                i30_store_root=promoter.store.root,
                purge_store_root=state_root / "cognition" / "verbatim-purge-i31",
            )
            purge = purger.purge(
                Pass218I31PurgeRequest(
                    expected_i30_promotion_receipt_hash72=str(
                        promotion["promotion_receipt_hash72"]
                    ),
                    expected_i30_promotion_hash72=str(promotion["promotion_hash72"]),
                    expected_promoted_object_hash72=str(
                        promotion["promoted_object_hash72"]
                    ),
                    expected_canonical_root_hash72=str(
                        promotion["target_root_after_hash72"]
                    ),
                    expected_i29_validation_hash72=str(
                        promotion["i29_validation_hash72"]
                    ),
                    purge_scope=PASS218_I31_PURGE_SCOPE,
                ).validated()
            )
            closer = Pass218I32SourceCloser(
                lifecycle=lifecycle,
                i31_store_root=purger.store.root,
                closure_store_root=state_root / "cognition" / "source-closure-i32",
            )
            closure_request = Pass218I32ClosureRequest(
                expected_i31_purge_receipt_hash72=str(purge["purge_receipt_hash72"]),
                expected_i31_purge_validation_hash72=str(
                    purge["purge_validation_hash72"]
                ),
                expected_i31_purge_gate_root_hash72=str(purge["purge_gate_root_hash72"]),
                expected_i31_purge_hash216=str(purge["purge_hash216"]),
                expected_i30_promotion_receipt_hash72=str(
                    purge["i30_promotion_receipt_hash72"]
                ),
                expected_promoted_object_hash72=str(purge["promoted_object_hash72"]),
                expected_canonical_root_hash72=str(purge["canonical_root_hash72"]),
                source_id=SOURCE_NAME,
                source_sha256=source_sha256,
                source_authority="REPOSITORY_NATIVE_CONTRACT_AUTHORITY",
                rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
                curriculum_identity_hash72=authority.manifest.curriculum_identity_hash72,
                curriculum_position=0,
                source_stage=int(CurriculumStage.EXPOSITORY),
                previous_closure_hash72=None,
                closure_scope=PASS218_I32_CLOSURE_SCOPE,
            ).validated()
            closure = closer.close(closure_request)
            advancer = Pass218I33CurriculumAdvancer(
                lifecycle=lifecycle,
                i32_store_root=closer.store.root,
                advance_store_root=state_root / "cognition" / "curriculum-advance-i33",
                authority=authority,
            )
            first = advancer.advance()
            replay = advancer.advance()
            assert first == replay
            assert first["advance_status"] == PASS218_I33_COMPLETE_STATUS
            assert first["curriculum_cursor_advanced"] is True
            assert first["source_binding_matches_authoritative_manifest"] is True
            assert first["upstream_semantic_curriculum_binding_verified"] is True
            assert first["stage_advance_permitted"] is False
            assert first["next_cursor"]["next_ordinal"] == 1
            assert first["next_cursor"]["last_closure_hash72"] == closure[
                "source_closure_hash72"
            ]
            restarted = Pass218I33CurriculumAdvancer(
                lifecycle=lifecycle,
                i32_store_root=closer.store.root,
                advance_store_root=state_root / "cognition" / "curriculum-advance-i33",
                authority=authority,
            )
            assert restarted.advance() == first
            return {
                "authoritative_i29_validation_hash72": validation[
                    "hash216_vm5184_validation_hash72"
                ],
                "authoritative_validated_hash216": validation[
                    "pass218_validated_hash216"
                ],
                "authoritative_i30_promotion_receipt_hash72": promotion[
                    "promotion_receipt_hash72"
                ],
                "authoritative_i31_purge_receipt_hash72": purge[
                    "purge_receipt_hash72"
                ],
                "authoritative_i32_source_closure_hash72": closure[
                    "source_closure_hash72"
                ],
                "i33_transition_hash72": first["transition_hash72"],
                "i33_advance_validation_hash72": first[
                    "i33_advance_validation_hash72"
                ],
                "i33_advance_receipt_hash72": first["advance_receipt_hash72"],
                "i33_advance_hash216": first["advance_hash216"],
                "i33_authority_root_hash72": first["authority_root_hash72"],
                "i33_manifest_hash72": first["manifest_hash72"],
                "i33_curriculum_identity_hash72": first[
                    "curriculum_identity_hash72"
                ],
                "i33_cursor_state_sha256": first["cursor_state_sha256"],
                "deterministic_replay_equal": True,
                "restart_replay_equal": True,
            }
        finally:
            lifecycle.shutdown()


def frozen_lineage_negative(
    repository_root: Path,
    source_sha256: str,
    authority,
):
    (
        frozen_source_sha256,
        i27,
        i29,
        promotion_request,
        frozen_validation,
    ) = build_frozen_chain(repository_root)
    assert frozen_source_sha256 == source_sha256
    assert frozen_validation["pass218_validated_hash216"] == FROZEN_I29_VALIDATED_HASH216
    assert frozen_validation["hash216_vm5184_validation_hash72"] == FROZEN_I29_VALIDATION_HASH72

    with TemporaryDirectory(prefix="hhs-pass218-i33-frozen-negative-") as temporary:
        state_root = Path(temporary) / "pass218-state"
        lifecycle = Pass218MultiprocessRuntimeLifecycle(state_root)
        startup = lifecycle.startup()
        assert startup["ingestion_enabled"] is True
        try:
            promoter, promotion = promote_exact_i30(
                state_root, lifecycle, i29, i27, promotion_request
            )
            purger = Pass218I31VerbatimPurger(
                lifecycle=lifecycle,
                i30_store_root=promoter.store.root,
                purge_store_root=state_root / "cognition" / "verbatim-purge-i31",
            )
            purge = purger.purge(make_purge_request(promotion))
            assert purge["purge_validation_hash72"] == FROZEN_I31_PURGE_VALIDATION_HASH72
            assert purge["purge_receipt_hash72"] == FROZEN_I31_PURGE_RECEIPT_HASH72
            assert purge["purge_gate_root_hash72"] == FROZEN_I31_PURGE_GATE_ROOT_HASH72
            assert purge["purge_hash216"] == FROZEN_I31_PURGE_HASH216
            closer = Pass218I32SourceCloser(
                lifecycle=lifecycle,
                i31_store_root=purger.store.root,
                closure_store_root=state_root / "cognition" / "source-closure-i32",
            )
            frozen_closure = closer.close(make_closure_request(source_sha256, purge))
            advancer = Pass218I33CurriculumAdvancer(
                lifecycle=lifecycle,
                i32_store_root=closer.store.root,
                advance_store_root=state_root / "cognition" / "curriculum-advance-i33",
                authority=authority,
            )
            try:
                advancer.advance()
            except Pass218I33CurriculumBindingError as exc:
                error = str(exc)
                assert error.startswith(
                    "P218_I33_AUTHORITATIVE_CURRICULUM_MISMATCH:"
                )
            else:
                raise AssertionError(
                    "frozen non-authoritative curriculum claim advanced unexpectedly"
                )
            assert advancer.store.state_record() is None
            return {
                "frozen_i32_curriculum_identity_hash72": frozen_closure[
                    "curriculum_identity_hash72"
                ],
                "frozen_i32_source_closure_hash72": frozen_closure[
                    "source_closure_hash72"
                ],
                "frozen_i32_closure_chain_root_hash72": frozen_closure[
                    "closure_chain_root_hash72"
                ],
                "frozen_lineage_authoritative_advance_rejected": True,
                "frozen_lineage_cursor_unchanged": True,
                "frozen_lineage_error": error,
            }
        finally:
            lifecycle.shutdown()


def main() -> None:
    repository_root = Path.cwd().resolve()
    source_path = repository_root / SOURCE_NAME
    source_sha256 = sha256(source_path.read_bytes()).hexdigest()
    authority = build_authority(repository_root, source_sha256)

    positive = positive_path(repository_root, source_sha256, authority)
    negative = frozen_lineage_negative(repository_root, source_sha256, authority)

    payload = {
        "schema": "HHS-P218-I33-EVIDENCE-V1",
        "iteration": 33,
        "source_id": SOURCE_NAME,
        "source_sha256": source_sha256,
        "authority_manifest_source_count": len(authority.manifest.sources),
        "authority_initial_ordinal": authority.initial_cursor.next_ordinal,
        "authoritative_advance_path_verified": True,
        "api_can_mint_curriculum_authority": False,
        "stage_advance_permitted": False,
        "vm81_authorization_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "canonical_learning_commit_invoked": False,
        "model_activation_invoked": False,
        "verbatim_corpus_source_retained": False,
        "authoritative_float_weights_created": False,
        **positive,
        **negative,
    }
    raw = canonical_bytes(payload) + b"\n"
    output_root = Path(".i33-evidence")
    output_root.mkdir(parents=True, exist_ok=True)
    evidence_path = output_root / "pass218_iteration33_evidence.json"
    evidence_path.write_bytes(raw)
    digest = sha256(raw).hexdigest()
    (output_root / "pass218_iteration33_evidence.sha256").write_text(
        digest + "  " + evidence_path.name + "\n",
        encoding="utf-8",
    )

    assert validate_hash72(payload["i33_transition_hash72"])
    assert validate_hash72(payload["i33_advance_validation_hash72"])
    assert validate_hash72(payload["i33_advance_receipt_hash72"])
    assert len(payload["i33_advance_hash216"]) == 216
    print(json.dumps({**payload, "evidence_sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
