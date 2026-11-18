import assert from "node:assert/strict";
import {translateHash72Graph,Hash72OrbitReader,leeDistance4} from "../examples/harmonicode_module194_graph_reader.mjs";

function fixture(tick=1n){
  const coordinates=new Uint8Array(10368*4),addresses=new Uint32Array(10368);
  for(let i=0;i<10368;i++){
    const x=i<5184?0:71,y=i<5184?0:71,z=i<5184?0:71,w=i<5184?0:71;
    coordinates.set([x,y,z,w],i*4);
    addresses[i]=x+72*y+5184*z+373248*w;
  }
  return {status:"OBSERVED",admitted:false,particleCount:10368,
    coordinates,addresses,physicsTick:tick,complementVerified:true};
}
const f=fixture();
assert.equal(leeDistance4(f,0,1),0);
assert.equal(leeDistance4(f,0,5184),4);
const graph=translateHash72Graph(f,{leeThreshold:0});
assert.equal(graph.vertexCount,5184);
assert.equal(graph.edgeCount,5184*5183/2);
assert.equal(graph.signatures.length,graph.edgeCount);
assert.deepEqual(graph.edges[0].weight,{numerator:1001n,denominator:1000n});
assert.equal(graph.admitted,false);
const orbit=new Hash72OrbitReader();
const initial=orbit.record(f,graph);
assert.equal(initial.novelCount,graph.edgeCount);
assert.deepEqual(initial.noveltyDensity,{numerator:1n,denominator:1n});
assert.deepEqual(orbit.probability(0),{numerator:1n,denominator:2n});
assert.deepEqual(orbit.probability(5183),{numerator:1n,denominator:2n});
assert.throws(()=>orbit.record(f,graph),/NONMONOTONE/);
const f2=fixture(2n),g2=translateHash72Graph(f2,{leeThreshold:0});
assert.equal(orbit.record(f2,g2).novelCount,0);
assert.deepEqual(orbit.probability(0),{numerator:1n,denominator:2n});
assert.throws(()=>translateHash72Graph({...f,status:"RETRY_NONATOMIC_OBSERVATION"}),/UNTRUSTED/);
assert.throws(()=>translateHash72Graph(f,{leeThreshold:-1}),/THRESHOLD/);
console.log("HHS Module194 Hash72 graph and exact probability tests passed");
