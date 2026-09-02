from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from .runtime import SceneState
from .types import GraphicsNode


class AnimationError(ValueError):
    pass


@dataclass(frozen=True)
class LinearTrack:
    node_id: str
    start_frame: int
    end_frame: int
    dx_q16_per_frame: int = 0
    dy_q16_per_frame: int = 0

    def __post_init__(self) -> None:
        if not self.node_id:
            raise AnimationError("P179_ANIMATION_NODE_REQUIRED")
        if self.start_frame < 0 or self.end_frame < self.start_frame:
            raise AnimationError("P179_ANIMATION_FRAME_RANGE")
        for value in (self.dx_q16_per_frame, self.dy_q16_per_frame):
            if not isinstance(value, int) or isinstance(value, bool):
                raise AnimationError("P179_ANIMATION_INTEGER_STEP_REQUIRED")


def scene_at_frame(
    base: SceneState,
    tracks: Iterable[LinearTrack],
    frame_index: int,
) -> SceneState:
    if not isinstance(frame_index, int) or isinstance(frame_index, bool) or frame_index < 0:
        raise AnimationError("P179_ANIMATION_FRAME_INVALID")
    track_map = {track.node_id: track for track in tracks}
    nodes: list[GraphicsNode] = []
    for node in base.nodes:
        track = track_map.get(node.node_id)
        if track is None or frame_index <= track.start_frame:
            nodes.append(node)
            continue
        applied = min(frame_index, track.end_frame) - track.start_frame
        nodes.append(
            replace(
                node,
                x_q16=node.x_q16 + track.dx_q16_per_frame * applied,
                y_q16=node.y_q16 + track.dy_q16_per_frame * applied,
            )
        )
    return SceneState(
        scene_id=base.scene_id,
        width=base.width,
        height=base.height,
        background=base.background,
        nodes=tuple(nodes),
        frame_index=frame_index,
    )
