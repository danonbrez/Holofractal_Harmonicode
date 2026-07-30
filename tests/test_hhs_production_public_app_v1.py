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


def test_procfile_boots_pass174_overlay_over_integrated_production_server():
    procfile = Path("Procfile").read_text(encoding="utf-8")
    assert "hhs_backend.pass174_server:app" in procfile
    assert "hhs_backend.heroku_server:app" not in procfile
    server_source = Path("hhs_backend/pass174_server.py").read_text(encoding="utf-8")
    assert "production_ide_server as inherited_ide" in server_source
    assert '"/legacy-ide"' in server_source
    assert "hhs-pass174-visual-ide" in server_source


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
    assert all("tests/" not in item.path for item in manifest.specifications)

    database = tmp_path / "pass174" / "vectors.sqlite3"
    key_path = tmp_path / "pass174" / "vectors.key"
    producer_store = PersistentEncryptedVectorStore(database, key_path=key_path)
    producer = Pass174Runtime(legacy_manifest=manifest, vector_store=producer_store)
    direct = producer.execute(thread=4, writes={0: 1, 8: 1, 72: 1, 80: -1})
    expected_frame = producer.vmrc.snapshot().to_bytes()
    expected_hash72 = producer.vmrc.state_hash72
    assert direct["path"] == "DIRECT_RUNTIME"
    assert direct["object"]["plaintext_exposed"] is False
    assert len(direct["object"]["hash216"]["combined"]) == 216
    assert len(direct["object"]["hash216"]["character_indexes_sha256"]) == 216
    assert producer_store.storage_status()["plaintext_persisted"] is False
    producer_store.close()

    consumer_store = PersistentEncryptedVectorStore(database, key_path=key_path)
    consumer = Pass174Runtime(legacy_manifest=manifest, vector_store=consumer_store)
    retrieved = consumer.execute(
        thread=4,
        writes={0: 1, 8: 1, 72: 1, 80: -1},
        prefer_retrieval=True,
    )
    assert retrieved["path"] == "RETRIEVAL"
    assert consumer.vmrc.snapshot().to_bytes() == expected_frame
    assert consumer.vmrc.state_hash72 == expected_hash72
    audit = consumer.audit(challenge="production-test-post-seal", deep=True)
    assert audit["classification"] == "HHS_PASS_174_AUDIT_PASS"
    replay = consumer.replay()
    assert replay["classification"] == "HHS_PASS_174_REPLAY_CLOSED"
    assert replay["receipt_chain_valid"] is True
    consumer_store.close()


def test_pass174_public_overlay_routes_http_websocket_and_visual_roots(tmp_path, monkeypatch):
    monkeypatch.setenv("HHS_PASS174_STATE_DIR", str(tmp_path / "api-state"))

    from fastapi.testclient import TestClient
    from hhs_backend import pass174_server

    paths = route_paths(pass174_server.app)
    required = {
        "/api/v1/pass174/status",
        "/api/v1/pass174/frame",
        "/api/v1/pass174/phase",
        "/api/v1/pass174/execute",
        "/api/v1/pass174/audit",
        "/api/v1/pass174/replay",
        "/api/v1/pass174/legacy-foundation",
        "/api/v1/pass174/sdlc/run",
        "/api/v1/pass174/ws/events",
        "/api/v1/pass174/deployment/status",
        "/legacy-ide",
        "",
    }
    assert required.issubset(paths)

    with TestClient(pass174_server.app) as client:
        deployment = client.get("/api/v1/pass174/deployment/status")
        assert deployment.status_code == 200
        assert deployment.json()["ready"] is True
        assert deployment.json()["silent_freeze"] is False

        status = client.get("/api/v1/pass174/status")
        assert status.status_code == 200
        body = status.json()
        assert body["frame_bits"] == 5184
        assert body["kernel_authorities"] == 1
        assert body["legacy_foundation"]["maximum_inherited_pass"] == 173
        assert body["persistent_vector_store"]["plaintext_persisted"] is False

        frame = client.get("/api/v1/pass174/frame")
        assert frame.status_code == 200
        assert frame.json()["frame_bytes"] == 648
        assert len(frame.json()["snapshot_b64"]) == 864

        direct = client.post(
            "/api/v1/pass174/execute",
            json={"thread": 0, "writes": {"0": 1, "8": 1, "72": 1}, "prefer_retrieval": True},
        )
        assert direct.status_code == 200, direct.text
        assert direct.json()["path"] == "DIRECT_RUNTIME"

        visual = client.get("/")
        assert visual.status_code == 200
        assert "Pass 174 Harmonic Visual SDLC Runtime" in visual.text
        legacy = client.get("/legacy-ide/")
        assert legacy.status_code == 200
        assert "Holofractal" in legacy.text

        with client.websocket_connect("/api/v1/pass174/ws/events") as websocket:
            event = websocket.receive_json()
            assert event["classification"] == "HHS_PASS_174_LIVE_PROJECTION"
            assert event["mutation_authority"] is False
