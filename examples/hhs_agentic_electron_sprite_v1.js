/* HHS Pass220: Agentic electron-sprite neural projection, no VM81 authority.
   This FlyVis-inspired recurrent SENSOR/MOTOR SURROGATE is not the FlyVis
   connectome, and cannot actuate native physics without a signed admission.
   No DOM, server, network or corpus writes occur in the inference kernel. */
(function(root){
  "use strict";
  const SCHEMA="HHS_PASS220_AGENTIC_ELECTRON_SPRITE_PROJECTION_V1";
  const WIDTH=4, LIMIT=10368, CELL_WIDTH=5184;
  const clamp=x=>Math.max(-1,Math.min(1,x));
  const number=x=>{if(!Number.isFinite(x)) throw Error("NONFINITE_SENSORY_INPUT");return x;};
  function create(count){
    if(!Number.isSafeInteger(count)||count<1||count>LIMIT) throw Error("INVALID_PARTICLE_POPULATION");
    const memory=new Float32Array(count*WIDTH);
    const motor=new Float32Array(count*WIDTH);
    const bond=new Uint8Array(count);
    let steps=0, meanActivity=0, proposals=0;
    function tick(frame){
      if(!frame||!frame.position||!frame.velocity||!frame.phase||!frame.charge||
         !frame.mass||!frame.neighbors||!frame.budget||
         frame.position.length!==count*3||frame.velocity.length!==count*3||
         frame.phase.length!==count||frame.charge.length!==count||
         frame.mass.length!==count||frame.neighbors.length!==count||
         frame.budget.length!==count) throw Error("INCOMPLETE_PROJECTED_SENSORY_FRAME");
      let sum=0, attempts=0;
      for(let i=0;i<count;i++){
        const k=i*3, m=i*WIDTH;
        const vx=number(frame.velocity[k]), vy=number(frame.velocity[k+1]),
              vz=number(frame.velocity[k+2]);
        const speed=Math.min(1,Math.hypot(vx,vy,vz)/2);
        const distance=Math.min(1,Math.hypot(
          number(frame.position[k]),number(frame.position[k+1]),number(frame.position[k+2])
        )/30);
        const electric=clamp(number(frame.charge[i]));
        const inertia=Math.min(1,Math.max(0,number(frame.mass[i]))/4);
        const density=Math.min(1,Math.max(0,number(frame.neighbors[i]))/20);
        const phase=number(frame.phase[i])*Math.PI/36;
        const slots=Math.max(0,Math.min(8,number(frame.budget[i])))/8;
        /* Deterministic synchronous recurrence: use all previous values,
           never updated values, for each particle's four virtual channels. */
        const a=memory[m],b=memory[m+1],c=memory[m+2],d=memory[m+3];
        const n0=Math.tanh(.63*a+.18*b+.48*density-.32*speed+.08*Math.cos(phase));
        const n1=Math.tanh(.62*b-.13*c+.36*electric-.28*distance+.10*Math.sin(phase));
        const n2=Math.tanh(.58*c+.21*d+.33*slots-.22*speed-.10*density);
        const n3=Math.tanh(.61*d+.17*a+.30*(1-distance)+.14*electric-.15*speed-.18*inertia);
        memory[m]=n0;memory[m+1]=n1;memory[m+2]=n2;memory[m+3]=n3;
        /* Wing-like thrust and yaw/pitch/roll are BOUNDED proposals only.
           Bond requests do not write the existing bond/channel geometry. */
        motor[m]=clamp(n0+n2*.2);
        motor[m+1]=clamp(n1-n0*.3);
        motor[m+2]=clamp(n2-n3*.25);
        motor[m+3]=clamp(n3+n1*.2);
        bond[i]=(slots>0 && electric!==0 && density>.15 && n2>.1)?1:0;
        attempts+=bond[i];
        sum+=Math.abs(n0)+Math.abs(n1)+Math.abs(n2)+Math.abs(n3);
      }
      steps++;meanActivity=sum/(count*WIDTH);proposals=attempts;
      return telemetry();
    }
    function proposal(i){
      if(!Number.isInteger(i)||i<0||i>=count) throw Error("INVALID_AGENT_ADDRESS");
      const j=i*WIDTH;
      return Object.freeze({
        schema:SCHEMA,agent_index:i,lo_shu_lane:Math.floor(i/CELL_WIDTH),
        lo_shu_local:i%CELL_WIDTH,
        thrust:motor[j],yaw:motor[j+1],pitch:motor[j+2],roll:motor[j+3],
        bond_request:bond[i]===1,
        role:"PROJECTION_ONLY",native_signed_vm81_admitted:false,
        hhs_hash216_minted:false,applied_to_physics:false
      });
    }
    function telemetry(){
      return Object.freeze({
        schema:SCHEMA,logical_agents:count,controller_kind:"FLYVIS_INSPIRED_RECURRENT_SURROGATE",
        flyvis_connectome_executed:false,vm81_hydration_executed:false,
        ticks:steps,mean_activity:meanActivity,bond_request_candidates:proposals,
        corpus_compatibility_required:true,canonical_mutation_authority:false,
        pending_native_admission:true
      });
    }
    function guardConfig(values){
      const keys=values && typeof values==="object" ? Object.keys(values) : [];
      return Object.freeze({
        status:keys.length?"FAIL_CLOSED_GLOBAL_CORPUS_NATIVE_ADMISSION_REQUIRED":"NO_PARAMETER_CHANGE",
        rejected_parameter_paths:keys.sort(),applied:false,
        reason:"Browser commands cannot grant dual-whitepaper or signed VM81 authority"
      });
    }
    return Object.freeze({tick,proposal,telemetry,guardConfig});
  }
  root.HHSAgenticElectronSpriteV1=Object.freeze({SCHEMA,WIDTH,LIMIT,create});
})(typeof window!=="undefined"?window:globalThis);
