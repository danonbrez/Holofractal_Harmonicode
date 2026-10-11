"""Pass 220 I085: exact, lazy 10,368-particle to neural-layer native membrane.

Each real ParticleSimulation.html carrier owns ONE layer, not one neuron.
The I082 total 86,805,555,555 neurons is fully addressable by a reversible,
bounded integer partition across these exact 10,368 distinct layers.
Individual I082 VM81 nucleus/edge identities remain explicitly witnessed;
no invented connectome, neuron state, edge execution or canonical commit.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass220_i069_harmonicode_i_tensor_v1 import hash72
from hhs_runtime.hhs_pass220_i082_neural_tensor_graph_v1 import (
    NEURON_COUNT, VM81_WIDTH, RAW_TENSOR, AUTHORITY as I082_AUTHORITY,
    graph_specification, sample_native_neuron, validate_sample_native_neuron,
)

SCHEMA = "HHS_PASS_220_I085_PHYSICS_10368_NEURAL_LAYER_MEMBRANE_V1"
LAYER_COUNT = 10368
LAYER_WIDTH = 5184
NOMINAL_OUTPUT_FPS = 60
PHYSICS_RAF_PER_RENDER = 4
BASE_SIZE, FIRST_EXTRA = divmod(NEURON_COUNT, LAYER_COUNT)
ROOT = Path(__file__).resolve().parents[1]
PHYSICS_HTML = ROOT / "examples" / "ParticleSimulation.html"
NEURAL_JS = ROOT / "examples" / "ParticleSimulationNeuralLayerBridge.js"
EXPECTED_I082 = "HHS_PASS_220_I082_NEURAL_TENSOR_GRAPH_V1"
EXPECTED_I063 = "HHS_PASS_220_I063_BROWN_NOISE_AUDIO_CARRIER_GRAFT_V1"


class NativeLayerMembraneError(ValueError):
    """Fail-closed violation of the inherited particle/neural layer geometry."""


def exact_int(value: Any, name: str) -> int:
    if type(value) is not int:
        raise NativeLayerMembraneError(f"{name} must be an exact integer (no float/bool)")
    return value


@dataclass(frozen=True)
class NeuralLayer:
    layer_id: int
    particle_id: int
    physical_layer: int
    native_neuron_start: int
    native_neuron_stop: int
    neuron_count: int

    def to_wire(self) -> dict[str, Any]:
        # BigInt / exact decimal transport, even if JavaScript Number is used
        # for the bounded 10,368 particle IDs.
        return {
            "schema": SCHEMA,
            "layer_id": self.layer_id,
            "particle_id": self.particle_id,
            "physical_layer": self.physical_layer,
            "native_neuron_start": str(self.native_neuron_start),
            "native_neuron_stop_exclusive": str(self.native_neuron_stop),
            "native_neuron_count": str(self.neuron_count),
        }


def layer_at_particle(particle_id: int) -> NeuralLayer:
    p = exact_int(particle_id, "particle_id")
    if not 0 <= p < LAYER_COUNT:
        raise NativeLayerMembraneError("particle/layer index out of 0..10367")
    count = BASE_SIZE + int(p < FIRST_EXTRA)
    start = p * BASE_SIZE + min(p, FIRST_EXTRA)
    stop = start + count
    if stop > NEURON_COUNT:
        raise NativeLayerMembraneError("native neuron partition escaped I082 range")
    return NeuralLayer(p, p, p // LAYER_WIDTH, start, stop, count)


def layer_at_neuron(neuron_id: int) -> NeuralLayer:
    n = exact_int(neuron_id, "neuron_id")
    if not 0 <= n < NEURON_COUNT:
        raise NativeLayerMembraneError("neuron_id outside inherited I082 domain")
    wide_end = FIRST_EXTRA * (BASE_SIZE + 1)
    layer = (n // (BASE_SIZE + 1) if n < wide_end
             else FIRST_EXTRA + ((n - wide_end) // BASE_SIZE))
    result = layer_at_particle(layer)
    if not result.native_neuron_start <= n < result.native_neuron_stop:
        raise NativeLayerMembraneError("reverse neuron/layer membership diverged")
    return result


def validate_scene_source() -> dict[str, Any]:
    if not PHYSICS_HTML.is_file() or not NEURAL_JS.is_file():
        raise NativeLayerMembraneError("original HTML or read-only JS layer membrane missing")
    source = PHYSICS_HTML.read_text(encoding="utf-8")
    for token in (
        "function updateSwarmCoupling()", "function updateSpiralParticles()",
        "updateTesseract();", "function constructorScan()",
        "initSpiralParticles(false)", "initExchangeNuclei(false)",
        "initSpiralParticles(true)", "initExchangeNuclei(true)",
        "renderGate=((renderTick%4)===0);",
        "syncParticleRenderBatches();",
        "HHS_PASS_220_I063_BROWN_NOISE_AUDIO_CARRIER_GRAFT_V1",
        'id="audioVizOverlay"',  # actual HTML creates the overlay via JS below
    ):
        # Overlay is dynamically created rather than a literal HTML element.
        if token == 'id="audioVizOverlay"':
            if 'canvas.id="audioVizOverlay"' not in source:
                raise NativeLayerMembraneError("original waveform canvas removed")
        elif token not in source:
            raise NativeLayerMembraneError(f"original scene invariant missing: {token}")
    if '<script src="ParticleSimulationNeuralLayerBridge.js"></script>' not in source:
        raise NativeLayerMembraneError("native neural layer JS ingress not loaded by original HTML")
    source_sha = hashlib.sha256(PHYSICS_HTML.read_bytes()).hexdigest()
    return {
        "original_html_path": "examples/ParticleSimulation.html",
        "original_html_sha256": source_sha,
        "read_only_bridge_path": "examples/ParticleSimulationNeuralLayerBridge.js",
        "read_only_bridge_sha256": hashlib.sha256(NEURAL_JS.read_bytes()).hexdigest(),
        "original_physics_retained": True,
        "original_waveform_and_i063_retained": True,
    }


def exact_cover() -> dict[str, Any]:
    graph = graph_specification()
    if graph["schema"] != EXPECTED_I082 or graph["neuron_count"] != NEURON_COUNT:
        raise NativeLayerMembraneError("I082 exact neural specification diverged")
    if graph["raw_tensor"] != RAW_TENSOR or graph["positions_per_neuron"] != VM81_WIDTH:
        raise NativeLayerMembraneError("I082 tensor order/VM81 geometry diverged")
    if graph["authority"] != I082_AUTHORITY or not I082_AUTHORITY["candidate_only"]:
        raise NativeLayerMembraneError("I082 candidate authority unexpectedly changed")
    next_start = 0
    capacities = set()
    for particle_id in range(LAYER_COUNT):
        layer = layer_at_particle(particle_id)
        if layer.layer_id != layer.particle_id or layer.native_neuron_start != next_start:
            raise NativeLayerMembraneError("particle to neuron partition has a gap/overlap")
        if layer.physical_layer != int(particle_id >= LAYER_WIDTH):
            raise NativeLayerMembraneError("original 5184+5184 physical layer ordering changed")
        capacities.add(layer.neuron_count)
        next_start = layer.native_neuron_stop
        if layer_at_neuron(layer.native_neuron_start).layer_id != particle_id:
            raise NativeLayerMembraneError("reverse start address mismatch")
        if layer_at_neuron(layer.native_neuron_stop - 1).layer_id != particle_id:
            raise NativeLayerMembraneError("reverse end address mismatch")
    if next_start != NEURON_COUNT or capacities != {BASE_SIZE, BASE_SIZE + 1}:
        raise NativeLayerMembraneError("I082 full neuron count not covered exactly")
    return {
        "schema": SCHEMA,
        "total_neurons": str(NEURON_COUNT),
        "total_logical_vm81_positions": str(NEURON_COUNT * VM81_WIDTH),
        "exact_layer_count": LAYER_COUNT,
        "particles_per_physical_layer": LAYER_WIDTH,
        "base_neurons_per_layer": str(BASE_SIZE),
        "extra_neuron_layers": FIRST_EXTRA,
        "first_neuron_id": "0",
        "last_neuron_id": str(NEURON_COUNT - 1),
        "complete_interval_cover": True,
        "reverse_membership_verified": True,
        "full_neural_graph_materialized": False,
    }


def bind_explicit_native_neuron(
    *, neuron_id: int, nucleus_index: int, particle_id: int,
) -> dict[str, Any]:
    """One real I082/I070 candidate derivation, no fabricated connectivity."""
    layer = layer_at_neuron(neuron_id)
    if layer.particle_id != exact_int(particle_id, "particle_id"):
        raise NativeLayerMembraneError("native neuron cannot cross layer/particle boundary")
    nucleus = exact_int(nucleus_index, "nucleus_index")
    sample = sample_native_neuron(neuron_id, nucleus)
    validate_sample_native_neuron(sample)
    if sample["authority"] != I082_AUTHORITY or not sample["inherited_hydration_exact"]:
        raise NativeLayerMembraneError("I082 inherited VM81 witness invalid")
    wire = layer.to_wire()
    candidate = {
        "schema": SCHEMA + "_SAMPLED_NATIVE_CANDIDATE",
        "particle_layer": wire,
        "native_neuron_id": str(neuron_id),
        "explicit_nucleus_index": nucleus,
        "native_vm81_cell_addresses": sample["vm81_cell_addresses"],
        "i070_candidate_hash216": sample["inherited_i070_candidate_hash216"],
        "i070_binding_hash72": sample["inherited_i070_binding_hash72"],
        "i082_sample_candidate_hash72": sample["sample_candidate_hash72"],
        "ordered_neural_relation_admitted": False,
        "canonical_state_commit": False,
    }
    candidate["i085_candidate_hash72"] = hash72(candidate)
    return candidate


def projection_tick(
    frame_id: int, observations: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """One 60Hz presentation tick with only explicitly identified native samples.

    Does not infer or execute edges, train 86B cells, or mutate 3D physics.
    """
    tick = exact_int(frame_id, "frame_id")
    if tick < 0:
        raise NativeLayerMembraneError("negative frame_id")
    if len(observations) > LAYER_COUNT:
        raise NativeLayerMembraneError("one frame cannot bind >10368 distinct layers")
    bound = []
    seen = set()
    for item in observations:
        if not isinstance(item, Mapping) or set(item) != {"neuron_id", "nucleus_index", "particle_id"}:
            raise NativeLayerMembraneError("native sample must carry exact three binding fields")
        w = bind_explicit_native_neuron(**item)
        index = w["particle_layer"]["particle_id"]
        if index in seen:
            raise NativeLayerMembraneError("duplicate particle layer sample on one frame")
        seen.add(index)
        bound.append(w)
    result = {
        "schema": SCHEMA + "_60HZ_PROJECTION_TICK",
        "frame_id": tick,
        "nominal_output_fps": NOMINAL_OUTPUT_FPS,
        "original_simulation_raf_per_visual_frame": PHYSICS_RAF_PER_RENDER,
        "physical_particle_count": LAYER_COUNT,
        "explicit_sample_count": len(bound),
        "samples": bound,
        "all_neural_edges_executed": False,
        "presentation_only": True,
        "native_vm81_commit": False,
        "hash72_hash216_persistence": False,
    }
    result["candidate_frame_hash72"] = hash72(result)
    return result


def self_test() -> dict[str, Any]:
    cover = exact_cover()
    source = validate_scene_source()
    first = bind_explicit_native_neuron(neuron_id=0, nucleus_index=0, particle_id=0)
    last = bind_explicit_native_neuron(
        neuron_id=NEURON_COUNT-1, nucleus_index=8, particle_id=LAYER_COUNT-1
    )
    return {
        "schema": SCHEMA + "_SELF_TEST",
        "status": "PASS",
        "coverage": cover,
        "source": source,
        "first_candidate_hash72": first["i085_candidate_hash72"],
        "last_candidate_hash72": last["i085_candidate_hash72"],
        "frame_0": projection_tick(0)["candidate_frame_hash72"],
    }


if __name__ == "__main__":
    print(json.dumps(self_test(), sort_keys=True, indent=2))
