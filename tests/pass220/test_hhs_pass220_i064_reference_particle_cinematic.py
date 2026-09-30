from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "examples/ParticleSimulation.html"


def source() -> str:
    return HTML.read_text(encoding="utf-8")


def block(text: str, start: str, end: str) -> str:
    a = text.index(start)
    b = text.index(end, a)
    return text[a:b]


def test_i064_reference_visual_contract_is_projection_only_and_live():
    text = source()
    assert 'schema:"HHS_PASS_220_I064_REFERENCE_PARTICLE_CINEMATIC_V1"' in text
    assert "projectionOnly:true" in text
    assert "logicalParticleMutation:false" in text
    assert "pureBlackBackground:true" in text
    assert "deterministicVisualProfile:true" in text
    assert "manualZoom:true" in text
    assert "boundaryOrbitAvailable:true" in text
    assert "defaultBoundaryOrbit:false" in text
    assert "continuousProjectionSync:true" in text
    assert "canonicalMutationAuthority:false" in text

    # Regression: I064 must never freeze live presentation or reintroduce
    # the former forced camera ingress/zoom path.
    assert "freezeStaticProjection" not in text
    assert "projectionFrozen" not in text
    assert "ingressCameraZ" not in text
    assert "updateReferenceCamera" not in text
    assert "applyReferenceStaticCamera" not in text


def test_i064_preserves_i057_and_authoritative_physics_loop_verbatim():
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


def test_i064_visual_profile_is_deterministic_render_only():
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
    assert "referenceFov:60" in visual
    assert "I064_ROLE_PRIMARY" in visual
    assert "I064_ROLE_SATELLITE" in visual
    assert "I064_ROLE_HALO" in visual
    assert "I064_ROLE_FOREGROUND" in visual


def test_i064_instanced_projection_scales_depth_without_logical_write():
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
    assert "particleBatchMatrix.compose" in render
    assert "mesh.setMatrixAt" in render
    assert "mesh.setColorAt" in render
    assert ".position.set(" not in render
    assert ".position.copy(" not in render
    assert "userData" not in render


def test_i064_projection_sync_is_continuous_and_cannot_freeze_scene():
    text = source()
    sync = block(
        text,
        "function syncParticleRenderBatches()",
        "function logDebug(message)",
    )
    assert "for(let i=0;i<particleRenderBatches.length;i++)" in sync
    assert "syncParticleRenderBatch(particleRenderBatches[i])" in sync
    assert "return;" not in sync
    assert "projectionFrozen" not in sync
    assert "force" not in sync


def test_i064_manual_camera_and_zoom_are_default():
    text = source()
    init = block(text, "function initScene()", "// Add basic lighting")
    assert "controls.enabled=true;" in init
    assert "controls.enableZoom = I064_REFERENCE_VISUAL.manualZoom;" in init
    assert "controls.zoomSpeed = 0.8;" in init
    assert "controls.minDistance = 0.5;" in init
    assert "controls.maxDistance = 500;" in init
    assert "I064_REFERENCE_VISUAL.initialCameraZ" in init
    assert "defaultBoundaryOrbit:false" in text
    assert "Boundary Orbit OFF (V)" in text


def test_i064_boundary_orbit_preserves_user_selected_radius():
    text = source()
    camera = block(
        text,
        "function captureBoundaryOrbitFromCamera()",
        "function originalReferenceParticlePosition",
    )
    assert "referenceTmp.copy(camera.position).sub(boundaryOrbit.target);" in camera
    assert "boundaryOrbit.radius=r;" in camera
    assert "boundaryOrbit.theta0=Math.atan2" in camera
    assert "boundaryOrbit.phi0=clampReferencePolar" in camera
    assert "camera.position.set(" in camera
    assert "camera.lookAt(boundaryOrbit.target);" in camera
    assert "toggleBoundaryOrbit(force)" in camera
    assert 'b.textContent=boundaryOrbit.on?"Boundary Orbit ON (V)":"Boundary Orbit OFF (V)";' in camera

    # Orbit may move around the boundary but must not impose a new distance.
    assert "staticCameraZ" not in camera
    assert "ingressCameraZ" not in camera
    assert "camera.zoom" not in camera


def test_i064_follow_seed_reconstructs_original_unaltered_spiral_path():
    text = source()
    follow = block(
        text,
        "function originalReferenceParticlePosition(nowMs,out)",
        "function resetReferenceFollow()",
    )

    # Original phyllotaxis seed geometry from initSpiralParticles().
    assert "const angle=j*goldenRatio*Math.PI*2;" in follow
    assert "const radius=Math.sqrt(j)*3;" in follow
    assert "const localX=radius*Math.cos(angle);" in follow
    assert "const localY=radius*Math.sin(angle);" in follow
    assert "const localZ=Math.sin(j/5)*5*(spiral%2===0?1:-1);" in follow

    # Original toroidal/quasi-periodic group orbit from updateSpiralParticles().
    assert "const t=nowMs*0.0005;" in follow
    assert "Math.sin(t+phaseShift)*orbitRadius" in follow
    assert "Math.cos(t*simParams.evolutionSpeed+phaseShift)*orbitRadius" in follow
    assert "Math.sin(t*simParams.goldenRatio+phaseShift)*orbitRadius" in follow

    # Follow seed must never read or join the live physics state.
    for forbidden in (
        "thPos",
        "thVel",
        "updateSwarmCoupling",
        "bond",
        "bary",
        "collision",
        "constructor",
        "compM",
        "particles[",
        "particles.push",
    ):
        assert forbidden not in follow


def test_i064_follow_camera_observes_reference_path_only():
    text = source()
    follow_camera = block(
        text,
        "function updateReferenceFollowCamera(nowMs)",
        "function toggleReferenceFollow(force)",
    )
    assert "originalReferenceParticlePosition(nowMs,referenceFollow.pos);" in follow_camera
    assert "referenceFollow.tangent" in follow_camera
    assert "camera.position.lerp(referenceFollow.cam,0.18);" in follow_camera
    assert "camera.lookAt(referenceFollow.look);" in follow_camera
    for forbidden in ("thPos", "thVel", "bary", "bond", "collision", "userData"):
        assert forbidden not in follow_camera

    assert "const chase={ on:false };" in text
    assert "toggleReferenceFollow(force);" in text
    assert "Follow Seed (C)" in text
    assert "function referenceFollowNext()" in text


def test_i064_follow_and_boundary_orbit_are_mutually_exclusive_projection_modes():
    text = source()
    assert "if(chase.on) toggleChase(false);" in text
    assert "boundaryOrbit.on=false;" in text
    assert "controls.enabled=!referenceFollow.on && !boundaryOrbit.on;" in text
    assert "if(!chase.on && !boundaryOrbit.on) controls.update();" in text
    assert "if(chase.on) updateChaseCamera();" in text
    assert "else if(boundaryOrbit.on) updateBoundaryOrbitCamera(performance.now());" in text
    assert 'else if(e.key==="v"||e.key==="V") toggleBoundaryOrbit();' in text


def test_i064_reference_profile_hides_debug_instrumentation_only_visually():
    text = source()
    assert "hideInstrumentation:true" in text
    assert "if(ninthNucleus) ninthNucleus.visible=false;" in text
    assert "if(tessGeo && tessGeo.lines) tessGeo.lines.visible=false;" in text
    assert "function initNinthNucleus()" in text
    assert "function updateNinthNucleus()" in text
    assert "function buildTesseract()" in text
    assert "function updateTesseract()" in text


def test_i064_reference_quality_uses_smoother_geometry_and_color_output():
    text = source()
    assert text.count("new THREE.SphereGeometry(0.1, 12, 8)") >= 2
    assert 'new THREE.MeshBasicMaterial({color:0xffffff, toneMapped:false})' in text
    assert "renderer.setClearColor(0x000000,1);" in text
    assert "renderer.outputEncoding=THREE.sRGBEncoding" in text


def test_i064_composition_has_primary_satellite_halo_foreground_roles():
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
    assert "return {scale,softScale,depth,compression,role,offset,rgb};" in visual


def test_i064_clean_presentation_preserves_controls_but_hides_idle_chrome():
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


def test_i064_static_core_uses_nonlinear_radial_compression():
    text = source()
    visual = block(
        text,
        "function buildReferenceVisualProfile(points,batchIndex)",
        "function clampReferencePolar(phi)",
    )
    assert "const localRadius=Math.hypot(p.position.x,p.position.y,p.position.z);" in visual
    assert "localRadius/I064_REFERENCE_VISUAL.coreRadialKnee" in visual
    assert "I064_REFERENCE_VISUAL.coreInnerCompression" in visual
    assert "localRadius/I064_REFERENCE_VISUAL.satelliteRadialKnee" in visual
    assert "I064_REFERENCE_VISUAL.satelliteInnerCompression" in visual
    assert "0.72+0.28*re" in visual


def test_i064_color_tail_preserves_muted_dark_and_pastel_particles():
    text = source()
    visual = block(
        text,
        "function buildReferenceVisualProfile(points,batchIndex)",
        "function clampReferencePolar(phi)",
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
        "function syncParticleRenderBatches()",
    )
    assert "const p=points[i], q=p.position" in render
    assert "if(profile && profile.rgb)" in render
    assert "mesh.setColorAt(i,p.material.color);" in render
