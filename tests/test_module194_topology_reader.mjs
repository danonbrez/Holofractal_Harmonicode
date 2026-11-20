import assert from "node:assert/strict";
import {extractHash72Topology,Hash72TopologyOrbit}
  from "../examples/harmonicode_module194_topology_reader.mjs";

function g(tick=7n,edges=[]){
  return {status:"TRANSLATED",admitted:false,sourceTick:tick,
    vertexCount:5184,edgeCount:edges.length,edges};
}
const edge=(a,b,phaseRatio="1:1")=>({
  source:a,target:b,phaseRatio,dLee:0,
  weight:{numerator:1001n,denominator:1000n}
});
const sample=g(7n,[edge(0,1),edge(0,2),edge(1,2),edge(4,5,"2:1")]);
const t=extractHash72Topology(sample);
assert.equal(t.status,"TOPOLOGY_EXTRACTED");
assert.equal(t.connectedComponentCount,5181); // {0,1,2}, {4,5}, plus 5179 isolates
assert.equal(t.phaseLockedTriangleCount,1);
assert.equal(t.triangleSignatures[0],"T:0,1,2@1:1|1:1|1:1");
assert(t.componentSignatures.includes("C:0,1,2"));
assert(t.componentSignatures.includes("C:4,5"));
assert.equal(t.admitted,false);
const orbit=new Hash72TopologyOrbit();
const r1=orbit.record(t);
assert.equal(r1.observedRecurrencePeriod,null);
assert.equal(r1.minimalOrbitPeriodVerified,false);
const t2=extractHash72Topology(g(11n,sample.edges));
const r2=orbit.record(t2);
assert.equal(r2.observedRecurrencePeriod,4n);
assert.equal(r2.novelStructuralCount,0);
assert.throws(()=>orbit.record(t2),/NONMONOTONE/);
assert.throws(()=>extractHash72Topology(g(12n,[edge(0,1),edge(0,1)])),/DUPLICATE_EDGE/);
assert.throws(()=>extractHash72Topology(g(12n,[edge(1,1)])),/EDGE_INVALID/);
assert.throws(()=>extractHash72Topology({...sample,edgeCount:0}),/EDGE_COUNT/);
assert.throws(()=>extractHash72Topology({...sample,status:"HNAN_TRAP"}),/INVALID_GRAPH/);
console.log("Module194 topology signatures and recurrence tests passed");
