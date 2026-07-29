from __future__ import annotations

from pathlib import Path
import json

from hhs_verification.pass173.dependency_scanner import DependencyScanner
from hhs_verification.pass173.requirement_scanner import RequirementScanner
from hhs_verification.pass173.static_audit import StaticAudit


def test_requirement_scanner_extracts_normative_clauses(tmp_path: Path) -> None:
    contract = tmp_path / "contract.md"
    contract.write_text(
        "# 1. Scope\n\nThe installer SHALL verify the source.\n\nThe verifier SHALL NOT trust self-reported counts.\n",
        encoding="utf-8",
    )
    clauses = RequirementScanner().scan(contract, pass_number=172)
    assert len(clauses) == 2
    assert clauses[0].section == "1. Scope"
    assert clauses[0].requirement_id.startswith("P172-R-")
    assert "SHALL" in clauses[0].normative_terms


def test_dependency_scanner_detects_undeclared_nonoptional_import(tmp_path: Path) -> None:
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "module.py").write_text(
        "import requests\ntry:\n    import optional_pkg\nexcept ImportError:\n    optional_pkg = None\n",
        encoding="utf-8",
    )
    (tmp_path / "requirements-core.txt").write_text("pydantic>=2\n", encoding="utf-8")
    scanner = DependencyScanner(tmp_path)
    imports = scanner.scan_python_imports(("pkg",))
    requirements = scanner.parse_requirements(("requirements-core.txt",))
    missing = scanner.undeclared_imports(imports, requirements, internal_top_levels=("pkg",))
    assert [item["module"] for item in missing] == ["requests"]


def test_native_inventory_generated_from_live_tree(tmp_path: Path) -> None:
    project = tmp_path / "native_projects" / "core"
    project.mkdir(parents=True)
    (project / "Makefile").write_text("all:\n\ttrue\n", encoding="utf-8")
    (project / "runtime.c").write_text("int main(void){return 0;}\n", encoding="utf-8")
    inventory = DependencyScanner(tmp_path).native_project_inventory()
    assert len(inventory) == 1
    assert inventory[0].path == "native_projects/core"
    assert inventory[0].classification == "REQUIRED_PROFILE"


def test_static_audit_reports_missing_paths(tmp_path: Path) -> None:
    p172 = tmp_path / "p172.md"
    p173 = tmp_path / "p173.md"
    p172.write_text("# A\nThe installer SHALL work.\n", encoding="utf-8")
    p173.write_text("# B\nThe verifier SHALL test it.\n", encoding="utf-8")
    traceability = tmp_path / "trace.json"
    traceability.write_text(
        json.dumps(
            {
                "mappings": [
                    {
                        "requirement_ids": ["P172-A"],
                        "implementation_paths": ["missing.py"],
                        "test_paths": ["test_missing.py"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    report = StaticAudit(tmp_path).audit(
        pass172_contract=p172,
        pass173_contract=p173,
        traceability_path=traceability,
    )
    assert report["summary"]["normative_clauses"] == 2
    assert report["summary"]["implementation_missing"] == 1
