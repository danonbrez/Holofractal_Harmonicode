"""Pass 219 Lane 5 global capability visibility and Hash216 hydration 1.76.

This successor closes the discovery/visibility gap without changing canonical
authority.  It statically discovers repository source/callable surfaces from
Git objects, including fetched branch and pull-request refs, and hydrates every
discovered surface into a candidate-only Hash216 vector database.

Discovery never imports or executes discovered modules.  Classification labels
such as demo/example/reference/candidate-only/disabled/not-ready are preserved
as metadata and are never visibility filters.
"""
from __future__ import annotations

import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import sqlite3
import subprocess
from typing import Any, Iterable, Mapping, Sequence

from hhs_runtime.pass191.repository_hydration import _hash216

SCHEMA = "HHS_PASS_219_LANE5_GLOBAL_CAPABILITY_VISIBILITY_1_76"
DB_SCHEMA = "HHS_PASS_219_LANE5_GLOBAL_CAPABILITY_HASH216_VECTOR_DB_1_76"
HASH216_CHARS = 216

SOURCE_SUFFIXES = {
    ".py", ".pyi", ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".hh",
    ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".harmonicode",
}
TEXT_SUFFIXES = SOURCE_SUFFIXES | {".md", ".rst", ".adoc", ".json", ".yaml", ".yml", ".toml"}

CLASSIFICATION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("DEMO", re.compile(r"(?i)(?:^|[^a-z0-9])demo(?:[^a-z0-9]|$)")),
    ("EXAMPLE", re.compile(r"(?i)(?:^|[^a-z0-9])example(?:[^a-z0-9]|$)")),
    ("REFERENCE", re.compile(r"(?i)(?:^|[^a-z0-9])reference(?:[^a-z0-9]|$)")),
    ("CANDIDATE_ONLY", re.compile(r"(?i)candidate[_ -]?only")),
    ("DISABLED", re.compile(r"(?i)(?:^|[^a-z0-9])disabled(?:[^a-z0-9]|$)")),
    ("DEPRECATED", re.compile(r"(?i)(?:^|[^a-z0-9])deprecated(?:[^a-z0-9]|$)")),
    ("NEEDS_ADAPTER", re.compile(r"(?i)needs?[_ -]?adapter")),
    ("NEEDS_CONFIGURATION", re.compile(r"(?i)needs?[_ -]?config(?:uration)?")),
    ("NOT_READY", re.compile(r"(?i)not[_ -]?ready")),
    ("NON_EXECUTABLE", re.compile(r"(?i)non[_ -]?executable")),
)

C_CPP_FUNCTION = re.compile(
    r"(?m)^[ \t]*(?!if\b|for\b|while\b|switch\b|return\b)"
    r"(?:[A-Za-z_][A-Za-z0-9_:<>\[\] \t*&]+[ \t]+)"
    r"([A-Za-z_][A-Za-z0-9_:]*)[ \t]*\([^;{}]*\)[ \t]*(?:\{|;)"
)
JS_TS_SYMBOL = re.compile(
    r"(?m)^[ \t]*(?:export[ \t]+)?(?:default[ \t]+)?"
    r"(?:(?:async[ \t]+)?function|class)[ \t]+([A-Za-z_$][A-Za-z0-9_$]*)"
)


class Pass219Lane5GlobalCapabilityVisibilityError(RuntimeError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass219Lane5GlobalCapabilityVisibilityError(
            f"floating-point visibility metadata forbidden at {path}"
        )
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _canonical(value: Any) -> str:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _h216(domain: str, payload: Any) -> str:
    value = _hash216(domain, payload)
    if not isinstance(value, str) or len(value) != HASH216_CHARS:
        raise Pass219Lane5GlobalCapabilityVisibilityError(
            f"{domain} did not produce a 216-character Hash216 identity"
        )
    return value


def _git(root: Path, *args: str, check: bool = True) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise Pass219Lane5GlobalCapabilityVisibilityError(
            f"git command failed: {' '.join(args)}"
        ) from exc
    return result.stdout


def _git_optional(root: Path, *args: str) -> str:
    try:
        return _git(root, *args)
    except Pass219Lane5GlobalCapabilityVisibilityError:
        return ""


def _source_path(path: str) -> bool:
    return PurePosixPath(path).suffix.lower() in SOURCE_SUFFIXES


def _read_git_text(root: Path, commit: str, path: str) -> str:
    if not _source_path(path):
        return ""
    return _git_optional(root, "show", f"{commit}:{path}")


def _classification_labels(path: str, text: str) -> list[str]:
    haystack = path + "\n" + text
    return [
        label
        for label, pattern in CLASSIFICATION_PATTERNS
        if pattern.search(haystack)
    ]


def _python_symbols(text: str) -> tuple[list[tuple[str, str, int]], str]:
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return [], "PARSE_ERROR_VISIBLE"

    found: list[tuple[str, str, int]] = []

    def walk(body: Sequence[ast.stmt], prefix: str = "") -> None:
        for node in body:
            if isinstance(node, ast.ClassDef):
                name = f"{prefix}{node.name}"
                found.append((name, "PYTHON_CLASS", int(node.lineno)))
                walk(node.body, name + ".")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = f"{prefix}{node.name}"
                found.append((name, "PYTHON_FUNCTION", int(node.lineno)))

    walk(tree.body)
    return found, "PARSED_STATICALLY"


def _symbols(path: str, text: str) -> tuple[list[tuple[str, str, int]], str]:
    suffix = PurePosixPath(path).suffix.lower()
    if suffix in {".py", ".pyi"}:
        return _python_symbols(text)
    if suffix in {".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".hh"}:
        rows = [
            (match.group(1), "C_CPP_CALLABLE", text.count("\n", 0, match.start()) + 1)
            for match in C_CPP_FUNCTION.finditer(text)
        ]
        return rows, "PARSED_STATICALLY"
    if suffix in {".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx"}:
        rows = [
            (match.group(1), "JS_TS_CALLABLE", text.count("\n", 0, match.start()) + 1)
            for match in JS_TS_SYMBOL.finditer(text)
        ]
        return rows, "PARSED_STATICALLY"
    return [], "SOURCE_VISIBLE"


def _node(
    *,
    source_state: str,
    ref_name: str,
    commit_sha: str,
    path: str,
    symbol: str,
    symbol_kind: str,
    line: int,
    labels: Sequence[str],
    parse_state: str,
) -> dict[str, Any]:
    core = {
        "node_kind": "CAPABILITY_SURFACE",
        "source_state": source_state,
        "ref_name": ref_name,
        "commit_sha": commit_sha,
        "source_path": path,
        "symbol": symbol,
        "symbol_kind": symbol_kind,
        "line": int(line),
        "classification_labels": sorted(set(str(v) for v in labels)),
        "parse_state": parse_state,
        "visible_to_lane5": True,
        "classification_is_visibility_filter": False,
        "closure_state": "DISCOVERED_UNCLASSIFIED",
        "execution_state": "UNRESOLVED_BY_VISIBILITY_LAYER",
        "validation_state": "UNRESOLVED_BY_VISIBILITY_LAYER",
        "admission_state": "NOT_GRANTED_BY_VISIBILITY_LAYER",
        "candidate_only": True,
        "direct_linux_or_service_bypass_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_mint_authority": False,
        "canonical_persistence_authority": False,
    }
    node_id_seed = {
        key: core[key]
        for key in ("source_state", "ref_name", "commit_sha", "source_path", "symbol", "symbol_kind", "line")
    }
    core["node_id"] = "capability-surface:" + sha256(
        _canonical(node_id_seed).encode("utf-8")
    ).hexdigest()
    core["hash216"] = _h216(
        "HHS-P219-LANE5-GLOBAL-CAPABILITY-VISIBILITY-NODE-1.76",
        core,
    )
    return core


def _nodes_for_path(
    root: Path,
    *,
    source_state: str,
    ref_name: str,
    commit_sha: str,
    path: str,
) -> list[dict[str, Any]]:
    text = _read_git_text(root, commit_sha, path)
    labels = _classification_labels(path, text)
    symbols, parse_state = _symbols(path, text)
    out = [
        _node(
            source_state=source_state,
            ref_name=ref_name,
            commit_sha=commit_sha,
            path=path,
            symbol="<source-file>",
            symbol_kind="SOURCE_FILE",
            line=1,
            labels=labels,
            parse_state=parse_state,
        )
    ]
    for symbol, kind, line in symbols:
        out.append(
            _node(
                source_state=source_state,
                ref_name=ref_name,
                commit_sha=commit_sha,
                path=path,
                symbol=symbol,
                symbol_kind=kind,
                line=line,
                labels=labels,
                parse_state=parse_state,
            )
        )
    return out


def _tracked_source_paths(root: Path, commit: str) -> list[str]:
    return sorted(
        path.strip()
        for path in _git(root, "ls-tree", "-r", "--name-only", commit).splitlines()
        if path.strip() and _source_path(path.strip())
    )


def _ref_kind(ref_name: str) -> str:
    if ref_name.startswith("refs/pull/") and ref_name.endswith("/head"):
        return "PR_HEAD"
    if ref_name.startswith("refs/remotes/"):
        return "REMOTE_BRANCH_HEAD"
    if ref_name.startswith("refs/heads/"):
        return "LOCAL_BRANCH_HEAD"
    return "OTHER_GIT_REF"


def discover_repository_refs(root: str | Path) -> list[dict[str, str]]:
    repo = Path(root).resolve()
    raw = _git_optional(
        repo,
        "for-each-ref",
        "--format=%(refname)%00%(objectname)",
        "refs/heads",
        "refs/remotes/origin",
        "refs/remotes/pull",
    )
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for line in raw.splitlines():
        if "\x00" not in line:
            continue
        ref_name, commit_sha = line.split("\x00", 1)
        ref_name, commit_sha = ref_name.strip(), commit_sha.strip()
        if not ref_name or not commit_sha or ref_name.endswith("/HEAD"):
            continue
        key = (ref_name, commit_sha)
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "ref_name": ref_name,
                "commit_sha": commit_sha,
                "source_state": _ref_kind(ref_name),
            }
        )
    return sorted(rows, key=lambda row: (row["ref_name"], row["commit_sha"]))


def _changed_source_paths(
    root: Path,
    *,
    base_commit: str,
    commit_sha: str,
) -> list[str]:
    if base_commit == commit_sha:
        return []
    merge_base = _git_optional(root, "merge-base", base_commit, commit_sha).strip()
    if not merge_base:
        return _tracked_source_paths(root, commit_sha)
    raw = _git_optional(root, "diff", "--name-only", merge_base, commit_sha)
    return sorted(
        {
            path.strip()
            for path in raw.splitlines()
            if path.strip() and _source_path(path.strip())
        }
    )


def build_global_capability_visibility(
    repository_root: str | Path,
    *,
    main_ref: str = "HEAD",
    include_refs: bool = True,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    main_commit = _git(root, "rev-parse", main_ref).strip()
    if not main_commit:
        raise Pass219Lane5GlobalCapabilityVisibilityError("main commit unavailable")

    nodes: list[dict[str, Any]] = []
    for path in _tracked_source_paths(root, main_commit):
        nodes.extend(
            _nodes_for_path(
                root,
                source_state="MAIN_TRACKED",
                ref_name=main_ref,
                commit_sha=main_commit,
                path=path,
            )
        )

    ref_inventory = discover_repository_refs(root) if include_refs else []
    for ref in ref_inventory:
        if ref["commit_sha"] == main_commit:
            continue
        for path in _changed_source_paths(
            root,
            base_commit=main_commit,
            commit_sha=ref["commit_sha"],
        ):
            nodes.extend(
                _nodes_for_path(
                    root,
                    source_state=ref["source_state"],
                    ref_name=ref["ref_name"],
                    commit_sha=ref["commit_sha"],
                    path=path,
                )
            )

    unique: dict[str, dict[str, Any]] = {}
    for node in nodes:
        node_id = str(node["node_id"])
        prior = unique.get(node_id)
        if prior is not None and prior != node:
            raise Pass219Lane5GlobalCapabilityVisibilityError(
                f"capability node collision: {node_id}"
            )
        unique[node_id] = node
    nodes = [unique[key] for key in sorted(unique)]

    if any(node.get("visible_to_lane5") is not True for node in nodes):
        raise Pass219Lane5GlobalCapabilityVisibilityError(
            "discovered capability was hidden from Lane 5"
        )
    if any(node.get("classification_is_visibility_filter") is not False for node in nodes):
        raise Pass219Lane5GlobalCapabilityVisibilityError(
            "classification metadata became a visibility filter"
        )
    forbidden_authority = (
        "direct_linux_or_service_bypass_authority",
        "canonical_vm81_mutation_authority",
        "canonical_hash72_mint_authority",
        "canonical_hash216_mint_authority",
        "canonical_persistence_authority",
    )
    if any(bool(node.get(field)) for node in nodes for field in forbidden_authority):
        raise Pass219Lane5GlobalCapabilityVisibilityError(
            "visibility discovery attempted authority escalation"
        )

    counts_by_state: dict[str, int] = {}
    classification_counts: dict[str, int] = {}
    for node in nodes:
        state = str(node["source_state"])
        counts_by_state[state] = counts_by_state.get(state, 0) + 1
        for label in node["classification_labels"]:
            classification_counts[str(label)] = classification_counts.get(str(label), 0) + 1

    node_root = _h216(
        "HHS-P219-LANE5-GLOBAL-CAPABILITY-VISIBILITY-NODE-ROOT-1.76",
        [node["hash216"] for node in nodes],
    )
    core = {
        "schema": SCHEMA,
        "version": 1,
        "main_ref": main_ref,
        "main_commit": main_commit,
        "include_refs": bool(include_refs),
        "ref_inventory": ref_inventory,
        "counts": {
            "nodes": len(nodes),
            "source_states": counts_by_state,
            "classification_labels": classification_counts,
        },
        "invariants": {
            "all_discovered_capabilities_visible_to_lane5": True,
            "classification_metadata_never_filters_visibility": True,
            "unresolved_state_remains_visible": True,
            "discovery_imports_or_executes_discovered_code": False,
            "visibility_implies_execution_authority": False,
            "visibility_implies_validation": False,
            "visibility_implies_admission": False,
            "visibility_implies_canonical_mutation": False,
        },
        "authority": {
            "candidate_only": True,
            "direct_linux_or_service_bypass_authority": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_mint_authority": False,
            "canonical_hash216_mint_authority": False,
            "canonical_persistence_authority": False,
            "runtime_validation_required_after_lane5_composition": True,
        },
        "node_root_hash216": node_root,
        "nodes": nodes,
    }
    core["snapshot_root_hash216"] = _h216(
        "HHS-P219-LANE5-GLOBAL-CAPABILITY-VISIBILITY-SNAPSHOT-1.76",
        {
            "main_commit": main_commit,
            "node_root_hash216": node_root,
            "counts": core["counts"],
            "invariants": core["invariants"],
            "authority": core["authority"],
        },
    )
    return core


def hydrate_hash216_vector_database(
    snapshot: Mapping[str, Any],
    database_path: str | Path,
) -> dict[str, Any]:
    _reject_float(snapshot)
    if snapshot.get("schema") != SCHEMA:
        raise Pass219Lane5GlobalCapabilityVisibilityError("snapshot schema mismatch")
    nodes = snapshot.get("nodes")
    if not isinstance(nodes, list):
        raise Pass219Lane5GlobalCapabilityVisibilityError("snapshot nodes missing")

    target = Path(database_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target)
    try:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute(
            "CREATE TABLE IF NOT EXISTS capability_nodes ("
            "node_id TEXT PRIMARY KEY, hash216 TEXT NOT NULL UNIQUE, payload_json TEXT NOT NULL)"
        )
        connection.execute(
            "CREATE TABLE IF NOT EXISTS hash216_vectors ("
            "node_id TEXT NOT NULL, position INTEGER NOT NULL, glyph TEXT NOT NULL, "
            "glyph_sha256 TEXT NOT NULL, PRIMARY KEY(node_id, position))"
        )
        connection.execute("BEGIN IMMEDIATE")
        for node in nodes:
            if not isinstance(node, Mapping):
                raise Pass219Lane5GlobalCapabilityVisibilityError("invalid node row")
            node_id = str(node["node_id"])
            identity = str(node["hash216"])
            if len(identity) != HASH216_CHARS:
                raise Pass219Lane5GlobalCapabilityVisibilityError("Hash216 width drift")
            payload = _canonical(dict(node))
            connection.execute(
                "INSERT OR REPLACE INTO capability_nodes(node_id, hash216, payload_json) VALUES(?,?,?)",
                (node_id, identity, payload),
            )
            connection.execute(
                "DELETE FROM hash216_vectors WHERE node_id=?",
                (node_id,),
            )
            connection.executemany(
                "INSERT INTO hash216_vectors(node_id, position, glyph, glyph_sha256) VALUES(?,?,?,?)",
                (
                    (node_id, position, glyph, sha256(glyph.encode("utf-8")).hexdigest())
                    for position, glyph in enumerate(identity)
                ),
            )
        connection.commit()
        node_count = int(
            connection.execute("SELECT COUNT(*) FROM capability_nodes").fetchone()[0]
        )
        vector_count = int(
            connection.execute("SELECT COUNT(*) FROM hash216_vectors").fetchone()[0]
        )
    finally:
        connection.close()

    expected_vectors = node_count * HASH216_CHARS
    if vector_count != expected_vectors:
        raise Pass219Lane5GlobalCapabilityVisibilityError(
            f"Hash216 vector count mismatch: {vector_count} != {expected_vectors}"
        )
    return {
        "schema": DB_SCHEMA,
        "database_path": str(target),
        "node_count": node_count,
        "hash216_vector_positions": vector_count,
        "expected_hash216_vector_positions": expected_vectors,
        "snapshot_root_hash216": str(snapshot["snapshot_root_hash216"]),
        "candidate_only": True,
        "canonical_persistence_authority": False,
        "restart_rehydratable": True,
    }


def build_and_hydrate_global_capability_visibility(
    repository_root: str | Path,
    state_root: str | Path,
    *,
    main_ref: str = "HEAD",
    include_refs: bool = True,
) -> dict[str, Any]:
    snapshot = build_global_capability_visibility(
        repository_root,
        main_ref=main_ref,
        include_refs=include_refs,
    )
    receipt = hydrate_hash216_vector_database(
        snapshot,
        Path(state_root) / "lane5-global-capability-visibility-1.76.sqlite3",
    )
    return {
        "schema": SCHEMA + "_HYDRATION_RECEIPT",
        "snapshot": snapshot,
        "database": receipt,
        "ok": True,
    }


def _summary(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": str(snapshot["schema"]),
        "main_commit": str(snapshot["main_commit"]),
        "counts": dict(snapshot["counts"]),
        "node_root_hash216": str(snapshot["node_root_hash216"]),
        "snapshot_root_hash216": str(snapshot["snapshot_root_hash216"]),
        "invariants": dict(snapshot["invariants"]),
        "authority": dict(snapshot["authority"]),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--state-root")
    parser.add_argument("--main-ref", default="HEAD")
    parser.add_argument("--without-refs", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    snapshot = build_global_capability_visibility(
        args.repository_root,
        main_ref=args.main_ref,
        include_refs=not args.without_refs,
    )
    result: dict[str, Any] = {"snapshot": _summary(snapshot)}
    if args.state_root:
        result["database"] = hydrate_hash216_vector_database(
            snapshot,
            Path(args.state_root) / "lane5-global-capability-visibility-1.76.sqlite3",
        )
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
