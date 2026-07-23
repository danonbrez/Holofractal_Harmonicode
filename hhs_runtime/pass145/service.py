from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from hhs_runtime.hhs_pass125_canonical_document_ingestion_v1 import (
    CanonicalDocumentIngestionEngine,
    DocumentIngestionBounds,
)
from hhs_runtime.hhs_pass126_document_claim_interpretation_v1 import (
    CanonicalDocumentInterpretationEngine,
    DocumentInterpretationBounds,
    Pass126Error,
)

from .canonical import canonical_json, hash72, sha256_bytes, stable_id
from .database import HHS145Database, SCHEMA_ID, SCHEMA_VERSION
from .errors import Pass145Error
from .parsers import PARSER_VERSION, ParseBounds, detect_mime, parse_document

PASS_ID = "HHS-P145"
VERSION = "145.1.0"


def _claim_core(text: str) -> str:
    value = re.sub(r"\b(?:no|not|never|cannot|can't|does\s+not|isn't|aren't|without)\b", " ", text.casefold())
    value = re.sub(r"[^\wπΩΨΘΔ]+", " ", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value).strip()


def _query_tokens(text: str) -> list[str]:
    # π and O remain distinct tokens by construction.
    return re.findall(r"π|Ω|Ψ|Θ|Δ|[A-Za-z_][A-Za-z0-9_\-]*|\d+", text, flags=re.UNICODE)


class HHS145Service:
    def __init__(self, db_path: str | Path, *, parse_bounds: ParseBounds | None = None):
        self.db = HHS145Database(db_path)
        self.parse_bounds = parse_bounds or ParseBounds()
        self.ingestion = CanonicalDocumentIngestionEngine(
            DocumentIngestionBounds(
                max_bytes=self.parse_bounds.max_bytes,
                max_segments=self.parse_bounds.max_segments,
                max_segment_chars=self.parse_bounds.max_segment_chars,
                max_metadata_fields=128,
            )
        )
        self.interpretation = CanonicalDocumentInterpretationEngine(
            DocumentInterpretationBounds(
                max_segments=self.parse_bounds.max_segments,
                max_claims=131072,
                max_claim_chars=8192,
                max_relations=524288,
                max_support_roots=512,
            )
        )

    def close(self) -> None:
        self.db.close()

    def __enter__(self) -> "HHS145Service":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def version(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS145_VERSION_V1",
            "pass_id": PASS_ID,
            "version": VERSION,
            "database_schema": {"id": SCHEMA_ID, "version": SCHEMA_VERSION},
            "parser_version": PARSER_VERSION,
            "parent": "HHS-P144",
        }

    def capabilities(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS145_CAPABILITIES_V1",
            "pass_id": PASS_ID,
            "capabilities": {
                "local_document_ingestion": "CLI_AVAILABLE",
                "source_preservation": "CLI_AVAILABLE",
                "transactional_knowledge_database": "CLI_AVAILABLE",
                "natural_language_query": "CLI_AVAILABLE",
                "deterministic_replay": "CLI_AVAILABLE",
                "workspace_sandboxes": "CLI_AVAILABLE",
                "script_workbench": "CLI_AVAILABLE",
                "logical_virtual_machines": "CLI_AVAILABLE",
                "loopback_api": "CLI_AVAILABLE",
                "workspace_management": "CLI_AVAILABLE",
                "api_workbench": "CLI_AVAILABLE",
                "governed_extensions": "CLI_AVAILABLE",
                "html_javascript_ui": "WEB_UI_AVAILABLE",
                "native_android_runtime_binding": "OBSERVED_FAILING",
                "installable_apk": "OBSERVED_FAILING",
                "real_device_validation": "NOT_EXPOSED",
            },
            "android_build_block": {
                "code": "ANDROID_BUILD_TOOLCHAIN_UNAVAILABLE",
                "required": ["Android SDK", "aapt2", "d8", "apksigner", "android.jar"],
                "not_a_capability_success": True,
                "source_projection_present": True,
                "build_attempt_outcome": "APK_BUILD_FAILED",
            },
        }

    def status(self) -> dict[str, Any]:
        integrity = self.db.integrity_check()
        chain = self.db.verify_receipt_chain()
        counts = {}
        for table in ("sources", "segments", "objects", "relations", "validations", "workspaces", "environments", "scripts", "lvms", "api_collections", "extensions", "transactions", "receipts"):
            counts[table] = int(self.db.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
        return {
            "schema": "HHS_PASS145_STATUS_V1",
            "ok": bool(integrity["ok"] and chain["ok"]),
            "version": self.version(),
            "integrity": integrity,
            "receipt_chain": chain,
            "counts": counts,
            "offline_core": True,
        }

    def doctor(self) -> dict[str, Any]:
        checks = {
            "database_integrity": self.db.integrity_check(),
            "receipt_chain": self.db.verify_receipt_chain(),
            "symbol_separation": {
                "ok": _query_tokens("O π") == ["O", "π"],
                "O_token": _query_tokens("O")[0],
                "pi_token": _query_tokens("π")[0],
                "constraint": "O != π",
            },
            "query_non_mutation": self._doctor_query_nonmutation(),
        }
        return {"schema": "HHS_PASS145_DOCTOR_V1", "ok": all(v.get("ok", False) for v in checks.values()), "checks": checks}

    def _doctor_query_nonmutation(self) -> dict[str, Any]:
        before = self.db.database_root()
        self.search("__HHS_PASS145_NONEXISTENT__", limit=1)
        after = self.db.database_root()
        return {"ok": before == after, "before": before, "after": after}

    def ingest_path(self, path: str | Path, *, mime_type: str | None = None, namespace: str = "default", source_kind: str = "LOCAL_FILE", parent_source_id: str | None = None, analyze: bool = True) -> dict[str, Any]:
        p = Path(path).expanduser().resolve()
        if not p.is_file():
            raise Pass145Error("INGESTION_REJECTED", "source path is not a file", "ADMISSION", str(p))
        stat_before = p.stat()
        raw = p.read_bytes()
        result = self.ingest_bytes(raw, name=p.name, mime_type=mime_type, namespace=namespace, source_kind=source_kind, acquisition={"path": str(p), "method": "LOCAL_FILE"}, parent_source_id=parent_source_id, analyze=analyze)
        stat_after = p.stat()
        if stat_before.st_size != stat_after.st_size or stat_before.st_mtime_ns != stat_after.st_mtime_ns:
            raise Pass145Error("SOURCE_PRESERVATION_FAILED", "source changed during ingestion", "SOURCE_PRESERVATION", str(p))
        return result

    def ingest_bytes(self, raw: bytes, *, name: str, mime_type: str | None = None, namespace: str = "default", source_kind: str = "LOCAL_BYTES", acquisition: Mapping[str, Any] | None = None, parent_source_id: str | None = None, analyze: bool = True) -> dict[str, Any]:
        bundle = parse_document(raw, name=name, mime_type=mime_type, source_kind=source_kind, namespace=namespace, acquisition=dict(acquisition or {}), bounds=self.parse_bounds)
        admitted = self.db.insert_source_bundle(bundle, namespace=namespace, logical_key=f"{namespace}:{name}", parent_source_id=parent_source_id)
        source_id = admitted["result"]["source_id"]
        duplicate = admitted["result"]["status"] == "DUPLICATE_SOURCE"
        interpretation_result: dict[str, Any] | None = None
        contradiction_result: dict[str, Any] | None = None
        if analyze and not duplicate:
            interpretation_result = self._interpret_and_store(bundle, source_id=source_id, namespace=namespace)
            contradiction_result = self._detect_and_store_contradictions(source_id=source_id, namespace=namespace)
        validation = self.validate_source(source_id, record=not duplicate)
        execution_receipts = {
            "DOCUMENT_INGESTION_RECEIPT": {"receipt_id": admitted["receipt_id"], "receipt_hash72": admitted["receipt_hash72"]},
            "SOURCE_PRESERVATION_RECEIPT": {
                "source_id": source_id,
                "raw_sha256": bundle["source"]["raw_sha256"],
                "source_root_hash72": bundle["source"]["source_root_hash72"],
                "byte_length": bundle["source"]["byte_length"],
            },
            "PARSE_RECEIPT": {
                "parse_id": bundle["parse"]["parse_id"],
                "parse_root_hash72": bundle["parse"]["parse_root_hash72"],
                "parser_version": bundle["parse"]["parser_version"],
                "script_execution": bundle["parse"]["script_execution"],
            },
        }
        for receipt_name in ("SOURCE_PRESERVATION_RECEIPT", "PARSE_RECEIPT"):
            execution_receipts[receipt_name]["receipt_hash72"] = hash72(f"hhs_pass145_{receipt_name.casefold()}_v1", execution_receipts[receipt_name])
        if bundle["source"]["mime_type"] == "text/html":
            execution_receipts["HTML_PARSE_RECEIPT"] = {
                "source_id": source_id,
                "parse_root_hash72": bundle["parse"]["parse_root_hash72"],
                "script_count": len(bundle["parse"]["parsed"].get("scripts", [])),
                "script_execution": "NOT_PERFORMED",
            }
            execution_receipts["HTML_PARSE_RECEIPT"]["receipt_hash72"] = hash72("hhs_pass145_html_parse_receipt_v1", execution_receipts["HTML_PARSE_RECEIPT"])
        if bundle["source"]["mime_type"] in {"text/javascript", "application/javascript"}:
            execution_receipts["JAVASCRIPT_ANALYSIS_RECEIPT"] = {
                "source_id": source_id,
                "parse_root_hash72": bundle["parse"]["parse_root_hash72"],
                "execution_performed": False,
                "static_analysis_hash72": hash72("hhs_pass145_javascript_static_analysis_v1", bundle["parse"]["parsed"].get("static_analysis", {})),
            }
            execution_receipts["JAVASCRIPT_ANALYSIS_RECEIPT"]["receipt_hash72"] = hash72("hhs_pass145_javascript_analysis_receipt_v1", execution_receipts["JAVASCRIPT_ANALYSIS_RECEIPT"])
        return {
            "schema": "HHS_PASS145_INGESTION_RESULT_V1",
            "status": "DUPLICATE_SOURCE" if duplicate else "SOURCE_ADMITTED",
            "source_id": source_id,
            "source_root_hash72": admitted["result"]["source_root_hash72"],
            "parse_id": admitted["result"].get("parse_id"),
            "segment_count": admitted["result"].get("segment_count", 0),
            "entity_count": admitted["result"].get("entity_count", 0),
            "interpretation": interpretation_result,
            "contradictions": contradiction_result,
            "validation": validation,
            "receipts": execution_receipts,
            "receipt_id": admitted["receipt_id"],
            "receipt_hash72": admitted["receipt_hash72"],
            "database_root_hash72": self.db.database_root(),
        }

    def _interpret_and_store(self, bundle: Mapping[str, Any], *, source_id: str, namespace: str) -> dict[str, Any]:
        text = str(bundle["parse"].get("extracted_text", ""))
        if not text.strip():
            return {"status": "UNVALIDATED", "reason": "NO_EXTRACTED_TEXT", "claim_count": 0}
        derived = self.ingestion.ingest_bytes(
            text.encode("utf-8"),
            source_kind="PASS145_DERIVED_TEXT_PROJECTION",
            source_id=bundle["parse"]["parse_id"],
            mime_type="text/plain",
            metadata={
                "parent_source_id": source_id,
                "parent_source_root_hash72": bundle["source"]["source_root_hash72"],
                "parse_root_hash72": bundle["parse"]["parse_root_hash72"],
            },
        )
        derived_segments = self.ingestion.segment(derived)
        try:
            inherited_claims = self.interpretation.extract_claims(derived, derived_segments)
        except Pass126Error as exc:
            if exc.code == "REJECT_EMPTY_INTERPRETATION":
                return {"status": "UNVALIDATED", "reason": exc.code, "claim_count": 0}
            raise Pass145Error("EXTRACTION_INCOMPLETE", str(exc), "INTERPRETATION", source_id) from exc
        claims: list[dict[str, Any]] = []
        for claim in inherited_claims:
            inherited_claim_type = claim["claim_type"]
            pass145_claim_type = self._classify_claim_type(
                claim["verbatim_text"],
                claim["normalized_proposition"],
                inherited_claim_type,
            )
            base = {
                "schema": "HHS_PASS145_CLAIM_V1",
                "claim_text": claim["verbatim_text"],
                "canonical_form": claim["normalized_proposition"],
                "source_segment_ids": [bundle["segments"][claim["segment_index"]]["segment_id"]] if claim["segment_index"] < len(bundle["segments"]) else [],
                "source_evidence_ids": [source_id, bundle["parse"]["parse_id"]],
                "speaker_or_author": None,
                "scope": namespace,
                "time_scope": None,
                "modality": claim["uncertainty"],
                "negation": claim["polarity"] == "NEGATIVE",
                "polarity": claim["polarity"],
                "claim_type": pass145_claim_type,
                "inherited_claim_type": inherited_claim_type,
                "classification_rule": "HHS_PASS145_CLAIM_CLASSIFICATION_V1",
                "authority_level": "A1",
                "validation_state": "UNVALIDATED",
                "truth_status": "UNVALIDATED_DOCUMENT_CLAIM",
                "interpretation_version": "P145-INTERPRETATION-1",
                "governing_contract": "HHS-P145+HHS-I132",
                "inherited_claim_root_hash72": claim["claim_root_hash72"],
                "source_start_char": claim["source_start_char"],
                "source_end_char": claim["source_end_char"],
                "execution_authority": False,
                "mutation_authority": False,
                "relationships": [],
            }
            base["interpretation_hash"] = hash72("hhs_pass145_interpretation_v1", base)
            base["object_hash72"] = hash72("hhs_pass145_claim_v1", base)
            base["object_id"] = stable_id("CLM", "hhs_pass145_claim_id_v1", {"source_id": source_id, "hash": base["object_hash72"]})
            claims.append(base)
        relations = self._claim_entity_relations(source_id, claims)
        committed = self.db.insert_objects(source_id, namespace, claims, relations)
        return {
            "status": "INTERPRETATION_COMMITTED",
            "claim_count": len(claims),
            "relation_count": len(relations),
            "receipt_id": committed["receipt_id"],
            "receipt_hash72": committed["receipt_hash72"],
        }

    @staticmethod
    def _classify_claim_type(verbatim: str, normalized: str, inherited_type: str) -> str:
        """Deterministically refine only forms required by the Pass 145 object model.

        The inherited Pass 126 classification is retained separately.  This adapter
        recognizes explicit definitional copulas without changing source wording.
        """
        candidates = [str(verbatim).strip(), str(normalized).strip()]
        definition_patterns = (
            r"^\s*[^.?!:]{1,160}\s+(?:is|means|denotes|defines|refers\s+to|shall\s+mean)\s+[^.?!]+[.?!]?\s*$",
            r"^\s*define\s+[^.?!:]{1,160}\s+as\s+[^.?!]+[.?!]?\s*$",
        )
        if any(re.match(pattern, text, flags=re.IGNORECASE) for text in candidates for pattern in definition_patterns):
            return "DEFINITION"
        return inherited_type

    def _claim_entity_relations(self, source_id: str, claims: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
        entities = [dict(r) for r in self.db.conn.execute("SELECT object_id,exact_text,object_type FROM objects WHERE source_id=? AND object_type IN ('SYMBOL','IDENTIFIER','URL','DATE')", (source_id,))]
        relations: list[dict[str, Any]] = []
        for claim in claims:
            text = str(claim["claim_text"])
            for entity in entities:
                exact = entity["exact_text"]
                if exact and re.search(rf"(?<!\w){re.escape(exact)}(?!\w)", text):
                    rtype = "DEFINES" if claim["claim_type"] == "DEFINITION" else "REFERS_TO"
                    payload = {
                        "relation_type": rtype,
                        "left_object_id": claim["object_id"],
                        "right_object_id": entity["object_id"],
                        "provenance": {"source_id": source_id, "claim_id": claim["object_id"], "entity_id": entity["object_id"]},
                    }
                    payload["relation_hash72"] = hash72("hhs_pass145_claim_entity_relation_v1", payload)
                    payload["relation_id"] = stable_id("REL", "hhs_pass145_claim_entity_relation_id_v1", payload)
                    relations.append(payload)
        return relations

    def _detect_and_store_contradictions(self, *, source_id: str, namespace: str) -> dict[str, Any]:
        current = [dict(r) for r in self.db.conn.execute("SELECT object_id,source_id,exact_text,normalized_text,object_json FROM objects WHERE source_id=? AND object_type IN ('ASSERTION','DEFINITION','EQUATION','DIRECTIVE')", (source_id,))]
        if not current:
            return {"status": "NO_CLAIMS", "contradiction_count": 0}
        all_claims = [dict(r) for r in self.db.conn.execute("SELECT object_id,source_id,exact_text,normalized_text,object_json FROM objects WHERE namespace=? AND object_type IN ('ASSERTION','DEFINITION','EQUATION','DIRECTIVE') AND quarantined=0", (namespace,))]
        contradictions: list[dict[str, Any]] = []
        relations: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()
        for left in current:
            lobj = json.loads(left["object_json"])
            lcore = _claim_core(left["normalized_text"] or left["exact_text"] or "")
            for right in all_claims:
                if left["object_id"] == right["object_id"]:
                    continue
                pair = tuple(sorted((left["object_id"], right["object_id"])))
                if pair in seen:
                    continue
                robj = json.loads(right["object_json"])
                rcore = _claim_core(right["normalized_text"] or right["exact_text"] or "")
                if lcore and lcore == rcore and bool(lobj.get("negation")) != bool(robj.get("negation")):
                    seen.add(pair)
                    c = {
                        "schema": "HHS_PASS145_CONTRADICTION_V1",
                        "object_type": "CONTRADICTION",
                        "conflicting_claim_ids": list(pair),
                        "exact_source_evidence": [left["source_id"], right["source_id"]],
                        "contradiction_type": "POLARITY_CONFLICT",
                        "scope": namespace,
                        "temporal_compatibility": "UNRESOLVED",
                        "namespace_compatibility": "SAME_NAMESPACE",
                        "authority_levels": [lobj.get("authority_level", "A1"), robj.get("authority_level", "A1")],
                        "conditional_compatibility": "UNRESOLVED",
                        "proposed_resolutions": [],
                        "accepted_resolution": None,
                        "validation_state": "CONTRADICTORY",
                        "authority_level": "A1",
                    }
                    c["object_hash72"] = hash72("hhs_pass145_contradiction_v1", c)
                    c["object_id"] = stable_id("CON", "hhs_pass145_contradiction_id_v1", c)
                    contradictions.append(c)
                    for claim_id in pair:
                        rel = {
                            "relation_type": "CONTRADICTS",
                            "left_object_id": c["object_id"],
                            "right_object_id": claim_id,
                            "provenance": {"source_ids": c["exact_source_evidence"], "contradiction_id": c["object_id"]},
                        }
                        rel["relation_hash72"] = hash72("hhs_pass145_contradiction_relation_v1", rel)
                        rel["relation_id"] = stable_id("REL", "hhs_pass145_contradiction_relation_id_v1", rel)
                        relations.append(rel)
        if not contradictions:
            return {"status": "NO_CONTRADICTIONS_DETECTED", "contradiction_count": 0}
        committed = self.db.insert_objects(source_id, namespace, contradictions, relations)
        return {"status": "CONTRADICTIONS_PRESERVED", "contradiction_count": len(contradictions), "receipt_id": committed["receipt_id"]}

    def validate_source(self, source_id: str, *, record: bool = True) -> dict[str, Any]:
        source = self.db.get_source(source_id, include_raw=True)
        if source is None:
            raise Pass145Error("PROVENANCE_INCOMPLETE", "source not found", "VALIDATION", source_id)
        raw = source["raw_bytes"]
        src = source["source"]
        stored_parse = source["parse"]
        stored_segments = source["segments"]
        rebuilt = parse_document(
            raw,
            name=src["source_name"],
            mime_type=src["mime_type"],
            source_kind=src["source_kind"],
            namespace=src["namespace"],
            acquisition=src.get("acquisition", {}),
            bounds=self.parse_bounds,
        )
        extracted_text = str(stored_parse.get("extracted_text", ""))
        object_rows = [dict(r) for r in self.db.conn.execute(
            "SELECT object_id,object_type,segment_id,exact_text,normalized_text,object_json FROM objects WHERE source_id=?",
            (source_id,),
        )]
        segment_ids = {s["segment_id"] for s in stored_segments}
        contiguous = True
        cursor = 0
        for segment in stored_segments:
            if segment["start_offset"] != cursor or segment["end_offset"] < segment["start_offset"] or segment["text"] != extracted_text[segment["start_offset"]:segment["end_offset"]]:
                contiguous = False
                break
            cursor = segment["end_offset"]
        contiguous = contiguous and cursor == len(extracted_text)

        provenance_ok = all(
            row["segment_id"] is None or row["segment_id"] in segment_ids
            for row in object_rows
        )
        no_symbol_substitution = all(
            not ((row["exact_text"] == "O" and row["normalized_text"] == "π") or (row["exact_text"] == "π" and row["normalized_text"] == "O"))
            for row in object_rows
        )
        claim_span_ok = True
        stored_inherited_roots: set[str] = set()
        for row in object_rows:
            obj = json.loads(row["object_json"])
            inherited_root = obj.get("inherited_claim_root_hash72")
            if inherited_root:
                stored_inherited_roots.add(inherited_root)
                a, b = obj.get("source_start_char"), obj.get("source_end_char")
                if not isinstance(a, int) or not isinstance(b, int) or extracted_text[a:b] != obj.get("claim_text"):
                    claim_span_ok = False

        runtime_details: dict[str, Any]
        if extracted_text.strip():
            derived = self.ingestion.ingest_bytes(
                extracted_text.encode("utf-8"),
                source_kind="PASS145_DERIVED_TEXT_PROJECTION",
                source_id=stored_parse["parse_id"],
                mime_type="text/plain",
                metadata={
                    "parent_source_id": source_id,
                    "parent_source_root_hash72": src["source_root_hash72"],
                    "parse_root_hash72": stored_parse["parse_root_hash72"],
                },
            )
            derived_segments = self.ingestion.segment(derived)
            try:
                rebuilt_claims = self.interpretation.extract_claims(derived, derived_segments)
                rebuilt_roots = {c["claim_root_hash72"] for c in rebuilt_claims}
                runtime_ok = rebuilt_roots == stored_inherited_roots
                runtime_details = {"rebuilt_claim_count": len(rebuilt_roots), "stored_claim_count": len(stored_inherited_roots), "claim_roots_equal": runtime_ok}
            except Pass126Error as exc:
                runtime_ok = exc.code == "REJECT_EMPTY_INTERPRETATION" and not stored_inherited_roots
                runtime_details = {"exception_code": exc.code, "claim_roots_equal": runtime_ok}
        else:
            runtime_ok = not stored_inherited_roots
            runtime_details = {"not_applicable": True, "reason": "NO_EXTRACTED_TEXT"}

        contradiction_rows = [json.loads(r[0]) for r in self.db.conn.execute(
            "SELECT object_json FROM objects WHERE source_id=? AND object_type='CONTRADICTION'",
            (source_id,),
        )]
        cross_document_ok = True
        missing_endpoints: list[str] = []
        for contradiction in contradiction_rows:
            for claim_id in contradiction.get("conflicting_claim_ids", []):
                if not self.db.conn.execute("SELECT 1 FROM objects WHERE object_id=?", (claim_id,)).fetchone():
                    cross_document_ok = False
                    missing_endpoints.append(claim_id)

        chain = self.db.verify_receipt_chain()
        layer_values = {
            "V1_BYTE_INTEGRITY": (sha256_bytes(raw) == src["raw_sha256"] and len(raw) == src["byte_length"], {"sha256_recomputed": True, "byte_length_recomputed": True}),
            "V2_FORMAT_INTEGRITY": (rebuilt["parse"]["parse_root_hash72"] == stored_parse["parse_root_hash72"], {"reparsed": True, "parser_version": stored_parse["parser_version"]}),
            "V3_STRUCTURAL_INTEGRITY": (contiguous and [x["segment_hash"] for x in rebuilt["segments"]] == [x["segment_hash"] for x in stored_segments], {"contiguous": contiguous, "segment_count": len(stored_segments)}),
            "V4_SCHEMA_INTEGRITY": (src.get("schema") == "HHS_PASS145_SOURCE_EVIDENCE_V1" and stored_parse.get("schema") == "HHS_PASS145_PARSE_V1" and all(s.get("schema") == "HHS_PASS145_SEGMENT_V1" for s in stored_segments), {"schemas_checked": [src.get("schema"), stored_parse.get("schema")]}),
            "V5_PROVENANCE_INTEGRITY": (provenance_ok and stored_parse.get("source_id") == source_id and stored_parse.get("source_root_hash72") == src["source_root_hash72"], {"object_count": len(object_rows), "segment_references_valid": provenance_ok}),
            "V6_SEMANTIC_INTEGRITY": (no_symbol_substitution and claim_span_ok, {"O_distinct_from_pi": no_symbol_substitution, "claim_evidence_spans_valid": claim_span_ok}),
            "V7_RUNTIME_CONFORMANCE": (runtime_ok, runtime_details),
            "V8_CROSS_DOCUMENT_CONSISTENCY": (cross_document_ok, {"contradiction_count": len(contradiction_rows), "missing_endpoints": missing_endpoints}),
            "V9_RECEIPT_INTEGRITY": (chain["ok"], chain),
        }
        layers = {
            name: {
                "executed": True,
                "outcome": "VALIDATED" if ok else "VALIDATION_FAILED",
                "details": details,
            }
            for name, (ok, details) in layer_values.items()
        }
        all_ok = all(ok for ok, _ in layer_values.values())
        outcome = "VALIDATED" if all_ok else "VALIDATION_FAILED"
        result = {
            "schema": "HHS_PASS145_SOURCE_VALIDATION_V1",
            "source_id": source_id,
            "outcome": outcome,
            "layers": layers,
            "authority_level": "A1",
            "validators_executed": list(layers),
        }
        result["validation_result_hash72"] = hash72("hhs_pass145_source_validation_v1", result)
        if record:
            receipt = self.db.add_validation("SOURCE", source_id, "V1-V9", outcome, result)
            result["validation_id"] = receipt["result"]["validation_id"]
            result["receipt_id"] = receipt["receipt_id"]
            result["receipt_hash72"] = receipt["receipt_hash72"]
        return result

    def replay_ingestion(self, source_id: str) -> dict[str, Any]:
        stored = self.db.get_source(source_id, include_raw=True)
        if stored is None:
            raise Pass145Error("PROVENANCE_INCOMPLETE", "source not found", "REPLAY", source_id)
        src = stored["source"]
        rebuilt = parse_document(
            stored["raw_bytes"],
            name=src["source_name"],
            mime_type=src["mime_type"],
            source_kind=src["source_kind"],
            namespace=src["namespace"],
            acquisition=src.get("acquisition", {}),
            bounds=self.parse_bounds,
        )
        comparison = {
            "source_root_hash72": rebuilt["source"]["source_root_hash72"] == src["source_root_hash72"],
            "parse_root_hash72": rebuilt["parse"]["parse_root_hash72"] == stored["parse"]["parse_root_hash72"],
            "segment_roots": [s["segment_hash"] for s in rebuilt["segments"]] == [s["segment_hash"] for s in stored["segments"]],
        }
        status = "REPLAY_VALIDATED" if all(comparison.values()) else "REPLAY_MISMATCH"
        result = {"schema": "HHS_PASS145_REPLAY_RESULT_V1", "source_id": source_id, "status": status, "comparison": comparison, "would_mutate": False}
        result["replay_receipt_hash72"] = hash72("hhs_pass145_replay_receipt_v1", result)
        if status != "REPLAY_VALIDATED":
            raise Pass145Error("REPLAY_MISMATCH", "reconstructed ingestion differs from committed state", "REPLAY", source_id, details=result)
        return result

    def search(self, text: str, *, symbol: bool = False, object_type: str | None = None, source_id: str | None = None, namespace: str | None = None, limit: int = 100) -> dict[str, Any]:
        before = self.db.database_root()
        objects = self.db.search(text, object_type=object_type, source_id=source_id, namespace=namespace, limit=limit, exact_symbol=symbol)
        sources = [] if symbol or object_type else self.db.source_search(text, namespace=namespace, limit=limit)
        after = self.db.database_root()
        if before != after:
            raise Pass145Error("QUERY_PLAN_FAILED", "read-only search mutated canonical state", "QUERY")
        result = {
            "schema": "HHS_PASS145_SEARCH_RESULT_V1",
            "query": text,
            "mode": "EXACT_SYMBOL" if symbol else "LEXICAL",
            "objects": objects,
            "sources": sources,
            "result_count": len(objects) + len(sources),
            "database_root_unchanged": before == after,
        }
        result["search_result_hash72"] = hash72("hhs_pass145_search_result_v1", result)
        return result

    def compile_query(self, question: str, *, namespace: str | None = None) -> dict[str, Any]:
        q = question.strip()
        lowered = q.casefold()
        tokens = _query_tokens(q)
        plan_type = "GENERIC_SEARCH"
        object_type = None
        exact_symbol = None
        search_terms = [t for t in tokens if t.casefold() not in {"what", "which", "show", "every", "all", "the", "a", "an", "of", "in", "this", "source", "document", "documents", "list", "why", "was", "is", "are", "complete"}]
        if "definition" in lowered or "define" in lowered:
            plan_type = "DEFINITION_LOOKUP"
            object_type = "DEFINITION"
        if "contradiction" in lowered or "conflict" in lowered:
            plan_type = "CONTRADICTION_LOOKUP"
            object_type = "CONTRADICTION"
        m = re.search(r"symbol\s+([A-Za-z_][A-Za-z0-9_]*|π|Ω|Ψ|Θ|Δ)", q, re.I)
        if m:
            plan_type = "SYMBOL_LOOKUP"
            exact_symbol = m.group(1)
        if "ancestry" in lowered:
            plan_type = "ANCESTRY_TRACE"
        if "evidence" in lowered and "support" in lowered:
            plan_type = "EVIDENCE_TRACE"
        plan = {
            "schema": "HHS_PASS145_QUERY_PLAN_V1",
            "question": q,
            "plan_type": plan_type,
            "tokens": tokens,
            "search_terms": search_terms,
            "object_type": object_type,
            "exact_symbol": exact_symbol,
            "namespace": namespace,
            "read_only": True,
            "mutation_authority": False,
        }
        plan["query_plan_hash72"] = hash72("hhs_pass145_query_plan_v1", plan)
        return plan

    def query(self, question: str, *, namespace: str | None = None, limit: int = 100) -> dict[str, Any]:
        before = self.db.database_root()
        plan = self.compile_query(question, namespace=namespace)
        evidence: list[dict[str, Any]] = []
        derived: list[dict[str, Any]] = []
        if plan["plan_type"] == "SYMBOL_LOOKUP":
            if plan.get("object_type") == "DEFINITION":
                rows = self.db.conn.execute(
                    """SELECT DISTINCT o.object_id,o.object_type,o.source_id,o.segment_id,o.namespace,o.exact_text,o.normalized_text,o.object_hash72,o.authority_level,o.validation_state
                       FROM objects sym
                       JOIN relations r ON r.right_object_id=sym.object_id AND r.relation_type='DEFINES'
                       JOIN objects o ON o.object_id=r.left_object_id
                       WHERE sym.quarantined=0 AND o.quarantined=0 AND (sym.exact_text=? OR sym.normalized_text=?)
                         AND (? IS NULL OR o.namespace=?)
                       ORDER BY o.source_id,o.object_id LIMIT ?""",
                    (plan["exact_symbol"], plan["exact_symbol"], namespace, namespace, max(1, min(limit, 1000))),
                ).fetchall()
                evidence = [dict(r) for r in rows]
            else:
                evidence = self.db.search(plan["exact_symbol"], namespace=namespace, exact_symbol=True, limit=limit)
        elif plan["plan_type"] == "CONTRADICTION_LOOKUP":
            evidence = self.db.search("", object_type="CONTRADICTION", namespace=namespace, limit=limit)
        elif plan["plan_type"] == "ANCESTRY_TRACE":
            term = plan["search_terms"][-1] if plan["search_terms"] else ""
            matches = self.db.source_search(term, namespace=namespace, limit=limit)
            for source in matches:
                chain = []
                cursor = source
                while cursor:
                    chain.append(cursor)
                    parent = cursor.get("parent_source_id")
                    cursor = None if not parent else next(iter(self.db.conn.execute("SELECT source_id,source_root_hash72,namespace,logical_key,parent_source_id,source_name,mime_type,byte_length,raw_sha256 FROM sources WHERE source_id=?", (parent,))), None)
                    if cursor is not None:
                        cursor = dict(cursor)
                derived.append({"source_id": source["source_id"], "ancestry": chain})
        else:
            terms = plan["search_terms"] or [question]
            seen = set()
            for term in terms:
                for row in self.db.search(term, object_type=plan["object_type"], namespace=namespace, limit=limit):
                    if row["object_id"] not in seen:
                        evidence.append(row)
                        seen.add(row["object_id"])
        after = self.db.database_root()
        if before != after:
            raise Pass145Error("QUERY_PLAN_FAILED", "natural-language query mutated canonical state", "QUERY")
        answer = {
            "directly_retrieved_evidence": evidence,
            "database_derived_relationships": derived,
            "deterministic_calculations": {"result_count": len(evidence) + len(derived)},
            "model_generated_explanation": None,
            "unresolved_ambiguity": [] if evidence or derived else ["No matching canonical evidence was found."],
        }
        result = {
            "schema": "HHS_PASS145_QUERY_RESULT_V1",
            "query_plan": plan,
            "answer": answer,
            "database_root_unchanged": before == after,
            "authority_level": "A1",
        }
        result["query_result_hash72"] = hash72("hhs_pass145_query_result_v1", result)
        result["query_plan_receipt"] = {
            "schema": "HHS_PASS145_QUERY_PLAN_RECEIPT_V1",
            "query_plan_hash72": plan["query_plan_hash72"],
            "database_root_hash72": before,
            "mutation_authority": False,
        }
        result["query_plan_receipt"]["receipt_hash72"] = hash72("hhs_pass145_query_plan_receipt_v1", result["query_plan_receipt"])
        result["query_result_receipt"] = {
            "schema": "HHS_PASS145_QUERY_RESULT_RECEIPT_V1",
            "query_plan_hash72": plan["query_plan_hash72"],
            "query_result_hash72": result["query_result_hash72"],
            "database_root_hash72": after,
            "database_root_unchanged": before == after,
        }
        result["query_result_receipt"]["receipt_hash72"] = hash72("hhs_pass145_query_result_receipt_v1", result["query_result_receipt"])
        return result

    def graph_trace(self, object_id: str, *, max_depth: int = 16) -> dict[str, Any]:
        if max_depth <= 0 or max_depth > 128:
            raise Pass145Error("RESOURCE_BOUND_UNRESOLVED", "graph depth must be 1..128", "GRAPH")
        visited: set[str] = set()
        frontier = [(object_id, 0)]
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        while frontier:
            current, depth = frontier.pop(0)
            if current in visited or depth > max_depth:
                continue
            visited.add(current)
            obj = self.db.get_object(current)
            if obj:
                nodes.append({k: obj[k] for k in ("object_id", "object_type", "source_id", "exact_text", "object_hash72", "validation_state")})
                for rel in obj["relations"]:
                    edges.append(rel)
                    nxt = rel["right_object_id"] if rel["left_object_id"] == current else rel["left_object_id"]
                    frontier.append((nxt, depth + 1))
        return {"schema": "HHS_PASS145_GRAPH_TRACE_V1", "root_object_id": object_id, "max_depth": max_depth, "nodes": nodes, "edges": edges, "cycle_detected": len(edges) >= len(nodes) and bool(nodes)}

    def analyze_changes(self, source_a: str, source_b: str) -> dict[str, Any]:
        a = self.db.get_source(source_a)
        b = self.db.get_source(source_b)
        if not a or not b:
            raise Pass145Error("PROVENANCE_INCOMPLETE", "source version not found", "ANALYSIS")
        ta = a["parse"].get("extracted_text", "").splitlines()
        tb = b["parse"].get("extracted_text", "").splitlines()
        import difflib
        diff = list(difflib.unified_diff(ta, tb, fromfile=source_a, tofile=source_b, lineterm=""))
        result = {"schema": "HHS_PASS145_CHANGE_ANALYSIS_V1", "source_a": source_a, "source_b": source_b, "diff": diff, "changed": bool(diff)}
        result["analysis_hash72"] = hash72("hhs_pass145_change_analysis_v1", result)
        return result

    def quarantine(self, target_id: str) -> dict[str, Any]:
        return self.db.quarantine(target_id, release=False)

    def release_quarantine(self, target_id: str) -> dict[str, Any]:
        return self.db.quarantine(target_id, release=True)

    def backup_create(self, path: str | Path) -> dict[str, Any]:
        result = self.db.create_backup(path)
        receipt = self.db.mutate(
            "BACKUP_CREATE_RECORD",
            {"path": str(Path(path).expanduser().resolve()), "archive_sha256": result["archive_sha256"], "database_root_hash72": result["manifest"]["database_root_hash72"]},
            lambda conn: {"status": "BACKUP_RECORDED", "archive_sha256": result["archive_sha256"]},
            receipt_type="BACKUP_RECEIPT",
        )
        result["receipt_id"] = receipt["receipt_id"]
        result["receipt_hash72"] = receipt["receipt_hash72"]
        return result

    def backup_verify(self, path: str | Path) -> dict[str, Any]:
        return self.db.verify_backup(path)

    def restore_preview(self, path: str | Path) -> dict[str, Any]:
        return self.db.restore_preview(path)


__all__ = ["HHS145Service", "Pass145Error"]
