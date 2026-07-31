from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HEALTH = (ROOT / "applications/holofractal_harmonizer/src/deployment-health.mjs").read_text(encoding="utf-8")
ENTRY = (ROOT / "applications/holofractal_harmonizer/src/visual-ide.mjs").read_text(encoding="utf-8")
SERVER = (ROOT / "hhs_backend/application_ide_server.py").read_text(encoding="utf-8")
TEMPLATES = (ROOT / "applications/holofractal_harmonizer/src/application-templates-runtime.mjs").read_text(encoding="utf-8")


def test_lightweight_health_routes_precede_fallback_and_static_mount():
    assert '"/health"' in SERVER and '"/api/health"' in SERVER
    assert "HHS_FULL_APPLICATION_IDE_LIVENESS_V1" in SERVER
    assert SERVER.index('app.add_api_route(\n        "/health"') < SERVER.index("app.router.routes.extend(_deferred_api_fallback_routes)")
    assert '"frontend_runtime_authority": False' in SERVER


def test_degraded_mode_keeps_local_work_available():
    runtime_selectors = HEALTH.split("const RUNTIME_SELECTORS = [", 1)[1].split("];", 1)[0]
    assert "Editing, preview, and source/runnable ZIP export remain available" in HEALTH
    assert "#hhs-app-test" in runtime_selectors
    assert "#pass175-terminal-window button" in runtime_selectors
    assert "#hhs-app-preview" not in runtime_selectors
    assert "#hhs-app-export" not in runtime_selectors


def test_assistant_is_gated_without_breaking_prompt_editing():
    assert "prompt.disabled = false" in HEALTH
    assert "prompt.readOnly = false" in HEALTH
    assert "form.addEventListener('submit'" in HEALTH
    assert "Your draft remains in the input" in HEALTH


def test_optimistic_runtime_controls_are_fail_closed():
    assert "node.disabled = true" in HEALTH
    assert "No firmware, VM81, Hash216, or receipt state was changed." in HEALTH
    assert "document.dispatchEvent(new CustomEvent('hhs:backend-health'" in HEALTH


def test_preview_console_deduplication_is_bound_once():
    assert "dedupePreviewConsole" in HEALTH
    assert "output.dataset.hhsDedupeBound = 'true'" in HEALTH
    assert "Application preview initialized" in HEALTH


def test_entrypoint_initializes_health_after_recovery():
    assert "import { initDeploymentHealth } from './deployment-health.mjs';" in ENTRY
    assert "initProductionRecovery(); initDeploymentHealth();" in ENTRY


def test_starters_are_readable_and_clean():
    assert "readableHtml" in TEMPLATES and "readableCss" in TEMPLATES
    assert "dirty: false" in TEMPLATES
    assert "checkpoint: `Created from ${template.label} starter`" in TEMPLATES
