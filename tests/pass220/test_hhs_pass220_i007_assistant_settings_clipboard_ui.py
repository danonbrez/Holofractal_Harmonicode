from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ASSISTANT = ROOT / "hhs_gui/runtime_os/workspace/ProductionAssistantChat.tsx"
CONTROL = ROOT / "hhs_gui/runtime_os/workspace/ProductionMobileControlCenter.tsx"
VERIFY = ROOT / "hhs_gui/scripts/workspace-source-verify.mjs"
BASE_ASSISTANT = ROOT / "hhs_backend/runtime/hhs_litert_lm_assistant_v1.py"
HHS_API_ASSISTANT = ROOT / "hhs_backend/runtime/hhs_litert_lm_hhs_api_assistant_v1.py"
ROUTES = ROOT / "hhs_backend/api/litert_lm_assistant_routes.py"


def _text(path: Path) -> str:
    return path.read_text("utf-8")


def test_settings_expose_persistent_custom_system_instruction():
    source = _text(ASSISTANT)

    for token in (
        "Settings",
        "Assistant settings",
        "System instructions",
        "assistant-system-instructions",
        "hhs.production.assistant.custom_system_instruction",
        "localStorage.getItem",
        "localStorage.setItem",
        "MAX_SYSTEM_INSTRUCTION_CHARS = 8192",
        "custom_system_instruction: instruction || null",
    ):
        assert token in source

    assert "vector_payload_auto_attached_to_prompt: false" in source
    assert "custom_system_instruction_present: Boolean(instruction)" in source


def test_mobile_copy_and_paste_controls_are_explicit_touch_actions():
    source = _text(ASSISTANT)

    for token in (
        "navigator.clipboard?.writeText",
        "navigator.clipboard?.readText",
        'document.execCommand("copy")',
        ">Copy<",
        ">Paste<",
        "min-h-10",
    ):
        assert token in source

    assert "onClick={() => void copyText(message.content, index)}" in source
    assert "onClick={() => void pasteClipboard()}" in source


def test_primary_assistant_renders_conversation_not_raw_turn_json():
    source = _text(ASSISTANT)

    assert "record(turn.assistant_message).content" in source
    assert "JSON.stringify(turn" not in source
    assert "JSON.stringify(messages" not in source
    assert "Ask naturally" in source


def test_vector_raw_json_is_hidden_until_explicit_inspection():
    source = _text(CONTROL)

    inspect_at = source.index("Inspect technical JSON")
    raw_at = source.index("JSON.stringify(vectorQuery")
    assert inspect_at < raw_at

    vector_block_start = source.rfind("Persisted vector retrieved", 0, raw_at)
    vector_block = source[vector_block_start: raw_at + 80]
    assert "<details className=" in vector_block
    assert "<details open" not in vector_block
    assert "Technical fields stay hidden unless you choose to inspect them." in vector_block


def test_provider_default_is_conversational_and_json_summary_first():
    base = _text(BASE_ASSISTANT)
    governed = _text(HHS_API_ASSISTANT)

    assert "Return clear conversational" in base
    assert "instead of dumping raw JSON unless the user explicitly asks to inspect it" in base
    assert "Answer the user conversationally in natural language" in governed
    assert "summarize tool evidence instead of exposing raw JSON" in governed


def test_assistant_api_exposes_bounded_custom_system_instruction():
    routes = _text(ROUTES)

    assert "custom_system_instruction: Optional[str] = Field(default=None, max_length=8192)" in routes
    assert "custom_system_instruction=request.custom_system_instruction" in routes
    assert 'request.get("custom_system_instruction")' in routes


def test_workspace_source_verifier_enforces_i007_product_contract():
    verifier = _text(VERIFY)

    for token in (
        "System instructions",
        "custom_system_instruction",
        "navigator.clipboard?.writeText",
        "navigator.clipboard?.readText",
        "Inspect technical JSON",
    ):
        assert token in verifier
