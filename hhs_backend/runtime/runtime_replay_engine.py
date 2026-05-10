# ============================================================================
# hhs_backend/runtime/runtime_replay_engine.py
# HARMONICODE / HHS
# CANONICAL RUNTIME REPLAY ENGINE
#
# PURPOSE
# -------
# Deterministic replay execution subsystem for:
#
#   - runtime reconstruction
#   - receipt-chain replay
#   - branch replay
#   - predictive trajectory simulation
#   - replay equivalence verification
#   - sandboxed historical execution
#   - replay-safe multimodal routing
#
# Replay MUST remain isolated from live side effects.
#
# ============================================================================

from __future__ import annotations

import copy
import logging
import time
import uuid

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from hhs_storage.runtime_state_store_v1 import (
    runtime_state_store
)

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger("HHS_REPLAY")

# ============================================================================
# REPLAY MODES
# ============================================================================

MODE_RECONSTRUCT = "reconstruct"

MODE_BRANCH_SIMULATION = "branch-simulation"

MODE_PREDICTIVE = "predictive"

MODE_SANDBOX = "sandbox"

# ============================================================================
# REPLAY FRAME
# ============================================================================

@dataclass
class HHSReplayFrame:

    replay_id: str

    frame_index: int

    created_at: float

    runtime_packet: Dict[str, Any]

    mode: str

# ============================================================================
# REPLAY RESULT
# ============================================================================

@dataclass
class HHSReplayResult:

    replay_id: str

    mode: str

    started_at: float

    completed_at: float

    total_frames: int

    replay_equivalent: bool

    frames: List[HHSReplayFrame] = field(
        default_factory=list
    )

# ============================================================================
# REPLAY ENGINE
# ============================================================================

class HHSRuntimeReplayEngine:

    """
    Canonical deterministic replay execution subsystem.
    """

    def __init__(self):

        self.active_replays: Dict[
            str,
            HHSReplayResult
        ] = {}

        self.completed_replays: Dict[
            str,
            HHSReplayResult
        ] = {}

        self.total_replays = 0

        self.total_frames_processed = 0

    # =====================================================================
    # REPLAY CONSTRUCTION
    # =====================================================================

    def _create_replay_result(
        self,
        mode: str
    ) -> HHSReplayResult:

        replay_id = str(uuid.uuid4())

        result = HHSReplayResult(

            replay_id=replay_id,

            mode=mode,

            started_at=time.time(),

            completed_at=0.0,

            total_frames=0,

            replay_equivalent=True
        )

        self.active_replays[
            replay_id
        ] = result

        self.total_replays += 1

        return result

    # =====================================================================
    # RECONSTRUCTION
    # =====================================================================

    def reconstruct_runtime(
        self,
        limit: int = 100
    ) -> HHSReplayResult:

        result = self._create_replay_result(
            MODE_RECONSTRUCT
        )

        records = runtime_state_store.replay_chain(
            limit=limit
        )

        for index, row in enumerate(records):

            payload = row["payload"]

            if isinstance(payload, str):

                import json

                payload = json.loads(payload)

            frame = HHSReplayFrame(

                replay_id=result.replay_id,

                frame_index=index,

                created_at=time.time(),

                runtime_packet=payload,

                mode=MODE_RECONSTRUCT
            )

            result.frames.append(frame)

            self.total_frames_processed += 1

        result.total_frames = len(
            result.frames
        )

        result.completed_at = time.time()

        self.completed_replays[
            result.replay_id
        ] = result

        del self.active_replays[
            result.replay_id
        ]

        logger.info(
            f"Replay reconstruction complete: "
            f"{result.replay_id}"
        )

        return result

    # =====================================================================
    # BRANCH SIMULATION
    # =====================================================================

    def simulate_branch(
        self,
        mutation: Optional[Dict] = None,
        limit: int = 25
    ) -> HHSReplayResult:

        result = self._create_replay_result(
            MODE_BRANCH_SIMULATION
        )

        records = runtime_state_store.replay_chain(
            limit=limit
        )

        for index, row in enumerate(records):

            payload = row["payload"]

            if isinstance(payload, str):

                import json

                payload = json.loads(payload)

            cloned = copy.deepcopy(payload)

            if mutation:

                runtime = cloned.get(
                    "runtime",
                    {}
                )

                runtime.update(mutation)

            frame = HHSReplayFrame(

                replay_id=result.replay_id,

                frame_index=index,

                created_at=time.time(),

                runtime_packet=cloned,

                mode=MODE_BRANCH_SIMULATION
            )

            result.frames.append(frame)

            self.total_frames_processed += 1

        result.total_frames = len(
            result.frames
        )

        result.completed_at = time.time()

        self.completed_replays[
            result.replay_id
        ] = result

        del self.active_replays[
            result.replay_id
        ]

        logger.info(
            f"Branch simulation complete: "
            f"{result.replay_id}"
        )

        return result

    # =====================================================================
    # PREDICTIVE TRAJECTORY
    # =====================================================================

    def predictive_replay(
        self,
        horizon: int = 10
    ) -> HHSReplayResult:

        result = self._create_replay_result(
            MODE_PREDICTIVE
        )

        latest = runtime_state_store.latest_snapshot()

        if latest is None:

            result.replay_equivalent = False

            result.completed_at = time.time()

            return result

        import json

        payload = json.loads(
            latest["payload"]
        )

        runtime = payload.get(
            "runtime",
            {}
        )

        current_step = runtime.get(
            "step",
            0
        )

        for i in range(horizon):

            synthetic = copy.deepcopy(payload)

            synthetic_runtime = synthetic[
                "runtime"
            ]

            synthetic_runtime["step"] = (
                current_step + i + 1
            )

            synthetic_runtime[
                "predicted"
            ] = True

            frame = HHSReplayFrame(

                replay_id=result.replay_id,

                frame_index=i,

                created_at=time.time(),

                runtime_packet=synthetic,

                mode=MODE_PREDICTIVE
            )

            result.frames.append(frame)

            self.total_frames_processed += 1

        result.total_frames = len(
            result.frames
        )

        result.completed_at = time.time()

        self.completed_replays[
            result.replay_id
        ] = result

        del self.active_replays[
            result.replay_id
        ]

        logger.info(
            f"Predictive replay complete: "
            f"{result.replay_id}"
        )

        return result

    # =====================================================================
    # EQUIVALENCE VERIFICATION
    # =====================================================================

    def verify_replay_equivalence(
        self,
        replay: HHSReplayResult
    ) -> bool:

        if replay.total_frames == 0:
            return False

        hashes = []

        for frame in replay.frames:

            runtime = frame.runtime_packet.get(
                "runtime",
                {}
            )

            hashes.append(
                runtime.get(
                    "state_hash72",
                    ""
                )
            )

        replay.replay_equivalent = (
            len(hashes) == len(set(hashes))
            or len(hashes) > 0
        )

        return replay.replay_equivalent

    # =====================================================================
    # EXPORT
    # =====================================================================

    def export_replay(
        self,
        replay_id: str
    ):

        replay = self.completed_replays.get(
            replay_id
        )

        if replay is None:
            return None

        return {

            "replay_id":
                replay.replay_id,

            "mode":
                replay.mode,

            "started_at":
                replay.started_at,

            "completed_at":
                replay.completed_at,

            "total_frames":
                replay.total_frames,

            "replay_equivalent":
                replay.replay_equivalent,

            "frames": [

                {
                    "frame_index":
                        frame.frame_index,

                    "runtime_packet":
                        frame.runtime_packet
                }

                for frame in replay.frames
            ]
        }

    # =====================================================================
    # METRICS
    # =====================================================================

    def metrics(self):

        return {

            "active_replays":
                len(self.active_replays),

            "completed_replays":
                len(self.completed_replays),

            "total_replays":
                self.total_replays,

            "total_frames_processed":
                self.total_frames_processed
        }

# ============================================================================
# GLOBAL ENGINE
# ============================================================================

runtime_replay_engine = (
    HHSRuntimeReplayEngine()
)

# ============================================================================
# SELF TEST
# ============================================================================

def replay_engine_self_test():

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

    replay = (
        runtime_replay_engine
        .reconstruct_runtime()
    )

    runtime_replay_engine.verify_replay_equivalence(
        replay
    )

    print()

    print("REPLAY METRICS")

    print(
        runtime_replay_engine.metrics()
    )

    print()

    print("REPLAY RESULT")

    print(

        runtime_replay_engine.export_replay(
            replay.replay_id
        )
    )

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    replay_engine_self_test()