"use strict";
const assert=require("node:assert/strict");
const {GuardedObservationTransport,SERVICE}=require("../../hhs_gui/rendering/hhs_guarded_observation_transport_v1.js");
const h=x=>x.repeat(216),frame=h("a"),decay=h("b"),packet=Buffer.from([1,2,3,4]).toString("base64");
let calls=[];
const nativeObservation={
  frameHash216:frame,decayHash216:decay,
  matrixVersion:"1",packet_base64:packet,
  identity:{frame_hash216:frame},
  verification:{frame_hash216:frame,decay_hash216:decay,
    verified_decay_matrix_binding:true,verified_live_vm81_commit:true}
};
let serviceResponse={schema:"HHS_SERVICE_DISPATCH_RECORD_V1",
  service:{name:SERVICE},zero_bypass_interposition:{propagation_allowed:true},
  unified_ledger:{tip_hash72:"c".repeat(72)},
  result:{schema:"HHS_PASS_220_NATIVE_OBSERVATION_EGRESS_V1",
    native_receipt_verified:true,native_decay_binding_verified:true,
    packet_identity_verified:true,native_source_verified:true,
    observation_source:"VMRC_RAW5184_SNAPSHOT",observation:nativeObservation}};
let enabled=true;
const fetchImpl=async(path,init)=>{
  calls.push({path,init});
  if(path.endsWith("/services"))return {
    ok:true,json:async()=>({schema:"HHS_RUNTIME_SERVICE_LIST_V1",services:enabled?
      [{name:SERVICE,conformance_decision:{derivation_complete:true}}]:[]})
  };
  return {ok:true,json:async()=>serviceResponse};
};
let accepted=[];
const sampler={ingest:r=>{accepted.push(r);return {frameHash216:r.identity.frame_hash216}}};
const t=new GuardedObservationTransport({fetchImpl,sampler});
(async()=>{
  await assert.rejects(()=>t.ingestNativeObservation({matrixVersion:1}),/NATIVE_SERVICE_NOT_DISCOVERED/);
  await t.discover();
  const result=await t.ingestNativeObservation({matrixVersion:1});
  assert.equal(result.frameHash216,frame);
  assert.deepEqual([...accepted[0].packet],[1,2,3,4]);
  assert.equal(accepted[0].matrixVersion,1n);
  assert.equal(calls[1].path,"/api/runtime/services/dispatch");
  assert.equal(JSON.parse(calls[1].init.body).service,SERVICE);
  assert.equal(t.stats().physicsClock,false);
  await assert.rejects(()=>t.ingestNativeObservation({nativeAdmission:true}),/CLIENT_AUTHORITY_CLAIM/);
  const original=serviceResponse;
  serviceResponse={...original,unified_ledger:{}};
  await assert.rejects(()=>t.ingestNativeObservation({matrixVersion:2}),/GUARDED_DISPATCH_UNVERIFIED/);
  serviceResponse={...original,result:{...original.result,native_decay_binding_verified:false}};
  await assert.rejects(()=>t.ingestNativeObservation({matrixVersion:2}),/NATIVE_OBSERVATION_UNVERIFIED/);
  serviceResponse={...original,result:{...original.result,observation:{...nativeObservation,packet_base64:"!!!!"}}};
  await assert.rejects(()=>t.ingestNativeObservation({matrixVersion:2}),/PACKET_ENCODING/);
  assert.equal(t.stats().accepted,1);
  enabled=false;
  const other=new GuardedObservationTransport({fetchImpl,sampler});
  await assert.rejects(()=>other.discover(),/NATIVE_SERVICE_UNAVAILABLE/);
  console.log("PASS: guarded observation transport / negative tests");
})().catch(err=>{console.error(err);process.exitCode=1;});
