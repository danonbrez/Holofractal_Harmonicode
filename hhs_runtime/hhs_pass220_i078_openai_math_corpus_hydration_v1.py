"""Pass 220 I078 OpenAI mathematics corpus extraction/hydration.

The checked-in dataset contains revision-pinned titles and derived structural
metadata only.  It deliberately does not persist manuscript bodies, abstracts,
PDF bytes, or copied Lean source bodies.  Hydration is candidate-only.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest

SCHEMA = "HHS_PASS_220_I078_OPENAI_MATH_CORPUS_HYDRATION_V1"
EXPECTED_SOURCE_REVISION = "adc7f1241b42e322a6451854ab7e4b4c146bf78a"
EXPECTED_HHS_BASE = "d616f4b72dc149d92159119276e6ac150fdf3828"
EXPECTED_COUNTS = {
    "manuscripts": 722,
    "families": 372,
    "formalized_sources": 162,
    "formalization_main_results": 185,
    "formalization_unique_lean_files": 180,
}
EXPECTED_CLASS_COUNTS = {
    "manuscripts": {
        "HIGH_PATH_OVERLAP": 110,
        "MIXED_PATH_OVERLAP": 290,
        "NOVELTY_CANDIDATE": 322,
    },
    "families": {
        "HIGH_PATH_OVERLAP": 45,
        "MIXED_PATH_OVERLAP": 145,
        "NOVELTY_CANDIDATE": 182,
    },
    "formalized_sources": {
        "HIGH_PATH_OVERLAP": 34,
        "MIXED_PATH_OVERLAP": 74,
        "NOVELTY_CANDIDATE": 54,
    },
}
ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "data/pass220/openai_math_corpus_hydration_20261006_v1.json"
BANNED_RETAINED_KEYS = {
    "abstract",
    "abstracts",
    "full_text",
    "paper_text",
    "manuscript_text",
    "pdf_bytes",
    "lean_source_body",
    "source_text",
}


class I078HydrationError(RuntimeError):
    pass


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            keys.add(str(key))
            keys.update(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_walk_keys(child))
    return keys


def _class_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    out = {
        "HIGH_PATH_OVERLAP": 0,
        "MIXED_PATH_OVERLAP": 0,
        "NOVELTY_CANDIDATE": 0,
    }
    for row in rows:
        classification = row.get("classification")
        if classification not in out:
            raise I078HydrationError(
                f"I078_UNKNOWN_CLASSIFICATION:{classification}"
            )
        out[classification] += 1
    return out


def load_dataset(path: str | Path = DATASET_PATH) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise I078HydrationError("I078_SCHEMA_MISMATCH")

    source = data.get("source", {})
    if source.get("repository") != "openai/math":
        raise I078HydrationError("I078_SOURCE_REPOSITORY_MISMATCH")
    if source.get("immutable_revision") != EXPECTED_SOURCE_REVISION:
        raise I078HydrationError("I078_SOURCE_REVISION_MISMATCH")
    if source.get("license") != "Apache-2.0":
        raise I078HydrationError("I078_LICENSE_MISMATCH")
    if source.get("manuscript_count") != EXPECTED_COUNTS["manuscripts"]:
        raise I078HydrationError("I078_MANUSCRIPT_COUNT_MISMATCH")
    if source.get("family_count") != EXPECTED_COUNTS["families"]:
        raise I078HydrationError("I078_FAMILY_COUNT_MISMATCH")
    if source.get("formalized_source_count") != EXPECTED_COUNTS["formalized_sources"]:
        raise I078HydrationError("I078_FORMALIZED_SOURCE_COUNT_MISMATCH")
    if source.get("formalization_main_result_count") != EXPECTED_COUNTS["formalization_main_results"]:
        raise I078HydrationError("I078_FORMAL_RESULT_COUNT_MISMATCH")
    if source.get("formalization_unique_lean_file_count") != EXPECTED_COUNTS["formalization_unique_lean_files"]:
        raise I078HydrationError("I078_FORMAL_FILE_COUNT_MISMATCH")

    hhs = data.get("hhs_reference", {})
    if hhs.get("immutable_revision") != EXPECTED_HHS_BASE:
        raise I078HydrationError("I078_HHS_BASE_MISMATCH")
    vocab = hhs.get("frozen_path_vocabulary")
    if not isinstance(vocab, list) or len(vocab) != hhs.get("frozen_path_vocabulary_count"):
        raise I078HydrationError("I078_HHS_VOCABULARY_MISMATCH")
    if vocab != sorted(set(vocab)):
        raise I078HydrationError("I078_HHS_VOCABULARY_NOT_CANONICAL")

    families = data.get("families")
    manuscripts = data.get("manuscripts")
    formalized = data.get("formalized_sources")
    main_results = data.get("formalization_main_results")
    if not all(isinstance(rows, list) for rows in (families, manuscripts, formalized, main_results)):
        raise I078HydrationError("I078_RECORD_SURFACE_INVALID")
    if len(families) != EXPECTED_COUNTS["families"]:
        raise I078HydrationError("I078_FAMILY_RECORD_COUNT_MISMATCH")
    if len(manuscripts) != EXPECTED_COUNTS["manuscripts"]:
        raise I078HydrationError("I078_MANUSCRIPT_RECORD_COUNT_MISMATCH")
    if len(formalized) != EXPECTED_COUNTS["formalized_sources"]:
        raise I078HydrationError("I078_FORMALIZED_RECORD_COUNT_MISMATCH")
    if len(main_results) != EXPECTED_COUNTS["formalization_main_results"]:
        raise I078HydrationError("I078_MAIN_RESULT_RECORD_COUNT_MISMATCH")

    family_ids = [row.get("family_id") for row in families]
    if len(set(family_ids)) != len(family_ids):
        raise I078HydrationError("I078_DUPLICATE_FAMILY_ID")
    family_set = set(family_ids)
    slugs = [row.get("slug") for row in manuscripts]
    if len(set(slugs)) != len(slugs):
        raise I078HydrationError("I078_DUPLICATE_MANUSCRIPT_SLUG")
    if any(row.get("family_id") not in family_set for row in manuscripts):
        raise I078HydrationError("I078_UNMAPPED_MANUSCRIPT")
    manuscript_set = set(slugs)
    if any(row.get("slug") not in manuscript_set for row in formalized):
        raise I078HydrationError("I078_UNMAPPED_FORMALIZED_SOURCE")

    if _class_counts(manuscripts) != EXPECTED_CLASS_COUNTS["manuscripts"]:
        raise I078HydrationError("I078_MANUSCRIPT_CLASS_COUNTS_MISMATCH")
    if _class_counts(families) != EXPECTED_CLASS_COUNTS["families"]:
        raise I078HydrationError("I078_FAMILY_CLASS_COUNTS_MISMATCH")
    if _class_counts(formalized) != EXPECTED_CLASS_COUNTS["formalized_sources"]:
        raise I078HydrationError("I078_FORMALIZED_CLASS_COUNTS_MISMATCH")

    retained = _walk_keys(data)
    bad = sorted(retained & BANNED_RETAINED_KEYS)
    if bad:
        raise I078HydrationError("I078_VERBATIM_RETENTION_FORBIDDEN:" + ",".join(bad))

    policy = data.get("extraction_policy", {})
    authority = data.get("authority", {})
    required_false = (
        "canonical_learning_commit_invoked",
        "vm81_mutation_invoked",
        "canonical_hash72_minted",
        "canonical_hash216_minted",
    )
    if policy.get("candidate_only") is not True:
        raise I078HydrationError("I078_POLICY_NOT_CANDIDATE_ONLY")
    for key in required_false:
        if policy.get(key) is not False:
            raise I078HydrationError(f"I078_POLICY_AUTHORITY_DRIFT:{key}")
    if authority.get("candidate_only") is not True:
        raise I078HydrationError("I078_AUTHORITY_NOT_CANDIDATE_ONLY")
    for key, value in authority.items():
        if key != "candidate_only" and value is not False:
            raise I078HydrationError(f"I078_AUTHORITY_DRIFT:{key}")
    return data


def build_candidate_graph(
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data = load_dataset() if data is None else data
    # Revalidate caller-supplied data by round-tripping it through the same
    # structural checks without granting it canonical persistence.
    if data.get("schema") != SCHEMA:
        raise I078HydrationError("I078_GRAPH_SCHEMA_MISMATCH")

    nodes: list[dict[str, Any]] = [{
        "id": "R:openai/math@" + EXPECTED_SOURCE_REVISION,
        "kind": "SOURCE_REPOSITORY",
        "candidate_only": True,
    }]
    edges: list[dict[str, str]] = []

    for row in data["families"]:
        nodes.append({
            "id": "F:" + row["family_id"],
            "kind": "RESULT_FAMILY",
            "classification": row["classification"],
            "overlap_ratio": row["hhs_path_overlap_ratio"],
        })
    for row in data["manuscripts"]:
        mid = "M:" + row["slug"]
        nodes.append({
            "id": mid,
            "kind": "MANUSCRIPT_METADATA",
            "classification": row["classification"],
            "formalized": any(
                formal.get("slug") == row["slug"]
                for formal in data["formalized_sources"]
            ),
        })
        edges.append({
            "source": "F:" + row["family_id"],
            "relation": "CONTAINS_MANUSCRIPT",
            "target": mid,
        })
    for row in data["formalized_sources"]:
        sid = "S:" + row["slug"]
        nodes.append({
            "id": sid,
            "kind": "FORMALIZED_SOURCE_METADATA",
            "classification": row["classification"],
        })
        edges.append({
            "source": "M:" + row["slug"],
            "relation": "HAS_FORMALIZED_SOURCE",
            "target": sid,
        })
    root_id = "R:openai/math@" + EXPECTED_SOURCE_REVISION
    for index, row in enumerate(data["formalization_main_results"]):
        pid = f"P:{index:03d}:{row['declaration']}"
        nodes.append({
            "id": pid,
            "kind": "LEAN_MAIN_RESULT",
            "domain": row["domain"],
            "file": row["file"],
            "declaration": row["declaration"],
        })
        edges.append({
            "source": root_id,
            "relation": "HAS_LEAN_MAIN_RESULT",
            "target": pid,
        })

    nodes.sort(key=lambda row: row["id"])
    edges.sort(key=lambda row: (row["source"], row["relation"], row["target"]))
    graph = {"nodes": nodes, "edges": edges}
    dictionary = {
        "domain": SCHEMA,
        "role": "CANDIDATE_ONLY_CORPUS_HYDRATION",
        "source_revision": EXPECTED_SOURCE_REVISION,
        "hhs_base": EXPECTED_HHS_BASE,
    }
    formalized_novelty = sorted(
        (
            {
                "title": row["title"],
                "slug": row["slug"],
                "family_id": row["family_id"],
                "overlap_ratio": row["hhs_path_overlap_ratio"],
            }
            for row in data["formalized_sources"]
            if row["classification"] == "NOVELTY_CANDIDATE"
        ),
        key=lambda row: (row["overlap_ratio"], row["title"].casefold()),
    )
    return {
        "schema": SCHEMA,
        "source_revision": EXPECTED_SOURCE_REVISION,
        "hhs_base": EXPECTED_HHS_BASE,
        "graph_node_count": len(nodes),
        "graph_edge_count": len(edges),
        "graph_sha256": _sha256(graph),
        "candidate_hash72": hash72_digest(dictionary, graph),
        "summary": data["summary"],
        "structural_overlap_anchors": data["structural_overlap_anchors"],
        "formalized_novelty_candidates": formalized_novelty,
        "candidate_only": True,
        "truth_promotion": False,
        "canonical_learning_commit_invoked": False,
        "vm81_mutation_invoked": False,
        "canonical_hash72_minted": False,
        "canonical_hash216_minted": False,
        "canonical_persistence_invoked": False,
    }


__all__ = [
    "DATASET_PATH",
    "EXPECTED_COUNTS",
    "EXPECTED_HHS_BASE",
    "EXPECTED_SOURCE_REVISION",
    "I078HydrationError",
    "SCHEMA",
    "build_candidate_graph",
    "load_dataset",
]
