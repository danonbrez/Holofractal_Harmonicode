from __future__ import annotations

import asyncio
from pathlib import Path


def route_paths(app) -> set[str]:
    return {str(getattr(route, "path", "")) for route in app.router.routes}


def test_production_server_composes_canonical_backend_and_visual_ide():
    from hhs_backend.production_server import app

    paths = route_paths(app)
    required = {
        "/healthz",
        "/api/system/status",
        "/api/product/health",
        "/api/runtime/authority/status",
        "/api/runtime/live/status",
        "/api/runtime/gui/command",
        "/api/runtime/workspace/status",
        "/api/runtime/workspace/session",
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
    assert "" in paths or "/" in paths


def test_integrated_workspace_session_is_lightweight_and_real():
    from hhs_backend import production_server

    snapshot = production_server._workspace_session_snapshot()
    assert snapshot["schema"] == "HHS_INTEGRATED_WORKSPACE_SESSION_V1"
    assert snapshot["ok"] is True
    assert snapshot["self_tests_executed"] is False
    assert set(snapshot["runtime"]) == {
        "canonical_runtime_attached",
        "graph_initialized",
        "websocket_ready",
        "live_workflow",
    }


def test_hosted_native_assistant_executes_receipt_bearing_turn_without_word2vec():
    from hhs_backend import production_server
    from hhs_backend.runtime.hhs_production_assistant_v1 import (
        DEFAULT_PRODUCTION_ASSISTANT_SERVICE,
    )

    service = DEFAULT_PRODUCTION_ASSISTANT_SERVICE
    service._health_timeout = max(float(service._health_timeout), 5.0)

    installation = service._native_installation_status()
    assert installation["ready"] is True, installation
    assert installation["word2vec_required"] is False, installation

    native_health = asyncio.run(service.native_service.health())
    assert native_health["ok"] is True, native_health
    assert native_health["online"] is True, native_health

    health = asyncio.run(production_server._assistant_health())
    assert health["ok"] is True, health
    assert health["online"] is True, health
    assert health["selected_provider_id"] == "provider:hhs.local.text", health
    assert health["effective_mode"] == "HHS_NATIVE_LITERT_COMPATIBLE", health
    assert health["native_hhs"]["installation"]["ready"] is True
    assert health["native_hhs"]["installation"]["word2vec_required"] is False
    assert health["repository_search_is_provider"] is False
    assert health["same_template_response_enabled"] is False

    thread = service.create_thread(
        project_id="project:hosted-assistant-test",
        title="Hosted assistant execution test",
    )
    turn = asyncio.run(service.send_message(thread["thread_id"], content="AB=P^4"))
    assert turn["ok"] is True, turn
    assert turn["effective_mode"] == "HHS_NATIVE_LITERT_COMPATIBLE", turn
    assert str(turn["assistant_message"]["content"]).strip(), turn
    assert turn["assistant_message"]["message_root_hash72"], turn
    assert turn["provider_invocation_receipt"]["provider_invocation_receipt_hash72"], turn
    assert turn["provider_result_ingress"]["provider_result_ingress_root_hash72"], turn
    assert turn["turn_root_hash72"], turn
    assert turn["runtime_mutation_admitted"] is False


def test_runtime_authority_boots_and_reports_real_workflow_state():
    from hhs_backend import production_server
    from hhs_backend import server as canonical

    async def verify() -> None:
        await canonical.startup_sequence()
        try:
            status = production_server._runtime_authority_status()
            assert status["ok"] is True
            assert status["status"] == "HHS_RUNTIME_AUTHORITY_ONLINE"
            assert status["canonical_runtime_attached"] is True
            assert status["graph_initialized"] is True
            assert status["websocket_ready"] is True
            assert status["live_workflow"]["running"] is True
            assert status["live_workflow"]["authority_ready"] is True
            assert status["runtime_state_hash72"]
            assert status["receipt_hash72"]
            tick = await canonical.LIVE_WORKFLOW.tick_once({"source": "production_authority_test"})
            assert tick["ok"] is True
            assert tick.get("receipt_hash72")
            assert tick.get("runtime_state_hash72")
        finally:
            await canonical.shutdown_sequence()

    asyncio.run(verify())


def test_procfile_boots_canonical_production_server():
    procfile = Path("Procfile").read_text(encoding="utf-8")
    assert "hhs_backend.production_server:app" in procfile
    assert "hhs_backend.heroku_server:app" not in procfile


def test_post_compile_refuses_assistant_offline_deployment():
    source = Path("bin/post_compile").read_text(encoding="utf-8")
    assert "--require-assistant" in source
    assert "HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC" in source
    assert "make c-abi" in source


def test_frontend_entrypoint_uses_integrated_client_not_legacy_desktop_runtime():
    source = Path("hhs_gui/main.tsx").read_text(encoding="utf-8")
    assert "CanonicalRuntimeIDE" in source
    assert "IntegratedRuntimeClient" in source
    assert "__HHS_RUNTIME_CLIENT__" in source
    assert 'from "./runtime_os/core/RuntimeOS"' not in source
    assert "ProductionApp" not in source
    assert "global.css" in source


def test_runtime_transport_is_deferred_but_authority_is_verified_independently():
    client = Path("hhs_gui/runtime_os/core/IntegratedRuntimeClient.ts").read_text(
        encoding="utf-8"
    )
    canonical = Path("hhs_gui/runtime_os/core/CanonicalRuntimeIDE.tsx").read_text(
        encoding="utf-8"
    )
    projection = Path(
        "hhs_gui/runtime_os/core/LiveRuntimeProjectionPanel.tsx"
    ).read_text(encoding="utf-8")
    product = Path(
        "hhs_gui/runtime_os/workspace/HHSProductWorkspace.tsx"
    ).read_text(encoding="utf-8")

    assert "RuntimeApplicationRegistry" not in client
    assert "RuntimeWindowManager" not in client
    assert "runtimeClient.shutdown" in canonical
    assert "runtimeOS.initialize()" in projection
    assert "runtimeOS.shutdown()" in projection
    assert "/api/runtime/authority/status" in projection
    assert "WebSockets are on-demand projection channels" in projection
    assert "/api/product/health" in product
    assert "runtimeOnline" in product
    assert "assistantOnline" in product


def test_canonical_workspace_is_one_shared_transaction_surface():
    source = Path("hhs_gui/runtime_os/workspace/HHSWorkspaceShell.tsx").read_text(
        encoding="utf-8"
    )

    for token in [
        "projectId",
        "selectedObjectId",
        "artifactId",
        "sessionId",
        "ensureProject",
        "ensureSource",
        "applyFeedback",
        'tab === "workbench"',
        'tab === "assistant"',
        'tab === "runtime"',
        'tab === "receipts"',
        "project.create",
        "ingress.register",
        "interpret.execute",
        "compile.execute",
        "emulator.create",
        "emulator.step",
        "Only operations that actually returned from the backend appear here",
    ]:
        assert token in source

    for token in [
        "RuntimeProjectTree",
        "MultimodalIngressPanel",
        "LiveBackendCapabilityPanel",
        "HHSSymbolicEditor",
        "InterpreterConsole",
        "CompilerWorkbench",
        "EmulatorControlPanel",
        "RuntimeGraphCanvas",
        "SemanticMemoryPanel",
        "ReceiptLedgerInspector",
        "MutationHistoryPanel",
        "RuntimeCommandPanel",
        "RuntimeMutationPanel",
        "runtime_application_missing",
    ]:
        assert token not in source


def test_public_html_keeps_boot_failure_visible():
    source = Path("hhs_gui/index.html").read_text(encoding="utf-8")
    assert "HHS Visual Runtime OS Workspace" in source
    assert "frontend_boot_timeout" in source
    assert "dataset.hhsMounted" in source
    assert "overlay.remove()" not in source


def test_assistant_is_bound_to_workspace_without_suggestion_autosubmit():
    source = Path(
        "hhs_gui/runtime_os/assistant/RuntimeAssistantPanel.tsx"
    ).read_text(encoding="utf-8")
    assert 'requestJson("/api/assistant/health")' in source
    assert 'requestJson("/api/assistant/chat"' in source
    assert "workspace_surface" in source
    assert "source_object_id" in source
    assert "artifact_id" in source
    assert "No response or runtime mutation was fabricated" in source
    assert "Suggestion" not in source
    assert 'setInput("Explain' not in source


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
