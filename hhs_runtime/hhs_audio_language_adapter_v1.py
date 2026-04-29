"""
HHS Audio Language Adapter v1
=============================

Thin adapter over the existing multimodal file tokenizer/database layer.

This module does not create a new tokenizer, database, phoneme model, or storage
schema. It writes cross-modal artifacts to disk and passes them into the existing
hhs_multimodal_file_tokenizer_db_v1.ingest_files pipeline.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_multimodal_file_tokenizer_db_v1 import ingest_files


@dataclass(frozen=True)
class AudioLanguageIngestionReceipt:
    expression: str
    artifact_paths: List[str]
    multimodal_ingestion_receipt: Dict[str, Any]
    adapter_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")


def ingest_audio_language_artifacts(
    *,
    expression: str,
    display_items: List[Dict[str, Any]],
    audio_manifest: Dict[str, Any],
    audio_roundtrip_receipt: Dict[str, Any] | None = None,
    artifact_dir: str | Path = "demo_reports/audio_language_adapter",
    database_path: str | Path = "demo_reports/hhs_multimodal_file_db_v1.json",
    symbol_cache_path: str | Path = "demo_reports/hhs_global_symbol_cache_v1.json",
    ledger_path: str | Path = "demo_reports/hhs_multimodal_file_ledger_v1.json",
) -> AudioLanguageIngestionReceipt:
    root = Path(artifact_dir)
    root.mkdir(parents=True, exist_ok=True)

    expression_path = root / "expression.txt"
    items_path = root / "display_items.json"
    manifest_path = root / "audio_manifest.json"
    receipt_path = root / "audio_roundtrip_receipt.json"
    relation_path = root / "audio_language_relation_packet.json"

    expression_path.write_text(expression, encoding="utf-8")
    _write_json(items_path, {"items": display_items})
    _write_json(manifest_path, audio_manifest)
    _write_json(receipt_path, audio_roundtrip_receipt or {"status": "NO_ROUNDTRIP_RECEIPT"})

    relation_packet = {
        "module": "hhs_audio_language_adapter_v1",
        "expression_path": str(expression_path),
        "display_items_path": str(items_path),
        "audio_manifest_path": str(manifest_path),
        "audio_roundtrip_receipt_path": str(receipt_path),
        "expression": expression,
        "display_item_count": len(display_items),
        "audio_manifest_hash72": audio_manifest.get("manifest_hash72"),
        "audio_receipt_hash72": (audio_roundtrip_receipt or {}).get("receipt_hash72"),
    }
    relation_packet["relation_hash72"] = hash72_digest(("hhs_audio_language_relation_packet_v1", relation_packet), width=24)
    _write_json(relation_path, relation_packet)

    artifact_paths = [str(expression_path), str(items_path), str(manifest_path), str(receipt_path), str(relation_path)]
    ingestion_receipt = ingest_files(
        artifact_paths,
        database_path=database_path,
        symbol_cache_path=symbol_cache_path,
        ledger_path=ledger_path,
        chunk_size=1024,
    )

    adapter_hash = hash72_digest(("hhs_audio_language_adapter_receipt_v1", expression, artifact_paths, ingestion_receipt.to_dict()), width=24)
    return AudioLanguageIngestionReceipt(expression, artifact_paths, ingestion_receipt.to_dict(), adapter_hash)


def main() -> None:
    demo = ingest_audio_language_artifacts(
        expression="xy=-1/yx",
        display_items=[{"id": "0", "text": "xy", "kind": "ORDERED_PRODUCT", "phaseIndex": 0}],
        audio_manifest={"manifest_hash72": "DEMO"},
    )
    print(json.dumps(demo.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
