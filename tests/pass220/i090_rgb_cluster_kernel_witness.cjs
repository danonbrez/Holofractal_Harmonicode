"use strict";
const fs=require("node:fs");
const vm=require("node:vm");
const assert=require("node:assert/strict");
const src=fs.readFileSync("examples/ParticleSimulation.html","utf8");
const begin=src.indexOf("const RGB_PARTITION = Object.freeze({");
const end=src.indexOf("function rgbPartitionReceipt(){",begin);
assert(begin>=0&&end>begin,"actual embedded kernel not found");
assert(src.includes("const rgbActive=simParams.rgbClusterOn && simParams.rgbClusterStrength>0"),"opt-in guard lost");
assert(src.includes("if(rgbActive){"),"force guard lost");
const context=vm.createContext({
  THREE:{Color:class Color{constructor(r,g,b){this.r=r;this.g=g;this.b=b}}},
  Float64Array,Math,
});
const expose='\n globalThis.inspect=function(pos,mass,n){ const admitted=rgbPrepare(pos,mass,n); return {admitted,means:Array.from(rgbMeans),targets:Array.from(rgbTargets),correction:Array.from(rgbCorrection),matrix:RGB_PARTITION.matrix}; };';
vm.runInContext(src.slice(begin,end)+expose,context);
const N=10368,mass=new Float64Array(N),pos=new Float64Array(N*3);
for(let i=0;i<N;i++){
  const q=Math.floor(i/2592);mass[i]=1+q/5;
  pos[3*i]=10*q;pos[3*i+1]=2*q;pos[3*i+2]=-3*q;
}
const base=context.inspect(pos,mass,N);
assert(base.admitted);
const matrix=[[8,4,4,0],[4,14,9,19],[4,9,13,18],[4,15,14,25]];
for(const row of matrix)assert.equal(row.reduce((a,v,j)=>a+v*[1,-1,-1,1][j],0),0);
const eq=(x,y,tol=1e-8)=>assert(Math.abs(x-y)<tol,"expected "+x+" ~= "+y);
for(let q=0;q<4;q++)for(let axis=0;axis<3;axis++){
  const sum=matrix[q].reduce((a,v)=>a+v,0);
  const target=matrix[q].reduce((a,v,p)=>a+v*base.means[3*p+axis],0)/sum;
  eq(base.targets[3*q+axis],target);
}
const translation=[100,-65,28],moved=pos.slice();
for(let i=0;i<N;i++)for(let a=0;a<3;a++)moved[i*3+a]+=translation[a];
const shifted=context.inspect(moved,mass,N);
assert(shifted.admitted);
for(let q=0;q<4;q++)for(let a=0;a<3;a++){
  eq(shifted.means[q*3+a]-base.means[q*3+a],translation[a]);
  eq(shifted.targets[q*3+a]-base.targets[q*3+a],translation[a]);
}
for(let a=0;a<3;a++)eq(shifted.correction[a],base.correction[a]);
const sumForce=[0,0,0];let totalMass=0,nonZero=0;
for(let i=0;i<N;i++){
  const q=Math.floor(i/2592),m=mass[i];totalMass+=m;
  for(let a=0;a<3;a++){
    const f=base.targets[3*q+a]-pos[3*i+a]-base.correction[a];
    sumForce[a]+=m*f;if(Math.abs(f)>1e-10)nonZero++;
  }
}
assert(nonZero>0,"cluster force must be nonzero for separated quadrants");
for(const f of sumForce)eq(f/totalMass,0);
assert(!context.inspect(pos,mass,N-1).admitted,"wrong particle count must reject");
console.log(JSON.stringify({
 schema:"HHS_PASS220_I090_RGB_PARTITION_KERNEL_NODE_WITNESS_V1",
 status:"PASS",particles:N,quadrants:4,first_target_x:base.targets[0],
 mean_force:sumForce.map(x=>x/totalMass),translation_invariant:true,
 wrong_count_rejected:true,canonical_vm81_admission:false,hash72_append:false
}));
