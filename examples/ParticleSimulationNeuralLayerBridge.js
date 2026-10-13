/* Pass 220 I085 — ORIGINAL 10,368 physics particles each own ONE native neural layer.
 *
 * Read-only membrane over the actual ParticleSimulation.html mesh array:
 *  - exact BigInt 86,805,555,555-neuron coverage in 10,368 adjacent intervals
 *  - no replacement physics, Three.js scene, shader, waveform, or I063 L2 graft
 *  - no implicit nucleus/edge relation; VM81 and Hash72 authority remains Lane 5
 *  - quartic simulation/render gating untouched (offline output still 60fps)
 */
(function(global) {
  "use strict";
  const SCHEMA="HHS_PASS_220_I085_PHYSICS_10368_NEURAL_LAYER_MEMBRANE_V1";
  const COUNT=10368, WIDTH=5184;
  const NEURONS=86805555555n, DENOM=BigInt(COUNT);
  const BASE=NEURONS/DENOM, EXTRA=Number(NEURONS%DENOM);
  const FPS=60, QUARTIC=4;
  const indexByParticle=new WeakMap();
  const carrierByIndex=new Array(COUNT);
  const fail=message=>{throw new Error("I085 fail closed: "+message);};
  function index(value,label){
    if(!Number.isSafeInteger(value))fail(label+" must be exact integer");
    if(value<0||value>=COUNT)fail(label+" out of particle range");
    return value;
  }
  function neutron(value){
    if(typeof value!=="string"||!/^(0|[1-9][0-9]*)$/.test(value))
      fail("neuron_id must be canonical unsigned decimal BigInt string");
    const n=BigInt(value);
    if(n>=NEURONS)fail("neuron_id out of I082 range");
    return n;
  }
  function bounds(indexValue){
    const p=index(indexValue,"layer_id");
    const start=BigInt(p)*BASE+BigInt(Math.min(p,EXTRA));
    const count=BASE+(p<EXTRA?1n:0n);
    return Object.freeze({
      schema:SCHEMA,layer_id:p,particle_id:p,
      physical_layer:p<WIDTH?0:1,
      native_neuron_start:start.toString(),
      native_neuron_stop_exclusive:(start+count).toString(),
      native_neuron_count:count.toString()
    });
  }
  function particleIndexForNeuron(id){
    const n=neutron(id), expandedEnd=BigInt(EXTRA)*(BASE+1n);
    const p=n<expandedEnd
      ? Number(n/(BASE+1n))
      : EXTRA+Number((n-expandedEnd)/BASE);
    const b=bounds(p);
    if(n<BigInt(b.native_neuron_start)||
       n>=BigInt(b.native_neuron_stop_exclusive))
      fail("inverse neuron-layer mapping inconsistent");
    return p;
  }
  const sceneParticles=typeof particles!=="undefined"?particles:null;
  if(!Array.isArray(sceneParticles)||sceneParticles.length!==COUNT)
    fail("actual original physics scene must contain 10368 particles");
  const recorded=new Set();
  for(let i=0;i<COUNT;i++){
    const p=sceneParticles[i];
    if(!p||!p.userData||!p.position||!p.material)
      fail("missing existing physical particle "+i);
    if(Boolean(p.userData.layer2)!==(i>=WIDTH))
      fail("original layer2 particle ordering diverged at "+i);
    if(indexByParticle.has(p)||recorded.has(p))
      fail("duplicate physical mesh identity");
    indexByParticle.set(p,i);
    carrierByIndex[i]=p;
    recorded.add(p);
  }
  function layerOfParticle(p){
    if(!indexByParticle.has(p))fail("mesh not in actual 10368-particle scene");
    return bounds(indexByParticle.get(p));
  }
  function particleOfLayer(layerId){
    return carrierByIndex[index(layerId,"layer_id")];
  }
  function nativeTickAddress(frameId,sweep,k){
    // This browser mapping cannot mint the native Pass174 Hash216Array.
    // That ONE 216-position indexed array is authored in native I085,
    // covering both successive 5184-address sweeps per logical cycle.
    if(!Number.isSafeInteger(frameId)||frameId<0)fail("frame_id must be exact nonnegative");
    if(!Number.isSafeInteger(sweep)||sweep<0||sweep>1)fail("sweep must be 0 or 1");
    if(!Number.isSafeInteger(k)||k<0||k>=WIDTH)fail("tick slot outside 5184");
    const p=sweep*WIDTH+k,layer=bounds(p);
    return Object.freeze({
      layer_id:p,physical_layer:sweep,position5184:k,
      native_tick_in_array:p,
      absolute_native_tick:(BigInt(frameId)*BigInt(COUNT)+BigInt(p)).toString(),
      hash72_row:Math.floor(k/72),hash72_column:k%72,
      vm81_cell:Math.floor(k/64),vm81_local64:k%64,
      mirror5184:WIDTH-1-k,neural_layer:layer,
      native_hash216_array_authority:false,projection_only:true
    });
  }
  function pairedTick(frameId,k){
    const a=nativeTickAddress(frameId,0,k),b=nativeTickAddress(frameId,1,k);
    if(b.layer_id-a.layer_id!==WIDTH||
       a.vm81_cell!==b.vm81_cell||
       a.vm81_local64!==b.vm81_local64||
       a.hash72_row!==b.hash72_row||
       a.hash72_column!==b.hash72_column)
      fail("ordered physical layer sweeps lost common VM81 coordinate");
    return Object.freeze({position5184:k,layer0:a,layer1:b,
      common_hash216_array_authority:"NATIVE_PASS174_ONLY",
      candidate_only:true});
  }
  function projectPhysicalState(layerId){
    // These numbers are float WebGL presentation coordinates only. Never
    // feed them back as native BigInt algebra or canonical VM81 state.
    const p=particleOfLayer(layerId);
    return Object.freeze({
      layer_id:layerId,
      physical_layer:layerId<WIDTH?0:1,
      position:[p.position.x,p.position.y,p.position.z],
      native_position_authority:false,
      physical_velocity:[p.userData.velocity.x,p.userData.velocity.y,p.userData.velocity.z],
      projection_only:true
    });
  }
  function validateWitnessIngress(event){
    // Browser cannot establish canonical Lane5 VM81/Hash72/216 execution.
    // Explicitly reject untrusted edge/neuron effects pending server admission;
    // no silent fake neural signals and no physics feedback.
    if(!event||typeof event!=="object"||event.authoritative!==true)
      fail("candidate cannot be admitted as native neural execution");
    fail("native ordered edge/witness verifier not connected to browser ingress");
  }
  function audit(){
    let next=0n;
    for(let i=0;i<COUNT;i++){
      const b=bounds(i),start=BigInt(b.native_neuron_start);
      const stop=BigInt(b.native_neuron_stop_exclusive);
      if(start!==next||stop<=start||
         indexByParticle.get(carrierByIndex[i])!==i||
         particleIndexForNeuron(start.toString())!==i||
         particleIndexForNeuron((stop-1n).toString())!==i)
         fail("particle or exact neuron partition invalid at "+i);
      next=stop;
    }
    if(next!==NEURONS||EXTRA!==4323||BASE!==8372449n)
      fail("I082 neuron count changed");
    return Object.freeze({
      schema:SCHEMA,passed:true,original_particles_bound:COUNT,
      native_neural_layers:COUNT,original_physical_layers:2,
      neuron_count:NEURONS.toString(),vm81_positions_per_neuron:WIDTH,
      logical_positions:(NEURONS*BigInt(WIDTH)).toString(),
      base_neurons_per_layer:BASE.toString(),extra_neuron_layers:EXTRA,
      nominal_capture_fps:FPS,physics_raf_per_visual_frame:QUARTIC,
      native_sweeps_per_hash216_array:2,
      native_layer_ticks_per_sweep:WIDTH,
      native_ticks_per_composed_hash216_array:COUNT,
      native_hash216_array_source:"PASS174_NATIVE",
      graph_full_edge_execution_verified:false,
      native_vm81_mutation:false,original_physics_mutated:false
    });
  }
  const diagnostics=audit();
  Object.freeze(carrierByIndex);
  global.HHSNeuralLayerMap=Object.freeze({
    schema:SCHEMA,diagnostics,layerBounds:bounds,
    layerOfParticle,particleOfLayer,particleIndexForNeuron,
    nativeTickAddress,pairedTick,
    projectPhysicalState,validateWitnessIngress,audit
  });
})(window);
