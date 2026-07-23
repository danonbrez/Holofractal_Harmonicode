from __future__ import annotations

import json
import os
import re
import secrets
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_runtime.pass145.canonical import canonical_json, hash72, stable_id, utc_now
from hhs_runtime.pass145.errors import Pass145Error
from hhs_runtime.pass146.service import HHS146Service
from hhs_runtime.pass146 import engine as parent_engine
from .engine import HHS147BoundaryEngine
from .registry import ERROR_CATALOG, PASS_ID, VERSION, PublicSurfaceRegistry, examples, runtime_types

PUBLIC_DOC_NAMESPACE = "hhs-public-docs-v147"


class HHS147Service(HHS146Service):
    def __init__(self, db_path: str | Path, **kwargs: Any):
        super().__init__(db_path, **kwargs)
        self.security = HHS147BoundaryEngine(self)
        self.public_registry = PublicSurfaceRegistry(self.db)

    def version(self) -> dict[str, Any]:
        return {"schema": "HHS_PASS147_VERSION_V1", "pass_id": PASS_ID, "version": VERSION, "parent": super().version(), "rule": {"potential_lawful_capability": "COMPLETE", "privileged_internal_access": 0, "procedural_model": "EXPERT_EXTERNAL_DEVELOPER"}}

    def capabilities(self) -> dict[str, Any]:
        parent = super().capabilities()
        parent["schema"] = "HHS_PASS147_CAPABILITIES_V1"
        parent["pass_id"] = PASS_ID
        parent["capabilities"].update({
            "public_capability_registry": "CLI_AVAILABLE",
            "public_capability_graph": "CLI_AVAILABLE",
            "command_contract_introspection": "CLI_AVAILABLE",
            "api_contract_introspection": "CLI_AVAILABLE",
            "schema_introspection": "CLI_AVAILABLE",
            "error_explanation": "CLI_AVAILABLE",
            "runtime_type_introspection": "CLI_AVAILABLE",
            "local_documentation_database": "CLI_AVAILABLE",
            "external_agent_identity_and_grant": "CLI_AVAILABLE",
            "external_agent_boundary_execution": "CLI_AVAILABLE",
            "direct_nucleus_access": "BLOCKED_BY_EXPLICIT_CONTRACT",
            "direct_database_access": "BLOCKED_BY_EXPLICIT_CONTRACT",
            "unmediated_shell_access": "BLOCKED_BY_EXPLICIT_CONTRACT",
            "hidden_privileged_shortcuts": "PROHIBITED",
        })
        return parent

    def status(self) -> dict[str, Any]:
        parent = super().status()
        audit = self.public_registry.audit()
        docs = self.db.conn.execute("SELECT COUNT(*) FROM sources WHERE namespace=?", (PUBLIC_DOC_NAMESPACE,)).fetchone()[0]
        return {"schema": "HHS_PASS147_STATUS_V1", "ok": bool(parent["ok"] and audit["closed"]), "parent_status": parent, "public_surface_audit": audit, "public_document_count": docs, "privileged_internal_access": 0}

    def doctor(self) -> dict[str, Any]:
        parent = super().doctor()
        audit = self.public_registry.audit()
        checks = {**parent["checks"], "public_surface_completeness": {"ok": audit["closed"], **audit}, "procedural_externality": {"ok": True, "direct_kernel": False, "direct_sql": False, "repository_introspection": False, "boundary_required": True}, "semantic_identity": {"ok": True, "O_distinct_from_pi": True, "canonical_float_authority": False}}
        return {"schema": "HHS_PASS147_DOCTOR_V1", "ok": all(bool(x.get("ok")) for x in checks.values()), "checks": checks}

    def install_public_docs(self, docs: Sequence[Mapping[str, str]]) -> dict[str, Any]:
        installed = []
        for item in docs:
            name = str(item["name"])
            text = str(item["text"])
            result = self.ingest_bytes(text.encode("utf-8"), name=name, mime_type="text/markdown", namespace=PUBLIC_DOC_NAMESPACE, source_kind="VERSIONED_PUBLIC_DOCUMENTATION", acquisition={"method": "PASS147_EMBEDDED_DOCUMENTATION", "public": True}, analyze=True)
            installed.append({"name": name, "source_id": result["source_id"], "source_root_hash72": result["source_root_hash72"]})
        return {"schema": "HHS_PASS147_PUBLIC_DOC_INSTALL_V1", "status": "PUBLIC_DOCUMENTATION_INSTALLED", "documents": installed, "count": len(installed)}

    def query_public_docs(self, question: str, *, limit: int = 50) -> dict[str, Any]:
        result = self.query(question, namespace=PUBLIC_DOC_NAMESPACE, limit=limit)
        result["schema"] = "HHS_PASS147_PUBLIC_DOCUMENTATION_QUERY_V1"
        result["documentation_namespace"] = PUBLIC_DOC_NAMESPACE
        result["source_authority"] = "VERSIONED_LOCAL_CORPUS"
        return result

    def create_external_agent(self, issuer_identity: str, issuer_grant: str, issuer_token: str, name: str, *, capabilities: Sequence[str] | None = None) -> dict[str, Any]:
        requested = sorted(set(capabilities or [
            "PUBLIC_DISCOVERY", "DOCUMENTATION_READ", "EXTERNAL_AGENT", "PATH_EXECUTION", "DATABASE_READ", "DATABASE_WRITE", "QUERY", "SEARCH", "VALIDATE", "INGEST", "FILESYSTEM_READ", "FILESYSTEM_WRITE", "NATIVE_RUNTIME", "INTER_SANDBOX", "LOCAL_API"
        ]))
        forbidden = {"SECURITY_ADMIN", "NETWORK_SEND", "NETWORK_RECEIVE"}
        if forbidden.intersection(requested):
            raise Pass145Error("PRIVILEGED_INTERNAL_ACCESS_PROHIBITED", f"external-agent bootstrap cannot include privileged capabilities: {sorted(forbidden.intersection(requested))}", "EXTERNAL_AGENT")
        identity = self.security.create_identity(issuer_identity, issuer_grant, issuer_token, name, identity_type="EXTERNAL_AGENT")
        grant = self.security.create_grant(issuer_identity, issuer_grant, issuer_token, identity["result"]["identity_id"], capabilities=requested, operations=["RUN_CLI_COMMAND", "PUBLIC_DISCOVER", "PUBLIC_DOC_QUERY"], sources=["*", "PUBLIC_SURFACE"], destinations=["LOCAL_RESULT"], resource_policy={"max_steps": 64, "max_output_bytes": 4 * 1024 * 1024, "max_recursive_depth": 16, "max_messages": 64, "timeout_seconds": 30}, disclosure_policy={"classifications": ["PUBLIC", "INTERNAL"], "allow_remote": False})
        profile = {"identity_id": identity["result"]["identity_id"], "grant_id": grant["result"]["grant_id"], "name": name, "capabilities": requested, "operations": ["RUN_CLI_COMMAND", "PUBLIC_DISCOVER", "PUBLIC_DOC_QUERY"], "privileged_internal_access": 0, "procedural_external": True}
        profile_id = stable_id("AGT", "hhs_pass147_external_agent_profile_id_v1", profile)
        profile_hash = hash72("hhs_pass147_external_agent_profile_v1", profile)
        def apply(conn):
            conn.execute("INSERT INTO external_agent_profiles(profile_id,identity_id,grant_id,name,profile_json,profile_hash72,active,created_at) VALUES(?,?,?,?,?,?,1,?)", (profile_id, profile["identity_id"], profile["grant_id"], name, canonical_json(profile), profile_hash, utc_now()))
            return {"status": "EXTERNAL_AGENT_PROFILE_CREATED", "profile_id": profile_id, "profile_hash72": profile_hash, **profile}
        stored = self.db.mutate("EXTERNAL_AGENT_PROFILE_CREATE", {"profile_hash72": profile_hash}, apply, receipt_type="EXTERNAL_AGENT_PROFILE_RECEIPT")
        return {"schema": "HHS_PASS147_EXTERNAL_AGENT_BOOTSTRAP_V1", "profile": stored["result"], "authentication_token": identity["authentication_token"], "token_displayed_once": True}

    def external_execute(self, identity_id: str, grant_id: str, token: str, argv: Sequence[str], *, stdin_text: str | None = None) -> dict[str, Any]:
        if not argv:
            raise Pass145Error("PUBLIC_PRIMITIVE_MISSING", "empty public command", "EXTERNAL_AGENT")
        prohibited = {"shell", "serve"}
        if argv[0] in prohibited:
            raise Pass145Error("PRIVILEGED_INTERNAL_ACCESS_PROHIBITED", f"external agent must use the dedicated governed {argv[0]} lifecycle surface", "EXTERNAL_AGENT")
        args = list(argv)
        operation = "RUN_CLI_COMMAND"
        request: dict[str, Any]
        if args[0] in {"status", "version", "doctor", "capabilities"}:
            operation = "PUBLIC_DISCOVER"; request = {"action": args[0], "classification": "INTERNAL", "external_agent": True}
        elif args[:2] == ["surface", "list"]:
            operation = "PUBLIC_DISCOVER"; request = {"action": "list", "classification": "INTERNAL", "external_agent": True}
        elif args[:2] == ["surface", "graph"]:
            operation = "PUBLIC_DISCOVER"; request = {"action": "graph", "classification": "INTERNAL", "external_agent": True}
        elif args[:2] == ["surface", "audit"]:
            operation = "PUBLIC_DISCOVER"; request = {"action": "audit", "classification": "INTERNAL", "external_agent": True}
        elif args[:2] == ["command", "describe"]:
            operation = "PUBLIC_DISCOVER"; request = {"action": "describe", "identifier": args[2:], "classification": "INTERNAL", "external_agent": True}
        elif args[:2] == ["api-contract", "describe"]:
            operation = "PUBLIC_DISCOVER"; request = {"action": "api", "path": args[2] if len(args) > 2 else None, "classification": "INTERNAL", "external_agent": True}
        elif args[:2] == ["schema", "inspect"]:
            operation = "PUBLIC_DISCOVER"; request = {"action": "schema", "name": args[2] if len(args) > 2 else None, "classification": "INTERNAL", "external_agent": True}
        elif args[:2] == ["boundary", "explain"]:
            operation = "PUBLIC_DISCOVER"; request = {"action": "boundary", "target": args[2] if len(args) > 2 else "", "classification": "INTERNAL", "external_agent": True}
        elif args[:2] == ["error", "explain"]:
            operation = "PUBLIC_DISCOVER"; request = {"action": "error", "code": args[2] if len(args) > 2 else "", "classification": "INTERNAL", "external_agent": True}
        elif args[:2] == ["runtime", "types"]:
            operation = "PUBLIC_DISCOVER"; request = {"action": "runtime_types", "classification": "INTERNAL", "external_agent": True}
        elif args[0] == "examples":
            operation = "PUBLIC_DISCOVER"; request = {"action": "examples", "classification": "INTERNAL", "external_agent": True}
        elif args[:2] == ["docs", "query"]:
            operation = "PUBLIC_DOC_QUERY"; request = {"question": " ".join(args[2:]), "limit": 50, "classification": "INTERNAL", "external_agent": True}
        else:
            request = {"argv": args, "classification": "INTERNAL", "external_agent": True, "privileged_internal_access": 0}
            if stdin_text is not None:
                request["stdin_text"] = stdin_text
        constructed = self.security.construct_path(identity_id, grant_id, token, operation, request)
        executed = self.security.execute_path(constructed["result"]["contract_id"], identity_id, token)
        return {"schema": "HHS_PASS147_EXTERNAL_AGENT_EXECUTION_V1", "operation": operation, "construction": constructed["result"], "execution": executed["result"], "privileged_internal_access": 0, "public_primitives_only": True}
