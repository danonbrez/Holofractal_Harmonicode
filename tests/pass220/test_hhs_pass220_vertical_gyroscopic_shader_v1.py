"""Phase-locked vertical reciprocal shader from inherited RML2/RML4 u72 gear."""
from pathlib import Path
import re
import shutil
import subprocess
import pytest

def test_exact_inline_shader_mirror_and_authority_separation():
    html=Path("examples/ParticleSimulation.html").read_text(encoding="utf-8")
    js=Path("examples/ParticleSimulationAudioBridge.js").read_text(encoding="utf-8")
    inline=re.search(r'<script id="hhsAudioInline">\s*([\s\S]*?)\s*</script>',html)
    assert inline and inline.group(1).strip()==js.strip()
    assert 'value="0.40" style="width:100%;"' in html
    assert 'paintGyroscopicVerticalPair(ctx,W,H,' in js
    assert 'GYRO_SHADER.quarterTurn' in js
    assert 'canonicalMutationAuthority:false' in js
    assert 'canonicalMutation:false' in js
    assert 'p.position.' not in js

def test_72_ring_18_quarter_product_orientation_and_vertical_shaders():
    node=shutil.which("node")
    if not node:
        pytest.skip("Node.js unavailable")
    code=r"""
const assert=require("assert"),fs=require("fs"),vm=require("vm");
const src=fs.readFileSync("examples/ParticleSimulationAudioBridge.js","utf8");
const win={},doc={readyState:"loading",addEventListener(){}};
vm.runInNewContext(src,{window:win,document:doc,
 Float32Array,WeakMap,Array,Math,Number,Object,isFinite});
const api=win.HHSAudioViz;
const mod=x=>(x%72+72)%72;
for(let step=0;step<72;step++){
 const a=api.gyroscopicPhaseGear72(step),b=api.gyroscopicPhaseGear72(step+72);
 assert.equal(JSON.stringify(a),JSON.stringify(b),"u72 period");
 assert.equal(mod(a.x+a.z),0,"primary reciprocal x/z");
 assert.equal(mod(a.y+a.w),36,"orthogonal reciprocal y/w");
 assert.equal(a.xy,mod(a.x+18),"ordered xy");
 assert.equal(a.yx,mod(a.y-18),"ordered yx");
 assert.equal(a.zw,mod(a.z-18),"ordered zw");
 assert.equal(a.wz,mod(a.w+18),"ordered wz");
 const pair=api.verticalReciprocalGradientPair(step,.3,-.6,.16,.22);
 assert.equal(pair.quarterTurn,18);
 assert.ok(pair.oppositeHuePairs,"Q144 reciprocal shader hues");
 for(let k=0;k<4;k++)
  assert.equal(pair.rightHues[k],(pair.leftHues[k]+72)%144);
}
const closed=api.gyroscopicPhaseGear72(0);
assert.equal(api.gyroscopicPhaseGear72(18).phase72,18);
assert.equal(api.gyroscopicPhaseGear72(36).phase72,36);
assert.equal(api.gyroscopicPhaseGear72(54).phase72,54);
assert.equal(api.gyroscopicPhaseGear72(72).phase72,closed.phase72);
const stay=api.transportGyroscopicPhase72(14,0,1,0,1);
const slow=api.transportGyroscopicPhase72(14,110,1,110,1);
const fast=api.transportGyroscopicPhase72(14,440,1,440,1);
assert.equal(stay,14);
assert.ok(fast>slow && slow>14,"harmonic frequency controls rotation");
assert.ok(api.transportGyroscopicPhase72(71.9,432,1,432,1)<2);
assert.ok(api.transportGyroscopicPhase72(1,220,2,220,2)>
          api.transportGyroscopicPhase72(1,220,1,220,1));
const draws=[];
const ctx={globalCompositeOperation:"source-over",
 createLinearGradient(x0,y0,x1,y1){
  const shader={x0,y0,x1,y1,stops:[],addColorStop(t,c){this.stops.push([t,c])}};
  draws.push(shader);return shader;
 },
 fillRect(x,y,w,h){assert.ok(w>0&&h>0)}
};
const pair=api.paintGyroscopicVerticalPair(ctx,900,500,.6,-.3,.25,.18,18);
assert.equal(draws.length,2);
assert.ok(pair.oppositeHuePairs);
assert.equal(draws[0].y0,0);
assert.equal(draws[0].y1,500);
assert.equal(draws[1].y0,0);
assert.equal(draws[1].y1,500);
assert.equal(draws[0].stops.length,6);
assert.equal(draws[1].stops.length,6);
assert.equal(ctx.globalCompositeOperation,"source-over");
draws.length=0;
api.paintGyroscopicVerticalPair(ctx,900,500,0,0,0,0,18);
assert.equal(draws.length,0,"silence does not repaint full-scene gradient");
assert.equal(api.diagnostics.gyroscopeFullPeriod,72);
assert.equal(api.diagnostics.gyroscopeQuarterTurn,18);
assert.equal(api.diagnostics.verticalReciprocalGyroscopicGradient,true);
assert.equal(api.diagnostics.canonicalMutation,false);
"""
    result=subprocess.run([node,"-e",code],capture_output=True,text=True)
    assert result.returncode==0,result.stdout+"\n"+result.stderr
