"""Fourier-17 phase-basis invariants and particle-population guard."""
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[2]

def test_fourier17_unitary_quadrature_and_cycle():
    assert shutil.which("node")
    code=r"""
const fs=require('fs'),assert=require('assert'),vm=require('vm');
const source=fs.readFileSync('examples/HHSFourier17.js','utf8');
const sandbox={window:{}};vm.runInNewContext(source,sandbox);
const m=sandbox.window.HHSFourier17,eps=1e-10;
assert.equal(m.size,17);assert.equal(m.relationshipSlots,289);
assert.equal(m.physicsMutation,false);
const close=(a,b)=>Math.abs(a-b)<eps;
for(let j=0;j<17;j++)for(let k=0;k<17;k++){
 let re=0,im=0;
 for(let n=0;n<17;n++){
  const [ar,ai]=m.basis[j][n],[br,bi]=m.basis[k][n];
  re+=ar*br+ai*bi;im+=ai*br-ar*bi;
 }
 assert(close(re,j===k?1:0)&&close(im,0));
}
const input=Array.from({length:17},(_,k)=>[k===3?1:0,0]);
const basis=m.transform(input),back=m.transform(basis,true);
for(let k=0;k<17;k++){assert(close(back[k][0],input[k][0]));assert(close(back[k][1],0));}
const quarter=m.quarterTurn(basis);
for(let k=0;k<17;k++) {
 assert(close(quarter[k][0],-basis[k][1]));
 assert(close(quarter[k][1],basis[k][0]));
}
const cycle=m.rotateParticleBasis(input,17);
for(let k=0;k<17;k++){
 assert(close(cycle[k][0],input[k][0]));
 assert(close(cycle[k][1],input[k][1]));
}
for(let j=0;j<17;j++)for(let k=0;k<17;k++){
 const a=m.reciprocalSlot(j,k),b=m.reciprocalSlot(k,j,1);
 assert.equal(a.slot,b.slot);assert.equal(a.physicalParticle,false);
}
"""
    subprocess.run(["node","-e",code],cwd=ROOT,check=True,timeout=30)
