from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUI = ROOT / "hhs_gui" / "runtime_os"


def read(path: str) -> str:
    return (GUI / path).read_text(encoding="utf-8")


def test_document_gui_surfaces_are_mounted_and_projection_only():
    shell = read("workspace/HHSWorkspaceShell.tsx")
    components = [
        "DocumentPerceptionPanel", "DocumentSourceInspector", "PageLayoutViewer",
        "OCRProjectionViewer", "DocumentFusionViewer", "TableProjectionViewer",
        "DocumentGraphViewer", "DocumentAmbiguityInspector", "DocumentReconstructionViewer",
    ]
    for component in components:
        assert component in shell
    haystack = "\n".join([
        read("document/DocumentPerceptionPanel.tsx"),
        read("document/DocumentSourceInspector.tsx"),
        read("document/PageLayoutViewer.tsx"),
        read("document/OCRProjectionViewer.tsx"),
        read("document/DocumentFusionViewer.tsx"),
        read("document/TableProjectionViewer.tsx"),
        read("document/DocumentGraphViewer.tsx"),
        read("document/DocumentAmbiguityInspector.tsx"),
        read("document/DocumentReconstructionViewer.tsx"),
    ])
    for token in [
        "PDF parser output ≠ PDF",
        "REJECT_OCR_TEXT_AS_DOCUMENT_SOURCE",
        "OCR text ≠ page image",
        "REJECT_PROVIDER_DISAGREEMENT_COLLAPSED_SILENTLY",
        "DOCUMENT_GRAPH_PROJECTION",
        "REJECT_DOCUMENT_PROJECTION_WITHOUT_RECONSTRUCTION",
    ]:
        assert token in haystack


def test_gui_source_verifier_includes_document_perception():
    verifier = (ROOT / "hhs_gui" / "scripts" / "live-gui-e2e-source-verify.mjs").read_text(encoding="utf-8")
    assert "deep-document-perception-source-verify" in verifier
    assert "DocumentReconstructionViewer" in verifier
