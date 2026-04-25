"""
hhs_input_bridge_v1.py

Physical/user input bridge for HHS GUI symbolic commitments.

Maps user input events into GUI macro calls committed through
TERMINAL_HHSPROG_V5_MACRO_ALGEBRA.

CLI:
    python hhs_input_bridge_v1.py click TARGET X Y
    python hhs_input_bridge_v1.py drag TARGET X1 Y1 X2 Y2
    python hhs_input_bridge_v1.py key KEY MODS
    python hhs_input_bridge_v1.py frame FRAME_ID PHASE
    python hhs_input_bridge_v1.py demo
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse
import json
import sys
import time

from terminal_hhsprog_v5_macro_algebra import HHSMacroAlgebraTerminalV5
from hhs_general_runtime_layer_v1 import DEFAULT_KERNEL_PATH


INPUT_BRIDGE_VERSION = "HHS_INPUT_BRIDGE_V1"


@dataclass(frozen=True)
class HHSGUIInputEvent:
    event_type: str
    target: str
    payload: Dict[str, Any]
    created_at: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HHSInputBridgeV1:
    def __init__(self, kernel_path: str | Path = DEFAULT_KERNEL_PATH):
        self.terminal = HHSMacroAlgebraTerminalV5(kernel_path)
        self.events: List[Dict[str, Any]] = []
        self._ensure_gui_macros()

    def _ensure_gui_macros(self) -> None:
        macros = [
            "DEF GUI_EVENT(type,target,payload) := List(type,target,payload)",
            "DEF CLICK_EVENT(target,x,y) := GUI_EVENT(click,target,List(x,y))",
            "DEF DRAG_EVENT(target,x1,y1,x2,y2) := GUI_EVENT(drag,target,List(x1,y1,x2,y2))",
            "DEF KEY_EVENT(key,mods) := GUI_EVENT(key,key,mods)",
            "DEF RENDER_FRAME(frame_id,phase,windows,receipts) := List(frame_id,phase,windows,receipts)",
            "DEF RECEIPT_PANEL(receipt,gate,phase) := List(receipt,gate,phase)",
            "DEF TRACE_ROW(step,op,hash,status) := List(step,op,hash,status)",
        ]
        for macro in macros:
            self.terminal.dispatch(macro)

    @staticmethod
    def quote_atom(value: Any) -> str:
        if isinstance(value, str):
            if value.replace("_", "").replace("-", "").isalnum():
                return value
            return json.dumps(value)
        return str(value)

    def commit_event(self, event: HHSGUIInputEvent, macro_call: str) -> Dict[str, Any]:
        result = self.terminal.dispatch(macro_call)
        record = {
            "bridge": INPUT_BRIDGE_VERSION,
            "event": event.to_dict(),
            "macro_call": macro_call,
            "result": result,
            "tip_hash72": self.terminal.runner.commitments.tip_hash72,
        }
        self.events.append(record)
        return record

    def click(self, target: str, x: Any, y: Any) -> Dict[str, Any]:
        event = HHSGUIInputEvent("click", target, {"x": x, "y": y}, time.time())
        call = f"CLICK_EVENT({self.quote_atom(target)},{self.quote_atom(x)},{self.quote_atom(y)})"
        return self.commit_event(event, call)

    def drag(self, target: str, x1: Any, y1: Any, x2: Any, y2: Any) -> Dict[str, Any]:
        event = HHSGUIInputEvent("drag", target, {"x1": x1, "y1": y1, "x2": x2, "y2": y2}, time.time())
        call = (
            f"DRAG_EVENT({self.quote_atom(target)},"
            f"{self.quote_atom(x1)},{self.quote_atom(y1)},"
            f"{self.quote_atom(x2)},{self.quote_atom(y2)})"
        )
        return self.commit_event(event, call)

    def key(self, key: str, mods: str = "none") -> Dict[str, Any]:
        event = HHSGUIInputEvent("key", key, {"mods": mods}, time.time())
        call = f"KEY_EVENT({self.quote_atom(key)},{self.quote_atom(mods)})"
        return self.commit_event(event, call)

    def render_frame(self, frame_id: str, phase: Any, windows: str = "windows", receipts: str = "receipts") -> Dict[str, Any]:
        event = HHSGUIInputEvent("render_frame", frame_id, {"phase": phase, "windows": windows, "receipts": receipts}, time.time())
        call = (
            f"RENDER_FRAME({self.quote_atom(frame_id)},"
            f"{self.quote_atom(phase)},"
            f"{self.quote_atom(windows)},"
            f"{self.quote_atom(receipts)})"
        )
        return self.commit_event(event, call)

    def save(self, path: str | Path) -> Dict[str, Any]:
        path = Path(path)
        payload = {
            "format": "HHS_INPUT_BRIDGE_RUN_V1",
            "bridge": INPUT_BRIDGE_VERSION,
            "events": self.events,
            "receipts": [r.to_dict() for r in self.terminal.runner.commitments.receipts],
            "chain": self.terminal.runner.commitments.verify_chain(),
            "tip_hash72": self.terminal.runner.commitments.tip_hash72,
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return {
            "ok": True,
            "saved": str(path),
            "event_count": len(self.events),
            "tip_hash72": self.terminal.runner.commitments.tip_hash72,
        }


def demo() -> Dict[str, Any]:
    bridge = HHSInputBridgeV1()
    click = bridge.click("AUDIT_LOG", 10, 20)
    drag = bridge.drag("AUDIT_LOG", 10, 20, 40, 80)
    key = bridge.key("ENTER", "CTRL")
    frame = bridge.render_frame("FRAME_0", 0)
    saved = bridge.save("/mnt/data/hhs_input_bridge_demo.hhsinput")
    return {"click": click, "drag": drag, "key": key, "frame": frame, "saved": saved}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="HHS input event bridge")
    sub = parser.add_subparsers(dest="command", required=True)

    p_click = sub.add_parser("click")
    p_click.add_argument("target")
    p_click.add_argument("x")
    p_click.add_argument("y")

    p_drag = sub.add_parser("drag")
    p_drag.add_argument("target")
    p_drag.add_argument("x1")
    p_drag.add_argument("y1")
    p_drag.add_argument("x2")
    p_drag.add_argument("y2")

    p_key = sub.add_parser("key")
    p_key.add_argument("key")
    p_key.add_argument("mods", nargs="?", default="none")

    p_frame = sub.add_parser("frame")
    p_frame.add_argument("frame_id")
    p_frame.add_argument("phase")

    sub.add_parser("demo")
    parser.add_argument("--save", default=None)

    args = parser.parse_args(argv)
    bridge = HHSInputBridgeV1()

    if args.command == "click":
        result = bridge.click(args.target, args.x, args.y)
    elif args.command == "drag":
        result = bridge.drag(args.target, args.x1, args.y1, args.x2, args.y2)
    elif args.command == "key":
        result = bridge.key(args.key, args.mods)
    elif args.command == "frame":
        result = bridge.render_frame(args.frame_id, args.phase)
    elif args.command == "demo":
        result = demo()
    else:
        result = {"ok": False, "error": "unknown command"}

    if args.save:
        result["save_report"] = bridge.save(args.save)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
