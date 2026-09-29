from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator
import argparse
import json

SOURCE_SUFFIXES = frozenset({
    ".py", ".pyi",
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp",
})
PYTHON_SUFFIXES = frozenset({".py", ".pyi"})
JS_SUFFIXES = frozenset({".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"})
C_LIKE_SUFFIXES = frozenset({
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp",
})
SKIP_DIR_NAMES = frozenset({
    ".git", ".hg", ".svn",
    ".venv", "venv", "__pycache__",
    "node_modules", "dist", "build",
    "release_artifacts", "artifacts",
})

SCHEMA = "HHS_SOURCE_TEXT_INTEGRITY_V1"
BACKTICK = chr(96)


@dataclass(frozen=True)
class SourceTextIssue:
    path: str
    line: int
    column: int
    kind: str
    snippet: str


class SourceTextIntegrityError(RuntimeError):
    pass


def _iter_source_files(root: Path) -> Iterator[Path]:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        try:
            relative = path.relative_to(root)
        except ValueError:
            continue
        if any(part in SKIP_DIR_NAMES for part in relative.parts[:-1]):
            continue
        yield path


def _regex_can_start(text: str, index: int) -> bool:
    cursor = index - 1
    while cursor >= 0 and text[cursor] in " \t":
        cursor -= 1
    if cursor < 0 or text[cursor] == "\n":
        return True
    return text[cursor] in "=([{,:;!&|?"


def find_literal_escaped_newline_issues(path: str | Path, text: str) -> list[SourceTextIssue]:
    suffix = Path(path).suffix.lower()
    if suffix not in SOURCE_SUFFIXES:
        return []

    lines = text.splitlines()
    issues: list[SourceTextIssue] = []
    i = 0
    line = 1
    column = 1
    quote: str | None = None
    triple_quote = False
    block_comment = False
    line_comment = False
    regex_literal = False
    regex_character_class = False
    template_stack: list[dict[str, object]] = []

    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""

        if ch == "\n":
            line += 1
            column = 1
            line_comment = False
            if regex_literal:
                regex_literal = False
                regex_character_class = False
            i += 1
            continue

        if line_comment:
            i += 1
            column += 1
            continue

        if block_comment:
            if ch == "*" and nxt == "/":
                block_comment = False
                i += 2
                column += 2
            else:
                i += 1
                column += 1
            continue

        if quote is not None:
            if triple_quote:
                if text.startswith(quote * 3, i):
                    quote = None
                    triple_quote = False
                    i += 3
                    column += 3
                    continue
                if ch == "\\":
                    step = min(2, len(text) - i)
                    i += step
                    column += step
                    continue
                i += 1
                column += 1
                continue

            if ch == "\\":
                step = min(2, len(text) - i)
                i += step
                column += step
                continue
            if ch == quote:
                quote = None
            i += 1
            column += 1
            continue

        if regex_literal:
            if ch == "\\":
                step = min(2, len(text) - i)
                i += step
                column += step
                continue
            if ch == "[":
                regex_character_class = True
            elif ch == "]":
                regex_character_class = False
            elif ch == "/" and not regex_character_class:
                regex_literal = False
            i += 1
            column += 1
            continue

        if suffix in PYTHON_SUFFIXES and ch == "#":
            line_comment = True
            i += 1
            column += 1
            continue

        if suffix in C_LIKE_SUFFIXES:
            if ch == "/" and nxt == "/":
                line_comment = True
                i += 2
                column += 2
                continue
            if ch == "/" and nxt == "*":
                block_comment = True
                i += 2
                column += 2
                continue

        if ch in {'"', "'"}:
            if suffix in PYTHON_SUFFIXES and text.startswith(ch * 3, i):
                quote = ch
                triple_quote = True
                i += 3
                column += 3
                continue
            quote = ch
            triple_quote = False
            i += 1
            column += 1
            continue

        if suffix in JS_SUFFIXES and ch == BACKTICK:
            template_stack.append({"mode": "text", "brace_depth": 0})
            i += 1
            column += 1
            continue

        if suffix in JS_SUFFIXES and template_stack and template_stack[-1]["mode"] == "expr":
            if ch == "{":
                template_stack[-1]["brace_depth"] = int(template_stack[-1]["brace_depth"]) + 1
                i += 1
                column += 1
                continue
            if ch == "}":
                depth = int(template_stack[-1]["brace_depth"]) - 1
                template_stack[-1]["brace_depth"] = depth
                if depth == 0:
                    template_stack[-1]["mode"] = "text"
                i += 1
                column += 1
                continue

        if suffix in JS_SUFFIXES and ch == "/" and _regex_can_start(text, i):
            regex_literal = True
            regex_character_class = False
            i += 1
            column += 1
            continue

        if ch == "\\" and nxt == "n":
            snippet = lines[line - 1] if 0 < line <= len(lines) else ""
            issues.append(SourceTextIssue(
                path=Path(path).as_posix(),
                line=line,
                column=column,
                kind="LITERAL_ESCAPED_NEWLINE_OUTSIDE_STRING_OR_COMMENT",
                snippet=snippet[:240],
            ))
            i += 2
            column += 2
            continue

        i += 1
        column += 1

    return issues


def scan_repository_source_text(root: str | Path) -> dict[str, object]:
    root_path = Path(root).resolve()
    issues: list[SourceTextIssue] = []
    files_scanned = 0

    for path in _iter_source_files(root_path):
        files_scanned += 1
        relative = path.relative_to(root_path).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            issues.append(SourceTextIssue(
                path=relative,
                line=1,
                column=1,
                kind="SOURCE_FILE_NOT_UTF8",
                snippet=str(exc)[:240],
            ))
            continue
        issues.extend(find_literal_escaped_newline_issues(relative, text))

    return {
        "schema": SCHEMA,
        "status": "ACCEPTED" if not issues else "REJECTED",
        "ok": not issues,
        "files_scanned": files_scanned,
        "issue_count": len(issues),
        "issues": [asdict(issue) for issue in issues],
    }


def assert_source_text_integrity(root: str | Path) -> dict[str, object]:
    report = scan_repository_source_text(root)
    if not report["ok"]:
        raise SourceTextIntegrityError(json.dumps(report, sort_keys=True))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Reject literal escaped-newline injection in HHS source text."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root to scan.")
    args = parser.parse_args(argv)
    report = scan_repository_source_text(args.repo_root)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
