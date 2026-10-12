"""I085 exact native neural-layer association to the original I084 60fps scene."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import shutil
import subprocess
import unittest

from hhs_runtime.hhs_pass220_i085_particle_neural_layer_membrane_v1 import (
    BASE_SIZE, FIRST_EXTRA, LAYER_COUNT, LAYER_WIDTH, NEURON_COUNT,
    NativeLayerMembraneError, bind_explicit_native_neuron, exact_cover,
    layer_at_neuron, layer_at_particle, projection_tick, validate_scene_source,
)

SRC = Path("examples/ParticleSimulationNeuralLayerBridge.js")
HTML = Path("examples/ParticleSimulation.html")


class I085ExactLayerMembraneTests(unittest.TestCase):
    def test_reversible_complete_86b_neuron_partition(self):
        self.assertEqual((LAYER_COUNT, LAYER_WIDTH), (10368, 5184))
        self.assertEqual((BASE_SIZE, FIRST_EXTRA), (8372449, 4323))
        self.assertEqual(NEURON_COUNT, 86805555555)
        self.assertTrue(exact_cover()["complete_interval_cover"])

    def test_immutable_identity_and_native_layer_boundaries(self):
        for idx in (0, 1, 4322, 4323, 5183, 5184, 7775, 7776, 10367):
            with self.subTest(layer=idx):
                layer=layer_at_particle(idx)
                self.assertEqual(layer.layer_id,idx)
                self.assertEqual(layer.particle_id,idx)
                self.assertEqual(layer.physical_layer,int(idx>=5184))
                self.assertEqual(layer_at_neuron(layer.native_neuron_start),layer)
                self.assertEqual(layer_at_neuron(layer.native_neuron_stop-1),layer)
                self.assertEqual(
                    layer.native_neuron_stop-layer.native_neuron_start,
                    BASE_SIZE+int(idx<FIRST_EXTRA)
                )
                self.assertEqual(layer.to_wire()["native_neuron_start"],str(layer.native_neuron_start))

    def test_out_of_bounds_and_float_values_fail_closed(self):
        for invalid in (-1, 10368, 1.1, True, False, None, "0"):
            with self.subTest(particle=invalid):
                with self.assertRaises(NativeLayerMembraneError):
                    layer_at_particle(invalid)
        for invalid in (-1, 86805555555, 0.0, True, "0", None):
            with self.subTest(neuron=invalid):
                with self.assertRaises(NativeLayerMembraneError):
                    layer_at_neuron(invalid)

    def test_native_i082_i070_vm81_candidate_is_explicit(self):
        first=bind_explicit_native_neuron(neuron_id=0,nucleus_index=0,particle_id=0)
        last=bind_explicit_native_neuron(neuron_id=NEURON_COUNT-1,nucleus_index=8,particle_id=10367)
        self.assertEqual(first["native_vm81_cell_addresses"],list(range(9)))
        self.assertEqual(last["native_vm81_cell_addresses"],list(range(72,81)))
        self.assertEqual(len(first["i070_candidate_hash216"]),216)
        self.assertEqual(len(first["i085_candidate_hash72"]),72)
        self.assertFalse(first["ordered_neural_relation_admitted"])
        self.assertFalse(first["canonical_state_commit"])
        for options in (
            dict(neuron_id=0,nucleus_index=0,particle_id=5184),
            dict(neuron_id=0,nucleus_index=9,particle_id=0),
            dict(neuron_id=True,nucleus_index=0,particle_id=0),
            dict(neuron_id=0,nucleus_index=0,particle_id=1.0),
        ):
            with self.subTest(options=options):
                with self.assertRaises((NativeLayerMembraneError,ValueError)):
                    bind_explicit_native_neuron(**options)

    def test_candidate_projection_tick_only_bound_explicit_native_events(self):
        empty=projection_tick(1)
        self.assertEqual(empty["nominal_output_fps"],60)
        self.assertEqual(empty["original_simulation_raf_per_visual_frame"],4)
        self.assertEqual(empty["explicit_sample_count"],0)
        self.assertFalse(empty["all_neural_edges_executed"])
        self.assertFalse(empty["native_vm81_commit"])
        self.assertEqual(len(empty["candidate_frame_hash72"]),72)
        valid=[dict(neuron_id=0,nucleus_index=0,particle_id=0)]
        self.assertEqual(projection_tick(2,valid)["explicit_sample_count"],1)
        with self.assertRaises(NativeLayerMembraneError):
            projection_tick(0,valid+valid)
        with self.assertRaises(NativeLayerMembraneError):
            projection_tick(-1)
        with self.assertRaises(NativeLayerMembraneError):
            projection_tick(0,[{"neuron_id":0}])

    def test_original_html_and_audio_simulation_remain_inherited(self):
        info=validate_scene_source()
        self.assertEqual(info["original_html_path"],"examples/ParticleSimulation.html")
        source=HTML.read_text(encoding="utf8")
        self.assertEqual(source.count('<script src="ParticleSimulationNeuralLayerBridge.js"></script>'),1)
        self.assertTrue(source.index("HHS PASS 220 I063") < source.index('src="ParticleSimulationNeuralLayerBridge.js"'))
        for invariant in (
            "function updateSwarmCoupling()", "function updateSpiralParticles()",
            "for(let s=0;s<steps;s++){ updateSpiralParticles();",
            "renderGate=((renderTick%4)===0);",
            "new THREE.InstancedMesh(", "function createParticleHaloBatch(",
            "window.HHSBrownL2=Object.freeze(", 'canvas.id="audioVizOverlay"',
            "G.localIdx=a.frame%5184;", "if(!a){ G.bypasses++; return; }"
        ):
            self.assertIn(invariant,source)

    def test_browser_bigint_inverse_weakmap_and_no_physics_mutation(self):
        node=shutil.which("node")
        if not node:self.skipTest("Node.js unavailable")
        script=r"""
const fs=require("fs"),vm=require("vm"),assert=require("assert");
const js=fs.readFileSync("examples/ParticleSimulationNeuralLayerBridge.js","utf8");
function simulate(incorrect){
  const ps=Array.from({length:10368},(_,i)=>({
    userData:{layer2:i>=5184,velocity:{x:0,y:0,z:0}},
    material:{color:1},position:{x:i,y:-i,z:0}
  }));
  if(incorrect==="layer")ps[5184].userData.layer2=false;
  if(incorrect==="duplicate")ps[3]=ps[2];
  const w={}, ctx={window:w,particles:ps,WeakMap,Set,BigInt,Number,Object,Array,Error,RegExp};
  if(incorrect){assert.throws(()=>vm.runInNewContext(js,ctx));return;}
  const prev=ps[5184].position.x;
  vm.runInNewContext(js,ctx);
  const m=w.HHSNeuralLayerMap;
  assert(m);
  assert.equal(m.diagnostics.original_particles_bound,10368);
  assert.equal(m.diagnostics.neuron_count,"86805555555");
  assert.equal(m.diagnostics.logical_positions,"449999999997120");
  assert.equal(m.diagnostics.nominal_capture_fps,60);
  assert.equal(m.diagnostics.native_sweeps_per_hash216_array,2);
  assert.equal(m.diagnostics.native_layer_ticks_per_sweep,5184);
  assert.equal(m.diagnostics.native_ticks_per_composed_hash216_array,10368);
  assert.equal(m.diagnostics.native_hash216_array_source,"PASS174_NATIVE");
  for(const k of [0,71,72,2592,5183]){
    const pair=m.pairedTick(7,k);
    assert.equal(pair.layer0.layer_id,k);
    assert.equal(pair.layer1.layer_id,5184+k);
    assert.equal(pair.layer0.vm81_cell,Math.floor(k/64));
    assert.equal(pair.layer1.vm81_cell,pair.layer0.vm81_cell);
    assert.equal(pair.layer0.absolute_native_tick,(7n*10368n+BigInt(k)).toString());
    assert.equal(pair.layer1.absolute_native_tick,(7n*10368n+5184n+BigInt(k)).toString());
    assert.equal(pair.common_hash216_array_authority,"NATIVE_PASS174_ONLY");
  }
  assert.throws(()=>m.nativeTickAddress(0,2,0));
  assert.throws(()=>m.nativeTickAddress(0,0,5184));
  assert.throws(()=>m.pairedTick(0,-1));
  assert.equal(m.layerBounds(0).native_neuron_count,"8372450");
  assert.equal(m.layerBounds(4323).native_neuron_count,"8372449");
  for(const i of [0,1,4322,4323,5183,5184,7775,10367]){
    const b=m.layerBounds(i),p=ps[i];
    assert.equal(m.layerOfParticle(p).layer_id,i);
    assert.equal(m.particleOfLayer(i),p);
    assert.equal(m.particleIndexForNeuron(b.native_neuron_start),i);
    assert.equal(m.particleIndexForNeuron((BigInt(b.native_neuron_stop_exclusive)-1n).toString()),i);
  }
  assert.equal(m.audit().passed,true);
  assert.throws(()=>m.particleIndexForNeuron("86805555555"));
  assert.throws(()=>m.particleIndexForNeuron("1.0"));
  assert.throws(()=>m.validateWitnessIngress({authoritative:true,neuron_id:"0"}));
  assert.equal(ps[5184].position.x,prev);
  assert.equal(m.projectPhysicalState(5184).projection_only,true);
}
simulate(null);simulate("layer");simulate("duplicate");
"""
        p=subprocess.run([node,"-e",script],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stdout+"\n"+p.stderr)


if __name__=="__main__":
    unittest.main()
