"""
hhs_state_layer_v1.py

Deterministic State Machine Layer for the HHS General Programming Environment.

Purpose
-------
Add canonical, evolving, kernel-audited state.

This is the missing OS/runtime layer between symbolic events and GUI/program state.

State transition flow:
    STATE_t
    + EVENT / PATCH
    -> APPLY deterministic diff
    -> STATE_t+1
    -> audit state mass through AuditedRunner
    -> commit transition receipt
    -> append version history

Rules
-----
- State is never overwritten without a patch receipt.
- Every state transition has parent_state_hash72 and state_hash72.
- Reads do not mutate state.
- Writes produce receipts.
- Failed writes quarantine and do not advance canonical state.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import copy
import json
import time

from hhs_general_runtime_layer_v1 import (
    AuditedRunner,
    DEFAULT_KERNEL_PATH,
    canonicalize_for_hash72,
)


STATE_LAYER_VERSION = "HHS_STATE_LAYER_V1"
GENESIS_STATE_HASH72 = "H72N-STATE-GENESIS"


class HHSStateError(RuntimeError):
    pass


@dataclass(frozen=True)
class StatePatch:
    op: str
    path: str
    value: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StateTransitionRecord:
    version: int
    parent_state_hash72: str
    state_hash72: str
    patch_hash72: str
    receipt_hash72: str
    operation: str
    path: str
    locked: bool
    quarantine: bool
    reason: str
    created_at: float
    patch: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HHSStateLayerV1:
    def __init__(
        self,
        *,
        initial_state: Optional[Dict[str, Any]] = None,
        runner: Optional[AuditedRunner] = None,
        kernel_path: str | Path = DEFAULT_KERNEL_PATH,
    ):
        self.runner = runner or AuditedRunner(kernel_path)
        self.state: Dict[str, Any] = copy.deepcopy(initial_state or {})
        self.version = 0
        self.history: List[StateTransitionRecord] = []
        self.state_hash72 = self._hash_state(self.state) if self.state else GENESIS_STATE_HASH72

    # ------------------------------------------------------------------
    # Canonical hashing / addressing
    # ------------------------------------------------------------------

    def _hash_state(self, state: Dict[str, Any]) -> str:
        return self.runner.authority.commit(
            {
                "layer": STATE_LAYER_VERSION,
                "state": canonicalize_for_hash72(state),
            },
            domain="HHS_STATE",
        )

    def _hash_patch(self, patch: StatePatch) -> str:
        return self.runner.authority.commit(
            {
                "layer": STATE_LAYER_VERSION,
                "patch": patch.to_dict(),
                "parent_state_hash72": self.state_hash72,
                "version": self.version,
            },
            domain="HHS_STATE_PATCH",
        )

    @staticmethod
    def split_path(path: str) -> List[str]:
        if not path or path == ".":
            return []
        return [p for p in path.strip(".").split(".") if p]

    def snapshot(self) -> Dict[str, Any]:
        return {
            "layer": STATE_LAYER_VERSION,
            "version": self.version,
            "state_hash72": self.state_hash72,
            "state": canonicalize_for_hash72(self.state),
            "history_count": len(self.history),
            "runner_tip_hash72": self.runner.commitments.tip_hash72,
        }

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def get(self, path: str, default: Any = None) -> Any:
        parts = self.split_path(path)
        node: Any = self.state
        for part in parts:
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return default
        return copy.deepcopy(node)

    def exists(self, path: str) -> bool:
        marker = object()
        return self.get(path, marker) is not marker

    # ------------------------------------------------------------------
    # Patch application
    # ------------------------------------------------------------------

    def _set_path(self, state: Dict[str, Any], path: str, value: Any) -> None:
        parts = self.split_path(path)
        if not parts:
            if not isinstance(value, dict):
                raise HHSStateError("root state must be a dict")
            state.clear()
            state.update(copy.deepcopy(value))
            return

        node = state
        for part in parts[:-1]:
            if part not in node:
                node[part] = {}
            if not isinstance(node[part], dict):
                raise HHSStateError(f"path collision at {part}: non-dict node")
            node = node[part]
        node[parts[-1]] = copy.deepcopy(value)

    def _delete_path(self, state: Dict[str, Any], path: str) -> None:
        parts = self.split_path(path)
        if not parts:
            state.clear()
            return

        node = state
        for part in parts[:-1]:
            if not isinstance(node, dict) or part not in node:
                return
            node = node[part]
        if isinstance(node, dict):
            node.pop(parts[-1], None)

    def _merge_path(self, state: Dict[str, Any], path: str, value: Dict[str, Any]) -> None:
        existing = self.get(path, {})
        if existing is None:
            existing = {}
        if not isinstance(existing, dict) or not isinstance(value, dict):
            raise HHSStateError("MERGE requires dict at target and dict value")
        merged = copy.deepcopy(existing)
        merged.update(copy.deepcopy(value))
        self._set_path(state, path, merged)

    def apply_patch_to_copy(self, patch: StatePatch) -> Dict[str, Any]:
        next_state = copy.deepcopy(self.state)

        if patch.op == "SET":
            self._set_path(next_state, patch.path, patch.value)
        elif patch.op == "DELETE":
            self._delete_path(next_state, patch.path)
        elif patch.op == "MERGE":
            self._merge_path(next_state, patch.path, patch.value)
        else:
            raise HHSStateError(f"unknown patch op: {patch.op}")

        return next_state

    # ------------------------------------------------------------------
    # State audit
    # ------------------------------------------------------------------

    def state_mass(self, state: Dict[str, Any]) -> int:
        """
        Deterministic state mass for kernel remap.

        Uses canonical JSON length plus structural counts. This is not the
        authority itself; it is the manifold audit carrier for the state.
        """
        encoded = json.dumps(canonicalize_for_hash72(state), sort_keys=True, separators=(",", ":"))
        node_count = self._node_count(state)
        return max(1, len(encoded) + node_count)

    def _node_count(self, obj: Any) -> int:
        if isinstance(obj, dict):
            return 1 + sum(self._node_count(v) for v in obj.values())
        if isinstance(obj, list):
            return 1 + sum(self._node_count(v) for v in obj)
        return 1

    # ------------------------------------------------------------------
    # Write transition
    # ------------------------------------------------------------------

    def apply_patch(self, patch: StatePatch) -> Dict[str, Any]:
        parent_hash = self.state_hash72
        patch_hash = self._hash_patch(patch)

        try:
            next_state = self.apply_patch_to_copy(patch)
            next_hash = self._hash_state(next_state)
            mass = self.state_mass(next_state)

            audit = self.runner.execute(
                "SUM",
                [mass],
                input_payload={
                    "layer": STATE_LAYER_VERSION,
                    "form": "STATE_TRANSITION_AUDIT",
                    "parent_state_hash72": parent_hash,
                    "patch_hash72": patch_hash,
                    "next_state_hash72": next_hash,
                    "patch": patch.to_dict(),
                    "state_mass": mass,
                },
            )

            locked = bool(audit.get("ok"))
            quarantine = not locked
            reason = "" if locked else audit.get("reason", "state transition audit failed")
            receipt = audit.get("receipt", {})
            receipt_hash = receipt.get("receipt_hash72", "")

            record = StateTransitionRecord(
                version=self.version + 1 if locked else self.version,
                parent_state_hash72=parent_hash,
                state_hash72=next_hash if locked else parent_hash,
                patch_hash72=patch_hash,
                receipt_hash72=receipt_hash,
                operation=patch.op,
                path=patch.path,
                locked=locked,
                quarantine=quarantine,
                reason=reason,
                created_at=time.time(),
                patch=patch.to_dict(),
            )

            if locked:
                self.state = next_state
                self.version += 1
                self.state_hash72 = next_hash

            self.history.append(record)

            return {
                "ok": locked,
                "quarantine": quarantine,
                "reason": reason,
                "transition": record.to_dict(),
                "audit": audit,
                "snapshot": self.snapshot(),
            }

        except Exception as exc:
            record = StateTransitionRecord(
                version=self.version,
                parent_state_hash72=parent_hash,
                state_hash72=parent_hash,
                patch_hash72=patch_hash,
                receipt_hash72="",
                operation=patch.op,
                path=patch.path,
                locked=False,
                quarantine=True,
                reason=f"{type(exc).__name__}: {exc}",
                created_at=time.time(),
                patch=patch.to_dict(),
            )
            self.history.append(record)
            return {
                "ok": False,
                "quarantine": True,
                "reason": record.reason,
                "transition": record.to_dict(),
                "snapshot": self.snapshot(),
            }

    # Convenience writes

    def set(self, path: str, value: Any, **metadata: Any) -> Dict[str, Any]:
        return self.apply_patch(StatePatch("SET", path, value, metadata))

    def delete(self, path: str, **metadata: Any) -> Dict[str, Any]:
        return self.apply_patch(StatePatch("DELETE", path, None, metadata))

    def merge(self, path: str, value: Dict[str, Any], **metadata: Any) -> Dict[str, Any]:
        return self.apply_patch(StatePatch("MERGE", path, value, metadata))

    # ------------------------------------------------------------------
    # Replay / verification
    # ------------------------------------------------------------------

    def replay_from_history(self, history: Optional[List[StateTransitionRecord]] = None) -> Dict[str, Any]:
        replay_state: Dict[str, Any] = {}
        replay_hash = GENESIS_STATE_HASH72
        version = 0

        records = history if history is not None else self.history

        for idx, rec in enumerate(records):
            r = rec.to_dict() if hasattr(rec, "to_dict") else rec
            if not r.get("locked"):
                continue

            if r["parent_state_hash72"] != replay_hash:
                return {
                    "ok": False,
                    "index": idx,
                    "reason": "parent_state_hash72 mismatch",
                    "expected": replay_hash,
                    "actual": r["parent_state_hash72"],
                }

            patch = StatePatch(**r["patch"])

            # Apply against replay_state manually using a temporary layer.
            temp = HHSStateLayerV1(initial_state=replay_state, runner=self.runner)
            temp.state_hash72 = replay_hash
            next_state = temp.apply_patch_to_copy(patch)
            next_hash = self._hash_state(next_state)

            if next_hash != r["state_hash72"]:
                return {
                    "ok": False,
                    "index": idx,
                    "reason": "state_hash72 mismatch",
                    "expected": next_hash,
                    "actual": r["state_hash72"],
                }

            replay_state = next_state
            replay_hash = next_hash
            version += 1

        return {
            "ok": replay_hash == self.state_hash72,
            "replay_state_hash72": replay_hash,
            "current_state_hash72": self.state_hash72,
            "version": version,
            "state": canonicalize_for_hash72(replay_state),
        }

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: str | Path) -> Dict[str, Any]:
        path = Path(path)
        payload = {
            "format": "HHS_STATE_LAYER_SNAPSHOT_V1",
            "snapshot": self.snapshot(),
            "history": [h.to_dict() for h in self.history],
            "receipts": [r.to_dict() for r in self.runner.commitments.receipts],
            "chain": self.runner.commitments.verify_chain(),
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return {
            "ok": True,
            "saved": str(path),
            "state_hash72": self.state_hash72,
            "version": self.version,
        }

    @classmethod
    def load(cls, path: str | Path, *, kernel_path: str | Path = DEFAULT_KERNEL_PATH) -> "HHSStateLayerV1":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("format") != "HHS_STATE_LAYER_SNAPSHOT_V1":
            raise HHSStateError("not an HHS_STATE_LAYER_SNAPSHOT_V1 file")
        snapshot = payload["snapshot"]
        layer = cls(initial_state=snapshot.get("state", {}), kernel_path=kernel_path)
        layer.version = snapshot["version"]
        layer.state_hash72 = snapshot["state_hash72"]
        layer.history = [StateTransitionRecord(**h) for h in payload.get("history", [])]
        return layer


def demo() -> Dict[str, Any]:
    state = HHSStateLayerV1()
    a = state.set("windows.AUDIT_LOG", {"x": 10, "y": 10, "w": 400, "h": 300, "z": 1})
    b = state.merge("windows.AUDIT_LOG", {"x": 40, "y": 80})
    c = state.set("variables.counter", 1)
    r = state.replay_from_history()
    s = state.save("/mnt/data/hhs_state_layer_demo.hhsstate")
    return {
        "set_window": a,
        "move_window": b,
        "set_counter": c,
        "replay": r,
        "save": s,
    }


def main() -> None:
    print(json.dumps(demo(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
