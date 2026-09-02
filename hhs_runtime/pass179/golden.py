from __future__ import annotations

from .runtime import SceneState
from .types import GraphicsNode, RGBA16, q16


def lattice_run_scene() -> SceneState:
    nodes: list[GraphicsNode] = []
    platform_color = RGBA16(7000, 28000, 50000, 65535)
    glow = RGBA16(15000, 52000, 65535, 65535)
    gold = RGBA16(65535, 47000, 6000, 65535)
    for index, (x, y, w, h) in enumerate(
        [
            (0, 150, 120, 30),
            (145, 150, 80, 30),
            (250, 150, 100, 30),
            (45, 115, 50, 8),
            (180, 100, 55, 8),
        ]
    ):
        nodes.append(
            GraphicsNode(
                node_id=f"platform:{index}",
                kind="RECT",
                x_q16=q16(x),
                y_q16=q16(y),
                w_q16=q16(w),
                h_q16=q16(h),
                color=platform_color,
                layer=10,
            )
        )
    for index, (x, y) in enumerate([(70, 100), (205, 85), (295, 120)]):
        nodes.append(
            GraphicsNode(
                node_id=f"shard:{index}",
                kind="RECT",
                x_q16=q16(x),
                y_q16=q16(y),
                w_q16=q16(5),
                h_q16=q16(5),
                color=gold,
                layer=20,
            )
        )
    nodes.extend(
        [
            GraphicsNode("player", "RECT", q16(20), q16(130), q16(10), q16(18), glow, 30),
            GraphicsNode("closure-gate", "RECT", q16(330), q16(95), q16(8), q16(55), gold, 30),
        ]
    )
    return SceneState(
        scene_id="pass179:golden:lattice-run:nucleus",
        width=360,
        height=180,
        background=RGBA16(800, 1500, 4500, 65535),
        nodes=tuple(nodes),
    )


def motion_5184_scene() -> SceneState:
    nodes: list[GraphicsNode] = []
    width, height = 320, 180
    for index in range(5184):
        phase = index % 216
        r = (phase * 257) % 65536
        g = ((phase * 109 + 72) * 257) % 65536
        b = ((phase * 53 + 144) * 257) % 65536
        x = (index * 37 + (index // 81) * 11) % width
        y = (index * 73 + (index // 64) * 7) % height
        nodes.append(
            GraphicsNode(
                node_id=f"particle:{index:04d}",
                kind="POINT",
                x_q16=q16(x),
                y_q16=q16(y),
                w_q16=q16(1),
                h_q16=q16(1),
                color=RGBA16(r, g, b, 65535),
                layer=index % 81,
            )
        )
    return SceneState(
        scene_id="pass179:golden:motion-5184:nucleus",
        width=width,
        height=height,
        background=RGBA16(0, 0, 1200, 65535),
        nodes=tuple(nodes),
    )


def golden_scene_manifest() -> dict:
    return {
        "schema": "HHS_PASS_179_GOLDEN_SCENE_MANIFEST_V1",
        "lattice_run": {
            "scene_id": lattice_run_scene().scene_id,
            "classification": "NATIVE_COMMAND_PARITY_NUCLEUS_NOT_FULL_PLAYTHROUGH",
        },
        "motion_5184": {
            "scene_id": motion_5184_scene().scene_id,
            "particle_count": 5184,
            "classification": "NATIVE_5184_ADDRESS_PARITY_NUCLEUS_NOT_FULL_MOTION_PARITY",
        },
        "terminal_golden_scene_parity": False,
    }
