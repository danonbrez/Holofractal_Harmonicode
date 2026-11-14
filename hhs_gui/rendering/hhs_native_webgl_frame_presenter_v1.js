/* Pass 220: admitted native GFX4 frame -> existing Three.js WebGL scene.
 * Only draw commands already bound by the native GFX4 packet are observed.
 * The passed scene/camera/object resources remain owned by the V147 renderer.
 * No render-loop, physics, particle, native receipt, or scene mutations here.
 */
(function(root,factory){
  "use strict";
  const api=factory();
  if(typeof module!=="undefined"&&module.exports)module.exports=api;
  if(root)root.HHSNativeWebGLFramePresenterV1=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  "use strict";
  const SCHEMA="HHS_PASS_220_ADMITTED_WEBGL_FRAME_PRESENTER_V1";
  const fail=code=>{throw Error("OBS_PRESENTER_"+code);};
  function member(scene,object){
    if(!scene||!object||typeof object!=="object")return false;
    for(let p=object,depth=0;p&&depth<4096;p=p.parent,depth++)
      if(p===scene)return true;
    return false;
  }
  class NativeWebGLFramePresenter{
    constructor({sampler,packetAPI}={}){
      if(!sampler||typeof sampler.select!=="function")fail("SAMPLER_REQUIRED");
      if(!packetAPI||typeof packetAPI.validate!=="function"||!packetAPI.OPCODE)fail("PACKET_VALIDATOR_REQUIRED");
      this.sampler=sampler;this.packetAPI=packetAPI;
      this._presented=0;this._lastFrame=null;
    }
    present({renderer,scene,camera,resources,timeNum,timeDen}={}){
      if(!renderer||typeof renderer.render!=="function"||typeof renderer.getContext!=="function"||
         !scene||!camera||!resources||typeof resources.require!=="function")
        fail("THREE_WEBGL_CONTEXT_REQUIRED");
      const selected=this.sampler.select(timeNum,timeDen);
      if(!selected)return null;
      // A frame interpolation interval is not an admitted physics state.
      // The last admitted prior frame is presented, never extrapolated.
      const observation=selected.prior;
      if(!observation||observation.nativeAdmission!==undefined&&observation.nativeAdmission!==true)
        fail("OBSERVATION_NOT_ADMITTED");
      const packet=this.packetAPI.validate(observation.packet);
      if(packet.compatibilityUnadmitted!==false||packet.vm81AdmissionAuthority===true)
        fail("NATIVE_PACKET_REQUIRED");
      if(packet.frameIndex!==observation.frameIndex ||
         packet.exactTimeNum!==observation.timeNum ||
         packet.exactTimeDen!==observation.timeDen)
        fail("PACKET_TIME_MISMATCH");
      const op=this.packetAPI.OPCODE;
      let activatedCamera=false,drawCount=0,viewport=null,clearBits=null;
      // Full validation of the ordered packet precedes any WebGL effects.
      for(const cmd of packet.commands){
        switch(cmd.opcode){
          case op.BEGIN_FRAME: case op.END_FRAME:break;
          case op.SET_CAMERA:
            if(resources.require(cmd.resourceId)!==camera)fail("CAMERA_RESOURCE_MISMATCH");
            activatedCamera=true;break;
          case op.DRAW_POINTS:case op.DRAW_MESHES:
            if(!activatedCamera)fail("CAMERA_REQUIRED_BEFORE_DRAW");
            if(!member(scene,resources.require(cmd.resourceId)))fail("DRAW_RESOURCE_OUTSIDE_SCENE");
            drawCount++;break;
          case op.SET_VIEWPORT:
            if(cmd.arg0===0n||cmd.arg1===0n||cmd.arg0>16384n||cmd.arg1>16384n)
              fail("VIEWPORT_INVALID");
            viewport=[Number(cmd.arg0),Number(cmd.arg1)];break;
          case op.CLEAR:
            if(cmd.arg0>7n)fail("CLEAR_BITS_INVALID");
            clearBits=Number(cmd.arg0);break;
          default:fail("UNSUPPORTED_OPCODE");
        }
      }
      if(drawCount===0)fail("GEOMETRY_COMMAND_REQUIRED");
      const gl=renderer.getContext();
      if(!gl||typeof gl.viewport!=="function")fail("WEBGL_CONTEXT_REQUIRED");
      if(viewport)gl.viewport(0,0,viewport[0],viewport[1]);
      if(clearBits!==null){
        if(typeof renderer.clear!=="function")fail("WEBGL_CLEAR_REQUIRED");
        renderer.clear(!!(clearBits&1),!!(clearBits&2),!!(clearBits&4));
      }
      // Existing scene, existing camera, single WebGL draw; neither
      // allocates nor re-parents geometry, and does not call physics ticks.
      renderer.render(scene,camera);
      this._presented++;
      this._lastFrame=observation.frameHash216;
      return Object.freeze({
        schema:SCHEMA,frameHash216:observation.frameHash216,
        matrixVersion:observation.matrixVersion,drawCommands:drawCount,
        sampledExact:selected.exact,canonicalMutationAuthority:false,
        physicsSchedulingAuthority:false,rendered:true
      });
    }
    stats(){return Object.freeze({schema:SCHEMA,presented:this._presented,
      lastFrameHash216:this._lastFrame,physicsSchedulingAuthority:false,
      nativeAdmissionAuthority:false});}
  }
  return Object.freeze({SCHEMA,NativeWebGLFramePresenter});
});
