"""
HHS Symbolic Selection Memory Adapter v1
=======================================

Thin adapter over the existing verbatim semantic database.

Records GUI-selected symbolic substitution candidates as validated state records,
transition traces, and cross-modality links. This does not define a new memory
system; it only calls HarmonicodeVerbatimSemanticDatabaseV1.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List
import json

from harmonicode_verbatim_semantic_database_v1 import (
    HarmonicodeVerbatimSemanticDatabaseV1,
    TransitionStep,
    TransitionTrace,
    VerbatimStateRecord,
    CrossModalityLink,
    hash72_like,
)
from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


@dataclass(frozen=True)
class SymbolicSelectionMemoryReceipt:
    source_state_hash72: str
    selected_state_hash72: str
    trace_hash72: str
    link_hash72: str
    db_summary: Dict[str, Any]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _tokens(text: str) -> List[str]:
    return [t for t in str(text).replace("(", " ( ").replace(")", " ) ").replace(",", " , ").split() if t]


def _state_record(modality: str, source_name: str, content: str, metadata: Dict[str, Any]) -> VerbatimStateRecord:
    toks = _tokens(content)
    state_hash = hash72_like({"modality": modality, "source_name": source_name, "content": content, "tokens": toks, "metadata": metadata})
    projection_hash = hash72_like({"projection": modality, "tokens": toks})
    witness_hash = hash72_like({"witness": modality, "state_hash": state_hash})
    return VerbatimStateRecord(
        state_hash72=state_hash,
        modality=modality,
        source_name=source_name,
        verbatim_content=content,
        token_sequence=toks,
        projection_hash72=projection_hash,
        witness_hash72=witness_hash,
        invariant_report={"round_trip": True, "selection_memory_adapter": "v1"},
        metadata=metadata,
    )


def record_symbolic_selection(
    *,
    source_text: str,
    selected_text: str,
    candidate: Dict[str, Any],
    evaluation_result: Dict[str, Any] | None = None,
    db_path: str | Path = "demo_reports/hhs_symbolic_selection_memory_v1.sqlite",
) -> SymbolicSelectionMemoryReceipt:
    db = HarmonicodeVerbatimSemanticDatabaseV1(db_path)

    source_record = _state_record(
        "calculator_source",
        "symbolic_selection_source",
        source_text,
        {"source": "CalculatorPanelV2"},
    )
    selected_record = _state_record(
        "symbolic_candidate_selection",
        "symbolic_selection_applied",
        selected_text,
        {
            "candidate_hash72": candidate.get("candidate_hash72"),
            "score": candidate.get("score"),
            "reason": candidate.get("reason"),
            "projected_phases": candidate.get("projected_phases", []),
            "evaluation_hash72": (evaluation_result or {}).get("result_hash72"),
        },
    )

    db.store_state_record(source_record)
    db.store_state_record(selected_record)

    trace = TransitionTrace(
        trace_hash72=hash72_like({
            "source": source_record.state_hash72,
            "selected": selected_record.state_hash72,
            "candidate": candidate,
        }),
        source_modality="calculator_source",
        target_modality="symbolic_candidate_selection",
        steps=[
            TransitionStep(
                step_index=0,
                op_name="select_symbolic_candidate",
                input_hash72=source_record.state_hash72,
                output_hash72=selected_record.state_hash72,
                details={"candidate": candidate},
            ),
        ],
        round_trip_ok=True,
        witness_hash72=hash72_like({"selection": selected_record.state_hash72, "source": source_record.state_hash72}),
        metadata={"adapter": "hhs_symbolic_selection_memory_adapter_v1"},
    )
    db.store_transition_trace(trace)

    link = CrossModalityLink(
        link_hash72=hash72_like({
            "left": source_record.state_hash72,
            "right": selected_record.state_hash72,
            "trace": trace.trace_hash72,
            "type": "selected_symbolic_path",
        }),
        left_state_hash72=source_record.state_hash72,
        right_state_hash72=selected_record.state_hash72,
        link_type="selected_symbolic_path",
        trace_hash72=trace.trace_hash72,
        round_trip_ok=True,
        metadata={"candidate_hash72": candidate.get("candidate_hash72")},
    )
    db.store_cross_modality_link(link)

    summary = db.state_summary()
    db.close()

    receipt_hash = hash72_digest(("hhs_symbolic_selection_memory_receipt_v1", source_record.state_hash72, selected_record.state_hash72, trace.trace_hash72, link.link_hash72, summary), width=24)
    return SymbolicSelectionMemoryReceipt(source_record.state_hash72, selected_record.state_hash72, trace.trace_hash72, link.link_hash72, summary, receipt_hash)


def main() -> None:
    out = record_symbolic_selection(
        source_text="meaning emerges through structure",
        selected_text="STATE(mnng) OP(mrgs) REL(thrgh) STATE(strctr)",
        candidate={"candidate_hash72": "DEMO", "score": 88, "reason": "demo"},
    )
    print(json.dumps(out.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
