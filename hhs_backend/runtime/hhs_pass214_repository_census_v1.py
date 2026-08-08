"""Pass 214 iteration 1: immutable Git-tree census and static optimization registry."""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.pass197_exact_v1 import canonical_json, hash72

CONTRACT = "HHS-P214-REPOSITORY-WIDE-COMPOUND-DATA-MANAGEMENT-MULTIMODAL-ML-OPTIMIZATION-INTEGRATION-BENCHMARK-CALIBRATION-EVIDENCE-H72-H216-VM5184-G243"
ITERATION = 1
PASS213_FOUNDATION = "86ec461818682fc87232740758769602e8f9fe05"
RUNTIME_CLASSIFICATION = "HHS_PASS_214_ITERATION_1_REPOSITORY_CENSUS_IMPLEMENTED"
DISPOSITIONS = (
    "SCANNED_CALLABLE", "SCANNED_DATA_AUTHORITY", "SCANNED_TEST_OR_EVIDENCE",
    "SCANNED_CONTRACT_ONLY", "SCANNED_COMPATIBLE_READ_ONLY", "SCANNED_SUPERSEDED",
    "SCANNED_DUPLICATE", "SCANNED_EXPERIMENTAL", "SCANNED_BROKEN",
    "SCANNED_QUARANTINED", "SCANNED_NOT_APPLICABLE",
)
SOURCE_EXTENSIONS = {".py", ".pyi", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".rs", ".go", ".java", ".kt", ".kts", ".swift", ".sh", ".bash", ".zsh", ".ps1", ".sql"}
DATA_EXTENSIONS = {".json", ".jsonl", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".csv", ".tsv", ".xml", ".html", ".css", ".scss", ".lock", ".txt", ".wasm", ".glsl", ".wgsl", ".vert", ".frag"}
DOC_EXTENSIONS = {".md", ".rst", ".adoc"}
LANGUAGES = {".py": "python", ".pyi": "python", ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript", ".jsx": "javascript", ".ts": "typescript", ".tsx": "typescript", ".c": "c", ".h": "c-header", ".cc": "cpp", ".cpp": "cpp", ".cxx": "cpp", ".hpp": "cpp-header", ".rs": "rust", ".go": "go", ".java": "java", ".kt": "kotlin", ".kts": "kotlin", ".swift": "swift", ".sh": "shell", ".bash": "shell", ".zsh": "shell", ".ps1": "powershell", ".sql": "sql"}
FAMILIES: Mapping[str, tuple[str, ...]] = {
    "source_storage_lifecycle": ("storage", "store", "blob", "file", "folder", "sqlite", "sql", "database", "snapshot", "checkpoint", "persist", "wal", "tombstone", "quarantine", "archive"),
    "cache_retrieval_reuse": ("cache", "memo", "reuse", "retrieval", "search", "index", "nearest", "similar", "semantic_composition", "predictive_continuation", "receipt_vector"),
    "delta_continuation_dependency": ("delta", "diff", "residual", "continuation", "dependency", "frontier", "branch", "replay", "resume", "rollback", "parametric"),
    "compression_hydration_recovery": ("compress", "codec", "hydrate", "hydration", "superframe", "shard", "parity", "erasure", "recover", "reconstruct", "generator", "exception"),
    "multimodal_machine_learning": ("multimodal", "learning", "train", "finetune", "backprop", "gradient", "weight", "feature", "embedding", "invariant", "novelty", "contradiction", "dataset", "model", "token", "attention", "transformer", "agi"),
    "graphics_audio_video_temporal": ("graphics", "image", "pixel", "sprite", "shader", "scene", "geometry", "physics", "audio", "pcm", "video", "cinematic", "animation", "motion", "frame", "temporal"),
    "compiled_rom_native_dispatch": ("compiled_rom", "compiled-rom", "rom", "native_dispatch", "dispatch", "vm81", "vm5184", "opcode", "abi", "kernel", "arena", "secure_memory"),
    "integrity_receipt_lineage": ("hash72", "hash216", "receipt", "ledger", "lineage", "integrity", "signature", "timestamp", "rfc3161", "pqc", "kem", "dsa", "authentication", "authority"),
    "compiler_artifact_packaging": ("compiler", "compile", "transpile", "artifact", "package", "bundle", "manifest", "registry", "schema", "openapi", "sdk", "cli", "api"),
    "parallel_accelerator": ("gpu", "cuda", "hip", "vulkan", "webgpu", "metal", "accelerator", "parallel", "thread", "worker", "batch", "simd", "soa", "csr"),
}
MODALITIES: Mapping[str, tuple[str, ...]] = {
    "text": ("text", "markdown", "language", "lex", "word", "grammar"),
    "source_code": ("source", "code", "ast", "compiler", "syntax"),
    "structured_data": ("json", "jsonl", "csv", "xml", "table", "sql"),
    "image_graphics": ("image", "graphics", "pixel", "sprite", "shader", "scene"),
    "audio": ("audio", "pcm", "wave", "frequency", "sound"),
    "video_animation": ("video", "cinematic", "animation", "motion", "frame"),
    "game_physics": ("game", "physics", "collision", "geometry", "lighting"),
    "machine_learning": ("model", "learning", "train", "feature", "weight", "attention", "transformer"),
    "binary_object": ("binary", "blob", "artifact", "package"),
}
PASS_RE = re.compile(r"(?:^|[^a-z0-9])(?:pass|p)[-_ ]*0*(\d{1,3})(?:[^0-9]|$)", re.I)
VENDOR = {"node_modules", "venv", "site", "packages", "vendor", "third", "party", "dist", "build", "pycache"}
TEST_EVIDENCE = {"test", "tests", "evidence", "fixtures", "benchmarks", "benchmark", "reports", "receipts"}
CONTRACT = CONTRACT


class Pass214CensusError(RuntimeError):
    pass


def _git(root: Path, *args: str) -> bytes:
    try:
        return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise Pass214CensusError(f"PASS214_GIT_COMMAND_FAILED:{' '.join(args)}") from exc


def hash216(domain: str, value: Any) -> str:
    payload = canonical_json(value).encode()
    name = domain.encode()
    return sha256(b"HHS-P214-HASH216-V1\0" + len(name).to_bytes(2, "big") + name + len(payload).to_bytes(8, "big") + payload).hexdigest()


def _tokens(path: str) -> set[str]:
    return {item for item in re.split(r"[^a-z0-9]+", path.lower()) if item}


def _origin(path: str) -> dict[str, Any]:
    values = [int(item) for item in PASS_RE.findall(path)]
    number = max(values) if values else None
    return {"origin_kind": "NUMBERED_PASS" if number is not None else "PRE_PASS_OR_UNNUMBERED_FOUNDATION", "pass_number": number, "origin_label": f"PASS_{number:03d}" if number is not None else "PRE_PASS_OR_UNNUMBERED"}


def _tags(path: str, name: str, registry: Mapping[str, tuple[str, ...]]) -> list[str]:
    text = f"{path} {name}".lower().replace("-", "_")
    return sorted(key for key, words in registry.items() if any(word.replace("-", "_") in text for word in words))


def _tree(root: Path, ref: str) -> tuple[str, str, str, list[dict[str, Any]]]:
    commit = _git(root, "rev-parse", ref).decode().strip()
    tree = _git(root, "rev-parse", f"{ref}^{{tree}}").decode().strip()
    timestamp = _git(root, "show", "-s", "--format=%cI", commit).decode().strip()
    raw = _git(root, "ls-tree", "-r", "-t", "-l", "-z", ref)
    result: list[dict[str, Any]] = []
    for row in raw.split(b"\0"):
        if not row:
            continue
        meta, path = row.split(b"\t", 1)
        mode, kind, object_id, size = meta.split(b" ", 3)
        result.append({"path": path.decode("utf-8", "surrogateescape"), "mode": mode.decode(), "object_type": kind.decode(), "object_id": object_id.decode(), "size": None if size.strip() == b"-" else int(size)})
    result.sort(key=lambda item: item["path"].encode("utf-8", "surrogateescape"))
    if len(result) != len({item["path"] for item in result}):
        raise Pass214CensusError("PASS214_GIT_TREE_DUPLICATE_PATH")
    return commit, tree, timestamp, result


def _language(path: str, kind: str) -> str:
    if kind == "tree": return "directory"
    suffix = PurePosixPath(path).suffix.lower()
    if suffix in LANGUAGES: return LANGUAGES[suffix]
    if suffix in DOC_EXTENSIONS: return "documentation"
    if suffix in DATA_EXTENSIONS: return "data"
    return "gitlink" if kind == "commit" else "binary_or_unclassified"


def _decorator(node: ast.expr) -> str:
    if isinstance(node, ast.Name): return node.id
    if isinstance(node, ast.Attribute):
        parent = _decorator(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    if isinstance(node, ast.Call): return _decorator(node.func)
    return node.__class__.__name__


class _Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.stack: list[str] = []
        self.items: list[dict[str, Any]] = []
    def add(self, node: ast.AST, name: str, kind: str, decorators: Sequence[ast.expr] = ()) -> None:
        qname = ".".join((*self.stack, name)) if self.stack else name
        self.items.append({"name": name, "qualified_name": qname, "kind": kind, "line_start": int(getattr(node, "lineno", 0)), "line_end": int(getattr(node, "end_lineno", getattr(node, "lineno", 0))), "decorators": sorted(_decorator(item) for item in decorators)})
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.add(node, node.name, "class", node.decorator_list); self.stack.append(node.name); self.generic_visit(node); self.stack.pop()
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.add(node, node.name, "method" if self.stack else "function", node.decorator_list); self.stack.append(node.name); self.generic_visit(node); self.stack.pop()
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.add(node, node.name, "async_method" if self.stack else "async_function", node.decorator_list); self.stack.append(node.name); self.generic_visit(node); self.stack.pop()


REGEXES: Mapping[str, tuple[tuple[str, re.Pattern[str]], ...]] = {
    "javascript": (("class", re.compile(r"(?m)^\s*(?:export\s+)?class\s+([A-Za-z_$][\w$]*)")), ("function", re.compile(r"(?m)^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(")), ("arrow", re.compile(r"(?m)^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^\n]*\)|[A-Za-z_$][\w$]*)\s*=>"))),
    "typescript": (),
    "c": (("function_or_prototype", re.compile(r"(?m)^\s*(?!if\b|for\b|while\b|switch\b|return\b)(?:[A-Za-z_][\w\s\*:&<>]*?\s+)+([A-Za-z_]\w*)\s*\([^;{}]*\)\s*(?:\{|;)")),),
    "rust": (("function", re.compile(r"(?m)^\s*(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?fn\s+([A-Za-z_]\w*)\s*\(")),),
    "go": (("function_or_method", re.compile(r"(?m)^\s*func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)\s*\(")),),
    "shell": (("function", re.compile(r"(?m)^\s*(?:function\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*(?:\(\))?\s*\{")),),
}
REGEXES = {**REGEXES, "typescript": REGEXES["javascript"], "c-header": REGEXES["c"], "cpp": REGEXES["c"], "cpp-header": REGEXES["c"], "powershell": REGEXES["shell"]}
SQL_RE = re.compile(r"(?im)^\s*create\s+(?:or\s+replace\s+)?(table|view|index|trigger|function|procedure)\s+(?:if\s+not\s+exists\s+)?[\"`\[]?([A-Za-z_][\w.]*)")


def _symbols(text: str | None, language: str, read_error: str | None) -> tuple[list[dict[str, Any]], str | None]:
    if read_error: return [], read_error
    if text is None: return [], None
    if language == "python":
        try: tree = ast.parse(text)
        except (SyntaxError, ValueError) as exc: return [], f"PYTHON_PARSE_ERROR:{getattr(exc, 'lineno', 0) or 0}"
        visitor = _Visitor(); visitor.visit(tree); return visitor.items, None
    if language == "sql":
        return [{"name": m.group(2), "qualified_name": m.group(2), "kind": f"sql_{m.group(1).lower()}", "line_start": text.count("\n", 0, m.start()) + 1, "line_end": text.count("\n", 0, m.end()) + 1, "decorators": []} for m in SQL_RE.finditer(text)], None
    output: list[dict[str, Any]] = []
    for kind, pattern in REGEXES.get(language, ()): 
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            output.append({"name": match.group(1), "qualified_name": match.group(1), "kind": kind, "line_start": line, "line_end": text.count("\n", 0, match.end()) + 1, "decorators": []})
    return output, None


def _read(root: Path, entry: Mapping[str, Any], limit: int) -> tuple[str | None, str | None]:
    if entry["object_type"] != "blob" or PurePosixPath(entry["path"]).suffix.lower() not in SOURCE_EXTENSIONS: return None, None
    if entry["size"] is not None and entry["size"] > limit: return None, "SOURCE_TOO_LARGE_FOR_STATIC_SYMBOL_EXTRACTION"
    try: raw = (root / entry["path"]).read_bytes()
    except OSError: return None, "TRACKED_SOURCE_NOT_MATERIALIZED"
    if b"\0" in raw: return None, "BINARY_SOURCE_CONTENT"
    return raw.decode("utf-8", "surrogateescape"), None


def _disposition(entry: Mapping[str, Any], parse_error: str | None, symbol_count: int) -> tuple[str, str]:
    tokens, suffix = _tokens(entry["path"]), PurePosixPath(entry["path"]).suffix.lower()
    if entry["object_type"] == "tree": return "SCANNED_NOT_APPLICABLE", "directory_container"
    if "quarantine" in tokens or "quarantined" in tokens: return "SCANNED_QUARANTINED", "explicit_quarantine_path"
    if tokens & VENDOR: return "SCANNED_NOT_APPLICABLE", "generated_or_third_party_dependency"
    if parse_error and suffix in SOURCE_EXTENSIONS: return "SCANNED_BROKEN", parse_error
    if tokens & {"deprecated", "obsolete", "legacy", "superseded", "old"}: return "SCANNED_SUPERSEDED", "explicit_legacy_or_superseded_path"
    if tokens & {"experimental", "prototype", "sandbox", "scratch", "spike", "lab"}: return "SCANNED_EXPERIMENTAL", "explicit_experimental_path"
    if tokens & TEST_EVIDENCE: return "SCANNED_TEST_OR_EVIDENCE", "test_benchmark_or_evidence_path"
    if suffix in DOC_EXTENSIONS or tokens & {"docs", "contracts", "spec", "specs", "documentation"}: return "SCANNED_CONTRACT_ONLY", "documentation_or_contract_surface"
    if tokens & {"release", "artifacts", "archive", "frozen", "snapshots"}: return "SCANNED_COMPATIBLE_READ_ONLY", "archival_or_release_surface"
    if symbol_count or suffix in SOURCE_EXTENSIONS: return "SCANNED_CALLABLE", "source_or_callable_surface"
    if suffix in DATA_EXTENSIONS: return "SCANNED_DATA_AUTHORITY", "structured_or_runtime_data_surface"
    return "SCANNED_NOT_APPLICABLE", "unclassified_noncallable_tracked_object"


def _symbol_record(entry: Mapping[str, Any], language: str, raw: Mapping[str, Any]) -> dict[str, Any]:
    text = f"{entry['path']} {raw['qualified_name']}".lower()
    record = {"path": entry["path"], "blob_object_id": entry["object_id"], "language": language, "entrypoint": raw["qualified_name"], "symbol_name": raw["name"], "symbol_kind": raw["kind"], "line_start": raw["line_start"], "line_end": raw["line_end"], "decorators": raw.get("decorators", []), "origin": _origin(entry["path"]), "optimization_families": _tags(entry["path"], raw["qualified_name"], FAMILIES), "modalities": _tags(entry["path"], raw["qualified_name"], MODALITIES), "exactness_class": "EXACT_OR_CONTRACTED_DETERMINISTIC" if any(key in text for key in ("exact", "bigint", "rational", "fixed_point", "no_float", "integer")) else "UNSPECIFIED_REQUIRES_CONFORMANCE", "mutation_authority": "INHERITED_VM81_OR_GOVERNED_AUTHORITY_CANDIDATE" if any(key in text for key in ("vm81", "authority", "admission", "commit", "dispatch", "ledger", "pass213")) else "UNRESOLVED_REQUIRES_CALLABLE_CONFORMANCE", "operational_status": "STATICALLY_DISCOVERED_NOT_YET_CALLABLE_VALIDATED"}
    return {**record, "symbol_hash216": hash216("optimization-symbol", record)}


def build_repository_census(repository_root: Path | str, *, source_ref: str = "HEAD", max_source_bytes: int = 4 * 1024 * 1024) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    if not (root / ".git").exists(): raise Pass214CensusError("PASS214_REPOSITORY_GIT_METADATA_REQUIRED")
    commit, tree_id, timestamp, entries = _tree(root, source_ref)
    by_object: dict[str, list[str]] = defaultdict(list)
    for item in entries:
        if item["object_type"] == "blob": by_object[item["object_id"]].append(item["path"])
    relations, duplicate_of = [], {}
    for object_id, paths in sorted(by_object.items()):
        if len(paths) < 2: continue
        paths.sort(); body = {"relation_class": "IDENTICAL", "object_id": object_id, "primary_path": paths[0], "member_paths": paths, "member_count": len(paths)}
        relations.append({**body, "relation_hash216": hash216("identical-blob-relation", body)})
        duplicate_of.update({path: paths[0] for path in paths[1:]})
    paths_out, symbols_out, errors = [], [], []
    dispositions, languages, origins, families, modalities = Counter(), Counter(), Counter(), Counter(), Counter()
    for entry in entries:
        language = _language(entry["path"], entry["object_type"])
        text, read_error = _read(root, entry, max_source_bytes)
        raw_symbols, parse_error = _symbols(text, language, read_error)
        symbols = [_symbol_record(entry, language, raw) for raw in raw_symbols]
        symbols_out.extend(symbols)
        if parse_error: errors.append({"path": entry["path"], "error": parse_error})
        disposition, reason = _disposition(entry, parse_error, len(symbols)); base = disposition
        duplicate = duplicate_of.get(entry["path"])
        if duplicate and disposition not in {"SCANNED_BROKEN", "SCANNED_QUARANTINED"}: disposition, reason = "SCANNED_DUPLICATE", "identical_git_blob"
        origin = _origin(entry["path"])
        family_tags = sorted(set(_tags(entry["path"], "", FAMILIES)) | {tag for item in symbols for tag in item["optimization_families"]})
        modality_tags = sorted(set(_tags(entry["path"], "", MODALITIES)) | {tag for item in symbols for tag in item["modalities"]})
        body = {**entry, "language": language, "origin": origin, "disposition": disposition, "base_disposition": base, "disposition_reason": reason, "duplicate_of": duplicate, "symbol_count": len(symbols), "optimization_families": family_tags, "modalities": modality_tags, "static_scan_error": parse_error}
        paths_out.append({**body, "path_record_hash216": hash216("path-census-record", body)})
        dispositions[disposition] += 1; languages[language] += 1; origins[origin["origin_label"]] += 1; families.update(family_tags); modalities.update(modality_tags)
    paths_out.sort(key=lambda item: item["path"]); symbols_out.sort(key=lambda item: (item["path"], item["line_start"], item["entrypoint"], item["symbol_kind"])); errors.sort(key=lambda item: item["path"])
    numbered = sorted({item["origin"]["pass_number"] for item in paths_out if item["origin"]["pass_number"] is not None})
    coverage = {"tracked_tree_entries": len(entries), "classified_tree_entries": len(paths_out), "classification_complete": len(entries) == len(paths_out), "unique_paths": len({item["path"] for item in paths_out}), "candidate_symbols": len(symbols_out), "exact_duplicate_groups": len(relations), "exact_duplicate_paths": len(duplicate_of), "static_scan_errors": len(errors), "numbered_pass_minimum": numbered[0] if numbered else None, "numbered_pass_maximum": numbered[-1] if numbered else None, "pre_pass_or_unnumbered_entries": origins["PRE_PASS_OR_UNNUMBERED"]}
    if not coverage["classification_complete"] or coverage["unique_paths"] != len(entries): raise Pass214CensusError("PASS214_PATH_CLASSIFICATION_INCOMPLETE")
    roots = {"repository_tree_root_hash216": hash216("repository-git-tree-manifest", entries), "path_census_root_hash216": hash216("repository-path-census", paths_out), "optimization_registry_root_hash216": hash216("optimization-symbol-registry", symbols_out), "duplicate_relation_root_hash216": hash216("duplicate-relation-registry", relations), "static_scan_error_root_hash216": hash216("static-scan-errors", errors)}
    semantic = {"contract": CONTRACT, "iteration": ITERATION, "source_commit": commit, "source_tree": tree_id, "pass213_foundation": PASS213_FOUNDATION, "roots": roots, "coverage": coverage, "disposition_counts": dict(sorted(dispositions.items())), "language_counts": dict(sorted(languages.items())), "origin_counts": dict(sorted(origins.items())), "optimization_family_counts": dict(sorted(families.items())), "modality_counts": dict(sorted(modalities.items()))}
    summary_body = {"schema": "HHS_PASS_214_REPOSITORY_CENSUS_V1", "contract": CONTRACT, "pass": 214, "iteration": ITERATION, "classification": RUNTIME_CLASSIFICATION, "source_commit": commit, "source_tree": tree_id, "source_commit_timestamp": timestamp, "pass213_foundation": PASS213_FOUNDATION, "roots": {**roots, "iteration1_semantic_root_hash216": hash216("pass214-iteration1-semantic-root", semantic)}, "coverage": coverage, "disposition_counts": semantic["disposition_counts"], "language_counts": semantic["language_counts"], "origin_counts": semantic["origin_counts"], "optimization_family_counts": semantic["optimization_family_counts"], "modality_counts": semantic["modality_counts"], "claim_boundary": {"repository_census_complete_for_bound_git_tree": True, "candidate_symbols_statically_discovered": True, "callable_runtime_conformance_complete": False, "compatibility_graph_complete": False, "compound_benchmark_complete": False, "pass214_terminal_roots_minted": False, "pass215_benchmark_authorized": False}}
    summary = {**summary_body, "receipt_hash72": hash72("pass214.iteration1.repository.census", summary_body)}
    return {"tree_manifest": entries, "path_census": paths_out, "optimization_registry": symbols_out, "duplicate_relations": relations, "static_scan_errors": errors, "summary": summary}


def write_census_outputs(result: Mapping[str, Any], output_directory: Path | str) -> dict[str, Path]:
    output = Path(output_directory); output.mkdir(parents=True, exist_ok=True)
    mapping = {"repository_tree_manifest": result["tree_manifest"], "path_census": result["path_census"], "optimization_registry": result["optimization_registry"], "duplicate_relations": result["duplicate_relations"], "static_scan_errors": result["static_scan_errors"], "iteration1_summary": result["summary"]}
    paths = {}
    for name, payload in mapping.items():
        path = output / f"{name}.json"; path.write_text(canonical_json(payload) + "\n", encoding="utf-8"); paths[name] = path
    return paths


def load_and_validate_outputs(output_directory: Path | str) -> dict[str, Any]:
    output = Path(output_directory); names = ("repository_tree_manifest", "path_census", "optimization_registry", "duplicate_relations", "static_scan_errors", "iteration1_summary")
    payloads = {name: json.loads((output / f"{name}.json").read_text(encoding="utf-8")) for name in names}
    roots = payloads["iteration1_summary"]["roots"]
    expected = {"repository_tree_root_hash216": hash216("repository-git-tree-manifest", payloads["repository_tree_manifest"]), "path_census_root_hash216": hash216("repository-path-census", payloads["path_census"]), "optimization_registry_root_hash216": hash216("optimization-symbol-registry", payloads["optimization_registry"]), "duplicate_relation_root_hash216": hash216("duplicate-relation-registry", payloads["duplicate_relations"]), "static_scan_error_root_hash216": hash216("static-scan-errors", payloads["static_scan_errors"])}
    for field, value in expected.items():
        if roots.get(field) != value: raise Pass214CensusError(f"PASS214_OUTPUT_ROOT_MISMATCH:{field}")
    summary = payloads["iteration1_summary"]
    if summary["coverage"]["tracked_tree_entries"] != len(payloads["repository_tree_manifest"]): raise Pass214CensusError("PASS214_TREE_COUNT_MISMATCH")
    if summary["coverage"]["classified_tree_entries"] != len(payloads["path_census"]): raise Pass214CensusError("PASS214_CENSUS_COUNT_MISMATCH")
    if summary["coverage"]["candidate_symbols"] != len(payloads["optimization_registry"]): raise Pass214CensusError("PASS214_SYMBOL_COUNT_MISMATCH")
    return payloads
