/* Pass 220 V161 — guarded V159/V157 geometry transfer to inherited WebGL cadence.
 * No new clock, GPU renderer, trusted producer, VM81 admission or receipt.
 * The caller must supply a previously authenticated service verification
 * callback and the inherited V151 presenter/cache resources.
 */
(function(root,factory){
  "use strict";
  const api=factory();
  if(typeof module!=="undefined"&&module.exports)module.exports=api;
  if(root)root.HHSV161ReceiptBoundGeometryPresenterV1=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  "use strict";
  const SCHEMA="HHS_PASS_220_V161_RECEIPT_BOUND_GEOMETRY_PRESENTER_V1";
  const fail=c=>{throw Error("V161_PRESENT_"+c);};
  const uint=v=>typeof v==="bigint"&&v>=0n?v:
    typeof v==="number"&&Number.isSafeInteger(v)&&v>=0?BigInt(v):null;
  function create({ingressV159,ingressV157,presenter}={}){
    if(!ingressV159||typeof ingressV159.stageVerified!=="function"||
       !ingressV157||typeof ingressV157.publish!=="function"||
       !presenter||typeof presenter.present!=="function")
      fail("INHERITED_MODULES_REQUIRED");
    let lastFrame=null,updates=0;
    async function present({egress,proof,verifyGuardedEgress,packetAPI,
      subtle,resource,positionAttribute,physicsPositionArray,
      renderer,scene,camera,resources,timeNum,timeDen}={}){
      if(!renderer||typeof renderer.render!=="function"||
         !scene||!camera||!resources||typeof resources.require!=="function")
        fail("EXISTING_RENDER_RESOURCES_REQUIRED");
      if(!egress||typeof egress.frame_hash216!=="string"||
         egress.frame_hash216===lastFrame)fail("FRAME_REPLAY_OR_MISSING");
      // This exact time must identify an already admitted cached frame;
      // no interpolation or new physics/render timer is introduced here.
      if(uint(timeNum)===null||uint(timeDen)===null||uint(timeDen)===0n)
        fail("EXACT_TIME_REQUIRED");
      const staged=await ingressV159.stageVerified({
        egress,proof,verifyGuardedEgress,packetAPI,
        presentationIngress:ingressV157,subtle,resource,
        positionAttribute,physicsPositionArray
      });
      if(staged.frameHash216!==egress.frame_hash216||
         staged.sourceProvenanceVerified!==false)
        fail("STAGING_IDENTITY_INVALID");
      // Preflight the authoritative resource identity on the inherited
      // scene registry before committing render-only coordinates.
      if(resources.require(egress.draw_resource_id)!==resource)
        fail("DRAW_RESOURCE_MISMATCH");
      // Presentation never certifies source provenance; the packet identity
      // and VM81 admission must be verified by the supplied guarded caller.
      const published=ingressV157.publish(staged.staged);
      const rendered=presenter.present({renderer,scene,camera,resources,timeNum,timeDen});
      if(!rendered||rendered.rendered!==true||
         rendered.frameHash216!==staged.frameHash216)
        fail("ADMITTED_FRAME_NOT_PRESENTED");
      lastFrame=staged.frameHash216;updates++;
      return Object.freeze({schema:SCHEMA,frameHash216:lastFrame,
        geometryHash216:staged.geometryHash216,copiedBytes:published.copiedBytes,
        presentationOnly:true,physicalSourceProvenanceVerified:false,
        physicsSchedulingAuthority:false,vm81MutationAuthority:false});
    }
    return Object.freeze({present,stats:()=>Object.freeze({schema:SCHEMA,
      updates,lastFrameHash216:lastFrame,physicsSchedulingAuthority:false,
      vm81MutationAuthority:false})});
  }
  return Object.freeze({SCHEMA,create});
});
