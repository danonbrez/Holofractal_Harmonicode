#!/usr/bin/env python3
"""Verify that external LiteRT-LM is not in the default runtime dependency closure."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

_TARGET_PACKAGE = "litert-lm"
_INCLUDE_RE = re.compile(r"^(?:-r|--requirement)(?:\s+|=)(.+?)\s*$", re.IGNORECASE)
_PACKAGE_RE = re.compile(r"^([A-Za-z0-9_.-]+)(?:\[[^\]]+\])?(?:\s*(?:===|==|~=|!=|<=|>=|<|>|@)|\s*$)")


class DependencyClosureError(RuntimeError):
    """Raised when the default requirements closure admits external LiteRT-LM."""


def _canonical_package_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _active_requirement(line: str) -> str:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return ""
    # Requirements-file comments begin after whitespace + '#'. Preserve URL
    # fragments such as '#egg=' because they are not preceded by whitespace.
    return re.sub(r"\s+#.*$", "", stripped).strip()


def _iter_active_lines(path: Path) -> Iterable[tuple[int, str]]:
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        active = _active_requirement(raw)
        if active:
            yield number, active


def verify_default_runtime_closure(entry: Path) -> tuple[Path, ...]:
    """Walk active requirements includes and reject LiteRT-LM admission."""

    entry = entry.resolve()
    root = entry.parent
    visited: set[Path] = set()
    stack: list[Path] = [entry]

    while stack:
        current = stack.pop().resolve()
        if current in visited:
            continue
        visited.add(current)

        try:
            current.relative_to(root)
        except ValueError as exc:
            raise DependencyClosureError(
                f"requirements include escapes repository closure: {current}"
            ) from exc

        if not current.is_file():
            raise DependencyClosureError(f"requirements include is missing: {current}")

        for line_number, active in _iter_active_lines(current):
            include = _INCLUDE_RE.match(active)
            if include:
                value = include.group(1).strip().strip("\"'")
                if "://" in value:
                    raise DependencyClosureError(
                        f"remote requirements include cannot be closure-verified: "
                        f"{current}:{line_number}: {value}"
                    )
                child = (current.parent / value).resolve()
                stack.append(child)
                continue

            package = _PACKAGE_RE.match(active)
            if package and _canonical_package_name(package.group(1)) == _TARGET_PACKAGE:
                raise DependencyClosureError(
                    "external LiteRT-LM must not be in the default runtime "
                    f"dependency closure: {current}:{line_number}: {active}"
                )

    return tuple(sorted(visited))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("requirements", nargs="?", default="requirements.txt")
    args = parser.parse_args()

    try:
        visited = verify_default_runtime_closure(Path(args.requirements))
    except DependencyClosureError as exc:
        print(f"LITERT_LM_DEFAULT_CLOSURE_FAIL: {exc}")
        return 1

    print(
        "LITERT_LM_DEFAULT_CLOSURE_PASS "
        f"files={len(visited)} target={_TARGET_PACKAGE}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
