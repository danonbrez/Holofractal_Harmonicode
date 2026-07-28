from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VISUAL_ROOT = ROOT / "applications" / "holofractal_harmonizer"


def test_visual_server_composes_assistant_and_static_home() -> None:
    source = (ROOT / "hhs_backend" / "visual_server.py").read_text(encoding="utf-8")
    assert "litert_lm_assistant_routes" in source
    assert "app.include_router(assistant_router)" in source
    assert "StaticFiles" in source
    assert "hhs-visual-home" in source
    assert '"/api/system/status"' in source


def test_visual_home_defaults_to_litert_lm_assistant() -> None:
    html = (VISUAL_ROOT / "index.html").read_text(encoding="utf-8")
    assert "HHS LiteRT-LM Development Assistant" in html
    assert 'id="assistant-view"' in html
    assert 'id="conversation"' in html
    assert 'id="prompt-form"' in html
    assert 'id="workspace-view" hidden' in html
    assert "/api/assistant" not in html  # endpoint details remain in the controller, not inline markup


def test_browser_binds_governed_assistant_api_and_registered_objects() -> None:
    source = (VISUAL_ROOT / "src" / "browser.mjs").read_text(encoding="utf-8")
    assert "hhs:model:litert-lm:gemma4" in source
    assert "hhs:agent:visual-development-assistant" in source
    assert "hhs:api:assistant-chat" in source
    assert "'/api/assistant/status'" in source
    assert "'/api/assistant/health'" in source
    assert "'/api/assistant/tools'" in source
    assert "/api/assistant/threads/" in source
    assert "direct_vm81_mutation_allowed: false" in source
    assert "mutating_model_tool_execution_allowed: false" in source


def test_startup_installs_model_and_launches_visual_server_by_default() -> None:
    startup = (ROOT / "start.sh").read_text(encoding="utf-8")
    assert '${HHS_LITERT_LM_AUTO_BOOTSTRAP:-1}' in startup
    assert '${HHS_LITERT_LM_AUTO_IMPORT:-1}' in startup
    assert "hhs_backend.visual_server:app" in startup
    assert "hhs_backend.server:app" not in startup
