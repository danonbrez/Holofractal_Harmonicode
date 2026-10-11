"""Second-layer 5184-cell audio-light Brownian probability and neuronal adjacency."""
from pathlib import Path
import re
import shutil
import subprocess
import pytest

def test_render_only_wiring_keeps_native_swarm_and_receipts_untouched():
    html=Path("examples/ParticleSimulation.html").read_text()
    js=Path("examples/ParticleSimulationAudioBridge.js").read_text()
    m=re.search(r'<script id="hhsAudioInline">\s*([\s\S]*?)\s*</script>',html)
    assert m and m.group(1).strip()==js.strip()
    assert "audioVisual.projectBrownianAntiParticle(p,particleBatchMatrix);" in html
    assert "window.HHSAudioViz.observeBrownianSubstep();" in html
    assert "for(let s=0;s<steps;s++){ updateSpiralParticles();" in html
    assert "if(!renderGate && audioVisualFrame){" in html
    assert "LAYER_SPLIT=CORE_N+8*EXC_N" in html
    assert "brownianPhysicsAdmission:false" in js
    assert "p.position." not in js
    for forbidden in ("thPos[","thVel[","updateSwarmCoupling(","computeManifoldHash("):
        assert forbidden not in js

def test_probability_replay_bounds_and_exact_5184_substep_history():
    node=shutil.which("node")
    if not node:pytest.skip("node missing")
    program=r"""
const fs=require("fs"),vm=require("vm"),assert=require("assert");
const src=fs.readFileSync("examples/ParticleSimulationAudioBridge.js","utf8");
function load(){
 let w={},d={readyState:"loading",addEventListener(){}};
 vm.runInNewContext(src,{window:w,document:d,
  Math,Number,Object,Array,isFinite,Float32Array,Uint8Array,WeakMap});
 return w.HHSAudioViz;
}
let a=load(),b=load();
assert.equal(a.diagnostics.brownianAntiParticleCells,5184);
assert.equal(a.diagnostics.brownianTickDelay,5184);
assert.equal(a.diagnostics.brownianPhysicsAdmission,false);
assert.equal(a.brownianProbabilityAt(-1,.4,110,2,0),0);
assert.equal(a.brownianProbabilityAt(5184,.4,110,2,0),0);
assert.equal(a.brownianProbabilityAt(0,0,110,2,0),0);
assert.ok(a.brownianProbabilityAt(0,.6,110,2,0)>
 a.brownianProbabilityAt(0,.6,2000,2,0));
for(const [frame,rms,hz,phase,flip] of [
 [0,.5,110,9,0],[1,.6,220,10,1],[2,.4,330,11,0],
 [3,.15,440,12,1],[4,0,0,12,0]]){
 assert.equal(a.advanceBrownianVisual(frame,rms,hz,phase,flip),true);
 assert.equal(b.advanceBrownianVisual(frame,rms,hz,phase,flip),true);
 assert.equal(a.advanceBrownianVisual(frame,rms,hz,phase,flip),false);
 for(const k of [0,1,71,72,1024,5183]){
  assert.equal(a.brownianProbabilitySlot(k),b.brownianProbabilitySlot(k));
  let av=a.brownianOffsetAt(k),bv=b.brownianOffsetAt(k);
  for(let i=0;i<3;i++){
   assert.equal(av[i],bv[i]);
   assert.ok(Math.abs(av[i])<=.05);
   assert.ok(Number.isFinite(av[i]));
  }
 }
}
assert.equal(a.brownianOffsetAt(5184),null);
const time=load();
for(let k=0;k<5184;k++){
 const v=time.observeBrownianSubstep();
 assert.equal(v.tick,k);
 assert.equal(v.delayedTick,-1);
 assert.equal(v.flip,k%2);
}
assert.equal(time.observeBrownianSubstep().delayedTick,0);
assert.equal(time.observeBrownianSubstep().delayedTick,1);
assert.equal(time.diagnostics.brownianTick,5186);
assert.equal(time.diagnostics.brownianDelayedTick,1);
"""
    p=subprocess.run([node,"-e",program],capture_output=True,text=True)
    assert p.returncode==0,p.stdout+"\n"+p.stderr
