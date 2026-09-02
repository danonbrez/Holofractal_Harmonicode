from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_graphics_studio_is_editable_served_surface():
    index = ROOT / "applications/holofractal_harmonizer/src/graphics-studio/index.html"
    app = ROOT / "applications/holofractal_harmonizer/src/graphics-studio/app.js"
    visual = (ROOT / "hhs_backend/visual_server.py").read_text("utf-8")
    assert index.is_file() and app.is_file()
    html = index.read_text("utf-8")
    js = app.read_text("utf-8")
    assert "Pass 179 Native Graphics Studio" in html
    assert "/api/runtime/pass179-graphics" in js
    assert 'app.mount("/graphics-studio"' in visual
    assert 'app.include_router(pass179_graphics_router)' in visual


def test_graphics_studio_does_not_claim_browser_authority():
    html = (ROOT / "applications/holofractal_harmonizer/src/graphics-studio/index.html").read_text("utf-8")
    assert "projection-only" in html
    assert "cannot mutate canonical scene state" in html
