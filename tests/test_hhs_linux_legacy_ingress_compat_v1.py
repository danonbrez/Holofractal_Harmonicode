import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.api.standard_ingress_compat_routes import (
    LEGACY_ROUTE_ALIASES,
    LINUX_ADAPTER_BINDINGS,
    build_standard_ingress_router,
    compatibility_status,
)
from hhs_backend.runtime.hhs_workspace_authority_loop_v1 import WorkspaceAuthorityLoop
from hhs_backend.runtime.multimodal_workspace_ingress_v1 import (
    ingest_workspace_source,
    translate_legacy_modality,
)
from hhs_backend.runtime.runtime_workspace_project_v1 import create_workspace_project


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(build_standard_ingress_router(WorkspaceAuthorityLoop()))
    return TestClient(app)


def test_visual_program_legacy_graph_type_translates_instead_of_rejecting():
    project = create_workspace_project("legacy graph")
    result = ingest_workspace_source(
        project=project,
        source_name="visual-program.hhsgraph.json",
        payload={"nodes": [], "edges": []},
        declared_modality="JSON_EXECUTION_GRAPH",
        media_type="application/json",
    )

    assert result["ok"] is True
    assert result["packet"]["declared_modality"] == "GRAPH_OBJECT"
    assert result["packet"]["source_declared_modality"] == "JSON_EXECUTION_GRAPH"
    assert result["legacy_ingress_redirected"] is True
    assert (
        result["compatibility_translation"]["translation_reason"]
        == "LEGACY_MODALITY_ALIAS"
    )


def test_unknown_legacy_binary_type_is_preserved_reversibly():
    source = b"\x00\xfflegacy\x7f"
    project = create_workspace_project("unknown binary")
    result = ingest_workspace_source(
        project=project,
        source_name="opaque.vendor",
        payload=source,
        declared_modality="VENDOR_RECORD_V2",
        media_type="application/x-vendor-record",
    )

    assert result["ok"] is True
    assert result["packet"]["declared_modality"] == "BINARY"
    assert result["packet"]["transport_encoding"] == "BASE64_REVERSIBLE"
    assert result["compatibility_translation"]["unknown_external_type_preserved"] is True
    encoded = result["workspace_object"]["source_provenance"]
    assert encoded["source_commitment_hash72"]


def test_linux_and_web_media_types_translate_to_canonical_adapters():
    cases = [
        ("main.py", None, "text/x-python", "CODE"),
        ("payload", None, "application/json", "JSON"),
        ("table", None, "text/csv", "CSV"),
        ("program.elf", None, "application/x-executable", "COMPILED_ARTIFACT"),
        ("library.so", "SHARED_LIBRARY", "application/octet-stream", "COMPILED_ARTIFACT"),
        ("stdin", "STRING", "text/plain", "TEXT"),
    ]
    for source_name, declared, media_type, expected in cases:
        translated = translate_legacy_modality(
            source_name=source_name,
            declared_modality=declared,
            media_type=media_type,
        )
        assert translated["canonical_modality"] == expected


def test_raw_octet_stream_redirects_to_workspace_ingress():
    client = _client()
    response = client.post(
        "/api/runtime/ingress",
        content=b"\x00\x01\xfe\xff",
        headers={
            "content-type": "application/x-legacy-binary",
            "x-hhs-filename": "legacy.payload",
            "x-hhs-modality": "LEGACY_BLOB_V1",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["status"] == "LEGACY_INGRESS_TRANSLATED_AND_REDIRECTED"
    assert body["redirected_operation"] == "workspace:ingress.register"
    ingress = body["authority_decision"]["result"]
    assert ingress["packet"]["declared_modality"] == "BINARY"
    payload = ingress["workspace_object"]
    assert payload["source_preserved"] is True


def test_malformed_json_falls_back_to_reversible_binary_instead_of_422():
    client = _client()
    response = client.post(
        "/api/runtime/ingress/legacy?source_name=old.json",
        content=b'{not-json',
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["transport_mode"] == "JSON_RAW_FALLBACK"
    ingress = body["authority_decision"]["result"]
    assert ingress["packet"]["declared_modality"] == "BINARY"
    assert ingress["packet"]["transport_encoding"] == "BASE64_REVERSIBLE"


def test_urlencoded_form_is_translated_to_json_object():
    client = _client()
    response = client.post(
        "/api/ingress?source_name=legacy-form",
        content=b"alpha=1&alpha=2&beta=three",
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["transport_mode"] == "URLENCODED_FORM"
    assert body["authority_decision"]["result"]["packet"]["declared_modality"] == "JSON"


def test_standard_browser_multipart_single_file_uses_file_type():
    client = _client()
    response = client.post(
        "/api/runtime/ingress/upload",
        files={"file": ("legacy.py", b"print('ok')\n", "text/x-python")},
        data={"project_id": "project:default"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["transport_mode"] == "MULTIPART_SINGLE_FILE"
    ingress = body["authority_decision"]["result"]
    assert ingress["packet"]["declared_modality"] == "CODE"
    source = ingress["workspace_object"]["source_provenance"]
    assert source["source_commitment_hash72"]


def test_ingress_body_limit_remains_bounded(monkeypatch):
    monkeypatch.setenv("HHS_STANDARD_INGRESS_MAX_BYTES", "4")
    client = _client()
    response = client.post(
        "/api/runtime/ingress",
        content=b"12345",
        headers={"content-type": "application/octet-stream"},
    )
    assert response.status_code == 413
    assert response.json()["detail"]["classification"] == "HHS_STANDARD_INGRESS_BODY_TOO_LARGE"


def test_compatibility_status_declares_linux_surface_and_no_alternate_authority():
    status = compatibility_status()
    assert status["ok"] is True
    assert status["unknown_type_policy"] == "PRESERVE_AS_REVERSIBLE_BINARY"
    assert "FILESYSTEM" in status["linux_compatibility_surfaces"]
    assert "STDIN_STDOUT_PROCESS" in status["linux_compatibility_surfaces"]
    assert "UNIX_DOMAIN_SOCKET" in status["linux_compatibility_surfaces"]
    assert status["linux_backend_profile"] == "PASS187_EXECUTABLE_UBUNTU_LINUX_ADAPTERS"
    assert LINUX_ADAPTER_BINDINGS["FILESYSTEM"].endswith(".read_file")
    assert LINUX_ADAPTER_BINDINGS["STDIN_STDOUT_PROCESS"].endswith(".run_process")
    assert LINUX_ADAPTER_BINDINGS["UNIX_DOMAIN_SOCKET"].endswith(".unix_socket_roundtrip")
    assert status["frontend_authority"] == "REQUEST_ONLY_NO_CANONICAL_COMMIT_AUTHORITY"
    assert status["native_backend_authority"] == "HHS_FASTAPI_KERNEL_RUNTIME_AUTHORITY_V1"
    assert "/api/ingress" in LEGACY_ROUTE_ALIASES


def test_pass187_linux_adapters_remain_repository_visible():
    source = Path("hhs_runtime/pass187/adapters.py").read_text(encoding="utf-8")
    for surface in (
        "def read_file(",
        "def run_process(",
        "def unix_socket_roundtrip(",
        "def http_get(",
    ):
        assert surface in source



def test_pass220_compatibility_contract_maps_aliases_to_one_canonical_operation():
    contract = json.loads(
        Path(
            "contracts/pass220/PASS_220_STANDARD_LEGACY_INGRESS_COMPAT_1_0.json"
        ).read_text(encoding="utf-8")
    )
    assert contract["canonical_operation"]["operation_id"] == "workspace.ingress.register"
    assert contract["canonical_operation"]["canonical_http_path"] == "/api/runtime/workspace/command"
    assert contract["translation_policy"]["block_unknown_external_types"] is False
    assert contract["translation_policy"]["unknown_external_type_fallback"] == "BINARY"
    assert contract["authority_invariants"]["compatibility_aliases_map_to_one_canonical_operation"] is True
    assert contract["authority_invariants"]["native_backend_remains_authoritative"] is True
    assert {
        row["path"] for row in contract["compatibility_aliases"]
    } == set(LEGACY_ROUTE_ALIASES)


def test_compatibility_routes_are_declared_in_kernel_surface_map():
    source = Path("hhs_runtime/hhs_kernel_conformance_surface_map_v1.py").read_text(
        encoding="utf-8"
    )
    for path in (
        "/api/runtime/ingress",
        "/api/runtime/ingress/legacy",
        "/api/runtime/ingress/upload",
        "/api/ingress",
        "/api/runtime/ingress/compatibility",
    ):
        assert path in source
    assert "workspace.ingress.compatibility.submit" in source
    assert "ingress.register" in source
