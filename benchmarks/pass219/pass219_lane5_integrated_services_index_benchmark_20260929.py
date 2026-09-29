from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import resource
import statistics
import subprocess
import tempfile
import time
from typing import Any, Callable, Iterable

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "HHS_PASS219_LANE5_INTEGRATED_SERVICES_INDEX_BENCHMARK_20260929_V1"
QUERIES = (
    "hash216",
    "lean",
    "wordnet",
    "physics",
    "hydration",
    "semantic",
    "constructor",
    "vm81",
    "rna",
)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _percentile(values: list[int], numerator: int, denominator: int) -> int:
    ordered = sorted(values)
    if not ordered:
        return 0
    index = ((len(ordered) - 1) * numerator) // denominator
    return int(ordered[index])


def _timed(fn: Callable[[], Any]) -> tuple[int, Any]:
    started = time.perf_counter_ns()
    value = fn()
    return time.perf_counter_ns() - started, value


def _loop(fn: Callable[[], Any], iterations: int) -> dict[str, Any]:
    samples: list[int] = []
    first = None
    for index in range(iterations):
        elapsed, value = _timed(fn)
        if index == 0:
            first = value
        elif value != first:
            raise RuntimeError("benchmark replay drift")
        samples.append(elapsed)
    total = sum(samples)
    return {
        "iterations": iterations,
        "total_ns": total,
        "median_ns": int(statistics.median(samples)),
        "p95_ns": _percentile(samples, 95, 100),
        "min_ns": min(samples),
        "max_ns": max(samples),
        "ops_per_second_floor": (iterations * 1_000_000_000) // max(1, total),
        "replay_equal": True,
        "result": first,
    }


def _git_identity() -> tuple[str, str]:
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    tree = subprocess.check_output(
        ["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True
    ).strip()
    return commit, tree


def _runner_identity() -> dict[str, Any]:
    cpu_model = ""
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        for line in cpuinfo.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("model name"):
                cpu_model = line.split(":", 1)[-1].strip()
                break
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "logical_cpu_count": os.cpu_count(),
        "cpu_model": cpu_model,
    }


def benchmark_repository_index(
    *,
    search_rounds: int,
    positional_iterations: int,
) -> dict[str, Any]:
    from hhs_backend.runtime.hhs_pass219_lane5_repository_hydration_knowledge_graph_1_69 import (
        Lane5RepositoryHydrationKnowledgeDatabase,
    )

    graph_path = ROOT / "artifacts/repository_index/REPOSITORY_HASH216_DEPENDENCY_GRAPH.json"
    knowledge_path = ROOT / "artifacts/repository_index/LANE5_HASH216_HYDRATION_KNOWLEDGE_GRAPH.json"
    if not graph_path.is_file() or not knowledge_path.is_file():
        raise RuntimeError("repository index artifacts missing")

    graph_bytes = graph_path.read_bytes()
    knowledge_bytes = knowledge_path.read_bytes()

    graph_parse_ns, graph = _timed(lambda: json.loads(graph_bytes))
    knowledge_parse_ns, knowledge = _timed(lambda: json.loads(knowledge_bytes))
    counts = knowledge["counts"]
    nodes = list(knowledge["capabilities"]) + list(knowledge["constructors"])
    expected_positions = (
        int(counts["capabilities"])
        + int(counts["constructors"])
        + int(counts["knowledge_edges"])
    ) * 216

    with tempfile.TemporaryDirectory(prefix="hhs-lane5-index-bench-") as td:
        db_path = Path(td) / "lane5.sqlite3"
        with Lane5RepositoryHydrationKnowledgeDatabase(db_path) as db:
            hydrate_ns, status = _timed(
                lambda: db.hydrate(
                    dependency_graph=graph,
                    knowledge_projection=knowledge,
                )
            )
            if status["repository_files"] != len(graph["files"]):
                raise RuntimeError("repository file count mismatch")
            if status["file_dependencies"] != len(graph["dependency_edges"]):
                raise RuntimeError("dependency count mismatch")
            if status["capabilities"] != int(counts["capabilities"]):
                raise RuntimeError("capability count mismatch")
            if status["constructors"] != int(counts["constructors"]):
                raise RuntimeError("constructor count mismatch")
            if status["knowledge_edges"] != int(counts["knowledge_edges"]):
                raise RuntimeError("knowledge edge count mismatch")
            if status["hash216_positions"] != expected_positions:
                raise RuntimeError("Hash216 position count mismatch")
            if status["journal_mode"].lower() != "wal" or not status["synchronous_full"]:
                raise RuntimeError("SQLite durability membrane mismatch")
            if status["execution_authority"] is not False:
                raise RuntimeError("repository index authority escalation")

            search_samples: dict[str, Any] = {}
            all_nodes = [
                {
                    "node_id": str(row["node_id"]),
                    "node_kind": str(row["node_kind"]),
                    "name": str(row["name"]),
                    "source_path": str(row.get("source_path") or ""),
                }
                for row in nodes
            ]
            for query in QUERIES:
                expected = [
                    row
                    for row in all_nodes
                    if query.lower() in row["name"].lower()
                    or query.lower() in row["node_id"].lower()
                    or query.lower() in row["source_path"].lower()
                ]
                expected.sort(
                    key=lambda row: (row["node_kind"], row["name"], row["node_id"])
                )
                expected_ids = [row["node_id"] for row in expected[:64]]

                sql_samples: list[int] = []
                scan_samples: list[int] = []
                for _ in range(search_rounds):
                    started = time.perf_counter_ns()
                    sql_rows = db.search(query, limit=64)
                    sql_samples.append(time.perf_counter_ns() - started)
                    sql_ids = [row["node_id"] for row in sql_rows]
                    if sql_ids != expected_ids:
                        raise RuntimeError(f"indexed search parity mismatch: {query}")

                    started = time.perf_counter_ns()
                    scanned = [
                        row
                        for row in all_nodes
                        if query.lower() in row["name"].lower()
                        or query.lower() in row["node_id"].lower()
                        or query.lower() in row["source_path"].lower()
                    ]
                    scanned.sort(
                        key=lambda row: (
                            row["node_kind"],
                            row["name"],
                            row["node_id"],
                        )
                    )
                    scan_ids = [row["node_id"] for row in scanned[:64]]
                    scan_samples.append(time.perf_counter_ns() - started)
                    if scan_ids != expected_ids:
                        raise RuntimeError(f"scan search parity mismatch: {query}")

                sql_median = int(statistics.median(sql_samples))
                scan_median = int(statistics.median(scan_samples))
                search_samples[query] = {
                    "result_count": len(expected_ids),
                    "rounds": search_rounds,
                    "indexed_median_ns": sql_median,
                    "indexed_p95_ns": _percentile(sql_samples, 95, 100),
                    "python_scan_median_ns": scan_median,
                    "python_scan_p95_ns": _percentile(scan_samples, 95, 100),
                    "indexed_over_scan_ratio_x1000": (
                        sql_median * 1000 // max(1, scan_median)
                    ),
                    "exact_result_parity": True,
                }

            source_node_ids = [
                str(row["node_id"])
                for row in nodes[: min(len(nodes), 256)]
            ]
            neighbor_ns, neighbor_digest = _timed(
                lambda: [
                    (
                        node_id,
                        tuple(
                            row["hash216"]
                            for row in db.neighbors(node_id, limit=256)
                        ),
                    )
                    for node_id in source_node_ids
                ]
            )
            neighbor_ns_2, neighbor_digest_2 = _timed(
                lambda: [
                    (
                        node_id,
                        tuple(
                            row["hash216"]
                            for row in db.neighbors(node_id, limit=256)
                        ),
                    )
                    for node_id in source_node_ids
                ]
            )
            if neighbor_digest != neighbor_digest_2:
                raise RuntimeError("neighbor replay drift")

            first_hash = str(nodes[0]["hash216"])
            positional = _loop(
                lambda: tuple(
                    db.db.execute(
                        "SELECT ordinal,lane,lane_offset,symbol,symbol_sha256 "
                        "FROM hash216_positions "
                        "WHERE owner_hash216=? AND ordinal IN (0,71,72,143,144,215) "
                        "ORDER BY ordinal",
                        (first_hash,),
                    ).fetchall()
                ),
                positional_iterations,
            )
            if len(positional["result"]) != 6:
                raise RuntimeError("Hash216 positional lookup incomplete")
            positional.pop("result", None)
            database_bytes = db_path.stat().st_size
            wal_path = Path(str(db_path) + "-wal")
            wal_bytes = wal_path.stat().st_size if wal_path.exists() else 0

        reopen_ns, reopened = _timed(
            lambda: Lane5RepositoryHydrationKnowledgeDatabase(db_path)
        )
        try:
            reopen_status_ns, reopen_status = _timed(reopened.status)
            if reopen_status["hash216_positions"] != expected_positions:
                raise RuntimeError("restart rehydration status mismatch")
        finally:
            reopened.close()

    return {
        "graph_json_bytes": len(graph_bytes),
        "knowledge_json_bytes": len(knowledge_bytes),
        "graph_parse_ns": graph_parse_ns,
        "knowledge_parse_ns": knowledge_parse_ns,
        "source_files": int(counts["source_files"]),
        "source_dependency_edges": int(counts["source_dependency_edges"]),
        "capabilities": int(counts["capabilities"]),
        "constructors": int(counts["constructors"]),
        "knowledge_nodes": int(counts["knowledge_nodes"]),
        "knowledge_edges": int(counts["knowledge_edges"]),
        "expected_hash216_positions": expected_positions,
        "hydrate_ns": hydrate_ns,
        "database_bytes": database_bytes,
        "wal_bytes_after_hydrate": wal_bytes,
        "searches": search_samples,
        "neighbor_node_count": len(source_node_ids),
        "neighbor_first_ns": neighbor_ns,
        "neighbor_replay_ns": neighbor_ns_2,
        "neighbor_replay_equal": True,
        "hash216_positional_lookup": positional,
        "reopen_ns": reopen_ns,
        "reopen_status_ns": reopen_status_ns,
        "restart_rehydratable": reopen_status["restart_rehydratable"],
        "candidate_only": reopen_status["candidate_only"],
        "canonical_hash216_authority": reopen_status["canonical_hash216_authority"],
    }


def benchmark_service_registry() -> dict[str, Any]:
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry

    cold_ns, cold_registry = _timed(make_default_service_registry)
    cold_services = cold_registry.services()
    warm_ns, warm_registry = _timed(make_default_service_registry)
    warm_services = warm_registry.services()
    cold_names = [row["name"] for row in cold_services]
    warm_names = [row["name"] for row in warm_services]
    if not cold_names or cold_names != warm_names:
        raise RuntimeError("service registry replay mismatch")
    return {
        "service_count": len(cold_names),
        "cold_build_ns": cold_ns,
        "warm_build_ns": warm_ns,
        "cold_over_warm_ratio_x1000": cold_ns * 1000 // max(1, warm_ns),
        "service_name_replay_equal": True,
    }


def benchmark_wordnet_alignment(*, iterations: int) -> dict[str, Any]:
    from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import (
        default_wordnet_paths,
        load_wordnet_relations,
    )
    from hhs_runtime.hhs_pass220_i051_native_lean_alignment_v1 import (
        admit_native_lean_alignment_tensor,
    )

    paths = default_wordnet_paths()
    load_ns, relation_db = _timed(
        lambda: load_wordnet_relations(paths, require_all=True)
    )
    if not relation_db:
        raise RuntimeError("WordNet relation database empty")

    prompt = "exact tensor preserves meaning through deterministic closure"
    response = "exact tensor preserves meaning through deterministic closure"

    first = admit_native_lean_alignment_tensor(
        prompt,
        response,
        relation_db=relation_db,
    )
    if not first["canonical"]:
        raise RuntimeError(
            "native alignment benchmark fixture rejected: "
            + ",".join(first["failure_reasons"])
        )
    root = first["admission_root_hash72"]
    samples: list[int] = []
    edge_counts: list[int] = []
    for _ in range(iterations):
        started = time.perf_counter_ns()
        value = admit_native_lean_alignment_tensor(
            prompt,
            response,
            relation_db=relation_db,
        )
        samples.append(time.perf_counter_ns() - started)
        if value["admission_root_hash72"] != root or not value["canonical"]:
            raise RuntimeError("native alignment replay drift")
        edge_counts.append(len(value["wordnet_geometry"]["edges"]))

    total = sum(samples)
    return {
        "wordnet_files": [str(path.relative_to(ROOT)) for path in paths],
        "wordnet_entries": len(relation_db),
        "wordnet_load_ns": load_ns,
        "iterations": iterations,
        "alignment_median_ns": int(statistics.median(samples)),
        "alignment_p95_ns": _percentile(samples, 95, 100),
        "alignment_ops_per_second_floor": (
            iterations * 1_000_000_000 // max(1, total)
        ),
        "lexical_edge_count": edge_counts[0],
        "all_replay_equal": len(set(edge_counts)) == 1,
        "canonical": True,
        "hash216_lineage_verified": first["lineage"]["hash216_lineage_verified"],
        "lean_identity_bound_into_receipt_hash72": first["lineage"][
            "lean_identity_bound_into_receipt_hash72"
        ],
    }


def benchmark_i060_lean_identity(*, iterations: int) -> dict[str, Any]:
    from hhs_runtime.hhs_pass220_i060_native_lean_exactrat_value_algebra_v1 import (
        lean_identity_receipt,
    )

    lean_identity_receipt.cache_clear()
    cold_ns, cold = _timed(lean_identity_receipt)
    if not cold["theorem_identity_valid"] or not cold["dependency_identity_valid"]:
        raise RuntimeError("I060 Lean proof identity invalid")

    loop = _loop(
        lambda: (
            lean_identity_receipt()["theorem_identity_hash72"],
            lean_identity_receipt()["dependency_identity_hash72"],
        ),
        iterations,
    )
    pair = loop.pop("result")
    if pair != (
        cold["theorem_identity_hash72"],
        cold["dependency_identity_hash72"],
    ):
        raise RuntimeError("I060 Lean identity cache drift")
    loop.update(
        {
            "cold_ns": cold_ns,
            "theorem_identity_hash72": cold["theorem_identity_hash72"],
            "dependency_identity_hash72": cold["dependency_identity_hash72"],
            "theorem_identity_valid": True,
            "dependency_identity_valid": True,
            "vm81_mutation_authority": cold["vm81_mutation_authority"],
            "hash72_commit_authority": cold["hash72_commit_authority"],
            "hash216_persistence_authority": cold["hash216_persistence_authority"],
        }
    )
    return loop


def benchmark_nine_loop_knowledge(*, repeats: int) -> dict[str, Any]:
    from hhs_runtime.pass219.lane5_nine_loop_knowledge_hydration_1_75 import (
        discover_knowledge_hydration,
    )

    samples: list[int] = []
    receipts: list[dict[str, Any]] = []
    for _ in range(repeats):
        elapsed, receipt = _timed(discover_knowledge_hydration)
        samples.append(elapsed)
        receipts.append(receipt)

    roots = {
        (
            row["admitted_corpus_root_hash72"],
            row["knowledge_graph_root_hash72"],
            row["admission_replay_bundle_sha256"],
            row["retrieval_replay_bundle_sha256"],
        )
        for row in receipts
    }
    if len(roots) != 1:
        raise RuntimeError("1.75 knowledge hydration replay drift")
    first = receipts[0]
    if first["admitted_record_count"] != 13:
        raise RuntimeError("1.75 admitted record count drift")
    if first["graph_node_count"] != 13 or first["graph_edge_count"] != 12:
        raise RuntimeError("1.75 graph shape drift")
    if first["query_count"] != 12:
        raise RuntimeError("1.75 query count drift")
    if first["execution_authority"] is not False:
        raise RuntimeError("1.75 authority escalation")

    return {
        "repeats": repeats,
        "median_ns": int(statistics.median(samples)),
        "p95_ns": _percentile(samples, 95, 100),
        "min_ns": min(samples),
        "max_ns": max(samples),
        "replay_equal": True,
        "admitted_record_count": first["admitted_record_count"],
        "graph_node_count": first["graph_node_count"],
        "graph_edge_count": first["graph_edge_count"],
        "query_count": first["query_count"],
        "admitted_corpus_root_hash72": first["admitted_corpus_root_hash72"],
        "knowledge_graph_root_hash72": first["knowledge_graph_root_hash72"],
        "admission_replay_bundle_sha256": first["admission_replay_bundle_sha256"],
        "retrieval_replay_bundle_sha256": first["retrieval_replay_bundle_sha256"],
        "execution_authority": False,
        "canonical_persistence_authority": first[
            "canonical_persistence_authority"
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--search-rounds", type=int, default=100)
    parser.add_argument("--positional-iterations", type=int, default=5000)
    parser.add_argument("--alignment-iterations", type=int, default=250)
    parser.add_argument("--lean-iterations", type=int, default=10000)
    parser.add_argument("--knowledge-repeats", type=int, default=2)
    args = parser.parse_args()

    if min(
        args.search_rounds,
        args.positional_iterations,
        args.alignment_iterations,
        args.lean_iterations,
        args.knowledge_repeats,
    ) < 1:
        parser.error("all benchmark iteration counts must be positive")

    source_commit, source_tree = _git_identity()
    started = time.perf_counter_ns()

    repository_index = benchmark_repository_index(
        search_rounds=args.search_rounds,
        positional_iterations=args.positional_iterations,
    )
    service_registry = benchmark_service_registry()
    wordnet_alignment = benchmark_wordnet_alignment(
        iterations=args.alignment_iterations
    )
    i060 = benchmark_i060_lean_identity(iterations=args.lean_iterations)
    knowledge = benchmark_nine_loop_knowledge(repeats=args.knowledge_repeats)

    body = {
        "schema": SCHEMA,
        "source_commit": source_commit,
        "source_tree": source_tree,
        "result": "PASS",
        "timing_clock": "perf_counter_ns",
        "timing_authority": "OBSERVATIONAL_ONLY",
        "runner": _runner_identity(),
        "repository_index": repository_index,
        "service_registry": service_registry,
        "wordnet_native_alignment": wordnet_alignment,
        "i060_lean_identity": i060,
        "nine_loop_knowledge_1_75": knowledge,
        "process_max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "suite_elapsed_ns": time.perf_counter_ns() - started,
        "authority": {
            "canonical_floating_point_authority": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_commit_authority": False,
            "canonical_hash216_persistence_authority": False,
            "performance_measurements_authorize_semantic_change": False,
        },
    }
    body["receipt_sha256"] = sha256(_canonical(body)).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(body, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "result": body["result"],
                "source_commit": source_commit,
                "knowledge_nodes": repository_index["knowledge_nodes"],
                "knowledge_edges": repository_index["knowledge_edges"],
                "hash216_positions": repository_index[
                    "expected_hash216_positions"
                ],
                "service_count": service_registry["service_count"],
                "wordnet_entries": wordnet_alignment["wordnet_entries"],
                "receipt_sha256": body["receipt_sha256"],
            },
            sort_keys=True,
        )
    )
    print("PASS219_LANE5_INTEGRATED_SERVICES_INDEX_BENCHMARK_20260929_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
