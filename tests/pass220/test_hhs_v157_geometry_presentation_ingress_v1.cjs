"use strict";
const assert=require("node:assert/strict");
const {loadRenderingUMD}=require("./load_rendering_umd_v1.cjs");
const api=loadRenderingUMD("hhs_v157_geometry_presentation_ingress_v1.js");
const COUNT=10368*3;
const physics=new Float32Array(COUNT);
physics[0]=-0;physics[1]=1.5;physics[2]=-0.25;
const bytes=Uint8Array.from(new Uint8Array(physics.buffer));
const position={array:new Float32Array(COUNT),itemSize:3,needsUpdate:false};
const resource={geometry:{attributes:{position}}};
const proof={schema:"HHS_PASS_220_V155_GEOMETRY_GFX4_RECEIPT_BINDING_V1",
 verified_vm81_frame_binding:true,verified_geometry_draw_binding:true,
 physical_source_provenance_verified:false,draw_resource_id:9};
const packet={commands:[{opcode:1},{opcode:3,resourceId:7n},
 {opcode:14,resourceId:9n},{opcode:24}]};
const args={positionBytes:bytes,producerTick:72,drawResourceId:9,
 proof,packet,resource,positionAttribute:position,physicsPositionArray:physics};
const staging=api.stage(args);
assert.equal(position.needsUpdate,false);
const result=api.publish(staging);
assert.equal(result.presentationOnly,true);
assert.equal(result.nativeProducerProvenanceVerified,false);
assert.equal(result.copiedBytes,124416);
assert.equal(position.needsUpdate,true);
assert.throws(()=>api.publish(staging),/STAGE_REQUIRED/);
assert.equal(Object.is(position.array[0],-0),true);
assert.equal(position.array[1],1.5);
assert.equal(position.array[2],-0.25);
assert.equal(Object.is(physics[0],-0),true);
assert.throws(()=>api.stage({...args,producerTick:-1}),/TICK_OR_RESOURCE_INVALID/);
assert.throws(()=>api.stage({...args,drawResourceId:10}),/INHERITED_PROOF_REQUIRED/);
assert.throws(()=>api.stage({...args,proof:{...proof,verified_vm81_frame_binding:false}}),/INHERITED_PROOF_REQUIRED/);
assert.throws(()=>api.stage({...args,packet:{commands:[{opcode:1},{opcode:24}]}}),/BOUND_DRAW_COMMAND_REQUIRED/);
assert.throws(()=>api.stage({...args,positionAttribute:{...position}}),/DEDICATED_DRAW_BUFFER_REQUIRED/);
assert.throws(()=>api.stage({...args,positionAttribute:{array:physics,itemSize:3},
 resource:{geometry:{attributes:{position:{array:physics,itemSize:3}}}}}),/DEDICATED_DRAW_BUFFER_REQUIRED/);
const wrong=Uint8Array.from(bytes);wrong[3]=0;
assert.throws(()=>api.stage({...args,positionBytes:wrong}),/PHYSICS_SOURCE_MISMATCH/);
const nonfinite=Uint8Array.from(bytes);
nonfinite.set([0,0,128,127],0);
assert.throws(()=>api.stage({...args,positionBytes:nonfinite}),/NONFINITE/);
const stale=api.stage(args);
physics[2]=99;
assert.throws(()=>api.publish(stale),/SOURCE_CHANGED_BEFORE_UPLOAD/);
assert.equal(position.array[2],-0.25);
console.log("PASS: V157 presentation-only ordered geometry transfer and fail-closed resource/source checks");
