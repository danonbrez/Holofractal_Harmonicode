from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "examples/ParticleSimulation.html"


def source() -> str:
    return HTML.read_text(encoding="utf-8")


def block(text: str, start: str, end: str) -> str:
    a = text.index(start)
    b = text.index(end, a)
    return text[a:b]


def test_i064_reference_visual_contract_is_projection_only():
    text = source()
    assert 'schema:"HHS_PASS_220_I064_REFERENCE_PARTICLE_CINEMATIC_V1"' in text
    assert "referenceClipSeconds:122/24" in text
    assert "projectionOnly:true" in text
    assert "logicalParticleMutation:false" in text
    assert "pureBlackBackground:true" in text
    assert "deterministicVisualProfile:true" in text
    assert "canonicalMutationAuthority:false" in text
    assert "defaultMotion:true" in text


def test_i064_preserves_i057_and_authoritative_physics_loop():
    text = source()
    assert 'schema:"HHS_PASS_220_I057_PARTICLE_SIMULATION_ZERO_LOSS_PERF_V1"' in text
    assert (
        "for(let s=0;s<steps;s++){ updateSpiralParticles(); "
        "time += simParams.evolutionSpeed * simParams.timeDilationFactor; }"
    ) in text
    assert "function updateSwarmCoupling()" in text
    assert "function constructorScan()" in text
    assert "renderGate=((renderTick%4)===0);" in text
    assert "syncParticleRenderBatches();" in text


def test_i064_visual_profile_is_deterministic_and_render_only():
    text = source()
    visual = block(
        text,
        "const I064_REFERENCE_VISUAL",
        "const particleRenderBatches=[]",
    )
    assert "function visualHash32" in visual
    assert "function buildReferenceVisualProfile" in visual
    assert "Math.random" not in visual
    assert "coreCompression:0.235" in visual
    assert "satelliteCompression:0.46" in visual
    assert "coreDepthSpan:18.0" in visual
    assert "satelliteDepthSpan:12.0" in visual
    assert "minParticleScale:0.38" in visual
    assert "maxParticleScale:5.25" in visual
    assert "staticCameraZ:36.0" in visual
    assert "ingressCameraZ:5.2" in visual
    assert "referenceFov:62" in visual


def test_i064_instanced_projection_scales_and_separates_depth_without_logical_write():
    text = source()
    render = block(
        text,
        "function syncParticleRenderBatch(batch)",
        "function syncParticleRenderBatches()",
    )
    assert "profile.compression[i]" in render
    assert "profile.scale[i]" in render
    assert "profile.depth[i]" in render
    assert "particleBatchMatrix.compose" in render
    assert "mesh.setMatrixAt" in render
    assert "mesh.setColorAt" in render
    assert ".position.set(" not in render
    assert ".position.copy(" not in render
    assert "userData" not in render


def test_i064_camera_matches_reference_clip_rhythm_and_has_user_toggle():
    text = source()
    camera = block(
        text,
        "function updateReferenceCamera(nowMs)",
        "function toggleReferenceMotion(force)",
    )
    assert "I064_REFERENCE_VISUAL.referenceClipSeconds*1000" in camera
    assert "Math.pow(Math.sin(Math.PI*u),2)" in camera
    assert "I064_REFERENCE_VISUAL.staticCameraZ" in camera
    assert "I064_REFERENCE_VISUAL.ingressCameraZ" in camera
    assert "camera.position.copy(referenceMotion.pos)" in camera
    assert "camera.lookAt(referenceMotion.look)" in camera

    assert 'id="referenceMotionBtn"' in text
    assert "Reference Motion ON (V)" in text
    assert 'else if(e.key==="v"||e.key==="V") toggleReferenceMotion();' in text


def test_i064_chase_camera_takes_priority_without_physics_changes():
    text = source()
    assert "referenceMotion.on=false;" in text
    assert "if(chase.on) updateChaseCamera();" in text
    assert "else if(referenceMotion.on) updateReferenceCamera(performance.now());" in text
    assert "if(!chase.on && !referenceMotion.on) controls.update();" in text


def test_i064_reference_profile_hides_debug_instrumentation_only_at_projection():
    text = source()
    assert "hideInstrumentation:true" in text
    assert "if(ninthNucleus) ninthNucleus.visible=false;" in text
    assert "if(tessGeo && tessGeo.lines) tessGeo.lines.visible=false;" in text
    # The underlying instrument constructors/update functions must remain.
    assert "function initNinthNucleus()" in text
    assert "function updateNinthNucleus()" in text
    assert "function buildTesseract()" in text
    assert "function updateTesseract()" in text
