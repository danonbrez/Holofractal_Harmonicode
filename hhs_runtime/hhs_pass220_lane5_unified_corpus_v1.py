"""Pass 220 unified Lane 5 corpus graph.

Composes Pass 165 exact 5,184-bit multimodal ingestion with Pass 213 Hash216
content identities and Pass 219 language-model candidate projections. It does
not introduce another VM81 mutation authority.
"""
from __future__ import annotations

from base64 import b64decode
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Any, Iterator, Mapping, Protocol, Sequence

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import canonical_bytes, hash216
from hhs_runtime.hhs_pass219_approved_projector_execution_v1 import (
    ProjectionExecutionRequest,
    execute_projection,
)
from hhs_runtime.pass165.durability import DurableMultimodalLearningService
from hhs_runtime.pass165.ingestion import (
    MAX_SOURCE_BYTES as PASS165_MAX_SOURCE_BYTES,
    IngestionResult,
)

VERSION = "HHS-P220-LANE5-UNIFIED-CORPUS-V1"
SOURCE_MANIFEST_SCHEMA = "HHS_PASS220_LANE5_UNIFIED_CORPUS_SOURCE_MANIFEST_V1"
GRAPH_SCHEMA = "HHS_PASS220_LANE5_UNIFIED_VECTOR_KNOWLEDGE_GRAPH_V1"
CHECKPOINT_SCHEMA = "HHS_PASS220_LANE5_UNIFIED_HYDRATION_FRONTIER_V1"
SCOPE = "PASS220_LANE5_UNIFIED_CORPUS_HYDRATION"
RAW_CHUNK_BYTES = 8 * 1024 * 1024
MAX_PAGE_PACKET_BYTES = 8 * 1024 * 1024
PERSPECTIVE_ORDER = (
    "SEMANTIC_TEXT",
    "FORMAL_ALGEBRA",
    "SOURCE_CODE",
    "STRUCTURED_DATA",
    "NARRATIVE_TEXT",
    "VISUAL_PAGE",
)


class UnifiedCorpusError(RuntimeError):
    pass


def file_sha256(path: Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        while True:
            block = handle.read(4 * 1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def _sha(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _validate_sha(value: str, label: str) -> str:
    value = str(value).strip().lower()
    if re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise UnifiedCorpusError(f"PASS220_SHA256_INVALID:{label}")
    return value


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("wb") as handle:
        handle.write(canonical_bytes(value) + b"\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def _append(path: Path, record: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = dict(record)
    envelope = {"record": body, "record_sha256": _sha(canonical_bytes(body))}
    with path.open("ab") as handle:
        handle.write(canonical_bytes(envelope) + b"\n")
        handle.flush()
        os.fsync(handle.fileno())


def _read(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    raw = path.read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise UnifiedCorpusError(f"PASS220_INCOMPLETE_JOURNAL:{path.name}")
    records: list[dict[str, Any]] = []
    for number, line in enumerate(raw.splitlines(), start=1):
        try:
            envelope = json.loads(line)
        except json.JSONDecodeError as exc:
            raise UnifiedCorpusError(f"PASS220_JOURNAL_JSON:{path.name}:{number}") from exc
        record = envelope.get("record")
        if not isinstance(record, dict):
            raise UnifiedCorpusError(f"PASS220_JOURNAL_RECORD:{path.name}:{number}")
        if envelope.get("record_sha256") != _sha(canonical_bytes(record)):
            raise UnifiedCorpusError(f"PASS220_JOURNAL_DIGEST:{path.name}:{number}")
        records.append(record)
    return records


@dataclass(frozen=True)
class SourceManifestEntry:
    source_id: str
    filename: str
    sha256: str
    size_bytes: int
    pages: int

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "SourceManifestEntry":
        item = cls(
            source_id=str(value.get("source_id") or "").strip(),
            filename=str(value.get("filename") or "").strip(),
            sha256=_validate_sha(str(value.get("sha256") or ""), "source"),
            size_bytes=int(value.get("size_bytes") or 0),
            pages=int(value.get("pages") or 0),
        )
        if not item.source_id or not item.filename or item.size_bytes <= 0 or item.pages <= 0:
            raise UnifiedCorpusError("PASS220_SOURCE_MANIFEST_ENTRY_INVALID")
        return item


@dataclass(frozen=True)
class ExtractedPage:
    page_number: int
    text: str
    image_bytes: bytes | None = None


class PDFExtractor(Protocol):
    def page_count(self, path: Path) -> int: ...
    def iter_pages(self, path: Path, *, start_page: int = 1) -> Iterator[ExtractedPage]: ...


class PopplerPDFExtractor:
    """Text plus page-render adapter; no hidden OCR substitution."""

    def __init__(self, *, render_images: bool = True, dpi: int = 96) -> None:
        if dpi < 36 or dpi > 300:
            raise UnifiedCorpusError("PASS220_RENDER_DPI_BOUND")
        self.render_images = bool(render_images)
        self.dpi = int(dpi)

    @staticmethod
    def _run(command: Sequence[str]) -> bytes:
        try:
            completed = subprocess.run(
                list(command),
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError as exc:
            raise UnifiedCorpusError(f"PASS220_PDF_TOOL_REQUIRED:{command[0]}") from exc
        except subprocess.CalledProcessError as exc:
            detail = exc.stderr.decode("utf-8", errors="replace")[-1000:]
            raise UnifiedCorpusError(f"PASS220_PDF_TOOL_FAILED:{command[0]}:{detail}") from exc
        return completed.stdout

    def page_count(self, path: Path) -> int:
        info = self._run(["pdfinfo", str(path)]).decode("utf-8", errors="strict")
        match = re.search(r"(?m)^Pages:\s+(\d+)\s*$", info)
        if match is None:
            raise UnifiedCorpusError("PASS220_PDF_PAGE_COUNT_UNAVAILABLE")
        return int(match.group(1))

    def _texts(self, path: Path, count: int, *, start_page: int) -> list[str]:
        expected = count - start_page + 1
        raw = self._run([
            "pdftotext", "-layout", "-enc", "UTF-8",
            "-f", str(start_page), "-l", str(count), str(path), "-"
        ])
        pages = raw.decode("utf-8", errors="strict").split("\f")
        if pages and pages[-1] == "":
            pages.pop()
        if len(pages) < expected:
            pages.extend("" for _ in range(expected - len(pages)))
        if len(pages) > expected:
            if any(value.strip() for value in pages[expected:]):
                raise UnifiedCorpusError("PASS220_PDF_TEXT_PAGE_COUNT_DRIFT")
            pages = pages[:expected]
        return pages

    def _image(self, path: Path, page_number: int) -> bytes:
        with tempfile.TemporaryDirectory(prefix="hhs-p220-page-") as temporary:
            prefix = Path(temporary) / "page"
            self._run([
                "pdftoppm", "-f", str(page_number), "-l", str(page_number),
                "-singlefile", "-jpeg", "-r", str(self.dpi), str(path), str(prefix),
            ])
            target = prefix.with_suffix(".jpg")
            if not target.is_file():
                raise UnifiedCorpusError("PASS220_PAGE_RENDER_MISSING")
            raw = target.read_bytes()
        if not raw or len(raw) > PASS165_MAX_SOURCE_BYTES:
            raise UnifiedCorpusError(f"PASS220_PAGE_IMAGE_BOUND:{page_number}")
        return raw

    def iter_pages(self, path: Path, *, start_page: int = 1) -> Iterator[ExtractedPage]:
        count = self.page_count(path)
        if start_page < 1 or start_page > count + 1:
            raise UnifiedCorpusError("PASS220_START_PAGE_INVALID")
        if start_page == count + 1:
            return
        texts = self._texts(path, count, start_page=start_page)
        for number, text in enumerate(texts, start=start_page):
            image = self._image(path, number) if self.render_images else None
            yield ExtractedPage(number, text, image)


def _perspectives(text: str) -> dict[str, dict[str, Any]]:
    lines = text.splitlines(keepends=True)
    groups = {name: [] for name in PERSPECTIVE_ORDER if name != "VISUAL_PAGE"}
    algebra = re.compile(
        r"(?:[=<>±∑∏√∆ΔΩΦφπ]|\b(?:mod|sqrt|sin|cos|tan|log|exp)\b|\d\s*[/^*+\-]\s*\d)",
        re.IGNORECASE,
    )
    code = re.compile(
        r"(?:^\s*(?:def|class|import|from|function|const|let|var|if|for|while|return)\b|\x60{3}|[{};]\s*$)",
        re.IGNORECASE,
    )
    structured = re.compile(r"(?:^\s*[\[{]|[\]}]\s*$|\t|\|.*\||:\s*[^\s])")
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        groups["SEMANTIC_TEXT"].append(index)
        special = False
        if algebra.search(line):
            groups["FORMAL_ALGEBRA"].append(index)
            special = True
        if code.search(line):
            groups["SOURCE_CODE"].append(index)
            special = True
        if structured.search(line):
            groups["STRUCTURED_DATA"].append(index)
            special = True
        if not special and len(stripped.split()) >= 4:
            groups["NARRATIVE_TEXT"].append(index)
    return {
        name: {
            "line_indices": indices,
            "text": "".join(lines[index] for index in indices),
        }
        for name, indices in groups.items()
    }


def build_page_packet(source: SourceManifestEntry, page: ExtractedPage) -> dict[str, Any]:
    perspectives = _perspectives(page.text)
    perspectives["VISUAL_PAGE"] = {
        "present": page.image_bytes is not None,
        "image_sha256": _sha(page.image_bytes) if page.image_bytes is not None else None,
        "media_type": "IMAGE" if page.image_bytes is not None else None,
    }
    packet = {
        "schema": "HHS_PASS220_PARALLEL_PAGE_PERSPECTIVE_PACKET_V1",
        "source_id": source.source_id,
        "source_sha256": source.sha256,
        "page_number": page.page_number,
        "exact_extracted_text": page.text,
        "exact_extracted_text_sha256": _sha(page.text.encode("utf-8")),
        "perspective_order": list(PERSPECTIVE_ORDER),
        "perspectives": perspectives,
        "all_perspectives_share_one_source_identity": True,
    }
    if len(canonical_bytes(packet)) > MAX_PAGE_PACKET_BYTES:
        raise UnifiedCorpusError(f"PASS220_PAGE_PACKET_BOUND:{source.source_id}:{page.page_number}")
    return packet


class UnifiedGraph:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.nodes_path = self.root / "nodes.jsonl"
        self.edges_path = self.root / "edges.jsonl"
        self.completed_path = self.root / "completed.jsonl"
        self.frontier_path = self.root / "frontier.json"
        self.root.mkdir(parents=True, exist_ok=True)
        self.nodes = {str(row["node_id"]) for row in _read(self.nodes_path)}
        self.edges = {str(row["edge_id"]) for row in _read(self.edges_path)}
        self.completed = {str(row["work_key"]) for row in _read(self.completed_path)}

    def add_node(self, kind: str, body: Mapping[str, Any]) -> str:
        payload = {"kind": str(kind), "body": dict(body)}
        node_id = hash216("pass220-unified-kg-node", canonical_bytes(payload))
        if node_id not in self.nodes:
            _append(self.nodes_path, {"schema": GRAPH_SCHEMA, "node_id": node_id, **payload})
            self.nodes.add(node_id)
        return node_id

    def add_edge(self, source: str, target: str, relation: str) -> str:
        if source not in self.nodes or target not in self.nodes:
            raise UnifiedCorpusError("PASS220_GRAPH_EDGE_ENDPOINT_MISSING")
        body = {"source": source, "target": target, "relation": relation}
        edge_id = hash216("pass220-unified-kg-edge", canonical_bytes(body))
        if edge_id not in self.edges:
            _append(self.edges_path, {"schema": GRAPH_SCHEMA, "edge_id": edge_id, **body})
            self.edges.add(edge_id)
        return edge_id

    def complete(self, key: str, detail: Mapping[str, Any] | None = None) -> None:
        if key not in self.completed:
            _append(
                self.completed_path,
                {"schema": CHECKPOINT_SCHEMA, "work_key": key, "detail": dict(detail or {})},
            )
            self.completed.add(key)
        _atomic_json(
            self.frontier_path,
            {
                "schema": CHECKPOINT_SCHEMA,
                "version": VERSION,
                "completed_units": len(self.completed),
                "graph_nodes": len(self.nodes),
                "graph_edges": len(self.edges),
                "last_work_key": key,
            },
        )

    def root_hash216(self) -> str:
        return hash216(
            "pass220-unified-kg-root",
            canonical_bytes({
                "nodes": sorted(self.nodes),
                "edges": sorted(self.edges),
                "completed": sorted(self.completed),
            }),
        )


def admitted_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    receipt = result.get("receipt") or {}
    return {
        "admission_status": "VM81_ADMITTED",
        "projection_hash72": result.get("projection_hash72"),
        "ingestion_operation_hash216": receipt.get("ingestion_operation_hash216"),
        "receipt_hash72": receipt.get("receipt_hash72"),
        "incoming_vm81_hash72": receipt.get("incoming_vm81_hash72"),
        "outgoing_vm81_hash72": receipt.get("outgoing_vm81_hash72"),
        "candidate_only": False,
    }


def candidate_summary(result: IngestionResult) -> dict[str, Any]:
    return {
        "admission_status": "CANDIDATE",
        "projection_hash72": result.projection_hash72,
        "ingestion_operation_hash216": result.ingestion_operation_hash216,
        "ingestion_positions_hash216": list(result.ingestion_positions_hash216),
        "canonical_learning_commit_invoked": False,
        "candidate_only": True,
    }


def iter_chunks(path: Path) -> Iterator[tuple[int, int, bytes]]:
    offset = 0
    index = 0
    with Path(path).open("rb") as handle:
        while True:
            raw = handle.read(RAW_CHUNK_BYTES)
            if not raw:
                break
            yield index, offset, raw
            offset += len(raw)
            index += 1


class Lane5UnifiedCorpus:
    def __init__(
        self,
        state_dir: Path,
        *,
        extractor: PDFExtractor | None = None,
        external_projector_runtime: Any | None = None,
    ) -> None:
        self.state_dir = Path(state_dir)
        self.graph = UnifiedGraph(self.state_dir / "unified_graph")
        self.service = DurableMultimodalLearningService(self.state_dir / "pass165")
        self.extractor = extractor or PopplerPDFExtractor()
        self.external_projector_runtime = external_projector_runtime

    def _commit(self, raw: bytes, media: str, provenance: str) -> str:
        result = self.service.ingest_source(
            raw,
            declared_media_type=media,
            provenance=provenance,
            authorization_scope=SCOPE,
        )
        return self.graph.add_node(
            "ADMITTED_HYDRATION_UNIT",
            {"provenance": provenance, "media_type": media, "hydration": admitted_summary(result)},
        )

    def candidate(
        self,
        raw: bytes,
        media: str,
        provenance: str,
        kind: str,
        extra: Mapping[str, Any] | None = None,
    ) -> str:
        result = self.service.analyze(
            raw,
            declared_media_type=media,
            provenance=provenance,
            authorization_scope=SCOPE,
        )
        return self.graph.add_node(
            kind,
            {
                "provenance": provenance,
                "media_type": media,
                "hydration": candidate_summary(result),
                "extra": dict(extra or {}),
                "external_evidence_cannot_commit_vm81": True,
            },
        )

    def process_document(
        self,
        entry: SourceManifestEntry,
        path: Path,
        *,
        corpus_root: str,
    ) -> str:
        path = Path(path)
        if not path.is_file():
            raise UnifiedCorpusError(f"PASS220_SOURCE_FILE_MISSING:{entry.filename}")
        if path.stat().st_size != entry.size_bytes:
            raise UnifiedCorpusError(f"PASS220_SOURCE_SIZE_MISMATCH:{entry.source_id}")
        if file_sha256(path) != entry.sha256:
            raise UnifiedCorpusError(f"PASS220_SOURCE_SHA256_MISMATCH:{entry.source_id}")

        document = self.graph.add_node("DOCUMENT", {**asdict(entry), "verified_source": True})
        self.graph.add_edge(corpus_root, document, "CONTAINS_DOCUMENT")
        document_key = f"document-complete:{entry.sha256}:{entry.pages}"
        if document_key in self.graph.completed:
            return document

        for chunk_index, offset, raw in iter_chunks(path):
            key = f"pdf-binary:{entry.sha256}:{chunk_index}:{_sha(raw)}"
            if key not in self.graph.completed:
                node = self._commit(
                    raw,
                    "BINARY_OBJECT",
                    f"pass220:{entry.source_id}:binary:{chunk_index}:offset:{offset}",
                )
                self.graph.add_edge(document, node, "HAS_SOURCE_BINARY_CHUNK")
                self.graph.complete(key, {"source_id": entry.source_id, "chunk": chunk_index})

        observed = self.extractor.page_count(path)
        if observed != entry.pages:
            raise UnifiedCorpusError(f"PASS220_SOURCE_PAGE_COUNT_MISMATCH:{entry.source_id}")

        start_page = 1
        while (
            start_page <= entry.pages
            and f"page-complete:{entry.sha256}:{start_page}" in self.graph.completed
        ):
            start_page += 1
        if start_page > entry.pages:
            self.graph.complete(document_key, {"source_id": entry.source_id, "pages": entry.pages})
            return document

        seen = start_page - 1
        for page in self.extractor.iter_pages(path, start_page=start_page):
            seen += 1
            if page.page_number != seen:
                raise UnifiedCorpusError(f"PASS220_PAGE_ORDER_INVALID:{entry.source_id}")
            packet = build_page_packet(entry, page)
            packet_bytes = canonical_bytes(packet)
            packet_sha = _sha(packet_bytes)
            page_identity = self.graph.add_node(
                "PAGE_IDENTITY",
                {
                    "source_id": entry.source_id,
                    "source_sha256": entry.sha256,
                    "page_number": page.page_number,
                    "packet_sha256": packet_sha,
                    "perspective_order": list(PERSPECTIVE_ORDER),
                },
            )
            self.graph.add_edge(document, page_identity, "HAS_PAGE")
            key = f"page-packet:{entry.sha256}:{page.page_number}:{packet_sha}"
            if key not in self.graph.completed:
                node = self._commit(
                    packet_bytes,
                    "HHS_VECTOR_PACKET",
                    f"pass220:{entry.source_id}:page:{page.page_number}:parallel-perspectives",
                )
                self.graph.add_edge(page_identity, node, "HYDRATED_PARALLEL_PERSPECTIVES")
                self.graph.complete(key, {"source_id": entry.source_id, "page": page.page_number})

            if page.image_bytes is not None:
                image_sha = _sha(page.image_bytes)
                image_key = f"page-image:{entry.sha256}:{page.page_number}:{image_sha}"
                if image_key not in self.graph.completed:
                    image_node = self._commit(
                        page.image_bytes,
                        "IMAGE",
                        f"pass220:{entry.source_id}:page:{page.page_number}:visual:{image_sha}",
                    )
                    self.graph.add_edge(page_identity, image_node, "HAS_VISUAL_PAGE_PERSPECTIVE")
                    self.graph.complete(image_key, {"source_id": entry.source_id, "page": page.page_number})

            if page.text.strip() and self.external_projector_runtime is not None:
                text_bytes = page.text.encode("utf-8")
                projector_key = f"language-vector:{entry.sha256}:{page.page_number}:{_sha(text_bytes)}"
                if projector_key not in self.graph.completed:
                    projection = execute_projection(
                        ProjectionExecutionRequest(
                            profile_id="MULTILINGUAL_MPNET_TEXT_V1",
                            source_bytes=text_bytes,
                            source_sha256=_sha(text_bytes),
                            source_language="und",
                            source_modality="TEXT",
                            pivot_text="HHS unified corpus semantic knowledge graph",
                            pivot_language="en",
                            semantic_labels=("PASS220_UNIFIED_CORPUS",),
                            translation_chain=(),
                        ),
                        self.external_projector_runtime,
                    )
                    vector_bytes = b64decode(projection["vector_identity_b64"], validate=True)
                    vector_node = self.candidate(
                        vector_bytes,
                        "BINARY_OBJECT",
                        f"pass220:language-projector:{entry.source_id}:page:{page.page_number}",
                        "LANGUAGE_MODEL_VECTOR_CANDIDATE",
                        {
                            "model_repository": projection["model_repository"],
                            "projector_profile_id": projection["projector_profile_id"],
                            "execution_record_sha256": projection["execution_record_sha256"],
                            "candidate_only": True,
                        },
                    )
                    self.graph.add_edge(page_identity, vector_node, "HAS_LANGUAGE_MODEL_VECTOR")
                    self.graph.complete(projector_key, {"source_id": entry.source_id, "page": page.page_number})

            self.graph.complete(
                f"page-complete:{entry.sha256}:{page.page_number}",
                {"source_id": entry.source_id, "page": page.page_number},
            )

        if seen != entry.pages:
            raise UnifiedCorpusError(f"PASS220_EXTRACTED_PAGE_COUNT_MISMATCH:{entry.source_id}")
        self.graph.complete(document_key, {"source_id": entry.source_id, "pages": entry.pages})
        return document

    def run_manifest(self, manifest_path: Path, source_root: Path) -> dict[str, Any]:
        manifest = json.loads(Path(manifest_path).read_text("utf-8"))
        if not isinstance(manifest, dict) or manifest.get("schema") != SOURCE_MANIFEST_SCHEMA:
            raise UnifiedCorpusError("PASS220_SOURCE_MANIFEST_SCHEMA_INVALID")
        raw_sources = manifest.get("sources")
        if not isinstance(raw_sources, list) or not raw_sources:
            raise UnifiedCorpusError("PASS220_SOURCE_MANIFEST_EMPTY")
        sources = [SourceManifestEntry.from_mapping(item) for item in raw_sources]
        if len({item.source_id for item in sources}) != len(sources):
            raise UnifiedCorpusError("PASS220_SOURCE_ID_DUPLICATE")

        corpus_root = self.graph.add_node(
            "UNIFIED_CORPUS_ROOT",
            {
                "manifest_hash216": hash216("pass220-source-manifest", canonical_bytes(manifest)),
                "one_vector_store_knowledge_graph": True,
                "parallel_modality_perspectives": True,
            },
        )
        documents = [
            self.process_document(item, Path(source_root) / item.filename, corpus_root=corpus_root)
            for item in sources
        ]
        receipt = {
            "schema": "HHS_PASS220_LANE5_UNIFIED_CORPUS_RECEIPT_V1",
            "version": VERSION,
            "source_count": len(sources),
            "declared_page_count": sum(item.pages for item in sources),
            "declared_source_bytes": sum(item.size_bytes for item in sources),
            "document_nodes": documents,
            "corpus_root_node": corpus_root,
            "graph_root_hash216": self.graph.root_hash216(),
            "graph_nodes": len(self.graph.nodes),
            "graph_edges": len(self.graph.edges),
            "completed_units": len(self.graph.completed),
            "pass165_status": self.service.status(),
            "one_vector_store_knowledge_graph": True,
            "canonical_authority_widened": False,
        }
        receipt["receipt_hash216"] = hash216(
            "pass220-unified-corpus-receipt",
            canonical_bytes(receipt),
        )
        _atomic_json(self.state_dir / "corpus.receipt.json", receipt)
        return receipt
