from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping
import json

from hhs_installer.canonical import hash216, stable
from hhs_installer.journal import atomic_write_json


class RequirementStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    STATICALLY_MAPPED = "STATICALLY_MAPPED"
    EXECUTED_POSITIVE = "EXECUTED_POSITIVE"
    EXECUTED_NEGATIVE = "EXECUTED_NEGATIVE"
    CALIBRATED = "CALIBRATED"
    REPAIRED = "REPAIRED"
    REVALIDATED = "REVALIDATED"
    NOT_APPLICABLE_WITH_JUSTIFICATION = "NOT_APPLICABLE_WITH_JUSTIFICATION"
    BLOCKED_BY_EXTERNAL_DEPENDENCY = "BLOCKED_BY_EXTERNAL_DEPENDENCY"
    VERIFIED = "VERIFIED"


@dataclass(frozen=True)
class CoverageRecord:
    requirement_id: str
    requirement_text_hash: str
    implementation_paths: tuple[str, ...]
    test_paths: tuple[str, ...]
    profiles: tuple[str, ...]
    platforms: tuple[str, ...]
    architectures: tuple[str, ...]
    positive_evidence: tuple[str, ...] = ()
    negative_evidence: tuple[str, ...] = ()
    calibration_evidence: tuple[str, ...] = ()
    repair_evidence: tuple[str, ...] = ()
    terminal_status: RequirementStatus = RequirementStatus.NOT_STARTED
    justification: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["terminal_status"] = self.terminal_status.value
        return stable(result)


class CoverageMatrix:
    def __init__(self, records: Iterable[CoverageRecord] = ()) -> None:
        ordered = sorted(records, key=lambda item: item.requirement_id)
        identifiers = [item.requirement_id for item in ordered]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("P173_DUPLICATE_REQUIREMENT_ID")
        self._records = {item.requirement_id: item for item in ordered}

    @classmethod
    def from_traceability(cls, path: str | Path) -> "CoverageMatrix":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        records: list[CoverageRecord] = []
        for mapping in payload.get("mappings", []):
            for requirement_id in mapping.get("requirement_ids", []):
                records.append(
                    CoverageRecord(
                        requirement_id=str(requirement_id),
                        requirement_text_hash=hash216(
                            {"requirement_id": requirement_id, "implementation_paths": mapping.get("implementation_paths", [])},
                            domain="HHS-P173-REQUIREMENT-TEXT-REFERENCE-V1",
                        ),
                        implementation_paths=tuple(mapping.get("implementation_paths", [])),
                        test_paths=tuple(mapping.get("test_paths", [])),
                        profiles=("all-applicable",),
                        platforms=("all-claimed",),
                        architectures=("all-claimed",),
                        terminal_status=RequirementStatus.STATICALLY_MAPPED,
                    )
                )
        return cls(records)

    def records(self) -> tuple[CoverageRecord, ...]:
        return tuple(self._records[key] for key in sorted(self._records))

    def update(
        self,
        requirement_id: str,
        *,
        status: RequirementStatus,
        positive_evidence: Iterable[str] = (),
        negative_evidence: Iterable[str] = (),
        calibration_evidence: Iterable[str] = (),
        repair_evidence: Iterable[str] = (),
        justification: str | None = None,
    ) -> None:
        current = self._records[requirement_id]
        if status is RequirementStatus.NOT_APPLICABLE_WITH_JUSTIFICATION and not justification:
            raise ValueError("P173_NA_JUSTIFICATION_REQUIRED")
        self._records[requirement_id] = CoverageRecord(
            requirement_id=current.requirement_id,
            requirement_text_hash=current.requirement_text_hash,
            implementation_paths=current.implementation_paths,
            test_paths=current.test_paths,
            profiles=current.profiles,
            platforms=current.platforms,
            architectures=current.architectures,
            positive_evidence=tuple(sorted(set(current.positive_evidence) | set(positive_evidence))),
            negative_evidence=tuple(sorted(set(current.negative_evidence) | set(negative_evidence))),
            calibration_evidence=tuple(sorted(set(current.calibration_evidence) | set(calibration_evidence))),
            repair_evidence=tuple(sorted(set(current.repair_evidence) | set(repair_evidence))),
            terminal_status=status,
            justification=justification or current.justification,
        )

    def verify_terminal_coverage(self) -> tuple[bool, list[str]]:
        incomplete: list[str] = []
        for record in self.records():
            if record.terminal_status is RequirementStatus.VERIFIED:
                if not record.positive_evidence or not record.negative_evidence:
                    incomplete.append(f"{record.requirement_id}:verified_without_positive_and_negative_evidence")
            elif record.terminal_status is RequirementStatus.NOT_APPLICABLE_WITH_JUSTIFICATION:
                if not record.justification:
                    incomplete.append(f"{record.requirement_id}:missing_justification")
            else:
                incomplete.append(f"{record.requirement_id}:{record.terminal_status.value}")
        return not incomplete, incomplete

    def to_dict(self) -> dict[str, Any]:
        records = [item.to_dict() for item in self.records()]
        complete, incomplete = self.verify_terminal_coverage()
        payload = {
            "schema": "HHS_PASS_173_COVERAGE_MATRIX_V1",
            "records": records,
            "terminal_complete": complete,
            "incomplete": incomplete,
        }
        payload["matrix_identity"] = hash216(payload, domain="HHS-P173-COVERAGE-MATRIX-V1")
        return payload

    def write(self, path: str | Path) -> None:
        atomic_write_json(path, self.to_dict())
