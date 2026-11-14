/* Pass 220 V159: receipt-bound V158 egress -> V157 presentation stage.
 * Read-only decoding and binding. Trusted authority comes exclusively from
 * the existing guarded transport's independent verifier, not the payload.
 * V158 does NOT attest physical producer provenance. This bridge does not
 * authorize physics, VM81 commits, or WebGL frame scheduling.
 */
(function(root,factory){
  "use strict";
  const api=factory();
  if(typeof module!=="undefined"&&module.exports)module.exports=api;
  if(root)root.HHSV159ReceiptBoundGeometryIngressV1=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  "use strict";
  const SCHEMA="HHS_PASS_220_V159_RECEIPT_BOUND_GEOMETRY_INGRESS_V1";
  const EGRESS="HHS_PASS_220_V158_ORDERED_GEOMETRY_NATIVE_EGRESS_V1";
  const PROOF="HHS_PASS_220_V155_GEOMETRY_GFX4_RECEIPT_BINDING_V1";
  const BYTES=124416, HASH=/^[0-9a-f]{64}$/;
  const fail=code=>{throw Error("V159_GEOMETRY_"+code);};
  const integer=v=>typeof v==="bigint"?v:typeof v==="number"&&Number.isSafeInteger(v)?BigInt(v):null;
  function decode(text) {
    if(typeof text!=="string"||text.length===0||text.length%4!==0||
       !/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(text))
      fail("BASE64_INVALID");
    const bytes=typeof Buffer!=="undefined"?new Uint8Array(Buffer.from(text,"base64")):
      Uint8Array.from(atob(text),x=>x.charCodeAt(0));
    const encoded=typeof Buffer!=="undefined"?Buffer.from(bytes).toString("base64"):
      btoa(Array.from(bytes,x=>String.fromCharCode(x)).join(""));
    if(encoded!==text)fail("BASE64_NONCANONICAL");
    return bytes;
  }
  function equals(a,b){if(a.length!==b.length)return false;
    for(let i=0;i<a.length;i++)if(a[i]!==b[i])return false;
    return true;}
  function hex(bytes){return Array.from(bytes,x=>x.toString(16).padStart(2,"0")).join("");}
  async function stageVerified({egress,verifyGuardedEgress,packetAPI,
    presentationIngress,proof,resource,positionAttribute,physicsPositionArray,
    subtle}={}){
    if(!egress||egress.schema!==EGRESS||
       egress.source_classification!=="RECEIPT_BOUND_GEOMETRY_PROJECTION"||
       egress.physical_source_provenance_verified!==false||
       egress.native_vm81_frame_binding_verified!==true||
       egress.native_packet_sealed_and_validated!==true||
       egress.native_geometry_execution_verified!==false||
       egress.position_byte_length!==BYTES||egress.particle_count!==10368||
       !HASH.test(egress.position_sha256||""))
      fail("EGRESS_SHAPE_INVALID");
    if(typeof verifyGuardedEgress!=="function")fail("TRUSTED_VERIFIER_REQUIRED");
    if(!packetAPI||typeof packetAPI.validate!=="function"||
       !presentationIngress||typeof presentationIngress.stage!=="function")
      fail("INHERITED_VALIDATORS_REQUIRED");
    const tick=integer(egress.producer_tick),rid=integer(egress.draw_resource_id);
    if(tick===null||tick<0n||rid===null||rid<=0n)fail("SOURCE_COORDINATES_INVALID");
    const positions=decode(egress.position_base64);
    const packetBytes=decode(egress.packet_base64);
    if(positions.length!==BYTES)fail("GEOMETRY_LENGTH");
    if(!subtle||typeof subtle.digest!=="function")fail("DIGEST_VERIFIER_REQUIRED");
    const digest=new Uint8Array(await subtle.digest("SHA-256",positions));
    if(hex(digest)!==egress.position_sha256)fail("GEOMETRY_DIGEST_MISMATCH");
    const packet=packetAPI.validate(packetBytes);
    if(!packet||packet.compatibilityUnadmitted!==false||
       packet.vm81AdmissionAuthority===true||!Array.isArray(packet.commands))
      fail("NATIVE_PACKET_REQUIRED");
    if(!proof||proof.schema!==PROOF||
       proof.frame_hash216!==egress.frame_hash216||
       proof.geometry_hash216!==egress.geometry_hash216||
       proof.dependency_root_hash216!==egress.dependency_root_hash216||
       proof.ordered_command_root_hash216!==egress.command_manifest_hash216||
       integer(proof.draw_resource_id)!==rid)
      fail("GEOMETRY_PROOF_MISMATCH");
    // This callback MUST verify server-owned egress against the existing
    // guarded route and VM81 journal; a caller-provided boolean is not proof.
    if(await verifyGuardedEgress(Object.freeze({
      egress,packetBytes:new Uint8Array(packetBytes),
      positionBytes:new Uint8Array(positions),proof,packet
    }))!==true)fail("GUARDED_EGRESS_UNVERIFIED");
    const staged=presentationIngress.stage({
      positionBytes:positions,producerTick:tick,drawResourceId:rid,
      proof,packet,resource,positionAttribute,physicsPositionArray
    });
    return Object.freeze({schema:SCHEMA,staged,
      frameHash216:egress.frame_hash216,
      geometryHash216:egress.geometry_hash216,
      sourceProvenanceVerified:false,physicsSchedulingAuthority:false,
      vm81MutationAuthority:false});
  }
  return Object.freeze({SCHEMA,EGRESS,stageVerified});
});
