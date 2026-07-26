# ============================================================================
# hhs_backend/runtime/runtime_replay_engine.py
# HARMONICODE / HHS
# CANONICAL RUNTIME REPLAY ENGINE
# ============================================================================

from __future__ import annotations

import copy
import json
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field, is_dataclass
from typing import Any, Dict, List, Mapping, Optional

from hhs_storage.runtime_state_store_v1 import runtime_state_store

logger = logging.getLogger("HHS_REPLAY")

MODE_RECONSTRUCT = "reconstruct"
MODE_BRANCH_SIMULATION = "branch-simulation"
MODE_PREDICTIVE = "predictive"
MODE_SANDBOX = "sandbox"
MODE_LIVE_WINDOW = "live-window"


@dataclass
class HHSReplayFrame:
    replay_id: str
    frame_index: int
    created_at: float
    runtime_packet: Dict[str, Any]
    mode: str


@dataclass
class HHSReplayResult:
    replay_id: str
    mode: str
    started_at: float
    completed_at: float
    total_frames: int
    replay_equivalent: bool
    frames: List[HHSReplayFrame] = field(default_factory=list)


class HHSRuntimeReplayEngine:
    """Canonical deterministic replay subsystem with a bounded live window."""

    def __init__(self):
        self.lock = threading.RLock()
        self.active_replays: Dict[str, HHSReplayResult] = {}
        self.completed_replays: Dict[str, HHSReplayResult] = {}
        self.total_replays = 0
        self.total_frames_processed = 0
        self.live_packets: List[Dict[str, Any]] = []
        self.live_packet_limit = 256

    def _create_replay_result(self, mode: str) -> HHSReplayResult:
        replay_id = str(uuid.uuid4())
        result = HHSReplayResult(
            replay_id=replay_id,
            mode=mode,
            started_at=time.time(),
            completed_at=0.0,
            total_frames=0,
            replay_equivalent=True,
        )
        with self.lock:
            self.active_replays[replay_id] = result
            self.total_replays += 1
        return result

    def _complete(self, result: HHSReplayResult) -> HHSReplayResult:
        result.total_frames = len(result.frames)
        result.completed_at = time.time()
        with self.lock:
            self.completed_replays[result.replay_id] = result
            self.active_replays.pop(result.replay_id, None)
        return result

    @staticmethod
    def _decode_payload(value: Any) -> Dict[str, Any]:
        if value is None:
            return {}
        if isinstance(value, str):
            decoded = json.loads(value)
            return dict(decoded) if isinstance(decoded, Mapping) else {}
        if isinstance(value, Mapping):
            return copy.deepcopy(dict(value))
        if is_dataclass(value):
            if hasattr(value, "runtime_state"):
                runtime_state = copy.deepcopy(getattr(value, "runtime_state"))
                if isinstance(runtime_state, Mapping):
                    runtime_state = dict(runtime_state)
                    if "runtime" in runtime_state:
                        return runtime_state
                    return {"runtime": runtime_state}
            return copy.deepcopy(vars(value))
        return {}

    @classmethod
    def _row_payload(cls, row: Any) -> Dict[str, Any]:
        if isinstance(row, Mapping):
            if "payload" in row:
                return cls._decode_payload(row.get("payload"))
            if "runtime_packet" in row:
                return cls._decode_payload(row.get("runtime_packet"))
            return cls._decode_payload(row)
        if hasattr(row, "payload"):
            return cls._decode_payload(getattr(row, "payload"))
        return cls._decode_payload(row)

    def ingest_live_packet(
        self,
        packet: Mapping[str, Any],
        *,
        history_limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        packet_dict = copy.deepcopy(dict(packet))
        runtime = dict(packet_dict.get("runtime") or {})
        if not runtime.get("state_hash72"):
            raise ValueError("live replay packet requires runtime.state_hash72")
        limit = max(1, int(history_limit or self.live_packet_limit))
        with self.lock:
            identity = (
                runtime.get("step"),
                runtime.get("state_hash72"),
                runtime.get("receipt_hash72"),
            )
            if self.live_packets:
                previous = dict(self.live_packets[-1].get("runtime") or {})
                previous_identity = (
                    previous.get("step"),
                    previous.get("state_hash72"),
                    previous.get("receipt_hash72"),
                )
                if identity == previous_identity:
                    return {
                        "ingested": False,
                        "duplicate": True,
                        "live_packets": len(self.live_packets),
                    }
            self.live_packets.append(packet_dict)
            overflow = len(self.live_packets) - limit
            if overflow > 0:
                del self.live_packets[:overflow]
            return {
                "ingested": True,
                "duplicate": False,
                "live_packets": len(self.live_packets),
            }

    def live_replay_window(self, limit: int = 10) -> HHSReplayResult:
        result = self._create_replay_result(MODE_LIVE_WINDOW)
        with self.lock:
            packets = copy.deepcopy(self.live_packets[-max(1, int(limit)):])
        for index, packet in enumerate(packets):
            result.frames.append(HHSReplayFrame(
                replay_id=result.replay_id,
                frame_index=index,
                created_at=time.time(),
                runtime_packet=packet,
                mode=MODE_LIVE_WINDOW,
            ))
            self.total_frames_processed += 1
        if not result.frames:
            result.replay_equivalent = False
        return self._complete(result)

    def reconstruct_runtime(self, limit: int = 100) -> HHSReplayResult:
        result = self._create_replay_result(MODE_RECONSTRUCT)
        records = runtime_state_store.replay_chain(limit=limit)
        for index, row in enumerate(records):
            payload = self._row_payload(row)
            result.frames.append(HHSReplayFrame(
                replay_id=result.replay_id,
                frame_index=index,
                created_at=time.time(),
                runtime_packet=payload,
                mode=MODE_RECONSTRUCT,
            ))
            self.total_frames_processed += 1
        if not result.frames:
            result.replay_equivalent = False
        logger.info("Replay reconstruction complete: %s", result.replay_id)
        return self._complete(result)

    def simulate_branch(
        self,
        mutation: Optional[Dict] = None,
        limit: int = 25,
    ) -> HHSReplayResult:
        result = self._create_replay_result(MODE_BRANCH_SIMULATION)
        records = runtime_state_store.replay_chain(limit=limit)
        for index, row in enumerate(records):
            cloned = self._row_payload(row)
            if mutation:
                cloned.setdefault("runtime", {}).update(mutation)
            result.frames.append(HHSReplayFrame(
                replay_id=result.replay_id,
                frame_index=index,
                created_at=time.time(),
                runtime_packet=cloned,
                mode=MODE_BRANCH_SIMULATION,
            ))
            self.total_frames_processed += 1
        if not result.frames:
            result.replay_equivalent = False
        logger.info("Branch simulation complete: %s", result.replay_id)
        return self._complete(result)

    def _latest_predictive_base(self) -> Dict[str, Any]:
        with self.lock:
            if self.live_packets:
                return copy.deepcopy(self.live_packets[-1])

        latest = runtime_state_store.latest_snapshot()
        payload = self._decode_payload(latest)
        if payload:
            return payload

        replay_records = getattr(runtime_state_store, "replay_records", None) or []
        if replay_records:
            return self._row_payload(replay_records[-1])
        return {}

    def predictive_replay(self, horizon: int = 10) -> HHSReplayResult:
        result = self._create_replay_result(MODE_PREDICTIVE)
        payload = self._latest_predictive_base()
        runtime = dict(payload.get("runtime") or {})
        if not runtime:
            result.replay_equivalent = False
            return self._complete(result)

        current_step = int(runtime.get("step") or 0)
        for index in range(max(0, int(horizon))):
            synthetic = copy.deepcopy(payload)
            synthetic_runtime = synthetic.setdefault("runtime", {})
            synthetic_runtime["step"] = current_step + index + 1
            synthetic_runtime["predicted"] = True
            result.frames.append(HHSReplayFrame(
                replay_id=result.replay_id,
                frame_index=index,
                created_at=time.time(),
                runtime_packet=synthetic,
                mode=MODE_PREDICTIVE,
            ))
            self.total_frames_processed += 1
        if not result.frames:
            result.replay_equivalent = False
        logger.info("Predictive replay complete: %s", result.replay_id)
        return self._complete(result)

    def verify_replay_equivalence(self, replay: HHSReplayResult) -> bool:
        if replay.total_frames == 0:
            replay.replay_equivalent = False
            return False
        hashes = [
            str((frame.runtime_packet.get("runtime") or {}).get("state_hash72") or "")
            for frame in replay.frames
        ]
        replay.replay_equivalent = bool(hashes and all(hashes))
        return replay.replay_equivalent

    def export_replay(self, replay_id: str):
        replay = self.completed_replays.get(replay_id)
        if replay is None:
            return None
        return {
            "replay_id": replay.replay_id,
            "mode": replay.mode,
            "started_at": replay.started_at,
            "completed_at": replay.completed_at,
            "total_frames": replay.total_frames,
            "replay_equivalent": replay.replay_equivalent,
            "frames": [
                {
                    "frame_index": frame.frame_index,
                    "runtime_packet": frame.runtime_packet,
                }
                for frame in replay.frames
            ],
        }

    def metrics(self):
        with self.lock:
            return {
                "active_replays": len(self.active_replays),
                "completed_replays": len(self.completed_replays),
                "total_replays": self.total_replays,
                "total_frames_processed": self.total_frames_processed,
                "live_packets": len(self.live_packets),
                "live_packet_limit": self.live_packet_limit,
            }


runtime_replay_engine = HHSRuntimeReplayEngine()


def replay_engine_self_test():
    packet = {
        "runtime": {
            "step": 1,
            "state_hash72": "abc123",
            "receipt_hash72": "xyz789",
        }
    }
    runtime_state_store.store_replay_record(packet)
    runtime_replay_engine.ingest_live_packet(packet)
    replay = runtime_replay_engine.live_replay_window()
    runtime_replay_engine.verify_replay_equivalence(replay)
    print(runtime_replay_engine.export_replay(replay.replay_id))


if __name__ == "__main__":
    replay_engine_self_test()
