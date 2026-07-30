from pathlib import Path

from fastapi import HTTPException

from hhs_backend.api.repository_history_routes import _catalog, repository_text_file

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_pass_catalog_projects_repository_visible_contract_history() -> None:
    catalog = _catalog()
    assert catalog["ok"] is True
    assert catalog["pass_count"] >= 50
    assert catalog["earliest_pass"] is not None
    assert catalog["latest_pass"] >= 174
    assert any(item["pass_number"] == 174 for item in catalog["passes"])
    assert any(
        file["kind"] == "CONTRACT"
        for item in catalog["passes"]
        for file in item["files"]
    )


def test_repository_text_reader_is_bounded_and_rejects_path_escape() -> None:
    payload = repository_text_file("HHS_PASS_174_HARMONIC_PHASE_GEAR_HASH216_VM81_VISUAL_IDE_MULTIMODAL_SDLC_RUNTIME.md")
    assert payload["ok"] is True
    assert payload["read_only"] is True
    assert "PASS 174" in payload["content"].upper()
    try:
        repository_text_file("../../etc/passwd")
    except HTTPException as exc:
        assert exc.status_code == 403
    else:
        raise AssertionError("repository path traversal was not rejected")


def test_hosted_entrypoint_orders_repository_routes_before_api_fallback() -> None:
    source = read("hhs_backend/production_ide_server.py")
    assert "repository_history_router" in source
    assert '"/api/runtime/repository"' in source
    assert '"/api/{unmatched_path:path}"' in source
    assert source.index("app.include_router(repository_history_router)") < source.index("app.mount(")
    assert "repository_routes" in source


def test_main_surface_is_ide_not_history_landing_page() -> None:
    source = read("applications/holofractal_harmonizer/src/integrated-workbench.mjs")
    visual_ide = read("applications/holofractal_harmonizer/src/visual-ide.mjs")
    assert "ide-file-tree" not in source  # existing file tree is preserved, not replaced
    assert "initIntegratedWorkbench" in visual_ide
    assert "ide-application-frame" in source
    assert "sandbox = 'allow-scripts allow-forms allow-modals allow-downloads'" in source
    assert "PASS CONSTRAINTS + HISTORY" in source
    assert "The editor remains the primary product surface" in source
