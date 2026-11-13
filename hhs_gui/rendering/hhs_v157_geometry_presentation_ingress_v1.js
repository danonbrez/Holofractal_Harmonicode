/* Pass 220 V157 — geometry-bearing GFX4 WebGL presentation buffer ingress.
 * Input is a verified-packet *projection* selected by the existing adapter.
 * This module cannot establish the native producer's provenance or VM81
 * authority, and it never schedules physics, admission, or renderer frames.
 * The target MUST be a dedicated presentation buffer, not thPos/physics.
 */
(function(root,factory){
  "use strict";
  const api=factory();
  if(typeof module!=="undefined"&&module.exports)module.exports=api;
  if(root)root.HHSV157GeometryPresentationIngressV1=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  "use strict";
  const SCHEMA="HHS_PASS_220_V157_GEOMETRY_PRESENTATION_INGRESS_V1";
  const PARTICLES=10368,COUNT=PARTICLES*3,BYTES=COUNT*4;
  const fail=code=>{throw Error("V157_GEOMETRY_"+code);};
  const consumed=new WeakSet();
  const uint=v=>typeof v==="bigint"?v>=0n?v:null:
    typeof v==="number"&&Number.isSafeInteger(v)&&v>=0?BigInt(v):null;
  function equalBytes(a,b){
    if(a.length!==b.length)return false;
    for(let i=0;i<a.length;i++)if(a[i]!==b[i])return false;
    return true;
  }
  function stage({positionBytes,producerTick,drawResourceId,
                 proof,packet,resource,positionAttribute,physicsPositionArray}={}){
    if(!(positionBytes instanceof Uint8Array)||positionBytes.byteLength!==BYTES)
      fail("POSITION_BYTES_REQUIRED");
    if(uint(producerTick)===null||uint(drawResourceId)===null||uint(drawResourceId)===0n)
      fail("TICK_OR_RESOURCE_INVALID");
    if(!proof||proof.schema!=="HHS_PASS_220_V155_GEOMETRY_GFX4_RECEIPT_BINDING_V1"||
       proof.verified_vm81_frame_binding!==true||
       proof.verified_geometry_draw_binding!==true||
       proof.physical_source_provenance_verified!==false||
       uint(proof.draw_resource_id)!==uint(drawResourceId))
      fail("INHERITED_PROOF_REQUIRED");
    if(!packet||!Array.isArray(packet.commands)||
       !packet.commands.some(c=>(c.opcode===14||c.opcode===16||
          c.opcode===14n||c.opcode===16n)&&uint(c.resourceId)===uint(drawResourceId)))
      fail("BOUND_DRAW_COMMAND_REQUIRED");
    // The provided packet MUST already have passed inherited packet/VM81
    // verification in the guarded transport. This is not a receipt verifier.
    if(!resource||!resource.geometry||!positionAttribute||
       resource.geometry.attributes?.position!==positionAttribute||
       !(positionAttribute.array instanceof Float32Array)||
       positionAttribute.array.length!==COUNT||positionAttribute.itemSize!==3)
      fail("DEDICATED_DRAW_BUFFER_REQUIRED");
    const target=positionAttribute.array;
    if(!(physicsPositionArray instanceof Float32Array)||physicsPositionArray.length!==COUNT||
       physicsPositionArray.buffer===target.buffer||positionBytes.buffer===target.buffer)
      fail("PHYSICS_BUFFER_ALIAS_OR_MISSING");
    const snapshot=new Uint8Array(BYTES);
    snapshot.set(positionBytes);
    const view=new DataView(snapshot.buffer);
    const values=new Float32Array(COUNT);
    for(let i=0;i<COUNT;i++){
      const bits=view.getUint32(i*4,true);
      if((bits&0x7f800000)===0x7f800000)fail("NONFINITE");
      values[i]=view.getFloat32(i*4,true);
    }
    // Compare source bytes to an independent physical observation. This
    // checks integrity but does NOT attest its authority or native origin.
    const sourceBytes=new Uint8Array(physicsPositionArray.buffer,
      physicsPositionArray.byteOffset,BYTES);
    const sourceCopy=new Uint8Array(BYTES);sourceCopy.set(sourceBytes);
    if(!equalBytes(snapshot,sourceCopy))fail("PHYSICS_SOURCE_MISMATCH");
    return Object.freeze({schema:SCHEMA,producerTick:uint(producerTick),
      drawResourceId:uint(drawResourceId),values,
      sourceSnapshot:snapshot,sourceReference:physicsPositionArray,
      target,positionAttribute,resource,committed:false});
  }
  function publish(staged){
    if(!staged||staged.schema!==SCHEMA||staged.committed!==false||consumed.has(staged))
      fail("STAGE_REQUIRED");
    const current=new Uint8Array(staged.sourceReference.buffer,
      staged.sourceReference.byteOffset,BYTES);
    if(!equalBytes(current,staged.sourceSnapshot))
      fail("SOURCE_CHANGED_BEFORE_UPLOAD");
    if(staged.positionAttribute.array!==staged.target||
       staged.resource.geometry.attributes?.position!==staged.positionAttribute)
      fail("DRAW_RESOURCE_REPLACED");
    consumed.add(staged);
    staged.target.set(staged.values);
    staged.positionAttribute.needsUpdate=true;
    // This schedules only a renderer-owned GPU upload on the next existing
    // render. It does not invoke render(), animate(), or any physics callback.
    return Object.freeze({schema:SCHEMA,copiedBytes:BYTES,
      producerTick:staged.producerTick,drawResourceId:staged.drawResourceId,
      presentationOnly:true,nativeProducerProvenanceVerified:false,
      physicsMutationAuthority:false,frameSchedulingAuthority:false});
  }
  return Object.freeze({SCHEMA,BYTES,PARTICLES,stage,publish});
});
