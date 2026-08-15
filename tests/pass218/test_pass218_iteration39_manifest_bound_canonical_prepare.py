from __future__ import annotations

import ast
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.runtime_os_pass218_manifest_canonical_prepare_i39 import (
    PASS218_I39_PREPARE_PATH,
    PASS218_I39_STATUS_PATH,
    install_pass218_i39_manifest_canonical_prepare_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass163.vmrc import SNAPSHOT_BYTES, THREADS
from hhs_runtime.pass218.curriculum import (
    CurriculumCursor,
    CurriculumSource,
    CurriculumStage,
    build_curriculum_manifest,
)
from hhs_runtime.pass218.curriculum_advance_i33 import Pass218I33CurriculumAuthority
from hhs_runtime.pass218.grammar import compile_grammar_rules
from hhs_runtime.pass218.hydration import NarrativeBeatHydrator
from hhs_runtime.pass218.manifest_bound_canonical_prepare_i39 import (
    PASS218_I39_COMPLETE_STATUS,
    Pass218I39BindingError,
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


class FakeI38Store:
    def __init__(self, receipt: dict[str, object], envelope: dict[str, object]) -> None:
        self.receipt = receipt
        self.envelope = envelope

    def active_record(self):
        return json.loads(json.dumps(self.receipt))

    def active_authorization_envelope(self):
        return json.loads(json.dumps(self.envelope))

    def active_authorization(self):
        return json.loads(json.dumps(self.envelope["i5_promotion_authorization"]))


def make_authority(source: bytes) -> Pass218I33CurriculumAuthority:
    genesis = hash72_digest(
        {"domain": "HHS-P218-I39-TEST-GENESIS-V1"},
        {"suite": "manifest-canonical-prepare"},
    )
    manifest = build_curriculum_manifest(
        genesis,
        (
            CurriculumSource(
                source_id="source-i39.md",
                stage=CurriculumStage.REFERENCE,
                locator="source-i39.md",
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
        source_id="source-i39.md",
        source_epistemic_class="REPOSITORY_NATIVE_REFERENCE",
        genesis_seed=fake_seed,
        grammar_rule_set=rules,
        expected_source_sha256=sha256(source).hexdigest(),
    )


def make_chain(tmp_path: Path, source: bytes):
    lifecycle = ReadyLifecycle()
    authority = make_authority(source)
    state = tmp_path / "state" / "cognition"
    i34 = Pass218I34ManifestBoundSourceIngress(
        lifecycle=lifecycle,
        authority=authority,
        i33_store_root=state / "curriculum-advance-i33",
        ingress_store_root=state / "manifest-source-ingress-i34",
    )
    i34.bind(source_id="source-i39.md", source_bytes=source)
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
    return lifecycle, i35, i36, i37, i38


def make_i39(tmp_path: Path, i36, i37, i38, *, lifecycle=None, i38_status=None, i36_status=None):
    return Pass218I39ManifestBoundCanonicalPrepare(
        lifecycle=lifecycle or ReadyLifecycle(),
        i38_store=i38.store,
        i37_store=i37.store,
        i36_store=i36.store,
        state_root=tmp_path / "state" / "cognition" / "manifest-canonical-prepare-i39",
        i38_status_provider=i38_status or i38.status,
        i36_status_provider=i36_status or i36.status,
    )


def test_i39_binds_exact_i38_authorization_to_frozen_i6_shadow_prepare(tmp_path: Path) -> None:
    source = b"I39 proves the exact authorized projection through a noncanonical VM81 shadow image."
    _, _, i36, i37, i38 = make_chain(tmp_path, source)
    i38_receipt = i38.store.active_record()
    i36_receipt = i36.store.active_record()
    assert i38_receipt is not None and i36_receipt is not None

    runtime = make_i39(tmp_path, i36, i37, i38)
    receipt = runtime.prepare()
    envelope = runtime.store.active_prepare()
    assert envelope is not None
    prepared = envelope["i6_prepare_record"]

    assert receipt["status"] == PASS218_I39_COMPLETE_STATUS
    assert receipt["i38_receipt_hash72"] == i38_receipt["i38_receipt_hash72"]
    assert receipt["manifest_bound_i4_stage_hash72"] == i36_receipt["manifest_bound_i4_stage_hash72"]
    assert receipt["manifest_binding"] == i38_receipt["manifest_binding"]
    assert receipt["pass218_i6_prepare_invoked"] is True
    assert receipt["i6_prepare_noncanonical"] is True
    assert receipt["i6_vm81_shadow_prepare_complete"] is True
    assert receipt["i6_vm81_shadow_commit_count"] == THREADS == 64
    assert receipt["i6_projection_bytes"] == SNAPSHOT_BYTES == 648
    assert prepared["vm81_prepared_snapshot_hash72"] == prepared["projection_hash72"]
    assert runtime.i6_prepare_invocation_count == 1


def test_i39_same_process_and_restart_replay_do_not_prepare_twice(tmp_path: Path) -> None:
    source = b"One exact I38 authorization produces one durable I6 shadow preparation across restart."
    _, _, i36, i37, i38 = make_chain(tmp_path, source)
    first = make_i39(tmp_path, i36, i37, i38)
    receipt = first.prepare()
    assert first.i6_prepare_invocation_count == 1
    assert first.prepare() == receipt
    assert first.i6_prepare_invocation_count == 1

    restarted = make_i39(tmp_path, i36, i37, i38)
    assert restarted.prepare() == receipt
    assert restarted.i6_prepare_invocation_count == 0
    assert restarted.store.active_prepare() == first.store.active_prepare()


def test_i39_prepare_stops_before_canonical_commit_and_i7_persistence(tmp_path: Path) -> None:
    source = b"Prepare proves VM81 admission without crossing the atomic canonical or persistence membrane."
    _, _, i36, i37, i38 = make_chain(tmp_path, source)
    receipt = make_i39(tmp_path, i36, i37, i38).prepare()
    for field in (
        "pass218_i6_canonical_commit_invoked",
        "pass218_i7_durable_persistence_invoked",
        "pass218_i30_canonical_semantic_promotion_invoked",
        "pass218_i31_verbatim_purge_invoked",
        "pass218_i32_source_closure_invoked",
        "curriculum_cursor_advanced",
        "stage_advance_permitted",
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


def test_i39_durable_state_contains_no_verbatim_source_or_projection_payload(tmp_path: Path) -> None:
    source = b"I39 forbidden verbatim phrase 39e7bb must never persist in canonical prepare state."
    _, _, i36, i37, i38 = make_chain(tmp_path, source)
    runtime = make_i39(tmp_path, i36, i37, i38)
    runtime.prepare()
    for path in runtime.store.root.rglob("*"):
        if path.is_file():
            payload = path.read_bytes()
            assert source not in payload
            assert b"vm5184_projection_b64" not in payload
            assert b"source_text" not in payload


def test_i39_rejects_tampered_i38_authorization_before_i6_prepare(tmp_path: Path) -> None:
    source = b"Tampering with durable authorization identity must fail before frozen I6 prepare executes."
    _, _, i36, i37, i38 = make_chain(tmp_path, source)
    receipt = i38.store.active_record()
    envelope = i38.store.active_authorization_envelope()
    assert receipt is not None and envelope is not None
    tampered = json.loads(json.dumps(envelope))
    tampered["i5_promotion_authorization"]["projection_sha256"] = "0" * 64
    runtime = Pass218I39ManifestBoundCanonicalPrepare(
        lifecycle=ReadyLifecycle(),
        i38_store=FakeI38Store(receipt, tampered),
        i37_store=i37.store,
        i36_store=i36.store,
        state_root=tmp_path / "tampered-i39",
    )
    with pytest.raises(Pass218I39BindingError):
        runtime.prepare()
    assert runtime.i6_prepare_invocation_count == 0


def test_i39_rejects_stale_i38_status_before_i6_prepare(tmp_path: Path) -> None:
    source = b"Only the current durable I38 authorization may enter the I6 preparation membrane."
    _, _, i36, i37, i38 = make_chain(tmp_path, source)
    runtime = make_i39(
        tmp_path,
        i36,
        i37,
        i38,
        i38_status=lambda: {
            "status": "MANIFEST_BOUND_PROMOTION_AUTHORIZATION_INGRESS_COMPLETE",
            "active_i38_receipt_hash72": "z" * 72,
        },
    )
    with pytest.raises(Pass218I39BindingError, match="P218_I39_I38_STATUS_RECEIPT_MISMATCH"):
        runtime.prepare()
    assert runtime.i6_prepare_invocation_count == 0


def test_runtimeos_i39_prepare_route_cannot_supply_or_cross_authority(tmp_path: Path) -> None:
    source = b"RuntimeOS I39 can request only the exact frozen noncanonical preparation."
    lifecycle, i35, i36, i37, i38 = make_chain(tmp_path, source)
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
    i38_control = SimpleNamespace(
        authorization=SimpleNamespace(store=i38.store),
        i37_control=i37_control,
        status=i38.status,
    )
    control = install_pass218_i39_manifest_canonical_prepare_control(
        app,
        i38_control,
        i36_control,
        lifecycle,
        state_root=tmp_path / "runtimeos-state",
    )
    client = TestClient(app)
    status = client.get(PASS218_I39_STATUS_PATH)
    assert status.status_code == 200
    assert status.json()["api_can_supply_i38_authorization"] is False
    assert status.json()["api_can_supply_i36_stage"] is False
    assert status.json()["api_can_invoke_i6_canonical_commit"] is False
    assert status.json()["api_can_invoke_i7_durable_persistence"] is False
    assert status.json()["api_can_invoke_canonical_vm81_commit"] is False

    response = client.post(
        PASS218_I39_PREPARE_PATH,
        json={"canonical_commit": True, "projection": "attacker", "target_root": "attacker"},
    )
    assert response.status_code == 200
    receipt = response.json()
    assert receipt["pass218_i6_prepare_invoked"] is True
    assert receipt["pass218_i6_canonical_commit_invoked"] is False
    assert receipt["pass218_i7_durable_persistence_invoked"] is False
    assert control.prepare_membrane.i6_prepare_invocation_count == 1


def test_i39_requires_real_writer_fence(tmp_path: Path) -> None:
    source = b"The writer fence remains mandatory before the 64-lane I6 shadow preparation."
    _, _, i36, i37, i38 = make_chain(tmp_path, source)
    runtime = make_i39(tmp_path, i36, i37, i38, lifecycle=ReadyLifecycle(False))
    with pytest.raises(RuntimeError, match="P218_I9_CANONICAL_WRITER_REQUIRED"):
        runtime.prepare()
    assert runtime.i6_prepare_invocation_count == 0


def test_no_float_literals_in_iteration39_authority_modules() -> None:
    paths = (
        ROOT / "hhs_runtime" / "pass218" / "manifest_bound_canonical_prepare_i39.py",
        ROOT / "hhs_backend" / "runtime_os_pass218_manifest_canonical_prepare_i39.py",
    )
    for path in paths:
        tree = ast.parse(path.read_text("utf-8"))
        floats = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, path
