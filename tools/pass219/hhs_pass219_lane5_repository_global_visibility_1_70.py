#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hhs_backend.runtime.hhs_pass219_lane5_repository_capability_reverse_discovery_1_44 import (  # noqa: E402
    build_repository_capability_reverse_discovery,
)
from hhs_backend.runtime.hhs_pass219_lane5_repository_global_visibility_1_70 import (  # noqa: E402
    Lane5RepositoryGlobalVisibilityDatabase,
    build_repository_global_visibility_graph,
    discover_local_ref_provenance,
)
from hhs_runtime.pass191.repository_hydration import _hash216  # noqa: E402


LANGUAGE_BY_SUFFIX = {
    ".py": "python", ".pyi": "python",
    ".c": "c", ".h": "c_header", ".cc": "cpp", ".cpp": "cpp",
    ".cxx": "cpp", ".hpp": "cpp_header", ".hh": "cpp_header",
    ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".jsx": "javascript", ".ts": "typescript", ".tsx": "typescript",
    ".sh": "shell", ".bash": "shell", ".zsh": "shell",
    ".md": "documentation", ".rst": "documentation", ".adoc": "documentation",
    ".json": "json", ".yaml": "yaml", ".yml": "yaml", ".toml": "toml",
}


def _git(root: Path, *args: str, binary: bool = False):
    result = subprocess.check_output(
        ["git", "-C", str(root), *args],
        stderr=subprocess.DEVNULL,
    )
    return result if binary else result.decode("utf-8", "surrogateescape").strip()


def _language(path: str) -> str:
    return LANGUAGE_BY_SUFFIX.get(PurePosixPath(path).suffix.lower(), "other")


def build_bound_repository_source_graph(root: Path) -> dict[str, Any]:
    raw = _git(root, "ls-files", "-s", "-z", binary=True)
    entries: list[tuple[str, str, str]] = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        prefix, encoded_path = record.split(b"\t", 1)
        mode, blob, _stage = prefix.decode("ascii").split()
        path = encoded_path.decode("utf-8", "surrogateescape")
        entries.append((path, mode, blob))

    files: list[dict[str, Any]] = []
    for path, mode, blob in sorted(entries):
        target = root / path
        try:
            size = target.stat().st_size
        except OSError:
            size = None
        body = {
            "path": path,
            "mode": mode,
            "git_blob": blob,
            "size_bytes": size,
            "language": _language(path),
            "disposition": "TRACKED",
            "origin": "REPOSITORY",
        }
        files.append({
            **body,
            "hash216": _hash216("HHS-REPOSITORY-INDEX-FILE-V1", body),
        })

    commit = str(_git(root, "rev-parse", "HEAD"))
    tree = str(_git(root, "rev-parse", "HEAD^{tree}"))
    file_root = _hash216(
        "HHS-P219-LANE5-GLOBAL-VISIBILITY-BOUND-FILE-ROOT-1.70",
        [row["hash216"] for row in files],
    )
    graph_root = _hash216(
        "HHS-P219-LANE5-GLOBAL-VISIBILITY-BOUND-SOURCE-GRAPH-1.70",
        {"commit": commit, "tree": tree, "file_root_hash216": file_root},
    )
    return {
        "schema": "HHS_PASS_219_LANE5_GLOBAL_VISIBILITY_BOUND_SOURCE_GRAPH_1_70",
        "source_commit": commit,
        "source_tree": tree,
        "counts": {
            "tracked_files": len(files),
            "file_dependency_edges": 0,
        },
        "roots": {
            "file_root_hash216": file_root,
            "graph_root_hash216": graph_root,
        },
        "files": files,
        "dependency_edges": [],
    }


def _load_provenance(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = payload.get("provenance")
    if not isinstance(payload, list):
        raise ValueError("provenance JSON must be a list or contain a provenance list")
    records: list[dict[str, Any]] = []
    for row in payload:
        if not isinstance(row, dict):
            raise ValueError("provenance entries must be objects")
        records.append(dict(row))
    return records


def _merge_provenance(
    observed: list[dict[str, Any]],
    supplied: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    keyed: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in observed + supplied:
        key = (
            str(row.get("ref_kind", "")).upper(),
            str(row.get("ref_name", "")),
            str(row.get("head_sha", "")),
        )
        previous = keyed.get(key, {})
        merged = {**previous, **row}
        previous_metadata = dict(previous.get("declared_metadata") or {})
        previous_metadata.update(dict(row.get("declared_metadata") or {}))
        if previous_metadata:
            merged["declared_metadata"] = previous_metadata
        keyed[key] = merged
    return [keyed[key] for key in sorted(keyed)]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Hydrate the bound repository and supplied/fetched ref provenance into "
            "the Pass219 Lane5 1.70 global visibility Hash216 graph."
        )
    )
    parser.add_argument("--repository-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--provenance-json", type=Path)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--receipt-json", type=Path, required=True)
    args = parser.parse_args()

    root = args.repository_root.resolve()
    dependency_graph = build_bound_repository_source_graph(root)
    lane5 = build_repository_capability_reverse_discovery(root)
    provenance = _merge_provenance(
        discover_local_ref_provenance(root),
        _load_provenance(args.provenance_json),
    )
    projection = build_repository_global_visibility_graph(
        root,
        dependency_graph,
        lane5_snapshot=lane5,
        provenance_records=provenance,
    )

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.database.parent.mkdir(parents=True, exist_ok=True)
    args.receipt_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(projection, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    with Lane5RepositoryGlobalVisibilityDatabase(args.database) as database:
        status = database.hydrate(projection)
    status.pop("database_path", None)

    receipt = {
        "schema": "HHS_PASS_219_LANE5_REPOSITORY_GLOBAL_VISIBILITY_RECEIPT_1_70",
        "source_commit": projection["source_commit"],
        "source_tree": projection["source_tree"],
        "projection_root_hash216": projection["roots"]["projection_root_hash216"],
        "counts": projection["counts"],
        "scope": projection["scope"],
        "authority": projection["authority"],
        "database_status": status,
        "provenance_records_supplied_or_observed": len(provenance),
        "external_ref_content_executed": False,
    }
    args.receipt_json.write_text(
        json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "source_commit": projection["source_commit"],
        "tracked_repository_objects": projection["counts"]["repository_objects"],
        "typed_capabilities": projection["counts"]["typed_capabilities"],
        "typed_constructors": projection["counts"]["typed_constructors"],
        "discovered_callables": projection["counts"]["discovered_callables"],
        "provenance_nodes": projection["counts"]["provenance_nodes"],
        "visibility_nodes": projection["counts"]["visibility_nodes"],
        "visibility_edges": projection["counts"]["visibility_edges"],
        "projection_root_hash216": projection["roots"]["projection_root_hash216"],
        "visibility_filtering_allowed": projection["authority"]["visibility_filtering_allowed"],
        "external_ref_content_executed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
