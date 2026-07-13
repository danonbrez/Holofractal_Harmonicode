"""Pass 049 interpreting compiler surface."""

from __future__ import annotations

from typing import Any, Dict, Mapping
import uuid

from hhs_backend.runtime.hhs_compiler_ir_v1 import SUPPORTED_TARGETS, build_compiled_artifact
from hhs_backend.runtime.runtime_workspace_object_v1 import VERSION, AUTHORITY, hash72

COMPILER_REQUEST_SCHEMA = "HHS_COMPILER_REQUEST_V1"


def build_compiler_request(project_id: str, source_object_id: str, source_text: str, target: str = "HHS_IR") -> Dict[str, Any]:
    request = {
        "schema": COMPILER_REQUEST_SCHEMA,
        "version": VERSION,
        "request_id": f"compile:{uuid.uuid4().hex}",
        "project_id": project_id,
        "source_object_id": source_object_id,
        "source_root_hash72": hash72("HHS_COMPILER_SOURCE_TEXT_V1", source_text),
        "target": target,
        "requires_conformance": True,
        "execution_authorization_requested": False,
    }
    request["request_root_hash72"] = hash72(COMPILER_REQUEST_SCHEMA, request)
    return request


def compile_hhs_source(request: Mapping[str, Any], source_text: str) -> Dict[str, Any]:
    target = str(request.get("target") or "HHS_IR")
    artifact = build_compiled_artifact(str(request.get("source_object_id")), source_text, target)
    if not artifact.get("ok"):
        return {
            "schema": "HHS_COMPILER_RESULT_V1",
            "version": VERSION,
            "ok": False,
            "status": artifact.get("status"),
            "request": dict(request),
            "artifact": artifact,
        }
    result = {
        "schema": "HHS_COMPILER_RESULT_V1",
        "version": VERSION,
        "ok": True,
        "status": "COMPILER_ARTIFACT_CREATED",
        "request": dict(request),
        "artifact": artifact,
        "source_to_artifact_provenance": {
            "source_object_id": request.get("source_object_id"),
            "source_root_hash72": request.get("source_root_hash72"),
            "artifact_id": artifact.get("artifact_id"),
            "artifact_root_hash72": artifact.get("receipt_hash72"),
        },
        "execution_authorized": False,
        "authority": AUTHORITY,
    }
    result["result_root_hash72"] = hash72("HHS_COMPILER_RESULT_V1", result)
    return result


def interpreting_compiler_self_test() -> Dict[str, Any]:
    request = build_compiler_request("project:pass049", "object:source", "a²=1 b²=2", "HHS_IR")
    result = compile_hhs_source(request, "a²=1 b²=2")
    bad_request = build_compiler_request("project:pass049", "object:source", "a²=1", "HOST_SIDE_EFFECT_BINARY")
    rejected = compile_hhs_source(bad_request, "a²=1")
    return {
        "schema": "HHS_INTERPRETING_COMPILER_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(result.get("ok") and not rejected.get("ok") and not result.get("execution_authorized")),
        "result": result,
        "unsupported_target_rejection": rejected,
        "supported_targets": SUPPORTED_TARGETS,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(interpreting_compiler_self_test(), indent=2, sort_keys=True, default=str))
