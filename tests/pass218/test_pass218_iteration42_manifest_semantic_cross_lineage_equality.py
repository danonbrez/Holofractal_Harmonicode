from __future__ import annotations

import ast
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_backend.runtime_os_pass218_hash216_vm5184_validation_i29 import (
    Pass218I29RuntimeValidationControl,
)
from hhs_backend.runtime_os_pass218_manifest_semantic_cross_lineage_equality_i42 import (
    PASS218_I42_PROVE_PATH,
    PASS218_I42_STATUS_PATH,
    install_pass218_i42_manifest_semantic_cross_lineage_equality_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.atomic_semantic_promotion_i30 import PASS218_I30_TARGET_SCOPE
from hhs_runtime.pass218.curriculum import (
    CurriculumCursor,
    CurriculumSource,
    CurriculumStage,
    build_curriculum_manifest,
)
from hhs_runtime.pass218.curriculum_advance_i33 import Pass218I33CurriculumAuthority
from hhs_runtime.pass218.grammar import compile_grammar_rules
from hhs_runtime.pass218.grounded_manifold_i26 import Pass218I26ManifoldRequest
from hhs_runtime.pass218.hash216_vm5184_transition_i28 import Pass218I28TransitionRequest
from hhs_runtime.pass218.hash216_vm5184_validation_i29 import (
    PASS218_I29_VALIDATION_SCHEMA,
    Pass218I29ValidationRequest,
)
from hhs_runtime.pass218.hydration import NarrativeBeatHydrator
from hhs_runtime.pass218.manifest_bound_canonical_commit_persistence_i40 import (
    Pass218I40ManifestBoundCanonicalCommitPersistence,
)
from hhs_runtime.pass218.manifest_bound_canonical_learning_ingress_i41 import (
    Pass218I41ManifestBoundCanonicalLearningIngress,
)
from hhs_runtime.pass218.manifest_bound_canonical_prepare_i39 import (
    Pass218I39ManifestBoundCanonicalPrepare,
)
from hhs_runtime.pass218.manifest_bound_promotion_admission_proof_i37 import (
    Pass218I37ManifestBoundPromotionAdmissionProof,
)
from hhs_runtime.pass218.manifest_bound_promotion_authorization_i38 import (
    Pass218I38ManifestBoundPromotionAuthorization,
)
from hhs_runtime.pass218.manifest_bound_semantic_source_transaction_i35 import (
    Pass218I35ManifestBoundSemanticSourceTransaction,
)
from hhs_runtime.pass218.manifest_bound_source_ingress_i34 import (
    Pass218I34ManifestBoundSourceIngress,
)
from hhs_runtime.pass218.manifest_bound_vector_vm5184_staging_i36 import (
    Pass218I36ManifestBoundVectorVM5184Staging,
)
from hhs_runtime.pass218.manifest_semantic_cross_lineage_equality_i42 import (
    PASS218_I42_COMPLETE_STATUS,
    Pass218I42BindingError,
    Pass218I42ManifestSemanticCrossLineageEquality,
    Pass218I42StateError,
)
from hhs_runtime.pass218.narrative_beat_i24 import Pass218I24BeatRequest
from hhs_runtime.pass218.perspective_context_i25 import (
    Pass218I25PerspectiveProfile,
    Pass218I25PerspectiveRequest,
)

ROOT = Path(__file__).resolve().parents[2]
GRAMMAR_PATH = ROOT / "hhs_runtime" / "Grammar Correction.csv"


def h72(domain: str, value: object) -> str:
    return hash72_digest({"domain": domain}, value)


class ReadyLifecycle:
    def __init__(self, ready: bool = True) -> None:
        self.ready = ready

    def require_ingestion_ready(self) -> None:
        if not self.ready:
            raise RuntimeError("P218_I9_CANONICAL_WRITER_REQUIRED")

    def status(self):
        return {"ingestion_enabled": self.ready}


class EmptyI30:
    def __init__(self, promotion_present: bool = False) -> None:
        self.promotion_present = promotion_present

    def status(self):
        return {
            "target_scope": PASS218_I30_TARGET_SCOPE,
            "promotion_present": self.promotion_present,
            "atomic_promotion_invoked": self.promotion_present,
        }


def make_authority(source: bytes) -> Pass218I33CurriculumAuthority:
    genesis = h72("HHS-P218-I42-TEST-GENESIS-V1", {"suite": "cross-lineage-equality"})
    manifest = build_curriculum_manifest(
        genesis,
        (
            CurriculumSource(
                source_id="source-i42.md",
                stage=CurriculumStage.REFERENCE,
                locator="source-i42.md",
                checksum_sha256=sha256(source).hexdigest(),
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


def make_candidate(source: bytes, authority: Pass218I33CurriculumAuthority):
    fake_seed = SimpleNamespace(
        genesis_seed_hash72=authority.manifest.genesis_seed_hash72,
        payload={"distinctions": []},
    )
    rules = compile_grammar_rules(GRAMMAR_PATH)
    return NarrativeBeatHydrator(paragraphs_per_beat=1).hydrate(
        source.decode("utf-8"),
        source_id="source-i42.md",
        source_epistemic_class="REPOSITORY_NATIVE_REFERENCE",
        genesis_seed=fake_seed,
        grammar_rule_set=rules,
        expected_source_sha256=sha256(source).hexdigest(),
    )


def make_i41(tmp_path: Path, source: bytes):
    lifecycle = ReadyLifecycle()
    authority = make_authority(source)
    state = tmp_path / "state" / "cognition"
    i34 = Pass218I34ManifestBoundSourceIngress(
        lifecycle=lifecycle,
        authority=authority,
        i33_store_root=state / "curriculum-advance-i33",
        ingress_store_root=state / "manifest-source-ingress-i34",
    )
    i34.bind(source_id="source-i42.md", source_bytes=source)
    i35 = Pass218I35ManifestBoundSemanticSourceTransaction(
        lifecycle=lifecycle,
        i34_store_root=state / "manifest-source-ingress-i34",
        transaction_store_root=state / "manifest-semantic-source-transaction-i35",
        manifest_genesis_seed_hash72=authority.manifest.genesis_seed_hash72,
        i34_store=i34.store,
        i34_status_provider=i34.status,
    )
    i35.ingest(semantic_candidate=make_candidate(source, authority), source_bytes=source)
    i36 = Pass218I36ManifestBoundVectorVM5184Staging(
        lifecycle=lifecycle,
        i35_store=i35.store,
        state_root=state / "manifest-vector-vm5184-staging-i36",
        i35_status_provider=i35.status,
    )
    i36.stage()
    i37 = Pass218I37ManifestBoundPromotionAdmissionProof(
        lifecycle=lifecycle,
        i36_store=i36.store,
        i35_store=i35.store,
        state_root=state / "manifest-promotion-admission-proof-i37",
        i36_status_provider=i36.status,
    )
    i37.prove()
    i38 = Pass218I38ManifestBoundPromotionAuthorization(
        lifecycle=lifecycle,
        i37_store=i37.store,
        state_root=state / "manifest-promotion-authorization-i38",
        i37_status_provider=i37.status,
    )
    i38.authorize()
    i39 = Pass218I39ManifestBoundCanonicalPrepare(
        lifecycle=lifecycle,
        i38_store=i38.store,
        i37_store=i37.store,
        i36_store=i36.store,
        state_root=state / "manifest-canonical-prepare-i39",
        i38_status_provider=i38.status,
        i36_status_provider=i36.status,
    )
    i39.prepare()
    i40 = Pass218I40ManifestBoundCanonicalCommitPersistence(
        lifecycle=lifecycle,
        i39_store=i39.store,
        i38_store=i38.store,
        i37_store=i37.store,
        i36_store=i36.store,
        state_root=state / "manifest-canonical-commit-persistence-i40",
        i39_status_provider=i39.status,
    )
    i40.commit_and_persist()
    i41 = Pass218I41ManifestBoundCanonicalLearningIngress(
        lifecycle=lifecycle,
        i40_store=i40.store,
        state_root=state / "manifest-canonical-learning-ingress-i41",
        i40_status_provider=i40.status,
        i30_status_provider=EmptyI30().status,
    )
    i41.admit()
    return lifecycle, authority, i41


def validation_request(
    source: bytes,
    authority: Pass218I33CurriculumAuthority,
    *,
    source_id: str = "source-i42.md",
    curriculum_identity_hash72: str | None = None,
    context_id: str = "i42 transient request marker 5fa2d1",
) -> Pass218I29ValidationRequest:
    beat = Pass218I24BeatRequest(
        tokens=("cross", "lineage", "equality"),
        context_id=context_id,
        curriculum_identity_hash72=(
            curriculum_identity_hash72 or authority.manifest.curriculum_identity_hash72
        ),
        curriculum_position=0,
        source_id=source_id,
        source_checksum_sha256=sha256(source).hexdigest(),
        source_authority="REPOSITORY_NATIVE_CONTRACT_AUTHORITY",
        rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
        evidence_id="i42-equality-evidence",
        evidence_type="RELATIONAL_OBSERVATION",
        evidence_epistemic_status="OBSERVED",
        evidence_payload_hash72=h72("I42-EVIDENCE", "cross-lineage"),
        attention_tokens=("cross", "lineage"),
        top_k=2,
        attention_radius=1,
        max_hydrated_nodes=24,
    ).validated()
    profile = Pass218I25PerspectiveProfile(
        profile_id="i42-cross-lineage-perspective",
        profile_version="v1",
        profile_origin="USER_AUTHORED",
        rules=(),
    ).validated()
    perspective = Pass218I25PerspectiveRequest(
        beat_request=beat,
        perspective_profile=profile,
    ).validated()
    manifold = Pass218I26ManifoldRequest(perspective_request=perspective).validated()
    from hhs_runtime.pass218.formal_analogical_differentiation_i27 import (
        Pass218I27DifferentiationRequest,
    )

    differentiation = Pass218I27DifferentiationRequest(
        manifold_request=manifold
    ).validated()
    return Pass218I29ValidationRequest(
        transition_request=Pass218I28TransitionRequest(
            differentiation_request=differentiation
        ).validated()
    ).validated()


def api_payload(request: Pass218I29ValidationRequest) -> dict:
    perspective = (
        request.transition_request
        .differentiation_request
        .manifold_request
        .perspective_request
    )
    beat = perspective.beat_request
    profile = perspective.perspective_profile
    return {
        "tokens": list(beat.tokens),
        "context_id": beat.context_id,
        "curriculum_identity_hash72": beat.curriculum_identity_hash72,
        "curriculum_position": beat.curriculum_position,
        "source_identity": {
            "source_id": beat.source_id,
            "source_checksum_sha256": beat.source_checksum_sha256,
            "source_authority": beat.source_authority,
            "rights_class": beat.rights_class,
        },
        "evidence": {
            "evidence_id": beat.evidence_id,
            "evidence_type": beat.evidence_type,
            "epistemic_status": beat.evidence_epistemic_status,
            "payload_hash72": beat.evidence_payload_hash72,
        },
        "attention_tokens": list(beat.attention_tokens),
        "top_k": beat.top_k,
        "attention_radius": beat.attention_radius,
        "max_hydrated_nodes": beat.max_hydrated_nodes,
        "allowed_relation_families": list(beat.allowed_relation_families),
        "perspective_profile": {
            "profile_id": profile.profile_id,
            "profile_version": profile.profile_version,
            "profile_origin": profile.profile_origin,
            "rules": [],
        },
    }


class FakeI29Validator:
    def __init__(self) -> None:
        self.validation_count = 0

    def validate(self, request: Pass218I29ValidationRequest) -> dict:
        validated = request.validated()
        beat = (
            validated.transition_request
            .differentiation_request
            .manifold_request
            .perspective_request
            .beat_request
        )
        curriculum = beat.curriculum_identity_hash72
        transition = h72(
            "I42-I29-TRANSITION",
            [beat.source_checksum_sha256, beat.curriculum_position],
        )
        validation_receipt = h72(
            "I42-I29-VALIDATION-RECEIPT",
            [curriculum, transition],
        )
        validated_hash216 = curriculum + transition + validation_receipt
        witness_hash72 = h72(
            "I42-I29-SEMANTIC-WITNESS",
            [beat.source_id, beat.source_checksum_sha256],
        )
        result_body = {
            "schema": PASS218_I29_VALIDATION_SCHEMA,
            "hash216_vm5184_validation_status": (
                "VALIDATED_REVISABLE_HASH216_VM5184_TRANSITION_CANDIDATE"
            ),
            "hash216_vm5184_validation_ready": True,
            "pass218_validated_hash216_segments": {
                "manifest_curriculum_hash72": curriculum,
                "hydrated_transition_state_hash72": transition,
                "validation_receipt_hash72": validation_receipt,
            },
            "pass218_validated_hash216": validated_hash216,
            "validation_receipt": {
                "curriculum_hash72": curriculum,
                "validation_receipt_hash72": validation_receipt,
            },
            "semantic_validation_witness": {
                "semantic_witness_hash72": witness_hash72,
            },
            "hash216_continuation_verified": True,
            "semantic_transition_validated": True,
            "vm5184_candidate_projection_verified": True,
            "candidate_semantic_binding_verified": True,
            "atomic_promotion_candidate_ready": True,
            "atomic_promotion_authorized": False,
            "vm5184_authoritative_projection_invoked": False,
            "vm81_authorization_invoked": False,
            "atomic_promotion_invoked": False,
            "authoritative_semantic_compression_ready": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }
        result = {
            **result_body,
            "hash216_vm5184_validation_hash72": h72(
                "I42-I29-VALIDATION-RESULT",
                result_body,
            ),
        }
        self.validation_count += 1
        return result


class FakeI29Runtime:
    def __init__(self, validator: FakeI29Validator) -> None:
        self.validator = validator

    @staticmethod
    def _request(payload):
        return Pass218I29RuntimeValidationControl._request(payload)


def make_i42(tmp_path: Path, lifecycle, i41, validator, *, i30=None):
    return Pass218I42ManifestSemanticCrossLineageEquality(
        lifecycle=lifecycle,
        i41_store=i41.store,
        i29_validator=validator,
        state_root=tmp_path / "state" / "cognition" / "manifest-semantic-cross-lineage-equality-i42",
        i41_status_provider=i41.status,
        i30_status_provider=(i30 or EmptyI30()).status,
    )


def test_i42_proves_exact_shared_identity_without_invoking_i30(tmp_path: Path) -> None:
    source = b"I42 binds the I41 manifest source identity to independently validated I29 semantics."
    lifecycle, authority, i41 = make_i41(tmp_path, source)
    validator = FakeI29Validator()
    runtime = make_i42(tmp_path, lifecycle, i41, validator)
    receipt = runtime.prove(validation_request(source, authority))
    proof = runtime.store.active_proof()
    assert receipt["status"] == PASS218_I42_COMPLETE_STATUS
    assert receipt["cross_lineage_shared_identity_equal"] is True
    assert receipt["i29_independently_revalidated"] is True
    assert receipt["i30_exact_validation_identity_ready"] is True
    assert receipt["i30_request_synthesized"] is False
    assert receipt["i30_authority_grant_present"] is False
    assert receipt["pass218_i30_canonical_semantic_promotion_invoked"] is False
    assert runtime.i30_invocation_count == 0
    assert validator.validation_count == 1
    assert proof["shared_identity"]["source_sha256"] == sha256(source).hexdigest()
    assert proof["i29_curriculum_hash72"] == authority.manifest.curriculum_identity_hash72
    assert proof["canonical_and_semantic_roots_kept_distinct"] is True


def test_i42_restart_replay_is_idempotent_and_request_exact(tmp_path: Path) -> None:
    source = b"I42 restart proof binds the exact transient typed request fingerprint."
    lifecycle, authority, i41 = make_i41(tmp_path, source)
    validator = FakeI29Validator()
    request = validation_request(source, authority)
    first = make_i42(tmp_path, lifecycle, i41, validator)
    receipt = first.prove(request)
    assert first.prove(request) == receipt
    assert validator.validation_count == 1
    restarted = make_i42(tmp_path, lifecycle, i41, validator)
    assert restarted.prove(request) == receipt
    assert validator.validation_count == 1
    alternate = validation_request(
        source,
        authority,
        context_id="different transient request must not alias existing proof",
    )
    with pytest.raises(Pass218I42StateError, match="P218_I42_ACTIVE_REQUEST_CONFLICT"):
        restarted.prove(alternate)


def test_i42_rejects_cross_lineage_source_or_curriculum_mismatch(tmp_path: Path) -> None:
    source = b"I42 rejects any mismatch between I41 manifest identity and I29 request identity."
    lifecycle, authority, i41 = make_i41(tmp_path, source)
    validator = FakeI29Validator()
    runtime = make_i42(tmp_path, lifecycle, i41, validator)
    with pytest.raises(Pass218I42BindingError, match="P218_I42_CROSS_LINEAGE_MISMATCH:source_id_equal"):
        runtime.prove(validation_request(source, authority, source_id="wrong-source.md"))
    assert runtime.store.active_record() is None

    other_curriculum = h72("I42-WRONG-CURRICULUM", "wrong")
    with pytest.raises(Pass218I42BindingError, match="P218_I42_CROSS_LINEAGE_MISMATCH:curriculum_identity_equal"):
        runtime.prove(
            validation_request(
                source,
                authority,
                curriculum_identity_hash72=other_curriculum,
            )
        )
    assert runtime.store.active_record() is None


def test_i42_rejects_existing_i30_promotion(tmp_path: Path) -> None:
    source = b"I42 cannot bridge into an already promoted I30 state."
    lifecycle, authority, i41 = make_i41(tmp_path, source)
    runtime = make_i42(
        tmp_path,
        lifecycle,
        i41,
        FakeI29Validator(),
        i30=EmptyI30(True),
    )
    with pytest.raises(Pass218I42BindingError, match="P218_I42_I30_PREVIOUS_PROMOTION_PENDING"):
        runtime.prove(validation_request(source, authority))
    assert runtime.store.active_record() is None


def test_i42_persists_no_transient_request_or_verbatim_source(tmp_path: Path) -> None:
    source = b"I42 forbidden verbatim payload 5fa2d1 must never enter durable equality state."
    marker = "i42 transient request marker 8c1e77 must not persist"
    lifecycle, authority, i41 = make_i41(tmp_path, source)
    runtime = make_i42(tmp_path, lifecycle, i41, FakeI29Validator())
    runtime.prove(validation_request(source, authority, context_id=marker))
    for path in runtime.store.root.rglob("*"):
        if path.is_file():
            payload = path.read_bytes()
            assert source not in payload
            assert marker.encode("utf-8") not in payload
            assert b"tokens" not in payload
            assert b"context_id" not in payload


def test_runtimeos_i42_accepts_transient_i29_request_but_not_i30_authority(tmp_path: Path) -> None:
    source = b"RuntimeOS I42 reconstructs a typed I29 request and persists only its fingerprint."
    lifecycle, authority, i41 = make_i41(tmp_path, source)
    validator = FakeI29Validator()
    app = FastAPI()
    i41_control = SimpleNamespace(ingress=i41, status=i41.status)
    i29_control = FakeI29Runtime(validator)
    control = install_pass218_i42_manifest_semantic_cross_lineage_equality_control(
        app,
        i41_control,
        i29_control,
        EmptyI30(),
        lifecycle,
        state_root=tmp_path / "runtime-os-state",
    )
    client = TestClient(app)
    before = client.get(PASS218_I42_STATUS_PATH).json()
    assert before["api_can_supply_transient_i29_validation_request"] is True
    assert before["api_can_supply_raw_source_payload"] is False
    assert before["api_can_supply_i29_validation_result"] is False
    assert before["api_can_supply_i30_authority_grant"] is False
    assert before["api_can_invoke_i30_canonical_promotion"] is False
    request = validation_request(source, authority)
    response = client.post(PASS218_I42_PROVE_PATH, json=api_payload(request))
    assert response.status_code == 200
    assert response.json()["status"] == PASS218_I42_COMPLETE_STATUS
    assert control.equality.i30_invocation_count == 0
    assert validator.validation_count == 1


def test_i42_authoritative_python_surface_contains_no_float_literals() -> None:
    paths = [
        ROOT / "hhs_runtime" / "pass218" / "manifest_semantic_cross_lineage_equality_i42.py",
        ROOT / "hhs_backend" / "runtime_os_pass218_manifest_semantic_cross_lineage_equality_i42.py",
    ]
    for path in paths:
        tree = ast.parse(path.read_text("utf-8"))
        floats = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, str(path)
