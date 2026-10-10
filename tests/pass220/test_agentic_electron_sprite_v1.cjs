"use strict";
/* Pass220 regression for the new derived browser; executes the actual
   companion JS in a Node VM and parses the complete HTML inline script. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const vm=require("node:vm");
const path=require("node:path");
const ROOT=path.resolve(__dirname,"..","..");
const js=fs.readFileSync(path.join(ROOT,"examples/hhs_agentic_electron_sprite_v1.js"),"utf8");
const original=fs.readFileSync(path.join(ROOT,"examples/ParticleSimulation.html"),"utf8");
const derived=fs.readFileSync(path.join(ROOT,"examples/ParticleSimulationAtomicNeural.html"),"utf8");

assert(original.includes('schema:"HHS_PASS_220_I057_PARTICLE_SIMULATION_ZERO_LOSS_PERF_V1"'));
assert(!derived.includes('<script src="hhs_agentic_electron_sprite_v1.js"></script>'),
  "Single-file HTML must not require a separate local module");
const inline=[...derived.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)]
  .map(m=>m[1]).filter(s=>s.trim());
assert.equal(inline.length,3,"Diagnostics + embedded neural controller + main simulation source");
new vm.Script(inline[0],{filename:"runtime_diagnostics.js"});
new vm.Script(inline[1],{filename:"embedded_agentic_sprite_controller.js"});
new vm.Script(inline[2],{filename:"ParticleSimulationAtomicNeural.html"});
assert(inline[1].includes(js.trim()),"Embedded neural source must match companion source");
const browserLike={window:{},Float32Array,Uint8Array,Math,Number,Object};
vm.runInNewContext(inline[1],browserLike,{filename:"standalone_inlined_controller.js"});
assert(browserLike.window.HHSAgenticElectronSpriteV1,
  "Opening the HTML alone must initialize the neural module");
const nativeStart=inline[2].indexOf("    window.HHS = (function(){");
const nativeEnd=inline[2].indexOf("    /* =====================================================================\n       POINCARÉ–PENROSE");
assert(nativeStart>0&&nativeEnd>nativeStart,"Embedded native HHS boot module must exist");
vm.runInNewContext(inline[2].slice(nativeStart,nativeEnd),
  browserLike,{filename:"standalone_hhs_boot.js"});
assert.equal(browserLike.window.HHS.boot.boot_halt,false,
  "Normal native I041 boot must not accidentally suppress the scene");
assert(derived.includes('try {\n        if(!window.HHSAgenticElectronSpriteV1) throw Error'),
  "Missing optional neural overlay must be caught before rendering");
assert(derived.includes("if(!window.HHS.boot.boot_halt) initScene()"));
assert(!derived.includes("Object.assign(simParams, config.HHS_System.global_parameters)"));
assert(derived.includes("FAIL_CLOSED_LIVE_STATE_MUTATING_DIAGNOSTIC"));
assert(derived.includes('MODULES["AgenticElectronSpriteStatus"]'));
assert(derived.includes("guardConfig(config.HHS_System.global_parameters)"));
assert(derived.includes('commandOutput").textContent'));
assert(!derived.includes('commandOutput").innerHTML'));
assert(derived.includes("renderTick===1"),"The initial frame must render without waiting for 4 physics callbacks");
assert(derived.includes('id="runtimeDiagnostics"'),"Visible runtime diagnostics required");
assert(derived.includes('OrbitControls unavailable: static camera fallback active'));
assert(!derived.includes('dat.gui.min.js'),"Unused third party dat.gui asset should not be loaded");
assert(derived.includes('"TopoInversionTest"]'),"Unsupported mutating topology diagnostic must be quarantined");
assert(derived.includes('observed_render_fps:1000*renderedFrames/elapsed'));
assert(derived.includes('computedHash')===false);
assert(derived.includes('compressedHash: "ON_DEMAND_GET_STATE_ONLY"'));
assert(original.includes("    initScene();"),"Original frozen page baseline preserved");
assert(derived.includes("agentController.tick({"));

const context={window:{},console,Math,Float32Array,Uint8Array,Number,Object};
vm.runInNewContext(js,context,{filename:"hhs_agentic_electron_sprite_v1.js"});
const factory=context.window.HHSAgenticElectronSpriteV1;
assert(factory);
assert.equal(factory.WIDTH,4);
assert.equal(factory.LIMIT,10368);
assert.throws(()=>factory.create(0),/INVALID_PARTICLE_POPULATION/);
assert.throws(()=>factory.create(10369),/INVALID_PARTICLE_POPULATION/);
function frame(n){
  const p=new Float32Array(n*3),v=new Float32Array(n*3);
  const phase=new Uint8Array(n),charge=new Float32Array(n);
  const mass=new Float32Array(n),neighbors=new Float32Array(n);
  const budget=new Uint8Array(n);
  for(let i=0;i<n;i++){
    p[i*3]=i%8;p[i*3+1]=i%7;p[i*3+2]=i%4;
    v[i*3]=.04;v[i*3+1]=-.01;
    phase[i]=i%72;charge[i]=i%2===0?1:-1;mass[i]=1;
    neighbors[i]=i%20;budget[i]=8;
  }
  return {position:p,velocity:v,phase,charge,mass,neighbors,budget};
}
const f=frame(10368), copy0=Array.from(f.position.slice(0,48));
const a=factory.create(10368),b=factory.create(10368);
const t1=a.tick(f),t2=b.tick(f);
assert.equal(t1.logical_agents,10368);
assert.equal(t1.ticks,1);
assert.equal(t1.flyvis_connectome_executed,false);
assert.equal(t1.canonical_mutation_authority,false);
assert.equal(t1.pending_native_admission,true);
assert.equal(t2.mean_activity,t1.mean_activity);
assert.equal(a.proposal(0).lo_shu_lane,0);
assert.equal(a.proposal(5184).lo_shu_lane,1);
assert.equal(a.proposal(5184).lo_shu_local,0);
assert.equal(a.proposal(10367).lo_shu_local,5183);
assert.deepEqual(Array.from(f.position.slice(0,48)),copy0,"Neural inference must not mutate physical positions");
for(const i of [0,37,5184,10367]){
  const pa=a.proposal(i),pb=b.proposal(i);
  assert.equal(JSON.stringify(pa),JSON.stringify(pb));
  for(const name of ["thrust","yaw","pitch","roll"]){
    assert(Math.abs(pa[name])<=1);
    assert(Number.isFinite(pa[name]));
  }
  assert.equal(pa.applied_to_physics,false);
  assert.equal(pa.hhs_hash216_minted,false);
}
assert.throws(()=>a.proposal(-1),/INVALID_AGENT_ADDRESS/);
assert.throws(()=>a.tick({}),/INCOMPLETE_PROJECTED_SENSORY_FRAME/);
const badFrame=frame(10368);
badFrame.velocity[10367*3+2]=NaN;
const previousTicks=a.telemetry().ticks;
assert.throws(()=>a.tick(badFrame),/NONFINITE_SENSORY_INPUT/);
assert.equal(a.telemetry().ticks,previousTicks,"Invalid frames cannot advance recurrence");
assert(!derived.includes("if(agentProjectionHalt) return"),
  "Rejected neural projection must not halt the independent field loop");
assert(derived.includes('agentProjectionHalt="NEURAL_SENSORY_GATE_REJECTED: "'));
assert(derived.includes("agentController=null;"),
  "Rejected neural projection must quarantine neural inference");
assert(derived.includes("pointerActive=false; });"));
assert(derived.includes('id="agentInspector"'));
assert(derived.includes('id="inspectAgent"'));
assert(derived.includes('getElementById("runCalibration").addEventListener'));
const guard=a.guardConfig({massBoost:2,unknown:8});
assert.equal(guard.applied,false);
assert.equal(guard.status,"FAIL_CLOSED_GLOBAL_CORPUS_NATIVE_ADMISSION_REQUIRED");
assert.equal(a.guardConfig({}).status,"NO_PARAMETER_CHANGE");
a.tick(f);
b.tick(f);
assert.equal(a.telemetry().ticks,2);
assert.equal(a.telemetry().mean_activity,b.telemetry().mean_activity);
const massProfile=frame(10368);
const controller1=factory.create(10368),controller2=factory.create(10368);
massProfile.mass[0]=1;controller1.tick(massProfile);
massProfile.mass[0]=4;controller2.tick(massProfile);
assert.notEqual(controller1.proposal(0).roll,controller2.proposal(0).roll,
  "Atomic-mass projection must influence the neuronal sensory response");
console.log("PASS: full 10368-agent transactional recurrent preview, browser syntax, visible interface and guarded input");
