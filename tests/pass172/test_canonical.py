from __future__ import annotations

from pathlib import Path

import pytest

from hhs_installer.canonical import CanonicalizationError, hash72, hash216, installation_identity


def _components() -> dict[str, object]:
    return {
        "contract": "HHS-P172-UCEOCI-DRVBRAS",
        "source": "source-id",
        "profile": "core",
        "platform": "Linux",
        "architecture": "x86_64",
        "dependencies": {"lock": "abc"},
        "native": {"artifact": "def"},
        "frontend": {},
        "provider": "disabled",
        "model": "skip",
        "evidence": ["validation-id"],
    }


def test_hashes_are_deterministic_and_domain_separated() -> None:
    value = {"b": 2, "a": 1}
    assert hash72(value) == hash72({"a": 1, "b": 2})
    assert hash216(value) == hash216({"a": 1, "b": 2})
    assert hash216(value, domain="A") != hash216(value, domain="B")
    assert len(hash72(value)) == 72
    assert len(hash216(value)) == 216


def test_installation_identity_excludes_runtime_metadata_by_construction() -> None:
    first = installation_identity(_components())
    second = installation_identity(_components())
    assert first == second


def test_float_rejected_from_canonical_identity() -> None:
    with pytest.raises(CanonicalizationError):
        hash216({"duration": 1.25})


def test_missing_identity_component_rejected() -> None:
    components = _components()
    del components["native"]
    with pytest.raises(CanonicalizationError):
        installation_identity(components)
