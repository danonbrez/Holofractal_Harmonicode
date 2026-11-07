#!/usr/bin/env python3
"""Read-only course/proof-corpus crosswalk validator; no canonical runtime mutation."""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COURSE = ROOT / "docs/course/HARMONICODE_Algebra_Course.md"
REGISTRY = ROOT / "contracts/pass220/HARMONICODE_COURSE_PROOF_CORPUS_CROSSWALK_V1.json"
PATTERN = re.compile(r"^#{1,4}\s+(?:Module|MODULE)\s+(\d+)([^\n]*)", re.MULTILINE)

def validate() -> dict:
    course = COURSE.read_text(encoding="utf-8")
    corpus = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert corpus["schema"] == "HHS_HARMONICODE_COURSE_PROOF_CORPUS_CROSSWALK_V1"
    heading = [(int(m.group(1)), m.group(0)) for m in PATTERN.finditer(course)]
    assert len(heading) == 124, ("MODULE_COUNT", len(heading))
    assert [i for i, _ in heading] == list(range(124)), "MODULE_ORDER_OR_DUPLICATE"
    indexed = corpus["modules"]
    assert len(indexed) == 124, "INDEX_COUNT"
    assert all(row["number"] == i and row["id"] == f"HHC-M{i:03d}" and
               row["source_heading"] == heading[i][1] for i, row in enumerate(indexed)), "INDEX_DRIFT"
    expected_blob = corpus["source"]["git_blob_sha"]
    actual_blob = subprocess.check_output(["git", "hash-object", "--", str(COURSE)],
                                          cwd=ROOT, text=True).strip()
    assert expected_blob == actual_blob, "SOURCE_BLOB_DRIFT"
    q4 = corpus["module123"]
    assert q4["native_q4_semantics"] == "OPEN"
    assert q4["new_lane5_execution"] == "NOT_EXECUTED"
    assert q4["proof_promotion"] is False
    assert q4["commutative_collapse_allowed"] is False
    assert q4["witnesses"]["whole_tone_stabilizer_size"] == 6
    assert q4["witnesses"]["whole_tone_distinct_transpositions"] == 2
    assert q4["witnesses"]["q144_address_return"] == "144/144"
    assert q4["witnesses"]["h36_address_return"] == "5184/5184"
    assert "Q₄" in course and "u¹⁴⁴" in course, "Q4_SOURCE_MISSING"
    # Exact derivation guards: the published examples must satisfy the
    # canonical guarded expressions rather than merely describe them.
    assert "m = (1 ± √(1+4(t³−t)))/2" in course
    assert "m=(1±√(1+4(t³−t)))/2" in course
    assert "h_k == 5r+60s degrees" in course
    assert "CurvaturePayload == c²·P(q−p)/(p+q) == c²" in course
    assert "BoxedMetricCell == c²+a²+b²+m c²" in course
    assert all((5 * (r + 12 * ss)) % 360 == (5 * r + 60 * ss) % 360
               for r in range(12) for ss in range(6)), "HUE_PHASE_LIFT_DRIFT"
    assert all((2 * (m * m - m)) == (2 * (t**3 - t))
               for t, m in ((2, 3), (2, -2))), "MODULUS_EXACT_BRANCH_DRIFT"
    assert all(P * ((P + 1) - (P - 1)) // ((P - 1) + (P + 1)) == 1
               for P in range(1, 25)), "CURVATURE_UNIT_GAIN_DRIFT"

    assert all(not row["proof_admitted"] for row in indexed), "UNAUTHORIZED_PROOF_PROMOTION"
    assert not any(corpus["authority"].values()), "UNAUTHORIZED_AUTHORITY"
    for relation in corpus["crosswalk"]:
        assert 0 <= relation["course_module"] <= 123
        assert relation["proof_equivalence"] is False
        assert relation["relation"] in {"STRUCTURAL_OVERLAP_CANDIDATE", "METHOD_OVERLAP_CANDIDATE"}
    hydration = corpus["hydration_contract"]
    assert hydration["principle"] == "PROVENANCE_INDEPENDENT_NATIVE_CONSTRUCTOR_AUTHORITY"
    assert hydration["discovery_hydration"]["native_constructor_validated"] is False
    assert hydration["validated_proof_hydration"]["source_provider_independent"] is True
    assert hydration["validated_proof_hydration"]["candidate_label_not_inherited_after_validation"] is True
    assert hydration["per_instance_status_required"] is True
    assert hydration["bulk_proof_validation_not_inferred_from_source_catalogue"] is True
    assert corpus["corpora"]["openai_revision"] == "adc7f1241b42e322a6451854ab7e4b4c146bf78a"
    for key in ("hhs_lemma", "hhs_axiom", "whitepaper_source_freeze",
                "openai_i078", "openai_i079", "openai_i080", "openai_i081"):
        assert (ROOT / corpus["corpora"][key]).is_file(), ("CORPUS_REFERENCE_MISSING", key)
    evidence_path = ROOT / "contracts/pass220/HARMONICODE_COURSE_NATIVE_PROOF_EVIDENCE_BRIDGE_V1.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["schema"] == "HHS_HARMONICODE_COURSE_NATIVE_PROOF_EVIDENCE_BRIDGE_V1"
    assert evidence["course_crosswalk"] == str(REGISTRY.relative_to(ROOT))
    assert evidence["policy"]["original_source_does_not_limit_validated_native_constructor"] is True
    assert evidence["policy"]["exact_source_and_statement_binding_required_for_specific_receipt"] is True
    assert evidence["policy"]["automatically_admit_new_ordered_q4"] is False
    assert evidence["policy"]["all_124_course_modules_native_validated_by_this_registry"] is False
    keys = {row["key"] for row in evidence["native_surfaces"]}
    assert len(keys) == len(evidence["native_surfaces"])
    for row in evidence["native_surfaces"]:
        assert (ROOT / row["path"]).is_file(), ("NATIVE_EVIDENCE_PATH_MISSING", row["key"])
        assert row["proves_new_course"] is False, "UNVERIFIED_COURSE_PROOF_PROMOTION"
    for binding in evidence["course_bindings"]:
        assert binding["native_key"] in keys, "UNKNOWN_NATIVE_EVIDENCE_LINK"
        assert binding["course_module"] in range(124)
        assert binding["proof_receipt_status"] in {"SOURCE_PATH_ONLY", "INHERITED_SCOPE_ONLY"}
    # Execute the existing I081 canonical registry checker and domain-separated replay
    # receipt. This validates the source-bound OpenAI registry, not every imported
    # theorem's native VM81 admission.
    from hhs_runtime.hhs_pass220_i081_openai_math_constructor_promotion_v1 import (
        load_registry, effective_frontier, build_registry_receipt,
    )
    openai_registry = load_registry()
    frontier = effective_frontier(openai_registry)
    native_source_receipt = build_registry_receipt(openai_registry)
    assert native_source_receipt["candidate_hash72"] == native_source_receipt["replay_hash72"]
    assert native_source_receipt["candidate_only"] is True
    assert native_source_receipt["canonical_hash72_minted"] is False
    assert native_source_receipt["canonical_hash216_minted"] is False
    assert openai_registry["result"]["effective_theorem_sources"] == 80
    assert openai_registry["result"]["effective_hold_sources"] == 242
    assert openai_registry["result"]["novelty_frontier_sources"] == 322
    assert openai_registry["result"]["source_level_coverage_gap"] == 0
    assert openai_registry["result"]["duplicate_assignment"] == 0
    assert native_source_receipt["frontier"] == frontier

    # Exercise every source-scoped promoted and partial native constructor
    # through the already registered I081 invocation interface. A replay
    # receipt is an invocation witness, not a fresh Lean proof or VM81 mint.
    from hhs_runtime.hhs_pass220_i081_openai_math_constructor_promotion_v1 import (
        invoke_promoted_constructor, invoke_partial_subconstructor,
    )
    assert len(openai_registry["full_promotions"]) == 26
    assert len(openai_registry["partial_subconstructors"]) == 13
    promoted_ids = set()
    for row in openai_registry["full_promotions"]:
        identifier = row["promotion_id"]
        assert identifier not in promoted_ids, "I081_DUPLICATE_PROMOTION_ID"
        promoted_ids.add(identifier)
        first = invoke_promoted_constructor(identifier, registry=openai_registry)
        replay = invoke_promoted_constructor(identifier, registry=openai_registry)
        assert first == replay, ("PROMOTED_REPLAY_DRIFT", identifier)
        assert first["source_slug"] == row["source_slug"]
        assert first["source_revision"] == openai_registry["source_revision"]
        assert first["proof_surface_bound"] is True
        assert first["candidate_hash72"] == first["replay_hash72"]
        assert first["manuscript_status"] == "FORMAL_THEOREM_CONSTRUCTOR"
        assert first["truth_promotion"] is False
        assert first["vm81_mutation_invoked"] is False
        assert first["canonical_hash72_minted"] is False
        assert first["canonical_hash216_minted"] is False
        assert first["canonical_persistence_invoked"] is False
    partial_ids = set()
    for row in openai_registry["partial_subconstructors"]:
        identifier = row["subconstructor_id"]
        assert identifier not in partial_ids, "I081_DUPLICATE_PARTIAL_ID"
        partial_ids.add(identifier)
        first = invoke_partial_subconstructor(identifier, registry=openai_registry)
        replay = invoke_partial_subconstructor(identifier, registry=openai_registry)
        assert first == replay, ("PARTIAL_REPLAY_DRIFT", identifier)
        assert first["source_slug"] == row["source_slug"]
        assert first["source_revision"] == openai_registry["source_revision"]
        assert first["candidate_hash72"] == first["replay_hash72"]
        assert first["formal_subtheorem_available"] is True
        assert first["full_source_promotion"] is False
        assert first["manuscript_status"] == "HOLD"
        assert first["truth_promotion"] is False

    from hhs_runtime.hhs_pass220_course_i081_exact_dependency_projection_v1 import (
        build_dependency_projection, validate_projection, self_test as dependency_self_test,
    )
    graph = build_dependency_projection()
    validate_projection(graph)
    assert graph["projection_sha256"] == build_dependency_projection()["projection_sha256"]
    assert dependency_self_test()["status"] == "PASS"
    assert sum(n["kind"] == "COURSE_MODULE" for n in graph["nodes"]) == 124
    assert sum(n["kind"] == "OPENAI_I081_PROMOTED" for n in graph["nodes"]) == 26
    assert sum(n["kind"] == "OPENAI_I081_PARTIAL" for n in graph["nodes"]) == 13
    assert sum(n["kind"] == "OPENAI_I078_NOVELTY_SOURCE" for n in graph["nodes"]) == 322
    assert sum(e["relation"] == "EXACT_SOURCE_IDENTITY" for e in graph["edges"]) == 39
    source_nodes = {n["id"] for n in graph["nodes"] if n["kind"] == "OPENAI_I078_NOVELTY_SOURCE"}
    assert len(source_nodes) == 322
    assert all(e["to"] in source_nodes for e in graph["edges"]
               if e["relation"] == "EXACT_SOURCE_IDENTITY")

    assert all(e["proof_equivalence_claimed"] is False for e in graph["edges"])
    # Negative tests: even a resealed graph must reject a constructor
    # re-pointed to a different but otherwise legitimate I078 source.
    from copy import deepcopy
    from hhs_runtime.hhs_pass220_course_i081_exact_dependency_projection_v1 import _digest
    tampered = deepcopy(graph)
    source_edges = [edge for edge in tampered["edges"]
                    if edge["relation"] == "EXACT_SOURCE_IDENTITY"]
    assert len(source_edges) == 39
    source_edges[0]["to"] = source_edges[1]["to"]
    tampered["projection_sha256"] = _digest({
        k: v for k, v in tampered.items() if k != "projection_sha256"
    })
    try:
        validate_projection(tampered)
    except ValueError as exc:
        assert "I081_SOURCE_EDGE_IDENTITY_MISMATCH" in str(exc)
    else:
        raise AssertionError("RESEALED_SOURCE_REWIRING_ACCEPTED")
    tampered = deepcopy(graph)
    formal_edges = [edge for edge in tampered["edges"]
                    if edge["relation"] == "PINNED_FORMAL_DEPENDENCY"]
    assert formal_edges
    formal_edges[0]["to"] = formal_edges[-1]["to"]
    tampered["projection_sha256"] = _digest({
        k: v for k, v in tampered.items() if k != "projection_sha256"
    })
    try:
        validate_projection(tampered)
    except ValueError as exc:
        assert "I081_FORMAL_DEPENDENCY_PARENT_MISMATCH" in str(exc)
    else:
        raise AssertionError("RESEALED_FORMAL_REWIRING_ACCEPTED")

    # A resealed formal node with altered Lean solution identity is invalid.
    forged = deepcopy(graph)
    formal = next(node for node in forged["nodes"]
                  if node["kind"] == "PINNED_OPENAI_FORMAL_SURFACE")
    formal["solution"]["sha"] = "0" * 40
    formal["theorem_names"] = ["invented.theorem"]
    forged["projection_sha256"] = _digest({
        k: v for k, v in forged.items() if k != "projection_sha256"
    })
    try:
        validate_projection(forged)
    except ValueError as exc:
        assert "I081_CANONICAL_FORMAL_PAYLOAD_MISMATCH" in str(exc)
    else:
        raise AssertionError("RESEALED_FORMAL_PAYLOAD_FORGERY_ACCEPTED")
    assert graph["canonical_authority_minted"] is False
    from hhs_runtime.hhs_pass220_course_i081_exact_dependency_projection_v1 import (
        build_lane5_snapshot_binding, validate_lane5_snapshot_binding,
    )
    binding = build_lane5_snapshot_binding(graph)
    validate_lane5_snapshot_binding(binding, graph)
    assert binding == build_lane5_snapshot_binding(graph)
    assert len(binding["candidate_binding_hash216"]) == 216
    assert binding["relationship"] == "HISTORICAL_SOURCE_SNAPSHOT_BINDING"
    assert binding["current_main_rehydration"] == "NOT_ESTABLISHED"
    assert binding["canonical_hash216_minted"] is False
    assert binding["canonical_vm81_admission"] is False
    corrupted = dict(binding, course_i081_projection_sha256="0" * 64)
    try:
        validate_lane5_snapshot_binding(corrupted, graph)
    except ValueError:
        pass
    else:
        raise AssertionError("LANE5_GRAPH_TAMPER_NOT_REJECTED")
    # Recomputed historical receipt bindings must not certify invented provenance.
    from hhs_backend.runtime.hhs_pass219_lane5_repository_hydration_knowledge_graph_1_69 import _h216
    for changes in (
        {"lane5_snapshot_source_commit": "0" * 40},
        {"lane5_snapshot_projection_root_hash216": "0" * 216},
        {"current_main_rehydration": "ESTABLISHED", "native_admission": True},
    ):
        corrupted = dict(binding, **changes)
        frame = {key: value for key, value in corrupted.items() if key not in (
            "schema", "candidate_binding_hash216", "canonical_hash216_minted",
            "canonical_vm81_admission",
        )}
        corrupted["candidate_binding_hash216"] = _h216(
            "HHS-P220-COURSE-I081-LANE5-SNAPSHOT-BINDING-V1", frame,
        )
        try:
            validate_lane5_snapshot_binding(corrupted, graph)
        except ValueError as exc:
            assert "LANE5_HISTORICAL_PROVENANCE_MISMATCH" in str(exc)
        else:
            raise AssertionError("RESEALED_SNAPSHOT_PROVENANCE_FORGERY_ACCEPTED")
    corrupted = dict(binding, canonical_vm81_admission=True)
    try:
        validate_lane5_snapshot_binding(corrupted, graph)
    except ValueError:
        pass
    else:
        raise AssertionError("LANE5_AUTHORITY_BYPASS_NOT_REJECTED")

    return {"status":"PASS", "module_coverage":"124/124", "source_blob":actual_blob,
            "openai_relation":"CANDIDATE_ONLY", "native_q4":"OPEN"}

def test_crosswalk_validation():
    assert validate()["status"] == "PASS"


if __name__ == "__main__":
    print(json.dumps(validate(), sort_keys=True))
