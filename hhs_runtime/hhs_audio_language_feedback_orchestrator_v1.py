"""
HHS Audio Language Feedback Orchestrator v1
==========================================

Thin caller over existing modules:
- hhs_audio_language_adapter_v1.ingest_audio_language_artifacts
- harmonicode_verbatim_semantic_database_v1.HarmonicodeVerbatimSemanticDatabaseV1
- hhs_linguistic_operator_training_loop_v1.run_linguistic_training_loop

No new tokenizer/database/training model is defined here. Pass219 I179 adds a
receipt table inside the same auxiliary semantic SQLite database so public audio
receipts can be replayed without re-running training or persistence. This table
is not VM81/Hash72/Hash216 canonical authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping
import json
import sqlite3

from harmonicode_verbatim_semantic_database_v1 import (
    HarmonicodeVerbatimSemanticDatabaseV1,
    VerbatimStateRecord,
    TransitionStep,
    TransitionTrace,
    CrossModalityLink,
    hash72_like,
)
from hhs_runtime.hhs_audio_language_adapter_v1 import ingest_audio_language_artifacts
from hhs_runtime.hhs_linguistic_operator_training_loop_v1 import run_linguistic_training_loop
from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


DEFAULT_SEMANTIC_DB_PATH = "demo_reports/harmonicode_verbatim_semantic_audio_language_v1.sqlite"
AUDIO_RECEIPT_TABLE = "audio_language_feedback_receipts_i179"
AUDIO_RECEIPT_SCHEMA = "HHS_AUDIO_LANGUAGE_FEEDBACK_RECEIPT_STORE_I179_V1"
AUDIO_REPLAY_SCHEMA = "HHS_AUDIO_LANGUAGE_FEEDBACK_REPLAY_I179_V1"


class AudioLanguageFeedbackReplayError(RuntimeError):
    pass


@dataclass(frozen=True)
class AudioLanguageFeedbackReceipt:
    adapter_receipt: Dict[str, Any]
    linguistic_training_receipt: Dict[str, Any]
    semantic_db_summary: Dict[str, Any]
    stored_state_hashes: List[str]
    cross_links: List[Dict[str, Any]]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _state_record(modality: str, name: str, content: str, tokens: List[str], metadata: Dict[str, Any]) -> VerbatimStateRecord:
    state_hash = hash72_like({"modality": modality, "name": name, "content": content, "tokens": tokens, "metadata": metadata})
    projection_hash = hash72_like({"projection": modality, "tokens": tokens})
    witness_hash = hash72_like({"witness": modality, "state_hash": state_hash})
    return VerbatimStateRecord(
        state_hash72=state_hash,
        modality=modality,
        source_name=name,
        verbatim_content=content,
        token_sequence=tokens,
        projection_hash72=projection_hash,
        witness_hash72=witness_hash,
        invariant_report={"round_trip": True, "adapter": "hhs_audio_language_feedback_orchestrator_v1"},
        metadata=metadata,
    )


def _ensure_receipt_table(db: HarmonicodeVerbatimSemanticDatabaseV1) -> None:
    db.conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {AUDIO_RECEIPT_TABLE} (
            receipt_hash72 TEXT PRIMARY KEY,
            receipt_json TEXT NOT NULL,
            security_binding_json TEXT NOT NULL,
            trace_hash72 TEXT NOT NULL,
            stored_state_hashes_json TEXT NOT NULL,
            cross_link_hashes_json TEXT NOT NULL,
            created_at INTEGER NOT NULL DEFAULT (unixepoch())
        )
        """
    )
    db.conn.commit()


def _store_receipt(
    db: HarmonicodeVerbatimSemanticDatabaseV1,
    *,
    receipt: AudioLanguageFeedbackReceipt,
    security_binding: Mapping[str, Any] | None,
    trace_hash72: str,
) -> None:
    _ensure_receipt_table(db)
    binding = dict(security_binding or {})
    cross_link_hashes = [
        str(item.get("link_hash72"))
        for item in receipt.cross_links
        if isinstance(item, Mapping) and item.get("link_hash72")
    ]
    db.conn.execute(
        f"""
        INSERT OR REPLACE INTO {AUDIO_RECEIPT_TABLE} (
            receipt_hash72,
            receipt_json,
            security_binding_json,
            trace_hash72,
            stored_state_hashes_json,
            cross_link_hashes_json
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            receipt.receipt_hash72,
            _canonical_json(receipt.to_dict()),
            _canonical_json(binding),
            trace_hash72,
            _canonical_json(receipt.stored_state_hashes),
            _canonical_json(cross_link_hashes),
        ),
    )
    db.conn.commit()


def _receipt_hash(
    *,
    adapter_receipt: Mapping[str, Any],
    training_receipt_hash72: Any,
    summary: Mapping[str, Any],
    stored_state_hashes: List[str],
    links: List[Dict[str, Any]],
    security_binding: Mapping[str, Any] | None,
) -> str:
    legacy_components: List[Any] = [
        "hhs_audio_language_feedback_receipt_v1",
        dict(adapter_receipt),
        training_receipt_hash72,
        dict(summary),
        list(stored_state_hashes),
        list(links),
    ]
    if security_binding is None:
        # Preserve the inherited internal receipt identity when no I179 public
        # security binding participates.
        return hash72_digest(tuple(legacy_components), width=24)

    # I179 receipts must survive JSON persistence/reload exactly. The legacy
    # local digest consumes str(object), which is insertion-order-sensitive for
    # mappings. Canonical JSON removes that incidental ordering from the public
    # replay receipt preimage without introducing a new Hash72 authority.
    canonical_preimage = {
        "schema": "HHS_AUDIO_LANGUAGE_FEEDBACK_RECEIPT_HASH_I179_V1",
        "adapter_receipt": dict(adapter_receipt),
        "training_receipt_hash72": training_receipt_hash72,
        "semantic_db_summary": dict(summary),
        "stored_state_hashes": list(stored_state_hashes),
        "cross_links": list(links),
        "security_binding": dict(security_binding),
    }
    return hash72_digest(
        (
            "hhs_audio_language_feedback_receipt_i179_v1",
            _canonical_json(canonical_preimage),
        ),
        width=24,
    )


def run_audio_language_feedback_cycle(
    *,
    expression: str,
    display_items: List[Dict[str, Any]],
    audio_manifest: Dict[str, Any],
    audio_roundtrip_receipt: Dict[str, Any] | None = None,
    semantic_db_path: str | Path = DEFAULT_SEMANTIC_DB_PATH,
    transport_security_binding: Mapping[str, Any] | None = None,
) -> AudioLanguageFeedbackReceipt:
    adapter_receipt = ingest_audio_language_artifacts(
        expression=expression,
        display_items=display_items,
        audio_manifest=audio_manifest,
        audio_roundtrip_receipt=audio_roundtrip_receipt,
    ).to_dict()

    training = run_linguistic_training_loop(
        expression,
        seed=str(audio_manifest.get("manifest_hash72") or "HHS_AUDIO_LANGUAGE_FEEDBACK"),
        feedback_records=adapter_receipt.get("multimodal_ingestion_receipt", {}).get("replay_receipt", {}).get("blocks", []),
        max_steps=9,
    ).to_dict()

    db = HarmonicodeVerbatimSemanticDatabaseV1(semantic_db_path)
    stored: List[str] = []

    expression_tokens = [str(item.get("text", "")) for item in display_items]
    expression_record = _state_record("symbolic_expression", "calculator_expression", expression, expression_tokens, {"display_items": display_items})
    audio_tokens = [str(item.get("item_hash72", item.get("text", ""))) for item in audio_manifest.get("items", [])]
    audio_record = _state_record("audio_phase_manifest", "audio_phase_transport", json.dumps(audio_manifest, sort_keys=True, ensure_ascii=False), audio_tokens, {"manifest_hash72": audio_manifest.get("manifest_hash72")})
    training_tokens = [str(step.get("step_hash72", "")) for step in training.get("steps", [])]
    training_record = _state_record("linguistic_training", "language_operator_feedback", json.dumps(training, sort_keys=True, ensure_ascii=False), training_tokens, {"receipt_hash72": training.get("receipt_hash72")})

    for record in [expression_record, audio_record, training_record]:
        stored.append(db.store_state_record(record))

    trace = TransitionTrace(
        trace_hash72=hash72_like({"source": expression_record.state_hash72, "audio": audio_record.state_hash72, "training": training_record.state_hash72}),
        source_modality="symbolic_expression",
        target_modality="audio_phase_manifest",
        steps=[
            TransitionStep(0, "audio_language_adapter", expression_record.state_hash72, audio_record.state_hash72, {"adapter_hash72": adapter_receipt.get("adapter_hash72")}),
            TransitionStep(1, "linguistic_training_loop", audio_record.state_hash72, training_record.state_hash72, {"training_receipt_hash72": training.get("receipt_hash72")}),
        ],
        round_trip_ok=True,
        witness_hash72=hash72_like({"adapter": adapter_receipt.get("adapter_hash72"), "training": training.get("receipt_hash72")}),
        metadata={"cycle": "audio_language_feedback"},
    )
    db.store_transition_trace(trace)

    links: List[Dict[str, Any]] = []
    for left, right, kind in [
        (expression_record.state_hash72, audio_record.state_hash72, "symbolic_to_audio_phase"),
        (audio_record.state_hash72, training_record.state_hash72, "audio_phase_to_linguistic_training"),
    ]:
        link = CrossModalityLink(
            link_hash72=hash72_like({"left": left, "right": right, "trace": trace.trace_hash72, "kind": kind}),
            left_state_hash72=left,
            right_state_hash72=right,
            link_type=kind,
            trace_hash72=trace.trace_hash72,
            round_trip_ok=True,
            metadata={"orchestrator": "hhs_audio_language_feedback_orchestrator_v1"},
        )
        db.store_cross_modality_link(link)
        links.append(json.loads(link.to_json()))

    summary = db.state_summary()
    receipt_hash = _receipt_hash(
        adapter_receipt=adapter_receipt,
        training_receipt_hash72=training.get("receipt_hash72"),
        summary=summary,
        stored_state_hashes=stored,
        links=links,
        security_binding=transport_security_binding,
    )
    receipt = AudioLanguageFeedbackReceipt(adapter_receipt, training, summary, stored, links, receipt_hash)
    _store_receipt(
        db,
        receipt=receipt,
        security_binding=transport_security_binding,
        trace_hash72=trace.trace_hash72,
    )
    db.close()
    return receipt


def replay_audio_language_feedback_receipt(
    receipt_hash72: str,
    *,
    semantic_db_path: str | Path = DEFAULT_SEMANTIC_DB_PATH,
) -> Dict[str, Any]:
    """Replay one stored audio receipt without re-executing training or writes."""
    if not isinstance(receipt_hash72, str) or not receipt_hash72:
        raise AudioLanguageFeedbackReplayError("HHS_AUDIO_LANGUAGE_REPLAY_HASH_REQUIRED")
    path = Path(semantic_db_path).resolve()
    if not path.is_file():
        raise AudioLanguageFeedbackReplayError("HHS_AUDIO_LANGUAGE_REPLAY_DATABASE_NOT_FOUND")
    uri = f"file:{path.as_posix()}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True)
    except sqlite3.Error as exc:
        raise AudioLanguageFeedbackReplayError(
            f"HHS_AUDIO_LANGUAGE_REPLAY_DATABASE_OPEN_FAILED:{exc}"
        ) from exc
    try:
        try:
            row = conn.execute(
                f"""
                SELECT receipt_json, security_binding_json, trace_hash72,
                       stored_state_hashes_json, cross_link_hashes_json
                FROM {AUDIO_RECEIPT_TABLE}
                WHERE receipt_hash72 = ?
                """,
                (receipt_hash72,),
            ).fetchone()
        except sqlite3.Error as exc:
            raise AudioLanguageFeedbackReplayError(
                f"HHS_AUDIO_LANGUAGE_REPLAY_TABLE_UNAVAILABLE:{exc}"
            ) from exc
        if row is None:
            raise AudioLanguageFeedbackReplayError("HHS_AUDIO_LANGUAGE_REPLAY_RECEIPT_NOT_FOUND")

        receipt = json.loads(row[0])
        security_binding = json.loads(row[1])
        trace_hash72 = str(row[2])
        stored_state_hashes = json.loads(row[3])
        cross_link_hashes = json.loads(row[4])
        if not isinstance(receipt, dict) or receipt.get("receipt_hash72") != receipt_hash72:
            raise AudioLanguageFeedbackReplayError("HHS_AUDIO_LANGUAGE_REPLAY_RECEIPT_IDENTITY_MISMATCH")
        if not isinstance(security_binding, dict):
            raise AudioLanguageFeedbackReplayError("HHS_AUDIO_LANGUAGE_REPLAY_SECURITY_BINDING_INVALID")
        if not isinstance(stored_state_hashes, list) or not isinstance(cross_link_hashes, list):
            raise AudioLanguageFeedbackReplayError("HHS_AUDIO_LANGUAGE_REPLAY_REFERENCE_SET_INVALID")

        expected_hash = _receipt_hash(
            adapter_receipt=receipt.get("adapter_receipt") or {},
            training_receipt_hash72=(receipt.get("linguistic_training_receipt") or {}).get("receipt_hash72"),
            summary=receipt.get("semantic_db_summary") or {},
            stored_state_hashes=[str(item) for item in receipt.get("stored_state_hashes") or []],
            links=list(receipt.get("cross_links") or []),
            security_binding=security_binding if security_binding else None,
        )
        if expected_hash != receipt_hash72:
            raise AudioLanguageFeedbackReplayError("HHS_AUDIO_LANGUAGE_REPLAY_HASH_MISMATCH")

        missing_states = [
            state_hash
            for state_hash in stored_state_hashes
            if conn.execute(
                "SELECT 1 FROM state_records WHERE state_hash72 = ?",
                (str(state_hash),),
            ).fetchone() is None
        ]
        trace_row = conn.execute(
            "SELECT round_trip_ok FROM transition_traces WHERE trace_hash72 = ?",
            (trace_hash72,),
        ).fetchone()
        missing_links = [
            link_hash
            for link_hash in cross_link_hashes
            if conn.execute(
                "SELECT 1 FROM cross_modality_links WHERE link_hash72 = ? AND round_trip_ok = 1",
                (str(link_hash),),
            ).fetchone() is None
        ]
        if missing_states or trace_row is None or int(trace_row[0]) != 1 or missing_links:
            raise AudioLanguageFeedbackReplayError(
                "HHS_AUDIO_LANGUAGE_REPLAY_REFERENTIAL_INTEGRITY_FAILURE"
            )
        return {
            "schema": AUDIO_REPLAY_SCHEMA,
            "receipt_hash72": receipt_hash72,
            "receipt": receipt,
            "security_binding": security_binding,
            "trace_hash72": trace_hash72,
            "integrity": {
                "receipt_hash_verified": True,
                "stored_state_count": len(stored_state_hashes),
                "stored_states_verified": True,
                "transition_trace_verified": True,
                "cross_link_count": len(cross_link_hashes),
                "cross_links_verified": True,
            },
            "reexecuted": False,
            "training_reexecuted": False,
            "auxiliary_persistence_mutated": False,
            "canonical_vm81_mutated": False,
            "new_hash72_mint_authority": False,
            "hash216_persistence_authority": False,
        }
    finally:
        conn.close()


def main() -> None:
    demo = run_audio_language_feedback_cycle(
        expression="xy=-1/yx",
        display_items=[{"id": "0", "text": "xy", "kind": "ORDERED_PRODUCT", "phaseIndex": 0}],
        audio_manifest={"manifest_hash72": "DEMO", "items": []},
    )
    print(json.dumps(demo.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()


__all__ = [
    "AUDIO_RECEIPT_SCHEMA",
    "AUDIO_RECEIPT_TABLE",
    "AUDIO_REPLAY_SCHEMA",
    "AudioLanguageFeedbackReceipt",
    "AudioLanguageFeedbackReplayError",
    "DEFAULT_SEMANTIC_DB_PATH",
    "replay_audio_language_feedback_receipt",
    "run_audio_language_feedback_cycle",
]
