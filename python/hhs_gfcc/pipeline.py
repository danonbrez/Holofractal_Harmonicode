from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

from .core import (
    CollisionObject,
    build_collision_constraint,
    build_delta369,
    build_dependency_graph,
    build_qudit9,
    build_vm81,
    canonical_bytes,
    digest256,
    enforce_collision,
    fibonacci_ratio,
    generate_shader_source,
    inherited_hash72,
    index_hash216,
    make_receipt,
    parameter_identity,
    project_hash72,
    replay_workload,
    shader_projection,
    stable,
    validate_spec,
)
from .dependencies import evaluate_dependency_graph
from .schema import load_canonical_spec


def run_spec_workload(
    spec: Mapping[str, Any],
    authority_root: str = "HHS_PASS_152_AUTHORITY_ROOT",
) -> dict[str, Any]:
    normalized = stable(spec)
    validation = validate_spec(normalized)
    graph = build_dependency_graph(normalized)
    shell = evaluate_dependency_graph(normalized, graph)
    ratio = fibonacci_ratio(int(normalized["fibonacci_stage"]))
    delta = build_delta369(normalized)
    qudit = build_qudit9(delta)
    vm81 = build_vm81(qudit, delta, ratio)
    parameters = parameter_identity(ratio, delta)
    hash72 = project_hash72(vm81, shell, authority_root)
    hash216 = index_hash216(vm81, hash72, delta, ratio, authority_root)
    shader = {
        "source": generate_shader_source(ratio),
        "projection": shader_projection(ratio),
    }
    object_a = CollisionObject(
        "A", 0, 0, 65536, 65536, ratio, 6, 40, hash72["value"], hash216["value"]
    )
    object_b = CollisionObject(
        "B", 98304, 0, 65536, 65536, ratio, 9, 41, hash72["value"], hash216["value"]
    )
    collision = build_collision_constraint(object_a, object_b)
    enforcement = enforce_collision(object_a, object_b, collision)
    operations = [
        ("GFCC_SOURCE_SPEC", normalized, validation),
        ("GFCC_DEPENDENCY_GRAPH", normalized, graph),
        ("GFCC_SHELL_CLOSURE", graph, shell),
        ("GFCC_DELTA369", normalized["delta369"], delta),
        ("GFCC_NONARY_QUDIT", delta, qudit),
        ("GFCC_VM81_CONSTRUCTION", qudit, vm81),
        ("GFCC_HASH72_PROJECTION", vm81, hash72),
        ("GFCC_HASH216_INDEX", hash72, hash216),
        ("GFCC_SHADER_CODEGEN", ratio.to_dict(), shader),
        (
            "GFCC_COLLISION_CONSTRUCTION",
            [asdict(object_a), asdict(object_b)],
            collision,
        ),
        ("GFCC_COLLISION_ENFORCEMENT", collision, enforcement),
    ]
    receipts: list[dict[str, Any]] = []
    predecessor = "0" * 64
    for sequence, (operation, inputs, outputs) in enumerate(operations, start=1):
        receipt = make_receipt(operation, sequence, predecessor, inputs, outputs)
        receipts.append(receipt)
        predecessor = receipt["receipt_digest"]
    canonical_result = stable(
        {
            "spec": normalized,
            "graph": graph,
            "shell": shell,
            "stage_ratio": ratio.to_dict(),
            "parameter_identity": parameters,
            "delta369": delta,
            "qudit9": qudit,
            "vm81": vm81,
            "hash72": hash72,
            "hash216": hash216,
            "shader": shader,
            "collision": collision,
            "enforcement": enforcement,
            "receipts": receipts,
            "authority_root": authority_root,
            "source_ingestion": {
                "mode": "JSON_FILE",
                "source_digest": digest256(normalized),
                "source_hash72": inherited_hash72(canonical_bytes(normalized)),
            },
        }
    )
    return stable(
        {
            **canonical_result,
            "canonical_result_digest": digest256(canonical_result),
            "canonical_result_hash72": inherited_hash72(canonical_bytes(canonical_result)),
        }
    )


def run_canonical_file_workload(
    repo: Path,
    authority_root: str = "HHS_PASS_152_AUTHORITY_ROOT",
) -> dict[str, Any]:
    return run_spec_workload(load_canonical_spec(repo), authority_root)


def replay_canonical_file_workload(repo: Path, original: Mapping[str, Any]) -> dict[str, Any]:
    replayed = run_canonical_file_workload(repo, str(original["authority_root"]))
    match = (
        replayed["canonical_result_digest"] == original["canonical_result_digest"]
        and replayed["canonical_result_hash72"] == original["canonical_result_hash72"]
    )
    return {
        "match": match,
        "expected_digest": original["canonical_result_digest"],
        "observed_digest": replayed["canonical_result_digest"],
        "expected_hash72": original["canonical_result_hash72"],
        "observed_hash72": replayed["canonical_result_hash72"],
        "classification": "IMPLEMENTED_AND_EXECUTION_VERIFIED" if match else "REPLAY_MISMATCH",
    }


__all__ = [
    "run_spec_workload",
    "run_canonical_file_workload",
    "replay_canonical_file_workload",
]
