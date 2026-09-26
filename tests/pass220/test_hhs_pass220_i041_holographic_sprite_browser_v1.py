from pathlib import Path


HTML = Path(
    "applications/holofractal_harmonizer/"
    "lane5_holographic_sprite_5184.html"
)


def test_lane5_browser_projection_is_single_5184_graph_with_two_projection_passes():
    source = HTML.read_text(encoding="utf-8")
    assert "const NODE_COUNT = 5184;" in source
    assert "const HASH72_SIDE = 72;" in source
    assert "72^72" in source
    assert "new THREE.Points(geometry,material1)" in source
    assert "new THREE.Points(geometry,material2)" in source
    assert "new THREE.ShaderMaterial" in source


def test_lane5_browser_path_matches_native_seeded_affine_cycle_contract():
    source = HTML.read_text(encoding="utf-8")
    for token in (
        'seedU64(seed,"PATH_START")',
        'seedU64(seed,"PATH_STRIDE")',
        "gcd(stride,NODE_COUNT)!==1",
        "path.start + path.stride*(rank%NODE_COUNT)",
        '"PATH72:"+rank+":"+address',
        'crypto.subtle.digest("SHA-256"',
    ):
        assert token in source, token


def test_lane5_browser_preserves_animation_projection_invariants_without_randomness():
    source = HTML.read_text(encoding="utf-8")
    assert "Math.random" not in source
    for token in (
        "const PHI = (1 + Math.sqrt(5)) / 2;",
        "const Q144_OCTANT = 18;",
        "const Q144_QUARTER = 36;",
        "const Q144_HALF = 72;",
        "const QUARTIC_RENDER_PERIOD = 4;",
        "aGroup*PI/4.0 + uLayer*PI/2.0",
        "p.xy=vec2(-p.y,p.x)",
        "float h2=h1/PHI",
        "renderFrame:(tick%QUARTIC_RENDER_PERIOD)===0",
        "authority=projection-only; no VM81/Hash72/Hash216 mutation",
    ):
        assert token in source, token


def test_lane5_browser_exposes_manual_animation_and_renderer_bypass_benchmark():
    source = HTML.read_text(encoding="utf-8")
    for token in (
        'window.HHS_LANE5_TEST={',
        'schema:"HHS_PASS_220_I041_HTML_TEST_API_V1"',
        'schema:"HHS_PASS_220_I041_HTML_RENDER_BOTTLENECK_BENCHMARK_V1"',
        'rendererRemovedControl:true',
        'dominantNonRenderComponent',
        'gl.finish()',
        'projectionTick(targetTick',
        'benchmark:runBottleneckBenchmark',
    ):
        assert token in source, token
