"""Pass 219 Lane 5 repository capability reverse discovery 1.44.

This successor preserves the exact 1.43 public/native discovery surfaces and adds
only Pass214's strict structural Python operation-registry keys.  Discovery is
evidence-only: registry keys are observations and are never automatically
promoted into Hash216 composition edges, superedges, or canonical authority.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from hhs_backend.runtime.hhs_pass214_python_operation_registry_v1 import (
    extract_python_operation_registry_keys,
)
from hhs_backend.runtime.hhs_pass219_lane5_executable_capability_self_model_1_43 import (
    CANONICAL_BOUNDARY_EXPORT,
    Pass219Lane5ExecutableCapabilitySelfModel,
    _sha256_root,
    _signature64,
)
from hhs_runtime.pass145.canonical import hash72
from hhs_python.runtime.hhs_pass219_lane5_repository_capability_reverse_discovery_bridge import (
    AUTH_CANONICAL_ADMISSION_BOUNDARY,
    AUTH_OBSERVATION,
    AUTH_RESTRICTED_OR_UNAVAILABLE,
    MAX_ENTRIES,
    SOURCE_NATIVE_EXACT_ABI,
    SOURCE_PUBLIC_REGISTRY,
    SOURCE_PYTHON_OPERATION_REGISTRY,
    VERSION,
    Pass219Lane5RepositoryCapabilityReverseDiscoveryBridge,
)

SCHEMA = "HHS_PASS_219_LANE5_REPOSITORY_CAPABILITY_REVERSE_DISCOVERY_1_44"
SOURCE_POLICY = "PASS214_STRUCTURAL_KEYS_ONLY_STRICT_OPERATION_REGISTRY_NAMES"


class Pass219Lane5RepositoryCapabilityReverseDiscovery:
    def __init__(
        self,
        repo_root: str | Path | None = None,
        *,
        bridge: Pass219Lane5RepositoryCapabilityReverseDiscoveryBridge | None = None,
    ) -> None:
        self.repo_root = (
            Path(repo_root).resolve()
            if repo_root is not None
            else Path(__file__).resolve().parents[2]
        )
        self.bridge = bridge or Pass219Lane5RepositoryCapabilityReverseDiscoveryBridge()
        # The inherited builder is used as the implementation source of truth for
        # 1.43 public/native discovery and node identity.  Its native bridge is not
        # invoked here.
        self.inherited = Pass219Lane5ExecutableCapabilitySelfModel(
            self.repo_root, bridge=object()  # type: ignore[arg-type]
        )

    def _python_operation_registry(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        records, manifest = extract_python_operation_registry_keys(self.repo_root)
        records = sorted(records, key=lambda item: str(item["operation_key"]))
        parse_errors = list(manifest.get("python_registry_parse_errors", []))
        if parse_errors:
            raise RuntimeError(
                f"structural Python registry scan has parse errors: {parse_errors}"
            )
        if int(manifest.get("python_operation_registry_keys", -1)) != len(records):
            raise RuntimeError("Pass214 Python registry manifest count drifted")
        if manifest.get("policy") != "STRUCTURAL_KEYS_ONLY_STRICT_OPERATION_REGISTRY_NAMES":
            raise RuntimeError("Pass214 Python registry extraction policy drifted")
        if not records:
            raise RuntimeError("structural Python operation registry surface is empty")
        return records, manifest

    @staticmethod
    def _python_registry_node(item: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
        normalized = {
            "node_id": f"python-registry:{item['operation_key']}",
            "source_kind": "PYTHON_OPERATION_REGISTRY",
            "source_kind_code": SOURCE_PYTHON_OPERATION_REGISTRY,
            "authority_class": AUTH_OBSERVATION,
            "operation_key": str(item["operation_key"]),
            "raw_name": str(item["raw_name"]),
            "normalized_semantic_name": str(item["normalized_semantic_name"]),
            "path": str(item["path"]),
            "line": int(item["line"]),
            "registry": str(item.get("registry", "")),
            "registry_shape": str(item.get("registry_shape", "")),
            "component": str(item.get("component", "")),
            "repository_authority": str(item.get("authority", "")),
            "origin_kind": str(item.get("origin_kind", "")),
            "pass_number": item.get("pass_number"),
            "execution_authority": "DISCOVERY_ONLY_UNCLASSIFIED",
            "hash216_composition_eligible": False,
            "superedge_promotion_eligible": False,
        }
        normalized["entry_signature64"] = _signature64(
            "hhs_pass219_lane5_repository_capability_python_registry_node_v1",
            normalized,
        )
        edge = {
            "from": normalized["node_id"],
            "to": f"python-registry-source:{normalized['path']}#{normalized['registry']}",
            "type": "DECLARED_IN_OPERATION_REGISTRY",
        }
        return normalized, edge

    def build(self) -> dict[str, Any]:
        public_catalog = self.inherited._public_catalog()
        native_exports = self.inherited._native_exports()
        python_registry, python_registry_manifest = self._python_operation_registry()
        if not public_catalog:
            raise RuntimeError("Pass147 public capability catalog is empty")
        if not native_exports:
            raise RuntimeError("cumulative exact ABI export surface is empty")

        public_nodes: list[dict[str, Any]] = []
        native_nodes: list[dict[str, Any]] = []
        python_nodes: list[dict[str, Any]] = []
        edges: list[dict[str, str]] = []

        for item in public_catalog:
            node, node_edges = self.inherited._public_node(item)
            public_nodes.append(node)
            edges.extend(node_edges)
        for item in native_exports:
            node, edge = self.inherited._native_node(item)
            native_nodes.append(node)
            edges.append(edge)
        for item in python_registry:
            node, edge = self._python_registry_node(item)
            python_nodes.append(node)
            edges.append(edge)

        if any(node["authority_class"] != AUTH_OBSERVATION for node in python_nodes):
            raise RuntimeError("Python registry discovery attempted an authority promotion")
        if any(
            node["hash216_composition_eligible"] or node["superedge_promotion_eligible"]
            for node in python_nodes
        ):
            raise RuntimeError("Python registry discovery attempted automatic graph promotion")

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

        nodes = sorted(
            public_nodes + native_nodes + python_nodes,
            key=lambda node: str(node["node_id"]),
        )
        node_ids = [str(node["node_id"]) for node in nodes]
        if len(node_ids) != len(set(node_ids)):
            raise RuntimeError("repository capability node IDs are not unique")
        signatures = [int(node["entry_signature64"]) for node in nodes]
        if len(signatures) != len(set(signatures)):
            raise RuntimeError("repository capability 64-bit entry signature collision")
        if len(nodes) > MAX_ENTRIES:
            raise RuntimeError(
                f"repository capability model contains {len(nodes)} entries, exceeding native bound {MAX_ENTRIES}"
            )

        edges = sorted(edges, key=lambda edge: (edge["from"], edge["type"], edge["to"]))
        if any(
            edge["type"] in {"HASH216_COMPOSITION", "HASH216_COMPOSITION_EDGE", "SUPEREDGE"}
            for edge in edges
        ):
            raise RuntimeError("discovery topology contains an unauthorized composition promotion")

        # These two domains are deliberately identical to 1.43 so a same-tree
        # successor can prove inherited source-root equality.
        public_catalog_root = hash72("hhs_pass147_public_catalog_v1", public_catalog)
        native_export_root = _sha256_root(
            "hhs_pass219_lane5_capability_self_model_native_exports_v1",
            native_exports,
        )
        python_registry_root = _sha256_root(
            "hhs_pass219_lane5_repository_capability_python_registry_v1",
            {
                "manifest": python_registry_manifest,
                "records": python_registry,
            },
        )
        dependency_root = _sha256_root(
            "hhs_pass219_lane5_repository_capability_dependency_graph_v1", edges
        )
        model_core = {
            "schema": SCHEMA,
            "version": VERSION,
            "source_policy": SOURCE_POLICY,
            "public_catalog_root_hash72": public_catalog_root,
            "native_export_root_sha256": native_export_root,
            "python_registry_root_sha256": python_registry_root,
            "python_registry_manifest": python_registry_manifest,
            "dependency_root_sha256": dependency_root,
            "canonical_boundary_export": CANONICAL_BOUNDARY_EXPORT,
            "nodes": nodes,
            "edges": edges,
            "scope": {
                "pass147_public_registry_complete": True,
                "cumulative_exact_abi_complete": True,
                "pass214_structural_python_operation_registry_complete": True,
                "repository_total_historical_capability_complete": False,
            },
            "promotion_policy": {
                "discovery_auto_promotes_hash216_composition": False,
                "discovery_auto_promotes_superedges": False,
                "typed_replay_proof_required_before_composition": True,
            },
        }
        model_root = _sha256_root(
            "hhs_pass219_lane5_repository_capability_reverse_discovery_v1",
            model_core,
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
            python_registry_root=python_registry_root,
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
                "python_operation_registry": len(python_nodes),
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


def build_repository_capability_reverse_discovery(
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    return Pass219Lane5RepositoryCapabilityReverseDiscovery(repo_root).build()


__all__ = [
    "SCHEMA",
    "SOURCE_POLICY",
    "CANONICAL_BOUNDARY_EXPORT",
    "Pass219Lane5RepositoryCapabilityReverseDiscovery",
    "build_repository_capability_reverse_discovery",
]
