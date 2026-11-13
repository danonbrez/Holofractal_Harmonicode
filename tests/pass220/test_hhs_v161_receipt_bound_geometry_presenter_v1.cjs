"use strict";
const assert=require("node:assert/strict");
const {createHash,webcrypto}=require("node:crypto");
const {loadRenderingUMD}=require("./load_rendering_umd_v1.cjs");
const v161=loadRenderingUMD("hhs_v161_receipt_bound_geometry_presenter_v1.js");
const v159=loadRenderingUMD("hhs_v159_receipt_bound_geometry_ingress_v1.js");
const v157=loadRenderingUMD("hhs_v157_geometry_presentation_ingress_v1.js");
const physics=new Float32Array(10368*3);
physics[0]=-0;physics[1]=4.5;
const positions=Buffer.from(physics.buffer);
const hash=c=>c.repeat(216);
const egress={
 schema:v159.EGRESS,source_classification:"RECEIPT_BOUND_GEOMETRY_PROJECTION",
 physical_source_provenance_verified:false,native_vm81_frame_binding_verified:true,
 native_packet_sealed_and_validated:true,native_geometry_execution_verified:false,
 position_byte_length:124416,particle_count:10368,
 position_sha256:createHash("sha256").update(positions).digest("hex"),
 position_base64:positions.toString("base64"),
 packet_base64:Buffer.from([1,2,3,4]).toString("base64"),
 producer_tick:72,draw_resource_id:9,
 frame_hash216:hash("a"),geometry_hash216:hash("b"),
 dependency_root_hash216:hash("c"),command_manifest_hash216:hash("d")
};
const proof={schema:"HHS_PASS_220_V155_GEOMETRY_GFX4_RECEIPT_BINDING_V1",
 verified_vm81_frame_binding:true,verified_geometry_draw_binding:true,
 physical_source_provenance_verified:false,draw_resource_id:9,
 frame_hash216:hash("a"),geometry_hash216:hash("b"),
 dependency_root_hash216:hash("c"),ordered_command_root_hash216:hash("d")};
const packetAPI={validate:()=>({compatibilityUnadmitted:false,
 vm81AdmissionAuthority:false,commands:[
 {opcode:1},{opcode:14,resourceId:9n},{opcode:24}]})};
const positionAttribute={array:new Float32Array(10368*3),itemSize:3,needsUpdate:false};
const resource={geometry:{attributes:{position:positionAttribute}}};
const scene={},camera={},renderCalls=[];
const renderer={render:()=>renderCalls.push(1)};
const resources={require:id=>Number(id)===9?resource:null};
const presenter={present:({timeNum,timeDen})=>{
 assert.equal(timeNum,72);assert.equal(timeDen,1);
 renderer.render(scene,camera);
 return {rendered:true,frameHash216:egress.frame_hash216};
}};
const bridge=v161.create({ingressV159:v159,ingressV157:v157,presenter});
const args={egress,proof,verifyGuardedEgress:async()=>true,
 packetAPI,subtle:webcrypto.subtle,resource,positionAttribute,
 physicsPositionArray:physics,renderer,scene,camera,resources,timeNum:72,timeDen:1};
(async()=>{
 assert.equal(bridge.stats().updates,0);
 await assert.rejects(bridge.present({...args,timeDen:0}),/EXACT_TIME_REQUIRED/);
 assert.equal(positionAttribute.needsUpdate,false);
 await assert.rejects(bridge.present({...args,resources:{require:()=>null}}),/DRAW_RESOURCE_MISMATCH/);
 assert.equal(positionAttribute.needsUpdate,false);
 await assert.rejects(bridge.present({...args,verifyGuardedEgress:async()=>false}),/GUARDED_EGRESS_UNVERIFIED/);
 assert.equal(positionAttribute.needsUpdate,false);
 const result=await bridge.present(args);
 assert.equal(result.copiedBytes,124416);
 assert.equal(result.presentationOnly,true);
 assert.equal(result.physicalSourceProvenanceVerified,false);
 assert.equal(result.physicsSchedulingAuthority,false);
 assert.equal(result.vm81MutationAuthority,false);
 assert.equal(bridge.stats().updates,1);
 assert.equal(renderCalls.length,1);
 assert.equal(Object.is(positionAttribute.array[0],-0),true);
 assert.equal(positionAttribute.array[1],4.5);
 await assert.rejects(bridge.present(args),/FRAME_REPLAY_OR_MISSING/);
 assert.equal(renderCalls.length,1);
 console.log("PASS: V161 guarded V159/V157 staging, resource check and inherited cadence");
})().catch(e=>{console.error(e);process.exitCode=1;});
