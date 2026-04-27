"""
HHS Google Drive Language Learning Crawler v1
============================================

Curated Google Drive crawler/scorer for the HARMONICODE language learner.

Purpose
-------
Rank Google Drive files for language-learning, reasoning, and HARMONICODE
training ingestion using the existing crawler constraints, with heavy emphasis on:

- HARMONICODE / HHS / Harmonicode runtime development
- artificial intelligence / AGI / agents / LLM reasoning
- ethical philosophy / alignment / consent / responsibility
- math, science, logic, symbolic algebra
- language learning, grammar, translation, transcription
- literature, creative writing, style, rhetoric
- social psychology and communication
- music theory / audio / DAW / harmonic synthesis

Low-weight categories such as news, current events, politics, controversial
content, and social media are not banned. They are simply demoted for language
learning and reasoning-training corpus use.

This module does not directly access Google Drive APIs. It defines deterministic
policy, metadata scoring, and corpus-candidate receipts. A Drive connector or
crawler should feed file metadata/text snippets into this module.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Sequence
import json
import re

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_language_learning_crawler_v1 import CrawlPriority, CrawlTopicScore, LOW_WEIGHT_TOPICS


class DriveCorpusUse(str, Enum):
    PRIMARY_HARMONICODE_CORPUS = "PRIMARY_HARMONICODE_CORPUS"
    PRIMARY_LANGUAGE_REASONING_CORPUS = "PRIMARY_LANGUAGE_REASONING_CORPUS"
    SECONDARY_REFERENCE_CORPUS = "SECONDARY_REFERENCE_CORPUS"
    LOW_WEIGHT_REFERENCE_ONLY = "LOW_WEIGHT_REFERENCE_ONLY"
    EXCLUDE_FROM_TRAINING = "EXCLUDE_FROM_TRAINING"


@dataclass(frozen=True)
class DriveFileRecord:
    file_id: str
    name: str
    mime_type: str | None
    path_hint: str | None
    modified_time: str | None
    text_snippet: str | None
    web_url: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DriveCorpusCandidate:
    file: DriveFileRecord
    priority: CrawlPriority
    corpus_use: DriveCorpusUse
    score: int
    topic_scores: List[CrawlTopicScore]
    candidate_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["priority"] = self.priority.value
        data["corpus_use"] = self.corpus_use.value
        data["topic_scores"] = [t.to_dict() for t in self.topic_scores]
        return data


@dataclass(frozen=True)
class DriveCrawlPlan:
    candidates: List[DriveCorpusCandidate]
    rejected: List[DriveCorpusCandidate]
    policy_hash72: str
    plan_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidates": [c.to_dict() for c in self.candidates],
            "rejected": [c.to_dict() for c in self.rejected],
            "policy_hash72": self.policy_hash72,
            "plan_hash72": self.plan_hash72,
        }


HARMONICODE_HEAVY_TOPICS = {
    "harmonicode_hhs": [
        "harmonicode", "hhs", "holofractal", "hash72", "torus72", "lo shu", "theta15", "ouroboros", "drift gate", "phase lock", "xyzw", "u^72", "u⁷²", "ers", "entangled reciprocal seesaw", "qgu", "kernel", "receipt", "replay", "manifold", "projection engine", "temporal shell",
    ],
    "artificial_intelligence": [
        "artificial intelligence", "agi", "ai", "llm", "language model", "agent", "multi-agent", "copilot", "reasoning", "prompt", "training loop", "crawler", "corpus", "alignment", "inference", "embedding", "semantic", "transformer",
    ],
    "ethical_philosophy_alignment": [
        "ethics", "ethical", "philosophy", "alignment", "consent", "responsibility", "autonomy", "sovereignty", "logos", "tao", "good", "moral", "invariants", "constraint", "accountability", "harm", "bias", "meaning", "truth", "epistemic",
    ],
}

SECONDARY_TOPICS = {
    "math_science_logic": ["math", "mathematics", "algebra", "logic", "proof", "geometry", "physics", "science", "equation", "symbolic", "compiler", "interpreter", "runtime", "formal system"],
    "language_translation": ["language", "grammar", "syntax", "semantics", "translation", "transcription", "linguistics", "phonetics", "vocabulary", "rhetoric"],
    "creative_writing_literature": ["creative writing", "poetry", "literature", "fiction", "style", "narrative", "metaphor", "voice", "exercise", "draft"],
    "social_psychology": ["social psychology", "communication", "group dynamics", "behavior", "cognition", "perception", "relationship", "psychology"],
    "music_audio_theory": ["music theory", "harmony", "rhythm", "audio", "daw", "synthesis", "sequencing", "mixing", "mastering", "waveform", "midi"],
}

SUPPORTED_TEXT_MIME_HINTS = ["document", "text", "pdf", "markdown", "plain", "html", "presentation", "spreadsheet"]
HARD_EXCLUDE_HINTS = [".zip", ".exe", ".bin", ".iso", "backup", "cache", "node_modules", "venv", "__pycache__"]


def _haystack(record: DriveFileRecord) -> str:
    return " ".join([
        record.name or "",
        record.mime_type or "",
        record.path_hint or "",
        record.text_snippet or "",
        record.web_url or "",
    ]).lower()


def _matches(text: str, terms: Sequence[str]) -> List[str]:
    hits = []
    for term in terms:
        if term.lower() in text:
            hits.append(term)
    return hits


def _is_supported_text(record: DriveFileRecord) -> bool:
    hay = _haystack(record)
    return any(h in hay for h in SUPPORTED_TEXT_MIME_HINTS)


def score_drive_file(record: DriveFileRecord) -> DriveCorpusCandidate:
    hay = _haystack(record)
    topic_scores: List[CrawlTopicScore] = []
    score = 0

    if any(h in hay for h in HARD_EXCLUDE_HINTS):
        topic_scores.append(CrawlTopicScore("hard_exclude", -100, "File appears to be binary/cache/archive/build artifact."))
        h = hash72_digest(("drive_corpus_candidate_v1", record.to_dict(), -100, [t.to_dict() for t in topic_scores]), width=24)
        return DriveCorpusCandidate(record, CrawlPriority.REJECT, DriveCorpusUse.EXCLUDE_FROM_TRAINING, -100, topic_scores, h)

    if _is_supported_text(record):
        score += 15
        topic_scores.append(CrawlTopicScore("supported_text_format", 15, "File appears to be readable text/document material."))

    for topic, terms in HARMONICODE_HEAVY_TOPICS.items():
        hits = _matches(hay, terms)
        if hits:
            s = min(90, 35 + len(hits) * 10)
            score += s
            topic_scores.append(CrawlTopicScore(topic, s, f"Matched heavy HHS/AI/ethics terms: {', '.join(hits[:8])}"))

    for topic, terms in SECONDARY_TOPICS.items():
        hits = _matches(hay, terms)
        if hits:
            s = min(45, 10 + len(hits) * 6)
            score += s
            topic_scores.append(CrawlTopicScore(topic, s, f"Matched secondary learning terms: {', '.join(hits[:8])}"))

    for topic, terms in LOW_WEIGHT_TOPICS.items():
        hits = _matches(hay, terms)
        if hits:
            s = -(20 + len(hits) * 7)
            score += s
            topic_scores.append(CrawlTopicScore(topic, s, f"Matched low-weight topic terms: {', '.join(hits[:8])}"))

    # Conversation/history documents are highly valuable if paired with HHS/AI/ethics.
    if any(k in hay for k in ["conversation", "chat", "alignment discussion", "notes", "transcript", "white paper", "roadmap", "spec"]):
        s = 20 if score >= 35 else 8
        score += s
        topic_scores.append(CrawlTopicScore("development_history", s, "File appears to contain curated development history or alignment discussion context."))

    if score >= 90:
        priority = CrawlPriority.HIGH
        use = DriveCorpusUse.PRIMARY_HARMONICODE_CORPUS
    elif score >= 60:
        priority = CrawlPriority.HIGH
        use = DriveCorpusUse.PRIMARY_LANGUAGE_REASONING_CORPUS
    elif score >= 30:
        priority = CrawlPriority.MEDIUM
        use = DriveCorpusUse.SECONDARY_REFERENCE_CORPUS
    elif score >= 0:
        priority = CrawlPriority.LOW
        use = DriveCorpusUse.LOW_WEIGHT_REFERENCE_ONLY
    else:
        priority = CrawlPriority.REJECT
        use = DriveCorpusUse.EXCLUDE_FROM_TRAINING

    h = hash72_digest(("drive_corpus_candidate_v1", record.to_dict(), score, priority.value, use.value, [t.to_dict() for t in topic_scores]), width=24)
    return DriveCorpusCandidate(record, priority, use, score, topic_scores, h)


def build_drive_crawl_plan(records: Sequence[DriveFileRecord | Dict[str, Any]]) -> DriveCrawlPlan:
    normalized: List[DriveFileRecord] = []
    for r in records:
        if isinstance(r, DriveFileRecord):
            normalized.append(r)
        else:
            normalized.append(DriveFileRecord(
                file_id=str(r.get("file_id") or r.get("id") or r.get("resource_id") or ""),
                name=str(r.get("name") or r.get("title") or ""),
                mime_type=r.get("mime_type") or r.get("mimeType"),
                path_hint=r.get("path_hint") or r.get("path"),
                modified_time=r.get("modified_time") or r.get("modifiedTime"),
                text_snippet=r.get("text_snippet") or r.get("snippet") or r.get("text"),
                web_url=r.get("web_url") or r.get("webViewLink") or r.get("url"),
            ))

    scored = [score_drive_file(r) for r in normalized]
    candidates = sorted([c for c in scored if c.priority != CrawlPriority.REJECT], key=lambda c: c.score, reverse=True)
    rejected = sorted([c for c in scored if c.priority == CrawlPriority.REJECT], key=lambda c: c.score)
    policy_hash = hash72_digest(("drive_language_learning_policy_v1", HARMONICODE_HEAVY_TOPICS, SECONDARY_TOPICS, LOW_WEIGHT_TOPICS, HARD_EXCLUDE_HINTS), width=24)
    plan_hash = hash72_digest(("drive_crawl_plan_v1", [c.candidate_hash72 for c in candidates], [r.candidate_hash72 for r in rejected], policy_hash), width=24)
    return DriveCrawlPlan(candidates, rejected, policy_hash, plan_hash)


def drive_candidate_to_ingestion_manifest(candidate: DriveCorpusCandidate) -> Dict[str, Any]:
    return {
        "source": "google_drive",
        "file_id": candidate.file.file_id,
        "name": candidate.file.name,
        "web_url": candidate.file.web_url,
        "priority": candidate.priority.value,
        "corpus_use": candidate.corpus_use.value,
        "score": candidate.score,
        "candidate_hash72": candidate.candidate_hash72,
        "ingestion_seed_hash72": hash72_digest(("drive_ingestion_seed_v1", candidate.to_dict()), width=24),
        "routing": {
            "language_training": candidate.corpus_use in {DriveCorpusUse.PRIMARY_HARMONICODE_CORPUS, DriveCorpusUse.PRIMARY_LANGUAGE_REASONING_CORPUS},
            "harmonicode_core": candidate.corpus_use == DriveCorpusUse.PRIMARY_HARMONICODE_CORPUS,
            "reference_only": candidate.corpus_use == DriveCorpusUse.LOW_WEIGHT_REFERENCE_ONLY,
        },
    }


def main() -> None:
    demo = [
        {"id": "1", "name": "HARMONICODE Alignment Discussion Notes", "mimeType": "application/vnd.google-apps.document", "text": "Hash72 ethics alignment AGI HHS drift gate Lo Shu"},
        {"id": "2", "name": "Election news clipping", "mimeType": "text/plain", "text": "politics election breaking news"},
        {"id": "3", "name": "Creative Writing Exercises", "mimeType": "application/vnd.google-apps.document", "text": "poetry style narrative metaphor grammar"},
    ]
    print(json.dumps(build_drive_crawl_plan(demo).to_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
