from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


@dataclass
class TransformationEdit:
    item_id: str
    new_text: str


@dataclass
class TransformationPatch:
    edits: List[TransformationEdit]
    justification: str
    predicted_effect: Dict[str, Any]
    patch_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "edits": [asdict(e) for e in self.edits],
            "justification": self.justification,
            "predicted_effect": self.predicted_effect,
            "patch_hash72": self.patch_hash72,
        }


def build_transformation_patch(edits: List[TransformationEdit], justification: str, predicted_effect: Dict[str, Any]) -> TransformationPatch:
    payload = {
        "edits": [asdict(e) for e in edits],
        "justification": justification,
        "predicted_effect": predicted_effect,
    }

    h = hash72_digest(("hhs_transformation_patch_v1", payload), width=24)

    return TransformationPatch(
        edits=edits,
        justification=justification,
        predicted_effect=predicted_effect,
        patch_hash72=h,
    )
