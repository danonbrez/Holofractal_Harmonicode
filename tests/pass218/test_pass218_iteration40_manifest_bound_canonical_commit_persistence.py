from __future__ import annotations

import ast
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.runtime_os_pass218_manifest_canonical_commit_persistence_i40 import (
    PASS218_I40_COMMIT_PATH,
    PASS218_I40_STATUS_PATH,
    install_pass218_i40_manifest_canonical_commit_persistence_control,
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
from hhs_runtime.pass218.manifest_bound_canonical_commit_persistence_i40 import (
    PASS218_I40_COMPLETE_STATUS,
    Pass218I40BindingError,
    Pass218I40ManifestBoundCanonicalCommitPersistence,
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


class FakeI39Store:
    def __init__(self, receipt, prepare) -> None:
        self.receipt = receipt
        self.prepare = prepare

    def active_record(self):
        return json.loads(json.dumps(self.receipt))

    def active_prepare(self):
        return json.loads(json.dumps(self.prepare))


def make_authority(source: bytes) -> Pass218I33CurriculumAuthority:
    genesis = hash72_digest(
        {"domain": "HHS-P218-I40-TEST-GENESIS-V1"},
        {"suite": "manifest-canonical-commit-persistence"},
    )
    manifest = build_curriculum_manifest(
        genesis,
        (
            CurriculumSource(
                source_id="source-i40.md",
                stage=CurriculumStage.REFERENCE,
                locator="source-i40.md",
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
        source_id="source-i40.md",
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
    i34.bind(source_id="source-i40.md", source_bytes=source)
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
    return lifecycle, i35, i36, i37, i38, i39


def make_i40(tmp_path: Path, i36, i37, i38, i39, *, lifecycle=None, status=None):
    return Pass218I40ManifestBoundCanonicalCommitPersistence(
        lifecycle=lifecycle or ReadyLifecycle(),
        i39_store=i39.store,
        i38_store=i38.store,
        i37_store=i37.store,
        i36_store=i36.store,
        state_root=tmp_path / "state" / "cognition" / "manifest-canonical-commit-persistence-i40",
        i39_status_provider=status or i39.status,
    )


def test_i40_commits_exact_i39_prepare_and_durably_restores_it(tmp_path: Path) -> None:
    source = b"I40 atomically admits the exact I39 projection and durably restores the canonical VM81 state."
    _, _, i36, i37, i38, i39 = make_chain(tmp_path, source)
    runtime = make_i40(tmp_path, i36, i37, i38, i39)
    receipt = runtime.commit_and_persist()
    assert receipt["status"] == PASS218_I40_COMPLETE_STATUS
    assert receipt["i39_receipt_hash72"] == i39.store.active_record()["i39_receipt_hash72"]
    assert receipt["pass218_i6_canonical_commit_invoked"] is True
    assert receipt["canonical_vector_store_mutation_invoked"] is True
    assert receipt["canonical_vm81_commit_invoked"] is True
    assert receipt["i6_authorization_consumed"] is True
    assert receipt["i6_atomic_swap"] is True
    assert receipt["pass218_i7_durable_persistence_invoked"] is True
    assert receipt["i7_checkpoint_durable"] is True
    assert receipt["i7_restore_verified"] is True
    assert receipt["i6_vm81_commit_count"] == THREADS == 64
    assert receipt["i7_vm81_snapshot_bytes"] == SNAPSHOT_BYTES == 648
    assert runtime.i6_prepare_reconstruction_count == 1
    assert runtime.i6_commit_invocation_count == 1
    assert runtime.i7_checkpoint_invocation_count == 1
    assert runtime.i7_restore_invocation_count == 1


def test_i40_reconstructed_i6_prepare_is_bit_exact_to_i39(tmp_path: Path) -> None:
    source = b"The I6 live prepare object may be reconstructed only when its durable proof is bit exact to I39."
    _, _, i36, i37, i38, i39 = make_chain(tmp_path, source)
    expected = i39.store.active_prepare()["i6_prepare_record"]
    runtime = make_i40(tmp_path, i36, i37, i38, i39)
    receipt = runtime.commit_and_persist()
    binding = runtime.store.active_binding()
    assert binding is not None
    assert receipt["i6_prepare_hash72"] == expected["prepare_hash72"]
    assert binding["i6_commit_receipt"]["prepare_hash72"] == expected["prepare_hash72"]
    assert receipt["i6_prepare_reconstructed_exactly"] is True


def test_i40_same_process_and_restart_replay_do_not_commit_twice(tmp_path: Path) -> None:
    source = b"One I39 authorization crosses the atomic canonical boundary exactly once across durable replay."
    _, _, i36, i37, i38, i39 = make_chain(tmp_path, source)
    first = make_i40(tmp_path, i36, i37, i38, i39)
    receipt = first.commit_and_persist()
    assert first.commit_and_persist() == receipt
    assert first.i6_commit_invocation_count == 1
    assert first.i7_checkpoint_invocation_count == 1

    restarted = make_i40(tmp_path, i36, i37, i38, i39)
    assert restarted.commit_and_persist() == receipt
    assert restarted.i6_prepare_reconstruction_count == 0
    assert restarted.i6_commit_invocation_count == 0
    assert restarted.i7_checkpoint_invocation_count == 0


def test_i40_recovers_i7_durable_state_when_final_i40_binding_is_missing(tmp_path: Path) -> None:
    source = b"Durable I7 state is sufficient to recover the I40 binding without a second canonical commit."
    _, _, i36, i37, i38, i39 = make_chain(tmp_path, source)
    first = make_i40(tmp_path, i36, i37, i38, i39)
    receipt = first.commit_and_persist()
    store = first.store
    for path in list(store.receipt_root.glob("*.json")) + list(store.binding_root.glob("*.json")):
        path.unlink()
    store.state_path.unlink()

    restarted = make_i40(tmp_path, i36, i37, i38, i39)
    recovered = restarted.commit_and_persist()
    assert recovered == receipt
    assert restarted.i6_prepare_reconstruction_count == 0
    assert restarted.i6_commit_invocation_count == 0
    assert restarted.i7_checkpoint_invocation_count == 0
    assert restarted.i7_restore_invocation_count == 1


def test_i40_stops_after_canonical_commit_and_i7_persistence(tmp_path: Path) -> None:
    source = b"I40 canonical admission does not authorize later learning truth action or curriculum boundaries."
    _, _, i36, i37, i38, i39 = make_chain(tmp_path, source)
    receipt = make_i40(tmp_path, i36, i37, i38, i39).commit_and_persist()
    for field in (
        "source_payload_persisted",
        "verbatim_corpus_source_retained",
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


def test_i40_durable_state_contains_no_verbatim_source(tmp_path: Path) -> None:
    source = b"I40 forbidden verbatim phrase a41d8c must never persist after canonical admission."
    _, _, i36, i37, i38, i39 = make_chain(tmp_path, source)
    runtime = make_i40(tmp_path, i36, i37, i38, i39)
    runtime.commit_and_persist()
    for path in runtime.store.root.rglob("*"):
        if path.is_file():
            payload = path.read_bytes()
            assert source not in payload
            assert b"source_text" not in payload
            assert b"raw_source" not in payload


def test_i40_rejects_tampered_i39_prepare_before_i6_commit(tmp_path: Path) -> None:
    source = b"Tampered I39 prepare identity must fail before the canonical I6 swap."
    _, _, i36, i37, i38, i39 = make_chain(tmp_path, source)
    receipt = i39.store.active_record()
    prepare = i39.store.active_prepare()
    tampered = json.loads(json.dumps(prepare))
    tampered["i6_prepare_record"]["prepare_hash72"] = "z" * 72
    runtime = Pass218I40ManifestBoundCanonicalCommitPersistence(
        lifecycle=ReadyLifecycle(),
        i39_store=FakeI39Store(receipt, tampered),
        i38_store=i38.store,
        i37_store=i37.store,
        i36_store=i36.store,
        state_root=tmp_path / "tampered-i40",
    )
    with pytest.raises(Exception):
        runtime.commit_and_persist()
    assert runtime.i6_commit_invocation_count == 0
    assert not runtime.store.i7_store.manifest_path.exists()


def test_i40_requires_current_i39_and_writer_fence(tmp_path: Path) -> None:
    source = b"The frozen current I39 receipt and writer fence remain mandatory for canonical mutation."
    _, _, i36, i37, i38, i39 = make_chain(tmp_path, source)
    stale = make_i40(
        tmp_path,
        i36,
        i37,
        i38,
        i39,
        status=lambda: {
            "status": "MANIFEST_BOUND_CANONICAL_PREPARE_INGRESS_COMPLETE",
            "active_i39_receipt_hash72": "z" * 72,
        },
    )
    with pytest.raises(Pass218I40BindingError, match="P218_I40_I39_STATUS_RECEIPT_MISMATCH"):
        stale.commit_and_persist()
    assert stale.i6_commit_invocation_count == 0

    fenced = make_i40(tmp_path / "fenced", i36, i37, i38, i39, lifecycle=ReadyLifecycle(False))
    with pytest.raises(RuntimeError, match="P218_I9_CANONICAL_WRITER_REQUIRED"):
        fenced.commit_and_persist()
    assert fenced.i6_commit_invocation_count == 0


def test_runtimeos_i40_route_is_parameterless_and_cannot_expand_authority(tmp_path: Path) -> None:
    source = b"RuntimeOS I40 may request only the exact frozen canonical commit and durability transaction."
    lifecycle, i35, i36, i37, i38, i39 = make_chain(tmp_path, source)
    app = FastAPI()
    i35_control = SimpleNamespace(ingress=SimpleNamespace(store=i35.store), status=i35.status)
    i36_control = SimpleNamespace(staging=SimpleNamespace(store=i36.store), i35_control=i35_control, status=i36.status)
    i37_control = SimpleNamespace(proof=SimpleNamespace(store=i37.store), i36_control=i36_control, status=i37.status)
    i38_control = SimpleNamespace(authorization=SimpleNamespace(store=i38.store), i37_control=i37_control, status=i38.status)
    i39_control = SimpleNamespace(prepare_membrane=i39, i38_control=i38_control, i36_control=i36_control, status=i39.status)
    control = install_pass218_i40_manifest_canonical_commit_persistence_control(
        app,
        i39_control,
        i38_control,
        i36_control,
        lifecycle,
        state_root=tmp_path / "runtimeos-state",
    )
    client = TestClient(app)
    status = client.get(PASS218_I40_STATUS_PATH)
    assert status.status_code == 200
    assert status.json()["api_can_supply_i39_prepare"] is False
    assert status.json()["api_can_supply_i38_authorization"] is False
    assert status.json()["api_can_override_canonical_target_root"] is False
    assert status.json()["api_can_invoke_canonical_learning"] is False
    response = client.post(
        PASS218_I40_COMMIT_PATH,
        json={"projection": "attacker", "target_root": "attacker", "truth": True},
    )
    assert response.status_code == 200
    receipt = response.json()
    assert receipt["pass218_i6_canonical_commit_invoked"] is True
    assert receipt["pass218_i7_durable_persistence_invoked"] is True
    assert receipt["truth_promotion"] is False
    assert receipt["action_authority_minted"] is False
    assert control.commit_membrane.i6_commit_invocation_count == 1


def test_no_float_literals_in_iteration40_authority_modules() -> None:
    paths = (
        ROOT / "hhs_runtime" / "pass218" / "manifest_bound_canonical_commit_persistence_i40.py",
        ROOT / "hhs_backend" / "runtime_os_pass218_manifest_canonical_commit_persistence_i40.py",
    )
    for path in paths:
        tree = ast.parse(path.read_text("utf-8"))
        floats = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, path
