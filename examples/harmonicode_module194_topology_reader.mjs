/**
 * Deterministic topology signatures for Module194 Hash72^2 observations.
 * Candidate-only/read-only: components, phase-locked triangles, orbit recurrences.
 * No physics ticks, VM81 admission, or phase registers are modified.
 */
const PAIRS=5184;
const SAFE_ID=i=>Number.isInteger(i)&&i>=0&&i<PAIRS;
function assertGraph(g){
  if(!g||g.status!=="TRANSLATED"||g.admitted!==false||
     g.vertexCount!==PAIRS||!Array.isArray(g.edges)||
     typeof g.sourceTick!=="bigint"||g.sourceTick<0n)
    throw Error("HHS_TOPOLOGY_INVALID_GRAPH");
}
function edgeIdentity(e){
  if(!SAFE_ID(e.source)||!SAFE_ID(e.target)||e.source>=e.target||
     typeof e.phaseRatio!=="string"||!["1:1","2:1","3:2","4:3"].includes(e.phaseRatio)||
     !Number.isInteger(e.dLee)||e.dLee<0||e.dLee>144)
    throw Error("HHS_TOPOLOGY_EDGE_INVALID");
  return e.source+">"+e.target+"@"+e.phaseRatio+":"+e.dLee;
}
export function extractHash72Topology(graph) {
  assertGraph(graph);
  const adj=Array.from({length:PAIRS},()=>new Set());
  const identities=new Map(),edgeByPair=new Map();
  for(const e of graph.edges){
    const id=edgeIdentity(e);
    if(identities.has(id)||adj[e.source].has(e.target))
      throw Error("HHS_TOPOLOGY_DUPLICATE_EDGE");
    identities.set(id,e);edgeByPair.set(e.source+":"+e.target,e);
    adj[e.source].add(e.target);adj[e.target].add(e.source);
  }
  if(graph.edgeCount!==graph.edges.length)
    throw Error("HHS_TOPOLOGY_EDGE_COUNT");
  const visited=new Uint8Array(PAIRS),components=[];
  for(let root=0;root<PAIRS;root++){
    if(visited[root])continue;
    const stack=[root],members=[];visited[root]=1;
    while(stack.length){
      const i=stack.pop();members.push(i);
      for(const j of adj[i])if(!visited[j]){visited[j]=1;stack.push(j);}
    }
    members.sort((a,b)=>a-b);
    components.push("C:"+members.join(","));
  }
  // A 3-clique contains every edge among three distinct pair identities.
  // Intersect sorted adjacency lists, visiting each triangle exactly once.
  const neighbors=adj.map(s=>[...s].sort((a,b)=>a-b));
  const triangles=[];
  for(let i=0;i<PAIRS;i++){
    for(const j of neighbors[i]){
      if(j<=i)continue;
      for(const k of neighbors[i]){
        if(k<=j)continue;
        if(!adj[j].has(k))continue;
        const e1=edgeByPair.get(i+":"+j);
        const e2=edgeByPair.get(i+":"+k);
        const e3=edgeByPair.get(j+":"+k);
        triangles.push("T:"+i+","+j+","+k+"@"+
          [e1.phaseRatio,e2.phaseRatio,e3.phaseRatio].join("|"));
      }
    }
  }
  triangles.sort();
  const edgeSignatures=[...identities.keys()].sort();
  const structuralSignatures=Object.freeze([...components,...triangles].sort());
  // Length-framed composition avoids ambiguous concatenation of signatures.
  const fullFingerprint=JSON.stringify([edgeSignatures,structuralSignatures]);
  return Object.freeze({
    status:"TOPOLOGY_EXTRACTED",admitted:false,sourceTick:graph.sourceTick,
    connectedComponentCount:components.length,phaseLockedTriangleCount:triangles.length,
    componentSignatures:Object.freeze(components),
    triangleSignatures:Object.freeze(triangles),
    structuralSignatures,fullFingerprint,nativeAdmissionVerified:false
  });
}
export class Hash72TopologyOrbit {
  #lastTick=null;#firstSeen=new Map();#seenStructure=new Set();
  record(topology){
    if(topology?.status!=="TOPOLOGY_EXTRACTED"||topology.admitted!==false||
       typeof topology.sourceTick!=="bigint")
      throw Error("HHS_TOPOLOGY_INVALID_OBSERVATION");
    const tick=topology.sourceTick;
    if(this.#lastTick!==null && tick<=this.#lastTick)
      throw Error("HHS_TOPOLOGY_NONMONOTONE_TICK");
    this.#lastTick=tick;
    let newStructures=0;
    for(const s of topology.structuralSignatures)
      if(!this.#seenStructure.has(s)){this.#seenStructure.add(s);newStructures++;}
    const previous=this.#firstSeen.get(topology.fullFingerprint);
    if(previous===undefined)this.#firstSeen.set(topology.fullFingerprint,tick);
    return Object.freeze({
      tick,novelStructuralCount:newStructures,
      cumulativeUniqueStructuralSignatures:this.#seenStructure.size,
      observedRecurrencePeriod:previous===undefined?null:tick-previous,
      firstSeenTick:previous??tick,
      // Equal observed signatures establish a recurrence interval only;
      // a minimal dynamical orbit period requires complete state evidence.
      minimalOrbitPeriodVerified:false,admitted:false
    });
  }
}
