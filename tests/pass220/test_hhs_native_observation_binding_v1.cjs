"use strict";
const assert=require("node:assert/strict");
const P=require("../../hhs_gui/rendering/hhs_harmonicode_render_packet_v1.js");
const B=require("../../hhs_gui/rendering/hhs_native_observation_binding_v1.js");
const {ObservationCache}=require("../../hhs_gui/rendering/hhs_observation_graph_cache_v1.js");
const h=(char,n=216)=>char.repeat(n);
const identity={
  classification:B.CLASSIFICATION,
  packet_identity_vm81_admitted:true,
  packet_compatibility_unadmitted:false,
  singleton_vm81_authority:true,
  gpu_or_renderer_mutation_authority:false,
  scene_snapshot_hash216:h("a"),
  frame_hash216:h("b"),
  prior_frame_hash216:"",
  resource_manifest_hash216:h("c"),
  camera_hash72:h("d",72),
  packet_identity_hash216:h("e"),
  vm81_admission:{receipt_hash72:h("f",72)}
};
function makePacket(){
  const raw=P.buildCompatibilityPacket({
    targetWidth:16,targetHeight:16,frameIndex:2,exactTimeNum:1,exactTimeDen:120,
    commands:[{opcode:P.OPCODE.BEGIN_FRAME},{opcode:P.OPCODE.END_FRAME}]
  });
  const v=new DataView(raw),b=new Uint8Array(raw);
  v.setUint32(32,P.FLAG_SEALED|P.FLAG_PROJECTION_ONLY,true);
  for(const [name,offset] of Object.entries(B.OFFSETS)){
    const s=({scene:identity.scene_snapshot_hash216,frame:identity.frame_hash216,
      prior:identity.prior_frame_hash216,resources:identity.resource_manifest_hash216,
      camera:identity.camera_hash72})[name];
    for(let i=0;i<B.LENGTHS[name];i++) b[offset+i]=i<s.length?s.charCodeAt(i):0;
  }
  v.setBigUint64(1080,P.projectionFingerprint(b),true);
  assert.equal(P.validate(raw).compatibilityUnadmitted,false);
  return raw;
}
const options={
  packet:makePacket(),identity,decayHash216:h("z"),matrixVersion:7,
  validatePacket:P.validate,
  verifyNativeAdmission:()=>true, // Mock trusted service in this isolated unit test.
  verifyDecayMatrixBinding:()=>true // Mock trusted service in this isolated unit test.
};
const valid=B.bindNativeObservation(options);
assert.equal(valid.frameHash216,identity.frame_hash216);
assert.equal(valid.timeNum,1n);
const cache=B.createNativeObservationCache({
  capacity:2,ObservationCache,validatePacket:P.validate,
  verifyNativeAdmission:()=>true,
  verifyDecayMatrixBinding:()=>true
});
cache.append(options);
assert.equal(cache.lookup(identity.frame_hash216).matrixVersion,7n);
assert.equal(cache.bracket(1,120).exact,true);
assert.equal(cache.bracket(0,120),null);
assert.throws(()=>B.bindNativeObservation({...options,verifyNativeAdmission:undefined}),/OBS_NATIVE_RECEIPT_VERIFIER_REQUIRED/);
assert.throws(()=>B.bindNativeObservation({...options,verifyDecayMatrixBinding:undefined}),/OBS_NATIVE_DECAY_VERIFIER_REQUIRED/);
assert.throws(()=>B.bindNativeObservation({...options,verifyNativeAdmission:()=>false}),/OBS_NATIVE_RECEIPT_UNVERIFIED/);
assert.throws(()=>B.bindNativeObservation({...options,verifyDecayMatrixBinding:()=>false}),/OBS_NATIVE_DECAY_BINDING_UNVERIFIED/);
assert.throws(()=>B.bindNativeObservation({...options,decayHash216:"wrong"}),/OBS_NATIVE_DECAY_HASH216_INVALID/);
assert.throws(()=>B.bindNativeObservation({...options,identity:{...identity,frame_hash216:h("q")}}),/OBS_NATIVE_FRAME_LANE_MISMATCH/);
assert.throws(()=>B.bindNativeObservation({...options,identity:{...identity,packet_identity_vm81_admitted:false}}),/OBS_NATIVE_GFX4_ADMISSION_RECORD_INVALID/);
const corrupt=new Uint8Array(options.packet);corrupt[B.OFFSETS.frame]^=1;
assert.throws(()=>B.bindNativeObservation({...options,packet:corrupt}),/HHS179_PACKET_FINGERPRINT/);
const compatibility=P.buildCompatibilityPacket({commands:[{opcode:P.OPCODE.BEGIN_FRAME},{opcode:P.OPCODE.END_FRAME}]});
assert.throws(()=>B.bindNativeObservation({...options,packet:compatibility}),/OBS_NATIVE_PACKET_NOT_ADMITTED/);
assert.throws(()=>cache.append(options),/OBS_REPLAY_OR_OUT_OF_ORDER/);
console.log("PASS: GFX4 packet lane + external receipt and decay binding (mocked) / presentation-only cache");
