"""Pass 214 semantic-equivalence reconciliation over the cumulative operation census.

This module is additive and evidence-oriented. It proves only relationships
that can be established mechanically from repository-visible mappings or exact
implementation structure. Name similarity alone never collapses operations.
Every coded operation also receives a stable discovery-registry identity; only
proven equivalence clusters share such an identity.
"""
from __future__ import annotations

import ast
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any, Iterable, Mapping

from hhs_backend.runtime.hhs_pass214_cumulative_operation_census_final_v1 import (
    build_final_cumulative_operation_census,
)
from hhs_backend.runtime.hhs_pass214_cumulative_operation_census_v1 import (
    MAX_DEFAULT_BYTES,
    OperationCensusError,
    _digest,
    _normalize,
)

SCHEMA = "HHS_PASS_214_SEMANTIC_EQUIVALENCE_RECONCILIATION_V1"
CLASSIFICATION = "HHS_PASS_214_CONSERVATIVE_SEMANTIC_EQUIVALENCE_AND_REUSE_PROOF"

PROOF_EXPLICIT_SEMANTIC_ID = "EXPLICIT_SEMANTIC_OPERATION_IDENTITY"
PROOF_EXACT_PROJECTION = "EXACT_NATIVE_REGISTRY_PROJECTION"
PROOF_IDENTICAL_IMPLEMENTATION = "IDENTICAL_IMPLEMENTATION_STRUCTURE"
PROOF_PURE_FORWARDER = "PURE_ARGUMENT_PRESERVING_FORWARDER"

EXECUTABLE_KIND_PREFIXES = (
    "PYTHON_FUNCTION", "PYTHON_METHOD", "C_FUNCTION", "CPP_FUNCTION",
    "JAVASCRIPT_FUNCTION", "JAVASCRIPT_ARROW", "TYPESCRIPT_FUNCTION",
    "RUST_FUNCTION", "JAVA_METHOD", "SHELL_FUNCTION", "PASS213_GOVERNED",
    "PASS079_NATIVE", "VM81_BASE20", "C_ENUM_OPCODE", "PYTHON_ENUM_OPCODE",
)
NON_BINDING_FAMILIES = {
    "ABI_DECLARATION_SURFACE", "FORMAL_SPECIFICATION", "BUILD_INTEGRATION",
}
EXPLICIT_OPERATION_FAMILIES = {
    "VM81_SUBSTRATE_OPCODE", "FROZEN_HHS_IR_OPCODE", "PASS158_LLABI_NFTC_OPCODE",
    "PASS079_NATIVE_ABI_OPCODE", "PASS213_GOVERNED_NATIVE_DISPATCH",
    "VM81_BASE20_NUMERICAL_ABI", "DECLARATIVE_CAPABILITY_REGISTRY",
}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


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


def _expr_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _expr_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def _arg_names(args: ast.arguments) -> list[str]:
    return [x.arg for x in (*args.posonlyargs, *args.args, *args.kwonlyargs)]


def _pure_forward_target(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    body = list(node.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        body = body[1:]
    if len(body) != 1:
        return None
    stmt = body[0]
    call: ast.Call | None = None
    if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Call):
        call = stmt.value
    elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
        call = stmt.value
    if call is None or any(k.arg is None for k in call.keywords):
        return None

    names = _arg_names(node.args)
    if names and names[0] in {"self", "cls"} and isinstance(call.func, ast.Attribute):
        owner = call.func.value
        if isinstance(owner, ast.Name) and owner.id == names[0]:
            names = names[1:]

    call_names: list[str] = []
    for arg in call.args:
        if not isinstance(arg, ast.Name):
            return None
        call_names.append(arg.id)
    if call_names != names[: len(call_names)]:
        return None
    for kw in call.keywords:
        if not isinstance(kw.value, ast.Name) or kw.arg != kw.value.id:
            return None
    target = _expr_name(call.func).split(".")[-1]
    return _normalize(target) if target else None


def _python_index(text: str) -> dict[tuple[str, int], dict[str, Any]]:
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return {}
    out: dict[tuple[str, int], dict[str, Any]] = {}
    stack: list[str] = []

    class Visitor(ast.NodeVisitor):
        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            stack.append(node.name)
            self.generic_visit(node)
            stack.pop()

        def _visit_fn(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
            qname = ".".join((*stack, node.name)) if stack else node.name
            args_dump = ast.dump(node.args, annotate_fields=True, include_attributes=False)
            body_dump = ast.dump(ast.Module(body=node.body, type_ignores=[]), annotate_fields=True, include_attributes=False)
            out[(qname, int(node.lineno))] = {
                "implementation_digest": sha256((args_dump + "\n" + body_dump).encode()).hexdigest(),
                "signature_digest": sha256(args_dump.encode()).hexdigest(),
                "pure_forward_target": _pure_forward_target(node),
            }
            stack.append(node.name)
            self.generic_visit(node)
            stack.pop()

        visit_FunctionDef = _visit_fn
        visit_AsyncFunctionDef = _visit_fn

    Visitor().visit(tree)
    return out


def _strip_c_like(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _brace_block(text: str, line: int) -> str | None:
    lines = text.splitlines(keepends=True)
    if line < 1 or line > len(lines):
        return None
    offset = sum(len(x) for x in lines[: line - 1])
    start = text.find("{", offset)
    if start < 0:
        return None
    depth = 0
    quote: str | None = None
    escaped = False
    for idx in range(start, len(text)):
        ch = text[idx]
        if quote:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            continue
        if ch in {"'", '"'}:
            quote = ch
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : idx + 1]
    return None


def _generic_structure(text: str, line: int) -> dict[str, Any] | None:
    block = _brace_block(text, line)
    if block is None:
        return None
    normalized = _strip_c_like(block)
    return {
        "implementation_digest": sha256(normalized.encode()).hexdigest(),
        "signature_digest": None,
        "pure_forward_target": None,
    }


def _implementation_evidence(
    root: Path,
    records: Iterable[Mapping[str, Any]],
    *,
    max_source_bytes: int,
) -> dict[str, dict[str, Any]]:
    by_path: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in records:
        by_path[str(row["path"])].append(row)
    out: dict[str, dict[str, Any]] = {}
    for path, rows in by_path.items():
        suffix = PurePosixPath(path).suffix.lower()
        if suffix not in {
            ".py", ".pyi", ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".inc",
            ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".rs", ".java",
            ".kt", ".kts", ".swift",
        }:
            continue
        text = _read(root, path, max_source_bytes)
        if text is None:
            continue
        py = _python_index(text) if suffix in {".py", ".pyi"} else {}
        for row in rows:
            key = str(row["operation_key"])
            kind = str(row["kind"])
            line = int(row.get("line") or 0)
            if suffix in {".py", ".pyi"} and kind in {"PYTHON_FUNCTION", "PYTHON_METHOD"}:
                hit = py.get((str(row["raw_name"]), line))
                if hit:
                    out[key] = hit
            elif kind.endswith("FUNCTION") or kind.endswith("METHOD") or "ARROW" in kind:
                hit = _generic_structure(text, line)
                if hit:
                    out[key] = hit
    return out


class _DSU:
    def __init__(self, keys: Iterable[str]) -> None:
        self.parent = {k: k for k in keys}

    def find(self, x: str) -> str:
        p = self.parent[x]
        if p != x:
            self.parent[x] = self.find(p)
        return self.parent[x]

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def _executable(row: Mapping[str, Any]) -> bool:
    if str(row.get("family")) in NON_BINDING_FAMILIES:
        return False
    kind = str(row.get("kind", ""))
    return kind.startswith(EXECUTABLE_KIND_PREFIXES) or str(row.get("family")) in EXPLICIT_OPERATION_FAMILIES | {"CALLABLE_OPERATION"}


def _top_level_promotable(row: Mapping[str, Any]) -> bool:
    if str(row.get("family")) in EXPLICIT_OPERATION_FAMILIES:
        return True
    kind = str(row.get("kind", ""))
    raw_name = str(row.get("raw_name", ""))
    leaf = raw_name.split(".")[-1]
    if leaf.startswith("_"):
        return False
    if kind == "PYTHON_METHOD":
        return False
    if kind == "PYTHON_FUNCTION":
        return "." not in raw_name
    if kind in {"JAVASCRIPT_FUNCTION", "JAVASCRIPT_ARROW_FUNCTION", "JAVASCRIPT_ARROW", "TYPESCRIPT_FUNCTION", "C_FUNCTION", "CPP_FUNCTION", "RUST_FUNCTION", "SHELL_FUNCTION"}:
        return "." not in raw_name
    return False


def _binding_priority(row: Mapping[str, Any]) -> tuple[int, int, str, int]:
    path = str(row["path"])
    family = str(row["family"])
    if family == "PASS213_GOVERNED_NATIVE_DISPATCH":
        rank = 0
    elif path.startswith("hhs_runtime/"):
        rank = 1
    elif path.startswith("hhs_backend/runtime/"):
        rank = 2
    elif path.startswith("hhs_python/"):
        rank = 3
    elif path.startswith("native/"):
        rank = 4
    elif path.startswith("native_projects/"):
        rank = 5
    elif path.startswith("applications/"):
        rank = 6
    else:
        rank = 7
    pass_no = int(row["pass_number"]) if row.get("pass_number") is not None else -1
    return rank, pass_no, path, int(row.get("line") or 0)


def build_semantic_equivalence_reconciliation(
    repository_root: Path,
    *,
    source_ref: str = "HEAD",
    max_source_bytes: int = MAX_DEFAULT_BYTES,
) -> dict[str, Any]:
    root = repository_root.resolve()
    census = build_final_cumulative_operation_census(
        root, source_ref=source_ref, max_source_bytes=max_source_bytes
    )
    records = [dict(x) for x in census["operations"]]
    by_key = {str(x["operation_key"]): x for x in records}
    by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        by_name[str(row["normalized_semantic_name"])].append(row)
    implementation = _implementation_evidence(root, records, max_source_bytes=max_source_bytes)

    groups: list[dict[str, Any]] = []
    registry_entries: list[dict[str, Any]] = []
    proof_edge_count = 0
    explicit_projection_pairs = 0
    identical_body_pairs = 0
    forwarder_pairs = 0

    for semantic_name, members in sorted(by_name.items()):
        if len(members) < 2:
            continue
        keys = [str(x["operation_key"]) for x in members]
        dsu = _DSU(keys)
        proofs: list[dict[str, Any]] = []
        conflicts: list[dict[str, Any]] = []

        def add_proof(a: str, b: str, proof_type: str, detail: Mapping[str, Any]) -> None:
            nonlocal proof_edge_count, explicit_projection_pairs, identical_body_pairs, forwarder_pairs
            if a == b:
                return
            dsu.union(a, b)
            proof_edge_count += 1
            if proof_type == PROOF_EXACT_PROJECTION:
                explicit_projection_pairs += 1
            elif proof_type == PROOF_IDENTICAL_IMPLEMENTATION:
                identical_body_pairs += 1
            elif proof_type == PROOF_PURE_FORWARDER:
                forwarder_pairs += 1
            proofs.append({"left": a, "right": b, "proof_type": proof_type, "detail": dict(detail)})

        semantic_ids: dict[str, list[str]] = defaultdict(list)
        for row in members:
            sid = row.get("semantic_operation_identity")
            if sid:
                semantic_ids[str(sid)].append(str(row["operation_key"]))
        for sid, bucket in semantic_ids.items():
            for other in bucket[1:]:
                add_proof(bucket[0], other, PROOF_EXPLICIT_SEMANTIC_ID, {"semantic_operation_identity": sid})
        if len(semantic_ids) > 1:
            conflicts.append({"type": "DIFFERENT_EXPLICIT_SEMANTIC_OPERATION_IDENTITIES", "values": sorted(semantic_ids)})

        projections: dict[str, list[str]] = defaultdict(list)
        for row in members:
            projection = row.get("exact_projection")
            if projection:
                target = _normalize(str(projection).split(":")[-1])
                projections[target].append(str(row["operation_key"]))
                targets = [
                    x for x in members
                    if str(x["normalized_semantic_name"]) == target
                    and str(x["family"]) == "VM81_SUBSTRATE_OPCODE"
                ]
                for target_row in targets:
                    add_proof(
                        str(row["operation_key"]),
                        str(target_row["operation_key"]),
                        PROOF_EXACT_PROJECTION,
                        {"exact_projection": projection},
                    )
        if len(projections) > 1:
            conflicts.append({"type": "DIFFERENT_EXACT_PROJECTIONS", "values": sorted(projections)})

        by_impl: dict[tuple[str, str | None], list[str]] = defaultdict(list)
        for row in members:
            ev = implementation.get(str(row["operation_key"]))
            if ev:
                by_impl[(str(ev["implementation_digest"]), ev.get("signature_digest"))].append(str(row["operation_key"]))
        for (digest, sig), bucket in by_impl.items():
            if len(bucket) > 1:
                for other in bucket[1:]:
                    add_proof(
                        bucket[0], other, PROOF_IDENTICAL_IMPLEMENTATION,
                        {"implementation_digest": digest, "signature_digest": sig},
                    )

        target_keys = {str(row["operation_key"]): row for row in members}
        for row in members:
            key = str(row["operation_key"])
            ev = implementation.get(key)
            target = ev.get("pure_forward_target") if ev else None
            if not target:
                continue
            target_rows = [
                x for x in members
                if _normalize(str(x["raw_name"]).split(".")[-1]) == target
            ]
            for target_row in target_rows:
                target_key = str(target_row["operation_key"])
                if target_key in target_keys and target_key != key:
                    add_proof(key, target_key, PROOF_PURE_FORWARDER, {"forward_target": target})

        clusters_map: dict[str, list[str]] = defaultdict(list)
        for key in keys:
            clusters_map[dsu.find(key)].append(key)
        clusters = [sorted(v) for v in clusters_map.values()]
        clusters.sort(key=lambda x: (len(x), x), reverse=True)
        proven_clusters = [x for x in clusters if len(x) > 1]

        if conflicts:
            status = "CONFLICT_EVIDENCE_REQUIRES_MANUAL_OR_BEHAVIORAL_REVIEW"
        elif len(proven_clusters) == 1 and len(proven_clusters[0]) == len(keys):
            status = "PROVEN_EQUIVALENT"
        elif proven_clusters:
            status = "PARTIALLY_PROVEN_EQUIVALENT"
        else:
            status = "UNRESOLVED_REQUIRES_BEHAVIORAL_CONFORMANCE"

        groups.append({
            "normalized_semantic_name": semantic_name,
            "status": status,
            "member_operation_keys": sorted(keys),
            "proven_equivalence_clusters": proven_clusters,
            "proofs": proofs,
            "conflicts": conflicts,
        })

        for cluster in proven_clusters:
            rows = [by_key[x] for x in cluster]
            executable = [x for x in rows if _executable(x)]
            preferred = min(executable, key=_binding_priority) if executable else None
            has_shared = any(str(x["reuse_status"]) == "SHARED_MODULE" for x in rows)
            isolated = [x for x in rows if str(x["reuse_status"]) == "ISOLATED_IMPLEMENTATION_CANDIDATE"]
            has_exact_projection = any(x.get("exact_projection") for x in rows)
            if has_exact_projection:
                action = "REGISTER_EXACT_PROJECTION"
            elif has_shared and isolated:
                action = "REUSE_EXISTING_SHARED_MODULE"
            elif len(isolated) >= 2 and all(_top_level_promotable(x) for x in isolated):
                action = "PROMOTE_TO_SHARED_MODULE_CANDIDATE"
            else:
                action = "REGISTER_PROVEN_ALIAS"
            registry_entries.append({
                "cluster_id": "hhs.reuse." + _sha(sorted(cluster))[:24],
                "normalized_semantic_name": semantic_name,
                "proof_status": "PROVEN_EQUIVALENT_CLUSTER",
                "member_operation_keys": sorted(cluster),
                "member_paths": sorted({str(x["path"]) for x in rows}),
                "preferred_binding": None if preferred is None else {
                    "operation_key": preferred["operation_key"],
                    "path": preferred["path"],
                    "line": preferred["line"],
                    "raw_name": preferred["raw_name"],
                    "family": preferred["family"],
                    "authority": preferred["authority"],
                },
                "migration_action": action,
                "isolated_member_operation_keys": sorted(str(x["operation_key"]) for x in isolated),
            })

    registry_entries.sort(key=lambda x: (x["normalized_semantic_name"], x["cluster_id"]))
    cluster_by_operation: dict[str, dict[str, Any]] = {}
    for entry in registry_entries:
        for key in entry["member_operation_keys"]:
            if key in cluster_by_operation:
                raise OperationCensusError(f"OPERATION_IN_MULTIPLE_PROVEN_CLUSTERS:{key}")
            cluster_by_operation[str(key)] = entry

    candidate_names = {str(x["normalized_semantic_name"]) for x in groups}
    operation_registry_entries: list[dict[str, Any]] = []
    for row in records:
        key = str(row["operation_key"])
        cluster = cluster_by_operation.get(key)
        if cluster is not None:
            registry_id = str(cluster["cluster_id"])
            registry_status = "PROVEN_EQUIVALENCE_SHARED_IDENTITY"
            migration_requirement = str(cluster["migration_action"])
        else:
            registry_id = "hhs.operation." + key[:24]
            registry_status = (
                "UNRESOLVED_MULTI_IDENTITY_DISTINCT_IDENTITY"
                if str(row["normalized_semantic_name"]) in candidate_names
                else "SINGLETON_DISTINCT_IDENTITY"
            )
            migration_requirement = (
                "REQUIRES_REUSABLE_EXTRACTION_OR_ADAPTER"
                if str(row["reuse_status"]) == "ISOLATED_IMPLEMENTATION_CANDIDATE"
                else "NONE"
            )
        if row.get("exact_projection"):
            migration_requirement = "PROJECTION_SURFACE_NOT_IMPLEMENTATION_BACKLOG"
        operation_registry_entries.append({
            "registry_id": registry_id,
            "registry_status": registry_status,
            "operation_key": key,
            "normalized_semantic_name": row["normalized_semantic_name"],
            "raw_name": row["raw_name"],
            "kind": row["kind"],
            "family": row["family"],
            "authority": row["authority"],
            "reuse_status": row["reuse_status"],
            "python_exposure": row["python_exposure"],
            "path": row["path"],
            "line": row["line"],
            "pass_number": row["pass_number"],
            "migration_requirement": migration_requirement,
        })
    operation_registry_entries.sort(key=lambda x: (x["registry_id"], x["path"], int(x["line"]), x["operation_key"]))

    status_counts: dict[str, int] = defaultdict(int)
    for group in groups:
        status_counts[str(group["status"])] += 1
    migration_counts: dict[str, int] = defaultdict(int)
    covered_isolated: set[str] = set()
    projection_isolated: set[str] = set()
    for entry in registry_entries:
        migration_counts[str(entry["migration_action"])] += 1
        if entry["migration_action"] in {"REUSE_EXISTING_SHARED_MODULE", "PROMOTE_TO_SHARED_MODULE_CANDIDATE"}:
            covered_isolated.update(str(x) for x in entry["isolated_member_operation_keys"])
    for row in records:
        if row.get("exact_projection") and str(row["reuse_status"]) == "ISOLATED_IMPLEMENTATION_CANDIDATE":
            projection_isolated.add(str(row["operation_key"]))

    isolated_total = int(census["summary"]["reuse_accounting"]["isolated_implementation_candidates"])
    implementation_backlog = max(0, isolated_total - len(projection_isolated))
    remaining_backlog = max(0, implementation_backlog - len(covered_isolated))
    registry_identity_count = len({str(x["registry_id"]) for x in operation_registry_entries})

    result = {
        "schema": SCHEMA,
        "classification": CLASSIFICATION,
        "parent_census_schema": census["schema"],
        "parent_census_sha256": census["census_sha256"],
        "policy": {
            "name_similarity_is_never_equivalence_proof": True,
            "proofs_are_repository_visible_and_deterministic": True,
            "unresolved_groups_remain_distinct": True,
            "every_coded_operation_has_registry_identity": True,
            "shared_registry_identity_requires_proven_equivalence": True,
            "registry_is_discovery_and_reuse_surface_not_execution_authority": True,
            "frozen_runtime_modified": False,
            "automatic_runtime_rewrite": False,
        },
        "summary": {
            "source_commit": census["summary"]["source_commit"],
            "source_tree": census["summary"]["source_tree"],
            "raw_operation_identities": census["summary"]["coverage"]["raw_operation_identities"],
            "operation_registry_entries": len(operation_registry_entries),
            "registry_identity_count_without_unproven_collapse": registry_identity_count,
            "candidate_groups": len(groups),
            "group_status_counts": dict(sorted(status_counts.items())),
            "proof_edges": proof_edge_count,
            "explicit_projection_proof_edges": explicit_projection_pairs,
            "identical_implementation_proof_edges": identical_body_pairs,
            "pure_forwarder_proof_edges": forwarder_pairs,
            "reusable_registry_entries": len(registry_entries),
            "migration_action_counts": dict(sorted(migration_counts.items())),
            "isolated_implementation_candidates_total": isolated_total,
            "projection_surfaces_removed_from_implementation_backlog": len(projection_isolated),
            "isolated_implementation_backlog_after_projection_filter": implementation_backlog,
            "isolated_candidates_covered_by_proven_reuse_or_promotion": len(covered_isolated),
            "isolated_candidates_remaining_reusable_extraction_backlog": remaining_backlog,
            "known_opcode_family_anchors": census["summary"]["known_opcode_family_anchors"],
            "frozen_runtime": census["summary"]["frozen_runtime"],
        },
        "semantic_groups": groups,
        "reusable_operation_registry_entries": registry_entries,
        "operation_registry_entries": operation_registry_entries,
        "unresolved_isolation_backlog": [
            x for x in operation_registry_entries
            if x["migration_requirement"] == "REQUIRES_REUSABLE_EXTRACTION_OR_ADAPTER"
        ],
    }
    if not result["summary"]["known_opcode_family_anchors"]["all_satisfied"]:
        raise OperationCensusError("SEMANTIC_RECONCILIATION_KNOWN_FAMILY_ANCHOR_FAILURE")
    if result["summary"]["operation_registry_entries"] != result["summary"]["raw_operation_identities"]:
        raise OperationCensusError("OPERATION_REGISTRY_COVERAGE_MISMATCH")
    result["reconciliation_sha256"] = _digest(result)
    return result


def write_reconciliation(result: Mapping[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_and_validate_reconciliation(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    supplied = data.pop("reconciliation_sha256", None)
    if supplied != _digest(data):
        raise OperationCensusError("SEMANTIC_RECONCILIATION_SHA256_FAILURE")
    data["reconciliation_sha256"] = supplied
    if data.get("schema") != SCHEMA:
        raise OperationCensusError("SEMANTIC_RECONCILIATION_SCHEMA_MISMATCH")
    if not data["summary"]["known_opcode_family_anchors"]["all_satisfied"]:
        raise OperationCensusError("SEMANTIC_RECONCILIATION_ANCHOR_FAILURE")
    if data["summary"]["operation_registry_entries"] != data["summary"]["raw_operation_identities"]:
        raise OperationCensusError("SEMANTIC_RECONCILIATION_REGISTRY_COVERAGE_FAILURE")
    return data
