"""I086 native 1.39/1.40 composition benchmark; no synthetic graph implementation.

Reports reference baseline native edge hydration vs composed authenticated orbit
under the same persisted graph and identical two edges.
"""
from __future__ import annotations
from pathlib import Path
from statistics import median
from tempfile import TemporaryDirectory
from time import perf_counter_ns
import json

from hhs_backend.runtime.hhs_pass219_lane5_recursive_hash216_composition_graph_1_40 import (
    Pass219Lane5RecursiveHash216CompositionGraph,
)
from hhs_runtime.hhs_pass220_i086_native_orbit_composition_v1 import (
    compose_authenticated_orbit,
)


def benchmark(iterations: int = 10) -> dict:
    if type(iterations) is not int or iterations < 1:
        raise ValueError("positive integer iterations required")
    mask = (1 << 64) - 1
    initial = [((73 * 0x9E3779B97F4A7C15) + i * 0x517CC1B727220A95) & mask
               for i in range(81)]
    step = [{"cell": 2, "control_g": 10, "xor_mask": 1 << 5}]
    with TemporaryDirectory(prefix="hhs-i086-") as tmp:
        with Pass219Lane5RecursiveHash216CompositionGraph(
            Path(tmp) / "graph", vector_key=bytes(range(32)),
            backend="CPU_REFERENCE",
        ) as graph:
            a = graph.memory.jump_store.build_validated_jump(
                jump_id="bench-forward", parent_state=initial, steps=[step],
                tick=5005, cycle_index=48, layer_index=7,
            )
            graph.memory.persist_validated_jump(parent_state=initial, jump=a)
            child = graph.memory.reuse(current_state=initial, jump_id=a.jump_id)["child_state"]
            b = graph.memory.jump_store.build_validated_jump(
                jump_id="bench-backward", parent_state=child, steps=[step],
                tick=5006, cycle_index=48, layer_index=7,
            )
            graph.memory.persist_validated_jump(parent_state=child, jump=b)
            if b.child_hash216 != graph.native.state_root(initial):
                raise RuntimeError("benchmark fixture did not close")
            baseline, composed = [], []
            for i in range(iterations):
                t = perf_counter_ns()
                one = graph.memory.reuse(current_state=initial, jump_id=a.jump_id)
                two = graph.memory.reuse(current_state=one["child_state"], jump_id=b.jump_id)
                if graph.native.state_root(two["child_state"]) != graph.native.state_root(initial):
                    raise RuntimeError("baseline did not close")
                baseline.append(perf_counter_ns() - t)
                t = perf_counter_ns()
                result = compose_authenticated_orbit(
                    graph=graph, initial_state=initial,
                    segments=[[a.jump_id], [b.jump_id]],
                    frame_id=i, tick=0, cycle_index=0,
                )
                if not result["orbit_closed"]:
                    raise RuntimeError("composition did not close")
                composed.append(perf_counter_ns() - t)
    return {
        "schema": "HHS_PASS220_I086_NATIVE_ORBIT_BENCHMARK_V1",
        "iterations": iterations,
        "baseline_median_ns": int(median(baseline)),
        "composition_median_ns": int(median(composed)),
        "baseline_samples_ns": baseline,
        "composition_samples_ns": composed,
        "native_1_39_1_40_persistent_edges": True,
        "represented_transitions_per_sample": 2,
        "candidate_only": True,
        "gpu_benchmarked": False,
        "signed_vm81_admission_benchmarked": False,
    }


if __name__ == "__main__":
    print(json.dumps(benchmark(), sort_keys=True))
