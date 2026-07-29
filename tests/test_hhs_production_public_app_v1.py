from __future__ import annotations

from pathlib import Path


def route_paths(app) -> set[str]:
    return {str(getattr(route, "path", "")) for route in app.router.routes}


def test_production_server_composes_canonical_backend_and_visual_ide():
    from hhs_backend.production_server import app

    paths = route_paths(app)
    required = {
        "/healthz",
        "/api/system/status",
        "/api/runtime/live/status",
        "/api/runtime/gui/command",
        "/api/runtime/workspace/status",
        "/api/runtime/workspace/command",
        "/api/runtime/capability/status",
        "/api/runtime/capability/resolve",
        "/api/runtime/document/perception/status",
        "/api/runtime/document/perceive",
        "/api/assistant/health",
        "/api/assistant/chat",
        "/v1/modalities/language/models/word2vec/status",
        "/ws/runtime",
    }
    assert required.issubset(paths)
    # Starlette represents a StaticFiles mount at the public root with path "".
    assert "" in paths or "/" in paths


def test_procfile_boots_canonical_production_server():
    procfile = Path("Procfile").read_text(encoding="utf-8")
    assert "hhs_backend.production_server:app" in procfile
    assert "hhs_backend.heroku_server:app" not in procfile


def test_frontend_entrypoint_is_canonical_runtime_ide_not_replacement_app():
    source = Path("hhs_gui/main.tsx").read_text(encoding="utf-8")
    assert "CanonicalRuntimeIDE" in source
    assert "RuntimeOS" in source
    assert "ProductionApp" not in source
    assert "global.css" in source


def test_canonical_workspace_exposes_only_integrated_callable_surfaces():
    source = Path("hhs_gui/runtime_os/workspace/HHSWorkspaceShell.tsx").read_text(
        encoding="utf-8"
    )
    for token in [
        "RuntimeAssistantPanel",
        "LiveBackendCapabilityPanel",
        "RuntimeProjectTree",
        "MultimodalIngressPanel",
        "HHSSymbolicEditor",
        "InterpreterConsole",
        "CompilerWorkbench",
        "EmulatorControlPanel",
        "RuntimeGraphCanvas",
        "SemanticMemoryPanel",
        "ReceiptLedgerInspector",
        "MutationHistoryPanel",
    ]:
        assert token in source

    for token in [
        "CapabilityRegistryPanel",
        "ProviderInspector",
        "DocumentPerceptionPanel",
        "OCRProjectionViewer",
        "runtime_application_missing",
    ]:
        assert token not in source


def test_public_html_keeps_boot_failure_visible():
    source = Path("hhs_gui/index.html").read_text(encoding="utf-8")
    assert "HHS Visual Runtime OS Workspace" in source
    assert "frontend_boot_timeout" in source
    assert "dataset.hhsMounted" in source
    assert "overlay.remove()" not in source


def test_assistant_is_real_api_client_without_suggestion_autosubmit():
    source = Path(
        "hhs_gui/runtime_os/assistant/RuntimeAssistantPanel.tsx"
    ).read_text(encoding="utf-8")
    assert 'requestJson("/api/assistant/health")' in source
    assert 'requestJson("/api/assistant/chat"' in source
    assert "No assistant response or runtime mutation was fabricated" in source
    assert "Suggestion" not in source
    assert "setInput(\"Explain" not in source


def test_live_capability_panel_calls_canonical_backend():
    source = Path(
        "hhs_gui/runtime_os/capability/LiveBackendCapabilityPanel.tsx"
    ).read_text(encoding="utf-8")
    for endpoint in [
        "/api/runtime/canonical-observer/status",
        "/api/runtime/capability/status",
        "/api/runtime/capability/contracts",
        "/api/runtime/capability/providers",
        "/api/runtime/capability/resolve",
        "/api/runtime/document/perception/status",
        "/v1/modalities/language/models/word2vec/status",
    ]:
        assert endpoint in source


def test_provider_hierarchy_uses_gemma_then_native_hhs_without_canned_demo():
    paths = [
        "hhs_backend/runtime/hhs_production_assistant_v1.py",
        "hhs_backend/runtime/hhs_native_litert_lm_provider_v1.py",
        "hhs_backend/runtime/hhs_capability_provider_registry_v1.py",
        "hhs_backend/runtime/hhs_litert_lm_assistant_v1.py",
    ]
    combined = "\n".join(Path(path).read_text(encoding="utf-8") for path in paths)
    assert "provider:hhs.litert_lm.gemma4" in combined
    assert "provider:hhs.local.text" in combined
    assert "Pass 166" in combined or "pass166" in combined
    assert "The request was received without runtime mutation" not in combined
