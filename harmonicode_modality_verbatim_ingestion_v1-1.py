
"""
harmonicode_modality_verbatim_ingestion_v1.py

Standalone modality-specific verbatim ingestion and lightweight machine-learning
module for the Harmonicode agent stack.

Design rules:
- Does NOT modify the locked kernel/agent contract.
- Treats the kernel as the deterministic foundation and this file as a
  sandboxed compiler/learner over verbatim modality data.
- Learns only on the probabilistic/example layer; foundation invariants remain
  fixed and external.
- Produces canonical artifacts, witnesses, and hash-addressable payloads that
  can be handed to the authoritative agent/kernel surfaces.

This module is intentionally stdlib-only.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
import hashlib
import json
import math
import re
import struct


# ---------------------------------------------------------------------------
# Shared constants and helpers
# ---------------------------------------------------------------------------

DEFAULT_PHASE_RING_SYMBOL_MAP_V1: Dict[str, int] = {
    "x": 32, "y": 33, "z": 34, "w": 31,
    "A": 35, "B": 36, "C": 37, "D": 38, "E": 39, "F": 40, "G": 41, "H": 42,
    "I": 43, "√": 71,
}
DEFAULT_CROSSING_MUTATION_MAP_V1: Dict[str, str] = {
    "xz": "xy", "zx": "zw", "yw": "yx", "wy": "wz",
}
DEFAULT_MULTIMODAL_CHAIN_REGISTRY_V1: Dict[str, List[str]] = {
    "text": ["symbol_ring72", "adjacency_grammar", "closure_serializer"],
    "ipa": ["phoneme_ring72", "adjacency_grammar", "closure_serializer"],
    "math": ["constructor_ladder", "tensor_lift", "orbit_serializer"],
    "audio": ["sample_phase72", "wave_projection", "qudit_serializer"],
    "image": ["grid_projection", "tensor_lift", "closure_serializer"],
}

TEXT_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|[^\w\s]", re.UNICODE)


def hash72_like(payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "H72N-" + hashlib.sha256(data).hexdigest()[:18]


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def symbol_to_ring_index(symbol: str, ring_map: Dict[str, int]) -> int:
    if symbol in ring_map:
        return ring_map[symbol]
    # Deterministic fallback for symbols not in the authoritative map:
    return sum(ord(ch) for ch in symbol) % 72


def text_to_symbol_sequence(text: str) -> List[str]:
    return TEXT_TOKEN_RE.findall(text)


def normalize_probability_distribution(counter: Counter) -> Dict[str, float]:
    total = sum(counter.values())
    if total <= 0:
        return {}
    return {k: v / total for k, v in counter.items()}


def top_n_probs(prob_map: Dict[str, float], n: int = 8) -> List[Tuple[str, float]]:
    return sorted(prob_map.items(), key=lambda kv: (-kv[1], kv[0]))[:n]


def detect_pythagorean_identity_tokens(tokens: Sequence[str]) -> Dict[str, Any]:
    """
    Detect a canonical math-pattern witness of the form:
        a ^ 2 + b ^ 2 = c ^ 2
    The detector is strict on token order so that any hit is explicit and auditable.
    """
    canonical = [t for t in tokens if t]
    pattern = ["a", "^", "2", "+", "b", "^", "2", "=", "c", "^", "2"]
    hits: List[Dict[str, Any]] = []
    for i in range(0, max(0, len(canonical) - len(pattern) + 1)):
        window = canonical[i:i + len(pattern)]
        if window == pattern:
            hits.append({
                "start": i,
                "end": i + len(pattern) - 1,
                "pattern": pattern,
                "window": window,
                "identity_class": "a2_plus_b2_eq_c2",
            })
    return {
        "matched": bool(hits),
        "hits": hits,
        "pattern": pattern,
    }


def build_cross_modality_entanglement_audit_v1(
    *,
    source_modality: str,
    target_modality: str,
    canonical_sequence: Sequence[str],
    detector_name: str,
    detector_result: Dict[str, Any],
) -> Dict[str, Any]:
    payload = {
        "audit_type": "CROSS_MODALITY_ENTANGLEMENT_AUDIT_V1",
        "source_modality": source_modality,
        "target_modality": target_modality,
        "detector_name": detector_name,
        "detector_result": detector_result,
        "canonical_sequence": list(canonical_sequence),
        "sequence_hash72": hash72_like(list(canonical_sequence)),
        "audit_hash72": hash72_like({
            "source_modality": source_modality,
            "target_modality": target_modality,
            "detector_name": detector_name,
            "detector_result": detector_result,
            "canonical_sequence": list(canonical_sequence),
        }),
        "status": "FLAGGED" if detector_result.get("matched") else "CLEAR",
    }
    return payload


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------

@dataclass
class VerbatimSource:
    modality: str
    content: str
    source_name: str = "inline"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CanonicalToken:
    raw: str
    canonical: str
    ring_index: int
    token_class: str
    position: int


@dataclass
class WitnessBundle:
    modality: str
    source_hash72: str
    canonical_hash72: str
    projection_hash72: str
    gates: Dict[str, bool]
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IngestionArtifact:
    modality: str
    source: VerbatimSource
    canonical_tokens: List[CanonicalToken]
    projection: Dict[str, Any]
    witness: WitnessBundle
    address_hash72: str
    cross_talk_audits: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TemperatureVector:
    lexical: float = 0.3
    syntactic: float = 0.2
    semantic: float = 0.2
    cross_modal: float = 0.1
    exploratory: float = 0.2

    def as_dict(self) -> Dict[str, float]:
        return {
            "lexical": self.lexical,
            "syntactic": self.syntactic,
            "semantic": self.semantic,
            "cross_modal": self.cross_modal,
            "exploratory": self.exploratory,
        }


# ---------------------------------------------------------------------------
# Lightweight example-layer learner
# ---------------------------------------------------------------------------

@dataclass
class LearnedExample:
    modality: str
    artifact_hash72: str
    example_hash72: str
    canonical_sequence: List[str]
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class RingTransitionModel:
    """
    A simple first-order transition learner over canonical token strings.
    This lives on the probabilistic/example layer only.
    """

    def __init__(self) -> None:
        self.starts: Counter = Counter()
        self.transitions: Dict[str, Counter] = defaultdict(Counter)
        self.example_count: int = 0

    def fit_examples(self, examples: Sequence[LearnedExample]) -> None:
        self.starts.clear()
        self.transitions.clear()
        self.example_count = 0
        for ex in examples:
            seq = ex.canonical_sequence
            if not seq:
                continue
            self.example_count += 1
            self.starts[seq[0]] += ex.weight
            for a, b in zip(seq, seq[1:]):
                self.transitions[a][b] += ex.weight

    def start_distribution(self) -> Dict[str, float]:
        return normalize_probability_distribution(self.starts)

    def next_distribution(self, token: str) -> Dict[str, float]:
        return normalize_probability_distribution(self.transitions[token])

    def generate(
        self,
        max_len: int = 32,
        start_token: Optional[str] = None,
        temperature: float = 0.0,
    ) -> List[str]:
        import random

        if self.example_count == 0:
            return []
        if start_token is None:
            starts = self.start_distribution()
            if not starts:
                return []
            tokens = list(starts.keys())
            weights = [starts[t] for t in tokens]
            start_token = random.choices(tokens, weights=weights, k=1)[0]

        out = [start_token]
        while len(out) < max_len:
            dist = self.next_distribution(out[-1])
            if not dist:
                break
            tokens = list(dist.keys())
            weights = [dist[t] for t in tokens]
            if temperature > 0:
                adjusted = [max(w, 1e-12) ** (1 / max(temperature, 1e-9)) for w in weights]
                weights = adjusted
            nxt = random.choices(tokens, weights=weights, k=1)[0]
            out.append(nxt)
        return out


class ExampleLayerMemory:
    """
    Stores only sandboxed learned examples; does not mutate foundation rules.
    """

    def __init__(self) -> None:
        self.examples: List[LearnedExample] = []
        self.by_modality: Dict[str, List[LearnedExample]] = defaultdict(list)
        self.transition_models: Dict[str, RingTransitionModel] = defaultdict(RingTransitionModel)

    def add_artifact(self, artifact: IngestionArtifact, weight: float = 1.0, metadata: Optional[Dict[str, Any]] = None) -> LearnedExample:
        sequence = [tok.canonical for tok in artifact.canonical_tokens]
        example = LearnedExample(
            modality=artifact.modality,
            artifact_hash72=artifact.address_hash72,
            example_hash72=hash72_like({
                "modality": artifact.modality,
                "address_hash72": artifact.address_hash72,
                "sequence": sequence,
            }),
            canonical_sequence=sequence,
            weight=float(weight),
            metadata=metadata or {},
        )
        self.examples.append(example)
        self.by_modality[artifact.modality].append(example)
        self.transition_models[artifact.modality].fit_examples(self.by_modality[artifact.modality])
        return example

    def modality_report(self, modality: str) -> Dict[str, Any]:
        model = self.transition_models[modality]
        return {
            "modality": modality,
            "example_count": len(self.by_modality[modality]),
            "start_distribution": top_n_probs(model.start_distribution()),
            "top_transitions": {
                token: top_n_probs(model.next_distribution(token))
                for token in list(model.transitions.keys())[:8]
            },
        }


# ---------------------------------------------------------------------------
# Modality ingestion interfaces
# ---------------------------------------------------------------------------

class ModalityVerbatimIngestionBase(ABC):
    modality: str = "unknown"

    def __init__(
        self,
        *,
        ring_map: Optional[Dict[str, int]] = None,
        crossing_mutation_map: Optional[Dict[str, str]] = None,
        chain_registry: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        self.ring_map = dict(ring_map or DEFAULT_PHASE_RING_SYMBOL_MAP_V1)
        self.crossing_mutation_map = dict(crossing_mutation_map or DEFAULT_CROSSING_MUTATION_MAP_V1)
        self.chain_registry = dict(chain_registry or DEFAULT_MULTIMODAL_CHAIN_REGISTRY_V1)

    @abstractmethod
    def canonicalize(self, source: VerbatimSource) -> List[CanonicalToken]:
        raise NotImplementedError

    @abstractmethod
    def project_to_kernel(self, tokens: List[CanonicalToken], source: VerbatimSource) -> Dict[str, Any]:
        raise NotImplementedError

    def run_gates(self, tokens: List[CanonicalToken], projection: Dict[str, Any]) -> Dict[str, bool]:
        token_strings = [t.canonical for t in tokens]
        joined = "".join(token_strings)
        mutation_safe = True
        for bad in self.crossing_mutation_map:
            if bad in joined:
                mutation_safe = False
                break
        has_ring_indices = all(0 <= t.ring_index < 72 for t in tokens)
        has_projection_hash = "projection_hash72" in projection
        return {
            "has_ring_indices": has_ring_indices,
            "mutation_safe": mutation_safe,
            "has_projection_hash": has_projection_hash,
            "nonempty": len(tokens) > 0,
        }

    def build_witness(self, source: VerbatimSource, tokens: List[CanonicalToken], projection: Dict[str, Any]) -> WitnessBundle:
        gates = self.run_gates(tokens, projection)
        source_hash = hash72_like({
            "modality": source.modality,
            "source_name": source.source_name,
            "content": source.content,
            "metadata": source.metadata,
        })
        canonical_hash = hash72_like([token.__dict__ for token in tokens])
        projection_hash = projection.get("projection_hash72", hash72_like(projection))
        return WitnessBundle(
            modality=self.modality,
            source_hash72=source_hash,
            canonical_hash72=canonical_hash,
            projection_hash72=projection_hash,
            gates=gates,
            details={
                "chain": self.chain_registry.get(self.modality, []),
                "token_count": len(tokens),
            },
        )

    def address_hash72(self, source: VerbatimSource, tokens: List[CanonicalToken], projection: Dict[str, Any], witness: WitnessBundle) -> str:
        return hash72_like({
            "modality": self.modality,
            "source_hash72": witness.source_hash72,
            "canonical_hash72": witness.canonical_hash72,
            "projection_hash72": witness.projection_hash72,
            "gates": witness.gates,
        })


def cross_talk_audits(self, source: VerbatimSource, tokens: List[CanonicalToken], projection: Dict[str, Any]) -> List[Dict[str, Any]]:
    sequence = [t.canonical for t in tokens]
    audits: List[Dict[str, Any]] = []

    if self.modality == "audio":
        detector = detect_pythagorean_identity_tokens(sequence)
        if detector.get("matched"):
            audits.append(build_cross_modality_entanglement_audit_v1(
                source_modality="audio",
                target_modality="math",
                canonical_sequence=sequence,
                detector_name="detect_pythagorean_identity_tokens",
                detector_result=detector,
            ))

    return audits

def ingest_verbatim(self, source: VerbatimSource) -> IngestionArtifact:
        tokens = self.canonicalize(source)
        projection = self.project_to_kernel(tokens, source)
        witness = self.build_witness(source, tokens, projection)
        address_hash = self.address_hash72(source, tokens, projection, witness)
        return IngestionArtifact(
            modality=self.modality,
            source=source,
            canonical_tokens=tokens,
            projection=projection,
            witness=witness,
            address_hash72=address_hash,
        )


# ---------------------------------------------------------------------------
# Text / IPA / Math implementations
# ---------------------------------------------------------------------------

class TextVerbatimIngestionV1(ModalityVerbatimIngestionBase):
    modality = "text"

    def canonicalize(self, source: VerbatimSource) -> List[CanonicalToken]:
        raw_tokens = text_to_symbol_sequence(source.content)
        tokens: List[CanonicalToken] = []
        for i, raw in enumerate(raw_tokens):
            canonical = raw.lower()
            token_class = "word" if canonical.isalnum() else "punct"
            ring_index = symbol_to_ring_index(canonical[0] if canonical else raw, self.ring_map)
            tokens.append(CanonicalToken(raw=raw, canonical=canonical, ring_index=ring_index, token_class=token_class, position=i))
        return tokens

    def project_to_kernel(self, tokens: List[CanonicalToken], source: VerbatimSource) -> Dict[str, Any]:
        ring_trace = [tok.ring_index for tok in tokens]
        adjacency_pairs = [tokens[i].canonical + tokens[i + 1].canonical for i in range(len(tokens) - 1)]
        safe_pairs = [self.crossing_mutation_map.get(p, p) for p in adjacency_pairs]
        payload = {
            "modality": self.modality,
            "ring_trace": ring_trace,
            "adjacency_pairs": adjacency_pairs,
            "safe_pairs": safe_pairs,
            "token_classes": [t.token_class for t in tokens],
            "projection_hash72": hash72_like({
                "ring_trace": ring_trace,
                "safe_pairs": safe_pairs,
            }),
        }
        return payload


class IPAVerbatimIngestionV1(ModalityVerbatimIngestionBase):
    modality = "ipa"

    def canonicalize(self, source: VerbatimSource) -> List[CanonicalToken]:
        # Minimal IPA segmentation: preserve non-space characters as units.
        chars = [ch for ch in source.content if not ch.isspace()]
        tokens: List[CanonicalToken] = []
        for i, raw in enumerate(chars):
            canonical = raw
            token_class = "phoneme"
            ring_index = symbol_to_ring_index(canonical, self.ring_map)
            tokens.append(CanonicalToken(raw=raw, canonical=canonical, ring_index=ring_index, token_class=token_class, position=i))
        return tokens

    def project_to_kernel(self, tokens: List[CanonicalToken], source: VerbatimSource) -> Dict[str, Any]:
        ring_trace = [tok.ring_index for tok in tokens]
        payload = {
            "modality": self.modality,
            "ring_trace": ring_trace,
            "phoneme_count": len(tokens),
            "projection_hash72": hash72_like({"ring_trace": ring_trace, "phoneme_count": len(tokens)}),
        }
        return payload


class MathVerbatimIngestionV1(ModalityVerbatimIngestionBase):
    modality = "math"

    def canonicalize(self, source: VerbatimSource) -> List[CanonicalToken]:
        raw_tokens = text_to_symbol_sequence(source.content)
        tokens: List[CanonicalToken] = []
        for i, raw in enumerate(raw_tokens):
            canonical = raw.replace(" ", "")
            if canonical in {"=", "+", "-", "*", "/", "^", "√", "(", ")", "[", "]", "{", "}"}:
                token_class = "operator"
            elif canonical.isalpha():
                token_class = "symbol"
            elif canonical.replace(".", "", 1).isdigit():
                token_class = "number"
            else:
                token_class = "math_token"
            key = canonical[0] if canonical else raw
            ring_index = symbol_to_ring_index(key, self.ring_map)
            tokens.append(CanonicalToken(raw=raw, canonical=canonical, ring_index=ring_index, token_class=token_class, position=i))
        return tokens

    def project_to_kernel(self, tokens: List[CanonicalToken], source: VerbatimSource) -> Dict[str, Any]:
        operators = [t.canonical for t in tokens if t.token_class == "operator"]
        symbols = [t.canonical for t in tokens if t.token_class == "symbol"]
        ring_trace = [tok.ring_index for tok in tokens]
        payload = {
            "modality": self.modality,
            "ring_trace": ring_trace,
            "operators": operators,
            "symbols": symbols,
            "constructor_ladder_hint": [1, 2, 3, 5, 8] if any(s in {"a", "b", "c", "d", "e"} for s in symbols) else [],
            "projection_hash72": hash72_like({
                "ring_trace": ring_trace,
                "operators": operators,
                "symbols": symbols,
            }),
        }
        return payload


# ---------------------------------------------------------------------------
# Audio support
# ---------------------------------------------------------------------------

def _read_riff_chunks(path: Path) -> Dict[str, bytes]:
    with path.open("rb") as f:
        data = f.read()
    if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        raise ValueError("Not a RIFF/WAVE file")
    pos = 12
    chunks: Dict[str, bytes] = {}
    while pos + 8 <= len(data):
        chunk_id = data[pos:pos + 4].decode("ascii", errors="replace")
        chunk_size = struct.unpack("<I", data[pos + 4:pos + 8])[0]
        chunk_data = data[pos + 8:pos + 8 + chunk_size]
        chunks[chunk_id] = chunk_data
        pos += 8 + chunk_size + (chunk_size % 2)
    return chunks


def read_wav_frames(path: Path) -> Dict[str, Any]:
    chunks = _read_riff_chunks(path)
    if "fmt " not in chunks or "data" not in chunks:
        raise ValueError("WAV missing fmt or data chunk")
    fmt = chunks["fmt "]
    audio_format, num_channels, sample_rate, byte_rate, block_align, bits_per_sample = struct.unpack("<HHIIHH", fmt[:16])
    data = chunks["data"]

    if audio_format == 1:  # PCM
        if bits_per_sample == 16:
            sample_fmt = "<" + "h" * num_channels
        elif bits_per_sample == 32:
            sample_fmt = "<" + "i" * num_channels
        else:
            raise ValueError(f"Unsupported PCM bits_per_sample={bits_per_sample}")
    elif audio_format == 3:  # IEEE float
        if bits_per_sample == 32:
            sample_fmt = "<" + "f" * num_channels
        elif bits_per_sample == 64:
            sample_fmt = "<" + "d" * num_channels
        else:
            raise ValueError(f"Unsupported float bits_per_sample={bits_per_sample}")
    else:
        raise ValueError(f"Unsupported WAV audio_format={audio_format}")

    frame_size = struct.calcsize(sample_fmt)
    if frame_size != block_align:
        raise ValueError("Block align mismatch")
    frames = []
    for i in range(0, len(data), frame_size):
        chunk = data[i:i + frame_size]
        if len(chunk) < frame_size:
            break
        frames.append(struct.unpack(sample_fmt, chunk))
    return {
        "audio_format": audio_format,
        "num_channels": num_channels,
        "sample_rate": sample_rate,
        "bits_per_sample": bits_per_sample,
        "frames": frames,
    }


class AudioVerbatimIngestionV1(ModalityVerbatimIngestionBase):
    modality = "audio"

    def canonicalize(self, source: VerbatimSource) -> List[CanonicalToken]:
        path = Path(source.content)
        wav = read_wav_frames(path)
        tokens: List[CanonicalToken] = []
        max_abs = 1.0
        if wav["audio_format"] == 1:
            max_abs = float(2 ** (wav["bits_per_sample"] - 1) - 1)
        for i, frame in enumerate(wav["frames"]):
            primary = float(frame[0]) if frame else 0.0
            if wav["audio_format"] == 1:
                primary = primary / max_abs
            phase_idx = int(((primary + 1.0) / 2.0) * 71) % 72
            if primary > 0.25:
                canonical = "x"
            elif primary < -0.25:
                canonical = "y"
            else:
                canonical = "0"
            tokens.append(CanonicalToken(
                raw=str(primary),
                canonical=canonical,
                ring_index=phase_idx,
                token_class="sample",
                position=i,
            ))
        return tokens

    def project_to_kernel(self, tokens: List[CanonicalToken], source: VerbatimSource) -> Dict[str, Any]:
        ring_trace = [tok.ring_index for tok in tokens]
        symbol_trace = "".join(tok.canonical for tok in tokens)
        payload = {
            "modality": self.modality,
            "frame_count": len(tokens),
            "ring_trace": ring_trace,
            "symbol_trace": symbol_trace,
            "zero_crossing_count": sum(1 for t in tokens if t.canonical == "0"),
            "projection_hash72": hash72_like({
                "frame_count": len(tokens),
                "ring_trace": ring_trace[:72],
                "symbol_trace": symbol_trace[:144],
            }),
        }
        return payload


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class HarmonicodeModalityLearningSuiteV1:
    """
    High-level orchestrator for modality-specific ingestion and example-layer ML.
    """

    def __init__(self) -> None:
        self.modules: Dict[str, ModalityVerbatimIngestionBase] = {
            "text": TextVerbatimIngestionV1(),
            "ipa": IPAVerbatimIngestionV1(),
            "math": MathVerbatimIngestionV1(),
            "audio": AudioVerbatimIngestionV1(),
        }
        self.memory = ExampleLayerMemory()

    def ingest(self, source: VerbatimSource, *, example_weight: float = 1.0) -> IngestionArtifact:
        if source.modality not in self.modules:
            raise ValueError(f"Unsupported modality: {source.modality}")
        artifact = self.modules[source.modality].ingest_verbatim(source)
        self.memory.add_artifact(artifact, weight=example_weight, metadata=source.metadata)
        return artifact

    def modality_report(self, modality: str) -> Dict[str, Any]:
        if modality not in self.modules:
            raise ValueError(f"Unsupported modality: {modality}")
        return self.memory.modality_report(modality)

    def generate_candidate_sequence(
        self,
        modality: str,
        *,
        max_len: int = 32,
        start_token: Optional[str] = None,
        temperature: float = 0.0,
    ) -> List[str]:
        if modality not in self.memory.transition_models:
            return []
        return self.memory.transition_models[modality].generate(
            max_len=max_len,
            start_token=start_token,
            temperature=temperature,
        )


def cross_modality_entanglement_report(self, artifact: IngestionArtifact) -> Dict[str, Any]:
    return {
        "artifact_hash72": artifact.address_hash72,
        "modality": artifact.modality,
        "audit_count": len(artifact.cross_talk_audits),
        "audits": artifact.cross_talk_audits,
        "report_hash72": hash72_like({
            "artifact_hash72": artifact.address_hash72,
            "audits": artifact.cross_talk_audits,
        }),
    }

    def cross_modal_projection_hint(self, source_modality: str, target_modality: str, artifact: IngestionArtifact) -> Dict[str, Any]:
        return {
            "source_modality": source_modality,
            "target_modality": target_modality,
            "shared_ring_trace": artifact.projection.get("ring_trace", []),
            "source_projection_hash72": artifact.witness.projection_hash72,
            "target_chain": DEFAULT_MULTIMODAL_CHAIN_REGISTRY_V1.get(target_modality, []),
            "hint_hash72": hash72_like({
                "source_modality": source_modality,
                "target_modality": target_modality,
                "ring_trace": artifact.projection.get("ring_trace", []),
            }),
        }


# ---------------------------------------------------------------------------
# Optional CLI demo
# ---------------------------------------------------------------------------

def _demo() -> None:
    suite = HarmonicodeModalityLearningSuiteV1()

    text_artifact = suite.ingest(VerbatimSource(
        modality="text",
        source_name="demo_text",
        content="Closure anchors live at phase 0 or 42.",
    ))
    math_artifact = suite.ingest(VerbatimSource(
        modality="math",
        source_name="demo_math",
        content="c^2 = a^2 + b^2 ; d^2 = b^2 + c^2",
    ))

    report = {
        "text_artifact": {
            "address_hash72": text_artifact.address_hash72,
            "projection_hash72": text_artifact.witness.projection_hash72,
            "gates": text_artifact.witness.gates,
        },
        "math_artifact": {
            "address_hash72": math_artifact.address_hash72,
            "projection_hash72": math_artifact.witness.projection_hash72,
            "gates": math_artifact.witness.gates,
            "cross_talk_audits": math_artifact.cross_talk_audits,
        },
        "text_model_report": suite.modality_report("text"),
        "math_model_report": suite.modality_report("math"),
        "generated_math_sequence": suite.generate_candidate_sequence("math", max_len=12, temperature=0.0),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    _demo()
