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
    assert "new HHS3D.Points(geometry,material1)" in source
    assert "new HHS3D.Points(geometry,material2)" in source
    assert "new HHS3D.ShaderMaterial" in source


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


def test_lane5_browser_self_hosts_exact_whitepaper_algebra_and_scheduler():
    source = HTML.read_text(encoding="utf-8")
    for token in (
        'schema:"HHS_I041_SELF_HOSTED_EXACT_MANIFOLD_V1"',
        '"whitepapers/HOLOFRACTAL_HARMONICODE.md"',
        '"docs/whitepapers/HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md"',
        '"docs/whitepapers/HHS_UNIFIED_TECHNICAL_WHITE_PAPER_LANE5_1_48_V1.md"',
        'cardinality:"144*36 = 12*12*3*12 = 81*64 = 72*72 = 5184"',
        'action:"Rot_72(k): j -> (j+k) mod 72"',
        'closure:"Rot_72(72) = identity"',
        'field:"Q(zeta_144)"',
        'optimizerMemory:"O(1)"',
        'canonicalFloatAuthority:false',
        'renderFloatProjectionOnly:true',
        "function projectionFloatRational(a)",
        "function q144RotationExact(k)",
        "function lane5ExactSchedule(targetTick)",
        "timeSeconds:brat(t,60n)",
        "function exactRatioFromText(value)",
        "function brFloor(a)",
        "simulationSpeedExact=null",
        "simulationTickExact=null",
        "canonicalResultChanged:false",
        'canonicalArithmetic:"BIGINT_RATIONAL_SYMBOLIC_Q144_TENSOR"',
        "selfHostedExactContract(){return SELF_HOSTED_HHS_EXACT;}",
    ):
        assert token in source, token
    assert "const seconds=tick/60;" not in source


def test_lane5_browser_preserves_animation_projection_invariants_without_randomness():
    source = HTML.read_text(encoding="utf-8")
    assert "Math.random" not in source
    for token in (
        'const PHI_EXACT = Object.freeze({',
        "const PHI_RENDER = (1 + Math.sqrt(5)) / 2;",
        "const Q144_OCTANT = 18;",
        "const Q144_QUARTER = 36;",
        "const Q144_HALF = 72;",
        "const QUARTIC_RENDER_PERIOD = 4;",
        "aGroup*PI/4.0 + uLayer*PI/2.0",
        "p.xy=vec2(-p.y,p.x)",
        "float h2=h1/PHI",
        "renderFrame:(next%QUARTIC_RENDER_PERIOD)===0",
        "authority=projection-only; no VM81/Hash72/Hash216 mutation",
    ):
        assert token in source, token


def test_lane5_browser_uses_exact_spherical_inspection_clock_and_hidden_guides():
    source = HTML.read_text(encoding="utf-8")
    for token in (
        "const SPACETIME_RADIUS = 90;",
        'enforcement:"shader-radius-clamp"',
        "uSpacetimeRadius:{value:SPACETIME_RADIUS}",
        "if(radius>uSpacetimeRadius){ p*=uSpacetimeRadius/max(radius,0.000001); }",
        "tesseractPhaseDriven:true",
        "tesseractVisibleGuide:false",
        "cameraWarpFromTesseract:false",
        "sphericalWireframeVisible:false",
        'id="simulationSpeed"',
        'id="stepOnce"',
        "simulationTickExact=brAdd(simulationTickExact,brMul(wallTickDelta,simulationSpeedExact));",
        "const wallTickDelta=brat(deltaMicros*60n,1000000n);",
        "renderFrame:(next%QUARTIC_RENDER_PERIOD)===0",
        "controls.enablePan=false",
    ):
        assert token in source, token

    assert "simTimeTicks+=dt*60.0*simulationSpeed" not in source
    assert "float persp=2.6/(2.2-w1);" not in source
    assert "p=vec3(x1,y1,z1)*persp;" not in source
    assert "new HHS3D.SphereGeometry" not in source
    assert "wireframe:true" not in source


def test_lane5_browser_restores_exact_orbital_phase_parameters_and_hide_toggles():
    source = HTML.read_text(encoding="utf-8")
    for token in (
        'id="toggleHudPanel"',
        'id="toggleCtlPanel"',
        'id="orbitRadius"',
        'id="orbitRate"',
        'id="orbitSlowRate"',
        'id="tesseractRate"',
        'id="q144PhaseRate"',
        'orbitRadius:"6"',
        'orbitRate:"1/2"',
        'orbitSlowRate:"1/200"',
        'tesseractRate:"1/5"',
        'q144PhaseRate:"1/50"',
        "p += vec3(sin(orbitT+shift)*uOrbitRadius",
        "cos(uTime*uOrbitSlowRate+shift)*uOrbitRadius",
        "sin(orbitT*PHI+shift)*uOrbitRadius",
        "installDynamicsControls();",
        "installPanelToggles();",
        'hud.classList.toggle("panelHidden")',
        'ctl.classList.toggle("panelHidden")',
        "function exactRatioFromText(value)",
        "dynamicsTuneExact[key]=brToString(ratio)",
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
        "new HHS3D.WebGLRenderTarget",
        "minFilter:HHS3D.NearestFilter",
        "magFilter:HHS3D.NearestFilter",
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




def test_holographic_animated_spritemap_requires_canonical_spherical_frame_binding():
    source = HTML.read_text(encoding="utf-8")
    for token in (
        'const I041_SPRITEMAP_BINDING = Object.freeze({',
        'addressTopologySeedBound:true',
        'canonicalAnimatedSeedBound:false',
        'currentTrajectoryAuthority:"NONE"',
        'currentMode:"PROJECTION_PIPELINE_PREVIEW"',
        'requiredCanonicalFrameSchema:"HHS_I041_CANONICAL_SPHERICAL_FRAME_V1"',
        'projection_preview_not_mislabeled_as_animated_seed:',
        'spritemapBinding:I041_SPRITEMAP_BINDING',
    ):
        assert token in source, token


def test_renderer_is_explicitly_fork_b_and_never_the_canonical_simulation_replacement():
    source = HTML.read_text(encoding="utf-8")
    for token in (
        'fork:"B"',
        'name:"MP4_RENDER_OBSERVATION_FORK"',
        'canonicalSimulationReplacement:false',
        'consumesCanonicalSimulationSemantics:true',
        'renderer_is_observation_fork:',
        'forkRole:I041_FORK_ROLE',
    ):
        assert token in source, token


def test_canonical_execution_contract_is_math_repair_only():
    source = HTML.read_text(encoding="utf-8")
    for token in (
        'const FOUNDATION_EXECUTION_CONTRACT = Object.freeze({',
        'repair mathematical/runtime faults in place',
        'lane5Rendering:"inherited Lane 5 optimization owns rendering/projection from the same canonical simulation state"',
        'simulationReductionAuthorized:false',
        'geometryMutationAuthorized:false',
        'physicsMutationAuthorized:false',
        'repairScope:"MATH_AND_RUNTIME_CORRECTION_ONLY"',
        'lane5RenderingInherited:true',
        'schema:"HHS_I041_FOUNDATION_PRESERVATION_RECEIPT_V1"',
        'foundationPreservationReceipt,',
    ):
        assert token in source, token
    assert "FOUNDATION_OPTIMIZATION_CONTRACT" not in source
    assert "phaseWordCache" not in source
    assert "modInverseCoprime" not in source






FOLLOW_SCENE = Path("apps/unified_gui/src/render/scene.js")
FOLLOW_BOOT = Path("apps/unified_gui/src/app/boot.js")


def test_particle_follow_is_passive_noninteractive_and_uses_native_curved_path():
    scene = FOLLOW_SCENE.read_text(encoding="utf-8")
    boot = FOLLOW_BOOT.read_text(encoding="utf-8")
    for token in (
        "followParticle(index)",
        "this.controls.enabled = false",
        "this.controls.enableRotate = false",
        "this.controls.enablePan = false",
        "this.controls.enableZoom = false",
        "const particle = this.engine.getParticle(this.followParticleIndex);",
        "const [vx, vy, vz] = particle.velocity;",
        ".addScaledVector(this._followTangent, -this.followDistance)",
        ".addScaledVector(this._followRadial, this.followHeight)",
        'physics_mutation: false',
        'trajectory_model: "NATIVE_CURVED_TOROIDAL_PATH"',
        'follow_physics_mutation: false',
    ):
        assert token in scene, token
    for token in (
        "followParticle: (index) => HHSApp.render.followParticle(index)",
        "clearParticleFollow: () => HHSApp.render.clearParticleFollow()",
        "focusParticle: (index) => HHSApp.render.followParticle(index)",
    ):
        assert token in boot, token


RAW_INGRESS = Path(
    "benchmarks/pass220/benchmark_i041_raw_html_lane5_ingress.py"
)


def test_raw_lane5_ingress_accepts_unaltered_html_and_quartic_capture():
    source = RAW_INGRESS.read_text(encoding="utf-8")
    for token in (
        'SCHEMA = "HHS_PASS_220_I041_RAW_HTML_LANE5_INGRESS_V1"',
        '"mode": "OPAQUE_UNALTERED_HTML"',
        '"source_unchanged": source_sha_before == source_sha_after',
        '"raf_step": args.raf_step',
        'parser.add_argument("--raf-step", type=int, default=4)',
        'parser.add_argument("--width", type=int, default=1920)',
        'parser.add_argument("--height", type=int, default=1080)',
        'page.on("pageerror"',
        '"console"',
        'console_errors.append(msg.text)',
    ):
        assert token in source, token



CONTRACT = Path(
    "contracts/pass220/"
    "PASS_220_I041_CANONICAL_HTML_SEED_HOLOGRAPHIC_PIXEL_SPRITE_V1.md"
)


def test_canonical_seed_contract_freezes_pixel_sprite_and_math_repair_boundaries():
    source = CONTRACT.read_text(encoding="utf-8")
    for token in (
        "Holofractal Hybrid QPU & Neural Swarm — HHS VM81 / I041",
        "Integer BigInt quotient truncation is forbidden.",
        "VM81 closure is six-cell and fail-closed",
        "It MUST NOT become a generic host division function.",
        "silently coerce this nonintegral coordinate into a Z/72 residue",
        "construction edges spend no capture budget",
        "source_frame_resolution == output_drawing_buffer_resolution",
        "5184 * 5184 = 26,873,856",
        "HHS_I041_CANONICAL_SEED_MATH_REPAIR_RECEIPT_V1 == PASS",
        "HHS_I041_FOUNDATION_PRESERVATION_RECEIPT_V1",
        "Canonical execution rule — math/runtime repair only",
        "Folded hyperspherical projection invariance",
        "Passive follow-particle observer",
        "execute all specified modules",
        "Lane 5 is the existing rendering optimization path",
        "Quartic closure and raw canonical-HTML ingress",
        "execute the complete canonical state update",
        "canonical HTML bytes (unchanged)",
        "source_bytes_before == source_bytes_after",
        "quartic_capture_step == 4 RAF ticks by default",
        "Realtime rendering and MP4 rendering are two observation modes",
        "HHS_I041_CANONICAL_SPHERICAL_FRAME_V1",
        "PROJECTION_PIPELINE_PREVIEW",
        "not yet the canonical animated",
        "applications/holofractal_harmonizer/lane5_holographic_sprite_5184.html",
        "benchmarks/pass220/benchmark_i041_raw_html_lane5_ingress.py",
    ):
        assert token in source, token
