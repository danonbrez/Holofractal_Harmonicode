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
        groups = list(traceability.get("mappings", []))

        exact_by_id: dict[str, dict[str, Any]] = {}
        exact_by_hash: dict[str, dict[str, Any]] = {}
        legacy_mapping_ids: list[str] = []
        for group in groups:
            legacy_mapping_ids.extend(str(item) for item in group.get("requirement_ids", ()))
            for requirement_id in group.get("scanner_requirement_ids", ()):
                exact_by_id[str(requirement_id)] = group
            for text_hash in group.get("requirement_hashes", ()):
                exact_by_hash[str(text_hash)] = group

        clauses = [
            RequirementClause(**item)
            for key in ("pass172", "pass173")
            for item in scan.get(key, [])
        ]
        findings: list[TraceabilityFinding] = []
        for clause in clauses:
            group = exact_by_id.get(clause.requirement_id) or exact_by_hash.get(clause.text_hash)
            if group is None:
                findings.append(
                    TraceabilityFinding(
                        requirement_id=clause.requirement_id,
                        implementation_paths=(),
                        test_paths=(),
                        existing_implementation_paths=(),
                        existing_test_paths=(),
                        classification="P173_REQUIREMENT_UNMAPPED",
                    )
                )
                continue

            implementation_paths = tuple(str(item) for item in group.get("implementation_paths", ()))
            test_paths = tuple(str(item) for item in group.get("test_paths", ()))
            existing_implementation = tuple(path for path in implementation_paths if (self.root / path).exists())
            existing_tests = tuple(path for path in test_paths if (self.root / path).exists())
            if existing_implementation and existing_tests:
                classification = "P173_REQUIREMENT_STATICALLY_MAPPED"
            elif existing_implementation:
                classification = "P173_REQUIREMENT_IMPLEMENTATION_WITHOUT_TEST"
            else:
                classification = "P173_REQUIREMENT_IMPLEMENTATION_MISSING"
            findings.append(
                TraceabilityFinding(
                    requirement_id=clause.requirement_id,
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
            "legacy_mapping_ids": sorted(set(legacy_mapping_ids)),
            "summary": {
                "normative_clauses": scan["counts"]["total"],
                "mapping_groups": len(groups),
                "mapped_requirements": sum(item.classification != "P173_REQUIREMENT_UNMAPPED" for item in findings),
                "unmapped_requirements": sum(item.classification == "P173_REQUIREMENT_UNMAPPED" for item in findings),
                "implementation_missing": sum(item.classification == "P173_REQUIREMENT_IMPLEMENTATION_MISSING" for item in findings),
                "tests_missing": sum(item.classification == "P173_REQUIREMENT_IMPLEMENTATION_WITHOUT_TEST" for item in findings),
                "full_normative_coverage": bool(findings) and all(
                    item.classification == "P173_REQUIREMENT_STATICALLY_MAPPED" for item in findings
                ),
            },
        }
        payload["audit_identity"] = hash216(payload, domain="HHS-P173-STATIC-AUDIT-V1")
        return stable(payload)
