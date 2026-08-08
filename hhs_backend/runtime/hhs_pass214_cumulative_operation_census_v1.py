"""Pass 214 additive cumulative operation/capability census.

Repository-wide static accounting for callable definitions and declarative
operation surfaces. This module is evidence-only: it never executes or promotes
runtime authority, and it never collapses same-named operations without proven
repository mappings.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Any, Iterable, Mapping, Sequence

SCHEMA = "HHS_PASS_214_CUMULATIVE_OPERATION_CAPABILITY_CENSUS_V1"
CLASSIFICATION = "HHS_PASS_214_REPOSITORY_WIDE_REUSABLE_OPERATION_ACCOUNTING"
FROZEN_RUNTIME = "hhs_runtime/HARMONICODE_VM_RUNTIME.c"
FROZEN_RUNTIME_GIT_BLOB = "362cd6e892ae66024333b111aec83f12023fdce3"
MAX_DEFAULT_BYTES = 4 * 1024 * 1024

SOURCE_EXTENSIONS = {
    ".py", ".pyi", ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".inc",
    ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".rs", ".go", ".java",
    ".kt", ".kts", ".swift", ".sh", ".bash", ".zsh", ".ps1", ".sql",
}
STRUCTURED_EXTENSIONS = {".json", ".jsonl", ".yaml", ".yml", ".toml"}
REFERENCE_EXTENSIONS = SOURCE_EXTENSIONS | STRUCTURED_EXTENSIONS | {".md", ".rst", ".adoc"}
SKIP_PARTS = {
    ".git", "node_modules", "vendor", "third_party", "site-packages", "venv",
    ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", "dist", "build",
    "coverage", "media", "screenshots",
}
REFERENCE_ONLY_PARTS = {
    "test", "tests", "evidence", "fixtures", "benchmark", "benchmarks",
    "receipts", "reports",
}
DECLARATIVE_KEYS = {
    "operation", "operation_id", "operation_name", "opcode", "opcode_id",
    "native_opcode", "native_dispatch_id", "mnemonic", "action", "action_id",
    "command", "command_id", "verb", "service", "service_id", "capability",
    "capability_id", "tool", "tool_id", "transition", "transition_id",
}
DECLARATIVE_CONTAINER_KEYS = {
    "operations", "opcodes", "actions", "commands", "verbs", "services",
    "capabilities", "tools", "transitions",
}
REGISTRY_NAME_RE = re.compile(
    r"(?:OP|OPCODE|INSTRUCTION|DISPATCH|REGISTRY|COMMAND|ACTION|SERVICE|"
    r"CAPABILIT|TRANSITION|BYTECODE|PRIMITIVE)", re.I,
)
IDENT_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]{2,}\b")
C_FUNC_RE = re.compile(
    r"(?m)^(?P<prefix>\s*(?:static\s+)?(?:inline\s+)?"
    r"(?:[A-Za-z_][\w\s\*\(\),:<>\[\]]*?\s+))"
    r"(?P<name>[A-Za-z_]\w*)\s*\((?P<args>[^;{}]*)\)\s*\{"
)
C_ENUM_RE = re.compile(
    r"(?ms)\b(?:typedef\s+)?enum(?:\s+(?P<tag>[A-Za-z_]\w*))?\s*\{"
    r"(?P<body>.*?)\}\s*(?P<typedef>[A-Za-z_]\w*)?\s*;"
)
C_DEFINE_OP_RE = re.compile(
    r"(?m)^\s*#\s*define\s+(?P<name>[A-Za-z_]\w*(?:OP|OPCODE|CMD|ACTION)"
    r"[A-Za-z0-9_]*)\b"
)
JS_FUNC_RE = re.compile(
    r"(?m)^\s*(?:export\s+)?(?:async\s+)?function\s+"
    r"(?P<name>[A-Za-z_$][\w$]*)\s*\("
)
JS_ARROW_RE = re.compile(
    r"(?m)^\s*(?:export\s+)?(?:const|let|var)\s+"
    r"(?P<name>[A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?"
    r"(?:\([^;\n]*\)|[A-Za-z_$][\w$]*)\s*=>"
)
JS_ROUTE_RE = re.compile(
    r"\.(?P<verb>get|post|put|patch|delete|options|head)\s*\(\s*"
    r"(?P<q>['\"`])(?P<route>[^'\"`]+)(?P=q)", re.I,
)
SHELL_FUNC_RE = re.compile(
    r"(?m)^\s*(?:function\s+)?(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
    r"\s*(?:\(\))?\s*\{"
)
SQL_RE = re.compile(
    r"(?im)^\s*create\s+(?:or\s+replace\s+)?"
    r"(?P<kind>table|view|index|trigger|function|procedure)\s+"
    r"(?:if\s+not\s+exists\s+)?[\"`\[]?(?P<name>[A-Za-z_][\w.]*)"
)
PASS_RE = re.compile(r"(?:^|[^a-z0-9])(?:pass|p)[-_ ]*0*(\d{1,3})(?:[^0-9]|$)", re.I)
PASS079_REGISTRY = "PASS_079_NATIVE_OPCODE_REGISTRY.json"
PASS213_DISPATCH = "hhs_backend/runtime/hhs_pass213_native_dispatch_common_v1.py"
BASE20_HEADER = "native_projects/hhs_vm81_game_level10/include/hhs_vm81_game.h"


class OperationCensusError(RuntimeError):
    pass


def _git(root: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), *args], stderr=subprocess.PIPE, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise OperationCensusError(f"PASS214_OPERATION_CENSUS_GIT_FAILED:{' '.join(args)}") from exc


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _tracked_paths(root: Path) -> list[str]:
    raw = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"])
    return sorted(
        (x.decode("utf-8", "surrogateescape") for x in raw.split(b"\0") if x),
        key=lambda x: x.encode("utf-8", "surrogateescape"),
    )


def _eligible(path: str) -> bool:
    p = PurePosixPath(path)
    return not (set(p.parts) & SKIP_PARTS) and p.suffix.lower() in REFERENCE_EXTENSIONS


def _definition_eligible(path: str) -> bool:
    p = PurePosixPath(path)
    return not (set(p.parts) & REFERENCE_ONLY_PARTS) and p.suffix.lower() in (SOURCE_EXTENSIONS | STRUCTURED_EXTENSIONS)


def _read(root: Path, path: str, limit: int) -> str | None:
    full = root / path
    try:
        if not full.is_file() or full.stat().st_size > limit:
            return None
        data = full.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:4096]:
        return None
    return data.decode("utf-8", "replace")


def _line(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _component(path: str) -> str:
    parts = PurePosixPath(path).parts
    if not parts:
        return "ROOT"
    if parts[0] in {"native_projects", "applications"} and len(parts) > 1:
        return f"{parts[0]}/{parts[1]}"
    if parts[0] == "hhs_backend" and len(parts) > 1:
        return "/".join(parts[:2])
    return parts[0]


def _origin(path: str) -> dict[str, Any]:
    nums = [int(x) for x in PASS_RE.findall(path)]
    n = max(nums) if nums else None
    return {"origin_kind": "NUMBERED_PASS" if n is not None else "PRE_PASS_OR_UNNUMBERED_FOUNDATION", "pass_number": n}


def _authority(path: str) -> str:
    if path.startswith("hhs_runtime/"):
        return "SHARED_RUNTIME"
    if path.startswith("hhs_backend/runtime/"):
        return "BACKEND_RUNTIME"
    if path.startswith("hhs_python/"):
        return "PYTHON_ABI_ORCHESTRATION"
    if path.startswith("native_projects/"):
        return "NATIVE_PROJECT"
    if path.startswith("applications/"):
        return "APPLICATION"
    if path.startswith(("deploy/", "deployment/")):
        return "DEPLOYMENT"
    if path.startswith(("tools/", "scripts/")):
        return "TOOLING"
    return "REPOSITORY_MODULE"


def _normalize(name: str) -> str:
    value = name.strip().replace("::", "_").replace(".", "_").replace("-", "_")
    value = re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_").upper()
    for prefix in ("HHS158_OP_", "HHS_VM81_REG_", "HHS_GAME_OP_", "HHS_NATIVE_U64_", "NATIVE_", "IR_", "OP_", "HHS_"):
        if value.startswith(prefix) and len(value) > len(prefix):
            value = value[len(prefix):]
            break
    if value.endswith("_V1"):
        value = value[:-3]
    return value or name.upper()


def _record(path: str, line: int, kind: str, name: str, **extra: Any) -> dict[str, Any]:
    key = sha256(f"{path}\0{line}\0{kind}\0{name}".encode()).hexdigest()
    item = {
        "operation_key": key,
        "path": path,
        "line": int(line),
        "kind": kind,
        "raw_name": name,
        "normalized_semantic_name": _normalize(name),
        "component": _component(path),
        "authority": _authority(path),
        **_origin(path),
    }
    item.update(extra)
    return item


def _expr_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _expr_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    if isinstance(node, ast.Call):
        return _expr_name(node.func)
    return ""


def _strings(node: ast.AST) -> Iterable[tuple[str, int]]:
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            yield child.value, int(getattr(child, "lineno", 0) or 0)


class _PyVisitor(ast.NodeVisitor):
    def __init__(self, path: str) -> None:
        self.path = path
        self.stack: list[str] = []
        self.items: list[dict[str, Any]] = []

    def add(self, node: ast.AST, kind: str, name: str, **extra: Any) -> None:
        self.items.append(_record(self.path, int(getattr(node, "lineno", 0) or 0), kind, name, **extra))

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        bases = {_expr_name(x).split(".")[-1] for x in node.bases}
        if bases & {"Enum", "IntEnum", "StrEnum", "Flag", "IntFlag"}:
            for child in node.body:
                if isinstance(child, ast.Assign):
                    for target in child.targets:
                        if isinstance(target, ast.Name) and not target.id.startswith("_"):
                            literal = child.value.value if isinstance(child.value, ast.Constant) else None
                            kind = "PYTHON_ENUM_OPCODE" if REGISTRY_NAME_RE.search(node.name) else "PYTHON_ENUM_MEMBER"
                            self.add(child, kind, target.id, enum=node.name, codepoint=literal)
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        qname = ".".join((*self.stack, node.name)) if self.stack else node.name
        kind = "PYTHON_METHOD" if self.stack else "PYTHON_FUNCTION"
        decorators = [_expr_name(x) for x in node.decorator_list]
        self.add(node, kind, qname, public=not node.name.startswith("_"), decorators=decorators)
        for deco in node.decorator_list:
            dname = _expr_name(deco).lower()
            if any(x in dname for x in ("route", ".get", ".post", ".put", ".patch", ".delete")):
                for value, line in _strings(deco):
                    if value.startswith("/"):
                        self.items.append(_record(self.path, line, "HTTP_ROUTE", f"{dname}:{value}"))
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name) and REGISTRY_NAME_RE.search(target.id):
                for value, line in _strings(node.value):
                    if 1 <= len(value) <= 160:
                        self.items.append(_record(self.path, line or node.lineno, "PYTHON_REGISTRY_ENTRY", value, registry=target.id))
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        call = _expr_name(node.func)
        lower = call.lower()
        if lower.endswith("add_parser") and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
            self.add(node, "CLI_COMMAND", node.args[0].value, registrar=call)
        if any(lower.endswith(x) for x in ("register", "register_operation", "register_service", "add_command")):
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                self.add(node, "PYTHON_REGISTERED_OPERATION", node.args[0].value, registrar=call)
        self.generic_visit(node)


def _python(path: str, text: str) -> tuple[list[dict[str, Any]], str | None]:
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError) as exc:
        return [], f"PYTHON_PARSE_ERROR:{getattr(exc, 'lineno', 0) or 0}"
    visitor = _PyVisitor(path)
    visitor.visit(tree)
    return visitor.items, None


def _enum_members(body: str) -> list[tuple[str, str | None]]:
    clean = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    clean = re.sub(r"//.*", "", clean)
    out: list[tuple[str, str | None]] = []
    for part in clean.split(","):
        match = re.match(r"\s*([A-Za-z_]\w*)\s*(?:=\s*([^,\n]+))?", part)
        if match:
            out.append((match.group(1), match.group(2).strip() if match.group(2) else None))
    return out


def _c(path: str, text: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for match in C_FUNC_RE.finditer(text):
        name = match.group("name")
        if name in {"if", "for", "while", "switch"}:
            continue
        prefix = " ".join(match.group("prefix").split())
        out.append(_record(path, _line(text, match.start()), "C_FUNCTION", name, public=not prefix.startswith("static "), linkage="INTERNAL_STATIC" if prefix.startswith("static ") else "EXTERNAL_LINKAGE"))
    for match in C_ENUM_RE.finditer(text):
        enum_name = match.group("tag") or match.group("typedef") or "anonymous_enum"
        opcodeish = bool(REGISTRY_NAME_RE.search(enum_name))
        for name, value in _enum_members(match.group("body")):
            if name.endswith("__COUNT") or name.endswith("_COUNT"):
                continue
            if opcodeish or re.search(r"(?:^|_)(?:OP|OPCODE|CMD|ACTION)(?:_|$)", name):
                out.append(_record(path, _line(text, match.start()), "C_ENUM_OPCODE", name, enum=enum_name, codepoint=value))
    for match in C_DEFINE_OP_RE.finditer(text):
        out.append(_record(path, _line(text, match.start()), "C_MACRO_OPERATION", match.group("name")))
    return out


def _javascript(path: str, text: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for pattern, kind in ((JS_FUNC_RE, "JS_FUNCTION"), (JS_ARROW_RE, "JS_ARROW_FUNCTION")):
        for match in pattern.finditer(text):
            out.append(_record(path, _line(text, match.start()), kind, match.group("name")))
    for match in JS_ROUTE_RE.finditer(text):
        out.append(_record(path, _line(text, match.start()), "HTTP_ROUTE", f"{match.group('verb').upper()}:{match.group('route')}"))
    return out


def _structured_walk(value: Any, tokens: Sequence[str] = ()) -> Iterable[tuple[str, str, str]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            skey = str(key)
            lower = skey.lower()
            if lower in DECLARATIVE_KEYS and isinstance(child, (str, int)):
                yield lower, str(child), ".".join((*tokens, skey))
            if lower in DECLARATIVE_CONTAINER_KEYS:
                if isinstance(child, Mapping):
                    for item_key in child:
                        yield lower, str(item_key), ".".join((*tokens, skey, str(item_key)))
                elif isinstance(child, list):
                    for i, entry in enumerate(child):
                        if isinstance(entry, (str, int)):
                            yield lower, str(entry), ".".join((*tokens, skey, str(i)))
            yield from _structured_walk(child, (*tokens, skey))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from _structured_walk(child, (*tokens, str(i)))


def _structured(path: str, text: str) -> list[dict[str, Any]]:
    suffix = PurePosixPath(path).suffix.lower()
    if suffix not in {".json", ".jsonl"}:
        return []
    try:
        values = [json.loads(text)] if suffix == ".json" else [json.loads(x) for x in text.splitlines() if x.strip()]
    except (json.JSONDecodeError, ValueError):
        return []
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for value in values:
        for key, name, location in _structured_walk(value):
            token = (key, name, location)
            if token not in seen and name and len(name) <= 256:
                seen.add(token)
                out.append(_record(path, 0, "DECLARATIVE_OPERATION", name, declarative_key=key, json_path=location))
    return out


def _pass079(root: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads((root / PASS079_REGISTRY).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [
        _record(PASS079_REGISTRY, 0, "PASS079_NATIVE_ABI_OPCODE", str(entry.get("native_opcode") or entry.get("abi_symbol")), abi_symbol=entry.get("abi_symbol"), semantic_operation_identity=entry.get("semantic_operation_identity"), callable=entry.get("callable"))
        for entry in data.get("entries", []) if entry.get("native_opcode") or entry.get("abi_symbol")
    ]


def _pass213(path: str, text: str) -> list[dict[str, Any]]:
    if path != PASS213_DISPATCH:
        return []
    match = re.search(r"_NATIVE_DISPATCH_IDS\s*=\s*\{(?P<body>.*?)\n\}", text, re.S)
    if not match:
        return []
    return [_record(path, _line(text, match.start()), "PASS213_GOVERNED_NATIVE_DISPATCH", name, codepoint=int(code)) for name, code in re.findall(r'[\"\']([^\"\']+)[\"\']\s*:\s*(\d+)', match.group("body"))]


def _base20(root: Path) -> list[dict[str, Any]]:
    text = _read(root, BASE20_HEADER, MAX_DEFAULT_BYTES) or ""
    match = re.search(r"typedef\s+enum\s+HHSVM81GameOpcodeDigit\s*\{(?P<body>.*?)\}\s*HHSVM81GameOpcodeDigit", text, re.S)
    if not match:
        return []
    out = []
    for name, value in _enum_members(match.group("body")):
        if name.startswith("HHS_GAME_OP_"):
            semantic = name.removeprefix("HHS_GAME_OP_")
            try:
                digit = int(value or "")
            except ValueError:
                digit = None
            out.append(_record(BASE20_HEADER, _line(text, match.start()), "VM81_BASE20_NUMERICAL_OPCODE", name, codepoint=digit, exact_projection=f"VM81_SUBSTRATE:{semantic}", semantic_equivalence="EXACT_PROJECTION_BY_NATIVE_REGISTRY"))
    return out


def _ctypes(path: str, text: str) -> set[str]:
    if PurePosixPath(path).suffix.lower() != ".py":
        return set()
    return set(re.findall(r"\.\s*(hhs_[A-Za-z0-9_]+)\s*\.\s*argtypes\s*=", text))


def _family(item: Mapping[str, Any]) -> str:
    if item["kind"] == "VM81_BASE20_NUMERICAL_OPCODE":
        return "VM81_BASE20_NUMERICAL_ABI"
    if item["path"] == FROZEN_RUNTIME and item["kind"] == "C_ENUM_OPCODE":
        if item.get("enum") == "Opcode":
            return "VM81_SUBSTRATE_OPCODE"
        if item.get("enum") == "HHS_IROp":
            return "FROZEN_HHS_IR_OPCODE"
    if str(item["path"]).endswith("hhs_pass158_opcodes.h") and item.get("enum") == "HHS158PublicOpcode":
        return "PASS158_LLABI_NFTC_OPCODE"
    if item["kind"] == "PASS079_NATIVE_ABI_OPCODE":
        return "PASS079_NATIVE_ABI_OPCODE"
    if item["kind"] == "PASS213_GOVERNED_NATIVE_DISPATCH":
        return "PASS213_GOVERNED_NATIVE_DISPATCH"
    if item["kind"] in {"C_ENUM_OPCODE", "PYTHON_ENUM_OPCODE", "C_MACRO_OPERATION"}:
        return "OTHER_OPCODE_OR_BYTECODE"
    if item["kind"] == "DECLARATIVE_OPERATION":
        return "DECLARATIVE_CAPABILITY_REGISTRY"
    if item["kind"] == "HTTP_ROUTE":
        return "HTTP_API"
    if item["kind"] == "CLI_COMMAND":
        return "CLI"
    return "CALLABLE_OPERATION"


def _reuse(item: Mapping[str, Any], cross_refs: int) -> str:
    name = str(item["raw_name"]).split(".")[-1]
    path = str(item["path"])
    if name.startswith("_") or item.get("linkage") == "INTERNAL_STATIC":
        return "INTERNAL_PRIMITIVE"
    if path.startswith(("hhs_runtime/", "hhs_backend/", "hhs_python/")):
        return "SHARED_MODULE"
    if any(x in path.lower() for x in ("bridge", "wrapper", "adapter", "/api/", "_cli")):
        return "WRAPPER_OR_ADAPTER"
    if path.startswith(("applications/", "native_projects/")):
        return "REUSED_ACROSS_COMPONENTS" if cross_refs else "ISOLATED_IMPLEMENTATION_CANDIDATE"
    if path.startswith(("tools/", "scripts/", "deploy/", "deployment/")):
        return "TOOLING_OR_OPERATIONS"
    if item["kind"] == "DECLARATIVE_OPERATION":
        return "DECLARATIVE_REGISTRY"
    return "REPOSITORY_MODULE"


def _python_exposure(item: Mapping[str, Any], ctypes_symbols: set[str], governed: set[str]) -> str:
    name = str(item["raw_name"])
    path = str(item["path"])
    if item["kind"] == "PASS213_GOVERNED_NATIVE_DISPATCH":
        return "GOVERNED_NATIVE_DISPATCH"
    if name in ctypes_symbols:
        return "CTYPES_DIRECT_ABI"
    if str(item["normalized_semantic_name"]) in governed:
        return "GOVERNED_SEMANTIC_PROJECTION"
    if path.startswith("hhs_python/") or "/bindings/python/" in path:
        return "PYTHON_SURFACE"
    if path.endswith(".py") and str(item["kind"]).startswith("PYTHON_"):
        return "PYTHON_IMPLEMENTATION"
    if item.get("linkage") == "INTERNAL_STATIC":
        return "INTENTIONALLY_INTERNAL_OR_UNEXPOSED"
    return "NOT_DEMONSTRATED"


def _anchor_report(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    counts = Counter(str(x["family"]) for x in records)
    expected = {
        "VM81_SUBSTRATE_OPCODE": 24,
        "FROZEN_HHS_IR_OPCODE": 20,
        "PASS079_NATIVE_ABI_OPCODE": 29,
        "PASS158_LLABI_NFTC_OPCODE": 36,
        "PASS213_GOVERNED_NATIVE_DISPATCH": 9,
        "VM81_BASE20_NUMERICAL_ABI": 19,
    }
    checks = {key: counts[key] == value for key, value in expected.items()}
    return {"expected": expected, "observed": {key: counts[key] for key in expected}, "checks": checks, "all_satisfied": all(checks.values()), "raw_known_opcode_identity_minimum": sum(counts[key] for key in expected)}


def build_cumulative_operation_census(repository_root: Path, *, source_ref: str = "HEAD", max_source_bytes: int = MAX_DEFAULT_BYTES) -> dict[str, Any]:
    root = repository_root.resolve()
    source_commit = _git(root, "rev-parse", source_ref)
    source_tree = _git(root, "rev-parse", f"{source_ref}^{{tree}}")
    frozen_blob = _git(root, "rev-parse", f"{source_ref}:{FROZEN_RUNTIME}")
    if frozen_blob != FROZEN_RUNTIME_GIT_BLOB:
        raise OperationCensusError(f"FROZEN_RUNTIME_BLOB_MISMATCH:{frozen_blob}")

    paths = [p for p in _tracked_paths(root) if _eligible(p)]
    texts: dict[str, str] = {}
    records: list[dict[str, Any]] = []
    parse_errors: list[dict[str, str]] = []
    skipped: list[str] = []
    ctypes_symbols: set[str] = set()

    for path in paths:
        text = _read(root, path, max_source_bytes)
        if text is None:
            skipped.append(path)
            continue
        texts[path] = text
        ctypes_symbols.update(_ctypes(path, text))
        if not _definition_eligible(path):
            continue
        suffix = PurePosixPath(path).suffix.lower()
        if suffix in {".py", ".pyi"}:
            items, error = _python(path, text)
            records.extend(items)
            records.extend(_pass213(path, text))
            if error:
                parse_errors.append({"path": path, "error": error})
        elif suffix in {".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".inc"}:
            records.extend(_c(path, text))
        elif suffix in {".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx"}:
            records.extend(_javascript(path, text))
        elif suffix in {".sh", ".bash", ".zsh", ".ps1"}:
            records.extend([_record(path, _line(text, m.start()), "SHELL_FUNCTION", m.group("name")) for m in SHELL_FUNC_RE.finditer(text)])
        elif suffix == ".sql":
            records.extend([_record(path, _line(text, m.start()), f"SQL_{m.group('kind').upper()}", m.group("name")) for m in SQL_RE.finditer(text)])
        elif suffix in STRUCTURED_EXTENSIONS:
            records.extend(_structured(path, text))

    records.extend(_pass079(root))
    records = [x for x in records if not (x["path"] == BASE20_HEADER and x["kind"] == "C_ENUM_OPCODE" and x.get("enum") == "HHSVM81GameOpcodeDigit")]
    records.extend(_base20(root))

    unique: dict[str, dict[str, Any]] = {}
    for item in records:
        item["family"] = _family(item)
        unique[item["operation_key"]] = item
    records = list(unique.values())

    token_files: dict[str, set[str]] = defaultdict(set)
    for path, text in texts.items():
        for token in IDENT_RE.findall(text):
            token_files[token.upper()].add(path)
    governed = {str(x["normalized_semantic_name"]) for x in records if x["kind"] == "PASS213_GOVERNED_NATIVE_DISPATCH"}
    components_by_name: dict[str, set[str]] = defaultdict(set)
    for item in records:
        components_by_name[str(item["normalized_semantic_name"])].add(str(item["component"]))

    for item in records:
        leaf = str(item["raw_name"]).split(".")[-1]
        refs = token_files.get(leaf.upper(), set()) if IDENT_RE.fullmatch(leaf) else set()
        cross = sorted(p for p in refs if _component(p) != item["component"])
        item["reference_file_count"] = len(refs)
        item["cross_component_reference_count"] = len(cross)
        item["cross_component_reference_examples"] = cross[:12]
        item["reuse_status"] = _reuse(item, len(cross))
        item["python_exposure"] = _python_exposure(item, ctypes_symbols, governed)
        peers = components_by_name[str(item["normalized_semantic_name"])]
        item["semantic_name_component_count"] = len(peers)
        if "semantic_equivalence" not in item:
            item["semantic_equivalence"] = "UNRESOLVED_NAME_NORMALIZED_CANDIDATE" if len(peers) > 1 else "DISTINCT_OR_UNRESOLVED"

    records.sort(key=lambda x: (str(x["family"]), str(x["normalized_semantic_name"]), str(x["path"]), int(x["line"]), str(x["raw_name"])))
    families = Counter(str(x["family"]) for x in records)
    kinds = Counter(str(x["kind"]) for x in records)
    reuse = Counter(str(x["reuse_status"]) for x in records)
    python = Counter(str(x["python_exposure"]) for x in records)
    authorities = Counter(str(x["authority"]) for x in records)
    origins = Counter("PRE_PASS_OR_UNNUMBERED" if x["pass_number"] is None else f"PASS_{int(x['pass_number']):03d}" for x in records)
    groups: dict[str, list[str]] = defaultdict(list)
    for item in records:
        groups[str(item["normalized_semantic_name"])].append(str(item["operation_key"]))
    multi = {k: v for k, v in groups.items() if len(v) > 1}
    isolated = [x for x in records if x["reuse_status"] == "ISOLATED_IMPLEMENTATION_CANDIDATE"]
    anchors = _anchor_report(records)
    if not anchors["all_satisfied"]:
        raise OperationCensusError("KNOWN_OPCODE_FAMILY_ANCHOR_FAILURE:" + _canonical(anchors))

    summary = {
        "source_commit": source_commit,
        "source_tree": source_tree,
        "frozen_runtime": {"path": FROZEN_RUNTIME, "git_blob": frozen_blob, "expected_git_blob": FROZEN_RUNTIME_GIT_BLOB, "preserved": True},
        "coverage": {"tracked_reference_files_considered": len(paths), "readable_reference_files": len(texts), "skipped_large_or_binary_files": len(skipped), "raw_operation_identities": len(records), "components_with_operations": len({x["component"] for x in records}), "pre_pass_or_unnumbered_operations": origins["PRE_PASS_OR_UNNUMBERED"], "numbered_pass_operations": len(records) - origins["PRE_PASS_OR_UNNUMBERED"]},
        "family_counts": dict(sorted(families.items())),
        "kind_counts": dict(sorted(kinds.items())),
        "reuse_counts": dict(sorted(reuse.items())),
        "python_exposure_counts": dict(sorted(python.items())),
        "authority_counts": dict(sorted(authorities.items())),
        "origin_counts": dict(sorted(origins.items())),
        "known_opcode_family_anchors": anchors,
        "semantic_accounting": {"normalized_semantic_name_groups": len(groups), "multi_identity_name_normalized_candidates": len(multi), "proven_exact_projection_records": sum(1 for x in records if x["semantic_equivalence"] == "EXACT_PROJECTION_BY_NATIVE_REGISTRY"), "automatic_semantic_collapse_performed": False},
        "reuse_accounting": {"isolated_implementation_candidates": len(isolated), "reused_across_components": reuse["REUSED_ACROSS_COMPONENTS"], "shared_module_records": reuse["SHARED_MODULE"], "internal_primitives": reuse["INTERNAL_PRIMITIVE"]},
        "ctypes_bound_native_symbols": sorted(ctypes_symbols),
        "parse_error_count": len(parse_errors),
    }
    result = {
        "schema": SCHEMA,
        "classification": CLASSIFICATION,
        "policy": {"repository_wide_not_opcode_only": True, "pre_pass_and_numbered_passes_included": True, "tests_and_evidence_are_reference_only": True, "applications_and_native_projects_are_scanned_for_isolated_capabilities": True, "name_similarity_never_proves_semantic_equivalence": True, "automatic_authority_promotion": False, "runtime_mutation_performed": False, "frozen_runtime_modified": False},
        "summary": summary,
        "parse_errors": parse_errors,
        "skipped_large_or_binary_files": skipped,
        "semantic_name_candidates": [{"normalized_name": k, "operation_keys": v} for k, v in sorted(multi.items())],
        "isolated_implementation_candidates": [{"operation_key": x["operation_key"], "raw_name": x["raw_name"], "kind": x["kind"], "path": x["path"], "component": x["component"], "family": x["family"], "python_exposure": x["python_exposure"]} for x in isolated],
        "operations": records,
    }
    result["census_sha256"] = _digest(result)
    return result


def write_census(result: Mapping[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_and_validate_census(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    supplied = data.pop("census_sha256", None)
    if supplied != _digest(data):
        raise OperationCensusError("CENSUS_SHA256_VALIDATION_FAILURE")
    data["census_sha256"] = supplied
    if data.get("schema") != SCHEMA:
        raise OperationCensusError("CENSUS_SCHEMA_MISMATCH")
    if not data["summary"]["known_opcode_family_anchors"]["all_satisfied"]:
        raise OperationCensusError("CENSUS_KNOWN_FAMILY_ANCHORS_FAILED")
    return data
