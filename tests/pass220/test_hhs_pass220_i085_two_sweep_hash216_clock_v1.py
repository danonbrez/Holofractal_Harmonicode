"""I085 one Pass174 Hash216 array binds two exact 5,184-position sweeps."""
from __future__ import annotations

from time import perf_counter_ns

import pytest

from hhs_runtime.hhs_pass220_i085_two_sweep_hash216_clock_v1 import (
    SCHEMA, address_tick, paired_tick, compose_single_hash216_array,
    validate_two_sweep_exact_cover, inherited_hash216_generator,
)
from hhs_runtime.hhs_pass220_i085_particle_neural_layer_membrane_v1 import (
    NativeLayerMembraneError, layer_at_particle,
)
from hhs_runtime.hhs_pass220_holographic_hash216_query_v1 import split_hash216


def test_one_inherited_hash216_array_covers_both_5184_sweeps():
    x=compose_single_hash216_array(frame_id=0)
    assert x["schema"]==SCHEMA
    assert x["one_hash216_array_per_two_sweeps"]
    assert x["native_tick_count"]==10368
    assert x["native_ticks_per_sweep"]==5184
    assert x["sweep_count"]==2
    assert x["phase_coordinate_count"]==5184
    assert x["neural_address_count"]=="86805555555"
    assert x["nominal_presentation_fps"]==60
    assert x["hash216_array_character_indexes"]==216
    assert x["source_i070_candidate_hash216"]==inherited_hash216_generator()
    assert [len(lane) for lane in split_hash216(x["source_i070_candidate_hash216"])]==[72,72,72]
    assert x["ordered_lane_roles"]==["PREVIOUS","CHANGE","RECEIPT"]
    assert len(x["hash216_array_index_root_sha256"])==64
    assert len(x["hash216_array_logical_identity_sha256"])==64
    assert x["candidate_only"]
    assert not x["canonical_vm81_commit"]
    assert not x["full_weighted_neural_execution_proven"]
    assert not x["realtime_60fps_native_neural_latency_proven"]
    assert x==compose_single_hash216_array(frame_id=0)


def test_address_tick_at_boundary_and_exact_inverse():
    for i in (0,1,71,72,2591,2592,4322,4323,5183):
        pair=paired_tick(frame_id=12,position5184=i)
        assert pair["same_hash72_vm81_coordinate"]
        for sweep,label in ((0,"layer0"),(1,"layer1")):
            a=pair[label]
            p=sweep*5184+i
            layer=layer_at_particle(p)
            assert a["schema"]==SCHEMA+"_TICK_ADDRESS"
            assert a["sweep"]==sweep and a["position5184"]==i
            assert a["native_tick_in_array"]==p
            assert a["absolute_native_tick"]==12*10368+p
            assert a["physical_particle_layer"]==p
            assert a["vm81_cell"]==i//64
            assert a["vm81_local64"]==i%64
            assert a["hash72_row"]==i//72
            assert a["hash72_column"]==i%72
            assert a["mirror5184"]==5183-i
            assert a["neuron_interval_start"]==str(layer.native_neuron_start)
            assert a["neuron_interval_stop_exclusive"]==str(layer.native_neuron_stop)
            assert a["native_neuron_count"]==str(layer.neuron_count)


def test_native_two_sweep_full_10368_cover_and_repeated_frame():
    for frame in (0,1,60):
        r=validate_two_sweep_exact_cover(frame)
        assert r["full_exact_cover"]
        assert r["addresses_verified"]==10368
        assert r["sweep_count"]==2
        assert r["no_dense_neuron_iteration"]
        assert r["neuron_addresses_covered"]=="86805555555"
    a=compose_single_hash216_array(frame_id=1)
    b=compose_single_hash216_array(frame_id=2)
    assert a["source_i070_candidate_hash216"]==b["source_i070_candidate_hash216"]
    assert a["hash216_array_logical_identity_sha256"]!=b["hash216_array_logical_identity_sha256"]
    assert a["hash216_array_index_root_sha256"]!=b["hash216_array_index_root_sha256"]


@pytest.mark.parametrize("sweep,position,frame",[
    (-1,0,0),(2,0,0),(0,-1,0),(1,5184,0),
    (0,0,-1),(True,0,0),(0,0,1.0),("0",0,0),
])
def test_bad_ticks_fail_closed(sweep,position,frame):
    with pytest.raises(NativeLayerMembraneError):
        address_tick(frame_id=frame,sweep=sweep,position5184=position)


def test_native_single_array_60hz_candidate_metadata_calibration(capsys):
    # Observational only. Per-frame source cache warm; exclude unrelated CI
    # cold startup. Do not conflate this with execution of neuron weights,
    # signed VM81 admission or GPU/browser frame time.
    compose_single_hash216_array(frame_id=0)
    measurements=[]
    for frame in range(1,21):
        start=perf_counter_ns()
        meta=compose_single_hash216_array(frame_id=frame)
        measurements.append(perf_counter_ns()-start)
        assert meta["one_hash216_array_per_two_sweeps"]
    measurements.sort()
    report={
        "schema":SCHEMA+"_METADATA_TIMING_OBSERVATION",
        "sample_count":len(measurements),
        "max_ns":measurements[-1],
        "p95_ns":measurements[18],
        "nominal_frame_budget_ns":1_000_000_000//60,
        "cpu_metadata_only_within_budget":measurements[-1] <= 1_000_000_000//60,
        "full_neural_runtime_latency_proven":False,
    }
    print(report)
    assert report["sample_count"]==20
