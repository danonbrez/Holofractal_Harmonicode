from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping

from hhs_runtime.hash72_checkpoint import make_hash72_witness
from hhs_runtime.pass163.vmrc import VMRCRuntime, VMRCError
from hhs_runtime.pass165.ingestion import DEFAULT_MULTIMODAL_LEARNING_SERVICE

from .software import render_command_stream
from .types import (
    MAX_DIMENSION,
    MAX_NODES,
    GraphicsNode,
    RGBA16,
    q16,
    reject_float,
    rgba16,
)


class GraphicsError(RuntimeError):
    pass


def _canonical(value: Any) -> bytes:
    reject_float(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _hash216(domain: str, payload: Mapping[str, Any]) -> str:
    lanes = [
        make_hash72_witness(f"{domain}:previous", payload, width=72).digest,
        make_hash72_witness(f"{domain}:change", payload, width=72).digest,
        make_hash72_witness(f"{domain}:receipt", payload, width=72).digest,
    ]
    value = "".join(lanes)
    if len(value) != 216:
        raise GraphicsError("P179_HASH216_LENGTH")
    return value


@dataclass(frozen=True)
class SceneState:
    scene_id: str
    width: int
    height: int
    background: RGBA16
    nodes: tuple[GraphicsNode, ...]
    frame_index: int = 0

    def __post_init__(self) -> None:
        if not self.scene_id or len(self.scene_id) > 128:
            raise GraphicsError("P179_SCENE_ID_INVALID")
        if not (1 <= self.width <= MAX_DIMENSION and 1 <= self.height <= MAX_DIMENSION):
            raise GraphicsError("P179_SCENE_DIMENSION_RANGE")
        if len(self.nodes) > MAX_NODES:
            raise GraphicsError("P179_SCENE_NODE_COUNT")
        if not isinstance(self.frame_index, int) or isinstance(self.frame_index, bool) or self.frame_index < 0:
            raise GraphicsError("P179_FRAME_INDEX_INVALID")
        ids = [node.node_id for node in self.nodes]
        if len(ids) != len(set(ids)):
            raise GraphicsError("P179_DUPLICATE_NODE_ID")

    def payload(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_179_SCENE_STATE_V1",
            "scene_id": self.scene_id,
            "width": self.width,
            "height": self.height,
            "background": list(self.background.as_tuple()),
            "frame_index": self.frame_index,
            "nodes": [
                {
                    "node_id": node.node_id,
                    "kind": node.kind,
                    "x_q16": node.x_q16,
                    "y_q16": node.y_q16,
                    "w_q16": node.w_q16,
                    "h_q16": node.h_q16,
                    "rgba16": list(node.color.as_tuple()),
                    "layer": node.layer,
                }
                for node in self.nodes
            ],
        }


def scene_from_payload(payload: Mapping[str, Any]) -> SceneState:
    reject_float(payload)
    scene_id = str(payload.get("scene_id") or "")
    width = int(payload.get("width", 0))
    height = int(payload.get("height", 0))
    background = rgba16(payload.get("background") or [0, 0, 0, 65535])
    raw_nodes = list(payload.get("nodes") or [])
    if len(raw_nodes) > MAX_NODES:
        raise GraphicsError("P179_SCENE_NODE_COUNT")
    nodes: list[GraphicsNode] = []
    for index, raw in enumerate(raw_nodes):
        if not isinstance(raw, Mapping):
            raise GraphicsError(f"P179_NODE_PAYLOAD:{index}")
        if any(key in raw for key in ("x_q16", "y_q16", "w_q16", "h_q16")):
            values = {
                "x_q16": int(raw.get("x_q16", 0)),
                "y_q16": int(raw.get("y_q16", 0)),
                "w_q16": int(raw.get("w_q16", 0)),
                "h_q16": int(raw.get("h_q16", 0)),
            }
        else:
            values = {
                "x_q16": q16(int(raw.get("x", 0))),
                "y_q16": q16(int(raw.get("y", 0))),
                "w_q16": q16(int(raw.get("w", 1))),
                "h_q16": q16(int(raw.get("h", 1))),
            }
        nodes.append(
            GraphicsNode(
                node_id=str(raw.get("node_id") or f"node:{index}"),
                kind=str(raw.get("kind") or "RECT").upper(),
                color=rgba16(raw.get("rgba16") or [65535, 65535, 65535, 65535]),
                layer=int(raw.get("layer", 0)),
                **values,
            )
        )
    nodes.sort(key=lambda item: (item.layer, item.node_id))
    return SceneState(
        scene_id=scene_id,
        width=width,
        height=height,
        background=background,
        nodes=tuple(nodes),
        frame_index=int(payload.get("frame_index", 0)),
    )


def command_stream(scene: SceneState) -> dict[str, Any]:
    commands: list[dict[str, Any]] = [
        {"op": "CLEAR", "rgba16": list(scene.background.as_tuple())}
    ]
    for node in scene.nodes:
        commands.append(
            {
                "op": node.kind,
                "x_q16": node.x_q16,
                "y_q16": node.y_q16,
                "w_q16": node.w_q16,
                "h_q16": node.h_q16,
                "rgba16": list(node.color.as_tuple()),
            }
        )
    stream = {
        "schema": "HHS_PASS_179_COMMAND_STREAM_V1",
        "width": scene.width,
        "height": scene.height,
        "commands": commands,
    }
    stream["command_stream_sha256"] = hashlib.sha256(_canonical(stream)).hexdigest()
    return stream


class GraphicsAuthority:
    def __init__(self, *, vm81: VMRCRuntime | None) -> None:
        self._vm81 = vm81
        self._admitted: dict[str, dict[str, Any]] = {}

    @property
    def vm81(self) -> VMRCRuntime | None:
        return self._vm81

    def status(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_179_GRAPHICS_STATUS_V1",
            "contract": "HHS-P179-NEGAS-MRL",
            "implementation_stage": "P179_NATIVE_CORE_PRESENT_NONTERMINAL",
            "vm81_authority_bound": self._vm81 is not None,
            "singleton_vm81_authority": True,
            "independent_vm81_authority": False,
            "independent_hash72_commit_authority": False,
            "hash216_mutation_authority": False,
            "software_renderer_mutation_authority": False,
            "gpu_mutation_authority": False,
            "browser_mutation_authority": False,
            "terminal_pass179_completion": False,
            "remaining_terminal_categories": [
                "FULL_NATIVE_2D_3D_LIBRARY",
                "FULL_SHADER_IR_GRAPH_AND_BACKEND_COMPILERS",
                "FULL_WEBGPU_WEBGL2_DEVICE_EXECUTION",
                "THREEJS_PASS178_PARITY",
                "PLAYABLE_NATIVE_LATTICE_RUN",
                "FULL_5184_MOTION_PARITY",
                "IDE_EDITOR_TIMELINE_SHADER_GRAPH",
                "FULL_CAPTURE_VIDEO_PIPELINE",
                "BROWSER_E2E_PERFORMANCE_ACCESSIBILITY_SECURITY",
                "AUTHORITATIVE_MAIN_INTEGRATION",
            ],
        }

    def _admit(self, transition: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        if self._vm81 is None:
            raise GraphicsError("P179_VM81_ADMISSION_AUTHORITY_REQUIRED")
        material = _canonical({"transition": transition, "payload": payload})
        digest = hashlib.sha256(material).digest()
        writes: dict[int, int] = {}
        for byte in digest[:24]:
            writes[int(byte % 81)] = 1 if byte & 1 else -1
        try:
            candidate = self._vm81.submit_candidate(
                thread=59,
                writes=writes,
                operation="VMRC_COMMIT",
                expected_input_hash72=self._vm81.state_hash72,
                dependency_root=hashlib.sha256(
                    b"HHS-P179-GRAPHICS-VM81\0" + material
                ).hexdigest(),
                capability_scope="P179_GRAPHICS_SCENE_ADMISSION",
                source_architecture="P179_NATIVE_GRAPHICS_LIBRARY",
                target_architecture="VM81",
            )
            result = self._vm81.execute(candidate)
        except VMRCError as error:
            raise GraphicsError(f"P179_VM81_ADMISSION_REJECTED:{error}") from error
        commit = result.get("commit") or {}
        receipt = commit.get("receipt") or {}
        validation = (result.get("validation") or {}).get("validated") or {}
        if commit.get("classification") != "HHS_PASS_163_COMMIT_ADMITTED":
            raise GraphicsError("P179_VM81_ADMISSION_NOT_COMMITTED")
        return {
            "classification": "HHS_PASS179_VM81_SCENE_ADMISSION_VERIFIED",
            "candidate_id": candidate.candidate_id,
            "receipt_hash72": str(receipt.get("receipt_hash72") or ""),
            "operation_hash216": str(receipt.get("operation_hash216") or ""),
            "output_hash72": str(receipt.get("output_hash72") or ""),
            "vm81_epoch": self._vm81.epoch,
            "singleton_authority": True,
            "independent_vm81_authority": False,
            "validation_mutation_authority": bool(validation.get("mutation_authority", False)),
        }

    def commit_scene(self, scene: SceneState) -> dict[str, Any]:
        stream = command_stream(scene)
        scene_payload = scene.payload()
        candidate_scene_sha256 = hashlib.sha256(_canonical(scene_payload)).hexdigest()
        admission = self._admit(
            "SCENE_COMMIT",
            {
                "scene_id": scene.scene_id,
                "frame_index": scene.frame_index,
                "candidate_scene_sha256": candidate_scene_sha256,
                "command_stream_sha256": stream["command_stream_sha256"],
            },
        )
        evidence_payload = {
            "scene_id": scene.scene_id,
            "frame_index": scene.frame_index,
            "candidate_scene_sha256": candidate_scene_sha256,
            "command_stream_sha256": stream["command_stream_sha256"],
            "vm81_receipt_hash72": admission["receipt_hash72"],
            "vm81_output_hash72": admission["output_hash72"],
        }
        evidence_hash72 = make_hash72_witness(
            "pass179:scene:post-vm81-evidence", evidence_payload, width=72
        ).digest
        scene_hash216 = _hash216("pass179:scene:archive", evidence_payload)
        record = {
            "schema": "HHS_PASS_179_ADMITTED_SCENE_V1",
            "scene": scene_payload,
            "command_stream": stream,
            "candidate_scene_sha256": candidate_scene_sha256,
            "vm81_admission": admission,
            "post_vm81_hash72_evidence": evidence_hash72,
            "scene_hash216": scene_hash216,
            "hash72_commit_authority": False,
            "hash216_mutation_authority": False,
        }
        self._admitted[scene.scene_id] = record
        return record

    def render_scene(self, scene_id: str) -> dict[str, Any]:
        record = self._admitted.get(scene_id)
        if record is None:
            raise GraphicsError("P179_SCENE_NOT_ADMITTED")
        frame = render_command_stream(record["command_stream"])
        evidence_payload = {
            "scene_hash216": record["scene_hash216"],
            "frame_sha256": frame["frame_sha256"],
            "frame_index": record["scene"]["frame_index"],
        }
        return {
            "schema": "HHS_PASS_179_RENDER_RESULT_V1",
            "scene_hash216": record["scene_hash216"],
            "frame": frame,
            "frame_hash216": _hash216("pass179:frame:archive", evidence_payload),
            "frame_hash72_evidence": make_hash72_witness(
                "pass179:frame:evidence", evidence_payload, width=72
            ).digest,
            "projection_only": True,
            "canonical_mutation_authority": False,
        }

    def replay_scene(self, scene_id: str, expected_scene_hash216: str) -> dict[str, Any]:
        record = self._admitted.get(scene_id)
        if record is None:
            raise GraphicsError("P179_SCENE_NOT_ADMITTED")
        actual = record["scene_hash216"]
        return {
            "schema": "HHS_PASS_179_SCENE_REPLAY_V1",
            "ok": actual == expected_scene_hash216,
            "scene_id": scene_id,
            "expected_scene_hash216": expected_scene_hash216,
            "actual_scene_hash216": actual,
            "deterministic_replay": actual == expected_scene_hash216,
        }


PASS179_GRAPHICS = GraphicsAuthority(
    vm81=DEFAULT_MULTIMODAL_LEARNING_SERVICE._vm81,
)
