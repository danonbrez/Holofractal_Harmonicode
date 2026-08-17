from __future__ import annotations

import ast
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.runtime_os_pass218_manifest_canonical_learning_ingress_i41 import (
    PASS218_I41_ADMIT_PATH,
    PASS218_I41_STATUS_PATH,
    install_pass218_i41_manifest_canonical_learning_ingress_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.atomic_semantic_promotion_i30 import PASS218_I30_TARGET_SCOPE
from hhs_runtime.pass218.curriculum import CurriculumCursor, CurriculumSource, CurriculumStage, build_curriculum_manifest
from hhs_runtime.pass218.curriculum_advance_i33 import Pass218I33CurriculumAuthority
from hhs_runtime.pass218.grammar import compile_grammar_rules
from hhs_runtime.pass218.hydration import NarrativeBeatHydrator
from hhs_runtime.pass218.manifest_bound_canonical_commit_persistence_i40 import Pass218I40ManifestBoundCanonicalCommitPersistence
from hhs_runtime.pass218.manifest_bound_canonical_learning_ingress_i41 import (
    PASS218_I41_COMPLETE_STATUS,
    Pass218I41BindingError,
    Pass218I41ManifestBoundCanonicalLearningIngress,
)
from hhs_runtime.pass218.manifest_bound_canonical_prepare_i39 import Pass218I39ManifestBoundCanonicalPrepare
from hhs_runtime.pass218.manifest_bound_promotion_admission_proof_i37 import Pass218I37ManifestBoundPromotionAdmissionProof
from hhs_runtime.pass218.manifest_bound_promotion_authorization_i38 import Pass218I38ManifestBoundPromotionAuthorization
from hhs_runtime.pass218.manifest_bound_semantic_source_transaction_i35 import Pass218I35ManifestBoundSemanticSourceTransaction
from hhs_runtime.pass218.manifest_bound_source_ingress_i34 import Pass218I34ManifestBoundSourceIngress
from hhs_runtime.pass218.manifest_bound_vector_vm5184_staging_i36 import Pass218I36ManifestBoundVectorVM5184Staging

ROOT = Path(__file__).resolve().parents[2]
GRAMMAR_PATH = ROOT / "hhs_runtime" / "Grammar Correction.csv"


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
    genesis = hash72_digest(
        {"domain": "HHS-P218-I41-TEST-GENESIS-V1"},
        {"suite": "manifest-canonical-learning-ingress"},
    )
    manifest = build_curriculum_manifest(
        genesis,
        (
            CurriculumSource(
                source_id="source-i41.md",
                stage=CurriculumStage.REFERENCE,
                locator="source-i41.md",
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
        source_id="source-i41.md",
        source_epistemic_class="REPOSITORY_NATIVE_REFERENCE",
        genesis_seed=fake_seed,
        grammar_rule_set=rules,
        expected_source_sha256=sha256(source).hexdigest(),
    )


def make_i40(tmp_path: Path, source: bytes):
    lifecycle = ReadyLifecycle()
    authority = make_authority(source)
    state = tmp_path / "state" / "cognition"
    i34 = Pass218I34ManifestBoundSourceIngress(
        lifecycle=lifecycle,
        authority=authority,
        i33_store_root=state / "curriculum-advance-i33",
        ingress_store_root=state / "manifest-source-ingress-i34",
    )
    i34.bind(source_id="source-i41.md", source_bytes=source)
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
    return lifecycle, i40


def make_i41(tmp_path: Path, lifecycle, i40, *, i30=None, status=None):
    return Pass218I41ManifestBoundCanonicalLearningIngress(
        lifecycle=lifecycle,
        i40_store=i40.store,
        state_root=tmp_path / "state" / "cognition" / "manifest-canonical-learning-ingress-i41",
        i40_status_provider=status or i40.status,
        i30_status_provider=(i30 or EmptyI30()).status,
    )


def test_i41_binds_exact_i40_canonical_root_without_invoking_i30(tmp_path: Path) -> None:
    lifecycle, i40 = make_i40(tmp_path, b"I41 binds durable I40 canonical state to later independent I30 validation.")
    runtime = make_i41(tmp_path, lifecycle, i40)
    receipt = runtime.admit()
    i40_receipt = i40.store.active_record()
    assert receipt["status"] == PASS218_I41_COMPLETE_STATUS
    assert receipt["i40_receipt_hash72"] == i40_receipt["i40_receipt_hash72"]
    assert receipt["i40_canonical_root_hash72"] == i40_receipt["i6_target_root_after_hash72"]
    assert receipt["target_surface"] == PASS218_I30_TARGET_SCOPE
    assert receipt["i30_exact_i27_i29_lineage_required"] is True
    assert receipt["i30_independent_validation_required"] is True
    assert receipt["i30_request_synthesized"] is False
    assert receipt["pass218_i30_canonical_semantic_promotion_invoked"] is False
    assert runtime.i30_invocation_count == 0


def test_i41_restart_replay_is_idempotent(tmp_path: Path) -> None:
    lifecycle, i40 = make_i40(tmp_path, b"I41 restart replay keeps one durable ingress identity.")
    first = make_i41(tmp_path, lifecycle, i40)
    receipt = first.admit()
    assert first.admit() == receipt
    assert first.admission_count == 1
    restarted = make_i41(tmp_path, lifecycle, i40)
    assert restarted.admit() == receipt
    assert restarted.admission_count == 0
    assert restarted.i30_invocation_count == 0


def test_i41_rejects_stale_i40_status(tmp_path: Path) -> None:
    lifecycle, i40 = make_i40(tmp_path, b"I41 requires the currently active I40 durable receipt.")
    runtime = make_i41(
        tmp_path,
        lifecycle,
        i40,
        status=lambda: {
            "status": "MANIFEST_BOUND_CANONICAL_COMMIT_PERSISTENCE_INGRESS_COMPLETE",
            "active_i40_receipt_hash72": "z" * 72,
            "canonical_root_hash72": i40.store.active_record()["i6_target_root_after_hash72"],
        },
    )
    with pytest.raises(Pass218I41BindingError, match="P218_I41_I40_STATUS_RECEIPT_MISMATCH"):
        runtime.admit()


def test_i41_rejects_i30_pending_promotion(tmp_path: Path) -> None:
    lifecycle, i40 = make_i40(tmp_path, b"I41 cannot ambiguously join an existing I30 promotion.")
    runtime = make_i41(tmp_path, lifecycle, i40, i30=EmptyI30(True))
    with pytest.raises(Pass218I41BindingError, match="P218_I41_I30_PREVIOUS_PROMOTION_PENDING"):
        runtime.admit()
    assert runtime.store.active_record() is None


def test_i41_stops_before_downstream_authority(tmp_path: Path) -> None:
    lifecycle, i40 = make_i40(tmp_path, b"I41 admits only a non-authoritative learning ingress candidate.")
    receipt = make_i41(tmp_path, lifecycle, i40).admit()
    for field in (
        "source_payload_persisted",
        "verbatim_corpus_source_retained",
        "i30_request_synthesized",
        "pass218_i30_canonical_semantic_promotion_invoked",
        "pass218_i31_verbatim_purge_invoked",
        "pass218_i32_source_closure_invoked",
        "curriculum_cursor_advanced",
        "stage_advance_permitted",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "authoritative_float_weights_created",
    ):
        assert receipt[field] is False


def test_i41_durable_state_contains_no_verbatim_source(tmp_path: Path) -> None:
    source = b"I41 forbidden verbatim phrase d4c7ab must not persist in the I41 store."
    lifecycle, i40 = make_i40(tmp_path, source)
    runtime = make_i41(tmp_path, lifecycle, i40)
    runtime.admit()
    for path in runtime.store.root.rglob("*"):
        if path.is_file():
            payload = path.read_bytes()
            assert source not in payload
            assert b"source_text" not in payload
            assert b"raw_source" not in payload


def test_runtimeos_i41_route_is_parameterless_and_cannot_expand_authority(tmp_path: Path) -> None:
    lifecycle, i40 = make_i40(tmp_path, b"RuntimeOS I41 admits only exact repository-derived I40 state.")
    app = FastAPI()
    i40_control = SimpleNamespace(commit_membrane=i40, status=i40.status)
    i30_control = EmptyI30()
    control = install_pass218_i41_manifest_canonical_learning_ingress_control(
        app,
        i40_control,
        i30_control,
        lifecycle,
        state_root=tmp_path / "runtime-os-state",
    )
    client = TestClient(app)
    status = client.get(PASS218_I41_STATUS_PATH).json()
    assert status["api_can_supply_source_payload"] is False
    assert status["api_can_supply_i29_validation"] is False
    assert status["api_can_supply_i30_authority_grant"] is False
    assert status["api_can_invoke_i30_canonical_promotion"] is False
    response = client.post(PASS218_I41_ADMIT_PATH)
    assert response.status_code == 200
    assert response.json()["status"] == PASS218_I41_COMPLETE_STATUS
    assert client.post(PASS218_I41_ADMIT_PATH, json={"source": "forbidden"}).status_code == 200
    assert control.ingress.i30_invocation_count == 0


def test_i41_authoritative_python_surface_contains_no_float_literals() -> None:
    paths = [
        ROOT / "hhs_runtime" / "pass218" / "manifest_bound_canonical_learning_ingress_i41.py",
        ROOT / "hhs_backend" / "runtime_os_pass218_manifest_canonical_learning_ingress_i41.py",
    ]
    for path in paths:
        tree = ast.parse(path.read_text("utf-8"))
        floats = [node for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, float)]
        assert not floats, str(path)
