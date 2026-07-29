from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping
import ast
import json
import re
import sys

from hhs_installer.canonical import hash216, stable


@dataclass(frozen=True)
class PythonImportRecord:
    path: str
    module: str
    optional: bool
    line: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RequirementRecord:
    source_file: str
    requirement: str
    package_name: str
    marker: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NativeProjectRecord:
    path: str
    has_makefile: bool
    has_cmake: bool
    c_sources: int
    headers: int
    classification: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DependencyScanner:
    STANDARD_LIBRARY = frozenset(getattr(sys, "stdlib_module_names", ())) | {
        "__future__",
        "builtins",
        "contextvars",
        "fcntl",
        "msvcrt",
        "resource",
        "winreg",
        "zlib",
    }

    def __init__(self, repository_root: str | Path) -> None:
        self.root = Path(repository_root).resolve()

    def scan_python_imports(self, roots: Iterable[str | Path]) -> tuple[PythonImportRecord, ...]:
        records: list[PythonImportRecord] = []
        for root_value in roots:
            root = (self.root / root_value).resolve() if not Path(root_value).is_absolute() else Path(root_value).resolve()
            if not root.exists():
                continue
            paths = (root,) if root.is_file() else root.rglob("*.py")
            for path in sorted(paths):
                if not path.is_file() or any(part in {".git", ".venv", "venv", "__pycache__"} for part in path.parts):
                    continue
                try:
                    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
                except (OSError, UnicodeDecodeError, SyntaxError):
                    continue
                optional_lines = self._optional_import_lines(tree)
                for node in ast.walk(tree):
                    modules: list[str] = []
                    if isinstance(node, ast.Import):
                        modules.extend(alias.name.split(".")[0] for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                        modules.append(node.module.split(".")[0])
                    for module in modules:
                        records.append(
                            PythonImportRecord(
                                path=str(path.relative_to(self.root)).replace("\\", "/"),
                                module=module,
                                optional=getattr(node, "lineno", 0) in optional_lines,
                                line=int(getattr(node, "lineno", 0)),
                            )
                        )
        unique = {(item.path, item.module, item.optional, item.line): item for item in records}
        return tuple(unique[key] for key in sorted(unique))

    @staticmethod
    def _optional_import_lines(tree: ast.AST) -> set[int]:
        lines: set[int] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Try) and any(isinstance(handler.type, ast.Name) and handler.type.id in {"ImportError", "ModuleNotFoundError"} for handler in node.handlers if handler.type):
                for child in node.body:
                    for nested in ast.walk(child):
                        if isinstance(nested, (ast.Import, ast.ImportFrom)):
                            lines.add(int(getattr(nested, "lineno", 0)))
        return lines

    def parse_requirements(self, paths: Iterable[str | Path]) -> tuple[RequirementRecord, ...]:
        records: list[RequirementRecord] = []
        visited: set[Path] = set()

        def parse(path: Path) -> None:
            resolved = path.resolve()
            if resolved in visited:
                return
            visited.add(resolved)
            if not resolved.is_file():
                return
            for raw in resolved.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith(("-r ", "--requirement ")):
                    include = line.split(maxsplit=1)[1]
                    parse((resolved.parent / include).resolve())
                    continue
                if line.startswith("-"):
                    continue
                requirement, separator, marker = line.partition(";")
                name_match = re.match(r"\s*([A-Za-z0-9_.-]+)", requirement)
                if not name_match:
                    continue
                records.append(
                    RequirementRecord(
                        source_file=str(resolved.relative_to(self.root)).replace("\\", "/") if self.root in resolved.parents else str(resolved),
                        requirement=requirement.strip(),
                        package_name=name_match.group(1).lower().replace("_", "-"),
                        marker=marker.strip() if separator else None,
                    )
                )

        for path_value in paths:
            path = (self.root / path_value).resolve() if not Path(path_value).is_absolute() else Path(path_value).resolve()
            parse(path)
        unique = {(item.source_file, item.requirement, item.marker): item for item in records}
        return tuple(unique[key] for key in sorted(unique))

    def undeclared_imports(
        self,
        imports: Iterable[PythonImportRecord],
        requirements: Iterable[RequirementRecord],
        *,
        internal_top_levels: Iterable[str] = (),
        import_to_package: Mapping[str, str] | None = None,
    ) -> tuple[dict[str, Any], ...]:
        declared = {item.package_name for item in requirements}
        internal = set(internal_top_levels)
        aliases = {key: value.lower().replace("_", "-") for key, value in (import_to_package or {}).items()}
        missing: list[dict[str, Any]] = []
        for record in imports:
            if record.module in self.STANDARD_LIBRARY or record.module in internal or record.optional:
                continue
            package = aliases.get(record.module, record.module.lower().replace("_", "-"))
            if package not in declared:
                missing.append({"classification": "P173_UNDECLARED_PYTHON_DEPENDENCY", **record.to_dict(), "expected_package": package})
        return tuple(sorted(missing, key=lambda item: (item["module"], item["path"], item["line"])))

    def native_project_inventory(self) -> tuple[NativeProjectRecord, ...]:
        root = self.root / "native_projects"
        if not root.is_dir():
            return ()
        projects: list[NativeProjectRecord] = []
        for child in sorted(path for path in root.iterdir() if path.is_dir()):
            makefiles = [child / "Makefile", child / "GNUmakefile"]
            has_makefile = any(path.is_file() for path in makefiles)
            has_cmake = (child / "CMakeLists.txt").is_file()
            c_sources = sum(1 for _ in child.rglob("*.c"))
            headers = sum(1 for _ in child.rglob("*.h"))
            if has_makefile or has_cmake:
                classification = "REQUIRED_PROFILE" if c_sources else "HISTORICAL_ONLY"
            elif c_sources:
                classification = "ORPHANED"
            else:
                classification = "HISTORICAL_ONLY"
            projects.append(
                NativeProjectRecord(
                    path=str(child.relative_to(self.root)).replace("\\", "/"),
                    has_makefile=has_makefile,
                    has_cmake=has_cmake,
                    c_sources=c_sources,
                    headers=headers,
                    classification=classification,
                )
            )
        return tuple(projects)

    def report(self) -> dict[str, Any]:
        requirement_paths = sorted(path.name for path in self.root.glob("requirements*.txt"))
        imports = self.scan_python_imports(("hhs_installer", "hhs_verification", "hhs_backend", "hhs_runtime", "python"))
        requirements = self.parse_requirements(requirement_paths)
        internal = {path.name for path in self.root.iterdir() if path.is_dir() and (path / "__init__.py").exists()}
        internal.update({"hhs_installer", "hhs_verification", "hhs_backend", "hhs_runtime", "python"})
        aliases = {"yaml": "pyyaml", "PIL": "pillow", "Crypto": "pycryptodome", "cv2": "opencv-python"}
        undeclared = self.undeclared_imports(imports, requirements, internal_top_levels=internal, import_to_package=aliases)
        native = self.native_project_inventory()
        payload = {
            "schema": "HHS_PASS_173_DEPENDENCY_SCAN_V1",
            "imports": [item.to_dict() for item in imports],
            "requirements": [item.to_dict() for item in requirements],
            "undeclared": list(undeclared),
            "native_projects": [item.to_dict() for item in native],
            "summary": {
                "imports": len(imports),
                "requirements": len(requirements),
                "undeclared": len(undeclared),
                "native_projects": len(native),
            },
        }
        payload["scan_identity"] = hash216(payload, domain="HHS-P173-DEPENDENCY-SCAN-V1")
        return stable(payload)
