from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_runtime.pass145.canonical import canonical_json, hash72, stable_id, utc_now
from hhs_runtime.pass145.errors import Pass145Error
from hhs_runtime.pass147.service import HHS147Service
from .engine import HHS148BoundaryEngine
from .registry import (
    AUTHORITY_LEVELS,
    CONSEQUENCE_CLASSES,
    INTERPRETATION_VERSION,
    PASS_ID,
    PRIMARY_CLASSES,
    SEMANTIC_REGISTRY_VERSION,
    VERSION,
    contamination_registry,
    declared_law_registry,
    derivation_rule_registry,
    full_registry,
    get_rule,
    operator_registry,
    projection_profile_registry,
)
from .semantics import analyze_expression, derive_consequence, run_control_projection, segment_document

SEMANTIC_SOURCE_NAMESPACE = "hhs-semantic-evidence-v148"


class HHS148Service(HHS147Service):
    def __init__(self, db_path: str | Path, **kwargs: Any):
        super().__init__(db_path, **kwargs)
        self.security = HHS148BoundaryEngine(self)
        from .public import Pass148PublicSurfaceRegistry
        self.public_registry = Pass148PublicSurfaceRegistry(self.db)

    def version(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS148_VERSION_V1",
            "pass_id": PASS_ID,
            "version": VERSION,
            "semantic_registry_version": SEMANTIC_REGISTRY_VERSION,
            "interpretation_version": INTERPRETATION_VERSION,
            "parent": super().version(),
            "governing_rule": "representation may vary; native semantic authority must not drift",
        }

    def capabilities(self) -> dict[str, Any]:
        parent = super().capabilities()
        parent["schema"] = "HHS_PASS148_CAPABILITIES_V1"
        parent["pass_id"] = PASS_ID
        parent["capabilities"].update({
            "native_semantic_registry": "CLI_AVAILABLE",
            "ordered_expression_ast": "CLI_AVAILABLE",
            "semantic_classification": "CLI_AVAILABLE",
            "mixed_document_semantic_segmentation": "CLI_AVAILABLE",
            "witnessed_derivation_graphs": "CLI_AVAILABLE",
            "isolated_control_projection": "CLI_AVAILABLE",
            "semantic_contamination_detection": "CLI_AVAILABLE",
            "promotion_request": "CLI_AVAILABLE",
            "promotion_evaluation": "PUBLICLY_REQUESTABLE_THROUGH_BOUNDARY",
            "semantic_replay": "CLI_AVAILABLE",
            "external_model_native_commit": "BLOCKED_BY_EXPLICIT_CONTRACT",
            "conventional_fallback_semantics": "PROHIBITED",
            "narrative_authority_promotion": "PROHIBITED",
        })
        return parent

    def status(self) -> dict[str, Any]:
        parent = super().status()
        counts = {}
        for table in ("semantic_rules", "semantic_asts", "semantic_propositions", "semantic_derivations", "semantic_projections", "semantic_contaminations", "semantic_promotion_requests", "semantic_promotion_decisions", "semantic_replays"):
            counts[table] = int(self.db.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
        registry = self.registry_audit()
        compiled_registry_ready = bool(full_registry().get("registry_hash72") and registry["expected_count"] > 0)
        registry_state = {
            **registry,
            "compiled_registry_ready": compiled_registry_ready,
            "durable_registry_synchronized": bool(registry["closed"]),
            "synchronization_required": not bool(registry["closed"]),
        }
        return {
            "schema": "HHS_PASS148_STATUS_V1",
            # Status remains a read-only health check. The compiled registry is
            # authoritative and queryable before its optional durable mirror is
            # synchronized, so a fresh database is ready without an implicit write.
            "ok": bool(parent["ok"] and compiled_registry_ready),
            "parent_status": parent,
            "semantic_registry": registry_state,
            "counts": counts,
            "external_privileged_semantic_authority": 0,
        }

    def doctor(self) -> dict[str, Any]:
        parent = super().doctor()
        registry = self.registry_audit()
        compiled_registry_ready = bool(full_registry().get("registry_hash72") and registry["expected_count"] > 0)
        checks = {
            **parent["checks"],
            "semantic_registry": {
                "ok": compiled_registry_ready,
                **registry,
                "compiled_registry_ready": compiled_registry_ready,
                "durable_registry_synchronized": bool(registry["closed"]),
                "synchronization_required": not bool(registry["closed"]),
            },
            "source_identity_preservation": {"ok": True, "normalization_replaces_source": False},
            "projection_isolation": {"ok": True, "control_namespace_separate": True, "native_mutation_allowed": False},
            "narrative_non_promotion": {"ok": True, "fiction_authority_ceiling": "A1"},
            "external_semantic_authority": {"ok": True, "privileged_semantic_authority": 0, "promotion_evaluation_public": False},
        }
        return {"schema": "HHS_PASS148_DOCTOR_V1", "ok": all(bool(v.get("ok")) for v in checks.values()), "checks": checks}

    def sync_semantic_registry(self) -> dict[str, Any]:
        entries: list[tuple[str, str, dict[str, Any]]] = []
        for item in operator_registry(): entries.append((str(item["operator_id"]), "OPERATOR", item))
        for item in declared_law_registry(): entries.append((str(item["rule_id"]), "DECLARED_LAW", item))
        for item in derivation_rule_registry(): entries.append((str(item["rule_id"]), "DERIVATION_RULE", item))
        for item in projection_profile_registry(): entries.append((str(item["profile_id"]), "PROJECTION_PROFILE", item))
        for item in contamination_registry(): entries.append((str(item["diagnostic_code"]), "CONTAMINATION_DIAGNOSTIC", item))

        def apply(conn):
            inserted = 0
            for rule_id, kind, item in entries:
                witness = str(item["hash72_witness"])
                existing = conn.execute("SELECT rule_hash72 FROM semantic_rules WHERE rule_id=?", (rule_id,)).fetchone()
                if existing and existing[0] != witness:
                    # Preserve historical version rather than overwrite it.
                    versioned_id = f"{rule_id}@{SEMANTIC_REGISTRY_VERSION}"
                    conn.execute("UPDATE semantic_rules SET active=0 WHERE rule_id=?", (rule_id,))
                    conn.execute("INSERT OR IGNORE INTO semantic_rules(rule_id,rule_kind,registry_version,rule_json,rule_hash72,active,created_at) VALUES(?,?,?,?,?,1,?)", (versioned_id, kind, SEMANTIC_REGISTRY_VERSION, canonical_json(item), witness, utc_now()))
                    inserted += 1
                elif not existing:
                    conn.execute("INSERT INTO semantic_rules(rule_id,rule_kind,registry_version,rule_json,rule_hash72,active,created_at) VALUES(?,?,?,?,?,1,?)", (rule_id, kind, SEMANTIC_REGISTRY_VERSION, canonical_json(item), witness, utc_now()))
                    inserted += 1
            return {"status": "SEMANTIC_REGISTRY_SYNCHRONIZED", "registry_version": SEMANTIC_REGISTRY_VERSION, "entry_count": len(entries), "inserted": inserted, "registry_hash72": full_registry()["registry_hash72"]}
        return self.db.mutate("SEMANTIC_REGISTRY_SYNC", {"registry_version": SEMANTIC_REGISTRY_VERSION, "registry_hash72": full_registry()["registry_hash72"]}, apply, receipt_type="SEMANTIC_REGISTRY_RECEIPT")

    def registry_audit(self) -> dict[str, Any]:
        expected = {}
        for item in operator_registry(): expected[str(item["operator_id"])] = item["hash72_witness"]
        for item in declared_law_registry(): expected[str(item["rule_id"])] = item["hash72_witness"]
        for item in derivation_rule_registry(): expected[str(item["rule_id"])] = item["hash72_witness"]
        for item in projection_profile_registry(): expected[str(item["profile_id"])] = item["hash72_witness"]
        for item in contamination_registry(): expected[str(item["diagnostic_code"])] = item["hash72_witness"]
        observed = {str(r["rule_id"]): str(r["rule_hash72"]) for r in self.db.conn.execute("SELECT rule_id,rule_hash72 FROM semantic_rules WHERE active=1")}
        missing = sorted(k for k in expected if observed.get(k) != expected[k])
        unexpected = sorted(k for k in observed if k not in expected and "@" not in k)
        return {"schema": "HHS_PASS148_REGISTRY_AUDIT_V1", "closed": not missing and not unexpected, "expected_count": len(expected), "observed_count": len(observed), "missing_or_mismatched": missing, "unexpected_active": unexpected, "registry_version": SEMANTIC_REGISTRY_VERSION, "registry_hash72": full_registry()["registry_hash72"]}

    @staticmethod
    def _ast_id(ast: Mapping[str, Any]) -> str:
        return stable_id("AST", "hhs_pass148_ast_id_v1", {"source_hash72": ast["source_hash72"], "canonical_ast_hash": ast["canonical_ast_hash"], "registry_version": SEMANTIC_REGISTRY_VERSION})

    def _insert_analysis(self, conn, analysis: Mapping[str, Any]) -> dict[str, Any]:
        ast = dict(analysis["ast"]); prop = dict(analysis["proposition"])
        ast_id = self._ast_id(ast)
        conn.execute("INSERT OR IGNORE INTO semantic_asts(ast_id,source_expression,source_hash72,canonical_ast_hash,registry_version,ast_json,created_at) VALUES(?,?,?,?,?,?,?)", (ast_id, ast["source_expression"], ast["source_hash72"], ast["canonical_ast_hash"], SEMANTIC_REGISTRY_VERSION, canonical_json(ast), utc_now()))
        conn.execute(
            "INSERT OR IGNORE INTO semantic_propositions(proposition_id,ast_id,source_expression,source_type,source_reference,primary_class,consequence_class,authority_level,operator_profile,lane_scope_json,gate_scope_json,branch_conditions_json,dependencies_json,assumptions_json,prohibited_promotions_json,interpretation_version,interpretation_hash,proposition_hash72,proposition_json,active,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1,?)",
            (prop["proposition_id"], ast_id, prop["source_expression"], prop["source_type"], prop["source_reference"], prop["primary_class"], prop["consequence_class"], prop["authority_level"], prop["operator_profile"], canonical_json(prop["lane_scope"]), canonical_json(prop["gate_scope"]), canonical_json(prop["branch_conditions"]), canonical_json(prop["dependencies"]), canonical_json(prop["assumptions"]), canonical_json(prop["prohibited_promotions"]), prop["interpretation_version"], prop["interpretation_hash"], prop["hash72_identity"], canonical_json(prop), utc_now()),
        )
        finding_ids = []
        for finding in analysis.get("contamination_findings", []):
            finding_id = stable_id("CNT", "hhs_pass148_contamination_id_v1", {"proposition_id": prop["proposition_id"], "finding_hash72": finding["diagnostic_hash72"]})
            conn.execute("INSERT OR IGNORE INTO semantic_contaminations(finding_id,proposition_id,diagnostic_code,severity,finding_json,finding_hash72,created_at) VALUES(?,?,?,?,?,?,?)", (finding_id, prop["proposition_id"], finding["diagnostic_code"], finding["severity"], canonical_json(finding), finding["diagnostic_hash72"], utc_now()))
            finding_ids.append(finding_id)
        semantic_receipt = {
            "schema": "HHS_PASS148_SEMANTIC_RECEIPT_V1",
            "operation": "ANALYZE_EXPRESSION",
            "source_hash72": ast["source_hash72"],
            "ast_hash72": ast["canonical_ast_hash"],
            "proposition_hash72": prop["hash72_identity"],
            "classification": [prop["primary_class"], prop["consequence_class"], prop["authority_level"]],
            "contamination_hashes": [f["diagnostic_hash72"] for f in analysis.get("contamination_findings", [])],
            "registry_version": SEMANTIC_REGISTRY_VERSION,
        }
        semantic_receipt["semantic_receipt_hash72"] = hash72("hhs_pass148_semantic_receipt_v1", semantic_receipt)
        return {"status": "SEMANTIC_ANALYSIS_PERSISTED", "ast_id": ast_id, "proposition_id": prop["proposition_id"], "finding_ids": finding_ids, "semantic_receipt": semantic_receipt}

    def analyze(self, expression: str, *, source_type: str, source_reference: str, profile_id: str = "HHS_NATIVE_TYPED_V1", declared_scope: Mapping[str, Any] | None = None, governing_contracts: Sequence[str] | None = None) -> dict[str, Any]:
        analysis = analyze_expression(expression, source_type=source_type, source_reference=source_reference, profile_id=profile_id, declared_scope=declared_scope, governing_contracts=governing_contracts)
        # Timestamp is occurrence provenance, not part of semantic identity.
        analysis["proposition"]["timestamp"] = utc_now()
        request = {"source_hash72": analysis["ast"]["source_hash72"], "source_type": source_type, "source_reference": source_reference, "profile_id": profile_id, "declared_scope": dict(declared_scope or {}), "governing_contracts": list(governing_contracts or []), "registry_version": SEMANTIC_REGISTRY_VERSION}
        stored = self.db.mutate("SEMANTIC_ANALYZE_EXPRESSION", request, lambda conn: self._insert_analysis(conn, analysis), receipt_type="SEMANTIC_ANALYSIS_RECEIPT")
        return {**analysis, "persistence": stored, "receipt": stored["receipt_id"], "semantic_receipt": stored["result"]["semantic_receipt"]}

    def analyze_document(self, text: str, *, name: str, source_type: str, source_reference: str, profile_id: str = "HHS_NATIVE_TYPED_V1", governing_contracts: Sequence[str] | None = None) -> dict[str, Any]:
        source = self.ingest_bytes(text.encode("utf-8"), name=name, mime_type="text/markdown", namespace=SEMANTIC_SOURCE_NAMESPACE, source_kind="PASS148_MIXED_SEMANTIC_SOURCE", acquisition={"method": "SEMANTIC_MEMBRANE", "source_type": source_type}, analyze=False)
        segments = segment_document(text)
        outputs = []
        dependencies = []
        narrative_boundaries = []
        candidate_declarations = []
        rejected_promotions = []
        narrative_markers = re.compile(r"(?:said|whispered|year\s+\d+|spaceship|alien|fiction|character|story|aboard|captain)", re.I)
        equation_pattern = re.compile(r"(?:O\s*[≠=]|Δ|\\Delta|∞|\\infty|==|\\frac)")
        for segment in segments:
            value = segment["text"]
            local_type = "fiction" if source_type == "fiction" or narrative_markers.search(value) else source_type
            analysis = self.analyze(value, source_type=local_type, source_reference=f"{source_reference}#span={segment['start_offset']}:{segment['end_offset']}", profile_id="NARRATIVE_WORLD_MODEL_V1" if local_type == "fiction" else profile_id, declared_scope={"source_id": source["source_id"], "source_span": [segment["start_offset"], segment["end_offset"]]}, governing_contracts=governing_contracts)
            entry = {"segment": segment, "analysis": analysis}
            if local_type == "fiction":
                narrative_boundaries.append({"segment_index": segment["segment_index"], "source_span": [segment["start_offset"], segment["end_offset"]], "classification": "NARRATIVE"})
                if equation_pattern.search(value):
                    candidate = self.analyze(value, source_type="documentation", source_reference=f"{source_reference}#analytic-candidate={segment['segment_index']}", profile_id="HHS_NATIVE_TYPED_V1", declared_scope={"source_id": source["source_id"], "source_span": [segment["start_offset"], segment["end_offset"]], "candidate_from_narrative": True}, governing_contracts=[])
                    entry["candidate_analytic_proposition"] = candidate
                    candidate_declarations.append(candidate["proposition"]["proposition_id"])
            outputs.append(entry)
            prop = analysis["proposition"]
            dependencies.append({"segment_index": segment["segment_index"], "proposition_id": prop["proposition_id"], "dependencies": prop["dependencies"]})
            for finding in analysis["contamination_findings"]:
                if finding["severity"].startswith("REJECT"):
                    rejected_promotions.append({"proposition_id": prop["proposition_id"], "diagnostic": finding})
        receipt_core = {"source_id": source["source_id"], "source_root_hash72": source["source_root_hash72"], "segment_hashes": [s["segment_hash72"] for s in segments], "proposition_hashes": [x["analysis"]["proposition"]["hash72_identity"] for x in outputs], "registry_version": SEMANTIC_REGISTRY_VERSION}
        return {"schema": "HHS_PASS148_DOCUMENT_ANALYSIS_V1", "source": source, "segments": outputs, "cross_proposition_dependency_graph": dependencies, "narrative_boundaries": narrative_boundaries, "candidate_declarations": candidate_declarations, "rejected_promotions": rejected_promotions, "document_semantic_receipt_hash72": hash72("hhs_pass148_document_semantic_receipt_v1", receipt_core), "original_document_reconstructable": True}

    def get_proposition(self, proposition_id: str) -> dict[str, Any]:
        row = self.db.conn.execute("SELECT proposition_json,ast_id,created_at FROM semantic_propositions WHERE proposition_id=?", (proposition_id,)).fetchone()
        if not row: raise Pass145Error("SEMANTIC_PROPOSITION_NOT_FOUND", "proposition not found", "SEMANTIC_RETRIEVE", proposition_id)
        value = json.loads(row["proposition_json"]); value["ast_id"] = row["ast_id"]; value["created_at"] = row["created_at"]
        return {"schema": "HHS_PASS148_PROPOSITION_RECORD_V1", "proposition": value}

    def get_derivation(self, derivation_id: str) -> dict[str, Any]:
        row = self.db.conn.execute("SELECT derivation_json,created_at FROM semantic_derivations WHERE derivation_id=?", (derivation_id,)).fetchone()
        if not row: raise Pass145Error("SEMANTIC_DERIVATION_NOT_FOUND", "derivation not found", "SEMANTIC_RETRIEVE", derivation_id)
        return {"schema": "HHS_PASS148_DERIVATION_RECORD_V1", "derivation": json.loads(row["derivation_json"]), "created_at": row["created_at"]}

    def get_rule_record(self, rule_id: str) -> dict[str, Any]:
        row = self.db.conn.execute("SELECT rule_json FROM semantic_rules WHERE rule_id=? AND active=1", (rule_id,)).fetchone()
        value = json.loads(row[0]) if row else get_rule(rule_id)
        if value is None: raise Pass145Error("SEMANTIC_RULE_NOT_FOUND", "semantic rule not found", "SEMANTIC_RULE", rule_id)
        return {"schema": "HHS_PASS148_RULE_RECORD_V1", "rule": value, "source": "PERSISTED_REGISTRY" if row else "PUBLIC_STATIC_REGISTRY", "privileged_internal_access": 0}

    def derive(self, proposition_ids: Sequence[str], *, rule_id: str, substitutions: Mapping[str, str] | None = None) -> dict[str, Any]:
        inputs = [self.get_proposition(pid)["proposition"] for pid in proposition_ids]
        result = derive_consequence(inputs, rule_id=rule_id, substitutions=substitutions)
        result["output_proposition"]["timestamp"] = utc_now()
        analysis = {"ast": result["output_ast"], "proposition": result["output_proposition"], "contamination_findings": [], "unresolved_elements": [], "source_identity_preserved": True}
        def apply(conn):
            stored = self._insert_analysis(conn, analysis)
            derivation = result["derivation"]
            conn.execute("INSERT OR IGNORE INTO semantic_derivations(derivation_id,output_proposition_id,derivation_json,derivation_hash72,registry_version,created_at) VALUES(?,?,?,?,?,?)", (derivation["derivation_id"], derivation["output_proposition"], canonical_json(derivation), derivation["derivation_hash72"], SEMANTIC_REGISTRY_VERSION, utc_now()))
            return {**stored, "status": "SEMANTIC_DERIVATION_PERSISTED", "derivation_id": derivation["derivation_id"], "derivation_hash72": derivation["derivation_hash72"]}
        tx = self.db.mutate("SEMANTIC_DERIVE_CONSEQUENCE", {"proposition_ids": list(proposition_ids), "rule_id": rule_id, "substitutions": dict(substitutions or {})}, apply, receipt_type="SEMANTIC_DERIVATION_RECEIPT")
        result["derivation"]["receipt"] = tx["receipt_id"]
        attachment = self.db.mutate(
            "SEMANTIC_DERIVATION_ATTACH_RECEIPT",
            {"derivation_id": result["derivation"]["derivation_id"], "derivation_receipt_id": tx["receipt_id"]},
            lambda conn: (
                conn.execute(
                    "UPDATE semantic_derivations SET derivation_json=? WHERE derivation_id=?",
                    (canonical_json(result["derivation"]), result["derivation"]["derivation_id"]),
                ),
                {"status": "DERIVATION_RECEIPT_ATTACHED", "derivation_id": result["derivation"]["derivation_id"], "derivation_receipt_id": tx["receipt_id"]},
            )[1],
            receipt_type="SEMANTIC_DERIVATION_RECEIPT_ATTACHMENT",
        )
        return {**result, "persistence": tx, "receipt_attachment": attachment, "receipt": tx["receipt_id"]}

    def project(self, expression: str, *, profile_id: str, assumptions: Sequence[str] | None = None) -> dict[str, Any]:
        projection = run_control_projection(expression, profile_id=profile_id, assumptions=assumptions)
        ast = {"source_expression": expression, "source_hash72": hash72("hhs_pass148_expression_source_v1", expression), "canonical_ast_hash": projection["source_ast_hash"], "registry_version": SEMANTIC_REGISTRY_VERSION}
        # Reparse is held in the persisted AST record.
        from .parser import parse_expression
        parsed = parse_expression(expression); ast_id = self._ast_id(parsed)
        def apply(conn):
            conn.execute("INSERT OR IGNORE INTO semantic_asts(ast_id,source_expression,source_hash72,canonical_ast_hash,registry_version,ast_json,created_at) VALUES(?,?,?,?,?,?,?)", (ast_id, expression, parsed["source_hash72"], parsed["canonical_ast_hash"], SEMANTIC_REGISTRY_VERSION, canonical_json(parsed), utc_now()))
            conn.execute("INSERT OR IGNORE INTO semantic_projections(projection_id,source_ast_id,profile_id,projection_json,projection_hash72,native_state_mutation,created_at) VALUES(?,?,?,?,?,0,?)", (projection["projection_id"], ast_id, profile_id, canonical_json(projection), projection["projection_hash72"], utc_now()))
            return {"status": "CONTROL_PROJECTION_PERSISTED", "projection_id": projection["projection_id"], "projection_hash72": projection["projection_hash72"], "native_state_mutation": False}
        tx = self.db.mutate("SEMANTIC_CONTROL_PROJECTION", {"source_hash72": parsed["source_hash72"], "profile_id": profile_id, "assumptions": list(assumptions or [])}, apply, receipt_type="SEMANTIC_PROJECTION_RECEIPT")
        return {**projection, "persistence": tx, "receipt": tx["receipt_id"]}

    def request_promotion(self, source_proposition_id: str, target_class: str, *, governing_rule: str, dependency_set: Sequence[str], scope: Mapping[str, Any], requested_by_identity: str) -> dict[str, Any]:
        source = self.get_proposition(source_proposition_id)["proposition"]
        if target_class not in PRIMARY_CLASSES:
            raise Pass145Error("SEMANTIC_CLASS_INVALID", f"invalid target class: {target_class}", "SEMANTIC_PROMOTION")
        core = {"source_proposition_id": source_proposition_id, "source_class": source["primary_class"], "target_class": target_class, "governing_rule": governing_rule, "dependency_set": list(dependency_set), "scope": dict(scope), "requested_by_identity": requested_by_identity, "status": "PROMOTION_REQUESTED_NOT_AUTHORIZED"}
        request_id = stable_id("PMR", "hhs_pass148_promotion_request_id_v1", core); request_hash = hash72("hhs_pass148_promotion_request_v1", {"promotion_request_id": request_id, **core})
        def apply(conn):
            conn.execute("INSERT OR IGNORE INTO semantic_promotion_requests(promotion_request_id,source_proposition_id,source_class,target_class,governing_rule,dependency_set_json,scope_json,requested_by_identity,status,request_json,request_hash72,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (request_id, source_proposition_id, source["primary_class"], target_class, governing_rule, canonical_json(list(dependency_set)), canonical_json(dict(scope)), requested_by_identity, core["status"], canonical_json(core), request_hash, utc_now()))
            return {"status": core["status"], "promotion_request_id": request_id, "request_hash72": request_hash, "authority_changed": False}
        tx = self.db.mutate("SEMANTIC_PROMOTION_REQUEST", {"promotion_request_id": request_id, "request_hash72": request_hash}, apply, receipt_type="SEMANTIC_PROMOTION_REQUEST_RECEIPT")
        return {"schema": "HHS_PASS148_PROMOTION_REQUEST_V1", "request": {"promotion_request_id": request_id, **core, "request_hash72": request_hash}, "persistence": tx, "receipt": tx["receipt_id"], "authority_changed": False}

    def evaluate_promotion(self, promotion_request_id: str, *, verifier_identity: str, authority_level: str, authorize: bool, rationale: str) -> dict[str, Any]:
        if authority_level not in {"A3", "A4"}:
            raise Pass145Error("PROMOTION_AUTHORITY_INSUFFICIENT", "promotion evaluation requires A3 or A4 authority", "SEMANTIC_PROMOTION", promotion_request_id)
        row = self.db.conn.execute("SELECT * FROM semantic_promotion_requests WHERE promotion_request_id=?", (promotion_request_id,)).fetchone()
        if not row: raise Pass145Error("SEMANTIC_PROMOTION_NOT_FOUND", "promotion request not found", "SEMANTIC_PROMOTION", promotion_request_id)
        request = json.loads(row["request_json"]); dependencies = json.loads(row["dependency_set_json"]); source = self.get_proposition(str(row["source_proposition_id"]))["proposition"]
        reasons: list[str] = []
        supporting_derivation = None
        supporting_proposition = None
        if source["primary_class"] in {"CONTROL_PROJECTION", "NARRATIVE_EXTRAPOLATION"}: reasons.append("SOURCE_CLASS_NON_PROMOTIVE_WITHOUT_SEPARATE_NATIVE_DERIVATION")
        rule = get_rule(str(row["governing_rule"]))
        if rule is None: reasons.append("GOVERNING_RULE_UNAVAILABLE")
        for dependency in dependencies:
            drow = self.db.conn.execute("SELECT derivation_json FROM semantic_derivations WHERE derivation_id=?", (dependency,)).fetchone()
            if drow:
                supporting_derivation = json.loads(drow[0])
                supporting_proposition = self.get_proposition(supporting_derivation["output_proposition"])["proposition"]
                break
        if source["primary_class"] == "UNRESOLVED_EXPRESSION":
            if supporting_derivation is None or supporting_proposition is None:
                reasons.append("UNRESOLVED_DEPENDENCIES")
            elif supporting_proposition["source_expression"] != source["source_expression"] or supporting_proposition["primary_class"] != "DERIVABLE_CONSEQUENCE":
                reasons.append("DERIVATION_DOES_NOT_ESTABLISH_SOURCE_PROPOSITION")
        target_class = str(row["target_class"])
        if target_class == "DECLARED_SYSTEM_LAW" and authority_level != "A4": reasons.append("DECLARATION_PROMOTION_REQUIRES_A4")
        decision = "AUTHORIZED" if authorize and not reasons else "REJECTED"
        promoted: dict[str, Any] | None = None
        source_row = self.db.conn.execute("SELECT ast_id FROM semantic_propositions WHERE proposition_id=?", (source["proposition_id"],)).fetchone()
        if decision == "AUTHORIZED":
            promoted = dict(source)
            promoted["primary_class"] = target_class
            if supporting_proposition:
                promoted["consequence_class"] = supporting_proposition["consequence_class"]
            promoted["authority_level"] = authority_level
            promoted["dependencies"] = sorted(set(list(source.get("dependencies", [])) + [str(x) for x in dependencies] + [str(row["governing_rule"])]))
            promoted["interpretation_version"] = INTERPRETATION_VERSION + "+PROMOTION"
            core = {k: v for k, v in promoted.items() if k not in {"proposition_id", "interpretation_hash", "hash72_identity"}}
            promoted["proposition_id"] = stable_id("PROP", "hhs_pass148_promoted_proposition_id_v1", core)
            promoted["interpretation_hash"] = hash72("hhs_pass148_promoted_interpretation_v1", core)
            promoted["hash72_identity"] = hash72("hhs_pass148_promoted_proposition_v1", {**core, "proposition_id": promoted["proposition_id"]})
        core = {"promotion_request_id": promotion_request_id, "verifier_identity": verifier_identity, "authority_level": authority_level, "decision": decision, "rationale": rationale, "blocking_reasons": reasons, "target_class": target_class, "source_proposition_id": row["source_proposition_id"], "target_proposition_id": promoted["proposition_id"] if promoted else None, "supporting_derivation_id": supporting_derivation.get("derivation_id") if supporting_derivation else None}
        decision_id = stable_id("PMD", "hhs_pass148_promotion_decision_id_v1", core); decision_hash = hash72("hhs_pass148_promotion_decision_v1", {"promotion_decision_id": decision_id, **core})
        def apply(conn):
            if promoted is not None:
                conn.execute("INSERT OR IGNORE INTO semantic_propositions(proposition_id,ast_id,source_expression,source_type,source_reference,primary_class,consequence_class,authority_level,operator_profile,lane_scope_json,gate_scope_json,branch_conditions_json,dependencies_json,assumptions_json,prohibited_promotions_json,interpretation_version,interpretation_hash,proposition_hash72,proposition_json,active,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1,?)", (promoted["proposition_id"], source_row["ast_id"], promoted["source_expression"], promoted["source_type"], promoted["source_reference"], promoted["primary_class"], promoted["consequence_class"], promoted["authority_level"], promoted["operator_profile"], canonical_json(promoted["lane_scope"]), canonical_json(promoted["gate_scope"]), canonical_json(promoted["branch_conditions"]), canonical_json(promoted["dependencies"]), canonical_json(promoted["assumptions"]), canonical_json(promoted["prohibited_promotions"]), promoted["interpretation_version"], promoted["interpretation_hash"], promoted["hash72_identity"], canonical_json(promoted), utc_now()))
            conn.execute("INSERT INTO semantic_promotion_decisions(promotion_decision_id,promotion_request_id,verifier_identity,authority_level,decision,decision_json,decision_hash72,receipt_id,created_at) VALUES(?,?,?,?,?,?,?,NULL,?)", (decision_id, promotion_request_id, verifier_identity, authority_level, decision, canonical_json(core), decision_hash, utc_now()))
            conn.execute("UPDATE semantic_promotion_requests SET status=? WHERE promotion_request_id=?", ("PROMOTION_AUTHORIZED" if decision == "AUTHORIZED" else "PROMOTION_REJECTED", promotion_request_id))
            return {"status": "PROMOTION_AUTHORIZED" if decision == "AUTHORIZED" else "PROMOTION_REJECTED", "promotion_decision_id": decision_id, "decision_hash72": decision_hash, "blocking_reasons": reasons, "authority_changed": decision == "AUTHORIZED", "target_proposition_id": promoted["proposition_id"] if promoted else None}
        tx = self.db.mutate("SEMANTIC_PROMOTION_EVALUATE", {"promotion_request_id": promotion_request_id, "decision_hash72": decision_hash}, apply, receipt_type="SEMANTIC_PROMOTION_DECISION_RECEIPT")
        attach = self.db.mutate("SEMANTIC_PROMOTION_DECISION_ATTACH_RECEIPT", {"promotion_decision_id": decision_id, "decision_receipt_id": tx["receipt_id"]}, lambda conn: (conn.execute("UPDATE semantic_promotion_decisions SET receipt_id=? WHERE promotion_decision_id=?", (tx["receipt_id"], decision_id)), {"status": "PROMOTION_DECISION_RECEIPT_ATTACHED", "promotion_decision_id": decision_id, "decision_receipt_id": tx["receipt_id"]})[1], receipt_type="SEMANTIC_PROMOTION_DECISION_RECEIPT_ATTACHMENT")
        return {"schema": "HHS_PASS148_PROMOTION_DECISION_V1", "decision": {"promotion_decision_id": decision_id, **core, "decision_hash72": decision_hash}, "promoted_proposition": promoted, "persistence": tx, "receipt": tx["receipt_id"], "receipt_attachment": attach["receipt_id"]}

    def replay_semantic(self, target_id: str) -> dict[str, Any]:
        prop_row = self.db.conn.execute("SELECT proposition_json FROM semantic_propositions WHERE proposition_id=?", (target_id,)).fetchone()
        if prop_row:
            original = json.loads(prop_row[0])
            drow = self.db.conn.execute("SELECT derivation_json FROM semantic_derivations WHERE output_proposition_id=? ORDER BY created_at LIMIT 1", (target_id,)).fetchone()
            if drow and original["primary_class"] == "DERIVABLE_CONSEQUENCE":
                derivation = json.loads(drow[0]); inputs = [self.get_proposition(pid)["proposition"] for pid in derivation["input_propositions"]]; step = derivation["ordered_steps"][0]
                replay_bundle = derive_consequence(inputs, rule_id=step["rule_id"], substitutions=step.get("substitution")); replayed_prop = replay_bundle["output_proposition"]; replayed_ast_hash = replay_bundle["output_ast"]["canonical_ast_hash"]
            else:
                replay_bundle = analyze_expression(original["source_expression"], source_type=original["source_type"], source_reference=original["source_reference"], profile_id=original["operator_profile"], declared_scope=original.get("scope", {}), governing_contracts=original.get("governing_contracts", [])); replayed_prop = replay_bundle["proposition"]; replayed_ast_hash = replay_bundle["ast"]["canonical_ast_hash"]
            original_hash = original["hash72_identity"]; replay_hash = replayed_prop["hash72_identity"]
            comparison = {"ast": replayed_ast_hash == original["canonical_ast_hash"], "classification": replayed_prop["primary_class"] == original["primary_class"] and replayed_prop["consequence_class"] == original["consequence_class"], "proposition_hash": replay_hash == original_hash}
            target_type = "PROPOSITION"
        else:
            proj_row = self.db.conn.execute("SELECT projection_json FROM semantic_projections WHERE projection_id=?", (target_id,)).fetchone()
            if proj_row:
                original = json.loads(proj_row[0]); replayed = run_control_projection(original["source_expression"], profile_id=original["profile_id"], assumptions=original["assumptions"])
                original_hash = original["projection_hash72"]; replay_hash = replayed["projection_hash72"]; comparison = {"projection_hash": original_hash == replay_hash}; target_type = "PROJECTION"
            else:
                drv_row = self.db.conn.execute("SELECT derivation_json FROM semantic_derivations WHERE derivation_id=?", (target_id,)).fetchone()
                if not drv_row: raise Pass145Error("SEMANTIC_REPLAY_TARGET_NOT_FOUND", "semantic replay target not found", "SEMANTIC_REPLAY", target_id)
                original = json.loads(drv_row[0]); inputs = [self.get_proposition(pid)["proposition"] for pid in original["input_propositions"]]; step = original["ordered_steps"][0]
                replayed = derive_consequence(inputs, rule_id=step["rule_id"], substitutions=step.get("substitution")); original_hash = original["derivation_hash72"]; replay_hash = replayed["derivation"]["derivation_hash72"]; comparison = {"derivation_hash": original_hash == replay_hash}; target_type = "DERIVATION"
        ok = all(comparison.values())
        core = {"target_type": target_type, "target_id": target_id, "original_hash72": original_hash, "replay_hash72": replay_hash, "status": "REPLAY_VALIDATED" if ok else "REPLAY_MISMATCH", "comparison": comparison, "registry_version": SEMANTIC_REGISTRY_VERSION}
        replay_id = stable_id("SRP", "hhs_pass148_replay_id_v1", core)
        def apply(conn):
            conn.execute("INSERT OR REPLACE INTO semantic_replays(replay_id,target_type,target_id,original_hash72,replay_hash72,status,replay_json,created_at) VALUES(?,?,?,?,?,?,?,?)", (replay_id, target_type, target_id, original_hash, replay_hash, core["status"], canonical_json(core), utc_now()))
            return {"replay_id": replay_id, **core}
        tx = self.db.mutate("SEMANTIC_REPLAY", {"target_type": target_type, "target_id": target_id}, apply, receipt_type="SEMANTIC_REPLAY_RECEIPT")
        return {"schema": "HHS_PASS148_REPLAY_V1", **core, "ok": ok, "replay_id": replay_id, "persistence": tx, "receipt": tx["receipt_id"]}

    def create_external_agent(self, issuer_identity: str, issuer_grant: str, issuer_token: str, name: str, *, capabilities: Sequence[str] | None = None) -> dict[str, Any]:
        requested = sorted(set(capabilities or [
            "PUBLIC_DISCOVERY", "DOCUMENTATION_READ", "EXTERNAL_AGENT", "PATH_EXECUTION",
            "DATABASE_READ", "DATABASE_WRITE", "QUERY", "SEARCH", "VALIDATE", "INGEST",
            "FILESYSTEM_READ", "FILESYSTEM_WRITE", "NATIVE_RUNTIME", "INTER_SANDBOX", "LOCAL_API",
            "SEMANTIC_READ", "SEMANTIC_ANALYZE", "SEMANTIC_DERIVE", "SEMANTIC_PROJECT", "SEMANTIC_PROMOTION_REQUEST",
        ]))
        forbidden = {"SECURITY_ADMIN", "NETWORK_SEND", "NETWORK_RECEIVE", "SEMANTIC_AUTHORITY_ADMIN"}
        if forbidden.intersection(requested):
            raise Pass145Error("PRIVILEGED_INTERNAL_ACCESS_PROHIBITED", f"external-agent bootstrap cannot include privileged capabilities: {sorted(forbidden.intersection(requested))}", "EXTERNAL_AGENT")
        identity = self.security.create_identity(issuer_identity, issuer_grant, issuer_token, name, identity_type="EXTERNAL_AGENT")
        operations = [
            "RUN_CLI_COMMAND", "PUBLIC_DISCOVER", "PUBLIC_DOC_QUERY",
            "SEMANTIC_ANALYZE", "SEMANTIC_DOCUMENT_ANALYZE", "SEMANTIC_DERIVE", "SEMANTIC_PROJECT",
            "SEMANTIC_PROMOTION_REQUEST", "SEMANTIC_RETRIEVE", "SEMANTIC_RULE_READ", "SEMANTIC_REPLAY", "SEMANTIC_AUDIT",
        ]
        grant = self.security.create_grant(issuer_identity, issuer_grant, issuer_token, identity["result"]["identity_id"], capabilities=requested, operations=operations, sources=["*", "PUBLIC_SURFACE", "SEMANTIC_MEMBRANE"], destinations=["LOCAL_RESULT"], resource_policy={"max_steps": 64, "max_output_bytes": 4 * 1024 * 1024, "max_recursive_depth": 16, "max_messages": 64, "timeout_seconds": 30}, disclosure_policy={"classifications": ["PUBLIC", "INTERNAL"], "allow_remote": False})
        profile = {"identity_id": identity["result"]["identity_id"], "grant_id": grant["result"]["grant_id"], "name": name, "capabilities": requested, "operations": operations, "privileged_internal_access": 0, "privileged_semantic_authority": 0, "procedural_external": True}
        profile_id = stable_id("AGT", "hhs_pass148_external_agent_profile_id_v1", profile)
        profile_hash = hash72("hhs_pass148_external_agent_profile_v1", profile)
        def apply(conn):
            conn.execute("INSERT INTO external_agent_profiles(profile_id,identity_id,grant_id,name,profile_json,profile_hash72,active,created_at) VALUES(?,?,?,?,?,?,1,?)", (profile_id, profile["identity_id"], profile["grant_id"], name, canonical_json(profile), profile_hash, utc_now()))
            return {"status": "PASS148_EXTERNAL_AGENT_PROFILE_CREATED", "profile_id": profile_id, "profile_hash72": profile_hash, **profile}
        stored = self.db.mutate("PASS148_EXTERNAL_AGENT_PROFILE_CREATE", {"profile_hash72": profile_hash}, apply, receipt_type="EXTERNAL_AGENT_PROFILE_RECEIPT")
        return {"schema": "HHS_PASS148_EXTERNAL_AGENT_BOOTSTRAP_V1", "profile": stored["result"], "authentication_token": identity["authentication_token"], "token_displayed_once": True}

    def external_execute(self, identity_id: str, grant_id: str, token: str, argv: Sequence[str], *, stdin_text: str | None = None) -> dict[str, Any]:
        args = [str(x) for x in argv]
        if args and args[0] == "semantic":
            from .cli import semantic_request_from_argv
            operation, request = semantic_request_from_argv(args, stdin_text=stdin_text)
            if operation in {"SEMANTIC_PROMOTION_EVALUATE", "SEMANTIC_REGISTRY_SYNC"}:
                raise Pass145Error("PRIVILEGED_INTERNAL_ACCESS_PROHIBITED", "external agents may request promotion but cannot evaluate authority or mutate the native rule registry", "EXTERNAL_AGENT")
            if operation in {"SEMANTIC_ANALYZE", "SEMANTIC_DOCUMENT_ANALYZE"} and request.get("source_type") in {"contract", "runtime", "user_declaration"}:
                raise Pass145Error(
                    "SEMANTIC_SOURCE_AUTHORITY_UNVERIFIED",
                    "an external agent cannot manufacture authoritative source identity through request fields; use model_output, documentation, fiction, or control_engine and reference the public rule separately",
                    "EXTERNAL_AGENT",
                )
            constructed = self.security.construct_path(identity_id, grant_id, token, operation, request)
            executed = self.security.execute_path(constructed["result"]["contract_id"], identity_id, token)
            return {"schema": "HHS_PASS148_EXTERNAL_AGENT_SEMANTIC_EXECUTION_V1", "operation": operation, "construction": constructed["result"], "execution": executed["result"], "privileged_internal_access": 0, "privileged_semantic_authority": 0, "public_primitives_only": True}
        return super().external_execute(identity_id, grant_id, token, args, stdin_text=stdin_text)

    def semantic_audit(self) -> dict[str, Any]:
        registry = self.registry_audit()
        bad = [dict(r) for r in self.db.conn.execute("SELECT proposition_id,primary_class,authority_level,operator_profile FROM semantic_propositions WHERE (primary_class='CONTROL_PROJECTION' AND authority_level!='A1') OR (primary_class='NARRATIVE_EXTRAPOLATION' AND authority_level!='A1')")]
        mutated_projection = [dict(r) for r in self.db.conn.execute("SELECT projection_id FROM semantic_projections WHERE native_state_mutation!=0")]
        unresolved_promoted = [dict(r) for r in self.db.conn.execute("SELECT r.promotion_request_id,d.decision FROM semantic_promotion_requests r JOIN semantic_promotion_decisions d USING(promotion_request_id) JOIN semantic_propositions p ON p.proposition_id=r.source_proposition_id WHERE p.primary_class='UNRESOLVED_EXPRESSION' AND d.decision='AUTHORIZED' AND r.dependency_set_json='[]'")]
        closed = registry["closed"] and not bad and not mutated_projection and not unresolved_promoted
        return {"schema": "HHS_PASS148_SEMANTIC_AUDIT_V1", "closed": closed, "registry": registry, "authority_violations": bad, "native_projection_mutations": mutated_projection, "unresolved_unauthorized_promotions": unresolved_promoted, "external_privileged_semantic_authority": 0}
