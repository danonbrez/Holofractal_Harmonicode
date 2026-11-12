/* Pass 220: packet-identity / decay-observation binding for read-only presentation.
 * Native VM81/GFX4 and decay-matrix validators remain the only authorities.
 * This adapter MUST NOT construct identities, mint receipts or mutate physics.
 */
(function(root,factory){
  "use strict";
  const api=factory(root);
  if(typeof module!=="undefined"&&module.exports)module.exports=api;
  if(root)root.HHSNativeObservationBindingV1=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(root){
  "use strict";
  const SCHEMA="HHS_PASS_220_NATIVE_OBSERVATION_BINDING_V1";
  const CLASSIFICATION="HHS_PASS_220_GFX4_GRAPHICS_FRAME_VM81_ADMITTED";
  const LENGTHS=Object.freeze({scene:216,frame:216,prior:216,resources:216,camera:72});
  const OFFSETS=Object.freeze({scene:80,frame:296,prior:512,resources:728,camera:944});
  const fail=code=>{throw new Error(code);};
  function bytes(input){
    if(input instanceof ArrayBuffer)return new Uint8Array(input);
    if(ArrayBuffer.isView(input))return new Uint8Array(input.buffer,input.byteOffset,input.byteLength);
    fail("OBS_NATIVE_PACKET_TYPE");
  }
  function decimal(value,name){
    if(typeof value==="bigint")return value;
    if(typeof value==="number"&&Number.isSafeInteger(value))return BigInt(value);
    if(typeof value==="string"&&/^-?\d+$/.test(value))return BigInt(value);
    fail("OBS_NATIVE_"+name+"_INVALID");
  }
  function identityText(value,length,name,allowEmpty=false){
    if(allowEmpty&&(value===undefined||value===null||value===""))return "";
    if(typeof value!=="string"||value.length!==length||!/^[\x21-\x7e]+$/.test(value))
      fail("OBS_NATIVE_"+name+"_INVALID");
    return value;
  }
  function laneMatch(packet,offset,length,expected){
    for(let i=0;i<length;i++){
      const byte=packet[offset+i],target=i<expected.length?expected.charCodeAt(i):0;
      if(byte!==target)return false;
    }
    return true;
  }
  function nativePayload(record){
    if(!record||typeof record!=="object")fail("OBS_NATIVE_RECORD_REQUIRED");
    if(record.classification!==CLASSIFICATION||
       record.packet_identity_vm81_admitted!==true||
       record.packet_compatibility_unadmitted!==false||
       record.singleton_vm81_authority!==true||
       record.gpu_or_renderer_mutation_authority!==false)
      fail("OBS_NATIVE_GFX4_ADMISSION_RECORD_INVALID");
    if(!record.vm81_admission||typeof record.vm81_admission!=="object"||
       typeof record.vm81_admission.receipt_hash72!=="string"||
       record.vm81_admission.receipt_hash72.length!==72)
      fail("OBS_NATIVE_RECEIPT_REQUIRED");
    const identity={
      scene:identityText(record.scene_snapshot_hash216,216,"SCENE"),
      frame:identityText(record.frame_hash216,216,"FRAME"),
      prior:identityText(record.prior_frame_hash216,216,"PRIOR",true),
      resources:identityText(record.resource_manifest_hash216,216,"RESOURCES"),
      camera:identityText(record.camera_hash72,72,"CAMERA")
    };
    identityText(record.packet_identity_hash216,216,"PACKET_IDENTITY");
    return identity;
  }
  function bindNativeObservation({
    packet,identity,decayHash216,matrixVersion,
    verifyNativeAdmission,verifyDecayMatrixBinding,
    validatePacket
  }={}){
    if(typeof validatePacket!=="function")fail("OBS_NATIVE_PACKET_VALIDATOR_REQUIRED");
    if(typeof verifyNativeAdmission!=="function")fail("OBS_NATIVE_RECEIPT_VERIFIER_REQUIRED");
    if(typeof verifyDecayMatrixBinding!=="function")fail("OBS_NATIVE_DECAY_VERIFIER_REQUIRED");
    const source=bytes(packet);
    const sealed=new Uint8Array(source.byteLength);sealed.set(source);
    const parsed=validatePacket(sealed);
    if(!parsed||parsed.compatibilityUnadmitted!==false||
       parsed.vm81AdmissionAuthority===true||
       parsed.hash216IdentityAuthority===true)fail("OBS_NATIVE_PACKET_NOT_ADMITTED");
    const lanes=nativePayload(identity);
    for(const name of Object.keys(LENGTHS))
      if(!laneMatch(sealed,OFFSETS[name],LENGTHS[name],lanes[name]))
        fail("OBS_NATIVE_"+name.toUpperCase()+"_LANE_MISMATCH");
    const frameIndex=decimal(parsed.frameIndex,"FRAME_INDEX");
    const timeNum=decimal(parsed.exactTimeNum,"TIME_NUM");
    const timeDen=decimal(parsed.exactTimeDen,"TIME_DEN");
    if(timeDen<=0n)fail("OBS_NATIVE_TIME_DEN_INVALID");
    const version=decimal(matrixVersion,"MATRIX_VERSION");
    if(version<0n)fail("OBS_NATIVE_MATRIX_VERSION_INVALID");
    identityText(decayHash216,216,"DECAY_HASH216");
    // The native verifier must check the actual VM81 receipt against its trusted ledger,
    // not just echo the supplied admission record.
    if(verifyNativeAdmission(Object.freeze({
      identity,frameIndex,timeNum,timeDen,packet:new Uint8Array(sealed)
    }))!==true)fail("OBS_NATIVE_RECEIPT_UNVERIFIED");
    // GFX4 packet has no decay-hash lane. Require a separate pre-existing
    // native decay-matrix binding verifier for exact observation coherence.
    if(verifyDecayMatrixBinding(Object.freeze({
      decayHash216,matrixVersion:version,frameHash216:lanes.frame,
      frameIndex,timeNum,timeDen,identity
    }))!==true)fail("OBS_NATIVE_DECAY_BINDING_UNVERIFIED");
    return Object.freeze({
      nativeAdmission:true,
      decayHash216,
      frameHash216:lanes.frame,
      matrixVersion:version,
      frameIndex,timeNum,timeDen,
      packet:sealed,
      schema:SCHEMA
    });
  }
  function createNativeObservationCache({
    capacity=64,validatePacket,verifyNativeAdmission,verifyDecayMatrixBinding,
    ObservationCache
  }={}){
    const Cache=ObservationCache||(root&&root.HHSObservationGraphCacheV1&&root.HHSObservationGraphCacheV1.ObservationCache);
    if(typeof Cache!=="function")fail("OBS_NATIVE_PRESENTATION_CACHE_REQUIRED");
    const cache=new Cache({capacity,validatePacket});
    return Object.freeze({
      append({packet,identity,decayHash216,matrixVersion}={}){
        return cache.append(bindNativeObservation({
          packet,identity,decayHash216,matrixVersion,
          validatePacket,verifyNativeAdmission,verifyDecayMatrixBinding
        }));
      },
      lookup(frameHash216){return cache.lookup(frameHash216);},
      bracket(timeNum,timeDen){return cache.bracket(timeNum,timeDen);},
      snapshot(){return cache.snapshot();}
    });
  }
  return Object.freeze({
    SCHEMA,CLASSIFICATION,LENGTHS,OFFSETS,
    bindNativeObservation,createNativeObservationCache
  });
});
