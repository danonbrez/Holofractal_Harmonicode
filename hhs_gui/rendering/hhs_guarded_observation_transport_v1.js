/* Pass 220: guarded Runtime OS observation egress to presentation sampler.
 * Calls the EXISTING /api/runtime/services and /api/runtime/services/dispatch
 * membrane; no alternate authority, transport clock, or physics scheduling.
 * Dispatch service must be explicitly registered by the native runtime.
 */
(function(root,factory){
  "use strict";
  const api=factory();
  if(typeof module!=="undefined"&&module.exports)module.exports=api;
  if(root)root.HHSGuardedObservationTransportV1=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  "use strict";
  const SCHEMA="HHS_PASS_220_GUARDED_OBSERVATION_TRANSPORT_V1";
  const SERVICE="pass220.gfx4_decay_matrix_observation.export";
  const FRAME=/^[\x21-\x7e]{216}$/;
  const fail=(code)=>{throw new Error("OBS_TRANSPORT_"+code);};
  function integer(s){
    if(typeof s==="bigint")return s;
    if(typeof s==="number"&&Number.isSafeInteger(s))return BigInt(s);
    if(typeof s==="string"&&/^(0|[1-9]\d*)$/.test(s))return BigInt(s);
    fail("INTEGER_INVALID");
  }
  function decodeBase64(s){
    if(typeof s!=="string"||s.length===0||s.length%4!==0||!/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(s))fail("PACKET_ENCODING");
    const buf=typeof Buffer!=="undefined"?Buffer.from(s,"base64"):Uint8Array.from(atob(s),c=>c.charCodeAt(0));
    const out=new Uint8Array(buf.length);out.set(buf);
    const encoded=typeof Buffer!=="undefined"?Buffer.from(out).toString("base64"):btoa(String.fromCharCode(...out));
    if(encoded!==s)fail("PACKET_NONCANONICAL");
    return out;
  }
  function unwrap(response){
    if(!response||typeof response!=="object")fail("RESPONSE_MISSING");
    // Native contract envelopes can expose the service dispatch record under
    // payload. Accept only an explicitly shaped guarded service dispatch record.
    const candidates=[response,response.payload,response.data,response.result,response.payload&&response.payload.result];
    const record=candidates.find(x=>x&&x.schema==="HHS_SERVICE_DISPATCH_RECORD_V1");
    if(!record||record.service?.name!==SERVICE||record.zero_bypass_interposition?.propagation_allowed!==true||
       record.execution_allowed===false||!record.unified_ledger?.tip_hash72)
      fail("GUARDED_DISPATCH_UNVERIFIED");
    return record.result;
  }
  class GuardedObservationTransport{
    constructor({fetchImpl,baseUrl="",sampler,serviceName=SERVICE}={}){
      if(typeof fetchImpl!=="function")fail("FETCH_REQUIRED");
      if(!sampler||typeof sampler.ingest!=="function")fail("SAMPLER_REQUIRED");
      if(serviceName!==SERVICE)fail("SERVICE_CONTRACT_INVALID");
      if(typeof baseUrl!=="string"||baseUrl.includes("?")||baseUrl.includes("#")||/^https?:\/\//.test(baseUrl)||baseUrl.includes(".."))fail("BASE_URL_INVALID");
      this._fetch=fetchImpl;this._base=baseUrl.replace(/\/$/,"");this._sampler=sampler;
      this._discovered=false;this._count=0;
    }
    async _json(path,options){
      const response=await this._fetch(this._base+path,options);
      if(!response||response.ok!==true)fail("HTTP_REJECTED");
      const data=await response.json();
      if(!data||typeof data!=="object")fail("JSON_INVALID");
      return data;
    }
    async discover(){
      const result=await this._json("/api/runtime/services",{method:"GET",credentials:"same-origin",cache:"no-store"});
      const nodes=[result,result.payload,result.data,result.result].filter(Boolean);
      const services=nodes.find(v=>v.schema==="HHS_RUNTIME_SERVICE_LIST_V1")?.services;
      this._discovered=Array.isArray(services)&&services.some(x=>x&&x.name===SERVICE&&x.conformance_decision?.derivation_complete===true);
      if(!this._discovered)fail("NATIVE_SERVICE_UNAVAILABLE");
      return true;
    }
    async ingestNativeObservation(request){
      if(!this._discovered)fail("NATIVE_SERVICE_NOT_DISCOVERED");
      if(!request||typeof request!=="object"||Array.isArray(request))fail("REQUEST_INVALID");
      // The server handles admission and packet generation. Never accept a
      // browser-produced nativeAdmission/receipt as proof.
      for(const key of ["nativeAdmission","identity","verification","packet"])
        if(Object.prototype.hasOwnProperty.call(request,key))fail("CLIENT_AUTHORITY_CLAIM");
      const response=await this._json("/api/runtime/services/dispatch",{
        method:"POST",credentials:"same-origin",cache:"no-store",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({service:SERVICE,payload:request})
      });
      const payload=unwrap(response);
      const bundle=payload&&payload.observation;
      if(!bundle||payload.schema!=="HHS_PASS_220_NATIVE_OBSERVATION_EGRESS_V1"||
         payload.native_receipt_verified!==true||
         payload.native_decay_binding_verified!==true||
         payload.packet_identity_verified!==true||
         !FRAME.test(bundle.frameHash216||"")||!FRAME.test(bundle.decayHash216||"")||
         bundle.identity?.frame_hash216!==bundle.frameHash216||
         bundle.verification?.frame_hash216!==bundle.frameHash216||
         bundle.verification?.decay_hash216!==bundle.decayHash216||
         bundle.verification?.verified_decay_matrix_binding!==true||
         bundle.verification?.verified_live_vm81_commit!==true||
         typeof bundle.packet_base64!=="string")fail("NATIVE_OBSERVATION_UNVERIFIED");
      const packet=decodeBase64(bundle.packet_base64);
      const record={
        packet,
        identity:bundle.identity,
        decayHash216:bundle.decayHash216,
        matrixVersion:integer(bundle.matrixVersion)
      };
      // The sampler's native observation cache independently checks sealed
      // packet lanes, times, VM81 receipt, and the associated decay root.
      const result=this._sampler.ingest(record);
      this._count++;
      return result;
    }
    stats(){return Object.freeze({schema:SCHEMA,accepted:this._count,discovered:this._discovered,authority:false,physicsClock:false});}
  }
  return Object.freeze({SCHEMA,SERVICE,GuardedObservationTransport});
});
