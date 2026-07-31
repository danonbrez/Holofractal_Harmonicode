from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "applications/holofractal_harmonizer/src/production-recovery.mjs"
ENTRY = ROOT / "applications/holofractal_harmonizer/src/visual-ide.mjs"


def test_bounded_jobs_and_recovery_controls():
    text = MODULE.read_text(encoding="utf-8")
    assert "PER_JOB_TIMEOUT_MS = 10_000" in text
    assert "cancelActiveJob" in text and ".abort(" in text
    assert "retryLastJob" in text
    assert "last_successful_checkpoint" in text
    assert "correlation_id" in text and "job_id" in text


def test_source_export_is_independent_of_compilation():
    text = MODULE.read_text(encoding="utf-8")
    source_fn = re.search(r"export function downloadSourceProject\(\).*?\n}\n", text, re.S)
    assert source_fn
    assert "sourceArchiveBuild" in source_fn.group(0)
    assert "buildDeployableApplicationZip" not in source_fn.group(0)
    assert "compilation_required: false" in text
    assert "backend_runtime_authority_claimed: false" in text


def test_preview_has_explicit_ready_error_and_test_bridge():
    text = MODULE.read_text(encoding="utf-8")
    for token in [
        "hhs-preview-bridge-v1",
        "hhs-preview-parent-v1",
        "PREVIEW_READY_TIMEOUT_MS = 5_000",
        "runtime-error",
        "test-result",
        "PREVIEW_TEST_BRIDGE_TIMEOUT",
    ]:
        assert token in text


def test_application_workspace_preserves_advanced_runtime():
    text = MODULE.read_text(encoding="utf-8")
    assert "APPLICATION IDE" in text
    assert "ADVANCED RUNTIME" in text
    assert "detachAdvancedSurfaces" in text
    assert "restoreAdvancedSurfaces" in text
    assert "frontend_runtime_authority: false" in text


def test_generated_starters_are_clean_and_entrypoint_loads_recovery():
    text = MODULE.read_text(encoding="utf-8")
    entry = ENTRY.read_text(encoding="utf-8")
    assert "file.dirty = false" in text
    assert "Created from" in text and "starter checkpoint" in text
    assert "initProductionRecovery" in entry


def test_whole_job_deadline_and_application_entrypoint_selection():
    text = MODULE.read_text(encoding="utf-8")
    assert "started_epoch_ms" in text
    assert "PER_JOB_TIMEOUT_MS - elapsed" in text
    assert "#ide-preview-entrypoint" in text
    assert "accessibility: () => previewCommand('accessibility')" in text


def test_all_primary_lifecycle_entrypoints_use_bounded_controller():
    entry = ENTRY.read_text(encoding="utf-8")
    module = MODULE.read_text(encoding="utf-8")
    assert "lifecycle: runBoundedProjectTest" in entry
    assert "runLifecycle" not in entry
    assert "lastRetry = runBoundedProjectTest" in module
