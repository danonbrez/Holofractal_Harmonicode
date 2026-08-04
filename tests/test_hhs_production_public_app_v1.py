from __future__ import annotations

import asyncio
import json
from pathlib import Path
import subprocess


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
    missing = sorted(required - paths)
    assert not missing, missing
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


def test_hosted_pass210_assistant_closes_without_kimi_or_gemma(monkeypatch, tmp_path):
    from hhs_backend import production_server
    from hhs_backend.runtime import hhs_pass210_production_assistant_v1 as production_module
    from hhs_backend.runtime.hhs_kimi_k3_agentic_assistant_v1 import (
        KimiConversationThreadStore,
        KimiK3AgenticAssistantService,
        KimiK3AssistantConfig,
    )
    from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import LiteRTLMConfig
    from hhs_backend.runtime.hhs_litert_lm_hhs_api_assistant_v1 import (
        HHSAPIAssistantService,
    )
    from hhs_backend.runtime.hhs_pass210_native_agi_optimizer_v1 import (
        NativeAGIOptimizer,
    )
    from hhs_backend.runtime.hhs_pass210_production_assistant_v1 import (
        Pass210ProductionAssistantService,
    )

    kimi_config = KimiK3AssistantConfig(
        enabled=False,
        api_key="",
        max_threads=8,
        max_messages_per_thread=32,
    )
    shared = KimiConversationThreadStore(
        kimi_config,
        provider_id="provider:hhs.pass210.production-test",
    )
    primary = KimiK3AgenticAssistantService(
        config=kimi_config,
        thread_store=shared,
    )
    fallback = HHSAPIAssistantService(
        config=LiteRTLMConfig(
            base_url="http://127.0.0.1:9/v1",
            model_id="gemma-4-E2B-it",
            timeout_seconds=0.1,
            max_threads=8,
            max_messages_per_thread=32,
        ),
        thread_store=shared,
    )
    optimizer = NativeAGIOptimizer(db_path=tmp_path / "optimizer.sqlite3")
    service = Pass210ProductionAssistantService(
        primary_service=primary,
        fallback_service=fallback,
        optimizer=optimizer,
    )
    service._health_timeout = 0.5
    monkeypatch.setattr(
        production_module,
        "DEFAULT_PASS210_PRODUCTION_ASSISTANT",
        service,
    )

    health = asyncio.run(production_server._assistant_health())
    assert health["ok"] is False, health
    assert health["online"] is False, health
    assert health["selected_provider_id"] is None, health
    assert health["effective_mode"] == "UNAVAILABLE", health
    assert health["native_agi_is_user_facing_provider"] is False
    assert health["native_agi_is_backend_learning_agent"] is True

    thread = service.create_thread(
        project_id="project:hosted-assistant-test",
        title="Hosted assistant fail-closed test",
    )
    turn = asyncio.run(service.send_message(thread["thread_id"], content="AB=P^4"))
    assert turn["ok"] is False, turn
    assert turn["status"] == "REJECT_ASSISTANT_TURN_WITHOUT_READY_PROVIDER"
    assert turn["effective_mode"] == "UNAVAILABLE"
    assert turn["selected_provider_id"] is None
    assert turn["assistant_message"] is None
    assert turn["native_agi_is_user_facing_provider"] is False
    assert turn["native_agi_observation_root_hash72"]
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


def test_procfile_boots_final_application_ide_over_pass174_overlay():
    procfile = Path("Procfile").read_text(encoding="utf-8")
    assert "hhs_backend.application_ide_server:app" in procfile
    assert "hhs_backend.heroku_server:app" not in procfile

    final_source = Path("hhs_backend/application_ide_server.py").read_text(encoding="utf-8")
    assert "pass174_server as pass174" in final_source
    assert '"/runtime-console"' in final_source
    assert "hhs-full-application-ide" in final_source
    assert "production.VISUAL_ROOT" in final_source

    overlay_source = Path("hhs_backend/pass174_server.py").read_text(encoding="utf-8")
    assert "production_ide_server as inherited_ide" in overlay_source
    assert "hhs-pass174-visual-ide" in overlay_source


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


def test_provider_hierarchy_uses_kimi_then_gemma_with_native_optimizer():
    paths = [
        "hhs_backend/runtime/hhs_kimi_k3_agentic_assistant_v1.py",
        "hhs_backend/runtime/hhs_pass210_production_assistant_v1.py",
        "hhs_backend/runtime/hhs_pass210_native_agi_optimizer_v1.py",
        "hhs_backend/runtime/hhs_capability_provider_registry_v1.py",
        "hhs_backend/runtime/hhs_litert_lm_assistant_v1.py",
    ]
    combined = "\n".join(Path(path).read_text(encoding="utf-8") for path in paths)
    assert "provider:hhs.moonshot.kimi_k3.agentic" in combined
    assert "provider:hhs.litert_lm.gemma4" in combined
    assert "provider:hhs.local.text" in combined
    assert "KIMI_K3_AGENTIC_SWARM_API" in combined
    assert "GEMMA4_LITERT_LM_FALLBACK" in combined
    assert "BACKEND_LEARNING_AND_OPTIMIZATION_AGENT" in combined
    assert "native_agi_is_user_facing_provider" in combined
    assert "HHS_NATIVE_LITERT_COMPATIBLE" not in combined
    assert "The request was received without runtime mutation" not in combined


def test_pass174_exact_legacy_foundation_and_persistent_retrieval(tmp_path):
    from hhs_runtime.pass174 import (
        Pass174Runtime,
        PersistentEncryptedVectorStore,
        build_legacy_manifest,
    )

    manifest = build_legacy_manifest(Path("."))
    assert manifest.maximum_inherited_pass == 173
    assert 173 in manifest.pass_numbers_present
    assert manifest.specification_count > 0
    assert all("evidence/" not in item.path for item in manifest.specifications)
