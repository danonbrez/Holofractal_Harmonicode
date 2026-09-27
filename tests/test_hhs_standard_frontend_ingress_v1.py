from pathlib import Path

import pytest

from hhs_backend.frontend_ingress_policy_v1 import (
    FrontendIngressPolicyError,
    STANDARD_BROWSER_METHODS,
    configured_frontend_ingress_policy,
    frontend_ingress_policy_self_test,
    parse_allowed_origins,
)


def test_standard_frontend_ingress_policy_self_test():
    result = frontend_ingress_policy_self_test()
    assert result["ok"] is True


def test_same_origin_is_default_and_cross_origin_is_explicit():
    policy = configured_frontend_ingress_policy({})
    assert policy["cors_allowed_origins"] == []
    assert policy["same_origin_requires_cors"] is False
    assert policy["wildcard_origin_forbidden"] is True
    assert policy["frontend_authority"] == "REQUEST_AND_PROJECTION_ONLY"
    assert policy["backend_authority"] == "HHS_FASTAPI_KERNEL_RUNTIME_AUTHORITY_V1"


def test_exact_cross_origin_frontends_are_normalized_and_deduplicated():
    assert parse_allowed_origins(
        "https://console.example.com/,http://127.0.0.1:5173,"
        "https://console.example.com"
    ) == [
        "https://console.example.com",
        "http://127.0.0.1:5173",
    ]


@pytest.mark.parametrize(
    "origin",
    [
        "*",
        "example.com",
        "https://example.com/path",
        "https://example.com/?query=1",
    ],
)
def test_unsafe_or_non_origin_cors_values_fail_closed(origin):
    with pytest.raises(FrontendIngressPolicyError):
        parse_allowed_origins(origin)


def test_standard_browser_methods_remain_available_at_transport_membrane():
    assert STANDARD_BROWSER_METHODS == (
        "GET",
        "HEAD",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    )


def test_canonical_server_no_longer_combines_wildcard_origin_with_credentials():
    source = Path("hhs_backend/server.py").read_text(encoding="utf-8")
    assert "configured_frontend_ingress_policy" in source
    assert 'allow_origins=["*"]' not in source
    assert 'allow_origins=FRONTEND_INGRESS_POLICY["cors_allowed_origins"]' in source
    assert 'allow_credentials=FRONTEND_INGRESS_POLICY["allow_credentials"]' in source


def test_production_env_documents_external_frontend_origin_configuration():
    example = Path("deploy/digitalocean/hhs-pass196.env.example").read_text(
        encoding="utf-8"
    )
    service = Path(
        "deploy/digitalocean/hhs-pass196-integrated-environment.service"
    ).read_text(encoding="utf-8")
    assert "HHS_CORS_ALLOWED_ORIGINS" in example
    assert "EnvironmentFile=-/etc/hhs/pass196.env" in service


def test_standard_frontend_contract_keeps_native_authority_boundary():
    policy = configured_frontend_ingress_policy(
        {"HHS_CORS_ALLOWED_ORIGINS": "https://frontend.example"}
    )
    assert policy["cors_allowed_origins"] == ["https://frontend.example"]
    assert policy["allow_credentials"] is True
    assert policy["allow_headers"] == ["*"]
    assert "x-hhs-runtime-cache" in policy["expose_headers"]
    assert "OPTIONS" in policy["allow_methods"]
