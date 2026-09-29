"""Lane 5 native capability provider policy.

Every HARMONICODE-owned Lane 5 capability resolves to its repository-native
implementation by default. External runtimes/libraries are compatibility,
testing, or deployment membranes and require an explicit per-capability
selection. There is no implicit "auto" fallback to an installed package.

A capability whose native implementation is declared but not yet implemented
fails closed in native mode. This prevents an absent native provider from
silently re-authorizing a foreign dependency.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import os
from pathlib import Path
import re
from typing import Any, Mapping

SCHEMA = "HHS_LANE5_NATIVE_CAPABILITY_PROVIDER_V1"
GLOBAL_DEFAULT_ENV = "HHS_LANE5_PROVIDER_DEFAULT"
ROOT = Path(__file__).resolve().parents[1]


class Lane5CapabilityProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class Lane5CapabilitySpec:
    capability_id: str
    native_surfaces: tuple[str, ...]
    external_target: str
    native_implemented: bool = True
    external_role: str = "EXPLICIT_COMPATIBILITY_ONLY"
    authority: str = "NO_CANONICAL_AUTHORITY_TRANSFER"

    @property
    def env_name(self) -> str:
        normalized = re.sub(r"[^A-Z0-9]+", "_", self.capability_id.upper()).strip("_")
        return f"HHS_LANE5_PROVIDER_{normalized}"

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["env_name"] = self.env_name
        value["default_provider"] = "native"
        return value


@dataclass(frozen=True)
class Lane5CapabilityResolution:
    capability_id: str
    provider: str
    explicit: bool
    native_implemented: bool
    native_surfaces: tuple[str, ...]
    external_target: str
    authority: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "capability_id": self.capability_id,
            "provider": self.provider,
            "explicit": self.explicit,
            "native_implemented": self.native_implemented,
            "native_surfaces": list(self.native_surfaces),
            "external_target": self.external_target,
            "external_role": "EXPLICIT_COMPATIBILITY_ONLY",
            "authority": self.authority,
            "canonical_state_mutation_authority": False,
            "vm81_admission_authority": False,
            "hash72_commit_authority": False,
            "hash216_persistence_authority": False,
            "host_float_canonical_authority": False,
        }


CAPABILITIES: Mapping[str, Lane5CapabilitySpec] = {
    "fastapi": Lane5CapabilitySpec(
        capability_id="fastapi",
        native_surfaces=(
            "hhs_backend/runtime/hhs_native_fastapi_compat_v1.py",
            "native_projects/hhs_pass220_fastapi_native_route_kernel",
        ),
        external_target="FastAPI/Starlette",
    ),
    "python1": Lane5CapabilitySpec(
        capability_id="python1",
        native_surfaces=(
            "hhs_runtime/hhs_pass220_python_native_execution_v1.py",
            "native_projects/hhs_pass220_python_native_execution",
        ),
        external_target="CPython 3.12",
    ),
    "python2": Lane5CapabilitySpec(
        capability_id="python2",
        native_surfaces=(
            "hhs_runtime/hhs_pass220_python_rna_class_registration_v1.py",
            "hhs_runtime/include/hhs_pass220_python_rna_class_registration_2_0.h",
        ),
        external_target="CPython object/class model",
    ),
    "numpy": Lane5CapabilitySpec(
        capability_id="numpy",
        native_surfaces=(
            "hhs_runtime/hhs_pass220_numpy_harmonicode_array_v1.py",
            "native_projects/hhs_pass220_numpy_native_array_kernel",
        ),
        external_target="NumPy",
    ),
    "matplotlib": Lane5CapabilitySpec(
        capability_id="matplotlib",
        native_surfaces=(),
        external_target="Matplotlib",
        native_implemented=False,
    ),
    "three_js": Lane5CapabilitySpec(
        capability_id="three_js",
        native_surfaces=(
            "hhs_gui/rendering/hhs_harmonicode_three_webgl_v1.js",
            "applications/holofractal_harmonizer/lane5_holographic_sprite_5184.html",
        ),
        external_target="Three.js / OrbitControls",
    ),
    "webgl": Lane5CapabilitySpec(
        capability_id="webgl",
        native_surfaces=(
            "hhs_gui/rendering/hhs_harmonicode_three_webgl_v1.js",
            "hhs_gui/rendering/hhs_harmonicode_render_packet_wasm_v1.js",
        ),
        external_target="direct application-owned WebGL/WebGL2",
    ),
    "litert_lm": Lane5CapabilitySpec(
        capability_id="litert_lm",
        native_surfaces=(
            "hhs_backend/runtime/hhs_native_litert_lm_provider_v1.py",
            "hhs_backend/runtime/hhs_pass220_native_litert_runtime_v1.py",
        ),
        external_target="LiteRT-LM 0.14.0 / OpenAI-compatible external provider",
    ),
    "mathlib": Lane5CapabilitySpec(
        capability_id="mathlib",
        native_surfaces=(
            "hhs_runtime/hhs_pass220_i048_native_mathlib_v1.py",
            "formal/lean/HHS/Mathlib/Native.lean",
            "native_projects/hhs_pass220_mathlib_native",
        ),
        external_target="upstream Mathlib semantic/runtime substitution",
    ),
    "lean4": Lane5CapabilitySpec(
        capability_id="lean4",
        native_surfaces=(
            "formal/lean/HHS/Mathlib/Native.lean",
            "formal/lean/HHS/Mathlib/Algebra/Native.lean",
        ),
        external_target="unbound external Lean proof/runtime authority",
    ),
}


def capability_spec(capability_id: str) -> Lane5CapabilitySpec:
    key = str(capability_id).strip().lower()
    try:
        return CAPABILITIES[key]
    except KeyError as exc:
        raise Lane5CapabilityProviderError(
            f"HHS_LANE5_CAPABILITY_UNREGISTERED:{key}"
        ) from exc


def _requested_provider(
    spec: Lane5CapabilitySpec,
    *,
    environ: Mapping[str, str] | None = None,
) -> tuple[str, bool]:
    env = os.environ if environ is None else environ
    if spec.env_name in env:
        value = str(env[spec.env_name]).strip().lower()
        explicit = True
    elif GLOBAL_DEFAULT_ENV in env:
        value = str(env[GLOBAL_DEFAULT_ENV]).strip().lower()
        explicit = True
    else:
        value = "native"
        explicit = False
    if value not in {"native", "external"}:
        raise Lane5CapabilityProviderError(
            f"HHS_LANE5_PROVIDER_INVALID:{spec.capability_id}:{value}:"
            "expected native|external"
        )
    return value, explicit


def _validate_native_surfaces(spec: Lane5CapabilitySpec) -> None:
    if not spec.native_implemented:
        raise Lane5CapabilityProviderError(
            f"HHS_LANE5_NATIVE_IMPLEMENTATION_UNAVAILABLE:{spec.capability_id}"
        )
    missing = [
        surface
        for surface in spec.native_surfaces
        if not (ROOT / surface).exists()
    ]
    if missing:
        raise Lane5CapabilityProviderError(
            "HHS_LANE5_NATIVE_SURFACE_MISSING:"
            + spec.capability_id
            + ":"
            + ",".join(missing)
        )


def resolve_lane5_capability(
    capability_id: str,
    *,
    environ: Mapping[str, str] | None = None,
    validate_native: bool = True,
) -> Lane5CapabilityResolution:
    spec = capability_spec(capability_id)
    provider, explicit = _requested_provider(spec, environ=environ)

    if provider == "external" and not explicit:
        raise Lane5CapabilityProviderError(
            f"HHS_LANE5_EXTERNAL_PROVIDER_REQUIRES_EXPLICIT_SELECTION:{spec.capability_id}"
        )

    if provider == "native" and validate_native:
        _validate_native_surfaces(spec)

    return Lane5CapabilityResolution(
        capability_id=spec.capability_id,
        provider=provider,
        explicit=explicit,
        native_implemented=spec.native_implemented,
        native_surfaces=spec.native_surfaces,
        external_target=spec.external_target,
        authority=spec.authority,
    )


def lane5_capability_provider_status(
    *,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for capability_id in sorted(CAPABILITIES):
        spec = CAPABILITIES[capability_id]
        provider, explicit = _requested_provider(spec, environ=environ)
        native_surfaces_present = all(
            (ROOT / surface).exists() for surface in spec.native_surfaces
        ) if spec.native_surfaces else False
        rows.append({
            **spec.to_dict(),
            "selected_provider": provider,
            "explicit_selection": explicit,
            "native_surfaces_present": native_surfaces_present,
            "implicit_external_fallback_allowed": False,
        })
    return {
        "schema": SCHEMA,
        "global_default_provider": "native",
        "external_provider_requires_explicit_selection": True,
        "unknown_capabilities_fail_closed": True,
        "missing_native_implementation_fails_closed": True,
        "capabilities": rows,
        "authority": {
            "canonical_state_mutation_authority": False,
            "vm81_admission_authority": False,
            "hash72_commit_authority": False,
            "hash216_persistence_authority": False,
            "host_float_canonical_authority": False,
        },
    }


__all__ = [
    "CAPABILITIES",
    "GLOBAL_DEFAULT_ENV",
    "Lane5CapabilityProviderError",
    "Lane5CapabilityResolution",
    "Lane5CapabilitySpec",
    "capability_spec",
    "lane5_capability_provider_status",
    "resolve_lane5_capability",
]
