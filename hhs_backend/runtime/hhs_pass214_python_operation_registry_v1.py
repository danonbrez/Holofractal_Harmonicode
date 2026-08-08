"""Precise Python declarative operation-registry extraction for Pass 214."""
from __future__ import annotations

import ast
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Any, Iterable

from hhs_backend.runtime.hhs_pass214_cumulative_operation_census_v1 import MAX_DEFAULT_BYTES, _read, _record

STRICT_REGISTRY_RE = re.compile(
    r"(?:^|_)(?:OP|OPS|OPCODE|OPCODES|OPERATOR|OPERATORS|OPERATION|OPERATIONS|"
    r"DISPATCH|DISPATCHES|COMMAND|COMMANDS|ACTION|ACTIONS|SERVICE|SERVICES|"
    r"CAPABILITY|CAPABILITIES|TRANSITION|TRANSITIONS|BYTECODE|PRIMITIVE|PRIMITIVES)(?:_|$)",
    re.I,
)
OPERATOR_TOKENS = {
    "+", "-", "*", "/", "%", "==", "!=", "<", "<=", ">", ">=", "=", ":=", "->", "=>", "**", "//", "&", "|", "^", "~", "<<", ">>",
}
IDENTITY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.:/-]*$")


def _tracked_python(root: Path) -> list[str]:
    raw = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z", "*.py", "*.pyi"])
    return sorted(x.decode("utf-8", "surrogateescape") for x in raw.split(b"\0") if x)


def _target_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    return None


def _literal_entries(node: ast.AST) -> Iterable[tuple[str, int, str]]:
    if isinstance(node, ast.Dict):
        for key in node.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, (str, int)):
                yield str(key.value), int(getattr(key, "lineno", 0) or 0), "DICT_KEY"
    elif isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        for entry in node.elts:
            if isinstance(entry, ast.Constant) and isinstance(entry.value, (str, int)):
                yield str(entry.value), int(getattr(entry, "lineno", 0) or 0), "SEQUENCE_ENTRY"


def _credible(value: str) -> bool:
    value = value.strip()
    if not value or len(value) > 160:
        return False
    if value in OPERATOR_TOKENS:
        return True
    if len(value) < 2 or value.replace(".", "").isdigit():
        return False
    return bool(IDENTITY_RE.fullmatch(value))


def extract_python_operation_registry_keys(repository_root: Path, *, max_source_bytes: int = MAX_DEFAULT_BYTES) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    root = repository_root.resolve()
    records: list[dict[str, Any]] = []
    parse_errors: list[str] = []
    registries = 0
    files = 0
    for path in _tracked_python(root):
        if set(PurePosixPath(path).parts) & {"tests", "test", "fixtures", "evidence", "benchmarks", "benchmark"}:
            continue
        text = _read(root, path, max_source_bytes)
        if text is None:
            continue
        try:
            tree = ast.parse(text)
        except (SyntaxError, ValueError):
            parse_errors.append(path)
            continue
        found_in_file = False
        for node in ast.walk(tree):
            target = None
            value = None
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target = _target_name(node.targets[0]); value = node.value
            elif isinstance(node, ast.AnnAssign):
                target = _target_name(node.target); value = node.value
            if not target or value is None or not STRICT_REGISTRY_RE.search(target):
                continue
            entries = [(name, line, shape) for name, line, shape in _literal_entries(value) if _credible(name)]
            if not entries:
                continue
            registries += 1
            found_in_file = True
            for name, line, shape in entries:
                records.append(_record(path, line or int(getattr(node, "lineno", 0) or 0), "PYTHON_OPERATION_REGISTRY_KEY", name, registry=target, registry_shape=shape))
        if found_in_file:
            files += 1
    unique = {row["operation_key"]: row for row in records}
    return list(unique.values()), {
        "python_registry_files": files,
        "python_operation_registries": registries,
        "python_operation_registry_keys": len(unique),
        "python_registry_parse_errors": parse_errors,
        "policy": "STRUCTURAL_KEYS_ONLY_STRICT_OPERATION_REGISTRY_NAMES",
    }
