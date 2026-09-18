from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ASSISTANT = ROOT / "hhs_gui/runtime_os/workspace/ProductionAssistantChat.tsx"
VERIFY = ROOT / "hhs_gui/scripts/workspace-source-verify.mjs"
ROUTES = ROOT / "hhs_backend/api/litert_lm_assistant_routes.py"
PRODUCTION = ROOT / "hhs_backend/runtime/hhs_production_assistant_v1.py"
NATIVE = ROOT / "hhs_backend/runtime/hhs_native_litert_lm_provider_v1.py"


def _text(path: Path) -> str:
    return path.read_text("utf-8")


def test_mobile_settings_expose_three_assistant_modes_and_persist_choice():
    source = _text(ASSISTANT)

    for token in (
        'type AssistantMode = "GENERAL_CHAT" | "AGENTIC_APPLICATION_DEVELOPMENT" | "BOTH"',
        'hhs.production.assistant.mode',
        'data-testid="assistant-mode"',
        '<option value="GENERAL_CHAT">General chat</option>',
        '<option value="AGENTIC_APPLICATION_DEVELOPMENT">Agentic application development</option>',
        '<option value="BOTH">Both</option>',
        'window.localStorage.setItem(ASSISTANT_MODE_STORAGE_KEY, value)',
        'assistant_mode: assistantMode',
    ):
        assert token in source


def test_both_is_compatibility_default_and_mode_is_visible_in_chat():
    source = _text(ASSISTANT)

    assert 'return "BOTH"' in source
    assert "{modeLabel(assistantMode)}" in source
    assert 'thread={threadId ? short(threadId) : "new"} · {modeLabel(assistantMode)}' in source
    assert "General chat keeps developer tools off." in source
    assert "Both switches naturally between conversation and development." in source


def test_api_route_carries_assistant_mode_for_rest_and_websocket():
    source = _text(ROUTES)

    assert 'assistant_mode: str = Field(default="BOTH"' in source
    assert "assistant_mode=request.assistant_mode" in source
    assert 'assistant_mode=request.get("assistant_mode", "BOTH")' in source


def test_native_provider_has_general_prompt_response_and_mixed_intent_routing():
    source = _text(NATIVE)

    for token in (
        "ASSISTANT_MODE_GENERAL_CHAT",
        "ASSISTANT_MODE_AGENTIC_APPLICATION_DEVELOPMENT",
        "ASSISTANT_MODE_BOTH",
        "_assistant_mode_from_messages",
        "_looks_like_development_request",
        "general_chat_prompt_response_cycle",
        "Hello. What would you like to talk about?",
        "does not appear to be an application-development task",
    ):
        assert token in source

    # This old behavior forced repository retrieval for every ordinary prompt.
    assert 'if not selections and not _looks_like_harmonicode_expression(query):' not in source


def test_production_native_instruction_supports_conversation_and_development():
    source = _text(PRODUCTION)

    assert "Support ordinary" in source
    assert "conversational prompt-response generation" in source
    assert "governed application" in source
    assert "assistant_modes" in source
    assert "default_assistant_mode" in source


def test_workspace_verifier_guards_all_three_modes():
    verifier = _text(VERIFY)

    for token in (
        "Assistant mode",
        "GENERAL_CHAT",
        "AGENTIC_APPLICATION_DEVELOPMENT",
        "BOTH",
        "hhs.production.assistant.mode",
        "assistant_mode: assistantMode",
    ):
        assert token in verifier
