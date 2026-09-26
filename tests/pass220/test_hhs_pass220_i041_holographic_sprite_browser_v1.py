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



def test_canonical_seed_contract_repairs_are_explicit_and_fail_closed():
    source = HTML.read_text(encoding="utf-8")
    for token in (
        'const CANONICAL_SEED_TITLE = "Holofractal Hybrid QPU & Neural Swarm — HHS VM81 / I041";',
        "function q23DivExact(x,y)",
        "num.map(c=>brDiv(c,n))",
        "function vm81ClosureGateBrowser(P,p,q,n,x,y)",
        'reason:"MISSING_OR_NONINTEGER_CELL_COORDINATE"',
        "passes:lhs===n4&&n4===xy",
        "function hnanGate10(lhs,rhs)",
        'denominator:"EmptySet"',
        "host_scalar_division_authorized:false",
        "function cycle9CoordinateReceipt(n)",
        "z72_projection_authorized:false",
        'schema:"HHS_I041_CANONICAL_SEED_MATH_REPAIR_RECEIPT_V1"',
    ):
        assert token in source, token
    assert "num[0]/N" not in source
    assert "num[1]/N" not in source


def test_holographic_pixel_sprite_compositor_preserves_source_resolution_and_transparency():
    source = HTML.read_text(encoding="utf-8")
    for token in (
        "const VIRTUAL_FRAME_PIXELS = NODE_COUNT * NODE_COUNT;",
        "new THREE.WebGLRenderTarget",
        "minFilter:THREE.NearestFilter",
        "magFilter:THREE.NearestFilter",
        "function renderProjectionFrame()",
        "renderer.setClearColor(0x000000,0)",
        "scene.background=null;",
        'uniform float uNucleusGain;',
        'uniform float uHaloRadiusPx;',
        'uniform float uHaloGain;',
        "vec3 composite=clamp(center.rgb+nucleusExtra+haloRgb,0.0,1.0);",
        "float compositeAlpha=max(center.a,haloAlpha);",
        "sourcePixelIsDenseNucleus:true",
        "haloMayOverlapAdjacentPixelCells:true",
        "haloBackgroundAlphaZero:true",
        "drivingPixelRemainsBehindHalo:true",
        "sameResolution:",
    ):
        assert token in source, token
