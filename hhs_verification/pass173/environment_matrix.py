from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from hhs_installer.canonical import hash216, stable


@dataclass(frozen=True)
class EnvironmentCase:
    case_id: str
    platform: str
    architecture: str
    profile: str
    real_runner: bool
    expected_classification: str
    required_capabilities: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


@dataclass(frozen=True)
class EnvironmentResult:
    case_id: str
    executed: bool
    observed_classification: str
    matched: bool
    evidence: tuple[str, ...]
    blocker: str | None
    result_identity: str

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


class EnvironmentMatrix:
    def __init__(self, cases: Iterable[EnvironmentCase]) -> None:
        ordered = sorted(cases, key=lambda item: item.case_id)
        if len({item.case_id for item in ordered}) != len(ordered):
            raise ValueError("P173_DUPLICATE_ENVIRONMENT_CASE")
        self.cases = {item.case_id: item for item in ordered}
        self.results: dict[str, EnvironmentResult] = {}

    def record(
        self,
        case_id: str,
        *,
        executed: bool,
        observed_classification: str,
        evidence: Iterable[str] = (),
        blocker: str | None = None,
    ) -> EnvironmentResult:
        case = self.cases[case_id]
        matched = executed and observed_classification == case.expected_classification
        if not executed:
            observed_classification = "P173_PLATFORM_NOT_VERIFIED"
            matched = False
            blocker = blocker or "real compatible runner not executed"
        payload = {
            "case": case.to_dict(),
            "executed": executed,
            "observed_classification": observed_classification,
            "matched": matched,
            "evidence": sorted(set(evidence)),
            "blocker": blocker,
        }
        result = EnvironmentResult(
            case_id=case_id,
            executed=executed,
            observed_classification=observed_classification,
            matched=matched,
            evidence=tuple(payload["evidence"]),
            blocker=blocker,
            result_identity=hash216(payload, domain="HHS-P173-ENVIRONMENT-RESULT-V1"),
        )
        self.results[case_id] = result
        return result

    def to_dict(self) -> dict[str, Any]:
        rows = []
        for case_id in sorted(self.cases):
            case = self.cases[case_id]
            result = self.results.get(case_id)
            rows.append({"case": case.to_dict(), "result": None if result is None else result.to_dict()})
        complete = all(item["result"] is not None and item["result"]["matched"] for item in rows)
        payload = {
            "schema": "HHS_PASS_173_ENVIRONMENT_MATRIX_V1",
            "rows": rows,
            "terminal_complete": complete,
            "unverified": [item["case"]["case_id"] for item in rows if item["result"] is None or not item["result"]["matched"]],
        }
        payload["matrix_identity"] = hash216(payload, domain="HHS-P173-ENVIRONMENT-MATRIX-V1")
        return stable(payload)


def minimum_contract_matrix() -> EnvironmentMatrix:
    cases = (
        EnvironmentCase("ubuntu-24.04-x86_64-core", "Ubuntu 24.04", "x86_64", "core", True, "HHS_ENVIRONMENT_CORE_ONLY_COMPATIBLE", ("python_3_11", "c11_compiler")),
        EnvironmentCase("ubuntu-24.04-aarch64-core", "Ubuntu 24.04", "aarch64", "core", True, "HHS_ENVIRONMENT_CORE_ONLY_COMPATIBLE", ("python_3_11", "c11_compiler")),
        EnvironmentCase("macos-arm64-runtime", "macOS", "arm64", "runtime", True, "HHS_ENVIRONMENT_COMPATIBLE_IN_ASSISTANT_DEGRADED_MODE", ("python_3_11", "c11_compiler", "loopback")),
        EnvironmentCase("windows-x86_64-runtime", "Windows", "x86_64", "runtime", True, "HHS_ENVIRONMENT_COMPATIBLE_IN_ASSISTANT_DEGRADED_MODE", ("python_3_11", "c11_compiler", "loopback")),
        EnvironmentCase("oci-x86_64-core", "OCI", "x86_64", "container", True, "HHS_ENVIRONMENT_CONTAINER_COMPATIBLE", ("container_runtime",)),
        EnvironmentCase("android-build", "Android build host", "declared", "android-build", True, "HHS_ENVIRONMENT_ANDROID_BUILD_COMPATIBLE", ("java", "android_sdk", "android_ndk")),
        EnvironmentCase("real-local-gpu", "supported", "supported", "assistant-local-gpu", True, "HHS_ENVIRONMENT_FULLY_COMPATIBLE", ("gpu_device", "vulkan_or_metal")),
    )
    return EnvironmentMatrix(cases)
