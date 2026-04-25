"""
HHS Text Semantic Reconstruction Layer v1
=========================================

Lossless text -> symbolic meaning adapter for the HHS multimodal ingestion stack.

This layer starts from files that are already deterministically ingested by the
multimodal tokenizer/database layer. It reconstructs textual content from stored
file bytes, verifies lossless round-trip hashing, emits structural text tokens,
maps those tokens into symbolic semantic nodes, and stores the reconstruction in
an auditable database + ledger.

Pipeline:

    ingested text-like file record
    -> raw byte reconstruction
    -> UTF-8 text projection
    -> line / word / symbol tokens
    -> semantic node extraction
    -> relation graph
    -> Hash72 + Unicode symbols
    -> invariant gate Δe/Ψ/Θ15/Ω
    -> database commit or quarantine
    -> ledger append + replay

This is a structural semantic layer, not an LLM summarizer. It does not guess
intent. Meaning is represented as addressable symbolic relations grounded in the
lossless source text.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple
import base64
import json
import re

from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest
from hhs_runtime.hhs_memory_ledger_replay_v1 import MemoryLedger, replay_ledger
from hhs_runtime.hhs_multimodal_file_tokenizer_db_v1 import (
    FileStorageRecord,
    Modality,
    MultimodalFileDatabase,
    StorageStatus,
    ingest_files,
)
from hhs_runtime.hhs_recursive_symbol_kernel_v1 import (
    AddressRelation,
    GlobalSymbolCache,
    OrthogonalChain,
    SymbolEntityType,
)
from hhs_runtime.hhs_self_modifying_agents_v1 import EthicalInvariantReceipt, ModificationStatus


TEXTUAL_MODALITIES = {
    Modality.TEXT.value,
    Modality.MARKDOWN.value,
    Modality.JSON.value,
    Modality.CSV.value,
    Modality.PYTHON.value,
}


class SemanticTokenKind(str, Enum):
    LINE = "LINE"
    WORD = "WORD"
    NUMBER = "NUMBER"
    SYMBOL = "SYMBOL"
    OPERATOR = "OPERATOR"
    HHS_TERM = "HHS_TERM"
    HASH72 = "HASH72"
    UNICODE = "UNICODE"


class SemanticRelationKind(str, Enum):
    CONTAINS = "CONTAINS"
    FOLLOWS = "FOLLOWS"
    DEFINES = "DEFINES"
    REFERENCES = "REFERENCES"
    EQUALS = "EQUALS"
    TRANSFORMS_TO = "TRANSFORMS_TO"
    ADDRESSES = "ADDRESSES"


class ReconstructionStatus(str, Enum):
    COMMITTED = "COMMITTED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class TextReconstruction:
    """Lossless text projection from a file record."""

    source_file_hash72: str
    filename: str
    modality: str
    encoding: str
    text_hash72: str
    byte_roundtrip_hash72: str
    roundtrip_ok: bool
    char_count: int
    line_count: int
    text_preview: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class SemanticToken:
    """Addressable structural token extracted from reconstructed text."""

    token_index: int
    kind: SemanticTokenKind
    value: str
    line_index: int
    char_start: int
    char_end: int
    token_hash72: str
    token_symbol: str
    token_codepoint: str

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["kind"] = self.kind.value
        return data


@dataclass(frozen=True)
class SemanticNode:
    """Symbolic meaning node grounded in source tokens."""

    node_index: int
    label: str
    category: str
    source_token_hashes: List[str]
    node_hash72: str
    node_symbol: str
    node_codepoint: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class SemanticRelation:
    """Addressable relation between tokens/nodes."""

    relation_index: int
    kind: SemanticRelationKind
    source_hash72: str
    target_hash72: str
    evidence_token_hash72: str
    relation_hash72: str

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["kind"] = self.kind.value
        return data


@dataclass(frozen=True)
class SemanticRecord:
    """Full semantic reconstruction database record."""

    reconstruction: TextReconstruction
    tokens: List[SemanticToken]
    nodes: List[SemanticNode]
    relations: List[SemanticRelation]
    invariant_gate: EthicalInvariantReceipt
    status: ReconstructionStatus
    semantic_hash72: str
    quarantine_hash72: str | None

    def to_dict(self) -> Dict[str, object]:
        return {
            "reconstruction": self.reconstruction.to_dict(),
            "tokens": [token.to_dict() for token in self.tokens],
            "nodes": [node.to_dict() for node in self.nodes],
            "relations": [relation.to_dict() for relation in self.relations],
            "invariant_gate": self.invariant_gate.to_dict(),
            "status": self.status.value,
            "semantic_hash72": self.semantic_hash72,
            "quarantine_hash72": self.quarantine_hash72,
        }


@dataclass(frozen=True)
class SemanticRunReceipt:
    """Receipt for a semantic reconstruction run."""

    module: str
    semantic_database_path: str
    files_seen: int
    records_committed: int
    records_quarantined: int
    token_count: int
    node_count: int
    relation_count: int
    ledger_commit_receipt: Dict[str, object]
    replay_receipt: Dict[str, object]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def theta15_true() -> bool:
    return (
        all(sum(row) == 15 for row in LO_SHU_3X3)
        and all(sum(LO_SHU_3X3[r][c] for r in range(3)) == 15 for c in range(3))
        and sum(LO_SHU_3X3[i][i] for i in range(3)) == 15
        and sum(LO_SHU_3X3[i][2 - i] for i in range(3)) == 15
    )


def _symbol_from_hash(h72: str, offset: int = 0) -> tuple[str, str]:
    base = 0xF500
    span = 0x0A00
    acc = offset
    for ch in h72:
        acc = (acc * 139 + ord(ch)) % span
    cp = base + acc
    return chr(cp), f"U+{cp:04X}"


def _record_from_dict(data: Dict[str, object]) -> Dict[str, object]:
    return data


def reconstruct_text_from_file_record(record: Dict[str, object]) -> tuple[TextReconstruction, str]:
    observation = record.get("observation", {})
    if not isinstance(observation, dict):
        raise ValueError("file record missing observation")
    modality = str(observation.get("modality", ""))
    if modality not in TEXTUAL_MODALITIES:
        raise ValueError(f"record modality is not textual: {modality}")

    path = Path(str(observation.get("path", "")))
    if not path.exists():
        raise FileNotFoundError(str(path))
    data = path.read_bytes()
    text = data.decode("utf-8", errors="replace")
    reencoded = text.encode("utf-8", errors="replace")
    byte_roundtrip_hash = hash72_digest(("text_roundtrip_bytes_v1", len(reencoded), base64.b64encode(reencoded).decode("ascii")), width=24)
    source_byte_hash = str(observation.get("byte_hash72", ""))
    # A strict equality can fail if source had non-UTF8 bytes. In that case the
    # record is still represented but quarantined by the invariant gate.
    roundtrip_ok = byte_roundtrip_hash == source_byte_hash
    lines = text.splitlines()
    reconstruction = TextReconstruction(
        source_file_hash72=source_byte_hash,
        filename=str(observation.get("filename", path.name)),
        modality=modality,
        encoding="utf-8-replace",
        text_hash72=hash72_digest(("text_projection_v1", text), width=24),
        byte_roundtrip_hash72=byte_roundtrip_hash,
        roundtrip_ok=roundtrip_ok,
        char_count=len(text),
        line_count=len(lines) if lines else (1 if text else 0),
        text_preview=text[:240].replace("\n", "\\n"),
    )
    return reconstruction, text


TOKEN_PATTERN = re.compile(r"Hash72|HHS|Lo\s*Shu|xyzw|u\^?72|u⁷²|Δe|Ψ|Θ₁₅|Theta15|Ω|[A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?|==|!=|<=|>=|->|=>|[=+\-*/^(){}\[\],.:;]|\S", re.UNICODE)


def classify_token(value: str) -> SemanticTokenKind:
    lower = value.lower().replace(" ", "")
    if lower in {"hhs", "hash72", "loshu", "xyzw", "u72", "u^72", "u⁷²", "δe", "δ", "ψ", "θ₁₅", "theta15", "ω"}:
        return SemanticTokenKind.HHS_TERM
    if value.startswith("H72") or "Hash72" in value:
        return SemanticTokenKind.HASH72
    if value.startswith("U+"):
        return SemanticTokenKind.UNICODE
    if re.fullmatch(r"\d+(?:\.\d+)?", value):
        return SemanticTokenKind.NUMBER
    if re.fullmatch(r"[=+\-*/^(){}\[\],.:;]|==|!=|<=|>=|->|=>", value):
        return SemanticTokenKind.OPERATOR
    if re.fullmatch(r"\W", value, re.UNICODE):
        return SemanticTokenKind.SYMBOL
    return SemanticTokenKind.WORD


def tokenize_text(text: str) -> List[SemanticToken]:
    tokens: List[SemanticToken] = []
    running_offset = 0
    for line_index, line in enumerate(text.splitlines() or ([text] if text else [])):
        line_start = running_offset
        line_hash = hash72_digest(("semantic_line_v1", line_index, line), width=18)
        line_symbol, line_codepoint = _symbol_from_hash(line_hash, line_index)
        tokens.append(
            SemanticToken(
                token_index=len(tokens),
                kind=SemanticTokenKind.LINE,
                value=line,
                line_index=line_index,
                char_start=line_start,
                char_end=line_start + len(line),
                token_hash72=line_hash,
                token_symbol=line_symbol,
                token_codepoint=line_codepoint,
            )
        )
        for match in TOKEN_PATTERN.finditer(line):
            value = match.group(0)
            kind = classify_token(value)
            start = line_start + match.start()
            end = line_start + match.end()
            token_hash = hash72_digest(("semantic_token_v1", len(tokens), kind.value, value, line_index, start, end), width=18)
            symbol, codepoint = _symbol_from_hash(token_hash, len(tokens))
            tokens.append(
                SemanticToken(
                    token_index=len(tokens),
                    kind=kind,
                    value=value,
                    line_index=line_index,
                    char_start=start,
                    char_end=end,
                    token_hash72=token_hash,
                    token_symbol=symbol,
                    token_codepoint=codepoint,
                )
            )
        running_offset += len(line) + 1
    return tokens


HHS_CATEGORY_MAP = {
    "hhs": "system",
    "hash72": "hashing",
    "loshu": "geometry",
    "lo shu": "geometry",
    "xyzw": "digital_dna",
    "u72": "phase",
    "u^72": "phase",
    "u⁷²": "phase",
    "δe": "ethical_invariant",
    "ψ": "semantic_invariant",
    "θ₁₅": "loshu_invariant",
    "theta15": "loshu_invariant",
    "ω": "closure_invariant",
}


def build_semantic_nodes(tokens: Sequence[SemanticToken]) -> List[SemanticNode]:
    grouped: Dict[tuple[str, str], List[str]] = {}
    for token in tokens:
        if token.kind in {SemanticTokenKind.HHS_TERM, SemanticTokenKind.HASH72, SemanticTokenKind.UNICODE}:
            key_label = token.value.lower().replace(" ", "")
            category = HHS_CATEGORY_MAP.get(key_label, token.kind.value.lower())
            grouped.setdefault((token.value, category), []).append(token.token_hash72)
    nodes: List[SemanticNode] = []
    for index, ((label, category), hashes) in enumerate(sorted(grouped.items(), key=lambda item: item[0][0].lower())):
        node_hash = hash72_digest(("semantic_node_v1", index, label, category, hashes), width=18)
        symbol, codepoint = _symbol_from_hash(node_hash, index + 4096)
        nodes.append(SemanticNode(index, label, category, hashes, node_hash, symbol, codepoint))
    return nodes


def build_semantic_relations(tokens: Sequence[SemanticToken], nodes: Sequence[SemanticNode]) -> List[SemanticRelation]:
    relations: List[SemanticRelation] = []

    def add(kind: SemanticRelationKind, source: str, target: str, evidence: str) -> None:
        r_hash = hash72_digest(("semantic_relation_v1", len(relations), kind.value, source, target, evidence), width=18)
        relations.append(SemanticRelation(len(relations), kind, source, target, evidence, r_hash))

    line_tokens = [t for t in tokens if t.kind == SemanticTokenKind.LINE]
    by_line: Dict[int, List[SemanticToken]] = {}
    for token in tokens:
        if token.kind != SemanticTokenKind.LINE:
            by_line.setdefault(token.line_index, []).append(token)

    for line in line_tokens:
        for token in by_line.get(line.line_index, []):
            add(SemanticRelationKind.CONTAINS, line.token_hash72, token.token_hash72, token.token_hash72)
        row = by_line.get(line.line_index, [])
        for left, right in zip(row, row[1:]):
            add(SemanticRelationKind.FOLLOWS, left.token_hash72, right.token_hash72, right.token_hash72)
        values = [t.value for t in row]
        hashes = [t.token_hash72 for t in row]
        for i, value in enumerate(values):
            if value in {"=", "==", ":=", "->", "=>"} and i > 0 and i + 1 < len(row):
                relation_kind = SemanticRelationKind.EQUALS if value in {"=", "==", ":="} else SemanticRelationKind.TRANSFORMS_TO
                add(relation_kind, hashes[i - 1], hashes[i + 1], hashes[i])
            if value == ":" and i > 0 and i + 1 < len(row):
                add(SemanticRelationKind.DEFINES, hashes[i - 1], hashes[i + 1], hashes[i])

    token_hashes_by_value: Dict[str, List[str]] = {}
    for token in tokens:
        token_hashes_by_value.setdefault(token.value, []).append(token.token_hash72)
    for node in nodes:
        for source_hash in node.source_token_hashes:
            add(SemanticRelationKind.REFERENCES, node.node_hash72, source_hash, source_hash)
    return relations


def invariant_gate_for_semantics(reconstruction: TextReconstruction, tokens: Sequence[SemanticToken], nodes: Sequence[SemanticNode], relations: Sequence[SemanticRelation]) -> EthicalInvariantReceipt:
    delta_e_zero = reconstruction.char_count >= 0 and len(tokens) > 0 and bool(reconstruction.text_hash72)
    psi_zero = reconstruction.modality in TEXTUAL_MODALITIES and all(token.char_start <= token.char_end for token in tokens)
    theta = theta15_true()
    omega_true = reconstruction.roundtrip_ok and bool(hash72_digest((reconstruction.to_dict(), [t.to_dict() for t in tokens], [n.to_dict() for n in nodes], [r.to_dict() for r in relations])))
    ok = delta_e_zero and psi_zero and theta and omega_true
    status = ModificationStatus.APPLIED if ok else ModificationStatus.QUARANTINED
    details = {
        "Δe=0": delta_e_zero,
        "Ψ=0": psi_zero,
        "Θ15=true": theta,
        "Ω=true": omega_true,
        "filename": reconstruction.filename,
        "token_count": len(tokens),
        "node_count": len(nodes),
        "relation_count": len(relations),
        "roundtrip_ok": reconstruction.roundtrip_ok,
    }
    receipt = hash72_digest(("text_semantic_invariant_gate_v1", reconstruction.to_dict(), details, status.value), width=24)
    return EthicalInvariantReceipt(delta_e_zero, psi_zero, theta, omega_true, status, details, receipt)


class TextSemanticDatabase:
    """JSON-backed semantic reconstruction database."""

    def __init__(self, path: str | Path = "demo_reports/hhs_text_semantic_db_v1.json") -> None:
        self.path = Path(path)

    def load(self) -> Dict[str, object]:
        if not self.path.exists():
            return {
                "module": "hhs_text_semantic_reconstruction_v1",
                "records": [],
                "file_index": {},
                "token_index": {},
                "node_index": {},
                "symbol_index": {},
            }
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data: Dict[str, object]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")

    def append_record(self, record: SemanticRecord) -> None:
        data = self.load()
        records = data.setdefault("records", [])
        file_index = data.setdefault("file_index", {})
        token_index = data.setdefault("token_index", {})
        node_index = data.setdefault("node_index", {})
        symbol_index = data.setdefault("symbol_index", {})
        records.append(record.to_dict())
        file_index[record.reconstruction.source_file_hash72] = record.semantic_hash72
        for token in record.tokens:
            token_index[token.token_hash72] = record.semantic_hash72
            symbol_index[token.token_symbol] = token.token_hash72
            symbol_index[token.token_codepoint] = token.token_hash72
        for node in record.nodes:
            node_index[node.node_hash72] = record.semantic_hash72
            node_index[node.label] = record.semantic_hash72
            symbol_index[node.node_symbol] = node.node_hash72
            symbol_index[node.node_codepoint] = node.node_hash72
        self.save(data)

    def search(self, key: str) -> List[Dict[str, object]]:
        data = self.load()
        hits = set()
        for name in ["file_index", "token_index", "node_index", "symbol_index"]:
            index = data.get(name, {})
            if isinstance(index, dict) and key in index:
                hits.add(str(index[key]))
        records = data.get("records", [])
        return [r for r in records if isinstance(r, dict) and r.get("semantic_hash72") in hits]


def reconstruct_record(file_record: Dict[str, object]) -> SemanticRecord:
    reconstruction, text = reconstruct_text_from_file_record(file_record)
    tokens = tokenize_text(text)
    nodes = build_semantic_nodes(tokens)
    relations = build_semantic_relations(tokens, nodes)
    gate = invariant_gate_for_semantics(reconstruction, tokens, nodes, relations)
    status = ReconstructionStatus.COMMITTED if gate.status == ModificationStatus.APPLIED else ReconstructionStatus.QUARANTINED
    quarantine = None if status == ReconstructionStatus.COMMITTED else hash72_digest(("semantic_quarantine", reconstruction.to_dict(), gate.to_dict()), width=24)
    semantic_hash = hash72_digest(("semantic_record_v1", reconstruction.to_dict(), [t.to_dict() for t in tokens], [n.to_dict() for n in nodes], [r.to_dict() for r in relations], gate.receipt_hash72, status.value), width=24)
    return SemanticRecord(reconstruction, tokens, nodes, relations, gate, status, semantic_hash, quarantine)


def register_semantics_in_symbol_cache(record: SemanticRecord, symbol_cache: GlobalSymbolCache) -> None:
    payload = record.to_dict()
    semantic_cache_record = symbol_cache.append_record(
        SymbolEntityType.MEMORY,
        f"semantic:{record.reconstruction.filename}",
        "memory_record",
        payload,
        [OrthogonalChain.MEMORY_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
        relation=AddressRelation(by_symbol=None, from_symbol=None, through_symbol=None, to_symbol=None),
    )
    source_symbol = semantic_cache_record.symbol_record.symbol
    for node in record.nodes:
        symbol_cache.append_record(
            SymbolEntityType.STATE,
            f"semantic_node:{node.label}",
            "memory_record",
            node.to_dict(),
            [OrthogonalChain.STATE_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
            relation=AddressRelation(by_symbol=source_symbol, from_symbol=source_symbol, through_symbol=None, to_symbol=node.node_symbol),
        )


def reconstruct_semantics_from_database(
    multimodal_database_path: str | Path = "demo_reports/hhs_multimodal_file_db_v1.json",
    semantic_database_path: str | Path = "demo_reports/hhs_text_semantic_db_v1.json",
    symbol_cache_path: str | Path = "demo_reports/hhs_global_symbol_cache_v1.json",
    ledger_path: str | Path = "demo_reports/hhs_text_semantic_ledger_v1.json",
) -> SemanticRunReceipt:
    file_db = MultimodalFileDatabase(multimodal_database_path)
    semantic_db = TextSemanticDatabase(semantic_database_path)
    symbol_cache = GlobalSymbolCache(symbol_cache_path)
    file_data = file_db.load()
    file_records = [r for r in file_data.get("files", []) if isinstance(r, dict)]
    semantic_records: List[SemanticRecord] = []
    for file_record in file_records:
        observation = file_record.get("observation", {})
        if not isinstance(observation, dict) or observation.get("modality") not in TEXTUAL_MODALITIES:
            continue
        semantic_record = reconstruct_record(file_record)
        semantic_db.append_record(semantic_record)
        register_semantics_in_symbol_cache(semantic_record, symbol_cache)
        semantic_records.append(semantic_record)

    ledger = MemoryLedger(ledger_path)
    commit = ledger.append_payloads("text_semantic_record_v1", [record.to_dict() for record in semantic_records])
    replay = replay_ledger(ledger_path)
    committed = sum(1 for record in semantic_records if record.status == ReconstructionStatus.COMMITTED)
    quarantined = len(semantic_records) - committed
    token_count = sum(len(record.tokens) for record in semantic_records)
    node_count = sum(len(record.nodes) for record in semantic_records)
    relation_count = sum(len(record.relations) for record in semantic_records)
    receipt = hash72_digest(("text_semantic_run_v1", [r.semantic_hash72 for r in semantic_records], commit.receipt_hash72, replay.receipt_hash72, committed, quarantined, token_count, node_count, relation_count), width=24)
    return SemanticRunReceipt(
        module="hhs_text_semantic_reconstruction_v1",
        semantic_database_path=str(semantic_database_path),
        files_seen=len(semantic_records),
        records_committed=committed,
        records_quarantined=quarantined,
        token_count=token_count,
        node_count=node_count,
        relation_count=relation_count,
        ledger_commit_receipt=commit.to_dict(),
        replay_receipt=replay.to_dict(),
        receipt_hash72=receipt,
    )


def ingest_and_reconstruct_text_files(
    file_paths: Sequence[str | Path],
    multimodal_database_path: str | Path = "demo_reports/hhs_multimodal_file_db_v1.json",
    semantic_database_path: str | Path = "demo_reports/hhs_text_semantic_db_v1.json",
    symbol_cache_path: str | Path = "demo_reports/hhs_global_symbol_cache_v1.json",
    multimodal_ledger_path: str | Path = "demo_reports/hhs_multimodal_file_ledger_v1.json",
    semantic_ledger_path: str | Path = "demo_reports/hhs_text_semantic_ledger_v1.json",
    chunk_size: int = 1024,
) -> Dict[str, object]:
    ingestion = ingest_files(
        file_paths,
        database_path=multimodal_database_path,
        symbol_cache_path=symbol_cache_path,
        ledger_path=multimodal_ledger_path,
        chunk_size=chunk_size,
    )
    semantic = reconstruct_semantics_from_database(
        multimodal_database_path=multimodal_database_path,
        semantic_database_path=semantic_database_path,
        symbol_cache_path=symbol_cache_path,
        ledger_path=semantic_ledger_path,
    )
    report_hash = hash72_digest(("ingest_and_reconstruct_text_files_v1", ingestion.receipt_hash72, semantic.receipt_hash72), width=24)
    return {
        "module": "hhs_text_semantic_reconstruction_v1",
        "ingestion_receipt": ingestion.to_dict(),
        "semantic_receipt": semantic.to_dict(),
        "report_hash72": report_hash,
    }


def demo() -> Dict[str, object]:
    demo_dir = Path("demo_reports")
    demo_dir.mkdir(parents=True, exist_ok=True)
    sample = demo_dir / "hhs_text_semantic_sample.md"
    sample.write_text(
        "# HHS Semantic Demo\n\nHash72 -> Lo Shu -> xyzw -> u⁷²\nΔe = 0\nΨ = 0\nΘ₁₅ = true\nΩ = true\n",
        encoding="utf-8",
    )
    return ingest_and_reconstruct_text_files(
        [sample],
        multimodal_database_path=demo_dir / "hhs_multimodal_file_db_semantic_demo_v1.json",
        semantic_database_path=demo_dir / "hhs_text_semantic_db_demo_v1.json",
        symbol_cache_path=demo_dir / "hhs_global_symbol_cache_semantic_demo_v1.json",
        multimodal_ledger_path=demo_dir / "hhs_multimodal_file_ledger_semantic_demo_v1.json",
        semantic_ledger_path=demo_dir / "hhs_text_semantic_ledger_demo_v1.json",
        chunk_size=32,
    )


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))
