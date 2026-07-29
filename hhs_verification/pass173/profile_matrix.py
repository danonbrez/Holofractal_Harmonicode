from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from hhs_installer.canonical import hash216, stable


@dataclass(frozen=True)
class ProfileExpectation:
    profile: str
    included_dependencies: tuple[str, ...]
    excluded_dependencies: tuple[str, ...]
    callable_surfaces: tuple[str, ...]
    provider_state: str

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


@dataclass(frozen=True)
class ProfileResult:
    profile: str
    included_match: bool
    excluded_match: bool
    callable_match: bool
    provider_match: bool
    evidence: tuple[str, ...]
    classification: str
    result_identity: str

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


class ProfileMatrix:
    def __init__(self, expectations: Iterable[ProfileExpectation]) -> None:
        ordered = sorted(expectations, key=lambda item: item.profile)
        if len({item.profile for item in ordered}) != len(ordered):
            raise ValueError("P173_DUPLICATE_PROFILE_EXPECTATION")
        self.expectations = {item.profile: item for item in ordered}
        self.results: dict[str, ProfileResult] = {}

    def record(
        self,
        profile: str,
        *,
        included_dependencies: Iterable[str],
        installed_dependencies: Iterable[str],
        callable_surfaces: Iterable[str],
        provider_state: str,
        evidence: Iterable[str] = (),
    ) -> ProfileResult:
        expected = self.expectations[profile]
        included = set(included_dependencies)
        installed = set(installed_dependencies)
        callable_set = set(callable_surfaces)
        required_dependencies = set(expected.included_dependencies)
        included_match = required_dependencies.issubset(included) and required_dependencies.issubset(installed)
        excluded_match = set(expected.excluded_dependencies).isdisjoint(installed)
        callable_match = set(expected.callable_surfaces).issubset(callable_set)
        provider_match = expected.provider_state == provider_state
        passed = included_match and excluded_match and callable_match and provider_match
        payload = {
            "expectation": expected.to_dict(),
            "included_dependencies": sorted(included),
            "installed_dependencies": sorted(installed),
            "missing_in_plan": sorted(required_dependencies - included),
            "missing_from_installation": sorted(required_dependencies - installed),
            "callable_surfaces": sorted(callable_set),
            "provider_state": provider_state,
            "evidence": sorted(set(evidence)),
        }
        result = ProfileResult(
            profile=profile,
            included_match=included_match,
            excluded_match=excluded_match,
            callable_match=callable_match,
            provider_match=provider_match,
            evidence=tuple(payload["evidence"]),
            classification="P173_PROFILE_VERIFIED" if passed else "P173_PROFILE_CLOSURE_MISMATCH",
            result_identity=hash216(payload, domain="HHS-P173-PROFILE-RESULT-V1"),
        )
        self.results[profile] = result
        return result

    def to_dict(self) -> dict[str, Any]:
        rows = []
        for profile in sorted(self.expectations):
            result = self.results.get(profile)
            rows.append({"expectation": self.expectations[profile].to_dict(), "result": None if result is None else result.to_dict()})
        complete = all(row["result"] is not None and row["result"]["classification"] == "P173_PROFILE_VERIFIED" for row in rows)
        payload = {
            "schema": "HHS_PASS_173_PROFILE_MATRIX_V1",
            "rows": rows,
            "terminal_complete": complete,
            "unverified": [row["expectation"]["profile"] for row in rows if row["result"] is None or row["result"]["classification"] != "P173_PROFILE_VERIFIED"],
        }
        payload["matrix_identity"] = hash216(payload, domain="HHS-P173-PROFILE-MATRIX-V1")
        return stable(payload)


def canonical_expectations() -> ProfileMatrix:
    return ProfileMatrix(
        (
            ProfileExpectation("core", ("core-python-packages", "c11-compiler"), ("litert-lm-provider", "node-runtime", "android-toolchain"), ("hhs", "vm81", "hash72", "hash216"), "DISABLED"),
            ProfileExpectation("runtime", ("core-python-packages", "runtime-python-packages"), ("litert-lm-provider", "android-toolchain"), ("http", "websocket", "visual-server"), "DEGRADED"),
            ProfileExpectation("assistant-external", ("runtime-python-packages",), ("litert-lm-provider", "model-asset-local"), ("assistant-api",), "EXTERNAL_READY"),
            ProfileExpectation("assistant-local-cpu", ("runtime-python-packages", "litert-lm-provider"), ("gpu-loader",), ("assistant-api", "provider-supervision"), "LOCAL_CPU_READY"),
            ProfileExpectation("assistant-local-gpu", ("runtime-python-packages", "litert-lm-provider", "gpu-loader"), (), ("assistant-api", "provider-supervision"), "LOCAL_GPU_READY"),
            ProfileExpectation("developer", ("runtime-python-packages", "node-runtime"), ("android-toolchain",), ("frontend-build", "browser-test"), "DEGRADED"),
            ProfileExpectation("android-build", ("core-python-packages", "android-toolchain"), ("litert-lm-provider",), ("apk-build", "jni-build"), "DISABLED"),
            ProfileExpectation("container", ("runtime-python-packages", "container-runtime"), (), ("oci-build", "healthcheck"), "DEGRADED"),
            ProfileExpectation("offline", ("core-python-packages",), (), ("offline-verify",), "DISABLED"),
        )
    )
