from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .types import reject_float


class BackendProjectionError(ValueError):
    pass


def project_backend(command_stream: Mapping[str, Any], backend: str) -> dict[str, Any]:
    reject_float(command_stream)
    if command_stream.get("schema") != "HHS_PASS_179_COMMAND_STREAM_V1":
        raise BackendProjectionError("P179_BACKEND_COMMAND_SCHEMA")
    backend = backend.upper()
    if backend not in {"WEBGPU", "WEBGL2", "THREEJS"}:
        raise BackendProjectionError("P179_BACKEND_UNSUPPORTED")
    canonical = json.dumps(
        command_stream, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    identity = hashlib.sha256(backend.encode() + b"\0" + canonical).hexdigest()
    return {
        "schema": "HHS_PASS_179_BACKEND_PACKET_V1",
        "backend": backend,
        "packet_sha256": identity,
        "command_stream_sha256": command_stream.get("command_stream_sha256"),
        "immutable_packet": True,
        "projection_only": True,
        "renderer_feedback_authority": False,
        "canonical_mutation_authority": False,
        "hash72_commit_authority": False,
        "context_loss_rebuild_source": "ADMITTED_COMMAND_STREAM",
    }
