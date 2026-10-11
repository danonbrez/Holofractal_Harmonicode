"""I084: original two-layer HTML physics and current I063 PCM lighting contract.

These are structural regressions; the Playwright raw-ingress benchmark provides
the independent browser/MP4 and activated-audio runtime witness.
"""
from pathlib import Path
import re

HTML = Path("examples/ParticleSimulation.html")
RAW = Path("benchmarks/pass220/benchmark_i041_raw_html_lane5_ingress.py")
BRIDGE = Path("examples/ParticleSimulationAudioBridge.js")


def test_original_10368_carrier_physics_remains_authoritative():
    s = HTML.read_text(encoding="utf8")
    for item in (
        "initSpiralParticles(false)",
        "initExchangeNuclei(false)",
        "initSpiralParticles(true)",
        "initExchangeNuclei(true)",
        "const particleCount = 2592;",
        "function updateSwarmCoupling()",
        "function updateSpiralParticles()",
        "updateTesseract();",
        "function constructorScan()",
        "const particleRenderBatches=[];",
        "renderGate=((renderTick%4)===0);",
        "for(let s=0;s<steps;s++){ updateSpiralParticles();",
        "renderer.render(scene, camera);",
    ):
        assert item in s, item


def test_inline_pcm_waveform_source_is_live_and_has_stereo_phase_channels():
    s = HTML.read_text(encoding="utf8")
    for item in (
        'id="hhsAudioInline"',
        'id="audioVizFile"',
        'id="audioVizPlayer"',
        'id="audioVizPlay"',
        "44,100 PCM Hz / 735 samples = 60 audio frames/s",
        "function q144Index(",
        "function lightAttenuation(",
        "projectParticleGlow",
        "particleHaloOpacity",
        "get diagnostics()",
        "window.HHSAudioViz",
    ):
        assert item in s, item


def test_current_i063_graft_is_post_simulation_and_gpu_only():
    s = HTML.read_text(encoding="utf8")
    assert s.index("function updateSwarmCoupling()") < s.index("HHS PASS 220 I063")
    graft = s.split("HHS PASS 220 I063", 1)[1]
    for item in (
        'HHS_PASS_220_I063_BROWN_NOISE_AUDIO_CARRIER_GRAFT_V1',
        "function audioState()",
        "function modulate()",
        "const reg=bindL2();",
        "if(base>=5184) l2batches.push({batch:bt, base});",
        "G.localIdx=a.frame%5184;",
        "const g=I063.attractionGain*a.rms*bn;",
        "let pull=g/(1+r2);",
        "const localGlow=Math.min(1,2*Math.sqrt(Math.max(0,a.rms)));",
        "const __frozenSync=syncParticleRenderBatches;",
        "syncParticleRenderBatches=function(){ __frozenSync(); if(G.on) modulate(); };",
        "batch.mesh.instanceMatrix.needsUpdate=true;",
        "window.HHSBrownL2=Object.freeze(",
        "physicsFeedbackEnabled:false",
        "vm81Admission:false",
        "canonicalMutation:false",
        "if(!a){ G.bypasses++; return; }",
    ):
        assert item in graft, item
    # No mutation of the particle simulation's core field positions/velocities
    for forbidden in ("thPos[ix]=", "thVel[ix]=", "p.position.set(", "updateSwarmCoupling();"):
        assert forbidden not in graft, forbidden


def test_current_html_differs_from_older_external_brownian_bridge_intentionally():
    html = HTML.read_text(encoding="utf8")
    bridge = BRIDGE.read_text(encoding="utf8")
    m = re.search(r'<script id="hhsAudioInline">\s*([\s\S]*?)\s*</script>', html)
    assert m
    assert "HHS_PASS_220_I063_BROWN_NOISE_AUDIO_CARRIER_GRAFT_V1" in html
    # The external bridge remains an older standalone artifact. The updated
    # inline implementation is the one actually executed by the HTML.
    assert m.group(1).strip() != bridge.strip()
    assert "function brownianProbabilityAt(" in bridge
    assert "function brownianProbabilityAt(" not in m.group(1)


def test_raw_capture_selects_actual_html_audio_and_verifies_l2_writes():
    s = RAW.read_text(encoding="utf8")
    for item in (
        'page.locator("#audioVizFile").set_input_files(',
        'page.locator("#audioVizPlay").click()',
        "window.HHSBrownL2.diagnostics",
        '"l2_writes_seen"',
        '"audio_waveform_capture": audio_capture',
        "source_sha_before == source_sha_after",
        "encode_video(frames, video_path, args.fps)",
    ):
        assert item in s, item
