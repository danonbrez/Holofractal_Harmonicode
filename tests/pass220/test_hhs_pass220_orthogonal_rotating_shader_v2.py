"""Regression: displayed reciprocal light gradients must actually rotate orthogonally."""
from pathlib import Path
import re
import shutil
import subprocess
import pytest

HTML=Path("examples/ParticleSimulation.html")
JS=Path("examples/ParticleSimulationAudioBridge.js")

def test_embedded_mirror_and_separate_physics_authority():
    html=HTML.read_text(encoding="utf8")
    bridge=JS.read_text(encoding="utf8")
    inline=re.search(r'<script id="hhsAudioInline">\s*([\s\S]*?)\s*</script>',html)
    assert inline and inline.group(1).strip()==bridge.strip()
    assert "state.gyroTransport72);" in bridge
    assert "paintGyroscopicLightBand(lightCtx,W,H,state.gyroTransport72,bus," in bridge
    assert 'ctx.createLinearGradient(x-extent,0,x+extent,0)' not in bridge
    assert "function gyroscopicGradientAxes72(" in bridge
    assert "if(!advanceLightingGate(clock.frame))return;" in bridge
    assert 'max="0.05" step="0.001" value="0.020"' in html
    assert 'canonicalMutation:false' in bridge
    assert 'p.position.' not in bridge
    # The 5,184-tick physical feedback is not permitted to leak into this UI-only pass.
    assert "FLD.Rb=" not in bridge
    assert "updateSwarmCoupling(" not in bridge

def test_two_true_orthogonal_full_screen_axes_and_continuous_rotation():
    node=shutil.which("node")
    if not node:pytest.skip("node not installed")
    code=r"""
const fs=require("fs"),vm=require("vm"),assert=require("assert");
const source=fs.readFileSync("examples/ParticleSimulationAudioBridge.js","utf8");
const win={},doc={readyState:"loading",addEventListener(){}};
vm.runInNewContext(source,{window:win,document:doc,
  Float32Array,WeakMap,Array,Math,Number,Object,isFinite});
const viz=win.HHSAudioViz;
function normalized(a){const x=a[2]-a[0],y=a[3]-a[1],n=Math.hypot(x,y);return [x/n,y/n]}
function axes(p){
  const a=viz.gyroscopicGradientAxes72(p,900,600);
  const x=normalized(a.left),y=normalized(a.right);
  assert.ok(Math.abs(x[0]*y[0]+x[1]*y[1])<1e-12,"not orthogonal "+p);
  assert.ok(Math.abs(Math.hypot(...x)-1)<1e-12);
  return a;
}
for(const p of [0,.25,1,9,18,27,36,54,71.75,72,144])axes(p);
let initial=axes(0),quarter=axes(18),eighth=axes(9);
assert.ok(Math.abs(normalized(initial.left)[0]-1)<1e-12);
assert.ok(Math.abs(normalized(initial.right)[1]-1)<1e-12);
assert.ok(Math.abs(normalized(quarter.left)[1]-1)<1e-12);
assert.ok(Math.abs(normalized(quarter.right)[0]+1)<1e-12);
assert.ok(Math.abs(normalized(eighth.left)[0]-Math.SQRT1_2)<1e-12);
assert.ok(Math.abs(axes(72).left[0]-initial.left[0])<1e-12);
const s=viz.transportGyroscopicPhase72(0,220,1,440,2,1);
const t=viz.transportGyroscopicPhase72(0,220,1,440,2,4);
assert.ok(t>s,"missed output frames must be transported");
assert.ok(axes(s).left[0]!==axes(t).left[0],"rotor changes physical pixel axes");
const low=new Float32Array(735);
for(let i=0;i<735;i++)low[i]=Math.sin(2*Math.PI*60*i/44100)*.45;
const fallback=viz.spectralFallbackHz(low);
assert.ok(fallback>=59&&fallback<=61,"one-cycle tone should rotate");
assert.equal(viz.spectralFallbackHz(new Float32Array(735)),0);
const shapes=[];
const ctx={globalCompositeOperation:"source-over",
 createLinearGradient(...points){
   const g={points,stops:[],addColorStop(t,c){this.stops.push([t,c])}};
   shapes.push(g);return g;
 },
 fillRect(x,y,w,h){assert.deepStrictEqual([x,y,w,h],[0,0,900,600])}
};
for(const p of [0,9,18]){
 shapes.length=0;
 const pair=viz.paintGyroscopicVerticalPair(ctx,900,600,.3,-.6,.25,.2,p);
 assert.ok(pair.oppositeHuePairs);
 assert.equal(shapes.length,2);
 assert.equal(shapes[0].stops.length,6);
 assert.equal(shapes[1].stops.length,6);
 const dx=shapes[0].points[2]-shapes[0].points[0],
  dy=shapes[0].points[3]-shapes[0].points[1];
 const ex=shapes[1].points[2]-shapes[1].points[0],
  ey=shapes[1].points[3]-shapes[1].points[1];
 assert.ok(Math.abs(dx*ex+dy*ey)<1e-6);
 assert.equal(ctx.globalCompositeOperation,"source-over");
}
for(const theta of [0,9,18,27]){
 const bands=[];
 const fake={
  beginPath(){},moveTo(){},lineTo(){},closePath(){},fill(){},
  createLinearGradient(...args){bands.push(args);return {addColorStop(){}}}
 };
 const left=viz.paintGyroscopicLightBand(fake,900,600,theta,0,0,50,12,.3);
 const right=viz.paintGyroscopicLightBand(fake,900,600,theta,1,0,50,83,.3);
 assert.equal(bands.length,2);
 const a=bands[0],b=bands[1];
 assert.ok(Math.abs((a[2]-a[0])*(b[2]-b[0])+
   (a[3]-a[1])*(b[3]-b[1]))<1e-8);
 assert.ok(Math.abs(left.normal[0]*right.normal[0]+
   left.normal[1]*right.normal[1])<1e-12);
}
assert.equal(viz.diagnostics.allLightBandsRotatingWithGyro,true);
assert.equal(viz.diagnostics.visualGradientAxesOrthogonal,true);
assert.equal(viz.diagnostics.canonicalMutation,false);
"""
    result=subprocess.run([node,"-e",code],text=True,capture_output=True)
    assert result.returncode==0,result.stdout+"\n"+result.stderr
