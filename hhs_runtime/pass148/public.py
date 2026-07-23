from __future__ import annotations

from typing import Any

from hhs_runtime.pass145.canonical import hash72, stable_id
from hhs_runtime.pass145.errors import Pass145Error
from hhs_runtime.pass147.registry import PublicSurfaceRegistry, _walk_parser


SEMANTIC_API_SURFACES = [
    ("POST", "/api/v1/semantic-membrane/analyze", "Parse, classify, diagnose, persist, and receipt an expression", True),
    ("POST", "/api/v1/semantic-membrane/documents/analyze", "Segment and classify mixed semantic and narrative documents", True),
    ("POST", "/api/v1/semantic-membrane/derive", "Execute a witnessed authorized derivation", True),
    ("POST", "/api/v1/semantic-membrane/project", "Run an explicitly isolated control projection", True),
    ("POST", "/api/v1/semantic-membrane/promotions/request", "Request but do not authorize semantic promotion", True),
    ("POST", "/api/v1/semantic-membrane/promotions/evaluate", "Evaluate promotion using separately authenticated semantic authority", True),
    ("GET", "/api/v1/semantic-membrane/propositions/{id}", "Retrieve a proposition record", False),
    ("GET", "/api/v1/semantic-membrane/derivations/{id}", "Retrieve a derivation graph", False),
    ("GET", "/api/v1/semantic-membrane/rules/{rule_id}", "Retrieve public semantic rule documentation", False),
    ("POST", "/api/v1/semantic-membrane/replay", "Replay a semantic proposition, derivation, or projection", True),
    ("GET", "/api/v1/semantic-membrane/audit", "Audit authority isolation and registry closure", False),
]

SCHEMAS: dict[str, dict[str, Any]] = {
    "pass148-proposition": {
        "$id": "hhs://schemas/pass148/proposition",
        "type": "object",
        "required": ["proposition_id", "source_expression", "canonical_ast_hash", "source_type", "source_reference", "primary_class", "consequence_class", "authority_level", "operator_profile", "lane_scope", "gate_scope", "branch_conditions", "dependencies", "assumptions", "prohibited_promotions", "interpretation_version", "interpretation_hash", "hash72_identity", "timestamp"],
    },
    "pass148-derivation": {
        "$id": "hhs://schemas/pass148/derivation",
        "type": "object",
        "required": ["derivation_id", "input_propositions", "output_proposition", "ordered_steps", "unresolved_dependencies", "control_contamination", "promotion_requested", "promotion_authorized", "derivation_hash72", "receipt"],
    },
    "pass148-promotion": {
        "$id": "hhs://schemas/pass148/promotion",
        "type": "object",
        "required": ["source_proposition_id", "source_class", "target_class", "governing_rule", "dependency_set", "scope", "requested_by_identity", "status"],
    },
    "pass148-analysis-request": {
        "$id": "hhs://schemas/pass148/analysis-request",
        "type": "object",
        "required": ["expression", "source_type", "requested_operator_profile"],
    },
}


class Pass148PublicSurfaceRegistry(PublicSurfaceRegistry):
    def build_catalog(self) -> list[dict[str, Any]]:
        records = super().build_catalog()
        from .cli import build_parser
        parser = build_parser()
        for leaf in _walk_parser(parser):
            argv = leaf["argv"]
            if not argv or argv[0] != "semantic":
                continue
            mutating = argv[1:2] not in (["classify"], ["proposition"], ["derivation"], ["rule"], ["audit"])
            admin = argv[1:2] in (["promotion-evaluate"], ["registry"])
            caps = ["SEMANTIC_READ", "PATH_EXECUTION"]
            if mutating: caps += ["DATABASE_WRITE"]
            if admin: caps += ["SEMANTIC_AUTHORITY_ADMIN"]
            canonical = {
                "surface_type": "CLI", "argv": argv,
                "classification": "PUBLICLY_REQUESTABLE_THROUGH_BOUNDARY" if admin else "PUBLICLY_CALLABLE",
                "capabilities": sorted(set(caps)),
                "reversibility_class": "APPEND_ONLY_NONDESTRUCTIVE" if not mutating else "CHECKPOINT_REVERSIBLE",
                "mutating": mutating,
                "parameters": leaf["parameters"],
                "description": leaf["description"] or f"Pass 148 semantic operation: {' '.join(argv)}",
                "privileged_semantic_authority": 0 if not admin else "SEPARATE_AUTHENTICATION_REQUIRED",
            }
            canonical["capability_id"] = stable_id("PUB", "hhs_pass147_public_capability_id_v1", canonical)
            canonical["capability_hash72"] = hash72("hhs_pass147_public_capability_v1", canonical)
            records.append(canonical)
        for method, path, description, mutating in SEMANTIC_API_SURFACES:
            admin = path.endswith("promotions/evaluate")
            canonical = {
                "surface_type": "API", "method": method, "path": path, "description": description,
                "classification": "PUBLICLY_REQUESTABLE_THROUGH_BOUNDARY",
                "capabilities": ["LOCAL_API", "PATH_EXECUTION", "SEMANTIC_AUTHORITY_ADMIN"] if admin else ["LOCAL_API", "PATH_EXECUTION", "SEMANTIC_READ"],
                "reversibility_class": "CHECKPOINT_REVERSIBLE" if mutating else "APPEND_ONLY_NONDESTRUCTIVE",
                "mutating": mutating, "parameters": [],
                "promotion_request_is_authorization": False,
                "explicit_semantic_authority_credentials_required": admin,
            }
            canonical["capability_id"] = stable_id("PUB", "hhs_pass147_public_capability_id_v1", canonical)
            canonical["capability_hash72"] = hash72("hhs_pass147_public_capability_v1", canonical)
            records.append(canonical)
        dedup = {item["capability_hash72"]: item for item in records}
        return sorted(dedup.values(), key=lambda x: (x["surface_type"], x.get("argv", []), x.get("path", "")))

    def schema_describe(self, name: str | None = None) -> dict[str, Any]:
        if name in SCHEMAS:
            return {"schema": "HHS_PASS148_SCHEMA_DESCRIPTION_V1", "name": name, "definition": SCHEMAS[name]}
        if name:
            return super().schema_describe(name)
        parent = super().schema_describe(None)
        parent["schemas"].extend({"name": k, "$id": v["$id"]} for k, v in sorted(SCHEMAS.items()))
        parent["schema"] = "HHS_PASS148_SCHEMA_CATALOG_V1"
        return parent
