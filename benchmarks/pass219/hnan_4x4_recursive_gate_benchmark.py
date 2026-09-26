from __future__ import annotations

import argparse
import json
from time import perf_counter

from hhs_runtime.pass219.hnan_4x4_recursive_gate_v1 import (
    TENSOR_01,
    materialize_xy_view,
    materialize_xy_view_reference,
    recursive_two_view,
    recursive_two_view_reference,
)


def _time(fn, iterations: int) -> float:
    start = perf_counter()
    for _ in range(iterations):
        fn()
    return perf_counter() - start


def run(iterations: int) -> dict[str, object]:
    recursive_source = (
        "Envelope",
        TENSOR_01,
        ("Quotient", 1, 0),
    )

    assert materialize_xy_view_reference() == materialize_xy_view()
    assert (
        recursive_two_view_reference(recursive_source)
        == recursive_two_view(recursive_source)
    )

    recursive_two_view(recursive_source)

    baseline_materialize = _time(
        materialize_xy_view_reference,
        iterations,
    )
    cached_materialize = _time(
        materialize_xy_view,
        iterations,
    )
    baseline_recursive = _time(
        lambda: recursive_two_view_reference(recursive_source),
        iterations,
    )
    cached_recursive = _time(
        lambda: recursive_two_view(recursive_source),
        iterations,
    )

    return {
        "schema": "HHS_PASS219_HNAN_4X4_BENCHMARK_V1",
        "iterations": iterations,
        "parity": True,
        "materialize_reference_seconds": baseline_materialize,
        "materialize_cached_seconds": cached_materialize,
        "materialize_speedup":
            baseline_materialize / cached_materialize,
        "recursive_reference_seconds": baseline_recursive,
        "recursive_cached_seconds": cached_recursive,
        "recursive_speedup":
            baseline_recursive / cached_recursive,
        "optimization":
            "immutable canonical view + memoized structural recursion",
        "semantic_change": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=100000)
    args = parser.parse_args()
    if args.iterations < 1:
        raise SystemExit("--iterations must be positive")
    print(json.dumps(run(args.iterations), sort_keys=True))


if __name__ == "__main__":
    main()
