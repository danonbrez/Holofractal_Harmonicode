from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread
import hashlib
import json

import pytest

from hhs_installer.model_assets import ModelAssetError, ModelAssetManager, ModelAssetRequest
from hhs_installer.provider import ProviderResolver, ProviderState
from hhs_installer.schema import NetworkPolicy, SourceKind


class _ModelsHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/v1/models":
            payload = json.dumps({"data": [{"id": "gemma4-12b"}]}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


def test_external_loopback_provider_verified() -> None:
    server = HTTPServer(("127.0.0.1", 0), _ModelsHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        endpoint = f"http://127.0.0.1:{server.server_port}/v1"
        result = ProviderResolver(timeout_seconds=3).classify(
            mode="external",
            endpoint=endpoint,
            model_id="gemma4-12b",
        )
        assert result.state is ProviderState.EXTERNAL_READY
        assert result.health_verified is True
        assert result.model_registry_verified is True
    finally:
        server.shutdown()
        thread.join(timeout=3)


def test_public_unprotected_provider_rejected() -> None:
    result = ProviderResolver(timeout_seconds=1).classify(
        mode="external",
        endpoint="http://example.com/v1",
        model_id="gemma4-12b",
    )
    assert result.state is ProviderState.INCOMPATIBLE
    assert result.blocker == "P172_EXTERNAL_PROVIDER_TRANSPORT_UNPROTECTED"


def test_disabled_provider_does_not_probe_network() -> None:
    result = ProviderResolver(timeout_seconds=1).classify(mode="disabled")
    assert result.state is ProviderState.DISABLED
    assert result.health_verified is False


def _request(source: Path) -> ModelAssetRequest:
    return ModelAssetRequest(
        registry_id="test-model",
        source_reference=str(source),
        source_kind=SourceKind.LOCAL,
        filename="model.bin",
        version="1",
        license_id="TEST-LICENSE",
        expected_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        provider="test-provider",
        expected_size=source.stat().st_size,
    )


def test_model_import_and_idempotent_reuse(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    source.write_bytes(b"model-bytes")
    manager = ModelAssetManager(tmp_path / "models")
    first = manager.import_asset(
        _request(source),
        network_policy=NetworkPolicy.OFFLINE,
        license_accepted=True,
        authentication_available=False,
        available_bytes=10_000,
    )
    second = manager.import_asset(
        _request(source),
        network_policy=NetworkPolicy.OFFLINE,
        license_accepted=True,
        authentication_available=False,
        available_bytes=10_000,
    )
    assert first.reused_existing is False
    assert second.reused_existing is True
    assert first.model_identity == second.model_identity
    assert Path(first.installed_path).read_bytes() == b"model-bytes"


def test_model_license_rejection_has_no_import(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    source.write_bytes(b"model-bytes")
    manager = ModelAssetManager(tmp_path / "models")
    with pytest.raises(ModelAssetError) as raised:
        manager.import_asset(
            _request(source),
            network_policy=NetworkPolicy.OFFLINE,
            license_accepted=False,
            authentication_available=False,
        )
    assert raised.value.code == "P172_MODEL_LICENSE_REJECTED"
    assert not list((tmp_path / "models").rglob("model.bin"))
