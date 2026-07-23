from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping, Sequence
from datetime import datetime, timezone

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass123_bounded_token_generalization_v1 import _canon
from hhs_runtime.hhs_pass126_document_claim_interpretation_v1 import (
    CanonicalDocumentInterpretationEngine, Pass126Error,
)

PASS_ID = "PASS_127"
EVIDENCE_SCHEMA = "HHS_KNOWLEDGE_EVIDENCE_ATTESTATION_V1"
POLICY_SCHEMA = "HHS_KNOWLEDGE_ADMISSION_POLICY_V1"
DECISION_SCHEMA = "HHS_KNOWLEDGE_ADMISSION_DECISION_V1"
RECORD_SCHEMA = "HHS_ADMITTED_KNOWLEDGE_RECORD_V1"
CORPUS_SCHEMA = "HHS_ADMITTED_KNOWLEDGE_CORPUS_V1"
REPLAY_SCHEMA = "HHS_KNOWLEDGE_ADMISSION_REPLAY_V1"

REJECTION_CODES = {
    "REJECT_INVALID_CANDIDATE", "REJECT_INVALID_EVIDENCE", "REJECT_EVIDENCE_ROOT_MISMATCH",
    "REJECT_POLICY_ROOT_MISMATCH", "REJECT_DECISION_ROOT_MISMATCH", "REJECT_RECORD_ROOT_MISMATCH",
    "REJECT_CORPUS_ROOT_MISMATCH", "REJECT_UNBOUNDED_ADMISSION", "REJECT_INSUFFICIENT_INDEPENDENT_SUPPORT",
    "REJECT_SOURCE_QUALITY", "REJECT_UNRESOLVED_CONTRADICTION", "REJECT_TEMPORAL_SCOPE_CONFLICT",
    "REJECT_FORMAL_VERIFICATION_REQUIRED", "REJECT_RUNTIME_VERIFICATION_REQUIRED", "REJECT_AUTHORITY_ESCALATION",
    "REJECT_EXECUTABLE_KNOWLEDGE_ESCALATION", "REJECT_REPLAY_MISMATCH", "REJECT_STALE_EVIDENCE",
}

class Pass127Error(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(f"{code}: {message}")

@dataclass(frozen=True)
class KnowledgeAdmissionBounds:
    max_evidence: int = 512
    max_independence_groups: int = 128
    max_records: int = 32768
    max_proposition_chars: int = 8192
    max_age_seconds: int = 315576000

class EvidenceGroundedKnowledgeAdmissionEngine:
    """Admits immutable knowledge only after bounded, independent, contradiction-aware validation."""
    SOURCE_QUALITY = {"UNKNOWN": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "AUTHORITATIVE": 4}
    EVIDENCE_KINDS = {"DOCUMENT_CLAIM", "FORMAL_PROOF", "RUNTIME_RECEIPT", "OBSERVATION", "DATASET", "EXTERNAL_ATTESTATION"}

    def __init__(self, bounds: KnowledgeAdmissionBounds | None = None):
        self.bounds = bounds or KnowledgeAdmissionBounds()
        if min(vars(self.bounds).values()) <= 0:
            raise Pass127Error("REJECT_UNBOUNDED_ADMISSION", "positive bounds required")
        self.interpretation = CanonicalDocumentInterpretationEngine()

    def attest(self, *, evidence_kind: str, subject_proposition: str, support: bool,
               source_root_hash72: str, independence_key: str, source_quality: str = "MEDIUM",
               observed_at: str = "1970-01-01T00:00:00+00:00", valid_from: str | None = None,
               valid_until: str | None = None, claim_root_hash72: str | None = None,
               formal_proof_root_hash72: str | None = None, runtime_receipt_root_hash72: str | None = None) -> dict[str, Any]:
        if evidence_kind not in self.EVIDENCE_KINDS or source_quality not in self.SOURCE_QUALITY:
            raise Pass127Error("REJECT_INVALID_EVIDENCE", evidence_kind)
        if not source_root_hash72 or not independence_key or len(subject_proposition) > self.bounds.max_proposition_chars:
            raise Pass127Error("REJECT_INVALID_EVIDENCE", "missing identity or oversized proposition")
        try:
            datetime.fromisoformat(observed_at)
            if valid_from: datetime.fromisoformat(valid_from)
            if valid_until: datetime.fromisoformat(valid_until)
        except ValueError as exc:
            raise Pass127Error("REJECT_INVALID_EVIDENCE", "invalid time") from exc
        obj = {
            "schema": EVIDENCE_SCHEMA, "pass_id": PASS_ID,
            "normalized_proposition": self.interpretation._normalized_proposition(subject_proposition),
            "evidence_kind": evidence_kind, "support": bool(support),
            "source_root_hash72": source_root_hash72, "independence_key": independence_key,
            "source_quality": source_quality, "observed_at": observed_at,
            "valid_from": valid_from, "valid_until": valid_until,
            "claim_root_hash72": claim_root_hash72,
            "formal_proof_root_hash72": formal_proof_root_hash72,
            "runtime_receipt_root_hash72": runtime_receipt_root_hash72,
            "execution_authority": False, "mutation_authority": False,
        }
        obj["evidence_root_hash72"] = _hash("hhs_pass127_evidence_v1", obj)
        return obj

    def verify_evidence(self, evidence: Mapping[str, Any]) -> dict[str, Any]:
        obj = dict(evidence); claimed = obj.pop("evidence_root_hash72", None)
        if obj.get("evidence_kind") not in self.EVIDENCE_KINDS or obj.get("source_quality") not in self.SOURCE_QUALITY:
            raise Pass127Error("REJECT_INVALID_EVIDENCE", str(obj.get("evidence_kind")))
        if claimed != _hash("hhs_pass127_evidence_v1", obj):
            raise Pass127Error("REJECT_EVIDENCE_ROOT_MISMATCH", str(claimed))
        obj["evidence_root_hash72"] = claimed
        return obj

    def make_policy(self, *, min_independent_support: int = 2, minimum_source_quality: str = "MEDIUM",
                    require_formal_proof: bool = False, require_runtime_receipt: bool = False,
                    reject_any_contradiction: bool = True, max_evidence_age_seconds: int | None = None) -> dict[str, Any]:
        if min_independent_support <= 0 or min_independent_support > self.bounds.max_independence_groups:
            raise Pass127Error("REJECT_UNBOUNDED_ADMISSION", "independent support")
        if minimum_source_quality not in self.SOURCE_QUALITY:
            raise Pass127Error("REJECT_SOURCE_QUALITY", minimum_source_quality)
        age = self.bounds.max_age_seconds if max_evidence_age_seconds is None else max_evidence_age_seconds
        if age <= 0 or age > self.bounds.max_age_seconds:
            raise Pass127Error("REJECT_UNBOUNDED_ADMISSION", "evidence age")
        obj = {"schema": POLICY_SCHEMA, "pass_id": PASS_ID,
               "min_independent_support": min_independent_support,
               "minimum_source_quality": minimum_source_quality,
               "require_formal_proof": require_formal_proof,
               "require_runtime_receipt": require_runtime_receipt,
               "reject_any_contradiction": reject_any_contradiction,
               "max_evidence_age_seconds": age}
        obj["policy_root_hash72"] = _hash("hhs_pass127_policy_v1", obj)
        return obj

    def decide(self, candidate: Mapping[str, Any], evidence: Sequence[Mapping[str, Any]], policy: Mapping[str, Any], *, as_of: str = "2026-07-17T00:00:00+00:00") -> dict[str, Any]:
        if candidate.get("schema") != "HHS_DOCUMENT_KNOWLEDGE_CANDIDATE_V1" or candidate.get("admission_status") != "CANDIDATE_ONLY_REQUIRES_EXTERNAL_VALIDATION":
            raise Pass127Error("REJECT_INVALID_CANDIDATE", str(candidate.get("schema")))
        if candidate.get("knowledge_authority") is not False:
            raise Pass127Error("REJECT_AUTHORITY_ESCALATION", "candidate")
        if len(evidence) == 0 or len(evidence) > self.bounds.max_evidence:
            raise Pass127Error("REJECT_UNBOUNDED_ADMISSION", "evidence count")
        pobj = dict(policy); proot = pobj.pop("policy_root_hash72", None)
        if proot != _hash("hhs_pass127_policy_v1", pobj):
            raise Pass127Error("REJECT_POLICY_ROOT_MISMATCH", str(proot))
        target = candidate["normalized_proposition"]
        now = datetime.fromisoformat(as_of)
        verified = [self.verify_evidence(e) for e in evidence]
        relevant = [e for e in verified if e["normalized_proposition"] == target]
        if not relevant:
            raise Pass127Error("REJECT_INVALID_EVIDENCE", "no proposition match")
        min_quality = self.SOURCE_QUALITY[policy["minimum_source_quality"]]
        usable = []
        for e in relevant:
            if self.SOURCE_QUALITY[e["source_quality"]] < min_quality:
                continue
            observed = datetime.fromisoformat(e["observed_at"])
            if abs((now-observed).total_seconds()) > policy["max_evidence_age_seconds"]:
                raise Pass127Error("REJECT_STALE_EVIDENCE", e["evidence_root_hash72"])
            if e["valid_from"] and now < datetime.fromisoformat(e["valid_from"]):
                raise Pass127Error("REJECT_TEMPORAL_SCOPE_CONFLICT", e["evidence_root_hash72"])
            if e["valid_until"] and now > datetime.fromisoformat(e["valid_until"]):
                raise Pass127Error("REJECT_TEMPORAL_SCOPE_CONFLICT", e["evidence_root_hash72"])
            usable.append(e)
        if not usable:
            raise Pass127Error("REJECT_SOURCE_QUALITY", target)
        contradictions = [e for e in usable if not e["support"]]
        if contradictions and policy["reject_any_contradiction"]:
            raise Pass127Error("REJECT_UNRESOLVED_CONTRADICTION", target)
        supports = [e for e in usable if e["support"]]
        independent = sorted({e["independence_key"] for e in supports})
        if len(independent) < policy["min_independent_support"]:
            raise Pass127Error("REJECT_INSUFFICIENT_INDEPENDENT_SUPPORT", target)
        if policy["require_formal_proof"] and not any(e["formal_proof_root_hash72"] for e in supports):
            raise Pass127Error("REJECT_FORMAL_VERIFICATION_REQUIRED", target)
        if policy["require_runtime_receipt"] and not any(e["runtime_receipt_root_hash72"] for e in supports):
            raise Pass127Error("REJECT_RUNTIME_VERIFICATION_REQUIRED", target)
        decision = {"schema": DECISION_SCHEMA, "pass_id": PASS_ID,
                    "candidate_root_hash72": candidate["candidate_root_hash72"],
                    "normalized_proposition": target,
                    "policy_root_hash72": policy["policy_root_hash72"],
                    "support_evidence_roots": sorted(e["evidence_root_hash72"] for e in supports),
                    "contradiction_evidence_roots": sorted(e["evidence_root_hash72"] for e in contradictions),
                    "independence_keys": independent,
                    "as_of": as_of, "decision": "ADMIT_KNOWLEDGE",
                    "execution_authority": False, "mutation_authority": False}
        decision["decision_root_hash72"] = _hash("hhs_pass127_decision_v1", decision)
        return decision

    def admit(self, decision: Mapping[str, Any]) -> dict[str, Any]:
        obj = dict(decision); root = obj.pop("decision_root_hash72", None)
        if root != _hash("hhs_pass127_decision_v1", obj) or obj.get("decision") != "ADMIT_KNOWLEDGE":
            raise Pass127Error("REJECT_DECISION_ROOT_MISMATCH", str(root))
        record = {"schema": RECORD_SCHEMA, "pass_id": PASS_ID,
                  "normalized_proposition": obj["normalized_proposition"],
                  "candidate_root_hash72": obj["candidate_root_hash72"],
                  "decision_root_hash72": root,
                  "support_evidence_roots": obj["support_evidence_roots"],
                  "knowledge_status": "ADMITTED_EVIDENCE_GROUNDED_KNOWLEDGE",
                  "knowledge_authority": True,
                  "execution_authority": False, "mutation_authority": False,
                  "executable": False}
        record["knowledge_record_root_hash72"] = _hash("hhs_pass127_record_v1", record)
        return record

    def build_corpus(self, records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        if not records or len(records) > self.bounds.max_records:
            raise Pass127Error("REJECT_UNBOUNDED_ADMISSION", "record count")
        roots=[]
        for record in records:
            obj=dict(record); root=obj.pop("knowledge_record_root_hash72",None)
            if root != _hash("hhs_pass127_record_v1",obj):
                raise Pass127Error("REJECT_RECORD_ROOT_MISMATCH",str(root))
            roots.append(root)
        corpus={"schema":CORPUS_SCHEMA,"pass_id":PASS_ID,"record_roots":roots,"record_count":len(roots),
                "execution_authority":False,"mutation_authority":False}
        corpus["corpus_root_hash72"]=_hash("hhs_pass127_corpus_v1",corpus)
        return corpus

    def assert_no_execution_escalation(self, *objects: Mapping[str, Any]) -> None:
        for obj in objects:
            if obj.get("execution_authority") is not False or obj.get("mutation_authority") is not False:
                raise Pass127Error("REJECT_AUTHORITY_ESCALATION", obj.get("schema","object"))
            if obj.get("executable", False):
                raise Pass127Error("REJECT_EXECUTABLE_KNOWLEDGE_ESCALATION", obj.get("schema","object"))

    def replay(self, candidate: Mapping[str, Any], evidence: Sequence[Mapping[str, Any]], policy: Mapping[str, Any], decision: Mapping[str, Any], *, as_of: str) -> dict[str, Any]:
        rebuilt=self.decide(candidate,evidence,policy,as_of=as_of)
        if _canon(rebuilt)!=_canon(decision):
            raise Pass127Error("REJECT_REPLAY_MISMATCH","decision")
        receipt={"schema":REPLAY_SCHEMA,"pass_id":PASS_ID,"decision_root_hash72":rebuilt["decision_root_hash72"],
                 "candidate_root_hash72":candidate["candidate_root_hash72"],"status":"KNOWLEDGE_ADMISSION_REPLAY_VALIDATED"}
        receipt["replay_root_hash72"]=_hash("hhs_pass127_replay_v1",receipt)
        return receipt

def pass127_self_test() -> dict[str, Any]:
    from hhs_runtime.hhs_pass125_canonical_document_ingestion_v1 import CanonicalDocumentIngestionEngine
    ing=CanonicalDocumentIngestionEngine(); src=ing.ingest_bytes(b"Mass is conserved.",source_kind="SELF_TEST",source_id="pass127:self",mime_type="text/plain")
    segs=ing.segment(src); ie=CanonicalDocumentInterpretationEngine(); claim=ie.extract_claims(src,segs)[0]
    cand=ie.build_candidate(claim["verbatim_text"],[claim])
    e=EvidenceGroundedKnowledgeAdmissionEngine()
    ev1=e.attest(evidence_kind="DOCUMENT_CLAIM",subject_proposition=claim["verbatim_text"],support=True,source_root_hash72=src["source_root_hash72"],independence_key="source:A",source_quality="HIGH",observed_at="2026-07-17T00:00:00+00:00",claim_root_hash72=claim["claim_root_hash72"])
    ev2=e.attest(evidence_kind="FORMAL_PROOF",subject_proposition=claim["verbatim_text"],support=True,source_root_hash72="proof:root",independence_key="proof:A",source_quality="AUTHORITATIVE",observed_at="2026-07-17T00:00:00+00:00",formal_proof_root_hash72="proof:receipt")
    policy=e.make_policy(require_formal_proof=True); decision=e.decide(cand,[ev1,ev2],policy,as_of="2026-07-17T00:00:00+00:00")
    record=e.admit(decision); corpus=e.build_corpus([record]); e.assert_no_execution_escalation(record,corpus)
    replay=e.replay(cand,[ev1,ev2],policy,decision,as_of="2026-07-17T00:00:00+00:00")
    return {"schema":"HHS_PASS127_SELF_TEST_V1","status":"PASS","record_root_hash72":record["knowledge_record_root_hash72"],"replay_root_hash72":replay["replay_root_hash72"]}
