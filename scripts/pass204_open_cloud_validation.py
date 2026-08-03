#!/usr/bin/env python3
"""Validate Pass 204 against the hosted application composition."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


def _unwrap(value: Any) -> Any:
    current = value
    for _ in range(8):
        if not isinstance(current, Mapping):
            break
        if "execution_status" in current or "all_declarations_executable" in current:
            break
        candidate = current.get("data", current.get("result"))
        if not isinstance(candidate, Mapping) or candidate is current:
            break
        current = candidate
    return current


def _required_arguments(record: Mapping[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for parameter in record.get("parameters") or []:
        if not parameter.get("required"):
            continue
        name = str(parameter.get("name") or "value")
        annotation = str(parameter.get("annotation") or "").lower()
        lowered = name.lower()
        if "bool" in annotation:
            value: Any = False
        elif "int" in annotation:
            value = 1
        elif "float" in annotation:
            value = 1
        elif "fraction" in annotation:
            value = {"numerator": 1, "denominator": 1}
        elif "bytes" in annotation:
            value = {"encoding": "base64", "data": "eA=="}
        elif any(token in annotation for token in ("list", "sequence", "tuple", "set")):
            value = []
        elif any(token in annotation for token in ("dict", "mapping")):
            value = {}
        elif "path" in annotation or "path" in lowered or "file" in lowered:
            value = "input"
        elif "expression" in lowered:
            value = "1+1"
        elif "source" in lowered or "text" in lowered:
            value = "a²=1 b²=2"
        elif "id" in lowered:
            value = f"validation:{name}"
        else:
            value = "1"
        result[name] = value
    return result


def _select(records: Iterable[Mapping[str, Any]], *, kind: str = "", inherited_mode: str = "") -> Mapping[str, Any]:
    for item in records:
        if kind and item.get("kind") != kind:
            continue
        if inherited_mode and item.get("inherited_execution_mode") != inherited_mode:
            continue
        return item
    raise AssertionError(f"missing representative kind={kind!r} inherited_mode={inherited_mode!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="hhs-pass204-validation-") as temporary:
        root = Path(temporary)
        os.environ["HHS_PASS203_STATE_ROOT"] = str(root / "pass203")
        os.environ["HHS_PASS204_STATE_ROOT"] = str(root / "pass204")

        from fastapi.testclient import TestClient
        from hhs_backend.application_ide_server import app
        from hhs_backend.runtime.hhs_pass204_open_cloud_mainframe import PASS204_MAINFRAME

        refresh = PASS204_MAINFRAME.refresh()
        status = PASS204_MAINFRAME.status()
        catalog = PASS204_MAINFRAME.catalog()

        assert refresh["closed"] is True
        assert refresh["unbound_count"] == 0
        assert refresh["catalog_count"] == refresh["hydrated_count"] == refresh["callable_count"]
        assert status["all_declarations_executable"] is True
        assert status["safe_open_cloud_computer_api"] is True
        assert status["valid_api_call_http_error"] is False
        assert all(item.get("hydrated") and item.get("callable") for item in catalog)
        assert all(item.get("binding_gap") is False for item in catalog)

        client = TestClient(app)
        closure_response = client.get("/api/runtime/open-cloud/closure")
        assert closure_response.status_code == 200, closure_response.text
        closure = _unwrap(closure_response.json())
        assert closure["all_declarations_executable"] is True
        assert closure["binding_gap_count"] == 0

        canonicalize = next(
            item for item in catalog
            if item.get("kind") == "PYTHON_FUNCTION"
            and item.get("name") == "canonicalize_for_hash72"
            and "hhs_general_runtime_layer_v1" in str(item.get("module"))
        )
        python_response = client.post(
            "/api/runtime/mainframe/invoke",
            json={"function_id": canonicalize["function_id"], "arguments": {"obj": {"b": 2, "a": 1}}},
        )
        assert python_response.status_code == 200, python_response.text
        python_invocation = _unwrap(python_response.json())
        assert python_invocation["execution_status"] == "COMPLETED"
        assert python_invocation["result"]["result"] == {"a": 1, "b": 2}

        native = _select(catalog, kind="NATIVE_ABI", inherited_mode="ABI_BINDING_REQUIRED")
        native_response = client.post(
            "/api/runtime/mainframe/invoke",
            json={"function_id": native["function_id"], "arguments": {}},
        )
        assert native_response.status_code == 200, native_response.text
        native_invocation = _unwrap(native_response.json())
        assert native_invocation["execution_status"] == "ACCEPTED"
        assert native_invocation["job"]["job_id"]

        # Validate one representative of every inherited binding-gap class. A
        # valid argument shape must return HTTP success, whether the sandbox
        # completes immediately or creates a durable continuation.
        representative_results = []
        for mode in ("ADAPTER_REQUIRED", "WORKSPACE_JOB_ADAPTER_REQUIRED", "FORBIDDEN"):
            candidates = [
                item for item in catalog
                if item.get("kind") == "PYTHON_FUNCTION"
                and item.get("inherited_execution_mode") == mode
            ]
            if not candidates:
                continue
            target = min(candidates, key=lambda item: sum(1 for p in item.get("parameters") or [] if p.get("required")))
            response = client.post(
                "/api/runtime/mainframe/invoke",
                json={"function_id": target["function_id"], "arguments": _required_arguments(target)},
            )
            assert response.status_code == 200, response.text
            invocation = _unwrap(response.json())
            assert invocation["execution_status"] in {"COMPLETED", "ACCEPTED", "CONTINUATION_REQUIRED"}
            representative_results.append(
                {
                    "inherited_mode": mode,
                    "function_id": target["function_id"],
                    "execution_status": invocation["execution_status"],
                }
            )

        recall_token = python_invocation["snapshot"]["recall_token"]
        recall_response = client.post("/api/runtime/open-cloud/recall", json={"recall_token": recall_token})
        assert recall_response.status_code == 200, recall_response.text
        recall = _unwrap(recall_response.json())
        assert recall["verified"] is True
        assert recall["capabilities_restored"] is False
        assert recall["snapshot"]["integrated_system_state"]["history_rewrite_permitted"] is False

        paths = app.openapi().get("paths", {})
        for required in (
            "/api/runtime/mainframe/status",
            "/api/runtime/mainframe/functions",
            "/api/runtime/mainframe/invoke",
            "/api/runtime/open-cloud/status",
            "/api/runtime/open-cloud/policy",
            "/api/runtime/open-cloud/closure",
            "/api/runtime/open-cloud/recall",
        ):
            assert required in paths, required

        evidence = {
            "schema": "HHS_PASS_204_OPEN_CLOUD_VALIDATION_RECEIPT_V1",
            "contract": status["contract"],
            "classification": status["classification"],
            "closed": True,
            "production_entrypoint": "hhs_backend.application_ide_server:app",
            "summary": {
                "catalog_count": status["catalog_count"],
                "hydrated_count": status["hydrated_count"],
                "callable_count": status["callable_count"],
                "binding_gap_count": status["unbound_internal_count"],
                "public_route_count": len(app.routes),
                "openapi_path_count": len(paths),
                "representative_results": representative_results,
            },
            "catalog_sha256": status["catalog_sha256"],
            "status_hash72": status["status_hash72"],
            "python_receipt_hash72": python_invocation["receipt"]["receipt_hash72"],
            "native_receipt_hash72": native_invocation["receipt"]["receipt_hash72"],
            "snapshot_root": python_invocation["snapshot"]["snapshot_root"],
            "recall_verified": recall["verified"],
            "sandbox_policy": status["sandbox_policy"],
            "kernel_constraint_manifest": status["kernel_constraint_manifest"],
            "host_trust_boundary": status["host_trust_boundary"],
        }
        target_path = Path(args.evidence)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
