from __future__ import annotations

from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "applications" / "holofractal_harmonizer"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_pass176_activation_gate_and_contract_are_repository_visible() -> None:
    contract = read(ROOT / "HHS_PASS_176_FROZEN_PRODUCTION_MULTIMODAL_IDE_STABILIZATION_PERFORMANCE_RECOVERY.md")
    receipt = json.loads(read(ROOT / "evidence" / "pass175" / "PASS_175_TERMINAL_COMPLETION_RECEIPT.json"))
    assert receipt["terminal_pass175_completion"] is True
    assert "HHS-P176-FPMIDE-SPR-HSI" in contract
    assert "frozen interface identity" in contract
    assert "Pass 176 SHALL consume Pass 175 services" in contract


def test_stability_runtime_implements_ordered_idempotent_boot_and_recovery() -> None:
    core = read(APP / "src" / "pass176-stability-core.mjs")
    browser = read(APP / "src" / "pass176-stability.mjs")
    visual = read(APP / "src" / "visual-ide.mjs")
    required_stages = [
        "DOCUMENT_READY",
        "STATIC_THEME_READY",
        "CORE_WORKSPACE_READY",
        "PROJECT_STATE_RESTORED",
        "EDITOR_READY",
        "PREVIEW_READY",
        "ASSISTANT_READY",
        "BACKEND_CAPABILITY_CHECKED",
        "OPTIONAL_REGISTRY_HISTORY_DIAGNOSTICS_LOADING",
        "INTERACTIVE",
    ]
    for stage in required_stages:
        assert stage in core
        assert stage in browser or stage in visual
    assert "if (this.bootPromise) return this.bootPromise" in browser
    assert "HHS_P176_STALE_ASYNC_RESPONSE" in core
    assert "HHS_PASS_176_RECOVERY_ENVELOPE_V1" in core
    assert "authoritativeBackendDurabilityClaimed: false" in browser
    assert "canonicalFrontendAuthority: false" in browser
    assert "HHS_PASS_176_BACKEND_AUTHORITY_EVIDENCE_V1" in browser
    assert "vm81AuthorityPreserved: this.authorityEvidence?.vm81AuthorityPreserved === true" in browser
    assert "hash72CommitStreams: this.authorityEvidence?.hash72CommitStreams || 0" in browser
    assert "setAuthorityEvidence({ productHealth, pass175 })" in visual


def test_human_safe_interaction_and_resource_lifecycle_are_bound() -> None:
    browser = read(APP / "src" / "pass176-stability.mjs")
    style = read(APP / "src" / "pass176-stability.css")
    core = read(APP / "src" / "pass176-stability-core.mjs")
    for token in [
        "DRAG_THRESHOLD_PX = 8",
        "pointercancel",
        "releasePointerCapture",
        "visibilitychange",
        "beforeunload",
        "PerformanceObserver",
        "disposeAll",
        "cancelAll",
    ]:
        assert token in browser or token in core
    assert "Promise.race([executionPromise, abortPromise])" in core
    assert "prefers-reduced-motion" in style
    assert "min-height: 2.75rem" in style
    assert "data-hhs-pointer-owner" in style


def test_real_ide_surfaces_remain_primary_and_pass175_is_preserved() -> None:
    visual = read(APP / "src" / "visual-ide.mjs")
    production = read(ROOT / "hhs_backend" / "production_server.py")
    application = read(ROOT / "hhs_backend" / "application_ide_server.py")
    procfile = read(ROOT / "Procfile")
    assert "initIntegratedAssistant" in visual
    assert "initApplicationStudio" in visual
    assert "initDeployableAppCompiler" in visual
    assert "initPass175Processor" in visual
    assert "initPass175TerminalProcessor" in visual
    assert "initProductionRecovery" in visual
    assert "initDeploymentHealth" in visual
    assert "HHSVisualIDE" in visual
    assert "window.HHSVisualIDEBoot" in visual
    assert 'VISUAL_ROOT = ROOT_DIR / "applications" / "holofractal_harmonizer"' in production
    assert "hhs-production-harmonizer" in production
    assert "pass175_terminal_router" in application
    assert "hhs-full-application-ide" in application
    assert "hhs_backend.application_ide_server:app" in procfile


def test_pass176_browser_and_repetition_evidence_harness_is_bounded() -> None:
    smoke = read(APP / "ux_lab" / "pass176_stability_smoke.py")
    node_test = read(APP / "tests" / "pass176-stability.test.mjs")
    assert "assistantCycles: 100" in smoke
    assert "paneCycles: 100" in smoke
    assert "resource growth detected" in smoke
    assert "console errors observed" in smoke
    assert "page errors observed" in smoke
    assert "HTTP errors observed" in smoke
    assert "HHSGUIReliability.selectMobilePane" in smoke
    assert "editorRestored" in smoke
    assert "authorityEvidence" in smoke
    assert "for (let cycle = 0; cycle < 100; cycle += 1)" in node_test
    assert "bounded jobs deduplicate duplicate invocations" in node_test
    assert "executor ignores AbortSignal" in node_test
    assert "canonical key" in node_test


def test_generated_template_projects_remain_editable_and_unsaved() -> None:
    runtime = read(APP / "src" / "application-templates-runtime.mjs")
    materializer = runtime[runtime.index("export function materializeApplicationTemplate"):]
    assert "dirty: true" in materializer
    assert "dirty: false" not in materializer
    assert "checkpoint: `Created from ${template.label} starter`" in materializer


def test_temporary_pass176_repair_machinery_is_absent() -> None:
    assert not (ROOT / "tools" / "patch_pass176.py").exists()
    assert not (ROOT / "tools" / "patch_pass176_terminal.py").exists()
    assert not (ROOT / "tools" / "patch_pass176_production_routes_and_smoke.py").exists()
    assert not (ROOT / "tools" / "patch_pass176_template_dirty.py").exists()
    assert not (ROOT / "tools" / "pass176_patch_b64").exists()
    assert not (ROOT / "tools" / "pass176_patch_chunks").exists()
    assert not (ROOT / ".github" / "workflows" / "pass176-terminal-repair.yml").exists()
    assert not (ROOT / ".github" / "workflows" / "pass176-production-route-repair.yml").exists()
    assert not (ROOT / ".github" / "workflows" / "pass176-template-dirty-repair.yml").exists()
    assert not (APP / "pass176-source-bundle.tar").exists()
