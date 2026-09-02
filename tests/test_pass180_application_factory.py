from __future__ import annotations

import io
import zipfile

from hhs_runtime.pass163.vmrc import VMRCRuntime

from hhs_backend.runtime.hhs_application_factory_v1 import (
    ApplicationFactory,
    LIFECYCLE_STAGES,
    MODULE_LIBRARY,
    WORKFLOW_LIBRARY,
    application_factory_self_test,
)


def _factory() -> ApplicationFactory:
    return ApplicationFactory(vm81=VMRCRuntime())


def test_library_exposes_plug_and_play_modules_and_complete_workflows():
    assert "runtime.vm81" in MODULE_LIBRARY
    assert "assistant.development" in MODULE_LIBRARY
    assert "graphics.native" in MODULE_LIBRARY
    assert "universal_multimodal" in WORKFLOW_LIBRARY
    universal = WORKFLOW_LIBRARY["universal_multimodal"]
    assert set(universal["modules"]) == set(MODULE_LIBRARY)


def test_project_creation_closes_dependency_graph_and_preserves_sources():
    factory = _factory()
    result = factory.create_project(name="Calculator", workflow_id="scientific_calculator")
    assert result["ok"] is True
    project = result["project"]
    assert project["workflow_id"] == "scientific_calculator"
    assert "core.project" in project["modules"]
    assert "runtime.vm81" in project["modules"]
    assert "math.exact" in project["modules"]
    assert "index.html" in project["files"]
    assert len(project["source_root_hash72"]) == 72
    assert len(project["project_root_hash72"]) == 72


def test_incremental_plan_limits_work_and_keeps_single_commit_authority():
    factory = _factory()
    project = factory.create_project(name="Game", workflow_id="game_2d")["project"]
    plan = factory.plan_changes(project["project_id"], ["src/game.js"])["plan"]
    assert "graphics.native" in plan["impacted_modules"]
    assert "testing.acceptance" in plan["impacted_modules"]
    assert plan["parallel_candidate_groups"]
    assert plan["singleton_commit_authority"] is True


def test_lifecycle_is_finite_checkpointed_and_replayable():
    factory = _factory()
    project = factory.create_project(name="App", workflow_id="web_application")["project"]
    result = factory.run_lifecycle(project["project_id"], ["src/app.js"], timeout_ms=5_000)
    assert result["ok"] is True
    job = result["job"]
    assert job["state"] == "SUCCEEDED"
    assert [checkpoint["stage"] for checkpoint in job["checkpoints"]] == list(LIFECYCLE_STAGES)
    assert all(len(checkpoint["checkpoint_root_hash72"]) == 72 for checkpoint in job["checkpoints"])
    assert job["result"]["package_manifest"]["source_zip_available_without_compile"] is True
    replay = factory.replay_project(project["project_id"])
    assert replay["ok"] is True
    assert replay["deterministic_replay"] is True


def test_source_zip_export_is_independent_of_compile_and_deterministic():
    factory = _factory()
    project = factory.create_project(name="Document", workflow_id="document_studio")["project"]
    first = factory.export_source_zip(project["project_id"])
    second = factory.export_source_zip(project["project_id"])
    assert first["ok"] is True
    assert first["manifest"]["compile_required"] is False
    assert first["zip_bytes"] == second["zip_bytes"]
    with zipfile.ZipFile(io.BytesIO(first["zip_bytes"])) as archive:
        names = set(archive.namelist())
        assert "index.html" in names
        assert "documents/main.md" in names
        assert ".hhs/application-factory-manifest.json" in names


def test_file_path_traversal_and_unknown_workflow_fail_closed():
    factory = _factory()
    project = factory.create_project(name="App", workflow_id="web_application")["project"]
    rejected_path = factory.upsert_file(project["project_id"], "../outside.txt", "no")
    rejected_workflow = factory.create_project(name="Unknown", workflow_id="not-real")
    assert rejected_path["ok"] is False
    assert rejected_workflow["ok"] is False


def test_canonical_mutation_requires_vm81_and_hash72_follows_admission():
    missing = ApplicationFactory()
    rejected = missing.create_project(name="No authority", workflow_id="web_application")
    assert rejected["ok"] is False
    assert rejected["status"] == "REJECT_APPLICATION_VM81_AUTHORITY"
    assert not missing.projects

    vm81 = VMRCRuntime()
    factory = ApplicationFactory(vm81=vm81)
    before = vm81.epoch
    created = factory.create_project(name="VM81 App", workflow_id="web_application")
    assert created["ok"] is True
    project = created["project"]
    assert vm81.epoch == before + 1
    assert project["vm81_admission"]["classification"] == (
        "HHS_PASS180_APPLICATION_FACTORY_VM81_ADMISSION_VERIFIED"
    )
    assert project["vm81_admission"]["singleton_authority"] is True
    assert project["vm81_admission"]["independent_vm81_authority"] is False
    assert project["vm81_admission"]["validation_mutation_authority"] is False
    assert project["creation_receipt_hash72"]
    assert project["vm81_admission"]["receipt_hash72"]

    before = vm81.epoch
    changed = factory.upsert_file(project["project_id"], "src/app.js", "updated\n")
    assert changed["ok"] is True
    assert vm81.epoch == before + 1
    assert changed["project"]["latest_receipt_hash72"]
    assert changed["project"]["vm81_admission"]["receipt_hash72"]

    before = vm81.epoch
    lifecycle = factory.run_lifecycle(project["project_id"], ["src/app.js"])
    assert lifecycle["ok"] is True
    assert vm81.epoch == before + 1
    assert lifecycle["job"]["result"]["vm81_admission"]["classification"] == (
        "HHS_PASS180_APPLICATION_FACTORY_VM81_ADMISSION_VERIFIED"
    )
    assert lifecycle["job"]["checkpoints"][-1]["details"]["vm81_receipt_hash72"]


def test_application_factory_self_test():
    result = application_factory_self_test()
    assert result["ok"] is True
    assert result["status"]["source_export_independent_of_compile"] is True
    assert result["status"]["parallel_state_authority"] is False
