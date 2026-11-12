"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const root=path.resolve(__dirname,"../..");
const source=fs.readFileSync(path.join(root,
  "applications/runtime_os/HHS_Alpha_V150_Decay_Pool_Observation.html"),"utf8");
const marker="    /* V150 additive observation of the EXISTING physical decay producer.";
const start=source.indexOf(marker),end=source.indexOf("    function dtFrame()",start);
assert.ok(start>0&&end>start);
const fragment=source.slice(start,end);
const scope={};
scope.window=scope;
vm.runInNewContext(
  "const respawnRing=[0,0,0,0];let respawnRingIdx=2;const CONSTRUCTOR_CYCLE=4;"+
  "let respawnTotal=6;let decayCount=11;let couplingCount=3;"+
  "let activeCohort=1;let cohortCount=2;const particles=[0,1,2,3];"+
  "const fractalSeeds=[{serial:1,pairing:'(x,y):(z,w)',layerA:1,layerB:2,sealedAtCoupling:72}];"+
  "respawnRing[0]=4;respawnRing[1]=5;respawnRing[2]=2;respawnRing[3]=3;"+
  fragment,scope);
const api=scope.HHSV150DecayPoolObservation;
assert.ok(Object.isFrozen(api));
const first=api.read();
assert.equal(first.schema,"HHS_V150_LOCAL_DECAY_POOL_OBSERVATION_V1");
assert.equal(first.respawnCapacity,4);
assert.equal(first.respawnTotal,6);
assert.deepEqual([...first.recentRespawns],[2,3,4,5]);
assert.equal(first.decayCount,11);
assert.equal(first.couplingCount,3);
assert.equal(first.activeCohort,1);
assert.equal(first.cohortCount,2);
assert.equal(first.nativeVM81Admission,false);
assert.equal(first.authoritativeNativeDecayMatrix,false);
assert.equal(first.physicsMutationAuthority,false);
assert.equal(first.rendererClockAuthority,false);
assert.ok(Object.isFrozen(first));
assert.ok(Object.isFrozen(first.recentRespawns));
assert.ok(Object.isFrozen(first.fractalSeeds));
assert.ok(Object.isFrozen(first.fractalSeeds[0]));
assert.throws(()=>first.recentRespawns.push(8),TypeError);
assert.equal(api.read().respawnTotal,6);
console.log("PASS: V150 existing decay ring read-only provenance and chronological ordering");
