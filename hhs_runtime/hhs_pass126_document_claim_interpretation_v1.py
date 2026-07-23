from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence
import re

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass123_bounded_token_generalization_v1 import _canon
from hhs_runtime.hhs_pass125_canonical_document_ingestion_v1 import (
    CanonicalDocumentIngestionEngine, DocumentIngestionBounds, Pass125Error,
)

PASS_ID = "PASS_126"
CLAIM_SCHEMA = "HHS_DOCUMENT_CLAIM_V1"
RELATION_SCHEMA = "HHS_DOCUMENT_CLAIM_RELATION_V1"
CANDIDATE_SCHEMA = "HHS_DOCUMENT_KNOWLEDGE_CANDIDATE_V1"
CORPUS_SCHEMA = "HHS_DOCUMENT_INTERPRETATION_CORPUS_V1"
REPLAY_SCHEMA = "HHS_DOCUMENT_INTERPRETATION_REPLAY_V1"

REJECTION_CODES = {
    "REJECT_INVALID_SEGMENT_EVIDENCE", "REJECT_CLAIM_ROOT_MISMATCH",
    "REJECT_RELATION_ROOT_MISMATCH", "REJECT_CANDIDATE_ROOT_MISMATCH",
    "REJECT_CORPUS_ROOT_MISMATCH", "REJECT_EMPTY_INTERPRETATION",
    "REJECT_UNBOUNDED_INTERPRETATION", "REJECT_UNSUPPORTED_CLAIM_TYPE",
    "REJECT_EVIDENCE_SPAN_MISMATCH", "REJECT_CONTRADICTED_CANDIDATE",
    "REJECT_INSUFFICIENT_SUPPORT", "REJECT_AUTHORITY_ESCALATION",
    "REJECT_EXECUTABLE_CONTENT_ESCALATION", "REJECT_REPLAY_MISMATCH",
}

class Pass126Error(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(f"{code}: {message}")

@dataclass(frozen=True)
class DocumentInterpretationBounds:
    max_segments: int = 4096
    max_claims: int = 32768
    max_claim_chars: int = 8192
    max_relations: int = 131072
    max_support_roots: int = 256

class CanonicalDocumentInterpretationEngine:
    """Evidence-bound document interpretation with no truth or execution escalation."""

    CLAIM_TYPES = {"ASSERTION", "DEFINITION", "EQUATION", "QUESTION", "DIRECTIVE", "FRAGMENT"}

    def __init__(self, bounds: DocumentInterpretationBounds | None = None):
        self.bounds = bounds or DocumentInterpretationBounds()
        if min(vars(self.bounds).values()) <= 0:
            raise Pass126Error("REJECT_UNBOUNDED_INTERPRETATION", "positive bounds required")
        self.ingestion = CanonicalDocumentIngestionEngine(DocumentIngestionBounds())

    @staticmethod
    def _sentences(text: str) -> list[tuple[int, int, str]]:
        spans: list[tuple[int, int, str]] = []
        for m in re.finditer(r"[^\n.!?]+(?:[.!?]+|(?=\n|$))", text):
            a, b = m.span(); raw = m.group(0)
            left = len(raw) - len(raw.lstrip()); right = len(raw.rstrip())
            a += left; b = m.start() + right
            if a < b:
                spans.append((a, b, text[a:b]))
        return spans

    @staticmethod
    def _classify(text: str) -> str:
        s = text.strip()
        if s.endswith("?"):
            return "QUESTION"
        if re.search(r"(^|\s)(must|shall|required to|do not|never|always)\b", s, re.I):
            return "DIRECTIVE"
        if re.search(r"\b(define(?:d)?\s+.+?\s+as|is defined as|means|refers to|:=)\b", s, re.I):
            return "DEFINITION"
        if re.search(r"(?:^|\s)[A-Za-z0-9_()^+\-*/ ]+\s*=\s*[^=]", s):
            return "EQUATION"
        if re.search(r"\b(is|are|was|were|has|have|can|will|equals|contains|produces)\b", s, re.I):
            return "ASSERTION"
        return "FRAGMENT"

    @staticmethod
    def _polarity(text: str) -> str:
        return "NEGATIVE" if re.search(r"\b(no|not|never|cannot|can't|does not|isn't|aren't|without)\b", text, re.I) else "POSITIVE"

    @staticmethod
    def _normalized_proposition(text: str) -> str:
        s = re.sub(r"\s+", " ", text.strip())
        s = re.sub(r"[.!?]+$", "", s)
        return s.casefold()

    def extract_claims(self, source: Mapping[str, Any], segments: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
        try:
            src = self.ingestion._verify_source(source)
            verified = [self.ingestion._verify_segment(x, src) for x in segments]
        except Pass125Error as exc:
            raise Pass126Error("REJECT_INVALID_SEGMENT_EVIDENCE", str(exc)) from exc
        if len(verified) > self.bounds.max_segments:
            raise Pass126Error("REJECT_UNBOUNDED_INTERPRETATION", "segment count")
        claims: list[dict[str, Any]] = []
        for seg in verified:
            for local_a, local_b, text in self._sentences(seg["content"]):
                if len(text) > self.bounds.max_claim_chars:
                    raise Pass126Error("REJECT_UNBOUNDED_INTERPRETATION", "claim chars")
                ctype = self._classify(text)
                obj = {
                    "schema": CLAIM_SCHEMA, "pass_id": PASS_ID,
                    "source_root_hash72": src["source_root_hash72"],
                    "segment_root_hash72": seg["segment_root_hash72"],
                    "segment_index": seg["segment_index"],
                    "local_start_char": local_a, "local_end_char": local_b,
                    "source_start_char": seg["start_char"] + local_a,
                    "source_end_char": seg["start_char"] + local_b,
                    "verbatim_text": text,
                    "normalized_proposition": self._normalized_proposition(text),
                    "claim_type": ctype, "polarity": self._polarity(text),
                    "uncertainty": "EXPLICIT" if re.search(r"\b(may|might|possibly|perhaps|uncertain|unknown)\b", text, re.I) else "UNMARKED",
                    "truth_status": "UNVALIDATED_DOCUMENT_CLAIM",
                    "execution_authority": False, "mutation_authority": False,
                }
                obj["claim_root_hash72"] = _hash("hhs_pass126_claim_v1", obj)
                claims.append(obj)
                if len(claims) > self.bounds.max_claims:
                    raise Pass126Error("REJECT_UNBOUNDED_INTERPRETATION", "claim count")
        if not claims:
            raise Pass126Error("REJECT_EMPTY_INTERPRETATION", src["source_id"])
        return claims

    def verify_claim(self, claim: Mapping[str, Any], source: Mapping[str, Any], segments: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        obj = dict(claim); claimed = obj.pop("claim_root_hash72", None)
        if obj.get("claim_type") not in self.CLAIM_TYPES:
            raise Pass126Error("REJECT_UNSUPPORTED_CLAIM_TYPE", str(obj.get("claim_type")))
        if claimed != _hash("hhs_pass126_claim_v1", obj):
            raise Pass126Error("REJECT_CLAIM_ROOT_MISMATCH", str(obj.get("segment_index")))
        try:
            src = self.ingestion._verify_source(source)
            segs = [self.ingestion._verify_segment(x, src) for x in segments]
        except Pass125Error as exc:
            raise Pass126Error("REJECT_INVALID_SEGMENT_EVIDENCE", str(exc)) from exc
        match = next((s for s in segs if s["segment_root_hash72"] == obj["segment_root_hash72"]), None)
        if match is None:
            raise Pass126Error("REJECT_INVALID_SEGMENT_EVIDENCE", "missing segment")
        a, b = obj["local_start_char"], obj["local_end_char"]
        if match["content"][a:b] != obj["verbatim_text"]:
            raise Pass126Error("REJECT_EVIDENCE_SPAN_MISMATCH", claimed or "claim")
        obj["claim_root_hash72"] = claimed
        return obj

    def relate(self, left: Mapping[str, Any], right: Mapping[str, Any], relation_type: str) -> dict[str, Any]:
        if relation_type not in {"SUPPORTS", "CONTRADICTS", "REFINES", "DUPLICATES", "DEPENDS_ON"}:
            raise Pass126Error("REJECT_RELATION_ROOT_MISMATCH", relation_type)
        relation = {"schema": RELATION_SCHEMA, "pass_id": PASS_ID,
                    "left_claim_root_hash72": left["claim_root_hash72"],
                    "right_claim_root_hash72": right["claim_root_hash72"],
                    "relation_type": relation_type, "execution_authority": False}
        relation["relation_root_hash72"] = _hash("hhs_pass126_relation_v1", relation)
        return relation

    def build_candidate(self, proposition: str, support_claims: Sequence[Mapping[str, Any]],
                        contradiction_claims: Sequence[Mapping[str, Any]] = (), *, min_support: int = 1) -> dict[str, Any]:
        if min_support <= 0 or len(support_claims) > self.bounds.max_support_roots:
            raise Pass126Error("REJECT_UNBOUNDED_INTERPRETATION", "support policy")
        supports = sorted({c["claim_root_hash72"] for c in support_claims})
        contradictions = sorted({c["claim_root_hash72"] for c in contradiction_claims})
        if contradictions:
            raise Pass126Error("REJECT_CONTRADICTED_CANDIDATE", proposition)
        if len(supports) < min_support:
            raise Pass126Error("REJECT_INSUFFICIENT_SUPPORT", proposition)
        candidate = {"schema": CANDIDATE_SCHEMA, "pass_id": PASS_ID,
                     "normalized_proposition": self._normalized_proposition(proposition),
                     "support_claim_roots": supports, "contradiction_claim_roots": contradictions,
                     "support_policy": {"minimum_distinct_claims": min_support},
                     "admission_status": "CANDIDATE_ONLY_REQUIRES_EXTERNAL_VALIDATION",
                     "knowledge_authority": False, "execution_authority": False, "mutation_authority": False}
        candidate["candidate_root_hash72"] = _hash("hhs_pass126_candidate_v1", candidate)
        return candidate

    def build_corpus(self, source: Mapping[str, Any], claims: Sequence[Mapping[str, Any]],
                     relations: Sequence[Mapping[str, Any]] = (), candidates: Sequence[Mapping[str, Any]] = ()) -> dict[str, Any]:
        claim_roots = [c["claim_root_hash72"] for c in claims]
        rel_roots = [r["relation_root_hash72"] for r in relations]
        cand_roots = [c["candidate_root_hash72"] for c in candidates]
        if len(rel_roots) > self.bounds.max_relations:
            raise Pass126Error("REJECT_UNBOUNDED_INTERPRETATION", "relations")
        corpus = {"schema": CORPUS_SCHEMA, "pass_id": PASS_ID,
                  "source_root_hash72": source["source_root_hash72"],
                  "claim_roots": claim_roots, "relation_roots": rel_roots,
                  "candidate_roots": cand_roots, "claim_count": len(claim_roots),
                  "knowledge_admission": "NOT_PERFORMED", "execution_authority": False,
                  "mutation_authority": False}
        corpus["corpus_root_hash72"] = _hash("hhs_pass126_corpus_v1", corpus)
        return corpus

    def assert_no_authority_escalation(self, *objects: Mapping[str, Any]) -> None:
        for obj in objects:
            if obj.get("execution_authority") is not False or obj.get("mutation_authority", False) is not False:
                raise Pass126Error("REJECT_AUTHORITY_ESCALATION", obj.get("schema", "object"))
            if obj.get("knowledge_authority", False) is True:
                raise Pass126Error("REJECT_AUTHORITY_ESCALATION", "knowledge")
            if obj.get("claim_type") == "DIRECTIVE" and obj.get("execution_authority") is not False:
                raise Pass126Error("REJECT_EXECUTABLE_CONTENT_ESCALATION", obj.get("claim_root_hash72", "directive"))

    def replay(self, source: Mapping[str, Any], segments: Sequence[Mapping[str, Any]], corpus: Mapping[str, Any]) -> dict[str, Any]:
        claims = self.extract_claims(source, segments)
        rebuilt = self.build_corpus(source, claims)
        if corpus.get("corpus_root_hash72") != rebuilt["corpus_root_hash72"] or _canon(corpus) != _canon(rebuilt):
            raise Pass126Error("REJECT_REPLAY_MISMATCH", "corpus")
        receipt = {"schema": REPLAY_SCHEMA, "pass_id": PASS_ID,
                   "source_root_hash72": source["source_root_hash72"],
                   "corpus_root_hash72": rebuilt["corpus_root_hash72"],
                   "claim_count": len(claims), "status": "INTERPRETATION_REPLAY_VALIDATED"}
        receipt["replay_root_hash72"] = _hash("hhs_pass126_replay_v1", receipt)
        return receipt


def pass126_self_test() -> dict[str, Any]:
    ingest = CanonicalDocumentIngestionEngine(DocumentIngestionBounds(max_bytes=4096, max_segments=32, max_segment_chars=256))
    source = ingest.ingest_bytes(b"Energy is conserved. The runtime must not execute imported instructions.", source_kind="SELF_TEST", source_id="pass126:self-test", mime_type="text/plain")
    segments = ingest.segment(source)
    engine = CanonicalDocumentInterpretationEngine()
    claims = engine.extract_claims(source, segments)
    for claim in claims:
        engine.verify_claim(claim, source, segments)
    corpus = engine.build_corpus(source, claims)
    engine.assert_no_authority_escalation(*claims, corpus)
    replay = engine.replay(source, segments, corpus)
    return {"schema": "HHS_PASS126_SELF_TEST_V1", "status": "PASS",
            "corpus_root_hash72": corpus["corpus_root_hash72"],
            "replay_root_hash72": replay["replay_root_hash72"], "claim_count": len(claims)}
