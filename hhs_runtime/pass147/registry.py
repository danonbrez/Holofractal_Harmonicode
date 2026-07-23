from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from hhs_runtime.pass145.canonical import canonical_json, hash72, stable_id, utc_now
from hhs_runtime.pass145.errors import Pass145Error
from hhs_runtime.pass145 import cli as pass145_cli
from hhs_runtime.pass146 import cli as pass146_cli
from hhs_runtime.pass146.engine import HHS146BoundaryEngine

PASS_ID = "HHS-P147"
VERSION = "147.1.0"

PUBLIC_CLASSIFICATIONS = {
    "PUBLICLY_CALLABLE",
    "PUBLICLY_COMPOSABLE",
    "PUBLICLY_SCRIPTABLE",
    "PUBLICLY_DECLARABLE",
    "PUBLICLY_REQUESTABLE_THROUGH_BOUNDARY",
    "EXPLICITLY_RESTRICTED_BY_CONTRACT",
    "PLATFORM_INAPPLICABLE",
    "OBSERVED_FAILING",
}

ERROR_CATALOG: dict[str, dict[str, Any]] = {
    "RUNTIME_REJECTED": {"meaning": "The authoritative runtime rejected the submitted script, object, or transition.", "recovery": "Inspect diagnostics, repair the public artifact, validate again, and resubmit through a new boundary."},
    "CAPABILITY_UNDECLARED": {"meaning": "Static validation inferred a capability that the artifact did not declare.", "recovery": "Declare the exact capability or remove the operation that requires it."},
    "SCRIPT_COMMAND_REJECTED": {"meaning": "A script contains a command outside the documented HHS script command set.", "recovery": "Replace it with a command exposed by the script contract and validate the repaired version."},
    "PUBLIC_PRIMITIVE_MISSING": {"meaning": "No documented public primitive currently represents the requested lawful operation.", "recovery": "Inspect the capability graph and register or implement the missing public primitive."},
    "DOCUMENTATION_INCOMPLETE": {"meaning": "The public contract lacks sufficient schemas, examples, constraints, or failure semantics for independent use.", "recovery": "Repair the versioned public documentation before claiming public reachability."},
    "SCHEMA_UNAVAILABLE": {"meaning": "The callable operation has no inspectable input/output schema.", "recovery": "Publish and register the governing schema."},
    "AUTHORITY_INSUFFICIENT": {"meaning": "The active grant does not contain the minimum capabilities required for the operation.", "recovery": "Request a separately authorized narrower or sufficient grant."},
    "CAPABILITY_DENIED": {"meaning": "A requested capability is prohibited by the active boundary contract.", "recovery": "Remove the capability or obtain explicit authority."},
    "PLATFORM_INAPPLICABLE": {"meaning": "The operation cannot execute on the active platform.", "recovery": "Use a compatible platform without weakening the contract."},
    "RESOURCE_BOUNDED": {"meaning": "The admitted resource budget was reached safely.", "recovery": "Resume through a continuation receipt or request a larger bounded budget."},
    "DEPENDENCY_UNAVAILABLE": {"meaning": "A declared public dependency is unavailable.", "recovery": "Install or bind the documented dependency."},
    "PUBLIC_PATH_NONCOMPOSABLE": {"meaning": "The requested public primitives cannot be composed without violating type, authority, or boundary constraints.", "recovery": "Inspect the capability graph and repair the incompatible edge."},
    "OBSERVED_FAILING": {"meaning": "The public capability exists but failed in observed execution.", "recovery": "Inspect the execution and receipt evidence; do not reclassify it as unavailable."},
    "EXPLICIT_CONTRACT_RESTRICTION": {"meaning": "A governing contract intentionally forbids the requested operation.", "recovery": "No execution is permitted without a separately authorized contract revision."},
    "PRIVILEGED_INTERNAL_ACCESS_PROHIBITED": {"meaning": "The request attempts direct access to nucleus internals rather than a public primitive.", "recovery": "Reconstruct the operation through documented CLI, API, schema, script, sandbox, or LVM surfaces."},
}

RUNTIME_TYPES = [
    {"name": "EXACT_INTEGER", "canonical_authority": True, "float_projection": False},
    {"name": "EXACT_RATIONAL", "canonical_authority": True, "float_projection": False},
    {"name": "PRIME_EXPONENT_RATIO", "canonical_authority": True, "float_projection": False},
    {"name": "SYMBOLIC_ROOT", "canonical_authority": True, "float_projection": False},
    {"name": "TYPED_HHS_SYMBOL", "canonical_authority": True, "identity_rule": "glyph != operator_semantics != contextual_result"},
    {"name": "HASH72_RECEIPT", "canonical_authority": True, "role": "ancestry and replay witness"},
    {"name": "VM81_STATE", "canonical_authority": True, "role": "typed ordered runtime state"},
    {"name": "IEEE_FLOAT_PROJECTION", "canonical_authority": False, "control_lane_only": True},
]

API_SURFACES = [
    ("GET", "/api/v1/status", "Read canonical system status", False),
    ("GET", "/api/v1/database/status", "Read database status", False),
    ("GET", "/api/v1/source/{id}", "Inspect preserved source evidence", False),
    ("GET", "/api/v1/object/{id}", "Inspect a canonical knowledge object", False),
    ("GET", "/api/v1/graph/{id}", "Trace provenance-bound relationships", False),
    ("GET", "/api/v1/receipt/{id}", "Inspect a receipt", False),
    ("POST", "/api/v1/ingest", "Admit source bytes or text", True),
    ("POST", "/api/v1/query", "Compile and execute a read-only natural-language query", False),
    ("POST", "/api/v1/search", "Execute exact, lexical, symbol, or typed search", False),
    ("POST", "/api/v1/validate", "Run validation", False),
    ("POST", "/api/v1/replay", "Replay a canonical ingestion", False),
    ("POST", "/api/v1/backup", "Create a verified backup", True),
    ("POST", "/api/v1/restore/preview", "Preview a restore without mutation", False),
    ("GET", "/api/v1/security/status", "Inspect boundary security state", False),
    ("POST", "/api/v1/security/path/construct", "Construct the minimum admissible path", True),
    ("POST", "/api/v1/security/path/execute", "Execute an admitted path", True),
    ("POST", "/api/v1/security/path/replay", "Replay an admitted path", False),
    ("GET", "/api/v1/public/capabilities", "List public capability contracts", False),
    ("GET", "/api/v1/public/capability/{id}", "Describe one public capability", False),
    ("POST", "/api/v1/public/docs/query", "Query the versioned local public documentation corpus", False),
    ("POST", "/api/v1/public/agent/execute", "Execute a public command with external-agent credentials", True),
]


SCHEMA_CATALOG: dict[str, dict[str, Any]] = {
    "public-capability": {"$id": "hhs://schemas/pass147/public-capability", "type": "object", "required": ["capability_id", "surface_type", "classification", "capabilities", "reversibility_class", "mutating", "capability_hash72"], "properties": {"capability_id": {"type": "string"}, "surface_type": {"enum": ["CLI", "API"]}, "classification": {"enum": sorted(PUBLIC_CLASSIFICATIONS)}, "capabilities": {"type": "array", "items": {"type": "string"}}, "reversibility_class": {"type": "string"}, "mutating": {"type": "boolean"}, "capability_hash72": {"type": "string"}}},
    "external-agent-profile": {"$id": "hhs://schemas/pass147/external-agent-profile", "type": "object", "required": ["identity_id", "grant_id", "name", "capabilities", "operations", "privileged_internal_access", "procedural_external"], "properties": {"identity_id": {"type": "string"}, "grant_id": {"type": "string"}, "name": {"type": "string"}, "capabilities": {"type": "array", "items": {"type": "string"}}, "operations": {"type": "array", "items": {"type": "string"}}, "privileged_internal_access": {"const": 0}, "procedural_external": {"const": True}}},
    "external-agent-execution": {"$id": "hhs://schemas/pass147/external-agent-execution", "type": "object", "required": ["construction", "execution", "privileged_internal_access", "public_primitives_only"], "properties": {"privileged_internal_access": {"const": 0}, "public_primitives_only": {"const": True}}},
}

EXAMPLES = [
    {"id": "discover", "description": "Discover public capabilities", "commands": ["hhs surface list", "hhs surface graph", "hhs command describe ingest file"]},
    {"id": "knowledge", "description": "Create and query a knowledge environment", "commands": ["hhs env create demo --namespace demo", "hhs ingest file notes.md --namespace demo", "hhs query 'What definitions are in demo?' --namespace demo"]},
    {"id": "script", "description": "Import, validate, and run a script", "commands": ["hhs script import workflow.hhs --language HHS_COMMAND --environment ENV_ID", "hhs script validate SCRIPT_ID", "hhs script run SCRIPT_ID --input-json '{}'"]},
    {"id": "lvm", "description": "Create and execute an LVM", "commands": ["hhs lvm create machine.json --environment ENV_ID", "hhs lvm run LVM_ID --input-json '{}'"]},
    {"id": "external-agent", "description": "Create an external identity, discover contracts, and execute without internal access", "commands": ["hhs agent bootstrap external-model", "hhs agent execute --identity ID --grant GRANT --token TOKEN -- query 'What defines Hash72?'"]},
]


def _action_schema(action: argparse.Action) -> dict[str, Any]:
    if action.dest in {"help", "command"}:
        return {}
    result: dict[str, Any] = {"name": action.dest, "required": bool(getattr(action, "required", False)), "nargs": action.nargs, "default": None if action.default is argparse.SUPPRESS else action.default}
    if action.option_strings:
        result["flags"] = list(action.option_strings)
    if action.choices is not None:
        result["choices"] = list(action.choices)
    result["type"] = getattr(action.type, "__name__", None) or action.__class__.__name__
    return result


def _walk_parser(parser: argparse.ArgumentParser, prefix: tuple[str, ...] = ()) -> Iterable[dict[str, Any]]:
    sub_actions = [a for a in parser._actions if isinstance(a, argparse._SubParsersAction)]
    if not sub_actions:
        yield {"argv": list(prefix), "description": parser.description or "", "parameters": [v for a in parser._actions if (v := _action_schema(a))]}
        return
    for sub in sub_actions:
        for name, child in sorted(sub.choices.items()):
            yield from _walk_parser(child, prefix + (name,))


def _classification(argv: list[str]) -> tuple[str, list[str], str, bool]:
    if not argv:
        return "EXPLICITLY_RESTRICTED_BY_CONTRACT", [], "REJECTED_AS_UNSAFE", False
    try:
        caps, reversibility = HHS146BoundaryEngine._cli_capabilities(argv)
        return "PUBLICLY_REQUESTABLE_THROUGH_BOUNDARY", sorted(caps), reversibility, reversibility not in {"APPEND_ONLY_NONDESTRUCTIVE", "EXACTLY_REVERSIBLE"}
    except Pass145Error:
        if argv[0] in {"serve", "shell"}:
            return "PUBLICLY_CALLABLE", ["LOCAL_API" if argv[0] == "serve" else "PATH_EXECUTION"], "CHECKPOINT_REVERSIBLE", True
        return "EXPLICITLY_RESTRICTED_BY_CONTRACT", [], "REJECTED_AS_UNSAFE", False


@dataclass
class PublicSurfaceRegistry:
    db: Any

    def build_catalog(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        seen: set[tuple[str, ...]] = set()
        for parser in (pass145_cli.build_parser(), pass146_cli._security_parser()):
            for leaf in _walk_parser(parser):
                argv = leaf["argv"]
                if parser.prog == "hhs security":
                    argv = ["security", *argv]
                    classification, caps, reversibility, mutating = "PUBLICLY_CALLABLE", ["SECURITY_INSPECT"], "APPEND_ONLY_NONDESTRUCTIVE", False
                    if any(x in argv for x in ("create", "construct", "execute", "trust", "receive", "admit", "bootstrap-local")):
                        caps = ["SECURITY_ADMIN", "PATH_EXECUTION"]
                        reversibility = "TRANSACTIONALLY_REVERSIBLE"
                        mutating = True
                else:
                    classification, caps, reversibility, mutating = _classification(argv)
                key = tuple(argv)
                if key in seen:
                    continue
                seen.add(key)
                canonical = {"surface_type": "CLI", "argv": argv, "classification": classification, "capabilities": caps, "reversibility_class": reversibility, "mutating": mutating, "parameters": leaf["parameters"], "description": leaf["description"] or f"Public CLI operation: {' '.join(argv)}"}
                canonical["capability_id"] = stable_id("PUB", "hhs_pass147_public_capability_id_v1", canonical)
                canonical["capability_hash72"] = hash72("hhs_pass147_public_capability_v1", canonical)
                records.append(canonical)
        for method, path, description, mutating in API_SURFACES:
            canonical = {"surface_type": "API", "method": method, "path": path, "description": description, "classification": "PUBLICLY_REQUESTABLE_THROUGH_BOUNDARY", "capabilities": ["LOCAL_API", "PATH_EXECUTION"], "reversibility_class": "CHECKPOINT_REVERSIBLE" if mutating else "APPEND_ONLY_NONDESTRUCTIVE", "mutating": mutating, "parameters": []}
            canonical["capability_id"] = stable_id("PUB", "hhs_pass147_public_capability_id_v1", canonical)
            canonical["capability_hash72"] = hash72("hhs_pass147_public_capability_v1", canonical)
            records.append(canonical)
        for name in ("status", "version", "doctor", "capabilities", "surface", "command", "api-contract", "schema", "error", "runtime", "examples", "docs", "agent", "serve-public"):
            canonical = {"surface_type": "CLI", "argv": [name], "description": "Pass 147 public-surface operation", "classification": "PUBLICLY_CALLABLE", "capabilities": ["PUBLIC_DISCOVERY", "PATH_EXECUTION"], "reversibility_class": "APPEND_ONLY_NONDESTRUCTIVE", "mutating": name in {"docs", "agent"}, "parameters": []}
            canonical["capability_id"] = stable_id("PUB", "hhs_pass147_public_capability_id_v1", canonical)
            canonical["capability_hash72"] = hash72("hhs_pass147_public_capability_v1", canonical)
            records.append(canonical)
        return sorted(records, key=lambda x: (x["surface_type"], x.get("argv", []), x.get("path", "")))

    def synchronize(self) -> dict[str, Any]:
        catalog = self.build_catalog()
        catalog_root = hash72("hhs_pass147_public_catalog_v1", catalog)
        now = utc_now()
        def apply(conn):
            conn.execute("DELETE FROM public_capabilities")
            for item in catalog:
                conn.execute("INSERT INTO public_capabilities(capability_id,surface_type,classification,contract_json,capability_hash72,active,created_at) VALUES(?,?,?,?,?,1,?)", (item["capability_id"], item["surface_type"], item["classification"], canonical_json(item), item["capability_hash72"], now))
            return {"status": "PUBLIC_CAPABILITY_CATALOG_SYNCHRONIZED", "count": len(catalog), "catalog_root_hash72": catalog_root}
        return self.db.mutate("PUBLIC_CAPABILITY_CATALOG_SYNC", {"catalog_root_hash72": catalog_root, "count": len(catalog)}, apply, receipt_type="PUBLIC_CAPABILITY_REGISTRY_RECEIPT")

    def _catalog(self) -> list[dict[str, Any]]:
        rows = self.db.conn.execute("SELECT contract_json FROM public_capabilities WHERE active=1 ORDER BY surface_type,capability_id").fetchall()
        return [json.loads(r[0]) for r in rows] if rows else self.build_catalog()

    def list(self, *, classification: str | None = None, surface_type: str | None = None) -> dict[str, Any]:
        items = self._catalog()
        if classification:
            items = [x for x in items if x["classification"] == classification.upper()]
        if surface_type:
            items = [x for x in items if x["surface_type"] == surface_type.upper()]
        return {"schema": "HHS_PASS147_PUBLIC_CAPABILITY_LIST_V1", "count": len(items), "capabilities": items, "catalog_root_hash72": hash72("hhs_pass147_public_catalog_v1", items)}

    def describe(self, identifier: str | list[str]) -> dict[str, Any]:
        catalog = self._catalog()
        if isinstance(identifier, list):
            target = identifier
            matches = [x for x in catalog if x.get("surface_type") == "CLI" and x.get("argv") == target]
        else:
            matches = [x for x in catalog if x.get("capability_id") == identifier]
        if not matches:
            raise Pass145Error("PUBLIC_PRIMITIVE_MISSING", "public capability was not found", "PUBLIC_CAPABILITY", identifier if isinstance(identifier, str) else " ".join(identifier))
        return {"schema": "HHS_PASS147_PUBLIC_CAPABILITY_DESCRIPTION_V1", "capability": matches[0], "privileged_internal_access": False, "execution_requires_boundary": True}


    def api_describe(self, path: str | None = None) -> dict[str, Any]:
        items = [x for x in self._catalog() if x.get("surface_type") == "API"]
        if path:
            items = [x for x in items if x.get("path") == path]
            if not items:
                raise Pass145Error("PUBLIC_PRIMITIVE_MISSING", f"public API path was not found: {path}", "PUBLIC_API")
        return {"schema": "HHS_PASS147_PUBLIC_API_DESCRIPTION_V1", "count": len(items), "operations": items, "direct_sql": False, "boundary_required": True}

    def schema_describe(self, name: str | None = None) -> dict[str, Any]:
        if name:
            value = SCHEMA_CATALOG.get(name)
            if value is None:
                raise Pass145Error("SCHEMA_UNAVAILABLE", f"public schema was not found: {name}", "PUBLIC_SCHEMA")
            return {"schema": "HHS_PASS147_SCHEMA_DESCRIPTION_V1", "name": name, "definition": value}
        return {"schema": "HHS_PASS147_SCHEMA_CATALOG_V1", "schemas": [{"name": k, "$id": v["$id"]} for k, v in sorted(SCHEMA_CATALOG.items())]}

    def graph(self) -> dict[str, Any]:
        items = self.list()["capabilities"]
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        cap_nodes: set[str] = set()
        for item in items:
            nodes.append({"id": item["capability_id"], "type": "PUBLIC_PRIMITIVE", "label": " ".join(item.get("argv", [])) or f"{item.get('method')} {item.get('path')}"})
            for cap in item.get("capabilities", []):
                cid = f"CAP:{cap}"
                if cid not in cap_nodes:
                    cap_nodes.add(cid); nodes.append({"id": cid, "type": "BOUNDARY_CAPABILITY", "label": cap})
                edges.append({"from": item["capability_id"], "to": cid, "type": "REQUIRES"})
        graph = {"schema": "HHS_PASS147_PUBLIC_CAPABILITY_GRAPH_V1", "nodes": nodes, "edges": edges, "privileged_edges": 0}
        graph["graph_hash72"] = hash72("hhs_pass147_public_capability_graph_v1", graph)
        return graph

    def audit(self) -> dict[str, Any]:
        items = self.list()["capabilities"]
        invalid = [x for x in items if x["classification"] not in PUBLIC_CLASSIFICATIONS]
        undocumented = [x for x in items if not x.get("description") and not x.get("parameters")]
        bypass = [x for x in items if x.get("privileged_internal_access")]
        reachable = [x for x in items if x["classification"] in {"PUBLICLY_CALLABLE", "PUBLICLY_COMPOSABLE", "PUBLICLY_SCRIPTABLE", "PUBLICLY_DECLARABLE", "PUBLICLY_REQUESTABLE_THROUGH_BOUNDARY"}]
        result = {"schema": "HHS_PASS147_PUBLIC_SURFACE_AUDIT_V1", "total": len(items), "lawfully_reachable": len(reachable), "invalid_classifications": invalid, "documentation_gaps": undocumented, "privileged_bypass_surfaces": bypass, "potential_capability_complete": not invalid and not undocumented, "privileged_internal_access": 0, "closed": not invalid and not undocumented and not bypass}
        result["audit_hash72"] = hash72("hhs_pass147_public_surface_audit_v1", result)
        return result


def error_explain(code: str) -> dict[str, Any]:
    key = code.upper()
    value = ERROR_CATALOG.get(key)
    if value is None:
        return {"schema": "HHS_PASS147_ERROR_EXPLANATION_V1", "code": key, "known": False, "classification": "DOCUMENTATION_INCOMPLETE", "recovery": "Inspect the originating receipt and governing subsystem documentation."}
    return {"schema": "HHS_PASS147_ERROR_EXPLANATION_V1", "code": key, "known": True, **value}


def runtime_types() -> dict[str, Any]:
    return {"schema": "HHS_PASS147_RUNTIME_TYPES_V1", "types": RUNTIME_TYPES, "O_distinct_from_pi": True, "canonical_float_authority": False}


def examples() -> dict[str, Any]:
    return {"schema": "HHS_PASS147_EXAMPLES_V1", "examples": EXAMPLES}
