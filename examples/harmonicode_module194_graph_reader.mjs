/**
 * HARMONICODE Hash72^2 read-only graph translator and finite-window orbit reader.
 * Source: sampleModule194Projection(). Not an authoritative VM81 admission gate.
 */
export const GRAPH_PAIRS=5184, GRAPH_PARTICLES=10368, GRAPH_MOD=72;
const RATIOS=Object.freeze([[1,1],[2,1],[3,2],[4,3]]);
const mod=n=>((n%GRAPH_MOD)+GRAPH_MOD)%GRAPH_MOD;
function assertFrame(frame){
  if(frame?.status!=="OBSERVED" || frame.admitted!==false ||
     frame.particleCount!==GRAPH_PARTICLES ||
     !(frame.coordinates instanceof Uint8Array) ||
     frame.coordinates.length!==GRAPH_PARTICLES*4 ||
     !(frame.addresses instanceof Uint32Array) ||
     frame.addresses.length!==GRAPH_PARTICLES ||
     typeof frame.physicsTick!=="bigint" || frame.physicsTick<0n)
    throw Error("HHS_GRAPH_INCOMPLETE_OR_UNTRUSTED_OBSERVATION");
}
function coord(frame,i,a){return frame.coordinates[4*i+a];}
export function leeDistance4(frame,i,j){
  let d=0;
  for(let k=0;k<4;k++){
    const diff=Math.abs(coord(frame,i,k)-coord(frame,j,k));
    d+=Math.min(diff,72-diff);
  }
  return d;
}
function phaseLock(a,b){
  for(const [p,q] of RATIOS)if(mod(p*a-q*b)===0)return [p,q];
  return null;
}
function gcd(a,b){while(b){const t=a%b;a=b;b=t;}return a;}
function weightFor(d){
  // (1001/1000) * (144-d)/144
  const n=1001n*BigInt(144-d),den=144000n;
  const g=gcd(n,den);
  return [n/g,den/g];
}
function keyOf(frame,i){return Array.from(frame.coordinates.subarray(i*4,i*4+4)).join(":");}
export function translateHash72Graph(frame,opts={}){
  assertFrame(frame);
  const threshold=opts.leeThreshold??12;
  if(!Number.isInteger(threshold)||threshold<0||threshold>144)
    throw RangeError("HHS_GRAPH_LEE_THRESHOLD");
  const vertices=new Array(GRAPH_PAIRS);
  const buckets=new Map(),sectorWidth=12,sectors=6;
  for(let i=0;i<GRAPH_PAIRS;i++){
    const x=coord(frame,i,0),y=coord(frame,i,1),z=coord(frame,i,2),w=coord(frame,i,3);
    const partner=i+GRAPH_PAIRS;
    const vertex={pairId:i,alpha:x+72*y,beta:z+72*w,
      primaryAddress:frame.addresses[i],reciprocalAddress:frame.addresses[partner],
      pairIntact:frame.addresses[i]+frame.addresses[partner]===26873855};
    vertices[i]=Object.freeze(vertex);
    const k=[x,y,z,w].map(v=>Math.floor(v/sectorWidth)).join(":");
    if(!buckets.has(k))buckets.set(k,[]);
    buckets.get(k).push(i);
  }
  const edges=[],signatures=new Set();
  // Each coordinate is 0..71. A threshold larger than 12 can span more
  // than adjacent sectors; search all sectors in that case (complete, slower).
  const searchRadius=Math.min(3,Math.ceil(threshold/sectorWidth)+1);
  for(let i=0;i<GRAPH_PAIRS;i++){
    const s=[0,1,2,3].map(a=>Math.floor(coord(frame,i,a)/sectorWidth));
    const scanned=new Set();
    for(let dx=-searchRadius;dx<=searchRadius;dx++)
    for(let dy=-searchRadius;dy<=searchRadius;dy++)
    for(let dz=-searchRadius;dz<=searchRadius;dz++)
    for(let dw=-searchRadius;dw<=searchRadius;dw++){
      const key=[dx,dy,dz,dw].map((v,a)=>((s[a]+v)%sectors+sectors)%sectors).join(":");
      if(scanned.has(key))continue;scanned.add(key);
      const bucket=buckets.get(key);if(!bucket)continue;
      for(const j of bucket){
        if(j<=i)continue;
        const d=leeDistance4(frame,i,j);if(d>threshold)continue;
        const ratio=phaseLock(coord(frame,i,3),coord(frame,j,3));
        if(!ratio)continue;
        const [numerator,denominator]=weightFor(d);
        edges.push(Object.freeze({source:i,target:j,dLee:d,phaseRatio:ratio.join(":"),
          weight:Object.freeze({numerator,denominator})}));
        // Pair identities are retained: equal positions are not equal vertices.
        signatures.add(i+">"+j+"@"+ratio.join(":")+":"+d);
      }
    }
  }
  const canonicalSignatures=Object.freeze([...signatures].sort());
  return Object.freeze({status:"TRANSLATED",admitted:false,
    sourceTick:frame.physicsTick,vertexCount:GRAPH_PAIRS,edgeCount:edges.length,
    vertices:Object.freeze(vertices),edges:Object.freeze(edges),
    signatures:canonicalSignatures,complementVerified:frame.complementVerified,
    nativeAdmissionVerified:false});
}
export class Hash72OrbitReader {
  #seen=new Set();#lastTick=null;#ticks=0n;#occupancy=new Map();
  record(frame,graph){
    assertFrame(frame);
    if(graph?.status!=="TRANSLATED"||graph.sourceTick!==frame.physicsTick)
      throw Error("HHS_GRAPH_TICK_MISMATCH");
    if(this.#lastTick!==null && frame.physicsTick<=this.#lastTick)
      throw Error("HHS_ORBIT_NONMONOTONE_TICK");
    this.#lastTick=frame.physicsTick;
    const novel=[];
    for(const s of graph.signatures)if(!this.#seen.has(s)){this.#seen.add(s);novel.push(s);}
    // Every observation contributes exactly 10,368 particles.
    for(let i=0;i<GRAPH_PARTICLES;i++){
      const alpha=coord(frame,i,0)+72*coord(frame,i,1);
      this.#occupancy.set(alpha,(this.#occupancy.get(alpha)??0n)+1n);
    }
    this.#ticks++;
    const total=BigInt(graph.signatures.length),n=BigInt(novel.length);
    const div=total===0n?1n:gcd(n,total);
    return Object.freeze({tick:frame.physicsTick,novelCount:novel.length,
      noveltyDensity:Object.freeze({numerator:total===0n?0n:n/div,
        denominator:total===0n?1n:total/div}),
      cumulativeUnique:this.#seen.size,observedTicks:this.#ticks,
      source:"FINITE_OBSERVED_TICKS",admitted:false});
  }
  probability(alpha){
    if(!Number.isInteger(alpha)||alpha<0||alpha>=5184)throw RangeError("HASH72_ALPHA_RANGE");
    const n=this.#occupancy.get(alpha)??0n,den=this.#ticks*BigInt(GRAPH_PARTICLES);
    if(den===0n)return Object.freeze({numerator:0n,denominator:1n});
    const g=gcd(n,den);
    return Object.freeze({numerator:n/g,denominator:den/g});
  }
}
