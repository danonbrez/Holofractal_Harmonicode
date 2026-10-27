"""Pass 220 coupled group projection is bijective and presentation only."""
from pathlib import Path
import re, shutil, subprocess
ROOT=Path(__file__).resolve().parents[2]

def test_coupled_group_address_projection():
    html=(ROOT/"examples/ParticleSimulation.html").read_text(encoding="utf8")
    assert 'id="hhsCoupledTensorPanel"' in html
    assert re.search(r'<script id="hhsCoupledTensorInline">([\s\S]*?)</script>',html)
    assert shutil.which("node")
    script=r"""
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const html=fs.readFileSync('examples/ParticleSimulation.html','utf8');
const match=html.match(/<script id="hhsCoupledTensorInline">([\s\S]*?)<\/script>/);
assert.ok(match);
const window={};
const document={readyState:'loading',addEventListener(){}};
vm.runInNewContext(match[1],{window,document,Object,Array,Math,Number,Error});
const m=window.HHSCoupledTensorProjection,d=m.audit();
assert.equal(d.count,10368);
assert.equal(d.perPopulation,5184);
assert.equal(d.hnanMappedPositions,1152);
assert.equal(d.spinRelationshipResidue,2754);
assert.equal(d.quantumEpsilon,289);
assert.equal(d.nativePhysicsMutation,false);
assert.equal(d.orthogonalityProofClaimed,false);
assert.equal(d.massQuantizationProofClaimed,false);
for(let i=0;i<10368;i++){
 const a=m.address(i),b=m.address(m.reciprocal(i));
 assert.equal(a.index,i);
 assert.equal(m.reciprocal(m.reciprocal(i)),i);
 assert.equal(a.constraint,b.constraint);
 assert.equal(a.scale,b.scale);
 assert.equal(a.phase,b.phase);
 assert.notEqual(a.spinor,b.spinor);
 const x=m.bias(i,4),y=m.bias(m.reciprocal(i),4);
 assert.equal((x.hue144+72)%144,y.hue144);
}
assert.equal(m.address(-1),null);
assert.equal(m.address(10368),null);
assert.equal(m.bias(-1),null);
"""
    subprocess.run(["node","-e",script],cwd=ROOT,check=True,timeout=30)
