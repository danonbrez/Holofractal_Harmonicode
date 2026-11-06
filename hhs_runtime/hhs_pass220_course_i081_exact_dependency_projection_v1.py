"""Read-only exact-source I081 constructor/dependency projection for the course corpus.

This projection never equates a HARMONICODE course module with an OpenAI
theorem without an independently verified typed correspondence. Existing
validated native constructors keep their authority irrespective of origin.
"""
from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from hhs_runtime.hhs_pass220_i081_openai_math_constructor_promotion_v1 import (
    load_registry, effective_frontier, invoke_promoted_constructor,
    invoke_partial_subconstructor,
)

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / "contracts/pass220/HARMONICODE_COURSE_PROOF_CORPUS_CROSSWALK_V1.json"
BRIDGE = ROOT / "contracts/pass220/HARMONICODE_COURSE_NATIVE_PROOF_EVIDENCE_BRIDGE_V1.json"
SCHEMA = "HHS_PASS220_COURSE_I081_EXACT_DEPENDENCY_PROJECTION_V1"


def _digest(obj: object) -> str:
    return sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def build_dependency_projection() -> dict:
    course = json.loads(COURSE.read_text(encoding="utf-8"))
    bridge = json.loads(BRIDGE.read_text(encoding="utf-8"))
    registry = load_registry()
    frontier = effective_frontier(registry)
    if frontier["novelty_sources"] != 322 or not frontier["complete"]:
        raise ValueError("I081_FRONTIER_INCOMPLETE")
    if len(course["modules"]) != 124:
        raise ValueError("COURSE_INCOMPLETE")
    nodes = []
    edges = []
    for idx, module in enumerate(course["modules"]):
        if module["id"] != f"HHC-M{idx:03d}" or module["number"] != idx:
            raise ValueError("COURSE_ID_DRIFT")
        nodes.append({"id": module["id"], "kind": "COURSE_MODULE",
                      "source_git_blob": course["source"]["git_blob_sha"],
                      "source_heading": module["source_heading"]})
    for row in registry["full_promotions"] + registry["partial_subconstructors"]:
        full = "promotion_id" in row
        key = "promotion_id" if full else "subconstructor_id"
        identifier = row[key]
        invoke = invoke_promoted_constructor if full else invoke_partial_subconstructor
        receipt = invoke(identifier, registry=registry)
        if receipt != invoke(identifier, registry=registry):
            raise ValueError("CONSTRUCTOR_REPLAY_DRIFT")
        if receipt["source_slug"] != row["source_slug"] or receipt["source_revision"] != registry["source_revision"]:
            raise ValueError("SOURCE_IDENTITY_DRIFT")
        if receipt["candidate_hash72"] != receipt["replay_hash72"] or not receipt["candidate_only"]:
            raise ValueError("INVALID_CANDIDATE_RECEIPT")
        nodes.append({"id": identifier, "kind": "OPENAI_I081_PROMOTED" if full else "OPENAI_I081_PARTIAL",
                      "source_slug": row["source_slug"], "source_tree_sha": row["source_tree_sha"],
                      "source_revision": row["source_revision"],
                      "family_doc_path": row["family_doc"]["path"],
                      "family_doc_sha": row["family_doc"]["sha"],
                      "candidate_hash72": receipt["candidate_hash72"],
                      "native_constructor_receipt_scope": "I081_SOURCE_BOUND_INVOCATION",
                      "canonical_vm81_admission_claimed": False})
        for ordinal, surface in enumerate(row["formal_surfaces"]):
            proof_id = f"{identifier}:formal:{ordinal}"
            if surface["source_revision"] != registry["source_revision"]:
                raise ValueError("PROOF_SURFACE_REVISION_DRIFT")
            nodes.append({"id": proof_id, "kind": "PINNED_OPENAI_FORMAL_SURFACE",
                          "comparator": surface["comparator"],
                          "solution": surface["solution"],
                          "theorem_names": surface["theorem_names"],
                          "source_revision": surface["source_revision"]})
            edges.append({"from": identifier, "to": proof_id,
                          "relation": "PINNED_FORMAL_DEPENDENCY", "proof_equivalence_claimed": False})
    for relation in course["crosswalk"]:
        module_id = f"HHC-M{relation['course_module']:03d}"
        # Anchor is a structural search term, not one of the 39 I081 identities.
        edges.append({"from": module_id, "to": relation["openai_anchor"],
                      "relation": relation["relation"], "proof_equivalence_claimed": False})
    for relation in bridge["course_bindings"]:
        module_id = f"HHC-M{relation['course_module']:03d}"
        edges.append({"from": module_id, "to": relation["native_key"],
                      "relation": relation["relation"], "proof_equivalence_claimed": False})
    result = {"schema": SCHEMA, "source_revision": registry["source_revision"],
              "course_git_blob": course["source"]["git_blob_sha"],
              "course_module_count": 124, "full_constructor_count": 26,
              "partial_constructor_count": 13,
              "frontier": frontier, "nodes": nodes, "edges": edges,
              "source_provenance_is_native_authority_limit": False,
              "canonical_authority_minted": False}
    result["projection_sha256"] = _digest(result)
    return result


def validate_projection(result: dict) -> None:
    seal = result.get("projection_sha256")
    if not isinstance(seal, str) or seal != _digest({k: v for k, v in result.items() if k != "projection_sha256"}):
        raise ValueError("PROJECTION_SEAL_DRIFT")
    if result["course_module_count"] != 124 or result["full_constructor_count"] != 26 or result["partial_constructor_count"] != 13:
        raise ValueError("CENSUS_DRIFT")
    ids = [node["id"] for node in result["nodes"]]
    if len(ids) != len(set(ids)):
        raise ValueError("DUPLICATE_PROOF_NODE")
    existing = set(ids)
    external_anchors = {edge["to"] for edge in result["edges"] if edge["relation"] in
                        ("STRUCTURAL_OVERLAP_CANDIDATE", "METHOD_OVERLAP_CANDIDATE")}
    native_keys = {row["key"] for row in json.loads(BRIDGE.read_text(encoding="utf-8"))["native_surfaces"]}
    for edge in result["edges"]:
        if edge["from"] not in existing or edge["to"] not in existing | external_anchors | native_keys:
            raise ValueError("DANGLING_PROOF_DEPENDENCY")
        if edge["proof_equivalence_claimed"] is not False:
            raise ValueError("UNVERIFIED_COURSE_EQUIVALENCE")
    if result["canonical_authority_minted"] is not False:
        raise ValueError("UNAUTHORIZED_MINT")


def self_test() -> dict:
    result = build_dependency_projection()
    validate_projection(result)
    return {"status": "PASS", "schema": SCHEMA, "projection_sha256": result["projection_sha256"],
            "node_count": len(result["nodes"]), "edge_count": len(result["edges"]),
            "course_modules": result["course_module_count"],
            "full_constructors": result["full_constructor_count"],
            "partial_constructors": result["partial_constructor_count"]}


if __name__ == "__main__":
    print(json.dumps(self_test(), sort_keys=True))
