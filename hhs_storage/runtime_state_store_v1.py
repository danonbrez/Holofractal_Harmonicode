# ============================================================================
# hhs_storage/runtime_state_store_v1.py
# HARMONICODE / HHS
# CANONICAL RUNTIME STATE STORE
#
# PURPOSE
# -------
# Persistent runtime storage substrate for:
#
#   - receipt-chain persistence
#   - runtime snapshot persistence
#   - replay persistence
#   - graph persistence
#   - vector persistence
#   - sandbox overlays
#   - multimodal packet archival
#
# ALL durable runtime state SHOULD route through here.
#
# ============================================================================

from __future__ import annotations

import json
import pathlib
import sqlite3
import threading
import time
import uuid

from dataclasses import dataclass
from typing import Dict, List, Optional, Any

# ============================================================================
# STORAGE ROOT
# ============================================================================

ROOT = pathlib.Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "runtime_data"

DATA_DIR.mkdir(
    exist_ok=True,
    parents=True
)

DB_PATH = DATA_DIR / "hhs_runtime_state.db"

# ============================================================================
# RECORDS
# ============================================================================

@dataclass
class RuntimeSnapshot:

    snapshot_id: str

    created_at: float

    runtime_packet: Dict[str, Any]

# ----------------------------------------------------------------------------

@dataclass
class ReplayRecord:

    replay_id: str

    created_at: float

    step: int

    state_hash72: str

    receipt_hash72: str

    payload: Dict[str, Any]

# ============================================================================
# STATE STORE
# ============================================================================

class HHSRuntimeStateStore:

    """
    Canonical persistent runtime state substrate.
    """

    def __init__(self):

        self.lock = threading.RLock()

        self.conn = sqlite3.connect(

            str(DB_PATH),

            check_same_thread=False
        )

        self.conn.row_factory = sqlite3.Row

        self._initialize_schema()

    # =====================================================================
    # SCHEMA
    # =====================================================================

    def _initialize_schema(self):

        with self.lock:

            cursor = self.conn.cursor()

            # ----------------------------------------------------------
            # SNAPSHOTS
            # ----------------------------------------------------------

            cursor.execute("""

                CREATE TABLE IF NOT EXISTS runtime_snapshots (

                    snapshot_id TEXT PRIMARY KEY,

                    created_at REAL,

                    step INTEGER,

                    state_hash72 TEXT,

                    receipt_hash72 TEXT,

                    payload TEXT
                )

            """)

            # ----------------------------------------------------------
            # REPLAY
            # ----------------------------------------------------------

            cursor.execute("""

                CREATE TABLE IF NOT EXISTS replay_records (

                    replay_id TEXT PRIMARY KEY,

                    created_at REAL,

                    step INTEGER,

                    state_hash72 TEXT,

                    receipt_hash72 TEXT,

                    payload TEXT
                )

            """)

            # ----------------------------------------------------------
            # EVENTS
            # ----------------------------------------------------------

            cursor.execute("""

                CREATE TABLE IF NOT EXISTS runtime_events (

                    event_id TEXT PRIMARY KEY,

                    created_at REAL,

                    event_type TEXT,

                    source TEXT,

                    payload TEXT
                )

            """)

            # ----------------------------------------------------------
            # VECTOR CACHE
            # ----------------------------------------------------------

            cursor.execute("""

                CREATE TABLE IF NOT EXISTS vector_cache (

                    vector_id TEXT PRIMARY KEY,

                    created_at REAL,

                    hash72 TEXT,

                    vector_json TEXT
                )

            """)

            # ----------------------------------------------------------
            # SANDBOX
            # ----------------------------------------------------------

            cursor.execute("""

                CREATE TABLE IF NOT EXISTS sandbox_overlays (

                    sandbox_id TEXT PRIMARY KEY,

                    created_at REAL,

                    metadata TEXT
                )

            """)

            self.conn.commit()

    # =====================================================================
    # SNAPSHOTS
    # =====================================================================

    def store_snapshot(
        self,
        runtime_packet: Dict
    ) -> str:

        with self.lock:

            snapshot_id = str(uuid.uuid4())

            runtime = runtime_packet["runtime"]

            self.conn.execute("""

                INSERT INTO runtime_snapshots (

                    snapshot_id,
                    created_at,
                    step,
                    state_hash72,
                    receipt_hash72,
                    payload

                ) VALUES (?, ?, ?, ?, ?, ?)

            """, (

                snapshot_id,

                time.time(),

                runtime["step"],

                runtime["state_hash72"],

                runtime["receipt_hash72"],

                json.dumps(runtime_packet)
            ))

            self.conn.commit()

            return snapshot_id

    # ---------------------------------------------------------------------

    def latest_snapshot(self):

        with self.lock:

            cursor = self.conn.execute("""

                SELECT *
                FROM runtime_snapshots
                ORDER BY created_at DESC
                LIMIT 1

            """)

            row = cursor.fetchone()

            if row is None:
                return None

            return dict(row)

    # =====================================================================
    # REPLAY
    # =====================================================================

    def store_replay_record(
        self,
        packet: Dict
    ):

        with self.lock:

            runtime = packet["runtime"]

            replay_id = str(uuid.uuid4())

            self.conn.execute("""

                INSERT INTO replay_records (

                    replay_id,
                    created_at,
                    step,
                    state_hash72,
                    receipt_hash72,
                    payload

                ) VALUES (?, ?, ?, ?, ?, ?)

            """, (

                replay_id,

                time.time(),

                runtime["step"],

                runtime["state_hash72"],

                runtime["receipt_hash72"],

                json.dumps(packet)
            ))

            self.conn.commit()

            return replay_id

    # ---------------------------------------------------------------------

    def replay_chain(
        self,
        limit: int = 100
    ):

        with self.lock:

            cursor = self.conn.execute("""

                SELECT *
                FROM replay_records
                ORDER BY step ASC
                LIMIT ?

            """, (limit,))

            rows = cursor.fetchall()

            return [

                dict(row)

                for row in rows
            ]

    # =====================================================================
    # EVENTS
    # =====================================================================

    def store_event(
        self,
        event_type: str,
        source: str,
        payload: Dict
    ):

        with self.lock:

            event_id = str(uuid.uuid4())

            self.conn.execute("""

                INSERT INTO runtime_events (

                    event_id,
                    created_at,
                    event_type,
                    source,
                    payload

                ) VALUES (?, ?, ?, ?, ?)

            """, (

                event_id,

                time.time(),

                event_type,

                source,

                json.dumps(payload)
            ))

            self.conn.commit()

            return event_id

    # =====================================================================
    # VECTOR CACHE
    # =====================================================================

    def store_vector_record(
        self,
        hash72: str,
        vector: List[float]
    ):

        with self.lock:

            vector_id = str(uuid.uuid4())

            self.conn.execute("""

                INSERT INTO vector_cache (

                    vector_id,
                    created_at,
                    hash72,
                    vector_json

                ) VALUES (?, ?, ?, ?)

            """, (

                vector_id,

                time.time(),

                hash72,

                json.dumps(vector)
            ))

            self.conn.commit()

            return vector_id

    # ---------------------------------------------------------------------

    def nearest_vectors(
        self,
        limit: int = 10
    ):

        with self.lock:

            cursor = self.conn.execute("""

                SELECT *
                FROM vector_cache
                ORDER BY created_at DESC
                LIMIT ?

            """, (limit,))

            rows = cursor.fetchall()

            return [

                dict(row)

                for row in rows
            ]

    # =====================================================================
    # SANDBOX
    # =====================================================================

    def create_sandbox_overlay(
        self,
        metadata: Optional[Dict] = None
    ):

        with self.lock:

            sandbox_id = str(uuid.uuid4())

            self.conn.execute("""

                INSERT INTO sandbox_overlays (

                    sandbox_id,
                    created_at,
                    metadata

                ) VALUES (?, ?, ?)

            """, (

                sandbox_id,

                time.time(),

                json.dumps(metadata or {})
            ))

            self.conn.commit()

            return sandbox_id

    # =====================================================================
    # METRICS
    # =====================================================================

    def metrics(self):

        with self.lock:

            def count(table):

                cursor = self.conn.execute(
                    f"SELECT COUNT(*) FROM {table}"
                )

                return cursor.fetchone()[0]

            return {

                "snapshots":
                    count("runtime_snapshots"),

                "replay_records":
                    count("replay_records"),

                "events":
                    count("runtime_events"),

                "vector_records":
                    count("vector_cache"),

                "sandboxes":
                    count("sandbox_overlays"),
            }

# ============================================================================
# GLOBAL STORE
# ============================================================================

runtime_state_store = (
    HHSRuntimeStateStore()
)

# ============================================================================
# SELF TEST
# ============================================================================

def state_store_self_test():

    packet = {

        "runtime": {

            "step": 1,

            "state_hash72":
                "abc123",

            "receipt_hash72":
                "xyz789"
        }
    }

    runtime_state_store.store_snapshot(
        packet
    )

    runtime_state_store.store_replay_record(
        packet
    )

    runtime_state_store.store_event(

        event_type="runtime.step",

        source="self_test",

        payload=packet
    )

    runtime_state_store.store_vector_record(

        hash72="abc123",

        vector=[0.1] * 72
    )

    print()

    print("STATE STORE METRICS")

    print(
        runtime_state_store.metrics()
    )

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    state_store_self_test()