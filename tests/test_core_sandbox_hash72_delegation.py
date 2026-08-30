from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

import hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 as runtime
from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import security_hash72_v44


def test_security_hash72_v44_delegates_to_authoritative_kernel() -> None:
    payload = {
        "tuple": ("xy", "yx"),
        "fraction": Fraction(144, 72),
        "path": Path("alpha/beta"),
        "nested": {"b": 2, "a": 1},
    }
    domain = "P170_CORE_SANDBOX_HASH72_DELEGATION_TEST"

    kernel = runtime.load_authoritative_kernel()
    canonical = runtime.canonicalize_for_hash72(payload)
    expected = kernel.security_hash72_v44(canonical, domain=domain)

    assert security_hash72_v44(payload, domain=domain) == expected


def test_security_hash72_v44_fails_closed_without_authority(monkeypatch: pytest.MonkeyPatch) -> None:
    def unavailable_kernel():
        raise runtime.HHSRuntimeLoadError("authoritative kernel unavailable")

    monkeypatch.setattr(runtime, "load_authoritative_kernel", unavailable_kernel)

    with pytest.raises(runtime.HHSRuntimeLoadError, match="authoritative kernel unavailable"):
        security_hash72_v44({"state": "candidate"}, domain="P170_FAIL_CLOSED_TEST")
