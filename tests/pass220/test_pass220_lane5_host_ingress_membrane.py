from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import pytest

from hhs_backend.lane5_ingress_gateway import (
    GATEWAY_SCHEMA,
    Lane5IngressMediator,
    Lane5IngressRejected,
    serialize_environmental_ingress,
)
from deployment.digitalocean.configure_lane5_ingress_nginx import patch_nginx_text

ROOT = Path(__file__).resolve().parents[2]


class _FakeBridge:
    def __init__(self, *, authority_overrides=None, receipt_overrides=None):
        self.authority_overrides = authority_overrides or {}
        self.receipt_overrides = receipt_overrides or {}
        self.last_workload = None

    def authority(self):
        value = {
            "any_byte_serializable_workload": True,
            "workload_class_agnostic": True,
            "streaming_candidate_ingress": True,
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash216_authority": False,
            "requires_signed_environmental_vm81_admission": True,
        }
        value.update(self.authority_overrides)
        return value

    def optimize(self, *, workload, **_kwargs):
        self.last_workload = workload
        value = {
            "admitted_candidates": 1,
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash216_authority": False,
            "requires_signed_environmental_vm81_admission": True,
            "workload_sha256": workload.workload_sha256.hex(),
            "route_receipt_signature64": 123456789,
        }
        value.update(self.receipt_overrides)
        return value


def test_environmental_ingress_serialization_is_exact_and_order_sensitive() -> None:
    first = serialize_environmental_ingress(
        transport=b"http",
        method_or_opcode=b"POST",
        raw_path=b"/api/test",
        query_string=b"x=1",
        headers=((b"x-a", b"1"), (b"x-b", b"2")),
        payload=b"abc",
    )
    replay = serialize_environmental_ingress(
        transport=b"http",
        method_or_opcode=b"POST",
        raw_path=b"/api/test",
        query_string=b"x=1",
        headers=((b"x-a", b"1"), (b"x-b", b"2")),
        payload=b"abc",
    )
    swapped = serialize_environmental_ingress(
        transport=b"http",
        method_or_opcode=b"POST",
        raw_path=b"/api/test",
        query_string=b"x=1",
        headers=((b"x-b", b"2"), (b"x-a", b"1")),
        payload=b"abc",
    )
    assert first == replay
    assert first != swapped
    assert first.startswith(GATEWAY_SCHEMA.encode("ascii") + b"\0")


def test_lane5_host_mediator_binds_actual_request_bytes_and_stays_candidate_only() -> None:
    fake = _FakeBridge()
    mediator = Lane5IngressMediator(bridge_factory=lambda: fake)
    raw = serialize_environmental_ingress(
        transport=b"http",
        method_or_opcode=b"POST",
        raw_path=b"/api/assistant",
        query_string=b"",
        headers=((b"content-type", b"application/json"),),
        payload=b'{"message":"hello"}',
    )
    receipt = mediator.mediate(raw, provenance="network:http:POST:/api/assistant")
    assert fake.last_workload is not None
    assert fake.last_workload.workload_sha256 == sha256(raw).digest()
    assert receipt["candidate_only"] is True
    assert receipt["canonical_vm81_mutation_authority"] is False
    assert receipt["canonical_hash216_authority"] is False
    assert receipt["requires_signed_environmental_vm81_admission"] is True


@pytest.mark.parametrize(
    "overrides",
    [
        {"candidate_only": False},
        {"canonical_vm81_mutation_authority": True},
        {"canonical_hash216_authority": True},
        {"requires_signed_environmental_vm81_admission": False},
    ],
)
def test_lane5_host_mediator_rejects_authority_drift(overrides) -> None:
    mediator = Lane5IngressMediator(
        bridge_factory=lambda: _FakeBridge(authority_overrides=overrides)
    )
    with pytest.raises(Lane5IngressRejected):
        mediator.health()


def test_nginx_migration_replaces_public_backend_bypass_only() -> None:
    source = """
server {
    listen 443 ssl;
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
    }
}
"""
    updated, changed = patch_nginx_text(source)
    assert changed is True
    assert "proxy_pass http://127.0.0.1:8715;" in updated
    assert "proxy_pass http://127.0.0.1:8080;" not in updated
    assert "proxy_http_version 1.1;" in updated
    assert "proxy_set_header Upgrade $http_upgrade;" in updated
    assert "proxy_set_header Connection $http_connection;" in updated

    replay, replay_changed = patch_nginx_text(updated)
    assert replay == updated
    assert replay_changed is False


def test_nginx_migration_preserves_existing_websocket_connection_policy() -> None:
    source = """
server {
    listen 443 ssl;
    location / {
        proxy_pass http://127.0.0.1:8715;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $hhs_connection_upgrade;
        proxy_set_header Host $host;
    }
}
"""
    updated, changed = patch_nginx_text(source)
    assert changed is False
    assert updated.count("proxy_set_header Connection ") == 1
    assert "proxy_set_header Connection $hhs_connection_upgrade;" in updated


def test_production_network_surfaces_have_no_direct_public_runtime_bypass() -> None:
    vm_nginx = (
        ROOT / "deployment/ubuntu/application_vm/nginx-hhs-application-vm.conf"
    ).read_text(encoding="utf-8")
    https = (ROOT / "scripts/complete_hhs_production_https_mobile.sh").read_text(
        encoding="utf-8"
    )
    static_first = (
        ROOT / "deployment/digitalocean/configure_runtime_os_static_first.py"
    ).read_text(encoding="utf-8")
    assert "proxy_pass http://127.0.0.1:8720" not in vm_nginx
    assert "proxy_pass http://127.0.0.1:8715" in vm_nginx
    expected_backend = 'HHS_BACKEND="' + "$" + '{HHS_BACKEND:-http://127.0.0.1:8715}"'
    assert expected_backend in https
    assert 'BACKEND_MARKER = "proxy_pass http://127.0.0.1:8715"' in static_first
    assert "root {root};" not in static_first


def test_lane5_gateway_systemd_and_installer_are_restartable_and_ssh_independent() -> None:
    service = (
        ROOT / "deploy/digitalocean/hhs-lane5-ingress.service"
    ).read_text(encoding="utf-8")
    socket = (
        ROOT / "deploy/digitalocean/hhs-lane5-ingress.socket"
    ).read_text(encoding="utf-8")
    installer = (
        ROOT / "deployment/digitalocean/guarded_auto_update/install.sh"
    ).read_text(encoding="utf-8")

    for token in (
        "--fd 3",
        "Sockets=hhs-lane5-ingress.socket",
        "HHS_DISABLE_C_AUTOBUILD=1",
        "StartLimitIntervalSec=300",
        "StartLimitBurst=5",
        "RestartSec=10",
        "NoNewPrivileges=true",
    ):
        assert token in service

    for token in (
        "hhs-lane5-ingress.service",
        "configure_lane5_ingress_nginx.py",
        "http://127.0.0.1:8715/__hhs_lane5_ingress_health",
        "HHS_LANE5_HOST_INGRESS_READY=1",
        "HHS_LANE5_HOST_INGRESS_SOCKET_ACTIVATED=1",
        "HHS_LANE5_HOST_INGRESS_NGINX_ZERO_BYPASS=1",
    ):
        assert token in installer

    assert "Requires=hhs.service" not in service
    assert "After=network-online.target hhs.service" not in service
    assert "ListenStream=127.0.0.1:8715" in socket
    assert "Service=hhs-lane5-ingress.service" in socket
    assert "WantedBy=sockets.target" in socket
    assert "sshd.service" not in service
    assert "port 22" not in service.lower()
