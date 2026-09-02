from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_physics_studio_is_served_product_surface():
    assert (ROOT/"applications/holofractal_harmonizer/src/physics-studio/index.html").is_file()
    html=(ROOT/"applications/holofractal_harmonizer/src/physics-studio/index.html").read_text()
    js=(ROOT/"applications/holofractal_harmonizer/src/physics-studio/app.js").read_text()
    assert "Relativistic Quantum Simulation Studio" in html
    assert "/api/runtime/pass178-physics" in js
    assert "projection-only" in html
