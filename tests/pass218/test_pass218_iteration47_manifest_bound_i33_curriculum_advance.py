from __future__ import annotations

import ast
from pathlib import Path
import runpy
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_backend.runtime_os_pass218_manifest_i33_curriculum_advance_i47 import (
    PASS218_I47_ADVANCE_PATH,
    PASS218_I47_STATUS_PATH,
    install_pass218_i47_manifest_bound_i33_curriculum_advance_control,
)
from hhs_runtime.pass218.curriculum_advance_i33 import Pass218I33CurriculumAdvancer
from hhs_runtime.pass218.manifest_bound_i31_verbatim_purge_i45 import (
    Pass218I45ManifestBoundI31VerbatimPurge,
)
from hhs_runtime.pass218.manifest_bound_i32_source_closure_i46 import (
    Pass218I46ManifestBoundI32SourceClosure,
)
from hhs_runtime.pass218.manifest_bound_i33_curriculum_advance_i47 import (
    PASS218_I47_COMPLETE_STATUS,
    Pass218I47BindingError,
    Pass218I47ManifestBoundI33CurriculumAdvance,
)
from hhs_runtime.pass218.manifest_bound_source_ingress_i34 import (
    Pass218I34ManifestSourceIngressStore,
)
from hhs_runtime.pass218.source_closure_i32 import Pass218I32SourceCloser
from hhs_runtime.pass218.verbatim_purge_i31 import Pass218I31VerbatimPurger

ROOT = Path(__file__).resolve().parents[2]
I46 = runpy.run_path(
    str(
        ROOT
        / "tests"
        / "pass218"
        / "test_pass218_iteration46_manifest_bound_i32_source_closure.py"
    )
)
I43 = I46["I43"]


def prepare_i47(
    tmp_path: Path,
    *,
    source: bytes = b"I47 advances the exact manifest-bound closed source exactly once through frozen I33.",
):
    _, lifecycle, authority, validator, validation_request, i42, i42_receipt = I43[
        "prepare_i42"
    ](
        tmp_path,
        source=source,
        context_id="i47 transient request context must not persist",
    )
    request = I43["promotion_request"](validation_request, i42_receipt)
    i43 = I43["make_i43"](tmp_path, lifecycle, i42, validator)
    i43_receipt = i43.authorize(request)
    state = tmp_path / "state" / "cognition"
    i34_store = Pass218I34ManifestSourceIngressStore(state / "manifest-source-ingress-i34")
    i34 = i34_store.active_record()
    assert i34 is not None
    i42_proof = i42.store.active_proof()
    assert i42_proof is not None
    i30_root = state / "atomic-semantic-promotion-i30"
    i30_store = I46["make_i30_store"](i30_root, i43_receipt=i43_receipt)
    i44_store = I46["make_i44_store"](
        i43_receipt=i43_receipt,
        i30_store=i30_store,
        shared_identity=dict(i42_proof["shared_identity"]),
    )
    purger = Pass218I31VerbatimPurger(
        lifecycle=lifecycle,
        i30_store_root=i30_root,
        purge_store_root=state / "verbatim-purge-i31",
    )
    i45 = Pass218I45ManifestBoundI31VerbatimPurge(
        lifecycle=lifecycle,
        i44_store=i44_store,
        i31_purger=purger,
        state_root=state / "manifest-bound-i31-verbatim-purge-i45",
    )
    i45.purge()
    closer = Pass218I32SourceCloser(
        lifecycle=lifecycle,
        i31_store_root=state / "verbatim-purge-i31",
        closure_store_root=state / "source-closure-i32",
    )
    i46 = Pass218I46ManifestBoundI32SourceClosure(
        lifecycle=lifecycle,
        i45_store=i45.store,
        i44_store=i44_store,
        i43_store=i43.store,
        i42_store=i42.store,
        i34_store=i34_store,
        i30_store=i30_store,
        i32_closer=closer,
        state_root=state / "manifest-bound-i32-source-closure-i46",
    )
    i46_receipt = i46.close()
    i33 = Pass218I33CurriculumAdvancer(
        lifecycle=lifecycle,
        i32_store_root=closer.store.root,
        advance_store_root=state / "curriculum-advance-i33",
        authority=authority,
    )
    i47 = Pass218I47ManifestBoundI33CurriculumAdvance(
        lifecycle=lifecycle,
        i46_store=i46.store,
        i30_store=i30_store,
        i33_advancer=i33,
        state_root=state / "manifest-bound-i33-curriculum-advance-i47",
    )
    return {
        "source": source,
        "lifecycle": lifecycle,
        "authority": authority,
        "i42": i42,
        "i43": i43,
        "i34_store": i34_store,
        "i30_store": i30_store,
        "i44_store": i44_store,
        "purger": purger,
        "i45": i45,
        "closer": closer,
        "i46": i46,
        "i46_receipt": i46_receipt,
        "i33": i33,
        "i47": i47,
    }


def test_i47_fresh_path_invokes_i33_once_and_preserves_i30_generation(tmp_path: Path) -> None:
    env = prepare_i47(tmp_path)
    before = env["i30_store"].active_generation()
    receipt = env["i47"].advance()
    after = env["i30_store"].active_generation()
    proof = env["i47"].store.active_proof()

    assert receipt["status"] == PASS218_I47_COMPLETE_STATUS
    assert receipt["i46_complete_source_closure_verified"] is True
    assert receipt["i32_exact_closure_verified"] is True
    assert receipt["i33_curriculum_advance_invoked"] is True
    assert receipt["i33_advance_receipt_committed"] is True
    assert receipt["curriculum_cursor_advanced"] is True
    assert receipt["next_source_ingress_invoked"] is False
    assert receipt["stage_advance_permitted"] is False
    assert receipt["canonical_learning_commit_invoked"] is False
    assert before == after
    assert env["i47"].i33_invocation_count == 1
    assert env["i33"].advance_count == 1
    assert proof is not None
    assert proof["i33_exactly_once_or_restart_adoption_verified"] is True
    assert proof["restart_does_not_require_duplicate_i33_invocation"] is True


def test_i47_restart_adopts_exact_existing_i33_without_duplicate_advance(tmp_path: Path) -> None:
    env = prepare_i47(tmp_path)
    direct = env["i33"].advance()
    assert env["i33"].advance_count == 1
    receipt = env["i47"].advance()
    assert receipt["i33_advance_receipt_hash72"] == direct["advance_receipt_hash72"]
    assert env["i47"].i33_invocation_count == 0
    assert env["i47"].restart_adoption_count == 1
    assert env["i33"].advance_count == 1

    restarted = Pass218I47ManifestBoundI33CurriculumAdvance(
        lifecycle=env["lifecycle"],
        i46_store=env["i46"].store,
        i30_store=env["i30_store"],
        i33_advancer=env["i33"],
        state_root=(
            tmp_path
            / "state"
            / "cognition"
            / "manifest-bound-i33-curriculum-advance-i47"
        ),
    )
    assert restarted.advance() == receipt
    assert restarted.i33_invocation_count == 0
    assert env["i33"].advance_count == 1


def test_i47_rejects_unrelated_curriculum_authority_before_i33(tmp_path: Path) -> None:
    primary = prepare_i47(tmp_path / "primary")
    other = prepare_i47(
        tmp_path / "other",
        source=b"A different source produces a different authoritative curriculum identity.",
    )
    mismatched_i33 = Pass218I33CurriculumAdvancer(
        lifecycle=primary["lifecycle"],
        i32_store_root=primary["closer"].store.root,
        advance_store_root=tmp_path / "mismatched-i33",
        authority=other["authority"],
    )
    runtime = Pass218I47ManifestBoundI33CurriculumAdvance(
        lifecycle=primary["lifecycle"],
        i46_store=primary["i46"].store,
        i30_store=primary["i30_store"],
        i33_advancer=mismatched_i33,
        state_root=tmp_path / "rejected-i47",
    )
    with pytest.raises(
        Pass218I47BindingError,
        match="P218_I47_I33_CURRICULUM_IDENTITY_MISMATCH",
    ):
        runtime.advance()
    assert runtime.i33_invocation_count == 0
    assert mismatched_i33.advance_count == 0
    assert runtime.store.active_record() is None


def test_i47_persists_no_source_payload_and_makes_no_erasure_claim(tmp_path: Path) -> None:
    marker = b"I47 transient verbatim marker 7b14d2 must never persist in I47 state"
    env = prepare_i47(tmp_path, source=marker)
    receipt = env["i47"].advance()
    serialized = b"".join(
        path.read_bytes()
        for path in sorted(env["i47"].store.root.rglob("*.json"))
    )
    assert marker not in serialized
    assert receipt["verbatim_corpus_source_retained"] is False
    assert receipt["physical_memory_erasure_claimed"] is False
    assert receipt["external_source_storage_erasure_claimed"] is False
    assert receipt["authoritative_float_weights_created"] is False


def test_i47_runtimeos_derives_advance_and_rejects_caller_override(tmp_path: Path) -> None:
    env = prepare_i47(tmp_path)
    app = FastAPI()
    i46_control = SimpleNamespace(closure=env["i46"])
    i33_control = SimpleNamespace(
        advancer=env["i33"],
        configuration_error=None,
        status=lambda: {
            "authority_configuration_source": "EXPLICIT_INTERNAL_CONFIGURATION"
        },
    )
    control = install_pass218_i47_manifest_bound_i33_curriculum_advance_control(
        app,
        i46_control,
        i33_control,
        env["lifecycle"],
        state_root=tmp_path / "runtime-os-state",
    )
    client = TestClient(app)
    rejected = client.post(
        PASS218_I47_ADVANCE_PATH,
        json={"curriculum_position": 99},
    )
    assert rejected.status_code == 409
    accepted = client.post(PASS218_I47_ADVANCE_PATH, json={})
    assert accepted.status_code == 200
    status = client.get(PASS218_I47_STATUS_PATH).json()
    assert status["api_derives_i33_advance_from_durable_i46_i32_chain"] is True
    assert status["api_can_override_curriculum_identity"] is False
    assert status["api_can_mint_curriculum_authority"] is False
    assert status["api_ingests_next_source"] is False
    assert status["api_advances_stage"] is False
    assert control.advance_control.i33_invocation_count == 1


def test_i47_authoritative_surfaces_contain_no_float_literals() -> None:
    paths = [
        ROOT / "hhs_runtime" / "pass218" / "manifest_bound_i33_curriculum_advance_i47.py",
        ROOT / "hhs_backend" / "runtime_os_pass218_manifest_i33_curriculum_advance_i47.py",
    ]
    for path in paths:
        tree = ast.parse(path.read_text("utf-8"))
        floats = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, path
