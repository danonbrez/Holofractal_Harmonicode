"""Per-particle centered halo shader and global reciprocal phase-lock regression."""
from pathlib import Path
import re
import shutil
import subprocess
import pytest
H=Path("examples/ParticleSimulation.html")
JS=Path("examples/ParticleSimulationAudioBridge.js")

def test_batch_halo_is_gpu_instanced_centered_and_noncanonical():
    html=H.read_text(encoding="utf8")
    bridge=JS.read_text(encoding="utf8")
    inline=re.search(r'<script id="hhsAudioInline">\s*([\s\S]*?)\s*</script>',html)
    assert inline and inline.group(1).strip()==bridge.strip()
    for token in (
        "function createParticleHaloBatch(group,mesh,count)",
        "new THREE.ShaderMaterial({",
        "new THREE.InstancedMesh(geometry,material,count)",
        "halo.instanceMatrix=mesh.instanceMatrix;",
        'halo.mesh.geometry.setAttribute("haloColor",mesh.instanceColor);',
        '"attribute vec3 haloColor;"',
        "halo.glowStrength.array[i]=glowEnabled?",
        "audioVisual.projectParticleGlow(p):0;",
        "halo.mesh.visible=glowEnabled;",
        "float radius=length((vUvHalo-0.5)*2.0);",
        "float fade=1.0-smoothstep(0.0,1.0,radius);",
        "float opacity=fade*fade*vStrengthHalo;",
        "gl_FragColor=vec4(vColorHalo,opacity);",
        "physicsFeedbackEnabled:false,vm81Admission:false",
    ):
        assert token in html,token
    assert '"attribute vec3 instanceColor;"' not in html
    assert "HALO_EMISSION_GAIN=0.16" in bridge
    assert "return clamp(HALO_EMISSION_GAIN*" in bridge
    assert "return clamp(state.gain*" not in bridge
    assert "scene.background=texture;" in html
    assert '" center.z-=0.035*size;"' in html
    assert "distanceDamp=1.0/(1.0+0.028*vHaloDistance*vHaloDistance)" in html
    assert "THREE.AdditiveBlending" in html
    assert "transparent:true,depthTest:true,depthWrite:false" in html
    assert "mesh.setMatrixAt(i,particleBatchMatrix);" in html
    assert "for(let s=0;s<steps;s++){ updateSpiralParticles();" in html
    assert "updateSwarmCoupling(" not in bridge
    assert "canonicalMutation:false" in bridge
    assert "p.position." not in bridge

def test_center_opacity_monotonic_phase_lock_and_per_bus_address():
    node=shutil.which("node")
    if not node:pytest.skip("Node.js missing")
    code=r"""
const fs=require("fs"),vm=require("vm"),assert=require("assert");
const bridge=fs.readFileSync("examples/ParticleSimulationAudioBridge.js","utf8");
const window={},document={readyState:"loading",addEventListener(){}};
vm.runInNewContext(bridge,{window,document,
 Float32Array,WeakMap,Array,Math,Number,Object,isFinite});
const a=window.HHSAudioViz;
for(const peak of [.2,.45,.75]){
 const ys=[0,.1,.25,.5,.75,1,1.2].map(r=>a.particleHaloOpacity(r,peak));
 assert.ok(Math.abs(ys[0]-peak)<1e-12,"center alpha must peak");
 assert.equal(ys[ys.length-1],0,"boundary completely transparent");
 for(let i=1;i<ys.length;i++)assert.ok(ys[i]<=ys[i-1]+1e-12);
}
assert.equal(a.particleHaloOpacity(.5,.8),.2);
assert.equal(a.particleHaloOpacity(-1,.6),.6);
const p=a.verticalReciprocalGradientPair(18,.3,.3,.2,.2);
assert.equal(p.oppositeHuePairs,true);
const q=a.q144Index(2*18+0,.3,.2,0,0);
assert.equal(p.leftHues[0],q);
assert.equal(a.q144Index(2*18,.3,.2,0,1),(q+72)%144);
assert.equal(a.diagnostics.geometryNormalizationGainMax,.05);
assert.equal(a.diagnostics.haloEmissionGain,.4);
const l=a.particleLayer5184(0,18),r=a.particleLayer5184(5184,18);
assert.equal(l.layer,0);assert.equal(r.layer,1);
assert.equal(l.address,0);assert.equal(r.address,0);
assert.equal(r.phase72,36);
assert.equal(a.particleLayer5184(10367,18).address,5183);
assert.equal(a.particleLayer5184(10368,18),null);
assert.ok(a.lightAttenuation(.5,100,0)>a.lightAttenuation(.5,1000,0));
assert.ok(a.lightAttenuation(.5,100,0)>a.lightAttenuation(.5,100,1));
assert.ok(a.lightAttenuation(.8,100,0)>a.lightAttenuation(.1,100,0));
assert.ok(a.lightAttenuation(1,0,0)<=.045);
assert.equal(a.lightAttenuation(0,100,0),0);
assert.equal(a.diagnostics.backLightLayerCells,5184);
assert.equal(a.diagnostics.backLightLayerCount,2);
assert.equal(a.diagnostics.backLightOpacityCap,.045);
assert.equal(a.diagnostics.particleHalosPhaseLocked,true);
assert.equal(a.diagnostics.allLightBandsRotatingWithGyro,true);
assert.equal(a.diagnostics.canonicalMutation,false);
"""
    result=subprocess.run([node,"-e",code],capture_output=True,text=True)
    assert result.returncode==0,result.stdout+"\n"+result.stderr
