from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.runtime_os_pass218_manifest_source_ingress_i34 import (
    PASS218_I34_BIND_PATH,
    PASS218_I34_STATUS_PATH,
    install_pass218_i34_manifest_source_ingress_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.curriculum import (
    CurriculumCursor,
    CurriculumSource,
    CurriculumStage,
    build_curriculum_manifest,
)
from hhs_runtime.pass218.curriculum_advance_i33 import (
    Pass218I33CurriculumAuthority,
)
from hhs_runtime.pass218.manifest_bound_source_ingress_i34 import (
    PASS218_I34_READY_STATUS,
    Pass218I34BindingError,
    Pass218I34ManifestBoundSourceIngress,
    Pass218I34ManifestSourceIngressStore,
    Pass218I34StateError,
)


class ReadyLifecycle:
    def __init__(self, ready: bool = True) -> None:
        self.ready = ready

    def require_ingestion_ready(self) -> None:
        if not self.ready:
            raise RuntimeError("P218_I9_CANONICAL_WRITER_REQUIRED")

    def status(self):
        return {"ingestion_enabled": self.ready}


class FakeI33Store:
    def __init__(self, authority, cursor, last_receipt=None) -> None:
        self.authority = authority
        self.cursor = cursor
        self.receipt = last_receipt

    def ensure_authority(self, authority):
        assert authority.record() == self.authority.record()
        return authority.record()

    def current_cursor(self, authority):
        assert authority.record() == self.authority.record()
        return self.cursor

    def last_receipt(self):
        return self.receipt


class StubI33Control:
    def __init__(self, root: Path, authority=None, configuration_error=None) -> None:
        self.store_root = root / "cognition" / "curriculum-advance-i33"
        self.advancer = SimpleNamespace(authority=authority)
        self.configuration_error = configuration_error

    def status(self):
        return {
            "authority_configuration_source": (
                "EXPLICIT_INTERNAL_CONFIGURATION"
                if self.advancer.authority is not None
                else "UNCONFIGURED"
            )
        }


def make_authority(source_bytes: bytes, *, second: bytes | None = None):
    genesis = hash72_digest(
        {"domain": "HHS-P218-I34-TEST-GENESIS-V1"},
        {"suite": "manifest-source-ingress"},
    )
    sources = [
        CurriculumSource(
            source_id="source-a.md",
            stage=CurriculumStage.REFERENCE,
            locator="source-a.md",
            checksum_sha256=sha256(source_bytes).hexdigest(),
            rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
            source_authority="REPOSITORY_NATIVE_CONTRACT_AUTHORITY",
            media_type="text/markdown",
        )
    ]
    if second is not None:
        sources.append(
            CurriculumSource(
                source_id="source-b.md",
                stage=CurriculumStage.EXPOSITORY,
                locator="source-b.md",
                checksum_sha256=sha256(second).hexdigest(),
                rights_class="REPOSITORY_NATIVE_TEST_AUTHORITY",
                source_authority="REPOSITORY_NATIVE_CONTRACT_AUTHORITY",
                media_type="text/markdown",
            )
        )
    manifest = build_curriculum_manifest(genesis, sources)
    return Pass218I33CurriculumAuthority(
        manifest=manifest,
        initial_cursor=CurriculumCursor.for_manifest(manifest),
    ).validated()


def test_manifest_bound_ingress_is_durable_nonverbatim_and_restart_idempotent(tmp_path: Path):
    source = (
        b"I34 unique manifest-bound ingress fixture. "
        b"This sentence must never be persisted verbatim in the durable receipt store."
    )
    authority = make_authority(source)
    state_root = tmp_path / "state"
    ingress_root = state_root / "cognition" / "manifest-source-ingress-i34"
    i33_root = state_root / "cognition" / "curriculum-advance-i33"

    first_runtime = Pass218I34ManifestBoundSourceIngress(
        lifecycle=ReadyLifecycle(),
        authority=authority,
        i33_store_root=i33_root,
        ingress_store_root=ingress_root,
    )
    first = first_runtime.bind(source_id="source-a.md", source_bytes=source)
    assert first["binding_status"] == PASS218_I34_READY_STATUS
    assert first["manifest_bound_source_ready"] is True
    assert first["source_checksum_verified"] is True
    assert first["managed_ingress_buffer_zeroized"] is True
    assert first["managed_ingress_buffer_cleared"] is True
    assert first["source_payload_persisted"] is False
    assert first["verbatim_corpus_source_retained"] is False
    assert first["i3_source_transaction_required"] is True
    assert first["i3_source_transaction_invoked"] is False
    assert first["semantic_construction_invoked"] is False
    assert first["curriculum_cursor_advanced"] is False
    assert first["stage_advance_permitted"] is False
    assert len(first["ingress_hash216"]) == 216

    for path in ingress_root.rglob("*"):
        if path.is_file():
            assert source not in path.read_bytes()

    restarted = Pass218I34ManifestBoundSourceIngress(
        lifecycle=ReadyLifecycle(),
        authority=authority,
        i33_store_root=i33_root,
        ingress_store_root=ingress_root,
    )
    replay = restarted.bind(source_id="source-a.md", source_bytes=source)
    assert replay == first
    status = restarted.status()
    assert status["manifest_bound_source_ready"] is True
    assert status["binding_current"] is True
    assert status["curriculum_cursor_advanced"] is False


def test_wrong_checksum_and_wrong_source_id_fail_without_durable_binding(tmp_path: Path):
    source = b"authoritative source bytes for checksum binding"
    authority = make_authority(source)
    state_root = tmp_path / "state"
    ingress_root = state_root / "ingress"
    runtime = Pass218I34ManifestBoundSourceIngress(
        lifecycle=ReadyLifecycle(),
        authority=authority,
        i33_store_root=state_root / "i33",
        ingress_store_root=ingress_root,
    )
    with pytest.raises(Pass218I34BindingError, match="P218_I34_UNEXPECTED_SOURCE_ID"):
        runtime.bind(source_id="other.md", source_bytes=source)
    assert Pass218I34ManifestSourceIngressStore(ingress_root).active_record() is None

    with pytest.raises(Pass218I34BindingError, match="P218_I34_SOURCE_CHECKSUM_MISMATCH"):
        runtime.bind(source_id="source-a.md", source_bytes=source + b" tampered")
    assert Pass218I34ManifestSourceIngressStore(ingress_root).active_record() is None


def test_stage_transition_cannot_be_bypassed_by_valid_next_source(tmp_path: Path):
    first = b"reference stage source"
    second = b"expository stage source"
    authority = make_authority(first, second=second)
    previous_closure = hash72_digest(
        {"domain": "HHS-P218-I34-TEST-CLOSURE-V1"}, {"ordinal": 0}
    )
    cursor = CurriculumCursor(
        manifest_hash72=authority.manifest.manifest_hash72,
        curriculum_identity_hash72=authority.manifest.curriculum_identity_hash72,
        next_ordinal=1,
        last_closure_hash72=previous_closure,
    )
    advance_receipt = hash72_digest(
        {"domain": "HHS-P218-I34-TEST-ADVANCE-V1"}, {"ordinal": 0}
    )
    fake_store = FakeI33Store(
        authority,
        cursor,
        {
            "advance_receipt_hash72": advance_receipt,
            "stage_transition_required": True,
            "stage_advance_permitted": False,
        },
    )
    runtime = Pass218I34ManifestBoundSourceIngress(
        lifecycle=ReadyLifecycle(),
        authority=authority,
        i33_store_root=tmp_path / "unused-i33",
        ingress_store_root=tmp_path / "ingress",
        i33_store=fake_store,
    )
    with pytest.raises(Pass218I34BindingError, match="P218_I34_STAGE_ACCEPTANCE_REQUIRED"):
        runtime.bind(source_id="source-b.md", source_bytes=second)
    assert runtime.store.active_record() is None
    assert runtime.status()["stage_advance_permitted"] is False


def test_same_stage_next_source_can_bind_to_advanced_cursor(tmp_path: Path):
    first = b"reference first"
    second = b"reference second"
    genesis = hash72_digest({"domain": "HHS-P218-I34-SAME-STAGE-V1"}, {"case": 1})
    manifest = build_curriculum_manifest(
        genesis,
        (
            CurriculumSource(
                "a.md", CurriculumStage.REFERENCE, "a.md", sha256(first).hexdigest(),
                "TEST", "TEST_AUTH", "text/markdown"
            ),
            CurriculumSource(
                "b.md", CurriculumStage.REFERENCE, "b.md", sha256(second).hexdigest(),
                "TEST", "TEST_AUTH", "text/markdown"
            ),
        ),
    )
    authority = Pass218I33CurriculumAuthority(
        manifest, CurriculumCursor.for_manifest(manifest)
    ).validated()
    closure = hash72_digest({"domain": "HHS-P218-I34-SAME-STAGE-CLOSE"}, {"i": 0})
    cursor = CurriculumCursor(
        manifest_hash72=manifest.manifest_hash72,
        curriculum_identity_hash72=manifest.curriculum_identity_hash72,
        next_ordinal=1,
        last_closure_hash72=closure,
    )
    fake_store = FakeI33Store(
        authority,
        cursor,
        {
            "advance_receipt_hash72": hash72_digest(
                {"domain": "HHS-P218-I34-SAME-STAGE-ADVANCE"}, {"i": 0}
            ),
            "stage_transition_required": False,
            "stage_advance_permitted": False,
        },
    )
    runtime = Pass218I34ManifestBoundSourceIngress(
        lifecycle=ReadyLifecycle(),
        authority=authority,
        i33_store_root=tmp_path / "unused",
        ingress_store_root=tmp_path / "ingress",
        i33_store=fake_store,
    )
    receipt = runtime.bind(source_id="b.md", source_bytes=second)
    assert receipt["curriculum_position"] == 1
    assert receipt["previous_closure_hash72"] == closure
    assert receipt["source_stage"] == int(CurriculumStage.REFERENCE)


def test_writer_fence_is_required_before_binding(tmp_path: Path):
    source = b"writer fence source"
    authority = make_authority(source)
    runtime = Pass218I34ManifestBoundSourceIngress(
        lifecycle=ReadyLifecycle(False),
        authority=authority,
        i33_store_root=tmp_path / "i33",
        ingress_store_root=tmp_path / "ingress",
    )
    with pytest.raises(RuntimeError, match="P218_I9_CANONICAL_WRITER_REQUIRED"):
        runtime.bind(source_id="source-a.md", source_bytes=source)
    assert runtime.store.active_record() is None


def test_tampered_durable_receipt_is_detected(tmp_path: Path):
    source = b"durable receipt tamper fixture"
    authority = make_authority(source)
    runtime = Pass218I34ManifestBoundSourceIngress(
        lifecycle=ReadyLifecycle(),
        authority=authority,
        i33_store_root=tmp_path / "i33",
        ingress_store_root=tmp_path / "ingress",
    )
    runtime.bind(source_id="source-a.md", source_bytes=source)
    state = json.loads(runtime.store.state_path.read_text("utf-8"))
    receipt_path = runtime.store.root / state["active_receipt_path"]
    receipt = json.loads(receipt_path.read_text("utf-8"))
    receipt["source_stage"] = int(CurriculumStage.MYTHOPOETIC)
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(Pass218I34StateError):
        runtime.store.active_record()


def test_runtime_os_fails_closed_without_authority_and_cannot_mint_it(tmp_path: Path):
    lifecycle = ReadyLifecycle()
    app = FastAPI()
    i33 = StubI33Control(tmp_path, authority=None)
    install_pass218_i34_manifest_source_ingress_control(
        app, i33, lifecycle, state_root=tmp_path
    )
    client = TestClient(app)
    status = client.get(PASS218_I34_STATUS_PATH)
    assert status.status_code == 200
    assert status.json()["authority_configured"] is False
    assert status.json()["api_can_mint_curriculum_authority"] is False
    response = client.post(
        PASS218_I34_BIND_PATH,
        json={"source_id": "source-a.md", "source_text": "anything"},
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "P218_I34_AUTHORITATIVE_CURRICULUM_NOT_CONFIGURED"


def test_runtime_os_accepts_transient_source_but_rejects_authority_fields(tmp_path: Path):
    source_text = "runtime os manifest-bound source payload"
    source = source_text.encode("utf-8")
    authority = make_authority(source)
    lifecycle = ReadyLifecycle()
    app = FastAPI()
    i33 = StubI33Control(tmp_path, authority=authority)
    install_pass218_i34_manifest_source_ingress_control(
        app, i33, lifecycle, state_root=tmp_path
    )
    client = TestClient(app)
    forbidden = client.post(
        PASS218_I34_BIND_PATH,
        json={
            "source_id": "source-a.md",
            "source_text": source_text,
            "manifest": authority.manifest.record(),
        },
    )
    assert forbidden.status_code == 422

    accepted = client.post(
        PASS218_I34_BIND_PATH,
        json={"source_id": "source-a.md", "source_text": source_text},
    )
    assert accepted.status_code == 200
    payload = accepted.json()
    assert payload["manifest_bound_source_ready"] is True
    assert payload["source_payload_persisted"] is False
    status = client.get(PASS218_I34_STATUS_PATH).json()
    assert status["manifest_bound_source_ready"] is True
    assert status["api_can_mint_curriculum_authority"] is False
    assert status["api_can_advance_curriculum_stage"] is False
