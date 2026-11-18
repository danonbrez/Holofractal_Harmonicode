import assert from "node:assert/strict";
import {translateHash72Graph,Hash72OrbitReader,leeDistance4} from "../examples/harmonicode_module194_graph_reader.mjs";

function fixture(tick=1n){
  const coordinates=new Uint8Array(10368*4),addresses=new Uint32Array(10368);
  for(let i=0;i<5184;i++){
    // Unique primary addresses except the deliberately coincident first pair.
    const k=i===1?0:i;
    const x=k%72,y=Math.floor(k/72);
    for(const [id,a,b,c,d] of [[i,x,y,0,0],[i+5184,71-x,71-y,71,71]]){
      coordinates.set([a,b,c,d],id*4);
      addresses[id]=a+72*b+5184*c+373248*d;
    }
  }
  return {status:"OBSERVED",admitted:false,particleCount:10368,
    coordinates,addresses,physicsTick:tick,complementVerified:true};
}
const f=fixture();
assert.equal(leeDistance4(f,0,1),0);
assert.equal(leeDistance4(f,0,5184),4); // x,y complement distance zero->71 each =1; z,w 0->71 =1
const graph=translateHash72Graph(f,{leeThreshold:0});
assert.equal(graph.vertexCount,5184);
assert.equal(graph.edgeCount,1);
assert.equal(graph.signatures.length,1);
assert.deepEqual(graph.edges[0].weight,{numerator:1001n,denominator:1000n});
assert.equal(graph.admitted,false);
const orbit=new Hash72OrbitReader();
const initial=orbit.record(f,graph);
assert.equal(initial.novelCount,1);
assert.deepEqual(initial.noveltyDensity,{numerator:1n,denominator:1n});
assert.deepEqual(orbit.probability(0),{numerator:1n,denominator:5184n});
assert.deepEqual(orbit.probability(5183),{numerator:1n,denominator:5184n});
assert.throws(()=>orbit.record(f,graph),/NONMONOTONE/);
const f2=fixture(2n),g2=translateHash72Graph(f2,{leeThreshold:0});
assert.equal(orbit.record(f2,g2).novelCount,0);
assert.deepEqual(orbit.probability(0),{numerator:1n,denominator:5184n});
assert.throws(()=>translateHash72Graph({...f,status:"RETRY_NONATOMIC_OBSERVATION"}),/UNTRUSTED/);
assert.throws(()=>translateHash72Graph(f,{leeThreshold:-1}),/THRESHOLD/);
console.log("HHS Module194 Hash72 graph and exact probability tests passed");
