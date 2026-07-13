from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_multimodal_ingress_gui_source_declares_source_preservation():
    text = (ROOT / "hhs_gui/runtime_os/workspace/MultimodalIngressPanel.tsx").read_text(encoding="utf-8")
    assert "multimodal-ingress-panel" in text
    assert "Original source is preserved" in text
    assert "ingress.register" in text
