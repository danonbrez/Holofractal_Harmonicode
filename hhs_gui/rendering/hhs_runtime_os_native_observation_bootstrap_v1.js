/* Pass 220: additive standalone/production Runtime OS observation bootstrap.
 * Included inside the expanded HTML after existing V147 application source.
 * The native renderer is an optional, guarded input to graphics presentation;
 * failed service discovery cannot stop V147 physics, controls, or WebGL.
 */
(function(root){
  "use strict";
  if(root.HHSRuntimeOSNativeObservationV1)return;
  const required=[
    root.HHSRenderPacket,
    root.HHSObservationGraphCacheV1,
    root.HHSNativeObservationBindingV1,
    root.HHSWebGLObservationSamplerV1,
    root.HHSGuardedObservationTransportV1,
    root.HHSNativeWebGLFramePresenterV1
  ];
  if(required.some(x=>!x))throw Error("HHS_NATIVE_OBSERVATION_EMBEDDED_MODULE_MISSING");
  const [packetAPI,cacheAPI,bindingAPI,samplerAPI,transportAPI,presenterAPI]=required;
  let active=null,availability="UNAVAILABLE",reason="";
  function integer(v){
    if(typeof v==="bigint")return v;
    if(typeof v==="number"&&Number.isSafeInteger(v))return BigInt(v);
    if(typeof v==="string"&&/^(0|[1-9]\d*)$/.test(v))return BigInt(v);
    return null;
  }
  function bound(context){
    const b=active&&active.bundle;
    if(!b||b.identity!==context.identity)return false;
    const v=b.verification||{};
    if(v.verified_live_vm81_commit!==true||v.verified_decay_matrix_binding!==true||
       v.frame_hash216!==b.frameHash216||v.decay_hash216!==b.decayHash216||
       v.vm81_receipt_hash72!==b.identity.vm81_admission?.receipt_hash72)return false;
    return context.frameIndex===integer(b.frameIndex)&&
      context.timeNum===integer(b.timeNum)&&
      context.timeDen===integer(b.timeDen);
  }
  const cache=bindingAPI.createNativeObservationCache({
    capacity:64,ObservationCache:cacheAPI.ObservationCache,
    validatePacket:packetAPI.validate,
    verifyNativeAdmission:context=>bound(context),
    verifyDecayMatrixBinding:context=>{
      const b=active&&active.bundle;
      return !!(b&&bound(context)&&
        b.decayHash216===context.decayHash216&&
        b.frameHash216===context.frameHash216&&
        integer(b.matrixVersion)===context.matrixVersion);
    }
  });
  const sampler=new samplerAPI.WebGLObservationSampler({
    nativeObservationCache:cache,displayHz:120,minLatencyMs:17,maxLatencyMs:250
  });
  const presenter=new presenterAPI.NativeWebGLFramePresenter({
    sampler,packetAPI
  });
  const transport=new transportAPI.GuardedObservationTransport({
    fetchImpl:(...args)=>root.fetch(...args),
    sampler,
    onVerifiedEgress:info=>{active=info;}
  });
  const online=/^https?:$/.test(root.location?.protocol||"");
  const ready=online?transport.discover().then(()=>{
    availability="READY";return true;
  }).catch(e=>{availability="UNAVAILABLE";reason=String(e);return false;}):
    Promise.resolve(false);
  const api=Object.freeze({
    ready,
    async ingest(request){
      if(!(await ready))throw Error("HHS_NATIVE_OBSERVATION_SERVICE_UNAVAILABLE");
      return transport.ingestNativeObservation(request);
    },
    async captureNativeSnapshot(graphics={}){
      if(!(await ready))throw Error("HHS_NATIVE_OBSERVATION_SERVICE_UNAVAILABLE");
      if(!graphics||typeof graphics!=="object"||Array.isArray(graphics))
        throw Error("HHS_NATIVE_OBSERVATION_GRAPHICS_REQUIRED");
      const forbidden=["matrix_hex","matrix_byte_length","matrix_version",
        "frame_index","exact_time_num","exact_time_den","identity","verification","packet"];
      if(forbidden.some(key=>Object.prototype.hasOwnProperty.call(graphics,key)))
        throw Error("HHS_NATIVE_OBSERVATION_CLIENT_SOURCE_OVERRIDE");
      return transport.ingestNativeObservation({...graphics,
        source_mode:"VMRC_RAW5184_SNAPSHOT"});
    },
    readLocalDecayPool(){
      const source=root.HHSV150DecayPoolObservation;
      if(!source||typeof source.read!=="function")
        throw Error("HHS_LOCAL_DECAY_POOL_PRODUCER_UNAVAILABLE");
      const sample=source.read();
      if(sample?.schema!=="HHS_V150_LOCAL_DECAY_POOL_OBSERVATION_V1"||
         sample.nativeVM81Admission!==false||sample.physicsMutationAuthority!==false)
        throw Error("HHS_LOCAL_DECAY_POOL_OBSERVATION_INVALID");
      return sample;
    },
    select(timeNum,timeDen){return sampler.select(timeNum,timeDen);},
    presentNativeFrame({renderer,scene,camera,resources,timeNum,timeDen}={}){
      return presenter.present({renderer,scene,camera,resources,timeNum,timeDen});
    },
    configure(options){return sampler.configure(options);},
    inspect(){return Object.freeze({
      availability,reason,
      transport:transport.stats(),sampler:sampler.stats(),
      presenter:presenter.stats(),
      nativeAdmissionAuthority:false,physicsSchedulingAuthority:false
    });}
  });
  root.HHSRuntimeOSNativeObservationV1=api;
})(typeof window!=="undefined"?window:globalThis);
