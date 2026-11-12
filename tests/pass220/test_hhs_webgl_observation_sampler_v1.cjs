"use strict";
const assert=require("node:assert/strict");
const {WebGLObservationSampler}=require("../../hhs_gui/rendering/hhs_webgl_observation_sampler_v1.js");
const h=c=>c.repeat(216);
const records=[];
const nativeCache={
  append(v){if(v.verified!==true)throw Error("NOT_NATIVE_VERIFIED");records.push(v);return {frameHash216:v.frameHash216};},
  bracket(n,d){
    const t=BigInt(n),den=BigInt(d);
    let p=null;
    for(const r of records){
      const cmp=r.timeNum*den-t*r.timeDen;
      if(cmp===0)return {prior:r,next:r,exact:true};
      if(cmp>0)return p?{prior:p,next:r,exact:false}:null;
      p=r;
    }
    return null;
  },
  snapshot(){return {count:records.length,canonicalMutationAuthority:false};}
};
const s=new WebGLObservationSampler({nativeObservationCache:nativeCache,displayHz:120,minLatencyMs:17,maxLatencyMs:250});
assert.equal(s.stats().physicsSchedulingAuthority,false);
assert.equal(s.stats().hash216MutationAuthority,false);
assert.equal(s.stats().gpuMutationAuthority,false);
assert.throws(()=>new WebGLObservationSampler({}),/NATIVE_CACHE_REQUIRED/);
assert.throws(()=>s.configure({displayHz:121}),/DISPLAY_HZ/);
assert.throws(()=>s.configure({minLatencyMs:251,maxLatencyMs:250}),/LATENCY_RANGE/);
assert.throws(()=>s.ingest({verified:false}),/NOT_NATIVE_VERIFIED/);
s.ingest({verified:true,frameHash216:h("a"),timeNum:1n,timeDen:120n});
s.ingest({verified:true,frameHash216:h("b"),timeNum:2n,timeDen:120n});
assert.equal(s.select(1,120).exact,true);
assert.equal(s.select(3,240).exact,false);
assert.equal(s.select(3,120),null);
assert.throws(()=>s.select(1,120),/DISPLAY_TIME_REVERSED/);
assert.equal(s.stats().accepted,2);
assert.equal(s.stats().selected,2);
assert.equal(s.stats().missed,1);
assert.equal(s.stats().cache.count,2);
console.log("PASS: Pass220 WebGL observation sampler - 16 assertions");
