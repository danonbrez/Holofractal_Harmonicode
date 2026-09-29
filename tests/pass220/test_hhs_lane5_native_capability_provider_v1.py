from __future__ import annotations

import json
from pathlib import Path

import pytest

from hhs_runtime.hhs_lane5_native_capability_provider_v1 import (
    CAPABILITIES,
    Lane5CapabilityProviderError,
    capability_spec,
    lane5_capability_provider_status,
    resolve_lane5_capability,
)

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contracts/pass220/PASS_220_LANE5_NATIVE_CAPABILITY_PROVIDER_V1.json"


def test_lane5_all_registered_capabilities_default_to_native() -> None:
    status = lane5_capability_provider_status(environ={})
    assert status["global_default_provider"] == "native"
    assert status["external_provider_requires_explicit_selection_at_runtime"] is True
    assert status["pull_request_native_unavailable_falls_back_to_declared_external"] is True
    assert status["pull_request_fallback_requires_warning"] is True
    assert status["unknown_capabilities_fail_closed"] is True
    assert status["runtime_missing_native_implementation_fails_closed"] is True
    assert status["authority"]["vm81_admission_authority"] is False
    assert status["authority"]["hash72_commit_authority"] is False
    assert status["authority"]["hash216_persistence_authority"] is False

    rows = {row["capability_id"]: row for row in status["capabilities"]}
    assert set(rows) == set(CAPABILITIES)
    for row in rows.values():
        assert row["selected_provider"] == "native"
        assert row["explicit_selection"] is False
        assert row["runtime_implicit_external_fallback_allowed"] is False
        assert row["pull_request_external_fallback_allowed"] is True
        assert row["default_provider"] == "native"


@pytest.mark.parametrize(
    "capability_id",
    [
        "fastapi",
        "python1",
        "python2",
        "numpy",
        "three_js",
        "webgl",
        "litert_lm",
        "mathlib",
        "lean4",
    ],
)
def test_implemented_lane5_native_capabilities_resolve_real_repository_surfaces(
    capability_id: str,
) -> None:
    resolution = resolve_lane5_capability(capability_id, environ={})
    assert resolution.provider == "native"
    assert resolution.explicit is False
    assert resolution.native_implemented is True
    assert resolution.native_surfaces
    for surface in resolution.native_surfaces:
        assert (ROOT / surface).exists(), (capability_id, surface)


@pytest.mark.parametrize("capability_id", ["matplotlib", "fastapi_application"])
def test_incomplete_native_capabilities_fail_closed_at_runtime(capability_id: str) -> None:
    spec = capability_spec(capability_id)
    assert spec.native_implemented is False
    assert spec.native_surfaces == ()
    with pytest.raises(
        Lane5CapabilityProviderError,
        match=f"HHS_LANE5_NATIVE_IMPLEMENTATION_UNAVAILABLE:{capability_id}",
    ):
        resolve_lane5_capability(capability_id, environ={}, provider_context="runtime")


def test_matplotlib_pull_request_falls_back_to_declared_external_with_warning() -> None:
    with pytest.warns(
        RuntimeWarning,
        match="HHS_LANE5_PR_EXTERNAL_PROVIDER_FALLBACK:matplotlib",
    ):
        resolution = resolve_lane5_capability(
            "matplotlib",
            environ={},
            provider_context="pull_request",
        )
    assert resolution.provider == "external"
    assert resolution.explicit is False
    assert resolution.fallback_used is True
    assert resolution.external_target == "Matplotlib"
    assert resolution.native_unavailable_reason == (
        "HHS_LANE5_NATIVE_IMPLEMENTATION_UNAVAILABLE:matplotlib"
    )
    assert resolution.warning is not None
    assert "compatibility_only_no_canonical_authority" in resolution.warning


def test_pull_request_status_exposes_fallback_warning_receipt() -> None:
    status = lane5_capability_provider_status(
        environ={},
        provider_context="pull_request",
    )
    rows = {row["capability_id"]: row for row in status["capabilities"]}
    for capability_id in ("matplotlib", "fastapi_application"):
        row = rows[capability_id]
        assert row["selected_provider"] == "external"
        assert row["pull_request_fallback_used"] is True
        assert row["warning"].startswith(
            f"HHS_LANE5_PR_EXTERNAL_PROVIDER_FALLBACK:{capability_id}"
        )
    assert rows["fastapi"]["selected_provider"] == "native"
    assert rows["numpy"]["selected_provider"] == "native"
    assert rows["numpy"]["pull_request_fallback_used"] is False


@pytest.mark.parametrize(
    "capability_id",
    [
        "fastapi",
        "python1",
        "python2",
        "numpy",
        "matplotlib",
        "three_js",
        "webgl",
        "litert_lm",
        "mathlib",
        "lean4",
    ],
)
def test_external_lane5_provider_requires_explicit_per_capability_selection(
    capability_id: str,
) -> None:
    spec = capability_spec(capability_id)
    resolution = resolve_lane5_capability(
        capability_id,
        environ={spec.env_name: "external"},
    )
    assert resolution.provider == "external"
    assert resolution.explicit is True
    assert resolution.external_target == spec.external_target


def test_explicit_global_external_selection_is_still_explicit() -> None:
    resolution = resolve_lane5_capability(
        "numpy",
        environ={"HHS_LANE5_PROVIDER_DEFAULT": "external"},
    )
    assert resolution.provider == "external"
    assert resolution.explicit is True


def test_invalid_provider_and_unknown_capability_fail_closed() -> None:
    numpy_spec = capability_spec("numpy")
    with pytest.raises(
        Lane5CapabilityProviderError,
        match="HHS_LANE5_PROVIDER_INVALID:numpy:auto",
    ):
        resolve_lane5_capability(
            "numpy",
            environ={numpy_spec.env_name: "auto"},
        )
    with pytest.raises(
        Lane5CapabilityProviderError,
        match="HHS_LANE5_CAPABILITY_UNREGISTERED",
    ):
        resolve_lane5_capability("unregistered_foreign_runtime", environ={})


def test_contract_freezes_native_default_for_current_and_future_capabilities() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    rule = contract["governing_rule"]
    assert contract["scope"] == "ALL_HARMONICODE_NATIVE_LANE5_CAPABILITIES"
    assert rule["implicit_provider"] == "HHS_NATIVE"
    assert rule["runtime_external_provider_requires_explicit_selection"] is True
    assert rule["installed_external_package_never_overrides_native_default"] is True
    assert rule["runtime_missing_native_implementation_fails_closed"] is True
    assert rule["pull_request_native_unavailable_falls_back_to_declared_external"] is True
    assert rule["pull_request_fallback_requires_warning"] is True
    assert rule["future_native_capabilities_inherit_rule"] is True
    assert contract["selection"]["auto_mode_allowed"] is False
    assert set(contract["registered_capabilities"]) == set(CAPABILITIES)


def test_lane5_threejs_application_remains_repository_native() -> None:
    html = (
        ROOT
        / "applications/holofractal_harmonizer/lane5_holographic_sprite_5184.html"
    ).read_text(encoding="utf-8")
    assert "../../hhs_gui/rendering/hhs_harmonicode_three_webgl_v1.js" in html
    assert "new HHS3D.WebGLRenderer" in html
    assert "three.min.js" not in html
    assert "cdn.jsdelivr.net/npm/three" not in html
    assert "cdnjs.cloudflare.com/ajax/libs/three" not in html
