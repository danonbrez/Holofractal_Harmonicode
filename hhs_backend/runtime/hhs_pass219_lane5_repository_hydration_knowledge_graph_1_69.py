"""Pass 219 Lane 5 repository hydration knowledge graph 1.69.

Lifts the generated repository Hash216 file/dependency census into a first-class,
candidate-only capability/constructor knowledge graph and restartable SQLite
Hash216 database. This surface never mints canonical VM81/Hash72/Hash216 state.
"""
from __future__ import annotations

import ast
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import sqlite3
from typing import Any, Mapping, Sequence

from hhs_runtime.pass191.repository_hydration import _hash216

SCHEMA = "HHS_PASS_219_LANE5_REPOSITORY_HYDRATION_KNOWLEDGE_GRAPH_1_69"
DB_SCHEMA = "HHS_PASS_219_LANE5_REPOSITORY_HYDRATION_HASH216_DATABASE_1_69"
LANE5_REPOSITORY_KNOWLEDGE_OPERATIONS = (
    "lane5.repository_hydration_knowledge.status",
    "lane5.repository_hydration_knowledge.search",
    "lane5.repository_hydration_knowledge.neighbors",
)
FACTORY_PREFIXES = ("build_", "create_", "construct_", "hydrate_", "make_", "new_", "register_")
TEXT_SUFFIXES = {".py",".pyi",".c",".h",".cc",".cpp",".cxx",".hpp",".hh",".js",".mjs",".cjs",".jsx",".ts",".tsx",".md",".rst",".adoc",".json",".yaml",".yml",".toml",".harmonicode"}
FORMAL_SUFFIXES = {".md",".rst",".adoc",".json",".harmonicode"}
C_FACTORY = re.compile(r"(?m)^[ \t]*(?:[A-Za-z_][A-Za-z0-9_ \t*]+[ \t]+)([A-Za-z_][A-Za-z0-9_]*(?:build|create|construct|hydrate|init|make|new|register)[A-Za-z0-9_]*)[ \t]*\(")
JS_CLASS = re.compile(r"(?m)^\s*(?:export\s+)?class\s+([A-Za-z_$][A-Za-z0-9_$]*)")
JS_FACTORY = re.compile(r"(?m)^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][A-Za-z0-9_$]*(?:build|create|construct|hydrate|make|register)[A-Za-z0-9_$]*)\s*\(")
TOKENS = re.compile(r"[A-Za-z0-9]+")
IGNORE = {"hhs","pass","runtime","api","v","v1","v2","exact","lane","lane5"}


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise ValueError(f"floating-point knowledge metadata forbidden at {path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _canon(value: Any) -> str:
    _reject_float(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _h216(domain: str, payload: Any) -> str:
    value = _hash216(domain, payload)
    if not isinstance(value, str) or len(value) != 216:
        raise ValueError(f"{domain} did not produce a 216-character Hash216 identity")
    return value


def _tokens(*values: object) -> list[str]:
    found = set()
    for value in values:
        found.update(token for token in TOKENS.findall(str(value).lower()) if token not in IGNORE)
    return sorted(found)


def _files(graph: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    rows = graph.get("files")
    if not isinstance(rows, list):
        raise ValueError("dependency graph files missing")
    out = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("file row must be a mapping")
        path, identity = str(row.get("path", "")), str(row.get("hash216", ""))
        if not path or len(identity) != 216 or path in out:
            raise ValueError("invalid/duplicate file identity")
        out[path] = row
    return out


def _text(root: Path, path: str, size: object) -> str | None:
    if PurePosixPath(path).suffix.lower() not in TEXT_SUFFIXES:
        return None
    try:
        if size is not None and int(size) > 8 * 1024 * 1024:
            return None
    except (TypeError, ValueError):
        pass
    target = (root / path).resolve()
    try:
        target.relative_to(root)
        raw = target.read_bytes()
    except (OSError, ValueError):
        return None
    return None if b"\0" in raw else raw.decode("utf-8", "surrogateescape")


def _ctor(path: str, name: str, kind: str, language: str, line: int, symbol: str, evidence: Sequence[str]) -> dict[str, Any]:
    body = {
        "node_id": f"constructor:{kind.lower()}:{path}#{name}:{line}",
        "node_kind": "CONSTRUCTOR",
        "name": name,
        "constructor_kind": kind,
        "language": language,
        "source_path": path,
        "line": int(line),
        "symbol": symbol,
        "semantic_tokens": _tokens(name, symbol, path),
        "discovery_evidence": sorted(set(evidence)),
        "candidate_only": True,
        "execution_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "automatic_composition_promotion": False,
        "automatic_superedge_promotion": False,
    }
    body["hash216"] = _h216("HHS-P219-LANE5-REPOSITORY-KNOWLEDGE-CONSTRUCTOR-1.69", body)
    return body


def _line(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def discover_repository_constructors(repo_root: str | Path, dependency_graph: Mapping[str, Any]) -> list[dict[str, Any]]:
    root, files, found = Path(repo_root).resolve(), _files(dependency_graph), []
    for path, row in sorted(files.items()):
        suffix, text = PurePosixPath(path).suffix.lower(), _text(root, path, row.get("size_bytes"))
        if text is not None and suffix in {".py", ".pyi"}:
            try:
                tree = ast.parse(text, filename=path)
            except (SyntaxError, ValueError):
                tree = None
            if tree is not None:
                module = str(PurePosixPath(path).with_suffix("")).replace("/", ".")
                for node in tree.body:
                    if isinstance(node, ast.ClassDef):
                        factories = sorted(
                            child.name for child in node.body
                            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                            and (child.name == "__init__" or child.name.startswith("from_") or child.name.startswith(FACTORY_PREFIXES))
                        )
                        found.append(_ctor(path, node.name, "PYTHON_CLASS", "python", node.lineno, f"{module}.{node.name}", ("AST_CLASS_DEF", *factories)))
                    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(FACTORY_PREFIXES):
                        found.append(_ctor(path, node.name, "PYTHON_FACTORY_FUNCTION", "python", node.lineno, f"{module}.{node.name}", ("AST_TOP_LEVEL_FACTORY",)))
        elif text is not None and suffix in {".c",".h",".cc",".cpp",".cxx",".hpp",".hh"}:
            for match in C_FACTORY.finditer(text):
                found.append(_ctor(path, match.group(1), "C_CPP_FACTORY_OR_INITIALIZER", "c_cpp", _line(text, match.start()), match.group(1), ("C_CPP_CONSTRUCTOR_VERB_SYMBOL",)))
        elif text is not None and suffix in {".js",".mjs",".cjs",".jsx",".ts",".tsx"}:
            for match in JS_CLASS.finditer(text):
                found.append(_ctor(path, match.group(1), "JS_TS_CLASS", "js_ts", _line(text, match.start()), match.group(1), ("JS_TS_CLASS_DECLARATION",)))
            for match in JS_FACTORY.finditer(text):
                found.append(_ctor(path, match.group(1), "JS_TS_FACTORY_FUNCTION", "js_ts", _line(text, match.start()), match.group(1), ("JS_TS_FACTORY_DECLARATION",)))
        if "constructor" in path.lower() and suffix in FORMAL_SUFFIXES:
            found.append(_ctor(path, PurePosixPath(path).name, "FORMAL_CONSTRUCTOR_ARTIFACT", "formal_or_documentation", 1, path, ("CONSTRUCTOR_NAMED_REPOSITORY_ARTIFACT",)))
    unique = {}
    for node in found:
        node_id = str(node["node_id"])
        if node_id in unique and unique[node_id] != node:
            raise ValueError(f"constructor identity collision: {node_id}")
        unique[node_id] = node
    return [unique[key] for key in sorted(unique)]


def _capability(raw: Mapping[str, Any]) -> dict[str, Any]:
    raw_id = str(raw.get("node_id", ""))
    if not raw_id:
        raise ValueError("Lane 5 capability node missing node_id")
    name = next((str(raw[key]) for key in ("normalized_semantic_name","operation_key","export_name","raw_name","node_id") if raw.get(key)), raw_id)
    source_path = next((str(raw[key]) for key in ("path","declaring_header") if raw.get(key)), None)
    body = {
        "node_id": f"capability:{raw_id}",
        "node_kind": "CAPABILITY",
        "name": name,
        "source_path": source_path,
        "line": int(raw.get("line") or 0),
        "source_kind": str(raw.get("source_kind", "")),
        "authority_class": int(raw.get("authority_class", 0)),
        "repository_capability_node_id": raw_id,
        "repository_entry_signature64": int(raw.get("entry_signature64", 0)),
        "semantic_tokens": _tokens(name, raw.get("raw_name",""), raw.get("operation_key",""), raw.get("export_name",""), source_path or ""),
        "candidate_only": True,
        "execution_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "automatic_composition_promotion": False,
        "automatic_superedge_promotion": False,
    }
    body["hash216"] = _h216("HHS-P219-LANE5-REPOSITORY-KNOWLEDGE-CAPABILITY-1.69", body)
    return body


def _edge(source: Mapping[str, Any], relation: str, *, target: Mapping[str, Any] | None = None, file_path: str | None = None, file_hash216: str | None = None, evidence: Sequence[str] = ()) -> dict[str, Any]:
    body = {
        "source_node_id": str(source["node_id"]),
        "source_hash216": str(source["hash216"]),
        "relation_type": relation,
        "candidate_only": True,
        "execution_authority": False,
        "canonical_mutation_authority": False,
        "automatic_composition_promotion": False,
        "automatic_superedge_promotion": False,
        "evidence": sorted(set(evidence)),
    }
    if target is not None:
        body.update(target_node_id=str(target["node_id"]), target_hash216=str(target["hash216"]))
    if file_path is not None:
        body["target_file_path"] = file_path
    if file_hash216 is not None:
        if len(file_hash216) != 216:
            raise ValueError("target file Hash216 must be 216 characters")
        body["target_file_hash216"] = file_hash216
    body["hash216"] = _h216("HHS-P219-LANE5-REPOSITORY-KNOWLEDGE-EDGE-1.69", body)
    return body


def build_repository_hydration_knowledge_graph(repo_root: str | Path, dependency_graph: Mapping[str, Any], *, lane5_snapshot: Mapping[str, Any] | None = None) -> dict[str, Any]:
    files = _files(dependency_graph)
    source_root = str(dependency_graph.get("roots", {}).get("graph_root_hash216", ""))
    if len(source_root) != 216:
        raise ValueError("dependency graph missing graph_root_hash216")
    if lane5_snapshot is None:
        from hhs_backend.runtime.hhs_pass219_lane5_repository_capability_reverse_discovery_1_44 import build_repository_capability_reverse_discovery
        lane5_snapshot = build_repository_capability_reverse_discovery(repo_root)
    raw_nodes = lane5_snapshot.get("nodes")
    receipt = lane5_snapshot.get("native_receipt")
    if not isinstance(raw_nodes, list) or not raw_nodes:
        raise ValueError("Lane 5 capability snapshot empty")
    if int(lane5_snapshot.get("counts", {}).get("canonical_boundaries", -1)) != 1:
        raise ValueError("Lane 5 snapshot must retain exactly one canonical boundary")
    if not isinstance(receipt, Mapping) or receipt.get("accepted") is not True or receipt.get("candidate_only") is not True:
        raise ValueError("Lane 5 native receipt is not accepted candidate-only evidence")

    capabilities = sorted((_capability(row) for row in raw_nodes if isinstance(row, Mapping)), key=lambda x: str(x["node_id"]))
    constructors = discover_repository_constructors(repo_root, dependency_graph)
    nodes = capabilities + constructors
    if len({str(x["node_id"]) for x in nodes}) != len(nodes) or len({str(x["hash216"]) for x in nodes}) != len(nodes):
        raise ValueError("knowledge node identity collision")

    caps_by_path, ctors_by_path = defaultdict(list), defaultdict(list)
    for node in capabilities:
        path = node.get("source_path")
        if isinstance(path, str) and path in files:
            caps_by_path[path].append(node)
    for node in constructors:
        if node["source_path"] in files:
            ctors_by_path[node["source_path"]].append(node)

    edges = []
    for path, values in sorted(caps_by_path.items()):
        edges += [_edge(node, "DECLARED_IN_FILE", file_path=path, file_hash216=str(files[path]["hash216"]), evidence=("LANE5_REVERSE_DISCOVERY_SOURCE_BINDING",)) for node in values]
    for path, values in sorted(ctors_by_path.items()):
        edges += [_edge(node, "DECLARED_IN_FILE", file_path=path, file_hash216=str(files[path]["hash216"]), evidence=("CONSTRUCTOR_SOURCE_BINDING",)) for node in values]
    for path in sorted(set(caps_by_path) & set(ctors_by_path)):
        for capability in caps_by_path[path]:
            cap_tokens = set(capability["semantic_tokens"])
            for constructor in ctors_by_path[path]:
                overlap = sorted(cap_tokens & set(constructor["semantic_tokens"]))
                if overlap:
                    edges.append(_edge(constructor, "SEMANTICALLY_ALIGNED_WITH_CAPABILITY", target=capability, evidence=("SAME_SOURCE_FILE","NAME_TOKEN_OVERLAP",*overlap)))
    edges.sort(key=lambda x: (str(x["source_node_id"]), str(x["relation_type"]), str(x.get("target_node_id", x.get("target_file_path",""))), str(x["hash216"])))
    if len({str(x["hash216"]) for x in edges}) != len(edges):
        raise ValueError("knowledge edge identity collision")

    roots = {
        "capability_root_hash216": _h216("HHS-P219-LANE5-REPOSITORY-KNOWLEDGE-CAPABILITY-ROOT-1.69", [x["hash216"] for x in capabilities]),
        "constructor_root_hash216": _h216("HHS-P219-LANE5-REPOSITORY-KNOWLEDGE-CONSTRUCTOR-ROOT-1.69", [x["hash216"] for x in constructors]),
        "knowledge_node_root_hash216": _h216("HHS-P219-LANE5-REPOSITORY-KNOWLEDGE-NODE-ROOT-1.69", [x["hash216"] for x in nodes]),
        "knowledge_edge_root_hash216": _h216("HHS-P219-LANE5-REPOSITORY-KNOWLEDGE-EDGE-ROOT-1.69", [x["hash216"] for x in edges]),
    }
    counts = {
        "capabilities": len(capabilities),
        "constructors": len(constructors),
        "knowledge_nodes": len(nodes),
        "knowledge_edges": len(edges),
        "source_files": len(files),
        "source_dependency_edges": int(dependency_graph.get("counts", {}).get("file_dependency_edges", 0)),
    }
    core = {
        "schema": SCHEMA,
        "version": 1,
        "source_commit": str(dependency_graph.get("source_commit", "")),
        "source_tree": str(dependency_graph.get("source_tree", "")),
        "source_dependency_graph_root_hash216": source_root,
        "source_lane5_model_root_sha256": str(lane5_snapshot.get("model_root_sha256", "")),
        "counts": counts,
        "roots": roots,
        "database_binding": {
            "schema": DB_SCHEMA,
            "source_dependency_graph_required": True,
            "knowledge_projection_required": True,
            "sqlite_wal_required": True,
            "sqlite_synchronous_full_required": True,
            "hash216_character_indexed": True,
            "sha256_per_character_codeword": True,
            "restart_rehydratable": True,
        },
        "authority": {
            "candidate_only": True,
            "execution_authority": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
            "canonical_persistence_authority": False,
            "automatic_hash216_composition_promotion": False,
            "automatic_superedge_promotion": False,
            "signed_environmental_vm81_admission_required_for_mutation": True,
        },
        "capabilities": capabilities,
        "constructors": constructors,
        "edges": edges,
    }
    roots["projection_root_hash216"] = _h216(
        "HHS-P219-LANE5-REPOSITORY-HYDRATION-KNOWLEDGE-GRAPH-ROOT-1.69",
        {"source_dependency_graph_root_hash216": source_root, "source_lane5_model_root_sha256": core["source_lane5_model_root_sha256"], "roots": dict(roots), "counts": counts},
    )
    return core


def _verify_projection(projection: Mapping[str, Any]) -> None:
    if projection.get("schema") != SCHEMA:
        raise ValueError("knowledge projection schema mismatch")
    authority = projection.get("authority")
    forbidden = ("execution_authority","canonical_vm81_mutation_authority","canonical_hash72_authority","canonical_hash216_authority","canonical_persistence_authority","automatic_hash216_composition_promotion","automatic_superedge_promotion")
    if not isinstance(authority, Mapping) or authority.get("candidate_only") is not True or any(authority.get(key) is not False for key in forbidden):
        raise ValueError("knowledge projection authority escalation")
    capabilities, constructors, edges = projection.get("capabilities"), projection.get("constructors"), projection.get("edges")
    if not all(isinstance(value, list) for value in (capabilities, constructors, edges)):
        raise ValueError("knowledge projection collections missing")
    nodes = list(capabilities) + list(constructors)
    for node in nodes:
        body, claimed = dict(node), str(node.get("hash216", ""))
        body.pop("hash216", None)
        domain = "HHS-P219-LANE5-REPOSITORY-KNOWLEDGE-CAPABILITY-1.69" if node.get("node_kind") == "CAPABILITY" else "HHS-P219-LANE5-REPOSITORY-KNOWLEDGE-CONSTRUCTOR-1.69"
        if claimed != _h216(domain, body):
            raise ValueError(f"knowledge node Hash216 mismatch: {node.get('node_id')}")
    for edge in edges:
        body, claimed = dict(edge), str(edge.get("hash216", ""))
        body.pop("hash216", None)
        if claimed != _h216("HHS-P219-LANE5-REPOSITORY-KNOWLEDGE-EDGE-1.69", body):
            raise ValueError("knowledge edge Hash216 mismatch")
    roots = projection.get("roots")
    if not isinstance(roots, Mapping):
        raise ValueError("knowledge roots missing")
    expected = {
        "capability_root_hash216": _h216("HHS-P219-LANE5-REPOSITORY-KNOWLEDGE-CAPABILITY-ROOT-1.69", [x["hash216"] for x in capabilities]),
        "constructor_root_hash216": _h216("HHS-P219-LANE5-REPOSITORY-KNOWLEDGE-CONSTRUCTOR-ROOT-1.69", [x["hash216"] for x in constructors]),
        "knowledge_node_root_hash216": _h216("HHS-P219-LANE5-REPOSITORY-KNOWLEDGE-NODE-ROOT-1.69", [x["hash216"] for x in nodes]),
        "knowledge_edge_root_hash216": _h216("HHS-P219-LANE5-REPOSITORY-KNOWLEDGE-EDGE-ROOT-1.69", [x["hash216"] for x in edges]),
    }
    for key, value in expected.items():
        if roots.get(key) != value:
            raise ValueError(f"knowledge aggregate root mismatch: {key}")
    projection_root = _h216("HHS-P219-LANE5-REPOSITORY-HYDRATION-KNOWLEDGE-GRAPH-ROOT-1.69", {
        "source_dependency_graph_root_hash216": projection.get("source_dependency_graph_root_hash216"),
        "source_lane5_model_root_sha256": projection.get("source_lane5_model_root_sha256"),
        "roots": expected,
        "counts": projection.get("counts"),
    })
    if roots.get("projection_root_hash216") != projection_root:
        raise ValueError("knowledge projection root Hash216 mismatch")


class Lane5RepositoryHydrationKnowledgeDatabase:
    """SQLite Hash216 database for restartable capability/constructor hydration."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path).resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.database_path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS repository_files(path TEXT PRIMARY KEY,file_hash216 TEXT NOT NULL UNIQUE,git_blob TEXT,language TEXT,disposition TEXT,origin TEXT);
        CREATE TABLE IF NOT EXISTS file_dependencies(edge_hash216 TEXT PRIMARY KEY,source_path TEXT NOT NULL REFERENCES repository_files(path),target_path TEXT NOT NULL REFERENCES repository_files(path),relation_type TEXT NOT NULL,line INTEGER NOT NULL,reference TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS file_dep_source ON file_dependencies(source_path,relation_type);
        CREATE INDEX IF NOT EXISTS file_dep_target ON file_dependencies(target_path,relation_type);
        CREATE TABLE IF NOT EXISTS knowledge_nodes(node_id TEXT PRIMARY KEY,node_hash216 TEXT NOT NULL UNIQUE,node_kind TEXT NOT NULL,name TEXT NOT NULL,source_path TEXT,source_line INTEGER NOT NULL,payload_json TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS knowledge_kind_name ON knowledge_nodes(node_kind,name);
        CREATE INDEX IF NOT EXISTS knowledge_source ON knowledge_nodes(source_path,node_kind);
        CREATE TABLE IF NOT EXISTS knowledge_edges(edge_hash216 TEXT PRIMARY KEY,source_node_id TEXT NOT NULL REFERENCES knowledge_nodes(node_id),target_node_id TEXT,target_file_path TEXT,relation_type TEXT NOT NULL,payload_json TEXT NOT NULL,CHECK(target_node_id IS NOT NULL OR target_file_path IS NOT NULL));
        CREATE INDEX IF NOT EXISTS knowledge_edge_source ON knowledge_edges(source_node_id,relation_type);
        CREATE INDEX IF NOT EXISTS knowledge_edge_target_node ON knowledge_edges(target_node_id,relation_type);
        CREATE INDEX IF NOT EXISTS knowledge_edge_target_file ON knowledge_edges(target_file_path,relation_type);
        CREATE TABLE IF NOT EXISTS hash216_positions(owner_hash216 TEXT NOT NULL,owner_kind TEXT NOT NULL,ordinal INTEGER NOT NULL,lane INTEGER NOT NULL,lane_offset INTEGER NOT NULL,symbol TEXT NOT NULL,symbol_sha256 TEXT NOT NULL,PRIMARY KEY(owner_hash216,ordinal),CHECK(ordinal>=0 AND ordinal<216),CHECK(lane>=0 AND lane<3),CHECK(lane_offset>=0 AND lane_offset<72));
        CREATE TABLE IF NOT EXISTS hydration_metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        """)
        self.db.commit()

    def __enter__(self):
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self.db.close()

    @staticmethod
    def _positions(identity: str, kind: str):
        if len(identity) != 216:
            raise ValueError("Hash216 position index requires 216 characters")
        return [(identity,kind,i,i//72,i%72,ch,sha256(ch.encode("utf-8")).hexdigest()) for i,ch in enumerate(identity)]

    def hydrate(self, *, dependency_graph: Mapping[str, Any], knowledge_projection: Mapping[str, Any]) -> dict[str, Any]:
        _verify_projection(knowledge_projection)
        files = _files(dependency_graph)
        source_root = str(dependency_graph.get("roots", {}).get("graph_root_hash216", ""))
        if source_root != knowledge_projection.get("source_dependency_graph_root_hash216"):
            raise ValueError("knowledge projection/dependency graph root mismatch")
        dependencies = dependency_graph.get("dependency_edges")
        if not isinstance(dependencies, list):
            raise ValueError("dependency_edges missing")
        nodes = list(knowledge_projection["capabilities"]) + list(knowledge_projection["constructors"])
        edges = list(knowledge_projection["edges"])
        with self.db:
            for table in ("hash216_positions","knowledge_edges","knowledge_nodes","file_dependencies","repository_files","hydration_metadata"):
                self.db.execute(f"DELETE FROM {table}")
            self.db.executemany("INSERT INTO repository_files VALUES(?,?,?,?,?,?)", [
                (path,str(row["hash216"]),str(row.get("git_blob","")),str(row.get("language","")),str(row.get("disposition","")),str(row.get("origin","")))
                for path,row in sorted(files.items())
            ])
            self.db.executemany("INSERT INTO file_dependencies VALUES(?,?,?,?,?,?)", [
                (str(edge["hash216"]),str(edge["from"]),str(edge["to"]),str(edge["type"]),int(edge.get("line",0)),str(edge.get("reference","")))
                for edge in dependencies if isinstance(edge, Mapping)
            ])
            self.db.executemany("INSERT INTO knowledge_nodes VALUES(?,?,?,?,?,?,?)", [
                (str(node["node_id"]),str(node["hash216"]),str(node["node_kind"]),str(node["name"]),node.get("source_path"),int(node.get("line",0)),_canon(node))
                for node in nodes
            ])
            self.db.executemany("INSERT INTO knowledge_edges VALUES(?,?,?,?,?,?)", [
                (str(edge["hash216"]),str(edge["source_node_id"]),edge.get("target_node_id"),edge.get("target_file_path"),str(edge["relation_type"]),_canon(edge))
                for edge in edges
            ])
            for node in nodes:
                self.db.executemany("INSERT INTO hash216_positions VALUES(?,?,?,?,?,?,?)", self._positions(str(node["hash216"]), str(node["node_kind"])))
            for edge in edges:
                self.db.executemany("INSERT INTO hash216_positions VALUES(?,?,?,?,?,?,?)", self._positions(str(edge["hash216"]), "KNOWLEDGE_EDGE"))
            metadata = {
                "schema": DB_SCHEMA,
                "source_commit": str(knowledge_projection.get("source_commit","")),
                "source_tree": str(knowledge_projection.get("source_tree","")),
                "source_dependency_graph_root_hash216": source_root,
                "projection_root_hash216": str(knowledge_projection["roots"]["projection_root_hash216"]),
                "candidate_only": "true",
                "execution_authority": "false",
                "canonical_mutation_authority": "false",
                "restart_rehydratable": "true",
            }
            self.db.executemany("INSERT INTO hydration_metadata VALUES(?,?)", sorted(metadata.items()))
        return self.status()

    def status(self) -> dict[str, Any]:
        synchronous = int(self.db.execute("PRAGMA synchronous").fetchone()[0])
        return {
            "schema": DB_SCHEMA,
            "database_path": str(self.database_path),
            "repository_files": int(self.db.execute("SELECT COUNT(*) FROM repository_files").fetchone()[0]),
            "file_dependencies": int(self.db.execute("SELECT COUNT(*) FROM file_dependencies").fetchone()[0]),
            "capabilities": int(self.db.execute("SELECT COUNT(*) FROM knowledge_nodes WHERE node_kind='CAPABILITY'").fetchone()[0]),
            "constructors": int(self.db.execute("SELECT COUNT(*) FROM knowledge_nodes WHERE node_kind='CONSTRUCTOR'").fetchone()[0]),
            "knowledge_edges": int(self.db.execute("SELECT COUNT(*) FROM knowledge_edges").fetchone()[0]),
            "hash216_positions": int(self.db.execute("SELECT COUNT(*) FROM hash216_positions").fetchone()[0]),
            "journal_mode": str(self.db.execute("PRAGMA journal_mode").fetchone()[0]),
            "synchronous_full": synchronous == 2,
            "restart_rehydratable": True,
            "candidate_only": True,
            "execution_authority": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
            "canonical_persistence_authority": False,
        }

    def search(self, text: str, *, kinds: Sequence[str] = ("CAPABILITY","CONSTRUCTOR"), limit: int = 64) -> list[dict[str, Any]]:
        query, canonical_kinds = text.strip(), tuple(sorted(set(str(kind) for kind in kinds)))
        if not query or not canonical_kinds or limit <= 0 or limit > 512:
            raise ValueError("invalid bounded knowledge search")
        placeholders, like = ",".join("?" for _ in canonical_kinds), f"%{query}%"
        rows = self.db.execute(
            f"SELECT * FROM knowledge_nodes WHERE node_kind IN ({placeholders}) AND (name LIKE ? OR node_id LIKE ? OR COALESCE(source_path,'') LIKE ?) ORDER BY node_kind,name,node_id LIMIT ?",
            (*canonical_kinds,like,like,like,int(limit)),
        ).fetchall()
        return [{"node_id":str(row["node_id"]),"hash216":str(row["node_hash216"]),"node_kind":str(row["node_kind"]),"name":str(row["name"]),"source_path":row["source_path"],"source_line":int(row["source_line"]),"payload":json.loads(str(row["payload_json"]))} for row in rows]

    def neighbors(self, node_id: str, *, limit: int = 256) -> list[dict[str, Any]]:
        if limit <= 0 or limit > 2048:
            raise ValueError("invalid neighbor limit")
        rows = self.db.execute(
            "SELECT * FROM knowledge_edges WHERE source_node_id=? OR target_node_id=? ORDER BY relation_type,edge_hash216 LIMIT ?",
            (node_id,node_id,int(limit)),
        ).fetchall()
        return [{"hash216":str(row["edge_hash216"]),"source_node_id":str(row["source_node_id"]),"target_node_id":row["target_node_id"],"target_file_path":row["target_file_path"],"relation_type":str(row["relation_type"]),"payload":json.loads(str(row["payload_json"]))} for row in rows]
