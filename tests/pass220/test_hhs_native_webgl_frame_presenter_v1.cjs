"use strict";
const assert=require("node:assert/strict");
const {NativeWebGLFramePresenter}=require("../../hhs_gui/rendering/hhs_native_webgl_frame_presenter_v1.js");
const packetAPI=require("../../hhs_gui/rendering/hhs_harmonicode_render_packet_v1.js");
const op=packetAPI.OPCODE;
const scene={parent:null},camera={};
const particle={parent:scene},foreign={parent:null};
const registry=new packetAPI.ResourceRegistry().register(2,camera).register(3,particle).register(4,foreign);
const draws=[],viewports=[],clears=[];
const renderer={render:(s,c)=>draws.push([s,c]),getContext:()=>({viewport:(...v)=>viewports.push(v)}),clear:(...v)=>clears.push(v)};
const hash="a".repeat(216);
function run(commands,opts={}){
  const mockAPI={OPCODE:op,validate:()=>({
    compatibilityUnadmitted:false,vm81AdmissionAuthority:false,
    frameIndex:1n,exactTimeNum:1n,exactTimeDen:120n,commands,
  })};
  const sampler={select:()=>({exact:true,prior:{
    frameIndex:1n,timeNum:1n,timeDen:120n,
    packet:new Uint8Array([1]),frameHash216:hash,matrixVersion:1n,nativeAdmission:true
  }})};
  return new NativeWebGLFramePresenter({sampler,packetAPI:mockAPI}).present({
    renderer,scene,camera,resources:registry,timeNum:1,timeDen:120,...opts
  });
}
const begin={opcode:op.BEGIN_FRAME},end={opcode:op.END_FRAME};
const setCamera={opcode:op.SET_CAMERA,resourceId:2n};
const draw={opcode:op.DRAW_POINTS,resourceId:3n};
const packet=[begin,setCamera,{opcode:op.SET_VIEWPORT,arg0:64n,arg1:32n},
  {opcode:op.CLEAR,arg0:1n},draw,end];
const result=run(packet);
assert.equal(result.rendered,true);
assert.equal(result.drawCommands,1);
assert.equal(result.canonicalMutationAuthority,false);
assert.equal(result.physicsSchedulingAuthority,false);
assert.equal(draws.length,1);
assert.equal(draws[0][0],scene);
assert.equal(draws[0][1],camera);
assert.deepEqual(viewports[0],[0,0,64,32]);
assert.deepEqual(clears[0],[true,false,false]);
const prev=draws.length,previousClear=clears.length;
assert.throws(()=>run([begin,setCamera,end]),/GEOMETRY_COMMAND_REQUIRED/);
assert.throws(()=>run([begin,draw,end]),/CAMERA_REQUIRED_BEFORE_DRAW/);
assert.throws(()=>run([begin,setCamera,{opcode:op.DRAW_POINTS,resourceId:4n},end]),/DRAW_RESOURCE_OUTSIDE_SCENE/);
assert.throws(()=>run([begin,setCamera,{opcode:op.APPLY_EFFECT},draw,end]),/UNSUPPORTED_OPCODE/);
assert.throws(()=>run([begin,{opcode:op.CLEAR,arg0:8n},setCamera,draw,end]),/CLEAR_BITS_INVALID/);
assert.equal(draws.length,prev);
assert.equal(clears.length,previousClear);
console.log("PASS: native WebGL presenter draws existing scene once and rejects unbound geometry before effects");
