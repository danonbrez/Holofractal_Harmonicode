from __future__ import annotations

import io
import zipfile

from hhs_backend.runtime.hhs_application_factory_v1 import (
    ApplicationFactory,
    LIFECYCLE_STAGES,
    MODULE_LIBRARY,
    WORKFLOW_LIBRARY,
    application_factory_self_test,
)


def test_library_exposes_plug_and_play_modules_and_complete_workflows():
    assert "runtime.vm81" in MODULE_LIBRARY
    assert "assistant.development" in MODULE_LIBRARY
    assert "graphics.native" in MODULE_LIBRARY
    assert "universal_multimodal" in WORKFLOW_LIBRARY
    universal = WORKFLOW_LIBRARY["universal_multimodal"]
    assert set(universal["modules"]) == set(MODULE_LIBRARY)


def test_project_creation_closes_dependency_graph_and_preserves_sources():
    factory = ApplicationFactory()
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
    factory = ApplicationFactory()
    project = factory.create_project(name="Game", workflow_id="game_2d")["project"]
    plan = factory.plan_changes(project["project_id"], ["src/game.js"])["plan"]
    assert "graphics.native" in plan["impacted_modules"]
    assert "testing.acceptance" in plan["impacted_modules"]
    assert plan["parallel_candidate_groups"]
    assert plan["singleton_commit_authority"] is True


def test_lifecycle_is_finite_checkpointed_and_replayable():
    factory = ApplicationFactory()
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
    factory = ApplicationFactory()
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
    factory = ApplicationFactory()
    project = factory.create_project(name="App", workflow_id="web_application")["project"]
    rejected_path = factory.upsert_file(project["project_id"], "../outside.txt", "no")
    rejected_workflow = factory.create_project(name="Unknown", workflow_id="not-real")
    assert rejected_path["ok"] is False
    assert rejected_workflow["ok"] is False


def test_application_factory_self_test():
    result = application_factory_self_test()
    assert result["ok"] is True
    assert result["status"]["source_export_independent_of_compile"] is True
    assert result["status"]["parallel_state_authority"] is False
