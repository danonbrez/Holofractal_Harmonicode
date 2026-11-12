/* Pass 220 V147 WebGL observation sampler.
 * Presentation-only cache consumer: no physics ticks, hash minting, or
 * renderer-driven native searches. Feed immutable admitted observations
 * asynchronously through the pre-existing native binding membrane.
 */
(function(root,factory){
  "use strict";
  const api=factory();
  if(typeof module!=="undefined"&&module.exports)module.exports=api;
  if(root)root.HHSWebGLObservationSamplerV1=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  "use strict";
  const SCHEMA="HHS_PASS_220_WEBGL_OBSERVATION_SAMPLER_V1";
  function exactInt(value,label,positive=false){
    if(typeof value==="number"&&!Number.isSafeInteger(value))throw Error("OBS_SAMPLER_"+label);
    if(!(typeof value==="bigint"||typeof value==="number"||
      (typeof value==="string"&&/^-?\d+$/.test(value))))throw Error("OBS_SAMPLER_"+label);
    const n=BigInt(value);
    if(positive?n<=0n:n<0n)throw Error("OBS_SAMPLER_"+label);
    return n;
  }
  function compare(a,b){const x=a.timeNum*b.timeDen,y=b.timeNum*a.timeDen;return x<y?-1:x>y?1:0;}
  class WebGLObservationSampler{
    constructor({nativeObservationCache,capacity=64,displayHz=120,minLatencyMs=17,maxLatencyMs=250}={}){
      if(!nativeObservationCache||typeof nativeObservationCache.append!=="function"||
         typeof nativeObservationCache.bracket!=="function"||
         typeof nativeObservationCache.snapshot!=="function")
        throw Error("OBS_SAMPLER_NATIVE_CACHE_REQUIRED");
      this.cache=nativeObservationCache;
      this.configure({displayHz,minLatencyMs,maxLatencyMs});
      this._lastDisplay=null;
      this._accepted=0;
      this._selected=0;
      this._missed=0;
    }
    configure({displayHz=this.displayHz,minLatencyMs=this.minLatencyMs,maxLatencyMs=this.maxLatencyMs}={}){
      if(!Number.isInteger(displayHz)||displayHz<1||displayHz>120)throw Error("OBS_SAMPLER_DISPLAY_HZ");
      if(!Number.isInteger(minLatencyMs)||!Number.isInteger(maxLatencyMs)||
         minLatencyMs<0||maxLatencyMs<minLatencyMs||maxLatencyMs>60000)
        throw Error("OBS_SAMPLER_LATENCY_RANGE");
      this.displayHz=displayHz;this.minLatencyMs=minLatencyMs;this.maxLatencyMs=maxLatencyMs;
    }
    ingest(bundle){
      // The native binding membrane validates all Hash216 packet lanes,
      // VM81 journal witnesses and ordered decay-matrix associations.
      const result=this.cache.append(bundle);
      this._accepted++;
      return result;
    }
    select(timeNum,timeDen){
      const target={timeNum:exactInt(timeNum,"TIME_NUM"),timeDen:exactInt(timeDen,"TIME_DEN",true)};
      if(this._lastDisplay&&compare(target,this._lastDisplay)<0)
        throw Error("OBS_SAMPLER_DISPLAY_TIME_REVERSED");
      this._lastDisplay=target;
      const pair=this.cache.bracket(target.timeNum,target.timeDen);
      if(!pair){this._missed++;return null;}
      // The renderer can interpolate presentation geometry but MUST NOT
      // treat interpolated samples as canonical admitted VM81 states.
      this._selected++;
      return Object.freeze({
        schema:SCHEMA,
        prior:pair.prior,
        next:pair.next,
        exact:pair.exact,
        canonicalMutationAuthority:false,
        sampledGraphicsOnly:true
      });
    }
    // Optional browser presentation clock adapter. No setTimeout,
    // requestAnimationFrame, physics tick, or Date.now is used here.
    // The host owns scheduling and passes the chosen native rational time.
    stats(){return Object.freeze({
      schema:SCHEMA,accepted:this._accepted,selected:this._selected,
      missed:this._missed,displayHz:this.displayHz,
      minLatencyMs:this.minLatencyMs,maxLatencyMs:this.maxLatencyMs,
      cache:this.cache.snapshot(),
      physicsSchedulingAuthority:false,
      hash216MutationAuthority:false,
      gpuMutationAuthority:false
    });}
  }
  return Object.freeze({SCHEMA,WebGLObservationSampler});
});
