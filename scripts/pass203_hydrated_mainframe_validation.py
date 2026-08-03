#!/usr/bin/env python3
"""Production validation for Pass 203 universal hydrated-function mainframe."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def unwrap(value: Any) -> Any:
    if isinstance(value, Mapping):
        for key in ("payload", "result"):
            nested = value.get(key)
            if isinstance(nested, Mapping):
                return nested
    return value


def request(client, method: str, path: str, **kwargs: Any) -> Any:
    response = client.request(method, path, **kwargs)
    if response.status_code >= 400:
        raise RuntimeError(f"{method} {path} -> {response.status_code}: {response.text[:2000]}")
    return unwrap(response.json())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="hhs-pass203-") as directory:
        os.environ["HHS_PASS203_STATE_ROOT"] = directory
        os.environ.setdefault("HHS_PASS190_CAPABILITY_SECRET", "pass203-validation-secret")

        from fastapi.testclient import TestClient
        from hhs_backend.application_ide_server import app

        with TestClient(app) as client:
            status = request(client, "GET", "/api/runtime/mainframe/status")
            functions = request(client, "GET", "/api/runtime/mainframe/functions?limit=1000")
            hydrated = request(client, "GET", "/api/runtime/mainframe/functions?hydrated_only=true&limit=1000")
            operations = request(client, "GET", "/api/runtime/mainframe/operations?limit=1000")
            public_catalog = request(client, "GET", "/api/public/catalog")
            openapi = request(client, "GET", "/api/public/openapi")

            assert status["pass_inheritance"] == "PASS_203_INHERITS_ALL_PRIOR_PASSES_AS_ONE_INTEGRATED_SYSTEM"
            assert status["arbitrary_host_eval_available"] is False
            assert status["unrestricted_subprocess_available"] is False
            assert status["native_authority_preserved"] is True
            assert status["catalog_count"] == functions["total"]
            assert status["hydrated_count"] == hydrated["total"]
            assert status["hydrated_count"] == status["callable_count"]
            assert status["kind_counts"]["GOVERNED_OPERATION"] > 10
            assert status["kind_counts"]["PYTHON_FUNCTION"] > 10
            assert status["kind_counts"]["NATIVE_ABI"] > 10
            assert operations["total"] == status["kind_counts"]["GOVERNED_OPERATION"]
            assert len({item["function_id"] for item in functions["functions"]}) == functions["total"]
            assert all(not item["hydrated"] or item["callable"] for item in functions["functions"])

            interpreter = request(
                client,
                "POST",
                "/api/runtime/mainframe/invoke",
                json={"function_id": "adapter:interpreter.exact", "arguments": {"expression": "1+2*3/4"}},
            )
            assert interpreter["result"]["exact_symbolic_value"] == {"numerator": 5, "denominator": 2}

            rejected = request(
                client,
                "POST",
                "/api/runtime/mainframe/invoke",
                json={
                    "function_id": "adapter:interpreter.exact",
                    "arguments": {"expression": "__import__('os').system('echo unsafe')"},
                },
            )
            assert rejected["result"]["ok"] is False
            assert "REJECT_INTERPRETER_HOST_EVAL" in rejected["result"]["reasons"]

            compiler = request(
                client,
                "POST",
                "/api/runtime/mainframe/invoke",
                json={
                    "function_id": "adapter:compiler.hhs_ir",
                    "arguments": {"source_text": "a²=1 b²=2", "target": "HHS_IR"},
                },
            )
            assert compiler["result"]["ok"] is True
            assert compiler["result"]["execution_authorized"] is False

            operation = request(
                client,
                "POST",
                "/api/runtime/mainframe/operations/invoke",
                json={"operation_id": "system.status", "arguments": {}},
            )
            assert operation["result"]["result"]["status"] == "ok"
            operation_native_receipt = operation["result"]["receipt"]["hash72"]
            replay = request(client, "GET", f"/api/runtime/mainframe/replay/{operation_native_receipt}")
            assert replay["replay_verified"] is True

            python_targets = [
                item for item in hydrated["functions"]
                if item["kind"] == "PYTHON_FUNCTION" and item["name"] == "live_interpreter_self_test"
            ]
            assert python_targets
            isolated = request(
                client,
                "POST",
                "/api/runtime/mainframe/invoke",
                json={"function_id": python_targets[0]["function_id"], "arguments": {}},
            )
            assert isolated["result"]["ok"] is True

            plan = {
                "plan_id": "pass203-production-validation",
                "workspace_id": "workspace:pass203",
                "project_id": "project:pass203",
                "steps": [
                    {
                        "step_id": "interpret",
                        "function_id": "adapter:interpreter.exact",
                        "arguments": {"expression": "9/3+7"},
                    },
                    {
                        "step_id": "compile",
                        "function_id": "adapter:compiler.hhs_ir",
                        "arguments": {"source_text": "a²=1 b²=2", "target": "HHS_IR"},
                        "depends_on": ["interpret"],
                    },
                    {
                        "step_id": "status",
                        "function_id": "op:system.status",
                        "arguments": {},
                        "depends_on": ["compile"],
                    },
                ],
            }
            plan_validation = request(client, "POST", "/api/runtime/mainframe/plans/validate", json=plan)
            assert plan_validation["execution_order"] == ["interpret", "compile", "status"]
            plan_execution = request(client, "POST", "/api/runtime/mainframe/plans/execute", json=plan)
            assert plan_execution["ok"] is True
            assert plan_execution["completed_step_count"] == 3
            assert plan_execution["failure_count"] == 0

            jobs = request(client, "GET", "/api/runtime/mainframe/jobs/runtime")
            assert jobs["worker_count"] >= 0
            assert jobs["governed_operation_count"] == operations["total"]

            missing = next((item for item in functions["functions"] if not item["hydrated"]), None)
            assert missing is not None
            response = client.post(
                "/api/runtime/mainframe/invoke",
                json={"function_id": missing["function_id"], "arguments": {}},
            )
            assert response.status_code == 409
            rejection = response.json()["detail"]
            assert rejection["retryable"] is False
            assert rejection["remediation"]

            route_paths = [getattr(route, "path", "") for route in app.router.routes]
            mainframe_index = route_paths.index("/api/runtime/mainframe/status")
            fallback_indexes = [index for index, path in enumerate(route_paths) if path.startswith("/api/{")]
            mount_indexes = [index for index, path in enumerate(route_paths) if path in {"", "/"}]
            assert not fallback_indexes or mainframe_index < min(fallback_indexes)
            assert not mount_indexes or mainframe_index < max(mount_indexes)

            openapi_paths = openapi.get("paths", {})
            required_paths = {
                "/api/runtime/mainframe/status",
                "/api/runtime/mainframe/functions",
                "/api/runtime/mainframe/invoke",
                "/api/runtime/mainframe/operations/invoke",
                "/api/runtime/mainframe/jobs/runtime",
                "/api/runtime/mainframe/plans/validate",
                "/api/runtime/mainframe/plans/execute",
            }
            assert required_paths <= set(openapi_paths)

            evidence = {
                "schema": "HHS_PASS_203_VALIDATION_RECEIPT_V1",
                "contract": status["contract"],
                "classification": status["classification"],
                "closed": True,
                "production_entrypoint": "hhs_backend.application_ide_server:app",
                "summary": {
                    "catalog_count": status["catalog_count"],
                    "hydrated_count": status["hydrated_count"],
                    "callable_count": status["callable_count"],
                    "unbound_internal_count": status["unbound_internal_count"],
                    "kind_counts": status["kind_counts"],
                    "execution_mode_counts": status["execution_mode_counts"],
                    "family_counts": status["family_counts"],
                    "governed_operation_count": operations["total"],
                    "public_route_count": public_catalog.get("summary", {}).get("route_count"),
                    "openapi_path_count": len(openapi_paths),
                    "plan_step_count": plan_execution["completed_step_count"],
                },
                "catalog_sha256": status["catalog_sha256"],
                "status_hash72": status["status_hash72"],
                "interpreter_receipt_hash72": interpreter["receipt"]["receipt_hash72"],
                "compiler_receipt_hash72": compiler["receipt"]["receipt_hash72"],
                "operation_receipt_hash72": operation["receipt"]["receipt_hash72"],
                "operation_native_receipt_hash72": operation_native_receipt,
                "plan_final_receipt_hash72": plan_execution["final_vm81_receipt_hash72"],
                "claim_boundary": {
                    "all_discovered_functions_indexed": True,
                    "all_hydrated_functions_callable": True,
                    "unbound_functions_fail_closed": True,
                    "arbitrary_host_eval_available": False,
                    "unrestricted_subprocess_available": False,
                    "assistant_plan_is_execution_authority": False,
                },
            }
            evidence["receipt_sha256"] = digest(evidence)

    output = Path(args.evidence)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
