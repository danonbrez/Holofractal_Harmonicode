"""Pass 219 Lane 5 repository-global capability visibility successor 1.76.

This successor does not replace or rewrite frozen 1.44/1.69 evidence.
It binds their exact repository snapshot into the stronger Pass 219 invariant:

    discover -> preserve -> hydrate -> compose -> runtime validate

Classification markers are metadata. They never remove an object from Lane 5
visibility and never create a second execution or mutation authority.

The projection is read-only discovery evidence. Executable capability paths
remain eligible for Lane 5 composition and still require the inherited
Pass 219 C++ RNA / signed environmental VM81 runtime validation boundary.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import sqlite3
from typing import Any, Iterable, Mapping, Sequence

from hhs_runtime.pass191.repository_hydration import _hash216

SCHEMA = "HHS_PASS_219_LANE5_REPOSITORY_GLOBAL_CAPABILITY_VISIBILITY_1_76"
DB_SCHEMA = "HHS_PASS_219_LANE5_REPOSITORY_GLOBAL_CAPABILITY_VISIBILITY_DB_1_76"

SOURCE_LIKE_SUFFIXES = {
    ".py", ".pyi", ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".hh",
    ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".sh", ".bash", ".zsh",
    ".ps1", ".rs", ".go", ".java", ".kt", ".kts", ".swift", ".sql",
    ".glsl", ".wgsl", ".vert", ".frag", ".harmonicode",
}
DECLARATIVE_SUFFIXES = {
    ".json", ".jsonl", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".xml",
    ".proto", ".graphql", ".gql",
}
DOCUMENT_SUFFIXES = {".md", ".rst", ".adoc", ".txt"}

_MARKERS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("DEMO", re.compile(r"(?i)(?:^|[^a-z0-9])demo(?:[^a-z0-9]|$)")),
    ("EXAMPLE", re.compile(r"(?i)(?:^|[^a-z0-9])example(?:[^a-z0-9]|$)")),
    ("REFERENCE", re.compile(r"(?i)(?:^|[^a-z0-9])reference(?:[^a-z0-9]|$)")),
    ("CANDIDATE_ONLY", re.compile(r"(?i)candidate[_ -]?only")),
    ("DISABLED_HINT", re.compile(r"(?i)(?:enabled\s*[:=]\s*false|disabled\s*[:=]\s*true|not[_ -]?enabled)")),
    ("NOT_READY_HINT", re.compile(r"(?i)(?:ready\s*[:=]\s*false|not[_ -]?ready)")),
    ("ADAPTER_HINT", re.compile(r"(?i)(?:needs?|requires?)[_ -]?(?:an?[_ -]?)?adapter")),
    ("CONFIGURATION_HINT", re.compile(r"(?i)(?:needs?|requires?)[_ -]?(?:configuration|config)")),
    ("DEPRECATED_HINT", re.compile(r"(?i)(?:^|[^a-z0-9])deprecated(?:[^a-z0-9]|$)")),
)

_RUNTIME_ROOT_PREFIXES = (
    "hhs_runtime/",
    "hhs_backend/",
    "hhs_gui/",
    "applications/",
    "apps/",
    "native_projects/",
    "python/",
    "sdk/",
    "tools/",
    "scripts/",
    "deployment/",
)


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise ValueError(f"floating-point visibility metadata forbidden at {path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _canon(value: Any) -> str:
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
    if not isinstance(value, str) or len(value) != 216:
        raise ValueError(f"{domain} did not produce a 216-character Hash216 identity")
    return value


def _files(dependency_graph: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = dependency_graph.get("files")
    if not isinstance(rows, list) or not rows:
        raise ValueError("dependency graph files missing")
    seen: set[str] = set()
    out: list[Mapping[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("repository file row must be a mapping")
        path = str(row.get("path", ""))
        identity = str(row.get("hash216", ""))
        if not path or path in seen or len(identity) != 216:
            raise ValueError("invalid or duplicate repository file identity")
        seen.add(path)
        out.append(row)
    return sorted(out, key=lambda item: str(item["path"]))


def _read_marker_text(repo_root: Path, path: str, size: object) -> str:
    try:
        if size is not None and int(size) > 2 * 1024 * 1024:
            return ""
    except (TypeError, ValueError):
        return ""
    target = (repo_root / path).resolve()
    try:
        target.relative_to(repo_root)
        raw = target.read_bytes()
    except (OSError, ValueError):
        return ""
    if b"\0" in raw:
        return ""
    return raw.decode("utf-8", "surrogateescape")


def _markers(path: str, text: str) -> list[str]:
    sample = f"{path}\n{text}"
    return sorted(name for name, pattern in _MARKERS if pattern.search(sample))


def _object_class(path: str) -> str:
    suffix = PurePosixPath(path).suffix.lower()
    if path.startswith(".github/workflows/"):
        return "WORKFLOW_CAPABILITY_EVIDENCE"
    if suffix in SOURCE_LIKE_SUFFIXES:
        return "EXECUTABLE_SOURCE_CAPABILITY_EVIDENCE"
    if suffix in DECLARATIVE_SUFFIXES:
        return "DECLARATIVE_CAPABILITY_EVIDENCE"
    if suffix in DOCUMENT_SUFFIXES:
        return "DOCUMENTED_CAPABILITY_EVIDENCE"
    if path.startswith(_RUNTIME_ROOT_PREFIXES):
        return "RUNTIME_REPOSITORY_OBJECT_EVIDENCE"
    return "REPOSITORY_OBJECT_EVIDENCE"


def _execution_eligibility(object_class: str) -> str:
    if object_class in {
        "EXECUTABLE_SOURCE_CAPABILITY_EVIDENCE",
        "WORKFLOW_CAPABILITY_EVIDENCE",
        "RUNTIME_REPOSITORY_OBJECT_EVIDENCE",
    }:
        return "LANE5_COMPOSITION_CANDIDATE_REQUIRES_RUNTIME_VALIDATION"
    if object_class == "DECLARATIVE_CAPABILITY_EVIDENCE":
        return "DECLARATIVE_INPUT_TO_LANE5_COMPOSITION"
    return "KNOWLEDGE_EVIDENCE_VISIBLE_TO_LANE5"


def _visibility_record(repo_root: Path, row: Mapping[str, Any]) -> dict[str, Any]:
    path = str(row["path"])
    text = _read_marker_text(repo_root, path, row.get("size_bytes"))
    object_class = _object_class(path)
    body = {
        "record_id": f"repository-object:{path}",
        "record_kind": "REPOSITORY_VISIBILITY",
        "path": path,
        "source_file_hash216": str(row["hash216"]),
        "git_blob": str(row.get("git_blob", "")),
        "language": str(row.get("language", "")),
        "disposition": str(row.get("disposition", "")),
        "origin": str(row.get("origin", "")),
        "object_class": object_class,
        "classification_markers": _markers(path, text),
        "lane5_visible": True,
        "visibility_filtered": False,
        "classification_is_metadata_only": True,
        "execution_eligibility": _execution_eligibility(object_class),
        "runtime_validation_required": True,
        "direct_linux_kernel_bypass_authority": False,
        "direct_service_bypass_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
    }
    body["hash216"] = _h216(
        "HHS-P219-LANE5-REPOSITORY-GLOBAL-VISIBILITY-OBJECT-1.76", body
    )
    return body


def _normalize_ref_record(raw: Mapping[str, Any]) -> dict[str, Any]:
    name = str(raw.get("name", "")).strip()
    sha = str(raw.get("sha", "")).strip()
    kind = str(raw.get("kind", "")).strip().upper() or "UNKNOWN_REF"
    if not name or not re.fullmatch(r"[0-9a-fA-F]{40}", sha):
        raise ValueError("reference inventory entry requires name and 40-hex SHA")
    changed_paths = raw.get("changed_paths", [])
    if changed_paths is None:
        changed_paths = []
    if not isinstance(changed_paths, list) or any(not isinstance(item, str) for item in changed_paths):
        raise ValueError("reference changed_paths must be a string list")
    body = {
        "record_id": f"repository-ref:{kind}:{name}",
        "record_kind": "REPOSITORY_REFERENCE_VISIBILITY",
        "reference_kind": kind,
        "reference_name": name,
        "head_sha": sha.lower(),
        "pull_request_number": (
            int(raw["pull_request_number"])
            if raw.get("pull_request_number") is not None
            else None
        ),
        "draft": (
            bool(raw["draft"])
            if raw.get("draft") is not None
            else None
        ),
        "validation_state": str(raw.get("validation_state", "UNRESOLVED")),
        "merge_state": str(raw.get("merge_state", "UNRESOLVED")),
        "changed_paths": sorted(set(changed_paths)),
        "lane5_visible": True,
        "visibility_filtered": False,
        "classification_is_metadata_only": True,
        "execution_eligibility": "REFERENCE_CAPABILITY_EVIDENCE_REQUIRES_RUNTIME_VALIDATION",
        "runtime_validation_required": True,
        "branch_or_pr_code_executed_during_discovery": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
    }
    body["hash216"] = _h216(
        "HHS-P219-LANE5-REPOSITORY-GLOBAL-VISIBILITY-REF-1.76", body
    )
    return body


def build_repository_global_capability_visibility(
    repo_root: str | Path,
    dependency_graph: Mapping[str, Any],
    *,
    lane5_snapshot: Mapping[str, Any],
    reference_inventory: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    files = _files(dependency_graph)
    source_root = str(dependency_graph.get("roots", {}).get("graph_root_hash216", ""))
    if len(source_root) != 216:
        raise ValueError("dependency graph missing graph_root_hash216")

    raw_nodes = lane5_snapshot.get("nodes")
    if not isinstance(raw_nodes, list) or not raw_nodes:
        raise ValueError("Lane 5 reverse-discovery snapshot empty")
    if int(lane5_snapshot.get("counts", {}).get("canonical_boundaries", -1)) != 1:
        raise ValueError("Lane 5 snapshot must preserve one canonical admission boundary")
    receipt = lane5_snapshot.get("native_receipt")
    if not isinstance(receipt, Mapping) or receipt.get("accepted") is not True:
        raise ValueError("Lane 5 reverse-discovery native receipt not accepted")

    visibility_records = [_visibility_record(root, row) for row in files]
    reference_records = sorted(
        (_normalize_ref_record(item) for item in reference_inventory),
        key=lambda item: str(item["record_id"]),
    )

    known_capability_ids = sorted(
        str(node.get("node_id"))
        for node in raw_nodes
        if isinstance(node, Mapping) and node.get("node_id")
    )
    if len(known_capability_ids) != len(set(known_capability_ids)):
        raise ValueError("duplicate inherited Lane 5 capability node identity")

    inherited_capability_bindings: list[dict[str, Any]] = []
    file_paths = {str(row["path"]) for row in files}
    for raw in raw_nodes:
        if not isinstance(raw, Mapping):
            continue
        path = str(raw.get("path") or raw.get("declaring_header") or "")
        if not path or path not in file_paths:
            continue
        body = {
            "edge_kind": "INHERITED_CAPABILITY_VISIBLE_IN_REPOSITORY_OBJECT",
            "capability_node_id": str(raw["node_id"]),
            "source_path": path,
            "lane5_visible": True,
            "visibility_filtered": False,
            "authority_class": int(raw.get("authority_class", 0)),
            "source_kind": str(raw.get("source_kind", "")),
            "runtime_validation_required": True,
            "classification_is_metadata_only": True,
        }
        body["hash216"] = _h216(
            "HHS-P219-LANE5-REPOSITORY-GLOBAL-VISIBILITY-BINDING-1.76", body
        )
        inherited_capability_bindings.append(body)
    inherited_capability_bindings.sort(
        key=lambda item: (str(item["source_path"]), str(item["capability_node_id"]))
    )

    all_record_hashes = (
        [str(item["hash216"]) for item in visibility_records]
        + [str(item["hash216"]) for item in reference_records]
        + [str(item["hash216"]) for item in inherited_capability_bindings]
    )
    if len(all_record_hashes) != len(set(all_record_hashes)):
        raise ValueError("global visibility Hash216 collision")

    counts = {
        "repository_objects_visible": len(visibility_records),
        "reference_objects_visible": len(reference_records),
        "inherited_lane5_capability_nodes": len(known_capability_ids),
        "inherited_capability_bindings": len(inherited_capability_bindings),
        "visibility_filtered_objects": sum(
            1 for item in visibility_records + reference_records
            if item.get("visibility_filtered") is True
        ),
        "objects_with_classification_markers": sum(
            1 for item in visibility_records if item["classification_markers"]
        ),
    }
    roots = {
        "repository_visibility_root_hash216": _h216(
            "HHS-P219-LANE5-REPOSITORY-GLOBAL-VISIBILITY-OBJECT-ROOT-1.76",
            [item["hash216"] for item in visibility_records],
        ),
        "reference_visibility_root_hash216": _h216(
            "HHS-P219-LANE5-REPOSITORY-GLOBAL-VISIBILITY-REF-ROOT-1.76",
            [item["hash216"] for item in reference_records],
        ),
        "inherited_capability_binding_root_hash216": _h216(
            "HHS-P219-LANE5-REPOSITORY-GLOBAL-VISIBILITY-BINDING-ROOT-1.76",
            [item["hash216"] for item in inherited_capability_bindings],
        ),
    }

    authority = {
        "lane5_is_pass219_composition_manifold": True,
        "global_repository_visibility": True,
        "classification_is_metadata_not_visibility_filter": True,
        "unresolved_objects_remain_visible": True,
        "default_executable_source_state_requires_runtime_validation": True,
        "graph_execution_authority": False,
        "direct_linux_kernel_bypass_authority": False,
        "direct_service_bypass_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "signed_environmental_vm81_admission_required_for_mutation": True,
    }
    core = {
        "schema": SCHEMA,
        "version": "1.76",
        "source_dependency_graph_root_hash216": source_root,
        "source_lane5_model_root_sha256": str(lane5_snapshot.get("model_root_sha256", "")),
        "counts": counts,
        "roots": roots,
        "authority": authority,
        "repository_visibility": visibility_records,
        "reference_visibility": reference_records,
        "inherited_capability_bindings": inherited_capability_bindings,
    }
    roots["projection_root_hash216"] = _h216(
        "HHS-P219-LANE5-REPOSITORY-GLOBAL-CAPABILITY-VISIBILITY-ROOT-1.76",
        {
            "source_dependency_graph_root_hash216": source_root,
            "source_lane5_model_root_sha256": core["source_lane5_model_root_sha256"],
            "counts": counts,
            "roots": dict(roots),
            "authority": authority,
        },
    )

    if counts["visibility_filtered_objects"] != 0:
        raise ValueError("repository object was removed from Lane 5 visibility")
    return core


class Lane5RepositoryGlobalVisibilityDatabase:
    """Restartable Hash216 vector projection for 1.76 visibility records."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.db = sqlite3.connect(self.database_path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS visibility_records(
                record_id TEXT PRIMARY KEY,
                record_kind TEXT NOT NULL,
                record_hash216 TEXT NOT NULL UNIQUE,
                source_path TEXT,
                payload_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS hash216_positions(
                record_hash216 TEXT NOT NULL,
                record_kind TEXT NOT NULL,
                ordinal INTEGER NOT NULL,
                lane INTEGER NOT NULL,
                lane_offset INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                symbol_sha256 TEXT NOT NULL,
                PRIMARY KEY(record_hash216, ordinal)
            );
            CREATE TABLE IF NOT EXISTS hydration_metadata(
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )

    def __enter__(self) -> "Lane5RepositoryGlobalVisibilityDatabase":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.db.close()

    @staticmethod
    def _positions(identity: str, kind: str) -> Iterable[tuple[object, ...]]:
        if len(identity) != 216:
            raise ValueError("Hash216 position index requires 216 characters")
        for ordinal, symbol in enumerate(identity):
            yield (
                identity,
                kind,
                ordinal,
                ordinal // 72,
                ordinal % 72,
                symbol,
                sha256(symbol.encode("utf-8")).hexdigest(),
            )

    def hydrate(self, projection: Mapping[str, Any]) -> dict[str, Any]:
        if projection.get("schema") != SCHEMA:
            raise ValueError("global visibility projection schema mismatch")
        authority = projection.get("authority")
        if not isinstance(authority, Mapping):
            raise ValueError("global visibility authority missing")
        if authority.get("global_repository_visibility") is not True:
            raise ValueError("global repository visibility disabled")
        if authority.get("classification_is_metadata_not_visibility_filter") is not True:
            raise ValueError("classification incorrectly controls visibility")
        forbidden = (
            "graph_execution_authority",
            "direct_linux_kernel_bypass_authority",
            "direct_service_bypass_authority",
            "canonical_vm81_mutation_authority",
            "canonical_hash72_authority",
            "canonical_hash216_authority",
            "canonical_persistence_authority",
        )
        if any(authority.get(key) is not False for key in forbidden):
            raise ValueError("global visibility authority escalation")

        records = (
            list(projection.get("repository_visibility", []))
            + list(projection.get("reference_visibility", []))
        )
        bindings = list(projection.get("inherited_capability_bindings", []))
        all_rows = records + [
            {
                "record_id": f"capability-binding:{item['capability_node_id']}:{item['source_path']}",
                "record_kind": "INHERITED_CAPABILITY_BINDING",
                "path": item["source_path"],
                "hash216": item["hash216"],
                **item,
            }
            for item in bindings
        ]
        if any(item.get("lane5_visible") is not True for item in records):
            raise ValueError("invisible repository/ref record in global visibility projection")
        with self.db:
            self.db.execute("DELETE FROM hash216_positions")
            self.db.execute("DELETE FROM visibility_records")
            self.db.execute("DELETE FROM hydration_metadata")
            for item in all_rows:
                identity = str(item["hash216"])
                record_kind = str(item.get("record_kind") or item.get("edge_kind") or "")
                source_path = item.get("path") or item.get("source_path")
                self.db.execute(
                    "INSERT INTO visibility_records VALUES(?,?,?,?,?)",
                    (
                        str(item["record_id"]),
                        record_kind,
                        identity,
                        source_path,
                        _canon(item),
                    ),
                )
                self.db.executemany(
                    "INSERT INTO hash216_positions VALUES(?,?,?,?,?,?,?)",
                    self._positions(identity, record_kind),
                )
            metadata = {
                "schema": DB_SCHEMA,
                "projection_root_hash216": str(projection["roots"]["projection_root_hash216"]),
                "global_repository_visibility": "true",
                "classification_is_metadata_not_visibility_filter": "true",
                "runtime_validation_required": "true",
                "restart_rehydratable": "true",
            }
            self.db.executemany(
                "INSERT INTO hydration_metadata VALUES(?,?)", sorted(metadata.items())
            )
        return self.status()

    def status(self) -> dict[str, Any]:
        count = int(self.db.execute("SELECT COUNT(*) FROM visibility_records").fetchone()[0])
        positions = int(self.db.execute("SELECT COUNT(*) FROM hash216_positions").fetchone()[0])
        return {
            "schema": DB_SCHEMA,
            "visibility_records": count,
            "hash216_positions": positions,
            "global_repository_visibility": True,
            "classification_is_metadata_not_visibility_filter": True,
            "runtime_validation_required": True,
            "graph_execution_authority": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
            "canonical_persistence_authority": False,
            "restart_rehydratable": True,
        }

    def search(self, text: str, *, limit: int = 128) -> list[dict[str, Any]]:
        query = text.strip()
        if not query or limit <= 0 or limit > 1024:
            raise ValueError("invalid bounded global visibility search")
        like = f"%{query}%"
        rows = self.db.execute(
            """
            SELECT * FROM visibility_records
            WHERE record_id LIKE ? OR COALESCE(source_path,'') LIKE ? OR payload_json LIKE ?
            ORDER BY record_kind, record_id LIMIT ?
            """,
            (like, like, like, int(limit)),
        ).fetchall()
        return [
            {
                "record_id": str(row["record_id"]),
                "record_kind": str(row["record_kind"]),
                "hash216": str(row["record_hash216"]),
                "source_path": row["source_path"],
                "payload": json.loads(str(row["payload_json"])),
            }
            for row in rows
        ]


__all__ = [
    "SCHEMA",
    "DB_SCHEMA",
    "build_repository_global_capability_visibility",
    "Lane5RepositoryGlobalVisibilityDatabase",
]
