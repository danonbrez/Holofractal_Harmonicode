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
    # Enumerate the complete I078 novelty frontier using the inherited
    # source inventory, then bind exact I081 promotion/partial source slugs.
    # HOLD remains source-scope status, never an assertion of native invalidity.
    i078 = json.loads((ROOT / "data/pass220/openai_math_corpus_hydration_20261006_v1.json").read_text(encoding="utf-8"))
    frontier_rows = [row for row in i078["manuscripts"]
                     if row.get("classification") == "NOVELTY_CANDIDATE"]
    slugs = [row["slug"] for row in frontier_rows]
    if len(slugs) != 322 or len(set(slugs)) != 322:
        raise ValueError("I078_FRONTIER_SOURCE_CENSUS_DRIFT")
    if i078["source"]["immutable_revision"] != registry["source_revision"]:
        raise ValueError("I078_REVISION_IDENTITY_DRIFT")
    for slug in sorted(slugs):
        nodes.append({"id": "OPENAI-SOURCE:" + slug,
                      "kind": "OPENAI_I078_NOVELTY_SOURCE",
                      "source_slug": slug,
                      "source_revision": registry["source_revision"],
                      "manuscript_source_scope": "I078_NOVELTY_FRONTIER",
                      "native_constructor_validity": "NOT_REASSESSED_BY_GRAPH"})
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
        if row["source_slug"] not in slugs:
            raise ValueError("I081_SOURCE_NOT_IN_I078_FRONTIER")
        edges.append({"from": identifier, "to": "OPENAI-SOURCE:" + row["source_slug"],
                      "relation": "EXACT_SOURCE_IDENTITY", "proof_equivalence_claimed": False})
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
    if sum(node["kind"] == "OPENAI_I078_NOVELTY_SOURCE" for node in result["nodes"]) != 322:
        raise ValueError("OPENAI_SOURCE_CENSUS_DRIFT")
    if sum(edge["relation"] == "EXACT_SOURCE_IDENTITY" for edge in result["edges"]) != 39:
        raise ValueError("I081_SOURCE_EDGE_COVERAGE_DRIFT")
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



def build_lane5_snapshot_binding(projection: dict | None = None) -> dict:
    """Bind the existing Lane 5 Hash216 receipt as a historical source snapshot.

    This uses the inherited Hash216 constructor; it does not claim that the
    snapshot's source commit equals the current PR commit or admit VM81 state.
    """
    from hhs_backend.runtime.hhs_pass219_lane5_repository_hydration_knowledge_graph_1_69 import (
        _h216,
    )
    projection = build_dependency_projection() if projection is None else projection
    validate_projection(projection)
    receipt_path = ROOT / "artifacts/repository_index/LANE5_HASH216_HYDRATION_DATABASE_RECEIPT.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt["schema"] != "HHS_PASS_219_LANE5_REPOSITORY_HYDRATION_DATABASE_RECEIPT_1_69":
        raise ValueError("LANE5_RECEIPT_SCHEMA_DRIFT")
    database = receipt["database_status"]
    if database["schema"] != "HHS_PASS_219_LANE5_REPOSITORY_HYDRATION_HASH216_DATABASE_1_69":
        raise ValueError("LANE5_DATABASE_SCHEMA_DRIFT")
    if database["candidate_only"] is not True:
        raise ValueError("LANE5_DISCOVERY_AUTHORITY_ESCALATION")
    for key in ("execution_authority", "canonical_hash216_authority",
                "canonical_hash72_authority", "canonical_vm81_mutation_authority",
                "canonical_persistence_authority"):
        if database[key] is not False:
            raise ValueError(f"LANE5_FORBIDDEN_AUTHORITY:{key}")
    if database["restart_rehydratable"] is not True or receipt["restart_rehydratable_from_repository_artifacts"] is not True:
        raise ValueError("LANE5_SNAPSHOT_NOT_REHYDRATABLE")
    for key in ("projection_root_hash216", "source_dependency_graph_root_hash216"):
        if not isinstance(receipt.get(key), str) or len(receipt[key]) != 216:
            raise ValueError("LANE5_SNAPSHOT_ROOT_INVALID")
    if not isinstance(receipt["source_commit"], str) or len(receipt["source_commit"]) != 40:
        raise ValueError("LANE5_SNAPSHOT_SOURCE_COMMIT_INVALID")
    frame = {"course_i081_projection_sha256": projection["projection_sha256"],
             "course_source_git_blob": projection["course_git_blob"],
             "openai_source_revision": projection["source_revision"],
             "lane5_snapshot_source_commit": receipt["source_commit"],
             "lane5_snapshot_projection_root_hash216": receipt["projection_root_hash216"],
             "lane5_snapshot_dependency_root_hash216": receipt["source_dependency_graph_root_hash216"],
             "relationship": "HISTORICAL_SOURCE_SNAPSHOT_BINDING",
             "current_main_rehydration": "NOT_ESTABLISHED",
             "native_admission": False}
    binding = _h216("HHS-P220-COURSE-I081-LANE5-SNAPSHOT-BINDING-V1", frame)
    return {"schema": "HHS_PASS220_COURSE_I081_LANE5_SNAPSHOT_BINDING_V1",
            **frame, "candidate_binding_hash216": binding,
            "canonical_hash216_minted": False,
            "canonical_vm81_admission": False}


def validate_lane5_snapshot_binding(binding: dict, projection: dict) -> None:
    from hhs_backend.runtime.hhs_pass219_lane5_repository_hydration_knowledge_graph_1_69 import _h216
    validate_projection(projection)
    if binding.get("schema") != "HHS_PASS220_COURSE_I081_LANE5_SNAPSHOT_BINDING_V1":
        raise ValueError("LANE5_BINDING_SCHEMA_DRIFT")
    if binding.get("course_i081_projection_sha256") != projection["projection_sha256"]:
        raise ValueError("LANE5_COURSE_PROJECTION_MISMATCH")
    if binding.get("canonical_hash216_minted") is not False or binding.get("canonical_vm81_admission") is not False:
        raise ValueError("LANE5_BINDING_AUTHORITY_ESCALATION")
    frame = {key: value for key, value in binding.items()
             if key not in ("schema", "candidate_binding_hash216",
                            "canonical_hash216_minted", "canonical_vm81_admission")}
    if binding.get("candidate_binding_hash216") != _h216("HHS-P220-COURSE-I081-LANE5-SNAPSHOT-BINDING-V1", frame):
        raise ValueError("LANE5_BINDING_HASH216_TAMPERED")


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
