from __future__ import annotations

import ast
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.runtime_os_pass218_manifest_vector_vm5184_staging_i36 import (
    PASS218_I36_STAGE_PATH,
    PASS218_I36_STATUS_PATH,
    install_pass218_i36_manifest_vector_vm5184_staging_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass163.vmrc import COORDINATES, SNAPSHOT_BYTES
from hhs_runtime.pass218.curriculum import (
    CurriculumCursor,
    CurriculumSource,
    CurriculumStage,
    build_curriculum_manifest,
)
from hhs_runtime.pass218.curriculum_advance_i33 import Pass218I33CurriculumAuthority
from hhs_runtime.pass218.grammar import compile_grammar_rules
from hhs_runtime.pass218.hydration import NarrativeBeatHydrator
from hhs_runtime.pass218.manifest_bound_semantic_source_transaction_i35 import (
    Pass218I35ManifestBoundSemanticSourceTransaction,
)
from hhs_runtime.pass218.manifest_bound_source_ingress_i34 import (
    Pass218I34ManifestBoundSourceIngress,
)
from hhs_runtime.pass218.manifest_bound_vector_vm5184_staging_i36 import (
    PASS218_I36_COMPLETE_STATUS,
    Pass218I36BindingError,
    Pass218I36ManifestBoundVectorVM5184Staging,
)
from hhs_runtime.pass218.staging import ClosedTransactionVectorVM5184Adapter

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


class FakeI35Store:
    def __init__(self, receipt: dict[str, object], snapshot: dict[str, object]) -> None:
        self.receipt = receipt
        self.snapshot = snapshot

    def active_record(self):
        return json.loads(json.dumps(self.receipt))

    def active_transaction_snapshot(self):
        return json.loads(json.dumps(self.snapshot))


class SpyAdapter:
    def __init__(self) -> None:
        self.calls = 0
        self.delegate = ClosedTransactionVectorVM5184Adapter()

    def stage(self, snapshot):
        self.calls += 1
        return self.delegate.stage(snapshot)


def make_authority(source: bytes) -> Pass218I33CurriculumAuthority:
    genesis = hash72_digest(
        {"domain": "HHS-P218-I36-TEST-GENESIS-V1"},
        {"suite": "manifest-vector-vm5184-staging"},
    )
    manifest = build_curriculum_manifest(
        genesis,
        (
            CurriculumSource(
                source_id="source-i36.md",
                stage=CurriculumStage.REFERENCE,
                locator="source-i36.md",
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
        source_id="source-i36.md",
        source_epistemic_class="REPOSITORY_NATIVE_REFERENCE",
        genesis_seed=fake_seed,
        grammar_rule_set=rules,
        expected_source_sha256=sha256(source).hexdigest(),
    )


def make_i35_complete(tmp_path: Path, source: bytes):
    authority = make_authority(source)
    i33_root = tmp_path / "state" / "cognition" / "curriculum-advance-i33"
    i34_root = tmp_path / "state" / "cognition" / "manifest-source-ingress-i34"
    i35_root = tmp_path / "state" / "cognition" / "manifest-semantic-source-transaction-i35"
    i34 = Pass218I34ManifestBoundSourceIngress(
        lifecycle=ReadyLifecycle(),
        authority=authority,
        i33_store_root=i33_root,
        ingress_store_root=i34_root,
    )
    i34.bind(source_id="source-i36.md", source_bytes=source)
    i35 = Pass218I35ManifestBoundSemanticSourceTransaction(
        lifecycle=ReadyLifecycle(),
        i34_store_root=i34_root,
        transaction_store_root=i35_root,
        manifest_genesis_seed_hash72=authority.manifest.genesis_seed_hash72,
        i34_store=i34.store,
        i34_status_provider=i34.status,
    )
    receipt = i35.ingest(
        semantic_candidate=make_candidate(source, authority),
        source_bytes=source,
    )
    snapshot = i35.closed_transaction_snapshot()
    assert snapshot is not None
    return i35, receipt, snapshot


def make_i36(tmp_path: Path, i35, *, lifecycle=None, adapter=None):
    return Pass218I36ManifestBoundVectorVM5184Staging(
        lifecycle=lifecycle or ReadyLifecycle(),
        i35_store=i35.store,
        state_root=(
            tmp_path / "state" / "cognition" / "manifest-vector-vm5184-staging-i36"
        ),
        i35_status_provider=i35.status,
        i4_adapter=adapter,
    )


def test_i36_binds_exact_i35_lineage_to_frozen_i4_candidate(tmp_path: Path) -> None:
    source = (
        b"Manifest lineage reaches exact VM5184 staging without promotion. "
        b"The staged vector remains a non-authoritative candidate."
    )
    i35, i35_receipt, _ = make_i35_complete(tmp_path, source)
    runtime = make_i36(tmp_path, i35)
    receipt = runtime.stage()
    stage = runtime.active_stage()

    assert receipt["status"] == PASS218_I36_COMPLETE_STATUS
    assert receipt["i35_receipt_hash72"] == i35_receipt["i35_receipt_hash72"]
    assert receipt["i34_ingress_receipt_hash72"] == i35_receipt["i34_ingress_receipt_hash72"]
    assert receipt["manifest_bound_semantic_hash72"] == i35_receipt["manifest_bound_semantic_hash72"]
    assert receipt["manifest_binding"] == i35_receipt["manifest_binding"]
    assert receipt["i3_transaction_id_hash72"] == i35_receipt["i3_transaction_id_hash72"]
    assert receipt["i3_transaction_snapshot_hash72"] == i35_receipt["i3_transaction_snapshot_hash72"]
    assert receipt["pass218_i4_staging_invoked"] is True
    assert receipt["i4_stage_candidate_non_authoritative"] is True
    assert receipt["i4_vector_admission_status"] == "CANDIDATE"
    assert runtime.i4_invocation_count == 1

    assert stage is not None
    assert stage["i35_receipt_hash72"] == i35_receipt["i35_receipt_hash72"]
    assert stage["manifest_binding"] == i35_receipt["manifest_binding"]
    assert stage["manifest_bound_i4_stage_hash72"] == receipt["manifest_bound_i4_stage_hash72"]
    assert stage["i4_stage_candidate"]["vector_entry"]["admission_status"] == "CANDIDATE"


def test_i36_projection_is_exact_5184_partition_and_non_authoritative(tmp_path: Path) -> None:
    source = b"Exact inherited projection geometry remains candidate-only at I36."
    i35, _, _ = make_i35_complete(tmp_path, source)
    runtime = make_i36(tmp_path, i35)
    receipt = runtime.stage()
    stage = runtime.active_stage()
    assert stage is not None
    i4 = stage["i4_stage_candidate"]
    entry = i4["vector_entry"]

    assert receipt["i4_projection_bytes"] == SNAPSHOT_BYTES == 648
    assert i4["vm5184_projection_bytes"] == SNAPSHOT_BYTES
    assert len(entry["forward_support"]) + len(entry["inverse_support"]) == COORDINATES
    assert set(entry["forward_support"]).isdisjoint(entry["inverse_support"])
    assert sorted(entry["forward_support"] + entry["inverse_support"]) == list(range(COORDINATES))
    assert receipt["authoritative_vector_store_promotion"] is False
    assert receipt["canonical_vm81_commit_invoked"] is False
    assert receipt["canonical_learning_commit_invoked"] is False


def test_i36_same_process_and_restart_replay_do_not_reinvoke_i4(tmp_path: Path) -> None:
    source = b"A closed I35 transaction stages only once across durable I36 restart replay."
    i35, _, _ = make_i35_complete(tmp_path, source)
    first = make_i36(tmp_path, i35)
    receipt = first.stage()
    assert first.i4_invocation_count == 1

    replay = first.stage()
    assert replay == receipt
    assert first.i4_invocation_count == 1

    restarted = make_i36(tmp_path, i35)
    restored = restarted.stage()
    assert restored == receipt
    assert restarted.i4_invocation_count == 0
    assert restarted.active_stage() == first.active_stage()


def test_i36_durable_state_does_not_retain_source_text(tmp_path: Path) -> None:
    source = b"I36 durable forbidden verbatim phrase 4ad27c must not persist anywhere."
    i35, _, _ = make_i35_complete(tmp_path, source)
    runtime = make_i36(tmp_path, i35)
    receipt = runtime.stage()
    for path in runtime.store.root.rglob("*"):
        if path.is_file():
            assert source not in path.read_bytes()
    assert receipt["source_payload_persisted"] is False
    assert receipt["verbatim_corpus_source_retained"] is False


def test_tampered_i35_receipt_fails_before_i4_invocation(tmp_path: Path) -> None:
    source = b"Tampered lineage cannot cross the I35 to I4 boundary."
    i35, receipt, snapshot = make_i35_complete(tmp_path, source)
    tampered = json.loads(json.dumps(receipt))
    tampered["manifest_bound_semantic_hash72"] = hash72_digest(
        {"domain": "HHS-P218-I36-TAMPERED-SEMANTIC"}, {"tampered": True}
    )
    spy = SpyAdapter()
    runtime = Pass218I36ManifestBoundVectorVM5184Staging(
        lifecycle=ReadyLifecycle(),
        i35_store=FakeI35Store(tampered, snapshot),
        state_root=tmp_path / "tampered-receipt-i36",
        i4_adapter=spy,
    )
    with pytest.raises(Pass218I36BindingError, match="P218_I36_I35_RECEIPT_HASH_MISMATCH"):
        runtime.stage()
    assert spy.calls == 0


def test_tampered_i35_snapshot_fails_before_i4_invocation(tmp_path: Path) -> None:
    source = b"The exact CLOSED I3 snapshot is part of the I36 staging identity."
    _, receipt, snapshot = make_i35_complete(tmp_path, source)
    tampered_snapshot = json.loads(json.dumps(snapshot))
    tampered_snapshot["snapshot_hash72"] = "x" * 72
    spy = SpyAdapter()
    runtime = Pass218I36ManifestBoundVectorVM5184Staging(
        lifecycle=ReadyLifecycle(),
        i35_store=FakeI35Store(receipt, tampered_snapshot),
        state_root=tmp_path / "tampered-snapshot-i36",
        i4_adapter=spy,
    )
    with pytest.raises(Pass218I36BindingError, match="P218_I36_I35_SNAPSHOT_INVALID"):
        runtime.stage()
    assert spy.calls == 0


def test_i35_status_drift_fails_before_i4_invocation(tmp_path: Path) -> None:
    source = b"I36 requires the currently active I35 receipt and snapshot."
    _, receipt, snapshot = make_i35_complete(tmp_path, source)
    spy = SpyAdapter()
    runtime = Pass218I36ManifestBoundVectorVM5184Staging(
        lifecycle=ReadyLifecycle(),
        i35_store=FakeI35Store(receipt, snapshot),
        state_root=tmp_path / "status-drift-i36",
        i35_status_provider=lambda: {
            "status": "MANIFEST_BOUND_SEMANTIC_SOURCE_TRANSACTION_INGRESS_COMPLETE",
            "active_i35_receipt_hash72": "z" * 72,
            "i3_transaction_snapshot_hash72": receipt["i3_transaction_snapshot_hash72"],
        },
        i4_adapter=spy,
    )
    with pytest.raises(Pass218I36BindingError, match="P218_I36_I35_STATUS_RECEIPT_MISMATCH"):
        runtime.stage()
    assert spy.calls == 0


def test_i36_keeps_all_later_authority_surfaces_closed(tmp_path: Path) -> None:
    source = b"Vector staging is not promotion, canonical learning, or VM81 authorization."
    i35, _, _ = make_i35_complete(tmp_path, source)
    receipt = make_i36(tmp_path, i35).stage()
    for field in (
        "pass218_i5_promotion_invoked",
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


def test_runtimeos_i36_stage_route_accepts_no_caller_authority_payload(tmp_path: Path) -> None:
    source = b"RuntimeOS can request staging of active I35 state only."
    i35, _, _ = make_i35_complete(tmp_path, source)
    app = FastAPI()
    i35_control = SimpleNamespace(ingress=SimpleNamespace(store=i35.store), status=i35.status)
    control = install_pass218_i36_manifest_vector_vm5184_staging_control(
        app,
        i35_control,
        ReadyLifecycle(),
        state_root=tmp_path / "runtimeos-state",
    )
    client = TestClient(app)

    status = client.get(PASS218_I36_STATUS_PATH)
    assert status.status_code == 200
    assert status.json()["api_can_supply_manifest_binding"] is False
    assert status.json()["api_can_supply_source_payload"] is False
    assert status.json()["api_can_invoke_i5_promotion"] is False
    assert status.json()["api_can_invoke_vm81_authority"] is False

    staged = client.post(PASS218_I36_STAGE_PATH)
    assert staged.status_code == 200
    assert staged.json()["i4_vector_admission_status"] == "CANDIDATE"
    assert control.staging.i4_invocation_count == 1

    rejected = client.post(PASS218_I36_STAGE_PATH, json={"manifest_binding": {"forged": True}})
    assert rejected.status_code == 200
    assert rejected.json() == staged.json()
    assert control.staging.i4_invocation_count == 1


def test_i36_writer_fence_failure_stops_before_i4(tmp_path: Path) -> None:
    source = b"The inherited ingestion writer fence remains required for I36."
    _, receipt, snapshot = make_i35_complete(tmp_path, source)
    spy = SpyAdapter()
    runtime = Pass218I36ManifestBoundVectorVM5184Staging(
        lifecycle=ReadyLifecycle(ready=False),
        i35_store=FakeI35Store(receipt, snapshot),
        state_root=tmp_path / "writer-fence-i36",
        i4_adapter=spy,
    )
    with pytest.raises(RuntimeError, match="P218_I9_CANONICAL_WRITER_REQUIRED"):
        runtime.stage()
    assert spy.calls == 0


def test_no_float_literals_in_i36_runtime_or_backend() -> None:
    paths = [
        ROOT / "hhs_runtime" / "pass218" / "manifest_bound_vector_vm5184_staging_i36.py",
        ROOT / "hhs_backend" / "runtime_os_pass218_manifest_vector_vm5184_staging_i36.py",
    ]
    for path in paths:
        tree = ast.parse(path.read_text("utf-8"))
        floats = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, path
