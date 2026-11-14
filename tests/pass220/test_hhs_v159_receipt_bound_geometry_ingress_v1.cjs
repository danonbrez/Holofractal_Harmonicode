"use strict";
const assert=require("node:assert/strict");
const {webcrypto}=require("node:crypto");
const {createHash}=require("node:crypto");
const {loadRenderingUMD}=require("./load_rendering_umd_v1.cjs");
const bridge=loadRenderingUMD("hhs_v159_receipt_bound_geometry_ingress_v1.js");
const ingress=loadRenderingUMD("hhs_v157_geometry_presentation_ingress_v1.js");
const physics=new Float32Array(10368*3);
physics[0]=-0;physics[1]=2.5;
const positionBytes=Buffer.from(physics.buffer);
const digest=createHash("sha256").update(positionBytes).digest("hex");
const packetBytes=Buffer.from([1,2,3,4]);
const h=x=>x.repeat(216);
const egress={
 schema:bridge.EGRESS,source_classification:"RECEIPT_BOUND_GEOMETRY_PROJECTION",
 physical_source_provenance_verified:false,native_vm81_frame_binding_verified:true,
 native_packet_sealed_and_validated:true,native_geometry_execution_verified:false,
 position_byte_length:124416,particle_count:10368,position_sha256:digest,
 position_base64:positionBytes.toString("base64"),packet_base64:packetBytes.toString("base64"),
 producer_tick:72,draw_resource_id:9,frame_hash216:h("a"),
 geometry_hash216:h("b"),dependency_root_hash216:h("c"),command_manifest_hash216:h("d")
};
const proof={
 schema:"HHS_PASS_220_V155_GEOMETRY_GFX4_RECEIPT_BINDING_V1",
 verified_vm81_frame_binding:true,verified_geometry_draw_binding:true,
 physical_source_provenance_verified:false,draw_resource_id:9,
 frame_hash216:h("a"),geometry_hash216:h("b"),
 dependency_root_hash216:h("c"),ordered_command_root_hash216:h("d")
};
const packetAPI={validate:b=>{
 assert.deepEqual([...b],[1,2,3,4]);
 return {compatibilityUnadmitted:false,vm81AdmissionAuthority:false,
 commands:[{opcode:1},{opcode:14,resourceId:9n},{opcode:24}]};
}};
const attribute={array:new Float32Array(10368*3),itemSize:3,needsUpdate:false};
const resource={geometry:{attributes:{position:attribute}}};
let checks=0;
const verifyGuardedEgress=async ctx=>{checks++;
 assert.equal(ctx.egress,egress);return true;};
const args={egress,verifyGuardedEgress,packetAPI,presentationIngress:ingress,
 proof,resource,positionAttribute:attribute,physicsPositionArray:physics,
 subtle:webcrypto.subtle};
(async()=>{
 const result=await bridge.stageVerified(args);
 assert.equal(result.sourceProvenanceVerified,false);
 assert.equal(result.vm81MutationAuthority,false);
 assert.equal(attribute.needsUpdate,false);
 const published=ingress.publish(result.staged);
 assert.equal(published.copiedBytes,124416);
 assert.equal(attribute.needsUpdate,true);
 assert.equal(Object.is(attribute.array[0],-0),true);
 assert.equal(attribute.array[1],2.5);
 assert.equal(checks,1);
 await assert.rejects(bridge.stageVerified({...args,verifyGuardedEgress:undefined}),/TRUSTED_VERIFIER_REQUIRED/);
 await assert.rejects(bridge.stageVerified({...args,verifyGuardedEgress:async()=>false}),/GUARDED_EGRESS_UNVERIFIED/);
 await assert.rejects(bridge.stageVerified({...args,egress:{...egress,position_sha256:"0".repeat(64)}}),/GEOMETRY_DIGEST_MISMATCH/);
 await assert.rejects(bridge.stageVerified({...args,egress:{...egress,position_base64:"AA=="}}),/GEOMETRY_LENGTH/);
 await assert.rejects(bridge.stageVerified({...args,egress:{...egress,position_base64:"AB=="}}),/BASE64_NONCANONICAL/);
 await assert.rejects(bridge.stageVerified({...args,egress:{...egress,physical_source_provenance_verified:true}}),/EGRESS_SHAPE_INVALID/);
 await assert.rejects(bridge.stageVerified({...args,proof:{...proof,geometry_hash216:h("x")}}),/GEOMETRY_PROOF_MISMATCH/);
 await assert.rejects(bridge.stageVerified({...args,packetAPI:{validate:()=>({compatibilityUnadmitted:true,commands:[]})}}),/NATIVE_PACKET_REQUIRED/);
 const changed=Buffer.from(positionBytes);changed[3]=0;
 await assert.rejects(bridge.stageVerified({...args,egress:{...egress,position_base64:changed.toString("base64")}}),/GEOMETRY_DIGEST_MISMATCH/);
 assert.equal(attribute.array[1],2.5);
 console.log("PASS: V159 guarded geometry egress ingress, SHA-256 and V157 publish");
})().catch(e=>{console.error(e);process.exitCode=1;});
