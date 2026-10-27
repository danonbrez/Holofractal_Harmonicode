"""Check that particle physics metadata is observed, not synthesized from layout."""
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "examples" / "ParticleSimulationAudioBridge.js"


def test_inherited_physical_metadata_projection():
    source = SOURCE.read_text(encoding="utf-8")
    assert "particlePhysicalProjection(p)" in source
    assert "chargeFromAddress:false" in source
    assert "normalizedKineticEnergy" in source
    assert "const physical=particlePhysicalProjection(p);" in source
    assert "particlePhysicalProjection,peakEnvelope" in source
    match = re.search(
        r"(  function particlePhysicalProjection\(p\)\{[\s\S]*?\n  \})\n  function projectColor",
        source,
    )
    assert match, "physics projection must remain inside the live color module"
    node = shutil.which("node")
    assert node, "Node required for executable projection regression"
    script = r"""
const assert=require('node:assert/strict');
const state={particleIndex:new WeakMap()};
""" + match.group(1) + r"""
const a={position:{x:1,y:2,z:3},userData:{}};
const b={position:{x:4,y:5,z:6},userData:{
  hhsPhysicalState:{charge:-2,mass:4,normalizedKineticEnergy:3}}};
state.particleIndex.set(a,0);
state.particleIndex.set(b,5184);
const pa=particlePhysicalProjection(a),pb=particlePhysicalProjection(b);
assert.equal(pa.charge,null);
assert.equal(pa.mass,null);
assert.equal(pa.source,'unavailable');
assert.equal(pb.charge,-2);
assert.equal(pb.mass,4);
assert.equal(pb.kineticEnergy,3);
assert.equal(pb.reciprocalIndex,0);
assert.equal(pb.physicsMutation,false);
assert.equal(pb.chargeFromAddress,false);
assert.equal(particlePhysicalProjection({userData:{}}),null);
assert.equal(pa.position[0],1);
assert.equal(pb.position[0],4);
"""
    subprocess.run([node, "-e", script], cwd=ROOT, check=True, timeout=30)

def test_coupled_particle_frame_uses_one_population_and_pcm_phase():
    source = SOURCE.read_text(encoding="utf-8")
    assert "function coupledParticleFrame(index,frame=state.lastFrame)" in source
    assert "coupledParticleFrame,peakEnvelope" in source
    fn = re.search(r"(  function coupledParticleFrame\\(index,frame=state.lastFrame\\)\\{[\\s\\S]*?\\n  \\})\\n  function projectColor",source)
    assert fn
    program = """
const assert=require('node:assert/strict');
const state={particles:[],lastFrame:0};
const particlePhysicalProjection=(p)=>p.record;
""" + fn.group(1) + """
for(let n=0;n<10368;n++){
 const a=coupledParticleFrame(n,3);
 assert.equal(a.index,n);
 assert.equal(a.constraint,Math.floor((n%5184)/648));
 assert.equal(a.fractalScale,Math.floor((n%648)/72));
 assert.equal(a.ionicLayer,a.fractalScale-4);
 assert.equal(a.phase72,((n%72)+54)%72);
 assert.equal(coupledParticleFrame(a.reciprocalIndex,3).reciprocalIndex,n);
}
const p={record:{position:[1,2,3],charge:2,mass:5,kineticEnergy:1,source:'inherited'}};
state.particles[0]=p;
assert.equal(coupledParticleFrame(0,0).mass,5);
assert.equal(coupledParticleFrame(0,0).charge,2);
assert.equal(coupledParticleFrame(1,0).charge,null);
assert.equal(coupledParticleFrame(-1,0),null);
"""
    subprocess.run([shutil.which("node"),"-e",program],cwd=ROOT,check=True,timeout=30)
