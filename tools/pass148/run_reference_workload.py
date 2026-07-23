#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_runtime.pass145.canonical import hash72
from hhs_runtime.pass148.service import HHS148Service


def negative_cases() -> list[tuple]:
    tree = ast.parse((ROOT / "tests/test_hhs_pass148_native_semantic_authority_membrane_v1.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "NEGATIVE_CASES" for t in node.targets):
            return list(ast.literal_eval(node.value))
    raise RuntimeError("NEGATIVE_CASES not found")


def main() -> int:
    out = ROOT / "release_artifacts/pass148/reference/internal"
    out.mkdir(parents=True, exist_ok=True)
    db = out / "PASS_148_REFERENCE.sqlite3"
    for path in (db, Path(str(db)+"-wal"), Path(str(db)+"-shm"), db.with_name(db.name+".pass146-session.json")):
        path.unlink(missing_ok=True)

    evidence: list[dict[str, Any]] = []
    def ev(kind: str, result: Any, authority: str = "A1") -> None:
        evidence.append({"ordinal": len(evidence)+1, "event": kind, "authority_level": authority, "classification": "OBSERVED_WORKING", "result_hash72": hash72("hhs_pass148_reference_evidence_v1", result), "result": result})

    with HHS148Service(db) as service:
        owner = service.security.bootstrap_local_owner("Pass148 Reference Authority")
        identity = owner["result"]["identity_id"]
        ev("OWNER_BOOTSTRAP", {"identity_id": identity, "status": owner["result"]["status"]})
        ev("SEMANTIC_REGISTRY_SYNC", service.sync_semantic_registry())
        ev("PUBLIC_REGISTRY_SYNC", service.public_registry.synchronize())

        o_pi = service.analyze("O≠π", source_type="contract", source_reference="HHS-P148-NSAM Ω148.9", governing_contracts=["HHS-P148-NSAM"])
        delta_norm = service.analyze("n/Δ=n", source_type="contract", source_reference="HHS-P148-NSAM Ω148.10", governing_contracts=["HHS-P148-NSAM"])
        delta_power = service.analyze("Δ^n=Δ", source_type="contract", source_reference="HHS-P148-NSAM Ω148.10", governing_contracts=["HHS-P148-NSAM"])
        residual = service.analyze("Δ-Δ=x+y", source_type="contract", source_reference="HHS-P148-NSAM 13.2", governing_contracts=["HHS-P148-NSAM"])
        infinity_exp = service.analyze("∞^{-Δ}=Δ", source_type="contract", source_reference="HHS-P148-NSAM 13.3", governing_contracts=["HHS-P148-NSAM"])
        infinity_sub = service.analyze("∞-Δ=∞", source_type="contract", source_reference="HHS-P148-NSAM 13.3", governing_contracts=["HHS-P148-NSAM"])
        ordered = service.analyze(r"P^2-(P-\frac{AB}{B^2}P+\frac{BA}{A^2})=Δ", source_type="documentation", source_reference="HHS-P148-NSAM 13.4")
        for label, result in (("O_DISTINCT_PI",o_pi),("DELTA_NORMALIZATION",delta_norm),("DELTA_POWER",delta_power),("DELTA_RESIDUAL",residual),("INFINITY_EXPONENT",infinity_exp),("INFINITY_SUBTRACTION",infinity_sub),("ORDERED_META_CONSTRAINT",ordered)):
            ev(label, {"proposition": result["proposition"], "ast_hash": result["ast"]["canonical_ast_hash"], "diagnostics": result["contamination_findings"], "receipt": result["receipt"]})

        derived = service.derive([delta_norm["proposition"]["proposition_id"]], rule_id="HHS_DELTA_SELF_NORMALIZATION_SUBSTITUTION_V1", substitutions={"n":"Δ"})
        ev("WITNESSED_DERIVATION", derived)
        projection = service.project(r"\frac{AB}{B^2}P", profile_id="COMMUTATIVE_FIELD_CONTROL_V1")
        ev("ISOLATED_CONTROL_PROJECTION", projection)
        story = "Year 2847, Dr. Yuki said O≠π.\n\nThe fictional ship proves it can erase entropy.\n\nAppendix: Δ=1."
        document = service.analyze_document(story, name="reference_story.md", source_type="fiction", source_reference="PASS148_REFERENCE_STORY")
        ev("MIXED_NARRATIVE_DOCUMENT", {"source_id": document["source"]["source_id"], "segments": document["segments"], "narrative_boundaries": document["narrative_boundaries"], "candidate_declarations": document["candidate_declarations"], "receipt_hash72": document["document_semantic_receipt_hash72"]})

        candidate = service.analyze("Δ/Δ=Δ", source_type="documentation", source_reference="PASS148_PROMOTION_CANDIDATE")
        request = service.request_promotion(candidate["proposition"]["proposition_id"], "DERIVABLE_CONSEQUENCE", governing_rule="HHS_DELTA_SELF_NORMALIZATION_SUBSTITUTION_V1", dependency_set=[derived["derivation"]["derivation_id"]], scope={"normalization_lane": True}, requested_by_identity=identity)
        decision = service.evaluate_promotion(request["request"]["promotion_request_id"], verifier_identity=identity, authority_level="A3", authorize=True, rationale="matching ordered derivation")
        ev("AUTHORIZED_PROMOTION", {"request": request, "decision": decision}, "A3")

        negative_rows = []
        for case_id, expression, source_type, expected_diag, expected_primary in negative_cases():
            profile = "NARRATIVE_WORLD_MODEL_V1" if source_type == "fiction" else "HHS_NATIVE_TYPED_V1"
            result = service.analyze(expression, source_type=source_type, source_reference=f"NEGATIVE:{case_id}", profile_id=profile)
            observed = sorted(x["diagnostic_code"] for x in result["contamination_findings"])
            passed = result["proposition"]["primary_class"] == expected_primary and (expected_diag is None or expected_diag in observed) and result["proposition"]["authority_level"] != "A4" and result["source_identity_preserved"]
            negative_rows.append({"case_id": case_id, "expression": expression, "source_type": source_type, "expected_primary": expected_primary, "observed_primary": result["proposition"]["primary_class"], "expected_diagnostic": expected_diag, "observed_diagnostics": observed, "source_identity_preserved": result["source_identity_preserved"], "authority_level": result["proposition"]["authority_level"], "classification": "FAILS_SAFELY" if passed else "OBSERVED_FAILING", "passed": passed, "receipt": result["receipt"]})
        negative_report = {"schema":"HHS_PASS148_NEGATIVE_TEST_REPORT_V1","authority_level":"A1","total":len(negative_rows),"passed":sum(1 for x in negative_rows if x["passed"]),"failed":sum(1 for x in negative_rows if not x["passed"]),"cases":negative_rows}
        negative_report["report_hash72"] = hash72("hhs_pass148_negative_test_report_v1", negative_report)
        (ROOT / "HHS_PASS_148_NEGATIVE_TEST_REPORT.json").write_text(json.dumps(negative_report,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        ev("NEGATIVE_TEST_CORPUS", {"total":negative_report["total"],"passed":negative_report["passed"],"failed":negative_report["failed"],"report_hash72":negative_report["report_hash72"]})

        targets = [o_pi["proposition"]["proposition_id"], derived["output_proposition"]["proposition_id"], derived["derivation"]["derivation_id"], projection["projection_id"]]
        replay_rows = [service.replay_semantic(target) for target in targets]
        replay_report = {"schema":"HHS_PASS148_REPLAY_REPORT_V1","authority_level":"A1","targets":targets,"results":replay_rows,"all_replay_validated":all(x["status"]=="REPLAY_VALIDATED" and x["ok"] for x in replay_rows)}
        replay_report["report_hash72"] = hash72("hhs_pass148_replay_report_v1", replay_report)
        (ROOT / "HHS_PASS_148_REPLAY_REPORT.json").write_text(json.dumps(replay_report,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        ev("DETERMINISTIC_REPLAY", replay_report)

        audit = service.semantic_audit(); integrity = service.db.integrity_check(); receipts = service.db.verify_receipt_chain()
        ev("SEMANTIC_AUDIT", audit, "A3"); ev("DATABASE_INTEGRITY", integrity); ev("RECEIPT_CHAIN", receipts)
        summary = {"schema":"HHS_PASS148_REFERENCE_WORKLOAD_V1","status":"REFERENCE_WORKLOAD_CLOSED" if audit["closed"] and replay_report["all_replay_validated"] and negative_report["failed"]==0 and receipts["ok"] else "REFERENCE_WORKLOAD_FAILED","semantic_registry":service.registry_audit(),"negative_tests":{"passed":negative_report["passed"],"total":negative_report["total"]},"replay_validated":replay_report["all_replay_validated"],"semantic_audit_closed":audit["closed"],"database_integrity":integrity["ok"],"receipt_chain_valid":receipts["ok"],"transaction_count":receipts["count"],"external_privileged_semantic_authority":0}
        summary["workload_hash72"] = hash72("hhs_pass148_reference_workload_v1", summary)
        (out / "PASS_148_REFERENCE_WORKLOAD.json").write_text(json.dumps(summary,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

    with (ROOT / "HHS_PASS_148_CEUAC_EVIDENCE.jsonl").open("w",encoding="utf-8") as fh:
        for row in evidence:
            fh.write(json.dumps(row,sort_keys=True,ensure_ascii=False)+"\n")
    # Runtime databases contain authentication material and are not release artifacts.
    for path in (db, Path(str(db)+"-wal"), Path(str(db)+"-shm"), db.with_name(db.name+".pass146-session.json")):
        path.unlink(missing_ok=True)
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    return 0 if summary["status"] == "REFERENCE_WORKLOAD_CLOSED" else 1

if __name__ == "__main__":
    raise SystemExit(main())
