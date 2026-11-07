"""Exact checked-out-source validation for the inherited Lane 5 deep-index output.

Run only *after* the existing dependency-index workflow regenerates its
repository graph, Lane 5 graph, and database receipt in the same checkout.
Read-only: no alternate VM81, Hash72, Hash216 or persistence authority.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from hhs_runtime.hhs_pass220_course_i081_exact_dependency_projection_v1 import (
    build_dependency_projection, build_lane5_snapshot_binding,
    validate_projection,
)

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "artifacts/repository_index/REPOSITORY_HASH216_DEPENDENCY_GRAPH.json"
KNOWLEDGE = ROOT / "artifacts/repository_index/LANE5_HASH216_HYDRATION_KNOWLEDGE_GRAPH.json"
RECEIPT = ROOT / "artifacts/repository_index/LANE5_HASH216_HYDRATION_DATABASE_RECEIPT.json"
SOURCES = (
    "docs/course/HARMONICODE_Algebra_Course.md",
    "contracts/pass220/HARMONICODE_COURSE_PROOF_CORPUS_CROSSWALK_V1.json",
    "contracts/pass220/HARMONICODE_COURSE_NATIVE_PROOF_EVIDENCE_BRIDGE_V1.json",
    "hhs_runtime/hhs_pass220_course_i081_exact_dependency_projection_v1.py",
    "hhs_runtime/hhs_pass220_course_lane5_exact_source_check_v1.py",
    "tests/pass220/test_harmonicode_course_proof_corpus_crosswalk_v1.py",
)


def verify_exact_source_graph() -> dict:
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    knowledge = json.loads(KNOWLEDGE.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    if any(row.get("source_commit") != commit for row in (graph, knowledge, receipt)):
        raise ValueError("LANE5_EXACT_CHECKOUT_REVISION_MISMATCH")
    source_files = {row["path"]: row for row in graph["files"]}
    if len(source_files) != len(graph["files"]):
        raise ValueError("LANE5_DUPLICATE_REPOSITORY_SOURCE")
    for path in SOURCES:
        if path not in source_files:
            raise ValueError("LANE5_COURSE_SOURCE_MISSING:" + path)
        actual_blob = subprocess.check_output(
            ["git", "hash-object", "--", str(ROOT / path)],
            cwd=ROOT, text=True,
        ).strip()
        if source_files[path]["git_blob"] != actual_blob:
            raise ValueError("LANE5_COURSE_SOURCE_BLOB_DRIFT:" + path)
        if len(source_files[path]["hash216"]) != 216:
            raise ValueError("LANE5_COURSE_SOURCE_HASH216_WIDTH:" + path)

    if knowledge["source_dependency_graph_root_hash216"] != graph["roots"]["graph_root_hash216"]:
        raise ValueError("LANE5_KNOWLEDGE_DEPENDENCY_ROOT_MISMATCH")
    if receipt["source_dependency_graph_root_hash216"] != graph["roots"]["graph_root_hash216"]:
        raise ValueError("LANE5_DATABASE_DEPENDENCY_ROOT_MISMATCH")
    if receipt["projection_root_hash216"] != knowledge["roots"]["projection_root_hash216"]:
        raise ValueError("LANE5_DATABASE_PROJECTION_ROOT_MISMATCH")
    if knowledge["authority"]["candidate_only"] is not True:
        raise ValueError("LANE5_DISCOVERY_AUTHORITY_ESCALATION")
    if any(knowledge["authority"][key] is not False for key in (
        "execution_authority", "canonical_vm81_mutation_authority",
        "canonical_hash72_authority", "canonical_hash216_authority",
        "canonical_persistence_authority")):
        raise ValueError("LANE5_CANONICAL_AUTHORITY_BYPASS")

    proof = build_dependency_projection()
    validate_projection(proof)
    # Existing snapshot binding must remain historical until this exact
    # regeneration check succeeds; never rewrite its source commit in place.
    historical = build_lane5_snapshot_binding(proof)
    if historical["canonical_vm81_admission"] is not False:
        raise ValueError("LANE5_HISTORICAL_RECEIPT_AUTHORITY_BYPASS")
    return {
        "status": "PASS",
        "exact_source_commit": commit,
        "source_paths_verified": len(SOURCES),
        "repository_graph_root_hash216": graph["roots"]["graph_root_hash216"],
        "knowledge_projection_root_hash216": knowledge["roots"]["projection_root_hash216"],
        "course_i081_projection_sha256": proof["projection_sha256"],
        "historical_snapshot_distinguished": True,
        "current_pr_generated_graph_verified": True,
        "canonical_vm81_admission": False,
        "canonical_hash216_minted": False,
    }


if __name__ == "__main__":
    print(json.dumps(verify_exact_source_graph(), sort_keys=True))
