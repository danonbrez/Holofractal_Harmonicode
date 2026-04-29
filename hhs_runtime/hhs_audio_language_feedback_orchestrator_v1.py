"""
HHS Audio Language Feedback Orchestrator v1
==========================================

Thin caller over existing modules:
- hhs_audio_language_adapter_v1.ingest_audio_language_artifacts
- harmonicode_verbatim_semantic_database_v1.HarmonicodeVerbatimSemanticDatabaseV1
- hhs_linguistic_operator_training_loop_v1.run_linguistic_training_loop

No new tokenizer/database/training model is defined here.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List
import json

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


def run_audio_language_feedback_cycle(
    *,
    expression: str,
    display_items: List[Dict[str, Any]],
    audio_manifest: Dict[str, Any],
    audio_roundtrip_receipt: Dict[str, Any] | None = None,
    semantic_db_path: str | Path = "demo_reports/harmonicode_verbatim_semantic_audio_language_v1.sqlite",
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
    db.close()

    receipt_hash = hash72_digest(("hhs_audio_language_feedback_receipt_v1", adapter_receipt, training.get("receipt_hash72"), summary, stored, links), width=24)
    return AudioLanguageFeedbackReceipt(adapter_receipt, training, summary, stored, links, receipt_hash)


def main() -> None:
    demo = run_audio_language_feedback_cycle(
        expression="xy=-1/yx",
        display_items=[{"id": "0", "text": "xy", "kind": "ORDERED_PRODUCT", "phaseIndex": 0}],
        audio_manifest={"manifest_hash72": "DEMO", "items": []},
    )
    print(json.dumps(demo.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
