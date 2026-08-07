"""Supplemental language/declaration extractors for the Pass 214 deep census.

These extractors cover callable/declarative surfaces that the base census does
not parse structurally. Records remain evidence-only and do not imply semantic
equivalence or execution authority.
"""
from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tomllib
from typing import Any, Iterable, Mapping

from hhs_backend.runtime.hhs_pass214_cumulative_operation_census_v1 import (
    MAX_DEFAULT_BYTES,
    _line,
    _read,
    _record,
)

C_DECL_RE = re.compile(
    r"(?m)^\s*(?:extern\s+)?(?:[A-Za-z_][\w\s\*,:<>\[\]]*?\s+)"
    r"(?P<name>[A-Za-z_]\w*)\s*\((?P<args>[^;{}]*)\)\s*;"
)
RUST_FN_RE = re.compile(r"(?m)^\s*(?P<public>pub(?:\([^)]*\))?\s+)?(?:async\s+)?(?:unsafe\s+)?fn\s+(?P<name>[A-Za-z_]\w*)\s*(?:<[^\n{>]*>)?\s*\(")
JAVA_METHOD_RE = re.compile(
    r"(?m)^\s*(?:(?:public|protected|private|static|final|synchronized|native|abstract|default|strictfp)\s+)*"
    r"(?:<[^>{};]+>\s+)?[A-Za-z_$][\w$<>,.?\[\]\s]*\s+(?P<name>[A-Za-z_$][\w$]*)\s*\([^;{}]*\)\s*(?:throws\s+[^\{]+)?\{"
)
KOTLIN_FN_RE = re.compile(r"(?m)^\s*(?:(?:public|private|protected|internal|open|override|suspend|inline|tailrec|operator|infix|external)\s+)*fun\s+(?:<[^>]+>\s*)?(?P<name>[A-Za-z_]\w*)\s*\(")
SWIFT_FN_RE = re.compile(r"(?m)^\s*(?:(?:public|private|fileprivate|internal|open|static|class|mutating|nonmutating|override)\s+)*func\s+(?P<name>[A-Za-z_]\w*)\s*(?:<[^>]+>)?\s*\(")
LEAN_DEF_RE = re.compile(r"(?m)^\s*(?P<kind>def|abbrev|theorem|lemma|axiom)\s+(?P<name>[A-Za-z_][\w'.]*)")
COQ_DEF_RE = re.compile(r"(?im)^\s*(?P<kind>definition|fixpoint|cofixpoint|theorem|lemma|corollary|proposition|axiom)\s+(?P<name>[A-Za-z_][\w']*)")
ASM_LABEL_RE = re.compile(r"(?m)^\s*(?:\.global|\.globl)\s+(?P<name>[A-Za-z_.$][\w.$]*)\s*$")
MAKE_TARGET_RE = re.compile(r"(?m)^(?P<name>[A-Za-z0-9_.%+@/-]+)\s*:(?![=])[^\n]*$")
CMAKE_FN_RE = re.compile(r"(?im)^\s*(?P<kind>function|macro)\s*\(\s*(?P<name>[A-Za-z_]\w*)")
YAML_KEY_RE = re.compile(r"^(?P<indent>\s*)(?P<key>[A-Za-z_][\w-]*)\s*:\s*(?P<value>.*?)\s*$")
KNOWN_DECL_KEYS = {
    "operation", "operation_id", "operation_name", "opcode", "opcode_id",
    "native_opcode", "native_dispatch_id", "mnemonic", "action", "action_id",
    "command", "command_id", "verb", "service", "service_id", "capability",
    "capability_id", "tool", "tool_id", "transition", "transition_id",
}
KNOWN_CONTAINER_KEYS = {"operations", "opcodes", "actions", "commands", "verbs", "services", "capabilities", "tools", "transitions"}


def _tracked(root: Path) -> list[str]:
    raw = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"])
    return sorted(x.decode("utf-8", "surrogateescape") for x in raw.split(b"\0") if x)


def _records_for_regex(path: str, text: str, regex: re.Pattern[str], kind: str, *, extra=None) -> list[dict[str, Any]]:
    out = []
    for match in regex.finditer(text):
        name = match.group("name")
        if name in {"if", "for", "while", "switch", "catch", "return", "sizeof"}:
            continue
        fields = extra(match) if extra else {}
        out.append(_record(path, _line(text, match.start()), kind, name, **fields))
    return out


def _walk_structured(value: Any, tokens: tuple[str, ...] = ()) -> Iterable[tuple[str, str, str]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            skey = str(key)
            lower = skey.lower()
            if lower in KNOWN_DECL_KEYS and isinstance(child, (str, int)):
                yield lower, str(child), ".".join((*tokens, skey))
            if lower in KNOWN_CONTAINER_KEYS:
                if isinstance(child, Mapping):
                    for member in child:
                        yield lower, str(member), ".".join((*tokens, skey, str(member)))
                elif isinstance(child, list):
                    for index, entry in enumerate(child):
                        if isinstance(entry, (str, int)):
                            yield lower, str(entry), ".".join((*tokens, skey, str(index)))
            yield from _walk_structured(child, (*tokens, skey))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_structured(child, (*tokens, str(index)))


def _toml(path: str, text: str) -> list[dict[str, Any]]:
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return []
    out = []
    seen = set()
    for key, name, location in _walk_structured(data):
        token = (key, name, location)
        if token in seen or not name or len(name) > 256:
            continue
        seen.add(token)
        out.append(_record(path, 0, "TOML_DECLARATIVE_OPERATION", name, declarative_key=key, document_path=location))
    return out


def _yaml(path: str, text: str) -> list[dict[str, Any]]:
    """Conservative YAML registry extraction without adding a YAML dependency."""
    out = []
    stack: list[tuple[int, str]] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = YAML_KEY_RE.match(line)
        if not match:
            continue
        indent = len(match.group("indent").replace("\t", "    "))
        key = match.group("key")
        value = match.group("value").strip().strip("'\"")
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1].lower() if stack else ""
        lower = key.lower()
        if lower in KNOWN_DECL_KEYS and value and value not in {"|", ">", "[]", "{}"}:
            out.append(_record(path, lineno, "YAML_DECLARATIVE_OPERATION", value, declarative_key=lower))
        elif parent in KNOWN_CONTAINER_KEYS and not value:
            out.append(_record(path, lineno, "YAML_DECLARATIVE_OPERATION", key, declarative_key=parent))
        stack.append((indent, key))
    return out


def extract_supplemental_operations(repository_root: Path, *, max_source_bytes: int = MAX_DEFAULT_BYTES) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    root = repository_root.resolve()
    records: list[dict[str, Any]] = []
    ext_counts: dict[str, int] = {}
    covered_counts: dict[str, int] = {}
    extractors_used: set[str] = set()
    for path in _tracked(root):
        suffix = PurePosixPath(path).suffix.lower()
        name = PurePosixPath(path).name
        ext_key = suffix or name
        ext_counts[ext_key] = ext_counts.get(ext_key, 0) + 1
        text = _read(root, path, max_source_bytes)
        if text is None:
            continue
        added: list[dict[str, Any]] = []
        if suffix in {".h", ".hpp", ".hh", ".hxx", ".inc"}:
            added.extend(_records_for_regex(path, text, C_DECL_RE, "C_ABI_DECLARATION", extra=lambda m: {"declaration_only": True}))
            extractors_used.add("C_HEADER_DECLARATION")
        elif suffix == ".rs":
            added.extend(_records_for_regex(path, text, RUST_FN_RE, "RUST_FUNCTION", extra=lambda m: {"public": bool(m.group("public"))}))
            extractors_used.add("RUST")
        elif suffix == ".java":
            added.extend(_records_for_regex(path, text, JAVA_METHOD_RE, "JAVA_METHOD"))
            extractors_used.add("JAVA")
        elif suffix in {".kt", ".kts"}:
            added.extend(_records_for_regex(path, text, KOTLIN_FN_RE, "KOTLIN_FUNCTION"))
            extractors_used.add("KOTLIN")
        elif suffix == ".swift":
            added.extend(_records_for_regex(path, text, SWIFT_FN_RE, "SWIFT_FUNCTION"))
            extractors_used.add("SWIFT")
        elif suffix == ".lean":
            for match in LEAN_DEF_RE.finditer(text):
                added.append(_record(path, _line(text, match.start()), "LEAN_FORMAL_DECLARATION", match.group("name"), formal_kind=match.group("kind")))
            extractors_used.add("LEAN")
        elif suffix == ".v":
            for match in COQ_DEF_RE.finditer(text):
                added.append(_record(path, _line(text, match.start()), "ROCQ_FORMAL_DECLARATION", match.group("name"), formal_kind=match.group("kind").upper()))
            extractors_used.add("ROCQ")
        elif suffix in {".s", ".asm"}:
            added.extend(_records_for_regex(path, text, ASM_LABEL_RE, "ASSEMBLY_PUBLIC_SYMBOL"))
            extractors_used.add("ASSEMBLY")
        elif suffix == ".toml":
            added.extend(_toml(path, text))
            extractors_used.add("TOML")
        elif suffix in {".yaml", ".yml"}:
            added.extend(_yaml(path, text))
            extractors_used.add("YAML")
        elif name in {"Makefile", "makefile", "GNUmakefile"} or suffix == ".mk":
            for match in MAKE_TARGET_RE.finditer(text):
                target = match.group("name")
                if not target.startswith(".") and "$" not in target:
                    added.append(_record(path, _line(text, match.start()), "BUILD_TASK", target))
            extractors_used.add("MAKE")
        elif name == "CMakeLists.txt" or suffix == ".cmake":
            for match in CMAKE_FN_RE.finditer(text):
                added.append(_record(path, _line(text, match.start()), "CMAKE_CALLABLE", match.group("name"), cmake_kind=match.group("kind").upper()))
            extractors_used.add("CMAKE")
        if added:
            covered_counts[ext_key] = covered_counts.get(ext_key, 0) + 1
            records.extend(added)
    manifest = {
        "tracked_extension_or_special_file_counts": dict(sorted(ext_counts.items())),
        "supplemental_extractor_file_counts": dict(sorted(covered_counts.items())),
        "extractors_used": sorted(extractors_used),
        "supplemental_record_count": len(records),
        "semantics": "SUPPLEMENTAL_SURFACE_ACCOUNTING_ONLY_NO_AUTHORITY_PROMOTION",
    }
    return records, manifest
