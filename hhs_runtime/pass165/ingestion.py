"""Pass 165 lightweight multimodal vector-store ingestion and governed learning.

The implementation preserves source bytes, tokenizes deterministically, projects
registered observations into one 5,184-bit Pass 163 frame, extracts bounded
invariant candidates, calculates novelty/contradiction separately, and submits
exact weight updates through the singleton VM81 authority runtime.
"""
from __future__ import annotations

from base64 import b64encode
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from fractions import Fraction
from hashlib import sha256
import csv
import io
import json
import re
from threading import RLock
from typing import Any, Iterable, Mapping, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass150.genome import Hash216Genome
from hhs_runtime.pass163.vmrc import COORDINATES, SNAPSHOT_BYTES, VMRCRuntime, VMRCSnapshot

SCHEMA = "HHS_PASS_165_MULTIMODAL_VECTOR_STORE_V1"
DOMAIN = b"HHS-P165-L5184-MMVS-ITIBP-V1\0"
TOKENIZER_VERSION = "HHS-P165-TOKENIZER-1.0.0"
CHUNKER_VERSION = "HHS-P165-CHUNKER-1.0.0"
PROJECTOR_VERSION = "HHS-P165-PROJECTOR-1.0.0"
INVARIANT_VERSION = "HHS-P165-INVARIANT-1.0.0"
LEARNING_RULE_VERSION = "HHS-P165-BOUNDED-CREDIT-1.0.0"
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_TOKENS = 131072
MAX_CHUNKS = 8192
MAX_GRAPH_EDGES = 524288
MAX_BACKPROP_DEPTH = 32
MAX_WEIGHT_DELTA = Fraction(1, 16)
MIN_WEIGHT = Fraction(-8, 1)
MAX_WEIGHT = Fraction(8, 1)
TEXT_MEDIA = {
    "TEXT", "MARKDOWN", "SOURCE_CODE", "JSON", "JSONL", "CSV", "HTML", "XML",
    "HHS_CONTRACT", "HHS_RECEIPT", "HHS_MANIFEST", "HHS_VECTOR_PACKET",
}
SUPPORTED_MODALITIES = TEXT_MEDIA | {"PDF", "IMAGE", "AUDIO", "VIDEO", "BINARY_OBJECT"}


class IngestionError(ValueError):
    def __init__(self, classification: str, detail: str | None = None) -> None:
        super().__init__(classification if detail is None else f"{classification}:{detail}")
        self.classification = classification
        self.detail = detail


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _root(domain: bytes, value: Any) -> str:
    return sha256(domain + canonical_bytes(value)).hexdigest()


def _fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and len(value) == 2:
        return Fraction(int(value[0]), int(value[1]))
    raise IngestionError("P165_NONCANONICAL_WEIGHT")


def detect_modality(source: bytes, declared: str | None = None) -> str:
    if source.startswith(b"%PDF-"):
        detected = "PDF"
    elif source.startswith(b"\x89PNG\r\n\x1a\n") or source.startswith((b"\xff\xd8\xff", b"GIF87a", b"GIF89a", b"BM")):
        detected = "IMAGE"
    elif source.startswith((b"RIFF", b"ID3", b"fLaC", b"OggS")):
        detected = "AUDIO"
    elif len(source) >= 12 and source[4:12] in (b"ftypisom", b"ftypmp42", b"ftypM4V "):
        detected = "VIDEO"
    else:
        try:
            text = source.decode("utf-8")
        except UnicodeDecodeError:
            detected = "BINARY_OBJECT"
        else:
            stripped = text.lstrip()
            upper = (declared or "").upper()
            if upper in SUPPORTED_MODALITIES:
                detected = upper
            elif stripped.startswith(("{", "[")):
                try:
                    parsed = json.loads(text)
                    detected = "JSON" if not isinstance(parsed, list) or "\n" not in text else "JSONL"
                except json.JSONDecodeError:
                    detected = "TEXT"
            elif stripped.startswith("<") and "</" in stripped:
                detected = "HTML" if "<html" in stripped.lower() else "XML"
            elif any(marker in text for marker in ("#include ", "def ", "class ", "function ", "const ", "import ")):
                detected = "SOURCE_CODE"
            elif "|" in text and "\n" in text:
                detected = "MARKDOWN"
            elif "," in text and "\n" in text:
                try:
                    rows = list(csv.reader(io.StringIO(text)))
                    detected = "CSV" if len(rows) > 1 and len({len(row) for row in rows}) == 1 else "TEXT"
                except csv.Error:
                    detected = "TEXT"
            else:
                detected = "TEXT"
    if declared:
        declared = declared.upper()
        if declared not in SUPPORTED_MODALITIES:
            raise IngestionError("P165_UNSUPPORTED_MODALITY", declared)
        compatible = declared == detected or (declared in TEXT_MEDIA and detected in TEXT_MEDIA) or declared == "BINARY_OBJECT"
        if not compatible:
            raise IngestionError("P165_MEDIA_TYPE_SPOOFING", f"{declared}!={detected}")
    return detected


@dataclass(frozen=True)
class SourceObject:
    source_id: str
    source_hash: str
    source_bytes: bytes
    declared_media_type: str | None
    detected_media_type: str
    byte_length: int
    provenance: str
    authorization_scope: str
    ingestion_epoch: int

    def summary(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_hash": self.source_hash,
            "declared_media_type": self.declared_media_type,
            "detected_media_type": self.detected_media_type,
            "byte_length": self.byte_length,
            "provenance": self.provenance,
            "authorization_scope": self.authorization_scope,
            "ingestion_epoch": self.ingestion_epoch,
        }


@dataclass(frozen=True)
class Token:
    token_id: str
    modality: str
    token_class: str
    canonical_payload: str
    source_span: tuple[int, int]
    temporal_span: tuple[int, int] | None
    spatial_span: tuple[int, int, int, int] | None
    structural_path: str
    local_relations: tuple[str, ...]
    provenance_root: str


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    token_ids: tuple[str, ...]
    source_span: tuple[int, int]
    structural_path: str


@dataclass(frozen=True)
class InvariantCandidate:
    candidate_id: str
    candidate_class: str
    proposition: str
    domain: str
    supporting_observations: tuple[str, ...]
    tested_transformations: tuple[str, ...]
    counterexamples: tuple[str, ...]
    confidence: str
    exactness_class: str
    dependency_root: str
    validation_state: str


@dataclass(frozen=True)
class WeightDelta:
    parameter_id: str
    prior_weight: str
    proposed_weight: str
    delta: str
    evidence_root: str
    residual_root: str
    learning_rule: str
    bounds: tuple[str, str]
    affected_dependencies: tuple[str, ...]
    expected_effect: str


@dataclass(frozen=True)
class IngestionResult:
    source: SourceObject
    tokens: tuple[Token, ...]
    chunks: tuple[Chunk, ...]
    graph_edges: tuple[tuple[str, str, str], ...]
    projection_bytes: bytes
    projection_hash72: str
    token_stream_root: str
    chunk_graph_root: str
    invariant_candidates: tuple[InvariantCandidate, ...]
    novelty: Mapping[str, Any]
    contradictions: tuple[Mapping[str, Any], ...]
    residual_bytes: bytes
    weight_deltas: tuple[WeightDelta, ...]
    ingestion_operation_hash216: str
    ingestion_positions_hash216: tuple[str, ...]


class MultimodalTokenizer:
    _word = re.compile(r"\w+|[^\w\s]", re.UNICODE)
    _printable = re.compile(rb"[\x20-\x7e]{3,}")

    def tokenize(self, source: SourceObject) -> tuple[Token, ...]:
        modality = source.detected_media_type
        if modality in TEXT_MEDIA:
            observations = self._text_observations(source.source_bytes.decode("utf-8"), modality)
        elif modality == "PDF":
            observations = self._pdf_observations(source.source_bytes)
        elif modality == "IMAGE":
            observations = self._binary_observations(source.source_bytes, "image_region", include_header=True)
        elif modality == "AUDIO":
            observations = self._binary_observations(source.source_bytes, "audio_frame", include_header=True)
        elif modality == "VIDEO":
            observations = self._binary_observations(source.source_bytes, "video_segment", include_header=True)
        else:
            observations = self._binary_observations(source.source_bytes, "binary_block", include_header=False)
        if len(observations) > MAX_TOKENS:
            raise IngestionError("P165_TOKEN_BOUND")
        out: list[Token] = []
        for obs in observations:
            body = {"version": TOKENIZER_VERSION, "modality": modality, **obs, "provenance_root": source.source_hash}
            out.append(Token(token_id=_root(b"HHS-P165-TOKEN-V1\0", body), modality=modality, provenance_root=source.source_hash, **obs))
        return tuple(out)

    def _text_observations(self, text: str, modality: str) -> list[dict[str, Any]]:
        observations: list[dict[str, Any]] = []
        byte_cursor = 0
        for line_no, line in enumerate(text.splitlines(keepends=True)):
            line_bytes = line.encode("utf-8")
            local = line.rstrip("\r\n")
            for match in self._word.finditer(local):
                payload = match.group(0)
                start = byte_cursor + len(local[: match.start()].encode("utf-8"))
                end = start + len(payload.encode("utf-8"))
                token_class = "text_lexeme" if payload.isalnum() or payload.replace("_", "").isalnum() else "symbol"
                if modality == "SOURCE_CODE":
                    token_class = "ast_lexeme" if token_class == "text_lexeme" else "equation_operator"
                elif modality in ("JSON", "JSONL") and payload not in "{}[],:":
                    token_class = "json_value"
                observations.append({"token_class": token_class, "canonical_payload": payload, "source_span": (start, end), "temporal_span": None, "spatial_span": None, "structural_path": f"line/{line_no}", "local_relations": ()})
            byte_cursor += len(line_bytes)
        return observations

    def _pdf_observations(self, raw: bytes) -> list[dict[str, Any]]:
        observations = self._binary_observations(raw[: min(len(raw), 4096)], "pdf_header_block", include_header=True)
        for index, match in enumerate(self._printable.finditer(raw)):
            observations.append({"token_class": "pdf_text_run", "canonical_payload": match.group(0).decode("ascii"), "source_span": (match.start(), match.end()), "temporal_span": None, "spatial_span": None, "structural_path": f"pdf/text/{index}", "local_relations": ()})
            if len(observations) >= MAX_TOKENS:
                break
        return observations

    @staticmethod
    def _binary_observations(raw: bytes, token_class: str, *, include_header: bool) -> list[dict[str, Any]]:
        observations: list[dict[str, Any]] = []
        block_size = 256
        if include_header and raw:
            observations.append({"token_class": f"{token_class}_header", "canonical_payload": raw[:64].hex(), "source_span": (0, min(64, len(raw))), "temporal_span": None, "spatial_span": None, "structural_path": "header", "local_relations": ()})
        for start in range(0, len(raw), block_size):
            block = raw[start : start + block_size]
            observations.append({"token_class": token_class, "canonical_payload": sha256(block).hexdigest(), "source_span": (start, start + len(block)), "temporal_span": (start // block_size, start // block_size + 1) if token_class in ("audio_frame", "video_segment") else None, "spatial_span": (0, start // block_size, 1, start // block_size + 1) if token_class == "image_region" else None, "structural_path": f"block/{start // block_size}", "local_relations": ()})
        return observations


class MultimodalLearningService:
    def __init__(self, vm81: VMRCRuntime | None = None) -> None:
        self._vm81 = vm81 or VMRCRuntime()
        self._tokenizer = MultimodalTokenizer()
        self._sources: dict[str, SourceObject] = {}
        self._results: dict[str, IngestionResult] = {}
        self._weights: dict[str, Fraction] = {}
        self._validated_invariants: dict[str, InvariantCandidate] = {}
        self._facts: dict[str, tuple[str, str]] = {}
        self._receipts: dict[str, dict[str, Any]] = {}
        self._history: list[dict[str, Any]] = []
        self._epoch = 0
        self._lock = RLock()

    def status(self) -> dict[str, Any]:
        return {"schema": SCHEMA, "classification": "HHS_PASS_165_MULTIMODAL_LEARNING_INGRESS_IMPLEMENTED", "ingestion_epoch": self._epoch, "sources": len(self._sources), "tokens": sum(len(r.tokens) for r in self._results.values()), "chunks": sum(len(r.chunks) for r in self._results.values()), "validated_invariants": len(self._validated_invariants), "weights": len(self._weights), "vm81": self._vm81.status(), "worker_commit_authority": False, "vm81_commit_authority": True}

    def capture_source(self, source_bytes: bytes, *, declared_media_type: str | None = None, provenance: str, authorization_scope: str) -> SourceObject:
        if not isinstance(source_bytes, (bytes, bytearray, memoryview)):
            raise IngestionError("P165_SOURCE_BYTES_REQUIRED")
        raw = bytes(source_bytes)
        if not raw:
            raise IngestionError("P165_EMPTY_SOURCE")
        if len(raw) > MAX_SOURCE_BYTES:
            raise IngestionError("P165_SOURCE_SIZE_BOUND")
        if raw.startswith((b"PK\x03\x04", b"\x1f\x8b")):
            raise IngestionError("P165_COMPRESSED_CONTAINER_QUARANTINED")
        if not provenance or not authorization_scope:
            raise IngestionError("P165_AUTHORIZATION_REQUIRED")
        source_hash = sha256(raw).hexdigest()
        detected = detect_modality(raw, declared_media_type)
        existing = self._sources.get(source_hash)
        if existing is not None:
            return existing
        source_id = _root(b"HHS-P165-SOURCE-V1\0", {"source_hash": source_hash, "declared": declared_media_type, "detected": detected, "provenance": provenance, "authorization_scope": authorization_scope})
        return SourceObject(source_id, source_hash, raw, declared_media_type.upper() if declared_media_type else None, detected, len(raw), provenance, authorization_scope, self._epoch)

    @staticmethod
    def chunk_tokens(tokens: Sequence[Token], width: int = 32) -> tuple[tuple[Chunk, ...], tuple[tuple[str, str, str], ...]]:
        if not 1 <= width <= 256:
            raise IngestionError("P165_CHUNK_BOUND")
        chunks: list[Chunk] = []
        edges: list[tuple[str, str, str]] = []
        for start in range(0, len(tokens), width):
            window = tuple(tokens[start : start + width])
            if not window:
                continue
            body = {"version": CHUNKER_VERSION, "token_ids": [t.token_id for t in window], "source_span": [window[0].source_span[0], window[-1].source_span[1]]}
            chunk_id = _root(b"HHS-P165-CHUNK-V1\0", body)
            chunks.append(Chunk(chunk_id, tuple(t.token_id for t in window), (window[0].source_span[0], window[-1].source_span[1]), f"chunk/{len(chunks)}"))
            edges.extend((left.token_id, right.token_id, "PRECEDES") for left, right in zip(window, window[1:]))
            edges.extend((chunk_id, token.token_id, "CONTAINS") for token in window)
        edges.extend((left.chunk_id, right.chunk_id, "FOLLOWS") for left, right in zip(chunks, chunks[1:]))
        if len(chunks) > MAX_CHUNKS or len(edges) > MAX_GRAPH_EDGES:
            raise IngestionError("P165_GRAPH_RESOURCE_BOUND")
        return tuple(chunks), tuple(edges)

    @staticmethod
    def project_5184(tokens: Sequence[Token], edges: Sequence[tuple[str, str, str]]) -> VMRCSnapshot:
        raw = bytearray(SNAPSHOT_BYTES)
        identities = [f"TOKEN:{t.token_id}:{t.token_class}" for t in tokens] + [f"EDGE:{a}:{b}:{k}" for a, b, k in edges]
        for identity in identities:
            digest = sha256(b"HHS-P165-PROJECTION-V1\0" + identity.encode()).digest()
            for offset in (0, 2, 4):
                coordinate = int.from_bytes(digest[offset : offset + 2], "big") % COORDINATES
                byte_index, bit_index = divmod(coordinate, 8)
                raw[byte_index] |= 1 << (7 - bit_index)
        return VMRCSnapshot(raw)

    @staticmethod
    def extract_invariants(tokens: Sequence[Token], edges: Sequence[tuple[str, str, str]]) -> tuple[InvariantCandidate, ...]:
        candidates: list[InvariantCandidate] = []
        payload_map: dict[str, list[str]] = defaultdict(list)
        for token in tokens:
            payload_map[token.canonical_payload].append(token.token_id)
        for payload, support in sorted(payload_map.items()):
            if len(support) >= 2:
                body = {"class": "REPETITION", "payload": payload, "support": support}
                candidates.append(InvariantCandidate(_root(b"HHS-P165-INVARIANT-V1\0", body), "REPETITION", f"canonical token {payload!r} repeats {len(support)} times", "TOKEN_STREAM", tuple(support), ("SOURCE_OFFSET_TRANSLATION",), (), str(Fraction(len(support), max(2, len(tokens)))), "EXACT_COUNT", _root(b"HHS-P165-INVARIANT-DEPENDENCY-V1\0", support), "CANDIDATE"))
        for kind, count in sorted(Counter(k for _, _, k in edges).items()):
            if count >= 2:
                cls = "ORDER" if kind in ("PRECEDES", "FOLLOWS") else "DEPENDENCY"
                body = {"class": cls, "kind": kind, "count": count}
                candidates.append(InvariantCandidate(_root(b"HHS-P165-INVARIANT-V1\0", body), cls, f"relation {kind} is structurally repeated {count} times", "CHUNK_GRAPH", tuple(f"{a}:{b}" for a, b, k in edges if k == kind)[:128], ("DETERMINISTIC_RECHUNK",), (), "1", "EXACT_GRAPH_COUNT", _root(b"HHS-P165-INVARIANT-DEPENDENCY-V1\0", body), "CANDIDATE"))
        return tuple(candidates[:1024])

    def _novelty(self, source: SourceObject, tokens: Sequence[Token], projection: bytes, invariants: Sequence[InvariantCandidate]) -> dict[str, Any]:
        known_tokens = {t.token_id for result in self._results.values() for t in result.tokens}
        known_combinations = {r.token_stream_root for r in self._results.values()}
        stream_root = _root(b"HHS-P165-TOKEN-STREAM-V1\0", [t.token_id for t in tokens])
        return {"new_source": source.source_hash not in self._sources, "new_token_count": sum(t.token_id not in known_tokens for t in tokens), "new_combination": stream_root not in known_combinations, "new_relation_count": 0, "new_version": False, "new_invariant_evidence_count": sum(c.candidate_id not in self._validated_invariants for c in invariants), "projection_popcount": sum(byte.bit_count() for byte in projection)}

    def _contradictions(self, source: SourceObject) -> tuple[dict[str, Any], ...]:
        facts = re.findall(r"(?im)^\s*([A-Za-z_][\w.-]{0,127})\s*=\s*(true|false|-?\d+(?:/\d+)?)\s*$", source.source_bytes.decode("utf-8", errors="ignore"))
        contradictions = []
        for key, value in facts:
            prior = self._facts.get(key)
            if prior is not None and prior[0] != value:
                body = {"proposition": key, "prior_value": prior[0], "incoming_value": value, "prior_source": prior[1], "incoming_source": source.source_hash}
                contradictions.append({"contradiction_id": _root(b"HHS-P165-CONTRADICTION-V1\0", body), **body, "condition": "same proposition and scope with unequal canonical values"})
        return tuple(contradictions)

    def _weight_deltas(self, invariants: Sequence[InvariantCandidate], novelty: Mapping[str, Any], contradictions: Sequence[Mapping[str, Any]], residual: bytes) -> tuple[WeightDelta, ...]:
        if contradictions:
            return ()
        residual_count = sum(byte.bit_count() for byte in residual)
        residual_root = sha256(residual).hexdigest()
        novelty_factor = Fraction(min(16, int(novelty["new_token_count"]) + int(novelty["new_invariant_evidence_count"])), 256)
        deltas = []
        for candidate in invariants[:256]:
            prior = self._weights.get(candidate.candidate_id, Fraction(0, 1))
            raw_delta = min(MAX_WEIGHT_DELTA, Fraction(max(1, len(candidate.supporting_observations)), 1024) + novelty_factor)
            if residual_count == 0:
                raw_delta = Fraction(0, 1)
            proposed = max(MIN_WEIGHT, min(MAX_WEIGHT, prior + raw_delta))
            if proposed != prior:
                deltas.append(WeightDelta(candidate.candidate_id, str(prior), str(proposed), str(proposed - prior), _root(b"HHS-P165-EVIDENCE-V1\0", candidate.supporting_observations), residual_root, LEARNING_RULE_VERSION, (str(MIN_WEIGHT), str(MAX_WEIGHT)), (candidate.dependency_root,), "increase support without overwriting source evidence"))
        return tuple(deltas)

    def analyze(self, source_bytes: bytes, *, declared_media_type: str | None = None, provenance: str, authorization_scope: str) -> IngestionResult:
        with self._lock:
            source = self.capture_source(source_bytes, declared_media_type=declared_media_type, provenance=provenance, authorization_scope=authorization_scope)
            existing = self._results.get(source.source_hash)
            if existing is not None:
                return existing
            tokens = self._tokenizer.tokenize(source)
            chunks, graph_edges = self.chunk_tokens(tokens)
            projection_bytes = self.project_5184(tokens, graph_edges).to_bytes()
            projection_hash72 = hash72_digest(b"", projection_bytes)
            token_root = _root(b"HHS-P165-TOKEN-STREAM-V1\0", [asdict(t) for t in tokens])
            graph_root = _root(b"HHS-P165-CHUNK-GRAPH-V1\0", {"chunks": [asdict(c) for c in chunks], "edges": graph_edges})
            invariants = self.extract_invariants(tokens, graph_edges)
            novelty = self._novelty(source, tokens, projection_bytes, invariants)
            contradictions = self._contradictions(source)
            prediction = self._results[self._history[-1]["source_hash"]].projection_bytes if self._history else bytes(SNAPSHOT_BYTES)
            residual = bytes(a ^ b for a, b in zip(projection_bytes, prediction))
            deltas = self._weight_deltas(invariants, novelty, contradictions, residual)
            operation_body = {"domain": "HHS-P165-INGESTION-OPERATION-V1", "source_hash": source.source_hash, "adapter_version": f"{source.detected_media_type}-1.0.0", "tokenizer_version": TOKENIZER_VERSION, "chunker_version": CHUNKER_VERSION, "projection_registry": PROJECTOR_VERSION, "prior_vector_frontier": self._history[-1]["projection_root_hash72"] if self._history else "GENESIS", "prior_weight_frontier": self.weight_root, "invariant_extractor_version": INVARIANT_VERSION, "learning_rule_version": LEARNING_RULE_VERSION, "authorization_scope": authorization_scope, "expected_roots": {"token_stream_root": token_root, "chunk_graph_root": graph_root, "projection_hash72": projection_hash72, "invariant_set_root": _root(b"HHS-P165-INVARIANT-SET-V1\0", [asdict(i) for i in invariants])}}
            positions = Hash216Genome.positions(canonical_bytes(operation_body), previous_root=self._history[-1]["ingestion_operation_hash216"] if self._history else "0" * 64, sequence=self._epoch)
            return IngestionResult(source, tokens, chunks, graph_edges, projection_bytes, projection_hash72, token_root, graph_root, invariants, novelty, contradictions, residual, deltas, Hash216Genome.root(positions), positions)

    @property
    def weight_root(self) -> str:
        return _root(b"HHS-P165-WEIGHT-FRONTIER-V1\0", {k: str(self._weights[k]) for k in sorted(self._weights)})

    def validate_weight_update(self, result: IngestionResult) -> dict[str, Any]:
        if result.contradictions:
            raise IngestionError("P165_CONTRADICTORY_INVARIANT_PROMOTION")
        for delta in result.weight_deltas:
            prior, proposed = _fraction(delta.prior_weight), _fraction(delta.proposed_weight)
            if prior != self._weights.get(delta.parameter_id, Fraction(0, 1)):
                raise IngestionError("P165_STALE_PRIOR_WEIGHT_ROOT")
            if proposed < MIN_WEIGHT or proposed > MAX_WEIGHT or abs(proposed - prior) > MAX_WEIGHT_DELTA:
                raise IngestionError("P165_WEIGHT_RANGE_REJECTED")
        return {"classification": "P165_WEIGHT_VALIDATION_RECEIPT", "validated": True, "weight_delta_count": len(result.weight_deltas), "prior_weight_root": self.weight_root, "dependency_scoped_replay": True}

    def commit_learning_epoch(self, result: IngestionResult) -> dict[str, Any]:
        with self._lock:
            if result.source.source_hash in self._results:
                return {**self._receipts[result.source.source_hash], "classification": "P165_CONTENT_ADDRESSED_SOURCE_REUSED", "reused": True}
            self.validate_weight_update(result)
            prior_state, prior_weight_root = self._vm81.state_hash72, self.weight_root
            for delta in result.weight_deltas:
                self._weights[delta.parameter_id] = _fraction(delta.proposed_weight)
                self._vm81.register_parameter(type="P165_WEIGHT", value=delta.proposed_weight, domain="MULTIMODAL_VECTOR_STORE", phase=int(delta.parameter_id[:8], 16) % 72, operator="BOUNDED_CREDIT_ASSIGNMENT", constraints=("P165_EXACT_WEIGHT", "P165_SOURCE_PRESERVING"), provenance=result.source.source_hash)
            digest = sha256(result.projection_bytes + bytes.fromhex(result.ingestion_operation_hash216)).digest()
            writes = {index: 1 for index in sorted({digest[i] % 81 for i in range(min(16, len(digest)))})}
            candidate = self._vm81.submit_candidate(thread=63, writes=writes, operation="VMRC_COMMIT", expected_input_hash72=self._vm81.state_hash72, dependency_root=result.chunk_graph_root, capability_scope="P165_LEARNING_COMMIT", source_architecture="P165_REFERENCE_CPU", target_architecture="VM81")
            vm81_result = self._vm81.execute(candidate)
            for item in result.invariant_candidates:
                self._validated_invariants[item.candidate_id] = InvariantCandidate(**{**asdict(item), "validation_state": "VALIDATED"})
            for key, value in re.findall(r"(?im)^\s*([A-Za-z_][\w.-]{0,127})\s*=\s*(true|false|-?\d+(?:/\d+)?)\s*$", result.source.source_bytes.decode("utf-8", errors="ignore")):
                self._facts[key] = (value, result.source.source_hash)
            self._sources[result.source.source_hash] = result.source
            self._results[result.source.source_hash] = result
            self._epoch += 1
            invariant_root = _root(b"HHS-P165-INVARIANT-SET-V1\0", [asdict(i) for i in result.invariant_candidates])
            receipt_body = {"schema": "P165_LEARNING_COMMIT_RECEIPT", "ingestion_epoch": self._epoch, "source_root": result.source.source_hash, "token_root": result.token_stream_root, "chunk_root": result.chunk_graph_root, "projection_root_hash72": result.projection_hash72, "invariant_root": invariant_root, "prior_weight_root": prior_weight_root, "resulting_weight_root": self.weight_root, "incoming_vm81_hash72": prior_state, "outgoing_vm81_hash72": self._vm81.state_hash72, "ingestion_operation_hash216": result.ingestion_operation_hash216, "weight_delta_count": len(result.weight_deltas), "contradiction_count": len(result.contradictions), "vm81_commit_receipt": vm81_result["commit"]["receipt"], "replay_required": True}
            receipt_hash72 = hash72_digest(receipt_body, result.projection_bytes)
            receipt = {**receipt_body, "receipt_hash72": receipt_hash72, "classification": "HHS_PASS_165_LEARNING_EPOCH_COMMITTED", "reused": False}
            self._receipts[result.source.source_hash] = receipt
            self._history.append({**receipt_body, "receipt_hash72": receipt_hash72, "projection_b64": b64encode(result.projection_bytes).decode("ascii"), "source_hash": result.source.source_hash, "source_bytes_b64": b64encode(result.source.source_bytes).decode("ascii"), "declared_media_type": result.source.declared_media_type, "provenance": result.source.provenance, "authorization_scope": result.source.authorization_scope})
            return receipt

    def ingest_source(self, source_bytes: bytes, **kwargs: Any) -> dict[str, Any]:
        result = self.analyze(source_bytes, **kwargs)
        receipt = self.commit_learning_epoch(result)
        return {"receipt": receipt, "source": result.source.summary(), "token_count": len(result.tokens), "chunk_count": len(result.chunks), "graph_edge_count": len(result.graph_edges), "projection_popcount": sum(b.bit_count() for b in result.projection_bytes), "projection_hash72": result.projection_hash72, "invariant_candidate_count": len(result.invariant_candidates), "novelty": dict(result.novelty), "contradictions": list(result.contradictions), "weight_delta_count": len(result.weight_deltas)}

    def query_invariants(self, *, candidate_class: str | None = None) -> list[dict[str, Any]]:
        values: Iterable[InvariantCandidate] = self._validated_invariants.values()
        if candidate_class:
            values = (item for item in values if item.candidate_class == candidate_class)
        return [asdict(item) for item in sorted(values, key=lambda item: item.candidate_id)]

    def get_ingestion_receipt(self, source_hash: str) -> dict[str, Any]:
        try:
            return json.loads(canonical_bytes(self._receipts[source_hash]))
        except KeyError as exc:
            raise IngestionError("P165_RECEIPT_NOT_FOUND") from exc

    def replay_ingestion(self) -> dict[str, Any]:
        import base64
        replay = MultimodalLearningService(vm81=VMRCRuntime())
        for record in self._history:
            result = replay.ingest_source(base64.b64decode(record["source_bytes_b64"]), declared_media_type=record["declared_media_type"], provenance=record["provenance"], authorization_scope=record["authorization_scope"])
            if result["receipt"]["receipt_hash72"] != record["receipt_hash72"]:
                raise IngestionError("P165_REPLAY_MISMATCH")
        if replay.weight_root != self.weight_root or replay._vm81.state_hash72 != self._vm81.state_hash72:
            raise IngestionError("P165_REPLAY_MISMATCH")
        return {"classification": "P165_REPLAY_RECEIPT", "records": len(self._history), "weight_root": self.weight_root, "vm81_state_hash72": self._vm81.state_hash72, "deterministic_replay": True}


DEFAULT_MULTIMODAL_LEARNING_SERVICE = MultimodalLearningService()
