from __future__ import annotations

import asyncio
import json
from pathlib import Path


def route_paths(app) -> set[str]:
    return {str(getattr(route, "path", "")) for route in app.router.routes}


def test_production_server_composes_canonical_backend_and_verified_harmonizer():
    from hhs_backend import production_server

    app = production_server.app
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
        "/api/runtime/services",
        "/api/runtime/services/dispatch",
        "/api/runtime/installation/status",
        "/api/assistant/health",
        "/api/assistant/chat",
        "/v1/modalities/language/models/word2vec/status",
        "/ws/runtime",
    }
    assert required.issubset(paths)
    assert "" in paths or "/" in paths
    assert production_server.VISUAL_ROOT == Path("applications/holofractal_harmonizer").resolve()
    assert (production_server.VISUAL_ROOT / "index.html").is_file()
    assert any(
        getattr(route, "name", None) == "hhs-production-harmonizer"
        for route in app.router.routes
    )


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


def test_procfile_boots_integrated_production_server():
    procfile = Path("Procfile").read_text(encoding="utf-8")
    assert "hhs_backend.production_server:app" in procfile
    assert "hhs_backend.heroku_server:app" not in procfile


def test_post_compile_refuses_assistant_offline_deployment():
    source = Path("bin/post_compile").read_text(encoding="utf-8")
    assert "--require-assistant" in source
    assert "HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC" in source
    assert "make c-abi" in source


def test_pass161_terminal_browser_is_the_public_html_authority():
    terminal = json.loads(
        Path("applications/holofractal_harmonizer/HHS_PASS_161_TERMINAL_RELEASE.json")
        .read_text(encoding="utf-8")
    )
    receipt = json.loads(
        Path("applications/holofractal_harmonizer/evidence/pass161/P161_COMPLETION_RECEIPT.json")
        .read_text(encoding="utf-8")
    )
    html = Path("applications/holofractal_harmonizer/index.html").read_text(encoding="utf-8")

    assert terminal["omega_161"] is True
    assert terminal["terminal_claimed"] is True
    assert receipt["checks"]["browser_complete"] is True
    assert receipt["checks"]["native_bound"] is True
    assert 'id="registry-tree"' in html
    assert 'id="assistant-view"' in html
    assert 'id="api-view"' in html
    assert 'id="inspector"' in html
    assert html.index("src/browser.mjs") < html.index("src/ux-default.mjs")
    assert html.index("src/ux-default.mjs") < html.index("src/production-integration.mjs")
    assert "hhs_gui/dist" not in html


def test_usability_evidence_promotes_workflow_first_without_removing_objects():
    report = Path("HHS_VISUAL_IDE_PARALLEL_AB_USABILITY_REPORT.md").read_text(
        encoding="utf-8"
    )
    metrics = json.loads(
        Path("applications/holofractal_harmonizer/evidence/ux_ab_optimization_v1/metrics.json")
        .read_text(encoding="utf-8")
    )
    ux_source = Path("applications/holofractal_harmonizer/src/ux-default.mjs").read_text(
        encoding="utf-8"
    )

    assert "WORKFLOW_FIRST_PROGRESSIVE_DISCLOSURE" in report
    assert "The enhancement does not replace `browser.mjs`, `core.mjs`, the object registry" in report
    assert metrics["recommended_default"] == "WORKFLOW_FIRST_PROGRESSIVE_DISCLOSURE"
    assert metrics["summary"]["relative_change_B_vs_A"] == {
        "actions_percent": -50.0,
        "context_switches_percent": -75.0,
        "completion_time_percent": -39.0,
    }
    assert "Advanced Object Controls" in ux_source
    assert "window.HHSHarmonizer" in ux_source
    assert "workflow-mobile-tabs" in ux_source


def test_verified_harmonizer_hydrates_live_backend_registry_and_dispatch():
    source = Path(
        "applications/holofractal_harmonizer/src/production-integration.mjs"
    ).read_text(encoding="utf-8")

    for endpoint in [
        "/api/runtime/authority/status",
        "/api/runtime/services",
        "/api/runtime/services/dispatch",
        "/api/runtime/workspace/session",
        "/api/runtime/installation/status",
    ]:
        assert endpoint in source

    for token in [
        "runtime.registry.register",
        "runtime.registry.relate",
        "serviceDescriptors",
        "serviceObjectIds",
        "schemaDefaults",
        "Execute registered service",
        "BACKEND RESULT RETURNED",
        "extractReceiptHash",
        "frontend_result_fabricated: false",
        "RUNTIME AUTHORITY · WARMING",
        "frontend_is_authority: false",
    ]:
        assert token in source

    assert "new HarmonizerRuntime" not in source
    assert "new WebSocket" not in source
    assert "simulated_raw_result" not in source
    assert "disabled registry item" not in source


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
