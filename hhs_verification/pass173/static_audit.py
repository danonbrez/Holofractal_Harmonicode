from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping
import json

from hhs_installer.canonical import hash216, stable
from .requirement_scanner import RequirementClause, RequirementScanner


@dataclass(frozen=True)
class TraceabilityFinding:
    requirement_id: str
    implementation_paths: tuple[str, ...]
    test_paths: tuple[str, ...]
    existing_implementation_paths: tuple[str, ...]
    existing_test_paths: tuple[str, ...]
    classification: str

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


class StaticAudit:
    def __init__(self, repository_root: str | Path) -> None:
        self.root = Path(repository_root).resolve()

    def audit(
        self,
        *,
        pass172_contract: str | Path,
        pass173_contract: str | Path,
        traceability_path: str | Path,
    ) -> dict[str, Any]:
        scanner = RequirementScanner()
        scan = scanner.scan_pair(pass172_contract, pass173_contract)
        traceability = json.loads(Path(traceability_path).read_text(encoding="utf-8"))
        mapped: dict[str, dict[str, Any]] = {}
        for group in traceability.get("mappings", []):
            for requirement_id in group.get("requirement_ids", []):
                mapped[str(requirement_id)] = group

        findings: list[TraceabilityFinding] = []
        for group in traceability.get("mappings", []):
            implementation_paths = tuple(str(item) for item in group.get("implementation_paths", ()))
            test_paths = tuple(str(item) for item in group.get("test_paths", ()))
            existing_implementation = tuple(path for path in implementation_paths if (self.root / path).exists())
            existing_tests = tuple(path for path in test_paths if (self.root / path).exists())
            for requirement_id in group.get("requirement_ids", []):
                if existing_implementation and existing_tests:
                    classification = "P173_REQUIREMENT_STATICALLY_MAPPED"
                elif existing_implementation:
                    classification = "P173_REQUIREMENT_IMPLEMENTATION_WITHOUT_TEST"
                else:
                    classification = "P173_REQUIREMENT_IMPLEMENTATION_MISSING"
                findings.append(
                    TraceabilityFinding(
                        requirement_id=str(requirement_id),
                        implementation_paths=implementation_paths,
                        test_paths=test_paths,
                        existing_implementation_paths=existing_implementation,
                        existing_test_paths=existing_tests,
                        classification=classification,
                    )
                )
        payload = {
            "schema": "HHS_PASS_173_STATIC_AUDIT_V1",
            "requirement_scan": scan,
            "traceability_findings": [item.to_dict() for item in sorted(findings, key=lambda item: item.requirement_id)],
            "summary": {
                "normative_clauses": scan["counts"]["total"],
                "mapping_groups": len(traceability.get("mappings", [])),
                "mapped_requirements": len(findings),
                "implementation_missing": sum(item.classification == "P173_REQUIREMENT_IMPLEMENTATION_MISSING" for item in findings),
                "tests_missing": sum(item.classification == "P173_REQUIREMENT_IMPLEMENTATION_WITHOUT_TEST" for item in findings),
            },
        }
        payload["audit_identity"] = hash216(payload, domain="HHS-P173-STATIC-AUDIT-V1")
        return stable(payload)
