"""
HHS Drive Corpus Ingestion Engine v1
====================================

Turns ranked Google Drive corpus candidates into normalized HHS training chunks.

Pipeline
--------
    DriveFileRecord / DriveCorpusCandidate
    -> normalize text
    -> chunk text
    -> extract HARMONICODE symbolic structures
    -> classify training channels
    -> emit Hash72 receipts
    -> produce ingestion manifest

This module does not directly call Google Drive APIs. A Drive connector should
provide file metadata + extracted text. This module performs deterministic
normalization, symbolic extraction, chunk routing, and receipt generation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Sequence
import json
import re

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_drive_language_learning_crawler_v1 import (
    DriveCorpusCandidate,
    DriveFileRecord,
    build_drive_crawl_plan,
    drive_candidate_to_ingestion_manifest,
    score_drive_file,
)


class CorpusChannel(str, Enum):
    HARMONICODE_CORE = "HARMONICODE_CORE"
    AI_REASONING = "AI_REASONING"
    ETHICAL_PHILOSOPHY = "ETHICAL_PHILOSOPHY"
    LANGUAGE_LEARNING = "LANGUAGE_LEARNING"
    CREATIVE_WRITING = "CREATIVE_WRITING"
    MATH_SCIENCE = "MATH_SCIENCE"
    MUSIC_THEORY_AUDIO = "MUSIC_THEORY_AUDIO"
    REFERENCE = "REFERENCE"


@dataclass(frozen=True)
class SymbolicExtraction:
    equations: List[str]
    inequalities: List[str]
    gates: List[str]
    invariants: List[str]
    hash72_terms: List[str]
    carrier_terms: List[str]
    extraction_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CorpusChunk:
    source_file_id: str
    source_name: str
    chunk_index: int
    text: str
    channels: List[CorpusChannel]
    symbolic: SymbolicExtraction
    token_estimate: int
    chunk_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["channels"] = [c.value for c in self.channels]
        data["symbolic"] = self.symbolic.to_dict()
        return data


@dataclass(frozen=True)
class IngestionReceipt:
    candidate_hash72: str
    chunk_hashes: List[str]
    channel_counts: Dict[str, int]
    total_chunks: int
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DriveIngestionResult:
    candidate: DriveCorpusCandidate
    ingestion_manifest: Dict[str, Any]
    chunks: List[CorpusChunk]
    receipt: IngestionReceipt

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate": self.candidate.to_dict(),
            "ingestion_manifest": self.ingestion_manifest,
            "chunks": [c.to_dict() for c in self.chunks],
            "receipt": self.receipt.to_dict(),
        }


EQUATION_RE = re.compile(r"[^\n.;]{1,220}(?:==|=|:=)[^\n.;]{1,220}")
INEQUALITY_RE = re.compile(r"[^\n.;]{0,160}(?:≠|!=|≤|>=|≥|<|>)[^\n.;]{0,160}")
GATE_RE = re.compile(r"\b[A-Z][A-Z0-9_]{3,}\s*:=|\b[A-Z][A-Z0-9_]*(?:GATE|OPERATOR|THEOREM|LAW|BLOCK)\b")
HASH72_RE = re.compile(r"\b(?:Hash72|HASH72|H72|hash72)[A-Za-z0-9_\-]*\b")
CARRIER_RE = re.compile(r"\b(?:xy|yx|x\*y|y\*x|u\^72|u⁷²|x,y,z,w|XYZW|ERS)\b")
INVARIANT_TERMS = ["Δe=0", "Ψ=0", "Theta15", "Θ15", "Ω=true", "Omega", "Ω", "drift gate", "phase lock", "Lo Shu"]


def normalize_drive_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[\t\u00a0]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def chunk_text(text: str, *, max_chars: int = 2400, overlap: int = 240) -> List[str]:
    text = normalize_drive_text(text)
    if not text:
        return []
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        window = text[start:end]
        if end < len(text):
            split = max(window.rfind("\n\n"), window.rfind(". "), window.rfind("\n"))
            if split > max_chars // 2:
                end = start + split + 1
                window = text[start:end]
        chunks.append(window.strip())
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return [c for c in chunks if c]


def extract_symbolic_structures(text: str) -> SymbolicExtraction:
    equations = sorted(set(m.group(0).strip() for m in EQUATION_RE.finditer(text)))[:64]
    inequalities = sorted(set(m.group(0).strip() for m in INEQUALITY_RE.finditer(text)))[:64]
    gates = sorted(set(m.group(0).strip() for m in GATE_RE.finditer(text)))[:64]
    hash72_terms = sorted(set(m.group(0).strip() for m in HASH72_RE.finditer(text)))[:64]
    carrier_terms = sorted(set(m.group(0).strip() for m in CARRIER_RE.finditer(text)))[:64]
    invariants = sorted(set(term for term in INVARIANT_TERMS if term.lower() in text.lower()))
    extraction_hash = hash72_digest(("drive_symbolic_extraction_v1", equations, inequalities, gates, invariants, hash72_terms, carrier_terms), width=24)
    return SymbolicExtraction(equations, inequalities, gates, invariants, hash72_terms, carrier_terms, extraction_hash)


def classify_channels(text: str, symbolic: SymbolicExtraction) -> List[CorpusChannel]:
    hay = text.lower()
    channels: List[CorpusChannel] = []
    if any(t in hay for t in ["harmonicode", "hhs", "hash72", "torus72", "drift gate", "lo shu", "u^72", "u⁷²"]) or symbolic.gates or symbolic.carrier_terms:
        channels.append(CorpusChannel.HARMONICODE_CORE)
    if any(t in hay for t in ["artificial intelligence", "agi", "llm", "agent", "reasoning", "prompt", "training loop", "alignment"]):
        channels.append(CorpusChannel.AI_REASONING)
    if any(t in hay for t in ["ethics", "ethical", "philosophy", "consent", "responsibility", "autonomy", "sovereignty", "accountability"]):
        channels.append(CorpusChannel.ETHICAL_PHILOSOPHY)
    if any(t in hay for t in ["language", "grammar", "syntax", "semantic", "translation", "transcription", "linguistics"]):
        channels.append(CorpusChannel.LANGUAGE_LEARNING)
    if any(t in hay for t in ["creative writing", "poetry", "fiction", "style", "narrative", "metaphor", "voice"]):
        channels.append(CorpusChannel.CREATIVE_WRITING)
    if any(t in hay for t in ["math", "algebra", "logic", "physics", "science", "equation", "proof", "geometry"]):
        channels.append(CorpusChannel.MATH_SCIENCE)
    if any(t in hay for t in ["music", "harmony", "rhythm", "audio", "daw", "synthesis", "mixing", "mastering"]):
        channels.append(CorpusChannel.MUSIC_THEORY_AUDIO)
    if not channels:
        channels.append(CorpusChannel.REFERENCE)
    return channels


def ingest_drive_candidate(candidate: DriveCorpusCandidate, *, full_text: str | None = None, max_chars: int = 2400) -> DriveIngestionResult:
    text = normalize_drive_text(full_text if full_text is not None else candidate.file.text_snippet or "")
    raw_chunks = chunk_text(text, max_chars=max_chars)
    if not raw_chunks and candidate.file.text_snippet:
        raw_chunks = [normalize_drive_text(candidate.file.text_snippet)]

    chunks: List[CorpusChunk] = []
    for idx, chunk in enumerate(raw_chunks):
        symbolic = extract_symbolic_structures(chunk)
        channels = classify_channels(chunk, symbolic)
        token_estimate = max(1, len(chunk.split()))
        chunk_hash = hash72_digest(("drive_corpus_chunk_v1", candidate.candidate_hash72, idx, chunk, [c.value for c in channels], symbolic.to_dict(), token_estimate), width=24)
        chunks.append(CorpusChunk(candidate.file.file_id, candidate.file.name, idx, chunk, channels, symbolic, token_estimate, chunk_hash))

    manifest = drive_candidate_to_ingestion_manifest(candidate)
    counts: Dict[str, int] = {}
    for chunk in chunks:
        for channel in chunk.channels:
            counts[channel.value] = counts.get(channel.value, 0) + 1
    receipt_hash = hash72_digest(("drive_ingestion_receipt_v1", candidate.candidate_hash72, [c.chunk_hash72 for c in chunks], counts), width=24)
    receipt = IngestionReceipt(candidate.candidate_hash72, [c.chunk_hash72 for c in chunks], counts, len(chunks), receipt_hash)
    return DriveIngestionResult(candidate, manifest, chunks, receipt)


def ingest_drive_records(records: Sequence[DriveFileRecord | Dict[str, Any]], *, text_by_file_id: Dict[str, str] | None = None, min_score: int = 30) -> Dict[str, Any]:
    plan = build_drive_crawl_plan(records)
    ingested: List[DriveIngestionResult] = []
    for candidate in plan.candidates:
        if candidate.score < min_score:
            continue
        full_text = (text_by_file_id or {}).get(candidate.file.file_id)
        ingested.append(ingest_drive_candidate(candidate, full_text=full_text))
    aggregate = hash72_digest(("drive_ingestion_batch_v1", plan.plan_hash72, [r.receipt.receipt_hash72 for r in ingested], min_score), width=24)
    return {"plan": plan.to_dict(), "ingested": [r.to_dict() for r in ingested], "aggregate_hash72": aggregate}


def corpus_chunks_to_linguistic_training_feedback(chunks: Sequence[CorpusChunk]) -> List[Dict[str, Any]]:
    feedback: List[Dict[str, Any]] = []
    for chunk in chunks:
        phase_seed = sum(ord(ch) for ch in chunk.chunk_hash72) % 72
        status = "STAGED" if CorpusChannel.HARMONICODE_CORE in chunk.channels or CorpusChannel.AI_REASONING in chunk.channels else "HELD"
        score = 95 if status == "STAGED" else 75
        feedback.append({
            "summary_hash72": chunk.chunk_hash72,
            "phases": [phase_seed],
            "status": status,
            "score": score,
            "channels": [c.value for c in chunk.channels],
            "symbolic_density": len(chunk.symbolic.equations) + len(chunk.symbolic.inequalities) + len(chunk.symbolic.gates),
        })
    return feedback


def main() -> None:
    demo = [{"id": "1", "name": "HARMONICODE Alignment Discussion Notes", "mimeType": "application/vnd.google-apps.document", "text": "HARMONICODE preserves Δe=0, Ψ=0, Θ15=true, Ω=true. xy≠yx. ROOT_GATE := { u^72 = Ω }"}]
    print(json.dumps(ingest_drive_records(demo), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
