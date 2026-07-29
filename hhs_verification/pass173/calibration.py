from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from hhs_installer.canonical import hash216, stable


@dataclass(frozen=True)
class CalibrationBoundary:
    metric: str
    maximum_integer_value: int
    unit: str

    def __post_init__(self) -> None:
        if self.maximum_integer_value < 0:
            raise ValueError("P173_CALIBRATION_BOUNDARY_INVALID")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CalibrationMeasurement:
    fixture_id: str
    metric: str
    integer_value: int
    unit: str
    expected_classification: str
    observed_classification: str
    evidence: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


class CalibrationCorpus:
    def __init__(self, boundaries: Iterable[CalibrationBoundary]) -> None:
        self.boundaries = {item.metric: item for item in boundaries}
        self.measurements: list[CalibrationMeasurement] = []

    def record(self, measurement: CalibrationMeasurement) -> dict[str, Any]:
        if measurement.integer_value < 0:
            raise ValueError("P173_CALIBRATION_VALUE_INVALID")
        boundary = self.boundaries.get(measurement.metric)
        within = boundary is None or (
            measurement.unit == boundary.unit
            and measurement.integer_value <= boundary.maximum_integer_value
        )
        classification_match = measurement.expected_classification == measurement.observed_classification
        self.measurements.append(measurement)
        payload = {
            "measurement": measurement.to_dict(),
            "boundary": None if boundary is None else boundary.to_dict(),
            "within_boundary": within,
            "classification_match": classification_match,
        }
        payload["result_identity"] = hash216(payload, domain="HHS-P173-CALIBRATION-RESULT-V1")
        return stable(payload)

    def to_dict(self) -> dict[str, Any]:
        results = []
        for measurement in self.measurements:
            boundary = self.boundaries.get(measurement.metric)
            results.append(
                {
                    "measurement": measurement.to_dict(),
                    "boundary": None if boundary is None else boundary.to_dict(),
                    "within_boundary": boundary is None or (
                        measurement.unit == boundary.unit
                        and measurement.integer_value <= boundary.maximum_integer_value
                    ),
                    "classification_match": measurement.expected_classification == measurement.observed_classification,
                }
            )
        measured_metrics = {item["measurement"]["metric"] for item in results}
        required_metrics = set(self.boundaries)
        missing_metrics = sorted(required_metrics - measured_metrics)
        coverage_complete = bool(required_metrics) and not missing_metrics
        passed = bool(results) and coverage_complete and all(
            item["within_boundary"] and item["classification_match"] for item in results
        )
        payload = {
            "schema": "HHS_PASS_173_CALIBRATION_CORPUS_V1",
            "boundaries": [item.to_dict() for item in sorted(self.boundaries.values(), key=lambda value: value.metric)],
            "results": results,
            "measured_metrics": sorted(measured_metrics),
            "missing_metrics": missing_metrics,
            "coverage_complete": coverage_complete,
            "passed": passed,
        }
        payload["corpus_identity"] = hash216(payload, domain="HHS-P173-CALIBRATION-CORPUS-V1")
        return stable(payload)


def default_boundaries() -> tuple[CalibrationBoundary, ...]:
    return (
        CalibrationBoundary("probe_retries", 3, "attempts"),
        CalibrationBoundary("provider_readiness_attempts", 12, "attempts"),
        CalibrationBoundary("port_selection_attempts", 16, "attempts"),
        CalibrationBoundary("archive_entries", 100_000, "entries"),
        CalibrationBoundary("archive_expanded_bytes", 4 * 1024 * 1024 * 1024, "bytes"),
        CalibrationBoundary("lock_age", 3_600_000_000_000, "nanoseconds"),
        CalibrationBoundary("rollback_versions", 5, "versions"),
    )
