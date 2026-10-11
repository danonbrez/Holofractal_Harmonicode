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
      graph_full_edge_execution_verified:false,
      native_vm81_mutation:false,original_physics_mutated:false
    });
  }
  const diagnostics=audit();
  Object.freeze(carrierByIndex);
  global.HHSNeuralLayerMap=Object.freeze({
    schema:SCHEMA,diagnostics,layerBounds:bounds,
    layerOfParticle,particleOfLayer,particleIndexForNeuron,
    projectPhysicalState,validateWitnessIngress,audit
  });
})(window);
