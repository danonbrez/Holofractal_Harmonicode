"""Pass 220 stereo audio projection amplitude, boundary and Q144 harmonic regression."""
from pathlib import Path
import re
import shutil
import subprocess
import pytest
HTML=Path("examples/ParticleSimulation.html")
BRIDGE=Path("examples/ParticleSimulationAudioBridge.js")

def test_mirrored_projection_low_gain_and_pure_render_authority():
    html=HTML.read_text(encoding="utf8")
    js=BRIDGE.read_text(encoding="utf8")
    inline=re.search(r'<script id="hhsAudioInline">\s*([\s\S]*?)\s*</script>',html)
    assert inline and inline.group(1).strip()==js.strip()
    assert 'id="audioVizGainValue">0.020</output>' in html
    assert 'min="0" max="0.05" step="0.001" value="0.020"' in html
    assert 'geometryEnabled:false, gain:GEOMETRY_GAIN.defaultValue' in js
    assert 'x*cellularBoundaryScale' in js
    assert 'e[0]*=particleSize' in js
    assert 'state.harmonicPhase[bus]' in js
    assert 'q144Index(0,sample,screenEnergy[bus],clock.frame,bus)' not in js
    assert 'p.position.' not in js
    assert 'canonicalMutation:false' in js

def test_pcm_frequency_and_harmonic_overtone_rotation_amplitude_growth():
    node=shutil.which("node")
    if not node:pytest.skip("node unavailable")
    program=r"""
const fs=require("fs"),vm=require("vm"),assert=require("assert");
const code=fs.readFileSync("examples/ParticleSimulationAudioBridge.js","utf8");
const win={},doc={readyState:"loading",addEventListener(){}};
vm.runInNewContext(code,{window:win,document:doc,
 Float32Array,WeakMap,Array,Math,Number,Object,isFinite});
const viz=win.HHSAudioViz;
function sizes(sample,rms,gain){
 const x=new Float32Array(3);viz.amplitudeGeometry(sample,rms,gain,x);
 return Array.from(x);
}
const zero=sizes(0,0,.02),noGain=sizes(.8,.6,0);
const quiet=sizes(.05,.01,.02),loud=sizes(.7,.4,.02);
const max=sizes(1,1,.05),clamped=sizes(1,1,5);
assert.deepStrictEqual(clamped,max,"geometry must fail closed at .05");
assert.ok(max[1]<=1.221&&max[2]<=1.161,"amplitude scale bounded");
assert.deepStrictEqual(zero,[0,1,1]);
assert.deepStrictEqual(noGain,[0,1,1]);
assert.ok(loud[0]>quiet[0]&&loud[1]>quiet[1]&&loud[2]>quiet[2]);
assert.ok(loud[1]>=loud[2]&&quiet[1]>=quiet[2]);
const tone=hz=>Float32Array.from({length:735},
 (_,k)=>.6*Math.sin(2*Math.PI*hz*k/44100));
const low=viz.harmonicProfile(tone(110),0,NaN);
const high=viz.harmonicProfile(tone(220),0,NaN);
assert.ok(Math.abs(low.frequencyHz-110)<1,low.frequencyHz);
assert.ok(Math.abs(high.frequencyHz-220)<1,high.frequencyHz);
assert.equal(viz.harmonicProfile(tone(0),0,NaN).frequencyHz,0);
assert.ok(viz.harmonicStep(220,1)>viz.harmonicStep(110,1));
assert.ok(viz.harmonicStep(110,2)>viz.harmonicStep(110,1));
assert.equal(viz.harmonicStep(0,4),0);
const a=viz.q144Index(12,.2,.1,3,0);
assert.notEqual(viz.q144Index(12,.2,.1,8,0),a);
assert.equal(viz.q144Index(12,.2,.1,3,1),(a+72)%144);
assert.equal(viz.diagnostics.geometryNormalizationGain,.02);
assert.equal(viz.diagnostics.geometryNormalizationGainMax,.05);
assert.equal(viz.diagnostics.haloEmissionGain,.4);
assert.equal(viz.diagnostics.harmonicColorWheel,true);
assert.equal(viz.diagnostics.cellularBoundaryAmplitudeResponsive,true);
assert.equal(viz.diagnostics.canonicalMutation,false);
"""
    result=subprocess.run([node,"-e",program],capture_output=True,text=True)
    assert result.returncode==0,result.stdout+"\n"+result.stderr
