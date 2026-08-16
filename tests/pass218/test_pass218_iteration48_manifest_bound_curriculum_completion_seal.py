from __future__ import annotations

import ast
from pathlib import Path
import runpy
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_backend.runtime_os_pass218_manifest_curriculum_completion_i48 import (
    PASS218_I48_SEAL_PATH,
    PASS218_I48_STATUS_PATH,
    install_pass218_i48_manifest_bound_curriculum_completion_control,
)
from hhs_runtime.pass218.curriculum_advance_i33 import PASS218_I33_COMPLETE_STATUS
from hhs_runtime.pass218.manifest_bound_curriculum_completion_seal_i48 import (
    PASS218_I48_COMPLETE_STATUS,
    Pass218I48BindingError,
    Pass218I48ManifestBoundCurriculumCompletionSeal,
)

ROOT = Path(__file__).resolve().parents[2]
I47 = runpy.run_path(
    str(
        ROOT
        / "tests"
        / "pass218"
        / "test_pass218_iteration47_manifest_bound_i33_curriculum_advance.py"
    )
)


def prepare_i48(
    tmp_path: Path,
    *,
    source: bytes = b"I48 seals exact manifest-bound curriculum exhaustion after frozen I47.",
):
    env = I47["prepare_i47"](tmp_path, source=source)
    i47_receipt = env["i47"].advance()
    completion = Pass218I48ManifestBoundCurriculumCompletionSeal(
        lifecycle=env["lifecycle"],
        i47_store=env["i47"].store,
        i30_store=env["i30_store"],
        i33_advancer=env["i33"],
        state_root=(
            tmp_path
            / "state"
            / "cognition"
            / "manifest-bound-curriculum-completion-i48"
        ),
    )
    return {**env, "i47_receipt": i47_receipt, "i48": completion}


def test_i48_seals_terminal_i47_and_proves_authoritative_cursor_exhaustion(
    tmp_path: Path,
) -> None:
    env = prepare_i48(tmp_path)
    before = env["i30_store"].active_generation()
    i33_count = env["i33"].advance_count
    receipt = env["i48"].seal()
    after = env["i30_store"].active_generation()
    proof = env["i48"].store.active_proof()

    assert receipt["status"] == PASS218_I48_COMPLETE_STATUS
    assert receipt["curriculum_status"] == PASS218_I33_COMPLETE_STATUS
    assert receipt["authoritative_manifest_exhausted"] is True
    assert receipt["final_cursor_exhausted"] is True
    assert receipt["final_cursor_source_count_matches_manifest"] is True
    assert receipt["no_next_expected_source_verified"] is True
    assert receipt["manifest_source_count"] == receipt["completed_source_count"] == 1
    assert receipt["next_expected_source_id"] is None
    assert receipt["next_expected_stage"] is None
    assert receipt["stage_transition_required"] is False
    assert receipt["i33_curriculum_advance_invoked"] is False
    assert receipt["pass219_handoff_authority_minted"] is False
    assert before == after
    assert env["i33"].advance_count == i33_count == 1
    assert env["i48"].seal_count == 1
    assert proof is not None
    assert proof["source_payload_persisted"] is False


def test_i48_restart_adopts_exact_completion_without_i33_or_i30_mutation(
    tmp_path: Path,
) -> None:
    env = prepare_i48(tmp_path)
    receipt = env["i48"].seal()
    i33_count = env["i33"].advance_count
    generation = env["i30_store"].active_generation()

    restarted = Pass218I48ManifestBoundCurriculumCompletionSeal(
        lifecycle=env["lifecycle"],
        i47_store=env["i47"].store,
        i30_store=env["i30_store"],
        i33_advancer=env["i33"],
        state_root=env["i48"].store.root,
    )
    assert restarted.seal() == receipt
    assert restarted.restart_adoption_count == 1
    assert restarted.seal_count == 0
    assert env["i33"].advance_count == i33_count
    assert env["i30_store"].active_generation() == generation


def test_i48_refuses_to_advance_i33_when_i47_terminal_state_is_absent(
    tmp_path: Path,
) -> None:
    env = I47["prepare_i47"](tmp_path)
    completion = Pass218I48ManifestBoundCurriculumCompletionSeal(
        lifecycle=env["lifecycle"],
        i47_store=env["i47"].store,
        i30_store=env["i30_store"],
        i33_advancer=env["i33"],
        state_root=tmp_path / "rejected-i48",
    )
    with pytest.raises(
        Pass218I48BindingError,
        match="P218_I48_I47_TERMINAL_COMPLETION_REQUIRED",
    ):
        completion.seal()
    assert env["i33"].advance_count == 0
    assert completion.store.active_record() is None


def test_i48_rejects_unrelated_i33_authority_without_mutating_either_lineage(
    tmp_path: Path,
) -> None:
    primary = prepare_i48(tmp_path / "primary")
    other = prepare_i48(
        tmp_path / "other",
        source=b"A different I48 source creates a different authoritative curriculum.",
    )
    primary_count = primary["i33"].advance_count
    other_count = other["i33"].advance_count
    completion = Pass218I48ManifestBoundCurriculumCompletionSeal(
        lifecycle=primary["lifecycle"],
        i47_store=primary["i47"].store,
        i30_store=primary["i30_store"],
        i33_advancer=other["i33"],
        state_root=tmp_path / "mismatched-i48",
    )
    with pytest.raises(
        Pass218I48BindingError,
        match="P218_I48_I33_AUTHORITY_ROOT_MISMATCH",
    ):
        completion.seal()
    assert primary["i33"].advance_count == primary_count
    assert other["i33"].advance_count == other_count
    assert completion.store.active_record() is None


def test_i48_runtimeos_seal_is_empty_intent_and_cannot_widen_authority(
    tmp_path: Path,
) -> None:
    env = prepare_i48(tmp_path)
    app = FastAPI()
    i47_control = SimpleNamespace(advance_control=env["i47"])
    i33_control = SimpleNamespace(
        advancer=env["i33"],
        configuration_error=None,
        status=lambda: {
            "authority_configuration_source": "EXPLICIT_INTERNAL_CONFIGURATION"
        },
    )
    control = install_pass218_i48_manifest_bound_curriculum_completion_control(
        app,
        i47_control,
        i33_control,
        env["lifecycle"],
        state_root=tmp_path / "runtime-os-state",
    )
    client = TestClient(app)
    rejected = client.post(PASS218_I48_SEAL_PATH, json={"advance_stage": True})
    assert rejected.status_code == 409
    accepted = client.post(PASS218_I48_SEAL_PATH, json={})
    assert accepted.status_code == 200
    status = client.get(PASS218_I48_STATUS_PATH).json()
    assert status["api_derives_completion_from_durable_i47_i33_chain"] is True
    assert status["api_can_invoke_i33_curriculum_advance"] is False
    assert status["api_can_ingest_next_source"] is False
    assert status["api_can_advance_stage"] is False
    assert status["api_can_mint_pass219_handoff_authority"] is False
    assert status["api_can_promote_truth"] is False
    assert status["api_can_mint_action_authority"] is False
    assert control.completion.seal_count == 1


def test_i48_persists_no_verbatim_source_payload_and_makes_no_erasure_claim(
    tmp_path: Path,
) -> None:
    marker = b"I48 transient verbatim marker 98b6d7 must not persist in completion state"
    env = prepare_i48(tmp_path, source=marker)
    receipt = env["i48"].seal()
    serialized = b"".join(
        path.read_bytes()
        for path in sorted(env["i48"].store.root.rglob("*.json"))
    )
    assert marker not in serialized
    assert receipt["verbatim_corpus_source_retained"] is False
    assert receipt["physical_memory_erasure_claimed"] is False
    assert receipt["external_source_storage_erasure_claimed"] is False
    assert receipt["authoritative_float_weights_created"] is False


def test_i48_authoritative_surfaces_contain_no_float_literals() -> None:
    paths = [
        ROOT
        / "hhs_runtime"
        / "pass218"
        / "manifest_bound_curriculum_completion_seal_i48.py",
        ROOT
        / "hhs_backend"
        / "runtime_os_pass218_manifest_curriculum_completion_i48.py",
    ]
    for path in paths:
        tree = ast.parse(path.read_text("utf-8"))
        floats = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, path
