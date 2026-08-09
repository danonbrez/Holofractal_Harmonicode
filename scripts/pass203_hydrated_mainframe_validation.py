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
        nested = value.get("payload")
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
        from hhs_backend.runtime.hhs_pass203_hydrated_mainframe_v1 import (
            PASS203_MAINFRAME,
            InvocationRejectedError,
        )
        from hhs_backend.runtime.hhs_pass204_open_cloud_mainframe import PASS204_MAINFRAME

        with TestClient(app) as client:
            # Pass 204 is an in-place cumulative upgrade of the public Pass 203
            # mainframe surface. The hosted endpoints must therefore expose the
            # Pass 204 overlay while retaining exactly the inherited Pass 203
            # function identities beneath that overlay.
            hosted_status = request(client, "GET", "/api/runtime/mainframe/status")
            hosted_first_page = request(client, "GET", "/api/runtime/mainframe/functions?limit=50")
            hosted_interpreter = request(
                client,
                "POST",
                "/api/runtime/mainframe/invoke",
                json={"function_id": "adapter:interpreter.exact", "arguments": {"expression": "1+2*3/4"}},
            )

            status = PASS203_MAINFRAME.status()
            catalog = PASS203_MAINFRAME.catalog()
            hydrated = [item for item in catalog if item["hydrated"]]
            operations = [item for item in catalog if item["kind"] == "GOVERNED_OPERATION"]
            unbound = [item for item in catalog if not item["hydrated"]]

            hosted_runtime_status = PASS204_MAINFRAME.status()
            hosted_catalog = PASS204_MAINFRAME.catalog()
            pass203_ids = {item["function_id"] for item in catalog}
            hosted_ids = {item["function_id"] for item in hosted_catalog}

            assert PASS204_MAINFRAME.base is PASS203_MAINFRAME
            assert hosted_status["catalog_sha256"] == hosted_runtime_status["catalog_sha256"]
            assert hosted_status["classification"] == hosted_runtime_status["classification"]
            assert hosted_status["pass_inheritance"] == "PASS_204_INHERITS_ALL_PRIOR_PASSES_AS_ONE_INTEGRATED_SYSTEM"
            assert hosted_first_page["total"] == len(hosted_catalog)
            assert hosted_ids == pass203_ids
            assert len(hosted_catalog) == len(catalog)
            assert hosted_runtime_status["callable_count"] == len(hosted_catalog)
            assert hosted_runtime_status["hydrated_count"] == len(hosted_catalog)
            assert hosted_runtime_status["unbound_internal_count"] == 0
            assert hosted_runtime_status["all_declarations_executable"] is True
            assert hosted_interpreter["execution_status"] == "COMPLETED"
            assert hosted_interpreter["result"]["result"]["result"]["exact_symbolic_value"] == {
                "numerator": 5,
                "denominator": 2,
            }

            assert len(catalog) == status["catalog_count"]
            assert len(hydrated) == status["hydrated_count"] == status["callable_count"]
            assert len(unbound) == status["unbound_internal_count"]
            assert len({item["function_id"] for item in catalog}) == len(catalog)
            assert all(not item["hydrated"] or item["callable"] for item in catalog)
            assert status["pass_inheritance"] == "PASS_203_INHERITS_ALL_PRIOR_PASSES_AS_ONE_INTEGRATED_SYSTEM"
            assert status["arbitrary_host_eval_available"] is False
            assert status["unrestricted_subprocess_available"] is False
            assert status["native_authority_preserved"] is True
            assert status["kind_counts"]["GOVERNED_OPERATION"] > 10
            assert status["kind_counts"]["PYTHON_FUNCTION"] > 10
            assert status["kind_counts"]["NATIVE_ABI"] > 10

            last_page = request(
                client,
                "GET",
                f"/api/runtime/mainframe/functions?offset={max(0, len(hosted_catalog) - 1)}&limit=1",
            )
            assert last_page["total"] == len(hosted_catalog)
            assert last_page["functions"] == [hosted_catalog[-1]]

            rejected = PASS203_MAINFRAME.invoke(
                "adapter:interpreter.exact",
                {"expression": "__import__('os').system('echo unsafe')"},
            )
            assert rejected["result"]["ok"] is False
            assert "REJECT_INTERPRETER_HOST_EVAL" in rejected["result"]["reasons"]

            compiler = PASS203_MAINFRAME.invoke(
                "adapter:compiler.hhs_ir",
                {"source_text": "a²=1 b²=2", "target": "HHS_IR"},
            )
            assert compiler["result"]["ok"] is True
            assert compiler["result"]["execution_authorized"] is False

            operation = PASS203_MAINFRAME.invoke("op:system.status", {})
            assert operation["result"]["result"]["status"] == "ok"
            operation_native_receipt = operation["result"]["receipt"]["hash72"]
            replay = PASS203_MAINFRAME.replay(operation_native_receipt)
            assert replay["replay_verified"] is True

            python_target = next(
                item for item in hydrated
                if item["kind"] == "PYTHON_FUNCTION" and item["name"] == "live_interpreter_self_test"
            )
            isolated = PASS203_MAINFRAME.invoke(python_target["function_id"], {})
            assert isolated["result"]["ok"] is True

            ordered_steps = (
                ("interpret", "adapter:interpreter.exact", {"expression": "9/3+7"}),
                ("compile", "adapter:compiler.hhs_ir", {"source_text": "a²=1 b²=2", "target": "HHS_IR"}),
                ("status", "op:system.status", {}),
            )
            plan_results = []
            for step_id, function_id, arguments in ordered_steps:
                invocation = PASS203_MAINFRAME.invoke(
                    function_id,
                    arguments,
                    workspace_id="workspace:pass203",
                    project_id="project:pass203",
                    idempotency_key=f"pass203-production-validation:{step_id}",
                )
                plan_results.append({"step_id": step_id, "invocation": invocation})
            assert [item["step_id"] for item in plan_results] == ["interpret", "compile", "status"]

            jobs = PASS203_MAINFRAME._pass190().execution_runtime_report()
            assert jobs["worker_count"] >= 0
            assert jobs["governed_operation_count"] == len(operations)

            assert unbound
            try:
                PASS203_MAINFRAME.invoke(unbound[0]["function_id"], {})
            except InvocationRejectedError:
                pass
            else:
                raise AssertionError("unhydrated function did not fail closed")

            route_paths = [getattr(route, "path", "") for route in app.router.routes]
            mainframe_index = route_paths.index("/api/runtime/mainframe/status")
            fallback_indexes = [index for index, path in enumerate(route_paths) if path.startswith("/api/{")]
            mount_indexes = [index for index, path in enumerate(route_paths) if path in {"", "/"}]
            assert not fallback_indexes or mainframe_index < min(fallback_indexes)
            assert not mount_indexes or mainframe_index < max(mount_indexes)

            openapi_paths = app.openapi().get("paths", {})
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
                "schema": "HHS_PASS_203_VALIDATION_RECEIPT_V2",
                "contract": status["contract"],
                "classification": status["classification"],
                "closed": True,
                "production_entrypoint": "hhs_backend.application_ide_server:app",
                "summary": {
                    "catalog_count": len(catalog),
                    "hydrated_count": len(hydrated),
                    "callable_count": status["callable_count"],
                    "unbound_internal_count": len(unbound),
                    "kind_counts": status["kind_counts"],
                    "execution_mode_counts": status["execution_mode_counts"],
                    "family_counts": status["family_counts"],
                    "governed_operation_count": len(operations),
                    "public_route_count": len(route_paths),
                    "openapi_path_count": len(openapi_paths),
                    "plan_step_count": len(plan_results),
                    "hosted_catalog_count": len(hosted_catalog),
                    "hosted_catalog_page_limit": hosted_first_page["limit"],
                    "last_catalog_page_reachable": True,
                    "hosted_surface_upgraded_by_pass204": True,
                },
                "catalog_sha256": status["catalog_sha256"],
                "hosted_catalog_sha256": hosted_runtime_status["catalog_sha256"],
                "hosted_catalog_inherits_same_function_ids": hosted_ids == pass203_ids,
                "status_hash72": status["status_hash72"],
                "hosted_status_hash72": hosted_runtime_status["status_hash72"],
                "interpreter_receipt_hash72": hosted_interpreter["receipt"]["receipt_hash72"],
                "compiler_receipt_hash72": compiler["receipt"]["receipt_hash72"],
                "operation_receipt_hash72": operation["receipt"]["receipt_hash72"],
                "operation_native_receipt_hash72": operation_native_receipt,
                "plan_final_receipt_hash72": plan_results[-1]["invocation"]["receipt"]["receipt_hash72"],
                "claim_boundary": {
                    "all_discovered_functions_indexed": True,
                    "all_hydrated_functions_callable": True,
                    "bounded_pagination_preserved": True,
                    "unbound_functions_fail_closed": True,
                    "arbitrary_host_eval_available": False,
                    "unrestricted_subprocess_available": False,
                    "assistant_plan_is_execution_authority": False,
                    "pass204_public_upgrade_preserves_pass203_function_identity": True,
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