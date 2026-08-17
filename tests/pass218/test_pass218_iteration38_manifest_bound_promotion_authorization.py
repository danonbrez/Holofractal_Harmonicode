from __future__ import annotations

import ast
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.runtime_os_pass218_manifest_promotion_authorization_i38 import (
    PASS218_I38_AUTHORIZE_PATH,
    PASS218_I38_STATUS_PATH,
    install_pass218_i38_manifest_promotion_authorization_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.curriculum import (
    CurriculumCursor,
    CurriculumSource,
    CurriculumStage,
    build_curriculum_manifest,
)
from hhs_runtime.pass218.curriculum_advance_i33 import Pass218I33CurriculumAuthority
from hhs_runtime.pass218.grammar import compile_grammar_rules
from hhs_runtime.pass218.hydration import NarrativeBeatHydrator
from hhs_runtime.pass218.manifest_bound_promotion_admission_proof_i37 import (
    Pass218I37ManifestBoundPromotionAdmissionProof,
)
from hhs_runtime.pass218.manifest_bound_promotion_authorization_i38 import (
    PASS218_I38_COMPLETE_STATUS,
    Pass218I38BindingError,
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
from hhs_runtime.pass218.promotion import PROMOTION_SCOPE

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


class FakeI37Store:
    def __init__(self, receipt: dict[str, object], proof: dict[str, object]) -> None:
        self.receipt = receipt
        self.proof = proof

    def active_record(self):
        return json.loads(json.dumps(self.receipt))

    def active_proof(self):
        return json.loads(json.dumps(self.proof))


def make_authority(source: bytes) -> Pass218I33CurriculumAuthority:
    genesis = hash72_digest(
        {"domain": "HHS-P218-I38-TEST-GENESIS-V1"},
        {"suite": "manifest-promotion-authorization"},
    )
    manifest = build_curriculum_manifest(
        genesis,
        (
            CurriculumSource(
                source_id="source-i38.md",
                stage=CurriculumStage.REFERENCE,
                locator="source-i38.md",
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
        source_id="source-i38.md",
        source_epistemic_class="REPOSITORY_NATIVE_REFERENCE",
        genesis_seed=fake_seed,
        grammar_rule_set=rules,
        expected_source_sha256=sha256(source).hexdigest(),
    )


def make_i37_complete(tmp_path: Path, source: bytes):
    lifecycle = ReadyLifecycle()
    authority = make_authority(source)
    state = tmp_path / "state" / "cognition"
    i34 = Pass218I34ManifestBoundSourceIngress(
        lifecycle=lifecycle,
        authority=authority,
        i33_store_root=state / "curriculum-advance-i33",
        ingress_store_root=state / "manifest-source-ingress-i34",
    )
    i34.bind(source_id="source-i38.md", source_bytes=source)
    i35 = Pass218I35ManifestBoundSemanticSourceTransaction(
        lifecycle=lifecycle,
        i34_store_root=state / "manifest-source-ingress-i34",
        transaction_store_root=state / "manifest-semantic-source-transaction-i35",
        manifest_genesis_seed_hash72=authority.manifest.genesis_seed_hash72,
        i34_store=i34.store,
        i34_status_provider=i34.status,
    )
    i35.ingest(
        semantic_candidate=make_candidate(source, authority),
        source_bytes=source,
    )
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
    return lifecycle, authority, i35, i36, i37


def make_i38(tmp_path: Path, i37, *, lifecycle=None, status_provider=None):
    return Pass218I38ManifestBoundPromotionAuthorization(
        lifecycle=lifecycle or ReadyLifecycle(),
        i37_store=i37.store,
        state_root=tmp_path / "state" / "cognition" / "manifest-promotion-authorization-i38",
        i37_status_provider=status_provider or i37.status,
    )


def test_i38_binds_frozen_i37_proof_to_explicit_i5_grant_and_authorization(tmp_path: Path) -> None:
    source = b"Promotability becomes explicitly authorized without crossing the I6 commit membrane."
    _, _, _, _, i37 = make_i37_complete(tmp_path, source)
    i37_receipt = i37.store.active_record()
    assert i37_receipt is not None
    runtime = make_i38(tmp_path, i37)
    receipt = runtime.authorize()
    grant = runtime.active_grant()
    authorization = runtime.active_authorization()

    assert receipt["status"] == PASS218_I38_COMPLETE_STATUS
    assert receipt["i37_receipt_hash72"] == i37_receipt["i37_receipt_hash72"]
    assert receipt["manifest_binding"] == i37_receipt["manifest_binding"]
    assert receipt["i5_explicit_authority_grant_present"] is True
    assert receipt["i5_promotion_authorization_invoked"] is True
    assert receipt["i5_authorized_pending_canonical_commit"] is True
    assert receipt["canonical_mutation_permitted"] is True
    assert runtime.i5_grant_invocation_count == 1
    assert runtime.i5_authorize_invocation_count == 1

    assert grant is not None
    assert authorization is not None
    assert grant["grantor_authority_hash72"] == i37_receipt["manifest_binding"]["authority_root_hash72"]
    assert grant["grant_sequence"] == i37_receipt["manifest_binding"]["curriculum_position"]
    assert grant["target_scope"] == PROMOTION_SCOPE
    assert authorization["state"] == "AUTHORIZED_PENDING_CANONICAL_COMMIT"
    assert authorization["entry_id_sha256"] == i37_receipt["i4_entry_id_sha256"]
    assert authorization["projection_sha256"] == i37_receipt["i4_projection_sha256"]


def test_i38_same_process_and_restart_replay_do_not_reauthorize(tmp_path: Path) -> None:
    source = b"One exact I37 proof receives one durable authorization across restart."
    _, _, _, _, i37 = make_i37_complete(tmp_path, source)
    first = make_i38(tmp_path, i37)
    receipt = first.authorize()
    assert first.i5_grant_invocation_count == 1
    assert first.i5_authorize_invocation_count == 1
    assert first.authorize() == receipt
    assert first.i5_grant_invocation_count == 1
    assert first.i5_authorize_invocation_count == 1

    restarted = make_i38(tmp_path, i37)
    assert restarted.authorize() == receipt
    assert restarted.i5_grant_invocation_count == 0
    assert restarted.i5_authorize_invocation_count == 0
    assert restarted.active_authorization() == first.active_authorization()


def test_i38_durable_state_does_not_retain_source_text(tmp_path: Path) -> None:
    source = b"I38 forbidden verbatim phrase 38d9aa must never persist in authorization state."
    _, _, _, _, i37 = make_i37_complete(tmp_path, source)
    runtime = make_i38(tmp_path, i37)
    receipt = runtime.authorize()
    for path in runtime.store.root.rglob("*"):
        if path.is_file():
            assert source not in path.read_bytes()
    assert receipt["source_payload_persisted"] is False
    assert receipt["verbatim_corpus_source_retained"] is False


def test_i38_rejects_i37_authority_drift_before_grant(tmp_path: Path) -> None:
    source = b"I37 authority drift must fail closed before the explicit grant is constructed."
    _, _, _, _, i37 = make_i37_complete(tmp_path, source)
    receipt = i37.store.active_record()
    proof = i37.store.active_proof()
    assert receipt is not None and proof is not None
    tampered = json.loads(json.dumps(receipt))
    tampered["canonical_mutation_permitted"] = True
    runtime = Pass218I38ManifestBoundPromotionAuthorization(
        lifecycle=ReadyLifecycle(),
        i37_store=FakeI37Store(tampered, proof),
        state_root=tmp_path / "tampered-i37-i38",
    )
    with pytest.raises(Pass218I38BindingError, match="P218_I38_I37_AUTHORITY_DRIFT"):
        runtime.authorize()
    assert runtime.i5_grant_invocation_count == 0
    assert runtime.i5_authorize_invocation_count == 0


def test_i38_rejects_i37_proof_envelope_drift_before_grant(tmp_path: Path) -> None:
    source = b"The exact manifest-bound I37 proof envelope is part of authorization identity."
    _, _, _, _, i37 = make_i37_complete(tmp_path, source)
    receipt = i37.store.active_record()
    proof = i37.store.active_proof()
    assert receipt is not None and proof is not None
    tampered = json.loads(json.dumps(proof))
    tampered["manifest_binding"]["source_id"] = "tampered-source"
    runtime = Pass218I38ManifestBoundPromotionAuthorization(
        lifecycle=ReadyLifecycle(),
        i37_store=FakeI37Store(receipt, tampered),
        state_root=tmp_path / "tampered-proof-i38",
    )
    with pytest.raises(Pass218I38BindingError, match="P218_I38_I37_PROOF_ENVELOPE_HASH_MISMATCH"):
        runtime.authorize()
    assert runtime.i5_grant_invocation_count == 0


def test_i37_status_drift_fails_before_i5_authorization(tmp_path: Path) -> None:
    source = b"Only the currently active frozen I37 receipt may receive I5 authorization."
    _, _, _, _, i37 = make_i37_complete(tmp_path, source)
    runtime = make_i38(
        tmp_path,
        i37,
        status_provider=lambda: {
            "status": "MANIFEST_BOUND_PROMOTION_ADMISSION_PROOF_INGRESS_COMPLETE",
            "active_i37_receipt_hash72": "z" * 72,
            "manifest_bound_i5_proof_hash72": i37.store.active_record()["manifest_bound_i5_proof_hash72"],
        },
    )
    with pytest.raises(Pass218I38BindingError, match="P218_I38_I37_STATUS_RECEIPT_MISMATCH"):
        runtime.authorize()
    assert runtime.i5_grant_invocation_count == 0
    assert runtime.i5_authorize_invocation_count == 0


def test_i38_authorization_stops_before_i6_and_all_later_authority(tmp_path: Path) -> None:
    source = b"Authorization is a precondition only; canonical execution remains a separate boundary."
    _, _, _, _, i37 = make_i37_complete(tmp_path, source)
    receipt = make_i38(tmp_path, i37).authorize()
    for field in (
        "pass218_i6_canonical_commit_invoked",
        "pass218_i30_canonical_semantic_promotion_invoked",
        "pass218_i31_verbatim_purge_invoked",
        "pass218_i32_source_closure_invoked",
        "curriculum_cursor_advanced",
        "stage_advance_permitted",
        "vm81_authorization_invoked",
        "truth_promotion",
        "action_authority_minted",
        "authoritative_vector_store_promotion",
        "canonical_vector_store_mutation_invoked",
        "canonical_vm81_commit_invoked",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "authoritative_float_weights_created",
    ):
        assert receipt[field] is False


def test_runtimeos_i38_authorize_route_cannot_override_grant_identity(tmp_path: Path) -> None:
    source = b"RuntimeOS can authorize only the active I37 proof with the frozen manifest authority root."
    lifecycle, _, i35, i36, i37 = make_i37_complete(tmp_path, source)
    app = FastAPI()
    i35_control = SimpleNamespace(ingress=SimpleNamespace(store=i35.store), status=i35.status)
    i36_control = SimpleNamespace(
        staging=SimpleNamespace(store=i36.store),
        i35_control=i35_control,
        status=i36.status,
    )
    i37_control = SimpleNamespace(
        proof=SimpleNamespace(store=i37.store),
        i36_control=i36_control,
        status=i37.status,
    )
    control = install_pass218_i38_manifest_promotion_authorization_control(
        app,
        i37_control,
        lifecycle,
        state_root=tmp_path / "runtimeos-state",
    )
    client = TestClient(app)

    before = client.get(PASS218_I38_STATUS_PATH)
    assert before.status_code == 200
    assert before.json()["api_can_supply_grantor_authority"] is False
    assert before.json()["api_can_supply_grant_sequence"] is False
    assert before.json()["api_can_invoke_i6_canonical_commit"] is False

    response = client.post(
        PASS218_I38_AUTHORIZE_PATH,
        json={"grantor_authority_hash72": "attacker", "grant_sequence": 999},
    )
    assert response.status_code == 200
    receipt = response.json()
    assert receipt["i5_grantor_authority_hash72"] == receipt["manifest_binding"]["authority_root_hash72"]
    assert receipt["i5_grant_sequence"] == receipt["manifest_binding"]["curriculum_position"]
    assert control.authorization.i5_authorize_invocation_count == 1


def test_i38_requires_real_writer_fence(tmp_path: Path) -> None:
    source = b"The writer fence remains mandatory before I38 can create promotion authorization."
    _, _, _, _, i37 = make_i37_complete(tmp_path, source)
    runtime = make_i38(tmp_path, i37, lifecycle=ReadyLifecycle(False))
    with pytest.raises(RuntimeError, match="P218_I9_CANONICAL_WRITER_REQUIRED"):
        runtime.authorize()
    assert runtime.i5_grant_invocation_count == 0
    assert runtime.i5_authorize_invocation_count == 0


def test_no_float_literals_in_iteration38_authority_modules() -> None:
    paths = (
        ROOT / "hhs_runtime" / "pass218" / "manifest_bound_promotion_authorization_i38.py",
        ROOT / "hhs_backend" / "runtime_os_pass218_manifest_promotion_authorization_i38.py",
    )
    for path in paths:
        tree = ast.parse(path.read_text("utf-8"))
        floats = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, path
