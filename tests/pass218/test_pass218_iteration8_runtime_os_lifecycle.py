from __future__ import annotations

import ast
import asyncio
from hashlib import sha256
from pathlib import Path

import pytest
from fastapi import FastAPI

from hhs_backend.runtime_os_pass218_lifecycle import (
    PASS218_APP_STATE_KEY,
    PASS218_RUNTIME_STATUS_PATH,
    install_pass218_runtime_os_lifecycle,
    resolve_pass218_state_root,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218 import (
    ClosedTransactionVectorVM5184Adapter,
    PASS218_RUNTIME_LIFECYCLE_VERSION,
    RUNTIME_LIFECYCLE_STATUS_SCHEMA,
    Pass218RuntimeLifecycle,
    Pass218RuntimeLifecycleError,
    Pass218RuntimeLifecycleNotReady,
    PromotionAuthorityGrant,
    PromotionAuthorizationJournal,
    PromotionProofMembrane,
    SourceTransaction,
)

ROOT = Path(__file__).resolve().parents[2]


def _source(label: str = "A") -> str:
    return (
        "A synthetic narrative exists only to test the Iteration 8 Runtime OS "
        f"lifecycle {label}. It must never be retained. A second sentence "
        "ensures a non-empty deterministic structural projection."
    )


def _beat(ordinal: int, label: str) -> dict[str, object]:
    payload: dict[str, object] = {
        "ordinal": ordinal,
        "source_span_sha256": sha256(
            f"iteration8-span-{ordinal}-{label}".encode("utf-8")
        ).hexdigest(),
        "paragraph_count": 1,
        "token_count": 17 + ordinal,
        "sentence_count": 1,
        "dialogue_turn_count": ordinal % 2,
        "perspective_counts": {
            "first_person": 0,
            "second_person": 0,
            "third_person": 1,
        },
        "negation_count": 1,
        "modal_count": 1,
        "authority_count": 1,
        "temporal_count": 1,
        "dominant_perspective": "THIRD_PERSON",
        "relation_types": ["TEMPORAL_SUCCESSION"],
        "distinction_mentions": [],
        "verbatim_source_retained": False,
    }
    payload["beat_hash72"] = hash72_digest(
        {"domain": "HHS-P218-NARRATIVE-BEAT-I2-V1"}, payload
    )
    return payload


def _hydration(label: str = "A") -> dict[str, object]:
    source = _source(label)
    genesis = hash72_digest({"domain": "P218-I8-TEST-GENESIS"}, label.encode())
    hydration = hash72_digest({"domain": "P218-I8-TEST-HYDRATION"}, label.encode())
    validation = hash72_digest({"domain": "P218-I8-TEST-VALIDATION"}, label.encode())
    return {
        "schema": "HHS-P218-NARRATIVE-HYDRATION-CANDIDATE-I2-V1",
        "hydrator_version": "HHS-P218-NARRATIVE-HYDRATOR-I2-V1",
        "source_id": f"iteration8-{label}",
        "source_sha256": sha256(source.encode("utf-8")).hexdigest(),
        "source_epistemic_class": "FICTIONAL_COUNTERFACTUAL",
        "genesis_seed_hash72": genesis,
        "grammar_rule_set_hash72": hash72_digest(
            {"domain": "P218-I8-TEST-GRAMMAR"}, label.encode()
        ),
        "beats": [_beat(index, label) for index in range(4)],
        "hydration_hash72": hydration,
        "validation_hash72": validation,
        "hash216": genesis + hydration + validation,
        "hash216_semantics": [
            "PREVIOUS_GENESIS_STATE",
            "NEXT_HYDRATION_CANDIDATE",
            "VALIDATION_RECEIPT",
        ],
        "verbatim_source_retained": False,
        "source_text_retained": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "authoritative_vector_store_promotion": False,
        "authoritative_float_weights": False,
    }


def _authorized(label: str = "A", *, sequence: int = 1):
    source = _source(label)
    transaction = SourceTransaction.begin(_hydration(label), source)
    transaction.commit_and_purge()
    staged = ClosedTransactionVectorVM5184Adapter().stage(transaction.snapshot())
    proof = PromotionProofMembrane().prove(
        closed_transaction_snapshot=transaction.snapshot(),
        staged_candidate=staged,
    )
    grant = PromotionAuthorityGrant.bind(
        proof,
        grantor_authority_hash72=hash72_digest(
            {"domain": "P218-I8-TEST-GRANTOR"},
            f"authority-{label}".encode("utf-8"),
        ),
        grant_sequence=sequence,
    )
    journal = PromotionAuthorizationJournal()
    authorization = journal.authorize(proof, grant)
    return staged, journal, authorization


def _prepare(lifecycle: Pass218RuntimeLifecycle, label: str = "A", *, sequence: int = 1):
    staged, journal, authorization = _authorized(label, sequence=sequence)
    boundary = lifecycle.canonical_boundary()
    prepared = boundary.prepare(
        authorization=authorization,
        staged_candidate=staged,
        authorization_journal=journal,
    )
    return prepared, journal, authorization


def _commit(lifecycle: Pass218RuntimeLifecycle, label: str = "A", *, sequence: int = 1):
    prepared, journal, authorization = _prepare(lifecycle, label, sequence=sequence)
    result = lifecycle.commit_prepared(
        prepared,
        authorization_journal=journal,
    )
    return result, journal, authorization


def test_iteration8_declares_runtime_lifecycle_contract() -> None:
    assert PASS218_RUNTIME_LIFECYCLE_VERSION == "HHS-P218-RUNTIME-OS-LIFECYCLE-I8-V1"
    assert RUNTIME_LIFECYCLE_STATUS_SCHEMA == "HHS-P218-I8-RUNTIME-LIFECYCLE-STATUS-V1"
    assert PASS218_RUNTIME_STATUS_PATH == "/api/runtime/pass218/lifecycle/status"


def test_ingestion_is_closed_before_startup(tmp_path: Path) -> None:
    lifecycle = Pass218RuntimeLifecycle(tmp_path)
    assert lifecycle.ingestion_enabled is False
    with pytest.raises(Pass218RuntimeLifecycleNotReady, match="P218_I8_INGESTION_GATE_CLOSED"):
        lifecycle.require_ingestion_ready()


def test_empty_first_boot_opens_gate_without_inventing_canonical_authority(tmp_path: Path) -> None:
    lifecycle = Pass218RuntimeLifecycle(tmp_path)
    status = lifecycle.startup()
    assert status["state"] == "EMPTY_READY"
    assert status["ingestion_enabled"] is True
    assert status["canonical_authority_present"] is False
    assert status["canonical_commit_count"] == 0
    assert status["restore_state"] == "NO_DURABLE_CANONICAL_GENERATION"
    assert not lifecycle.store.manifest_path.exists()


def test_present_invalid_manifest_fails_closed_for_ingestion(tmp_path: Path) -> None:
    lifecycle = Pass218RuntimeLifecycle(tmp_path)
    lifecycle.store.root.mkdir(parents=True, exist_ok=True)
    lifecycle.store.manifest_path.write_bytes(b"{invalid")
    status = lifecycle.startup()
    assert status["state"] == "STARTUP_RECOVERY_BLOCKED"
    assert status["ingestion_enabled"] is False
    assert status["authority_ready"] is False
    assert status["last_error_code"].startswith("P218_")


def test_commit_is_checkpointed_before_ingestion_reopens(tmp_path: Path) -> None:
    lifecycle = Pass218RuntimeLifecycle(tmp_path)
    lifecycle.startup()
    result, _, _ = _commit(lifecycle)
    status = lifecycle.status()
    assert result["state"] == "CANONICAL_COMMITTED_DURABLE_READY"
    assert status["ingestion_enabled"] is True
    assert status["durability_ready"] is True
    assert status["durability_pending"] is False
    assert status["canonical_commit_count"] == 1
    assert lifecycle.store.manifest_path.is_file()
    assert result["canonical_root_hash72"] == status["canonical_root_hash72"]


def test_crash_restart_restores_exact_root_snapshot_and_consumed_receipt(tmp_path: Path) -> None:
    lifecycle = Pass218RuntimeLifecycle(tmp_path)
    lifecycle.startup()
    result, _, authorization = _commit(lifecycle)
    root = lifecycle.target.root_hash72()
    snapshot = lifecycle.target.snapshot_bytes()
    receipt = result["canonical_receipt"]

    restarted = Pass218RuntimeLifecycle(tmp_path)
    status = restarted.startup()
    assert status["state"] == "RESTORED_READY"
    assert restarted.target.root_hash72() == root
    assert restarted.target.snapshot_bytes() == snapshot
    assert restarted.target.committed_receipt(authorization["authorization_hash72"]) == receipt
    assert status["restart_new_authorization_minted"] is False
    assert status["restart_new_canonical_mutation_invoked"] is False


def test_durability_failure_closes_ingestion_and_marks_pending(tmp_path: Path) -> None:
    lifecycle = Pass218RuntimeLifecycle(tmp_path)
    lifecycle.startup()
    prepared, journal, _ = _prepare(lifecycle)
    with pytest.raises(
        Pass218RuntimeLifecycleError,
        match="P218_I8_COMMIT_DURABILITY_CHECKPOINT_FAILED",
    ):
        lifecycle.commit_prepared(
            prepared,
            authorization_journal=journal,
            fail_before_manifest_swap=True,
        )
    status = lifecycle.status()
    assert status["canonical_commit_count"] == 1
    assert status["ingestion_enabled"] is False
    assert status["durability_pending"] is True
    assert status["state"] == "CANONICAL_COMMITTED_DURABILITY_BLOCKED"
    assert not lifecycle.store.manifest_path.exists()


def test_pending_durability_retry_requires_no_new_authorization_or_commit(tmp_path: Path) -> None:
    lifecycle = Pass218RuntimeLifecycle(tmp_path)
    lifecycle.startup()
    prepared, journal, authorization = _prepare(lifecycle)
    with pytest.raises(Pass218RuntimeLifecycleError):
        lifecycle.commit_prepared(
            prepared,
            authorization_journal=journal,
            fail_before_manifest_swap=True,
        )
    receipt_before = lifecycle.target.committed_receipt(authorization["authorization_hash72"])
    root_before = lifecycle.target.root_hash72()
    retry = lifecycle.retry_pending_durability()
    assert retry["state"] == "DURABLE_CHECKPOINT_COMMITTED"
    assert lifecycle.ingestion_enabled is True
    assert lifecycle.durability_pending is False
    assert lifecycle.target.root_hash72() == root_before
    assert lifecycle.target.committed_receipt(authorization["authorization_hash72"]) == receipt_before


def test_i6_pre_swap_commit_failure_does_not_create_durability_pending(tmp_path: Path) -> None:
    lifecycle = Pass218RuntimeLifecycle(tmp_path)
    lifecycle.startup()
    prepared, journal, _ = _prepare(lifecycle)
    with pytest.raises(Exception, match="P218_I6_INJECTED_COMMIT_FAILURE_BEFORE_ATOMIC_SWAP"):
        lifecycle.commit_prepared(
            prepared,
            authorization_journal=journal,
            fail_before_atomic_swap=True,
        )
    status = lifecycle.status()
    assert status["canonical_commit_count"] == 0
    assert status["ingestion_enabled"] is True
    assert status["durability_pending"] is False
    assert not lifecycle.store.manifest_path.exists()


def test_clean_shutdown_persists_latest_committed_state_idempotently(tmp_path: Path) -> None:
    lifecycle = Pass218RuntimeLifecycle(tmp_path)
    lifecycle.startup()
    _commit(lifecycle)
    manifest_before = lifecycle.store.manifest_path.read_bytes()
    status = lifecycle.shutdown()
    assert status["state"] == "CLEAN_SHUTDOWN_DURABLE"
    assert status["ingestion_enabled"] is False
    assert status["last_checkpoint_state"] == "DURABLE_CHECKPOINT_IDEMPOTENT_REPLAY"
    assert lifecycle.store.manifest_path.read_bytes() == manifest_before


def test_clean_shutdown_of_empty_first_boot_does_not_create_fake_checkpoint(tmp_path: Path) -> None:
    lifecycle = Pass218RuntimeLifecycle(tmp_path)
    lifecycle.startup()
    status = lifecycle.shutdown()
    assert status["state"] == "CLEAN_SHUTDOWN_EMPTY"
    assert status["canonical_commit_count"] == 0
    assert not lifecycle.store.manifest_path.exists()


def test_second_commit_after_restart_extends_restored_authority(tmp_path: Path) -> None:
    first = Pass218RuntimeLifecycle(tmp_path)
    first.startup()
    _commit(first, "A", sequence=1)

    second = Pass218RuntimeLifecycle(tmp_path)
    second.startup()
    _commit(second, "B", sequence=2)
    assert second.status()["canonical_commit_count"] == 2
    restored = Pass218RuntimeLifecycle(tmp_path)
    restored.startup()
    assert restored.status()["canonical_commit_count"] == 2
    assert restored.target.root_hash72() == second.target.root_hash72()


def test_corrupt_active_generation_recovers_previous_and_reopens_ingestion(tmp_path: Path) -> None:
    lifecycle = Pass218RuntimeLifecycle(tmp_path)
    lifecycle.startup()
    _commit(lifecycle, "A", sequence=1)
    root_first = lifecycle.target.root_hash72()
    _commit(lifecycle, "B", sequence=2)
    manifest = lifecycle.store._load_manifest()
    (lifecycle.store.generations / manifest["active_generation"]).write_bytes(b"{corrupt")

    restarted = Pass218RuntimeLifecycle(tmp_path)
    status = restarted.startup()
    assert status["state"] == "RECOVERED_PREVIOUS_READY"
    assert status["restore_state"] == "RECOVERED_PREVIOUS_VALID_GENERATION"
    assert status["ingestion_enabled"] is True
    assert restarted.target.root_hash72() == root_first


def test_unrecoverable_generation_corruption_keeps_gate_closed(tmp_path: Path) -> None:
    lifecycle = Pass218RuntimeLifecycle(tmp_path)
    lifecycle.startup()
    _commit(lifecycle)
    manifest = lifecycle.store._load_manifest()
    (lifecycle.store.generations / manifest["active_generation"]).write_bytes(b"{corrupt")

    restarted = Pass218RuntimeLifecycle(tmp_path)
    status = restarted.startup()
    assert status["state"] == "STARTUP_RECOVERY_BLOCKED"
    assert status["ingestion_enabled"] is False
    with pytest.raises(Pass218RuntimeLifecycleNotReady):
        restarted.canonical_boundary()


def test_status_carries_no_source_learning_truth_or_action_authority(tmp_path: Path) -> None:
    lifecycle = Pass218RuntimeLifecycle(tmp_path)
    lifecycle.startup()
    _commit(lifecycle)
    status = lifecycle.status()
    assert status["canonical_learning_commit_invoked"] is False
    assert status["truth_promotion"] is False
    assert status["action_authority_minted"] is False
    assert status["verbatim_source_retained"] is False
    assert status["pass165_source_retaining_path_invoked"] is False


def test_checkpoint_current_on_empty_state_is_non_mutating(tmp_path: Path) -> None:
    lifecycle = Pass218RuntimeLifecycle(tmp_path)
    lifecycle.startup()
    result = lifecycle.checkpoint_current()
    assert result["state"] == "NO_CANONICAL_COMMIT_TO_CHECKPOINT"
    assert lifecycle.target.record()["canonical_commit_count"] == 0
    assert not lifecycle.store.manifest_path.exists()


def test_backend_installer_is_idempotent_and_registers_status_before_root_mount(tmp_path: Path) -> None:
    app = FastAPI()
    first = install_pass218_runtime_os_lifecycle(app, state_root=tmp_path)
    lifespan_after_first = app.router.lifespan_context
    second = install_pass218_runtime_os_lifecycle(app, state_root=tmp_path / "ignored")
    assert first is second
    assert app.router.lifespan_context is lifespan_after_first
    assert getattr(app.state, PASS218_APP_STATE_KEY) is first
    paths = [str(getattr(route, "path", "")) for route in app.router.routes]
    assert paths.count(PASS218_RUNTIME_STATUS_PATH) == 1


def test_backend_lifespan_opens_ingestion_only_inside_started_service(tmp_path: Path) -> None:
    app = FastAPI()
    lifecycle = install_pass218_runtime_os_lifecycle(app, state_root=tmp_path)

    async def exercise() -> tuple[dict[str, object], dict[str, object]]:
        async with app.router.lifespan_context(app):
            inside = lifecycle.status()
        outside = lifecycle.status()
        return inside, outside

    inside, outside = asyncio.run(exercise())
    assert inside["state"] == "EMPTY_READY"
    assert inside["ingestion_enabled"] is True
    assert outside["state"] == "CLEAN_SHUTDOWN_EMPTY"
    assert outside["ingestion_enabled"] is False


def test_state_root_resolution_prefers_explicit_pass218_root(monkeypatch, tmp_path: Path) -> None:
    explicit = tmp_path / "explicit"
    data = tmp_path / "data"
    monkeypatch.setenv("HHS_PASS218_STATE_ROOT", str(explicit))
    monkeypatch.setenv("HHS_DATA_DIR", str(data))
    assert resolve_pass218_state_root() == explicit.resolve()


def test_state_root_resolution_uses_data_dir_when_explicit_absent(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("HHS_PASS218_STATE_ROOT", raising=False)
    monkeypatch.setenv("HHS_DATA_DIR", str(tmp_path / "data"))
    assert resolve_pass218_state_root() == (tmp_path / "data" / "pass218").resolve()


def test_runtime_os_entrypoints_install_lifecycle_before_public_projection() -> None:
    for relative in (
        "hhs_backend/runtime_os_visual_server.py",
        "hhs_backend/runtime_os_application_server.py",
    ):
        source = (ROOT / relative).read_text("utf-8")
        install_at = source.index("PASS218_RUNTIME_OS_LIFECYCLE = install_pass218_runtime_os_lifecycle(app)")
        project_at = source.index("project_runtime_os(app, mount_name=PUBLIC_MOUNT_NAME)")
        assert install_at < project_at
        assert "PASS218_RUNTIME_STATUS_PATH" in source


def test_digitalocean_service_provisions_persistent_pass218_state_root() -> None:
    service = (
        ROOT / "deploy/digitalocean/hhs-pass196-integrated-environment.service"
    ).read_text("utf-8")
    assert "Environment=HHS_PASS218_STATE_ROOT=/var/lib/hhs/pass218" in service
    assert "ReadWritePaths=/var/lib/hhs" in service


def test_iteration8_modules_do_not_import_pass165_or_use_authoritative_float_literals() -> None:
    for relative in (
        "hhs_runtime/pass218/lifecycle.py",
        "hhs_backend/runtime_os_pass218_lifecycle.py",
    ):
        source = (ROOT / relative).read_text("utf-8")
        tree = ast.parse(source)
        imports = []
        floats = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
            elif isinstance(node, ast.Constant) and isinstance(node.value, float):
                floats.append(node.value)
        assert all("pass165" not in name.lower() for name in imports)
        assert not floats
