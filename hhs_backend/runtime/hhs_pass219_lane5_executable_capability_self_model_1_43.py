"""Pass 219 Lane 5 executable capability self-model 1.43.

The model is derived from repository-visible authoritative surfaces.  It does not
invent a replacement registry and does not gain canonical mutation authority.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

from hhs_runtime.pass145.canonical import hash72
from hhs_runtime.pass147.registry import PublicSurfaceRegistry
from hhs_python.runtime.hhs_pass219_lane5_capability_self_model_bridge import (
    AUTH_CANONICAL_ADMISSION_BOUNDARY,
    AUTH_GOVERNED_TRANSFORM,
    AUTH_OBSERVATION,
    AUTH_RESTRICTED_OR_UNAVAILABLE,
    MAX_ENTRIES,
    SOURCE_NATIVE_EXACT_ABI,
    SOURCE_PUBLIC_REGISTRY,
    VERSION,
    Pass219Lane5CapabilitySelfModelBridge,
)

SCHEMA = "HHS_PASS_219_LANE5_EXECUTABLE_CAPABILITY_SELF_MODEL_1_43"
CANONICAL_BOUNDARY_EXPORT = "hhs_exact_pass219_vm81_environment_admit_signed"

_RESTRICTED_PUBLIC_CLASSIFICATIONS = {
    "EXPLICITLY_RESTRICTED_BY_CONTRACT",
    "PLATFORM_INAPPLICABLE",
    "OBSERVED_FAILING",
}

_INCLUDE_RE = re.compile(r'^\s*#include\s+"([^"]+)"', re.MULTILINE)
_EXPORT_RE = re.compile(
    r"\bHHS_EXACT_API\b[^;{}]*?\b(hhs_exact_[A-Za-z0-9_]+)\s*\(",
    re.MULTILINE | re.DOTALL,
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_root(domain: str, value: Any) -> str:
    payload = domain.encode("utf-8") + b"\0" + _canonical_json(value).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _signature64(domain: str, value: Any) -> int:
    payload = domain.encode("utf-8") + b"\0" + _canonical_json(value).encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "little") or 1


def _public_authority_class(item: dict[str, Any]) -> int:
    classification = str(item.get("classification", "")).upper()
    if classification in _RESTRICTED_PUBLIC_CLASSIFICATIONS:
        return AUTH_RESTRICTED_OR_UNAVAILABLE
    if bool(item.get("mutating")):
        return AUTH_GOVERNED_TRANSFORM
    return AUTH_OBSERVATION


def _native_authority_class(export_name: str) -> int:
    if export_name == CANONICAL_BOUNDARY_EXPORT:
        return AUTH_CANONICAL_ADMISSION_BOUNDARY
    if export_name.endswith("_version") or export_name.endswith("_authority"):
        return AUTH_OBSERVATION
    return AUTH_GOVERNED_TRANSFORM


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


class Pass219Lane5ExecutableCapabilitySelfModel:
    def __init__(
        self,
        repo_root: str | Path | None = None,
        *,
        bridge: Pass219Lane5CapabilitySelfModelBridge | None = None,
    ) -> None:
        self.repo_root = (
            Path(repo_root).resolve()
            if repo_root is not None
            else Path(__file__).resolve().parents[2]
        )
        self.include_root = (self.repo_root / "hhs_runtime" / "include").resolve()
        self.aggregate_header = self.include_root / "hhs_runtime_exact_abi.h"
        self.bridge = bridge or Pass219Lane5CapabilitySelfModelBridge()

    def _public_catalog(self) -> list[dict[str, Any]]:
        # build_catalog is intentionally used instead of a hand-maintained mirror.
        catalog = PublicSurfaceRegistry(db=None).build_catalog()
        ids = [str(item["capability_id"]) for item in catalog]
        if len(ids) != len(set(ids)):
            raise RuntimeError("Pass147 public capability IDs are not unique")
        return catalog

    def _reachable_headers(self) -> list[Path]:
        if not self.aggregate_header.is_file():
            raise FileNotFoundError(self.aggregate_header)
        pending = [self.aggregate_header]
        visited: set[Path] = set()
        while pending:
            header = pending.pop()
            header = header.resolve()
            if header in visited:
                continue
            if not _inside(self.include_root, header) or not header.is_file():
                continue
            visited.add(header)
            text = header.read_text(encoding="utf-8")
            for include_name in _INCLUDE_RE.findall(text):
                candidate = (header.parent / include_name).resolve()
                if _inside(self.include_root, candidate) and candidate.suffix == ".h":
                    pending.append(candidate)
        return sorted(visited, key=lambda path: path.relative_to(self.include_root).as_posix())

    def _native_exports(self) -> list[dict[str, str]]:
        by_name: dict[str, str] = {}
        duplicate_origins: dict[str, set[str]] = {}
        for header in self._reachable_headers():
            relative = header.relative_to(self.repo_root).as_posix()
            text = header.read_text(encoding="utf-8")
            for export_name in _EXPORT_RE.findall(text):
                if export_name in by_name and by_name[export_name] != relative:
                    duplicate_origins.setdefault(export_name, {by_name[export_name]}).add(relative)
                    continue
                by_name[export_name] = relative
        if duplicate_origins:
            details = {key: sorted(value) for key, value in sorted(duplicate_origins.items())}
            raise RuntimeError(f"exact ABI export declarations are duplicated across headers: {details}")
        return [
            {"export_name": name, "declaring_header": by_name[name]}
            for name in sorted(by_name)
        ]

    @staticmethod
    def _public_node(item: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, str]]]:
        normalized = {
            "node_id": f"public:{item['capability_id']}",
            "source_kind": "PUBLIC_REGISTRY",
            "source_kind_code": SOURCE_PUBLIC_REGISTRY,
            "authority_class": _public_authority_class(item),
            "capability_id": str(item["capability_id"]),
            "capability_hash72": str(item["capability_hash72"]),
            "surface_type": str(item["surface_type"]),
            "classification": str(item["classification"]),
            "capabilities": sorted(str(value) for value in item.get("capabilities", [])),
            "reversibility_class": str(item.get("reversibility_class", "")),
            "mutating": bool(item.get("mutating")),
            "argv": [str(value) for value in item.get("argv", [])],
            "method": str(item.get("method", "")),
            "path": str(item.get("path", "")),
        }
        signature = _signature64("hhs_pass219_lane5_capability_self_model_public_node_v1", normalized)
        normalized["entry_signature64"] = signature
        edges = [
            {
                "from": normalized["node_id"],
                "to": f"boundary-capability:{capability}",
                "type": "REQUIRES_BOUNDARY_CAPABILITY",
            }
            for capability in normalized["capabilities"]
        ]
        return normalized, edges

    @staticmethod
    def _native_node(item: dict[str, str]) -> tuple[dict[str, Any], dict[str, str]]:
        export_name = item["export_name"]
        normalized = {
            "node_id": f"native:{export_name}",
            "source_kind": "NATIVE_EXACT_ABI",
            "source_kind_code": SOURCE_NATIVE_EXACT_ABI,
            "authority_class": _native_authority_class(export_name),
            "export_name": export_name,
            "declaring_header": item["declaring_header"],
        }
        signature = _signature64("hhs_pass219_lane5_capability_self_model_native_node_v1", normalized)
        normalized["entry_signature64"] = signature
        edge = {
            "from": normalized["node_id"],
            "to": f"header:{item['declaring_header']}",
            "type": "DECLARED_BY",
        }
        return normalized, edge

    def build(self) -> dict[str, Any]:
        public_catalog = self._public_catalog()
        native_exports = self._native_exports()
        if not public_catalog:
            raise RuntimeError("Pass147 public capability catalog is empty")
        if not native_exports:
            raise RuntimeError("cumulative exact ABI export surface is empty")

        public_nodes: list[dict[str, Any]] = []
        native_nodes: list[dict[str, Any]] = []
        edges: list[dict[str, str]] = []
        for item in public_catalog:
            node, node_edges = self._public_node(item)
            public_nodes.append(node)
            edges.extend(node_edges)
        for item in native_exports:
            node, edge = self._native_node(item)
            native_nodes.append(node)
            edges.append(edge)

        boundary_nodes = [
            node
            for node in native_nodes
            if node["authority_class"] == AUTH_CANONICAL_ADMISSION_BOUNDARY
        ]
        if len(boundary_nodes) != 1:
            raise RuntimeError(
                f"expected exactly one signed environmental canonical boundary, found {len(boundary_nodes)}"
            )
        if boundary_nodes[0]["export_name"] != CANONICAL_BOUNDARY_EXPORT:
            raise RuntimeError("canonical boundary export identity drifted")

        nodes = sorted(public_nodes + native_nodes, key=lambda node: str(node["node_id"]))
        node_ids = [str(node["node_id"]) for node in nodes]
        if len(node_ids) != len(set(node_ids)):
            raise RuntimeError("self-model node IDs are not unique")
        entry_signatures = [int(node["entry_signature64"]) for node in nodes]
        if len(entry_signatures) != len(set(entry_signatures)):
            raise RuntimeError("self-model 64-bit entry signature collision")
        if len(nodes) > MAX_ENTRIES:
            raise RuntimeError(
                f"self-model contains {len(nodes)} entries, exceeding native bound {MAX_ENTRIES}"
            )

        edges = sorted(edges, key=lambda edge: (edge["from"], edge["type"], edge["to"]))
        public_catalog_root = hash72("hhs_pass147_public_catalog_v1", public_catalog)
        native_export_root = _sha256_root(
            "hhs_pass219_lane5_capability_self_model_native_exports_v1", native_exports
        )
        dependency_root = _sha256_root(
            "hhs_pass219_lane5_capability_self_model_dependency_graph_v1", edges
        )
        model_core = {
            "schema": SCHEMA,
            "version": VERSION,
            "public_catalog_root_hash72": public_catalog_root,
            "native_export_root_sha256": native_export_root,
            "dependency_root_sha256": dependency_root,
            "canonical_boundary_export": CANONICAL_BOUNDARY_EXPORT,
            "nodes": nodes,
            "edges": edges,
            "scope": {
                "pass147_public_registry_complete": True,
                "cumulative_exact_abi_complete": True,
                "repository_total_historical_capability_complete": False,
            },
        }
        model_root = _sha256_root(
            "hhs_pass219_lane5_executable_capability_self_model_v1", model_core
        )

        bridge_entries = [
            (
                int(node["entry_signature64"]),
                int(node["source_kind_code"]),
                int(node["authority_class"]),
            )
            for node in nodes
        ]
        native_receipt = self.bridge.validate_snapshot(
            entries=bridge_entries,
            public_catalog_root=public_catalog_root,
            native_export_root=native_export_root,
            dependency_root=dependency_root,
            model_root=model_root,
            canonical_boundary_signature64=int(boundary_nodes[0]["entry_signature64"]),
        )
        authority = self.bridge.authority()

        return {
            **model_core,
            "model_root_sha256": model_root,
            "counts": {
                "public_registry": len(public_nodes),
                "native_exact_abi": len(native_nodes),
                "total": len(nodes),
                "restricted": sum(
                    1
                    for node in nodes
                    if node["authority_class"] == AUTH_RESTRICTED_OR_UNAVAILABLE
                ),
                "canonical_boundaries": len(boundary_nodes),
            },
            "native_receipt": native_receipt,
            "authority": authority,
        }


def build_capability_self_model(repo_root: str | Path | None = None) -> dict[str, Any]:
    return Pass219Lane5ExecutableCapabilitySelfModel(repo_root).build()


__all__ = [
    "SCHEMA",
    "CANONICAL_BOUNDARY_EXPORT",
    "Pass219Lane5ExecutableCapabilitySelfModel",
    "build_capability_self_model",
]
