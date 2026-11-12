"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const root=path.resolve(__dirname,"../..");
const sources=[
  "hhs_gui/rendering/hhs_harmonicode_render_packet_v1.js",
  "hhs_gui/rendering/hhs_observation_graph_cache_v1.js",
  "hhs_gui/rendering/hhs_native_observation_binding_v1.js",
  "hhs_gui/rendering/hhs_webgl_observation_sampler_v1.js",
  "hhs_gui/rendering/hhs_guarded_observation_transport_v1.js",
  "hhs_gui/rendering/hhs_runtime_os_native_observation_bootstrap_v1.js"
];
let called=0;
const context=vm.createContext({
  location:{protocol:"file:"},
  fetch(){called++;throw Error("offline bootstrap must not access remote services");}
});
context.window=context;
for(const source of sources){
  vm.runInContext(fs.readFileSync(path.join(root,source),"utf8"),context,{filename:source});
}
const api=context.HHSRuntimeOSNativeObservationV1;
assert.ok(api);
(async()=>{
  assert.equal(await api.ready,false);
  assert.equal(called,0);
  const info=api.inspect();
  assert.equal(info.availability,"UNAVAILABLE");
  assert.equal(info.nativeAdmissionAuthority,false);
  assert.equal(info.physicsSchedulingAuthority,false);
  assert.equal(info.sampler.physicsSchedulingAuthority,false);
  assert.equal(api.select(1,120),null);
  await assert.rejects(()=>api.ingest({}),/SERVICE_UNAVAILABLE/);
  assert.equal(called,0);
  console.log("PASS: standalone V148 native observation bootstrap preserves offline execution");
})().catch(err=>{console.error(err);process.exitCode=1;});
