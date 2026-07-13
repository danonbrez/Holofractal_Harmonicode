"""Visual emulator session substrate for Pass 049."""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Mapping, Optional
import uuid

from hhs_backend.runtime.runtime_workspace_object_v1 import VERSION, AUTHORITY, hash72

SESSION_SCHEMA = "HHS_EMULATOR_SESSION_V1"
SESSION_COMMAND_SCHEMA = "HHS_EMULATOR_SESSION_COMMAND_V1"

BOUNDED_RUN_LIMIT = 32


def _unique(prefix: str) -> str:
    return f"{prefix}:{uuid.uuid4().hex}"


@dataclass
class VisualEmulatorSession:
    schema: str = SESSION_SCHEMA
    version: str = VERSION
    session_id: str = field(default_factory=lambda: _unique("emulator"))
    project_id: str = "project:default"
    program_artifact_id: str = "artifact:receipt-only-plan"
    initial_state_root_hash72: str = ""
    current_state_root_hash72: str = ""
    tick: int = 0
    mode: str = "PAUSED"
    execution_policy: str = "AUTHORIZED_KERNEL_EMULATION"
    receipt_tip_hash72: str = ""
    branch_id: str = "branch:main"
    snapshot_ids: List[str] = field(default_factory=list)
    receipts: List[Dict[str, Any]] = field(default_factory=list)
    parent_receipt_hash72: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class VisualEmulatorRuntime:
    def __init__(self) -> None:
        self.sessions: Dict[str, VisualEmulatorSession] = {}

    def create_session(self, project_id: str, program_artifact_id: str, initial_state: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        initial_root = hash72("HHS_EMULATOR_INITIAL_STATE_V1", dict(initial_state or {"state": "zero"}))
        session = VisualEmulatorSession(
            project_id=project_id,
            program_artifact_id=program_artifact_id,
            initial_state_root_hash72=initial_root,
            current_state_root_hash72=initial_root,
            receipt_tip_hash72=initial_root,
        )
        self.sessions[session.session_id] = session
        result = {
            "schema": "HHS_EMULATOR_SESSION_CREATE_RESULT_V1",
            "version": VERSION,
            "ok": True,
            "status": "EMULATOR_SESSION_CREATED",
            "session": session.to_dict(),
        }
        result["receipt_hash72"] = hash72("HHS_EMULATOR_SESSION_CREATE_RESULT_V1", result)
        return result

    def command(self, session_id: str, command: str, payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        if session_id not in self.sessions:
            return {"schema": "HHS_EMULATOR_COMMAND_REJECTION_V1", "ok": False, "status": "REJECT_EMULATOR_SESSION_UNKNOWN"}
        session = self.sessions[session_id]
        payload_dict = dict(payload or {})
        if command == "run" and int(payload_dict.get("steps") or 0) > BOUNDED_RUN_LIMIT:
            return {"schema": "HHS_EMULATOR_COMMAND_REJECTION_V1", "ok": False, "status": "REJECT_EMULATOR_UNBOUNDED_RUN", "limit": BOUNDED_RUN_LIMIT}
        if command == "restore" and payload_dict.get("snapshot_id") not in session.snapshot_ids:
            return {"schema": "HHS_EMULATOR_COMMAND_REJECTION_V1", "ok": False, "status": "REJECT_SNAPSHOT_ROOT_MISMATCH"}
        if command == "branch" and payload_dict.get("parent_receipt_hash72") not in [r.get("receipt_hash72") for r in session.receipts] and session.receipts:
            return {"schema": "HHS_EMULATOR_COMMAND_REJECTION_V1", "ok": False, "status": "REJECT_REPLAY_PARENT_MISMATCH"}

        pre = session.current_state_root_hash72
        if command == "step":
            session.tick += 1
            session.mode = "PAUSED"
        elif command == "run":
            steps = max(1, int(payload_dict.get("steps") or 1))
            session.tick += steps
            session.mode = "PAUSED"
        elif command == "pause":
            session.mode = "PAUSED"
        elif command == "resume":
            session.mode = "RUNNING"
        elif command == "stop":
            session.mode = "STOPPED"
        elif command == "snapshot":
            snapshot_id = _unique("snapshot")
            session.snapshot_ids.append(snapshot_id)
            session.mode = "SNAPSHOTTED"
        elif command == "restore":
            session.mode = "PAUSED"
        elif command == "replay":
            session.mode = "REPLAYING"
        elif command == "branch":
            session.branch_id = _unique("branch")
            session.parent_receipt_hash72 = payload_dict.get("parent_receipt_hash72") or session.receipt_tip_hash72
            session.mode = "PAUSED"
        elif command == "close":
            session.mode = "CLOSED"
        post = hash72("HHS_EMULATOR_STATE_TRANSITION_V1", {
            "session_id": session_id,
            "command": command,
            "pre": pre,
            "tick": session.tick,
            "mode": session.mode,
            "branch_id": session.branch_id,
        })
        session.current_state_root_hash72 = post
        receipt = {
            "schema": "HHS_EMULATOR_STEP_RECEIPT_V1",
            "session_id": session_id,
            "command": command,
            "pre_state_hash72": pre,
            "post_state_hash72": post,
            "tick": session.tick,
            "mode": session.mode,
            "history_erased": False,
            "authority": AUTHORITY,
        }
        receipt["receipt_hash72"] = hash72("HHS_EMULATOR_STEP_RECEIPT_V1", receipt)
        session.receipt_tip_hash72 = receipt["receipt_hash72"]
        session.receipts.append(receipt)
        return {
            "schema": "HHS_EMULATOR_COMMAND_RESULT_V1",
            "version": VERSION,
            "ok": True,
            "status": f"EMULATOR_{command.upper()}_COMMITTED",
            "session": session.to_dict(),
            "receipt": receipt,
        }


def visual_emulator_session_self_test() -> Dict[str, Any]:
    runtime = VisualEmulatorRuntime()
    created = runtime.create_session("project:pass049", "artifact:hhs-ir")
    session_id = created["session"]["session_id"]
    step = runtime.command(session_id, "step")
    run = runtime.command(session_id, "run", {"steps": 3})
    pause = runtime.command(session_id, "pause")
    snapshot = runtime.command(session_id, "snapshot")
    restore = runtime.command(session_id, "restore", {"snapshot_id": snapshot["session"]["snapshot_ids"][-1]})
    replay = runtime.command(session_id, "replay")
    branch = runtime.command(session_id, "branch", {"parent_receipt_hash72": step["receipt"]["receipt_hash72"]})
    unbounded = runtime.command(session_id, "run", {"steps": 999})
    unknown = runtime.command("emulator:missing", "step")
    return {
        "schema": "HHS_VISUAL_EMULATOR_SESSION_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(created.get("ok") and step.get("ok") and run.get("ok") and pause.get("ok") and snapshot.get("ok") and restore.get("ok") and replay.get("ok") and branch.get("ok") and not unbounded.get("ok") and not unknown.get("ok")),
        "created": created,
        "step": step,
        "run": run,
        "pause": pause,
        "snapshot": snapshot,
        "restore": restore,
        "replay": replay,
        "branch": branch,
        "unbounded_rejection": unbounded,
        "unknown_session_rejection": unknown,
        "constraint": "REWIND_OR_REPLAY_DOES_NOT_ERASE_HISTORY",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(visual_emulator_session_self_test(), indent=2, sort_keys=True, default=str))
