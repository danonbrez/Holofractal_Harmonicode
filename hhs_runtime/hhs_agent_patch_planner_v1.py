from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List

from hhs_runtime.hhs_transformation_patch_v1 import TransformationEdit, build_transformation_patch


def plan_transformation_patch(packet: Dict[str, Any]) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = list(packet.get("items", []))
    influences: List[Dict[str, Any]] = list(packet.get("influences", []))

    edits: List[TransformationEdit] = []
    target = influences[0] if influences else (items[0] if items else None)

    if target:
        text = str(target.get("text", ""))
        kind = str(target.get("kind", ""))
        if kind == "ORDERED_PRODUCT" and text == "yx":
            replacement = "-xy"
        elif kind == "ORDERED_PRODUCT" and text == "wz":
            replacement = "-zw"
        elif text == "==":
            replacement = "="
        else:
            replacement = text
        edits.append(TransformationEdit(item_id=str(target.get("id", "")), new_text=replacement))

    patch = build_transformation_patch(
        edits=edits,
        justification="Deterministic first-pass convergence patch from highest-influence display item.",
        predicted_effect={
            "phase_shift": int(target.get("phaseIndex", 0)) if target else 0,
            "drift_delta": -1 if edits else 0,
            "mode": "review_only",
        },
    )
    return patch.to_dict()
