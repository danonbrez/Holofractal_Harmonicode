#!/usr/bin/env python3
"""Replay the inherited Pass 203 authority independently of Pass 204 routing."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="hhs-pass203-inherited-") as directory:
        os.environ["HHS_PASS203_STATE_ROOT"] = directory
        os.environ.setdefault("HHS_PASS190_CAPABILITY_SECRET", "pass204-inherited-pass203-secret")

        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        import hhs_backend.api.pass203_mainframe_routes as routes
        from hhs_backend.runtime.hhs_pass203_hydrated_mainframe_v1 import (
            HydratedMainframe,
            InvocationRejectedError,
        )

        repo_root = Path(__file__).resolve().parents[1]
        authority = HydratedMainframe(repo_root)
        counter = {"step": 0}

        def tick(source: str):
            counter["step"] += 1
            return {
                "source": source,
                "receipt": {"receipt_hash72": "P" * 71 + str(counter["step"] % 10)},
                "runtime": {"step": counter["step"]},
            }

        authority.configure_authority(tick)
        routes.PASS203_MAINFRAME = authority
        app = FastAPI(title="Pass 203 Inherited Replay")
        app.include_router(routes.router)
        client = TestClient(app)

        refresh = authority.refresh()
        status = authority.status()
        catalog = authority.catalog()
        unbound = [item for item in catalog if not item["hydrated"]]

        assert refresh["closed"] is True
        assert status["pass_inheritance"] == "PASS_203_INHERITS_ALL_PRIOR_PASSES_AS_ONE_INTEGRATED_SYSTEM"
        assert status["arbitrary_host_eval_available"] is False
        assert status["unrestricted_subprocess_available"] is False
        assert status["native_authority_preserved"] is True
        assert len({item["function_id"] for item in catalog}) == len(catalog)
        assert unbound

        hosted_status = client.get("/api/runtime/mainframe/status")
        assert hosted_status.status_code == 200, hosted_status.text
        hosted_catalog = client.get("/api/runtime/mainframe/functions?limit=50")
        assert hosted_catalog.status_code == 200, hosted_catalog.text

        interpreter = authority.invoke("adapter:interpreter.exact", {"expression": "1+2*3/4"})
        assert interpreter["result"]["exact_symbolic_value"] == {"numerator": 5, "denominator": 2}
        compiler = authority.invoke(
            "adapter:compiler.hhs_ir",
            {"source_text": "a²=1 b²=2", "target": "HHS_IR"},
        )
        assert compiler["result"]["ok"] is True
        assert compiler["result"]["execution_authorized"] is False
        operation = authority.invoke("op:system.status", {})
        assert operation["result"]["result"]["status"] == "ok"
        native_receipt = operation["result"]["receipt"]["hash72"]
        assert authority.replay(native_receipt)["replay_verified"] is True

        python_target = next(
            item for item in catalog
            if item["kind"] == "PYTHON_FUNCTION"
            and item["hydrated"]
            and item["name"] == "live_interpreter_self_test"
        )
        isolated = authority.invoke(python_target["function_id"], {})
        assert isolated["result"]["ok"] is True

        try:
            authority.invoke(unbound[0]["function_id"], {})
        except InvocationRejectedError:
            pass
        else:
            raise AssertionError("Pass 203 unbound declaration did not preserve its inherited fail-closed behavior")

        evidence = {
            "schema": "HHS_PASS_204_INHERITED_PASS_203_REPLAY_RECEIPT_V1",
            "contract": status["contract"],
            "classification": status["classification"],
            "closed": True,
            "standalone_replay": True,
            "summary": {
                "catalog_count": len(catalog),
                "hydrated_count": status["hydrated_count"],
                "callable_count": status["callable_count"],
                "unbound_internal_count": len(unbound),
                "route_count": len(app.routes),
                "openapi_path_count": len(app.openapi().get("paths", {})),
            },
            "catalog_sha256": status["catalog_sha256"],
            "status_hash72": status["status_hash72"],
            "interpreter_receipt_hash72": interpreter["receipt"]["receipt_hash72"],
            "compiler_receipt_hash72": compiler["receipt"]["receipt_hash72"],
            "operation_receipt_hash72": operation["receipt"]["receipt_hash72"],
            "operation_native_receipt_hash72": native_receipt,
        }

    output = Path(args.evidence)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
