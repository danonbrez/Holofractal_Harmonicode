"""HHS quantum-epsilon visualization cardinality and nonmutation contract."""
from pathlib import Path
import re
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[2]

def test_qepsilon_projection_is_distinct_from_particle_population():
    source=(ROOT/"examples/ParticleSimulation.html").read_text(encoding="utf-8")
    match=re.search(r'<script id="hhsQuantumEpsilonInline">([\s\S]*?)</script>',source)
    assert match
    script=match.group(1)
    assert 'PARTICLE_TOTAL=10368' in script
    assert 'SPIN_STATES=17' in script
    assert 'EPSILON_POSITIONS=SPIN_STATES*SPIN_STATES' in script
    assert 'nativePhysicsMutation:false' in script
    assert 'claimedOrthogonalityValidated:false' in script
    assert 'hhsQuantumEpsilonPanel' in source
    assert shutil.which("node")
    js=r"""
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('examples/ParticleSimulation.html','utf8');
const match=source.match(/<script id="hhsQuantumEpsilonInline">([\s\S]*?)<\/script>/);
assert.ok(match);
const window={};
const document={readyState:'loading',addEventListener(){}};
vm.runInNewContext(match[1],{window,document,Number,Object,Math,Error});
const layer=window.HHSQuantumEpsilon;
const d=layer.diagnostics();
assert.equal(d.particles,10368);
assert.equal(d.layeredCardinality,13122);
assert.equal(d.differenceResidue,2754);
assert.equal(d.spinRelationPositions,289);
assert.equal(d.spinParticleIdentities,17);
assert.equal(d.nativePhysicsMutation,false);
assert.equal(d.claimedOrthogonalityValidated,false);
for(let i=0;i<10368;i++){
 const address=layer.particleAddress(i);
 assert.equal(address.index,i);
 assert.ok(address.cell>=0&&address.cell<81);
 assert.ok(address.coordinate>=0&&address.coordinate<64);
 assert.equal(layer.reciprocalIndex(layer.reciprocalIndex(i)),i);
}
for(let i=0;i<17;i++)for(let j=0;j<17;j++){
 const a=layer.spinAddress(0,i,j),b=layer.spinAddress(1,j,i);
 assert.equal(a.address,b.address);
 assert.equal(a.physicalParticle,false);
}
assert.equal(layer.spinAddress(0,17,0),null);
assert.equal(layer.particleAddress(10368),null);
"""
    subprocess.run(["node","-e",js],check=True,cwd=ROOT,timeout=30)
