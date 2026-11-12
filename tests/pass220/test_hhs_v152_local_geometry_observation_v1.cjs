"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const root=path.resolve(__dirname,"../..");
const source=fs.readFileSync(path.join(root,
  "applications/runtime_os/HHS_Alpha_V152_Ordered_Physical_Geometry_Observation.html"),"utf8");
const begin="    /* V152: read-only ordered particle geometry export from EXISTING thPos.";
const start=source.indexOf(begin),end=source.indexOf("    const tHead=",start);
assert.ok(start>0&&end>start);
const fragment=source.slice(start,end);
const scope={};scope.window=scope;
vm.runInNewContext(
  "let thPos=new Float32Array([1.5,-2.25,3,0,4,5]);"+
  "const particles=[{},{}];let physicsTicks=12;"+
  fragment,scope
);
const api=scope.HHSV152GeometryObservation;
assert.ok(Object.isFrozen(api));
const sample=api.read();
assert.equal(sample.schema,"HHS_V152_LOCAL_GEOMETRY_OBSERVATION_V1");
assert.equal(sample.source,"V147_EXISTING_TH_POS_PHYSICS_PARTICLE_ARRAY");
assert.equal(sample.particleCount,2);
assert.equal(sample.physicsTick,12);
assert.equal(sample.byteLength,24);
assert.equal(sample.componentsPerParticle,3);
assert.equal(sample.serialization,"ORDERED_FLOAT32_LE_XYZ");
assert.equal(sample.nativeVM81Admission,false);
assert.equal(sample.nativeHash216Proof,false);
assert.equal(sample.physicsMutationAuthority,false);
assert.equal(sample.renderSchedulingAuthority,false);
const first=sample.copyPositionBytes();
assert.equal(first.length,24);
const view=new DataView(first.buffer);
assert.deepEqual(Array.from({length:6},(_,i)=>view.getFloat32(i*4,true)),[1.5,-2.25,3,0,4,5]);
first[0]^=255;
const second=sample.copyPositionBytes();
assert.notEqual(first[0],second[0]);
assert.ok(Object.isFrozen(sample));
assert.ok(Object.isFrozen(api));
console.log("PASS: V152 physical Float32LE read-only geometry, tick provenance and copy isolation");
