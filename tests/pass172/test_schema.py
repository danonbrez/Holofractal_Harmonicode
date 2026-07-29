from __future__ import annotations

import pytest

from hhs_installer.schema import (
    InstallationRequest,
    InstallerSchemaError,
    NetworkPolicy,
    Profile,
    SourceKind,
    SourceSpec,
)


def test_request_round_trip() -> None:
    request = InstallationRequest(
        source=SourceSpec(SourceKind.LOCAL, "."),
        profile=Profile.CORE,
        timeout_seconds=120,
    )
    reconstructed = InstallationRequest.from_mapping(request.to_dict())
    assert reconstructed == request
    assert reconstructed.to_dict()["contract_id"] == "HHS-P172-UCEOCI-DRVBRAS"


def test_unknown_request_field_rejected() -> None:
    with pytest.raises(InstallerSchemaError) as raised:
        InstallationRequest.from_mapping(
            {
                "contract_id": "HHS-P172-UCEOCI-DRVBRAS",
                "operation": "install",
                "source": {"kind": "local", "reference": "."},
                "profile": "core",
                "install_mode": "user",
                "network_policy": "online",
                "privilege_policy": "prompt",
                "provider_policy": "disabled",
                "model_policy": "skip",
                "parallel_runtime": True,
            }
        )
    assert raised.value.code == "P172_UNKNOWN_REQUEST_FIELDS"


def test_offline_profile_requires_offline_policy() -> None:
    with pytest.raises(InstallerSchemaError) as raised:
        InstallationRequest(
            source=SourceSpec(SourceKind.LOCAL, "."),
            profile=Profile.OFFLINE,
            network_policy=NetworkPolicy.ONLINE,
        )
    assert raised.value.code == "P172_OFFLINE_PROFILE_NETWORK_POLICY"


def test_timeout_is_bounded() -> None:
    with pytest.raises(InstallerSchemaError):
        InstallationRequest(timeout_seconds=0)
    with pytest.raises(InstallerSchemaError):
        InstallationRequest(timeout_seconds=86_401)
