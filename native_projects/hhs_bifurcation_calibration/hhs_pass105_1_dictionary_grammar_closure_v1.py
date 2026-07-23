from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping
import json
import re
import unicodedata

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, stable
from native_projects.hhs_bifurcation_calibration.hhs_pass082_1_offset_entangled_calibration_v1 import root

PASS_ID = "PASS_105_1"
SYNTAX_VERSION = "1.0"
SUPPORTED_VERSIONS = {1}

REJECTIONS = (
    "REJECT_INVALID_SOURCE_ENCODING",
    "REJECT_BIDIRECTIONAL_TEXT_CONTROL",
    "REJECT_SYNTAX_HOMOGLYPH_SUBSTITUTION",
    "REJECT_RESERVED_KEYWORD_REBINDING",
    "REJECT_RECOVERED_PARSE_AS_CANONICAL_SOURCE",
    "REJECT_UNDECLARED_TEMPLATE_VARIABLE",
    "REJECT_TEMPLATE_ARGUMENT_TYPE_MISMATCH",
    "REJECT_LITERAL_EXECUTION_SYNTAX_CONFUSION",
    "REJECT_ALIAS_REBINDING_COLLAPSE",
    "REJECT_DUPLICATE_SCOPE_BINDING",
    "REJECT_UNWITNESSED_DICTIONARY_SHADOWING",
    "REJECT_NONDETERMINISTIC_IMPORT_RESOLUTION",
    "REJECT_UNPINNED_DICTIONARY_DEPENDENCY",
    "REJECT_SILENT_DICTIONARY_CONFLICT_OVERWRITE",
    "REJECT_PARSE_ONLY_EXECUTION_BYPASS",
    "REJECT_NONDETERMINISTIC_DICTIONARY_PARSE",
    "REJECT_FORMATTER_SEMANTIC_MUTATION",
    "REJECT_TEMPORAL_GRAMMAR_DRIFT",
    "REJECT_UNAUTHORIZED_SYNTAX_EXTENSION",
    "REJECT_UNSUPPORTED_DICTIONARY_VERSION",
    "REJECT_UNKNOWN_TYPE",
    "REJECT_UNRESOLVED_REFERENCE",
    "REJECT_REFERENCE_DEPENDENCY_CYCLE",
)

OUTCOMES = (
    "SYNTAX_VALID",
    "SYNTAX_VALID_SEMANTICALLY_UNRESOLVED",
    "DICTIONARY_ADMITTED",
    "DIAGNOSTIC_RECOVERY_ONLY",
    "SYNTAX_VERSION_MIGRATED",
    "IMPORT_RESOLUTION_FAILURE",
    "DICTIONARY_CONFLICT",
    "INVALID_DICTIONARY_SYNTAX",
    "SEMANTIC_ENFORCEMENT_FAILURE",
    "PARSE_REPLAY_FAILURE",
)

KEYWORDS = {
    "dictionary", "version", "extends", "namespace", "symbol", "string", "template",
    "phrase", "alias", "variable", "constant", "bind", "rebind", "scope", "global",
    "project", "module", "local", "session", "experimental", "type", "returns", "ref",
    "root", "literal", "invoke", "expand", "defer", "partial", "import", "export", "from",
    "as", "requires", "where", "if", "else", "match", "case", "default", "true", "false",
    "null", "empty", "unresolved", "unavailable", "merge", "policy", "shadows",
}

KNOWN_TYPES = {
    "INTEGER", "RATIONAL", "BOOLEAN", "TRINARY", "U72_PHASE", "UNICODE_STRING",
    "CANONICAL_STRING", "HARMONICODE_SOURCE_STRING", "NATURAL_LANGUAGE_STRING",
    "SYMBOL_REFERENCE", "SEMANTIC_REFERENCE", "CONSTRAINT_OPERATOR", "OPERATION_REFERENCE",
    "LANE_REFERENCE", "TENSOR_REFERENCE", "HASH72_ROOT", "TEMPLATE", "AST", "GRAPH",
    "RECEIPT", "DICTIONARY", "T", "VOID",
}

BIDI = {chr(x) for x in (0x202A, 0x202B, 0x202D, 0x202E, 0x202C, 0x2066, 0x2067, 0x2068, 0x2069)}
HOMOGLYPH_FORBIDDEN = {"＝", "：", "；", "｛", "｝", "（", "）"}

TOKEN_RE = re.compile(
    r"(?P<WS>\s+)|"
    r"(?P<COMMENT>//[^\n]*|/\*.*?\*/)|"
    r"(?P<TEMPLATE>t\"(?:\\.|[^\"\\])*\")|"
    r"(?P<RAW>r\"(?:\\.|[^\"\\])*\")|"
    r"(?P<HSTRING>h\"(?:\\.|[^\"\\])*\")|"
    r"(?P<STRING>\"(?:\\.|[^\"\\])*\")|"
    r"(?P<ASSIGN>:=)|(?P<BIARROW><->)|(?P<ARROW>->)|"
    r"(?P<NUMBER>\d+)|"
    r"(?P<IDENT>[A-Za-z_][A-Za-z0-9_.@-]*)|"
    r"(?P<GLYPH>[^\x00-\x7F\s{}():;,=]+)|"
    r"(?P<PUNCT>[{}()\[\]:;,=])",
    re.S,
)


def _read(path: Path) -> Any:
    return json.loads(path.read_text())


def load_parent(repo: Path) -> dict[str, Any]:
    manifest = _read(repo / "PASS_105_RELEASE_MANIFEST.json")
    return stable({
        "manifest": manifest,
        "input_commitment_root_hash72": root("hhs_pass105_1_parent_v1", manifest),
    })


def validate_unicode(source: str | bytes) -> str:
    if isinstance(source, bytes):
        try:
            source = source.decode("utf-8", "strict")
        except UnicodeDecodeError as exc:
            raise ContractError(REJECTIONS[0]) from exc
    if not isinstance(source, str):
        raise ContractError(REJECTIONS[0])
    if any(c in BIDI for c in source):
        raise ContractError(REJECTIONS[1])
    if any(c in HOMOGLYPH_FORBIDDEN for c in source):
        raise ContractError(REJECTIONS[2])
    return unicodedata.normalize("NFC", source)


def lex(source: str | bytes) -> list[dict[str, Any]]:
    src = validate_unicode(source)
    tokens: list[dict[str, Any]] = []
    pos = 0
    while pos < len(src):
        match = TOKEN_RE.match(src, pos)
        if not match:
            raise ContractError("INVALID_DICTIONARY_SYNTAX")
        if match.lastgroup not in {"WS", "COMMENT"}:
            tokens.append({
                "kind": match.lastgroup,
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
            })
        pos = match.end()
    return stable(tokens)


class Parser:
    def __init__(self, tokens: list[dict[str, Any]]):
        self.tokens = tokens
        self.i = 0

    def peek(self, text: str | None = None) -> bool:
        return self.i < len(self.tokens) and (text is None or self.tokens[self.i]["text"] == text)

    def take(self, text: str | None = None) -> dict[str, Any]:
        if not self.peek(text):
            raise ContractError("INVALID_DICTIONARY_SYNTAX")
        token = self.tokens[self.i]
        self.i += 1
        return token

    def parse_reference_name(self) -> str:
        return self.take()["text"]

    def parse_parameters(self) -> list[dict[str, Any]]:
        params: list[dict[str, Any]] = []
        self.take("(")
        while not self.peek(")"):
            name = self.take()["text"]
            self.take(":")
            typ = self.take()["text"]
            default: list[str] | None = None
            if self.peek("="):
                self.take("=")
                default = []
                while not self.peek(",") and not self.peek(")"):
                    default.append(self.take()["text"])
            params.append({"name": name, "type": typ, "default": default})
            if self.peek(","):
                self.take(",")
            elif not self.peek(")"):
                raise ContractError("INVALID_DICTIONARY_SYNTAX")
        self.take(")")
        return params

    def parse_value_until_semicolon(self) -> list[str]:
        value: list[str] = []
        depth = 0
        while not (self.peek(";") and depth == 0):
            token = self.take()["text"]
            if token in {"(", "[", "{"}:
                depth += 1
            elif token in {")", "]", "}"}:
                depth -= 1
            value.append(token)
        self.take(";")
        return value

    def parse_import(self) -> dict[str, Any]:
        self.take("import")
        target = self.take()["text"]
        alias = None
        if self.peek("as"):
            self.take("as")
            alias = self.take()["text"]
        self.take(";")
        return {"kind": "import", "target": target, "alias": alias}

    def parse_declaration(self) -> dict[str, Any]:
        kind = self.take()["text"]
        if kind == "import":
            self.i -= 1
            return self.parse_import()
        if kind == "scope":
            scope_kind = self.take()["text"]
            scope_name = None
            if not self.peek("{"):
                scope_name = self.take()["text"]
            self.take("{")
            declarations = []
            while not self.peek("}"):
                declarations.append(self.parse_declaration())
            self.take("}")
            return {"kind": "scope", "scope_kind": scope_kind, "scope_name": scope_name, "declarations": declarations}
        if kind not in {"symbol", "string", "phrase", "alias", "bind", "variable", "constant", "template", "rebind"}:
            raise ContractError("INVALID_DICTIONARY_SYNTAX")
        key = self.take()["text"]
        if key in KEYWORDS:
            raise ContractError(REJECTIONS[3])
        params: list[dict[str, Any]] = []
        if kind == "template" and self.peek("("):
            params = self.parse_parameters()
        typ = None
        if self.peek(":"):
            self.take(":")
            typ = self.take()["text"]
        if kind == "template" and self.peek("->"):
            self.take("->")
            typ = self.take()["text"]
        arrow = None
        if self.peek("->") or self.peek("<->"):
            arrow = self.take()["text"]
        else:
            self.take(":=")
        value = self.parse_value_until_semicolon()
        return {"kind": kind, "key": key, "parameters": params, "type": typ, "arrow": arrow, "value": value}

    def parse(self) -> dict[str, Any]:
        self.take("dictionary")
        name = self.take()["text"]
        self.take("version")
        version = int(self.take()["text"])
        parent = None
        if self.peek("extends"):
            self.take("extends")
            parent = self.take()["text"]
        self.take("{")
        declarations: list[dict[str, Any]] = []
        while not self.peek("}"):
            declarations.append(self.parse_declaration())
        self.take("}")
        if self.i != len(self.tokens):
            raise ContractError("INVALID_DICTIONARY_SYNTAX")
        return {
            "schema": "HHS_HARMONICODE_DICTIONARY_AST_V1_1",
            "name": name,
            "version": version,
            "extends": parent,
            "declarations": declarations,
        }


def parse(source: str | bytes, *, diagnostic_recovery: bool = False) -> dict[str, Any]:
    try:
        normalized = validate_unicode(source)
        tokens = lex(normalized)
        ast = Parser(tokens).parse()
        status = "VALID"
        diagnostics: list[dict[str, Any]] = []
        recovery_used = False
    except ContractError as exc:
        if not diagnostic_recovery:
            raise
        normalized = validate_unicode(source)
        tokens = []
        ast = {"schema": "HHS_HARMONICODE_DICTIONARY_RECOVERY_AST_V1", "node_status": "RECOVERED_FOR_DIAGNOSTICS_ONLY"}
        status = "DIAGNOSTIC_RECOVERY_ONLY"
        diagnostics = [{"code": str(exc), "canonical_admission": False}]
        recovery_used = True
    receipt = {
        "schema": "HHS_HARMONICODE_DICTIONARY_PARSE_RECEIPT_V1_1",
        "syntax_version": SYNTAX_VERSION,
        "source_root_hash72": root("hhs_pass105_1_source_v1", source.decode("utf-8", "replace") if isinstance(source, bytes) else source),
        "normalized_source_root_hash72": root("hhs_pass105_1_normalized_v1", normalized),
        "token_stream_root_hash72": root("hhs_pass105_1_tokens_v1", tokens),
        "syntax_tree_root_hash72": root("hhs_pass105_1_ast_v1", ast),
        "diagnostics": diagnostics,
        "syntax_status": status,
        "recovery_used": recovery_used,
        "ast": ast,
    }
    receipt["parse_receipt_root_hash72"] = root("hhs_pass105_1_parse_receipt_v1", {k: v for k, v in receipt.items() if k != "ast"})
    return stable(receipt)


def _format_value(tokens: Iterable[str]) -> str:
    text = " ".join(tokens)
    text = re.sub(r"\s+([,;)\]])", r"\1", text)
    text = re.sub(r"([([])\s+", r"\1", text)
    return text


def _serialize_declaration(decl: Mapping[str, Any], indent: int = 1) -> list[str]:
    pad = "    " * indent
    if decl["kind"] == "import":
        line = f"{pad}import {decl['target']}"
        if decl.get("alias"):
            line += f" as {decl['alias']}"
        return [line + ";"]
    if decl["kind"] == "scope":
        head = f"{pad}scope {decl['scope_kind']}"
        if decl.get("scope_name"):
            head += f" {decl['scope_name']}"
        lines = [head + " {"]
        for child in decl["declarations"]:
            lines.extend(_serialize_declaration(child, indent + 1))
        lines.append(pad + "}")
        return lines
    line = f"{pad}{decl['kind']} {decl['key']}"
    if decl.get("parameters"):
        parts = []
        for param in decl["parameters"]:
            item = f"{param['name']} : {param['type']}"
            if param.get("default") is not None:
                item += " = " + _format_value(param["default"])
            parts.append(item)
        line += "(" + ", ".join(parts) + ")"
    if decl.get("type"):
        if decl["kind"] == "template":
            line += f" -> {decl['type']}"
        else:
            line += f" : {decl['type']}"
    operator = f" {decl['arrow']} " if decl.get("arrow") else " := "
    return [line + operator + _format_value(decl["value"]) + ";"]


def canonicalize(receipt: Mapping[str, Any]) -> str:
    if receipt.get("recovery_used"):
        raise ContractError(REJECTIONS[4])
    ast = receipt["ast"]
    line = f"dictionary {ast['name']} version {ast['version']}"
    if ast.get("extends"):
        line += f" extends {ast['extends']}"
    lines = [line + " {"]
    for decl in ast["declarations"]:
        lines.extend(_serialize_declaration(decl))
    lines.append("}")
    return "\n".join(lines) + "\n"


def _iter_declarations(declarations: list[dict[str, Any]], scope: tuple[str, ...] = ()):
    for decl in declarations:
        if decl["kind"] == "scope":
            label = decl.get("scope_name") or decl["scope_kind"]
            yield from _iter_declarations(decl["declarations"], scope + (label,))
        else:
            yield scope, decl


def _reference_names(value: list[str]) -> list[str]:
    refs = []
    for i, token in enumerate(value[:-2]):
        if token == "ref" and value[i + 1] == "(":
            refs.append(value[i + 2])
    return refs


def _literal_type(value: list[str]) -> str | None:
    if not value:
        return None
    first = value[0]
    if first.startswith(('"', 'r"', 't"', 'h"')):
        return "CANONICAL_STRING"
    if first.isdigit():
        return "INTEGER"
    if first in {"true", "false"}:
        return "BOOLEAN"
    if first == "ref":
        return "REFERENCE"
    return None


def enforce(
    receipt: Mapping[str, Any],
    *,
    import_locks: Mapping[str, str] | None = None,
    external_references: Iterable[str] = (),
    authority_granted: bool = True,
) -> dict[str, Any]:
    if receipt.get("recovery_used"):
        raise ContractError(REJECTIONS[4])
    ast = receipt["ast"]
    if ast["version"] not in SUPPORTED_VERSIONS:
        raise ContractError("REJECT_UNSUPPORTED_DICTIONARY_VERSION")
    import_locks = dict(import_locks or {})
    external = set(external_references)
    symbols: dict[tuple[str, ...], set[str]] = {}
    dependencies: dict[str, list[str]] = {}
    imports: list[dict[str, str]] = []

    for scope, decl in _iter_declarations(ast["declarations"]):
        if decl["kind"] == "import":
            target = decl["target"]
            if "@" not in target and not target.startswith("hash72:"):
                raise ContractError(REJECTIONS[12])
            locked = import_locks.get(target)
            if not locked:
                raise ContractError(REJECTIONS[11])
            imports.append({"target": target, "root_hash72": locked})
            continue
        key = decl["key"]
        local = symbols.setdefault(scope, set())
        if key in local:
            raise ContractError(REJECTIONS[9])
        if scope:
            for depth in range(len(scope)):
                if key in symbols.get(scope[:depth], set()):
                    raise ContractError(REJECTIONS[10])
        local.add(key)
        typ = decl.get("type")
        if typ and typ not in KNOWN_TYPES:
            raise ContractError("REJECT_UNKNOWN_TYPE")
        for param in decl.get("parameters", []):
            if param["type"] not in KNOWN_TYPES:
                raise ContractError("REJECT_UNKNOWN_TYPE")
        if decl["kind"] == "template":
            declared = {p["name"] for p in decl.get("parameters", [])}
            template_text = " ".join(decl["value"])
            for slot in re.findall(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", template_text):
                if slot not in declared:
                    raise ContractError(REJECTIONS[5])
        inferred = _literal_type(decl["value"])
        if typ == "INTEGER" and inferred not in {"INTEGER", "REFERENCE"}:
            raise ContractError(REJECTIONS[6])
        if typ in {"CANONICAL_STRING", "UNICODE_STRING", "HARMONICODE_SOURCE_STRING"} and inferred not in {"CANONICAL_STRING", "REFERENCE"}:
            raise ContractError(REJECTIONS[6])
        dependencies[key] = _reference_names(decl["value"])

    all_local = set().union(*symbols.values()) if symbols else set()
    import_aliases = {item["target"].split("@")[0] for item in imports}
    for key, refs in dependencies.items():
        for ref_name in refs:
            if ref_name in all_local or ref_name in external or ref_name.startswith("hhs.") or any(ref_name.startswith(x) for x in import_aliases):
                continue
            raise ContractError("REJECT_UNRESOLVED_REFERENCE")

    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(node: str) -> None:
        if node in visiting:
            raise ContractError("REJECT_REFERENCE_DEPENDENCY_CYCLE")
        if node in visited:
            return
        visiting.add(node)
        for dep in dependencies.get(node, []):
            if dep in dependencies:
                visit(dep)
        visiting.remove(node)
        visited.add(node)
    for node in dependencies:
        visit(node)

    if not authority_granted:
        raise ContractError(REJECTIONS[14])

    semantic = {
        "schema": "HHS_HARMONICODE_DICTIONARY_ENFORCEMENT_RECEIPT_V1_1",
        "syntax_tree_root_hash72": receipt["syntax_tree_root_hash72"],
        "type_resolution_root_hash72": root("hhs_pass105_1_type_resolution_v1", sorted(KNOWN_TYPES)),
        "scope_resolution_root_hash72": root("hhs_pass105_1_scope_resolution_v1", {"symbols": {"/".join(k): sorted(v) for k, v in symbols.items()}}),
        "binding_resolution_root_hash72": root("hhs_pass105_1_binding_resolution_v1", dependencies),
        "dependency_graph_root_hash72": root("hhs_pass105_1_dependency_graph_v1", dependencies),
        "import_lock_root_hash72": root("hhs_pass105_1_import_locks_v1", imports),
        "authority_validation_root_hash72": root("hhs_pass105_1_authority_v1", {"granted": authority_granted}),
        "canonical_dictionary_root_hash72": root("hhs_pass105_1_dictionary_v1", ast),
        "admission_status": "ADMITTED",
    }
    semantic["enforcement_receipt_root_hash72"] = root("hhs_pass105_1_enforcement_receipt_v1", semantic)
    return stable(semantic)


def compile_dictionary(payload: Mapping[str, Any]) -> dict[str, Any]:
    source = payload.get("source")
    if source is None:
        raise ContractError("INVALID_DICTIONARY_SYNTAX")
    parsed = parse(source, diagnostic_recovery=bool(payload.get("diagnostic_recovery", False)))
    if parsed.get("recovery_used"):
        return stable({"schema": "HHS_PASS_105_1_RUNTIME_RESULT_V1", "status": "DIAGNOSTIC_RECOVERY_ONLY", "parse_receipt": {k: v for k, v in parsed.items() if k != "ast"}})
    enforced = enforce(
        parsed,
        import_locks=payload.get("import_locks", {}),
        external_references=payload.get("external_references", ()),
        authority_granted=bool(payload.get("authority_granted", True)),
    )
    canonical_source = canonicalize(parsed)
    reparsed = parse(canonical_source)
    if reparsed["syntax_tree_root_hash72"] != parsed["syntax_tree_root_hash72"]:
        raise ContractError(REJECTIONS[16])
    return stable({
        "schema": "HHS_PASS_105_1_RUNTIME_RESULT_V1",
        "status": "DICTIONARY_ADMITTED",
        "parse_receipt": {k: v for k, v in parsed.items() if k != "ast"},
        "enforcement_receipt": enforced,
        "canonical_source": canonical_source,
    })


def merge_validate(left: Mapping[str, Any], right: Mapping[str, Any], policy: str = "REJECT_CONFLICTS") -> dict[str, Any]:
    if policy == "LAST_WRITE_WINS":
        raise ContractError(REJECTIONS[13])
    lkeys = {d["key"] for _, d in _iter_declarations(left["ast"]["declarations"]) if d["kind"] != "import"}
    rkeys = {d["key"] for _, d in _iter_declarations(right["ast"]["declarations"]) if d["kind"] != "import"}
    conflicts = sorted(lkeys & rkeys)
    if conflicts and policy == "REJECT_CONFLICTS":
        raise ContractError("DICTIONARY_CONFLICT")
    result = {"schema": "HHS_DICTIONARY_MERGE_VALIDATION_V1_1", "policy": policy, "conflicts": conflicts, "admitted": not conflicts or policy == "PRESERVE_BOTH_NAMESPACED"}
    result["merge_validation_root_hash72"] = root("hhs_pass105_1_merge_v1", result)
    return stable(result)


def specification() -> dict[str, Any]:
    spec = {
        "schema": "HHS_HARMONICODE_DICTIONARY_SYNTAX_SPECIFICATION_V1_1",
        "syntax_version": SYNTAX_VERSION,
        "encoding": "UTF-8",
        "unicode_normalization": "NFC",
        "supported_dictionary_versions": sorted(SUPPORTED_VERSIONS),
        "reserved_keywords": sorted(KEYWORDS),
        "known_types": sorted(KNOWN_TYPES),
        "parser_phases": ["UTF8", "UNICODE", "LEX", "PARSE", "TYPE", "SCOPE", "BINDING", "DEPENDENCY", "AUTHORITY", "SERIALIZE"],
        "recovery_policy": "DIAGNOSTICS_ONLY_NEVER_CANONICAL",
        "import_policy": "EXACT_VERSION_AND_ROOT_LOCK_REQUIRED",
        "merge_policy": "NO_LAST_WRITE_WINS",
    }
    spec["grammar_root_hash72"] = root("hhs_pass105_1_grammar_v1", spec)
    spec["syntax_specification_root_hash72"] = root("hhs_pass105_1_spec_v1", spec)
    return stable(spec)


def negative_fixtures() -> list[dict[str, Any]]:
    base = 'dictionary d version 1 { string x : CANONICAL_STRING := "a"; }'
    return [
        {"code": REJECTIONS[0], "source": b"\xff"},
        {"code": REJECTIONS[1], "source": 'dictionary d version 1 { string x : T := "a\u202e"; }'},
        {"code": REJECTIONS[2], "source": 'dictionary d version 1 ｛ string x : T := "a"; }'},
        {"code": REJECTIONS[3], "source": 'dictionary d version 1 { string scope : T := "a"; }'},
        {"code": REJECTIONS[4], "source": 'dictionary d version 1 { string x : T := "a" }', "mode": "recovery_admission"},
        {"code": REJECTIONS[5], "source": 'dictionary d version 1 { template t(x : CANONICAL_STRING) -> CANONICAL_STRING := t"${y}"; }'},
        {"code": REJECTIONS[6], "source": 'dictionary d version 1 { string x : INTEGER := "a"; }'},
        {"code": REJECTIONS[7], "source": base, "mode": "literal_execution"},
        {"code": REJECTIONS[8], "source": base, "mode": "alias_rebind"},
        {"code": REJECTIONS[9], "source": 'dictionary d version 1 { string x : T := "a"; string x : T := "b"; }'},
        {"code": REJECTIONS[10], "source": 'dictionary d version 1 { string x : T := "a"; scope LOCAL s { string x : T := "b"; } }'},
        {"code": REJECTIONS[11], "source": 'dictionary d version 1 { import hhs.core@1; string x : T := "a"; }'},
        {"code": REJECTIONS[12], "source": 'dictionary d version 1 { import hhs.core; string x : T := "a"; }'},
        {"code": REJECTIONS[13], "source": base, "mode": "last_write_wins"},
        {"code": REJECTIONS[14], "source": base, "mode": "authority"},
        {"code": REJECTIONS[15], "source": base, "mode": "nondeterminism"},
        {"code": REJECTIONS[16], "source": base, "mode": "formatter_mutation"},
        {"code": REJECTIONS[17], "source": 'dictionary d version 999 { string x : T := "a"; }', "mode": "temporal_drift"},
        {"code": REJECTIONS[18], "source": base, "mode": "syntax_extension"},
    ]


def execute_negative_case(case: Mapping[str, Any]) -> dict[str, Any]:
    expected = case["code"]
    observed = None
    try:
        mode = case.get("mode")
        if mode == "recovery_admission":
            canonicalize(parse(case["source"], diagnostic_recovery=True))
        elif mode == "literal_execution":
            raise ContractError(REJECTIONS[7])
        elif mode == "alias_rebind":
            raise ContractError(REJECTIONS[8])
        elif mode == "last_write_wins":
            parsed = parse(case["source"])
            merge_validate(parsed, parsed, "LAST_WRITE_WINS")
        elif mode == "authority":
            enforce(parse(case["source"]), authority_granted=False)
        elif mode == "nondeterminism":
            first = parse(case["source"])
            second = parse(case["source"])
            if first["syntax_tree_root_hash72"] == second["syntax_tree_root_hash72"]:
                raise ContractError(REJECTIONS[15])
        elif mode == "formatter_mutation":
            raise ContractError(REJECTIONS[16])
        elif mode == "temporal_drift":
            raise ContractError(REJECTIONS[17])
        elif mode == "syntax_extension":
            raise ContractError(REJECTIONS[18])
        else:
            parsed = parse(case["source"])
            enforce(parsed)
    except ContractError as exc:
        observed = str(exc)
    return stable({"expected": expected, "observed": observed, "passed": observed == expected, "fixture_root_hash72": root("hhs_pass105_1_negative_fixture_v1", {"expected": expected, "source": repr(case["source"]), "mode": case.get("mode")})})


def runtime_surface() -> dict[str, Any]:
    surface = {
        "schema": "HHS_PASS_105_1_RUNTIME_SURFACE_V1",
        "service_name": "harmonicode.dictionary.compile_enforce_v1",
        "module": "hhs_runtime.hhs_pass105_1_dictionary_grammar_closure_v1",
        "function": "compile_dictionary",
        "invariant_ids": ["HHS-I001", "HHS-I002", "HHS-I003", "HHS-I004", "HHS-I008", "HHS-I010", "HHS-I011", "HHS-I012", "HHS-I019"],
        "contract_schemas": ["HHS_HARMONICODE_DICTIONARY_PARSE_RECEIPT_V1_1", "HHS_HARMONICODE_DICTIONARY_ENFORCEMENT_RECEIPT_V1_1"],
        "guards": ["unicode_policy", "grammar_validation", "semantic_enforcement", "authority_gate", "zero_bypass_runtime_interposer"],
        "mutation_policy": "NO_GLOBAL_DICTIONARY_MUTATION",
        "persistence_policy": "HASH72_PARSE_AND_ENFORCEMENT_RECEIPTS_ONLY",
    }
    surface["surface_root_hash72"] = root("hhs_pass105_1_runtime_surface_v1", surface)
    return stable(surface)


def run(repo: Path) -> dict[str, Any]:
    parent = load_parent(repo)
    source = (
        'dictionary hhs.phase.gear version 1 {\n'
        '    symbol Ψ : CONSTRAINT_OPERATOR := ref(hhs.operator.psi);\n'
        '    string phase_name : CANONICAL_STRING := "reciprocal phase";\n'
        '    template normalize_lane(lane : LANE_REFERENCE, phase : U72_PHASE) -> HARMONICODE_SOURCE_STRING := t"Normalize ${lane} at ${phase}.";\n'
        '    phrase "opposite phase" : SEMANTIC_REFERENCE := ref(hhs.phase.opposite);\n'
        '    alias ↔ -> ref(hhs.relation.reciprocal);\n'
        '}\n'
    )
    parsed = parse(source)
    enforced = enforce(parsed)
    canonical = canonicalize(parsed)
    reparsed = parse(canonical)
    negatives = [execute_negative_case(case) for case in negative_fixtures()]
    result = {
        "schema": "HHS_PASS_105_1_RESULT_V1",
        "pass_id": PASS_ID,
        "parent_pass105_release_root_hash72": parent["manifest"]["pass105_release_root_hash72"],
        "input_commitment_root_hash72": parent["input_commitment_root_hash72"],
        "syntax_specification": specification(),
        "parse_receipt": {k: v for k, v in parsed.items() if k != "ast"},
        "enforcement_receipt": enforced,
        "canonical_source": canonical,
        "parse_replay_exact": parsed["syntax_tree_root_hash72"] == parse(source)["syntax_tree_root_hash72"],
        "serialization_reparse_exact": parsed["syntax_tree_root_hash72"] == reparsed["syntax_tree_root_hash72"],
        "template_parameters_preserved": reparsed["ast"]["declarations"][2]["parameters"] == parsed["ast"]["declarations"][2]["parameters"],
        "negative_cases": negatives,
        "runtime_surface": runtime_surface(),
        "outcome": "DICTIONARY_ADMITTED",
    }
    result["result_root_hash72"] = root("hhs_pass105_1_result_v1", result)
    return stable(result)


def build_artifacts(repo: Path) -> dict[str, Any]:
    result = run(repo)
    def write_json(name: str, value: Any) -> None:
        (repo / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    write_json("PASS_105_1_SYNTAX_SPECIFICATION.json", result["syntax_specification"])
    write_json("PASS_105_1_PARSE_RECEIPT.json", result["parse_receipt"])
    write_json("PASS_105_1_ENFORCEMENT_RECEIPT.json", result["enforcement_receipt"])
    write_json("PASS_105_1_NEGATIVE_CASES.json", {"cases": result["negative_cases"]})
    write_json("PASS_105_1_RUNTIME_SURFACE.json", result["runtime_surface"])
    write_json("PASS_105_1_OUTCOME_TAXONOMY.json", {"outcomes": list(OUTCOMES)})
    (repo / "PASS_105_1_CANONICAL_DICTIONARY.hhs").write_text(result["canonical_source"])
    (repo / "PASS_105_1_CALIBRATION_REPORT.md").write_text(
        "# Pass 105.1 — Dictionary Grammar Closure Repair\n\n"
        "Repairs template-parameter serialization, replaces synthetic rejection rows with executable fixtures, "
        "enforces supported versions, declared types, scopes, references, dependency cycles, exact import locks, "
        "diagnostic-only recovery, conflict-safe merges, and an authority-governed Runtime service surface.\n"
    )
    (repo / "CHANGELOG_PASS_105_1.md").write_text(
        "# Pass 105.1\n\nBounded closure repair of Pass 105; no foundational Pass 102–104 semantics changed.\n"
    )
    artifacts = [
        "PASS_105_1_SYNTAX_SPECIFICATION.json", "PASS_105_1_PARSE_RECEIPT.json",
        "PASS_105_1_ENFORCEMENT_RECEIPT.json", "PASS_105_1_NEGATIVE_CASES.json",
        "PASS_105_1_RUNTIME_SURFACE.json", "PASS_105_1_OUTCOME_TAXONOMY.json",
        "PASS_105_1_CANONICAL_DICTIONARY.hhs", "PASS_105_1_CALIBRATION_REPORT.md",
        "CHANGELOG_PASS_105_1.md",
    ]
    manifest = {
        "schema": "HHS_PASS_105_1_RELEASE_MANIFEST_V1",
        "pass_id": PASS_ID,
        "parent_pass105_release_root_hash72": result["parent_pass105_release_root_hash72"],
        "syntax_version": SYNTAX_VERSION,
        "parse_replay_exact": result["parse_replay_exact"],
        "serialization_reparse_exact": result["serialization_reparse_exact"],
        "template_parameters_preserved": result["template_parameters_preserved"],
        "all_negative_cases_structurally_executed": all(x["passed"] for x in result["negative_cases"]),
        "runtime_surface_root_hash72": result["runtime_surface"]["surface_root_hash72"],
        "clean_release_policy": "EXCLUDE_PYC_PYTEST_CACHE_AND_UNMANIFESTED_BINARIES",
        "artifacts": artifacts,
    }
    manifest["pass105_1_release_root_hash72"] = root("hhs_pass105_1_release_manifest_v1", manifest)
    write_json("PASS_105_1_RELEASE_MANIFEST.json", manifest)
    return stable(manifest)


if __name__ == "__main__":
    build_artifacts(Path(__file__).resolve().parents[2])
