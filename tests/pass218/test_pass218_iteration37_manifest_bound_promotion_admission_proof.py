from __future__ import annotations

import ast
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.runtime_os_pass218_manifest_promotion_admission_proof_i37 import (
    PASS218_I37_PROVE_PATH,
    PASS218_I37_STATUS_PATH,
    install_pass218_i37_manifest_promotion_admission_proof_control,
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
    PASS218_I37_COMPLETE_STATUS,
    Pass218I37BindingError,
    Pass218I37ManifestBoundPromotionAdmissionProof,
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
from hhs_runtime.pass218.promotion import PromotionProofMembrane

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


class FakeI36Store:
    def __init__(self, receipt: dict[str, object], stage: dict[str, object]) -> None:
        self.receipt = receipt
        self.stage = stage

    def active_record(self):
        return json.loads(json.dumps(self.receipt))

    def active_stage(self):
        return json.loads(json.dumps(self.stage))


class FakeI35Store:
    def __init__(self, snapshot: dict[str, object]) -> None:
        self.snapshot = snapshot

    def active_transaction_snapshot(self):
        return json.loads(json.dumps(self.snapshot))


class SpyProofMembrane:
    def __init__(self) -> None:
        self.calls = 0
        self.delegate = PromotionProofMembrane()

    def prove(self, *, closed_transaction_snapshot, staged_candidate):
        self.calls += 1
        return self.delegate.prove(
            closed_transaction_snapshot=closed_transaction_snapshot,
            staged_candidate=staged_candidate,
        )


def make_authority(source: bytes) -> Pass218I33CurriculumAuthority:
    genesis = hash72_digest(
        {"domain": "HHS-P218-I37-TEST-GENESIS-V1"},
        {"suite": "manifest-promotion-admission-proof"},
    )
    manifest = build_curriculum_manifest(
        genesis,
        (
            CurriculumSource(
                source_id="source-i37.md",
                stage=CurriculumStage.REFERENCE,
                locator="source-i37.md",
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
        source_id="source-i37.md",
        source_epistemic_class="REPOSITORY_NATIVE_REFERENCE",
        genesis_seed=fake_seed,
        grammar_rule_set=rules,
        expected_source_sha256=sha256(source).hexdigest(),
    )


def make_i36_complete(tmp_path: Path, source: bytes):
    lifecycle = ReadyLifecycle()
    authority = make_authority(source)
    i33_root = tmp_path / "state" / "cognition" / "curriculum-advance-i33"
    i34_root = tmp_path / "state" / "cognition" / "manifest-source-ingress-i34"
    i35_root = tmp_path / "state" / "cognition" / "manifest-semantic-source-transaction-i35"
    i36_root = tmp_path / "state" / "cognition" / "manifest-vector-vm5184-staging-i36"
    i34 = Pass218I34ManifestBoundSourceIngress(
        lifecycle=lifecycle,
        authority=authority,
        i33_store_root=i33_root,
        ingress_store_root=i34_root,
    )
    i34.bind(source_id="source-i37.md", source_bytes=source)
    i35 = Pass218I35ManifestBoundSemanticSourceTransaction(
        lifecycle=lifecycle,
        i34_store_root=i34_root,
        transaction_store_root=i35_root,
        manifest_genesis_seed_hash72=authority.manifest.genesis_seed_hash72,
        i34_store=i34.store,
        i34_status_provider=i34.status,
    )
    i35.ingest(
        semantic_candidate=make_candidate(source, authority),
        source_bytes=source,
    )
    snapshot = i35.closed_transaction_snapshot()
    assert snapshot is not None
    i36 = Pass218I36ManifestBoundVectorVM5184Staging(
        lifecycle=lifecycle,
        i35_store=i35.store,
        state_root=i36_root,
        i35_status_provider=i35.status,
    )
    receipt = i36.stage()
    stage = i36.active_stage()
    assert stage is not None
    return lifecycle, i35, i36, receipt, stage, snapshot


def make_i37(tmp_path: Path, i35, i36, *, lifecycle=None, membrane=None):
    return Pass218I37ManifestBoundPromotionAdmissionProof(
        lifecycle=lifecycle or ReadyLifecycle(),
        i36_store=i36.store,
        i35_store=i35.store,
        state_root=(
            tmp_path / "state" / "cognition" / "manifest-promotion-admission-proof-i37"
        ),
        i36_status_provider=i36.status,
        proof_membrane=membrane,
    )


def test_i37_binds_exact_i36_lineage_to_frozen_i5_promotability_proof(tmp_path: Path) -> None:
    source = (
        b"Manifest-bound I4 staging can be proven reproducible without minting "
        b"promotion authority or mutating a canonical target."
    )
    _, i35, i36, i36_receipt, _, _ = make_i36_complete(tmp_path, source)
    runtime = make_i37(tmp_path, i35, i36)
    receipt = runtime.prove()
    envelope = runtime.active_proof()

    assert receipt["status"] == PASS218_I37_COMPLETE_STATUS
    assert receipt["i36_receipt_hash72"] == i36_receipt["i36_receipt_hash72"]
    assert receipt["manifest_bound_i4_stage_hash72"] == i36_receipt["manifest_bound_i4_stage_hash72"]
    assert receipt["manifest_binding"] == i36_receipt["manifest_binding"]
    assert receipt["pass218_i5_promotability_proof_invoked"] is True
    assert receipt["i5_promotable"] is True
    assert receipt["promotability_proof_non_authoritative"] is True
    assert runtime.i5_prove_invocation_count == 1

    assert envelope is not None
    proof = envelope["i5_promotability_proof"]
    assert envelope["i36_receipt_hash72"] == i36_receipt["i36_receipt_hash72"]
    assert envelope["manifest_binding"] == i36_receipt["manifest_binding"]
    assert proof["promotable"] is True
    assert proof["explicit_authority_grant_present"] is False
    assert proof["canonical_mutation_permitted"] is False
    assert proof["entry_id_sha256"] == i36_receipt["i4_entry_id_sha256"]
    assert proof["projection_sha256"] == i36_receipt["i4_projection_sha256"]


def test_i37_same_process_and_restart_replay_do_not_reinvoke_i5(tmp_path: Path) -> None:
    source = b"The exact I36 candidate receives one durable promotability proof across restart."
    _, i35, i36, _, _, _ = make_i36_complete(tmp_path, source)
    spy = SpyProofMembrane()
    first = make_i37(tmp_path, i35, i36, membrane=spy)
    receipt = first.prove()
    assert spy.calls == 1
    assert first.i5_prove_invocation_count == 1

    replay = first.prove()
    assert replay == receipt
    assert spy.calls == 1
    assert first.i5_prove_invocation_count == 1

    restarted_spy = SpyProofMembrane()
    restarted = make_i37(tmp_path, i35, i36, membrane=restarted_spy)
    restored = restarted.prove()
    assert restored == receipt
    assert restarted_spy.calls == 0
    assert restarted.i5_prove_invocation_count == 0
    assert restarted.active_proof() == first.active_proof()


def test_i37_durable_state_does_not_retain_source_text(tmp_path: Path) -> None:
    source = b"I37 forbidden verbatim phrase b736ac must never persist in proof state."
    _, i35, i36, _, _, _ = make_i36_complete(tmp_path, source)
    runtime = make_i37(tmp_path, i35, i36)
    receipt = runtime.prove()
    for path in runtime.store.root.rglob("*"):
        if path.is_file():
            assert source not in path.read_bytes()
    assert receipt["source_payload_persisted"] is False
    assert receipt["verbatim_corpus_source_retained"] is False


def test_tampered_i36_receipt_fails_before_i5_invocation(tmp_path: Path) -> None:
    source = b"Tampered I36 lineage cannot cross into frozen I5 proof construction."
    _, _, _, receipt, stage, snapshot = make_i36_complete(tmp_path, source)
    tampered = json.loads(json.dumps(receipt))
    tampered["i4_entry_id_sha256"] = "0" * 64
    spy = SpyProofMembrane()
    runtime = Pass218I37ManifestBoundPromotionAdmissionProof(
        lifecycle=ReadyLifecycle(),
        i36_store=FakeI36Store(tampered, stage),
        i35_store=FakeI35Store(snapshot),
        state_root=tmp_path / "tampered-i36-receipt-i37",
        proof_membrane=spy,
    )
    with pytest.raises(Pass218I37BindingError, match="P218_I37_I36_RECEIPT_HASH_MISMATCH"):
        runtime.prove()
    assert spy.calls == 0


def test_tampered_i36_stage_fails_before_i5_invocation(tmp_path: Path) -> None:
    source = b"The exact manifest-bound I4 stage envelope is part of I37 identity."
    _, _, _, receipt, stage, snapshot = make_i36_complete(tmp_path, source)
    tampered = json.loads(json.dumps(stage))
    tampered["i4_stage_candidate"]["vector_entry"]["collision_bucket"] += 1
    spy = SpyProofMembrane()
    runtime = Pass218I37ManifestBoundPromotionAdmissionProof(
        lifecycle=ReadyLifecycle(),
        i36_store=FakeI36Store(receipt, tampered),
        i35_store=FakeI35Store(snapshot),
        state_root=tmp_path / "tampered-i36-stage-i37",
        proof_membrane=spy,
    )
    with pytest.raises(Pass218I37BindingError, match="P218_I37_I36_STAGE_HASH_MISMATCH"):
        runtime.prove()
    assert spy.calls == 0


def test_tampered_closed_snapshot_fails_before_i5_invocation(tmp_path: Path) -> None:
    source = b"I37 carries the same exact CLOSED I3 snapshot identity used by I36."
    _, _, _, receipt, stage, snapshot = make_i36_complete(tmp_path, source)
    tampered = json.loads(json.dumps(snapshot))
    tampered["snapshot_hash72"] = "x" * 72
    spy = SpyProofMembrane()
    runtime = Pass218I37ManifestBoundPromotionAdmissionProof(
        lifecycle=ReadyLifecycle(),
        i36_store=FakeI36Store(receipt, stage),
        i35_store=FakeI35Store(tampered),
        state_root=tmp_path / "tampered-snapshot-i37",
        proof_membrane=spy,
    )
    with pytest.raises(Pass218I37BindingError, match="P218_I37_I3_SNAPSHOT_INVALID"):
        runtime.prove()
    assert spy.calls == 0


def test_i36_status_drift_fails_before_i5_invocation(tmp_path: Path) -> None:
    source = b"Only the currently active frozen I36 receipt may enter proof construction."
    _, _, _, receipt, stage, snapshot = make_i36_complete(tmp_path, source)
    spy = SpyProofMembrane()
    runtime = Pass218I37ManifestBoundPromotionAdmissionProof(
        lifecycle=ReadyLifecycle(),
        i36_store=FakeI36Store(receipt, stage),
        i35_store=FakeI35Store(snapshot),
        state_root=tmp_path / "status-drift-i37",
        i36_status_provider=lambda: {
            "status": "MANIFEST_BOUND_VECTOR_VM5184_STAGING_INGRESS_COMPLETE",
            "active_i36_receipt_hash72": "z" * 72,
            "manifest_bound_i4_stage_hash72": receipt["manifest_bound_i4_stage_hash72"],
        },
        proof_membrane=spy,
    )
    with pytest.raises(Pass218I37BindingError, match="P218_I37_I36_STATUS_RECEIPT_MISMATCH"):
        runtime.prove()
    assert spy.calls == 0


def test_i37_proof_does_not_self_grant_or_authorize_canonical_mutation(tmp_path: Path) -> None:
    source = b"Promotability is evidence, not an authority grant or canonical mutation permit."
    _, i35, i36, _, _, _ = make_i36_complete(tmp_path, source)
    receipt = make_i37(tmp_path, i35, i36).prove()
    for field in (
        "pass218_i5_promotion_invoked",
        "i5_explicit_authority_grant_present",
        "i5_promotion_authorization_invoked",
        "canonical_mutation_permitted",
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
        "canonical_vm81_commit_invoked",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "authoritative_float_weights_created",
    ):
        assert receipt[field] is False


def test_runtimeos_i37_prove_route_accepts_no_grant_or_authority_payload(tmp_path: Path) -> None:
    source = b"RuntimeOS can request proof of active I36 state only."
    lifecycle, i35, i36, _, _, _ = make_i36_complete(tmp_path, source)
    app = FastAPI()
    i35_control = SimpleNamespace(ingress=SimpleNamespace(store=i35.store), status=i35.status)
    i36_control = SimpleNamespace(
        staging=SimpleNamespace(store=i36.store),
        i35_control=i35_control,
        status=i36.status,
    )
    control = install_pass218_i37_manifest_promotion_admission_proof_control(
        app,
        i36_control,
        lifecycle,
        state_root=tmp_path / "runtimeos-state",
    )
    client = TestClient(app)

    status = client.get(PASS218_I37_STATUS_PATH)
    assert status.status_code == 200
    assert status.json()["api_can_supply_promotion_grant"] is False
    assert status.json()["api_can_supply_grantor_authority"] is False
    assert status.json()["api_can_invoke_promotion_authorization"] is False
    assert status.json()["api_can_invoke_i6_canonical_commit"] is False

    proven = client.post(PASS218_I37_PROVE_PATH)
    assert proven.status_code == 200
    assert proven.json()["i5_promotable"] is True
    assert proven.json()["canonical_mutation_permitted"] is False
    assert control.proof.i5_prove_invocation_count == 1

    ignored = client.post(
        PASS218_I37_PROVE_PATH,
        json={
            "grantor_authority_hash72": "forged",
            "promotion_grant": {"forged": True},
            "canonical_mutation_permitted": True,
        },
    )
    assert ignored.status_code == 200
    assert ignored.json() == proven.json()
    assert control.proof.i5_prove_invocation_count == 1


def test_i37_writer_fence_failure_stops_before_i5(tmp_path: Path) -> None:
    source = b"The inherited canonical writer fence remains required at I37 proof ingress."
    _, _, _, receipt, stage, snapshot = make_i36_complete(tmp_path, source)
    spy = SpyProofMembrane()
    runtime = Pass218I37ManifestBoundPromotionAdmissionProof(
        lifecycle=ReadyLifecycle(ready=False),
        i36_store=FakeI36Store(receipt, stage),
        i35_store=FakeI35Store(snapshot),
        state_root=tmp_path / "writer-fence-i37",
        proof_membrane=spy,
    )
    with pytest.raises(RuntimeError, match="P218_I9_CANONICAL_WRITER_REQUIRED"):
        runtime.prove()
    assert spy.calls == 0


def test_no_float_literals_in_i37_runtime_or_backend() -> None:
    paths = [
        ROOT / "hhs_runtime" / "pass218" / "manifest_bound_promotion_admission_proof_i37.py",
        ROOT / "hhs_backend" / "runtime_os_pass218_manifest_promotion_admission_proof_i37.py",
    ]
    for path in paths:
        tree = ast.parse(path.read_text("utf-8"))
        floats = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, path
