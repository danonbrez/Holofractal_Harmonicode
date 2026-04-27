"""
HHS Language Learning Crawler v1
================================

Curated network crawler policy + scoring layer for the HARMONICODE language
learner.

Purpose
-------
Discover and rank corpus candidates for language learning, grammar,
transcription/translation, math/science, literature/creative writing, social
psychology, and music theory while demoting low-priority domains/topics such as
news, current events, politics, controversial content, and social media.

Important
---------
This module defines crawl policy, URL/topic scoring, and deterministic candidate
receipts. It intentionally does not perform unrestricted crawling by default.
Network fetching must be done by a caller that enforces robots.txt, rate limits,
content licenses, and storage boundaries.

Filtering semantics
-------------------
Low-priority topics are not banned or censored. They receive low corpus weight
for language-learning and reasoning-training runs.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, Iterable, List, Sequence
from urllib.parse import urlparse
import json
import re

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


class CrawlPriority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    REJECT = "REJECT"


@dataclass(frozen=True)
class CrawlTopicScore:
    topic: str
    score: int
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CrawlCandidate:
    url: str
    domain: str
    title: str | None
    priority: CrawlPriority
    score: int
    topic_scores: List[CrawlTopicScore]
    recommended_use: str
    candidate_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["priority"] = self.priority.value
        data["topic_scores"] = [t.to_dict() for t in self.topic_scores]
        return data


@dataclass(frozen=True)
class CrawlPolicyReceipt:
    allowed_topics: List[str]
    low_weight_topics: List[str]
    hard_reject_patterns: List[str]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CrawlPlan:
    seed_urls: List[str]
    candidates: List[CrawlCandidate]
    rejected: List[CrawlCandidate]
    policy: CrawlPolicyReceipt
    plan_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seed_urls": self.seed_urls,
            "candidates": [c.to_dict() for c in self.candidates],
            "rejected": [c.to_dict() for c in self.rejected],
            "policy": self.policy.to_dict(),
            "plan_hash72": self.plan_hash72,
        }


HIGH_VALUE_TOPICS = {
    "language_learning": ["language", "grammar", "syntax", "vocabulary", "phonetics", "phonology", "morphology", "linguistics", "esl", "foreign-language"],
    "transcription_translation": ["transcription", "translation", "bilingual", "parallel text", "subtitles", "captioning", "interlinear"],
    "math_science": ["mathematics", "algebra", "calculus", "geometry", "physics", "chemistry", "biology", "computer science", "logic", "proof"],
    "literature_creative_writing": ["literature", "poetry", "fiction", "creative writing", "rhetoric", "style", "narrative", "metaphor"],
    "social_psychology": ["social psychology", "cognition", "communication", "behavior", "perception", "group dynamics", "motivation"],
    "music_theory": ["music theory", "harmony", "counterpoint", "rhythm", "composition", "ear training", "orchestration", "synthesis"],
}

LOW_WEIGHT_TOPICS = {
    "news_current_events": ["news", "breaking", "current events", "headline", "daily", "live updates"],
    "politics": ["politics", "election", "president", "congress", "campaign", "party", "policy debate"],
    "controversial_content": ["controversy", "culture war", "scandal", "outrage", "polarizing"],
    "social_media": ["twitter", "x.com", "facebook", "instagram", "tiktok", "reddit", "threads", "social media"],
}

PREFERRED_EDU_DOMAINS = [".edu", ".ac.", "khanacademy.org", "mit.edu", "stanford.edu", "harvard.edu", "openstax.org", "wikibooks.org", "wikisource.org", "gutenberg.org", "imslp.org", "musictheory.net"]
HARD_REJECT_PATTERNS = ["/login", "/signup", "/account", "/cart", "/checkout", "javascript:", "mailto:"]


def default_policy_receipt() -> CrawlPolicyReceipt:
    allowed = sorted(HIGH_VALUE_TOPICS.keys())
    low = sorted(LOW_WEIGHT_TOPICS.keys())
    h = hash72_digest(("language_learning_crawler_policy_v1", allowed, low, HARD_REJECT_PATTERNS), width=24)
    return CrawlPolicyReceipt(allowed, low, HARD_REJECT_PATTERNS, h)


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def _haystack(url: str, title: str | None, snippet: str | None) -> str:
    return " ".join([url or "", title or "", snippet or ""]).lower()


def _contains_any(text: str, needles: Sequence[str]) -> List[str]:
    return [n for n in needles if n.lower() in text]


def score_url_candidate(url: str, *, title: str | None = None, snippet: str | None = None) -> CrawlCandidate:
    domain = _domain(url)
    hay = _haystack(url, title, snippet)
    topic_scores: List[CrawlTopicScore] = []
    score = 0

    if any(p in hay for p in HARD_REJECT_PATTERNS):
        topic_scores.append(CrawlTopicScore("hard_reject", -100, "URL matches a hard reject pattern such as login/signup/cart/mailto/javascript."))
        candidate_hash = hash72_digest(("crawl_candidate_v1", url, domain, title, score, [t.to_dict() for t in topic_scores]), width=24)
        return CrawlCandidate(url, domain, title, CrawlPriority.REJECT, -100, topic_scores, "reject", candidate_hash)

    if any(domain.endswith(d) or d in domain for d in PREFERRED_EDU_DOMAINS):
        score += 25
        topic_scores.append(CrawlTopicScore("preferred_source", 25, "Domain matches preferred educational/public-domain source class."))

    for topic, terms in HIGH_VALUE_TOPICS.items():
        hits = _contains_any(hay, terms)
        if hits:
            s = min(40, 12 + len(hits) * 7)
            score += s
            topic_scores.append(CrawlTopicScore(topic, s, f"Matched high-value terms: {', '.join(hits[:6])}"))

    for topic, terms in LOW_WEIGHT_TOPICS.items():
        hits = _contains_any(hay, terms)
        if hits:
            s = -(18 + len(hits) * 6)
            score += s
            topic_scores.append(CrawlTopicScore(topic, s, f"Matched low-weight terms: {', '.join(hits[:6])}"))

    if re.search(r"\.(pdf|txt|html|htm)$", url.lower()):
        score += 5
        topic_scores.append(CrawlTopicScore("crawlable_format", 5, "URL appears to target a crawlable educational document format."))

    if score >= 45:
        priority = CrawlPriority.HIGH
        use = "primary_training_corpus_candidate"
    elif score >= 20:
        priority = CrawlPriority.MEDIUM
        use = "secondary_training_corpus_candidate"
    elif score >= 0:
        priority = CrawlPriority.LOW
        use = "low_weight_reference_only"
    else:
        priority = CrawlPriority.REJECT
        use = "exclude_from_language_training_corpus"

    candidate_hash = hash72_digest(("crawl_candidate_v1", url, domain, title, score, [t.to_dict() for t in topic_scores], use), width=24)
    return CrawlCandidate(url, domain, title, priority, score, topic_scores, use, candidate_hash)


def build_crawl_plan(seed_urls: Sequence[str], metadata: Dict[str, Dict[str, str]] | None = None) -> CrawlPlan:
    policy = default_policy_receipt()
    candidates: List[CrawlCandidate] = []
    rejected: List[CrawlCandidate] = []
    for url in seed_urls:
        meta = (metadata or {}).get(url, {})
        c = score_url_candidate(url, title=meta.get("title"), snippet=meta.get("snippet"))
        if c.priority == CrawlPriority.REJECT:
            rejected.append(c)
        else:
            candidates.append(c)
    candidates = sorted(candidates, key=lambda c: c.score, reverse=True)
    rejected = sorted(rejected, key=lambda c: c.score)
    plan_hash = hash72_digest(("crawl_plan_v1", list(seed_urls), [c.candidate_hash72 for c in candidates], [r.candidate_hash72 for r in rejected], policy.receipt_hash72), width=24)
    return CrawlPlan(list(seed_urls), candidates, rejected, policy, plan_hash)


def corpus_candidate_to_training_seed(candidate: CrawlCandidate) -> Dict[str, Any]:
    return {
        "source_url": candidate.url,
        "domain": candidate.domain,
        "priority": candidate.priority.value,
        "score": candidate.score,
        "recommended_use": candidate.recommended_use,
        "crawler_candidate_hash72": candidate.candidate_hash72,
        "training_seed_hash72": hash72_digest(("corpus_training_seed_v1", candidate.to_dict()), width=24),
    }


def main() -> None:
    urls = [
        "https://www.gutenberg.org/files/1342/1342-h/1342-h.htm",
        "https://www.musictheory.net/lessons",
        "https://news.example.com/live-election-updates",
        "https://openstax.org/details/books/calculus-volume-1",
    ]
    print(json.dumps(build_crawl_plan(urls).to_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
