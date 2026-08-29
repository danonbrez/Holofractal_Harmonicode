#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path

from hhs_runtime.pass187.composition import CompositionAuthority


def receipt(n: int) -> str:
    return f"{n:072x}"


def descriptor(logical_id: str, index: int) -> dict:
    return CompositionAuthority.descriptor(
        logical_object_id=logical_id,
        object_class="benchmark_node",
        modality_set=["data"],
        content_identity=f"content:{logical_id}",
        source_identity=f"source:{logical_id}",
        provenance={"benchmark": "pass187"},
        owner_or_mutation_authority="benchmark",
        permissions=["connect", "replace"],
        inputs=[] if index == 0 else [{"name": "in", "type": "bench/value"}],
        outputs=[{"name": "out", "type": "bench/value"}],
        operations=["execute"],
        dependencies=[],
        state_schema={"type": "object"},
        state={"index": index},
        compatible_egress_targets=["web-app", "project-bundle", "native-cli"],
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as temp:
        db = Path(temp) / "benchmark.sqlite3"
        authority = CompositionAuthority(db, project_id="project.benchmark")
        counter = 1
        try:
            nodes = [f"node.{i:03d}" for i in range(100)]
            for index, logical_id in enumerate(nodes):
                authority.create_object(descriptor(logical_id, index), receipt(counter))
                counter += 1
                if index:
                    authority.connect(
                        edge_id=f"edge.{index-1:03d}.{index:03d}",
                        source_logical_object_id=nodes[index - 1],
                        source_port="out",
                        target_logical_object_id=logical_id,
                        target_port="in",
                        relationship="LIVE",
                        vm81_receipt_hash72=receipt(counter),
                    )
                    counter += 1
            start = time.perf_counter_ns()
            result = authority.recompose(
                [nodes[0]],
                receipt(counter),
                authority_scope="benchmark",
                license_scope="benchmark",
            )["result"]
            elapsed_ns = time.perf_counter_ns() - start
            counter += 1
            if result["executed"] != nodes:
                raise SystemExit("unexpected execution plan")
            if result["unaffected"]:
                raise SystemExit("unexpected unaffected nodes")
            payload = {
                "schema": "HHS_PASS_187_INCREMENTAL_PLANNER_BENCHMARK_V1",
                "nodes": 100,
                "edges": 99,
                "executed_nodes": len(result["executed"]),
                "cache_hits": len(result["cache_hits"]),
                "elapsed_nanoseconds": elapsed_ns,
                "timing_authority": "NONAUTHORITATIVE",
                "semantic_output_authority": "EXACT_INTEGER_IDENTITY_AND_EXECUTION_COUNTS",
                "floating_point_canonical_authority": False,
            }
            print(json.dumps(payload, sort_keys=True))
        finally:
            authority.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
