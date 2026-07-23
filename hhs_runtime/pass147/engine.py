from __future__ import annotations

from typing import Any, Mapping

from hhs_runtime.pass145.errors import Pass145Error
from hhs_runtime.pass146 import engine as parent_engine
from hhs_runtime.pass146.engine import HHS146BoundaryEngine

# Additive Pass 147 boundary vocabulary. The inherited engine remains authoritative.
parent_engine.CAPABILITIES.update({"PUBLIC_DISCOVERY", "DOCUMENTATION_READ", "EXTERNAL_AGENT"})
parent_engine.OPERATION_SPECS.update({
    "PUBLIC_DISCOVER": {"capabilities": ["PUBLIC_DISCOVERY", "DATABASE_READ", "PATH_EXECUTION"], "reversibility": "APPEND_ONLY_NONDESTRUCTIVE", "components": ["PUBLIC_CAPABILITY_REGISTRY"], "mutating": False},
    "PUBLIC_DOC_QUERY": {"capabilities": ["DOCUMENTATION_READ", "DATABASE_READ", "QUERY", "PATH_EXECUTION"], "reversibility": "APPEND_ONLY_NONDESTRUCTIVE", "components": ["PUBLIC_DOCUMENTATION_DATABASE", "KNOWLEDGE_QUERY_PLANNER"], "mutating": False},
    "PUBLIC_DOC_INSTALL": {"capabilities": ["DOCUMENTATION_READ", "INGEST", "DATABASE_WRITE", "PATH_EXECUTION"], "reversibility": "CHECKPOINT_REVERSIBLE", "components": ["PUBLIC_DOCUMENTATION_INSTALLER", "DOCUMENT_INGESTION", "KNOWLEDGE_DATABASE"], "mutating": True},
    "PUBLIC_REGISTRY_SYNC": {"capabilities": ["PUBLIC_DISCOVERY", "DATABASE_WRITE", "PATH_EXECUTION"], "reversibility": "TRANSACTIONALLY_REVERSIBLE", "components": ["PUBLIC_CAPABILITY_REGISTRY"], "mutating": True},
})


class HHS147BoundaryEngine(HHS146BoundaryEngine):
    def _target_scope_value(self, operation: str, request: Mapping[str, Any]) -> str:
        if operation in {"PUBLIC_DISCOVER", "PUBLIC_DOC_QUERY", "PUBLIC_DOC_INSTALL", "PUBLIC_REGISTRY_SYNC"}:
            return "PUBLIC_SURFACE"
        return super()._target_scope_value(operation, request)

    def _relevant_state_root(self, identity: Mapping[str, Any], grant: Mapping[str, Any], operation: str, request: Mapping[str, Any]) -> str:
        if operation in {"PUBLIC_DISCOVER", "PUBLIC_DOC_QUERY", "PUBLIC_DOC_INSTALL", "PUBLIC_REGISTRY_SYNC"}:
            from hhs_runtime.pass145.canonical import hash72
            if operation in {"PUBLIC_DISCOVER", "PUBLIC_REGISTRY_SYNC"}:
                relevant = {"catalog_root_hash72": hash72("hhs_pass147_public_catalog_v1", self.service.public_registry.build_catalog())}
            else:
                rows = self.db.conn.execute("SELECT source_id,source_root_hash72,raw_sha256 FROM sources WHERE namespace='hhs-public-docs-v147' ORDER BY source_id").fetchall()
                relevant = {"public_document_roots": [dict(r) for r in rows]}
            return hash72("hhs_pass147_public_relevant_state_v1", {"identity": {"identity_id": identity["identity_id"], "identity_hash72": identity["identity_hash72"], "active": identity["active"]}, "grant": {"grant_id": grant["grant_id"], "grant_hash72": grant["grant_hash72"], "revoked": grant["revoked"]}, "operation": operation, "request": dict(request), "relevant": relevant})
        return super()._relevant_state_root(identity, grant, operation, request)

    def _dispatch(self, contract: Mapping[str, Any], *, identity_token: str | None = None) -> tuple[Any, dict[str, Any]]:
        operation = contract["operation"]
        request = contract["request"]
        if operation == "PUBLIC_DISCOVER":
            action = str(request.get("action", "list"))
            registry = self.service.public_registry
            if action == "version": return self.service.version(), {}
            if action == "status": return self.service.status(), {}
            if action == "doctor": return self.service.doctor(), {}
            if action == "capabilities": return self.service.capabilities(), {}
            if action == "list":
                return registry.list(classification=request.get("filter_classification"), surface_type=request.get("surface_type")), {}
            if action == "describe":
                return registry.describe(request.get("identifier", "")), {}
            if action == "graph":
                return registry.graph(), {}
            if action == "audit":
                return registry.audit(), {}
            if action == "api":
                return registry.api_describe(request.get("path")), {}
            if action == "schema":
                return registry.schema_describe(request.get("name")), {}
            if action == "boundary":
                target = str(request.get("target", ""))
                if target.startswith("BND-"):
                    contract = self.get_contract(target)
                    return {"schema": "HHS_PASS147_BOUNDARY_EXPLANATION_V1", "kind": "ADMITTED_CONTRACT", "contract": contract, "privileged_internal_access": 0}, {}
                from hhs_runtime.pass146 import engine as pe
                spec = pe.OPERATION_SPECS.get(target.upper())
                if spec is None:
                    raise Pass145Error("PUBLIC_PRIMITIVE_MISSING", f"boundary operation not found: {target}", "BOUNDARY_EXPLAIN")
                return {"schema": "HHS_PASS147_BOUNDARY_EXPLANATION_V1", "kind": "OPERATION_CONTRACT", "operation": target.upper(), "minimum_capabilities": spec["capabilities"], "reversibility_class": spec["reversibility"], "components": spec["components"], "mutating": spec["mutating"], "path_constructed_before_execution": True}, {}
            if action == "runtime_types":
                from .registry import runtime_types
                return runtime_types(), {}
            if action == "examples":
                from .registry import examples
                return examples(), {}
            if action == "error":
                from .registry import error_explain
                return error_explain(str(request.get("code", ""))), {}
            raise Pass145Error("PUBLIC_PRIMITIVE_MISSING", f"unknown public discovery action: {action}", "PUBLIC_DISCOVERY")
        if operation == "PUBLIC_DOC_QUERY":
            return self.service.query_public_docs(str(request.get("question", "")), limit=min(int(request.get("limit", 50)), 200)), {}
        if operation == "PUBLIC_DOC_INSTALL":
            from .docs import PUBLIC_DOCUMENTS
            return self.service.install_public_docs(PUBLIC_DOCUMENTS), {}
        if operation == "PUBLIC_REGISTRY_SYNC":
            return self.service.public_registry.synchronize(), {}
        return super()._dispatch(contract, identity_token=identity_token)
