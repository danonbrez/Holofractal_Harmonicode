from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence
import json
import unicodedata

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass123_bounded_token_generalization_v1 import _canon

PASS_ID = "PASS_125"
SOURCE_SCHEMA = "HHS_CANONICAL_DOCUMENT_SOURCE_V1"
SEGMENT_SCHEMA = "HHS_CANONICAL_DOCUMENT_SEGMENT_V1"
MANIFEST_SCHEMA = "HHS_DOCUMENT_INGESTION_MANIFEST_V1"
REPLAY_SCHEMA = "HHS_DOCUMENT_INGESTION_REPLAY_V1"

REJECTION_CODES = {
    "REJECT_UNSUPPORTED_DOCUMENT_TYPE", "REJECT_DOCUMENT_TOO_LARGE",
    "REJECT_INVALID_UTF8", "REJECT_SOURCE_ROOT_MISMATCH",
    "REJECT_SEGMENT_ROOT_MISMATCH", "REJECT_MANIFEST_ROOT_MISMATCH",
    "REJECT_EMPTY_DOCUMENT", "REJECT_UNBOUNDED_INGESTION_REQUEST",
    "REJECT_DRIVE_METADATA_INCOMPLETE", "REJECT_DRIVE_EXPORT_MISMATCH",
    "REJECT_SOURCE_MUTATION", "REJECT_EXECUTION_AUTHORITY_ESCALATION",
    "REJECT_REPLAY_MISMATCH",
}

class Pass125Error(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(f"{code}: {message}")

@dataclass(frozen=True)
class DocumentIngestionBounds:
    max_bytes: int = 8 * 1024 * 1024
    max_segments: int = 4096
    max_segment_chars: int = 4096
    max_metadata_fields: int = 64

class CanonicalDocumentIngestionEngine:
    """Lossless, bounded text/Drive-export ingestion with Hash72 lineage and no authority escalation."""

    SUPPORTED_MIME = {
        "text/plain", "text/markdown", "application/json",
        "application/vnd.google-apps.document", "application/vnd.google-apps.spreadsheet",
        "application/vnd.google-apps.presentation",
    }

    def __init__(self, bounds: DocumentIngestionBounds | None = None):
        self.bounds = bounds or DocumentIngestionBounds()
        if min(self.bounds.max_bytes, self.bounds.max_segments, self.bounds.max_segment_chars, self.bounds.max_metadata_fields) <= 0:
            raise Pass125Error("REJECT_UNBOUNDED_INGESTION_REQUEST", "positive bounds required")

    def ingest_text_file(self, path: str | Path, *, mime_type: str | None = None) -> dict[str, Any]:
        p = Path(path).resolve()
        raw = p.read_bytes()
        stat_before = p.stat()
        source = self.ingest_bytes(raw, source_kind="LOCAL_TEXT_FILE", source_id=str(p),
                                   mime_type=mime_type or self._mime_from_suffix(p.suffix),
                                   metadata={"filename": p.name, "size_bytes": len(raw)})
        stat_after = p.stat()
        if stat_before.st_size != stat_after.st_size or stat_before.st_mtime_ns != stat_after.st_mtime_ns:
            raise Pass125Error("REJECT_SOURCE_MUTATION", str(p))
        return source

    def ingest_drive_export(self, *, file_id: str, name: str, mime_type: str,
                            modified_time: str, export_mime_type: str,
                            exported_bytes: bytes, export_sha256: str | None = None) -> dict[str, Any]:
        if not all([file_id, name, mime_type, modified_time, export_mime_type]):
            raise Pass125Error("REJECT_DRIVE_METADATA_INCOMPLETE", file_id or "missing file id")
        if mime_type not in self.SUPPORTED_MIME or export_mime_type not in {"text/plain", "text/markdown", "application/json"}:
            raise Pass125Error("REJECT_UNSUPPORTED_DOCUMENT_TYPE", f"{mime_type}->{export_mime_type}")
        actual = _hash("hhs_pass125_drive_export_bytes_v1", {"hex": exported_bytes.hex()})
        if export_sha256 is not None and export_sha256 != actual:
            raise Pass125Error("REJECT_DRIVE_EXPORT_MISMATCH", file_id)
        return self.ingest_bytes(
            exported_bytes, source_kind="GOOGLE_DRIVE_EXPORT", source_id=file_id,
            mime_type=export_mime_type,
            metadata={"drive_file_id": file_id, "drive_name": name, "drive_native_mime_type": mime_type,
                      "drive_modified_time": modified_time, "export_mime_type": export_mime_type,
                      "export_content_root_hash72": actual},
        )

    def ingest_bytes(self, raw: bytes, *, source_kind: str, source_id: str,
                     mime_type: str, metadata: Mapping[str, Any] | None = None) -> dict[str, Any]:
        if mime_type not in self.SUPPORTED_MIME and mime_type not in {"text/plain", "text/markdown", "application/json"}:
            raise Pass125Error("REJECT_UNSUPPORTED_DOCUMENT_TYPE", mime_type)
        if not raw:
            raise Pass125Error("REJECT_EMPTY_DOCUMENT", source_id)
        if len(raw) > self.bounds.max_bytes:
            raise Pass125Error("REJECT_DOCUMENT_TOO_LARGE", str(len(raw)))
        try:
            decoded = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise Pass125Error("REJECT_INVALID_UTF8", str(exc)) from exc
        canonical_text = unicodedata.normalize("NFC", decoded.replace("\r\n", "\n").replace("\r", "\n"))
        if not canonical_text:
            raise Pass125Error("REJECT_EMPTY_DOCUMENT", source_id)
        meta = dict(metadata or {})
        if len(meta) > self.bounds.max_metadata_fields:
            raise Pass125Error("REJECT_UNBOUNDED_INGESTION_REQUEST", "metadata fields")
        source = {
            "schema": SOURCE_SCHEMA, "pass_id": PASS_ID, "source_kind": source_kind,
            "source_id": source_id, "mime_type": mime_type, "byte_length": len(raw),
            "raw_content_root_hash72": _hash("hhs_pass125_raw_bytes_v1", {"hex": raw.hex()}),
            "canonical_text": canonical_text,
            "canonical_text_root_hash72": _hash("hhs_pass125_text_v1", canonical_text),
            "normalization": {"unicode": "NFC", "newline": "LF", "encoding": "UTF-8"},
            "metadata": _canon(meta), "execution_authority": False, "mutation_authority": False,
        }
        source["source_root_hash72"] = _hash("hhs_pass125_source_v1", source)
        return source

    def segment(self, source: Mapping[str, Any]) -> list[dict[str, Any]]:
        src = self._verify_source(source)
        text = src["canonical_text"]
        pieces: list[tuple[int, int, str]] = []
        start = 0
        while start < len(text):
            hard_end = min(len(text), start + self.bounds.max_segment_chars)
            end = hard_end
            if hard_end < len(text):
                newline = text.rfind("\n", start, hard_end)
                space = text.rfind(" ", start, hard_end)
                split = max(newline, space)
                if split > start:
                    end = split + 1
            pieces.append((start, end, text[start:end]))
            start = end
        if len(pieces) > self.bounds.max_segments:
            raise Pass125Error("REJECT_UNBOUNDED_INGESTION_REQUEST", "segment count")
        segments = []
        parent = src["source_root_hash72"]
        for idx, (a, b, content) in enumerate(pieces):
            obj = {"schema": SEGMENT_SCHEMA, "pass_id": PASS_ID, "source_root_hash72": src["source_root_hash72"],
                   "segment_index": idx, "start_char": a, "end_char": b, "content": content,
                   "content_root_hash72": _hash("hhs_pass125_segment_content_v1", content),
                   "parent_segment_or_source_root_hash72": parent,
                   "execution_authority": False, "mutation_authority": False}
            obj["segment_root_hash72"] = _hash("hhs_pass125_segment_v1", obj)
            parent = obj["segment_root_hash72"]
            segments.append(obj)
        return segments

    def build_manifest(self, source: Mapping[str, Any], segments: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        src = self._verify_source(source)
        verified = [self._verify_segment(x, src) for x in segments]
        reconstructed = "".join(x["content"] for x in verified)
        if reconstructed != src["canonical_text"]:
            raise Pass125Error("REJECT_SEGMENT_ROOT_MISMATCH", "lossless reconstruction failed")
        manifest = {"schema": MANIFEST_SCHEMA, "pass_id": PASS_ID,
                    "source_root_hash72": src["source_root_hash72"],
                    "segment_roots": [x["segment_root_hash72"] for x in verified],
                    "segment_count": len(verified), "lossless_reconstruction": True,
                    "knowledge_admission": "NOT_PERFORMED", "execution_authority": False,
                    "mutation_authority": False}
        manifest["manifest_root_hash72"] = _hash("hhs_pass125_manifest_v1", manifest)
        return manifest

    def replay(self, source: Mapping[str, Any], segments: Sequence[Mapping[str, Any]], manifest: Mapping[str, Any]) -> dict[str, Any]:
        rebuilt = self.build_manifest(source, segments)
        if manifest.get("manifest_root_hash72") != rebuilt["manifest_root_hash72"] or _canon(manifest) != _canon(rebuilt):
            raise Pass125Error("REJECT_REPLAY_MISMATCH", "manifest")
        receipt = {"schema": REPLAY_SCHEMA, "pass_id": PASS_ID,
                   "source_root_hash72": source["source_root_hash72"],
                   "manifest_root_hash72": rebuilt["manifest_root_hash72"],
                   "segment_count": rebuilt["segment_count"], "status": "LOSSLESS_REPLAY_VALIDATED"}
        receipt["replay_root_hash72"] = _hash("hhs_pass125_replay_v1", receipt)
        return receipt

    def assert_no_authority_escalation(self, *objects: Mapping[str, Any]) -> None:
        for obj in objects:
            if obj.get("execution_authority") is not False or obj.get("mutation_authority") is not False:
                raise Pass125Error("REJECT_EXECUTION_AUTHORITY_ESCALATION", obj.get("schema", "object"))

    def _verify_source(self, source: Mapping[str, Any]) -> dict[str, Any]:
        obj = dict(source); claimed = obj.pop("source_root_hash72", None)
        if claimed != _hash("hhs_pass125_source_v1", obj):
            raise Pass125Error("REJECT_SOURCE_ROOT_MISMATCH", str(source.get("source_id")))
        obj["source_root_hash72"] = claimed
        return obj

    def _verify_segment(self, segment: Mapping[str, Any], source: Mapping[str, Any]) -> dict[str, Any]:
        obj = dict(segment); claimed = obj.pop("segment_root_hash72", None)
        if obj.get("source_root_hash72") != source["source_root_hash72"] or claimed != _hash("hhs_pass125_segment_v1", obj):
            raise Pass125Error("REJECT_SEGMENT_ROOT_MISMATCH", str(obj.get("segment_index")))
        obj["segment_root_hash72"] = claimed
        return obj

    @staticmethod
    def _mime_from_suffix(suffix: str) -> str:
        return {".txt": "text/plain", ".md": "text/markdown", ".json": "application/json"}.get(suffix.lower(), "text/plain")


def pass125_self_test() -> dict[str, Any]:
    engine = CanonicalDocumentIngestionEngine(DocumentIngestionBounds(max_bytes=4096, max_segments=32, max_segment_chars=32))
    source = engine.ingest_bytes(b"alpha\r\nbeta\n", source_kind="SELF_TEST", source_id="pass125:self-test", mime_type="text/plain")
    segments = engine.segment(source)
    manifest = engine.build_manifest(source, segments)
    engine.assert_no_authority_escalation(source, *segments, manifest)
    replay = engine.replay(source, segments, manifest)
    return {"schema": "HHS_PASS125_SELF_TEST_V1", "status": "PASS",
            "source_root_hash72": source["source_root_hash72"],
            "manifest_root_hash72": manifest["manifest_root_hash72"],
            "replay_root_hash72": replay["replay_root_hash72"]}
