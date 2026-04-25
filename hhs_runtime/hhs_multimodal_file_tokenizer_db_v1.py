"""
HHS Multimodal File Upload Tokenizer + Database Storage v1
==========================================================

Real-world sensor/interface layer for file uploads.

This module ingests local files as raw observations, classifies modality,
creates deterministic multimodal tokens, assigns Unicode/Hash72 symbols, stores
records in a JSON database cache, and appends commit/quarantine receipts to the
ledger.

Pipeline:

    file bytes
    -> file fingerprint
    -> modality classifier
    -> chunk tokenizer
    -> Hash72 token records
    -> Unicode symbol assignment
    -> invariant gate Δe/Ψ/Θ15/Ω
    -> database commit or quarantine
    -> ledger append + replay

No OCR, image recognition, audio transcription, or lossy semantic extraction is
performed in v1.  This is the deterministic storage/tokenization substrate that
higher multimodal adapters can attach to.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable, List, Sequence
import base64
import json
import mimetypes

from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3, hash72_digest
from hhs_runtime.hhs_memory_ledger_replay_v1 import MemoryLedger, replay_ledger
from hhs_runtime.hhs_recursive_symbol_kernel_v1 import (
    AddressRelation,
    GlobalSymbolCache,
    OrthogonalChain,
    RecursiveKernelStatus,
    SymbolEntityType,
    chains_for_entity,
)
from hhs_runtime.hhs_self_modifying_agents_v1 import EthicalInvariantReceipt, ModificationStatus


class Modality(str, Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    PDF = "PDF"
    ARCHIVE = "ARCHIVE"
    BINARY = "BINARY"
    JSON = "JSON"
    CSV = "CSV"
    PYTHON = "PYTHON"
    MARKDOWN = "MARKDOWN"


class StorageStatus(str, Enum):
    COMMITTED = "COMMITTED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class FileObservation:
    """Raw file observation metadata."""

    path: str
    filename: str
    suffix: str
    size_bytes: int
    mime_type: str
    modality: Modality
    byte_hash72: str
    head_b64: str

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["modality"] = self.modality.value
        return data


@dataclass(frozen=True)
class MultimodalToken:
    """Deterministic chunk/token produced from file bytes."""

    token_index: int
    modality: Modality
    byte_start: int
    byte_end: int
    token_hash72: str
    token_symbol: str
    token_codepoint: str
    preview: str

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["modality"] = self.modality.value
        return data


@dataclass(frozen=True)
class FileStorageRecord:
    """Database record for one ingested file."""

    observation: FileObservation
    file_symbol: str
    file_codepoint: str
    file_symbol_hash72: str
    tokens: List[MultimodalToken]
    invariant_gate: EthicalInvariantReceipt
    status: StorageStatus
    database_hash72: str
    quarantine_hash72: str | None

    def to_dict(self) -> Dict[str, object]:
        return {
            "observation": self.observation.to_dict(),
            "file_symbol": self.file_symbol,
            "file_codepoint": self.file_codepoint,
            "file_symbol_hash72": self.file_symbol_hash72,
            "tokens": [token.to_dict() for token in self.tokens],
            "invariant_gate": self.invariant_gate.to_dict(),
            "status": self.status.value,
            "database_hash72": self.database_hash72,
            "quarantine_hash72": self.quarantine_hash72,
        }


@dataclass(frozen=True)
class IngestionRunReceipt:
    """Receipt for a multimodal ingestion run."""

    module: str
    database_path: str
    files_seen: int
    files_committed: int
    files_quarantined: int
    token_count: int
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


def classify_modality(path: Path, mime_type: str) -> Modality:
    suffix = path.suffix.lower()
    if suffix == ".pdf" or mime_type == "application/pdf":
        return Modality.PDF
    if suffix in {".md", ".markdown"}:
        return Modality.MARKDOWN
    if suffix == ".py":
        return Modality.PYTHON
    if suffix == ".json" or mime_type == "application/json":
        return Modality.JSON
    if suffix in {".csv", ".tsv"}:
        return Modality.CSV
    if mime_type.startswith("text/") or suffix in {".txt", ".log", ".toml", ".yaml", ".yml"}:
        return Modality.TEXT
    if mime_type.startswith("image/") or suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".svg"}:
        return Modality.IMAGE
    if mime_type.startswith("audio/") or suffix in {".mp3", ".wav", ".flac", ".m4a", ".ogg"}:
        return Modality.AUDIO
    if mime_type.startswith("video/") or suffix in {".mp4", ".mov", ".webm", ".mkv"}:
        return Modality.VIDEO
    if suffix in {".zip", ".tar", ".gz", ".tgz", ".7z"}:
        return Modality.ARCHIVE
    return Modality.BINARY


def observe_file(file_path: str | Path) -> tuple[FileObservation, bytes]:
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(str(path))
    data = path.read_bytes()
    mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    modality = classify_modality(path, mime_type)
    byte_hash = hash72_digest(("file_bytes_v1", len(data), base64.b64encode(data).decode("ascii")), width=24)
    head = base64.b64encode(data[:96]).decode("ascii")
    obs = FileObservation(
        path=str(path),
        filename=path.name,
        suffix=path.suffix.lower(),
        size_bytes=len(data),
        mime_type=mime_type,
        modality=modality,
        byte_hash72=byte_hash,
        head_b64=head,
    )
    return obs, data


def _text_preview(chunk: bytes, modality: Modality) -> str:
    if modality in {Modality.TEXT, Modality.MARKDOWN, Modality.JSON, Modality.CSV, Modality.PYTHON}:
        text = chunk.decode("utf-8", errors="replace")
        return text[:120].replace("\n", "\\n")
    return base64.b64encode(chunk[:48]).decode("ascii")


def _symbol_from_hash(token_hash72: str, offset: int = 0) -> tuple[str, str]:
    # Use a separate PUA band from recursive symbol kernel but deterministic.
    base = 0xF000
    span = 0x0F00
    acc = offset
    for ch in token_hash72:
        acc = (acc * 137 + ord(ch)) % span
    cp = base + acc
    return chr(cp), f"U+{cp:04X}"


def tokenize_bytes(observation: FileObservation, data: bytes, chunk_size: int = 1024) -> List[MultimodalToken]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    tokens: List[MultimodalToken] = []
    if not data:
        token_hash = hash72_digest(("empty_file_token_v1", observation.byte_hash72), width=18)
        symbol, codepoint = _symbol_from_hash(token_hash, 0)
        return [
            MultimodalToken(0, observation.modality, 0, 0, token_hash, symbol, codepoint, "")
        ]
    for index, start in enumerate(range(0, len(data), chunk_size)):
        end = min(start + chunk_size, len(data))
        chunk = data[start:end]
        chunk_b64 = base64.b64encode(chunk).decode("ascii")
        token_hash = hash72_digest(("multimodal_token_v1", observation.byte_hash72, index, start, end, chunk_b64), width=18)
        symbol, codepoint = _symbol_from_hash(token_hash, index)
        tokens.append(
            MultimodalToken(
                token_index=index,
                modality=observation.modality,
                byte_start=start,
                byte_end=end,
                token_hash72=token_hash,
                token_symbol=symbol,
                token_codepoint=codepoint,
                preview=_text_preview(chunk, observation.modality),
            )
        )
    return tokens


def invariant_gate_for_file(observation: FileObservation, tokens: Sequence[MultimodalToken]) -> EthicalInvariantReceipt:
    delta_e_zero = observation.size_bytes >= 0 and bool(observation.byte_hash72) and len(tokens) > 0
    psi_zero = all(token.modality == observation.modality for token in tokens)
    theta = theta15_true()
    omega_true = all(token.byte_start <= token.byte_end for token in tokens) and bool(hash72_digest((observation.to_dict(), [t.to_dict() for t in tokens])))
    ok = delta_e_zero and psi_zero and theta and omega_true
    status = ModificationStatus.APPLIED if ok else ModificationStatus.QUARANTINED
    details = {
        "Δe=0": delta_e_zero,
        "Ψ=0": psi_zero,
        "Θ15=true": theta,
        "Ω=true": omega_true,
        "filename": observation.filename,
        "modality": observation.modality.value,
        "token_count": len(tokens),
    }
    receipt = hash72_digest(("multimodal_file_invariant_gate_v1", observation.to_dict(), [t.to_dict() for t in tokens], details, status.value))
    return EthicalInvariantReceipt(delta_e_zero, psi_zero, theta, omega_true, status, details, receipt)


class MultimodalFileDatabase:
    """JSON-backed multimodal token database."""

    def __init__(self, path: str | Path = "demo_reports/hhs_multimodal_file_db_v1.json") -> None:
        self.path = Path(path)

    def load(self) -> Dict[str, object]:
        if not self.path.exists():
            return {
                "module": "hhs_multimodal_file_tokenizer_db_v1",
                "files": [],
                "file_index": {},
                "token_index": {},
                "symbol_index": {},
                "modality_index": {},
            }
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data: Dict[str, object]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")

    def append_record(self, record: FileStorageRecord) -> None:
        data = self.load()
        files = data.setdefault("files", [])
        file_index = data.setdefault("file_index", {})
        token_index = data.setdefault("token_index", {})
        symbol_index = data.setdefault("symbol_index", {})
        modality_index = data.setdefault("modality_index", {})
        files.append(record.to_dict())
        file_index[record.observation.byte_hash72] = record.database_hash72
        symbol_index[record.file_symbol] = record.database_hash72
        symbol_index[record.file_codepoint] = record.database_hash72
        modality_index.setdefault(record.observation.modality.value, [])
        modality_index[record.observation.modality.value].append(record.database_hash72)
        for token in record.tokens:
            token_index[token.token_hash72] = record.database_hash72
            symbol_index[token.token_symbol] = token.token_hash72
            symbol_index[token.token_codepoint] = token.token_hash72
        self.save(data)

    def search(self, key: str) -> List[Dict[str, object]]:
        data = self.load()
        hits = set()
        for index_name in ["file_index", "token_index", "symbol_index"]:
            index = data.get(index_name, {})
            if isinstance(index, dict) and key in index:
                hits.add(str(index[key]))
        modality_index = data.get("modality_index", {})
        if isinstance(modality_index, dict) and key in modality_index:
            hits.update(str(x) for x in modality_index[key])
        files = data.get("files", [])
        out = []
        for record in files:
            if not isinstance(record, dict):
                continue
            if record.get("database_hash72") in hits or any(t.get("token_hash72") in hits for t in record.get("tokens", []) if isinstance(t, dict)):
                out.append(record)
        return out


def store_file(
    file_path: str | Path,
    db: MultimodalFileDatabase,
    symbol_cache: GlobalSymbolCache | None = None,
    chunk_size: int = 1024,
) -> FileStorageRecord:
    observation, data = observe_file(file_path)
    tokens = tokenize_bytes(observation, data, chunk_size=chunk_size)
    gate = invariant_gate_for_file(observation, tokens)
    status = StorageStatus.COMMITTED if gate.status == ModificationStatus.APPLIED else StorageStatus.QUARANTINED
    file_symbol_hash = hash72_digest(("file_symbol_v1", observation.to_dict(), gate.receipt_hash72), width=18)
    file_symbol, file_codepoint = _symbol_from_hash(file_symbol_hash, 777)
    quarantine = None if status == StorageStatus.COMMITTED else hash72_digest(("file_quarantine", observation.to_dict(), gate.to_dict()))
    database_hash = hash72_digest(("file_storage_record_v1", observation.to_dict(), [t.to_dict() for t in tokens], file_symbol, gate.receipt_hash72, status.value, quarantine), width=24)
    record = FileStorageRecord(observation, file_symbol, file_codepoint, file_symbol_hash, tokens, gate, status, database_hash, quarantine)
    db.append_record(record)

    if symbol_cache is not None:
        payload = record.to_dict()
        symbol_cache.append_record(
            SymbolEntityType.MEMORY,
            f"file:{observation.filename}",
            "memory_record",
            payload,
            [OrthogonalChain.MEMORY_CHAIN, OrthogonalChain.SYMBOL_CHAIN],
            relation=AddressRelation(by_symbol=file_symbol, from_symbol=file_symbol, through_symbol=None, to_symbol=None),
        )
    return record


def ingest_files(
    file_paths: Sequence[str | Path],
    database_path: str | Path = "demo_reports/hhs_multimodal_file_db_v1.json",
    symbol_cache_path: str | Path = "demo_reports/hhs_global_symbol_cache_v1.json",
    ledger_path: str | Path = "demo_reports/hhs_multimodal_file_ledger_v1.json",
    chunk_size: int = 1024,
) -> IngestionRunReceipt:
    db = MultimodalFileDatabase(database_path)
    cache = GlobalSymbolCache(symbol_cache_path)
    records: List[FileStorageRecord] = []
    for path in file_paths:
        records.append(store_file(path, db, symbol_cache=cache, chunk_size=chunk_size))

    ledger = MemoryLedger(ledger_path)
    commit = ledger.append_payloads("multimodal_file_storage_record_v1", [r.to_dict() for r in records])
    replay = replay_ledger(ledger_path)
    committed = sum(1 for r in records if r.status == StorageStatus.COMMITTED)
    quarantined = len(records) - committed
    token_count = sum(len(r.tokens) for r in records)
    receipt = hash72_digest(("multimodal_ingestion_run_v1", [r.database_hash72 for r in records], commit.receipt_hash72, replay.receipt_hash72, committed, quarantined, token_count), width=24)
    return IngestionRunReceipt(
        module="hhs_multimodal_file_tokenizer_db_v1",
        database_path=str(database_path),
        files_seen=len(records),
        files_committed=committed,
        files_quarantined=quarantined,
        token_count=token_count,
        ledger_commit_receipt=commit.to_dict(),
        replay_receipt=replay.to_dict(),
        receipt_hash72=receipt,
    )


def demo() -> Dict[str, object]:
    demo_dir = Path("demo_reports")
    demo_dir.mkdir(parents=True, exist_ok=True)
    sample = demo_dir / "hhs_multimodal_sample.txt"
    sample.write_text("HHS multimodal upload tokenizer demo\n179971 -> u72 -> Lo Shu -> xyzw -> Hash72\n", encoding="utf-8")
    receipt = ingest_files(
        [sample],
        database_path=demo_dir / "hhs_multimodal_file_db_demo_v1.json",
        symbol_cache_path=demo_dir / "hhs_global_symbol_cache_file_demo_v1.json",
        ledger_path=demo_dir / "hhs_multimodal_file_ledger_demo_v1.json",
        chunk_size=32,
    )
    return receipt.to_dict()


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))
