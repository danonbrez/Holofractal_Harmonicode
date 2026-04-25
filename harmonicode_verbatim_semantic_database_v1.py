
"""
harmonicode_verbatim_semantic_database_v1.py

Standalone verbatim-tokenized semantic database layer for the Harmonicode stack.

Purpose
-------
Store:
- verbatim token sequences
- hash-validated canonical states
- transition traces
- witnesses and invariant reports
- cross-modality equivalence links

Design constraints
------------------
- Does NOT mutate the locked kernel or locked agent.
- Assumes the canonical stored state is the losslessly compressed Hash72 seed.
- Modality-specific processing remains external; this layer stores only validated
  results and the legal traces that produced them.
- Uses stdlib only.

This is the database layer that sits above:
- harmonicode_modality_verbatim_ingestion_v1.py
- the locked kernel / locked agent authority path
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from collections import defaultdict
import hashlib
import json
import sqlite3
import time


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def hash72_like(payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "H72N-" + hashlib.sha256(data).hexdigest()[:18]


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def utc_timestamp() -> float:
    return time.time()


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class TransitionStep:
    step_index: int
    op_name: str
    input_hash72: str
    output_hash72: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return canonical_json(asdict(self))


@dataclass
class TransitionTrace:
    trace_hash72: str
    source_modality: str
    target_modality: str
    steps: List[TransitionStep]
    round_trip_ok: bool
    witness_hash72: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return canonical_json({
            "trace_hash72": self.trace_hash72,
            "source_modality": self.source_modality,
            "target_modality": self.target_modality,
            "steps": [asdict(s) for s in self.steps],
            "round_trip_ok": self.round_trip_ok,
            "witness_hash72": self.witness_hash72,
            "metadata": self.metadata,
        })


@dataclass
class VerbatimStateRecord:
    state_hash72: str
    modality: str
    source_name: str
    verbatim_content: str
    token_sequence: List[str]
    projection_hash72: str
    witness_hash72: str
    invariant_report: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=utc_timestamp)

    def to_json(self) -> str:
        return canonical_json({
            "state_hash72": self.state_hash72,
            "modality": self.modality,
            "source_name": self.source_name,
            "verbatim_content": self.verbatim_content,
            "token_sequence": self.token_sequence,
            "projection_hash72": self.projection_hash72,
            "witness_hash72": self.witness_hash72,
            "invariant_report": self.invariant_report,
            "metadata": self.metadata,
            "created_at": self.created_at,
        })


@dataclass
class CrossModalityLink:
    link_hash72: str
    left_state_hash72: str
    right_state_hash72: str
    link_type: str
    trace_hash72: str
    round_trip_ok: bool
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return canonical_json({
            "link_hash72": self.link_hash72,
            "left_state_hash72": self.left_state_hash72,
            "right_state_hash72": self.right_state_hash72,
            "link_type": self.link_type,
            "trace_hash72": self.trace_hash72,
            "round_trip_ok": self.round_trip_ok,
            "metadata": self.metadata,
        })


# ---------------------------------------------------------------------------
# Round-trip invariant harness
# ---------------------------------------------------------------------------

class RoundTripInvariantHarnessV1:
    """
    Kernel-facing invariant harness contract.

    This layer does not own the kernel. Instead, it expects an external callback
    or adapter that can:
    - canonicalize an object into a kernel state hash
    - verify round-trip identity
    """

    def __init__(self, canonicalize_fn=None, round_trip_fn=None) -> None:
        self.canonicalize_fn = canonicalize_fn
        self.round_trip_fn = round_trip_fn

    def canonicalize(self, payload: Any) -> str:
        if self.canonicalize_fn is None:
            return hash72_like(payload)
        return self.canonicalize_fn(payload)

    def verify_round_trip(self, source_payload: Any, reconstructed_payload: Any) -> Dict[str, Any]:
        if self.round_trip_fn is None:
            left = self.canonicalize(source_payload)
            right = self.canonicalize(reconstructed_payload)
            return {
                "round_trip_ok": left == right,
                "input_hash72": left,
                "output_hash72": right,
                "invariant_name": "canonical_hash_identity",
            }
        return self.round_trip_fn(source_payload, reconstructed_payload)


# ---------------------------------------------------------------------------
# Database layer
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS state_records (
    state_hash72 TEXT PRIMARY KEY,
    modality TEXT NOT NULL,
    source_name TEXT NOT NULL,
    verbatim_content TEXT NOT NULL,
    token_sequence_json TEXT NOT NULL,
    projection_hash72 TEXT NOT NULL,
    witness_hash72 TEXT NOT NULL,
    invariant_report_json TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS transition_traces (
    trace_hash72 TEXT PRIMARY KEY,
    source_modality TEXT NOT NULL,
    target_modality TEXT NOT NULL,
    steps_json TEXT NOT NULL,
    round_trip_ok INTEGER NOT NULL,
    witness_hash72 TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cross_modality_links (
    link_hash72 TEXT PRIMARY KEY,
    left_state_hash72 TEXT NOT NULL,
    right_state_hash72 TEXT NOT NULL,
    link_type TEXT NOT NULL,
    trace_hash72 TEXT NOT NULL,
    round_trip_ok INTEGER NOT NULL,
    metadata_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS token_index (
    token_hash72 TEXT PRIMARY KEY,
    state_hash72 TEXT NOT NULL,
    modality TEXT NOT NULL,
    token_position INTEGER NOT NULL,
    token_value TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_state_modality ON state_records(modality);
CREATE INDEX IF NOT EXISTS idx_token_value ON token_index(token_value);
CREATE INDEX IF NOT EXISTS idx_link_left ON cross_modality_links(left_state_hash72);
CREATE INDEX IF NOT EXISTS idx_link_right ON cross_modality_links(right_state_hash72);
"""


class HarmonicodeVerbatimSemanticDatabaseV1:
    def __init__(self, db_path: str | Path, harness: Optional[RoundTripInvariantHarnessV1] = None) -> None:
        self.db_path = str(db_path)
        self.harness = harness or RoundTripInvariantHarnessV1()
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self._init_schema()

    def close(self) -> None:
        self.conn.close()

    def _init_schema(self) -> None:
        self.conn.executescript(SCHEMA_SQL)
        self.conn.commit()

    # ---------------------------------------------------------------------
    # State record storage
    # ---------------------------------------------------------------------

    def store_state_record(self, record: VerbatimStateRecord) -> str:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO state_records (
                state_hash72, modality, source_name, verbatim_content,
                token_sequence_json, projection_hash72, witness_hash72,
                invariant_report_json, metadata_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.state_hash72,
                record.modality,
                record.source_name,
                record.verbatim_content,
                canonical_json(record.token_sequence),
                record.projection_hash72,
                record.witness_hash72,
                canonical_json(record.invariant_report),
                canonical_json(record.metadata),
                record.created_at,
            ),
        )
        self._index_tokens(record)
        self.conn.commit()
        return record.state_hash72

    def _index_tokens(self, record: VerbatimStateRecord) -> None:
        self.conn.execute("DELETE FROM token_index WHERE state_hash72 = ?", (record.state_hash72,))
        for i, token in enumerate(record.token_sequence):
            token_hash72 = hash72_like({
                "state_hash72": record.state_hash72,
                "position": i,
                "token": token,
            })
            self.conn.execute(
                """
                INSERT OR REPLACE INTO token_index (
                    token_hash72, state_hash72, modality, token_position, token_value
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (token_hash72, record.state_hash72, record.modality, i, token),
            )

    def get_state_record(self, state_hash72: str) -> Optional[VerbatimStateRecord]:
        row = self.conn.execute(
            """
            SELECT state_hash72, modality, source_name, verbatim_content,
                   token_sequence_json, projection_hash72, witness_hash72,
                   invariant_report_json, metadata_json, created_at
            FROM state_records
            WHERE state_hash72 = ?
            """,
            (state_hash72,),
        ).fetchone()
        if row is None:
            return None
        return VerbatimStateRecord(
            state_hash72=row[0],
            modality=row[1],
            source_name=row[2],
            verbatim_content=row[3],
            token_sequence=json.loads(row[4]),
            projection_hash72=row[5],
            witness_hash72=row[6],
            invariant_report=json.loads(row[7]),
            metadata=json.loads(row[8]),
            created_at=row[9],
        )

    def search_by_token(self, token: str, modality: Optional[str] = None) -> List[Dict[str, Any]]:
        if modality is None:
            rows = self.conn.execute(
                """
                SELECT state_hash72, modality, token_position, token_value
                FROM token_index
                WHERE token_value = ?
                ORDER BY modality, state_hash72, token_position
                """,
                (token,),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """
                SELECT state_hash72, modality, token_position, token_value
                FROM token_index
                WHERE token_value = ? AND modality = ?
                ORDER BY state_hash72, token_position
                """,
                (token, modality),
            ).fetchall()
        return [
            {
                "state_hash72": r[0],
                "modality": r[1],
                "token_position": r[2],
                "token_value": r[3],
            }
            for r in rows
        ]

    # ---------------------------------------------------------------------
    # Trace storage
    # ---------------------------------------------------------------------

    def store_transition_trace(self, trace: TransitionTrace) -> str:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO transition_traces (
                trace_hash72, source_modality, target_modality,
                steps_json, round_trip_ok, witness_hash72, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trace.trace_hash72,
                trace.source_modality,
                trace.target_modality,
                canonical_json([asdict(s) for s in trace.steps]),
                1 if trace.round_trip_ok else 0,
                trace.witness_hash72,
                canonical_json(trace.metadata),
            ),
        )
        self.conn.commit()
        return trace.trace_hash72

    def get_transition_trace(self, trace_hash72: str) -> Optional[TransitionTrace]:
        row = self.conn.execute(
            """
            SELECT trace_hash72, source_modality, target_modality,
                   steps_json, round_trip_ok, witness_hash72, metadata_json
            FROM transition_traces
            WHERE trace_hash72 = ?
            """,
            (trace_hash72,),
        ).fetchone()
        if row is None:
            return None
        steps_data = json.loads(row[3])
        return TransitionTrace(
            trace_hash72=row[0],
            source_modality=row[1],
            target_modality=row[2],
            steps=[TransitionStep(**s) for s in steps_data],
            round_trip_ok=bool(row[4]),
            witness_hash72=row[5],
            metadata=json.loads(row[6]),
        )

    # ---------------------------------------------------------------------
    # Cross-modality links
    # ---------------------------------------------------------------------

    def store_cross_modality_link(self, link: CrossModalityLink) -> str:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO cross_modality_links (
                link_hash72, left_state_hash72, right_state_hash72,
                link_type, trace_hash72, round_trip_ok, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                link.link_hash72,
                link.left_state_hash72,
                link.right_state_hash72,
                link.link_type,
                link.trace_hash72,
                1 if link.round_trip_ok else 0,
                canonical_json(link.metadata),
            ),
        )
        self.conn.commit()
        return link.link_hash72

    def links_for_state(self, state_hash72: str) -> List[CrossModalityLink]:
        rows = self.conn.execute(
            """
            SELECT link_hash72, left_state_hash72, right_state_hash72,
                   link_type, trace_hash72, round_trip_ok, metadata_json
            FROM cross_modality_links
            WHERE left_state_hash72 = ? OR right_state_hash72 = ?
            """,
            (state_hash72, state_hash72),
        ).fetchall()
        return [
            CrossModalityLink(
                link_hash72=r[0],
                left_state_hash72=r[1],
                right_state_hash72=r[2],
                link_type=r[3],
                trace_hash72=r[4],
                round_trip_ok=bool(r[5]),
                metadata=json.loads(r[6]),
            )
            for r in rows
        ]

    # ---------------------------------------------------------------------
    # Construction helpers
    # ---------------------------------------------------------------------

    def record_ingestion_artifact(self, artifact: Any) -> str:
        """
        Accepts an artifact from the standalone modality ingestion module.
        The object is duck-typed to avoid direct dependency.
        """
        token_sequence = [tok.canonical for tok in artifact.canonical_tokens]
        record = VerbatimStateRecord(
            state_hash72=artifact.address_hash72,
            modality=artifact.modality,
            source_name=getattr(artifact.source, "source_name", "inline"),
            verbatim_content=getattr(artifact.source, "content", ""),
            token_sequence=token_sequence,
            projection_hash72=artifact.witness.projection_hash72,
            witness_hash72=artifact.witness.projection_hash72,
            invariant_report={
                "gates": artifact.witness.gates,
                "details": artifact.witness.details,
                "cross_talk_audits": getattr(artifact, "cross_talk_audits", []),
            },
            metadata=getattr(artifact.source, "metadata", {}),
        )
        return self.store_state_record(record)

    def build_round_trip_trace(
        self,
        *,
        source_modality: str,
        target_modality: str,
        input_payload: Any,
        projected_payload: Any,
        reconstructed_payload: Any,
        step_names: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TransitionTrace:
        step_names = step_names or ["project", "reconstruct", "canonicalize"]
        pre_hash = self.harness.canonicalize(input_payload)
        proj_hash = hash72_like(projected_payload)
        post_report = self.harness.verify_round_trip(input_payload, reconstructed_payload)
        post_hash = post_report["output_hash72"]

        steps = [
            TransitionStep(
                step_index=0,
                op_name=step_names[0],
                input_hash72=pre_hash,
                output_hash72=proj_hash,
                details={"payload_hash72": proj_hash},
            ),
            TransitionStep(
                step_index=1,
                op_name=step_names[1],
                input_hash72=proj_hash,
                output_hash72=post_hash,
                details={"reconstructed_hash72": post_hash},
            ),
            TransitionStep(
                step_index=2,
                op_name=step_names[2],
                input_hash72=pre_hash,
                output_hash72=post_hash,
                details=post_report,
            ),
        ]
        trace_hash = hash72_like({
            "source_modality": source_modality,
            "target_modality": target_modality,
            "steps": [asdict(s) for s in steps],
        })
        witness_hash = hash72_like({
            "round_trip_ok": post_report["round_trip_ok"],
            "input_hash72": pre_hash,
            "output_hash72": post_hash,
        })
        return TransitionTrace(
            trace_hash72=trace_hash,
            source_modality=source_modality,
            target_modality=target_modality,
            steps=steps,
            round_trip_ok=bool(post_report["round_trip_ok"]),
            witness_hash72=witness_hash,
            metadata=metadata or {},
        )

    def link_equivalent_states(
        self,
        left_state_hash72: str,
        right_state_hash72: str,
        trace: TransitionTrace,
        link_type: str = "cross_modal_equivalence",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CrossModalityLink:
        link = CrossModalityLink(
            link_hash72=hash72_like({
                "left": left_state_hash72,
                "right": right_state_hash72,
                "trace": trace.trace_hash72,
                "link_type": link_type,
            }),
            left_state_hash72=left_state_hash72,
            right_state_hash72=right_state_hash72,
            link_type=link_type,
            trace_hash72=trace.trace_hash72,
            round_trip_ok=trace.round_trip_ok,
            metadata=metadata or {},
        )
        self.store_cross_modality_link(link)
        return link

    # ---------------------------------------------------------------------
    # Reports
    # ---------------------------------------------------------------------

    def state_summary(self) -> Dict[str, Any]:
        by_modality = self.conn.execute(
            """
            SELECT modality, COUNT(*)
            FROM state_records
            GROUP BY modality
            ORDER BY modality
            """
        ).fetchall()
        trace_count = self.conn.execute("SELECT COUNT(*) FROM transition_traces").fetchone()[0]
        link_count = self.conn.execute("SELECT COUNT(*) FROM cross_modality_links").fetchone()[0]
        state_count = self.conn.execute("SELECT COUNT(*) FROM state_records").fetchone()[0]
        return {
            "db_path": self.db_path,
            "state_count": state_count,
            "trace_count": trace_count,
            "link_count": link_count,
            "states_by_modality": {row[0]: row[1] for row in by_modality},
            "summary_hash72": hash72_like({
                "state_count": state_count,
                "trace_count": trace_count,
                "link_count": link_count,
                "states_by_modality": by_modality,
            }),
        }


# ---------------------------------------------------------------------------
# Optional helper for lossless compression/translation assertions
# ---------------------------------------------------------------------------

def lossless_round_trip_proof_v1(
    harness: RoundTripInvariantHarnessV1,
    source_payload: Any,
    projected_payload: Any,
    reconstructed_payload: Any,
) -> Dict[str, Any]:
    report = harness.verify_round_trip(source_payload, reconstructed_payload)
    return {
        "proof_type": "LOSSLESS_ROUND_TRIP_PROOF_V1",
        "input_hash72": report["input_hash72"],
        "output_hash72": report["output_hash72"],
        "round_trip_ok": report["round_trip_ok"],
        "projected_hash72": hash72_like(projected_payload),
        "proof_hash72": hash72_like({
            "input_hash72": report["input_hash72"],
            "output_hash72": report["output_hash72"],
            "round_trip_ok": report["round_trip_ok"],
            "projected_hash72": hash72_like(projected_payload),
        }),
    }


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def _demo() -> None:
    db = HarmonicodeVerbatimSemanticDatabaseV1(":memory:")

    # Simulated ingested records
    rec1 = VerbatimStateRecord(
        state_hash72=hash72_like({"seed": "alpha"}),
        modality="text",
        source_name="demo_text",
        verbatim_content="a ^ 2 + b ^ 2 = c ^ 2",
        token_sequence=["a", "^", "2", "+", "b", "^", "2", "=", "c", "^", "2"],
        projection_hash72=hash72_like({"projection": "text_math_identity"}),
        witness_hash72=hash72_like({"witness": "text_math_identity"}),
        invariant_report={"gates": {"round_trip": True}},
    )
    rec2 = VerbatimStateRecord(
        state_hash72=hash72_like({"seed": "beta"}),
        modality="math",
        source_name="demo_math",
        verbatim_content="a^2+b^2=c^2",
        token_sequence=["a", "^", "2", "+", "b", "^", "2", "=", "c", "^", "2"],
        projection_hash72=hash72_like({"projection": "math_identity"}),
        witness_hash72=hash72_like({"witness": "math_identity"}),
        invariant_report={"gates": {"round_trip": True}},
    )
    db.store_state_record(rec1)
    db.store_state_record(rec2)

    trace = db.build_round_trip_trace(
        source_modality="text",
        target_modality="math",
        input_payload={"seed": "alpha", "tokens": rec1.token_sequence},
        projected_payload={"math_tokens": rec2.token_sequence},
        reconstructed_payload={"seed": "alpha", "tokens": rec1.token_sequence},
    )
    db.store_transition_trace(trace)
    link = db.link_equivalent_states(rec1.state_hash72, rec2.state_hash72, trace)

    report = {
        "summary": db.state_summary(),
        "trace": json.loads(trace.to_json()),
        "link": json.loads(link.to_json()),
        "search_token_a": db.search_by_token("a"),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    db.close()


if __name__ == "__main__":
    _demo()
