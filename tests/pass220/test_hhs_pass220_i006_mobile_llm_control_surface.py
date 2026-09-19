from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MOBILE = ROOT / "hhs_gui/runtime_os/workspace/ProductionMobileControlCenter.tsx"
ASSISTANT = ROOT / "hhs_gui/runtime_os/workspace/ProductionAssistantChat.tsx"
PRODUCT = ROOT / "hhs_gui/runtime_os/workspace/HHSProductWorkspace.tsx"
VERIFY = ROOT / "hhs_gui/scripts/workspace-source-verify.mjs"
DEPLOY = ROOT / ".github/workflows/digitalocean-production-main.yml"


def _text(path: Path) -> str:
    return path.read_text("utf-8")


def test_mobile_control_mounts_llm_assistant_and_user_controlled_multimodal_ingress():
    mobile = _text(MOBILE)
    assert 'import ProductionAssistantChat from "./ProductionAssistantChat"' in mobile
    assert "<ProductionAssistantChat" in mobile
    assert "onOpenFiles={() => fileInput.current?.click()}" in mobile

    for token in (
        "/api/v1/pass174/sdlc/run",
        "/api/v1/pass174/hash216/query",
        'type="file"',
        "multiple",
        "Hydrate vector store",
        "Files → multimodal ingress → vector store",
        "PDF",
        "IMAGE",
        "AUDIO",
        "VIDEO",
        "CODE",
        "TEXT",
        "BINARY",
    ):
        assert token in mobile


def test_mobile_assistant_has_normal_llm_chat_shape_and_dark_mobile_surface():
    assistant = _text(ASSISTANT)

    for token in (
        "/api/assistant/health",
        "/api/assistant/chat",
        "New chat",
        "Message HHS",
        "How can I help?",
        "Generating response",
        "Enter sends",
        "Shift+Enter",
        "min-h-[42vh]",
        "bg-neutral-900/70",
        "rounded-3xl",
    ):
        assert token in assistant

    assert "vector_payload_auto_attached_to_prompt: false" in assistant
    assert "uploaded payloads are not automatically attached to assistant prompts" in assistant
    assert 'project_id: projectId || "project:production-mobile-control"' in assistant
    assert "thread_id: threadId" in assistant
    assert "setThreadId(nextThreadId)" in assistant


def test_vector_ingress_and_chat_are_separate_user_actions():
    assistant = _text(ASSISTANT)
    mobile = _text(MOBILE)

    assert "onOpenFiles" in assistant
    assert "onClick={onOpenFiles}" in assistant
    assert "fileInput.current?.click()" in mobile
    assert "void ingest()" in mobile

    # The assistant must not post file bytes or the Pass 174 ingress payload.
    assert "/api/v1/pass174/sdlc/run" not in assistant
    assert "source_b64" not in assistant
    assert "bytesToBase64" not in assistant


def test_canonical_product_defaults_to_mobile_control_surface():
    product = _text(PRODUCT)
    assert 'useState<ProductSurface>("control")' in product
    assert "ProductionMobileControlCenter" in product
    assert 'surface === "control"' in product


def test_workspace_source_verifier_enforces_i006_surface():
    verifier = _text(VERIFY)
    for token in (
        "ProductionMobileControlCenter.tsx",
        "ProductionAssistantChat.tsx",
        "/api/assistant/chat",
        "/api/v1/pass174/sdlc/run",
        "uploaded payloads are not automatically attached to assistant prompts",
        "mobile LLM assistant surface missing",
    ):
        assert token in verifier


def test_digitalocean_exact_main_workflow_is_the_deployment_boundary():
    deploy = _text(DEPLOY)
    assert "main" in deploy
    assert "HHS_PRODUCTION_HOST" in deploy
    assert "HHS_DIGITALOCEAN_SSH_PRIVATE_KEY" in deploy
    assert "hhs-runtime-os" in deploy
