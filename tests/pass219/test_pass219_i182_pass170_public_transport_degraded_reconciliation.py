from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path

import httpx
import pytest

from hhs_runtime.pass219.pass170_public_transport_i182 import (
    AUDIO_NATIVE_SYMBOL,
    AUDIO_OPERATION_ID,
    Pass170I182TransportError,
    invoke_public_operation_python,
    operation_records,
)
from hhs_runtime.pass219.pass170_transport_degraded_reconciliation_i182 import (
    EXPECTED_TARGET_BLOCKERS,
    NEXT_BOUNDARY,
    verify_i182_transport_degraded_reconciliation,
)

ROOT = Path(__file__).resolve().parents[2]


def test_complete_frozen_operation_chain_has_59_unique_records() -> None:
    records = operation_records(ROOT)
    assert len(records) == 59
    assert len(set(records)) == 59
    http = [record for record in records.values() if record.get("HTTP_method") and record.get("HTTP_path")]
    streaming_only = [
        record
        for record in records.values()
        if not record.get("HTTP_method") and record.get("WebSocket_channel")
    ]
    native = [record for record in records.values() if record.get("native_ABI_symbol")]
    assert len(http) == 58
    assert len(streaming_only) == 1
    assert len(native) == 1
    assert native[0]["operation_id"] == AUDIO_OPERATION_ID
    assert native[0]["native_ABI_symbol"] == AUDIO_NATIVE_SYMBOL


def test_streaming_operation_is_not_scalarized_into_cli_http() -> None:
    records = operation_records(ROOT)
    streaming = [
        record
        for record in records.values()
        if not record.get("HTTP_method") and record.get("WebSocket_channel")
    ]
    assert [record["operation_id"] for record in streaming] == ["public.receipts.websocket"]
    with pytest.raises(Pass170I182TransportError, match="STREAMING_OPERATION_REQUIRES_WEBSOCKET"):
        invoke_public_operation_python("public.receipts.websocket", repository_root=ROOT)


def test_float_transport_is_rejected_before_canonical_app_dispatch() -> None:
    with pytest.raises(Pass170I182TransportError, match="FLOAT_TRANSPORT_REJECTED"):
        invoke_public_operation_python(
            "public.system.status",
            payload={"illegal": 0.5},
            repository_root=ROOT,
        )


def test_path_parameter_set_is_exact_and_fail_closed() -> None:
    with pytest.raises(Pass170I182TransportError, match="PATH_PARAMETER_SET_MISMATCH"):
        invoke_public_operation_python(
            "pass168.parameter_circuit.parameter.get",
            path_parameters={},
            repository_root=ROOT,
        )


def test_records_cli_surface_reports_complete_identity_set() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "hhs_runtime.pass219.pass170_public_transport_i182",
            "records",
            "--repository-root",
            str(ROOT),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["count"] == 59
    assert len(payload["operation_ids"]) == 59
    assert "public.audio_language.feedback.run" in payload["operation_ids"]


def test_generic_python_transport_executes_through_canonical_full_app() -> None:
    result = invoke_public_operation_python("public.system.status", repository_root=ROOT)
    assert result["operation_id"] == "public.system.status"
    assert result["method"] == "GET"
    assert result["path"] == "/v1/system/status"
    assert result["status_code"] == 200
    assert result["canonical_gateway"] == "hhs_backend.public_api_server:app"
    assert result["transport"] == "IN_PROCESS_ASGI_CANONICAL_GATEWAY"
    assert result["semantic_engine_reimplemented"] is False
    assert result["new_vm81_authority"] is False
    assert result["new_hash72_mint_authority"] is False
    assert result["hash216_persistence_authority"] is False
    assert result["floating_point_canonical_authority"] is False


def test_stale_composition_marker_reconciles_complete_i180_bundle_once() -> None:
    from fastapi import FastAPI

    from hhs_backend import public_api_server
    from hhs_backend.pass170_legacy_runtime_routes import MIGRATED_HTTP_SIGNATURES

    target = FastAPI()
    target.state.hhs_pass170_routes_composed = True

    public_api_server._compose_pass170(  # type: ignore[attr-defined]
        target,
        authority_context=None,
        registry_report={},
    )

    signatures = set()
    for route in target.router.routes:
        path = str(getattr(route, "path", ""))
        methods = getattr(route, "methods", None)
        if methods:
            for method in methods:
                method_name = str(method).upper()
                if method_name not in {"HEAD", "OPTIONS"}:
                    signatures.add((method_name, path))

    required = set(MIGRATED_HTTP_SIGNATURES)
    assert required <= signatures
    assert target.state.hhs_pass170_route_bundle_revision == public_api_server.PASS170_ROUTE_BUNDLE_REVISION

    route_count = len(target.router.routes)
    public_api_server._compose_pass170(  # type: ignore[attr-defined]
        target,
        authority_context=None,
        registry_report={},
    )
    assert len(target.router.routes) == route_count


def test_degraded_shell_remains_fail_closed_and_noncanonical() -> None:
    from hhs_backend.runtime_os_source_only_server import app

    async def exercise() -> tuple[dict, dict]:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://source-only.local") as client:
            health = await client.get("/health")
            missing = await client.post("/api/not-a-canonical-operation", json={})
        return health.json(), {"status_code": missing.status_code, "body": missing.json()}

    health, missing = asyncio.run(exercise())
    assert health["ok"] is False
    assert health["source_only_degraded_mode"] is True
    assert health["canonical_mutation_permitted"] is False
    assert health["frontend_is_authority"] is False
    assert missing["status_code"] == 503
    assert missing["body"]["detail"]["canonical_mutation_permitted"] is False
    assert missing["body"]["detail"]["frontend_result_fabricated"] is False


def test_i182_verifier_clears_only_transport_and_degraded_shell_residuals() -> None:
    report = verify_i182_transport_degraded_reconciliation(ROOT)
    assert report["evidence_verified"] is True
    assert report["aggregate_operation_count"] == 59
    assert report["http_operation_count"] == 58
    assert report["streaming_only_operation_count"] == 1
    assert report["native_declared_operation_count"] == 1
    assert report["canonical_http_routes_verified"] == 58
    assert report["canonical_application_identity_verified"] is True
    assert report["generic_cli_transport_bound"] is True
    assert report["generic_python_transport_bound"] is True
    assert report["semantic_engine_reimplemented"] is False
    assert report["source_only_degraded_shell_reconciled"] is True
    assert report["source_only_degraded_shell_retained_fail_closed"] is True
    assert report["new_capability_token_authority"] is False
    assert report["new_vm81_authority"] is False
    assert report["new_hash72_mint_authority"] is False
    assert report["hash216_persistence_authority"] is False
    assert report["floating_point_canonical_authority"] is False
    assert report["target_blockers"] == list(EXPECTED_TARGET_BLOCKERS)
    assert report["target_blockers"] == ["PASS170_FULL_PUBLIC_E2E_TERMINAL_PROOF_PENDING"]
    assert report["pass170_terminal_contract_verified"] is False
    assert report["next_boundary"] == NEXT_BOUNDARY
    assert NEXT_BOUNDARY == "PASS170_FULL_PUBLIC_E2E_TERMINAL_PROOF"
