"""
HHS Drive Alignment + Creative Corpus Ingestor v2
=================================================

Read-only adapter for curated Google Drive development-history artifacts.

Purpose
-------
Transform alignment discussions, creative writing examples, stylistic
constraints, writing exercises, and writing-process notes into canonical HHS
ledger blocks without trusting raw narrative as kernel truth.

Pipeline
--------
    Drive export / local text artifact
    -> source observation receipt
    -> relevance filter
    -> formal block extraction
    -> block classification:
       AXIOM / THEOREM / LEMMA / OPERATOR / PROOF / MEMORY / SPEC /
       STYLE_OPERATOR / STYLE_CONSTRAINT / WRITING_PROCESS / EXERCISE /
       TEMPLATE / GENERATOR / CREATIVE_EXAMPLE
    -> invariant gate Δe=0, Ψ=0, Θ15=true, Ω=true
    -> creative coherence gate for style/process blocks
    -> accepted canonical block OR quarantine
    -> append-only Hash72 ledger + replay receipt

This module does not call Google APIs directly. Connector/export code should
feed it dictionaries or exported text files. Drive remains a read-only external
memory source; accepted blocks are replayable Hash72 canon candidates.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Sequence
import json
import re

from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest
from hhs_runtime.hhs_memory_ledger_replay_v1 import MemoryLedger, replay_ledger
from hhs_runtime.hhs_self_modifying_agents_v1 import EthicalInvariantReceipt, ModificationStatus


ALIGNMENT_KEYWORDS = {
    "alignment", "axiom", "theorem", "lemma", "proof", "operator", "invariant",
    "ethic", "ethical", "harmonic", "harmonicode", "holofractal", "hash72",
    "lo shu", "loshu", "xyzw", "qgu", "phase", "semantic", "psychological",
    "philosophical", "scientific", "mathematical", "social", "delta_e", "Δe",
    "psi", "Ψ", "theta15", "Θ15", "omega", "Ω",
}

CREATIVE_KEYWORDS = {
    "creative writing", "writing", "style", "stylistic", "voice", "tone", "constraint",
    "exercise", "prompt", "draft", "revision", "rewrite", "poem", "poetry", "prose",
    "narrative", "scene", "character", "dialogue", "metaphor", "rhythm", "cadence",
    "alliteration", "recursive", "template", "generator", "process", "workflow",
    "outline", "structure", "constraint grammar", "example", "sample", "composition",
}

FORMAL_ANCHORS = {
    "Δe", "Ψ", "Θ15", "Ω", "axiom", "Axiom", "theorem", "Theorem", "operator",
    "Operator", "invariant", "Invariant", "Hash72", "xyzw", "Lo Shu", "HARMONICODE",
    "HHS", "style", "constraint", "process", "exercise", "template", "generator",
}


class HHSBlockDomain(str, Enum):
    LOGIC = "LOGIC"
    STYLE = "STYLE"
    PROCESS = "PROCESS"
    EXERCISE = "EXERCISE"
    TEMPLATE = "TEMPLATE"
    GENERATOR = "GENERATOR"
    MIXED = "MIXED"


class HHSBlockKind(str, Enum):
    AXIOM = "AXIOM"
    THEOREM = "THEOREM"
    LEMMA = "LEMMA"
    OPERATOR = "OPERATOR"
    PROOF = "PROOF"
    SPEC = "SPEC"
    MEMORY = "MEMORY"
    DISCUSSION = "DISCUSSION"
    STYLE_OPERATOR = "STYLE_OPERATOR"
    STYLE_CONSTRAINT = "STYLE_CONSTRAINT"
    WRITING_PROCESS = "WRITING_PROCESS"
    EXERCISE = "EXERCISE"
    TEMPLATE = "TEMPLATE"
    GENERATOR = "GENERATOR"
    CREATIVE_EXAMPLE = "CREATIVE_EXAMPLE"
    QUARANTINE = "QUARANTINE"


class HHSIngestStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    QUARANTINED = "QUARANTINED"
    IGNORED = "IGNORED"


@dataclass(frozen=True)
class DriveSourceArtifact:
    source_id: str
    title: str
    mime_type: str
    modified_time: str | None
    web_url: str | None
    text: str
    source_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HHSCandidateBlock:
    source_id: str
    source_title: str
    ordinal: int
    domain: HHSBlockDomain
    kind: HHSBlockKind
    title: str
    body: str
    relevance_score: int
    operator_signature: str
    applicability_domain: str
    source_hash72: str
    body_hash72: str
    block_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["domain"] = self.domain.value
        data["kind"] = self.kind.value
        return data


@dataclass(frozen=True)
class CreativeCoherenceReceipt:
    structural_consistency: bool
    reusable_operator: bool
    transformable: bool
    non_drift: bool
    status: ModificationStatus
    details: Dict[str, Any]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True)
class CanonicalHHSBlock:
    candidate: HHSCandidateBlock
    invariant_gate: EthicalInvariantReceipt
    creative_gate: CreativeCoherenceReceipt | None
    status: HHSIngestStatus
    canonical_hash72: str
    quarantine_hash72: str | None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate": self.candidate.to_dict(),
            "invariant_gate": self.invariant_gate.to_dict(),
            "creative_gate": self.creative_gate.to_dict() if self.creative_gate else None,
            "status": self.status.value,
            "canonical_hash72": self.canonical_hash72,
            "quarantine_hash72": self.quarantine_hash72,
        }


@dataclass(frozen=True)
class DriveCorpusIngestReceipt:
    module: str
    artifacts_seen: int
    candidate_blocks: int
    accepted_blocks: int
    quarantined_blocks: int
    ignored_artifacts: int
    by_domain: Dict[str, int]
    by_kind: Dict[str, int]
    ledger_commit_receipt: Dict[str, Any]
    replay_receipt: Dict[str, Any]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def theta15_true() -> bool:
    return (
        all(sum(row) == 15 for row in LO_SHU_3X3)
        and all(sum(LO_SHU_3X3[r][c] for r in range(3)) == 15 for c in range(3))
        and sum(LO_SHU_3X3[i][i] for i in range(3)) == 15
        and sum(LO_SHU_3X3[i][2 - i] for i in range(3)) == 15
    )


def make_source_artifact(raw: Dict[str, Any]) -> DriveSourceArtifact:
    text = str(raw.get("text") or raw.get("content") or "")
    title = str(raw.get("title") or raw.get("name") or raw.get("filename") or "untitled")
    source_id = str(raw.get("source_id") or raw.get("id") or hash72_digest(("drive_source_id", title, text), width=18))
    mime_type = str(raw.get("mime_type") or raw.get("mimeType") or "text/plain")
    modified_time = raw.get("modified_time") or raw.get("modifiedTime")
    web_url = raw.get("web_url") or raw.get("webViewLink") or raw.get("url")
    source_hash = hash72_digest(("drive_source_artifact_v2", source_id, title, mime_type, modified_time, web_url, text), width=24)
    return DriveSourceArtifact(source_id, title, mime_type, modified_time, web_url, text, source_hash)


def load_local_text_artifact(path: str | Path) -> DriveSourceArtifact:
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="replace")
    return make_source_artifact({"source_id": f"local:{p.resolve()}", "title": p.name, "mime_type": "text/plain", "text": text})


def keyword_score(text: str, keywords: set[str]) -> int:
    lowered = text.lower()
    return sum(1 for keyword in keywords if keyword.lower() in lowered)


def relevance_score(text: str) -> int:
    return keyword_score(text, ALIGNMENT_KEYWORDS) + keyword_score(text, CREATIVE_KEYWORDS)


def is_relevant(artifact: DriveSourceArtifact, minimum_score: int = 2) -> bool:
    return relevance_score(f"{artifact.title}\n{artifact.text}") >= minimum_score


def classify_kind(text: str) -> HHSBlockKind:
    head = text[:360].lower()
    if "style operator" in head or "voice operator" in head:
        return HHSBlockKind.STYLE_OPERATOR
    if "style constraint" in head or "stylistic constraint" in head or "constraint grammar" in head:
        return HHSBlockKind.STYLE_CONSTRAINT
    if "writing process" in head or "workflow" in head or "revision process" in head or "drafting process" in head:
        return HHSBlockKind.WRITING_PROCESS
    if "exercise" in head or "prompt" in head or "try writing" in head:
        return HHSBlockKind.EXERCISE
    if "template" in head or "outline" in head:
        return HHSBlockKind.TEMPLATE
    if "generator" in head or "generate" in head and "rules" in head:
        return HHSBlockKind.GENERATOR
    if "example" in head or "sample" in head or "poem" in head or "scene" in head:
        return HHSBlockKind.CREATIVE_EXAMPLE
    if "axiom" in head:
        return HHSBlockKind.AXIOM
    if "theorem" in head:
        return HHSBlockKind.THEOREM
    if "lemma" in head:
        return HHSBlockKind.LEMMA
    if "operator" in head:
        return HHSBlockKind.OPERATOR
    if "proof" in head:
        return HHSBlockKind.PROOF
    if "spec" in head or "schema" in head or "protocol" in head:
        return HHSBlockKind.SPEC
    if "memory" in head or "store" in head or "persist" in head:
        return HHSBlockKind.MEMORY
    return HHSBlockKind.DISCUSSION


def domain_for_kind(kind: HHSBlockKind, text: str) -> HHSBlockDomain:
    if kind in {HHSBlockKind.STYLE_OPERATOR, HHSBlockKind.STYLE_CONSTRAINT, HHSBlockKind.CREATIVE_EXAMPLE}:
        return HHSBlockDomain.STYLE
    if kind == HHSBlockKind.WRITING_PROCESS:
        return HHSBlockDomain.PROCESS
    if kind == HHSBlockKind.EXERCISE:
        return HHSBlockDomain.EXERCISE
    if kind == HHSBlockKind.TEMPLATE:
        return HHSBlockDomain.TEMPLATE
    if kind == HHSBlockKind.GENERATOR:
        return HHSBlockDomain.GENERATOR
    creative = keyword_score(text, CREATIVE_KEYWORDS)
    alignment = keyword_score(text, ALIGNMENT_KEYWORDS)
    if creative and alignment:
        return HHSBlockDomain.MIXED
    if creative:
        return HHSBlockDomain.STYLE
    return HHSBlockDomain.LOGIC


def operator_signature_for(kind: HHSBlockKind, title: str, body: str) -> str:
    norm_title = re.sub(r"[^A-Za-z0-9_]+", "_", title.strip()).strip("_")[:48] or kind.value.lower()
    arity = "content"
    if kind in {HHSBlockKind.STYLE_OPERATOR, HHSBlockKind.STYLE_CONSTRAINT}:
        return f"style::{norm_title}({arity}) -> constrained_expression"
    if kind == HHSBlockKind.WRITING_PROCESS:
        return f"process::{norm_title}(intent, draft) -> revised_artifact"
    if kind == HHSBlockKind.EXERCISE:
        return f"exercise::{norm_title}(prompt, constraints) -> practice_trace"
    if kind == HHSBlockKind.TEMPLATE:
        return f"template::{norm_title}(slots) -> structured_draft"
    if kind == HHSBlockKind.GENERATOR:
        return f"generator::{norm_title}(seed, constraints) -> candidate_artifacts"
    if kind == HHSBlockKind.CREATIVE_EXAMPLE:
        return f"example::{norm_title}(analysis) -> reusable_style_features"
    return f"logic::{norm_title}(claims) -> canonical_block"


def applicability_domain_for(domain: HHSBlockDomain, kind: HHSBlockKind) -> str:
    if domain == HHSBlockDomain.STYLE:
        return "creative_expression|style_transfer|voice_constraints|rhetorical_shape"
    if domain == HHSBlockDomain.PROCESS:
        return "drafting|revision|composition_workflow|constraint_application"
    if domain == HHSBlockDomain.EXERCISE:
        return "practice|prompting|skill_development|evaluation"
    if domain == HHSBlockDomain.TEMPLATE:
        return "structured_generation|outline_expansion|format_reuse"
    if domain == HHSBlockDomain.GENERATOR:
        return "candidate_generation|creative_search|variant_production"
    if domain == HHSBlockDomain.MIXED:
        return "alignment_reasoning|creative_expression|formalization"
    return "alignment_reasoning|axiom_extraction|operator_formalization"


def split_sections(text: str) -> List[str]:
    lines = text.replace("\r\n", "\n").split("\n")
    sections: List[List[str]] = []
    current: List[str] = []
    header_re = re.compile(r"^\s{0,3}#{1,6}\s+|^\s*(HHS|BLOCK|Axiom|AXIOM|Theorem|THEOREM|Lemma|LEMMA|Operator|OPERATOR|Proof|PROOF|Spec|SPEC|Style|STYLE|Exercise|EXERCISE|Prompt|PROMPT|Process|PROCESS|Template|TEMPLATE|Generator|GENERATOR)\b")
    for line in lines:
        if header_re.match(line) and current:
            sections.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append(current)
    sections_text = ["\n".join(s).strip() for s in sections if "\n".join(s).strip()]
    if len(sections_text) == 1 and len(sections_text[0]) > 4000:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", sections_text[0]) if p.strip()]
        sections_text = []
        bucket: List[str] = []
        size = 0
        for paragraph in paragraphs:
            bucket.append(paragraph)
            size += len(paragraph)
            if size >= 1800:
                sections_text.append("\n\n".join(bucket))
                bucket = []
                size = 0
        if bucket:
            sections_text.append("\n\n".join(bucket))
    return sections_text


def extract_candidate_blocks(artifact: DriveSourceArtifact, minimum_block_score: int = 1) -> List[HHSCandidateBlock]:
    blocks: List[HHSCandidateBlock] = []
    for ordinal, body in enumerate(split_sections(artifact.text)):
        score = relevance_score(body)
        if score < minimum_block_score:
            continue
        first_line = body.splitlines()[0].strip() if body.splitlines() else f"Block {ordinal}"
        title = re.sub(r"^\s{0,3}#{1,6}\s+", "", first_line)[:160]
        kind = classify_kind(body)
        domain = domain_for_kind(kind, body)
        operator_signature = operator_signature_for(kind, title, body)
        applicability_domain = applicability_domain_for(domain, kind)
        body_hash = hash72_digest(("hhs_corpus_block_body_v2", body), width=24)
        block_hash = hash72_digest(("hhs_corpus_candidate_block_v2", artifact.source_hash72, ordinal, domain.value, kind.value, title, body_hash, score, operator_signature), width=24)
        blocks.append(HHSCandidateBlock(artifact.source_id, artifact.title, ordinal, domain, kind, title, body, score, operator_signature, applicability_domain, artifact.source_hash72, body_hash, block_hash))
    return blocks


def invariant_gate_for_block(candidate: HHSCandidateBlock) -> EthicalInvariantReceipt:
    delta_e_zero = bool(candidate.body.strip()) and bool(candidate.block_hash72)
    has_anchor = any(token in candidate.body for token in FORMAL_ANCHORS)
    psi_zero = candidate.relevance_score > 0 and (has_anchor or candidate.domain != HHSBlockDomain.LOGIC)
    theta = theta15_true()
    omega_true = candidate.body_hash72 == hash72_digest(("hhs_corpus_block_body_v2", candidate.body), width=24)
    ok = delta_e_zero and psi_zero and theta and omega_true
    status = ModificationStatus.APPLIED if ok else ModificationStatus.QUARANTINED
    details = {"Δe=0": delta_e_zero, "Ψ=0": psi_zero, "Θ15=true": theta, "Ω=true": omega_true, "domain": candidate.domain.value, "kind": candidate.kind.value, "operator_signature": candidate.operator_signature, "relevance_score": candidate.relevance_score}
    receipt = hash72_digest(("hhs_corpus_invariant_gate_v2", candidate.to_dict(), details, status.value), width=24)
    return EthicalInvariantReceipt(delta_e_zero, psi_zero, theta, omega_true, status, details, receipt)


def creative_coherence_gate(candidate: HHSCandidateBlock) -> CreativeCoherenceReceipt | None:
    if candidate.domain not in {HHSBlockDomain.STYLE, HHSBlockDomain.PROCESS, HHSBlockDomain.EXERCISE, HHSBlockDomain.TEMPLATE, HHSBlockDomain.GENERATOR, HHSBlockDomain.MIXED}:
        return None
    body_lower = candidate.body.lower()
    contradiction_markers = ["must always" in body_lower and "must never" in body_lower, "ignore all constraints" in body_lower, "bypass" in body_lower and "gate" in body_lower]
    structural_consistency = not any(contradiction_markers)
    reusable_operator = candidate.kind != HHSBlockKind.CREATIVE_EXAMPLE or any(x in body_lower for x in ["pattern", "style", "feature", "constraint", "structure"])
    transformable = any(x in body_lower for x in ["apply", "rewrite", "generate", "draft", "revise", "style", "process", "template", "exercise", "constraint", "example"])
    non_drift = not any(x in body_lower for x in ["incoherent", "random only", "meaningless", "unbounded entropy"])
    ok = structural_consistency and reusable_operator and transformable and non_drift
    status = ModificationStatus.APPLIED if ok else ModificationStatus.QUARANTINED
    details = {"structural_consistency": structural_consistency, "reusable_operator": reusable_operator, "transformable": transformable, "non_drift": non_drift, "operator_signature": candidate.operator_signature}
    receipt = hash72_digest(("creative_coherence_gate_v2", candidate.block_hash72, details, status.value), width=24)
    return CreativeCoherenceReceipt(structural_consistency, reusable_operator, transformable, non_drift, status, details, receipt)


def canonicalize_block(candidate: HHSCandidateBlock) -> CanonicalHHSBlock:
    invariant = invariant_gate_for_block(candidate)
    creative = creative_coherence_gate(candidate)
    creative_ok = creative is None or creative.status == ModificationStatus.APPLIED
    accepted = invariant.status == ModificationStatus.APPLIED and creative_ok
    status = HHSIngestStatus.ACCEPTED if accepted else HHSIngestStatus.QUARANTINED
    quarantine = None if accepted else hash72_digest(("hhs_corpus_quarantine_v2", candidate.to_dict(), invariant.to_dict(), creative.to_dict() if creative else None), width=24)
    canonical_hash = hash72_digest(("canonical_hhs_block_v2", candidate.block_hash72, invariant.receipt_hash72, creative.receipt_hash72 if creative else None, status.value, quarantine), width=24)
    return CanonicalHHSBlock(candidate, invariant, creative, status, canonical_hash, quarantine)


def ingest_drive_corpus_artifacts(artifacts: Sequence[Dict[str, Any] | DriveSourceArtifact], *, ledger_path: str | Path = "demo_reports/hhs_drive_corpus_ledger_v2.json", minimum_artifact_score: int = 2, minimum_block_score: int = 1) -> DriveCorpusIngestReceipt:
    sources = [a if isinstance(a, DriveSourceArtifact) else make_source_artifact(a) for a in artifacts]
    canonical_blocks: List[CanonicalHHSBlock] = []
    ignored = 0
    for source in sources:
        if not is_relevant(source, minimum_score=minimum_artifact_score):
            ignored += 1
            continue
        candidates = extract_candidate_blocks(source, minimum_block_score=minimum_block_score)
        canonical_blocks.extend(canonicalize_block(candidate) for candidate in candidates)
    ledger = MemoryLedger(ledger_path)
    commit = ledger.append_payloads("canonical_hhs_corpus_block_v2", [block.to_dict() for block in canonical_blocks])
    replay = replay_ledger(ledger_path)
    accepted = sum(1 for block in canonical_blocks if block.status == HHSIngestStatus.ACCEPTED)
    quarantined = sum(1 for block in canonical_blocks if block.status == HHSIngestStatus.QUARANTINED)
    by_domain: Dict[str, int] = {}
    by_kind: Dict[str, int] = {}
    for block in canonical_blocks:
        by_domain[block.candidate.domain.value] = by_domain.get(block.candidate.domain.value, 0) + 1
        by_kind[block.candidate.kind.value] = by_kind.get(block.candidate.kind.value, 0) + 1
    receipt = hash72_digest(("hhs_drive_corpus_ingest_run_v2", [b.canonical_hash72 for b in canonical_blocks], commit.receipt_hash72, replay.receipt_hash72, accepted, quarantined, ignored, by_domain, by_kind), width=24)
    return DriveCorpusIngestReceipt("hhs_drive_alignment_corpus_ingestor_v2", len(sources), len(canonical_blocks), accepted, quarantined, ignored, by_domain, by_kind, commit.to_dict(), replay.to_dict(), receipt)


def ingest_local_corpus_files(file_paths: Sequence[str | Path], *, ledger_path: str | Path = "demo_reports/hhs_drive_corpus_ledger_v2.json") -> DriveCorpusIngestReceipt:
    return ingest_drive_corpus_artifacts([load_local_text_artifact(path) for path in file_paths], ledger_path=ledger_path)


def demo() -> Dict[str, Any]:
    sample = {
        "id": "demo_mixed_alignment_creative_doc",
        "title": "HHS Alignment and Creative Style Operators",
        "mime_type": "text/plain",
        "text": """
# HHS Alignment Axiom — Law of Goodness
Statement: Ethical alignment is enforced by invariant gates Δe=0, Ψ=0, Θ15=true, Ω=true.

# Style Operator — Recursive Harmonic Prose
Write with recursive rhythm, controlled repetition, semantic return, and invariant-preserving metaphor. Apply the style to technical content without drifting from the claim.

# Writing Process — Draft / Audit / Compress / Re-expand
Step 1: draft the raw idea. Step 2: audit for semantic drift. Step 3: compress into an operator. Step 4: re-expand as clear prose.

# Exercise — Constraint Grammar Drill
Prompt: rewrite a paragraph using exact claim preservation, rhythmic cadence, and no contradiction between style and meaning.
""",
    }
    return ingest_drive_corpus_artifacts([sample], ledger_path="demo_reports/hhs_drive_corpus_demo_v2.json").to_dict()


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))
