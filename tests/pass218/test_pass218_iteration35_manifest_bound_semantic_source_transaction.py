from __future__ import annotations

import ast
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.runtime_os_pass218_manifest_semantic_source_transaction_i35 import (
    PASS218_I35_INGEST_PATH,
    PASS218_I35_STATUS_PATH,
    install_pass218_i35_manifest_semantic_transaction_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
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
    PASS218_I35_COMPLETE_STATUS,
    Pass218I35BindingError,
    Pass218I35ManifestBoundSemanticSourceTransaction,
)
from hhs_runtime.pass218.manifest_bound_source_ingress_i34 import (
    Pass218I34ManifestBoundSourceIngress,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
GRAMMAR_PATH = REPOSITORY_ROOT / "hhs_runtime" / "Grammar Correction.csv"


class ReadyLifecycle:
    def __init__(self, ready: bool = True) -> None:
        self.ready = ready

    def require_ingestion_ready(self) -> None:
        if not self.ready:
            raise RuntimeError("P218_I9_CANONICAL_WRITER_REQUIRED")

    def status(self):
        return {"ingestion_enabled": self.ready}


def make_authority(source: bytes) -> Pass218I33CurriculumAuthority:
    genesis = hash72_digest(
        {"domain": "HHS-P218-I35-TEST-GENESIS-V1"},
        {"suite": "manifest-semantic-source-transaction"},
    )
    manifest = build_curriculum_manifest(
        genesis,
        (
            CurriculumSource(
                source_id="source-a.md",
                stage=CurriculumStage.REFERENCE,
                locator="source-a.md",
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
        source_id="source-a.md",
        source_epistemic_class="REPOSITORY_NATIVE_REFERENCE",
        genesis_seed=fake_seed,
        grammar_rule_set=rules,
        expected_source_sha256=sha256(source).hexdigest(),
    )


def bind_i34(tmp_path: Path, source: bytes, authority: Pass218I33CurriculumAuthority):
    i33_root = tmp_path / "state" / "cognition" / "curriculum-advance-i33"
    i34_root = tmp_path / "state" / "cognition" / "manifest-source-ingress-i34"
    runtime = Pass218I34ManifestBoundSourceIngress(
        lifecycle=ReadyLifecycle(),
        authority=authority,
        i33_store_root=i33_root,
        ingress_store_root=i34_root,
    )
    receipt = runtime.bind(source_id="source-a.md", source_bytes=source)
    return runtime, receipt, i34_root


def make_i35(
    tmp_path: Path,
    authority: Pass218I33CurriculumAuthority,
    i34_runtime: Pass218I34ManifestBoundSourceIngress,
    i34_root: Path,
    *,
    lifecycle=None,
):
    return Pass218I35ManifestBoundSemanticSourceTransaction(
        lifecycle=lifecycle or ReadyLifecycle(),
        i34_store_root=i34_root,
        transaction_store_root=(
            tmp_path / "state" / "cognition" / "manifest-semantic-source-transaction-i35"
        ),
        manifest_genesis_seed_hash72=authority.manifest.genesis_seed_hash72,
        i34_store=i34_runtime.store,
        i34_status_provider=i34_runtime.status,
    )


def test_i35_propagates_exact_i34_binding_before_one_frozen_i3_transaction(
    tmp_path: Path,
) -> None:
    source = (
        b"Permission narrows authority while the exact source lineage remains bounded. "
        b"No later promotion authority is implied."
    )
    authority = make_authority(source)
    i34_runtime, i34_receipt, i34_root = bind_i34(tmp_path, source, authority)
    candidate = make_candidate(source, authority)
    runtime = make_i35(tmp_path, authority, i34_runtime, i34_root)

    receipt = runtime.ingest(semantic_candidate=candidate, source_bytes=source)

    assert receipt["status"] == PASS218_I35_COMPLETE_STATUS
    assert receipt["i34_ingress_receipt_hash72"] == i34_receipt["ingress_receipt_hash72"]
    for field in (
        "authority_root_hash72",
        "manifest_hash72",
        "curriculum_identity_hash72",
        "curriculum_position",
        "source_id",
        "source_sha256",
        "source_stage",
        "source_stage_name",
        "rights_class",
        "source_authority",
        "media_type",
        "source_byte_count",
        "previous_closure_hash72",
        "previous_advance_receipt_hash72",
        "source_identity_hash72",
        "source_binding_hash72",
        "ingress_validation_hash72",
        "ingress_receipt_hash72",
        "ingress_hash216",
    ):
        assert receipt["manifest_binding"][field] == i34_receipt[field]
    assert receipt["semantic_construction_invoked"] is True
    assert receipt["i3_source_transaction_required"] is True
    assert receipt["i3_source_transaction_invoked"] is True
    assert receipt["i3_transaction_closed"] is True
    assert receipt["i3_managed_buffer_zeroized"] is True
    assert receipt["i3_managed_buffer_cleared"] is True
    assert receipt["structural_candidate_admitted_non_authoritatively"] is True
    assert runtime.i3_invocation_count == 1
    assert len(receipt["i35_hash216"]) == 216
    assert all(
        validate_hash72(receipt["i35_hash216"][start:start + 72])
        for start in (0, 72, 144)
    )

    snapshot = runtime.closed_transaction_snapshot()
    assert snapshot is not None
    assert snapshot["candidate_record"]["manifest_binding"] == receipt["manifest_binding"]
    assert (
        snapshot["candidate_record"]["manifest_bound_semantic_hash72"]
        == receipt["manifest_bound_semantic_hash72"]
    )
    assert snapshot["candidate_record"]["i3_source_transaction_invoked"] is False
    assert snapshot["closure_receipt"]["managed_buffer_zeroized"] is True
    assert snapshot["closure_receipt"]["managed_buffer_cleared"] is True


def test_i35_durable_state_is_nonverbatim_and_replay_does_not_reinvoke_i3(
    tmp_path: Path,
) -> None:
    source = (
        b"I35 durable unique source phrase 7f124b. "
        b"This exact phrase must never enter the durable I35 state."
    )
    authority = make_authority(source)
    i34_runtime, _, i34_root = bind_i34(tmp_path, source, authority)
    candidate = make_candidate(source, authority)
    first = make_i35(tmp_path, authority, i34_runtime, i34_root)
    receipt = first.ingest(semantic_candidate=candidate, source_bytes=source)
    assert first.i3_invocation_count == 1

    store_root = first.store.root
    for path in store_root.rglob("*"):
        if path.is_file():
            assert source not in path.read_bytes()

    replay = first.ingest(semantic_candidate=candidate, source_bytes=source)
    assert replay == receipt
    assert first.i3_invocation_count == 1

    restarted = make_i35(tmp_path, authority, i34_runtime, i34_root)
    restored = restarted.ingest(semantic_candidate=candidate, source_bytes=source)
    assert restored == receipt
    assert restarted.i3_invocation_count == 0
    assert restarted.closed_transaction_snapshot() == first.closed_transaction_snapshot()


def test_candidate_identity_failures_stop_before_i3_invocation(tmp_path: Path) -> None:
    source = b"Manifest identity must precede semantic transaction construction."
    authority = make_authority(source)
    i34_runtime, _, i34_root = bind_i34(tmp_path, source, authority)
    candidate = make_candidate(source, authority).to_record()

    wrong_source = dict(candidate)
    wrong_source["source_id"] = "other.md"
    runtime = make_i35(tmp_path, authority, i34_runtime, i34_root)
    with pytest.raises(Pass218I35BindingError, match="P218_I35_CANDIDATE_SOURCE_ID_MISMATCH"):
        runtime.ingest(semantic_candidate=wrong_source, source_bytes=source)
    assert runtime.i3_invocation_count == 0

    wrong_genesis = dict(candidate)
    wrong_genesis["genesis_seed_hash72"] = hash72_digest(
        {"domain": "HHS-P218-I35-WRONG-GENESIS-V1"},
        {"wrong": True},
    )
    with pytest.raises(
        Pass218I35BindingError,
        match="P218_I35_CANDIDATE_GENESIS_IDENTITY_MISMATCH",
    ):
        runtime.ingest(semantic_candidate=wrong_genesis, source_bytes=source)
    assert runtime.i3_invocation_count == 0

    with pytest.raises(
        Pass218I35BindingError,
        match="P218_I35_TRANSIENT_SOURCE_SHA256_MISMATCH",
    ):
        runtime.ingest(semantic_candidate=candidate, source_bytes=source + b" tampered")
    assert runtime.i3_invocation_count == 0


def test_request_cannot_override_manifest_binding_or_curriculum_identity(
    tmp_path: Path,
) -> None:
    source = b"The caller supplies semantics but cannot mint the I34 authority envelope."
    authority = make_authority(source)
    i34_runtime, _, i34_root = bind_i34(tmp_path, source, authority)
    candidate = make_candidate(source, authority).to_record()
    candidate["manifest_binding"] = {"curriculum_identity_hash72": "caller"}
    runtime = make_i35(tmp_path, authority, i34_runtime, i34_root)
    with pytest.raises(
        Pass218I35BindingError,
        match="P218_I35_REQUEST_CANNOT_SUPPLY_MANIFEST_BINDING",
    ):
        runtime.ingest(semantic_candidate=candidate, source_bytes=source)
    assert runtime.i3_invocation_count == 0
    assert runtime.store.active_record() is None


def test_tampered_i34_receipt_is_rejected_before_i3(tmp_path: Path) -> None:
    source = b"I34 lineage tampering cannot become a semantic transaction."
    authority = make_authority(source)
    i34_runtime, receipt, i34_root = bind_i34(tmp_path, source, authority)
    candidate = make_candidate(source, authority)
    tampered = dict(receipt)
    tampered["rights_class"] = "ALTERED"

    class TamperedStore:
        def active_record(self):
            return tampered

    runtime = Pass218I35ManifestBoundSemanticSourceTransaction(
        lifecycle=ReadyLifecycle(),
        i34_store_root=i34_root,
        transaction_store_root=tmp_path / "i35",
        manifest_genesis_seed_hash72=authority.manifest.genesis_seed_hash72,
        i34_store=TamperedStore(),
    )
    with pytest.raises(Pass218I35BindingError, match="P218_I35_I34_RECEIPT_HASH_MISMATCH"):
        runtime.ingest(semantic_candidate=candidate, source_bytes=source)
    assert runtime.i3_invocation_count == 0


def test_writer_fence_is_required_before_semantic_or_i3_work(tmp_path: Path) -> None:
    source = b"The writer fence remains authoritative at I35."
    authority = make_authority(source)
    i34_runtime, _, i34_root = bind_i34(tmp_path, source, authority)
    candidate = make_candidate(source, authority)
    runtime = make_i35(
        tmp_path,
        authority,
        i34_runtime,
        i34_root,
        lifecycle=ReadyLifecycle(False),
    )
    with pytest.raises(RuntimeError, match="P218_I9_CANONICAL_WRITER_REQUIRED"):
        runtime.ingest(semantic_candidate=candidate, source_bytes=source)
    assert runtime.semantic_construction_count == 0
    assert runtime.i3_invocation_count == 0


def test_i35_stops_before_all_later_pass218_authority(tmp_path: Path) -> None:
    source = b"I35 closes only the inherited I3 transaction boundary."
    authority = make_authority(source)
    i34_runtime, _, i34_root = bind_i34(tmp_path, source, authority)
    runtime = make_i35(tmp_path, authority, i34_runtime, i34_root)
    receipt = runtime.ingest(
        semantic_candidate=make_candidate(source, authority),
        source_bytes=source,
    )
    for field in (
        "pass218_i4_staging_invoked",
        "pass218_i5_promotion_invoked",
        "pass218_i30_canonical_semantic_promotion_invoked",
        "pass218_i31_verbatim_purge_invoked",
        "pass218_i32_source_closure_invoked",
        "curriculum_cursor_advanced",
        "stage_advance_permitted",
        "vm81_authorization_invoked",
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "authoritative_float_weights_created",
    ):
        assert receipt[field] is False


def test_runtimeos_ingest_route_uses_preconfigured_authority_and_cannot_override_it(
    tmp_path: Path,
) -> None:
    source = b"RuntimeOS carries a frozen I2 candidate into the exact I34 binding."
    authority = make_authority(source)
    i34_runtime, _, i34_root = bind_i34(tmp_path, source, authority)
    i33_control = SimpleNamespace(
        advancer=SimpleNamespace(authority=authority),
        configuration_error=None,
        status=lambda: {"authority_configuration_source": "EXPLICIT_INTERNAL_CONFIGURATION"},
    )
    i34_control = SimpleNamespace(
        i33_control=i33_control,
        store_root=i34_root,
        ingress=i34_runtime,
        status=i34_runtime.status,
    )
    app = FastAPI()
    install_pass218_i35_manifest_semantic_transaction_control(
        app,
        i34_control,
        ReadyLifecycle(),
        state_root=tmp_path / "api-state",
    )
    client = TestClient(app)

    initial = client.get(PASS218_I35_STATUS_PATH)
    assert initial.status_code == 200
    assert initial.json()["api_can_mint_curriculum_authority"] is False
    assert initial.json()["api_can_override_manifest_binding"] is False
    assert initial.json()["api_can_advance_curriculum"] is False

    response = client.post(
        PASS218_I35_INGEST_PATH,
        json={
            "source_text": source.decode("utf-8"),
            "semantic_candidate": make_candidate(source, authority).to_record(),
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == PASS218_I35_COMPLETE_STATUS
    assert body["curriculum_cursor_advanced"] is False

    rejected = client.post(
        PASS218_I35_INGEST_PATH,
        json={
            "source_text": source.decode("utf-8"),
            "semantic_candidate": make_candidate(source, authority).to_record(),
            "curriculum_identity_hash72": authority.manifest.curriculum_identity_hash72,
        },
    )
    assert rejected.status_code == 422


def test_runtimeos_without_authoritative_curriculum_fails_closed(tmp_path: Path) -> None:
    app = FastAPI()
    i33_control = SimpleNamespace(
        advancer=SimpleNamespace(authority=None),
        configuration_error=None,
        status=lambda: {"authority_configuration_source": "UNCONFIGURED"},
    )
    i34_control = SimpleNamespace(
        i33_control=i33_control,
        store_root=tmp_path / "i34",
        ingress=SimpleNamespace(store=SimpleNamespace(active_record=lambda: None)),
        status=lambda: {
            "manifest_bound_source_ready": False,
            "binding_current": False,
            "active_ingress_receipt_hash72": None,
        },
    )
    install_pass218_i35_manifest_semantic_transaction_control(
        app,
        i34_control,
        ReadyLifecycle(),
        state_root=tmp_path / "api-state",
    )
    client = TestClient(app)
    response = client.post(
        PASS218_I35_INGEST_PATH,
        json={"source_text": "x", "semantic_candidate": {}},
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "P218_I35_AUTHORITATIVE_CURRICULUM_NOT_CONFIGURED"


def test_i35_authority_adjacent_modules_have_no_float_literals() -> None:
    paths = (
        REPOSITORY_ROOT
        / "hhs_runtime"
        / "pass218"
        / "manifest_bound_semantic_source_transaction_i35.py",
        REPOSITORY_ROOT
        / "hhs_backend"
        / "runtime_os_pass218_manifest_semantic_source_transaction_i35.py",
    )
    for path in paths:
        tree = ast.parse(path.read_text("utf-8"))
        floats = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, path
