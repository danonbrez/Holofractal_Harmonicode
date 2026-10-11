"""Regression guards for the canonical particle-game stereo HTML patch."""
import shutil
import subprocess
from pathlib import Path
import pytest

HTML=Path("examples/ParticleSimulation.html")
BRIDGE=Path("examples/ParticleSimulationAudioBridge.js")

def test_game_controls_are_present_and_all_primary_bindings_work():
    html=HTML.read_text(encoding="utf-8")
    for control in ("toggleShell","runCommand","runCalibration","stepCycle",
                    "freqSlider","massSlider","collSlider","ctorSlider",
                    "bondSlider","topoBtn","chaseBtn","jsonCommandInput",
                    "sendQpuCommand","audioVizFile","audioVizPlayer",
                    "audioVizPlay","audioVizStop","audioVizGain"):
        assert html.count('id="'+control+'"')==1,control
    for action in ("runCommand","runCalibration","stepCycle"):
        assert 'document.getElementById("'+action+'").addEventListener("click"' in html
    for slider in ("freqSlider","massSlider","collSlider","ctorSlider","bondSlider"):
        assert slider+'.addEventListener("input"' in html
    assert 'chaseBtn.addEventListener("click"' in html
    assert 'topoBtn.addEventListener("click"' in html
    assert 'toggleButton.addEventListener("click"' in html
    assert 'id="qpuConsolePanel"' in html
    assert '<details id="qpuConsolePanel"' in html
    assert 'src="./ParticleSimulationAudioBridge.js"' in html
    assert 'id="audioVizOverlay"' not in html # dynamically added, not a second overlay
    assert 'document.getElementById("commandOutput").innerHTML' not in html

def test_audio_waveform_is_projection_only_and_preserves_physics_receipts():
    html=HTML.read_text(encoding="utf-8")
    bridge=BRIDGE.read_text(encoding="utf-8")
    assert 'for(let s=0;s<steps;s++){ updateSpiralParticles();' in html
    assert 'renderGate=((renderTick%4)===0);' in html
    assert 'compressedHash: computeManifoldHash()' in html
    assert 'window.HHSAudioViz.projectMatrix(p,particleBatchMatrix);' in html
    assert 'particleBatchMatrix.makeTranslation(q.x,q.y,q.z);' in html
    assert 'const N=10368;' in bridge
    assert 'p.position.' not in bridge
    assert 'canonicalMutation:false' in bridge
    assert 'numerator:Object.freeze(["x","xy","x+y","y"]), denominator:"zw"' in bridge
    assert 'numerator:Object.freeze(["z","zw","z-w","w"]), denominator:"xy"' in bridge
    assert 'Math.floor(i*bins/samples.length)' in bridge
    assert 'firstFrame+i-1+frac' in bridge
    assert 'registerProcessor(' in bridge
    assert 'cells=[new Float32Array(72),new Float32Array(72)]' in bridge

def test_bridge_js_and_pcm_crossing_runtime():
    node=shutil.which("node")
    if not node:
        pytest.skip("Node.js is not installed")
    program=r"""
const fs=require("fs"),vm=require("vm"),assert=require("assert");
const code=fs.readFileSync("examples/ParticleSimulationAudioBridge.js","utf8");
const window={},document={readyState:"loading",addEventListener(){}};
vm.runInNewContext(code,{window,document,Float32Array,WeakMap,Array,Math,Number,Object,
  isFinite,URL,Blob,AudioWorkletNode:undefined});
const viz=window.HHSAudioViz;
assert.equal(viz.busPair.left.denominator,"zw");
assert.equal(viz.busPair.right.denominator,"xy");
const p=viz.peakEnvelope(new Float32Array([.1,-.7,.3,.1,.9,-.2]),3);
assert.ok(Math.abs(p[0]+.7)<1e-6 && Math.abs(p[1]-.3)<1e-6 && Math.abs(p[2]-.9)<1e-6);
const prior=[0,0];
const a=viz.crossingsFromBlock(new Float32Array([-1,-.5]),
  new Float32Array([1,.5]),0,100,prior);
assert.equal(a.length,0);
const b=viz.crossingsFromBlock(new Float32Array([.5,-.5]),
  new Float32Array([-.5,.5]),2,100,prior);
assert.equal(b.length,4);
assert.ok(Math.abs(b[0][1]-.015)<1e-9);
assert.ok(Math.abs(b[1][1]-.025)<1e-9);
assert.equal(viz.diagnostics.canonicalMutation,false);
const m=code.match(/const WORKLET=\(([\s\S]*?)\);\s*async function installProcessor/);
assert.ok(m);
const processorSource=Function("return ("+m[1]+")")();
new Function(processorSource); // parse generated AudioWorklet in isolation
"""
    run=subprocess.run([node,"-e",program],text=True,capture_output=True)
    assert run.returncode==0,run.stderr
