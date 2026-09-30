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
    assert "coreCompression:0.20" in visual
    assert "coreInnerCompression:0.125" in visual
    assert "coreRadialKnee:25.0" in visual
    assert "satelliteCompression:0.115" in visual
    assert "satelliteInnerCompression:0.072" in visual
    assert "satelliteRadialKnee:15.0" in visual
    assert "haloCompression:0.50" in visual
    assert "foregroundCompression:0.72" in visual
    assert "coreDepthSpan:12.0" in visual
    assert "satelliteDepthSpan:5.5" in visual
    assert "haloDepthSpan:19.0" in visual
    assert "foregroundDepthSpan:25.0" in visual
    assert "primaryCenterX:-0.4" in visual
    assert "primaryCenterY:3.9" in visual
    assert "satelliteCenterX:-12.5" in visual
    assert "satelliteCenterY:14.5" in visual
    assert "satelliteFraction:0.10" in visual
    assert "haloFraction:0.15" in visual
    assert "foregroundFraction:0.045" in visual
    assert "minParticleScale:0.30" in visual
    assert "maxParticleScale:7.25" in visual
    assert "foregroundHaloScale:1.14" in visual
    assert "foregroundHaloOpacity:0.085" in visual
    assert "neutralColorFraction:0.085" in visual
    assert "dimColorFraction:0.11" in visual
    assert "freezeStaticProjection:true" in visual
    assert "staticCameraZ:34.0" in visual
    assert "ingressCameraZ:4.8" in visual
    assert "referenceFov:60" in visual
    assert "I064_ROLE_PRIMARY" in visual
    assert "I064_ROLE_SATELLITE" in visual
    assert "I064_ROLE_HALO" in visual
    assert "I064_ROLE_FOREGROUND" in visual


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
    assert "profile.offset[o]" in render
    assert "const wx=q.x+gx, wy=q.y+gy, wz=q.z+gz;" in render
    assert " - gx" in render
    assert " - gy" in render
    assert " - gz" in render
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
    assert "function applyReferenceStaticCamera()" in text
    assert 'referenceMotion.look.set(-0.4,0.15,-2.7);' in text
    assert 'b.textContent=referenceMotion.on?"Reference Motion ON (V)":"Reference Static (V)";' in text

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



def test_i064_static_reference_quality_uses_smoother_geometry_and_color_output():
    text = source()
    assert text.count("new THREE.SphereGeometry(0.1, 12, 8)") >= 2
    assert 'new THREE.MeshBasicMaterial({color:0xffffff, toneMapped:false})' in text
    assert "renderer.setClearColor(0x000000,1);" in text
    assert "renderer.outputEncoding=THREE.sRGBEncoding" in text


def test_i064_static_composition_has_distinct_primary_satellite_halo_foreground_roles():
    text = source()
    visual = block(
        text,
        "const I064_REFERENCE_VISUAL",
        "const particleRenderBatches=[]",
    )
    assert "I064_ROLE_PRIMARY=0" in visual
    assert "I064_ROLE_SATELLITE=1" in visual
    assert "I064_ROLE_HALO=2" in visual
    assert "I064_ROLE_FOREGROUND=3" in visual
    assert "Role selection is deterministic and projection-only." in visual
    assert "primaryCenterX" in visual
    assert "satelliteCenterX" in visual
    assert "foregroundFraction" in visual
    assert "return {scale,softScale,depth,compression,role,offset,rgb};" in visual



def test_i064_reference_clean_static_presentation_preserves_controls_but_hides_idle_chrome():
    text = source()
    assert "body { margin: 0; overflow: hidden; background: #000;" in text
    assert "autoHideChrome:true" in text
    assert "chromeIdleMs:1800" in text
    assert 'body.reference-clean-ui #toggleShell' in text
    assert 'body.reference-clean-ui #osShell' in text
    assert 'body.reference-clean-ui #hud' in text
    assert 'body.reference-clean-ui #densityCtl' in text
    assert "function setReferenceChromeVisible(show)" in text
    assert "function scheduleReferenceChromeHide()" in text
    assert "function wakeReferenceChrome()" in text
    assert "function toggleReferenceChromePin()" in text
    assert "window.addEventListener('mousemove',wakeReferenceChrome,{passive:true});" in text
    assert "window.addEventListener('touchstart',wakeReferenceChrome,{passive:true});" in text
    assert 'else if(e.key==="h"||e.key==="H") toggleReferenceChromePin();' in text


def test_i064_static_projection_is_a_true_visual_freeze_without_stopping_physics():
    text = source()
    assert "projectionFrozen:false" in text
    assert "freezeStaticProjection:true" in text
    assert "referenceMotion.projectionFrozen=false;" in text
    assert "syncParticleRenderBatches(true);" in text
    assert (
        "referenceMotion.projectionFrozen="
        "I064_REFERENCE_VISUAL.freezeStaticProjection;"
    ) in text
    assert "function syncParticleRenderBatches(force)" in text
    assert "if(referenceMotion.projectionFrozen && !force) return;" in text
    # Physics remains outside the presentation freeze and continues every step.
    assert (
        "for(let s=0;s<steps;s++){ updateSpiralParticles(); "
        "time += simParams.evolutionSpeed * simParams.timeDilationFactor; }"
    ) in text


def test_i064_static_core_uses_nonlinear_radial_compression_for_pinpoint_density():
    text = source()
    visual = block(
        text,
        "function buildReferenceVisualProfile(points,batchIndex)",
        "function referenceEase(x)",
    )
    assert "const localRadius=Math.hypot(p.position.x,p.position.y,p.position.z);" in visual
    assert "localRadius/I064_REFERENCE_VISUAL.coreRadialKnee" in visual
    assert "I064_REFERENCE_VISUAL.coreInnerCompression" in visual
    assert "localRadius/I064_REFERENCE_VISUAL.satelliteRadialKnee" in visual
    assert "I064_REFERENCE_VISUAL.satelliteInnerCompression" in visual
    assert "0.72+0.28*re" in visual


def test_i064_color_tail_preserves_muted_dark_and_pastel_reference_particles():
    text = source()
    visual = block(
        text,
        "function buildReferenceVisualProfile(points,batchIndex)",
        "function referenceEase(x)",
    )
    assert "I064_REFERENCE_VISUAL.neutralColorFraction" in visual
    assert "I064_REFERENCE_VISUAL.dimColorFraction" in visual
    assert "sat=0.12+0.30*u1;" in visual
    assert "light=0.18+0.22*u1;" in visual
    assert "sat=0.52+0.38*u1;" in visual


def test_i064_foreground_halo_is_sparse_local_projection_not_global_bloom():
    text = source()
    assert "const softMesh=new THREE.InstancedMesh(" in text
    assert "opacity:I064_REFERENCE_VISUAL.foregroundHaloOpacity" in text
    assert "depthWrite:false" in text
    assert "softScale[i]=(r===I064_ROLE_FOREGROUND)" in text
    assert "softMesh.setMatrixAt(i,particleBatchMatrix);" in text
    assert "softMesh.setColorAt(i,particleBatchColor);" in text
    assert "UnrealBloomPass" not in text


def test_i064_keeps_frozen_i057_color_projection_as_real_fallback():
    text = source()
    render = block(
        text,
        "function syncParticleRenderBatch(batch)",
        "function syncParticleRenderBatches(force)",
    )
    assert "const p=points[i], q=p.position" in render
    assert "if(profile && profile.rgb)" in render
    assert "mesh.setColorAt(i,p.material.color);" in render
