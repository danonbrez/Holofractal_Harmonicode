#!/usr/bin/env python3
"""Pass 205 production closure validation and evidence writer."""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import tempfile
import time
from typing import Any

from hhs_backend.runtime.hhs_pass205_accelerator_translation_v1 import (
    Pass205AcceleratorTranslation,
)
from hhs_backend.runtime.hhs_pass205_continuation_runtime_v1 import (
    CLOSURE_CLASSIFICATION,
    CONTRACT,
    Pass205ContinuationRuntime,
)
from hhs_python.runtime.hhs_pass205_continuation_bridge import (
    CELL_COUNT,
    CONTROL_COUNT,
    Q_COUNT,
    STATE_BITS,
    Pass205NativeBridge,
    build_native_library,
)


def _event(cell: int, mask: int, control: int) -> dict[str, int]:
    return {"cell": cell, "xor_mask": mask, "control_g": control}


def run(*, db_path: pathlib.Path, include_hosted: bool = True) -> dict[str, Any]:
    started = time.perf_counter_ns()
    library = build_native_library(force=True)
    native = Pass205NativeBridge()

    # Exact full hydration address bijection.
    q_checks = 0
    for s in range(STATE_BITS):
        for g in range(CONTROL_COUNT):
            q = native.q_address(s, g)
            if q != 243 * s + g or native.q_decode(q) != (s, g):
                raise AssertionError(f"q bijection failed at s={s}, g={g}, q={q}")
            q_checks += 1
    if q_checks != Q_COUNT:
        raise AssertionError("q address count mismatch")

    runtime = Pass205ContinuationRuntime(db_path)
    genesis = runtime.snapshot(runtime.genesis_root216)
    chain = [genesis]
    for generation in range(1, 73):
        parent = chain[-1]
        cell_a = generation % CELL_COUNT
        cell_b = (generation * 17) % CELL_COUNT
        if cell_b == cell_a:
            cell_b = (cell_b + 1) % CELL_COUNT
        events = [
            _event(cell_a, 1 << (generation % 64), generation % 243),
            _event(cell_b, 1 << ((generation * 5) % 64), (generation * 7) % 243),
        ]
        child = runtime.advance(
            parent_root216=parent["continuation_root216"],
            expected_parent_receipt_hash72=parent["receipt_hash72"],
            events=events,
        )
        verification = runtime.verify(child["continuation_root216"])
        if not verification["ok"]:
            raise AssertionError(verification)
        chain.append(child)

    branch_parent = chain[36]
    branch_a = runtime.branch(
        parent_root216=branch_parent["continuation_root216"],
        expected_parent_receipt_hash72=branch_parent["receipt_hash72"],
        events=[_event(3, 0xA5A5, 72)],
    )
    branch_b = runtime.branch(
        parent_root216=branch_parent["continuation_root216"],
        expected_parent_receipt_hash72=branch_parent["receipt_hash72"],
        events=[_event(3, 0x5A5A, 216)],
    )
    if branch_a["continuation_root216"] == branch_b["continuation_root216"]:
        raise AssertionError("branch identity collapsed")

    replay = runtime.replay(chain[-1]["continuation_root216"])
    if not replay["ok"] or replay["generation_count"] != 73:
        raise AssertionError(replay)

    inverse = runtime.reverse(chain[-1]["continuation_root216"])
    if inverse["content_root216"] != chain[-2]["content_root216"]:
        raise AssertionError("inverse continuation did not restore prior content")
    if inverse["continuation_root216"] == chain[-2]["continuation_root216"]:
        raise AssertionError("inverse continuation rewrote prior identity")

    target = list(chain[20]["state_words"])
    target[60] ^= 0x10000000001
    retrieval = runtime.retrieve(target_state_words=target, top_k=32)
    hydrated = runtime.hydrate_target(
        target_state_words=target,
        controls_by_cell={"60": 81},
        top_k=32,
    )
    if hydrated["snapshot"]["state_words"] != target:
        raise AssertionError("retrieval hydration target mismatch")
    if not runtime.verify(hydrated["snapshot"]["continuation_root216"])["ok"]:
        raise AssertionError("retrieval-hydrated continuation failed verification")

    translation = Pass205AcceleratorTranslation()
    states = [snapshot["state_words"] for snapshot in chain[1:9]]
    projections = [snapshot["projection_channels"] for snapshot in chain[1:9]]
    deltas = [
        [_event(index, 1 << (index % 32), index % 243)]
        for index in range(8)
    ]
    batch = translation.pack_batch(states=states, projections=projections, deltas=deltas)
    accelerator_result = translation.execute_cpu_reference(batch)
    if not accelerator_result["ok"]:
        raise AssertionError(accelerator_result)
    dispatches = {
        backend: translation.dispatch_descriptor(backend, batch)
        for backend in ("CUDA", "HIP", "VULKAN_COMPUTE", "WEBGPU", "METAL")
    }
    if any(value["gpu_may_commit_hash72"] for value in dispatches.values()):
        raise AssertionError("accelerator backend was allowed to commit Hash72")

    hosted_routes: list[str] = []
    if include_hosted:
        from hhs_backend.application_ide_server import app

        hosted_routes = sorted({str(getattr(route, "path", "")) for route in app.router.routes})
        required = {
            "/api/runtime/continuation/status",
            "/api/runtime/continuation/snapshots/{continuation_root216:path}",
            "/api/runtime/continuation/graph/{continuation_root216:path}",
            "/api/runtime/continuation/projections/{continuation_root216:path}",
            "/api/runtime/continuation/retrieve",
            "/api/runtime/continuation/hydrate",
            "/api/runtime/continuation/advance",
            "/api/runtime/continuation/branch",
            "/api/runtime/continuation/reverse",
            "/api/runtime/continuation/replay",
            "/api/runtime/continuation/verify",
            "/api/runtime/continuation/studio",
        }
        missing = sorted(required - set(hosted_routes))
        if missing:
            raise AssertionError({"missing_hosted_routes": missing})
        schema_paths = set(app.openapi().get("paths", {}))
        normalized_required = {path.replace(":path", "") for path in required if path != "/api/runtime/continuation/studio"}
        missing_openapi = sorted(normalized_required - schema_paths)
        if missing_openapi:
            raise AssertionError({"missing_openapi_routes": missing_openapi})

    elapsed_ns = time.perf_counter_ns() - started
    status = runtime.status()
    checks = {
        "native_library_built": library.is_file(),
        "state_bits_exact": status["state_bits"] == 5184,
        "q_bijection_complete": q_checks == 1_259_712,
        "projection_channels_exact": status["projection_channel_count"] == 32,
        "continuation_chain_verified": all(runtime.verify(item["continuation_root216"])["ok"] for item in chain),
        "branch_identity_distinct": branch_a["continuation_root216"] != branch_b["continuation_root216"],
        "replay_verified": replay["ok"],
        "inverse_history_preserved": inverse["continuation_root216"] != chain[-2]["continuation_root216"],
        "retrieval_exact_rerank": retrieval["exact_rerank_applied"],
        "retrieval_hydration_verified": hydrated["snapshot"]["state_words"] == target,
        "accelerator_cpu_oracle": accelerator_result["ok"],
        "gpu_commit_forbidden": all(not value["gpu_may_commit_hash72"] for value in dispatches.values()),
        "hosted_routes_exposed": bool(hosted_routes),
        "no_float_canonical_authority": status["native_abi"]["canonical_float_fields"] == 0,
        "single_vm81_mutation_authority": status["single_vm81_mutation_authority"],
        "single_hash72_commit_stream": status["single_ordered_hash72_commit_stream"],
        "vercel_not_acceptance_gate": status["external_vercel_quota_is_not_acceptance_gate"],
    }
    closed = all(checks.values())
    return {
        "schema": "HHS_PASS_205_PRODUCTION_VALIDATION_RECEIPT_V1",
        "contract": CONTRACT,
        "classification": CLOSURE_CLASSIFICATION if closed else "HHS_PASS_205_PRODUCTION_VALIDATION_FAILED",
        "ok": closed,
        "closed": closed,
        "checks": checks,
        "measurements": {
            "q_addresses_verified": q_checks,
            "ordered_chain_generations": len(chain),
            "stored_snapshots": status["snapshot_count"],
            "lineage_edges": status["lineage_edge_count"],
            "retrieval_exact_delta_cost": retrieval["exact_delta_cost"],
            "accelerator_batch_size": batch.batch_size,
            "accelerator_transfer_bytes": batch.transfer_bytes,
            "accelerator_dense_transfer_bytes": batch.dense_transfer_bytes,
            "accelerator_transfer_reduction_ratio": batch.dense_transfer_bytes / batch.transfer_bytes,
            "hosted_route_count": len(hosted_routes),
            "elapsed_ns": elapsed_ns,
        },
        "runtime_status": status,
        "terminal_root216": chain[-1]["continuation_root216"],
        "terminal_receipt_hash72": chain[-1]["receipt_hash72"],
        "retrieval_root216": retrieval["retrieval_root216"],
        "hydrated_root216": hydrated["snapshot"]["continuation_root216"],
        "physical_gpu_execution_claimed": False,
        "external_vercel_quota_is_not_acceptance_gate": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=pathlib.Path, required=True)
    parser.add_argument("--db", type=pathlib.Path)
    parser.add_argument("--skip-hosted", action="store_true")
    args = parser.parse_args()
    db_path = args.db or pathlib.Path(tempfile.mkdtemp(prefix="hhs-pass205-")) / "continuation.sqlite3"
    os.environ["HHS_PASS205_DB"] = str(db_path)
    result = run(db_path=db_path, include_hosted=not args.skip_hosted)
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
