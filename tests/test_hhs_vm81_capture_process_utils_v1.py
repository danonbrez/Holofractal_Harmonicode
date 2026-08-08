from __future__ import annotations

import ast
from fractions import Fraction
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "native_projects" / "hhs_vm81_game_level10" / "tools"
SHARED = TOOLS / "hhs_capture_process_utils_v1.py"
CONSUMERS = (
    TOOLS / "render_sprite_capture.py",
    TOOLS / "render_terminal_capture.py",
)


def _load_shared():
    spec = importlib.util.spec_from_file_location("hhs_capture_process_utils_v1", SHARED)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_shared_rate_parser_is_exact_fractional_tooling() -> None:
    module = _load_shared()
    assert module.parse_rate("") == Fraction(0, 1)
    assert module.parse_rate("0/0") == Fraction(0, 1)
    assert module.parse_rate("30000/1001") == Fraction(30000, 1001)


def test_shared_run_checked_preserves_captured_text_contract() -> None:
    module = _load_shared()
    result = module.run_checked([sys.executable, "-c", "print('vm81-shared')"])
    assert result.returncode == 0
    assert result.stdout == "vm81-shared\n"
    assert result.stderr == ""


def test_consumers_import_helpers_instead_of_reimplementing_them() -> None:
    for path in CONSUMERS:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        definitions = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        assert "parse_rate" not in definitions
        assert "run_checked" not in definitions
        imports = [
            node
            for node in tree.body
            if isinstance(node, ast.ImportFrom)
            and node.module == "hhs_capture_process_utils_v1"
        ]
        assert imports
        imported = {alias.name for node in imports for alias in node.names}
        assert {"parse_rate", "run_checked"} <= imported


def test_shared_module_has_no_hhs_mutation_authority_imports() -> None:
    tree = ast.parse(SHARED.read_text(encoding="utf-8"))
    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)
    assert not any(name.startswith("hhs_runtime") for name in imported_modules)
    assert not any(name.startswith("hhs_backend") for name in imported_modules)
